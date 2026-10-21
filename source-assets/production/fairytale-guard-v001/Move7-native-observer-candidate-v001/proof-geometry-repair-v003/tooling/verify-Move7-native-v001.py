"""Readonly original Guard movement/event/derived seven-part native proof."""
import argparse,json,math,numbers,runpy,struct,subprocess,sys
from move7_native_contract_v001 import *
def near(a,b,tol=1e-8):return isinstance(a,numbers.Real)and not isinstance(a,bool)and isinstance(b,numbers.Real)and not isinstance(b,bool)and math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol
def point(a,b,tol=1e-8):return len(a)==len(b)==2 and all(near(x,y,tol)for x,y in zip(a,b))
def f32(v):return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def float_near(a,b):
 if not near(a,b,float('inf')):return False
 u=struct.unpack('<I',struct.pack('<f',abs(b)))[0];nextv=struct.unpack('<f',struct.pack('<I',u+1))[0]
 return abs(a-b)<=max(1e-6,4*(nextv-abs(b)))
def quad_equal(a,b):return a==b
def straight_move(q,player,guard,side):
 return q['facing']==side and(q['to'][0]-q['from'][0])*side>0 and q['to'][1]==q['from'][1]and(player[0]-guard[0])*side>=80
def legacy_rows():
 fixed=read(C/'read-only-input-pins-v001.json')['inputs'];old=read(pin(fixed['old_known44_source_profile']));extension=read(pin(fixed['old_Stomp50_row_approval']))
 need(extension['schema']=='Stomp50-Root-overlay-rows-v001'and extension['RootApproved']is True and extension['base_known_unique']==44 and extension['new_unique']==6 and extension['overlay_unique']==50 and extension['FinalAccepted']is False,'Old exact44+Stomp6 source authority changed')
 rows={x['clip']:x for x in old['profile_facts']}
 for row in extension['rows']:rows[row['clip']]=row
 unique={f['object_path']for row in rows.values()for f in row['frames']};need(len(unique)==50 and 'Move'not in rows,'Old50 raster rows must remain distinct from derived Move7')
 return rows
def verify_full_source(o,rows):
 d=o['full_draw'];clip=d.get('clip');row=rows[clip];need(row['trial_allowed']is True and row['final_accepted']is False and row['source_pose_approved']is True,'Old raster row trial gate changed')
 alias=row.get('alias');asset=rows[alias]if alias else row;frame=row['alias_frame']if alias else d['frame'];need(type(frame)is int and 0<=frame<len(asset['frames']),'Actual legacy frame outside row');source=asset['frames'][frame];pin(source['source'])
 need(d['texture']==source['object_path']and d['source_SHA']==source['source']['sha256']and d['source_RGBA_SHA']==source['RGBA_sha256']and d['native_source_id']==asset['native_source_id']and d['profile_id']=='GuardStomp50V004','Actual legacy source50 path/native/source owner changed')
 scale=asset['target_standing_body_height_px']/asset['standing_body_extent_px'];pivot=source['floor_pivot_source_px'];side=d['facing'];raw=[640+(o['guard_ground'][0]-o['camera_ground'][0])*f32(.65),490-o['guard_ground'][1]*f32(.38)];ground=[f32(x)for x in raw];top=[f32(raw[0]-(pivot[0]if side>0 else 512-pivot[0])*scale),f32(raw[1]-pivot[1]*scale)]
 need(all(float_near(a,b)for a,b in zip(d['ground_screen'],ground))and all(float_near(a,b)for a,b in zip(d['top'],top))and d['size']==[f32(512*scale)]*2 and d['uv']==([0,0]if side>0 else[1,0])and d['uv_size']==[side,1]and d['pivot']==[0,0]and d['rotation']==0 and d['draw_scale']==1 and d['scale_position']is False,'Actual old row source floor/scale/one mirror quad changed')
