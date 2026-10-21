"""Supplement frozen three Stage0 groups with independently authored body/hip test."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-hip-root-test-candidate-v001'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x):
 q=Path(x['path']);q=q if q.is_absolute()else R/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
freeze=C/'Move7-body-hip-root-test-freeze-v001.json'
assert pin(freeze)['sha256']=='fa117cdc6cd1f47c6f83afec0471873a343b0eefefbe749fd547569febf894c3'
f=read(freeze);check(f['test_source']);beforepins=check(f['exact_beforepins']);before=read(beforepins)['actual_source_files']
assert len(before)==278 and len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==278
for repeat in range(2):
 for x in before:check(x)
last=R/'UnrealGame/Saved/Bootstrap/last-build.json';assert read(last)['ExitCode']==0
assert Path(read(last)['Log']).name=='build-editor-20261018-220849.log'
target=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleGuardMoveRigBodyHipRootV001Tests.cpp';assert not target.exists()
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/stage0-independent-fourth-test-admission-v001';assert not out.exists();out.mkdir(parents=True)
receipt=dict(schema='Root-GuardMove7-independent-fourth-test-admission-v001',is_template=False,RootApproved=True,success=False,
 utc=datetime.now(timezone.utc).isoformat(),before_Source=278,Source=279,Production=1371,expected_registered_tests=200,
 expected_stage0_old_passes=196,expected_stage0_new_semantic_failures=4,candidate_freeze=pin(freeze),prior278_build=pin(last),
 old196_and_frozen_three_tests_unchanged=True,reason='Independent source-root/body-hip attachment and actual Canvas float-corner collapse coverage',FinalAccepted=False)
try:
 shutil.copy2(check(f['test_source']),target);assert pin(target)['sha256']==f['test_source']['sha256']
 for x in before:check(x)
 assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==279
 receipt.update(success=True,added_source=pin(target))
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(success=True,Source=279,Production=1371,receipt=pin(out/'admission-receipt-v001.json'))))
