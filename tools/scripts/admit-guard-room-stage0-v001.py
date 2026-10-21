from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path('F:/Ourgame'); B=R/'source-assets/production/stone-guard-room-reward-v001'
O=R/'docs/production/first-batch-v2/evidence/guard-room-v001/root-stage0-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 d=p.read_bytes();return dict(path=p.as_posix(),bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
f=B/'stage0-freeze-v001.json'; v=read(f)
assert v['tests_remain_identical_for_production'] and len(v['test_groups'])==3
for row in v['files']:assert pin(Path(row['path']))==row
assert pin(Path(v['exact_before']['path']))==v['exact_before']
for row in read(Path(v['exact_before']['path']))['files']:assert pin(Path(row['path']))==row
snapshot=read(R/'source-assets/production/backups/v127-walk-169G/compiled-source-manifest.json')
expected={x['path']:x for x in snapshot['files'] if x['path'].startswith('UnrealGame/Source/')}
actual={p.relative_to(R).as_posix():p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
assert set(expected)==set(actual)
for k,p in actual.items():assert pin(p)['sha256']==expected[k]['sha256'] and p.stat().st_size==expected[k]['bytes']
targets=[]
for name in ['DungeonFirstBatchGuardRoom.h','DungeonGameMode.cpp','DungeonGameMode.h','DungeonRunRewards.h']:
 targets.append((B/'stage0-source'/name,R/'UnrealGame/Source/CodexDungeon'/name))
targets.append((B/'new-tests/DungeonFirstBatchGuardRoomTests.cpp',R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFirstBatchGuardRoomTests.cpp'))
assert not O.exists();O.mkdir(parents=True)
shutil.copy2(f,O/f.name)
progress=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(progress,O/'before-progress.json')
for src,dst in targets:
 if dst.exists():shutil.copy2(dst,O/('before-'+dst.name))
 shutil.copy2(src,dst);os.utime(dst,None);assert dst.read_bytes()==src.read_bytes()
record=dict(before_Source_checked=len(actual),files=[pin(dst) for src,dst in targets],test_groups=v['test_groups'],actual_compile=None,actual_RED=None,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(progress);p.update(goal_status='active',ue_current_working_source_compiled=False,ue_current_working_source_verified=False,
 current_source_uncompiled_changes='Guard Bridge finite room Stage0: explicit plan API and three native tests; production not admitted',
 current_task='EV048 Guard body identity and formal three-enemy room/reward/feedback production; actual Source Stage0 requires native RED then production GREEN.')
p['guard_room_v001']=dict(stage0_admission=pin(O/'admission.json'),actual_RED=None,actual_GREEN=None,formal_complete=False)
p['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(before_Source_checked=len(actual),changed=3,new=2,next='actual UBT compile then exact3semanticRED'),ensure_ascii=False))
