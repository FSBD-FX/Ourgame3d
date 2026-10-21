from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');E=R/'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001'
A=R/'过程图稿与视频/2026-10-16_局内存档原生两进程继续实证_v001';assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
files=list(p for p in E.rglob('*') if p.is_file())
for topic in ['20261016-163146-native-two-process-v001','20261016-163507-native-two-process-v002']:
    files.extend(p for p in (R/'UnrealGame/Saved/RunPristineProofs'/topic).rglob('*') if p.is_file())
for run in ['150911','151902','154411','160830','161619','161755','161855','162940']:
    files.append(R/f'UnrealGame/Saved/Automation/FirstRoom-20261016-{run}/index.json')
for run in ['154143','160747','161509','162546','162803','162916']:
    files.append(R/f'UnrealGame/Saved/Bootstrap/build-editor-20261016-{run}.log')
files.extend([R/'docs/production/first-batch-v2/run-pristine-two-process-runtime-proof-v001.md',R/'docs/production/first-batch-v2/runtime-review-sword-primary2-fit-v002.md',
    R/'tools/scripts/verify-run-pristine-two-process-v001.py',R/'tools/scripts/verify-run-pristine-two-process-v001.ps1',
    R/'tools/scripts/verify-run-pristine-two-process-v002.py',R/'tools/scripts/verify-run-pristine-two-process-v002.ps1',
    R/'tools/scripts/audit-run-two-process-v113.py',Path(__file__)])
for name in ['DungeonGameMode.h','DungeonGameMode.cpp','DungeonRunAggregate.cpp','DungeonRunInstaller.h','DungeonRunInstaller.cpp',
    'DungeonNativeGeometryGuards.h','DungeonNativeGeometryGuards.cpp','DungeonRunContinueProbe.h','DungeonRunContinueProbe.cpp','DungeonHUD.cpp',
    'DungeonRunSnapshotCodec.cpp','DungeonRunSaveAdapter.cpp','DungeonSaveGenerationStore.cpp',
    'Tests/DungeonNativeGeometryGuardsTests.cpp','Tests/DungeonRunPristineBootstrapTests.cpp']:
    files.append(R/'UnrealGame/Source/CodexDungeon'/name)
files.append(R/'source-assets/production/backups/2026-10-16_RunTwoProcessProbe-admitted-full138GREEN-v113/compiled-source-manifest.json')
for version in ['v002','v003']:
    files.extend(p for p in (R/f'source-assets/production/fairytale-sword-primary2-v001/primary2-measurement-{version}').rglob('*') if p.is_file())
entries=[]
for i,p in enumerate(dict.fromkeys(files)):
    before=desc(p);q=A/'原件'/f'{i:04d}-{p.name}';shutil.copy2(p,q)
    assert desc(p)==before and all(desc(q)[k]==before[k] for k in ['bytes','sha256'])
    entries.append({'source':before,'retained':desc(q)})
proof=R/'docs/production/first-batch-v2/run-pristine-two-process-runtime-proof-v001.md';q=A/'展示副本/run-pristine-proof.md';shutil.copy2(proof,q);assert proof.read_bytes()==q.read_bytes()
(A/'index.json').write_text(json.dumps({'files':entries,'status':'Actual full138 and two native sequential process Run-only proof passed; failed compile/verifier predecessors preserved',
    'source_snapshot':'v113','scope':'BoundDevelopmentRunV1 only','full_D13':False,'audio_device_auditioned':False,'new_video_proof':False,
    'native171_armor_or_motion_accepted':False,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('真实两个UE进程局内存档证明、实际磁盘原件、源码及构建/自动化/独立核验原报告；同时保留失败编译与首轮核验器错误。没有新视频、设备试听或完整D13/装备验收。源/版本/状态详见index；旧失败不覆盖。\n',encoding='utf-8')
print(json.dumps({'archive':A.as_posix(),'original_copies':len(entries),'bytes':sum(x['source']['bytes'] for x in entries)},ensure_ascii=False))
