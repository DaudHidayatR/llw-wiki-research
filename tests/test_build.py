import shutil,unittest
from pathlib import Path
from helpers import *
class BuildTests(unittest.TestCase):
 def setUp(self):self.v=base();source(self.v);wiki(self.v,sources=['Raw/Sources/evidence.md'])
 def tearDown(self):shutil.rmtree(self.v)
 def test_byte_identical_and_ordered(self):
  self.assertEqual(run(self.v,'build').returncode,0); paths=[self.v/'Wiki/catalog.jsonl',self.v/'Wiki/index.md',self.v/'Schema/source-manifest.jsonl'];a=[p.read_bytes() for p in paths]
  self.assertEqual(run(self.v,'build').returncode,0);self.assertEqual(a,[p.read_bytes() for p in paths]);rows=[json.loads(x) for x in paths[0].read_text().splitlines()];self.assertEqual([x['path'] for x in rows],sorted(x['path'] for x in rows))
 def test_stable_id_survives_rename_in_generated_catalog(self):
  p=self.v/'Wiki/Concepts/architecture.md';q=p.with_name('renamed-architecture.md');p.rename(q);self.assertEqual(run(self.v,'build').returncode,0);rows=[json.loads(x) for x in (self.v/'Wiki/catalog.jsonl').read_text().splitlines()];row=next(x for x in rows if x['path']=='Wiki/Concepts/renamed-architecture.md');self.assertEqual(row['id'],'concept-architecture')
if __name__=='__main__':unittest.main()
