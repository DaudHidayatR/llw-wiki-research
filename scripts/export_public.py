#!/usr/bin/env python3
"""One-way allow-listed public Markdown export."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site-output'
ALLOW = ('Wiki', 'Research', 'Decisions')


def within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


if OUT.is_symlink():
    OUT.unlink()
elif OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for base in ALLOW:
    src = ROOT / base
    if not src.is_dir() or src.is_symlink():
        continue
    allowed_root = src.resolve()
    for path in src.rglob('*.md'):
        resolved = path.resolve()
        if path.is_symlink() or not path.is_file() or not within(resolved, allowed_root):
            continue
        dst = OUT / path.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
welcome = ROOT / 'Welcome.md'
if welcome.is_file() and not welcome.is_symlink() and welcome.resolve().parent == ROOT.resolve():
    shutil.copy2(welcome, OUT / 'Welcome.md')
print(f'export_public: {sum(1 for _ in OUT.rglob("*.md"))} markdown files -> {OUT}')
