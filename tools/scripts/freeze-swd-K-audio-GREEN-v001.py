from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001';O=R/'source-assets/production/backups/v147-SWDStepAudio303-1439-203GREEN-v001'
ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);a=ap.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,rel=False):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if rel else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
adp=EV/'Root-forward-step-regression-source-admission-v001/actual-source-admission.json';ad=read(adp);old=read(Path(ad['predecessor_compiled_manifest']['path']));changed={x['path']:x for x in ad['after_files']}
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'],True)==changed.get(row['path'],row)
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());content=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file());assert len(source)==303 and len(content)==1439
suite=Path(a.suite).resolve();q=read(suite);assert suite.is_relative_to(R/'UnrealGame/Saved/Automation');assert [q[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess')]==[203,0,0,0,0]
assert len(q['tests'])==203 and {t['fullTestPath'] for t in q['tests']}=={t['fullTestPath'] for t in read(Path(old['full_suite']['path']))['tests']}
for t in q['tests']:assert t['state']=='Success' and t['warnings']==t['errors']==0 and not any(x['event']['type'] in ('Error','Warning') for x in t['entries'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0 and datetime.fromisoformat(b['Utc'].replace('Z','+00:00'))>datetime.fromisoformat(ad['utc']);assert suite.stat().st_mtime>=datetime.fromisoformat(b['Utc'].replace('Z','+00:00')).timestamp()
log=Path(b['Log']);dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';files=source+content+[build,log,suite,dll];pins=[pin(p,True) for p in files];assert not O.exists();O.mkdir()
for p in source+[build,log,suite,dll,adp,EV/'Root-forward-step-audio-source-admission-v001/actual-source-admission.json']:
 t=O/'snapshot'/p.relative_to(R);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t);assert pin(t)['sha256']==pin(p)['sha256']
for _ in range(2):
 for row in pins:assert pin(R/row['path'],True)==row
out=O/'compiled-source-manifest.json';out.write_text(json.dumps(dict(schema='Root-SWDStepAudio-current303-1439-full203-GREEN-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=303,production_files=1439,production_textures=1433,SoundWaves=6,registered_tests=203,passed=203,failed=0,build=pin(build),build_log=pin(log),full_suite=pin(suite),source_admission_pin=pin(adp),files=pins,verification_passes=2,twoSHA_mismatches=0,old203_test_IDs_preserved=True,regression_GREEN=True,native_K_art_or_audio_verified=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(out),ensure_ascii=False))
