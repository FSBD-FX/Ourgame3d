"""Freeze actual strict184 inputs and fill a new Root first-Axe trial registration."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001';C=B/'presentation-full-known44-observer-candidate-v001'
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,v):
 assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=(R/a.report).resolve();assert report.is_relative_to(R);s=read(report)
assert (s['succeeded'],s['failed'],s['succeededWithWarnings'],s['notRun'],s['inProcess'])==(184,0,0,0,0)
assert len(s['tests'])==len({t['fullTestPath'] for t in s['tests']})==184 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in s['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
log=Path(b['Log']);dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
files={Path(__file__),report,build,log,dll,R/'UnrealGame/CodexDungeon.uproject'}
for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:
 files.update(q for q in (R/folder).rglob('*') if q.is_file())
for directory,name in [(B/'presentation-full-candidate-v003','presentation-full-freeze-v003.json'),(B/'presentation-full-candidate-v004','known44-admission-milestone-freeze-v004.json'),(C,'known44-AxeCycle-freeze-v001.json')]:
 f=directory/name;files.add(f)
 for row in read(f)['files']:
  q=directory/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'];files.add(q)
prereg=read(C/'root-templates/known44-AxeCycle-Root-prereg-TEMPLATE-v001.json')
for key in ['Root_row_trial_record_pin','actual_native_import_receipt_pin','independent_import_two_pass_receipt_pin']:
 row=prereg[key];q=Path(row['path']);assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'];files.add(q)
registration=B/'root-full-registration-v001';files.add(registration/'import-manifest.json')
for row in prereg['profile_facts']:
 for key in ['alias_evidence','registration_evidence','source_index']:
  if key in row:
   f=row[key];q=R/f['path'] if not Path(f['path']).is_absolute() else Path(f['path']);assert q.stat().st_size==f['bytes'] and sha(q)==f['sha256'];files.add(q)
 for frame in row['frames']:
  f=frame['source'];q=Path(f['path']);assert q.stat().st_size==f['bytes'] and sha(q)==f['sha256'];files.add(q)
sources=[q for q in files if q.is_relative_to(R/'UnrealGame/Source')];production=[q for q in files if q.is_relative_to(R/'UnrealGame/Content/Production')]
assert len(sources)==231 and len(production)==1254 and dll.stat().st_mtime>=max(q.stat().st_mtime for q in sources)
out=R/'source-assets/production/backups/v132-guard-known44-184G';assert not out.exists();out.mkdir(parents=True)
rows=[];copied=0
for q in sorted(files):
 row=pin(q);rows.append(row)
 if not q.is_relative_to(R/'UnrealGame/Content'):
  target=out/'files'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target);copied+=1
for repeat in range(2):
 for row in rows:
  q=R/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
  if not q.is_relative_to(R/'UnrealGame/Content'):
   target=out/'files'/row['path'];assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256']
manifest=dict(version=out.name,strict_registered_tests=len(s['tests']),production_files=len(production),source_files=len(sources),full_suite=pin(report),current_build=pin(build),files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,content_packages_pinned_in_place=True,formal_complete_units=0,art_accepted=False)
write(out/'compiled-source-manifest.json',manifest)
actual={x['path']:x for x in rows};prereg.update(is_template=False,pre_registered_before_capture=True,status='ROOT_SCOPED_KNOWN44_FIRST_AXE_TRIAL_NOT_FINAL',registered_at_utc=datetime.now(timezone.utc).isoformat(),compiled_manifest_sha256=sha(out/'compiled-source-manifest.json'),strict_registered_tests=len(s['tests']),source_files=len(sources),production_files=len(production))
prereg['admitted_source_files']=[actual[x['path']] for x in prereg['admitted_source_files']]
prereg['candidate_freeze_pin']=dict(path=(C/'known44-AxeCycle-freeze-v001.json').as_posix(),bytes=(C/'known44-AxeCycle-freeze-v001.json').stat().st_size,sha256=sha(C/'known44-AxeCycle-freeze-v001.json'))
dest=registration/'v132-known44-AxeCycle-Root-prereg-v001.json';write(dest,prereg)
(out/'README.md').write_text('Actual strict184 GREEN; Source231/Production1254. NonContent copies and all input pins verified twice. Root scoped known44 trial; native first-Axe and visual proof pending. Formal complete0/15.\n',encoding='utf-8')
print(json.dumps(dict(snapshot=out.as_posix(),snapshot_files=len(rows),source=len(sources),production=len(production),strict_registered_tests=len(s['tests']),copied=copied,hash_mismatches=0,prereg=dest.as_posix())))
