"""Bounded adapter to frozenv009 + independent two-row Stomp50 input gate."""
from pathlib import Path
import argparse,ast,hashlib,json,re,copy
R=Path('F:/Ourgame').resolve();HERE=Path(__file__).resolve().parent
OLD=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Death40-manual-checkpoint-tooling-candidate-v001'
OLD_CHECKER=OLD/'verify-Death1326-manual-input-v001.py'
OLD_SHA='dcbb34d283943508c7f8fbcb508e37fdb6a2ce9c14ab85af34cc18f14b108070'
STOMP_TESTS=tuple('CodexDungeon.Content.FairytaleGuardStompV004.'+n for n in ['RealNativeHalfOpenClockAndEventIdentity','Versioned50BindingsAndAtomicMirroredFloor','RealActorReceiptRecoveryAndInterruptedExclusion'])
NEW_SOURCE=tuple('UnrealGame/Source/CodexDungeon/'+n for n in ['DungeonFairytaleGuardStompProfileV004.h','DungeonFairytaleGuardStompDataV004.inl','Tests/DungeonFairytaleGuardStompV004Tests.cpp','DungeonGuardStompProbeV001.h','DungeonGuardStompProbeV001.cpp','DungeonFairytaleGuardFullProfileV003.h','DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.h','DungeonHUD.cpp'])
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def adapter():
 need(sha(OLD_CHECKER)==OLD_SHA,'Original frozenv009 checker changed')
 text=OLD_CHECKER.read_text(encoding='utf-8-sig');tree=ast.parse(text)
 class Bounded(ast.NodeTransformer):
  def visit_Constant(self,n):
   if type(n.value) is int and n.value in [190,1326]:return ast.copy_location(ast.Constant({190:193,1326:1332}[n.value]),n)
   if type(n.value) is str:
    names={'Death1326-manual-tooling-freeze-v001.json':'Stomp50-manual-tooling-freeze-v001.json','Death1326-Root-manual-input-v001':'Stomp1332-Root-manual-input-v001','validate-Death1326-production-extension-v001.py':'validate-Stomp1332-production-extension-v001.py'}
    if n.value in names:return ast.copy_location(ast.Constant(names[n.value]),n)
   return n
 tree=ast.fix_missing_locations(Bounded().visit(tree));scope={'__file__':str(Path(__file__).resolve()),'__name__':'Stomp1332_manual_adapter'};exec(compile(tree,str(OLD_CHECKER),'exec'),scope);scope['C']=HERE
 old_freeze=OLD/'Death1326-manual-tooling-freeze-v001.json';need(sha(old_freeze)=='85e7ffeec9eb1a71266b590da4b2a83bfe49f869c40e2d29bf90ef108d15a15b','Original frozenv009 tooling changed');scope['rows_of_freeze'](old_freeze)
 for dependency in read(HERE/'immutable-v009-input-pins-v001.json')['files']:scope['check'](dependency)
 return scope
def overlay_rows(a):
 need(a.get('is_template') is False and a.get('RootApproved') is True,'Actual non-template Stomp row approval required')
 need(a['schema']=='Stomp50-Root-overlay-rows-v001' and a['profile_id']=='GuardStomp50V004' and a['flag']=='DungeonFairytaleGuardStompPreview' and a['FinalAccepted'] is False,'Typed independent Stomp limited-trial profile required')
 need((a['base_known_unique'],a['new_unique'],a['overlay_unique'],a['rows_total'],a['logical_contract'],a['remaining_Move_gap'])==(44,6,50,13,57,6),'44base+6overlay/57 contract differs')
 rows=a['rows'];need(len(rows)==2 and {r['clip'] for r in rows}=={'StompActive','StompRecovery'},'Only two Stomp rows may override')
 objects=[]
 for row in rows:
  n=2 if row['clip']=='StompActive' else 4
  need(type(row['native_source_id']) is int and row['native_source_id']>0,'Root must provide actual approved native source ID')
  need(row['source_pose_approved'] is True and row['trial_allowed'] is True and row['final_accepted'] is False and bool(row['trial_approval_record']),'Explicit limited row trial approval missing')
  need(len(row['frames'])==n and [x['frame'] for x in row['frames']]==list(range(n)),'Complete ordered two/four phase row required')
  need(row['target_standing_body_height_px']==100.8 and row['canvas_source_px']==[512,512] and row['standing_body_extent_px']>0 and row['standing_body_nearsole_y']-row['standing_body_crown_y']+1==row['standing_body_extent_px'] and 0<=row['standing_basis_frame']<n,'ONE row body basis differs')
  for frame in row['frames']:
   objects.append(frame['object_path']);need(frame['clip']==row['clip'] and frame['native_source_id']==row['native_source_id'],'Frame identity differs')
   need(len(frame['floor_pivot_source_px'])==2 and all(type(x) in [int,float] and 0<=x<=512 for x in frame['floor_pivot_source_px']) and frame['pivot_authority'] in ['VisibleShoeSupport','ArtistStandingRootPropagation','ArtistNearSupportDeltaPropagation'],'Explicit real/artist floor authority required')
 need(len(set(objects))==6,'New six object paths repeat');return rows
