"""Pin actual compiled Death40 RED/GREEN evidence without changing prior snapshots."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil
R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['stage0-red','green'],required=True);p.add_argument('--report',required=True);p.add_argument('--version',required=True);a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x,base=R):
 p=Path(x['path']);p=p if p.is_absolute() else base/p
 assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
def io(p):return Path('\\\\?\\'+str(p.resolve())) if os.name=='nt' else p
report=Path(a.report);report=report if report.is_absolute() else R/report
assert report.resolve().is_relative_to(R)
t=read(report);tests=t['tests'];assert len(tests)==len({x['fullTestPath'] for x in tests})
assert t['succeededWithWarnings']==t['notRun']==t['inProcess']==0
if a.mode=='stage0-red':
 assert t['succeeded']==0 and t['failed']==len(tests)==3
 for x in tests:
  errors=[q['event']['message'] for q in x['entries'] if q['event']['type']=='Error']
  assert 'Fairytale' in x['fullTestPath'] and 'Death' in x['fullTestPath']
  assert x['state']=='Fail' and x['errors']==1 and x['warnings']==0 and len(errors)==1 and 'TARGET Stage0 RED:' in errors[0],x['fullTestPath']
else:
 assert t['succeeded']==len(tests)==190 and t['failed']==0
 assert all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in tests)
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';log=Path(b['Log'])
files={Path(__file__),report,build,log,dll,R/'UnrealGame/CodexDungeon.uproject'}
for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:
 files.update(q for q in (R/folder).rglob('*') if q.is_file())
sources={q for q in files if q.is_relative_to(R/'UnrealGame/Source')}
production={q for q in files if q.is_relative_to(R/'UnrealGame/Content/Production')}
assert len(production)==1326 and dll.stat().st_mtime>=max(q.stat().st_mtime for q in sources)
manifest=B/'Root-Death40-import-v001/import-manifest.json';m=read(manifest);files.add(manifest)
check(m['candidate_freeze']);check(m['root_trial_registration']);check(m['source_manifest'])
for key in ['candidate_freeze','root_trial_registration','source_manifest']:files.add(Path(m[key]['path']))
for x in m['assets']:check(x['source']);files.add(Path(x['source']['path']))
receipts=list((R/'UnrealGame/Saved/Bootstrap').glob('hero-Death40-v001-import-*.json'))
assert len(receipts)==1 and read(receipts[0])['success'];files.add(receipts[0])
for x in read(receipts[0])['assets']:check(x['saved'])
independent=list((B/'Root-Death40-import-v001').glob('independent-import-verification-*.json'))
assert len(independent)==1 and read(independent[0])['success'];files.add(independent[0])
for q in [R/'tools/scripts/ue-import-hero-Death40-v001.py',R/'tools/scripts/import-hero-Death40-v001.ps1',R/'tools/scripts/prepare-hero-Death40-import-v001.py']:files.add(q)
cf=read(Path(m['candidate_freeze']['path']))
for x in cf['files']:check(x);files.add(Path(x['path']))
for x in m['old_production_files']:check(x)
for dirname in (['Death40-native-observer-candidate-v001'] if a.mode=='green' else []):
 d=B/dirname
 if d.exists():files.update(q for q in d.rglob('*') if q.is_file())
out=R/'source-assets/production/backups'/a.version
assert out.parent==(R/'source-assets/production/backups') and not out.exists();out.mkdir()
rows=[];copied=0
for q in sorted(files):
 row=pin(q);rows.append(row)
 if not q.is_relative_to(R/'UnrealGame/Content'):
  target=out/'files'/row['path'];io(target).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(io(q),io(target));copied+=1
for repeat in range(2):
 for x in rows:
  check(x)
  if not x['path'].startswith('UnrealGame/Content/'):check(x,out/'files')
 for x in m['old_production_files']:check(x)
v=dict(version=a.version,status='ACTUAL_THREE_SEMANTIC_RED' if a.mode=='stage0-red' else 'ACTUAL_FULL190_GREEN',
 utc=datetime.now(timezone.utc).isoformat(),source_files=len(sources),production_files=len(production),
 full_suite=pin(report) if a.mode=='green' else None,focused_report=pin(report) if a.mode=='stage0-red' else None,
 strict_registered_tests=len(tests) if a.mode=='green' else None,focused_semantic_failed=3 if a.mode=='stage0-red' else None,
 fixture_or_compile_failure=False,current_build=pin(build),native_import_receipt=pin(receipts[0]),independent_import_receipt=pin(independent[0]),
 files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,
 content_packages_pinned_in_place=True,old1286_byte_unchanged=True,formal_complete_units=0,art_accepted=False,native_verified=False)
name='compiled-stage0-semantic-red-manifest.json' if a.mode=='stage0-red' else 'compiled-source-manifest.json'
target=out/name;target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'README.md').write_text(v['status']+'; Source'+str(len(sources))+'/Production1326. Old1286 unchanged,40 actual native imported. Snapshot copies/pins verified twice. Native Death40 both sides pending. Formal complete0/15.\n',encoding='utf-8')
print(json.dumps(dict(snapshot=out.as_posix(),manifest=pin(target),mode=a.mode,source=len(sources),production=1326,input_pins=len(rows),copied=copied,hash_mismatches=0)))
