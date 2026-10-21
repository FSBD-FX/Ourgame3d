"""Freeze the current compiled binding proof inputs without borrowing historical test results."""
from pathlib import Path
import argparse,hashlib,json,os,shutil

R=Path('F:/Ourgame')
def io(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
def read(p):return json.loads(io(p).read_text(encoding='utf-8-sig'))
def desc(p):
    b=io(p).read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--name',required=True);ap.add_argument('--build-log',required=True)
ap.add_argument('--automation-report');ap.add_argument('--expected-tests',type=int,default=144);ap.add_argument('--extra',action='append',default=[]);args=ap.parse_args()
assert args.name and all(c.isalnum() or c in '_-' for c in args.name)
out=R/'source-assets/production/backups'/args.name;assert not io(out).exists()
build=(R/args.build_log).resolve();assert build.is_relative_to(R)
last=R/'UnrealGame/Saved/Bootstrap/last-build.json';lastv=read(last)
assert lastv['ExitCode']==0 and Path(lastv['Log']).resolve()==build and lastv['Target']=='CodexDungeonEditor'
automation=None
if args.automation_report:
    report=(R/args.automation_report).resolve();assert report.is_relative_to(R);automation=read(report)
    assert automation['succeeded']==args.expected_tests and len(automation['tests'])==args.expected_tests
    assert len({t['fullTestPath'] for t in automation['tests']})==args.expected_tests
    assert all(automation.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
    assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in automation['tests'])
old=read(R/'source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116/compiled-source-manifest.json')
oldproduction={x['path']:x for x in old['files'] if x['path'].startswith('UnrealGame/Content/Production/')}
paths=[]
for directory in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content/Production']:
    for p in io(R/directory).rglob('*'):
        if p.is_file():paths.append(Path(str(p)[4:]) if str(p).startswith('\\\\?\\') else p)
production={p.relative_to(R).as_posix():p for p in paths if p.is_relative_to(R/'UnrealGame/Content/Production')}
assert len(production)==1085 and set(production)==set(oldproduction)
assert all(desc(p)==oldproduction[k] for k,p in production.items()), 'Existing production asset changed'
paths += [build,last,R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__).resolve(),R/'tools/scripts/test-first-room.ps1']
if automation is not None:paths.append(report)
for name in args.extra:
    p=(R/name).resolve();assert p.is_relative_to(R) and io(p).is_file();paths.append(p)
rows=[]
for p in sorted(set(paths)):
    row=desc(p);q=out/row['path'];io(q.parent).mkdir(parents=True,exist_ok=True)
    assert not io(q).exists();shutil.copy2(io(p),io(q));assert io(q).read_bytes()==io(p).read_bytes()
    rows.append(row)
for row in rows:
    assert desc(R/row['path'])==row
    q=out/row['path'];assert io(q).stat().st_size==row['bytes'] and hashlib.sha256(io(q).read_bytes()).hexdigest()==row['sha256']
result=dict(schema='equipment-bound-current-build-freeze-v002',snapshot=out.as_posix(),status=f'current{args.expected_tests}GREEN_before_native_flow' if automation else 'current_compiled_native_RED_fixture_no_current_full_test_claim',files=rows,copied_files=len(rows),bytes=sum(x['bytes'] for x in rows),production_packages=1085,old_production_unchanged=True,current_automation_report=args.automation_report,current_automation_succeeded=args.expected_tests if automation else None,build_log=args.build_log,source_and_copy_checks=2*len(rows),mismatches=0,formal_complete_units=0)
io(out/'compiled-source-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
