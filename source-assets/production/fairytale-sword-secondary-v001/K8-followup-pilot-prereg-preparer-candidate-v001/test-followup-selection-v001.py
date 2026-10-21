"""Finite follow-up route selection checks; no new native evidence."""
from pathlib import Path
import copy,importlib.util,json,unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('followup',HERE/'prepare-followup-K-pilot-prereg-v001.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class Selection(unittest.TestCase):
 def setUp(self):self.t=json.loads(M.TEMPLATE.read_text('utf-8-sig'))
 def test_all_five_exact_frozen_routes_selected_without_mutating_template(self):
  prior=copy.deepcopy(self.t)
  for case in M.CASES:
   with self.subTest(case=case):self.assertEqual(M.select_case(self.t,case),self.t['cases'][case])
  self.assertEqual(self.t,prior)
 def test_repeated_fullright_and_unknown_case_rejected(self):
  for case in ['full_right','invented','none_full_left']:
   with self.subTest(case=case),self.assertRaises(M.NotReady):M.select_case(self.t,case)
 def test_verified_or_diagnostic_route_cannot_be_invented(self):
  for key,value in [('normal_route_native_verified',True),('route_native_verification',{}),('enemy_diagnostic_used',True)]:
   bad=copy.deepcopy(self.t);bad['cases']['full_left'][key]=value
   with self.subTest(key=key),self.assertRaises(M.NotReady):M.select_case(bad,'full_left')
 def test_case_facing_must_match_real_requested_side(self):
  bad=copy.deepcopy(self.t);bad['cases']['full_left']['facing']=1
  with self.assertRaises(M.NotReady):M.select_case(bad,'full_left')
if __name__=='__main__':unittest.main(verbosity=2)
