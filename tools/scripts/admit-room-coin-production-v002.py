from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/room-coin-allocation-v001/compat-v002'
O=D/'evidence/room-coin-allocation-v001/root-threeRED-production-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'final-freeze-v002.json';assert desc(f)['sha256']=='b4e4214ea067ec27f5dadb8d28b7aef622a7e78845ae650c53196ab70e76dbf9'
for row in read(f)['files']:assert desc(Path(row['path']))==row
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-001348/index.json';v=read(report)
assert v['failed']==len(v['tests'])==3 and v['succeeded']==0 and all(v.get(k,0)==0 for k in ['succeededWithWarnings','notRun','inProcess'])
assert all(t['state']=='Fail' and t['errors']==1 and t['warnings']==0 and len(t['entries'])==1 and "Explicit full manifest preallocates successfully" in t['entries'][0]['event']['message'] for t in v['tests'])
actual=R/'UnrealGame/Source/CodexDungeon';tests=actual/'Tests/DungeonRoomCoinAllocationTests.cpp';assert desc(tests)['sha256']=='8453e3d39af11540077c147238856300fcf57a9530b044b6f4822ab506c915d5'
assert desc(actual/'DungeonRoomCoinAllocation.cpp')['sha256']=='6b0d70dfdea1e41f9bde7ed06110251818cbfc4c9d22f26d56c7befcec38a4e8'
assert desc(B/'candidate-source/DungeonRoomCoinAllocation.cpp')['sha256']=='66fd8d41d9351d228aab559edd5226a755c88393ff4559e62ca5e8eb3cb035e8'
assert desc(B/'candidate-source/DungeonRoomCoinAllocation.h')['sha256']=='7a3cbb3591f1049559ebb85bf467a92c2a99cf0ffc16f583fd256c64fd84eb1e'
build=R/'UnrealGame/Saved/Bootstrap/build-editor-20261017-001032.log';last=read(R/'UnrealGame/Saved/Bootstrap/last-build.json');assert last['ExitCode']==0 and Path(last['Log']).resolve()==build.resolve()
assert not O.exists();O.mkdir(parents=True)
for p in [actual/'DungeonRoomCoinAllocation.h',actual/'DungeonRoomCoinAllocation.cpp',tests,report,build,R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',f]:
 q=O/'compiled-threeRED-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file() and p.name not in ['DungeonRoomCoinAllocation.cpp','DungeonRoomCoinAllocation.h']}
after=[]
for name in ['DungeonRoomCoinAllocation.h','DungeonRoomCoinAllocation.cpp']:
 p=actual/name;q=B/'candidate-source'/name;shutil.copy2(q,p);os.utime(p,None);assert p.read_bytes()==q.read_bytes();after.append(desc(p))
assert all(desc(p)==row for p,row in before.items())
(O/'admission.json').write_text(json.dumps(dict(actual_UE_threeRED=desc(report),production_files=after,all_other_Source_and_tests_unchanged=True,source_mtime_refreshed=True,Build_cs_unchanged=True,no_EH_module_enable=True,actual_UE_GREEN=None,actual_room_source_manifest_binding=None,actual_reward_payout=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['actual_registered_test_count_current']=154;v['current_source_uncompiled_changes']='RoomCoin3actualcleanRED preserved then compat2 h/CPP production admitted/uncompiled; GuardNative3actualcleanRED still honest stub, production not yet admitted.';v['room_coin_allocation_v001'].update(actual_UE_RED=desc(report),production_admission=desc(O/'admission.json'),actual_UE_GREEN=None,formal_room_binding=None,actual_payout=False);v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(preserved_actual_UE_threeRED=True,production_files_changed=2,other_Source_unchanged=True,actual_GREEN_not_yet=True),ensure_ascii=False))
