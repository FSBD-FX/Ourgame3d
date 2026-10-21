"""Root admits the bounded seven-component implementation after actual four semantic RED."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-runtime-candidate-v001/production-v001';S=R/'UnrealGame/Source/CodexDungeon'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
p=argparse.ArgumentParser();p.add_argument('--freeze',required=True);p.add_argument('--freeze-sha256',required=True);p.add_argument('--approve-reviewed-production',action='store_true');a=p.parse_args();assert a.approve_reviewed_production
freeze=Path(a.freeze);freeze=freeze if freeze.is_absolute()else C/freeze
assert pin(freeze)['sha256']==a.freeze_sha256
for x in read(freeze)['files']:check(x,C)
cm=R/'source-assets/production/backups/v141-GuardMove7-Stage0-four-semantic-RED-v002/compiled-source-manifest.json'
assert pin(cm)['sha256']=='62a0e1ab2bdf45d4a6caebc304b8c4bd14306f50327e65e459626d7cba6d8d6e'
m=read(cm);assert m['mode']=='stage0'and m['semantic_stage0_RED_observed']and(m['source_files'],m['production_files'],m['passed'],m['failed'])==(279,1371,196,4)
previous_source=[x for x in m['files']if x['path'].startswith('UnrealGame/Source/')]
assert len(previous_source)==len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==279
for repeat in range(2):
 for x in m['files']:
  if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):check(x)
approval=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json'
assert pin(approval)['sha256']=='d78bcbca8cd47caa781ee9a1bdcc1c25c5f9a3036be5d72dc2a2dcceb57feb9e'
assert read(approval)['RootApproved']and read(approval)['RuntimeTrialAllowed']and not read(approval)['FinalAccepted']
changed=['DungeonFairytaleGuardMoveRigV001.cpp','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleGuardFullPresentationV003.cpp']
added=['DungeonFairytaleGuardMoveRigDataV001.inl','DungeonFairytaleGuardMovePresentationV001.cpp']
assert{q.name for q in(C/'changed-source').iterdir()if q.is_file()}==set(changed)
assert{q.name for q in(C/'new-source').iterdir()if q.is_file()}==set(added)
assert all(not(S/n).exists()for n in added)
for n in changed:assert pin(S/n)['sha256']==pin(C/'before'/n)['sha256']
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/production-admission-v001';assert not out.exists();out.mkdir(parents=True)
previous=[pin(S/n)for n in changed]
for n in changed:shutil.copy2(S/n,out/(n+'.before'))
receipt=dict(schema='Root-GuardMove7-production-admission-v001',utc=datetime.now(timezone.utc).isoformat(),is_template=False,RootApproved=True,success=False,
 previous_Source_count=279,Source_count=281,Production_count=1371,previous=previous,candidate_freeze=pin(freeze),actual_semantic_RED_snapshot=pin(cm),
 runtime_trial_approval=pin(approval),expected_registered_tests=200,all_four_tests_unchanged=True,old196_tests_unchanged=True,
 legacy_six_raster_Move_gate_unchanged=True,source_compiled_after_admission=False,native_passed=False,formal_complete_units=0,FinalAccepted=False)
try:
 for n in changed:shutil.copy2(C/'changed-source'/n,S/n)
 for n in added:shutil.copy2(C/'new-source'/n,S/n)
 touched={f'UnrealGame/Source/CodexDungeon/{n}'for n in changed}
 for x in previous_source:
  if x['path']not in touched:check(x)
 for n in changed+added:
  folder='changed-source'if n in changed else'new-source'
  assert pin(S/n)['sha256']==pin(C/folder/n)['sha256']
 assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==281
 receipt.update(success=True,admitted=[pin(S/n)for n in changed+added],unaffected_Source_unchanged=True)
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=281,Production=1371,receipt=pin(out/'admission-receipt-v001.json'))))
