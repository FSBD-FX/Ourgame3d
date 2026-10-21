from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-native-v001';D=R/'docs/production/first-batch-v2'
O=D/'evidence/stone-guard-native-v001/root-production-admission-v001';S=R/'UnrealGame/Source/CodexDungeon'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'production-freeze-v001.json';assert desc(f)['sha256']=='7a3c607bfd01a350408ecc4337c55ded799e055bca9fabefbd728c010a388dc0'
v=read(f)
for row in v['files']:assert desc(Path(row['path']))==row
test=S/'Tests/DungeonStoneGuardNativeTests.cpp';assert desc(test)['sha256']=='406892b287684c00e753b39e36c8eee62722e68717af37a53c6b23bb3732a93d'
assert desc(S/'DungeonStoneGuardDriver.cpp')['sha256']=='f8196dfa481079a684f5690fd0d24472b4eaaeea592ca9dffad2ce83b4155780'
assert desc(S/'DungeonStoneGuardDriver.h')['sha256']=='55e4e8eaa74ad93022ebd23f18049cfa3833559dd22c651c2868f6ebbda76b1a'
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-003132/index.json';q=read(report)
assert q['succeeded']==len(q['tests'])==3 and all(q.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in q['tests'])
patch=B/'patches/production-after-stage0-v001.patch'
subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
assert not O.exists();O.mkdir(parents=True)
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
for p in [*before,R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',report,R/'UnrealGame/Saved/Bootstrap/build-editor-20261017-002226.log',f,D/'progress.json']:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
subprocess.run(['git','apply',str(patch)],cwd=R,check=True)
shutil.copy2(B/'candidate-source/DungeonStoneGuardDriver.cpp',S/'DungeonStoneGuardDriver.cpp')
names=['DungeonStoneGuardDriver.cpp','DungeonFighter.cpp','DungeonGameMode.cpp','DungeonWorldProjectiles.cpp','DungeonHUD.cpp']
changed={p for p,d in before.items() if desc(p)!=d};assert changed=={S/n for n in names}
for n in names:
 p=S/n;c=B/'candidate-source'/n
 assert p.read_bytes().replace(b'\r\n',b'\n')==c.read_bytes().replace(b'\r\n',b'\n'),n
 os.utime(p,None)
assert desc(test)['sha256']=='406892b287684c00e753b39e36c8eee62722e68717af37a53c6b23bb3732a93d'
(O/'admission.json').write_text(json.dumps(dict(production_freeze=desc(f),actual_coin_threeGREEN=desc(report),before_source=list(before.values()),after_changed=[desc(S/n) for n in names],all_other_Source_tests_unchanged=True,source_mtime_refreshed=True,actual_native_production_compiled=False,actual_native_production_GREEN=None,actual_full154_GREEN=None,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['actual_registered_test_count_current']=154;v['current_source_uncompiled_changes']='NativeGuard production five CPP admitted after actual3 cleanRED; compiling pending. Coin compat2 actual3GREEN; full154 not run.';v['room_coin_allocation_v001']['actual_UE_GREEN']=desc(report);v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(admitted_changed_cpp=names,tests_unchanged=True,coin_actual_threeGREEN=True,native_production_compiled=False),ensure_ascii=False))
