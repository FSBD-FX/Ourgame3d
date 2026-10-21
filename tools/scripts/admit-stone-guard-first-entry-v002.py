from pathlib import Path
import datetime,hashlib,json,os,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/stone-guard-kernel-v001/movement-split-v002'
O=R/'docs/production/first-batch-v2/evidence/stone-guard-kernel-v001/root-first-entry-RED-and-production-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=B/'final-freeze-v002.json'
assert desc(freeze)['sha256']=='bdf792dfbc13a6c14eb5a754a3d6ffe449485a03a275613e505b0bfe636cdb4c'
cpp=R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuard.cpp';candidate=B/'candidate-source/DungeonStoneGuard.cpp'
assert desc(cpp)['sha256']=='4de8ffab4f8b8a6ac4400c268199b84adf630bdaf1943803c548ff05851dd061'
assert desc(candidate)['sha256']=='0387697ec2618f473623e83c9974a9248e7b7f4ffe82a4d7df9cad26e00ed4f7'
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-231203/index.json';v=read(report)
assert v['succeeded']==3 and v['failed']==1 and len(v['tests'])==4
assert all(v.get(k,0)==0 for k in ['succeededWithWarnings','notRun','inProcess'])
red=[t for t in v['tests'] if t['state']=='Fail'];assert len(red)==1 and red[0]['fullTestPath'].endswith('.MovementFirstEntryPartitionAndZeroReceipts') and red[0]['errors']==24 and red[0]['warnings']==0
assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in v['tests'] if t!=red[0])
assert len(red[0]['entries'])==24 and all(e['event']['type']=='Error' and 'Expected ' in e['event']['message'] for e in red[0]['entries'])
build=R/'UnrealGame/Saved/Bootstrap/build-editor-20261016-231123.log';last=read(R/'UnrealGame/Saved/Bootstrap/last-build.json')
assert last['ExitCode']==0 and Path(last['Log']).resolve()==build.resolve()
assert 'Compile [x64] DungeonStoneGuard.cpp' in build.read_text(encoding='utf-8-sig')
paths=[cpp,cpp.with_suffix('.h'),cpp.parent/'Tests/DungeonStoneGuardKernelTests.cpp',cpp.parent/'Tests/StoneGuardKernelTestOracle.h',cpp.parent/'Tests/DungeonStoneGuardMovementTests.cpp',cpp.parent/'Tests/StoneGuardMovementCases.h',R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',report,build,freeze]
assert not O.exists();O.mkdir(parents=True);pins=[]
for p in paths:
 q=O/'compiled-movement-RED-overlay'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();pins.append(desc(p))
before={p:desc(p) for p in (R/'UnrealGame/Source').rglob('*') if p.is_file() and p!=cpp}
shutil.copy2(candidate,cpp);os.utime(cpp,None);assert cpp.read_bytes()==candidate.read_bytes()
assert all(desc(p)==d for p,d in before.items())
(O/'admission.json').write_text(json.dumps(dict(actual_RED=dict(report=desc(report),success=3,failed=1,errors=24,warnings=0),compiled_RED_files=pins,base_unchanged_source_snapshot='v121',production_cpp=desc(cpp),source_mtime_touched=True,all_other_Source_unchanged=True,actual_GREEN=None,native_driver=None,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';v=read(p);v['ue_current_working_source_compiled']=False;v['ue_current_working_source_verified']=False;v['current_source_uncompiled_changes']='StoneGuard exact first-axis attack-shape entry v002 CPP; real prior3GREEN/newMovement1RED preserved, fixed candidate not yet compiled.';v['stone_guard_kernel_v001'].update(dict(actual_UE_original_3_GREEN=desc(report),actual_UE_movement_RED=desc(report),production_v002=desc(cpp),actual_UE_GREEN=None,actual_native_driver=None,formal_unit_complete=False));v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(preserved_actual_RED=True,source_changed=1,other_source_unchanged=True,next='actual UBT compile and full148'),ensure_ascii=False))
