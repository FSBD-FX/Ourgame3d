"""Independent real-J StunIR receipt/clock/source proof; no UE launch or owner writes."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,subprocess,sys
C=Path(__file__).resolve().parent.parent;R=C.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def need(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def path(p):p=Path(p);return p if p.is_absolute() else R/p
def pin(p,x):need(p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Exact input pin differs: '+str(p))
def near(a,b,t=1.e-8):return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=t
def preflight(snapshot,profile,prereg):
 f=C/'StunIR-candidate-freeze-v003.json'
 for x in read(f)['files']:pin(C/x['path'],x)
 inp=read(C/'independent-profile-input-pins-v003.json')
 for x in inp.values():
  if isinstance(x,dict) and 'sha256' in x:pin(path(x['path']),x)
 module=runpy.run_path(str(path(inp['profile_source_checker']['path'])));m,facts,_=module['source_check'](snapshot,profile)
 p=read(prereg);protocol=read(C/'proof-protocol-v003.json')
 need(p['schema']==protocol['Root_prereg_schema'] and p['scenario']=='StunIR' and p['is_template'] is False and p['pre_registered_before_capture'] is True,'Actual independent StunIR Root prereg required')
 need(p['compiled_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json'),'Combat prereg bound another compiled snapshot')
 q=p['source_profile_prereg_pin'];pin(path(q['path']),q);need(path(q['path']).resolve()==profile.resolve(),'Combat/source-profile prereg differ')
 q=p['combat_candidate_freeze_pin'];pin(path(q['path']),q);need(path(q['path']).resolve()==f.resolve(),'Combat prereg bound another tool/source freeze')
 files={x['path']:x for x in m['files']};admitted={x['path']:x for x in p['admitted_combat_source_files']}
 required={'UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonGuardArtCombatProbeV003.h','DungeonGuardArtCombatProbeV003.cpp','DungeonHUD.cpp']}
 need(required==set(admitted) and len(admitted)==len(p['admitted_combat_source_files']),'Exact new actor/HUD admitted pins required')
 for n,x in admitted.items():need(files[n]==x,'Combat Source differs from actual compiled snapshot');pin(R/n,x)
 for n in ['DungeonGuardArtCombatProbeV003.h','DungeonGuardArtCombatProbeV003.cpp']:
  actual=(R/'UnrealGame/Source/CodexDungeon'/n).read_text(encoding='utf-8-sig');need(actual==(C/'new-source'/n).read_text(encoding='utf-8-sig'),'Compiled combat actor differs from this frozen source beyond line endings')
 need('SpawnActor<ADungeonGuardArtCombatProbeV003>()' in (R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_text(encoding='utf-8-sig'),'Independent combat startup missing')
 return m,facts,protocol
def spatial(o,d,r):
 s=d['Selection'];n=o.get('guard_native');side=r['actual_approach_side']
 if not n or o['phase']!='normal_guard_J_and_StunIR' or not o['approach_spatial']['route_reached'] or int(s['AttackId'])!=int(r['interrupted_attack_id']):return False
 dx=side*(o['player_ground'][0]-n['ground'][0]);dy=o['player_ground'][1]-n['ground'][1]
 if not 110<=dx<=155 or abs(dy)>20 or o['player_HP']<=0 or n['HP']<=0 or not n['interrupted']:return False
 if s['Clip']=='Stunned':return int(s['SourceEventId'])==int(r['break_event_id']) and n['phase']==6 and r['break_at']<=s['SampleTime']<r['stun_end']
 if s['Clip']=='InterruptedRecovery':return int(s['SourceEventId'])==0 and n['phase']==5 and r['stun_end']<=s['SampleTime']<r['original_occupied_until']
 return False
def verify(archive,facts,snapshot,prereg,protocol):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json');freeze=C/'StunIR-candidate-freeze-v003.json'
 need(index['schema']==protocol['session_schema'] and index['candidate_freeze_sha256']==sha(freeze) and index['snapshot_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json') and index['root_prereg_sha256']==sha(prereg),'Session does not bind real combat prereg/source/tooling')
 need(r['schema']==protocol['runtime_report_schema'] and r['scenario']=='StunIR' and r['passed'] is True and r['flow_complete'] is True and r['break_pinned'] is True,'Native independent StunIR RED/wrong schema')
 need(str(index['process_id'])==r['process_id'] and r['restart_serial']=='1' and int(r['owner'])>0 and r['actual_approach_side'] in [-1,1],'Fresh process/run/restart/side scope differs')
 need(r['guard_public_damage_used'] is False and r['guard_normal_J_only'] is True and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False and r['player_damage_preserved'] is True and r['normal_J_full_clear'] is False,'Actual normal-J/diagnostic scope differs')
 need(r['silent_video'] is True and r['audio_recorded'] is False and r['visual_reviewed'] is False and r['formal_complete_units']==0,'Acceptance/audio scope differs')
 diag=r['diagnostic_public_hits'];need(len(diag)==2 and [x['content_id'] for x in diag]==['ENM-STN-001','ENM-STN-002'] and all(x['dead'] and x['after_HP']==0 and x['api']=='ADungeonFighter::ApplyCombatHit' for x in diag),'Only predecessor diagnostic public clears allowed')
 gid=int(r['guard_entity']);aid=int(r['interrupted_attack_id']);bid=int(r['break_event_id']);events=r['guard_original_issued_events'];ids=[int(x['EventId']) for x in events]
 need(ids==sorted(set(ids)) and all(int(x['EntityId'])==gid and x['Kind'] not in [12,13] for x in events),'Guard event identities/true nonlethal scope differ')
 bs=[x for x in events if x['Kind']==9];need(len(bs)==1 and int(bs[0]['EventId'])==bid,'Exactly one actual PoiseBroken required');b=bs[0]
 need(b['AtTime']==r['break_at'] and b['EndTime']==r['stun_end'] and near(b['EndTime'],b['AtTime']+.4),'Original400ms stun changed')
 starts=[x for x in events if x['Kind']==2 and int(x['AttackId'])==aid];ints=[x for x in events if x['Kind']==10 and int(x['AttackId'])==aid and x['AtTime']==b['AtTime']]
 need(len(starts)==len(ints)==1 and starts[0]['Action']==r['original_interrupted_action'] and ints[0]['Action']==r['interrupted_action_at_break'],'Original attack/interrupt receipt differs')
 a=starts[0]['Action'];ia=ints[0]['Action'];end=r['original_occupied_until']
 need(ia['interrupted'] is True and ia['in_progress'] is False and a['recovery_end']==end and r['original_idle_ready_at']==end+.3 and end-r['stun_end']>=.4,'Original occupied/idle obligation changed or insufficient observable IR')
 for k in ['start','lock_at','active_at','active_end','recovery_end','cooldown_end']:need(a[k]==ia[k],'Interruption rewrote original deadline')
 rec=[x for x in events if x['Kind']==5 and int(x['AttackId'])==aid and x['AtTime']==r['stun_end']];done=[x for x in events if x['Kind']==6 and int(x['AttackId'])==aid]
 need(len(rec)==len(done)==1 and rec[0]['EndTime']==end and done[0]['AtTime']==end,'Original IR recovery/completion receipts missing')
 need(not any(int(x['AttackId'])==aid and x['Kind'] in [4,11] and x['AtTime']>=b['AtTime'] for x in events),'Interrupted original action reissued Active/Hit')
 closes=[x for x in r['guard_original_closures'] if int(x['AttackId'])==aid];wins=[x for x in r['guard_original_damage_windows'] if int(x['AttackId'])==aid]
 need((len(wins)==len(closes)==1 and closes[0]['AtTime']==b['AtTime']) if ia['window_issued'] else not wins and not closes,'Closure does not match actual previously issued window')
 incoming=r['guard_original_received_hits'];need(incoming and [int(x['ReceiptId']) for x in incoming]==list(range(1,len(incoming)+1)) and r['guard_incoming_receipt_count']==len(incoming),'Actual unique Guard resolved receipt sequence missing')
 hits=[x for x in r['player_original_hit_receipts'] if int(x['TargetId'])==gid];windows={int(x['AttackId']):x for x in r['player_original_issued_windows']}
 need(len(hits)==len(incoming) and len({(x['AttackId'],x['SubhitId'],x['TargetId']) for x in hits})==len(hits),'Normal J hit admission differs from Guard received hits')
 poise=0.;last=-1.;protection=0.;expected_breaks=[];hp=185.
 for hit,h in zip(hits,incoming):
  w=windows[int(hit['AttackId'])];pa=w['FrozenAction'];need(hit['SubhitId']==0 and pa['Weapon']==0 and int(pa['WeaponInstanceId'])==1 and pa['Locked'] is True and pa['WindowIssued'] is True and not pa['StartedAirborne'],'Guard damage is not actual grounded starter-SWD J')
  need(w['Start']<=h['AtTime']<w['End'] and near(h['Stagger'],pa['Stagger']) and near(h['ActualHPLoss'],min(hp,pa['Damage']*.625),1.e-5),'Actual J time/stagger/single armor mitigation differs')
  hp-=h['ActualHPLoss'];need(hp>0,'StunIR normal-J hit killed Guard')
  if h['AtTime']>=protection:
   if last>=0:poise=max(0.,poise-20.*max(0.,h['AtTime']-(last+1.)))
   poise+=h['Stagger'];last=h['AtTime']
   if poise>=85:expected_breaks.append(h['AtTime']);poise=0.;protection=h['AtTime']+1.
 need(expected_breaks==[b['AtTime']] and near(hp,r['guard_final_HP']),'Independent actual85 replay differs; no J-count shortcut')
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>2 and all(y>x for x,y in zip(offsets,offsets[1:])) and r['capture_timing']['use_fixed_time_step'] is False,'Actual callbacks/offsets/pacing differ')
 need(all(near(x['wall_offset_s'],t) and not x['interface_visible'] and x['text_calls']==0 for x,t in zip(obs,offsets)),'Hidden HUD/real callback offsets differ')
 hpseries=[x['player_HP'] for x in obs];need(all(0<x<=100 for x in hpseries) and all(y<=x for x,y in zip(hpseries,hpseries[1:])) and hpseries[-1]==r['player_final_HP'],'Real player damage was healed/ignored or player died')
 keys=[x['key'] for x in r['normal_input_requests'] if x['down']];need(keys.count('Enter')==keys.count('E')==1 and keys.count('J')>=len(hits) and set(keys)<={'Enter','E','J','A','D','W','S'},'Actual controller-only normal J/input sequence differs')
 need(any(x['hero_bound_skin'] and x['LGT_drawn'] for x in obs),'Real E committed LGT binding missing')
 loaded=r['startup_resident_textures'];expected={f['object_path']:(clip,row,f) for clip,row in facts.items() for f in row['frames']};need(len(loaded)==len(expected)==44 and {x['actual_object_path'] for x in loaded}==set(expected),'Exact approved44 residency absent')
 for x in loaded:
  _,row,f=expected[x['actual_object_path']];need(x['native_source_id']==row['native_source_id'] and x['actual_class']=='Texture2D' and x['actual_width']==x['actual_height']==512 and x['resource_resident'] is True and x['source_SHA256_metadata']==f['source']['sha256'] and x['source_RGBA_SHA256_metadata']==f['RGBA_sha256'],'Actual startup texture metadata differs')
 masks={'Stunned':0,'InterruptedRecovery':0};seen=set();coverage=[]
 for i,o in enumerate(obs):
  n=o.get('guard_native')
  if n:need(int(n['entity'])==gid and n['HP']>0 and not n['dead'],'Guard identity/nonlethal state differs')
  for d in o['guard_draws']:
   if int(d['EntityId'])!=gid:continue
   s=d['Selection'];clip=s['Clip'];frame=s['Frame'];stamp=s['SampleTime'];eligible=spatial(o,d,r)
   need(d['SpatialCoverageEligible']==eligible and s['Valid'] and not s['TerminalPresentation'],'Actual native selection/spatial qualification differs')
   if clip not in facts:need(clip in ['Move','StompActive','StompRecovery'] and not d['Drawn'] and d['ProceduralFallback'] and not d['DrawStack'] and bool(d['MissingReason']),'Gap concealed by unapproved sprite');continue
   asset='Wake' if clip=='Dormant' else clip;row=facts[asset];f=row['frames'][0 if clip=='Dormant' else frame]
   need(d['Drawn'] and d['TextureReady'] and d['RegistrationReady'] and d['TrialAllowed'] and d['FinalAccepted'] is False and not d['ProceduralFallback'],'Approved full known row was not really drawn')
   need(d['TexturePath']==f['object_path'] and d['SourceSHA256']==f['source']['sha256'] and d['SourceRGBASHA256']==f['RGBA_sha256'] and d['SourceFloorPivot']==f['floor_pivot_source_px'] and d['NativeSourceId']==row['native_source_id'],'Actual texture/source/RGBA/floor differs')
   need(d['TrialApprovalRecord']==row['trial_approval_record'] and d['RequestedTrialApprovalRecord']==facts[clip]['trial_approval_record'] and d['RegistrationEvidenceSHA256']==row['registration_evidence']['sha256'] and d['SourceIndexSHA256']==row['source_index']['sha256'],'Actual full trial registration differs')
   scale=100.8/row['standing_body_extent_px'];px,py=f['floor_pivot_source_px'];px=512-px if s['Facing']<0 else px
   need(d['WholebodyIncludesAxe'] and d['DrawStack']==[d['TexturePath']] and near(d['RowScale'],scale) and near(d['CanvasSize'],512*scale) and near(d['TopScreen'][0],d['GroundScreen'][0]-px*scale,1.e-3) and near(d['TopScreen'][1],d['GroundScreen'][1]-py*scale,1.e-3),'Single fixedaxe/ONErow/mirrored floor differs')
   recent=[e for e in events if e['Kind']==8 and e['Amount']>0 and 0<=stamp-e['AtTime']<.22]
   need(s['MaterialHit']==bool(recent) and (int(s['MaterialEventId'])==int(recent[-1]['EventId']) if recent else int(s['MaterialEventId'])==0),'Material hit is not a real finite positive Damaged receipt')
   if clip not in masks:continue
   need(int(s['AttackId'])==aid,'Another break/action donated Stun/IR frame')
   if clip=='Stunned':need(s['Phase']==6 and int(s['SourceEventId'])==bid and s['IntervalStart']==b['AtTime'] and s['IntervalEnd']==b['EndTime'] and b['AtTime']<=stamp<b['EndTime'] and frame==sum(stamp>=b['AtTime']+x for x in [.1,.2,.3]),'Original Stun clock/event/frame differs')
   else:need(s['Phase']==5 and int(s['SourceEventId'])==0 and s['IntervalStart']==r['stun_end'] and s['IntervalEnd']==end and r['stun_end']<=stamp<end and frame==min(3,math.floor((stamp-r['stun_end'])/(end-r['stun_end'])*4)),'IR used new/fixed clock or wrong SourceEventId oracle')
   key=int(d['DrawId'])
   if key in seen:continue
   seen.add(key);need(n and stamp<=n['time']+1.e-9 and n['interrupted'] and int(n['attack_id'])==aid,'Draw is future/uninterrupted/another native action')
   if eligible:masks[clip]|=1<<frame;coverage.append(dict(observation=i,DrawId=d['DrawId'],clip=clip,frame=frame,sample=stamp,AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],object=d['TexturePath'],player=o['player_ground'],guard=n['ground']))
  if n:
   for bound,clip in [(r['stun_end'],'Stunned'),(end,'InterruptedRecovery')]:
    if n['time']>=bound:need(masks[clip]==15,'Original phase ended before true four-frame coverage')
 need(masks==protocol['mask_requirements'] and masks['Stunned']==r['StunMask'] and masks['InterruptedRecovery']==r['InterruptedRecoveryMask'],'True single-break Stun4/IR4 coverage missing')
 need(obs[-1]['phase']=='complete' and obs[-1]['guard_native']['time']>=end and not obs[-1]['room_cleared'],'Completion altered original deadline or killed room')
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tooling/verify-combat-native-pixels-v003.py'),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(result.returncode==0,'Native CRC/FIFO proof failed: '+result.stderr);pixels=json.loads(result.stdout);need(pixels['passed'] and pixels['native_async_writer_verified'],'Native pixel writer proof missing')
 return dict(passed=True,scope=protocol['scope'],native_report_sha256=sha(original/'runtime-report.json'),run=r['run'],process_id=r['process_id'],break_event_id=str(bid),interrupted_attack_id=str(aid),masks=masks,native_frames=len(obs),actual_J_hit_count=len(hits),guard_final_HP=hp,player_final_HP=r['player_final_HP'],coverage_witnesses=coverage,pixel_proof=pixels,visual_reviewed=False,formal_complete_units=0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--profile-prereg',required=True);p.add_argument('--combat-prereg',required=True);p.add_argument('--archive');p.add_argument('--source-only',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args();snapshot=path(a.snapshot);profile=path(a.profile_prereg);prereg=path(a.combat_prereg);m,facts,protocol=preflight(snapshot,profile,prereg)
 if a.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=m['strict_registered_tests'],known_unique=44,scenario='StunIR',UE_started=False)));return
 need(a.archive is not None,'Actual independent StunIR archive required');archive=path(a.archive);result=verify(archive,facts,snapshot,prereg,protocol)
 if a.write_receipt:
  out=archive/'原件/independent-StunIR-v003.json';need(not out.exists(),'Never overwrite independent receipt');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
