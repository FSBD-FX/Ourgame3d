"""Small synthetic value tests + readonly real failed-v001 first-jump component.
No UE / images / native runs. Historical report is never rewritten.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import copy
import hashlib
import importlib.util
import json
import os
import sys
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import air_production_contract_v001 as C
HERE=Path(__file__).resolve().parent
OLD=C.AIR/'production-observer-candidate-v001/tooling-freeze-relative-v002'
REAL=C.ROOT/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_left_v001/原件/runtime-report.json'
OLD_TEST=C.AIR/'production-observer-candidate-v001/tooling/test-Air-production-host-v001.py'
V=C.module(HERE/'verify-Air-production-native-v001.py','new_queued_native_checker')
T=C.module(OLD_TEST,'old_frozen_value_fixture')
PROFILE,MANIFEST=T.PROFILE,T.MANIFEST
RUN=HERE/'validation-runs'/('q'+datetime.now(timezone.utc).strftime('%H%M%S%f'))

def pin(p):
 b=Path(p).read_bytes();return dict(path=str(Path(p).resolve()).replace('\\','/'),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:
  json.dump(o,f,ensure_ascii=False,allow_nan=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def source_first_air(start,end):
 at,h,v=start,0.,630.
 while at<end:
  to=min(end,at+.005);dt=to-at
  h=C.f32(max(0.,h+v*dt-900.*dt*dt));v=C.f32(v-C.f32(1800.*C.f32(dt)));at=to
 return h,v

def full_fixture(side=1):
 r=T.flow_fixture(side);obs=[]
 def add(frame,ordinal,sim,phase=None,physical=None):
  o=T.drawn_observation(frame,ordinal,side,sim,len(obs)+1);o['wall_offset_s']=sim+.01
  if phase is not None:o['phase']=phase
  if physical is not None:
   h,v=physical;d=o['new_air_draw'];old=o['old_draw'];root=d['root_source'];grip=d['grip_source'];scale=d['source_to_screen_scale']
   g=d['context_ground'];top=[g[0]-(root[0] if side>0 else 512-root[0])*scale,g[1]-h*.70-root[1]*scale]
   at=[g[0]+side*(grip[0]-root[0])*scale,g[1]-h*.70+(grip[1]-root[1])*scale]
   swordtop=[at[k]-d['sword_pivot_uv'][k]*d['weapon_width'] for k in range(2)]
   o.update(jump_height=h,vertical_velocity=v);d.update(sample_H=h,sample_V=v,jump_height=h,body_top=top,grip_screen=at,sword_top=swordtop)
   old['grip_screen']=at
   for slot in d['slots']:slot['top']=[C.f32(x) for x in (swordtop if slot['component']==8 else top)]
  o['melee_grounded']=o['wa_grounded']=(o['jump_height']==o['vertical_velocity']==0)
  obs.append(o);return o
 def ready(ordinal,sim,phase,light=False):
  o=add(5,2 if light else max(1,ordinal),sim,phase)
  o.update(physical_visual_key=-1,landing_visual_age=C.f32(.12),observed_air_transition_ordinal=ordinal,new_air_query_ok=False)
  o['new_air_draw']['drawn']=False;o['old_draw'].update(clip='sword_ready_idle',armor_drawn=light)
  return o
 ready(0,.1,2);ready(0,.12,3)
 add(0,1,.135,physical=source_first_air(.12,.135))
 for f,t in enumerate((.30,.47,.65,.83,.91),1):add(f,1,t)
 token_o=ready(1,.96,5,True)
 ready(1,1.02,6,True)
 add(0,2,1.035,physical=source_first_air(1.02,1.035))
 for f,t in enumerate((1.20,1.37,1.55,1.73,1.81),1):add(f,2,t)
 add(5,2,1.82,7)
 add(0,3,1.835,physical=source_first_air(1.82,1.835))
 for f,t in enumerate((2.,2.17,2.35,2.53,2.61),1):add(f,3,t)
 ready(3,2.68,9,True);ready(3,2.70,9,True)
 keys=('Enter','A' if side<0 else 'D','SpaceBar','E','SpaceBar','SpaceBar')
 walls=(.001,.04,.125,.94,1.025,1.825);sims=(0.,0.,.12,.93,1.02,1.82)
 inputs=[]
 for n,(key,wall,sim) in enumerate(zip(keys,walls,sims)):
  ordinal=(0,0,0,1,1,2)[n];light=n>=4;age=C.f32(.08) if n==5 else C.f32(.12)
  for down in (True,False):
   inputs.append(dict(key=key,down=down,wall_offset_s=wall+(0 if down else .003),sim=sim,
    before_H=0.,before_V=0.,before_landing_age=age,after_H=0.,after_V=0.,after_landing_age=age,
    context_sampled_before_InputKey=True,run=r['run'],owner=r['owner'],current_room=r['current_room'],epoch=r['epoch'],player_entity=r['owner'],
    weapon_instance=r['weapon_instance'],weapon_version=r['weapon_version'],armor_instance=r['armor_instance'] if light else '0',armor_version=r['armor_version'] if light else '0',
    observed_air_transition_ordinal_before=ordinal,space_enqueue_observer_ordinal=(1 if n==2 else 2 if n==4 else 3 if n==5 else 0) if down else 0,
    space_enqueue_ordinal_is_gameplay_jump_id=False))
 r.update(observations=obs,normal_inputs=inputs,capture_timing=dict(frame_wall_offsets_s=[o['wall_offset_s'] for o in obs],capture_start_monotonic_s=10.,capture_stop_monotonic_s=13.),
  starter_NoArmor_frames=sum(o['physical_visual_key']>=0 and o['observed_air_transition_ordinal']==1 for o in obs),
  light_frames=sum(o['physical_visual_key']>=0 and o['observed_air_transition_ordinal']>=2 for o in obs),landing_frames=sum(o['physical_visual_key']>=4 for o in obs),
  LGT_completed_Ready_callback_observed=True,LGT_completed_Ready_callback_consumed_once=True)
 r['LGT_completed_Ready_callback']=dict(completed_native_screenshot_callback=True,observation_index=obs.index(token_o),draw_id=token_o['old_draw']['draw_id'],
  draw_sim=token_o['sim'],callback_sim=token_o['sim'],wall_offset_s=token_o['wall_offset_s'],run=r['run'],owner=r['owner'],room=r['current_room'],epoch=r['epoch'],
  weapon_instance=r['weapon_instance'],weapon_version=r['weapon_version'],armor_instance=r['armor_instance'],armor_version=r['armor_version'],
  facing=side,old_draw=copy.deepcopy(token_o['old_draw']),actual_stack=copy.deepcopy(token_o['rendered_player_stack']))
 return r

class Tests(unittest.TestCase):
 def reject(self,r,fn=None):
  with self.assertRaises((ValueError,KeyError,StopIteration)):
   (fn or V.verify_queued_spaces)(r)
 def test_01_real_failed_first_jump_component_preserves_failed_full_report(self):
  before=pin(REAL);r=C.read(REAL);proof=V.verify_queued_spaces(r,require_enqueue_binding=False)
  self.assertFalse(r['passed']);self.assertEqual(proof['witnesses'][0]['post_enqueue_ground_callbacks'],1)
  self.assertFalse(proof['witnesses'][0]['enqueue_binding_observed'])
  self.assertTrue(proof['witnesses'][0]['physics']['diagnostic_matched']);self.assertFalse(proof['native_PASS_claimed'])
  with self.assertRaises(ValueError):V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=-1,diagnostic_clear_knight=True))
  self.assertEqual(before,pin(REAL));write(RUN/'actual-failed-v001-first-jump-component.json',dict(report=before,proof=proof,original_passed=False,full_native_rejected=True,UE_started=False,View=False))
 def test_02_missing_old_enqueue_binding_not_accepted_as_full_native(self):
  self.reject(C.read(REAL))
 def test_03_three_unique_queued_components_and_full_fixed_flow_both_sides(self):
  for side in (-1,1):
   r=full_fixture(side);proof=V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=side,diagnostic_clear_knight=False))
   self.assertEqual(proof['actual6pose_masks'],[63,63,63]);self.assertEqual(len(proof['queued_input_causality']['witnesses']),3)
   self.assertTrue(proof['completed_LGT_Ready_handoff']['exact_token_observation_equal'])
 def test_04_no_input_and_duplicate_and_reused_ordinal_rejected(self):
  for change in (lambda r:r['normal_inputs'].pop(4),lambda r:r['normal_inputs'].append(copy.deepcopy(r['normal_inputs'][4])),
   lambda r:r['normal_inputs'][8].update(space_enqueue_observer_ordinal=1)):
   r=full_fixture();change(r);self.reject(r)
 def test_05_air_before_enqueue_and_same_wall_or_sim_rejected(self):
  for change in (lambda r:r['normal_inputs'][4].update(wall_offset_s=.15),lambda r:r['normal_inputs'][4].update(wall_offset_s=r['observations'][2]['wall_offset_s']),
   lambda r:r['normal_inputs'][4].update(sim=.135),lambda r:r['observations'][1].update(sim=.125)):
   r=full_fixture();change(r);self.reject(r)
 def test_06_wrong_input_owner_room_epoch_run_and_gear_rejected(self):
  for k,v in (('owner','2'),('current_room','2'),('epoch','1'),('run','b'*32),('player_entity','2'),('weapon_version','99'),('armor_instance','99')):
   r=full_fixture();r['normal_inputs'][8][k]=v;self.reject(r)
 def test_07_wrong_callback_owner_time_ordinal_and_borrowed_jump_rejected(self):
  for change in (lambda r:r['observations'][2].update(owner='2'),lambda r:r['observations'][2].update(sim=.12),
   lambda r:r['observations'][2].update(observed_air_transition_ordinal=2),lambda r:r['observations'][1].update(jump_height=1,vertical_velocity=600)):
   r=full_fixture();change(r);self.reject(r)
 def test_08_immediate_physical_mutation_fake630_or_wrong_air0_range_rejected(self):
  for change in (lambda r:r['normal_inputs'][4].update(after_V=630),lambda r:r['normal_inputs'][4].update(after_H=1),
   lambda r:r['normal_inputs'][4].update(after_landing_age=0),lambda r:r['observations'][2].update(vertical_velocity=631),
   lambda r:r['observations'][2].update(vertical_velocity=315),lambda r:r['observations'][2].update(jump_height=0)):
   r=full_fixture();change(r);self.reject(r)
 def test_09_no_tolerance_base_partition_diagnostic_is_not_native_gate(self):
  r=full_fixture();r['observations'][2]['jump_height']=C.f32(r['observations'][2]['jump_height']+.001)
  proof=V.verify_queued_spaces(r);d=proof['witnesses'][0]['physics']
  self.assertFalse(d['diagnostic_matched']);self.assertFalse(d['required_for_native_PASS']);self.assertEqual(d['numeric_error_tolerance'],0)
  self.assertEqual(d['actual_native_substep_numeric_replay'],'OPEN_not_recorded')
 def test_10_callback_handoff_rejects_missing_unconsumed_fake_index_or_clock(self):
  for change in (lambda r:r.update(LGT_completed_Ready_callback_observed=False),lambda r:r.update(LGT_completed_Ready_callback_consumed_once=False),
   lambda r:r['LGT_completed_Ready_callback'].update(observation_index=1),lambda r:r['LGT_completed_Ready_callback'].update(callback_sim=.5),
   lambda r:r['LGT_completed_Ready_callback'].update(completed_native_screenshot_callback=False)):
   r=full_fixture();change(r);self.reject(r,V.verify_completed_light_ready)
 def test_11_callback_handoff_rejects_placeholder_bad_facing_binding_stale_draw(self):
  for change in (lambda r:r['LGT_completed_Ready_callback']['old_draw'].update(gear_placeholder=True),
   lambda r:r['LGT_completed_Ready_callback'].update(facing=-1),lambda r:r['LGT_completed_Ready_callback'].update(armor_version='99'),
   lambda r:r['LGT_completed_Ready_callback'].update(draw_id='1'),lambda r:r['normal_inputs'][8].update(armor_version='99')):
   r=full_fixture();change(r);self.reject(r,V.verify_completed_light_ready)
 def test_12_complete_flow_original_masks_landing_ready_HP_UI_gates_preserved(self):
  for change in (lambda r:r.update(light_second_mask=31),lambda r:r['normal_inputs'][-2].update(before_landing_age=C.f32(.12)),
   lambda r:r['observations'][-1]['old_draw'].update(draw_id=r['observations'][-2]['old_draw']['draw_id']),
   lambda r:r['observations'][3].update(hp=99),lambda r:r['observations'][3].update(interface_visible=True)):
   r=full_fixture();change(r)
   self.reject(r,lambda z:V.verify_flow(z,MANIFEST,PROFILE,dict(requested_facing=1,diagnostic_clear_knight=False)))
 def test_13_contract_byte_identical_and_unmodified_functions_AST_equal(self):
  self.assertEqual((HERE/'air_production_contract_v001.py').read_bytes(),(OLD/'air_production_contract_v001.py').read_bytes())
  old=ast.parse((OLD/'verify-Air-production-native-v001.py').read_text());new=ast.parse((HERE/'verify-Air-production-native-v001.py').read_text())
  names=('verify_png_fifo','optical_witnesses','fixed_optical_gate','verify_native','paircheck')
  for name in names:
   a=next(x for x in old.body if isinstance(x,ast.FunctionDef) and x.name==name);b=next(x for x in new.body if isinstance(x,ast.FunctionDef) and x.name==name)
   self.assertEqual(ast.dump(a,include_attributes=False),ast.dump(b,include_attributes=False))
 def test_14_grounded_budget_transition_must_match_actual_physical_transition(self):
  for change in (lambda r:r['observations'][0].update(melee_grounded=False),lambda r:r['observations'][1].update(wa_grounded=False),
   lambda r:r['observations'][2].update(melee_grounded=True),lambda r:r['observations'][2].update(wa_grounded=True)):
   r=full_fixture();change(r);self.reject(r)
 def test_15_exact_source_delta_passes_and_unrelated_writes_or_gate_edits_fail(self):
  a=C.module(HERE/'audit-Air-callback-ready-source-v003.py','new_source_delta_audit')
  proof=a.audit();self.assertTrue(proof['exact_restore_to_old_source'])
  old=Path(proof['old_source_cpp']['path']).read_text();new=Path(proof['new_source_cpp']['path']).read_text()
  for changed in (new.replace('Now-Start<12.&&Now-PhaseAt<5.','Now-Start<60.&&Now-PhaseAt<5.'),
   new.replace('NoArmorMask==63','NoArmorMask==31'),new.replace('  if(Stopped)return;const double Now=', '  P->JumpHeight=0.f;\n  if(Stopped)return;const double Now=')):
   self.assertNotEqual(a.restore_cpp_to_baseline(changed,old),old)
 def test_16_exact_checker_delta_rejects_pixel_threshold_and_mask_edits(self):
  a=C.module(HERE/'audit-Air-callback-ready-source-v003.py','new_checker_delta_audit')
  old=(OLD/'verify-Air-production-native-v001.py').read_text();new=(HERE/'verify-Air-production-native-v001.py').read_text()
  for changed in (new.replace('bc >= 150','bc >= 149'),new.replace('masks == [63, 63, 63]','masks == [31, 63, 63]')):
   with self.assertRaises(ValueError):a.checker_delta(old,changed)
 def test_17_nonfinite_raw_input_and_nonbool_edge_rejected(self):
  for change in (lambda r:r['normal_inputs'][4].update(after_V=float('nan')),lambda r:r['normal_inputs'][4].update(down=1),
   lambda r:r['observations'][2].update(wall_offset_s=float('nan'))):
   r=full_fixture();change(r);self.reject(r)

if __name__=='__main__':
 RUN.mkdir(parents=True,exist_ok=False)
 before=[pin(HERE/'verify-Air-production-native-v001.py'),pin(HERE/'air_production_contract_v001.py'),pin(__file__),pin(REAL)]
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 after=[pin(HERE/'verify-Air-production-native-v001.py'),pin(HERE/'air_production_contract_v001.py'),pin(__file__),pin(REAL)]
 payload=dict(schema='hero-Air6-queued-input-host-tests-v003',synthetic_value_tests=True,real_failed_report_component_only=True,
  tests_run=result.testsRun,failed=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful() and before==after,
  source_before=before,source_after=after,source_unchanged=before==after,UE_started=False,native_game_run=False,View=False,
  fixed_original_geometry_pixel_audio_gates_unchanged=True,actual_substep_trace='OPEN_not_recorded',FinalAccepted=False)
 write(RUN/'host-tests-result.json',payload)
 print(json.dumps(dict(result=pin(RUN/'host-tests-result.json'),passed=payload['passed']),ensure_ascii=False))
 raise SystemExit(0 if payload['passed'] else 1)
