"""Pin actual compiled project and exact real Stomp test outcome, with two SHA passes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil
R=Path('F:/Ourgame')
p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--report',required=True)
p.add_argument('--source-count',type=int,required=True);p.add_argument('--production-count',type=int,required=True)
p.add_argument('--mode',choices=['stage0','green'],required=True);p.add_argument('--extra',action='append',default=[]);a=p.parse_args()
def io(q):return Path('\\\\?\\'+str(q.resolve())) if os.name=='nt' else q
def read(q):return json.loads(io(q).read_text(encoding='utf-8-sig'))
def sha(q):
    h=hashlib.sha256()
    with io(q).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=io(q).stat().st_size,sha256=sha(q))
report=Path(a.report);report=report if report.is_absolute() else R/report;d=read(report)
tests=d['tests'];assert len(tests)==len({t['fullTestPath'] for t in tests})==193
assert d['notRun']==d['inProcess']==d['succeededWithWarnings']==0
failed=[t for t in tests if t['state']!='Success']
assert (d['succeeded'],d['failed'])==((190,3) if a.mode=='stage0' else (193,0))
assert all(t['warnings']==0 for t in tests)
if a.mode=='stage0':
    expected={'CodexDungeon.Content.FairytaleGuardStompV004.'+s for s in [
        'RealNativeHalfOpenClockAndEventIdentity','Versioned50BindingsAndAtomicMirroredFloor',
        'RealActorReceiptRecoveryAndInterruptedExclusion']}
    assert {t['fullTestPath'] for t in failed}==expected
    for t in failed:
        errors=[e['event']['message'] for e in t['entries'] if e['event']['type']=='Error']
        assert t['errors']==len(errors)==1 and 'TARGET Stage0:' in errors[0]
assert all(t['errors']==0 for t in tests if t['state']=='Success')
last=R/'UnrealGame/Saved/Bootstrap/last-build.json';build=read(last);assert build['ExitCode']==0
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';log=Path(build['Log'])
files={Path(__file__),report,last,log,dll,R/'UnrealGame/CodexDungeon.uproject'}
for f in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:
    files.update(q for q in (R/f).rglob('*') if q.is_file())
for x in a.extra:
    q=R/x
    if q.is_dir():files.update(z for z in q.rglob('*') if z.is_file() and not z.name.endswith('.sg-rwlock'))
    else:assert q.is_file();files.add(q)
sources=[q for q in files if q.is_relative_to(R/'UnrealGame/Source')]
production=[q for q in files if q.is_relative_to(R/'UnrealGame/Content/Production')]
assert len(sources)==a.source_count and len(production)==a.production_count
assert dll.stat().st_mtime>=max(q.stat().st_mtime for q in sources)
out=R/'source-assets/production/backups'/a.version;assert not out.exists();out.mkdir(parents=True)
rows=[];copied=0
for q in sorted(files):
    x=pin(q);rows.append(x)
    if not q.is_relative_to(R/'UnrealGame/Content'):
        target=out/'files'/x['path'];io(target).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(io(q),io(target));copied+=1
for repeat in range(2):
    for x in rows:
        q=R/x['path'];assert pin(q)==x
        if not q.is_relative_to(R/'UnrealGame/Content'):
            target=out/'files'/x['path'];assert io(target).stat().st_size==x['bytes'] and sha(target)==x['sha256']
m=dict(version=a.version,utc=datetime.now(timezone.utc).isoformat(),mode=a.mode,
       strict_registered_tests=193,passed=d['succeeded'],failed=d['failed'],
       source_files=len(sources),production_files=len(production),full_suite=pin(report),current_build=pin(last),
       files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,
       formal_complete_units=0,art_accepted=False)
with (out/'compiled-source-manifest.json').open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(snapshot=out.as_posix(),input_pins=len(rows),copied=copied,source=len(sources),production=len(production),passed=d['succeeded'],failed=d['failed'],twoSHA0=True)))
