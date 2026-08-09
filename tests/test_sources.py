import shutil,unittest
from helpers import *
class SourceTests(unittest.TestCase):
 def test_hash_mismatch_fails(self):
  v=base();source(v,bad=True);r=run(v,'source-hash','--check');shutil.rmtree(v);self.assertNotEqual(r.returncode,0);self.assertIn('FAIL',r.stdout)
 def test_missing_hash_populated_only(self):
  v=base();p=source(v);text=p.read_text();start=text.index('ContentHash: ');end=text.index('\n',start);p.write_text(text[:start]+'ContentHash: ""'+text[end:]);r=run(v,'source-hash','--update-missing');self.assertEqual(r.returncode,0);self.assertIn('sha256:',p.read_text());shutil.rmtree(v)
 def test_malformed_source_is_reported_without_traceback(self):
  v=base();(v/'Raw/Sources/bad.md').write_text('not frontmatter');r=run(v,'source-lint');self.assertNotEqual(r.returncode,0);self.assertIn('frontmatter',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_hash_check_reports_malformed_source_without_traceback(self):
  v=base();(v/'Raw/Sources/bad.md').write_text('not frontmatter');r=run(v,'source-hash','--check');self.assertNotEqual(r.returncode,0);self.assertIn('frontmatter',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_invalid_utf8_source_is_reported_without_traceback(self):
  for args in [('source-lint',),('source-hash','--check')]:
   with self.subTest(args=args):
    v=base();(v/'Raw/Sources/bad.md').write_bytes(b'\xff\xfe');r=run(v,*args);self.assertNotEqual(r.returncode,0);self.assertIn('bad.md',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_hash_update_is_non_mutating_when_any_source_is_malformed(self):
  v=base();p=source(v);text=p.read_text();start=text.index('ContentHash: ');end=text.index('\n',start);p.write_text(text[:start]+'ContentHash: ""'+text[end:]);(v/'Raw/Sources/bad.md').write_text('not frontmatter');before=pbytes(v);r=run(v,'source-hash','--update-missing');self.assertNotEqual(r.returncode,0);self.assertEqual(before,pbytes(v));shutil.rmtree(v)
 def test_manifest_rebuild_preserves_canonical_processed_coverage(self):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);self.assertEqual(run(v,'source-scan','--update','--accept-covered').returncode,0);(v/'Schema/source-manifest.jsonl').unlink();self.assertEqual(run(v,'build').returncode,0);r=run(v,'source-lint');self.assertEqual(r.returncode,0,r.stdout+r.stderr);row=json.loads((v/'Schema/source-manifest.jsonl').read_text());self.assertEqual(row['covered_by'],['concept-architecture']);shutil.rmtree(v)
 def test_changed_source_invalidates_coverage_and_cannot_be_accepted_covered(self):
  v=base();p=source(v);wiki(v,sources=['Raw/Sources/evidence.md']);self.assertEqual(run(v,'source-scan','--update','--accept-covered').returncode,0);p.write_text(p.read_text()+'changed\n');run(v,'build');row=json.loads((v/'Schema/source-manifest.jsonl').read_text());self.assertEqual(row['covered_by'],[]);self.assertFalse(row['processed']);r=run(v,'source-scan','--update','--accept-covered');self.assertNotEqual(r.returncode,0);shutil.rmtree(v)
 def test_source_coverage_fails_for_any_uncovered_source(self):
  v=base();source(v);run(v,'build');r=run(v,'source-coverage');self.assertNotEqual(r.returncode,0);self.assertIn('uncovered=1',r.stdout);shutil.rmtree(v)
 def test_accept_covered_refuses_when_strict_lint_fails(self):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md'],body='\n# Broken\n\nClaim [C-001]\n');r=run(v,'source-scan','--update','--accept-covered');self.assertNotEqual(r.returncode,0);self.assertIn('lint',r.stdout+r.stderr);self.assertFalse(parse_fixture(v/'Raw/Sources/evidence.md')[0]['Processed']);shutil.rmtree(v)
 def test_accept_change_is_contained_and_requires_an_actual_change(self):
  v=base();source(v);same=run(v,'source-hash','--accept-change','Raw/Sources/evidence.md');self.assertNotEqual(same.returncode,0);escape=run(v,'source-hash','--accept-change','../outside.md');self.assertNotEqual(escape.returncode,0);self.assertNotIn('Traceback',escape.stderr);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
