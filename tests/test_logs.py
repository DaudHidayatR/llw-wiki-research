import shutil,unittest
from helpers import *

class LogTests(unittest.TestCase):
 def test_empty_ascii_slug_is_refused_before_write(self):
  v=base();before=pbytes(v);r=run(v,'log','--title','💥','--details','unicode');self.assertNotEqual(r.returncode,0);self.assertIn('slug',r.stderr);self.assertEqual(before,pbytes(v));shutil.rmtree(v)

if __name__=='__main__':unittest.main()