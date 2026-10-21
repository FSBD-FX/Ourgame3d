"""Bounded Move7 source/import/trial gates. Read-only; never starts UE."""
from pathlib import Path
import hashlib,json,math,runpy,sys
ROOT=Path('F:/Ourgame').resolve();C=ROOT/'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001'
D=Path(__file__).resolve().parent.parent
DERIVATIVE_FREEZE=D/'Move7-tool-contract-fix-freeze-v002.json'
P='UnrealGame/Source/CodexDungeon/'
SOURCE_ROOT=C/'source-compile-fix-v003'
SOURCE_FREEZE=SOURCE_ROOT/'Move7-observer-source-freeze-v003.json'
PROFILE_SHA='03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51'
SNAPSHOT_SHA='a16a6a151ca0f6895c80ce108221bb3bed8f9c267c8016d142c18ed74f84cd94'
PROFILE_ID='GuardMoveRig252_250_251_AuthorOwnHipC128_v001'
PARTS=['bodyrest_fixedaxe','near_thigh','near_shin','near_foot','far_thigh','far_shin','far_foot']
NAMES=['BodyRest','NearThigh','NearShin','NearFoot','FarThigh','FarShin','FarFoot']
ORDER=[6,5,4,3,2,1,0]
TESTS={'CodexDungeon.Content.FairytaleGuardMoveRigV001.'+x for x in ['RealCompletedGuardOwnerAndAcceptedPath','FixedSurfaceRigSingleMirrorAndFiniteBounds','AtomicSevenResourcesAndLegacyIsolation','BodyHipAttachmentAndActualSourceRoot']}
STAGE={P+n for n in ['DungeonGuardMovePresentation.h','DungeonFairytaleGuardMoveRigV001.h','DungeonFairytaleGuardMoveRigV001.cpp','DungeonFairytaleGuardMoveDrawStateV001.h','Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp']}
INTERFACE={P+n for n in ['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h']}
FOURTH=P+'Tests/DungeonFairytaleGuardMoveRigBodyHipRootV001Tests.cpp'
PROD={P+n for n in ['DungeonFairytaleGuardMoveRigDataV001.inl','DungeonFairytaleGuardMovePresentationV001.cpp']}
PROD_ALLOWED=PROD|{P+n for n in ['DungeonFairytaleGuardMoveRigV001.cpp','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleGuardFullPresentationV003.cpp']}
PROBE={P+n for n in ['DungeonGuardMoveProbeV001.h','DungeonGuardMoveProbeV001.cpp']}

def need(v,why):
 if not v:raise ValueError(why)
def path(v):
 p=Path(v);p=(p if p.is_absolute()else ROOT/p).resolve();need(p.is_relative_to(ROOT),'Project path required');return p
def read(v):return json.loads(path(v).read_text(encoding='utf-8-sig'))
def fact(v):
 p=path(v);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def pin(x):
 p=path(x['path']);a=fact(p);need((a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),'Changed pinned bytes: '+str(p));return p
def equalpin(a,b):return path(a['path'])==path(b['path'])and(a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])
def frozen(v):
 p=path(v)
 if read(p).get('schema')=='Guard-Move7-body-hip-root-added-semantic-test-freeze-v001':
  fourth_test_closure(read(p));return
 for x in read(p)['files']:
  q=Path(x['path']);q=q if q.is_absolute()else p.parent/q
  if not q.exists():q=ROOT/x['path']
  pin(dict(x,path=q.as_posix()))
def keyed(rows):
 d={path(x['path']).relative_to(ROOT).as_posix():dict(x,path=path(x['path']).relative_to(ROOT).as_posix())for x in rows};need(len(d)==len(rows),'Duplicate source membership');return d
