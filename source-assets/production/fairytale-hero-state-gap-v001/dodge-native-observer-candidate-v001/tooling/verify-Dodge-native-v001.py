"""Readonly actual Shift/Dodge33/nine submitted quads/CRC proof. Never launches UE."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,struct,subprocess,sys
ROOT=Path('F:/Ourgame').resolve();C=Path(__file__).resolve().parent.parent
MANUAL=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/dodge-manual-checkpoint-candidate-v001'
sys.path.insert(0,str(MANUAL))
from dodge_manual_contract_v001 import read,check as pin,pin as fact,resolve as path,need,frozen
COMPONENTS=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand','IndependentSword']
OWN='Dodge-native-observer-freeze-v001.json';SOURCE='Dodge-observer-source-freeze-v001.json'

def near(a,b,tol=1.e-4):return type(a)in[int,float]and type(b)in[int,float]and math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol
def point(a,b,tol=1.e-4):return len(a)==len(b)==2 and all(near(x,y,tol)for x,y in zip(a,b))
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def frame_at(sample,start):return sum(sample>=start+x for x in [.1,.2,.3])
def quad_project(s,p):
 u,v=s['uv'];du,dv=s['uv_size'];w,h=s['size'];x,y=s['top'];px,py=s['rotation_pivot'];qx=(p[0]/512-u)/du*w-px*w;qy=(p[1]/512-v)/dv*h-py*h
 a=math.radians(s['rotation']);co,si=math.cos(a),math.sin(a);return[x+px*w+co*qx-si*qy,y+py*h+si*qx+co*qy]

def preflight(snapshot,prereg):
 p=read(prereg);need(p['schema']=='hero-Dodge4-Root-prereg-v001'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True and p['FinalAccepted']is False,'Actual typed Root prereg required, template cannot execute')
 for name,key in [(OWN,'candidate_freeze_pin'),(SOURCE,'source_probe_freeze_pin')]:
  q=C/name;frozen(q);need(p[key]==fact(q),'Root bound another frozen observer');pin(p[key])
 immutable=read(C/'read-only-input-pins-v001.json')['inputs']
 for v in immutable.values():pin(v)
 for k in ['Dodge_production_candidate_freeze_pin','prepared_profile_pin','Dodge_source_manifest_pin']:
  need(p[k]==immutable[k],'Source candidate/profile differs: '+k)
 frozen(pin(p['Dodge_production_candidate_freeze_pin']))
 need(type(p['approach_side'])is int and p['approach_side']in[-1,1],'Explicit spatial approach side required')
 manifest=snapshot/'compiled-source-manifest.json';need(p['compiled_manifest_pin']==fact(manifest)and p['compiled_manifest_sha256']==fact(manifest)['sha256'],'Fresh compiled snapshot differs')
 m=read(manifest);need(p['expected_source_files']==m['source_files']and p['expected_production_files']==m['production_files']==1364 and p['expected_strict_registered_tests']==m['strict_registered_tests']==196,'Fresh real Source count/Production1364/full196 required')
 manual=pin(p['manual_input_pin']);gate=runpy.run_path(str(MANUAL/'verify-Dodge1364-manual-input-v001.py'))['verify'](manual,snapshot)
 mm=read(manual);need(pin(mm['snapshot_manifest_pin'])==manifest.resolve(),'Manual gate bound another compiled snapshot')
 need(mm['Dodge_production_Source_admission_pin']['path']and pin(read(pin(mm['Dodge_production_Source_admission_pin']))['candidate_freeze'])==pin(p['Dodge_production_candidate_freeze_pin']),'Admitted production candidate differs')
 observer=read(pin(mm['Dodge_observer_Source_admission_pin']));need(pin(observer['candidate_freeze'])==pin(p['source_probe_freeze_pin']),'Actual observer admission does not bind exact frozen source milestone')
 files={v['path']:v for v in m['files']};need(len(files)==len(m['files']),'Duplicate compiled input')
 for row in m['files']:pin(row)
 source_names={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Source').rglob('*')if x.is_file()}
 prod_names={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Content/Production').rglob('*')if x.is_file()}
 need(source_names=={n for n in files if n.startswith('UnrealGame/Source/')}and prod_names=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Compiled disk membership changed')
 for name in ['DungeonHeroDodgeProbeV001.h','DungeonHeroDodgeProbeV001.cpp']:
  need(fact(ROOT/'UnrealGame/Source/CodexDungeon'/name)['sha256']==fact(C/'new-source'/name)['sha256'],'Actual Actor differs from source freeze')
 before=(C/'before/DungeonHUD.cpp').read_text(encoding='utf-8-sig');inc='#include "DungeonGuardStompProbeV001.h"';branch='        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardStompProofV001")))GetWorld()->SpawnActor<ADungeonGuardStompProbeV001>();'
 need(before.count(inc)==before.count(branch)==1,'HUD bootstrap anchors ambiguous')
 expected=before.replace(inc,inc+'\n#include "DungeonHeroDodgeProbeV001.h"').replace(branch,'        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDodgeProofV001")))GetWorld()->SpawnActor<ADungeonHeroDodgeProbeV001>();\n        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardStompProofV001")))GetWorld()->SpawnActor<ADungeonGuardStompProbeV001>();')
 need((ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_text(encoding='utf-8-sig')==expected,'HUD exceeds admitted production plus exact observer bootstrap')
 return m,p,read(pin(p['prepared_profile_pin'])),read(pin(p['Dodge_source_manifest_pin'])),gate

def verify_draw(o,f,profile,manifest,r):
 d=o['dodge_draw'];spec=profile['frames'][f];side=r['actual_approach_side'];scale=72/416*d['ui_scale'];root=spec['ground_root_source_xy'];grip=spec['Grip_source_xy'];axis=spec['Axis_artist_raw_xy'];ground=d['context_ground']
 need(d['opt_in']and d['drawn']and d['atomic_preflight_ready']and d['supported']and not d['missing_reason'],'Actual shared renderer not completely ready/drawn')
 need(d['sim']==o['sim']and d['player_entity']==r['player_entity']and d['frame']==f and d['facing']==o['facing']==side and d['profile']==profile['profile_id'],'Actual frame/profile/facing/entity differs')
 rec=o['dodge_record'];t=rec['time'];start=r['dodge_start'];end=r['dodge_end'];need(d['dodge_active']and start<=t<end and d['dodge_owner']==rec['owner']==r['player_entity']and d['dodge_action']==rec['action']==r['dodge_action']and d['dodge_start_event']==rec['start_event']==r['dodge_start_event'],'Native action/sample identity differs')
 need(d['dodge_sample_time']==t and d['dodge_start']==rec['start']==start and d['dodge_end']==rec['end']==end and d['dodge_ready_at']==rec['ready_at']==r['dodge_ready_at']and d['dodge_elapsed']==o['dodge_elapsed']==t-start and d['dodge_remaining']==o['dodge_remaining']==end-t,'Raw original double clock/deadline differs')
 need(d['dodge_travelled']==rec['travelled']and d['dodge_direction']==rec['direction']==[side,0]and d['dodge_block']==rec['block']==0 and d['dodge_finish']==rec['finish']==0,'Native accepted action direction/block/finish differs')
 need(d['dodge_invulnerable']==rec['invulnerable_at_sample']==(start+.06<=t<start+.20)and o['animation']=='dodge'and o['animation_time']==f32(t-start),'Original iframe or float AnimationTime changed')
 need(d['run']==r['run']and d['owner']==r['owner']and d['weapon_instance']==o['weapon_instance']==r['sword_instance']and d['armor_instance']==o['armor_instance']==r['light_instance']and d['weapon_version']==o['weapon_version']==r['sword_version']and d['armor_version']==o['armor_version']==r['light_version']and d['weapon_content']=='WPN-SWD-001'and d['armor_content']=='ARM-LGT-001','Committed gear identity/version differs')
 need(point(d['root_source'],root,0)and point(d['grip_source'],grip,0)and point(d['axis_artist'],axis,0),'Author source points differ')
 need(d['jump_height']==0 and d['ui_scale']==1 and near(d['canvas_size'],72*512/416,1.e-10)and near(d['source_to_screen_scale'],scale,1.e-12)and d['weapon_scale']==.5 and near(d['weapon_width'],512*scale*.5,1.e-10),'Constant72/416/Sword.50 scale differs')
 wantground=[640+(o['ground'][0]-o['camera_ground'][0])*.65,490-o['ground'][1]*.38];need(point(ground,wantground,1.e-3),'Actual world-ground projection differs')
 top=[ground[0]-(root[0]if side>0 else 512-root[0])*scale,ground[1]-root[1]*scale];at=[ground[0]+side*(grip[0]-root[0])*scale,ground[1]+(grip[1]-root[1])*scale]
 need(point(d['body_top'],top)and point(d['grip_screen'],at),'BodyRoot/grip screen transform differs')
 theta=math.atan2(axis[1],axis[0]);angle=math.degrees(theta)*side;pivot=[99/512 if side>0 else 1-99/512,.5]
 need(near(d['weapon_angle'],angle,1.e-9)and point(d['sword_pivot_uv'],pivot,1.e-12)and d['texture_u']==(0 if side>0 else 1)and d['texture_du']==side,'One full X mirror/angle/UV/pivot differs')
 need(point(d['sword_top'],[at[i]-pivot[i]*d['weapon_width']for i in range(2)]),'Sword top/pivot differs')
 bycomponent={a['component']:a for a in manifest['assets']if a['frame']==f};slots=d['slots'];order=spec['expected_nonempty_render_layers'];need(len(slots)==len(order)==9,'Exactly nine submitted slots required');expected=[];swordslot=None
 for i,(name,s)in enumerate(zip(order,slots)):
  sword=name=='IndependentSword';texture=profile['independent_sword']['object_path']if sword else bycomponent[name]['object_path'];expected.append(texture)
  need(s['slot']==i and s['component']==COMPONENTS.index(name)and s['texture']==texture and s['known_empty']is False and s['texture_ready']is True and s['drawn']is True,'Complete nine source owners/order/path differs')
  need(s['draw_scale']==1 and s['scale_position']is False and s['trace_tint']==d['tint']and point(s['uv'],[d['texture_u'],0],0)and point(s['uv_size'],[d['texture_du'],1],0),'Actual submitted UV/Tint/scale differs')
  width=d['weapon_width']if sword else 512*scale;wanttop=d['sword_top']if sword else d['body_top']
  need(point(s['top'],[f32(x)for x in wanttop],0)and point(s['size'],[f32(width)]*2,0)and s['rotation']==(f32(angle)if sword else 0)and point(s['rotation_pivot'],pivot if sword else[0,0],1.e-12),'Actual float quad differs from consumed plan')
  if sword:swordslot=s
  else:need(point(quad_project(s,root),ground,2.e-4)and point(quad_project(s,grip),at,2.e-4),'Actual sourceRoot/grip projected quad differs')
 need(d['actual_stack']==o['rendered_stack']==expected and d['nonempty_count']==9,'Actual rendered stack differs')
 for source in [[99,256],[199,256],[99,356]]:
  x,y=source[0]-99,source[1]-256;v=[math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y];want=[at[0]+side*.5*scale*v[0],at[1]+.5*scale*v[1]];need(point(quad_project(swordslot,source),want,2.e-4),'Actual sword matrix double-mirrored/misregistered')
 residents=d['resident_textures'];wantset={a['object_path']for a in manifest['assets']}|{profile['independent_sword']['object_path']}
 need(len(residents)==33 and {x['texture']for x in residents}==wantset and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resource_ready']is True and x['pending_initialization']is False for x in residents),'Actual complete33 GPU resources differ')

def join(o,r,walk):
 j=o['join_draw'];return not o['dodge_query_ok']and not o['dodge_active']and not o['dodge_draw']['drawn']and j['active']and j['supported']and j['walk']is walk and j['texture_ready']and j['armor_drawn']and j['weapon_instance']==r['sword_instance']and j['stack']==o['rendered_stack']and len(j['stack'])==(8 if walk else 7) and (walk or j['clip']=='sword_ready_idle')

def verify(archive,p,profile,manifest,prereg):
 r=read(archive/'原件/runtime-report.json');index=read(archive/'index.json')
 need(r['schema']=='hero-SWD-LGT-Dodge4-native-observer-v001'and r['scenario']=='NormalShiftOutwardUnblockedDodge4'and r['passed']is True and r['flow_complete']is True,'Actual original native trial failed')
 need(index['schema']=='hero-Dodge4-native-session-v001'and index['process_id']==int(r['process_id'])and index['exit_code']==0 and index['native_reported_passed']is True and index['snapshot_manifest_sha256']==p['compiled_manifest_sha256']and path(index['root_prereg'])==prereg and index['root_prereg_sha256']==fact(prereg)['sha256']and index['candidate_freeze_sha256']==p['candidate_freeze_pin']['sha256'],'Session PID/exit/prereg/snapshot/candidate differs')
 need(r['requested_approach_side']==p['approach_side']==index['requested_approach_side']==r['actual_approach_side'],'Actual requested spatial side differs')
 side=r['actual_approach_side'];need(r['restart_serial']=='1'and r['player_or_Guard_public_damage_used']is False and r['HP_poise_clock_actor_writes']is False and r['silent_video']is True and r['audio_recorded']is False and r['visual_reviewed']is False and r['formal_complete_units']==0,'Normal startup/trial scope changed')
 need(r['guard_final_HP']==185 and r['guard_incoming_count']==0,'Guard was damaged by proof')
 diag=r['diagnostic_predecessor_hits'];need(len(diag)==2 and [d['content']for d in diag]==['ENM-STN-001','ENM-STN-002']and all(d['api']=='ADungeonFighter::ApplyCombatHit'and d['before_HP']>d['after_HP']==0 and d['dead']is True for d in diag),'Only two explicit predecessor diagnostic hits allowed')
 downs=[i['key']for i in r['normal_inputs']if i['down']];need(downs.count('Enter')==downs.count('E')==downs.count('LeftShift')==1 and set(downs)<={'Enter','E','LeftShift','W','A','S','D'}and bool(set(downs)&{'W','S'})and bool(set(downs)&{'A','D'}),'Exactly normal Enter/E/one Shift/WASD input required')
 reached=[w for w in r['route_witnesses']if w['event']=='reached'and w['stage']==2];need(len(reached)==1,'One actual body-aware route must complete');w=reached[0];need(120<=(w['player'][0]-w['guard'][0])*side<=160 and abs(w['player'][1]-w['guard'][1])<=6,'Facing cannot replace requested real spatial approach')
 need(r['dodge_action']=='1'and r['dodge_start_event']=='1'and r['dodge_end']==r['dodge_start']+.4 and r['dodge_ready_at']==r['dodge_start']+1.2,'First fresh original400ms/Cooldown1.2 action required')
 sources={a['object_path']:a for a in manifest['assets']};startup=r['startup_resident_textures'];need(len(startup)==33 and len({x['texture']for x in startup})==33 and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resident']is True for x in startup),'Actual33 GPU resources not resident before Enter')
 for s in startup:
  if s.get('sword'):need(s['texture']==profile['independent_sword']['object_path'],'Sword source differs');continue
  a=sources[s['texture']];need(s['frame']==a['frame']and COMPONENTS[s['component']]==a['component']and s['source_SHA']==a['source_sha256']and s['source_RGBA_SHA']==a['source_RGBA_sha256']and s['source_alpha_nonzero']==a['source_alpha_nonzero_pixels']and s['known_empty']is False,'Startup exact RGBA/source metadata differs')
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>5 and all(b>a for a,b in zip(offsets,offsets[1:]))and r['capture_timing']['use_fixed_time_step']is False,'Actual FIFO/callback native timing differs')
 dodges=[];frames=set();draws=set();first_completed=None;ready=[];walk=[];lastmotion=-1.;distance=0.;walk_starts=[s['sim']for s in r['steps']if s['phase']==11];need(len(walk_starts)==1,'One original Walk window required')
 for i,(o,t)in enumerate(zip(obs,offsets)):
  need(o['wall_offset_s']==t and not o['interface_visible']and o['text_calls']==0 and not o['combat_range_debug']and o['combat_range_lines']==0,'HiddenUI/defaultRangeOff/callback differs')
  rec=o['dodge_record']
  if rec['record_count']:
   need(rec['record_count']==1 and rec['action']==r['dodge_action']and rec['start_event']==r['dodge_start_event']and rec['start']==r['dodge_start']and rec['end']==r['dodge_end']and rec['ready_at']==r['dodge_ready_at']and rec['owner']==r['player_entity']and rec['direction']==[side,0]and rec['block']==0 and rec['block_event']=='0'and rec['blocked_at']==-1,'Original single action/owner/lock/block changed')
   need(rec['iframe_before_start']is False and rec['iframe_at_start']is True and rec['iframe_before_end']is True and rec['iframe_at_end']is False and rec['iframe_at_action_end']is False,'Original half-open60..200ms iframe gate changed')
   need(o['weapon_instance']==r['sword_instance']and o['armor_instance']==r['light_instance']and o['weapon_version']==r['sword_version']and o['armor_version']==r['light_version']and o['HP']>0 and o['armor']==14 and o['poise_threshold']==30 and o['physical_vulnerability']==1,'Gear/current living stats changed during action/joins')
   if rec['finish']==1:
    need(rec['phase']==0 and rec['finish_event']=='2'and rec['finished_at']==rec['end']and rec['travelled']==185,'Actual completion is not original unblocked185 at End')
    if first_completed is None:first_completed=i
   else:need(rec['finish']==0 and rec['finish_event']=='0'and rec['finished_at']==-1,'Original action interrupted/died')
  if o['dodge_query_ok']or o['dodge_active']or o['dodge_draw']['drawn']:
   need(o['phase']==9 and o['dodge_query_ok']and o['dodge_active']and rec['phase']==1,'Only actual original action can render Dodge')
   f=frame_at(rec['time'],rec['start']);verify_draw(o,f,profile,manifest,r);d=o['dodge_draw'];need(d['draw_id']not in draws,'Duplicate DrawId cannot earn phase credit');draws.add(d['draw_id']);frames.add(f);dodges.append(o)
   travel=min(185,max(0,(rec['time']-rec['start'])*462.5));want=[rec['origin'][k]+rec['direction'][k]*travel for k in range(2)]
   need(rec['travelled']==travel and point(rec['position'],want,1.e-10)and point(o['ground'],rec['position'],0),'Actual accepted physics position differs from native record')
   origin=rec['origin_receipt'];need(int(origin['id'])>0 and origin['after_action']=='0'and origin['at']<=rec['start']and origin['position']==rec['origin'],'Actor-resolved position receipt missing')
  if o['phase']==10 and join(o,r,False):ready.append(o)
  if o['phase']==11 and join(o,r,True):
   m=o['motion'];out=o['held_D']and not o['held_A']if side>0 else o['held_A']and not o['held_D']
   if m['query_ok']and m['published']and m['grounded']and m['ordinary']and m['intent']and m['owner']==r['owner']and m['run']==r['run']and m['from_time']>=walk_starts[0]and m['to_time']>m['from_time']and m['to_time']>lastmotion and out and not o['held_W']and not o['held_S']and(m['to'][0]-m['from'][0])*side>0 and m['to'][1]==m['from'][1]and m['accepted']>0:
    need(near(m['accepted'],math.dist(m['from'],m['to']),1.e-6),'Actual accepted Walk distance differs from path');lastmotion=m['to_time'];distance+=m['accepted'];walk.append(o)
 need(frames==set(range(4))and r['DodgeMask']==15 and first_completed is not None,'All four original half-open phases and unique completion required')
 need(len(ready)==r['ReadySeen']>=2 and len(walk)==r['WalkSeen']>=4 and distance==r['accepted_walk']>=24,'Actual Ready and unique accepted outward Walk callbacks differ')
 need(len({o['join_draw']['draw_id']for o in ready+walk})==len(ready+walk),'Repeated Ready/Walk DrawId')
 events=r['guard_original_events'];losses=r['guard_actual_confirmed_losses'];receipts=r['guard_original_hit_receipts'];hits={e['event']:e for e in events if e['kind']==11 and e['target']==r['player_entity']}
 need(len({e['event']for e in events})==len(events)and len(losses)==len(hits)==len(receipts),'Actual Guard issued/receipt/confirmed losses do not close')
 hp=r['pre_guard_HP'];last_at=-1.
 for loss in losses:
  e=hits[loss['event']];a=e['action'];need(loss['target']==r['player_entity']and e['entity']==r['guard_entity']and loss['source_kind']==11 and loss['at']==e['at']>last_at and loss['attack']==a['attack_id']and a['active_at']<=loss['at']<a['active_end'],'Actual Guard contact source/locked original window differs');last_at=loss['at']
  need(sum(x['attack']==loss['attack']and x['target']==loss['target']and x['at']==loss['at']for x in receipts)==1,'Actual outgoing Guard receipt not unique')
  need(not(r['dodge_start']+.06<=loss['at']<r['dodge_start']+.20),'Actual direct hit crossed protected original iframe')
  need(near(loss['actual_HP_loss'],min(hp,a['damage']/1.14),1.e-4),'Actual real damage does not match locked hit plus one armor mitigation');hp=max(0,hp-loss['actual_HP_loss'])
 need(near(obs[-1]['HP'],hp,1.e-4),'Player HP differs from actual original Guard receipts')
 edges=[]
 for i in range(len(obs)-1):
  a,b=obs[i:i+2]
  if a['dodge_query_ok']and a['dodge_draw']['frame']==3 and join(b,r,False):edges.append(dict(kind='Dodge3_to_Ready',from_observation=i,to_observation=i+1,from_draw=a['dodge_draw']['draw_id'],to_draw=b['join_draw']['draw_id']))
  if join(a,r,False)and join(b,r,True):edges.append(dict(kind='Ready_to_Walk',from_observation=i,to_observation=i+1,from_draw=a['join_draw']['draw_id'],to_draw=b['join_draw']['draw_id']))
 need([e['kind']for e in edges]==['Dodge3_to_Ready','Ready_to_Walk']and edges[0]['to_observation']==first_completed,'Exact real renderer-adjacent Dodge3→Ready→Walk joins required; no gap fabrication')
 subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tooling/verify-Dodge-native-pixels-v001.py'),'--archive',str(archive)],check=True,capture_output=True,text=True)
 optical=runpy.run_path(str(C/'tooling/verify-Dodge-source-pixels-v001.py'))['verify_source_pixels'](archive,profile,manifest,dodges)
 return dict(schema='hero-Dodge4-independent-native-v001',passed=True,scenario=r['scenario'],process_id=int(r['process_id']),native_report_pin=fact(archive/'原件/runtime-report.json'),native_Dodge_frames=sorted(frames),native_Dodge_draws=len(dodges),actual_action=r['dodge_action'],original400ms_unblocked185_verified=True,original60to200ms_iframe_verified=True,actual33resident_and9slots_verified=True,actual_quad_source_projection_and_fullXmirror_verified=True,actual_guard_confirmed_hits=len(losses),actual_adjacent_joins=edges,native_PNG_CRC_FIFO_verified=True,optical_source_projection=optical,native_backwards_covered=False,blocked_native_covered=False,source_contact_floor_hidden_socket_physics_verified=False,audio_recorded=False,visual_reviewed=False,FinalAccepted=False)

def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--root-prereg',required=True);a.add_argument('--archive');a.add_argument('--source-only',action='store_true');a.add_argument('--write-receipt',action='store_true');q=a.parse_args();snapshot=path(q.snapshot);prereg=path(q.root_prereg);m,p,profile,manifest,_=preflight(snapshot,prereg)
 if q.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=196,production_files=1364,source_files=m['source_files'],Dodge_source32=32,approach_side=p['approach_side'],UE_started=False)));return
 need(q.archive,'Actual native archive required');archive=path(q.archive);result=verify(archive,p,profile,manifest,prereg)
 if q.write_receipt:
  with(archive/'原件/Dodge-independent-native-verification-v001.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
