import shutil,unittest
from helpers import *
class GraphTests(unittest.TestCase):
 def test_explicit_and_source_edges(self):
  v=base();source(v);wiki(v,'topic','domain',sources=[]);wiki(v,sources=['Raw/Sources/evidence.md'],relationships=['part-of|topic-domain']);r=run(v,'graph-build');self.assertEqual(r.returncode,0);text=(v/'Wiki/graph.jsonl').read_text();self.assertIn('part-of',text);self.assertIn('supported-by',text);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
