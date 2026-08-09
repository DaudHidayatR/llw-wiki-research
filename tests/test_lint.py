import shutil,unittest
from helpers import *
class LintTests(unittest.TestCase):
 def check_bad(self,mutate,needle):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);mutate(v);r=run(v,'lint','--strict-evidence');shutil.rmtree(v);self.assertNotEqual(r.returncode,0);self.assertIn(needle,r.stdout+r.stderr)
 def test_duplicate_id(self):self.check_bad(lambda v:wiki(v,'topic','other','concept-architecture',[]), 'duplicate id')
 def test_bad_slug(self):self.check_bad(lambda v:(v/'Wiki/Concepts/architecture.md').rename(v/'Wiki/Concepts/Bad Name.md'),'invalid filename slug')
 def test_broken_raw(self):self.check_bad(lambda v:wiki(v,slug='broken',sources=['Raw/Sources/missing.md']),'broken/invalid source')
 def test_source_count(self):self.check_bad(lambda v:wiki(v,slug='count',sources=['Raw/Sources/evidence.md'],source_count=2),'source_count mismatch')
 def test_relationship_target(self):self.check_bad(lambda v:wiki(v,slug='relation',relationships=['requires|concept-missing']),'unresolved relationship')
 def test_claim_without_entry(self):self.check_bad(lambda v:wiki(v,slug='claim',body='\n# X\n\nClaim [C-001]\n'),'has no ledger entry')
 def test_ledger_missing_source(self):self.check_bad(lambda v:wiki(v,slug='ledger',body='\n# X\n\nClaim [C-001]\n\n## Evidence Ledger\n\n- C-001 | confidence=high | Claim\n  - source: [[Raw/Sources/no.md]]\n'),'missing ledger source')
if __name__=='__main__':unittest.main()
