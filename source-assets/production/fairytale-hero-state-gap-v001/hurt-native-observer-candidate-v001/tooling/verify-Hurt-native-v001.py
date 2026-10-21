"""Independent readonly Guard-Axe→real player Hurt4 proof; no UE launch or gameplay writes."""
from pathlib import Path
import argparse,hashlib,json,math,re,runpy,subprocess,sys
ROOT=Path('F:/Ourgame').resolve();CANDIDATE=Path(__file__).resolve().parent.parent
COMPONENTS=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand','IndependentSword']
STACK=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','IndependentSword','NearHand']
TESTS=['ActualPoiseBreakFourPhasesAndExclusions','RealBindingSource32MirrorAndAtomicRejection','RealCodecPauseContinueKeepsAgeAndEquipment']
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def path(p):p=Path(p);return (p if p.is_absolute()else ROOT/p).resolve()
def pin(r):
 need(type(r)is dict and set(r)=={'path','bytes','sha256'},'Actual input pin missing/malformed')
 p=path(r['path']);f=fact(p);need(f['bytes']==r['bytes']and f['sha256']==r['sha256'],'Pinned input differs: '+str(p));return p
def near(a,b,tol=1.e-4):return math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol
def point(a,b,tol=1.e-4):return len(a)==len(b)==2 and all(near(x,y,tol)for x,y in zip(a,b))
def original_frame(age):return 3 if age>=.3 else 2 if age>=.2 else 1 if age>=.1 else 0
def quad_project(slot,source):
 # AHUD::DrawTexture actual arguments, not the shared planner's formulas.
 u,v=slot['uv'];du,dv=slot['uv_size'];w,h=slot['size'];x,y=slot['top'];px,py=slot['rotation_pivot']
 qx=(source[0]/512.-u)/du*w; qy=(source[1]/512.-v)/dv*h
 a=math.radians(slot['rotation']);c,s=math.cos(a),math.sin(a);qx-=px*w;qy-=py*h
 return [x+px*w+c*qx-s*qy,y+py*h+s*qx+c*qy]
