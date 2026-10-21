"""Freeze actual v143 build and unchanged complete203; derive Source inventory from admission."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001'
def need(v,s):
 if not v:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);ap.add_argument('--output-name',required=True);a=ap.parse_args()
need(a.output_name.replace('-','').replace('_','').isalnum(),'Safe NEW snapshot name required')
adpath=EV/'Root-source-admission-v001/actual-source-admission.json';repairpath=EV/'Root-Printf-literal-repair-v001/actual-source-repair-admission.json';ad=read(adpath);repair=read(repairpath)
need(ad['RootApproved'] is True and ad['actual_applied'] is True and repair['actual_applied'] is True,'Actual reviewed admission and literal repair required')
suite=Path(a.suite).resolve();need(suite.is_relative_to(R/'UnrealGame/Saved/Automation'),'Actual native automation report required');q=read(suite)
need(tuple(q[k] for k in ['succeeded','succeededWithWarnings','failed','notRun','inProcess'])==(203,0,0,0,0),'Full203 strictly GREEN required')
need(len(q['tests'])==len({x['fullTestPath'] for x in q['tests']})==203,'203 unique actual tests required')
for t in q['tests']:
 need(t['state']=='Success' and t['warnings']==0 and t['errors']==0 and not any(e['event']['type'] in ('Error','Warning') for e in t['entries']),'Test not strictly GREEN')
before=read(ad['predecessor_compiled_manifest']['path']);changed={x['path']:x for x in ad['after_files']};repaired=Path(repair['after']['path']);changed[repaired.relative_to(R).as_posix()]=pin(repaired)
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());prod=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
oldsource={x['path'] for x in before['files'] if x['path'].startswith('UnrealGame/Source/')};newnames={x for x in changed if x not in oldsource}
need(len(newnames)==ad['new_source_files']==2 and {p.relative_to(R).as_posix() for p in source}==oldsource|newnames,'Reviewed exact Source inventory required')
need(len(source)==ad['actual_source_files'] and len(prod)==ad['actual_production_files']==1419,'Derived actual count differs')
for row in before['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')) and row['path'] not in changed:need(pin(R/row['path'])==row,'Unrelated source/test/production changed')
for row in changed.values():need(pin(R/row['path'])==row,'Current admitted source differs')
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);need(b['ExitCode']==0,'Latest actual build failed');log=Path(b['Log'])
def dt(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
need(dt(b['Utc'])>dt(repair['utc']) and suite.stat().st_mtime>=dt(b['Utc']).timestamp(),'Fresh build and subsequent suite required')
O=R/'source-assets/production/backups'/a.output_name;need(not O.exists(),'Preserve old snapshot');O.mkdir()
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';files=source+prod+[dll,build,log,suite];pins=[pin(p) for p in files];copies=[]
for p in source+[dll,build,log,suite,adpath,repairpath]:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);need(pin(dst)['sha256']==pin(p)['sha256'],'Snapshot copy differs');copies.append(dict(source=pin(p),copy=pin(dst)))
for repeat in range(2):
 for row in pins:need(pin(R/row['path'])==row,'Actual compiled input changed during freeze')
report=dict(schema='Root-hero-landing-priority-full203-GREEN-build-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=len(source),production_files=len(prod),registered_tests=203,passed=203,failed=0,notRun=0,full_suite=pin(suite,True),build=pin(build,True),build_log=pin(log,True),files=pins,copies=copies,source_admission_pin=pin(adpath,True),supplemental_source_repair_pin=pin(repairpath,True),verification_passes=2,twoSHA_mismatches=0,native_landing_actions_reviewed=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
out=O/'compiled-source-manifest.json'
with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True)))
