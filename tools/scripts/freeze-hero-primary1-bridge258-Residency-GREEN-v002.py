from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);ap.add_argument('--source-admission',required=True);a=ap.parse_args()
adp=Path(a.source_admission).resolve();ad=read(adp);old=read(ad['predecessor_compiled_manifest']['path']);content=read(ad['content_admission_pin']['path'])
assert ad['RootApproved'] and ad['actual_applied'] and not ad['is_template'] and ad['actual_source_files']==303 and ad['actual_production_files']==1439
changed={x['path']:x for x in ad['after_files']};assert len(changed)==2
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'])==changed.get(row['path'],row)
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());production=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
assert len(source)==303 and len(production)==1439 and len(content['added'])==14
assert {p.relative_to(R).as_posix() for p in source}=={x['path'] for x in old['files'] if x['path'].startswith('UnrealGame/Source/')}
oldp={x['path'] for x in old['files'] if x['path'].startswith('UnrealGame/Content/Production/')}
assert {p.relative_to(R).as_posix() for p in production}==oldp|{x['path'] for x in content['added']}
for row in content['added']:assert pin(R/row['path'])==row
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);log=Path(b['Log']);suite=Path(a.suite).resolve();q=read(suite)
assert b['ExitCode']==0 and datetime.fromisoformat(b['Utc'].replace('Z','+00:00'))>datetime.fromisoformat(ad['utc'])
assert suite.is_relative_to(R/'UnrealGame/Saved/Automation') and suite.stat().st_mtime>=datetime.fromisoformat(b['Utc'].replace('Z','+00:00')).timestamp()
assert tuple(q[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess'))==(203,0,0,0,0)
assert len(q['tests'])==len({t['fullTestPath'] for t in q['tests']})==203
assert {t['fullTestPath'] for t in q['tests']}=={t['fullTestPath'] for t in read(old['full_suite']['path'])['tests']}
for t in q['tests']:assert t['state']=='Success' and t['warnings']==t['errors']==0 and not any(x['event']['type'] in ('Error','Warning') for x in t['entries'])
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
O=R/'source-assets/production/backups/v146-Primary1Bridge258-Residency-303-1439-203GREEN-v002';assert not O.exists();O.mkdir()
files=source+production+[dll,build,log,suite];pins=[pin(p) for p in files];copies=[]
for p in source+[R/x['path'] for x in content['added']]+[dll,build,log,suite,adp,Path(ad['content_admission_pin']['path']),Path(content['actual_import']['path']),Path(content['actual_process']['path'])]:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(p)['sha256']==pin(dst)['sha256'];copies.append(dict(source=pin(p),copy=pin(dst)))
for _ in range(2):
 for row in pins:assert pin(R/row['path'])==row
out=O/'compiled-source-manifest.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary1-bridge258-residency-full203-GREEN-build-v002',utc=datetime.now(timezone.utc).isoformat(),source_files=303,production_files=1439,production_textures=1433,production_new_SoundWaves=6,registered_tests=203,passed=203,failed=0,notRun=0,full_suite=pin(suite,True),build=pin(build,True),build_log=pin(log,True),files=pins,copies=copies,source_admission_pin=pin(adp,True),content_admission_pin=ad['content_admission_pin'],verification_passes=2,twoSHA_mismatches=0,old203_tests_unchanged=True,native_new_art_verified=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True),ensure_ascii=False))
