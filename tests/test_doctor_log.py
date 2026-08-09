import json,shutil,unittest
from helpers import *
class DoctorLogTests(unittest.TestCase):
 def test_doctor_reports_malformed_inputs_without_traceback_or_mutation(self):
  v=base();(v/'Schema/version.json').write_text('{bad');(v/'Raw/Sources/bad.md').write_text('bad');before=pbytes(v);r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertNotIn('Traceback',r.stdout+r.stderr);self.assertIn('malformed',r.stdout);self.assertEqual(before,pbytes(v));shutil.rmtree(v)
 def test_doctor_checks_all_required_catalogs_and_test_payloads(self):
  v=base();r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn('missing_catalogs=',r.stdout);self.assertIn('fixture_payloads=missing',r.stdout);shutil.rmtree(v)
 def test_doctor_checks_complete_required_structure(self):
  for missing in ('Wiki/Entities','Wiki/Projects','Wiki/Comparisons','Wiki/Synthesis','Wiki/Logs','Research/Investigations','Research/Findings','Research/Open','Memory/Preferences','Memory/Observations','Decisions/Superseded','Context/Packs'):
   with self.subTest(missing=missing):
    v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);run(v,'build');shutil.rmtree(v/missing);r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn(missing,r.stdout+r.stderr);shutil.rmtree(v)
 def test_doctor_checks_every_generated_index_and_jsonl(self):
  required=['Schema/source-manifest.jsonl','Wiki/catalog.jsonl','Wiki/graph.jsonl','Wiki/index.md','Wiki/Topics/index.md','Wiki/Concepts/index.md','Wiki/Entities/index.md','Wiki/Projects/index.md','Wiki/Comparisons/index.md','Wiki/Synthesis/index.md','Wiki/Logs/index.md','Research/catalog.jsonl','Research/index.md','Memory/catalog.jsonl','Memory/index.md','Decisions/catalog.jsonl','Decisions/index.md']
  for missing in required:
   with self.subTest(missing=missing):
    v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);run(v,'build');(v/missing).unlink();r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn(missing,r.stdout+r.stderr);shutil.rmtree(v)
 def test_doctor_reports_malformed_jsonl_and_invalid_utf8_without_traceback(self):
  for relative,payload in [('Wiki/catalog.jsonl',b'{bad\n'),('Wiki/Concepts/bad.md',b'\xff\xfe')]:
   with self.subTest(relative=relative):
    v=base();source(v);wiki(v,sources=['Raw/Sources/evidence.md']);run(v,'build');(v/relative).parent.mkdir(parents=True,exist_ok=True);(v/relative).write_bytes(payload);r=run(v,'doctor');self.assertNotEqual(r.returncode,0);self.assertIn(relative,r.stdout+r.stderr);self.assertNotIn('Traceback',r.stdout+r.stderr);shutil.rmtree(v)
 def test_log_refuses_empty_slug(self):
  v=base();r=run(v,'log','--title','!!!','--details','x');self.assertNotEqual(r.returncode,0);self.assertIn('empty slug',r.stderr);self.assertEqual(list((v/'Wiki/Logs').glob('*.md')),[]);shutil.rmtree(v)
if __name__=='__main__':unittest.main()