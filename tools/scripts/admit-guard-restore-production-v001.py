from pathlib import Path
import hashlib,json,shutil,os,datetime
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/stone-guard-restore-v001';F=B/'production-freeze-v001.json';O=D/'evidence/stone-guard-restore-v001/root-production-admission-v001'
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not O.exists();assert pin(F)['sha256']=='e5b13edc9fd19d3eedf620301c55d8661d6b30e4348b7861e5c15c6482e4afbb'
for r in read(F)['files']:
 d=pin(Path(r['path']));assert (d['bytes'],d['sha256'])==(r['bytes'],r['sha256'])
red=D/'evidence/stone-guard-restore-v001/root-actual-threeRED-v001/manifest.json';assert red.is_file()
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-013106/index.json';v=read(report)
assert v['failed']==3 and v['succeeded']==0 and len(v['tests'])==3
assert all(t['state']=='Fail' and t['errors']==1 and t['warnings']==0 for t in v['tests'])
assert all(v.get(k,0)==0 for k in ['succeededWithWarnings','notRun','inProcess'])
for name in ['StoneGuardRestoreCases.h','DungeonStoneGuardRestoreTests.cpp']:
 p=R/'UnrealGame/Source/CodexDungeon/Tests'/name;c=B/'shared-tests'/name
 if not c.exists():
  candidates=[Path(x['path']) for x in read(F)['files'] if Path(x['path']).name==name and 'test' in x['path'].lower()];assert candidates;c=candidates[0]
 assert p.read_bytes()==c.read_bytes(),name
for name in ['DungeonStoneGuard.h','DungeonStoneGuard.cpp']:
 p=R/'UnrealGame/Source/CodexDungeon'/name;c=B/'stage0-source'/name
 assert p.read_bytes().replace(b'\r\n',b'\n')==c.read_bytes().replace(b'\r\n',b'\n'),name
before={p:pin(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}
O.mkdir(parents=True)
for p in [R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.h',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',D/'progress.json']:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
admitted=[]
for name in ['DungeonStoneGuard.h','DungeonStoneGuard.cpp']:
 p=R/'UnrealGame/Source/CodexDungeon'/name;c=B/'candidate-source'/name;shutil.copy2(c,p);os.utime(p,None);assert p.read_bytes()==c.read_bytes();admitted.append(pin(p))
expected={R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.h',R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp'}
assert {p for p,d in before.items() if pin(p)!=d}==expected
write(O/'admission.json',dict(freeze=pin(F),actual_RED_report=pin(report),compiled_RED_preservation=pin(red),admitted=admitted,all_other_Source_unchanged=True,frozen_tests_byte_identical=True,source_mtime_refreshed=True,compiled=False,target_three_GREEN=None,full157=None,native_owner_persistence=False,formal_complete_units=0))
p=D/'progress.json';x=read(p);x.update(ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_source_uncompiled_changes='Guard Restore production h/cpp admitted over preserved actual3RED; frozen tests unchanged. Actual compile/3GREEN/full157 pending.',actual_registered_test_count_current=157,updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());x['stone_guard_restore_v001'].update(production_admission=pin(O/'admission.json'),production_applied=True,actual_UE_GREEN=None,native_owner_persistence=False);write(p,x)
print(json.dumps(dict(production_guard_two_Source_admitted=True,frozen_tests_unchanged=True,actual_build_pending=True),ensure_ascii=False))
