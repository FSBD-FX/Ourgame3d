"""Finite host gate tests; historical UE report is input, never new K native proof."""
from pathlib import Path
import copy, importlib.util, json, unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('firstK',HERE/'prepare-first-K-pilot-prereg-v001.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
REPORT=Path('F:/Ourgame/UnrealGame/Saved/Automation/FirstRoomNativeRHI-20261019-063714/index.json')
class Gates(unittest.TestCase):
 def setUp(self):
  self.suite=json.loads(REPORT.read_text('utf-8-sig'));self.ids={x['fullTestPath'] for x in self.suite['tests']}
  self.cm=dict(registered_tests=203,passed=203,failed=0,notRun=0,inProcess=0,warnings=0)
 def test_real_historical203_shape_accepts_only_as_schema_input(self):
  self.assertIs(M.validate_green203(self.cm,self.suite,self.ids),True)
 def test_manifest_omitted_or_nonzero_notrun_inprocess_warnings_rejected(self):
  for key in ['notRun','inProcess','warnings']:
   for value in [1,None]:
    bad=copy.deepcopy(self.cm)
    if value is None:bad.pop(key)
    else:bad[key]=value
    with self.subTest(key=key,value=value),self.assertRaises(M.NotReady):M.validate_green203(bad,self.suite,self.ids)
 def test_actual_failed_or_warning_test_overrides_green_summary(self):
  for key,value in [('state','Fail'),('warnings',1),('errors',1)]:
   bad=copy.deepcopy(self.suite);bad['tests'][0][key]=value
   with self.subTest(key=key),self.assertRaises(M.NotReady):M.validate_green203(self.cm,bad,self.ids)
 def test_duplicate_or_changed_actual_test_ids_rejected(self):
  for duplicate in [True,False]:
   bad=copy.deepcopy(self.suite);bad['tests'][0]['fullTestPath']=bad['tests'][1]['fullTestPath'] if duplicate else 'CodexDungeon.UnknownReplacement'
   with self.subTest(duplicate=duplicate),self.assertRaises(M.NotReady):M.validate_green203(self.cm,bad,self.ids)
 def test_error_entry_rejected_even_if_counters_zero(self):
  bad=copy.deepcopy(self.suite);bad['tests'][0]['entries']=[{'event':{'type':'Error','message':'host rejection example, not native data'}}]
  with self.assertRaises(M.NotReady):M.validate_green203(self.cm,bad,self.ids)
 def test_output_cannot_escape_or_be_inside_capture_archive(self):
  archive=Path('F:/Ourgame/过程图稿与视频/2026-10-19_军剑K右侧前踏首次原生试验_v001')
  for output in [Path('F:/Ourgame/UnrealGame/Source/fake.json'),archive/'prereg.json',HERE/'prepare-first-K-pilot-prereg-v001.py']:
   with self.subTest(output=str(output)),self.assertRaises(M.NotReady):M.validate_output(output,archive)
if __name__=='__main__':unittest.main(verbosity=2)