def resources(rows,profile,startup=False):
 need(len(rows)==len({x['component']for x in rows})==7,'Complete unique seven GPU resources required');by={x['component']:x for x in rows}
 for i,s in enumerate(profile['source7']):
  x=by[i];need(x['texture']==s['texture_object_path']and x['source_SHA']==s['source']['sha256']and x['source_RGBA_SHA']==s['RGBA_sha256']and x['class']=='Texture2D'and x['width']==x['height']==512 and x['resource_ready']is True and x['pending_initialization']is False,'Actual seven resource/source owner differs')
  if startup:need(x['source_native_batch_id']==s['source_native_batch_id'],'Component batch provenance differs')
def verify_rig(o,r,profile,solver,event,total):
 q=o['move_query'];d=o['rig_draw'];need(o['move_query_ok']and q['valid']and not q['block_known']and d['drawn'],'Only completed actual movement may render Move7')
 need(q['entity']==q['path_owner']==r['guard_entity']and q['run']==r['run']and q['room']==r['room']and q['epoch']==r['epoch']and q['content']=='ENM-STN-003','Actual Guard/run/room/epoch/path owner differs')
 need(q['sample_time']==q['movement_at']==o['sim']==o['guard_time']==event['at']and event['entity']==r['guard_entity']and event['kind']==7 and q['movement_event']==event['event'],'Stale/mismatched completed Movement witness')
 need(q['from']==event['from']and q['to']==event['to']and q['ground']==o['guard_ground']and point(q['to'],q['ground'],f32(1e-4))and near(q['current_accepted'],math.dist(event['from'],event['to']))and q['current_accepted']>0 and near(q['accepted_distance'],total),'Native accepted path history differs')
 delta=[event['to'][i]-event['from'][i]for i in range(2)];length=math.hypot(*delta);need(point(q['direction'],[v/length for v in delta],1e-12),'Actual movement direction differs')
 need(q['native_selection_valid']is True and q['native_selection_phase']==o['guard_phase']==2 and q['native_selection_clip']=='Move'and q['native_selection_event']==event['event']and q['native_selection_time']==q['sample_time']and q['native_selection_distance']==q['accepted_distance'],'Native full selector disagrees with query')
 need(d['sample']==q and d['entity']==r['guard_entity']and d['opt_in']and d['trial_allowed']and not d['final_accepted']and d['registration_ready']and d['texture_ready']and not d['procedural_fallback']and d['body_includes_axe']and d['plan_body_includes_axe']and d['plan_valid']and d['rig_valid']and d['required_resources']==7 and d['independent_axe_layers']==0 and d['type']=='GuardMoveSevenComponentRigDerived'and not d['missing'],'Actual renderer SAME plan/atomic7/type/wholeaxe differs')
 need(not o['full_draw'].get('drawn',False),'Old wholebody duplicated the derived seven-part Move')
 need(d['facing']==q['facing']==o['guard_facing']and d['accepted_distance']==q['accepted_distance']and d['profile_id']==PROFILE_ID and d['profile_sha256']==PROFILE_SHA and d['source_snapshot_sha256']==SNAPSHOT_SHA,'Rig identity/facing/actual-distance binding differs');resources(d['resident_textures'],profile)
 # Actual HUD Ground() uses float constants; Screen() accepts float X/Y.
 ground=[f32(640+(o['guard_ground'][0]-o['camera_ground'][0])*f32(.65)),f32(490-o['guard_ground'][1]*f32(.38))]
 expected=solver.solve(dict(owner_entity_id=int(r['guard_entity']),accepted_path_owner_entity_id=int(r['guard_entity']),accepted_distance_world=q['accepted_distance'],actual_facing=q['facing'],screen_ground_px=ground,ui_scale=1,source_snapshot_sha256=SNAPSHOT_SHA,profile_sha256=PROFILE_SHA,atomic_texture_ready_paths=[x['texture_object_path']for x in profile['source7']]))
 need(expected['valid_reference_plan'],'Independent frozen source solver rejected real sample: '+str(expected['rejection']))
 need(d['reflection_count']==expected['reflection_count']and d['half']==expected['half']and d['cycle_position']==expected['cycle_position']and near(d['u'],expected['u'],1e-12)and near(d['body_rise'],expected['bob_up_display'],1e-9),'Actual distance/half/u/bob/mirror differs')
 need(len(d['planned_parts'])==len(d['submitted_parts'])==7 and [x['component']for x in d['submitted_parts']]==ORDER,'Actual seven layer order differs')
 for planned,actual,want in zip(d['planned_parts'],d['submitted_parts'],expected['parts']):
  c=PARTS.index(want['part']);src=profile['source7'][c];need(planned['component']==actual['component']==c and actual['submitted']and actual['texture']==planned['texture']==want['texture_object_path']and actual['source_SHA']==planned['source_SHA']==src['source']['sha256']and actual['source_RGBA_SHA']==planned['source_RGBA_SHA']==src['RGBA_sha256']and actual['source_native_batch_id']==planned['source_native_batch_id']==src['source_native_batch_id'],'Submitted source component/batch owner differs')
  need(quad_equal(planned['quad'],actual['quad']),'Renderer did not submit SAME planned float arguments')
  need(point(planned['source_pivot'],want['source_pivot_px'],0)and planned['component_scale']==want['component_to_rest_scale']and near(planned['source_rotation_radians'],want['source_rotation_radians'],1e-9)and point(planned['art_anchor_from_ground'],want['art_anchor_from_source_ground'],1e-8)and point(planned['screen_anchor'],want['screen_anchor'],1e-8),'Original surface/own-hip IK geometry differs')
  a=actual['quad'];b=want['DrawTexture_float32_trace']
  for key,wk in [('top','Top'),('size','Size')]:need(all(float_near(x,y)for x,y in zip(a[key],b[wk])),'Actual float quad '+key+' differs from frozen independent solver')
  need(a['uv']==b['UV']and a['uv_size']==b['UVSize']and a['pivot']==b['RotationPivotUV']and float_near(a['rotation'],b['RotationDegrees'])and a['draw_scale']==1 and a['scale_position']is False and a['tint']==[1,1,1,1],'One reflection/rotation/UV/white tint submission differs')
 return d
