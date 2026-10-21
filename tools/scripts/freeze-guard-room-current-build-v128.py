from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--report',required=True);p.add_argument('--name',default='v128-guard-room-176G');a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
report=(R/a.report).resolve();assert report.is_relative_to(R)
suite=read(report);assert (suite['succeeded'],suite['failed'],suite['succeededWithWarnings'],suite['notRun'],suite['inProcess'])==(176,0,0,0,0)
assert len(suite['tests'])==176 and len({x['fullTestPath'] for x in suite['tests']})==176
assert all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in suite['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
log=Path(b['Log']);assert log.is_file()
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';assert dll.is_file()
files=set()
for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:
 files.update(q for q in (R/folder).rglob('*') if q.is_file())
files.update([R/'UnrealGame/CodexDungeon.uproject',dll,build,log,report])
for name in ['capture-guard-room-native-flow-v001.ps1','verify-guard-room-native-flow-v001.py','prepare-guard-room-native-media-v001.py','launch-guard-room-native-trial-v001.ps1','verify-native-bound-capture-pixels-v001.py','test-first-room.ps1','unreal-build.ps1','freeze-guard-room-current-build-v128.py']:
 files.add(R/'tools/scripts'/name)
sources=[q for q in files if q.is_relative_to(R/'UnrealGame/Source')];production=[q for q in files if q.is_relative_to(R/'UnrealGame/Content/Production')]
assert len(sources)==213 and len(production)==1210
assert dll.stat().st_mtime>=max(q.stat().st_mtime for q in sources),'DLL predates current Source'
assert a.name and '/' not in a.name and '\\' not in a.name
out=R/'source-assets/production/backups'/a.name;assert not out.exists();out.mkdir(parents=True)
rows=[];copied=0
for q in sorted(files):
 row=pin(q);rows.append(row)
 if not q.is_relative_to(R/'UnrealGame/Content'):
  target=out/'files'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
  assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256'];copied+=1
for repeat in range(2):
 for row in rows:
  q=R/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
manifest=dict(version=a.name,strict_registered_tests=176,production_files=1210,source_files=len(sources),full_suite=pin(report),current_build=pin(build),files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,content_packages_pinned_in_place=True,formal_complete_units=0,native_flow_proof=None,art_accepted=False)
(out/'compiled-source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text('Actual Source/Config/tools/build/report are copied. Immutable Content is pinned in place and verified twice; no duplicate content-package copy is claimed. Full176 strictGREEN, native flow/visual review still pending, formal complete0/15.\n',encoding='utf-8')
print(json.dumps(dict(snapshot=out.as_posix(),files=len(rows),copied=copied,source=len(sources),production=len(production),full176GREEN=True,hash_mismatches=0)))
