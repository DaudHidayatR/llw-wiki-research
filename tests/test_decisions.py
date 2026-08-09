import shutil,unittest
from helpers import *
class DecisionTests(unittest.TestCase):
 def test_supersession_preserves_body_and_links(self):
  v=base();decision(v,'decision-old');decision(v,'decision-new');r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertEqual(r.returncode,0);old=(v/'Decisions/Superseded/old.md').read_text();new=(v/'Decisions/Active/new.md').read_text();self.assertIn('Original rationale marker',old);self.assertIn('decision-new',old);self.assertIn('decision-old',new);shutil.rmtree(v)
 def test_cycle_fails(self):
  v=base();decision(v,'decision-old',supersedes=['decision-new']);decision(v,'decision-new');r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('cycle refused',r.stderr);shutil.rmtree(v)
 def test_destination_collision_refuses_without_mutation(self):
  v=base();old=decision(v,'decision-old');new=decision(v,'decision-new');collision=v/'Decisions/Superseded/old.md';d=parse_fixture(decision(v,'decision-collision','superseded'))[0];(v/'Decisions/Superseded/collision.md').unlink();collision.write_text(fm(d,'\n# Collision\n\nDO NOT OVERWRITE\n'));before=pbytes(v);r=run(v,'decision-supersede','--old','decision-old','--new','decision-new');self.assertNotEqual(r.returncode,0);self.assertIn('destination exists',r.stderr);self.assertEqual(before,pbytes(v));shutil.rmtree(v)
if __name__=='__main__':unittest.main()
