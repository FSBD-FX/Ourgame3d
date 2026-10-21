from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'source-assets/production/backups/v127-walk-169G';assert not O.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-091143';d=read(report/'index.json')
assert len(d['tests'])==len({t['fullTestPath'] for t in d['tests']})==d['succeeded']==169
assert all(d[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in d['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0 and Path(b['Log']).name=='build-editor-20261018-091037.log'
paths=set()
for folder in ['UnrealGame/Source','UnrealGame/Config','UnrealGame/Content/Production','tools/scripts']:
 paths.update(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo'))
paths.update([R/'UnrealGame/CodexDungeon.uproject',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',build,Path(b['Log'])])
paths.update(p for p in report.rglob('*') if p.is_file())
B=R/'source-assets/production/fairytale-lgt-readability-v003'
for folder in ['walk-profile-root-v001','walk-native-root-profile-input-v001','walk-native-proof-candidate-v001/tooling','walk-import-candidate-v001']:
 paths.update(p for p in (B/folder).rglob('*') if p.is_file() and p.suffix in ('.json','.py','.ps1','.md','.inl'))
manifest=B/'walk-import-candidate-v001/import-walk48-v001.json';assets=read(manifest)
paths.update(Path(x['source']) for x in assets['assets'])
paths.update(Path(x['path']) for x in assets['references'].values())
paths.add(B/'walk-native-proof-candidate-v001/native-code-freeze-v003.json')
paths.add(R/'UnrealGame/Saved/Bootstrap/fairytale-walk48-v001-import-20261018-010848-373769.json')
production=[p for p in paths if p.is_relative_to(R/'UnrealGame/Content/Production')];assert len(production)==1199
O.mkdir(parents=True);rows=[]
for p in sorted(paths):
 row=desc(p);q=O/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(row)
for row in rows:
 assert desc(R/row['path'])==row and (O/row['path']).stat().st_size==row['bytes'] and hashlib.sha256((O/row['path']).read_bytes()).hexdigest()==row['sha256']
result=dict(schema='current-compiled-ground-walk-v127',files=rows,file_count=len(rows),endpoint_checks=2*len(rows),endpoint_mismatches=0,strict_registered_tests=169,full_suite=desc(report/'index.json'),current_build=desc(build),production_files=1199,new_walk_files=48,old_production_files=1151,profile_scope='80 art tuned CycleDistanceWorld/.498; unchanged movement speed; displayRoot and artistGripAxis; no foot lock/zero slip',current_art_static_source_review=True,native_walk_visual_review=False,guard_two_process_proved=False,formal_complete_units=0)
(O/'compiled-source-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False))
