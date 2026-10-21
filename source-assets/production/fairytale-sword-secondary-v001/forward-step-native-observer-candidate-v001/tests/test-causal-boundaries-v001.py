"""Host model tests only: no native assets, audio, frames, or production claims."""
from pathlib import Path
import importlib.util,json,copy,sys
C=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('swdcheck',C/'check-swd-forward-step-native-v001.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def fixture(face=1,kind='full'):
 a=dict(action_id='5',instance_id='11',type=2,weapon=0,phase=1,active=True,locked=False,started_airborne=False,forward_step_issued=False,next_subhit=0,facing=face,start=2.,lock_at=2.08,active_at=2.20,active_end=2.30,end=2.68,sample_time=2.,terminal=0,speed_pct=0,cooldown_duration=0)
 locked=copy.deepcopy(a);locked.update(locked=True,cooldown_duration=4,sample_time=2.11)
 distance=30 if kind=='full' else 12
 f=dict(sequence='1',cue=m.CUE,at_time=2.2,run='ab'*16,room='3',owner='9',action_id='5',instance_id='11',operation_id='0',revision='20',forward_step=dict(present=True,event_id='13',subhit_id='0',requested_signed_distance=face*30.,before=[0.,0.],after=[face*distance,0.],committed_delta=[face*distance,0.]),first_seen_callback=6,first_seen_wall_min_s=.4,first_seen_wall_max_s=.425,observed_sim=2.225)
 q=dict(source={k:copy.deepcopy(f[k]) for k in m.PARENT},sound_path=m.SOUND,requested_at=2.225,volume=.25,pitch=1.,first_seen_callback=6,first_seen_wall_min_s=.4,first_seen_wall_max_s=.425)
 r=dict(schema='swd-forward-step-native-observer-v001',case=kind+('_right' if face>0 else '_left'),passed=True,failure='',flow_complete=True,player_enemy_HP_position_AI_clock_writes=False,enemy_diagnostic_used=False,formal_accepted=False,audio_listened=False,device_onset_measured=False,run='ab'*16,room='3',owner='9',epoch='1',restart='0',weapon_instance='11',weapon_version='1',weapon_version_end='2',armor_instance='7',requested_facing=face,accepted_action=a,locked_action_source=locked,secondary_frame_mask=255,ready_before_frames=3,ready_after_frames=2,normal_inputs=[dict(key=x,down=True) for x in ['Enter','E','D' if face>0 else 'A','K']],action_audio=dict(schema='swd-forward-step-action-audio-observation-v001',scope_changes=0,fact_sequence_gaps=0,request_only=True,source_epoch_available=False,device_onset_measured=False,facts=[f],requests=[q]))
 bounds=[2.,2.08,2.14,2.20,2.25,2.30,2.42,2.55,2.68];times=[1.82,1.85,1.88]+[(x+y)/2 for x,y in zip(bounds,bounds[1:])]+[2.70,2.73];rows=[]
 for i,t in enumerate(times):
  k=3<=i<11;x=copy.deepcopy(a);x.update(active=k,locked=t>=2.08,phase=1,sample_time=t,cooldown_duration=4 if t>=2.08 else 0)
  if k:
   paths=['/res/'+str(j) for j in range(8)];d=dict(draw_id=str(i),player_entity_id='9',opt_in=True,owns_branch=True,profile_ready=True,atomic_preflight_ready=True,drawn=True,missing_reason='',binding=dict(run=r['run'],owner='9',weapon_instance='11',weapon_version='1',weapon_version_end='2',armor_instance='7'),sample=dict(action=copy.deepcopy(x),frame=i-3,boundaries=bounds),expected_draw_count=8,slots=[dict(slot=j,selected=True,texture_ready=True,drawn=True,texture=p) for j,p in enumerate(paths)],actual_stack=paths,residents=[dict(texture='/res/'+str(j),ready=True,pending_initialization=False,**{'class':'Texture2D'},width=512,height=512) for j in range(57)])
  else:d=dict(drawn=False)
  if k:d['binding']['weapon_version']='2' if t>=2.08 else '1'
  update=dict(receipt_id='1',instance_id='11',before_version='1',after_version='2',base_revision='19',at_time=2.08,before_ammo=0,ammo=0,before_cooldown=0,cooldown_deadline=6.08,ok=True,replayed=False)
  rows.append(dict(runtime_inventory=dict(available=True,runtime_updates=[update] if t>=2.08 else []),callback_index=i,wall_offset_s=t-1.8,sim=t,action=x,height=0,vertical_velocity=0,melee_grounded=True,weapon_grounded=True,secondary=d,common_draw=dict(clip='sword_secondary' if k else 'sword_ready_idle',supported=True,draw_id=str(i),actual_stack=d.get('actual_stack',[]))))
 r['observations']=rows;r['capture_timing']=dict(frame_wall_offsets_s=[o['wall_offset_s'] for o in rows]);return r
results=[]
def test(name,fn):
 try:fn();results.append(dict(name=name,passed=True))
 except Exception as e:results.append(dict(name=name,passed=False,reason=repr(e)))
def positive(face,kind):m.audit_causal(fixture(face,kind))
def reject(change,kind=ValueError):
 r=fixture();change(r)
 try:m.audit_causal(r)
 except kind:return
 raise AssertionError('counterexample was accepted')
for face in [1,-1]:
 for kind in ['full','partial']:test('model_'+kind+str(face),lambda f=face,k=kind:positive(f,k))
test('wrong_owner_parent',lambda:reject(lambda r:r['action_audio']['facts'][0].update(owner='8')))
test('stale_run_parent',lambda:reject(lambda r:r['action_audio']['facts'][0].update(run='cd'*16)))
test('wrong_instance',lambda:reject(lambda r:r['action_audio']['facts'][0].update(instance_id='12')))
test('DTO_present_false_not_zero',lambda:reject(lambda r:r['action_audio']['facts'][0]['forward_step'].update(present=False)))
test('DTO_after_not_actual_delta',lambda:reject(lambda r:r['action_audio']['facts'][0]['forward_step'].update(after=[9.,0.])))
test('requested_equals_committed_mistake',lambda:reject(lambda r:r['action_audio']['facts'][0]['forward_step'].update(requested_signed_distance=12.)))
test('wrong_subhit',lambda:reject(lambda r:r['action_audio']['facts'][0]['forward_step'].update(subhit_id='1')))
test('duplicate_fact',lambda:reject(lambda r:r['action_audio']['facts'].append(copy.deepcopy(r['action_audio']['facts'][0]))))
test('duplicate_HUD_request',lambda:reject(lambda r:r['action_audio']['requests'].append(copy.deepcopy(r['action_audio']['requests'][0]))))
test('wrong_sound',lambda:reject(lambda r:r['action_audio']['requests'][0].update(sound_path='/fake')))
test('wrong_gain',lambda:reject(lambda r:r['action_audio']['requests'][0].update(volume=.32)))
test('stale_HUD_age',lambda:reject(lambda r:r['action_audio']['requests'][0].update(requested_at=2.5)))
test('callback_before_source',lambda:reject(lambda r:r['action_audio']['requests'][0].update(first_seen_callback=5)))
test('HUD_DTO_not_source_copy',lambda:reject(lambda r:r['action_audio']['requests'][0]['source']['forward_step'].update(event_id='99')))
test('parent_time_not_active_deadline',lambda:reject(lambda r:r['action_audio']['facts'][0].update(at_time=2.21)))
test('gapped_source_log',lambda:reject(lambda r:r['action_audio'].update(fact_sequence_gaps=1)))
test('scope_changed',lambda:reject(lambda r:r['action_audio'].update(scope_changes=1)))
test('missing_K7',lambda:reject(lambda r:r['observations'][10]['secondary']['sample'].update(frame=6)))
test('trace_stale_instance',lambda:reject(lambda r:r['observations'][5]['secondary']['sample']['action'].update(instance_id='99')))
test('trace_not_same_draw',lambda:reject(lambda r:r['observations'][6]['common_draw'].update(draw_id='999')))
test('one_slot_not_drawn',lambda:reject(lambda r:r['observations'][6]['secondary']['slots'][3].update(drawn=False)))
test('one_resident_missing',lambda:reject(lambda r:r['observations'][6]['secondary']['residents'].pop()))
test('original_End_extended',lambda:reject(lambda r:r['accepted_action'].update(end=2.78)))
test('Ready_join_not_done',lambda:reject(lambda r:r.update(ready_after_frames=1)))
test('Space_input_injected',lambda:reject(lambda r:r['normal_inputs'].append(dict(key='SpaceBar',down=True))))
test('non_grounded_K',lambda:reject(lambda r:r['observations'][7].update(height=1)))
test('zero_false_positive',lambda:reject(lambda r:r.update(case='blocked_zero_right')))
def absent_zero(r):r.update(case='blocked_zero_right');r['action_audio'].update(facts=[],requests=[])
test('zero_without_independent_actual_witness_is_NotReady',lambda:reject(absent_zero,m.NotReady))
test('unreceipted_version_increment',lambda:reject(lambda r:r['observations'][6]['runtime_inventory']['runtime_updates'].clear()))
test('cooldown_deadline_delayed',lambda:reject(lambda r:r['observations'][6]['runtime_inventory']['runtime_updates'][0].update(cooldown_deadline=6.18)))
test('version_jump_not_one',lambda:reject(lambda r:r.update(weapon_version_end='3')))
test('source_wall_observation_not_callback',lambda:reject(lambda r:r['action_audio']['facts'][0].update(first_seen_wall_max_s=5.)))
result=dict(schema='swd-forward-step-host-model-tests-v001',passed=sum(x['passed'] for x in results),failed=sum(not x['passed'] for x in results),native_executed=False,UE_editor_compiled=False,models_are_not_native_proof=True,cases=results)
print(json.dumps(result,indent=2));sys.exit(bool(result['failed']))
