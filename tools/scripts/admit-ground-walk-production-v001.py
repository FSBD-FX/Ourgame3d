from pathlib import Path
import hashlib,json,shutil,os
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/walk-runtime-candidate-v001'
E=R/'docs/production/first-batch-v2/evidence/ground-walk-v001'
RED=E/'root-threeRED-v001';O=E/'root-production-original-v001';assert not RED.exists() and not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def valid(row):
 p=R/row['path'];d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256']),p
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-085757';d=read(report/'index.json')
assert len(d['tests'])==3 and d['failed']==3 and all(d[k]==0 for k in ['succeeded','succeededWithWarnings','notRun','inProcess'])
for t in d['tests']:
 assert t['state']=='Fail' and t['errors']==1 and t['warnings']==0
 errors=[x['event']['message'] for x in t['entries'] if x['event']['type']=='Error']
 assert errors==["Expected 'Expected production completed-ground-motion witness after actual normal-input Tick' to be true."]
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';assert read(build)['ExitCode']==0 and Path(read(build)['Log']).name=='build-editor-20261018-085700.log'
for row in read(B/'production-freeze-v001.json')['files']:valid(row)
for row in read(B/'baseline-pins-v001.json')['actual_source_files']:
 if not row['path'].endswith(('DungeonFighter.h','DungeonFighter.cpp')):valid(row)
src=R/'UnrealGame/Source/CodexDungeon'
for rel in ['DungeonFighter.h','DungeonFighter.cpp','DungeonCompletedGroundMotion.h','DungeonGroundWalkPhase.h']:
 assert (src/rel).read_bytes()==(B/'stage0-source'/rel).read_bytes()
test=src/'Tests/DungeonFairytaleGroundWalkTests.cpp';fixed=B/'review-20261018-v001/test-header-repair-v002/DungeonFairytaleGroundWalkTests.cpp';assert test.read_bytes()==fixed.read_bytes()
RED.mkdir(parents=True);rows=[]
files=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()]+[build,Path(read(build)['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']+[p for p in report.rglob('*') if p.is_file()]
for p in files:
 q=RED/'compiled-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(desc(p),retained=q.relative_to(RED).as_posix()))
(RED/'manifest.json').write_text(json.dumps(dict(files=rows,native_test_count=3,native_failed=3,expected_errors_each=1,warnings=0,clean_semantic_RED=True,art_profile_configured=False),ensure_ascii=False,indent=2),encoding='utf-8')
before={p.relative_to(R).as_posix():desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
O.mkdir();(O/'before-source.json').write_text(json.dumps(list(before.values()),indent=2),encoding='utf-8')
dest=[]
for p in sorted((B/'production-source').glob('*')):
 q=src/p.name;shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes();dest.append(desc(q))
boundary=B/'review-20261018-v001/production-repair-v002';f=read(boundary/'freeze-v002.json');valid(f['new_test'])
p=R/f['new_test']['path'];q=src/'Tests'/p.name;assert not q.exists();shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes();dest.append(desc(q))
changed={rel for rel,x in before.items() if desc(R/rel)!=x}
allowed={f'UnrealGame/Source/CodexDungeon/{p.name}' for p in (B/'production-source').glob('*')}
assert changed<=allowed and test.read_bytes()==fixed.read_bytes(),changed
receipt=dict(production_freeze=desc(B/'production-freeze-v001.json'),previous_RED_manifest=desc(RED/'manifest.json'),destinations=dest,existing_changed=sorted(changed),original_three_assertions_unchanged=True,boundary_test_admitted_repair_not_applied=True,runtime_profile_configured=False,mtime_refreshed=True,actual_compile=False,registered_tests=168)
(O/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(retained_RED_files=len(rows),production_sources=len(dest)-1,new_boundary_test=1,registered_tests=168,profile_configured=False,receipt=str(O/'admission.json'))))
