"""Bounded host negatives; no UE, Content writes or manufactured native success."""
import copy,json,unittest
from move7_import_contract_v001 import *
M=read(HERE/'Move7-source-import-contract-v001.json')
LAYOUT=dict(M,schema='Root-GuardMove7-native-import-v001')
class Contracts(unittest.TestCase):
 def test_source7_owner_identity(self):
  validate_layout(LAYOUT);self.assertEqual(tuple(x['source_native_batch_id']for x in M['assets']),SOURCE_IDS)
  self.assertEqual(sum(len(x['artist_surface_markers'])for x in M['assets']),18)
 def test_duplicate_component_and_fake_animation_id_rejected(self):
  for mutate in [lambda x:x['assets'][1].update(component='BodyRest'),lambda x:x['assets'][1].update(frame=0),lambda x:x['assets'][0].update(NativeSourceId=252)]:
   x=copy.deepcopy(LAYOUT);mutate(x)
   with self.assertRaises(ValueError):validate_layout(x)
 def test_replace_or_wrong_total_rejected(self):
  for key,value in [('replace_existing',True),('expected_final_count',1370),('namespace','/Game/Production/FirstBatch')]:
   x=copy.deepcopy(LAYOUT);x[key]=value
   with self.assertRaises(ValueError):validate_layout(x)
 def test_pending_approval_rejects(self):
  with self.assertRaisesRegex(ValueError,'Actual explicit Root'):approval(HERE/'Root-limited-import-approval-TEMPLATE-v001.json',dict(LAYOUT,manifest_path=HERE/'Move7-source-import-contract-v001.json'))
 def test_old_package_digest_tamper_detected_without_write(self):
  old,_=old_contracts();x=copy.deepcopy(old[0]);x['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Pinned bytes changed'):check(x)
if __name__=='__main__':unittest.main()
