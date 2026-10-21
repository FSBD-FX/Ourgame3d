"""Root admits source-v002 observer after independently frozen actual200 GREEN."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001/source-boundary-fix-v002';S=R/'UnrealGame/Source/CodexDungeon'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
freeze=C/'Move7-observer-source-freeze-v002.json';assert pin(freeze)['sha256']=='7e356ed2dfdd38645b6828619dce71f789b3af02f6a51c6a352027cb088c1818'
for x in read(freeze)['files']:check(x,C)
cm=R/'source-assets/production/backups/v141-GuardMove7-Production200G-v001/compiled-source-manifest.json'
assert pin(cm)['sha256']=='0f011ba7e2963f4a686e7fcf84324ed3c5815f6c020fc2e818e6be79234ead38'
m=read(cm);assert(m['source_files'],m['production_files'],m['strict_registered_tests'],m['passed'],m['failed'])==(281,1371,200,200,0)
source=[x for x in m['files']if x['path'].startswith('UnrealGame/Source/')]
assert len(source)==len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==281
for repeat in range(2):
 for x in m['files']:
  if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):check(x)
for x in read(C/'actual-before-pins-v001.json')['files']:check(x)
names=['DungeonGuardMoveProbeV001.h','DungeonGuardMoveProbeV001.cpp'];assert all(not(S/n).exists()for n in names)
patch=C/'patches/DungeonHUD.cpp.patch'
r=subprocess.run(['git','apply','--check','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stderr
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/observer-admission-v001';assert not out.exists();out.mkdir(parents=True)
previous=[pin(S/'DungeonHUD.cpp')];shutil.copy2(S/'DungeonHUD.cpp',out/'DungeonHUD.cpp.before')
receipt=dict(schema='Root-GuardMove7-observer-admission-v001',utc=datetime.now(timezone.utc).isoformat(),is_template=False,RootApproved=True,success=False,
 previous_Source_count=281,Source_count=283,Production_count=1371,previous=previous,candidate_freeze=pin(freeze),previous_production200_GREEN=pin(cm),
 expected_registered_tests=200,all_four_tests_unchanged=True,old196_tests_unchanged=True,source_compiled_after_admission=False,native_passed=False,
 source_v002_only_change='Canonical positive X endpoint qualification accommodates genuine reciprocal-multiply direction rounding; original distances/times/AI and other targets unchanged.',
 diagnostic_scope='Normal controller Enter/E/WASD; Knight/Bat predecessors only public diagnostic damage,Guard185/incoming0; Move to combat to Ready,no native Hurt/Stun claim.',
 formal_complete_units=0,FinalAccepted=False)
try:
 for n in names:shutil.copy2(C/'new-source'/n,S/n)
 r=subprocess.run(['git','apply','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert r.returncode==0,r.stderr
 for x in source:
  if x['path']!='UnrealGame/Source/CodexDungeon/DungeonHUD.cpp':check(x)
 for n in names:assert pin(S/n)['sha256']==pin(C/'new-source'/n)['sha256']
 assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==283
 receipt.update(success=True,admitted=[pin(S/n)for n in names+['DungeonHUD.cpp']],unaffected_Source_unchanged=True)
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=283,Production=1371,receipt=pin(out/'admission-receipt-v001.json'))))
