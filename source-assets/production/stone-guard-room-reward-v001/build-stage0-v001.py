from pathlib import Path
import difflib,hashlib,json
ROOT=Path('F:/Ourgame');OUT=ROOT/'source-assets/production/stone-guard-room-reward-v001'
STAGE=OUT/'stage0-source';STAGE.mkdir(exist_ok=False)
def load(n):return (OUT/'baseline-source'/n).read_bytes().decode()
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
files={}
h=load('DungeonGameMode.h')
h=change(h,'    bool BeginSceneExplorationPreview(); // Explicit development layout, not a formal D07/D08/D13 entry.\r\n',
 '    bool BeginSceneExplorationPreview(); // Explicit development layout, not a formal D07/D08/D13 entry.\r\n'
 '    bool BeginFirstBatchGuardRoom(uint64 Seed=71); // Explicit native finite Bridge game entry; no QA flag required.\r\n'
 '    bool QueryFirstBatchGuardRoom(FDungeonFirstBatchGuardRoomView& Out) const;\r\n')
files['DungeonGameMode.h']=h
r=load('DungeonRunRewards.h');NL='\r\n' if '\r\n' in r else '\n'
r=change(r,'#include "DungeonWorldProjectiles.h"'+NL,'#include "DungeonWorldProjectiles.h"'+NL+'#include "DungeonFirstBatchGuardRoom.h"'+NL)
r=change(r,'    TArray<FDungeonRunRewardRoomExit> RoomExits;'+NL,'    TArray<FDungeonRunRewardRoomExit> RoomExits;'+NL+'    TArray<FDungeonFirstBatchGuardRoomView> RoomPlans; // Schema2 only; legacy schema1 stays empty. '+NL)
files['DungeonRunRewards.h']=r
c=load('DungeonGameMode.cpp')
c+='''
// Stage0: genuine existing FirstBatch/Scene setup, intentionally no Bridge plan
// or future-wave/reward implementation. Native positive witnesses must fail.
bool ADungeonGameMode::BeginFirstBatchGuardRoom(uint64 Seed)
{
    if(IsRunInstallGated()||!IsValid(PlayerFighter)||!GetWorld())return false;
    const auto Layout=DungeonRoomLayout::ExplorationPreview();
    PlayerFighter->SetActorLocation(FVector(Layout.Entry.X,Layout.Entry.Y,0.));
    if(!BeginEquipmentRun(EDungeonEquipmentRunConfig::FirstBatch,Seed))return false;
    PlayerFighter->SetActorTickEnabled(false);
    if(!SceneObjects->BeginRoom(EquipmentRuntime->View.RunGuid,EquipmentRuntime->View.RoomInstanceId)
        ||!SpawnSceneExplorationRoom())return false;
    bWaitingForStart=true;return true;
}
bool ADungeonGameMode::QueryFirstBatchGuardRoom(FDungeonFirstBatchGuardRoomView&) const
{return false;}
'''
files['DungeonGameMode.cpp']=c
patch=''
for name,s in files.items():
 before=load(name);(STAGE/name).write_bytes(s.encode());patch+=''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name))
(STAGE/'DungeonFirstBatchGuardRoom.h').write_bytes((OUT/'new-source/DungeonFirstBatchGuardRoom.h').read_bytes())
(OUT/'stage0-existing-source.patch').write_bytes(patch.encode())
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
freeze={'schema':'stone-guard-room-reward-stage0-v001','exact_before':pin(OUT/'exact-before-pins-v001.json'),
 'files':[pin(p) for p in sorted(STAGE.glob('*'))]+[pin(OUT/'new-tests/DungeonFirstBatchGuardRoomTests.cpp'),pin(OUT/'stage0-existing-source.patch')],
 'test_groups':['CodexDungeon.Content.FirstBatchGuardRoom.SeededFullManifestAndPreallocation','CodexDungeon.Content.FirstBatchGuardRoom.FutureWavesDeathCoinPickupAndClearOnce','CodexDungeon.Content.FirstBatchGuardRoom.RootV2PendingPlanAndSettlementContinuity'],
 'expected_first_semantic_RED':['Expected committed complete native Bridge slot plan after real FirstBatch room entry',
 'Expected future required slots prevent room-clear after initial true death','Expected RootV2 and explicit Rewards schema2 for complete pending Guard-room plan'],
 'legal_precondition':'Real new FirstBatch bound Run20 initial wallet with existing Scene geometry/nativeKnight/normal freshEnter. No SpawnStoneGuard/QAflag/forcedstate used.',
 'damage_scope':'Existing actual ApplyCombatHit adapter used for deterministic real native death; not a normalJ hit-geometry proof.',
 'tests_remain_identical_for_production':True,'UE_UBT_native_run':False,'actualSource_modified':False,'status':'ROOT_MUST_COMPILE_AND_VERIFY_REAL_THREE_RED'}
(OUT/'stage0-freeze-v001.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(freeze,ensure_ascii=False,indent=2))