def verify(archive,p,profile,trial,prereg):
 r=read(archive/'原件/runtime-report.json');index=read(archive/'index.json');need(r['schema']=='guard-Move7-native-observer-v001'and r['scenario']=='NormalWASDLeadActualGuardMove128CombatReady'and r['passed']is True and r['flow_complete']is True,'Actual original Move7 native trial failed')
 need(index['schema']=='guard-Move7-native-session-v001'and index['process_id']==int(r['process_id'])and index['exit_code']==0 and index['native_reported_passed']is True and index['snapshot_manifest_sha256']==p['compiled_manifest_pin']['sha256']and path(index['root_prereg'])==prereg and index['root_prereg_sha256']==fact(prereg)['sha256']and index['candidate_freeze_sha256']==p['candidate_freeze_pin']['sha256'],'Native session/PID/CM/prereg differs')
 need(index['tool_contract_fix_freeze_sha256']==p['tool_contract_fix_freeze_pin']['sha256']and index['tool_contract_fix_checker_sha256']==p['tool_contract_fix_checker_pin']['sha256'],'Native session derivative tool binding differs')
 need(index['proof_geometry_repair_freeze_sha256']==p['proof_geometry_repair_freeze_pin']['sha256']and index['proof_geometry_repair_checker_sha256']==p['proof_geometry_repair_checker_pin']['sha256'],'Native session supplemental numerical type repair binding differs')
 side=p['approach_side'];need(r['requested_approach_side']==r['actual_approach_side']==index['requested_approach_side']==side and r['restart_serial']=='1','Normal startup/real requested side differs')
 for k in ['player_or_Guard_public_damage_used','HP_poise_clock_actor_writes','AI_toggle_used','historical_Sweep_requeried','wallclock_gait_used','raster_Move6_frames_claimed','Guard_Hurt_Stun_native_covered','audio_recorded','visual_reviewed']:need(r[k]is False,'Trial scope changed: '+k)
 need(r['silent_video']is True and r['formal_complete_units']==0 and r['guard_final_HP']==185 and r['guard_incoming_count']==0,'Living Guard185/no incoming/silent limited trial differs')
 diag=r['diagnostic_predecessor_hits'];need(len(diag)==2 and [x['content']for x in diag]==['ENM-STN-001','ENM-STN-002']and all(x['api']=='ADungeonFighter::ApplyCombatHit'and x['before_HP']>x['after_HP']==0 and x['dead']is True for x in diag),'Only Knight/Bat diagnostics allowed')
 downs=[x['key']for x in r['normal_inputs']if x['down']];need(downs.count('Enter')==downs.count('E')==1 and set(downs)<=set(['Enter','E','A','D','W','S'])and set(downs)&{'A','D'}and set(downs)&{'W','S'},'Normal Enter/E/WASD only; no J/private input')
 reached=[x for x in r['route_witnesses']if x['event']=='reached'and x['stage']==2];need(len(reached)==1 and 120<=(reached[0]['player'][0]-reached[0]['guard'][0])*side<=160 and abs(reached[0]['player'][1]-reached[0]['guard'][1])<=6,'Facing-only false spatial approach')
 slots=r['actual_formal_room_slots'];need(len(slots)==3 and [x['content']for x in slots]==['ENM-STN-001','ENM-STN-002','ENM-STN-003']and slots[2]['entity']==r['guard_entity']and slots[2]['stage']==2 and slots[2]['spawn']==r['guard_initial_position'],'Guard must belong to original planned formal slot')
 for previous,current in zip(slots,slots[1:]):need(previous['stage']==3 and current['warning_at']>=previous['dead_at']+2 and current['materialized_at']>=current['warning_at']+1.2,'Original warning/materialization deadlines shortened')
 resources(r['startup_resident_textures'],profile,True)
 fixed=read(C/'read-only-input-pins-v001.json')['inputs'];solver=runpy.run_path(str(pin(fixed['host_solver'])))['ReferenceSolver'](pin(fixed['prepared_profile']),PROFILE_SHA)
 events=r['guard_original_events'];need([int(x['event'])for x in events]==list(range(1,len(events)+1)),'Original issued event sequence not closed');by={x['event']:x for x in events};totals={};total=0.;prev=r['guard_initial_position'];feet=[]
 for e in events:
  if e['kind']!=7:continue
  need(e['entity']==r['guard_entity']and(prev is None or e['from']==prev),'Movement path broke continuity');prev=e['to'];length=math.dist(e['from'],e['to']);before=total;total+=length;totals[e['event']]=total
  if length:
   for ordinal in range(math.floor(before/64)+1,math.floor(total/64)+1):
    a=max(0,min(1,(ordinal*64-before)/length));feet.append(dict(event=e['event'],foot_ordinal=str(ordinal),at=e['at'],position=[e['from'][k]+(e['to'][k]-e['from'][k])*a for k in range(2)]))
 actualfeet=[x for x in r['guard_feedback']if x['cue']=='GUARD_STEP_01'];need(len(feet)==len(actualfeet),'64 accepted-distance footstep count differs')
 for a,b in zip(feet,actualfeet):need(a['event']==b['event']and a['foot_ordinal']==b['foot_ordinal']and a['at']==b['at']and point(a['position'],b['position'])and b['source_kind']==7,'Actual footstep event/ordinal/interpolated point differs')
 oldrows=legacy_rows();obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>6 and all(b>a for a,b in zip(offsets,offsets[1:]))and not r['capture_timing']['use_fixed_time_step'],'Native callback timing differs');qual=[];seen=set();mask=0;last_event=-1;draws=set()
 for i,(o,t)in enumerate(zip(obs,offsets)):
  need(o['wall_offset_s']==t and not o['interface_visible']and o['text_calls']==0 and not o['range_debug']and o['range_lines']==0,'UI/default ranges visible or offset differs')
  if 'guard_time'not in o:continue
  need(o['guard_time']==o['sim']and o['guard_HP']==185 and o['guard_incoming_count']==0,'Actual Guard clock/HP changed')
  if o['full_draw'].get('drawn',False):verify_full_source(o,oldrows)
  if o['phase']>=7:need(o['weapon_instance']==r['sword_instance']and o['armor_instance']==r['light_instance']and o['weapon_version']==r['sword_version']and o['armor_version']==r['light_version'],'Committed equipment changed')
  if not o['move_query_ok']:need(not o['rig_draw'].get('drawn',False),'Stale movement rendered');continue
  q=o['move_query'];d=verify_rig(o,r,profile,solver,by[q['movement_event']],totals[q['movement_event']]);need(path(d['trial_record'])==pin(p['runtime_trial_approval_pin']),'Actual renderer consumed another Root runtime registration')
  if o['phase']==8 and straight_move(q,o['player_ground'],o['guard_ground'],side)and int(q['movement_event'])>last_event and d['draw_id']not in draws:
   last_event=int(q['movement_event']);draws.add(d['draw_id']);mask|=1<<int(d['cycle_position']/(128/6));qual.append(o);seen.add(q['movement_event'])
 need(qual and mask==r['distance_window_mask']==63 and len(qual)==r['move_draws']and qual[0]['move_query']['accepted_distance']==r['first_distance']and qual[-1]['move_query']['accepted_distance']==r['last_distance']and r['last_distance']-r['first_distance']>=128 and qual[0]['sim']==r['first_move_time']and qual[-1]['sim']==r['last_move_time'],'One fresh straight-X128 cycle with all six distance windows required')
 battle=r['battle_original_envelope'];aid=r['battle_attack'];need(aid==battle['attack_id']and battle['start']>=r['last_move_time']and battle['kind']in[1,2]and not battle['interrupted'],'First natural postcycle action differs')
 attacks=[e for e in events if e['kind']==2 and e['at']>=r['last_move_time']];need(attacks and attacks[0]['action']['attack_id']==aid,'Later cycle cannot replace first original combat cycle')
 edges=[];ready=[]
 for i,o in enumerate(obs):
  if o['phase']!=9:continue
  b=o['full_draw'];a=o['guard_action'];need(o['player_HP']>0,'Hero died before original Ready')
  if a['attack_id']==aid:
   for k in ['kind','facing','start','lock_at','active_at','active_end','recovery_end','cooldown_end','damage','stagger','origin']:need(a[k]==battle[k],'Original combat envelope changed: '+k)
  if o['visual_kind']=='Ready'and b.get('drawn')and b['attack']==aid and a['completed_at']==battle['recovery_end']and battle['recovery_end']<=o['sim']<battle['recovery_end']+.3:
   need(b['ready']and b['quad_submitted']and not b['fallback']and b['sample_time']==o['sim']and o['guard_phase']==2 and not o['move_query_ok']and not any(o[k]for k in ['held_A','held_D','held_W','held_S']),'Actual stationary Ready quad/input boundary missing');ready.append(o)
  if not i:continue
  before=obs[i-1];x=before['full_draw']
  if before['visual_kind']=='Move7'and o['visual_kind']in['AxeWindup','StompWindup']and b['frame']==0 and b['attack']==aid:
   need(b['drawn']and b['quad_submitted']and b['ready']and not b['fallback']and b['interval_start']==battle['start']and b['interval_end']==battle['active_at'],'Original Windup0 submitted window differs');edges.append(dict(kind='Move7_to_native_Windup',from_observation=i-1,to_observation=i))
  if before['visual_kind']in['AxeRecovery','StompRecovery']and x['frame']==3 and x['attack']==aid and x['interval_end']==battle['recovery_end']and o in ready:
   need(before['sim']<battle['recovery_end']<=o['sim']and x['drawn']and x['quad_submitted'],'Original adjacent Recovery3→Ready boundary differs');edges.append(dict(kind='native_Recovery_to_Ready_stop',from_observation=i-1,to_observation=i))
 need(len(ready)==r['ready_seen']>=3 and len({x['full_draw']['draw_id']for x in ready})==len(ready)and [e['kind']for e in edges]==['Move7_to_native_Windup','native_Recovery_to_Ready_stop']and edges==r['actual_adjacent_joins']and r['MoveCombatJoin']and r['RecoveryReadyJoin'],'Exact original native joins/one Ready window missing')
 losses=[x for x in r['guard_feedback']if x['actual_HP_loss']>0];hits=[x for x in events if x['kind']==11];receipts=r['guard_original_hit_receipts'];need(len(losses)==len(hits)==len(receipts),'Outgoing original hit/confirmed loss/receipt closure differs');hp=r['pre_guard_HP']
 for loss,hit in zip(losses,hits):
  a=hit['action'];need(loss['event']==hit['event']and loss['target']==hit['target']==r['player_entity']and loss['attack']==a['attack_id']and loss['at']==hit['at']and a['active_at']<=loss['at']<a['active_end']and sum(x['attack']==loss['attack']and x['target']==loss['target']and x['at']==loss['at']for x in receipts)==1,'Actual locked contact/receipt differs');need(near(loss['actual_HP_loss'],min(hp,a['damage']/1.14),1e-4),'Actual single Armor14 mitigation differs');hp=max(0,hp-loss['actual_HP_loss'])
 need(near(obs[-1]['player_HP'],hp,1e-4),'Final hero HP differs from real Guard receipts')
 subprocess.run([sys.executable,'-B','-X','utf8',str(D/'tooling/verify-Move7-native-pixels-v001.py'),'--archive',str(archive)],check=True,capture_output=True,text=True)
 optical=runpy.run_path(str(D/'tooling/verify-Move7-source-pixels-v001.py'))['verify_source_pixels'](archive,profile,qual)
 return dict(proof_geometry_repair_freeze_pin=p['proof_geometry_repair_freeze_pin'],proof_geometry_repair_checker_pin=p['proof_geometry_repair_checker_pin'],tool_contract_fix_freeze_pin=p['tool_contract_fix_freeze_pin'],tool_contract_fix_checker_pin=p['tool_contract_fix_checker_pin'],schema='guard-Move7-independent-native-v001',passed=True,process_id=int(r['process_id']),native_report_pin=fact(archive/'原件/runtime-report.json'),actual_facing=side,accepted_cycle_distance=r['last_distance']-r['first_distance'],six_distance_window_mask=mask,unique_Move_draws=len(qual),original_combat_attack_id=aid,actual_adjacent_joins=edges,actual_guard_confirmed_hits=len(losses),actual64distance_footsteps=len(feet),complete7GPU_and_submitted_floatquads=True,original_clock_and_source_projection=True,native_PNG_CRC_FIFO_verified=True,optical_source_projection=optical,Hurt_Stun_native_covered=False,historical_block_cause_verified=False,footlock=False,audio_recorded=False,visual_reviewed=False,FinalAccepted=False)
def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--root-prereg',required=True);a.add_argument('--archive');a.add_argument('--source-only',action='store_true');a.add_argument('--write-receipt',action='store_true');q=a.parse_args();prereg=path(q.root_prereg);m,p,profile,_,trial=preflight(path(q.snapshot),prereg)
 if q.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=200,production_files=1371,source_files=m['source_files'],Move7_sources=7,approach_side=p['approach_side'],UE_started=False)));return
 need(q.archive,'Actual native archive required');archive=path(q.archive);result=verify(archive,p,profile,trial,prereg)
 if q.write_receipt:
  with(archive/'原件/Move7-independent-native-verification-v001.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
