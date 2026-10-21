"""Twelve small malformed-flow boundaries; no new native or pixel proof."""
from pathlib import Path
import copy,importlib.util,json,sys,unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('ready_tested',HERE/'verify-ready-entry-native-v001.py');V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
PINS=V.read(HERE/'required-pins-v001.json')['pins'];CONTRACT=V.read(HERE/'ready-entry-source-contract-v001.json')
def synthetic():
 r=V.read(PINS['old_synthetic_basis']['path']);r['leather_combo_only_trial']=False
 for o in r['observations']:
  if o['supported'] and o['committed_armor_id']==r['light_instance_id'] and o['clip'] in CONTRACT['frames']:
   f=CONTRACT['frames'][o['clip']][o['frame']];o['draw_stack']=list(f['draw_stack']);o['root']=list(f['root']);o['grip']=list(f['grip']);o['weapon_angle']=V.math.degrees(V.math.atan2(f['axis'][1],f['axis'][0]))*o['facing']
 return r
def delete_observation(r,index):
 r['observations'].pop(index);r['capture_timing']['frame_wall_offsets_s'].pop(index)
class Boundaries(unittest.TestCase):
 def test_01_full_synthetic_ready_entry(self):
  result=V.verify_flow(synthetic(),CONTRACT);self.assertEqual(result['three_stage_masks'],[63,63,63]);self.assertEqual(result['isolated_J1_to_Ready'],'OPEN_full_chain_intervenes')
 def test_02_fewer_than_three_ready_before(self):
  r=synthetic();delete_observation(r,next(i for i,o in enumerate(r['observations']) if o['flow_step']==5))
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_03_wrong_new_J0_stack(self):
  r=synthetic();o=next(o for o in r['observations'] if o['clip']=='sword_primary_1' and o['frame']==0);o['draw_stack'][0]='wrong.old.layer'
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_04_old_J2_frame_stack_changed(self):
  r=synthetic();o=next(o for o in r['observations'] if o['clip']=='sword_primary_1' and o['frame']==2);o['draw_stack'][0]='wrong.new.layer'
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_05_extra_Space_input(self):
  r=synthetic();r['normal_input_requests'].append(dict(key='SpaceBar',down=True))
  with self.assertRaises(ValueError):V.verify_inputs(r)
 def test_06_integer_boolean_input(self):
  r=synthetic();r['normal_input_requests'][0]['down']=1
  with self.assertRaises(ValueError):V.verify_inputs(r)
 def test_07_wrong_light_instance(self):
  r=synthetic();o=next(o for o in r['observations'] if o['clip']=='sword_primary_1');o['committed_armor_id']='99'
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_08_missing_extra_combo_phase(self):
  r=synthetic();r['light_primary_phase_masks'][2]=31
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_09_stripped_medium_phase(self):
  r=synthetic();r['phasechecks'].pop(9)
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_10_fewer_than_three_fresh_post_chain_ready(self):
  r=synthetic();end=max(o['end'] for o in r['observations'] if o['clip']=='sword_primary_3');i=next(i for i,o in enumerate(r['observations']) if o['flow_step']==6 and o['clip']=='sword_ready_idle' and o['sim']>=end);delete_observation(r,i)
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_11_same_draw_clock_mismatch(self):
  r=synthetic();r['observations'][0]['actual_sim']+=.01
  with self.assertRaises(ValueError):V.verify_flow(r,CONTRACT)
 def test_12_sources_and_default_map_flags(self):
  _,_,c=V.setup();self.assertEqual(len(c['sources']),67);args=V.expected_arguments(Path('F:/Ourgame/synthetic-only'))
  self.assertIn('/Game/Maps/FirstRoom',args);self.assertEqual(args.count('-DungeonFairytalePrimary1Bridge258Preview'),1)
  self.assertFalse(any('OnlyProof' in x or 'Knight' in x or 'LandingPriority' in x or 'UseFixed' in x for x in args))
if __name__=='__main__':unittest.main(verbosity=2)
