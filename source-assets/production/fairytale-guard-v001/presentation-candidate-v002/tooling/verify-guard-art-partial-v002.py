"""Independent compiled-input and original native partial Guard trial audit. No UE launch."""
from pathlib import Path
import argparse,hashlib,json,math,re,subprocess,sys
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parent
WORKSPACE=CANDIDATE.parents[3]
V001=CANDIDATE.parent/'presentation-candidate-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def need(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b,tol=1.e-8):return math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol
def check_pin(p,r):need(p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'Pin differs: '+str(p))
def source_check(snapshot,prereg_path):
 for manifest,base in [(CANDIDATE/'observer-freeze-v002.json',CANDIDATE),(V001/'presentation-freeze-v001.json',V001)]:
  if manifest.exists():
   for row in read(manifest)['files']:check_pin(base/row['path'],row)
 m=read(snapshot/'compiled-source-manifest.json');files={r['path'].replace('\\','/'):r for r in m['files']}
 for name,r in files.items():check_pin(WORKSPACE/name,r)
 for folder in ['UnrealGame/Source','UnrealGame/Content/Production']:
  actual={p.relative_to(WORKSPACE).as_posix() for p in (WORKSPACE/folder).rglob('*') if p.is_file()}
  need(actual=={p for p in files if p.startswith(folder+'/')},'Compiled file set differs: '+folder)
 need(any(p.endswith('/Binaries/Win64/UnrealEditor-CodexDungeon.dll') for p in files),'Compiled DLL pin missing')
 for k in ['full_suite','current_build']:check_pin(WORKSPACE/m[k]['path'],m[k])
 suite=read(WORKSPACE/m['full_suite']['path']);build=read(WORKSPACE/m['current_build']['path'])
 need(build['ExitCode']==0 and suite['succeeded']==m['strict_registered_tests']>=179,'Actual build/full registry unavailable')
 need(all(suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Strict full registry is not GREEN')
 need('CodexDungeon.Content.FairytaleGuardPresentation' in json.dumps(suite),'New three semantic test results absent')
 prereg=read(prereg_path)
 need(prereg['schema']=='guard-art-partial-Root-prereg-v1' and prereg['pre_registered_before_capture'] is True,'Explicit Root typed preregistration required')
 need(prereg['compiled_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json'),'Root prereg binds another compiled snapshot')
 counts={'strict_registered_tests':m['strict_registered_tests'],'source_files':sum(p.startswith('UnrealGame/Source/') for p in files),'production_files':sum(p.startswith('UnrealGame/Content/Production/') for p in files)}
 for k,value in counts.items():need(type(prereg[k]) is int and prereg[k]==value,'Typed Root prereg count differs: '+k)
 need(m['production_files']==counts['production_files'],'Compiled manifest Production count differs')
 src='UnrealGame/Source/CodexDungeon/'
 required={src+n for n in ['DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleGuardPose.h','DungeonFairytaleGuardProfile.h','DungeonFairytaleGuardDataV001.inl','DungeonFairytaleGuardDrawState.h','DungeonFairytaleGuardPresentation.cpp','DungeonGuardArtPartialProbe.h','DungeonGuardArtPartialProbe.cpp','Tests/DungeonFairytaleGuardPresentationTests.cpp']}
 admitted={x['path'].replace('\\','/'):x for x in prereg['admitted_source_files']}
 need(required<=set(admitted),'Root prereg omits admitted observer/presenter/HUD/test source')
 for name,row in admitted.items():
  need(name in files and row['bytes']==files[name]['bytes'] and row['sha256']==files[name]['sha256'],'Root admitted source pin differs from exact compiled snapshot: '+name)
  check_pin(WORKSPACE/name,row)
 rows=prereg['profile_facts'];need(type(rows) is list and {x['clip'] for x in rows}=={'Ready','Wake','AxeWindup'} and len(rows)==3,'Root typed three-row profile facts required')
 for expected in rows:
  need(expected['native_source_id']=={'Ready':209,'Wake':210,'AxeWindup':212}[expected['clip']],'Root approved native row differs')
  need(expected['trial_allowed'] is True and expected['final_accepted'] is False and type(expected['trial_approval_record']) is str and bool(expected['trial_approval_record']),'Explicit Root trial/final fields differ')
  need(len(expected['frames'])=={'Ready':4,'Wake':6,'AxeWindup':6}[expected['clip']] and expected['target_standing_body_height_px']==100.8 and expected['canvas_source_px']==[512,512],'Root typed full row / body target / canvas differs')
  need([f['frame'] for f in expected['frames']]==list(range(len(expected['frames']))) and len({f['object_path'] for f in expected['frames']})==len(expected['frames']),'Root full row frame order/object uniqueness differs')
  check_pin(WORKSPACE/expected['registration_evidence']['path'],expected['registration_evidence'])
 profile={'rows':rows}
 text=(WORKSPACE/src/'DungeonFairytaleGuardDataV001.inl').read_text(encoding='utf-8-sig')
 facts={}
 for expected in profile['rows']:
  clip=expected['clip'];block=re.search(r'\{FRow R;\s*R\.Clip=EClip::'+clip+r';(?P<body>.*?)A\.Add\(MoveTemp\(R\)\);\}',text,re.S)
  need(block is not None,'Exact source row not found: '+clip);b=block['body']
  def number(k):
   q=re.search(r'R\.'+k+r'=([0-9.]+);',b);need(q is not None,'Source scalar missing: '+k);return float(q[1])
  need(number('NativeSourceId')==expected['native_source_id'] and number('StandingBasisFrame')==expected['standing_basis_frame'],'Source identity / standing basis differs')
  for k,key in [('StandingCrownY','standing_body_crown_y'),('StandingSoleY','standing_body_nearsole_y'),('StandingExtent','standing_body_extent_px')]:need(number(k)==expected[key],'Source row scale basis differs: '+k)
  need('R.SourcePoseApproved=true;' in b and 'R.TrialAllowed=true;' in b and 'R.FinalAccepted=false;' in b,'Explicit partial Root trial needed, final acceptance must remain false')
  record=re.search(r'R.TrialApprovalRecord=TEXT\("([^"\n]+)"\);',b);need(record is not None and record[1]==expected['trial_approval_record'],'Concrete Root trial record differs from prereg')
  pin=re.search(r'R.RegistrationEvidenceSHA256=TEXT\("([0-9a-f]{64})"\);',b);need(pin is not None and pin[1]==expected['registration_evidence']['sha256'],'Source registration pin differs')
  fs=re.findall(r'R.Frames.Add\(\{TEXT\("([^"\n]+)"\),TEXT\("([0-9a-f]{64})"\),FVector2D\(([0-9.]+),([0-9.]+)\)\}\);',b)
  need(len(fs)==len(expected['frames']),'Exact full frame bindings absent: '+clip)
  for actual,ef in zip(fs,expected['frames']):
   path,pin,x,y=actual;need(path==ef['object_path'] and pin==ef['source']['sha256'] and [float(x),float(y)]==ef['floor_pivot_source_px'],'Source texture/sha/floor binding differs')
   check_pin(Path(ef['source']['path']),ef['source'])
  facts[clip]={**expected,'TrialApprovalRecord':record[1]}
 hud=(WORKSPACE/src/'DungeonHUD.cpp').read_text(encoding='utf-8-sig')
 need('DungeonGuardArtPartialProof' in hud and 'SpawnActor<ADungeonGuardArtPartialProbe>()' in hud,'Observer actual startup branch absent')
 return m,facts

def verify(archive,facts,snapshot,prereg_path):
 original=archive/'原件';r=read(original/'runtime-report.json');index=read(archive/'index.json')
 need(index['snapshot_manifest_sha256']==sha(snapshot/'compiled-source-manifest.json') and index['root_prereg_sha256']==sha(prereg_path),'Capture session compiled snapshot / prereg binding changed')
 need(r['schema']=='guard-art-partial-native-observer-v002' and r['passed'] and r['flow_complete'],'Actual observer RED or wrong schema')
 need(r['normal_J_full_clear'] is False and r['diagnostic_public_damage_used'] is True and r['guard_public_damage_used'] is False and r['guard_spawned_by_probe'] is False,'Diagnostic/full-combat/Guard-birth scope differs')
 need(r['silent_video'] and r['audio_recorded'] is False and r['visual_reviewed'] is False and r['formal_complete_units']==0 and r['game_tick_called_manually'] is False,'Acceptance/pacing scope differs')
 hits=r['diagnostic_public_hits'];need(len(hits)==2 and [h['content_id'] for h in hits]==['ENM-STN-001','ENM-STN-002'],'Only two predecessor diagnostic clears allowed')
 need(all(h['api']=='ADungeonFighter::ApplyCombatHit' and h['before_HP']>h['after_HP']==0 and h['dead'] for h in hits),'Real public diagnostic HP commit absent')
 gid=int(r['guard_entity']);side=r['actual_approach_side'];need(gid>0 and side in [-1,1] and r['requested_approach_side'] in [-1,0,1],'Actual Guard / side absent')
 if r['requested_approach_side']:need(side==r['requested_approach_side'],'Requested legal approach side changed')
 need(r['guard_final_HP']==185 and r['guard_incoming_receipt_count']==0,'Guard was damaged')
 events=r['guard_original_issued_events'];need(all(int(e['EntityId'])==gid and e['Kind'] not in [8,9,12] for e in events),'Guard history contains incoming damage / poise / death')
 need([int(e['EventId']) for e in events]==sorted({int(e['EventId']) for e in events}),'Original issued events duplicated / reordered')
 wake=[e for e in events if e['Kind']==0];need(len(wake)==1,'Unique actual WakeStarted required');w=wake[0];wake_end=w['EndTime'];starts={int(e['AttackId']):e['AtTime'] for e in events if e['Kind']==2}
 obs=r['observations'];t=r['capture_timing'];off=t['frame_wall_offsets_s']
 need(len(obs)==len(off)>2 and all(b>a for a,b in zip(off,off[1:])) and t['use_fixed_time_step'] is False,'Original observation offsets lost')
 need(all(near(o['wall_offset_s'],v) and not o['interface_visible'] and o['text_calls']==0 for o,v in zip(obs,off)),'Hidden HUD / original callback offsets differ')
 need(any(o['LGT_drawn'] and o['hero_bound_skin'] for o in obs),'Actual committed LGT renderer absent')
 inputs=r['normal_input_requests'];downs=[x['key'] for x in inputs if x['down']]
 need(downs.count('Enter')==1 and downs.count('E')==1 and set(downs)<={'Enter','E','A','D','W','S'} and bool(set(downs)&{'A','D'}) and bool(set(downs)&{'W','S'}),'Controller-only input contract differs')
 warned={i:[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==1 and o['slots'][i]['slot'] in o['rendered_warning_slots']] for i in [1,2]}
 for i in [1,2]:
  need(len(warned[i])>=2,'Real rendered warning frames absent: '+str(i))
  born=[o for o in obs if len(o.get('slots',[]))==3 and int(o['slots'][i]['stage'])==2];need(bool(born),'Plan birth absent')
  b=born[0]['slots'][i];need(b['warning_at']>=born[0]['slots'][i-1]['dead_at']+2. and b['materialized_at']>=b['warning_at']+1.2,'Native breather / warning shortened')
  if i==2:need(int(b['entity'])==gid,'Guard is not slot2 entity')
 masks={'Wake':0,'Ready':0,'AxeWindup':0};dormant=0;gaps=0;seen=set();coverage=[]
 for oi,o in enumerate(obs):
  n=o.get('guard_native')
  if n:
   need(int(n['entity'])==gid and n['HP']==185 and n['incoming_receipts']==0 and not n['dead'],'Guard native identity / HP mutated')
   need(n['initial_time']==o['slots'][2]['materialized_at'],'Guard birth is not native materialization clock')
  for d in o['guard_draws']:
   if int(d['EntityId'])!=gid:continue
   s=d['Selection'];c=s['Clip'];frame=s['Frame'];stamp=s['SampleTime'];known=c in ['Dormant','Wake','Ready','AxeWindup']
   need(s['Valid'] and int(s['EntityId'])==gid and d['OptIn'] and s['TerminalPresentation'] is False and s['MaterialHit'] is False,'Actual draw authority differs')
   if not known:
    need(not d['Drawn'] and d['ProceduralFallback'] and bool(d['MissingReason']) and not d['DrawStack'],'Missing action hidden by substitute sprite');gaps+=1;continue
   need(s['Phase']=={'Dormant':0,'Wake':1,'Ready':2,'AxeWindup':3}[c],'Known clip does not match actual selected native phase')
   distance=sum(math.hypot(e['To'][0]-e['From'][0],e['To'][1]-e['From'][1]) for e in events if e['Kind']==7 and e['AtTime']<=stamp)
   need(near(s['AcceptedDistance'],distance,1.e-6) and near(s['DistancePhase'],math.fmod(distance,128.)/128.,1.e-8),'Accepted distance differs from immutable movement history')
   asset='Wake' if c=='Dormant' else c;ef=facts[asset];af=0 if c=='Dormant' else frame;need(0<=af<len(ef['frames']),'Source frame index invalid');f=ef['frames'][af]
   need(d['Drawn'] and d['TextureReady'] and d['RegistrationReady'] and d['TrialAllowed'] and d['FinalAccepted'] is False and not d['ProceduralFallback'] and not d['MissingReason'],'Partial row not actually drawn')
   need(d['AssetClip']==asset and d['AssetFrame']==af and d['NativeSourceId']==ef['native_source_id'],'Exact native source/alias/frame differs')
   need(d['TexturePath']==f['object_path'] and d['SourceSHA256']==f['source']['sha256'] and d['SourceFloorPivot']==f['floor_pivot_source_px'],'Actual texture/source/floor binding differs')
   need(d['TrialApprovalRecord']==ef['TrialApprovalRecord'] and d['RegistrationEvidenceSHA256']==ef['registration_evidence']['sha256'],'Explicit Root trial record/pin differs')
   scale=100.8/ef['standing_body_extent_px'];need(d['StandingExtent']==ef['standing_body_extent_px'] and d['TargetBodyHeight']==100.8 and near(d['RowScale'],scale) and near(d['CanvasSize'],512*scale),'ONE row body scale differs')
   need(d['WholebodyIncludesAxe'] and d['DrawStack']==[d['TexturePath']],'Wholebody stack duplicates axe/grips')
   px,py=f['floor_pivot_source_px'];mpx=512-px if s['Facing']<0 else px
   need(s['Facing'] in [-1,1] and near(d['TopScreen'][0],d['GroundScreen'][0]-mpx*scale,1.e-3) and near(d['TopScreen'][1],d['GroundScreen'][1]-py*scale,1.e-3),'Mirrored floor projection differs')
   if c=='Wake':
    need(near(s['IntervalStart'],w['AtTime']) and near(s['IntervalEnd'],wake_end) and int(s['SourceEventId'])==int(w['EventId']) and w['AtTime']<=stamp<wake_end,'Wake original event/clock differs')
    expected=sum(stamp>=w['AtTime']+x for x in [.167,.333,.5,.667,.833]);need(frame==expected,'Wake phase does not match original clock')
   elif c=='Ready':need(frame==int(math.floor(math.fmod(max(0.,stamp-wake_end),1.)/.25)),'Ready native clock phase differs')
   elif c=='AxeWindup':
    aid=int(s['AttackId']);need(aid in starts,'Axe original AttackStarted absent');start=starts[aid]
    need(near(s['IntervalStart'],start) and near(s['IntervalEnd'],start+1.) and start<=stamp<start+1.,'Axe original native window differs')
    need(frame==sum(stamp>=start+x for x in [.167,.333,.5,.667,.833]),'Axe windup phase differs')
   else:need(frame==0 and af==0 and stamp<=w['AtTime'],'Dormant alias timestamp differs')
   key=int(d['DrawId'])
   if not n or key in seen:continue
   seen.add(key)
   need(stamp<=n['time']+1.e-9,'Draw samples a future native clock')
   if near(stamp,n['time']):
    need(s['Phase']==n['phase'],'Same-stamp actual native phase differs from selected clip')
    gx=640.+(n['ground'][0]-o['camera_ground'][0])*.65;gy=490.-n['ground'][1]*.38
    need(near(d['GroundScreen'][0],gx,1.e-3) and near(d['GroundScreen'][1],gy,1.e-3),'Same-stamp native ground projection differs')
   if c=='AxeWindup' and int(s['AttackId'])==int(n['attack_id']):need(n['attack_kind']==1 and not n['interrupted'],'Selected axe row differs from actual native action')
   if c=='Dormant':dormant+=1
   if c in masks and (c=='Wake' or s['Facing']==side):masks[c]|=1<<frame;coverage.append({'observation':oi,'DrawId':str(key),'clip':c,'frame':frame,'facing':s['Facing'],'sample':stamp,'object':d['TexturePath']})
 need(masks=={'Wake':63,'Ready':15,'AxeWindup':63} and masks=={'Wake':r['WakeMask'],'Ready':r['ReadyMask'],'AxeWindup':r['WindupMask']},'Each exact drawn row phase required')
 need(dormant==r['DormantSeen'] and r['DormantUnobserved']==(dormant==0) and gaps>0 and r['procedural_gap_seen'],'Dormant absence / procedural gaps misreported')
 need(obs[-1]['phase']=='complete' and not obs[-1]['room_cleared'],'Partial trial cannot clear live Guard room')
 pixel=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'verify-native-pixels-v002.py'),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8')
 need(pixel.returncode==0,'Original pixel/FIFO verification failed: '+pixel.stderr);p=json.loads(pixel.stdout);need(p['passed'] and p['native_async_writer_verified'],'Native CRC/FIFO not verified')
 return {'passed':True,'scope':'Actual source-bound native partial art observer; diagnostic Knight/Bat clears, formal Guard birth, no final visual/art/audio acceptance.','native_frames':len(obs),'DormantSeen':dormant,'masks':masks,'actual_approach_side':side,'coverage_witnesses':coverage,'pixel_proof':p,'visual_reviewed':False,'formal_complete_units':0}

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--root-prereg',required=True);p.add_argument('--archive');p.add_argument('--source-only',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
 snapshot=Path(a.snapshot);snapshot=snapshot if snapshot.is_absolute() else WORKSPACE/snapshot;prereg=Path(a.root_prereg).resolve();m,facts=source_check(snapshot,prereg)
 if a.source_only:print(json.dumps({'compiled_inputs_verified':True,'strict_registry':m['strict_registered_tests'],'profile_facts':facts,'UE_started':False},ensure_ascii=False));return
 need(a.archive is not None,'Actual archive required');archive=Path(a.archive).resolve();result=verify(archive,facts,snapshot,prereg)
 if a.write_receipt:
  dest=archive/'原件/independent-guard-art-partial-v002.json';need(not dest.exists(),'Never overwrite receipt');dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
