"""Independent readonly Stomp50 native proof; pending Root inputs cannot run UE."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,subprocess,sys
R=Path('F:/Ourgame');C=Path(__file__).resolve().parent.parent
def need(v,w):
 if not v:raise ValueError(w)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def resolve(p):
 p=Path(p);return(p if p.is_absolute()else R/p).resolve()
def fact(p):
 p=resolve(p);b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def pin(x,base=R):
 need(isinstance(x,dict)and set(x)=={'path','bytes','sha256'},'Exact immutable input pin required');p=Path(x['path']);p=(p if p.is_absolute()else base/p).resolve();f=fact(p);need(f['bytes']==x['bytes']and f['sha256']==x['sha256'],'Pinned input differs: '+str(p));return p
def same_pin(a,b):return fact(pin(a))==fact(pin(b))
def near(a,b,e=1.e-4):return math.isfinite(a)and math.isfinite(b)and abs(a-b)<=e
def pt(a,b,e=1.e-4):return len(a)==len(b)==2 and all(near(x,y,e)for x,y in zip(a,b))
def frozen(name):
 p=C/name
 for x in read(p)['files']:pin(x,C)
 return fact(p)
def source_check(snapshot,prereg):
 p=read(prereg);need(p['schema']=='guard-Stomp50-Root-prereg-v001'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True and p['FinalAccepted']is False,'Actual typed Root approval required; pending template cannot execute')
 own=frozen('Stomp-native-proof-freeze-v001.json');need(same_pin(p['candidate_freeze_pin'],own),'Prereg binds another tool candidate');base_source=frozen('Stomp-native-source-freeze-v001.json');source=frozen('source-boundary-fix-v002/Stomp-source-boundary-fix-freeze-v002.json');need(read(C/'source-boundary-fix-v002/Stomp-source-boundary-fix-freeze-v002.json')['base_source_freeze']==base_source and same_pin(p['source_freeze_pin'],source),'Prereg binds another Source candidate')
 m=read(snapshot/'compiled-source-manifest.json');need(same_pin(p['compiled_manifest_pin'],fact(snapshot/'compiled-source-manifest.json')),'Fresh exact compiled snapshot binding required')
 for key in ['source_files','production_files','strict_registered_tests']:need(type(p['expected_'+key])is int and p['expected_'+key]==m[key],'Actual fresh count missing/differs: '+key)
 need(m['source_files']>=262 and m['production_files']>=1332 and m['strict_registered_tests']>=193,'New overlay/probe/source6/full193 must actually be compiled/imported')
 files={x['path'].replace('\\','/'):x for x in m['files']};need(len(files)==len(m['files']),'Snapshot repeats paths')
 for x in m['files']:pin(x)
 actualSource={p.relative_to(R).as_posix()for p in(R/'UnrealGame/Source').rglob('*')if p.is_file()};actualContent={p.relative_to(R).as_posix()for p in(R/'UnrealGame/Content/Production').rglob('*')if p.is_file()};need(actualSource=={n for n in files if n.startswith('UnrealGame/Source/')}and actualContent=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Current exact Source/Production membership differs')
 need(len(actualSource)==m['source_files']and len(actualContent)==m['production_files'],'Snapshot count differs from exact current membership');need('UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'in files,'Current compiled DLL absent')
 need(read(pin(m['current_build']))['ExitCode']==0,'Actual UBT build is not exit0');suite=read(pin(m['full_suite']));need(suite['succeeded']==m['strict_registered_tests']and all(suite[k]==0 for k in ['succeededWithWarnings','failed','notRun','inProcess'])and len(suite['tests'])==suite['succeeded']and all(t['state']=='Success'and t['errors']==t['warnings']==0 for t in suite['tests']),'Fresh strict full registry is not all GREEN')
 required=['RealNativeHalfOpenClockAndEventIdentity','Versioned50BindingsAndAtomicMirroredFloor','RealActorReceiptRecoveryAndInterruptedExclusion']
 for name in required:need(sum(t['fullTestPath']=='CodexDungeon.Content.FairytaleGuardStompV004.'+name for t in suite['tests'])==1,'Actual original Stomp semantic test missing')
 before=read(R/'source-assets/production/backups/v138-HeroDeath190G/compiled-source-manifest.json');old={x['path']:x for x in before['files']}
 for name in ['DungeonStoneGuard.h','DungeonStoneGuard.cpp','DungeonStoneGuardDriver.h','DungeonStoneGuardDriver.cpp','DungeonFairytaleGuardFullPoseV003.h','DungeonFairytaleGuardFullDataV003.inl','DungeonGuardArtKnown44Probe.h','DungeonGuardArtKnown44Probe.cpp','Tests/DungeonFairytaleGuardFullV003Tests.cpp']:
  k='UnrealGame/Source/CodexDungeon/'+name;need(k in files and files[k]['sha256']==old[k]['sha256'],'Old kernel/selector/44 source entry/tests changed: '+name)
 for name in ['DungeonGuardStompProbeV001.h','DungeonGuardStompProbeV001.cpp']:need(fact(C/('source-boundary-fix-v002'if name.endswith('.cpp')else 'new-source')/name)['sha256']==files['UnrealGame/Source/CodexDungeon/'+name]['sha256'],'Actual new Probe differs from Source freeze')
 need(p['approach_side']in[-1,1]and type(p['approach_side'])is int,'Explicit requested spatial side required')
 admission=read(pin(p['Root_source_admission_pin']));need(admission['schema']=='Root-GuardStomp-observer-admission-v001'and admission['success']is True and admission['FinalAccepted']is False and same_pin(admission['source_freeze'],base_source)and same_pin(admission['same_Aid2_Ready_fix'],source),'Root actual scoped Source admission missing');admitted=p['admitted_source_files'];current={pin(x).relative_to(R).as_posix():x for x in admitted}
 required_current=['DungeonFairytaleGuardStompProfileV004.h','DungeonFairytaleGuardStompDataV004.inl','Tests/DungeonFairytaleGuardStompV004Tests.cpp','DungeonFairytaleGuardFullProfileV003.h','DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonGuardStompProbeV001.h','DungeonGuardStompProbeV001.cpp'];need({'UnrealGame/Source/CodexDungeon/'+n for n in required_current}<=set(current),'Fresh exact10 Stomp Source inputs absent')
 for x in admission['admitted']:
  k=resolve(x['path']).relative_to(R).as_posix();need(k in current and same_pin(current[k],x),'Actual observer-admitted Source5 changed after controlled patch')
 for x in admitted:
  k=pin(x).relative_to(R).as_posix();need(k in files and files[k]['sha256']==x['sha256'],'Admitted current source not in compiled snapshot')
 profile=read(pin(p['profile_contract_pin']));need(profile['schema']=='Root-GuardStomp50-profile-contract-v001'and profile['RootApproved']is True and profile['is_template']is False and profile['profile_id']=='GuardStomp50V004'and profile['source_count']==50 and profile['logical_budget']==57 and len(profile['rows'])==13 and profile['FinalAccepted']is False,'Actual approved typed overlay contract required')
 rows={x['clip']:x for x in profile['rows']};counts={'Wake':6,'Ready':4,'AxeWindup':6,'AxeActive':4,'AxeRecovery':4,'StompWindup':6,'StompActive':2,'StompRecovery':4,'Stunned':4,'Death':6,'InterruptedRecovery':4};need(set(rows)==set(counts)|{'Dormant','Move'} and rows['Move']['frames']==[]and rows['Move']['trial_allowed']is False and rows['Move']['final_accepted']is False,'Exact thirteen rows/Move gap must remain explicit')
 expected={}
 for row in profile['rows']:
  if row['clip']=='Move':continue
  need(row['trial_allowed']is True and row['final_accepted']is False and row['trial_approval_record'],'Each known row needs explicit limited Root trial')
  if row['clip']=='Dormant':need(row['alias_target']=='Wake'and row['alias_frame']==0 and row['frames']==[],'Only Dormant→Wake0 alias legal');continue
  need(type(row['native_source_id'])is int and row['native_source_id']>0 and row['canvas']==[512,512]and row['target_body_height']==100.8 and row['standing_extent']>0 and len(row['frames'])==counts[row['clip']]and [f['frame']for f in row['frames']]==list(range(counts[row['clip']])),'Actual complete ordered known row source/geometry missing');pin(row['registration_evidence']);pin(row['source_index'])
  for f in row['frames']:
   need(f['object_path']not in expected,'Duplicate frame object path');source_png=pin(f['source']);
   from PIL import Image
   with Image.open(source_png)as image:need(image.mode=='RGBA'and image.size==(512,512)and hashlib.sha256(image.tobytes()).hexdigest()==f['RGBA_sha256'],'Actual source RGBA/canvas differs from typed mapping')
   need(len(f['RGBA_sha256'])==64 and len(f['floor_pivot'])==2 and all(0<=z<=512 for z in f['floor_pivot'])and f['pivot_authority']in[1,2,3],'Source frame/root authority missing');expected[f['object_path']]=(row,f)
 need(len(expected)==50 and len(rows['StompWindup']['frames'])==6 and len(rows['StompActive']['frames'])==2 and len(rows['StompRecovery']['frames'])==4,'Complete WU6/A2/R4 and50 unique source bindings required')
 im=read(pin(p['actual_import_manifest_pin']));need(im['schema']=='Root-GuardStomp6-import-v001'and(im['expected_old_count'],im['expected_new_count'],im['expected_final_count'])==(1326,6,1332),'Actual bounded Root import manifest missing');trial=read(pin(im['root_trial_registration']));need(trial['limited_import_approved']is True and trial['FinalAccepted']is False,'Actual limited Root import approval absent');pin(im['source_manifest']);pin(im['old_compiled_snapshot']);imp=read(pin(p['actual_import_receipt_pin']));need(imp['schema']=='guard-Stomp6-actual-import-v001'and same_pin(imp['manifest'],p['actual_import_manifest_pin'])and same_pin(imp['importer'],p['actual_importer_pin'])and same_pin(p['actual_importer_pin'],read(C/'host-static-verification-v001.json')['checks']['actual_importer_current_interface_only_not_executed']),'Actual receipt belongs to another importer/manifest');ind=read(pin(p['independent_import_receipt_pin']));need(imp['success']is True and ind['schema']=='Stomp6-independent-import-twoSHA-v001'and ind['success']is True and imp['verification_passes']==ind['verification_passes']==2 and ind['hash_mismatches']==0 and same_pin(ind['receipt'],p['actual_import_receipt_pin'])and same_pin(ind['manifest'],p['actual_import_manifest_pin']),'Actual six-source import/two-SHA independent receipt missing')
 need(imp['old1326_unchanged']is True and imp['actual_total']==1332 and ind['old1326_unchanged_twice']is True and ind['new6_saved_twice']is True and ind['exact_total']==1332 and len(im['assets'])==len(imp['assets'])==6,'New exact6 no-replacement import must preserve old1326')
 newpaths={f['object_path']:f for name in ['StompActive','StompRecovery']for f in rows[name]['frames']};manifest_assets={x['object_path']:x for x in im['assets']};need(len(manifest_assets)==6 and {a['actual_object_path']for a in imp['assets']}==set(manifest_assets)==set(newpaths),'Actual new6 object set differs from Root source rows');need(sorted((x['component'],x['frame'])for x in im['assets'])==[('StompActive',0),('StompActive',1)]+[('StompRecovery',i)for i in range(4)],'Actual six import phase identities differ')
 newcontent=set()
 for a in imp['assets']:
  f=newpaths[a['actual_object_path']];mi=manifest_assets[a['actual_object_path']];src=pin(f['source']);need(a['actual_class']=='Texture2D'and a['actual_dimensions']==[512,512]and same_pin(a['source'],f['source'])and same_pin(mi['source'],f['source'])and mi['source_RGBA_sha256']==f['RGBA_sha256']and len(a['actual_import_filenames'])==1 and resolve(a['actual_import_filenames'][0])==src,'Actual imported Texture2D/provenance differs');settings=a['actual_settings'];need(all(v in settings[k]for k,v in [('compression_settings','TC_EDITOR_ICON'),('mip_gen_settings','TMGS_NO_MIPMAPS'),('lod_group','TEXTUREGROUP_UI'),('filter','TF_BILINEAR')])and settings['never_stream']==settings['srgb']=='True','Actual UI/bilinear/noMips/sRGB/native texture settings differ');k=pin(a['saved']).relative_to(R).as_posix();want='UnrealGame/Content/'+a['actual_object_path'].split('.',1)[0].removeprefix('/Game/')+'.uasset';need(k==want and k in files and files[k]['sha256']==a['saved']['sha256'],'New saved package differs from exact object/compiled input');newcontent.add(k)
 oldcontent={k:x for k,x in old.items()if k.startswith('UnrealGame/Content/Production/')};need(len(oldcontent)==1326,'Before v1381326 manifest missing');manifest_old={pin(x).relative_to(R).as_posix():x for x in im['old_production_files']};need(len(manifest_old)==len(im['old_production_files'])==1326 and set(manifest_old)==set(oldcontent)and all(manifest_old[k]['sha256']==x['sha256']and manifest_old[k]['bytes']==x['bytes']for k,x in oldcontent.items()),'Root import old1326 pins differ from v138')
 for k,x in oldcontent.items():need(k in files and files[k]['sha256']==x['sha256'],'Old1326 bytes changed')
 additional={pin(x).relative_to(R).as_posix()for x in p['explicit_additional_production_pins']};need(actualContent==set(oldcontent)|newcontent|additional,'Unexpected or unbound Production files')
 return m,p,profile,rows,expected
def phase_interval(clip,a):
 return {'StompWindup':(a['start'],a['active_at'],[0,.15,.3,.45,.6,.75],2),'StompActive':(a['active_at'],a['active_end'],[0,.075],4),'StompRecovery':(a['active_end'],a['recovery_end'],[0,.375,.75,1.125],5)}[clip]

def phase_frame(clip,a,t):
 lo,hi,starts,_=phase_interval(clip,a);need(lo<=t<hi,'Actual phase sample outside half-open original window');return max(i for i,z in enumerate(starts)if t>=lo+z)

def verify_draw(d,o,row,f):
 s=d['Selection'];need(d['RequestedClip']==s['Clip']and d['AssetClip']==('Wake'if s['Clip']=='Dormant'else s['Clip'])and d['AssetFrame']==(0 if s['Clip']=='Dormant'else s['Frame']),'Actual requested/native clip was substituted by another source row');need(d['ProfileId']=='GuardStomp50V004'and d['OptIn']and d['TrialAllowed']and d['RequestedRowTrialAllowed']and not d['FinalAccepted']and d['RegistrationReady']and d['TextureReady']and d['Drawn']and d['QuadSubmitted']and not d['ProceduralFallback']and d['WholebodyIncludesAxe']and not d['MissingReason'],'Actual approved wholebody quad did not render')
 need(d['TexturePath']==f['object_path']and d['SourceSHA256']==f['source']['sha256']and d['SourceRGBASHA256']==f['RGBA_sha256']and d['NativeSourceId']==row['native_source_id']and d['SourceFloorPivot']==f['floor_pivot']and d['PivotAuthority']==f['pivot_authority']and d['DrawStack']==[f['object_path']],'Actual source/one-layer ownership/registered floor differs')
 need(d['TrialApprovalRecord']==row['trial_approval_record']and d['RegistrationEvidenceSHA256']==row['registration_evidence']['sha256']and d['SourceIndexSHA256']==row['source_index']['sha256'],'Actual row approval/evidence differs')
 scale=100.8/row['standing_extent'];need(d['StandingExtent']==row['standing_extent']and d['TargetBodyHeight']==100.8 and near(d['RowScale'],scale,1.e-12)and near(d['CanvasSize'],512*scale,1.e-10)and d['UIScale']==1,'Constant body-only ONErow scale differs')
 ground=[640+(o['guard_ground'][0]-o['camera_ground'][0])*.65,490-o['guard_ground'][1]*.38];need(pt(d['GroundScreen'],ground,1.e-3),'Actual native actor ground projection differs');face=s['Facing'];need(face in[-1,1],'Actual nativeFacing missing');px,py=f['floor_pivot'];top=[ground[0]-(px if face>0 else 512-px)*scale,ground[1]-py*scale]
 need(pt(d['TopScreen'],top,1.e-3)and pt(d['QuadTop'],top,1.e-3)and pt(d['QuadSize'],[512*scale,512*scale])and pt(d['QuadUV'],[0 if face>0 else 1,0],0.)and pt(d['QuadUVSize'],[face,1],0.),'Actual submitted float quad/floor/mirror differs')
 need(d['QuadRotationDegrees']==0 and d['QuadRotationPivot']==[0,0]and d['QuadDrawScale']==1 and d['QuadScalePosition']is False and d['QuadTint']==[1,1,1,1],'Actual quad defaults/white material differs')
 residents=d['RowResidents'];want={x['object_path']for x in row['frames']};need(len(residents)==len(want)and{z['TexturePath']for z in residents}==want and all(z['ClassName']=='Texture2D'and z['Width']==z['Height']==512 and z['ResourceReady']is True and z['PendingInitialization']is False for z in residents),'Actual complete selected row residency absent')
def verify(archive,p,profile,rows,expected,prereg,snapshot):
 original=archive/'原件';r=read(original/'runtime-report.json');session=read(archive/'index.json');need(r['schema']=='guard-Stomp50-native-observer-v001'and r['scenario']=='FirstNaturalStompAid2Cycle'and r['passed']and r['flow_complete'],'Native Stomp cycle did not pass')
 need(session['schema']=='guard-Stomp50-native-session-v001'and session['process_id']==int(r['process_id'])and session['candidate_freeze_sha256']==p['candidate_freeze_pin']['sha256']and session['root_prereg_sha256']==fact(prereg)['sha256']and session['snapshot_manifest_sha256']==fact(snapshot/'compiled-source-manifest.json')['sha256'],'Actual session PID/candidate/prereg/compiled provenance differs')
 need(r['actual_approach_side']==r['requested_approach_side']==session['requested_approach_side']==p['approach_side'],'Requested side is not actual side');need(not r['player_or_Guard_public_damage_used']and not r['HP_poise_clock_actor_writes']and r['guard_final_HP']==185 and r['guard_incoming_count']==0 and r['silent_video']and not r['audio_recorded']and not r['visual_reviewed']and r['formal_complete_units']==0,'Natural unmodified Guard/live hero scope differs')
 diag=r['diagnostic_predecessor_hits'];need(len(diag)==2 and[x['content']for x in diag]==['ENM-STN-001','ENM-STN-002']and all(x['api']=='ADungeonFighter::ApplyCombatHit'and x['after_HP']==0 and x['dead']for x in diag),'Only declared Knight/Bat predecessor diagnostics allowed')
 keys=[x['key']for x in r['normal_inputs']if x['down']];need(keys.count('Enter')==keys.count('E')==1 and set(keys)<={'Enter','E','W','A','S','D'}and set(keys)&{'A','D'}and set(keys)&{'W','S'},'Only normal start/E/body-aware input route allowed')
 start=r['startup_resident_textures'];need(len(start)==50 and{x['texture']for x in start}==set(expected)and all(x['class']=='Texture2D'and x['width']==x['height']==512 and x['resident']for x in start),'All50 actual GPU resident resources missing before Enter')
 for x in start:
  row,f=expected[x['texture']];need(x['clip']==row['clip']and x['frame']==f['frame']and x['native_source_id']==row['native_source_id']and x['source_SHA']==f['source']['sha256']and x['source_RGBA_SHA']==f['RGBA_sha256'],'Startup compiler profile differs from actual source contract')
 events=r['guard_original_events'];first=next(e for e in events if e['kind']==2 and e['action']['kind']==2);a=first['action'];aid=a['attack_id'];need(aid==r['cycle_attack_id']=='2'and a['kind']==2,'Selected cycle is not first original natural Aid2 Stomp')
 need(a['damage']==18 and a['stagger']==25 and all(near(a[k]-a['start'],z,1.e-8)for k,z in zip(['lock_at','active_at','active_end','recovery_end','cooldown_end'],[.45,.9,1.05,2.55,3.])),'Original Stomp deadlines/stats changed')
 bykind={}
 for k in[2,3,4,5,6]:
  found=[e for e in events if e['kind']==k and e['action']['attack_id']==aid];need(len(found)==1,'Original phase event absent/duplicate');bykind[k]=found[0]
 need(bykind[2]['at']==a['start']and bykind[3]['at']==a['lock_at']and bykind[4]['at']==a['active_at']and bykind[4]['end']==a['active_end']and bykind[5]['at']==a['active_end']and bykind[5]['end']==a['recovery_end']and bykind[6]['at']==a['recovery_end'],'Original issued phase events/endpoints differ')
 window=[w for w in r['guard_original_windows']if w['attack']==aid];need(len(window)==1,'Original single Stomp window absent/duplicate');w=window[0];locked=bykind[3]['action'];need(w['event']==bykind[4]['event']and w['start']==a['active_at']and w['end']==a['active_end']and w['center']==locked['locked_center']and w['center_z']==locked['locked_center_z']and w['facing']==locked['facing']==a['facing']and w['damage']==18 and w['stagger']==25,'Actual locked Target/center/window identity differs')
 need(not any(x['attack']==aid for x in r['guard_original_closures']),'Uninterrupted proof cycle was canceled')
 hits=[h for h in r['guard_actual_confirmed_losses']if h['attack']==aid];receipts=[h for h in r['guard_original_hit_receipts']if h['attack']==aid];need(len(hits)==len(receipts)==r['StompConfirmedHits']==1 and a['active_at']<=hits[0]['at']<a['active_end']and receipts[0]['at']==hits[0]['at']and receipts[0]['target']==hits[0]['target']==r['player_entity'],'Actual Stomp hit half-open/target/unique receipt differs')
 hit_events={e['event']:e for e in events if e['kind']==11};confirmed={x['event']:x for x in r['guard_actual_confirmed_losses']};need(len(confirmed)==len(r['guard_hit_witnesses'])==len(hit_events),'Actual ConfirmHit/issued Hit/HP witness sets differ')
 hp=r['pre_guard_HP'];need(hp>0,'Actual preGuardHP missing')
 for loss in r['guard_hit_witnesses']:
  e=hit_events[loss['event']];confirmation=confirmed[loss['event']];need(e['target']==confirmation['target']==r['player_entity']and e['at']==confirmation['at']==loss['at']and e['action']['attack_id']==confirmation['attack']==loss['attack']and confirmation['actual_HP_loss']==loss['actual_HP_loss']and e['action']==loss['action'],'Actual issuedHit/ConfirmHit/HP loss identity differs');k=loss['action']['kind'];need(k in[1,2]and near(loss['chain_before'],hp),'Natural HP chain interrupted');want=(24 if k==1 else 18)/1.14;need(near(loss['actual_HP_loss'],want)and near(loss['chain_after'],hp-want)and loss['chain_after']>0,'Actual HP not original Guard damage mitigated once by armor14');hp=loss['chain_after']
 obs=r['observations'];offsets=r['capture_timing']['frame_wall_offsets_s'];need(len(obs)==len(offsets)>1 and all(b>a for a,b in zip(offsets,offsets[1:]))and not r['capture_timing']['use_fixed_time_step'],'Actual native callback pacing differs');coverage=[];masks={'StompWindup':0,'StompActive':0,'StompRecovery':0};seen=set();qualified={}
 for i,o in enumerate(obs):
  need(o['wall_offset_s']==offsets[i]and o['player_HP']>0 and not o['dead']and not o['game_over']and not o['interface_visible']and o['text_calls']==0 and not o['combat_range_debug']and o['combat_range_lines']==0,'Actual live/hiddenHUD/defaultoffRange/PNGcallback facts differ')
  if 'guard_time'not in o:continue
  need(o['guard_HP']==185 and o['guard_incoming_count']==0,'Guard changed during native capture')
  for d in o['guard_draws']:
   if d['EntityId']!=r['guard_entity']:continue
   s=d['Selection'];need(s['Valid']and s['SampleTime']==o['guard_time']and int(d['DrawId'])not in seen,'Actual native draw/sample identity absent/repeated');seen.add(int(d['DrawId']))
   if not d['Drawn']:continue
   clip=d['AssetClip'];row=rows[clip];f=row['frames'][d['AssetFrame']];verify_draw(d,o,row,f)
   dx=(o['player_ground'][0]-o['guard_ground'][0])*p['approach_side'];dy=o['player_ground'][1]-o['guard_ground'][1];eligible=120<=dx<=160 and abs(dy)<=6
   if s['AttackId']==aid and s['Clip']in masks:
    need(eligible and o['actual_side_eligible'],'Actual correct side/dy absent; Facing is not position credit');name=s['Clip'];lo,hi,starts,eventkind=phase_interval(name,a);need(lo<=s['SampleTime']<hi and s['IntervalStart']==lo and s['IntervalEnd']==hi and s['SourceEventId']==bykind[eventkind]['event'],'Actual half-open phase/source event identity differs');frame=phase_frame(name,a,s['SampleTime']);need(s['Frame']==d['AssetFrame']==frame and s['Facing']==a['facing'],'Actual native phase frame/facing differs');masks[name]|=1<<frame;coverage.append(dict(observation=i,draw=d,clip=name,frame=frame))
   qualified[i]=d
 lock_before=[o for o in obs if 'guard_time'in o and o['guard_time']<=a['lock_at']];lock_after=[o for o in obs if 'guard_time'in o and o['guard_time']>=a['lock_at']];need(lock_before and lock_after,'Actual LockTarget bracket absent');lb,la=lock_before[-1],lock_after[0];need(pt(lb['player_ground'],la['player_ground'],1.e-8)and pt(locked['target'],la['player_ground'],1.e-8)and locked['target_z']==0 and locked['locked']is True and pt(locked['locked_center'],la['guard_ground'],1.e-8),'Actual original lockedTarget/center cannot be explained by true stationary actor positions')
 need(masks=={'StompWindup':63,'StompActive':3,'StompRecovery':15}and r['StompWindupMask']==63 and r['StompActiveMask']==3 and r['StompRecoveryMask']==15,'Same earliest Stomp cycle lacks12 actual source frames')
 joins=r['joins'];names=['Ready-to-StompWU0','StompWU5-to-Active0','StompActive1-to-Recovery0','StompRecovery3-to-actual-Ready'];need(len(joins)==4 and{x['name']for x in joins}==set(names),'Four actual adjacent renderer joins absent/duplicate')
 for j in joins:
  before,after=j['before_observation'],j['after_observation'];need(after==before+1 and before in qualified and after in qualified and j['before_draw']==qualified[before]and j['after_draw']==qualified[after],'Join is not two original adjacent actual draw callbacks')
  
  for index in[before,after]:
   jo=obs[index];signed=(jo['player_ground'][0]-jo['guard_ground'][0])*p['approach_side'];need(120<=signed<=160 and abs(jo['player_ground'][1]-jo['guard_ground'][1])<=6 and jo['actual_side_eligible'],'Both original adjacent join callbacks require actual side position, not Facing')
  left,right=qualified[before]['Selection'],qualified[after]['Selection'];name=j['name'];want={'Ready-to-StompWU0':('Ready',None,'StompWindup',0),'StompWU5-to-Active0':('StompWindup',5,'StompActive',0),'StompActive1-to-Recovery0':('StompActive',1,'StompRecovery',0),'StompRecovery3-to-actual-Ready':('StompRecovery',3,'Ready',None)}[name];need(left['Clip']==want[0]and right['Clip']==want[2]and(want[1]is None or left['Frame']==want[1])and(want[3]is None or right['Frame']==want[3]),'Actual join source phases differ')
  for s in[left,right]:
   if s['Clip']=='Ready':
    completed=[e for e in events if e['kind']==6 and e['at']<=s['SampleTime']];need(completed,'Ready lacks original completed action');prior=max(completed,key=lambda e:e['at']);need(s['AttackId']==prior['action']['attack_id']and(name!='StompRecovery3-to-actual-Ready'or s['AttackId']==aid)and s['Frame']==int(math.floor(math.fmod(max(0,s['SampleTime']-obs[after]['wake_end']),1.)/.25)),'Actual Ready original completedAction/running clock differs; beforeReady legitimately retainsAxe1')
   else:need(s['AttackId']==aid,'Join spliced another attack')
 need(near(obs[-1]['player_HP'],hp)and a['recovery_end']<=obs[-1]['guard_time']<a['recovery_end']+.3 and obs[-1]['guard_action']['completed_at']==a['recovery_end'],'Actual cycle did not reach original recovery end/live finalHP')
 pixels=subprocess.run([sys.executable,'-B','-X','utf8',str(C/'tooling/verify-Stomp-native-pixels-v001.py'),'--archive',str(archive)],capture_output=True,text=True);need(pixels.returncode==0,'Native original CRC/FIFO rejected: '+pixels.stderr)
 optics=runpy.run_path(str(C/'tooling/verify-Stomp-source-pixels-v001.py'))['verify_source_pixels'](archive,rows,coverage)
 return dict(schema='independent-Stomp50-native-verification-v001',passed=True,actual_archive=archive.as_posix(),process_id=r['process_id'],native_report=fact(original/'runtime-report.json'),compiled_manifest=fact(snapshot/'compiled-source-manifest.json'),Root_prereg=fact(prereg),candidate_freeze=p['candidate_freeze_pin'],scenario=r['scenario'],cycle_attack_id=aid,source_phase_frames=12,coverage_witnesses=[dict(observation=x['observation'],DrawId=x['draw']['DrawId'],clip=x['clip'],frame=x['frame'],AttackId=x['draw']['Selection']['AttackId'],SourceEventId=x['draw']['Selection']['SourceEventId'])for x in coverage],actual_adjacent_joins=joins,actual_complete50_resident=True,actual_quad_source_floor_and_mirror_verified=True,native_CRC_FIFO_verified=True,optical_source_projection=optics,native_Hero_HP=obs[-1]['player_HP'],Guard_HP=185,no_actor_clock_HP_or_pose_writes=True,source_contact_floor_or_hidden_socket_measured=False,audio_recorded=False,visual_reviewed=False,FinalAccepted=False)
def main():
 a=argparse.ArgumentParser();a.add_argument('--snapshot',required=True);a.add_argument('--root-prereg',required=True);a.add_argument('--source-only',action='store_true');a.add_argument('--archive');a.add_argument('--write-receipt',action='store_true');q=a.parse_args();snapshot=resolve(q.snapshot);prereg=resolve(q.root_prereg);m,p,profile,rows,expected=source_check(snapshot,prereg)
 if q.source_only:print(json.dumps(dict(compiled_inputs_verified=True,strict_registry=m['strict_registered_tests'],production_files=m['production_files'],source_files=m['source_files'],known_unique=50,approach_side=p['approach_side'],UE_started=False)));return
 need(q.archive,'Actual archive required');archive=resolve(q.archive);result=verify(archive,p,profile,rows,expected,prereg,snapshot)
 if q.write_receipt:
  with(archive/'原件/independent-Stomp50-native-verification-v001.json').open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
