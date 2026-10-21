from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-native-v001';D=R/'docs/production/first-batch-v2'
O=D/'evidence/stone-guard-native-v001/root-stage0-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'stage0-freeze-v001.json';assert desc(f)['sha256']=='2707715ee895d33e7657d1b21f3da036ef5b2daae46ad78c63da041a3c96eeb1'
v=read(f);assert v['registration_count']==3 and v['prospective_full_after_new_groups']==151
for row in v['files']:assert desc(Path(row['path']))==row
m=read(R/'source-assets/production/backups/2026-10-16_StoneGuardKernel-full148GREEN-beforeNative-v122/compiled-source-manifest.json')
expected={x['path']:x for x in m['files'] if x['path'].startswith('UnrealGame/Source/')}
actual={p.relative_to(R).as_posix():p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
assert set(expected)==set(actual)
for k,p in actual.items():d=desc(p);assert d['bytes']==expected[k]['bytes'] and d['sha256']==expected[k]['sha256']
changed=['DungeonFighter.h','DungeonFighter.cpp','DungeonGameMode.h','DungeonGameMode.cpp']
for n in changed:assert (R/'UnrealGame/Source/CodexDungeon'/n).read_bytes()==(B/'before'/n).read_bytes()
newfiles=[(B/'stage0-v001/DungeonStoneGuardDriver.h',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuardDriver.h'),(B/'stage0-v001/DungeonStoneGuardDriver.cpp',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuardDriver.cpp'),(B/'tests/DungeonStoneGuardNativeTests.cpp',R/'UnrealGame/Source/CodexDungeon/Tests/DungeonStoneGuardNativeTests.cpp')]
assert all(not q.exists() for p,q in newfiles)
patch=B/v['existing_four_file_patch'];check=subprocess.run(['git','apply','--check',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert check.returncode==0,(check.stdout,check.stderr)
assert not O.exists();O.mkdir(parents=True);shutil.copy2(f,O/f.name);shutil.copy2(D/'progress.json',O/'before-progress.json')
for n in changed:shutil.copy2(R/'UnrealGame/Source/CodexDungeon'/n,O/('before-'+n))
run=subprocess.run(['git','apply',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');assert run.returncode==0,(run.stdout,run.stderr)
for n in changed:
 p=R/'UnrealGame/Source/CodexDungeon'/n;q=B/'stage0-v001'/n
 assert p.read_bytes().replace(b'\r\n',b'\n')==q.read_bytes().replace(b'\r\n',b'\n'),n
 os.utime(p,None)
for p,q in newfiles:shutil.copy2(p,q);os.utime(q,None);assert p.read_bytes()==q.read_bytes()
pins=[desc(R/'UnrealGame/Source/CodexDungeon'/n) for n in changed]+[desc(q) for p,q in newfiles]
write=dict(source_freeze=desc(f),prior_Source_v122_checked=len(actual),modified_files=4,new_files=3,after=pins,native_new_tests=3,prospective_full151_not_actual=True,git_apply_check=check.returncode,git_apply=run.returncode,source_mtime_refreshed=True,actual_compile=None,actual_UE_RED=None,production_applied=False,formal_complete_units=0)
(O/'admission.json').write_text(json.dumps(write,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(D/'progress.json');v.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='STN003 Native Stage0 4 API files +NEW Driver h/cpp/3 registered real UE integration tests; honest stub not yet compiled.',current_task='Continue EV048 light armor corrections184/185/186 and STN003 true NativeDriver. ActualSource now Native Stage0 uncompiled; priorv122148GREEN/nativev005 historical, production candidate not admitted.',goal_status='active',completed_content_units=0)
v['stone_guard_native_v001']=dict(stage0_admission=desc(O/'admission.json'),actual_UE_RED=None,actual_UE_GREEN=None,production_applied=False,native_runtime_proof=None,save_supported=False,reward_supported=False,formal_unit_complete=False);v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(old_Source_checked=len(actual),modified=4,new=3,next='actual UBT compile then3cleanUE RED'),ensure_ascii=False))
