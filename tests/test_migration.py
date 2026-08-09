import hashlib,shutil,unittest
from helpers import *
class MigrationTests(unittest.TestCase):
 def test_check_non_mutating(self):
  v=base();source(v);wiki(v);before={str(p.relative_to(v)):hashlib.sha256(p.read_bytes()).hexdigest() for p in v.rglob('*') if p.is_file()};r=run(v,'migrate','--check');after={str(p.relative_to(v)):hashlib.sha256(p.read_bytes()).hexdigest() for p in v.rglob('*') if p.is_file()};self.assertEqual(r.returncode,0);self.assertEqual(before,after);shutil.rmtree(v)
 def test_apply_preserves_body(self):
  v=base();p=wiki(v);marker='Durable architecture separates evidence and memory.';r=run(v,'migrate','--apply');self.assertEqual(r.returncode,0,r.stdout+r.stderr);self.assertIn(marker,p.read_text());shutil.rmtree(v)
if __name__=='__main__':unittest.main()
