import os,shutil,unittest
from helpers import *
class LintTests(unittest.TestCase):
 def check_bad(self,mutate,needle):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);mutate(v);r=run(v,'lint','--strict-evidence');shutil.rmtree(v);self.assertNotEqual(r.returncode,0);self.assertIn(needle,r.stdout+r.stderr)
 def test_duplicate_id(self):self.check_bad(lambda v:wiki(v,'topic','other','concept-architecture',[]), 'duplicate id')
 def test_bad_slug(self):self.check_bad(lambda v:(v/'Wiki/Concepts/architecture.md').rename(v/'Wiki/Concepts/Bad Name.md'),'invalid filename slug')
 def test_broken_raw(self):self.check_bad(lambda v:wiki(v,slug='broken',sources=['Raw/Sources/missing.md']),'broken/invalid source')
 def test_broken_research_source(self):self.check_bad(lambda v:research(v,'investigation','broken','Broken',sources=['Raw/Sources/missing.md']),'broken/invalid source')
 def test_source_count(self):self.check_bad(lambda v:wiki(v,slug='count',sources=['Raw/Sources/evidence.md'],source_count=2),'source_count mismatch')
 def test_relationship_target(self):self.check_bad(lambda v:wiki(v,slug='relation',relationships=['requires|concept-missing']),'unresolved relationship')
 def test_claim_without_entry(self):self.check_bad(lambda v:wiki(v,slug='claim',body='\n# X\n\nClaim [C-001]\n'),'has no ledger entry')
 def test_ledger_missing_source(self):self.check_bad(lambda v:wiki(v,slug='ledger',body='\n# X\n\nClaim [C-001]\n\n## Evidence Ledger\n\n- C-001 | confidence=high | Claim\n  - source: [[Raw/Sources/no.md]]\n'),'missing ledger source')
 def test_required_and_type_specific_fields(self):
  self.check_bad(lambda v:rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.pop('created')),'missing fields')
  self.check_bad(lambda v:rewrite(v/'Raw/Sources/evidence.md',lambda d:d.pop('Author')),'missing fields')
 def test_type_specific_status_confidence_location_slug_and_prefix(self):
  self.check_bad(lambda v:rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(status='open')),'invalid status')
  self.check_bad(lambda v:rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(confidence='confirmed')),'invalid confidence')
  self.check_bad(lambda v:rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(id='topic-wrong')),'id must start concept-')
  self.check_bad(lambda v:(v/'Raw/Sources/evidence.md').rename(v/'Raw/Sources/Bad Name.md'),'invalid filename slug')
 def test_all_id_references_resolve_and_supersession_cycles_fail(self):
  self.check_bad(lambda v:rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(supersedes=['concept-missing'])),'unresolved supersedes id')
  def cycle(v):
   wiki(v,'concept','other',ident='concept-other');rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(supersedes=['concept-other']));rewrite(v/'Wiki/Concepts/other.md',lambda d:d.update(supersedes=['concept-architecture']))
  self.check_bad(cycle,'supersession cycle')
  def reverse_cycle(v):
   wiki(v,'concept','other',ident='concept-other');rewrite(v/'Wiki/Concepts/architecture.md',lambda d:d.update(superseded_by=['concept-other']));rewrite(v/'Wiki/Concepts/other.md',lambda d:d.update(superseded_by=['concept-architecture']))
  self.check_bad(reverse_cycle,'supersession cycle')
 def test_malformed_evidence_ledger_syntax_fails(self):
  self.check_bad(lambda v:wiki(v,slug='ledger-syntax',body='\n# X\n\n## Evidence Ledger\n\n- C-001 confidence=high | missing separator\n'),'malformed evidence ledger')
 def test_source_paths_cannot_escape_or_resolve_through_symlink(self):
  outside=Path(tempfile.mkdtemp())/'outside.md';outside.write_text('secret')
  try:
   self.check_bad(lambda v:wiki(v,slug='escape',sources=['Raw/Sources/../../../'+outside.as_posix().lstrip('/')]),'escapes repository')
   def link(v):
    (v/'Raw/Sources/link.md').symlink_to(outside);wiki(v,slug='link',sources=['Raw/Sources/link.md'])
   self.check_bad(link,'symlink')
  finally:shutil.rmtree(outside.parent)
 def test_invalid_utf8_is_reported_without_traceback(self):
  v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);(v/'Wiki/Concepts/bad.md').write_bytes(b'\xff\xfe');r=run(v,'lint');self.assertNotEqual(r.returncode,0);self.assertIn('bad.md',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_list_valued_scalar_is_reported_without_traceback(self):
  v=base();source(v);p=wiki(v,sources=['Raw/Sources/evidence.md']);rewrite(p,lambda d:d.update(status=['active']));r=run(v,'lint');self.assertNotEqual(r.returncode,0);self.assertIn('status',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_wrong_scalar_and_list_types_are_reported_without_traceback(self):
  v=base();source(v);p=wiki(v,sources=['Raw/Sources/evidence.md']);rewrite(p,lambda d:d.update(type=['concept'],id=['concept-x'],sources=1,relationships=1,supersedes=1));r=run(v,'lint');self.assertNotEqual(r.returncode,0);self.assertIn('invalid type',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_list_valued_source_type_is_reported_without_traceback(self):
  v=base();p=source(v);rewrite(p,lambda d:d.update(SourceType=['web']));r=run(v,'lint');self.assertNotEqual(r.returncode,0);self.assertIn('SourceType',r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
if __name__=='__main__':unittest.main()
