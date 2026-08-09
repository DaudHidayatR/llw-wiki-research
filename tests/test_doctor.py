import shutil,unittest
from helpers import *

class DoctorTests(unittest.TestCase):
 def test_missing_catalog_fails(self):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);run(v,'build');(v/'Decisions/catalog.jsonl').unlink();r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn('catalog',r.stdout+r.stderr);shutil.rmtree(v)
 def test_malformed_note_is_reported_without_traceback(self):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);run(v,'build');(v/'Wiki/Concepts/malformed.md').write_text('not frontmatter\n');r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn('malformed',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)

if __name__=='__main__':unittest.main()
