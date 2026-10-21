"""Retain actual compiled Stage0/three intended native semantic failures before implementation."""
from pathlib import Path
import hashlib,json,shutil,os
R=Path('F:/Ourgame'); report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-160223/index.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
j=read(report);assert (j['succeeded'],j['failed'],j['notRun'],j['inProcess'])==(0,3,0,0)
assert len(j['tests'])==len({t['fullTestPath'] for t in j['tests']})==3
for t in j['tests']:
 errors=[e['event']['message'] for e in t['entries'] if e['event']['type']=='Error']
 assert t['state']=='Fail' and t['errors']==1 and t['warnings']==0 and len(errors)==1 and 'TARGET Stage0 RED:' in errors[0]
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';assert read(build)['ExitCode']==0
files={report,build,Path(read(build)['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'}
for folder in ['UnrealGame/Source','UnrealGame/Config']:
 files.update(p for p in (R/folder).rglob('*') if p.is_file())
source=[p for p in files if p.is_relative_to(R/'UnrealGame/Source')]; assert len(source)==241
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';assert dll.stat().st_mtime>=max(p.stat().st_mtime for p in source)
out=R/'source-assets/production/backups/Hurt-stage0-actual-three-semantic-RED-v001'; assert not out.exists();out.mkdir(parents=True)
rows=[]
for p in sorted(files):
 row=pin(p);rows.append(row);q=out/'files'/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
prior=read(R/'source-assets/production/backups/v135-Death-184G/compiled-source-manifest.json')
production=[x for x in prior['files'] if x['path'].startswith('UnrealGame/Content/Production/')];assert len(production)==1254
for repeat in range(2):
 for x in rows:
  for p in [R/x['path'],out/'files'/x['path']]:assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 for x in production:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
receipt=dict(status='ACTUAL_THREE_SEMANTIC_RED_RETAINED',source_files=241,focused_tests=3,focused_semantic_failed=3,fixture_or_compile_failure=False,full_suite_not_run=True,registered_full_count_unverified=True,production1254_unchanged_twice=True,verification_passes=2,hash_mismatches=0,report=pin(report),files=rows,production=production,production_selector_implemented=False,formal_complete_units=0)
(out/'compiled-stage0-semantic-red-manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(snapshot=out.as_posix(),source=241,focused_semantic_RED=3,copied=len(rows),production=1254,hash_mismatches=0)))
