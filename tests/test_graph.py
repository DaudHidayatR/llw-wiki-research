import shutil,unittest
from helpers import *
class GraphTests(unittest.TestCase):
 def test_explicit_and_source_edges(self):
  v=base();source(v);wiki(v,'topic','domain',sources=[]);wiki(v,sources=['Raw/Sources/evidence.md'],relationships=['part-of|topic-domain']);r=run(v,'graph-build');self.assertEqual(r.returncode,0);text=(v/'Wiki/graph.jsonl').read_text();self.assertIn('part-of',text);self.assertIn('supported-by',text);shutil.rmtree(v)
 def test_wikilinks_resolve_by_canonical_path_not_ambiguous_stem(self):
  v=base();source(v);wiki(v,'topic','same',ident='topic-same',sources=[]);wiki(v,'concept','same',ident='concept-same',sources=[]);wiki(v,slug='linker',ident='concept-linker',body='\n# Linker\n\n[[Wiki/Concepts/same]]\n');run(v,'graph-build');edges=[json.loads(x) for x in (v/'Wiki/graph.jsonl').read_text().splitlines()];links=[x for x in edges if x['from']=='concept-linker' and x['source']=='wikilink'];self.assertEqual([x['to'] for x in links],['concept-same']);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
