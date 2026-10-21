from pathlib import Path
import hashlib,json,shutil,subprocess,os,datetime
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-restore-v001';D=R/'docs/production/first-batch-v2';F=D/'evidence/stone-guard-restore-v001/stage0-admission-freeze-v001.json';O=D/'evidence/stone-guard-restore-v001/root-stage0-admission-v001';assert not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
v=read(F)
for row in v['files']:
 d=desc(Path(row['path']));assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
snap=R/'source-assets/production/backups/2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124'
for row in read(snap/'compiled-source-manifest.json')['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Config/','UnrealGame/Content/Production/')):
  d=desc(R/row['path']);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
patch=B/'patches/stage0-api-v001.patch';subprocess.run(['git','apply','--check',str(patch)],cwd=R,check=True)
O.mkdir(parents=True);before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
for p in [R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.h',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',D/'progress.json']:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
subprocess.run(['git','apply',str(patch)],cwd=R,check=True)
for row in v['files']:
 if row.get('destination'):
  p=R/row['destination'];c=Path(row['path'])
  if '/Tests/' in row['destination']:
   assert not p.exists();shutil.copy2(c,p)
  assert p.read_bytes().replace(b'\r\n',b'\n')==c.read_bytes().replace(b'\r\n',b'\n');os.utime(p,None)
expected={R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.h',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp'}
assert {p for p,d in before.items() if desc(p)!=d}==expected
write=lambda p,x:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(O/'admission.json',dict(freeze=desc(F),previous_source=list(before.values()),stage0_destinations=[desc(R/r['destination']) for r in v['files'] if r.get('destination')],other_Source_unchanged=True,source_mtime_refreshed=True,compiled=False,actual_UE_RED=None,production_applied=False))
p=D/'progress.json';x=read(p);x.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Guard Restore Stage0 two API files plus two NEW UEtest/header admitted; actual compile/3RED pending.',actual_registered_test_count_current=157,previous_goal_turn_classification='progress',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());x['stone_guard_restore_v001']=dict(stage0_admission=desc(O/'admission.json'),actual_UE_RED=None,actual_UE_GREEN=None,native_owner_persistence=False,formal_complete_units=0);x['generation_accounting_current'].update(requested_count=190,window_requested=22,window_remaining=2,lifetime_requested_count=214);x['next_native_request']=191;write(p,x)
print(json.dumps(dict(stage0_API_and_new_tests_admitted=True,other_Source_unchanged=True,actual_RED_not_yet=True)))
