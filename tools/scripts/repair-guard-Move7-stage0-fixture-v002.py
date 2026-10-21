"""Fix one out-of-bounds test birth sign; retain every original assertion and failure."""
from pathlib import Path
from datetime import datetime, timezone
import difflib, hashlib, json, shutil
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp'
C=R/'source-assets/production/fairytale-guard-v001/Move7-runtime-candidate-v001/stage0-fixture-repair-v002'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x):
 q=Path(x['path']);q=q if q.is_absolute()else R/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
cm=R/'source-assets/production/backups/v141-GuardMove7-Stage0-fixture-failure-v001/compiled-source-manifest.json'
m=read(cm);assert m['mode']=='fixture-failure'and m['fixture_failure_preserved']and not m['semantic_stage0_RED_observed']
assert m['source_files']==279 and m['production_files']==1371 and m['passed']==196 and m['failed']==4
for x in m['files']:
 if x['path'].startswith('UnrealGame/Source/'):check(x)
before=S.read_bytes();assert hashlib.sha256(before).hexdigest()=='74c08cf8a94cb2712e6274088b65abe2c2e24a6b66467a5e0769f413f1d0704f'
needle=b'W.Player->GetGroundPosition()-FVector2D(Side*210.,0.)'
replacement=b'W.Player->GetGroundPosition()+FVector2D(Side*210.,0.)'
assert before.count(needle)==1;after=before.replace(needle,replacement);assert len(before)==len(after)
assert sum(a!=b for a,b in zip(before,after))==1
assert not C.exists();C.mkdir(parents=True)
source=C/'new/Tests'/S.name;source.parent.mkdir(parents=True);source.write_bytes(after)
old=C/'before'/S.name;old.parent.mkdir();old.write_bytes(before)
patch=C/'one-spawn-sign-only-v002.patch'
patch.write_text(''.join(difflib.unified_diff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True),fromfile='a/UnrealGame/Source/CodexDungeon/Tests/'+S.name,tofile='b/UnrealGame/Source/CodexDungeon/Tests/'+S.name)),encoding='utf-8')
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/stage0-fixture-repair-v002';assert not out.exists();out.mkdir(parents=True)
receipt=dict(schema='Root-GuardMove7-Stage0-one-birth-sign-repair-v002',utc=datetime.now(timezone.utc).isoformat(),is_template=False,RootApproved=True,success=False,
 reason='Actual Scene Entry.X=-1180; former Entry-210=-1390 outside CenterBounds MinX=-1350. Native Spawn correctly returned null before target assertions.',
 exact_code_change='PlayerGround - Side*210 -> PlayerGround + Side*210',changed_byte_count=1,default_spawn_x_before=-1390.,default_spawn_x_after=-970.,
 original_failed_compiled_snapshot=pin(cm),original_failure_report=m['full_suite'],before=pin(S),candidate=pin(source),patch=pin(patch),
 all_functional_assertions_and_thresholds_unchanged=True,old196_and_independent_fourth_test_unchanged=True,
 Source=279,Production=1371,registered_tests=200,semantic_RED_observed_after_repair=False,RuntimeTrialAllowed=False,FinalAccepted=False)
with(C/'fixture-repair-freeze-v002.json').open('x',encoding='utf-8')as f:json.dump(dict(schema='GuardMove7-fixture-only-repair-freeze-v002',files=[pin(source),pin(old),pin(patch)],source_before=pin(S),original_failed_snapshot=pin(cm),changed_byte_count=1,all_functional_assertions_unchanged=True,production_implementation_allowed=False),f,ensure_ascii=False,indent=2)
try:
 shutil.copy2(source,S);assert S.read_bytes()==after
 for x in m['files']:
  if x['path'].startswith('UnrealGame/Source/')and x['path']!=S.relative_to(R).as_posix():check(x)
 receipt.update(success=True,after=pin(S),candidate_freeze=pin(C/'fixture-repair-freeze-v002.json'))
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v002.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,changed_code_bytes=1,Source=279,Production=1371,receipt=pin(out/'admission-receipt-v002.json'))))
