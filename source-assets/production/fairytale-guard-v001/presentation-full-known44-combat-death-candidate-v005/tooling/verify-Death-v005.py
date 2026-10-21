"""Independent real-J Death/automatic reward receipt/clock/source proof; no UE launch or owner writes."""
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
 f=C/'Death-candidate-freeze-v005.json'
 for x in read(f)['files']:pin(C/x['path'],x)
 inp=read(C/'independent-profile-input-pins-v005.json')
 for x in inp.values():
  if isinstance(x,dict) and 'sha256' in x:pin(path(x['path']),x)
 module=runpy.run_path(str(path(inp['profile_source_checker']['path'])));m,facts,_=module['source_check'](snapshot,profile)
 p=read(prereg);protocol=read(C/'proof-protocol-v005.json')
 need(p['schema']==protocol['Root_prereg_schema'] and p['scenario']=='Death' and p['is_template'] is False and p['pre_registered_before_capture'] is True,'Actual independent Death Root prereg required')
 need(p['compiled_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json'),'Combat prereg bound another compiled snapshot')
 q=p['source_profile_prereg_pin'];pin(path(q['path']),q);need(path(q['path']).resolve()==profile.resolve(),'Combat/source-profile prereg differ')
 q=p['death_candidate_freeze_pin'];pin(path(q['path']),q);need(path(q['path']).resolve()==f.resolve(),'Combat prereg bound another tool/source freeze')
 files={x['path']:x for x in m['files']};admitted={x['path']:x for x in p['admitted_death_source_files']}
 required={'UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonGuardArtDeathProbeV005.h','DungeonGuardArtDeathProbeV005.cpp','DungeonHUD.cpp']}
 need(required==set(admitted) and len(admitted)==len(p['admitted_death_source_files']),'Exact new actor/HUD admitted pins required')
 for n,x in admitted.items():need(files[n]==x,'Combat Source differs from actual compiled snapshot');pin(R/n,x)
 for n in ['DungeonGuardArtDeathProbeV005.h','DungeonGuardArtDeathProbeV005.cpp']:
  actual=(R/'UnrealGame/Source/CodexDungeon'/n).read_text(encoding='utf-8-sig');need(actual==(C/'new-source'/n).read_text(encoding='utf-8-sig'),'Compiled combat actor differs from this frozen source beyond line endings')
 need('SpawnActor<ADungeonGuardArtDeathProbeV005>()' in (R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_text(encoding='utf-8-sig'),'Independent combat startup missing')
 return m,facts,protocol
def spatial(o,d,r):
 s=d['Selection'];n=o.get('guard_native');side=r['actual_approach_side']
 if not n or o['phase']!='normal_guard_J_Death_and_coin' or not o['approach_spatial']['route_reached'] or s['Clip']!='Death' or int(s['SourceEventId'])!=int(r['death_event_id']):return False
 dx=side*(o['player_ground'][0]-n['ground'][0]);dy=o['player_ground'][1]-n['ground'][1]
 return n['dead'] is True and n['HP']==0 and o['player_HP']>0 and 90<=dx<=155 and abs(dy)<=20 and r['death_at']<=s['SampleTime']<r['death_at']+1.

def reward_proof(r,death,obs):
 rewards=r['rewards_final'];gid=int(r['guard_entity']);owner=int(r['owner']);oid=int(r['coin_object_id']);op=int(r['coin_operation_id'])
 need(rewards['Schema']==2 and rewards['Bound'] is True and rewards['Run']==r['run'] and int(rewards['OwnerId'])==owner and int(rewards['Room'])==1 and rewards['InitialCoins']==20,'Actual bound Rewards schema2/run/owner/room differs')
 ds=[x for x in rewards['Deaths'] if int(x['EntityId'])==gid];need(len(ds)==1,'Exactly one formal Guard death reward fact required');d=ds[0]
 need(d['ContentId']=='ENM-STN-003' and int(d['Room'])==1 and d['AtTime']==death['AtTime'] and d['FirstDeath'] is False and d['RoomCleared'] is True,'Reward source death is not original native Died time/last slot')
 ss=[x for x in rewards['Sources'] if int(x['EntityId'])==gid];need(len(ss)==len(d['SourceIds'])==1 and str(ss[0]['SourceId'])==str(d['SourceIds'][0]),'Guard must allocate exactly one original source');src=ss[0]
 need(src['Kind']==0 and int(src['ObjectId'])==oid and src['AtTime']==death['AtTime'] and int(src['Room'])==1,'Guard source is not unique native enemy coin')
 os=[x for x in rewards['Objects'] if int(x['SourceId'])==int(src['SourceId'])];need(len(os)==1,'Guard coin object duplicated');coin=os[0]
 need(int(coin['ObjectId'])==oid and coin['Kind']==0 and coin['Amount']==9 and coin['Consumed'] is True and coin['Retired'] is False and int(coin['CollectionOperationId'])==op and int(coin['Room'])==1 and coin['Position']==[d['Position'][0]-18.,d['Position'][1]-12.],'Automatic Guard coin9 identity/position/state differs')
 cs=[x for x in rewards['Collections'] if int(x['ObjectId'])==oid];need(len(cs)==1,'Guard coin was collected more/less than once');col=cs[0]
 need(int(col['OperationId'])==op and int(col['SourceId'])==int(src['SourceId']) and int(col['OwnerId'])==owner and int(col['Room'])==1 and col['AtTime']==r['coin_collected_at'] and col['AtTime']>=death['AtTime']+1. and col['BeforeCoins']==r['coin_before'] and col['AfterCoins']==r['coin_after']==col['BeforeCoins']+9,'Original automatic collection receipt/after-art ordering differs')
 wallet=20;operations=[];objects={int(x['ObjectId']):x for x in rewards['Objects']}
 for x in rewards['Collections']:
  q=objects[int(x['ObjectId'])];need(q['Kind']==0 and x['BeforeCoins']==wallet and x['AfterCoins']==wallet+q['Amount'] and int(x['OwnerId'])==owner,'Full actual wallet chain differs');wallet=x['AfterCoins'];operations.append(int(x['OperationId']))
 need(operations==list(range(1,len(operations)+1)) and wallet==r['wallet'],'Automatic collection operation/wallet continuity differs')
 deadseen=[];consumed=[]
 for i,o in enumerate(obs):
  n=o.get('guard_native');rw=o['rewards']
  need(rw['Schema']==2 and rw['Run']==r['run'] and int(rw['OwnerId'])==owner and len([x for x in rw['Deaths'] if int(x['EntityId'])==gid])<=1 and len([x for x in rw['Collections'] if int(x['ObjectId'])==oid])<=1,'Observed same owner death/collection duplicated')
  if n and n['dead']:
   need(n['HP']==0 and n['phase']==7 and n['can_receive_direct_hit'] is False and not n['in_progress'],'Dead owner kept gameplay life/hit admission/action');deadseen.append(i)
  if any(int(x['ObjectId'])==oid and x['Consumed'] for x in rw['Objects']):consumed.append(i)
 need(deadseen and consumed,'Actual dead owner/automatic pickup not observed')
 i=consumed[0];o=obs[i];n=o['guard_native'];delta=[o['player_ground'][k]-coin['Position'][k] for k in [0,1]]
 need(o['player_HP']>0 and o['sim']>=col['AtTime'] and abs(delta[0])<=60 and abs(delta[1])<=30 and o['wallet']==col['AfterCoins'],'First actual consumed callback lacks live normal pickup position/wallet')
 need(all(obs[k]['guard_native']['dead'] and obs[k]['guard_native']['HP']==0 for k in range(i,len(obs))),'Guard revived after original auto collection')
 last=obs[-1];need(last['room_cleared'] and last['slots'][2]['stage']=='3' and int(last['slots'][2]['entity'])==gid and int(last['slots'][2]['coin'])==oid and last['slots'][2]['coin_share']==9 and last['slots'][2]['dead_at']==death['AtTime'] and last['guard_native']['death_observed'] and last['guard_native']['death_settled'] and last['guard_native']['reward_claimed'],'Actual settled original slot2/room/claim differs')
 return dict(coin_object_id=str(oid),collection_operation_id=str(op),collected_at=col['AtTime'],before=col['BeforeCoins'],after=col['AfterCoins'],first_consumed_observation=i,automatic_collection_position=o['player_ground'])

def verify(archive,facts,snapshot,prereg,protocol):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json');freeze=C/'Death-candidate-freeze-v005.json'
 need(index['schema']==protocol['session_schema'] and index['candidate_freeze_sha256']==sha(freeze) and index['snapshot_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json') and index['root_prereg_sha256']==sha(prereg),'Session does not bind real combat prereg/source/tooling')
 need(r['schema']==protocol['runtime_report_schema'] and r['scenario']=='Death' and r['passed'] is True and r['flow_complete'] is True and r['death_pinned'] is True,'Native independent Death RED/wrong schema')
 need(str(index['process_id'])==r['process_id'] and r['restart_serial']=='1' and int(r['owner'])>0 and r['actual_approach_side'] in [-1,1],'Fresh process/run/restart/side scope differs')
 need(r['guard_public_damage_used'] is False and r['guard_normal_J_only'] is True and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False and r['player_damage_preserved'] is True and r['normal_J_full_clear'] is False,'Actual normal-J/diagnostic scope differs')
 need(r['silent_video'] is True and r['audio_recorded'] is False and r['visual_reviewed'] is False and r['formal_complete_units']==0,'Acceptance/audio scope differs')
 diag=r['diagnostic_public_hits'];need(len(diag)==2 and [x['content_id'] for x in diag]==['ENM-STN-001','ENM-STN-002'] and all(x['dead'] and x['after_HP']==0 and x['api']=='ADungeonFighter::ApplyCombatHit' for x in diag),'Only predecessor diagnostic public clears allowed')
 gid=int(r['guard_entity']);did=int(r['death_event_id']);events=r['guard_original_issued_events'];ids=[int(x['EventId']) for x in events]
 need(ids==sorted(set(ids)) and all(int(x['EntityId'])==gid for x in events),'Guard event identities differ')
 deaths=[x for x in events if x['Kind']==12];claims=[x for x in events if x['Kind']==13]
 need(len(deaths)==len(claims)==1 and int(deaths[0]['EventId'])==did and deaths[0]['AtTime']==r['death_at'] and claims[0]['AtTime']>=r['death_at'],'Exactly one original Died/automatic claim required');death=deaths[0]
 need(not death['Action']['in_progress'] and not any(x['Kind']!=13 for x in events if int(x['EventId'])>did),'Dead original owner emitted a later attack/damage/death event')
 da=death['Action'];aid=int(da['attack_id'])
 if aid:
  starts=[x for x in events if x['Kind']==2 and int(x['AttackId'])==aid];need(len(starts)==1,'Death retained an unknown original native attack')
  for k in ['start','lock_at','active_at','active_end','recovery_end','cooldown_end']:need(da[k]==starts[0]['Action'][k],'Death rewrote original attack deadline')
  if da['interrupted'] and da['interrupted_at']==death['AtTime']:
   interrupted=[x for x in events if x['Kind']==10 and int(x['AttackId'])==aid and x['AtTime']==death['AtTime']]
   closed=[x for x in r['guard_original_closures'] if int(x['AttackId'])==aid and x['AtTime']==death['AtTime']]
   need(len(interrupted)==1 and (len(closed)==1 if da['window_issued'] else not closed),'Death interruption/issued-window closure differs')
 incoming=r['guard_original_received_hits'];need(incoming and [int(x['ReceiptId']) for x in incoming]==list(range(1,len(incoming)+1)) and r['guard_incoming_receipt_count']==len(incoming),'Actual unique Guard resolved receipt sequence missing')
 hits=[x for x in r['player_original_hit_receipts'] if int(x['TargetId'])==gid];windows={int(x['AttackId']):x for x in r['player_original_issued_windows']}
 need(len(hits)==len(incoming) and len({(x['AttackId'],x['SubhitId'],x['TargetId']) for x in hits})==len(hits),'Normal J hit admission differs from Guard received hits')
 hp=185.;poise=0.;last=-1.;protection=0.;expected_breaks=[];lethal=[]
 for hit,h in zip(hits,incoming):
  w=windows[int(hit['AttackId'])];pa=w['FrozenAction'];need(hit['SubhitId']==0 and pa['Weapon']==0 and int(pa['WeaponInstanceId'])==1 and pa['Locked'] is True and pa['WindowIssued'] is True and not pa['StartedAirborne'] and pa['Facing']==-r['actual_approach_side'],'Guard damage is not actual inward grounded starter-SWD J')
  need(hp>0 and w['Start']<=h['AtTime']<w['End'] and near(h['Stagger'],pa['Stagger']) and h['ActualHPLoss']>0 and near(h['ActualHPLoss'],min(hp,pa['Damage']*.625),1.e-5),'Actual J time/stagger/single armor/lethal clamp differs')
  hp-=h['ActualHPLoss']
  if hp==0:lethal.append(h['AtTime']);continue
  if h['AtTime']>=protection:
   if last>=0:poise=max(0.,poise-20.*max(0.,h['AtTime']-(last+1.)))
   poise+=h['Stagger'];last=h['AtTime']
   if poise>=85:expected_breaks.append(h['AtTime']);poise=0.;protection=h['AtTime']+1.
 need(hp==r['guard_final_HP']==0 and lethal==[death['AtTime']] and expected_breaks==[x['AtTime'] for x in events if x['Kind']==9],'Independent lethal185/real85 history differs; no J-count shortcut')
 need(r['coin_collected'] is True and int(r['coin_object_id'])>0 and int(r['coin_operation_id'])>0,'Normal automatic coin was not completed')
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>2 and all(y>x for x,y in zip(offsets,offsets[1:])) and r['capture_timing']['use_fixed_time_step'] is False,'Actual callbacks/offsets/pacing differ')
 need(all(near(x['wall_offset_s'],t) and not x['interface_visible'] and x['text_calls']==0 for x,t in zip(obs,offsets)),'Hidden HUD/real callback offsets differ')
 hpseries=[x['player_HP'] for x in obs];need(all(0<x<=100 for x in hpseries) and all(y<=x for x,y in zip(hpseries,hpseries[1:])) and hpseries[-1]==r['player_final_HP'],'Real player damage was healed/ignored or player died')
 keys=[x['key'] for x in r['normal_input_requests'] if x['down']];need(keys.count('Enter')==keys.count('E')==1 and keys.count('J')>=len(hits) and set(keys)<={'Enter','E','J','A','D','W','S'},'Actual controller-only normal J/input sequence differs')
 need(any(x['hero_bound_skin'] and x['LGT_drawn'] for x in obs),'Real E committed LGT binding missing')
 for i in [1,2]:
  warned=[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==1 and o['slots'][i]['slot'] in o['rendered_warning_slots']];need(len(warned)>=2,'Actual formal world warning was not rendered')
  born=[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==2];need(bool(born),'Actual formal slot was not born');slot=born[0]['slots'][i]
  need(slot['warning_at']>=born[0]['slots'][i-1]['dead_at']+2. and slot['materialized_at']>=slot['warning_at']+1.2,'Original predecessor/breather/warning gates shortened')
  if i==2:need(int(slot['entity'])==gid,'Guard was not the formal slot2 birth')
 loaded=r['startup_resident_textures'];expected={f['object_path']:(clip,row,f) for clip,row in facts.items() for f in row['frames']};need(len(loaded)==len(expected)==44 and {x['actual_object_path'] for x in loaded}==set(expected),'Exact approved44 residency absent')
 for x in loaded:
  _,row,f=expected[x['actual_object_path']];need(x['native_source_id']==row['native_source_id'] and x['actual_class']=='Texture2D' and x['actual_width']==x['actual_height']==512 and x['resource_resident'] is True and x['source_SHA256_metadata']==f['source']['sha256'] and x['source_RGBA_SHA256_metadata']==f['RGBA_sha256'],'Actual startup texture metadata differs')
 masks={'Death':0};seen=set();coverage=[]
 for i,o in enumerate(obs):
  n=o.get('guard_native')
  if n:need(int(n['entity'])==gid and n['initial_time']==o['slots'][2]['materialized_at'] and ((n['HP']>0 and not n['dead'] and n['time']<=death['AtTime']) or (n['HP']==0 and n['dead'] and n['phase']==7 and n['time']>=death['AtTime'])),'Guard identity/life/death/birth state differs')
  for d in o['guard_draws']:
   if int(d['EntityId'])!=gid:continue
   s=d['Selection'];clip=s['Clip'];frame=s['Frame'];stamp=s['SampleTime'];eligible=spatial(o,d,r)
   need(d['SpatialCoverageEligible']==eligible and s['Valid'] and s['Facing'] in [-1,1] and not s['TerminalPresentation'],'Actual native selection/spatial qualification differs')
   if clip not in facts:need(clip in ['Move','StompActive','StompRecovery'] and not d['Drawn'] and d['ProceduralFallback'] and not d['DrawStack'] and bool(d['MissingReason']),'Gap concealed by unapproved sprite');continue
   asset='Wake' if clip=='Dormant' else clip;row=facts[asset];f=row['frames'][0 if clip=='Dormant' else frame]
   need(d['Drawn'] and d['TextureReady'] and d['RegistrationReady'] and d['TrialAllowed'] and d['RequestedRowTrialAllowed'] and d['FinalAccepted'] is False and not d['ProceduralFallback'] and d['RequestedClip']==clip and d['AssetClip']==asset,'Approved full known row was not really drawn')
   need(d['TexturePath']==f['object_path'] and d['SourceSHA256']==f['source']['sha256'] and d['SourceRGBASHA256']==f['RGBA_sha256'] and d['SourceFloorPivot']==f['floor_pivot_source_px'] and d['NativeSourceId']==row['native_source_id'],'Actual texture/source/RGBA/floor differs')
   need(d['TrialApprovalRecord']==row['trial_approval_record'] and d['RequestedTrialApprovalRecord']==facts[clip]['trial_approval_record'] and d['RegistrationEvidenceSHA256']==row['registration_evidence']['sha256'] and d['SourceIndexSHA256']==row['source_index']['sha256'],'Actual full trial registration differs')
   scale=100.8/row['standing_body_extent_px'];px,py=f['floor_pivot_source_px'];px=512-px if s['Facing']<0 else px
   need(d['WholebodyIncludesAxe'] and d['DrawStack']==[d['TexturePath']] and near(d['RowScale'],scale) and near(d['CanvasSize'],512*scale) and near(d['TopScreen'][0],d['GroundScreen'][0]-px*scale,1.e-3) and near(d['TopScreen'][1],d['GroundScreen'][1]-py*scale,1.e-3),'Single fixedaxe/ONErow/mirrored floor differs')
   recent=[e for e in events if e['Kind']==8 and e['Amount']>0 and 0<=stamp-e['AtTime']<.22]
   need(s['MaterialHit']==bool(recent) and (int(s['MaterialEventId'])==int(recent[-1]['EventId']) if recent else int(s['MaterialEventId'])==0),'Material hit is not a real finite positive Damaged receipt')
   if clip!='Death':continue
   age=stamp-death['AtTime'];need(s['Phase']==7 and int(s['SourceEventId'])==did and s['IntervalStart']==death['AtTime'] and s['IntervalEnd']==death['AtTime']+1. and age>=0 and near(s['DeathAge'],age) and s['DeathAfterglow']==(age<.1) and frame==sum(stamp>=death['AtTime']+x for x in [.1,.2,.35,.55,.75]),'Original1s Death/100ms afterglow/frame/event clock differs')
   key=int(d['DrawId'])
   if key in seen:continue
   seen.add(key);need(n and stamp<=n['time']+1.e-9 and n['dead'] and n['HP']==0,'Death draw is future or live owner')
   if eligible:masks[clip]|=1<<frame;coverage.append(dict(observation=i,DrawId=d['DrawId'],clip=clip,frame=frame,sample=stamp,AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],object=d['TexturePath'],player=o['player_ground'],guard=n['ground']))
  if n and n['time']>=death['AtTime']+1.:need(masks['Death']==63,'Original1s Death ended before true six-frame coverage')
 need(masks==protocol['mask_requirements'] and masks['Death']==r['DeathMask'],'True single original Died Death6 coverage missing')
 need(obs[-1]['phase']=='complete' and obs[-1]['guard_native']['time']>=r['coin_collected_at']+.2,'Completion bypassed original art/normal coin settle observation')
 reward=reward_proof(r,death,obs)
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tooling/verify-death-native-pixels-v005.py'),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(result.returncode==0,'Native CRC/FIFO proof failed: '+result.stderr);pixels=json.loads(result.stdout);need(pixels['passed'] and pixels['native_async_writer_verified'],'Native pixel writer proof missing')
 return dict(passed=True,scope=protocol['scope'],native_report_sha256=sha(original/'runtime-report.json'),run=r['run'],process_id=r['process_id'],death_event_id=str(did),death_at=death['AtTime'],masks=masks,native_frames=len(obs),actual_J_hit_count=len(hits),guard_final_HP=hp,player_final_HP=r['player_final_HP'],automatic_reward=reward,coverage_witnesses=coverage,pixel_proof=pixels,visual_reviewed=False,formal_complete_units=0)

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--profile-prereg',required=True);p.add_argument('--death-prereg',required=True);p.add_argument('--archive');p.add_argument('--source-only',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args();snapshot=path(a.snapshot);profile=path(a.profile_prereg);prereg=path(a.death_prereg);m,facts,protocol=preflight(snapshot,profile,prereg)
 if a.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=m['strict_registered_tests'],known_unique=44,scenario='Death',UE_started=False)));return
 need(a.archive is not None,'Actual independent Death archive required');archive=path(a.archive);result=verify(archive,facts,snapshot,prereg,protocol)
 if a.write_receipt:
  out=archive/'原件/independent-Death-v005.json';need(not out.exists(),'Never overwrite independent receipt');out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
