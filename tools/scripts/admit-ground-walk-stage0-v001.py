from pathlib import Path
import hashlib,json,shutil,os,datetime
R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-lgt-readability-v003/walk-runtime-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/ground-walk-v001/root-stage0-admission-v001'
assert not O.exists()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def valid(p,row):
 d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256']),p
freeze=B/'stage0-freeze-v001.json'
for row in read(freeze)['files']:valid(R/row['path'],row)
baseline=read(B/'baseline-pins-v001.json')
for row in baseline['actual_source_files']:valid(R/row['path'],row)
src=R/'UnrealGame/Source/CodexDungeon'
existing={p.relative_to(R).as_posix():desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
targets={
 'DungeonFighter.h':B/'stage0-source/DungeonFighter.h',
 'DungeonFighter.cpp':B/'stage0-source/DungeonFighter.cpp',
 'DungeonCompletedGroundMotion.h':B/'stage0-source/DungeonCompletedGroundMotion.h',
 'DungeonGroundWalkPhase.h':B/'stage0-source/DungeonGroundWalkPhase.h',
 'Tests/DungeonFairytaleGroundWalkTests.cpp':B/'new-tests/DungeonFairytaleGroundWalkTests.cpp'}
for rel in targets:
 if rel not in ('DungeonFighter.h','DungeonFighter.cpp'):assert not (src/rel).exists()
O.mkdir(parents=True)
for p in [src/'DungeonFighter.h',src/'DungeonFighter.cpp',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',R/'UnrealGame/Saved/Bootstrap/last-build.json',R/'docs/production/first-batch-v2/progress.json']:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert desc(p)['sha256']==desc(q)['sha256']
for rel,p in targets.items():
 q=src/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes()
changed={rel for rel,d in existing.items() if desc(R/rel)!=d}
assert changed=={'UnrealGame/Source/CodexDungeon/DungeonFighter.h','UnrealGame/Source/CodexDungeon/DungeonFighter.cpp'},changed
after={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
assert after-set(existing)=={f'UnrealGame/Source/CodexDungeon/{r}' for r in targets if r not in ('DungeonFighter.h','DungeonFighter.cpp')}
receipt={'schema':'ground-walk-stage0-admission-v001','freeze':desc(freeze),'before_source':list(existing.values()),'destinations':[desc(src/rel) for rel in targets],'other_source_unchanged':True,'mtime_refreshed':True,'actual_compile':False,'actual_RED':None,'previous_strict_registry':164,'new_registered_test_groups':3,'profile_configured':False}
(O/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';d=read(p)
d.update(date='2026-10-18',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Ground Walk Stage0 two API files and three new headers/test files admitted; native 3RED pending.',actual_registered_test_count_current=167,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
d['ground_walk_v001']={'stage0_admission':desc(O/'admission.json'),'actual_RED':None,'actual_GREEN':None,'profile_configured':False,'foot_lock_implemented':False,'formal_complete_units':0}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'stage0_admitted':True,'only_two_existing_source_changed':True,'new_files':3,'next':'actual UE compile and frozen three native RED','receipt':str(O/'admission.json')}))
