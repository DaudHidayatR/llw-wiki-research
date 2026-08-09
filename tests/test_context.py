import shutil,unittest
from helpers import *
class ContextTests(unittest.TestCase):
 def test_fixed_ranking_and_tie_break(self):
  v=base();source(v);wiki(v,'concept','zulu',ident='concept-zulu',sources=['Raw/Sources/evidence.md']);wiki(v,'synthesis','alpha',ident='synthesis-alpha',sources=['Raw/Sources/evidence.md']);
  profile={'schema_version':2,'id':'context-profile-default-research','type':'context-profile','title':'Default','name':'default-research','max_items':20,'include_memory':False,'include_decisions':True,'include_research':True,'include_raw':'fallback','created':DATE,'updated':DATE};(v/'Context/Profiles/default-research.md').write_text(fm(profile,'\n# Context Profile\n'))
  r1=run(v,'context-pack','--query','architecture','--profile','default-research');first=(v/'Context/Packs/architecture.md').read_bytes();r2=run(v,'context-pack','--query','architecture','--profile','default-research');self.assertEqual(r1.returncode,0);self.assertEqual(first,(v/'Context/Packs/architecture.md').read_bytes());lines=[x for x in r1.stdout.splitlines() if x[:1].isdigit()];self.assertIn('synthesis-alpha',lines[0]);shutil.rmtree(v)
 def test_stage_a_includes_direct_research_and_decision_candidates(self):
  v=base();research(v,'investigation','sandbox','Agent Sandbox');decision(v,'decision-sandbox',body='\n# Agent Sandbox Decision\n');r=run(v,'context-pack','--query','agent sandbox');self.assertEqual(r.returncode,0);self.assertIn('investigation-sandbox',r.stdout);self.assertIn('decision-sandbox',r.stdout);shutil.rmtree(v)
 def test_profile_priority_applies_before_top_eight_seed_cutoff(self):
  v=base()
  for i in range(8):wiki(v,'synthesis',f'syn-{i}',ident=f'synthesis-syn-{i}',body='\n# Same\n\nneedle\n')
  wiki(v,'concept','preferred',ident='concept-preferred',body='\n# Same\n\nneedle\n');profile(v,'concept-first',['concept','synthesis']);r=run(v,'context-pack','--query','needle','--profile','concept-first');self.assertIn('concept-preferred',r.stdout);shutil.rmtree(v)
 def test_exact_normalization_removes_stopwords(self):
  v=base();wiki(v,title='The Architecture');r=run(v,'search-catalog','--query','architecture');line=next(x for x in r.stdout.splitlines() if 'concept-architecture' in x);self.assertTrue(line.strip().startswith('125 '),line);shutil.rmtree(v)
 def test_raw_fallback_only_when_no_non_raw_candidate(self):
  v=base();source(v,'quokka',title='Quokka Evidence');r=run(v,'context-pack','--query','quokka');self.assertIn('source-quokka',r.stdout);wiki(v,title='Quokka');r=run(v,'context-pack','--query','quokka');self.assertIn('concept-architecture',r.stdout);self.assertNotIn('source-quokka',r.stdout);shutil.rmtree(v)
 def test_benchmark_recall_counts_each_expected_id(self):
  v=base();wiki(v,title='Found');(v/'Schema/retrieval-benchmark.jsonl').write_text(json.dumps({'query':'found','expected_ids':['concept-architecture','concept-missing']})+'\n');r=run(v,'benchmark-retrieval');metrics=json.loads(r.stdout[:r.stdout.index('\nbenchmark-retrieval:')]);self.assertEqual(metrics['Recall@10'],.5);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