def bytes_equal(a,b):return(a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])
def fourth_test_closure(d):
 # This one historical schema is a named closure, not files[]. Historical
 # beforepins describe Stage0 278; changed files are checked against that
 # exact admitted map, never incorrectly compared to current production.
 need(d['schema']=='Guard-Move7-body-hip-root-added-semantic-test-freeze-v001'and d['test_name']=='CodexDungeon.Content.FairytaleGuardMoveRigV001.BodyHipAttachmentAndActualSourceRoot','Only exact fourth-test named closure is supported')
 source=pin(d['test_source']);need(source.name=='DungeonFairytaleGuardMoveRigBodyHipRootV001Tests.cpp'and path(d['proposed_actual_path'])==ROOT/FOURTH,'Typed fourth-test source identity differs')
 fixed=read(C/'read-only-input-pins-v001.json')['inputs'];stage=read(pin(fixed['actual_stage0_receipt']));fourth=read(pin(fixed['actual_fourth_test_receipt']))
 need(bytes_equal(d['test_source'],fourth['added_source']),'Actual fourth-test admission differs from frozen candidate source')
 need(equalpin(d['stage0_v001_freeze'],stage['candidate_freeze']),'Typed fourth-test Stage0 closure differs');frozen(pin(d['stage0_v001_freeze']))
 before=read(pin(d['exact_beforepins']));need(before['schema']=='Guard-Move7-body-hip-root-added-test-exact-beforepins-v001'and before['actual_source_count']==278 and path(before['actual_source_root'])==ROOT/'UnrealGame/Source','Exact historical278 before closure required')
 baseline=read(pin(fixed['base_compiled_manifest']));expected=keyed([x for x in baseline['files']if x['path'].startswith('UnrealGame/Source/')]);need(len(expected)==stage['previous_Source_count']==273,'Typed closure baseline differs')
 rows=keyed(stage['admitted']);need(set(rows)==STAGE|INTERFACE and set(rows)-set(expected)==STAGE and stage['Source_count']==278,'Typed closure Stage0 extension differs');expected.update(rows)
 need(keyed(before['actual_source_files'])==expected and len(expected)==278 and expected[P+'Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp']['sha256']==d['frozen_three_test_sha256'],'Historical278 exact map/frozen three-test source differs')
 engine=Path('G:/UE_5.5/Engine/Source').resolve();allowed={engine/n for n in ['Runtime/Engine/Private/HUD.cpp','Runtime/Engine/Private/UserInterface/CanvasItem.cpp','Runtime/Core/Public/Math/RotationTranslationMatrix.h']}
 backends=d['independent_backend_sources'];actual={Path(x['path']).resolve()for x in backends};need(len(backends)==3 and actual==allowed,'Only three explicitly frozen UE backend source paths are permitted')
 for x in backends:
  backend=Path(x['path']).resolve();need(backend.is_absolute()and backend.is_relative_to(engine),'Backend outside exact engine source scope');h=hashlib.sha256()
  with backend.open('rb')as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  need((backend.stat().st_size,h.hexdigest())==(x['bytes'],x['sha256']),'Independent actual engine source pin changed: '+str(backend))
