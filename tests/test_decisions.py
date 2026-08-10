import shutil,unittest
from helpers import *
class DecisionTests(unittest.TestCase):
 def test_supersession_preserves_body_and_links(self):
  v=base();decision(v,'decision-old');decision(v,'decision-new');r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertEqual(r.returncode,0);old=(v/'Decisions/Superseded/old.md').read_text();new=(v/'Decisions/Active/new.md').read_text();self.assertIn('Original rationale marker',old);self.assertIn('decision-new',old);self.assertIn('decision-old',new);shutil.rmtree(v)
 def test_cycle_fails(self):
  v=base();decision(v,'decision-old',supersedes=['decision-new']);decision(v,'decision-new');r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('cycle refused',r.stderr);shutil.rmtree(v)
 def test_destination_collision_refuses_without_mutation(self):
  v=base();old=decision(v,'decision-old');new=decision(v,'decision-new');collision=v/'Decisions/Superseded/old.md';d=parse_fixture(decision(v,'decision-collision','superseded'))[0];(v/'Decisions/Superseded/collision.md').unlink();collision.write_text(fm(d,'\n# Collision\n\nDO NOT OVERWRITE\n'));before=pbytes(v);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('destination exists',r.stderr);self.assertEqual(before,pbytes(v));shutil.rmtree(v)
 def test_dangling_destination_symlink_refuses_without_external_write(self):
  v=base();decision(v,'decision-old');decision(v,'decision-new');outside=Path(tempfile.mkdtemp())/'outside.md';dest=v/'Decisions/Superseded/old.md';dest.symlink_to(outside);before=pbytes(v);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('destination exists',r.stderr);self.assertEqual(before,pbytes(v));self.assertFalse(outside.exists());shutil.rmtree(v);shutil.rmtree(outside.parent)
 def test_symlinked_destination_directory_refuses_external_write(self):
  v=base();decision(v,'decision-old');decision(v,'decision-new');outside=Path(tempfile.mkdtemp());shutil.rmtree(v/'Decisions/Superseded');(v/'Decisions/Superseded').symlink_to(outside,target_is_directory=True);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('unsafe destination',r.stderr);self.assertEqual(list(outside.iterdir()),[]);shutil.rmtree(v);shutil.rmtree(outside)
 def test_symlinked_decisions_root_refuses_external_access(self):
  v=base();outside=Path(tempfile.mkdtemp());shutil.rmtree(v/'Decisions');(v/'Decisions').symlink_to(outside,target_is_directory=True);(outside/'Active').mkdir();(outside/'Superseded').mkdir();decision(v,'decision-old');decision(v,'decision-new');before=pbytes(outside);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('unsafe decisions root',r.stderr);self.assertEqual(before,pbytes(outside));shutil.rmtree(v);shutil.rmtree(outside)
 def test_scalar_supersession_fields_refuse_without_mutation(self):
  v=base();old=decision(v,'decision-old');decision(v,'decision-new');rewrite(old,lambda d:d.update(supersedes=1));before=pbytes(v);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('invalid supersession metadata',r.stderr);self.assertNotIn('Traceback',r.stderr);self.assertEqual(before,pbytes(v));shutil.rmtree(v)
if __name__=='__main__':unittest.main()
