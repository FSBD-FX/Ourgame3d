"""Freeze the actual complete203 GREEN build; no native visual acceptance claim."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,s):
 if not v:raise ValueError(s)
ap=argparse.ArgumentParser();ap.add_argument('--suite',required=True);ap.add_argument('--expected-source',required=True,type=int);ap.add_argument('--output-name',required=True);a=ap.parse_args()
need(a.expected_source in (294,296),'Actual reviewed Air source count required')
need(a.output_name.replace('-','').replace('_','').isalnum(),'Safe snapshot folder name required')
suite=Path(a.suite).resolve();need(suite.is_relative_to(R/'UnrealGame/Saved/Automation'),'Actual automation report required');q=read(suite)
need(tuple(q[k] for k in ['succeeded','succeededWithWarnings','failed','notRun','inProcess'])==(203,0,0,0,0),'Full203 strictly GREEN required')
need(len(q['tests'])==203 and len({t['fullTestPath'] for t in q['tests']})==203,'203 unique tests required')
for t in q['tests']:
 need(t['state']=='Success' and t['warnings']==0 and t['errors']==0,'Test not strictly GREEN')
 need(not any(e['event']['type'] in ('Error','Warning') for e in t['entries']),'Warning/error entry present')
source=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());prod=sorted(p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file())
need(len(source)==a.expected_source and len(prod)==1419,'Actual Source/Production count differs')
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);need(b['ExitCode']==0,'Latest actual build failed');log=Path(b['Log']);need(log.is_file() and 'build-editor-20261019-' in log.name,'Fresh current build required')
O=R/'source-assets/production/backups'/a.output_name;need(not O.exists(),'New snapshot required');O.mkdir()
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';files=source+prod+[dll,build,log,suite];pins=[pin(p) for p in files];copies=[]
for p in source+[dll,build,log,suite]:
 dst=O/'snapshot'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);need(pin(dst)['sha256']==pin(p)['sha256'],'Snapshot copy differs');copies.append(dict(source=pin(p),copy=pin(dst)))
for repeat in range(2):
 for row in pins:need(pin(R/row['path'])==row,'Actual compiled input changed during freeze')
report=dict(schema='Root-HeroAir6-full203-GREEN-build-v001',utc=datetime.now(timezone.utc).isoformat(),source_files=len(source),production_files=len(prod),registered_tests=203,passed=203,failed=0,notRun=0,full_suite=pin(suite,True),build=pin(build,True),build_log=pin(log,True),files=pins,copies=copies,verification_passes=2,twoSHA_mismatches=0,new_air_art_imported=True,native_new_air_reviewed=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
out=O/'compiled-source-manifest.json'
with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True)))
