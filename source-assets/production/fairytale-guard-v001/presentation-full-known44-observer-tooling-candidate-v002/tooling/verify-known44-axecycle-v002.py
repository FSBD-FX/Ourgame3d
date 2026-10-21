"""Independent exact-input and native Known44 AxeCycle proof. No UE launch."""
from pathlib import Path
import argparse,hashlib,json,math,re,subprocess,sys
HERE=Path(__file__).resolve().parent;CANDIDATE=HERE.parent;WORKSPACE=CANDIDATE.parents[3]
V003=CANDIDATE.parent/'presentation-full-candidate-v003'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def need(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resolve(p):p=Path(p);return p if p.is_absolute() else WORKSPACE/p
def pin(p,r):need(p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Exact pin differs: '+str(p))
def near(a,b,tol=1.e-8):return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol
REQUIRED_NATIVE_GUARD_TESTS=(
 'CodexDungeon.Content.FairytaleGuardPresentation.NativeClockMaterialAndDeath',
 'CodexDungeon.Content.FairytaleGuardPresentation.Accepted128DistanceAndBlocked',
 'CodexDungeon.Content.FairytaleGuardPresentation.InterruptedDeadlineAndPartialRows',
 'CodexDungeon.Content.FairytaleGuardFullV003.NativeAxe4Recovery4AndStomp6_2_4',
 'CodexDungeon.Content.FairytaleGuardFullV003.AcceptedPath128AndOriginalInterruptedInterval',
 'CodexDungeon.Content.FairytaleGuardFullV003.RealTerminalClockAndVersionedProfileIsolation',
)
def require_native_guard_tests(suite):
 for name in REQUIRED_NATIVE_GUARD_TESTS:
  tests=[t for t in suite['tests'] if t['fullTestPath']==name]
  need(len(tests)==1 and tests[0]['state']=='Success' and type(tests[0]['errors']) is int and tests[0]['errors']==0 and type(tests[0]['warnings']) is int and tests[0]['warnings']==0,'Exact required native Guard test absent/duplicate/non-strict: '+name)
def unique_rows(rows,label):
 need(type(rows) is list and all(type(x) is dict and type(x.get('clip')) is str for x in rows),label+' must be typed clip rows')
 result={x['clip']:x for x in rows};need(len(result)==len(rows),label+' repeats a clip');return result
def profile_facts(p,known):
 # A Root record may put only the ten known gates in profile_facts, or all13.
 # In both formats the explicit13-row table is mandatory and the three gaps
 # remain SourceId0/no frames/closed. No count is inferred from a future build.
 gaps={'Move':6,'StompActive':2,'StompRecovery':4};allrows=unique_rows(p['all_profile_rows'],'all_profile_rows');facts=unique_rows(p['profile_facts'],'profile_facts')
 need(set(allrows)==set(known)|set(gaps),'Exact13 Root allrows required')
 need(set(facts) in [set(known),set(allrows)],'profile_facts must be exact10 known or exact13 allrows')
 for clip in known:
  need(facts[clip]==allrows[clip],'Root known gate facts differ between tables: '+clip)
  need(facts[clip]['source_pose_approved'] is True and facts[clip]['logical_frames']==known[clip]['logical_frames'],'Known Root source pose/logical budget differs')
 for clip,budget in gaps.items():
  row=allrows[clip];need(type(row['native_source_id']) is int and row['native_source_id']==0 and row['source_pose_approved'] is False and row['trial_allowed'] is False and row['final_accepted'] is False and row['frames']==[] and not row['trial_approval_record'] and row['logical_frames']==budget and bool(row['gap_reason']),'Unaccepted12 Root gap facts admitted: '+clip)
  if clip in facts:need(facts[clip]==row,'Root gap facts differ between tables: '+clip)
 return {clip:facts[clip] for clip in known}
def source_check(snapshot,prereg_path):
 protocol=read(CANDIDATE/'proof-protocol-v001.json');freeze=CANDIDATE/'known44-AxeCycle-tooling-freeze-v002.json';need(freeze.is_file(),'Immutable whole candidate freeze required')
 for row in read(freeze)['files']:pin(CANDIDATE/row['path'],row)
 for dep in read(CANDIDATE/'immutable-input-pins-v001.json')['files']:pin(resolve(dep['path']),dep)
 for row in read(V003/'presentation-full-freeze-v003.json')['files']:pin(V003/row['path'],row)
 m=read(snapshot/'compiled-source-manifest.json');files={r['path'].replace('\\','/'):r for r in m['files']}
 for name,row in files.items():pin(WORKSPACE/name,row)
 for folder in ['UnrealGame/Source','UnrealGame/Content/Production']:
  actual={p.relative_to(WORKSPACE).as_posix() for p in (WORKSPACE/folder).rglob('*') if p.is_file()};need(actual=={n for n in files if n.startswith(folder+'/')},'Compiled file set differs: '+folder)
 need(any(n.endswith('/Binaries/Win64/UnrealEditor-CodexDungeon.dll') for n in files),'Actual DLL pin absent')
 for k in ['full_suite','current_build']:pin(WORKSPACE/m[k]['path'],m[k])
 suite=read(WORKSPACE/m['full_suite']['path']);build=read(WORKSPACE/m['current_build']['path'])
 need(build['ExitCode']==0 and suite['succeeded']==m['strict_registered_tests']>=184 and all(suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Actual full strict registry/build not GREEN')
 need(len(suite['tests'])==len({t['fullTestPath'] for t in suite['tests']})==m['strict_registered_tests'] and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in suite['tests']),'Full native registry is not unique/every-test strict GREEN')
 require_native_guard_tests(suite)
 p=read(prereg_path);need(p['schema']==protocol['Root_prereg_schema'] and p['scenario']==protocol['scenario'] and p['pre_registered_before_capture'] is True and not p.get('is_template',False),'Actual typed Root prereg required')
 need(p['compiled_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json'),'Root prereg binds another compiled snapshot')
 counts={'strict_registered_tests':m['strict_registered_tests'],'source_files':sum(n.startswith('UnrealGame/Source/') for n in files),'production_files':sum(n.startswith('UnrealGame/Content/Production/') for n in files)}
 for k,v in counts.items():need(type(p[k]) is int and p[k]==v,'Typed actual Root count differs: '+k)
 need(p['candidate_freeze_pin']['sha256']==sha(freeze),'Prereg does not bind this tool/source candidate');pin(resolve(p['candidate_freeze_pin']['path']),p['candidate_freeze_pin'])
 src='UnrealGame/Source/CodexDungeon/';required={src+n for n in ['DungeonHUD.cpp','DungeonHUD.h','DungeonFairytaleGuardPose.h','DungeonFairytaleGuardFullPoseV003.h','DungeonFairytaleGuardFullProfileV003.h','DungeonFairytaleGuardFullDataV003.inl','DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonGuardArtKnown44Probe.h','DungeonGuardArtKnown44Probe.cpp','Tests/DungeonFairytaleGuardFullV003Tests.cpp','Tests/DungeonFairytaleGuardPresentationTests.cpp']}
 admitted={r['path'].replace('\\','/'):r for r in p['admitted_source_files']};need(required<=set(admitted) and len(admitted)==len(p['admitted_source_files']),'Root admitted source pins incomplete/duplicate')
 for name,row in admitted.items():need(name in files and row['bytes']==files[name]['bytes'] and row['sha256']==files[name]['sha256'],'Root source differs from compiled snapshot');pin(WORKSPACE/name,row)
 actor=(WORKSPACE/src/'DungeonGuardArtKnown44Probe.cpp').read_text(encoding='utf-8-sig');need(protocol['runtime_report_schema'] in actor and 'First->Action.AttackId==A.AttackId' in actor and 'ActiveMask!=15' in actor,'Actual compiled independent actor/first-cycle failfast absent')
 hud=(WORKSPACE/src/'DungeonHUD.cpp').read_text(encoding='utf-8-sig');need('SpawnActor<ADungeonGuardArtKnown44Probe>()' in hud and 'LoadFairytaleGuardFullTrial();' in hud,'Independent full startup/renderer missing')
 trial_pin=p['Root_row_trial_record_pin'];pin(resolve(trial_pin['path']),trial_pin);trial=read(resolve(trial_pin['path']));need(trial['schema']=='guard-full-known44-Root-scoped-trial-v001' and trial['RootApproved'] is True and not trial.get('is_template',False) and trial['flag']=='DungeonFairytaleGuardFullPreview' and trial['FinalAccepted'] is False,'Root full scoped row trial approval is absent')
 inp=read(V003/'source-registration-resource-map-v003.json');known={r['clip']:r for r in inp['rows'] if r['source_pose_approved']};facts=profile_facts(p,known);tr=unique_rows(trial['rows'],'Root row trial approval')
 need(set(known)==set(facts)==set(tr) and len(facts)==10,'Exact known44/alias Root rows required')
 text=(WORKSPACE/src/'DungeonFairytaleGuardFullDataV003.inl').read_text(encoding='utf-8-sig');blocks=dict(re.findall(r'\{FRow R;\s*R\.Clip=EClip::([A-Za-z]+);(.*?)A\.Add\(MoveTemp\(R\)\);\}',text,re.S));need(len(blocks)==13,'Full13 rows changed')
 for clip,expected in known.items():
  ef=facts[clip];b=blocks[clip];need(ef['native_source_id']==expected['native_source_id'] and ef['frames']==expected['frames'],'Prereg source frames differ from frozen accepted inputs: '+clip)
  need(tr[clip]['native_source_id']==ef['native_source_id'] and tr[clip]['logical_frames']==ef['logical_frames'] and tr[clip]['frames']==ef['frames'],'Root actual approval binds different source frames: '+clip)
  need(ef['trial_allowed'] is True and ef['final_accepted'] is False and bool(ef['trial_approval_record']) and tr[clip]['trial_allowed'] is True and tr[clip]['final_accepted'] is False and tr[clip]['approved_by_Root'] is True and tr[clip]['trial_approval_record']==ef['trial_approval_record'],'Scoped full Root trial differs: '+clip)
  need('R.TrialAllowed=true;' in b and 'R.FinalAccepted=false;' in b and 'R.SourcePoseApproved=true;' in b and f"R.NativeSourceId={expected['native_source_id']};" in b,'Actual row not explicitly full trial approved')
  record=re.search(r'R.TrialApprovalRecord=TEXT\("([^"\n]+)"\);',b);need(record and record[1]==ef['trial_approval_record'],'Actual trial record differs')
  if clip=='Dormant':
   need('R.AliasTarget=EClip::Wake;R.AliasFrame=0;' in b and 'R.Frames.Add' not in b,'Only explicit Wake0 alias allowed')
   for k in ['alias','alias_frame','alias_evidence']:need(ef[k]==tr[clip][k]==expected[k],'Root Dormant alias facts differ')
   pin(resolve(expected['alias_evidence']['path']),expected['alias_evidence']);continue
  for k in ['standing_basis_frame','standing_body_crown_y','standing_body_nearsole_y','standing_body_extent_px','target_standing_body_height_px','canvas_source_px','registration_evidence','source_index']:need(ef[k]==tr[clip][k]==expected[k],'Root row scalar/evidence differs: '+clip+'/'+k)
  for k in ['registration_evidence','source_index']:pin(resolve(expected[k]['path']),expected[k]);need(expected[k]['sha256'] in b,'Actual row evidence pin differs')
  for ck,jk in [('StandingBasisFrame','standing_basis_frame'),('StandingCrownY','standing_body_crown_y'),('StandingSoleY','standing_body_nearsole_y'),('StandingExtent','standing_body_extent_px')]:
   q=re.search(r'R\.'+ck+r'=([0-9.]+);',b);need(q and float(q[1])==expected[jk],'Actual body-only scale basis differs')
  fs=re.findall(r'R\.Frames.Add\(\{TEXT\("([^"]+)"\),TEXT\("([0-9a-f]{64})"\),TEXT\("([0-9a-f]{64})"\),FVector2D\(([0-9.]+),([0-9.]+)\),EPivotAuthority::([A-Za-z]+)\}\);',b);need(len(fs)==len(expected['frames']),'Whole row incomplete')
  for a,f in zip(fs,expected['frames']):need(a[:3]==(f['object_path'],f['source']['sha256'],f['RGBA_sha256']) and [float(a[3]),float(a[4])]==f['floor_pivot_source_px'] and a[5]==f['pivot_authority'],'Actual frame metadata differs');pin(resolve(f['source']['path']),f['source'])
 for clip in ['Move','StompActive','StompRecovery']:
  b=blocks[clip];need('R.NativeSourceId=0;' in b and 'R.SourcePoseApproved=false;' in b and 'R.TrialAllowed=false;' in b and 'R.Frames.Add' not in b,'Unaccepted12 gaps admitted')
 ip=p['actual_native_import_receipt_pin'];pin(resolve(ip['path']),ip);receipt=read(resolve(ip['path']));need(receipt['schema']=='guard-full28-actual-native-import-v001' and receipt['success'] is True and len(receipt['assets'])==28,'Actual native28 import receipt missing')
 import_manifest=receipt['manifest'];pin(resolve(import_manifest['path']),import_manifest);im=read(resolve(import_manifest['path']));old=im['old_production_files'];need(im['expected_new_count']==28 and im['expected_old_count']==len(old),'Exact old/new import counts differ')
 need(im['RootImportApproved'] is True and im['prepared_only'] is False and im['root_trial_registration']==trial_pin,'Native import is not bound to this actual Root trial approval')
 for row in old:pin(resolve(row['path']),row)
 expected28={f['object_path']:f for e in known.values() for f in e['frames'] if '/GuardWhole_full_v003/' in f['object_path']};need(len(expected28)==28 and {a['actual_object_path'] for a in receipt['assets']}==set(expected28),'Native imported28 exact paths differ')
 saved=set()
 for a in receipt['assets']:
  f=expected28[a['actual_object_path']];settings=a['actual_settings']
  for key,want in [('compression_settings','TC_EDITOR_ICON'),('mip_gen_settings','TMGS_NO_MIPMAPS'),('lod_group','TEXTUREGROUP_UI'),('filter','TF_BILINEAR')]:need(want in settings[key],'Actual native texture setting differs: '+key)
  need(settings['never_stream']=='True' and settings['srgb']=='True','Actual native stream/sRGB setting differs')
  need(a['actual_class']=='Texture2D' and a['actual_dimensions']==[512,512] and len(a['actual_import_filenames'])==1 and Path(a['actual_import_filenames'][0]).resolve()==resolve(f['source']['path']).resolve() and a['source']['sha256']==f['source']['sha256'],'Actual native class/dimensions/source provenance differs');pin(resolve(a['saved']['path']),a['saved']);saved.add(resolve(a['saved']['path']).relative_to(WORKSPACE).as_posix())
 need({resolve(x['path']).relative_to(WORKSPACE).as_posix() for x in old}|saved=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Old Production+28 native saved packages is not exact compiled set')
 qp=p['independent_import_two_pass_receipt_pin'];pin(resolve(qp['path']),qp);proof=read(resolve(qp['path']));need(proof['success'] is True and proof['verification_passes']==2 and proof['receipt']==ip and proof['actual_total']==len(old)+28,'Independent old/new two-SHA verification absent/different import')
 return m,facts,protocol

def strict_approach(p,g,side):
 dx,dy=p[0]-g[0],p[1]-g[1];return 120.<=side*dx<=180. and math.hypot(dx,dy)<=180. and abs(dy)<=12.
def spatial_credit(o,d,side,cid):
 s=d['Selection'];c=s['Clip'];n=o.get('guard_native');sp=o.get('approach_spatial',{})
 if c in ['Dormant','Wake']:return True
 if not n or o['phase']!='normal_guard_approach_and_cycles' or not sp.get('route_reached') or s['Facing']!=side:return False
 strict=strict_approach(o['player_ground'],n['ground'],side)
 if c=='Ready':return strict
 if int(s['AttackId'])!=cid or int(n['attack_id'])!=cid or n['attack_kind']!=1 or n['interrupted']:return False
 dx=side*(o['player_ground'][0]-n['ground'][0])
 if not 120.<=dx<=180.:return False
 if c=='AxeWindup':return strict or (s['Frame']>=3 and n['phase']==3 and n['locked'] is True and s['SampleTime']>=n['lock_at'])
 if c=='AxeActive':return n['phase']==4 and n['locked'] is True and s['SampleTime']>=n['lock_at']
 if c=='AxeRecovery':return n['phase']==5 and n['locked'] is True and s['SampleTime']>=n['active_end']
 return False

def validate_spatial_observation(o,r):
 n=o.get('guard_native')
 if not n:return
 sp=o['approach_spatial'];side=r['actual_approach_side'];p=o['player_ground'];g=n['ground'];dx,dy=p[0]-g[0],p[1]-g[1]
 need(all(math.isfinite(v) for v in p+g),'Nonfinite actual spatial input')
 need(sp['player']==p and sp['guard']==g and near(sp['dx'],dx) and near(sp['dy'],dy) and near(sp['distance'],math.hypot(dx,dy)) and sp['player_HP']==o['player_HP'],'Serialized spatial position/HP differs from independent actual native observation')
 need(type(sp['route_reached']) is bool and type(sp['route_planned']) is bool and sp['requested_side']==r['requested_approach_side'],'Route typed request/reached fields differ')
 if o['phase'] in ['normal_guard_approach_and_cycles','complete']:
  need(sp['selected_side']==side and near(sp['signed_dx'],side*dx) and sp['strict_point']==strict_approach(p,g,side),'Actual selected side/strict point differs')
  need(o['player_HP']==100.,'Actual approach incurred player damage; cannot pass safe readable side trial')
 if sp['route_reached']:
  need(sp['route_planned'] and sp['route_stage']==3 and sp['selected_side']==side,'Reached route lacks completed three normal-input legs')
  need(0.<=sp['first_reached_sim']<=o['sim'] and strict_approach(sp['first_reached_player'],sp['first_reached_guard'],side),'Claimed first reached point is not actual signed120..180/radius180/dy12')
def validate_route(r):
 side=r['actual_approach_side'];sp=r['spatial_approach'];obs=r['observations'];ws=r['route_witnesses']
 need(sp['route_planned'] is True and sp['route_reached'] is True and sp['route_stage']==3,'Actual normal route never reached requested side')
 need(len(ws)==4 and ws[0]['event']=='normal_route_planned' and [x['stage'] for x in ws[1:]]==[0,1,2] and all(x['event']=='normal_route_waypoint_reached' for x in ws[1:]),'Three ordered actual route witnesses required')
 plan=ws[0];p,g=plan['player'],plan['guard'];lane=plan['outside_lane'][1]
 need(plan['outside_lane'][0]==p[0] and abs(lane-g[1])==140. and plan['side_lane']==[g[0]+side*150.,lane] and plan['approach_point']==[g[0]+side*150.,g[1]],'Known-body outside140 route geometry differs')
 need(sp['route_start_player']==p and sp['route_start_guard']==g and sp['lane_y']==lane,'Root route start/lane changed')
 for row,target in zip(ws[1:],[plan['outside_lane'],plan['side_lane'],plan['approach_point']]):
  need(all(abs(a-b)<=6. for a,b in zip(row['actual_player'],target)) and row['actual_guard']==g,'Actual WASD waypoint not reached within original6 world tolerance')
  need(any(near(o['sim'],row['sim']) and o['player_ground']==row['actual_player'] and o.get('guard_native',{}).get('ground')==row['actual_guard'] for o in obs),'Route witness has no matching unmodified native observation')
 need(all(a['sim']<b['sim'] for a,b in zip(ws,ws[1:])),'Route witness time did not progress normally')
 final=ws[-1]
 need(sp['first_reached_sim']==final['sim'] and sp['first_reached_player']==final['actual_player'] and sp['first_reached_guard']==final['actual_guard'] and strict_approach(final['actual_player'],final['actual_guard'],side),'First reached actual normal route point differs')
 need(any(o.get('approach_spatial',{}).get('route_reached') and near(o['sim'],sp['first_reached_sim']) and o['player_ground']==sp['first_reached_player'] for o in obs),'Reached route lacks actual frame witness')
 need(side*(obs[-1]['player_ground'][0]-obs[-1]['guard_native']['ground'][0])>=120.,'Completed trial ended on wrong/overlapped side')
 return {'route_reached':True,'first_reached_sim':sp['first_reached_sim'],'side':side,'waypoint_witnesses':ws,'spatial_thresholds':{'signed_dx':[120,180],'strict_radius_max':180,'strict_abs_dy_max':12,'late_windup_y_evade_requires_native_lock':True}}


def verify(archive,facts,snapshot,prereg_path,protocol):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json')
 need(index['schema']==protocol['session_schema'] and index['candidate_freeze_sha256']==sha(CANDIDATE/'known44-AxeCycle-tooling-freeze-v002.json') and index['snapshot_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json') and index['root_prereg_sha256']==sha(prereg_path),'Session does not bind exact prereg/compiled inputs/tooling')
 need(r['schema']==protocol['runtime_report_schema'] and r['scenario']=='AxeCycle' and r['passed'] is True and r['flow_complete'] is True and r['cycle_pinned'] is True,'Actual independent AxeCycle is RED/wrong schema')
 need(str(index['process_id'])==r['process_id'] and r['restart_serial']==protocol['normal_startup_restart_serial'] and re.fullmatch('[0-9A-Fa-f]{32}',r['run']) and int(r['owner'])>0,'Actual fresh normal-start PID/run/restart scope differs')
 need(r['normal_J_full_clear'] is False and r['diagnostic_public_damage_used'] is True and r['guard_public_damage_used'] is False and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False,'Explicit diagnostic/no Guard mutation scope differs')
 need(r['silent_video'] and r['audio_recorded'] is False and r['visual_reviewed'] is False and r['formal_complete_units']==0,'Acceptance/audio scope differs')
 hits=r['diagnostic_public_hits'];need(len(hits)==2 and [h['content_id'] for h in hits]==['ENM-STN-001','ENM-STN-002'] and all(h['api']=='ADungeonFighter::ApplyCombatHit' and h['before_HP']>h['after_HP']==0 and h['dead'] for h in hits),'Only legal predecessor public diagnostic clears allowed')
 gid=int(r['guard_entity']);side=r['actual_approach_side'];cid=int(r['cycle_attack_id']);need(gid>0 and cid>0 and side in [-1,1] and index['requested_approach_side']==r['requested_approach_side'] and (r['requested_approach_side']==0 or r['requested_approach_side']==side),'Guard/cycle/requested side identity differs')
 need(r['guard_final_HP']==185 and r['guard_incoming_receipt_count']==r['guard_outgoing_hit_receipt_count']==0,'Guard/player was damaged')
 events=r['guard_original_issued_events'];need(all(int(e['EntityId'])==gid and e['Kind'] not in [8,9,10,11,12,13] for e in events),'Actual passive Guard history contains damage/poise/cancel/hit/death/reward')
 ids=[int(e['EventId']) for e in events];need(ids==sorted(set(ids)),'Issued events duplicate/reorder')
 wakes=[e for e in events if e['Kind']==0];need(len(wakes)==1,'Once-only Wake event required');wake=wakes[0];wend=wake['EndTime'];need(near(wend-wake['AtTime'],1.),'Native Wake window changed')
 starts={int(e['AttackId']):e for e in events if e['Kind']==2};first=next(e for e in events if e['Kind']==2 and e['Action']['kind']==1);need(int(first['AttackId'])==cid and cid in starts,'Later Axe cycle substituted for first original Axe')
 a=first['Action'];copied=r['cycle_action_at_pin'];need(copied['kind']==1 and int(copied['attack_id'])==cid and copied['interrupted'] is False and copied['locked'] is False and copied['window_issued'] is False,'Selected first Windup0 action premise differs')
 for key in ['start','lock_at','active_at','active_end','recovery_end','cooldown_end']:need(near(copied[key],a[key]),'Pin changed original native action clock: '+key)
 for key,value in [('lock_at',.5),('active_at',1.),('active_end',1.2),('recovery_end',2.6),('cooldown_end',3.1)]:need(near(a[key]-a['start'],value),'Original Axe duration/gate changed: '+key)
 need(a['start']<=r['cycle_pin_native_time']<a['start']+.167 and strict_approach(r['cycle_pin_player'],r['cycle_pin_guard'],side),'First original Axe was selected after WU0 or outside actual side point')
 selected={}
 for kind in [2,3,4,5,6]:
  es=[e for e in events if e['Kind']==kind and int(e['AttackId'])==cid];need(len(es)==1,'Original selected cycle missing/duplicate native event kind '+str(kind));selected[kind]=es[0]
 for kind,key in [(2,'start'),(3,'lock_at'),(4,'active_at'),(5,'active_end'),(6,'recovery_end')]:need(near(selected[kind]['AtTime'],a[key]),'Original event timestamp differs')
 need(near(selected[4]['EndTime'],a['active_end']) and near(selected[5]['EndTime'],a['recovery_end']),'Original half-open Active/Recovery event ends differ')
 win=[x for x in r['guard_original_damage_windows'] if int(x['AttackId'])==cid];need(len(win)==1,'Exactly one original native Axe damage window required');win=win[0];locked=selected[3]['Action']
 need(int(win['EventId'])==int(selected[4]['EventId']) and win['Kind']==1 and near(win['Start'],a['active_at']) and near(win['End'],a['active_end']) and win['Center']==locked['locked_center'] and win['CenterZ']==locked['locked_center_z'] and win['Facing']==locked['facing']==side and win['Damage']==a['damage'] and win['Stagger']==a['stagger'],'Real locked native damage window geometry/event authority differs')
 loaded=r['startup_resident_textures'];expected={f['object_path']:(clip,e,f) for clip,e in facts.items() for f in e['frames']}
 need(len(expected)==len(loaded)==r['known_source_unique_count']==44 and r['selector_logical_contract']==57 and {x['actual_object_path'] for x in loaded}==set(expected),'Exact known44 preload before Enter absent')
 for x in loaded:
  clip,e,f=expected[x['actual_object_path']];need(x['clip']==clip and x['frame']==f['frame'] and x['native_source_id']==e['native_source_id'] and x['actual_class']=='Texture2D' and x['actual_width']==x['actual_height']==512 and x['resource_resident'] is True and x['source_SHA256_metadata']==f['source']['sha256'] and x['source_RGBA_SHA256_metadata']==f['RGBA_sha256'],'Actual startup resident object/metadata differs')
 obs=r['observations'];timing=r['capture_timing'];offsets=timing['frame_wall_offsets_s'];need(len(obs)==len(offsets)>2 and all(b>a for a,b in zip(offsets,offsets[1:])) and timing['use_fixed_time_step'] is False,'Original native callbacks/offsets/pacing differ');route=validate_route(r)
 need(all(near(o['wall_offset_s'],t) and not o['interface_visible'] and o['text_calls']==0 for o,t in zip(obs,offsets)),'Hidden HUD / actual offsets differ')
 need(any(o['LGT_drawn'] and o['hero_bound_skin'] for o in obs),'Actual real E committed LGT absent')
 downs=[x['key'] for x in r['normal_input_requests'] if x['down']];need(downs.count('Enter')==downs.count('E')==1 and set(downs)<={'Enter','E','A','D','W','S'} and bool(set(downs)&{'A','D'}) and bool(set(downs)&{'W','S'}),'Normal passive controller-only input contract differs')
 for i in [1,2]:
  warned=[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==1 and o['slots'][i]['slot'] in o['rendered_warning_slots']];need(len(warned)>=2,'Actual world warning not rendered')
  born=[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==2];need(bool(born),'Actual formal slot not born');b=born[0]['slots'][i];need(b['warning_at']>=born[0]['slots'][i-1]['dead_at']+2. and b['materialized_at']>=b['warning_at']+1.2,'Native warning/breather shortened')
  if i==2:need(int(b['entity'])==gid,'Guard is not formal planned slot2')
 masks={k:0 for k in protocol['mask_requirements']};seen=set();coverage=[];dormant=gaps=0;lastsample=-1.
 phases={'Dormant':0,'Wake':1,'Ready':2,'AxeWindup':3,'AxeActive':4,'AxeRecovery':5,'StompWindup':3}
 for oi,o in enumerate(obs):
  n=o.get('guard_native');validate_spatial_observation(o,r)
  if n:need(int(n['entity'])==gid and n['HP']==185 and n['incoming_receipts']==0 and not n['dead'] and n['initial_time']==o['slots'][2]['materialized_at'],'Actual native Guard/birth/HP differs')
  for d in o['guard_draws']:
   if int(d['EntityId'])!=gid:continue
   s=d['Selection'];clip=s['Clip'];frame=s['Frame'];stamp=s['SampleTime'];known=clip in facts;eligible=spatial_credit(o,d,side,cid)
   need(type(d['SpatialCoverageEligible']) is bool and d['SpatialCoverageEligible']==eligible,'Reported per-cycle spatial credit differs from real positions/lock/Aid')
   need(s['Valid'] and int(s['EntityId'])==gid and d['OptIn'] and s['TerminalPresentation'] is False and s['MaterialHit'] is False,'Actual full draw authority/material differs')
   if not known:
    need(clip in ['Move','StompActive','StompRecovery'] and not d['Drawn'] and d['ProceduralFallback'] and bool(d['MissingReason']) and not d['DrawStack'] and d['NativeSourceId']==0,'Unaccepted gap substituted/hidden');gaps+=1;continue
   need(clip in phases and s['Phase']==phases[clip],'Unexpected passive phase or phase/row mismatch')
   asset='Wake' if clip=='Dormant' else clip;ef=facts[asset];af=0 if clip=='Dormant' else frame;need(0<=af<len(ef['frames']),'Full source frame out of range');f=ef['frames'][af]
   need(d['Drawn'] and d['TextureReady'] and d['RegistrationReady'] and d['TrialAllowed'] and d['RequestedRowTrialAllowed'] and d['FinalAccepted'] is False and not d['ProceduralFallback'] and not d['MissingReason'],'Known full row not actually admitted/drawn')
   need(d['RequestedClip']==clip and d['AssetClip']==asset and d['AssetFrame']==af and d['NativeSourceId']==ef['native_source_id'] and d['TexturePath']==f['object_path'] and d['SourceSHA256']==f['source']['sha256'] and d['SourceRGBASHA256']==f['RGBA_sha256'] and d['SourceFloorPivot']==f['floor_pivot_source_px'],'Actual texture/alias/sourceRGBA/floor differs')
   need(d['TrialApprovalRecord']==ef['trial_approval_record'] and d['RequestedTrialApprovalRecord']==facts[clip]['trial_approval_record'] and d['RegistrationEvidenceSHA256']==ef['registration_evidence']['sha256'] and d['SourceIndexSHA256']==ef['source_index']['sha256'],'Actual Root trial/source-index/registration differs')
   need(d['PivotAuthority']=={'VisibleShoeSupport':1,'ArtistStandingRootPropagation':2,'ArtistNearSupportDeltaPropagation':3}[f['pivot_authority']],'Artist/visible floor authority erased')
   scale=100.8/ef['standing_body_extent_px'];need(d['StandingExtent']==ef['standing_body_extent_px'] and d['TargetBodyHeight']==100.8 and near(d['RowScale'],scale) and near(d['CanvasSize'],512*scale) and d['WholebodyIncludesAxe'] and d['DrawStack']==[d['TexturePath']],'ONE row scale or fixed-axe single submission differs')
   px,py=f['floor_pivot_source_px'];px=512-px if s['Facing']<0 else px;need(s['Facing'] in [-1,1] and near(d['TopScreen'][0],d['GroundScreen'][0]-px*scale,1.e-3) and near(d['TopScreen'][1],d['GroundScreen'][1]-py*scale,1.e-3),'Mirrored source floor projection differs')
   distance=sum(math.hypot(e['To'][0]-e['From'][0],e['To'][1]-e['From'][1]) for e in events if e['Kind']==7 and e['AtTime']<=stamp);need(near(s['AcceptedDistance'],distance,1.e-6) and near(s['DistancePhase'],math.fmod(distance,128.)/128.),'Accepted128 path differs')
   if clip=='Wake':need(near(s['IntervalStart'],wake['AtTime']) and near(s['IntervalEnd'],wend) and int(s['SourceEventId'])==int(wake['EventId']) and wake['AtTime']<=stamp<wend and frame==sum(stamp>=wake['AtTime']+x for x in [.167,.333,.5,.667,.833]),'Wake original half-open clock/event differs')
   elif clip=='Dormant':need(frame==0 and stamp<=wake['AtTime'],'Dormant alias clock differs')
   elif clip=='Ready':need(int(s['SourceEventId'])==0 and stamp>=wend and frame==int(math.floor(math.fmod(max(0.,stamp-wend),1.)/.25)) and not any(e['Kind']==7 and e['AtTime']==stamp and e['From']!=e['To'] for e in events),'Ready resets idleclock or contains actual movement')
   else:
    aid=int(s['AttackId']);need(aid in starts,'Actual AttackStarted receipt absent');action=starts[aid]['Action'];kind=2 if clip.endswith('Windup') else 4 if clip.endswith('Active') else 5
    es=[e for e in events if e['Kind']==kind and int(e['AttackId'])==aid];need(len(es)==1 and int(s['SourceEventId'])==int(es[0]['EventId']),'SourceEventId is not original native phase eventId')
    if clip.endswith('Windup'):begin,end,offs=action['start'],action['active_at'],[.167,.333,.5,.667,.833] if action['kind']==1 else [.15,.3,.45,.6,.75]
    elif clip=='AxeActive':begin,end,offs=action['active_at'],action['active_end'],[.05,.1,.15]
    else:begin,end,offs=action['active_end'],action['recovery_end'],[.35,.7,1.05]
    need(begin<=stamp<end and near(s['IntervalStart'],begin) and near(s['IntervalEnd'],end) and frame==sum(stamp>=begin+x for x in offs),'Actual split row half-open interval/frame differs')
    if clip in ['AxeActive','AxeRecovery']:need(action['kind']==1,'Axe split uses Stomp clock')
   key=int(d['DrawId'])
   if not n or key in seen:continue
   seen.add(key);need(stamp<=n['time']+1.e-9 and stamp>=lastsample,'Draw future/backwards native sample');lastsample=stamp
   if near(stamp,n['time']):
    need(s['Phase']==n['phase'] and near(d['GroundScreen'][0],640.+(n['ground'][0]-o['camera_ground'][0])*.65,1.e-3) and near(d['GroundScreen'][1],490.-n['ground'][1]*.38,1.e-3),'Same-stamp full phase/ground differs')
    if clip in ['AxeWindup','AxeActive','AxeRecovery'] and int(s['AttackId'])==cid:
     need(int(n['attack_id'])==cid and n['attack_kind']==1 and n['interrupted'] is False,'Selected draw not the original uninterrupted native Axe')
     if stamp>=a['lock_at']:need(n['locked'] is True and n['action']['locked_center']==locked['locked_center'] and n['action']['locked_center_z']==locked['locked_center_z'] and n['action']['facing']==locked['facing']==s['Facing'],'Selected post-lock draw differs from original AimLocked geometry')
   if clip=='Dormant':dormant+=1
   if clip in masks and eligible:masks[clip]|=1<<frame;coverage.append({'observation':oi,'DrawId':str(key),'clip':clip,'frame':frame,'sample':stamp,'AttackId':s['AttackId'],'SourceEventId':s['SourceEventId'],'player':o['player_ground'],'guard':n['ground'],'object':d['TexturePath']})
 need(masks==protocol['mask_requirements'] and masks=={'Wake':r['WakeMask'],'Ready':r['ReadyMask'],'AxeWindup':r['AxeWindupMask'],'AxeActive':r['AxeActiveMask'],'AxeRecovery':r['AxeRecoveryMask']},'Exact same-Axe WU6/A4/R4 and real Ready4/Wake6 coverage missing')
 need(dormant==r['DormantSeen'] and r['DormantUnobserved']==(dormant==0) and bool(gaps)==r['procedural_gap_seen'],'Dormant/gap scope misreported')
 need(obs[-1]['phase']=='complete' and not obs[-1]['room_cleared'] and obs[-1]['guard_native']['time']>=a['recovery_end'],'Cycle completion predates original RecoveryEnd / cleared room')
 # Window-end failfast can be audited independently from every recorded callback.
 for oi,o in enumerate(obs):
  n=o.get('guard_native')
  if not n:continue
  for end,clip,mask in [(a['active_at'],'AxeWindup',63),(a['active_end'],'AxeActive',15),(a['recovery_end'],'AxeRecovery',15)]:
   if n['time']>=end:
    earned=0
    for x in coverage:
     if x['clip']==clip and x['observation']<=oi:earned|=1<<x['frame']
    need(earned==mask,'Original window passed before true complete phase coverage')
 pixel=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'verify-known44-native-pixels-v002.py'),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(pixel.returncode==0,'Actual original CRC/FIFO proof failed: '+pixel.stderr);px=json.loads(pixel.stdout);need(px['passed'] and px['native_async_writer_verified'],'Actual native CRC/FIFO not verified')
 return {'passed':True,'scope':protocol['scope'],'cycle_attack_id':str(cid),'masks':masks,'native_frames':len(obs),'DormantSeen':dormant,'covered_required_texture_paths':sorted({x['object'] for x in coverage}),'observed_drawn_texture_paths':sorted({d['TexturePath'] for o in obs for d in o['guard_draws'] if int(d['EntityId'])==gid and d['Drawn']}),'startup_known_unique_count':44,'coverage_witnesses':coverage,'native_damage_window':win,'spatial_route_proof':route,'pixel_proof':px,'visual_reviewed':False,'formal_complete_units':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--root-prereg',required=True);p.add_argument('--archive');p.add_argument('--source-only',action='store_true');p.add_argument('--write-receipt',action='store_true');args=p.parse_args();snapshot=resolve(args.snapshot);prereg=Path(args.root_prereg).resolve();m,facts,protocol=source_check(snapshot,prereg)
 if args.source_only:print(json.dumps({'compiled_inputs_verified':True,'strict_registry':m['strict_registered_tests'],'profile_facts':facts,'known_unique':44,'UE_started':False},ensure_ascii=False));return
 need(args.archive is not None,'Actual fresh archive required');archive=Path(args.archive).resolve();result=verify(archive,facts,snapshot,prereg,protocol)
 if args.write_receipt:
  dest=archive/'原件/independent-known44-AxeCycle-v002.json';need(not dest.exists(),'Never overwrite receipt');dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
