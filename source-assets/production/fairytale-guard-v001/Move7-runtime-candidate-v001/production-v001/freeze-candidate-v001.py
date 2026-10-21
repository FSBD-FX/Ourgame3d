"""Freeze the isolated candidate and independently recheck every before pin."""
from pathlib import Path
import hashlib,json
C=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
CM=ROOT/'source-assets/production/backups/v141-GuardMove7-Stage0-four-semantic-RED-v002/compiled-source-manifest.json'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
assert pin(CM)['sha256']=='62a0e1ab2bdf45d4a6caebc304b8c4bd14306f50327e65e459626d7cba6d8d6e'
cm=read(CM);sourcepins={x['path']:x for x in cm['files'] if x['path'].startswith('UnrealGame/Source/')}
assert len(sourcepins)==279
for _ in range(2):
 for key,old in sourcepins.items():
  q=pin(ROOT/key);assert (q['bytes'],q['sha256'])==(old['bytes'],old['sha256']),key
changes=sorted((C/'changed-source').iterdir());new=sorted((C/'new-source').iterdir())
assert len(changes)==5 and len(new)==2
targets=[]
for p in changes:
 key='UnrealGame/Source/CodexDungeon/'+p.name;before=pin(C/'before'/p.name);old=sourcepins[key]
 assert (before['bytes'],before['sha256'])==(old['bytes'],old['sha256'])
 assert (C/'patches'/(p.name+'.patch')).exists()
 targets.append(dict(actual_target=key,before=before,candidate=pin(p),patch=pin(C/'patches'/(p.name+'.patch'))))
for p in new:
 key='UnrealGame/Source/CodexDungeon/'+p.name
 assert key not in sourcepins and not (ROOT/key).exists()
 targets.append(dict(actual_target=key,before=None,candidate=pin(p)))
checkfile=C/'host-checks-v002.json';checks=read(checkfile)
assert checks['all_checks_passed'] and checks['numerical_cases']==1084 and not checks['native_Cpp_executed']
reviewfile=C/'independent-review-v001.json';review=read(reviewfile)
assert review['review_complete'] and not review['blocking_findings'] and review['read_only']
out=C/'Move7-production-candidate-freeze-v001.json';assert not out.exists()
members=[pin(p) for p in sorted(C.rglob('*')) if p.is_file() and p!=out]
for _ in range(2):
 for old in members:assert pin(Path(old['path']))==old
dependencies=['DungeonFairytaleGuardMoveRigV001.h','DungeonFairytaleGuardMoveDrawStateV001.h','DungeonGuardMovePresentation.h','Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp','Tests/DungeonFairytaleGuardMoveRigBodyHipRootV001Tests.cpp']
result=dict(schema='GuardMove7-production-candidate-freeze-v001',candidate_only=True,actual_Source_written=False,actual_Content_written=False,UE_build_run_performed=False,native_draw_verified=False,production_compiled=False,actual_Source_before=279,expected_Source_after_production_only=281,expected_Production=1371,registered_tests=200,old196_and_four_new_tests_unchanged=True,stage0_compiled_manifest=pin(CM),root_limited_trial_approval=pin(ROOT/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json'),host_checks=pin(checkfile),independent_review=pin(reviewfile),targets=targets,frozen_dependency_sources=[sourcepins['UnrealGame/Source/CodexDungeon/'+x] for x in dependencies],member_count=len(members),member_SHA_verification_passes=2,member_mismatches=0,actual_Source_SHA_verification_passes=2,actual_Source_mismatches=0,files=members,formal_complete_units=0,completed_combinations=0,FinalAccepted=False,limitations=['Only unrotated Rest body enters legacy occlusion masks; rotating legs excluded','Straight-X trajectory does not certify diagonal/reversal foot contact','Passing knees/boots overlap and Rest252-to-old nonMove silhouette continuity await real native visible review'],next='Root exact patch admission, real UE compilation/frozen4/full200, then retained native proof and optical review')
with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(freeze=pin(out),member_count=len(members),actual_Source_mismatches=0,member_mismatches=0),ensure_ascii=False))
