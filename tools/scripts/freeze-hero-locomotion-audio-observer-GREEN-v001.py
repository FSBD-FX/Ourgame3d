from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);a=ap.parse_args()
admitp=EV/'Root-observer-source-admission-v001/actual-source-admission.json';admit=read(admitp);old=read(admit['predecessor_compiled_manifest']['path'])
assert admit['actual_applied'] and admit['RootApproved'] and not admit['is_template']
changed={r['path']:r for r in admit['after_files']}
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'])==changed.get(row['path'],row)
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());production=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
assert len(source)==303 and len(production)==1425
assert {p.relative_to(R).as_posix() for p in source+production}=={r['path'] for r in old['files'] if r['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/'))}
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';bd=read(build);log=Path(bd['Log']);suite=Path(a.suite).resolve();q=read(suite)
assert bd['ExitCode']==0 and datetime.fromisoformat(bd['Utc'].replace('Z','+00:00'))>datetime.fromisoformat(admit['utc']) and suite.stat().st_mtime>=datetime.fromisoformat(bd['Utc'].replace('Z','+00:00')).timestamp()
assert tuple(q[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess'))==(203,0,0,0,0)
assert len(q['tests'])==len({t['fullTestPath'] for t in q['tests']})==203
assert {t['fullTestPath'] for t in q['tests']}=={t['fullTestPath'] for t in read(old['full_suite']['path'])['tests']}
for t in q['tests']:assert t['state']=='Success' and t['warnings']==t['errors']==0 and not any(e['event']['type'] in ('Warning','Error') for e in t['entries'])
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
O=R/'source-assets/production/backups/v145-HeroLocomotionObserver303-1425-203GREEN-v001';assert not O.exists();O.mkdir()
files=source+production+[dll,build,log,suite];pins=[pin(p) for p in files];copies=[]
for p in source+[dll,build,log,suite,admitp]:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(p)['sha256']==pin(dst)['sha256'];copies.append(dict(source=pin(p),copy=pin(dst)))
for _ in range(2):
 for row in pins:assert pin(R/row['path'])==row
out=O/'compiled-source-manifest.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-hero-locomotion-observer-full203-GREEN-build-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=303,production_files=1425,production_textures=1419,production_new_SoundWaves=6,registered_tests=203,passed=203,failed=0,notRun=0,full_suite=pin(suite,True),build=pin(build,True),build_log=pin(log,True),files=pins,copies=copies,source_admission_pin=pin(admitp,True),verification_passes=2,twoSHA_mismatches=0,old203_tests_unchanged=True,native_audio_verified=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True),ensure_ascii=False))