def strict_suite(suite,names):
 need(set(x['fullTestPath']for x in suite['tests'])==names and len(suite['tests'])==len(names),'Exact old196 plus four registered targets required')
 need(suite['succeeded']==len(names)and all(type(suite[k])is int and suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']),'Full200 strict counters required')
 for x in suite['tests']:need(x['state']=='Success'and x['errors']==x['warnings']==0 and not any(e.get('event',{}).get('type')in['Error','Warning']for e in x.get('entries',[])),'Non-strict test: '+x['fullTestPath'])

def source_chain(p,base):
 expected=keyed([x for x in base['files']if x['path'].startswith('UnrealGame/Source/')]);need(len(expected)==273,'Wrong actual v140 baseline')
 chain=p['source_extension_chain'];need([x['role']for x in chain]==['stage0','independent_fourth_test','fixture_repair','production','observer'],'Five ordered bounded source receipts required')
 for index,link in enumerate(chain):
  if index<3:need(equalpin(link['receipt_pin'],read(C/'read-only-input-pins-v001.json')['inputs'][['actual_stage0_receipt','actual_fourth_test_receipt','actual_fixture_repair_receipt'][index]]),'Initial three actual admissions must remain exact')
  d=read(pin(link['receipt_pin']));role=link['role'];need(d['is_template']is False and d['RootApproved']is True and d['success']is True and d['FinalAccepted']is False,'Actual Root source admission required')
  frozen(pin(d['candidate_freeze']))
  if role=='stage0':
   need(d['schema']=='Root-GuardMove7-stage0-admission-v001'and d['previous_Source_count']==len(expected)and d['unaffected_Source_unchanged']is True,'Original Stage0 admission differs')
   rows=keyed(d['admitted']);need(set(rows)==STAGE|INTERFACE and set(rows)-set(expected)==STAGE,'Stage0 exact5+three interfaces differs')
   # Original receipt has no previous array: its three retained before copies
   # must independently equal the exact v140 source pins.
   for n in INTERFACE:need(bytes_equal(fact(pin(link['receipt_pin']).parent/(Path(n).name+'.before')),expected[n]),'Stage0 before copy differs from v140: '+n)
   expected.update(rows);need(d['Source_count']==len(expected),'Stage0 Source count differs')
  elif role=='independent_fourth_test':
   need(d['schema']=='Root-GuardMove7-independent-fourth-test-admission-v001'and d['before_Source']==len(expected)and d['old196_and_frozen_three_tests_unchanged']is True,'Independent fourth-test admission differs')
   rows=keyed([d['added_source']]);need(set(rows)=={FOURTH}and FOURTH not in expected,'Only exact fourth test may be added');expected.update(rows);need(d['Source']==len(expected),'Fourth-test count differs')
  elif role=='fixture_repair':
   n=P+'Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp';need(d['schema']=='Root-GuardMove7-Stage0-one-birth-sign-repair-v002'and bytes_equal(d['before'],expected[n])and d['changed_byte_count']==1 and d['all_functional_assertions_and_thresholds_unchanged']is True and d['old196_and_independent_fourth_test_unchanged']is True,'Exact preserved one-byte legal birth fixture repair required')
   need(path(d['after']['path']).relative_to(ROOT).as_posix()==n and bytes_equal(d['candidate'],d['after'])and d['Source']==len(expected),'Fixture repair after/count differs');pin(d['candidate']);expected[n]=dict(d['after'],path=n)
  else:
   need(d['schema']=='Root-GuardMove7-'+role+'-admission-v001'and d['previous_Source_count']==len(expected)and d['unaffected_Source_unchanged']is True,'Bounded '+role+' admission differs')
   rows=keyed(d['admitted']);before=keyed(d['previous']);changed=set(rows)&set(expected);new=set(rows)-set(expected)
   need(set(before)==changed and all(bytes_equal(before[n],expected[n])for n in changed),'Admission skips previous exact source pins')
   need((new==PROD and set(rows)<=PROD_ALLOWED)if role=='production'else(new==PROBE and set(rows)==PROBE|{P+'DungeonHUD.cpp'}),'Non-Move7 source/test/kernel touched by '+role)
   expected.update(rows);need(d['Source_count']==len(expected),'Current Source count differs')
   if role=='observer':need(equalpin(d['candidate_freeze'],fact(SOURCE_FREEZE)),'Observer admission binds another source milestone')
 return expected

def preflight(snapshot,prereg):
 p=read(prereg);need(p['schema']=='GuardMove7-Root-native-prereg-v001'and p['is_template']is False and p['RootApproved']is True and p['pre_registered_before_capture']is True and p['FinalAccepted']is False,'Actual pre-capture Root prereg required; template rejects')
 need(type(p['approach_side'])is int and p['approach_side']in[-1,1],'Explicit actual facing/side required')
 frozen(DERIVATIVE_FREEZE);need(equalpin(p['tool_contract_fix_freeze_pin'],fact(DERIVATIVE_FREEZE))and equalpin(p['tool_contract_fix_checker_pin'],fact(D/'tooling/verify-Move7-native-v001.py')),'Explicit derivative tool freeze/checker binding differs')
 frozen(C/'Move7-native-observer-freeze-v001.json');frozen(SOURCE_FREEZE)
 need(equalpin(p['candidate_freeze_pin'],fact(C/'Move7-native-observer-freeze-v001.json'))and equalpin(p['source_probe_freeze_pin'],fact(SOURCE_FREEZE)),'Different observer candidate/source freeze')
 fixed=read(C/'read-only-input-pins-v001.json')['inputs']
 for x in fixed.values():pin(x)
 base=read(pin(fixed['base_compiled_manifest']));need(base['production_files']==1364 and base['strict_registered_tests']==196,'Wrong actual old CM')
 manifest=path(snapshot)/'compiled-source-manifest.json';need(equalpin(p['compiled_manifest_pin'],fact(manifest)),'Fresh compiled CM pin differs');m=read(manifest)
 need(m['mode']=='green'and m['passed']==m['strict_registered_tests']==200 and m['failed']==0 and m['production_files']==1371 and p['expected_source_files']==m['source_files'],'Fresh actual200/1371/current Source required')
 files=keyed(m['files']);need(len(files)==len(m['files']),'Duplicate compiled files')
 for x in files.values():pin(x)
 old_suite=read(pin(base['full_suite']));old_names={x['fullTestPath']for x in old_suite['tests']};need(len(old_names)==196 and not old_names&TESTS,'Wrong old196 registry');strict_suite(read(pin(m['full_suite'])),old_names|TESTS)
 actualsource={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Source').rglob('*')if x.is_file()};actualprod={x.relative_to(ROOT).as_posix()for x in(ROOT/'UnrealGame/Content/Production').rglob('*')if x.is_file()}
 need(actualsource=={n for n in files if n.startswith('UnrealGame/Source/')}and actualprod=={n for n in files if n.startswith('UnrealGame/Content/Production/')},'Actual Source/Production membership changed after build')
 expected=source_chain(p,base);need({n:x for n,x in files.items()if n.startswith('UnrealGame/Source/')}==expected,'Current Source differs from exact five-receipt extension chain')
 for n in PROBE:need(path(n).read_text(encoding='utf-8-sig')==(SOURCE_ROOT/'new-source'/Path(n).name).read_text(encoding='utf-8-sig'),'Actual observer Source changed beyond line endings')
 observer_path=pin(p['source_extension_chain'][-1]['receipt_pin']);before=(observer_path.parent/'DungeonHUD.cpp.before').read_text(encoding='utf-8-sig');startup=read(C/'startup-contract-v001.json');inc=startup['expected_unique_include'];branch=startup['expected_unique_branch'];need(before.count(inc)==before.count(branch)==1,'Production HUD startup anchors ambiguous')
 after=before.replace(inc,inc+'\n#include "DungeonGuardMoveProbeV001.h"').replace(branch,'        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardMoveProofV001")))GetWorld()->SpawnActor<ADungeonGuardMoveProbeV001>();\n'+branch.replace('if(','else if(',1));need(path(P+'DungeonHUD.cpp').read_text(encoding='utf-8-sig')==after,'HUD exceeds exact production plus two observer bootstrap edits')
 importer=ROOT/'source-assets/production/fairytale-guard-v001/Move7-import-candidate-v001';sys.path.insert(0,str(importer));import move7_import_contract_v001 as ic
 frozen(pin(fixed['importer_freeze']));imp=ic.load_manifest(pin(p['import_manifest_pin']));native=read(pin(p['native_import_pin']));ind=read(pin(p['independent_import_pin']));ic.validate_receipt_assets(imp,native)
 need(native['schema']=='GuardMove7-native-import-v001'and native['success']is True and native['total_production_files']==1371 and equalpin(native['manifest'],p['import_manifest_pin']),'Actual native seven import differs')
 need(ind['schema']=='GuardMove7-independent-import-twoSHA-v001'and ind['success']is True and ind['old1364_unchanged_twice']is True and ind['new7_saved_twice']is True and ind['exact_total']==1371 and ind['verification_passes']==2 and ind['hash_mismatches']==0 and equalpin(ind['receipt'],p['native_import_pin'])and equalpin(ind['manifest'],p['import_manifest_pin']),'Actual old1364/new7 saved-byte twoSHA receipt differs')
 for repeat in range(2):
  ic.verify_old(imp['old_production_files']);ic.exact_membership(imp,True)
  for x in native['assets']:pin(x['saved'])
 trial=read(pin(p['runtime_trial_approval_pin']));need(trial['schema']=='Root-GuardMove7-bounded-runtime-trial-approval-v001'and trial['is_template']is False and trial['RootApproved']is True and trial['RuntimeTrialAllowed']is True and trial['TrialAllowed']is True and trial['FinalAccepted']is False,'Separate actual Root bounded runtime trial approval required, import-only cannot open runtime')
 need(trial['profile_id']==PROFILE_ID and trial['runtime_profile']['sha256']==PROFILE_SHA and trial['source_snapshot_sha256']==SNAPSHOT_SHA and trial['presentation_type']=='GuardMoveSevenComponentRigDerived'and trial['component_count']==7 and trial['artist_surface_points']==18 and trial['expected_Production']==1371 and trial['required_registered_tests']==200,'Runtime profile/source/atomic7 contract differs')
 need(equalpin(trial['native_import'],p['native_import_pin'])and equalpin(trial['independent_import'],p['independent_import_pin'])and trial['native_GPU_residency_verified']is False and trial['native_draw_verified']is False and trial['production_compiled']is False,'Original pre-production approval cannot claim GPU/native proof')
 need(trial['old50_nonMove_source_gates_unchanged']is True and trial['kernel_AI_clock_collision_damage_save_changes']is False and trial['old_six_raster_Move_accepted']is False,'Move-only bounded scope changed')
 pin(trial['actual_stage0_compiled_snapshot']);pin(trial['runtime_profile']);pin(trial['source_profile_freeze'])
 profile=read(pin(fixed['prepared_profile']));need(fact(pin(fixed['prepared_profile']))['sha256']==PROFILE_SHA,'Frozen host profile differs');return m,p,profile,imp,trial
