"""Only schema/layout adapter tests; no prereg/native evidence is generated."""
from pathlib import Path
from types import SimpleNamespace
import copy, importlib.util, json, unittest
HERE=Path(__file__).resolve().parent
C=HERE.parent
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
M=module(HERE/'prepare-first-K-pilot-prereg-v002.py','pilotAdapter')
PIX=C/'K8-native-pixel-checker-candidate-v002'
FREEZE=PIX/'candidate-freeze-v002.json'
CHECKER=PIX/'verify-K8-native-pixels-v002.py'
class OptionalInterface(unittest.TestCase):
 def ns(self,present=True):
  return SimpleNamespace(pixel_checker=CHECKER if present else None,pixel_checker_sha='aa677a9c15fb5dcf2414c22b7b5940870db4711d8d566e22122d942d6ee08188' if present else None,pixel_freeze=FREEZE if present else None,pixel_freeze_sha='fb14b809e95a53cb4b318f1e9cd97d5e8a68c1c53c1ba4ffa14d7eda7d57e28a' if present else None)
 def adapter(self):
  self.assertTrue(hasattr(M,'pixel_dependencies'),'optional dependency adapter missing');return M.pixel_dependencies
 def test_real_relative_pixel_freeze_is_accepted(self):
  try:j=M.frozen_members(M.filepin(FREEZE))
  except (KeyError,M.NotReady) as e:self.fail('real pixel files/relative_path schema rejected: '+str(e))
  self.assertEqual(j['schema'],'K8-native-pixel-checker-candidate-freeze-v002')
 def test_actual_pixel_own_freeze_consumes_both_nested_fields(self):
  deps=self.adapter()(self.ns());p={'checker_dependencies':deps};pixel=module(CHECKER,'realPixelInterface')
  self.assertEqual(pixel.own_freeze(p),M.filepin(FREEZE))
  self.assertNotIn('K_pixel_composition_freeze',p)
 def test_default_null_stays_pending_and_incomplete_pair_rejects(self):
  fn=self.adapter();self.assertEqual(fn(self.ns(False)),dict(K_pixel_composition=None,K_pixel_composition_freeze=None))
  ns=self.ns();ns.pixel_freeze_sha=None
  with self.assertRaises(M.NotReady):fn(ns)
 def test_unknown_and_mixed_freeze_schema_rejected(self):
  self.assertTrue(hasattr(M,'freeze_member_pins'),'explicit schema/path adapter missing')
  for change in ['unknown','mixed']:
   j=M.load(FREEZE)
   if change=='unknown':j['schema']='Invented-files-schema'
   else:j['members']=[]
   with self.subTest(change=change),self.assertRaises(M.NotReady):M.freeze_member_pins(FREEZE,j)
 def test_relative_paths_cannot_be_absolute_driven_or_escape(self):
  self.assertTrue(hasattr(M,'freeze_member_pins'),'explicit schema/path adapter missing')
  for rel in ['../escape.py','F:/fake.py','F:fake.py','/fake.py','sub\\fake.py','a//b.py','a/./b.py','']:
   j=M.load(FREEZE);j['files'][0]['relative_path']=rel
   with self.subTest(relative_path=rel),self.assertRaises(M.NotReady):M.freeze_member_pins(FREEZE,j)
 def test_root_members_keep_absolute_paths_and_duplicate_rejected(self):
  self.assertTrue(hasattr(M,'freeze_member_pins'),'explicit schema/path adapter missing')
  p=M.check(M.fixed('compound_freeze'));j=M.load(p)
  for kind in ['relative','duplicate']:
   bad=copy.deepcopy(j)
   if kind=='relative':bad['members'][0]['path']='before/fake.cpp'
   else:bad['members'].append(copy.deepcopy(bad['members'][0]))
   with self.subTest(kind=kind),self.assertRaises(M.NotReady):M.freeze_member_pins(p,bad)
if __name__=='__main__':unittest.main(verbosity=2)
