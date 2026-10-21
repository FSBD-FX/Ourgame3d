"""Independent readonly natural-Guard→actual heroDeath5/terminal/source41 proof.
Never launches UE, writes gameplay, aligns imagery or changes optical gates.
"""
from pathlib import Path
import argparse,hashlib,json,math,runpy,subprocess,sys
ROOT=Path('F:/Ourgame').resolve();C=Path(__file__).resolve().parent.parent
COMPONENTS=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','FarHandForeground','NearHand','IndependentSword']
TESTS=['ActualFatalTerminalFivePhasesAndExclusions','RealBindingSource40MirrorAndAtomicRejection','RealCodecPauseContinueKeepsTerminalAgeAndEquipment']
REQUIRED=['DungeonHeroDeathProbeV001.h','DungeonHeroDeathProbeV001.cpp','DungeonDeathPresentation.h','DungeonFairytaleSwordDeathProfile.h','DungeonFairytaleSwordDeathProfile.cpp','DungeonFairytaleSwordDeathPlan.h','DungeonFairytaleSwordDeathPlan.cpp','DungeonFairytaleSwordDeathDrawState.h','DungeonFairytaleSwordDeathPresentation.cpp','DungeonFairytaleSwordDeathTextures.inl','DungeonFairytaleSwordPresentation.cpp','DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','Tests/DungeonFairytaleSwordDeathV001Tests.cpp']
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def path(p):
 p=Path(p);return(p if p.is_absolute()else ROOT/p).resolve()
def fact(p):
 p=path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def pin(r,base=ROOT):
 need(type(r)is dict and set(r)=={'path','bytes','sha256'},'Exact actual input pin required')
 p=Path(r['path']);p=(p if p.is_absolute()else base/p).resolve();f=fact(p)
 need(f['bytes']==r['bytes']and f['sha256']==r['sha256'],'Pinned input differs: '+str(p));return p
def near(a,b,tol=1.e-4):return isinstance(a,(int,float))and isinstance(b,(int,float))and math.isfinite(a)and math.isfinite(b)and abs(a-b)<=tol
def point(a,b,tol=1.e-4):return len(a)==len(b)==2 and all(near(x,y,tol)for x,y in zip(a,b))
def original_frame(age):
 need(math.isfinite(age)and age>=0,'Invalid actual terminalage')
 return 0 if age<.2 else 1 if age<.4 else 2 if age<.6 else 3 if age<.8 else 4
def quad_project(slot,source):
 u,v=slot['uv'];du,dv=slot['uv_size'];w,h=slot['size'];x,y=slot['top'];px,py=slot['rotation_pivot'];qx=(source[0]/512.-u)/du*w-px*w;qy=(source[1]/512.-v)/dv*h-py*h
 a=math.radians(slot['rotation']);co,si=math.cos(a),math.sin(a);return[x+px*w+co*qx-si*qy,y+py*h+si*qx+co*qy]
def check_frozen(candidate,filename):
 f=candidate/filename;data=read(f)
 for row in data['files']:pin(row,candidate)
 return fact(f)
