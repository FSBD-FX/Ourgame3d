"""Root admits a frozen bounded Dodge production/observer phase using narrow patches."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon'
p=argparse.ArgumentParser();p.add_argument('--role',choices=['production','observer'],required=True);p.add_argument('--candidate',required=True);p.add_argument('--freeze',required=True);p.add_argument('--freeze-sha',required=True);p.add_argument('--before-count',type=int,required=True);p.add_argument('--expected-new',action='append',required=True);p.add_argument('--expected-change',action='append',required=True);a=p.parse_args()
def resolve(q):q=Path(q);return q if q.is_absolute()else R/q
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=sha(q))
C=resolve(a.candidate);freeze=resolve(a.freeze);assert sha(freeze)==a.freeze_sha
for x in read(freeze)['files']:
 q=Path(x['path']);q=q if q.is_absolute()else freeze.parent/q
 assert(q.stat().st_size,sha(q))==(x['bytes'],x['sha256']),q
before=[pin(q)for q in sorted((R/'UnrealGame/Source').rglob('*'))if q.is_file()];assert len(before)==a.before_count
news=sorted(a.expected_new);changes=sorted(a.expected_change)
assert len(news)==len(set(news))==2 and len(changes)==len(set(changes))
assert{q.relative_to(C/'new-source').as_posix()for q in(C/'new-source').rglob('*')if q.is_file()}==set(news)
assert all(not(S/n).exists()for n in news) and all((S/n).is_file()for n in changes)
for name in news+changes:assert not Path(name).is_absolute()and '..'not in Path(name).parts
assert all(not n.startswith('Tests/')for n in news+changes)
allowed_new={'production':{'DungeonFairytaleSwordDodgePresentation.cpp','DungeonFairytaleSwordDodgeTextures.inl'},'observer':{'DungeonHeroDodgeProbeV001.h','DungeonHeroDodgeProbeV001.cpp'}}
allowed_changes={'production':{'DungeonFairytaleSwordDodgePlan.cpp','DungeonFighter.cpp','DungeonHUD.h','DungeonHUD.cpp','DungeonFairytaleSwordPresentation.cpp'},'observer':{'DungeonHUD.cpp'}}
assert set(news)==allowed_new[a.role] and set(changes)<=allowed_changes[a.role]
before_pins=C/'actual-before-pins-v001.json'
assert before_pins.is_file()
declared_before=read(before_pins)['files']
assert {resolve(x['path']).relative_to(R).as_posix()for x in declared_before}=={f'UnrealGame/Source/CodexDungeon/{n}'for n in changes}
for x in declared_before:
 q=resolve(x['path']);assert(q.stat().st_size,sha(q))==(x['bytes'],x['sha256']),q
patches=[C/'patches'/f'{n}.patch'for n in changes];assert all(q.is_file()for q in patches)
for name,patch in zip(changes,patches):
 headers=[line[4:].split('\t',1)[0]for line in patch.read_text(encoding='utf-8-sig').splitlines()if line.startswith('--- ')or line.startswith('+++ ')]
 assert headers==[f'UnrealGame/Source/CodexDungeon/{name}']*2,'Patch may touch only its declared existing file'
 run=subprocess.run(['git','apply','--check','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert run.returncode==0,run.stderr
out=R/f'docs/production/first-batch-v2/evidence/hero-Dodge32-v140-v001/{a.role}-admission-v001';assert not out.exists();out.mkdir(parents=True)
previous=[pin(S/n)for n in changes]
for name in changes:shutil.copy2(S/name,out/(name+'.before'))
rec=dict(schema=f'Root-Dodge-{a.role}-admission-v001',is_template=False,RootApproved=True,success=False,FinalAccepted=False,
 utc=datetime.now(timezone.utc).isoformat(),previous_Source_count=a.before_count,Source_count=a.before_count+2,previous=previous,candidate_freeze=pin(freeze),formal_complete_units=0,
 old193_tests_and_newDodge3_tests_unchanged=True,source_compiled_after_admission=False,native_Dodge_verified=False)
try:
 for name in news:
  target=S/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(C/'new-source'/name,target)
 for patch in patches:
  run=subprocess.run(['git','apply','--ignore-space-change','-p0',str(patch)],cwd=R,capture_output=True,text=True);assert run.returncode==0,run.stderr
 touched={f'UnrealGame/Source/CodexDungeon/{n}'for n in changes}
 for x in before:
  if x['path']not in touched:
   q=R/x['path'];assert(q.stat().st_size,sha(q))==(x['bytes'],x['sha256']),q
 assert len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==a.before_count+2
 for name in news:assert sha(S/name)==sha(C/'new-source'/name)
 rec.update(success=True,admitted=[pin(S/n)for n in news+changes],unaffected_Source_unchanged=True)
except Exception as e:rec['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(rec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=a.before_count+2,receipt=pin(out/'admission-receipt-v001.json')),ensure_ascii=False))
