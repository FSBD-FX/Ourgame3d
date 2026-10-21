"""Assemble independent candidate only. No UE/UBT/import/capture/View."""
from pathlib import Path
import ast,hashlib,json,shutil
C=Path(__file__).resolve().parent;R=C.parents[3]
S=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-combat-observer-candidate-v004'
assert not (C/'Death-candidate-freeze-v005.json').exists(),'Never edit a frozen candidate'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(n,t):
 p=C/n;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
def js(n,v):write(n,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
for x in read(S/'StunIR-candidate-freeze-v004.json')['files']:
 p=S/x['path'];assert p.stat().st_size==x['bytes'] and pin(p)['sha256']==x['sha256']
protocol=dict(schema='guard-known44-death-proof-protocol-v005',runtime_report_schema='guard-art-known44-death-observer-v005',session_schema='guard-art-known44-death-session-v005',Root_prereg_schema='guard-known44-death-Root-prereg-v005',scenario='Death',supported_scenarios=['Death'],source_interface='DungeonFairytaleGuardFullV003',known_unique_sources=44,selector_logical_contract=57,mask_requirements={'Death':63},normal_startup_restart_serial='1',normal_waypoint_tolerance=6,normal_staging_abs_dx=140,normal_J_actual_strike_dx=[110,132],normal_J_facing_requires_actual_inward_AD_input=True,coverage_signed_dx=[90,155],coverage_abs_dy_max=20,Death_art_duration_s=1.,Death_first_afterglow_s=.1,Death_phase_starts_s=[0.,.1,.2,.35,.55,.75],gameplay_death_delay_s=0,Guard_coin_amount=9,automatic_coin_capture_only=True,phase8_timeout_wall_s=34,capture_timeout_wall_s=48,public_Guard_damage_allowed=False,player_damage_preserved=True,scope='One actual normal-J HP0/Died and original1s Death6 plus existing GameMode-only settlement/claim, normal WASD automatic coin9. Diagnostic Knight/Bat clears; not all57/final art/audio acceptance.')
js('proof-protocol-v005.json',protocol)
inp=read(S/'independent-profile-input-pins-v003.json');inp['schema']='guard-death-independent-source-inputs-v005';js('independent-profile-input-pins-v005.json',inp)
text=(S/'tooling/verify-StunIR-v003.py').read_text(encoding='utf-8-sig')
for a,b in [('StunIR-candidate-freeze-v004.json','Death-candidate-freeze-v005.json'),('independent-profile-input-pins-v003.json','independent-profile-input-pins-v005.json'),('proof-protocol-v003.json','proof-protocol-v005.json'),('DungeonGuardArtCombatProbeV003','DungeonGuardArtDeathProbeV005'),('combat_candidate_freeze_pin','death_candidate_freeze_pin'),('admitted_combat_source_files','admitted_death_source_files'),('verify-combat-native-pixels-v003.py','verify-death-native-pixels-v005.py'),('independent-StunIR-v003.json','independent-Death-v005.json'),('combat-prereg','death-prereg'),('a.combat_prereg','a.death_prereg')]:text=text.replace(a,b)
text=text.replace("p['scenario']=='StunIR'","p['scenario']=='Death'").replace("r['scenario']=='StunIR'","r['scenario']=='Death'").replace("r['break_pinned']","r['death_pinned']").replace("scenario='StunIR'","scenario='Death'")
text=text.replace('Independent real-J StunIR receipt/clock/source proof','Independent real-J Death/automatic reward receipt/clock/source proof').replace('StunIR Root prereg','Death Root prereg').replace('independent StunIR','independent Death').replace('StunIR RED','Death RED')
start=text.index('def spatial(');end=text.index('def verify(',start)
text=text[:start]+'''def spatial(o,d,r):
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

''' +text[end:]
start=text.index(" gid=int(r['guard_entity'])");end=text.index(" obs=r['observations']",start)
text=text[:start]+''' gid=int(r['guard_entity']);did=int(r['death_event_id']);events=r['guard_original_issued_events'];ids=[int(x['EventId']) for x in events]
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
''' +text[end:]
text=text.replace(" masks={'Stunned':0,'InterruptedRecovery':0};seen=set();coverage=[]"," masks={'Death':0};seen=set();coverage=[]")
text=text.replace("if n:need(int(n['entity'])==gid and n['HP']>0 and not n['dead'] and n['initial_time']==o['slots'][2]['materialized_at'],'Guard identity/nonlethal/birth state differs')","if n:need(int(n['entity'])==gid and n['initial_time']==o['slots'][2]['materialized_at'] and ((n['HP']>0 and not n['dead'] and n['time']<=death['AtTime']) or (n['HP']==0 and n['dead'] and n['phase']==7 and n['time']>=death['AtTime'])),'Guard identity/life/death/birth state differs')")
start=text.index('   if clip not in masks:continue');end=text.index(' result=subprocess.run',start)
text=text[:start]+'''   if clip!='Death':continue
   age=stamp-death['AtTime'];need(s['Phase']==7 and int(s['SourceEventId'])==did and s['IntervalStart']==death['AtTime'] and s['IntervalEnd']==death['AtTime']+1. and age>=0 and near(s['DeathAge'],age) and s['DeathAfterglow']==(age<.1) and frame==sum(stamp>=death['AtTime']+x for x in [.1,.2,.35,.55,.75]),'Original1s Death/100ms afterglow/frame/event clock differs')
   key=int(d['DrawId'])
   if key in seen:continue
   seen.add(key);need(n and stamp<=n['time']+1.e-9 and n['dead'] and n['HP']==0,'Death draw is future or live owner')
   if eligible:masks[clip]|=1<<frame;coverage.append(dict(observation=i,DrawId=d['DrawId'],clip=clip,frame=frame,sample=stamp,AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],object=d['TexturePath'],player=o['player_ground'],guard=n['ground']))
  if n and n['time']>=death['AtTime']+1.:need(masks['Death']==63,'Original1s Death ended before true six-frame coverage')
 need(masks==protocol['mask_requirements'] and masks['Death']==r['DeathMask'],'True single original Died Death6 coverage missing')
 need(obs[-1]['phase']=='complete' and obs[-1]['guard_native']['time']>=r['coin_collected_at']+.2,'Completion bypassed original art/normal coin settle observation')
 reward=reward_proof(r,death,obs)
''' +text[end:]
start=text.index(' return dict(passed=True,scope=protocol');end=text.index('\ndef main():',start)
text=text[:start]+" return dict(passed=True,scope=protocol['scope'],native_report_sha256=sha(original/'runtime-report.json'),run=r['run'],process_id=r['process_id'],death_event_id=str(did),death_at=death['AtTime'],masks=masks,native_frames=len(obs),actual_J_hit_count=len(hits),guard_final_HP=hp,player_final_HP=r['player_final_HP'],automatic_reward=reward,coverage_witnesses=coverage,pixel_proof=pixels,visual_reviewed=False,formal_complete_units=0)\n"+text[end:]
ast.parse(text);write('tooling/verify-Death-v005.py',text)
pixels=(S/'tooling/verify-combat-native-pixels-v003.py').read_text(encoding='utf-8-sig').replace('proof-protocol-v003.json','proof-protocol-v005.json')
ast.parse(pixels);write('tooling/verify-death-native-pixels-v005.py',pixels)
launch=(S/'tooling/capture-StunIR-v004.ps1').read_text(encoding='utf-8-sig')
for a,b in [('verify-StunIR-v003.py','verify-Death-v005.py'),('combat-prereg','death-prereg'),('石守卫正常军剑破韧与原窗恢复试样','石守卫正常军剑死亡与自动金币试样'),('guard-art-known44-combat-session-v003','guard-art-known44-death-session-v005'),('StunIR-candidate-freeze-v004.json','Death-candidate-freeze-v005.json'),('DungeonGuardArtCombatProofV003','DungeonGuardArtDeathProofV005'),('DungeonGuardArtScenario=StunIR','DungeonGuardArtScenario=Death'),('StunIR','Death')]:launch=launch.replace(a,b)
write('tooling/capture-Death-v005.ps1',launch)
template=read(S/'root-templates/StunIR-Root-prereg-TEMPLATE-v004.json')
template['schema']=protocol['Root_prereg_schema'];template['scenario']='Death';template['Death_implemented']=True
template['death_candidate_freeze_pin']=dict(path=(C/'Death-candidate-freeze-v005.json').as_posix(),bytes=None,sha256=None);del template['combat_candidate_freeze_pin']
template['admitted_death_source_files']=[dict(path=x['path'].replace('DungeonGuardArtCombatProbeV003','DungeonGuardArtDeathProbeV005'),bytes=None,sha256=None) for x in template.pop('admitted_combat_source_files')]
template['fill_instructions']=[x.replace('StunIR','Death').replace('admitted_combat_source_files','admitted_death_source_files').replace('combat_candidate_freeze_pin','death_candidate_freeze_pin') for x in template['fill_instructions']]
template['fill_instructions'].append('Root must merge Death branch with actual StunIR startup branch; preserve AxeCycle/partial flags and source unchanged. No new Content required.')
js('root-templates/Death-Root-prereg-TEMPLATE-v005.json',template)
print(json.dumps(dict(candidate_tooling_assembled=True,UE_started=False,UBT_started=False,View_used=False)))
