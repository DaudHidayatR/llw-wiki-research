import shutil,unittest
from helpers import *
class SourceTests(unittest.TestCase):
 def test_hash_mismatch_fails(self):
  v=base();source(v,bad=True);r=run(v,'source-hash','--check');shutil.rmtree(v);self.assertNotEqual(r.returncode,0);self.assertIn('FAIL',r.stdout)
 def test_missing_hash_populated_only(self):
  v=base();p=source(v);text=p.read_text();start=text.index('ContentHash: ');end=text.index('\n',start);p.write_text(text[:start]+'ContentHash: ""'+text[end:]);r=run(v,'source-hash','--update-missing');self.assertEqual(r.returncode,0);self.assertIn('sha256:',p.read_text());shutil.rmtree(v)
if __name__=='__main__':unittest.main()
