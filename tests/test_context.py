import shutil,unittest
from helpers import *
class ContextTests(unittest.TestCase):
 def test_fixed_ranking_and_tie_break(self):
  v=base();source(v);wiki(v,'concept','zulu',ident='concept-zulu',sources=['Raw/Sources/evidence.md']);wiki(v,'synthesis','alpha',ident='synthesis-alpha',sources=['Raw/Sources/evidence.md']);
  profile={'schema_version':2,'id':'context-profile-default-research','type':'context-profile','title':'Default','name':'default-research','max_items':20,'include_memory':False,'include_decisions':True,'include_research':True,'include_raw':'fallback','created':DATE,'updated':DATE};(v/'Context/Profiles/default-research.md').write_text(fm(profile,'\n# Context Profile\n'))
  r1=run(v,'context-pack','--query','architecture','--profile','default-research');first=(v/'Context/Packs/architecture.md').read_bytes();r2=run(v,'context-pack','--query','architecture','--profile','default-research');self.assertEqual(r1.returncode,0);self.assertEqual(first,(v/'Context/Packs/architecture.md').read_bytes());lines=[x for x in r1.stdout.splitlines() if x[:1].isdigit()];self.assertIn('synthesis-alpha',lines[0]);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
