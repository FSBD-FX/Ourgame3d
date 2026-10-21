"""Root admits exact5 Stage0 sources/3 patches after actual native7 import."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, shutil, subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-runtime-candidate-v001/stage0'
S=R/'UnrealGame/Source/CodexDungeon'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
p=argparse.ArgumentParser();p.add_argument('--freeze',required=True);p.add_argument('--freeze-sha256',required=True);p.add_argument('--approve-stage0',action='store_true');a=p.parse_args()
assert a.approve_stage0
freeze=Path(a.freeze);freeze=freeze if freeze.is_absolute()else C/freeze
assert pin(freeze)['sha256']==a.freeze_sha256
for x in read(freeze)['files']:check(x,C)
before=[pin(q)for q in sorted((R/'UnrealGame/Source').rglob('*'))if q.is_file()];assert len(before)==273
cm=read(R/'source-assets/production/backups/v140-Dodge196G/compiled-source-manifest.json')
assert{x['path']:x for x in before}=={x['path']:x for x in cm['files']if x['path'].startswith('UnrealGame/Source/')}
native=R/'UnrealGame/Saved/Bootstrap/GuardMove7-v001-import-20261018-140342-134561.json'
ind=R/'source-assets/production/fairytale-guard-v001/Root-Move7-import-v001/independent-import-verification-20261018-140403-753926.json'
assert read(native)['success']and read(native)['actual_total']==1371 and read(ind)['success']and read(ind)['hash_mismatches']==0
for repeat in range(2):
 for x in cm['files']:
  if x['path'].startswith('UnrealGame/Content/Production/'):check(x)
 for x in read(native)['assets']:check(x['saved'])
assert len([q for q in(R/'UnrealGame/Content/Production').rglob('*')if q.is_file()])==1371
names=['DungeonGuardMovePresentation.h','DungeonFairytaleGuardMoveRigV001.h','DungeonFairytaleGuardMoveRigV001.cpp','DungeonFairytaleGuardMoveDrawStateV001.h','Tests/DungeonFairytaleGuardMoveRigV001Tests.cpp']
assert{q.relative_to(C/'new').as_posix()for q in(C/'new').rglob('*')if q.is_file()}==set(names)
assert all(not(S/n).exists()for n in names)
patchnames=['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h'];patches=sorted((C/'patches').glob('*.patch'));assert len(patches)==3
targets=[]
for patch in patches:
 r=subprocess.run(['git','apply','--numstat','-p1',str(patch)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stderr
 rows=[line.split('\t')[-1]for line in r.stdout.splitlines()];assert len(rows)==1
 targets.extend(rows)
 r=subprocess.run(['git','apply','--check','--ignore-space-change','-p1',str(patch)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stderr
assert set(targets)=={f'UnrealGame/Source/CodexDungeon/{n}'for n in patchnames}
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/stage0-admission-v001';assert not out.exists();out.mkdir(parents=True)
for name in patchnames:shutil.copy2(S/name,out/(name+'.before'))
receipt=dict(schema='Root-GuardMove7-stage0-admission-v001',is_template=False,RootApproved=True,success=False,FinalAccepted=False,
 utc=datetime.now(timezone.utc).isoformat(),previous_Source_count=273,Source_count=278,Production_count=1371,
 candidate_freeze=pin(freeze),native_import=pin(native),independent_twoSHA=pin(ind),expected_registered_tests=199,
 old196_tests_unchanged=True,source_compiled_after_admission=False,formal_complete_units=0)
try:
 for name in names:
  target=S/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(C/'new'/name,target)
 for patch in patches:
  r=subprocess.run(['git','apply','--ignore-space-change','-p1',str(patch)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stderr
 touched={f'UnrealGame/Source/CodexDungeon/{n}'for n in patchnames}
 for x in before:
  if x['path']not in touched:check(x)
 assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==278
 for name in names:assert pin(S/name)['sha256']==pin(C/'new'/name)['sha256']
 receipt.update(success=True,admitted=[pin(S/n)for n in names+patchnames],unaffected_Source_unchanged=True)
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=278,Production=1371,receipt=pin(out/'admission-receipt-v001.json')),ensure_ascii=False))
