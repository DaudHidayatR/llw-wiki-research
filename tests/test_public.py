import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/public-audit'


def vault():
    root = Path(tempfile.mkdtemp())
    (root / 'scripts').mkdir()
    for name in ('export_public.py', 'audit_public.py'):
        shutil.copy2(ROOT / 'scripts' / name, root / 'scripts' / name)
    return root


def run(root, script):
    return subprocess.run(
        [sys.executable, str(root / 'scripts' / script)],
        cwd=root, text=True, capture_output=True,
    )


class ExportPublicTests(unittest.TestCase):
    def setUp(self):
        self.root = vault()

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_export_skips_symlinked_markdown_file(self):
        (self.root / 'Wiki').mkdir()
        outside = self.root / 'outside.md'
        outside.write_text('# private\n')
        (self.root / 'Wiki/leak.md').symlink_to(outside)

        result = run(self.root, 'export_public.py')

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / 'site-output/Wiki/leak.md').exists())

    def test_export_skips_symlinked_allowed_root_and_welcome(self):
        outside = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, outside)
        (outside / 'leak.md').write_text('# private\n')
        (outside / 'welcome.md').write_text('# private welcome\n')
        (self.root / 'Wiki').symlink_to(outside, target_is_directory=True)
        (self.root / 'Welcome.md').symlink_to(outside / 'welcome.md')

        result = run(self.root, 'export_public.py')

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / 'site-output/Wiki/leak.md').exists())
        self.assertFalse((self.root / 'site-output/Welcome.md').exists())


class AuditPublicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.secret_cases = json.loads((FIXTURES / 'secret-cases.json').read_text())

    def setUp(self):
        self.root = vault()
        (self.root / 'site-output').mkdir()

    def tearDown(self):
        shutil.rmtree(self.root)

    def audit_text(self, text):
        path = self.root / 'site-output/Wiki/leak.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return run(self.root, 'audit_public.py')

    def test_audit_fails_when_output_is_missing(self):
        shutil.rmtree(self.root / 'site-output')

        result = run(self.root, 'audit_public.py')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('missing output', result.stdout)

    def test_audit_denies_roots_at_any_path_depth(self):
        for denied in ('Raw', 'Memory', 'Context', 'Schema', '.agents', 'scripts', 'tests'):
            with self.subTest(denied=denied):
                target = self.root / 'site-output/Wiki/nested' / denied
                target.mkdir(parents=True)
                result = run(self.root, 'audit_public.py')
                self.assertNotEqual(result.returncode, 0, denied)
                self.assertIn('denied path', result.stdout)
                shutil.rmtree(target)

    def test_audit_denies_obsidian_plugin_and_cache_state(self):
        for relative in (
            '.obsidian/workspace.json',
            'Wiki/.obsidian/plugins/example/main.js',
            'Research/.obsidian/cache/state',
            'Decisions/.obsidian/logs/debug.log',
        ):
            with self.subTest(relative=relative):
                target = self.root / 'site-output' / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('state')
                result = run(self.root, 'audit_public.py')
                self.assertNotEqual(result.returncode, 0, relative)
                self.assertIn('obsidian state', result.stdout)
                shutil.rmtree(next(p for p in target.parents if p.name == '.obsidian'))

    def test_audit_rejects_non_markdown_and_binary_markdown(self):
        non_markdown = self.root / 'site-output/Wiki/image.png'
        non_markdown.parent.mkdir(parents=True)
        non_markdown.write_bytes(b'not really an image')
        binary_markdown = self.root / 'site-output/Wiki/binary.md'
        binary_markdown.write_bytes((FIXTURES / 'invalid-utf8.bin').read_bytes())

        result = run(self.root, 'audit_public.py')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('binary/non-markdown: Wiki/image.png', result.stdout)
        self.assertIn('binary content: Wiki/binary.md', result.stdout)

    def test_audit_rejects_symlinked_output(self):
        outside = self.root / 'outside.md'
        outside.write_text('# private\n')
        target = self.root / 'site-output/Wiki/leak.md'
        target.parent.mkdir(parents=True)
        target.symlink_to(outside)

        result = run(self.root, 'audit_public.py')

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stdout)

    def test_audit_rejects_secret_payloads(self):
        for case in self.secret_cases:
            with self.subTest(name=case['name']):
                result = self.audit_text(''.join(case['parts']))
                self.assertNotEqual(result.returncode, 0, case['name'])
                self.assertIn(case['finding'], result.stdout)

    def test_audit_rejects_machine_local_paths(self):
        for path in (
            '/home/alice/wiki', '/Users/alice/wiki', '/root/wiki',
            '/etc/hosts', '/var/lib/wiki', '/srv', '/workspace', '/tmp',
            '/srv/wiki', '/workspace/wiki', '/tmp/wiki',
            r'C:\Users\Alice\wiki', r'D:\workspace\wiki', 'E:/tmp/wiki',
        ):
            with self.subTest(path=path):
                result = self.audit_text(f'Local checkout: `{path}`\n')
                self.assertNotEqual(result.returncode, 0, path)
                self.assertIn('absolute local path', result.stdout)

    def test_audit_allows_web_urls(self):
        result = self.audit_text('Public reference: https://example.com/docs/guide\n')

        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