def preflight(snapshot,prereg):
 # Reject pending approval before any expensive dependency/content scan.
 p=read(prereg);need(p['schema']=='hero-Death5-Root-prereg-v001'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True,'Actual typed Root Death5 prereg required; pending template cannot execute')
 own=check_frozen(C,'Death-native-observer-freeze-v001.json');need(p['candidate_freeze_pin']==own,'Root bound another observer/tool candidate');pin(p['candidate_freeze_pin'])
 sourcefreeze=check_frozen(C,'Death-observer-source-freeze-v001.json');need(p['source_probe_freeze_pin']==sourcefreeze,'Root bound another independent native Actor')
 inputs=read(C/'read-only-input-pins-v001.json');roles=inputs['inputs']
 for r in roles.values():pin(r)
 for r in inputs['actual_DTO_headers']:pin(r)
 manifest_path=snapshot/'compiled-source-manifest.json';need(p['compiled_manifest_pin']==fact(manifest_path)and p['compiled_manifest_sha256']==fact(manifest_path)['sha256'],'Root prereg/snapshot exact pin differs');m=read(manifest_path)
 need(type(p['expected_source_files'])is int and p['expected_source_files']>0 and p['expected_source_files']==m['source_files'],'Fresh actualSource count missing/differs; neverreuse246/253')
 need(p['expected_production_files']==m['production_files']==1326 and p['expected_strict_registered_tests']==m['strict_registered_tests']==190,'Fresh exact1326 Production/full190 required')
 files={r['path'].replace('\\','/'):r for r in m['files']};need(len(files)==len(m['files']),'Compiled snapshot repeats input paths')
 for row in m['files']:pin(row)
 actual_sources={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Source').rglob('*')if x.is_file()};source_set={n for n in files if n.startswith('UnrealGame/Source/')}
 actual_production={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Content/Production').rglob('*')if x.is_file()};prod_set={n for n in files if n.startswith('UnrealGame/Content/Production/')}
 need(actual_sources==source_set and len(source_set)==m['source_files']and actual_production==prod_set and len(prod_set)==1326,'Actual source/Production disk membership differs from compiled snapshot')
 dll='UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';need(dll in files,'Actual compiled DLL missing from snapshot');pin(files[dll]);build=read(pin(m['current_build']));need(build.get('ExitCode')==0,'Actual compiled build receipt is not exit0')
 suite=read(pin(m['full_suite']));need(suite['succeeded']==190 and all(suite[k]==0 for k in ['succeededWithWarnings','failed','notRun','inProcess'])and len(suite['tests'])==190,'Actual full190 strict GREEN missing')
 need(all(t['state']=='Success'and t['errors']==t['warnings']==0 for t in suite['tests']),'Actual full registry contains non-GREEN/warnings')
 for n in TESTS:need(sum(t['fullTestPath']=='CodexDungeon.Content.FairytaleSwordDeathV001.'+n for t in suite['tests'])==1,'Exact Death semantic group missing: '+n)
 admitted={path(r['path']).relative_to(ROOT).as_posix():r for r in p['admitted_source_files']};need(len(admitted)==len(p['admitted_source_files'])and {'UnrealGame/Source/CodexDungeon/'+n for n in REQUIRED}<=set(admitted),'Actual Death source list incomplete/duplicate')
 for name,row in admitted.items():need(name in files and all(row[k]==files[name][k]for k in ['bytes','sha256']),'Admitted source differs from fresh compiled input');pin(row)
 for n in ['DungeonHeroDeathProbeV001.h','DungeonHeroDeathProbeV001.cpp']:need(fact(ROOT/'UnrealGame/Source/CodexDungeon'/n)['sha256']==fact(C/'new-source'/n)['sha256'],'Actual independent Actor differs from frozen candidate')
 production=pin(p['Death40_production_candidate_freeze_pin']);check_frozen(production.parent,production.name);pd=read(production)
 admission_path=pin(p['Root_source_admission_pin']);need(p['Root_source_admission_pin']==roles['Root_source_admission'],'Exact Root source admission differs');admission=read(admission_path)
 need(admission['schema']=='Root-Death40-production-and-observer-source-admission-v001'and admission['production_freeze']==p['Death40_production_candidate_freeze_pin']and admission['observer_source_freeze']==sourcefreeze and admission['source_files']==m['source_files']and admission['production_files']==1326 and admission['old241_source_byte_unchanged']is True and admission['original_RED_tests_unchanged']is True,'Root exact production/probe controlled admission missing')
 admitted_by_root={path(r['path']).relative_to(ROOT).as_posix():r for r in admission['new_source_files']+admission['existing_modified_files']};need(admitted==admitted_by_root,'Prereg current16 source pins differ from actual Root controlled admission')
 for row in pd['admitted_source_file_pins']:
  if path(row['path']).name!='DungeonHUD.cpp':pin(row)
 # Production HUD has exactly the independently frozen two-line startup delta.
 before=(production.parent/'changed-source/DungeonHUD.cpp').read_bytes();eol=b'\r\n'if b'\r\n'in before else b'\n';include=b'#include "DungeonHeroHurtProbeV001.h"';branch=b'        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroHurtProofV001")))GetWorld()->SpawnActor<ADungeonHeroHurtProbeV001>();'
 need(before.count(include)==before.count(branch)==1,'Frozen production HUD startup anchors are ambiguous')
 expected=before.replace(include,include+eol+b'#include "DungeonHeroDeathProbeV001.h"').replace(branch,b'        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroDeathProofV001")))GetWorld()->SpawnActor<ADungeonHeroDeathProbeV001>();'+eol+b'        else if(FParse::Param(FCommandLine::Get(),TEXT("DungeonHeroHurtProofV001")))GetWorld()->SpawnActor<ADungeonHeroHurtProbeV001>();')
 need((ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_bytes()==expected,'Actual HUD exceeds frozen production plus exact probe-only startup patch')
 hud=(ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp').read_text(encoding='utf-8-sig');need('SpawnActor<ADungeonHeroDeathProbeV001>()'in hud and 'DungeonFairytaleSwordDeath' in hud and 'FinishCompilation(ReadyArmorTextures)'in hud,'Actual Death startup/preload/compilation hook missing')
 need(p['Root_scoped_trial_pin']==roles['Root_scoped_trial']and p['actual_import_receipt_pin']==roles['actual_import_receipt']and p['independent_import_receipt_pin']==roles['independent_import_receipt'],'Root fresh trial/import bindings differ')
 trial=read(pin(p['Root_scoped_trial_pin']));need(trial['schema']=='ROOT_SCOPED_DEATH40_IMPORT_AND_NATIVE_TRIAL'and trial['source_allowed_for_limited_import']is True and trial['FinalAccepted']is False and trial['formal_complete_units']==0,'Exact Root scoped limited Death40 trial missing')
 manifest=read(pin(roles['Death40_source_manifest']));profile=read(pin(roles['Death5_profile']));readyfreeze=pin(roles['Death40_source_freeze']);need(trial['source_freeze']==roles['Death40_source_freeze']and trial['source_manifest']==roles['Death40_source_manifest']and trial['runtime_profile']==roles['Death5_profile'],'Root scoped source manifest/profile differs')
 need(profile['source_manifest']==roles['Death40_source_manifest']and manifest['asset_count']==40 and profile['standing_source_extent']==416 and profile['standing_display_height']==72 and profile['weapon_scale']==.5 and len(profile['frames'])==5,'Exact Death40 source/scale identity differs')
 for row in read(readyfreeze)['files']+read(readyfreeze)['source40']:pin(row,readyfreeze.parent)
 original_import=read(pin(roles['actual_import_manifest']));receipt=read(pin(p['actual_import_receipt_pin']));independent=read(pin(p['independent_import_receipt_pin']))
 need(original_import['schema']=='Root-Death40-native-import-v001'and original_import['expected_old_count']==1286 and original_import['expected_new_count']==40 and original_import['expected_final_count']==1326 and original_import['replace_existing']is False and original_import['candidate_freeze']==roles['Death40_source_freeze'],'Exact new40/no-replacement import contract differs')
 need(receipt['success']is True and receipt['old1286_unchanged']is True and receipt['verification_passes']==2 and receipt['total_production_files']==1326 and receipt['manifest']==roles['actual_import_manifest'],'Actual import receipt is not exact1326/twoSHA')
 need(independent['success']is True and independent['old1286_unchanged_twice']is True and independent['new40_saved_twice']is True and independent['exact_total']==1326 and independent['verification_passes']==2 and independent['hash_mismatches']==0 and independent['receipt']==p['actual_import_receipt_pin']and independent['manifest']==roles['actual_import_manifest'],'Independent actual import verification differs')
 sources={a['object_path']:a for a in manifest['assets']};need(len(sources)==40 and len(receipt['assets'])==40,'Duplicate/missing source40 import entries')
 old_names=set()
 for row in original_import['old_production_files']:need(row['path']in files and all(row[k]==files[row['path']][k]for k in ['bytes','sha256']),'Old1286 bytes changed');old_names.add(row['path'])
 new_names=set()
 for a in receipt['assets']:
  source=sources[a['actual_object_path']];need(a['actual_class']=='Texture2D'and a['actual_dimensions']==[512,512]and a['source']=={'path':source['source'],'bytes':source['source_bytes'],'sha256':source['source_sha256']},'Actual saved Texture2D/source differs');saved=pin(a['saved']);rel=saved.relative_to(ROOT).as_posix();need(rel in files and all(files[rel][k]==a['saved'][k]for k in ['bytes','sha256']),'Saved Death40 bytes differ from compiled snapshot');new_names.add(rel)
 need(len(old_names)==1286 and len(new_names)==40 and prod_set==old_names|new_names and not(old_names&new_names),'Production exact old1286+new40 set differs')
 need(type(p['approach_side'])is int and p['approach_side']in [-1,1],'Explicit real left/right side required')
 return m,p,profile,manifest
def verify_draw(o,frame,profile,manifest,r):
 d=o['death_draw'];f=profile['frames'][frame];side=-r['actual_approach_side'];scale=72/416*d['ui_scale'];root=f['root_source_author'];anchor=f['weapon_anchor_source_author'];axis=f['weapon_axis_artist'];ground=d['context_ground']
 need(d['opt_in']and d['drawn']and d['atomic_preflight_ready']and d['supported']and not d['missing_reason'],'Actual Death renderer/preflight failed')
 need(d['sim']==o['sim']==r['frozen_sim']and d['player_entity']==r['player_entity']and d['frame']==frame and d['facing']==o['facing']==side and d['profile']==profile['profile_id'],'Actual draw/frame/facing/profile identity differs')
 need(d['death_active']and d['dead']and d['death_reported']and d['death_health']==0 and d['death_animation']=='death'and d['death_elapsed']==o['death_elapsed']==o['animation_time'],'Real terminal sample and animationage differ')
 need(d['run']==r['run']and d['owner']==r['owner']and d['weapon_instance']==o['weapon_instance']==r['sword_instance']and d['armor_instance']==o['armor_instance']==r['light_instance']and d['weapon_content']=='WPN-SWD-001'and d['armor_content']=='ARM-LGT-001','Actual committed equipment changed')
 need(d['tint']==d['plan_tint']==[1,1,1,1],'Terminal display is not actualwhite (persistentHitFlash forbidden)')
 need(d['visual_sword_released']is(frame>=1)and d['last_frame_held']is(frame==4),'Actual release/lastframe policy differs')
 need(point(d['root_source'],root,0.)and point(d['sword_anchor_source'],anchor,0.)and point(d['axis_artist'],axis,0.),'Author source Root/Swordanchor/axis differs')
 need(d['jump_height']==0 and d['ui_scale']==1 and near(d['canvas_size'],72*512/416,1.e-10)and near(d['source_to_screen_scale'],scale,1.e-12)and d['weapon_scale']==.5 and near(d['weapon_width'],512*scale*.5,1.e-10),'Constant72/416/Sword.50 scale differs')
 wantground=[640+(o['ground'][0]-o['camera_ground'][0])*.65,490-o['ground'][1]*.38];need(point(ground,wantground,1.e-3),'Actual projected actorGround differs')
 top=[ground[0]-(root[0]if side>0 else 512-root[0])*scale,ground[1]-root[1]*scale];at=[ground[0]+side*(anchor[0]-root[0])*scale,ground[1]+(anchor[1]-root[1])*scale]
 need(point(d['body_top'],top)and point(d['sword_anchor_screen'],at),'Actual sourceRoot/Swordanchor screen differs')
 theta=math.atan2(axis[1],axis[0]);angle=math.degrees(theta)*(1 if side>0 else -1);pivot=[99/512 if side>0 else 1-99/512,.5]
 need(near(d['weapon_angle'],angle,1.e-9)and point(d['sword_pivot_uv'],pivot,1.e-12)and d['texture_u']==(0 if side>0 else 1)and d['texture_du']==side,'One fullXreflection angle/UV/pivot differs')
 need(point(d['sword_top'],[at[i]-pivot[i]*d['weapon_width']for i in range(2)]),'ActualSword quad top/pivot differs')
 bycomponent={a['component']:a for a in manifest['assets']if a['frame']==frame};slots=d['slots'];need(len(slots)==9 and len(f['slots_bottom_to_top'])==9,'Exactlynine slots required');expected=[];swordslot=None
 for i,(spec,s)in enumerate(zip(f['slots_bottom_to_top'],slots)):
  name=spec['component'];sword=name=='IndependentSword';texture=profile['weapon_native_texture_path']if sword else bycomponent[name]['object_path'];expected.append(texture)
  need(s['slot']==i and s['component']==COMPONENTS.index(name)and s['texture']==texture and s['known_empty']is False and s['texture_ready']is True and s['drawn']is True,'Actual nine-slot dynamic order/path/readiness differs')
  need(s['draw_scale']==1 and s['scale_position']is False and point(s['uv'],[d['texture_u'],0],0.)and point(s['uv_size'],[d['texture_du'],1],0.),'Actual submitted quad UV/scale differs')
  width=d['weapon_width']if sword else 512*scale;wanttop=d['sword_top']if sword else d['body_top']
  need(point(s['top'],wanttop)and point(s['size'],[width,width])and near(s['rotation'],angle if sword else 0,1.e-4)and point(s['rotation_pivot'],pivot if sword else[0,0],1.e-12),'Actual floatquad differs from consumed sharedplan')
  if sword:swordslot=s
  else:need(point(quad_project(s,root),ground,2.e-4)and point(quad_project(s,anchor),at,2.e-4),'Actualbody submittedquad source projection differs')
 need(d['actual_stack']==o['rendered_stack']==expected and d['nonempty_count']==9,'Actual rendered stack differs from complete nine-slot plan')
 for source in [[99,256],[199,256],[99,356]]:
  x,y=source[0]-99,source[1]-256;v=[math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y];want=[at[0]+side*.5*scale*v[0],at[1]+.5*scale*v[1]];need(point(quad_project(swordslot,source),want,2.e-4),'Actual independentSword anchor/axis/perpendicular transform differs (doublemirror forbidden)')
 resident=d['resident_textures'];wantset={a['object_path']for a in manifest['assets']}|{profile['weapon_native_texture_path']};need(len(resident)==41 and {x['texture']for x in resident}==wantset and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resource_ready']is True for x in resident),'Actual complete41resident resources absent (not a document count)')
def verify(archive,snapshot,p,profile,manifest,prereg):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json')
 need(r['schema']=='hero-SWD-LGT-Death5-native-observer-v001'and r['scenario']=='NaturalGuardAttacksToHeroDeath5'and r['passed']is True and r['flow_complete']is True,'Original naturalGuard→Death5 native trial is RED')
 need(index['schema']=='hero-Death5-native-session-v001'and index['process_id']==int(r['process_id'])and index['snapshot_manifest_sha256']==p['compiled_manifest_sha256']and path(index['root_prereg'])==prereg and index['root_prereg_sha256']==fact(prereg)['sha256']and index['candidate_freeze_sha256']==p['candidate_freeze_pin']['sha256'],'Session PID/prereg/snapshot/candidate binding differs')
 need(r['requested_approach_side']==p['approach_side']==index['requested_approach_side']==r['actual_approach_side']and r['actual_approach_side']in [-1,1],'Actual requested position side differs')
 need(r['player_or_Guard_public_damage_used']is False and r['HP_poise_clock_actor_writes']is False and r['silent_video']is True and r['audio_recorded']is False and r['visual_reviewed']is False and r['formal_complete_units']==0,'Native trial scope changed')
 need(r['guard_final_HP']==185 and r['guard_incoming_count']==0,'Guard received player/diagnostic damage or HP preset')
 diag=r['diagnostic_predecessor_hits'];need(len(diag)==2 and [x['content']for x in diag]==['ENM-STN-001','ENM-STN-002']and all(x['api']=='ADungeonFighter::ApplyCombatHit'and x['before_HP']>x['after_HP']==0 and x['dead']is True for x in diag),'Only explicitly marked Knight/Bat predecessor diagnostics allowed')
 downs=[x['key']for x in r['normal_inputs']if x['down']];need(downs.count('Enter')==downs.count('E')==1 and set(downs)<={'Enter','E','A','D','W','S'}and bool(set(downs)&{'W','S'})and bool(set(downs)&{'A','D'}),'NormalEnter/E/body-awareWASD only contract differs')
 reached=[x for x in r['route_witnesses']if x['event']=='reached'and x['stage']==2];need(len(reached)==1,'Exactlyone actual completed route required');a=reached[0];dx=(a['player'][0]-a['guard'][0])*r['actual_approach_side'];need(120<=dx<=160 and abs(a['player'][1]-a['guard'][1])<=6,'Facing cannot replace actualrequested spatialside')
 events=r['guard_original_events'];need([int(e['event'])for e in events]==sorted({int(e['event'])for e in events}),'OriginalGuard issued events duplicate/reorder')
 hit_events={e['event']:e for e in events if e['kind']==11 and e['target']==r['player_entity']};confirmed=[x for x in r['guard_actual_confirmed_losses']if x['target']==r['player_entity']];receipts=r['guard_original_hit_receipts'];witnesses=r['guard_hit_witnesses']
 need(len(confirmed)==len(hit_events)==len(receipts)==len(witnesses)>1 and len({x['event']for x in confirmed})==len(confirmed),'OriginalGuard multiplehit/receipt/actualConfirmHit chain incomplete')
 hp=r['pre_guard_HP'];need(hp>0,'Actual preGuardpositiveHP missing');last_at=-1;lethal=[]
 for i,(loss,w)in enumerate(zip(confirmed,witnesses)):
  e=hit_events[loss['event']];a=e['action'];kind=a['kind'];need(kind in[1,2]and(i>0 or kind==1),'FirstactualGuardAxe then naturalAxe/Stomp expected')
  need(e['entity']==r['guard_entity']and loss['source_kind']==11 and loss['at']==e['at']==w['at']>last_at and loss['attack']==a['attack_id']==w['attack']and loss['event']==w['event']and a['active_at']<=e['at']<a['active_end'],'Actualissued hit/action/ConfirmHit identity/window differs');last_at=e['at']
  need(sum(x['attack']==a['attack_id']and x['target']==r['player_entity']and x['at']==e['at']for x in receipts)==1,'Original outgoingHitReceipt not unique/exact')
  times=[.5,1.,1.2,2.6,3.1]if kind==1 else[.45,.9,1.05,2.55,3.];damage,stagger=(24,30)if kind==1 else(18,25)
  need(a['damage']==damage and a['stagger']==stagger and all(near(a[k]-a['start'],v,1.e-8)for k,v in zip(['lock_at','active_at','active_end','recovery_end','cooldown_end'],times)),'Actual originalGuard locked stats/deadlines changed')
  expected=min(hp,damage/1.14);need(near(loss['actual_HP_loss'],expected,1.e-4)and loss['actual_HP_loss']==w['actual_HP_loss']and near(w['chain_before'],hp,1.e-4),'ActualHP loss not explained by lockedGuard damage+one14armor mitigation')
  hp=max(0.,hp-loss['actual_HP_loss']);need(near(w['chain_after'],hp,1.e-4),'OriginalconfirmedHP chain differs')
  if hp<=1.e-4:lethal.append(e)
 need(len(lethal)==1 and lethal[0]['event']==confirmed[-1]['event'] and lethal[0]['event']==r['lethal_event']and lethal[0]['action']['attack_id']==r['lethal_attack']and lethal[0]['at']==r['lethal_at']and near(r['confirmed_HP_loss'],r['pre_guard_HP'],1.e-4),'Unique actuallethal end boundary is missing')
 startup=r['startup_resident_textures'];sources={a['object_path']:a for a in manifest['assets']};need(len(startup)==41 and len({x['texture']for x in startup})==41 and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resident']is True for x in startup),'BeforeEnter actual41GPUresident facts missing')
 for s in startup:
  if s.get('sword'):need(s['texture']==profile['weapon_native_texture_path'],'ReusedSword textureidentity differs');continue
  source=sources[s['texture']];need(s['frame']==source['frame']and COMPONENTS[s['component']]==source['component']and s['source_SHA']==source['source_sha256']and s['source_RGBA_SHA']==source['source_RGBA_sha256']and s['source_alpha_nonzero']==source['source_alpha_nonzero_pixels']and s['known_empty']is False,'Startup source40 metadata differs')
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>5 and all(b>a for a,b in zip(offsets,offsets[1:]))and r['capture_timing']['use_fixed_time_step']is False,'Originalcallback/nativepacing facts differ')
 before=r['equipment_before_death'];world=r['world_pickups_before_death'];need(before['armor']==r['light_instance']and r['sword_instance']in[before['weapon0'],before['weapon1']]and not any(x['action']==2 or int(x['dropped'])or int(x['dropped_source'])for x in before['operations'])and not any(s['available']and s['content']=='WPN-SWD-001'for s in before['sources']),'Originalequipment already has a droppedSword')
 deaths=[];frames=set();draws=set();seen_dead=False;seen_over=False;dead_edges=0;over_edges=0
 for o,t in zip(obs,offsets):
  need(o['wall_offset_s']==t and not o['interface_visible']and o['text_calls']==0 and not o['combat_range_debug']and o['combat_range_lines']==0,'Actualcallback timing/hiddenHUD/defaultoffrange differs')
  if o['dead']and not seen_dead:dead_edges+=1
  if o['game_over']and not seen_over:over_edges+=1
  need(not seen_dead or o['dead'],'Hero revived inside one terminaltrial');need(not seen_over or o['game_over'],'GameOver reset inside one trial');seen_dead=o['dead'];seen_over=o['game_over']
  if o['dead']:
   need(o['phase']==9 and o['HP']==0 and o['game_over']and o['animation']=='death'and o['death_query_ok']and o['death_active']and o['death_reported']and o['death_query_health']==0 and o['death_elapsed']==o['animation_time']and not any(o[k]for k in['held_A','held_D','held_W','held_S']),'ActualterminalHP0/query/GameOver/neutralinput differs')
   need(o['sim']==r['frozen_sim']and o['guard_time']==r['frozen_guard_time']and o['player_combat_time']==r['frozen_combat_time']and o['player_weapon_time']==r['frozen_weapon_time']and o['player_dodge_time']==r['frozen_dodge_time'],'Gameplay/kernel clocks continued during terminaldisplay')
   need(o['equipment']==before and o['world_pickup_identity']==world and o['guard_HP']==185 and o['guard_received_count']==0 and o['armor']==14 and o['poise_threshold']==30 and o['physical_vulnerability']==1,'Inventory/worldSword drop/GuardHP/stats changed during death')
   f=original_frame(o['death_elapsed']);verify_draw(o,f,profile,manifest,r);d=o['death_draw'];need(d['draw_id']not in draws,'RepeatednativeDeath drawcannot earn phase credit');draws.add(d['draw_id']);frames.add(f);deaths.append(o)
  else:need(o['HP']>0 and not o['game_over']and not o['death_query_ok']and not o['death_active']and not o['death_draw']['drawn'],'Death renderer activated before reall lethal boundary')
 need(dead_edges==over_edges==r['observed_dead_transitions']==r['observed_game_over_transitions']==1 and frames==set(range(5))and r['DeathMask']==31,'ActualsingleHP0/GameOver/fivephase coverage differs')
 need(all(b['death_elapsed']>a['death_elapsed']for a,b in zip(deaths,deaths[1:])),'ActualterminalAnimationTime didnot continuouslyadvance')
 hold=[o for o in deaths if o['death_draw']['frame']==4 and o['death_draw']['last_frame_held']];need(len(hold)==r['HoldSeen']>=2 and hold[0]['death_elapsed']==r['MinimumHoldAge']>=.8 and deaths[-1]['death_elapsed']==r['MaximumDeathAge']>=1.2 and hold[-1]['death_elapsed']-hold[0]['death_elapsed']>=.35,'Actual.8+finalhold proof missing; no gameplaydeadline substitution')
 subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tooling/verify-Death-native-pixels-v001.py'),'--archive',str(archive)],check=True,capture_output=True,text=True)
 optical=runpy.run_path(str(C/'tooling/verify-Death-source-pixels-v001.py'))['verify_source_pixels'](archive,profile,manifest,deaths)
 return dict(passed=True,scenario=r['scenario'],native_Death_frames=sorted(frames),native_Death_draws=len(deaths),actual_guard_committed_hits=len(confirmed),observed_dead_transition_count=dead_edges,observed_GameOver_transition_count=over_edges,real_terminal_max_age=r['MaximumDeathAge'],actual_hold_callbacks=len(hold),gameplay_and_kernel_clocks_frozen=True,actual41resident_and9slots_verified=True,actual_quad_source_projection_and_fullXmirror_verified=True,actual_white_terminal_material_verified=True,inventory_and_world_pickup_identity_unchanged=True,native_PNG_CRC_FIFO_verified=True,optical_source_projection=optical,source_contact_floor_hidden_socket_physics_verified=False,audio_recorded=False,visual_reviewed=False,FinalAccepted=False)
def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--root-prereg',required=True);a.add_argument('--archive');a.add_argument('--source-only',action='store_true');a.add_argument('--write-receipt',action='store_true');q=a.parse_args();snapshot=path(q.snapshot);prereg=path(q.root_prereg);m,p,profile,manifest=preflight(snapshot,prereg)
 if q.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=m['strict_registered_tests'],production_files=m['production_files'],source_files=m['source_files'],Death_source40=40,approach_side=p['approach_side'],UE_started=False)));return
 need(q.archive,'Actual original native archive required');archive=path(q.archive);result=verify(archive,snapshot,p,profile,manifest,prereg)
 if q.write_receipt:
  with(archive/'原件/Death-independent-native-verification-v001.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