def preflight(snapshot,prereg_path):
 freeze=read(CANDIDATE/'Hurt-native-observer-freeze-v001.json')
 for row in freeze['files']:pin(row)
 p=read(prereg_path);need(p['schema']=='hero-Hurt4-Root-prereg-v001'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True,'Actual Root Hurt prereg required')
 need(p['candidate_freeze_pin']==fact(CANDIDATE/'Hurt-native-observer-freeze-v001.json'),'Root prereg binds another observer candidate')
 pin(p['candidate_freeze_pin']);need(p['compiled_manifest_sha256']==fact(snapshot/'compiled-source-manifest.json')['sha256'],'Root Hurt prereg binds another compiled snapshot')
 inputs=read(CANDIDATE/'read-only-input-pins-v001.json');checker=pin(inputs['Guard_approved1286_source_checker'])
 gp=pin(p['Guard_profile_prereg_pin']);g=read(gp);pin(p['production_extension_approval_pin'])
 need(g['production_extension_pin']==p['production_extension_approval_pin']and g['compiled_manifest_sha256']==p['compiled_manifest_sha256'],'Hurt/Guard production approval or compiled snapshot differ')
 m,_,_=runpy.run_path(str(checker))['source_check'](snapshot,gp)
 files={r['path'].replace('\\','/'):r for r in m['files']};need(sum(x.startswith('UnrealGame/Content/Production/')for x in files)==1286,'Fresh exact1286 compiled Production required')
 suite=read(ROOT/m['full_suite']['path'])
 for name in TESTS:
  rows=[t for t in suite['tests']if t['fullTestPath']=='CodexDungeon.Content.FairytaleSwordHurtV001.'+name]
  need(len(rows)==1 and rows[0]['state']=='Success'and rows[0]['errors']==rows[0]['warnings']==0,'Strict actual Hurt semantic GREEN missing: '+name)
 required=['DungeonHeroHurtProbeV001.h','DungeonHeroHurtProbeV001.cpp','DungeonFairytaleSwordHurtDrawState.h','DungeonFairytaleSwordHurtPresentation.cpp','DungeonFairytaleSwordHurtTextures.inl','DungeonFairytaleSwordHurtPlan.h','DungeonFairytaleSwordHurtPlan.cpp','DungeonFairytaleSwordHurtProfile.h','DungeonFairytaleSwordHurtProfile.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFighter.h','DungeonFighter.cpp','Tests/DungeonFairytaleSwordHurtV001Tests.cpp']
 admitted={r['path'].replace('\\','/'):r for r in p['admitted_source_files']}
 need(len(admitted)==len(p['admitted_source_files'])and {'UnrealGame/Source/CodexDungeon/'+n for n in required}<=set(admitted),'Hurt actual source pins incomplete/duplicate')
 for n,r in admitted.items():need(n in files and all(r[k]==files[n][k]for k in ['bytes','sha256']),'Hurt admitted source differs from fresh compiled pins');pin(r)
 for n in ['DungeonHeroHurtProbeV001.h','DungeonHeroHurtProbeV001.cpp']:
  need(fact(ROOT/'UnrealGame/Source/CodexDungeon'/n)['sha256']==fact(CANDIDATE/'new-source'/n)['sha256'],'Actual independent Hurt actor differs')
 hud=(ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_text(encoding='utf-8-sig')
 need('SpawnActor<ADungeonHeroHurtProbeV001>()'in hud and 'DungeonFairytaleSwordHurtV001::PreloadTexture' in hud and 'FinishCompilation(ReadyArmorTextures)'in hud,'Actual HUD startup/Hurt preload hook missing')
 need(p['Hurt_production_candidate_freeze_pin']==inputs['Hurt_production_candidate_freeze'],'Root Hurt production candidate differs')
 production_freeze=pin(p['Hurt_production_candidate_freeze_pin'])
 for member in read(production_freeze)['files']:pin({'path':str(production_freeze.parent/member['path']),'bytes':member['bytes'],'sha256':member['sha256']})
 profile=read(pin(inputs['Hurt_prepared_profile']));manifest=read(pin(inputs['Hurt32_import_manifest']))
 need(manifest['source_closure_digest']==profile['source_closure_digest']and profile['standing_height_source_px']==416 and profile['standing_display_height_px']==72,'Prepared source identity/constant scale differs')
 need(type(p['approach_side'])is int and p['approach_side']in [-1,0,1],'Root typed side required')
 return m,p,profile,manifest
def verify_draw(o,frame,profile,manifest,report):
 d=o['hurt_draw'];f=profile['frames'][frame];side=-report['actual_approach_side'];scale=72/416*d['ui_scale']
 need(d['opt_in']and d['drawn']and d['atomic_preflight_ready']and d['supported']and not d['missing_reason'],'Hurt actual renderer/preflight failed')
 need(d['sim']==o['sim']and d['player_entity']==report['player_entity']and d['frame']==frame and d['facing']==o['facing']==side and d['profile']==profile['profile_id'],'Hurt actual draw identity/frame/facing differs')
 need(d['hurt_active']and d['hurt_elapsed']==o['hurt_elapsed']==o['animation_time']and d['hurt_remaining']==o['hurt_remaining']>0,'Hurt query/real animation age differs')
 need(d['run']==report['run']and d['owner']==report['owner']and d['weapon_instance']==o['weapon_instance']==report['sword_instance']and d['armor_instance']==o['armor_instance']==report['light_instance']and d['weapon_content']=='WPN-SWD-001'and d['armor_content']=='ARM-LGT-001','Hurt actual committed gear/Run differs')
 root=f['ground_root_source_xy'];grip=f['Grip_source_xy'];axis=f['Axis_artist_raw_xy'];ground=d['context_ground']
 need(point(d['root_source'],root,0.)and point(d['grip_source'],grip,0.)and point(d['axis_artist'],axis,0.),'Hurt source registration/author axis differs')
 need(d['jump_height']==0 and near(d['ui_scale'],1.,0.)and near(d['canvas_size'],72*512/416,1.e-10)and near(d['source_to_screen_scale'],scale,1.e-12)and d['weapon_scale']==.5 and near(d['weapon_width'],512*scale*.5,1.e-10),'Hurt constant row/sword scale or grounded premise differs')
 expected_ground=[640+(o['ground'][0]-o['camera_ground'][0])*.65,490-o['ground'][1]*.38]
 need(point(ground,expected_ground,1.e-3),'Actual HUD ground pixel differs from actor/camera projection')
 expected_top=[ground[0]-(root[0]if side>0 else 512-root[0])*scale,ground[1]-root[1]*scale]
 expected_grip=[ground[0]+side*(grip[0]-root[0])*scale,ground[1]+(grip[1]-root[1])*scale]
 need(point(d['body_top'],expected_top)and point(d['grip_screen'],expected_grip),'Hurt native Root/Grip screen pixels differ')
 theta=math.atan2(axis[1],axis[0]);want_angle=math.degrees(theta)*(1 if side>0 else -1);pivot=[99/512 if side>0 else 1-99/512,.5]
 need(near(d['weapon_angle'],want_angle,1.e-9)and point(d['sword_pivot_uv'],pivot,1.e-12)and d['texture_u']==(0 if side>0 else 1)and d['texture_du']==side,'Hurt weapon angle/one-X-reflection differs')
 need(point(d['sword_top'],[expected_grip[i]-pivot[i]*d['weapon_width']for i in range(2)]),'Sword pivot/top does not place the source grip into the actual fist')
 bycomponent={r['component']:r for r in manifest['assets']if r['frame']==frame};slots=d['slots'];need(len(slots)==9,'Nine declared slots required including empty')
 expected_stack=[]
 for i,(name,s)in enumerate(zip(STACK,slots)):
  sword=name=='IndependentSword';e=None if sword else bycomponent[name];empty=False if sword else e['known_optional_empty'];texture=profile['independent_sword']['object_path']if sword else e['object_path']
  need(s['slot']==i and s['component']==COMPONENTS.index(name)and s['texture']==texture and s['known_empty']is empty and s['texture_ready']is True and s['drawn']is(not empty),'Actual slot order/object/readiness/empty skip differs')
  need(s['draw_scale']==1 and s['scale_position']is False and point(s['uv'],[d['texture_u'],0],0.)and point(s['uv_size'],[d['texture_du'],1],0.),'Actual quad UV/scale arguments differ')
  width=d['weapon_width']if sword else 512*scale;top=d['sword_top']if sword else d['body_top']
  need(point(s['top'],top)and point(s['size'],[width,width])and near(s['rotation'],d['weapon_angle']if sword else 0.,1.e-4)and point(s['rotation_pivot'],pivot if sword else [0,0],1.e-12),'Actual float quad arguments differ from consumed plan')
  if not empty:expected_stack.append(texture)
  if not sword:need(point(quad_project(s,root),ground,2.e-4)and point(quad_project(s,grip),expected_grip,2.e-4),'Body actual submitted quad does not project source Root/Grip pixels')
 need(d['actual_stack']==o['rendered_stack']==expected_stack and d['nonempty_count']==len(expected_stack)==(9 if frame==0 else 8),'Actual rendered stack/count differs from nine-slot contract')
 sword=slots[7]
 for src in [[99,256],[199,256],[99,356]]:
  x,y=src[0]-99,src[1]-256;v=[math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y]
  expected=[expected_grip[0]+side*.5*scale*v[0],expected_grip[1]+.5*scale*v[1]]
  need(point(quad_project(sword,src),expected,2.e-4),'Actual sword grip/axis/perpendicular pixel transform differs; double mirror forbidden')
def verify(archive,snapshot,p,profile,manifest,prereg_path):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json')
 need(r['schema']=='hero-SWD-LGT-Hurt4-native-observer-v001'and r['scenario']=='GuardAxeToHeroHurt4'and r['passed']is True and r['flow_complete']is True,'Native original Hurt trial is RED')
 need(index['schema']=='hero-Hurt4-native-session-v001'and index['process_id']==int(r['process_id'])and index['snapshot_manifest_sha256']==p['compiled_manifest_sha256']and path(index['root_prereg'])==prereg_path and index['root_prereg_sha256']==fact(prereg_path)['sha256']and index['candidate_freeze_sha256']==p['candidate_freeze_pin']['sha256'],'Session PID/prereg/snapshot/candidate binding differs')
 need(r['requested_approach_side']==p['approach_side']==index['requested_approach_side']and r['actual_approach_side']in [-1,1]and (p['approach_side']==0 or p['approach_side']==r['actual_approach_side']),'Actual requested side differs')
 need(r['player_or_Guard_public_damage_used']is False and r['HP_poise_clock_actor_writes']is False and r['silent_video']is True and r['audio_recorded']is False and r['visual_reviewed']is False and r['formal_complete_units']==0,'Native trial scope differs')
 need(r['guard_final_HP']==185 and r['guard_incoming_count']==0,'Real Guard was damaged/preset')
 diag=r['diagnostic_predecessor_hits'];need(len(diag)==2 and [x['content']for x in diag]==['ENM-STN-001','ENM-STN-002']and all(x['api']=='ADungeonFighter::ApplyCombatHit'and x['before_HP']>x['after_HP']==0 and x['dead']is True for x in diag),'Only two explicitly scoped predecessor diagnostic hits allowed')
 downs=[x['key']for x in r['normal_inputs']if x['down']];need(downs.count('Enter')==downs.count('E')==1 and set(downs)<={'Enter','E','A','D','W','S'}and bool(set(downs)&{'W','S'})and bool(set(downs)&{'A','D'}),'Normal controller input only contract differs')
 for x in r['normal_inputs']:need(math.isfinite(x['sim'])and math.isfinite(x['wall_offset_s']),'Normal input timing invalid')
 events=r['guard_original_events'];need([int(x['event'])for x in events]==sorted({int(x['event'])for x in events}),'Guard issued facts duplicate/reorder')
 hits=[e for e in events if e['kind']==11 and e['target']==r['player_entity']];need(len(hits)==1,'Exactly one original Guard hit must own the Hurt proof')
 hit=hits[0];a=hit['action'];need(hit['entity']==r['guard_entity']and hit['event']==r['hit_event']and a['attack_id']==r['hit_attack']and hit['at']==r['hit_at']and a['kind']==1 and a['damage']==24 and a['stagger']==30 and a['active_at']<=hit['at']<a['active_end'],'Real original Axe hit identity/window differs')
 for key,value in [('lock_at',.5),('active_at',1.),('active_end',1.2),('recovery_end',2.6),('cooldown_end',3.1)]:need(near(a[key]-a['start'],value,1.e-8),'Original Guard Axe clock changed')
 rc=r['guard_original_hit_receipts'];need(len(rc)==1 and rc[0]['attack']==r['hit_attack']and rc[0]['target']==r['player_entity']and rc[0]['at']==r['hit_at'],'Native outgoing Guard hit receipt differs')
 confirmed=[x for x in r['guard_actual_confirmed_losses']if x['target']==r['player_entity']];need(len(confirmed)==1 and confirmed[0]['event']==r['hit_event']and confirmed[0]['attack']==r['hit_attack']and confirmed[0]['at']==r['hit_at']and confirmed[0]['actual_HP_loss']==r['actual_HP_loss']>0 and confirmed[0]['source_kind']==11,'Actual committed HP loss is not linked to original Guard hit')
 need(near(r['actual_HP_loss'],24/1.14,1.e-4)and r['prehit_HP']-r['actual_HP_loss']>0,'Axe damage mitigation/nonlethal premise differs')
 startup=r['startup_resident_textures'];need(len(startup)==33 and len({x['texture']for x in startup})==33 and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resident']is True for x in startup),'Exact32 + reused sword startup residency absent')
 sources={x['object_path']:x for x in manifest['assets']}
 for s in startup:
  if s.get('sword'):need(s['texture']==profile['independent_sword']['object_path'],'Reused sword identity differs');continue
  e=sources[s['texture']];need(s['frame']==e['frame']and COMPONENTS[s['component']]==e['component']and s['source_SHA']==e['source_sha256']and s['source_RGBA_SHA']==e['source_RGBA_sha256']and s['known_empty']is e['known_optional_empty']and s['source_alpha_nonzero']==e['source_alpha_nonzero_pixels'],'Startup source metadata/known-empty differs')
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>4 and all(y>x for x,y in zip(offsets,offsets[1:]))and r['capture_timing']['use_fixed_time_step']is False,'Original native callbacks/ordinary pacing differ')
 frames=set();draws=set();hobs=[];ready=[];walk=[];walk_distance=0.;motion_times=set();join_draws=set();steps=r['steps'];walk_starts=[s['sim']for s in steps if s['phase']==11];need(len(walk_starts)==1,'Exactly one original Walk join window required')
 for o,t in zip(obs,offsets):
  need(o['wall_offset_s']==t and not o['interface_visible']and o['text_calls']==0,'Actual callback offset/hidden interface differs')
  if o['hurt_query_ok']and o['hurt_active']:
   need(o['phase']==9 and o['animation']=='hurt'and o['hurt_remaining']>0 and o['hurt_elapsed']>=0 and not any(o[k]for k in ['held_A','held_D','held_W','held_S']),'Only original stationary native Hurt can earn phase coverage')
   f=original_frame(o['hurt_elapsed']);verify_draw(o,f,profile,manifest,r);d=o['hurt_draw'];need(d['draw_id']not in draws,'Repeated native Hurt draw witness');draws.add(d['draw_id']);frames.add(f);hobs.append(o)
   need(near(o['HP'],r['prehit_HP']-r['actual_HP_loss'],1.e-4)and o['poise_threshold']==30 and o['armor']==14 and o['physical_vulnerability']==1,'Native actual player HP/poise/armor changed')
  if o['phase']in [10,11]:
   j=o['join_draw'];need(o['hurt_query_ok']is False and o['animation']!='hurt'and o['hurt_draw']['drawn']is False,'Post-Hurt source continued beyond real owner exit')
   good=j['active']and j['supported']and j['texture_ready']and j['armor_drawn']and j['weapon_instance']==r['sword_instance']and j['stack']==o['rendered_stack']
   if o['phase']==10 and good and not j['walk']and j['clip']=='sword_ready_idle':
    need(j['draw_id']not in join_draws,'Repeated Ready join draw witness');join_draws.add(j['draw_id']);ready.append(o)
   if o['phase']==11 and good and j['walk']and j['facing']==r['actual_approach_side']:
    m=o['motion'];side=r['actual_approach_side'];outward=o['held_D']if side>0 else o['held_A'];opposite=o['held_A']if side>0 else o['held_D']
    if all(m[k]for k in ['query_ok','published','grounded','ordinary','intent'])and m['from_time']>=walk_starts[0]and m['to_time']not in motion_times and m['to_time']>m['from_time']and outward and not opposite and not o['held_W']and not o['held_S']and (m['to'][0]-m['from'][0])*side>0 and m['to'][1]==m['from'][1]and m['owner']==r['owner']and m['run']==r['run']:
     need(j['draw_id']not in join_draws,'Repeated Walk join draw witness');join_draws.add(j['draw_id']);need(near(m['accepted'],math.dist(m['from'],m['to']),1.e-6),'Accepted Walk distance differs from actual path');motion_times.add(m['to_time']);walk.append(o);walk_distance+=m['accepted']
 need(frames=={0,1,2,3}and r['HurtMask']==15 and len(ready)>=2 and len(walk)>=4 and walk_distance>=24 and r['ReadySeen']==len(ready)and r['WalkSeen']==len(walk)and near(r['accepted_walk'],walk_distance,1.e-6),'Original Hurt4/actual Ready/accepted Walk coverage incomplete or fabricated')
 need(all(y['hurt_elapsed']>x['hurt_elapsed']and y['hurt_remaining']<x['hurt_remaining']for x,y in zip(hobs,hobs[1:])),'Hurt source age repeated or reversed')
 # Use the unchanged native lossless CRC/FIFO/stop→flush verifier with this scenario schema.
 subprocess.run([sys.executable,'-B','-X','utf8',str(CANDIDATE/'tooling/verify-Hurt-native-pixels-v001.py'),'--archive',str(archive)],check=True,capture_output=True,text=True)
 optical=runpy.run_path(str(CANDIDATE/'tooling/verify-Hurt-source-pixels-v001.py'))['verify_source_pixels'](archive,profile,manifest,hobs)
 return {'passed':True,'original_Hurt_frames':sorted(frames),'native_Hurt_draws':len(hobs),'actual_Ready_draws':len(ready),'actual_Walk_draws':len(walk),'actual_accepted_Walk_distance':walk_distance,'native_quad_Root_Grip_axis_full_mirror_verified':True,'native_PNG_CRC_FIFO_verified':True,'optical_source_projection':optical,'audio_recorded':False,'visual_reviewed':False,'FinalAccepted':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--root-prereg',required=True);p.add_argument('--archive');p.add_argument('--source-only',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args();snapshot=path(a.snapshot);prereg=path(a.root_prereg);m,root,profile,manifest=preflight(snapshot,prereg)
 if a.source_only:print(json.dumps({'compiled_inputs_verified':True,'strict_registry':m['strict_registered_tests'],'production_files':1286,'Hurt_source32':32,'approach_side':root['approach_side'],'UE_started':False}));return
 need(a.archive,'Actual original archive required');result=verify(path(a.archive),snapshot,root,profile,manifest,prereg)
 if a.write_receipt:
  with (path(a.archive)/'原件/Hurt-independent-native-verification-v001.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
