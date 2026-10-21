"""Freeze the actual strict181 build and pre-register its scoped Guard16 trial."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def write(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=(R/a.report).resolve();assert report.is_relative_to(R)
suite=read(report);assert (suite['succeeded'],suite['failed'],suite['succeededWithWarnings'],suite['notRun'],suite['inProcess'])==(181,0,0,0,0)
assert len(suite['tests'])==181 and len({x['fullTestPath'] for x in suite['tests']})==181
assert all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in suite['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0
log=Path(b['Log']);dll=R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll';assert log.is_file() and dll.is_file()
base=R/'source-assets/production/fairytale-guard-v001'
approval=read(base/'root-trial-registration-v001/approval.json')
assert approval['TrialAllowed'] and not approval['FinalAccepted']
template=read(base/'presentation-candidate-v002/Root-prereg-template-v001.json')
files=set()
for folder,freeze_name in [('presentation-observer-fix-candidate-v005','wake-native-regression-freeze-v005.json'),('presentation-observer-fix-candidate-v007','wake-driver-open-slice-fix-freeze-v007.json'),('presentation-observer-failfast-candidate-v004','observer-failfast-freeze-v004.json'),('presentation-observer-route-candidate-v009','observer-route-freeze-v009.json'),('presentation-observer-route-tooling-candidate-v010','observer-route-tooling-freeze-v010.json')]:
 root=base/folder;f=root/freeze_name;files.add(f)
 for row in read(f)['files']:
  q=root/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'];files.add(q)
for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content']:
 files.update(q for q in (R/folder).rglob('*') if q.is_file())
files.update([R/'UnrealGame/CodexDungeon.uproject',dll,build,log,report,Path(__file__)])
for folder,freeze in [('presentation-candidate-v001','presentation-freeze-v001.json'),('presentation-candidate-v002','observer-freeze-v002.json')]:
 root=base/folder;f=root/freeze;files.add(f)
 for row in read(f)['files']:
  q=root/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'];files.add(q)
for name in ['approval.json','import-manifest.json','independent-import-verification-v001.json']:
 files.add(base/'root-trial-registration-v001'/name)
for row in approval['rows']:
 evidence=row['registration_evidence'];q=R/evidence['path'];assert q.stat().st_size==evidence['bytes'] and sha(q)==evidence['sha256'];files.add(q)
 for frame in row['frames']:
  f=frame['source'];q=Path(f['path']);assert q.stat().st_size==f['bytes'] and sha(q)==f['sha256'];files.add(q)
sources=[q for q in files if q.is_relative_to(R/'UnrealGame/Source')];production=[q for q in files if q.is_relative_to(R/'UnrealGame/Content/Production')]
assert len(sources)==223 and len(production)==1226
assert dll.stat().st_mtime>=max(q.stat().st_mtime for q in sources),'DLL predates current Source'
out=R/'source-assets/production/backups/v131-guard-partial-181G';assert not out.exists();out.mkdir(parents=True)
rows=[];copied=0
for q in sorted(files):
 row=pin(q);rows.append(row)
 if not q.is_relative_to(R/'UnrealGame/Content'):
  target=out/'files'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
  assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256'];copied+=1
for repeat in range(2):
 for row in rows:
  q=R/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
  if not q.is_relative_to(R/'UnrealGame/Content'):
   target=out/'files'/row['path'];assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256']
manifest=dict(version=out.name,strict_registered_tests=181,production_files=1226,source_files=223,full_suite=pin(report),current_build=pin(build),files=rows,source_verification_passes=2,source_hash_mismatches=0,source_config_tools_build_copies=copied,content_packages_pinned_in_place=True,formal_complete_units=0,native_flow_proof=None,art_accepted=False)
write(out/'compiled-source-manifest.json',manifest)
actual={row['path']:row for row in rows}
prereg=template;prereg.update(status='ROOT_APPROVED_SCOPED_TRIAL_NOT_FINAL',pre_registered_before_capture=True,compiled_manifest_sha256=sha(out/'compiled-source-manifest.json'),strict_registered_tests=181,source_files=223,production_files=1226)
prereg['admitted_source_files']=[actual[row['path']] for row in prereg['admitted_source_files']]
prereg['admitted_source_files'].append(actual['UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleGuardTerminalMaterialReviewTests.cpp'])
approved={row['clip']:row for row in approval['rows']}
for row in prereg['profile_facts']:
 ar=approved[row['clip']];row['trial_allowed']=ar['trial_allowed'];row['trial_approval_record']=ar['trial_approval_record']
 for f,af in zip(row['frames'],ar['frames']):assert f['object_path']==af['proposed_object_path'] and f['source']==af['source']
write(base/'root-trial-registration-v001/v131-partial-art-root-prereg-v001.json',prereg)
(out/'README.md').write_text('Actual strict181 GREEN. Source/Config/tools/build/report/Guard trial source inputs are copied and verified twice. Immutable Content is pinned in place twice, not duplicated. Guard16 partial trial only; native visual review pending; formal complete0/15.\n',encoding='utf-8')
print(json.dumps(dict(snapshot=out.as_posix(),files=len(rows),copied=copied,source=223,production=1226,full181GREEN=True,hash_mismatches=0,prereg_sha256=sha(base/'root-trial-registration-v001/v131-partial-art-root-prereg-v001.json'))))
