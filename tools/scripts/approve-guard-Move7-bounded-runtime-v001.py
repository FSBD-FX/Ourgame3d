"""Root extends source preparation to a bounded runtime trial after actual semantic RED."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
R=Path('F:/Ourgame');P=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/Move7-profile-preparation-v001'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
p=argparse.ArgumentParser();p.add_argument('--approve-bounded-runtime-trial',action='store_true');a=p.parse_args();assert a.approve_bounded_runtime_trial
cm=R/'source-assets/production/backups/v141-GuardMove7-Stage0-four-semantic-RED-v002/compiled-source-manifest.json'
assert pin(cm)['sha256']=='62a0e1ab2bdf45d4a6caebc304b8c4bd14306f50327e65e459626d7cba6d8d6e'
m=read(cm);assert m['mode']=='stage0'and m['semantic_stage0_RED_observed']and m['source_files']==279 and m['production_files']==1371
assert(m['strict_registered_tests'],m['passed'],m['failed'])==(200,196,4)
for repeat in range(2):
 for x in m['files']:
  if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):check(x)
profile=P/'GuardMove7-runtime-profile-candidate-v001.json'
assert pin(profile)['sha256']=='03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51'
pf=P/'Move7-profile-host-preparation-freeze-v001.json';assert pin(pf)['sha256']=='675adf3166d0414f6e4725f7b50d465f76581d07c4ed754f9a4e7ab86747bbcb'
for x in read(pf)['files']:check(x,P)
verification=P/'host-reference-verification-v002.json';assert read(verification)['all_checks_passed']and read(verification)['check_count']==266
source_review=R/'docs/production/first-batch-v2/evidence/GuardMove-v140-v001/Root-Rest252-seven-part-preparation-review-v001.json'
assert pin(source_review)['sha256']=='988aad91d063be6ba0be253cbc55957fe8e145a93eca56652365c06cd50f1b79'
assert read(source_review)['PreparationAllowed']and not read(source_review)['RuntimeTrialAllowed']
native=R/'UnrealGame/Saved/Bootstrap/GuardMove7-v001-import-20261018-140342-134561.json'
ind=R/'source-assets/production/fairytale-guard-v001/Root-Move7-import-v001/independent-import-verification-20261018-140403-753926.json'
assert read(native)['success']and read(native)['actual_total']==1371 and read(ind)['success']and read(ind)['hash_mismatches']==0
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001';assert not out.exists();out.mkdir(parents=True)
record=dict(schema='Root-GuardMove7-bounded-runtime-trial-approval-v001',is_template=False,RootApproved=True,
 approval_method='Root CLI --approve-bounded-runtime-trial',utc=datetime.now(timezone.utc).isoformat(),
 presentation_type='GuardMoveSevenComponentRigDerived',profile_id=read(profile)['profile_id'],RuntimeTrialAllowed=True,TrialAllowed=True,FinalAccepted=False,
 scope='One separate seven-component Move trial only. Requires subsequent exact Root production source admission,200 GREEN and actual native/visible review; not final unit acceptance.',
 root_preparation_review=pin(source_review),runtime_profile=pin(profile),source_profile_freeze=pin(pf),source_snapshot_sha256=read(profile)['source_snapshot_sha256'],
 source_surface18=read(profile)['frozen_inputs']['surface18']if 'surface18'in read(profile)['frozen_inputs']else pin(R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/rest252-seven-part-author-trial-v001/surface18-and-fixed-parameters-v001.json'),
 pure_host_verification=pin(verification),native_import=pin(native),independent_import=pin(ind),actual_stage0_compiled_snapshot=pin(cm),
 source_native_component_batches=[252,250,251],component_count=7,artist_surface_points=18,expected_Production=1371,
 actual_stage0_source_count=279,required_registered_tests=200,old196_test_sources_unchanged=True,
 fixed_geometry_parameters=read(profile)['parameters'],layer_order=read(profile)['layer_order'],
 allowed_changes=['Read-only current Guard sample query','Fixed seven-component profile and solver','Atomic resident preflight and same submitted float quads','HUD Move opt-in and existing Stomp50 preload','Diagnostic native observer,manual launcher and evidence'],
 required_gates=['Current actual Guard entity/run/room/time/facing and flat ground','Open install/start/game-over gates','Positive current native Movement event','All7 exact Texture2D512 resources ready and not pending','One whole-rig X reflection','Actual Canvas float corners not collapsed'],
 historical_blocker_known=False,hero_ground_motion_reused=False,kernel_AI_clock_collision_damage_save_changes=False,
 old_six_raster_Move_accepted=False,old50_nonMove_source_gates_unchanged=True,
 native_GPU_residency_verified=False,native_draw_verified=False,production_compiled=False,formal_complete_units=0,completed_combinations=0,
 visible_risks=['Passing knees/boots overlap','Rest252-to-old Ready/attack silhouette continuity','Canonical straight-X art does not certify Y alignment/reversal foot contact','Legacy player occlusion outline will initially cover only unrotated BodyRest; rotating leg outline remains open'],
 host_limit='Frozen host accepts huge finite screen coordinates. Production must add actual Canvas float-corner collapse rejection, preserving art constants.',
 native_initial_scope='Both actual AI facings and >=128 accepted path each, then real combat and stopped Ready; Guard185/incoming0. Hurt/Stun native visuals not covered by this initial probe.',
 generation_calls=0,external_API_calls=0,approval_tool=pin(Path(__file__)))
target=out/'Root-limited-runtime-trial-approval-v001.json'
with target.open('x',encoding='utf-8')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(approval=pin(target),Source=279,Production=1371,semantic_RED_observed=True,RuntimeTrialAllowed=True,native_passed=False,FinalAccepted=False)))
