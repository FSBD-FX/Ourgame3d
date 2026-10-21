"""Admit only the frozen, stronger pending-gear native expectations."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame')
C=R/'source-assets/production/fairytale-equipment-retain-gear-v001'
O=R/'docs/production/first-batch-v2/evidence/pending-gear-native-v001/probe-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def same(p,row):
 d=desc(p);return d['bytes']==row['bytes'] and d['sha256']==row['sha256']
freeze=C/'test-v001/stage0-freeze-v001.json';v=read(freeze)
assert not O.exists() and v['files_excluding_manifest']==5
for row in v['files']:assert same(C/row['path'],row),row
for row in read(C/'test-v001/v118-baseline-pins-v001.json')['inputs']:assert same(Path(row['path']),row),row
actual=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleEquipmentBoundProbe.cpp'
candidate=C/'test-v001/candidate-source'/actual.name
patch=C/'test-v001/patch/pending-committed-gear-native-expectation-v001.patch'
check=subprocess.run(['git','apply','--check','--',str(patch)],cwd=R,capture_output=True,text=True)
assert check.returncode==0,check.stderr
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
O.mkdir(parents=True);shutil.copy2(actual,O/'before-DungeonFairytaleEquipmentBoundProbe.cpp')
shutil.copy2(candidate,actual);assert actual.read_bytes()==candidate.read_bytes()
changed=[p.as_posix() for p,row in before.items() if desc(p)!=row]
assert changed==[actual.as_posix()],changed
(O/'admission.json').write_text(json.dumps(dict(frozen_candidate=desc(freeze),patch=desc(patch),apply_check_exit=0,before=before[actual],after=desc(actual),actual_changed_Source=changed,production_implementation_changed=False,compiled=False,native_feature_RED=None,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(changed=changed,production_unchanged=True,next='Compile and run actual native pending-gear RED'),ensure_ascii=False))
