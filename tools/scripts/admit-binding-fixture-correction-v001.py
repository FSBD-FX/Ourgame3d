from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-sword-equipment-binding-v001';D=B/'fixture-correction-v001';P=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleSwordEquipmentBindingTests.cpp'
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
f=D/'fixture-correction-freeze-v001.json';assert desc(f)['sha256']=='f68389ddf7d38b6d952ff095c003dfec862437c2c75937492568de7147e2f981'
for pin in json.loads(f.read_text(encoding='utf-8'))['files']:
    q=D/pin['path'];a=desc(q);assert a['bytes']==pin['bytes'] and a['sha256']==pin['sha256']
assert desc(P)['sha256']=='00ee8da24589d6ba121d85136290711eb59914167ed473a93dec93aea68e5cfa'
C=D/'candidate-source/Tests/DungeonFairytaleSwordEquipmentBindingTests.cpp';assert desc(C)['sha256']=='174593b8f156cf0e78c7b031c375d5a7234875cf2a6b92ba020cb78f61fa8877'
old=P.read_text(encoding='utf-8');new=old.replace('StartActualPickup(W,M.SourceId)','StartActualPickup(W,M.SourceId,2)').replace('StartActualPickup(W,ActualGroundSource(W,A.InstanceId))','StartActualPickup(W,ActualGroundSource(W,A.InstanceId),2)')
assert new==C.read_text(encoding='utf-8')
O=B/'root-fixture-admission-v001';assert not O.exists();O.mkdir();shutil.copy2(P,O/'before-test.cpp')
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-190734/index.json';result=json.loads(report.read_text(encoding='utf-8-sig'))
assert result['failed']==3 and result['succeeded']==0
record={'actual_before_report':desc(report),'actual_stage0_build':desc(R/'UnrealGame/Saved/Bootstrap/build-editor-20261016-190617.log'),'DLL_before_fixture_rebuild':desc(R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'),'classification':'Actual3Fail has9 honest-stub positives plus1 missing public armor-slot confirmation fixture error; not clean fullStage0 RED. Original report retained. Only2 calls add Slot2, no relaxed assertions.','before':desc(P),'candidate':desc(C),'freeze':desc(f),'formal_complete_units':0}
shutil.copy2(C,P);assert C.read_bytes()==P.read_bytes();record['admitted']=desc(P)
(O/'admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'admitted':desc(P),'test_fixture_only':True},ensure_ascii=False))
