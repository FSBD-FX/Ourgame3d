from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/room-coin-allocation-v001'
O=D/'evidence/room-coin-allocation-v001/root-stage0-admission-v001'
N=D/'evidence/stone-guard-native-v001/root-stage0-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'final-freeze-v001.json';assert desc(f)['sha256']=='05618cc4736d416ae56b980500867180338e80bd98d0c3b1d6ea9051220169a3'
v=read(f)
for row in v['files']:assert desc(Path(row['path']))==row
prior=read(N/'admission.json');m=read(R/'source-assets/production/backups/2026-10-16_StoneGuardKernel-full148GREEN-beforeNative-v122/compiled-source-manifest.json')
expected={x['path']:x for x in m['files'] if x['path'].startswith('UnrealGame/Source/')}
for row in prior['after']:expected[Path(row['path']).relative_to(R).as_posix()]={**row,'path':Path(row['path']).relative_to(R).as_posix()}
actual={p.relative_to(R).as_posix():p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};assert set(expected)==set(actual)
for k,p in actual.items():d=desc(p);assert d['bytes']==expected[k]['bytes'] and d['sha256']==expected[k]['sha256'],p
red=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-000138/index.json';report=read(red)
assert report['failed']==len(report['tests'])==3 and report['succeeded']==0
assert all(report.get(k,0)==0 for k in ['succeededWithWarnings','notRun','inProcess'])
assert all(t['errors']==1 and t['warnings']==0 and t['state']=='Fail' and len(t['entries'])==1 and 'Stage0 semantic stub' in t['entries'][0]['event']['message'] for t in report['tests'])
nativeOverlay=N/'actual-compiled-threeRED-overlay-v001';assert not nativeOverlay.exists();nativeOverlay.mkdir()
for p in [Path(x['path']) for x in prior['after']]+[R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',R/'UnrealGame/Saved/Bootstrap/build-editor-20261016-235751.log',red]:
 q=nativeOverlay/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
assert not O.exists();O.mkdir(parents=True);shutil.copy2(f,O/f.name);shutil.copy2(D/'progress.json',O/'before-progress.json')
files=[(B/'stage0/DungeonRoomCoinAllocation.h',R/'UnrealGame/Source/CodexDungeon/DungeonRoomCoinAllocation.h'),(B/'stage0/DungeonRoomCoinAllocation.cpp',R/'UnrealGame/Source/CodexDungeon/DungeonRoomCoinAllocation.cpp'),(B/'tests/DungeonRoomCoinAllocationTests.cpp',R/'UnrealGame/Source/CodexDungeon/Tests/DungeonRoomCoinAllocationTests.cpp')]
added=[]
for p,q in files:
 assert p.is_file() and not q.exists();shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes();added.append(desc(q))
(O/'admission.json').write_text(json.dumps(dict(source_freeze=desc(f),added=added,old_Source_checked=len(actual),old_Source_bytes_unchanged=True,guard_actual_threeRED=desc(red),guard_compiled_RED_overlay=nativeOverlay.as_posix(),native_driver_production_not_applied=True,prospective_full_after_production=154,actual_compile=None,actual_UE_RED=None,room_source_node_binding=None,actual_reward_payout=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v['current_source_uncompiled_changes']='STN003 native honest Stage0 now compiled235751 and actual3cleanRED000138; NEW roomCoin h/stubCpp/3UE groups now added, uncompiled. Both production candidates not admitted.';v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['stone_guard_native_v001']['actual_UE_RED']=desc(red);v['room_coin_allocation_v001']=dict(stage0_admission=desc(O/'admission.json'),actual_UE_RED=None,actual_UE_GREEN=None,formal_room_binding=None,actual_payout=False);v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(preserved_native3cleanRED=True,added_source=3,old_source_unchanged=True,next='compile then3RoomCoin RED',prospective_full154_not_actual=True),ensure_ascii=False))