def required_stomp(suite):
 names=[x['fullTestPath'] for x in suite['tests']]
 for name in STOMP_TESTS:need(names.count(name)==1,'Exact new Stomp target absent/duplicate: '+name)
def controlled_source(scope,m,files):
 check=scope['check'];inputs=read(HERE/'immutable-v009-input-pins-v001.json');base_pin=inputs['prior_v138_compiled_manifest_pin'];base=read(check(base_pin))
 expected={x['path']:x for x in base['files'] if x['path'].startswith('UnrealGame/Source/')};need(len(expected)==base['source_files']==257,'Exact priorv138 Source257 required')
 prefix='UnrealGame/Source/CodexDungeon/'
 def receipt(pin,schema,targets):
  doc=read(check(pin));need(doc['schema']==schema and doc['success'] is True and doc['FinalAccepted'] is False,'Actual controlled Source admission receipt required')
  admitted={x['path']:x for x in doc['admitted']};need(set(admitted)=={prefix+x for x in targets} and len(admitted)==len(doc['admitted']),'Admission changes unexpected Source files')
  expected.update(admitted);need(doc['Source_count']==len(expected),'Admission Source count differs from exact chain');return doc
 stage=receipt(m['stage0_Source_admission_pin'],'Root-GuardStomp-Stage0-admission-v001',['DungeonFairytaleGuardFullProfileV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.h','DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardStompDataV004.inl','DungeonFairytaleGuardStompProfileV004.h','Tests/DungeonFairytaleGuardStompV004Tests.cpp'])
 need(stage['old_snapshot']==dict(base_pin,path=Path(base_pin['path']).relative_to(R).as_posix()) and stage['old_unaffected_Source253_byte_unchanged'] is True,'Stage0 admission does not preserve the prior257 boundary')
 check(stage['candidate_freeze'])
 observer=receipt(m['observer_Source_admission_pin'],'Root-GuardStomp-observer-admission-v001',['DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.cpp','DungeonGuardStompProbeV001.h','DungeonGuardStompProbeV001.cpp'])
 need(observer['unaffected_old_Source257_unchanged'] is True,'Observer admission did not preserve its unrelated Source');check(observer['source_freeze']);check(observer['same_Aid2_Ready_fix']);check(observer['stage0_snapshot'])
 # These two real Root receipts are immutable bounded steps, not a generic
 # permission to accept any currentSource hash mismatch.
 need(m['stage0_Source_admission_pin']==inputs['stage0_Source_admission_pin'] and m['observer_Source_admission_pin']==inputs['observer_Source_admission_pin'],'Wrong controlled Stage0/observer admission')
 data=read(check(m['approved_Data_Source_admission_pin']));scope['approval'](data)
 need(data['schema']=='Root-GuardStomp-approved-Data-admission-v001' and data['success'] is True and data['FinalAccepted'] is False,'Actual future approvedData admission required')
 data_path=prefix+'DungeonFairytaleGuardStompDataV004.inl';need(data['previous_Data_pin']==expected[data_path] and len(data['admitted'])==1 and data['admitted'][0]['path']==data_path,'ApprovedData admission changed a different/extra Source or skipped prior stub')
 expected[data_path]=data['admitted'][0];need(data['Source_count']==len(expected),'ApprovedData Source count differs')
 actual={k:v for k,v in files.items() if k.startswith('UnrealGame/Source/')};need(actual==expected,'Fresh Source is not exact v138 + bounded Stage0 + bounded observer + approvedData')
 for value in expected.values():check(value)
