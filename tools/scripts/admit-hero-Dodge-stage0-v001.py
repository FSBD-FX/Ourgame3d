"""Root admits exact seven new sources and three narrow patches after native32 import."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-state-gap-v001/dodge-runtime-candidate-v001'
S=R/'UnrealGame/Source/CodexDungeon'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
freeze=C/'Dodge-stage0-freeze-v001.json';assert pin(freeze)['sha256']=='de4bc579dc522621127d2ce0931effd230beb55650ca071a74b586bcd0be5472'
for x in read(freeze)['files']:check(x,C)
before=[pin(q)for q in sorted((R/'UnrealGame/Source').rglob('*'))if q.is_file()];assert len(before)==262
cm=read(R/'source-assets/production/backups/v139-Stomp193G/compiled-source-manifest.json')
assert {x['path']:x for x in before}=={x['path']:x for x in cm['files']if x['path'].startswith('UnrealGame/Source/')}
interface=read(C/'stage0/exact-before-pins-v001.json')
for x in interface['actual_files_to_narrow_patch']+interface['readonly_interface_and_prior_test_pins']:check(x)
native=R/'UnrealGame/Saved/Bootstrap/hero-Dodge32-v001-import-20261018-122934-381505.json'
ind=R/'source-assets/production/fairytale-hero-state-gap-v001/dodge-state-preparation-v001/Root-Dodge32-import-v001/independent-import-verification-20261018-122953-794979.json'
assert read(native)['success'] and read(native)['actual_total']==1364 and read(ind)['success'] and read(ind)['hash_mismatches']==0
assert len([q for q in(R/'UnrealGame/Content/Production').rglob('*')if q.is_file()])==1364
names=['DungeonDodgePresentation.h','DungeonFairytaleSwordDodgeProfile.h','DungeonFairytaleSwordDodgeProfile.cpp','DungeonFairytaleSwordDodgePlan.h','DungeonFairytaleSwordDodgePlan.cpp','DungeonFairytaleSwordDodgeDrawState.h','Tests/DungeonFairytaleSwordDodgeV001Tests.cpp']
assert{q.relative_to(C/'stage0/new-source').as_posix()for q in(C/'stage0/new-source').rglob('*')if q.is_file()}==set(names)
assert all(not(S/n).exists()for n in names)
patchnames=['DungeonFighter.h','DungeonFighter.cpp','DungeonHUD.h'];patches=[C/'stage0/patches'/f'minimal-{n}.patch'for n in patchnames]
for patch in patches:
 p=subprocess.run(['git','apply','--check','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
out=R/'docs/production/first-batch-v2/evidence/hero-Dodge32-v140-v001/stage0-admission-v001';assert not out.exists();out.mkdir(parents=True)
previous=[pin(S/n)for n in patchnames]
for name in patchnames:shutil.copy2(S/name,out/(name+'.before'))
receipt=dict(schema='Root-Dodge-stage0-admission-v001',is_template=False,RootApproved=True,success=False,FinalAccepted=False,
 utc=datetime.now(timezone.utc).isoformat(),previous_Source_count=262,Source_count=269,previous=previous,
 candidate_freeze=pin(freeze),native_import=pin(native),independent_twoSHA=pin(ind),expected_registered_tests=196,
 old193_tests_unchanged=True,source_compiled_after_admission=False,formal_complete_units=0)
try:
 for name in names:
  target=S/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(C/'stage0/new-source'/name,target)
 for patch in patches:
  p=subprocess.run(['git','apply','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
 touched={f'UnrealGame/Source/CodexDungeon/{n}'for n in patchnames}
 for x in before:
  if x['path']not in touched:check(x)
 actual=[pin(q)for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()];assert len(actual)==269
 for name in names:assert pin(S/name)['sha256']==pin(C/'stage0/new-source'/name)['sha256']
 receipt.update(success=True,admitted=[pin(S/n)for n in names+patchnames],unaffected_Source_unchanged=True)
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=269,Production=1364,receipt=pin(out/'admission-receipt-v001.json')),ensure_ascii=False))