def verify(path,snapshot=None):
 scope=adapter();result=scope['verify'](scope['resolve'](path),snapshot);check=scope['check'];m=read(scope['resolve'](path));cm=read(check(m['snapshot_manifest_pin']));files={x['path']:x for x in cm['files']}
 controlled_source(scope,m,files)
 suite=read(check(m['full_suite_pin']));required_stomp(suite)
 historical=read(check(read(HERE/'immutable-v009-input-pins-v001.json')['prior190_full_suite_pin']))
 prior_names={x['fullTestPath'] for x in historical['tests']};need(len(prior_names)==historical['succeeded']==190 and all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in historical['tests']),'Pinned historical190 is not strictGREEN')
 need({x['fullTestPath'] for x in suite['tests']}==prior_names|set(STOMP_TESTS),'Fresh193 must preserve exact prior190 plus only these three Stomp targets')
 a=read(check(m['Stomp50_row_approval_pin']));rows=overlay_rows(a);need(a['compiled_manifest_sha256']==sha(check(m['snapshot_manifest_pin'])),'Stomp rows bind another compiledsnapshot')
 ext=read(check(m['production_extension_approval_pin']));need(ext['Stomp50_row_approval_pin']==m['Stomp50_row_approval_pin'],'Manual and extension row approvals differ')
 admitted={x['path']:x for x in m['admitted_Stomp_source_files']};need(set(NEW_SOURCE)<=set(admitted) and len(admitted)==len(m['admitted_Stomp_source_files']),'New source/profile/observer/DTO interface missing/duplicate')
 for name,pin in admitted.items():need(name in files and files[name]==pin,'New source not exactly compiled: '+name);check(pin)
 base=read(check(m['source_profile_prereg_pin']));known_objects={f['object_path'] for row in base['profile_facts'] if row['source_pose_approved'] for f in row['frames']};need(len(known_objects)==44,'Old44 source facts were expanded or changed')
 new_objects={f['object_path'] for row in rows for f in row['frames']};need(not known_objects&new_objects and len(known_objects|new_objects)==50,'New overlay is not disjoint44+6')
 text=(R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleGuardStompDataV004.inl').read_text(encoding='utf-8-sig')
 text=re.sub(r'//[^\n]*|/\*.*?\*/','',text,flags=re.S)
 blocks=dict(re.findall(r'\{FRow R;\s*R\.Clip=EClip::([A-Za-z]+);(.*?)A\.Add\(MoveTemp\(R\)\);\}',text,re.S));need(set(blocks)=={'StompActive','StompRecovery'},'Only two explicit FRow override blocks required; Stage0/pending stub cannot pass')
 for row in rows:
  b=blocks[row['clip']];need(f"R.NativeSourceId={row['native_source_id']};" in b and 'R.SourcePoseApproved=true;' in b and 'R.TrialAllowed=true;' in b and 'R.FinalAccepted=false;' in b and f'R.TrialApprovalRecord=TEXT("{row["trial_approval_record"]}");' in b,'Actual compiled row gates differ')
  for ck,jk in [('StandingBasisFrame','standing_basis_frame'),('StandingCrownY','standing_body_crown_y'),('StandingSoleY','standing_body_nearsole_y'),('StandingExtent','standing_body_extent_px')]:
   match=re.search(r'R\.'+ck+r'=([0-9.]+);',b);need(match and float(match[1])==row[jk],'Actual new body basis differs')
  for key in ['registration_evidence','source_index']:check(row[key]);need(row[key]['sha256'] in b,'Actual new source/registration pin differs')
  fs=re.findall(r'R\.Frames.Add\(\{TEXT\("([^"]+)"\),TEXT\("([0-9a-f]{64})"\),TEXT\("([0-9a-f]{64})"\),FVector2D\(([0-9.]+),([0-9.]+)\),EPivotAuthority::([A-Za-z]+)\}\);',b)
  need(len(fs)==len(row['frames']),'Actual new frame metadata incomplete')
  for actual,f in zip(fs,row['frames']):need(actual[:3]==(f['object_path'],f['source']['sha256'],f['RGBA_sha256']) and [float(actual[3]),float(actual[4])]==f['floor_pivot_source_px'] and actual[5]==f['pivot_authority'],'Actual new frame metadata differs');check(f['source'])
 need(m['Guard_known_unique']==44 and m['Stomp_overlay_unique']==50 and m['Stomp_new_textures']==6 and m['Stomp_flag']=='DungeonFairytaleGuardStompPreview','Manual scopes contradict44/50')
 result.update(strict_registry=193,production_files=1332,Stomp_overlay_unique=50,Stomp_new_textures=6,Stomp_flag=m['Stomp_flag']);return result
def self_test():
 s=adapter();synthetic={'succeeded':193,'failed':0,'succeededWithWarnings':0,'notRun':0,'inProcess':0,'tests':[dict(fullTestPath=n,state='Success',errors=0,warnings=0,entries=[]) for n in list(s['DEATH_TESTS'])+list(STOMP_TESTS)+['HOST_SYNTHETIC_ONLY.'+str(i) for i in range(187)]]};s['strict_suite'](synthetic);required_stomp(synthetic)
 negative=[]
 for label,change in [('old190',lambda q:q.update(succeeded=190)),('duplicate',lambda q:q['tests'].__setitem__(6,q['tests'][0])),('warning',lambda q:q['tests'][0].update(warnings=1)),('hiddenError',lambda q:q['tests'][0].update(entries=[{'event':{'type':'Error'}}]))]:
  q=copy.deepcopy(synthetic);change(q)
  try:s['strict_suite'](q)
  except ValueError:negative.append(label)
  else:raise AssertionError('Rejected gate accepted '+label)
 q=copy.deepcopy(synthetic);q['tests'][3]['fullTestPath']='HOST_SYNTHETIC_ONLY.missingStomp'
 try:required_stomp(q)
 except ValueError:negative.append('missingStompTarget')
 else:raise AssertionError('MissingStomp target accepted')
 try:overlay_rows(read(HERE/'Root-Stomp50-overlay-rows-TEMPLATE-NOT-APPROVED-v001.json'))
 except ValueError:negative.append('unapproved_pending_rows')
 else:raise AssertionError('Pending Root row template accepted')
 valid=read(HERE/'Root-Stomp50-overlay-rows-TEMPLATE-NOT-APPROVED-v001.json');valid.update(is_template=False,RootApproved=True)
 for ri,row in enumerate(valid['rows']):
  row.update(native_source_id=99000+ri,source_pose_approved=True,trial_allowed=True,trial_approval_record='HOST_SYNTHETIC_ONLY',standing_basis_frame=0,standing_body_crown_y=64,standing_body_nearsole_y=463,standing_body_extent_px=400)
  row['frames']=[dict(clip=row['clip'],frame=i,native_source_id=row['native_source_id'],object_path=f'HOST_SYNTHETIC_ONLY/{ri}/{i}',floor_pivot_source_px=[231,464],pivot_authority='ArtistStandingRootPropagation') for i in range(2 if ri==0 else 4)]
 overlay_rows(valid)
 for label,change in [('44_equals50',lambda q:q.update(base_known_unique=50)),('missingRow',lambda q:q['rows'].pop()),('duplicatePath',lambda q:q['rows'][1]['frames'][0].update(object_path=q['rows'][0]['frames'][0]['object_path'])),('trialOff',lambda q:q['rows'][0].update(trial_allowed=False))]:
  q=copy.deepcopy(valid);change(q)
  try:overlay_rows(q)
  except ValueError:negative.append(label)
  else:raise AssertionError('Bad overlay gate accepted '+label)
 return {'host_self_test':True,'synthetic_report_only':True,'negative_gates':negative,'actual193_GREEN_claimed':False,'UE_started':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manual-input');ap.add_argument('--snapshot');ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
 if args.self_test:print(json.dumps(self_test()));return
 need(args.manual_input,'Root must select fresh non-template Stomp1332 checkpoint');print(json.dumps(verify(args.manual_input,args.snapshot)))
if __name__=='__main__':main()
