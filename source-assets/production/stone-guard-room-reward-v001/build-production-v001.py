from pathlib import Path
import difflib,hashlib,json
ROOT=Path('F:/Ourgame');OUT=ROOT/'source-assets/production/stone-guard-room-reward-v001';PROD=OUT/'production-source';PROD.mkdir(exist_ok=True)
assert not any(PROD.iterdir()), "Refuse overwrite of produced candidates"
def base(n):return (OUT/'baseline-source'/n).read_bytes().decode()
def edit(s,a,b):
 if "\r\n" not in s:a=a.replace("\r\n","\n");b=b.replace("\r\n","\n")
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
files={}
# Declarations/API are the candidate Stage0 text generated from exact baseline,
# never the concurrently admitted actual Source. Frozen assertions are unchanged.
h=(OUT/'stage0-source/DungeonGameMode.h').read_bytes().decode()
h=edit(h,'    bool QueryFirstBatchGuardRoom(FDungeonFirstBatchGuardRoomView& Out) const;\r\n',
 '    bool QueryFirstBatchGuardRoom(FDungeonFirstBatchGuardRoomView& Out) const;\r\n'
 '    UFUNCTION(BlueprintCallable, Category="Dungeon") void StartFirstBatchGuardRoom();\r\n')
h=edit(h,'private:\r\n','private:\r\n    bool bFirstBatchGuardRoomRequested=false;\r\n'
 '    void AdvanceFirstBatchGuardRoom();\r\n    void SettleFirstBatchGuardDeath(ADungeonFighter* Fighter);\r\n'
 '    bool GuardRoomAnchorLegal(FVector2D Position,FVector2D Half,double MinimumDistance) const;\r\n'
 '    bool GuardRoomMayStartAttack(uint64 Entity,double At) const;\r\n')
files['DungeonGameMode.h']=h

rh=(OUT/'stage0-source/DungeonRunRewards.h').read_bytes().decode();nl='\r\n' if '\r\n' in rh else '\n'
rh=edit(rh,'    bool Begin(FGuid RunGuid,uint64 OwnerId,uint64 RoomInstanceId,int32 InitialCoins,FString& Diagnostic);'+nl,
 '    bool Begin(FGuid RunGuid,uint64 OwnerId,uint64 RoomInstanceId,int32 InitialCoins,FString& Diagnostic);'+nl+
 '    bool BeginFirstBatchGuardPlan(uint64 Seed,uint64 InitialEntity,double AtTime,FString& Diagnostic);'+nl+
 '    bool CommitFirstBatchGuardPlan(const FDungeonFirstBatchGuardRoomView& Plan,FString& Diagnostic);'+nl)
files['DungeonRunRewards.h']=rh
rc=base('DungeonRunRewards.cpp');nl='\r\n' if '\r\n' in rc else '\n'
rc=edit(rc,'#include "DungeonRunRewards.h"'+nl,'#include "DungeonRunRewards.h"'+nl+'#include "DungeonGuardRoomRewardsV2.h"'+nl)
rc=edit(rc,'bool Validate(const FS& S,const FDungeonRunRewardValidationContext* C,FString& Why)'+nl+'{',
 'bool Validate(const FS& S,const FDungeonRunRewardValidationContext* C,FString& Why)'+nl+'{'+nl+
 '    if(S.Schema==2)return DungeonGuardRoomRewardsV2::Validate(S,C,Why);'+nl+
 '    if(!S.RoomPlans.IsEmpty())return Fail(Why,TEXT("Legacy reward schema1 cannot carry a Bridge plan"));')
rc=edit(rc,'    FDungeonRunRewardDeathResult R;R.Status=EDungeonRunRewardStatus::InvalidRequest;'+nl,
 '    if(State.Schema==2)return DungeonGuardRoomRewardsV2::ResolveDeath(State,Q,Diagnostic);'+nl+'    FDungeonRunRewardDeathResult R;R.Status=EDungeonRunRewardStatus::InvalidRequest;'+nl)
rc=edit(rc,'    FS Candidate=State;Candidate.RoomExits.Add(Q);Candidate.CurrentRoomInstanceId=Q.NextRoomInstanceId;'+nl,
 '    FS Candidate=State;Candidate.RoomExits.Add(Q);Candidate.CurrentRoomInstanceId=Q.NextRoomInstanceId;'+nl+
 '    if(Candidate.Schema==2)Candidate.RoomPlans.Add(DungeonGuardRoomRewardsV2::Plan(Candidate.RunGuid,Q.NextRoomInstanceId,Candidate.RoomPlans[0].Seed,Q.AtTime));'+nl)
rc+='''
bool FDungeonRunRewards::BeginFirstBatchGuardPlan(uint64 Seed,uint64 InitialEntity,double AtTime,FString& Why)
{
 if(State.Schema!=1||!State.Bound||State.CurrentRoomInstanceId!=1||!State.Deaths.IsEmpty()||!State.RoomPlans.IsEmpty()||!InitialEntity)return false;
 auto C=State;C.Schema=2;auto P=DungeonGuardRoomRewardsV2::Plan(C.RunGuid,1,Seed,AtTime);
 P.Slots[0].Stage=EDungeonGuardRoomSlotStage::Materialized;P.Slots[0].EntityId=InitialEntity;P.Slots[0].MaterializedAt=AtTime;C.RoomPlans.Add(P);
 if(!Validate(C,nullptr,Why))return false;State=MoveTemp(C);return true;
}
bool FDungeonRunRewards::CommitFirstBatchGuardPlan(const FDungeonFirstBatchGuardRoomView& P,FString& Why)
{
 if(State.Schema!=2||State.RoomPlans.IsEmpty()||P.RoomInstanceId!=State.CurrentRoomInstanceId)return false;
 auto C=State;C.RoomPlans.Last()=P;if(!Validate(C,nullptr,Why))return false;State=MoveTemp(C);return true;
}
'''
files['DungeonRunRewards.cpp']=rc

gm=base('DungeonGameMode.cpp');gm=edit(gm,'#include "DungeonRunRewards.h"\r\n','#include "DungeonRunRewards.h"\r\n#include "DungeonGuardRoomRewardsV2.h"\r\n') if '#include "DungeonRunRewards.h"\r\n' in gm else edit(gm,'#include "DungeonRunAggregate.h"\r\n','#include "DungeonRunAggregate.h"\r\n#include "DungeonGuardRoomRewardsV2.h"\r\n')
gm=edit(gm,'    Super::InitGame(MapName,Options,ErrorMessage);\r\n','    Super::InitGame(MapName,Options,ErrorMessage);\r\n    bFirstBatchGuardRoomRequested=UGameplayStatics::HasOption(Options,TEXT("DungeonFirstBatchGuardRoom"));\r\n')
gm=edit(gm,'    RestartRun();\r\n    bWaitingForStart = FParse::Param',
 '    if(bFirstBatchGuardRoomRequested){RestartRun();return;}\r\n    RestartRun();\r\n    bWaitingForStart = FParse::Param')
gm=edit(gm,'    if(SceneObjects->Current().Active||FParse::Param(FCommandLine::Get(),TEXT("DungeonSceneExplorationPreview")))\r\n',
 '    if(bFirstBatchGuardRoomRequested||(RunRewards&&RunRewards->Capture().Schema==2))\r\n'
 '    {if(Controller){Controller->Possess(PlayerFighter);Controller->SetInputMode(FInputModeGameOnly());Controller->bShowMouseCursor=false;AddTickPrerequisiteActor(Controller);}\r\n'
 '     BeginFirstBatchGuardRoom(EquipmentRuntime->View.Bound?EquipmentRuntime->View.CombatSeed:71);return;}\r\n'
 '    if(SceneObjects->Current().Active||FParse::Param(FCommandLine::Get(),TEXT("DungeonSceneExplorationPreview")))\r\n')
gm=edit(gm,'    SceneEncounterEntityId=Entity;bRoomCleared=false;return true;\r\n',
 '    SceneEncounterEntityId=Entity;bRoomCleared=false;\r\n'
 '    if(RunRewards&&RunRewards->Capture().Schema==2)\r\n'
 '    {auto P=RunRewards->Capture().RoomPlans.Last();P.Slots[0].EntityId=Entity;P.Slots[0].Stage=EDungeonGuardRoomSlotStage::Materialized;P.Slots[0].MaterializedAt=SimulationTime;\r\n'
 '     FString Why;if(!RunRewards->CommitFirstBatchGuardPlan(P,Why)){LastMessage=Why;return false;}}\r\n'
 '    return true;\r\n')
gm=edit(gm,'    Frame.bCanStartAttack = !bGameOver && !bWaitingForStart && Knight->bAIEnabled;\r\n',
 '    Frame.bCanStartAttack = !bGameOver && !bWaitingForStart && Knight->bAIEnabled\r\n'
 '        &&GuardRoomMayStartAttack(FindWorldEntityId(Knight),FromTime);\r\n')
gm=edit(gm,'        bSimulationBatch=false;\r\n        // Every old/bat/new-player damage and death at this point has drained.\r\n',
 '        bSimulationBatch=false;\r\n        AdvanceFirstBatchGuardRoom(); // Full same-timestamp deaths precede settlement/admission.\r\n'
 '        // Every old/bat/new-player damage and death at this point has drained.\r\n')
gm=edit(gm,'    if(Fighter->StoneGuard)\r\n    {\r\n        if(!Fighter->bGuardDeathObserved)',
 '    if(Fighter->bEnemy&&RunRewards&&RunRewards->Capture().Schema==2){SettleFirstBatchGuardDeath(Fighter);return;}\r\n'
 '    if(Fighter->StoneGuard)\r\n    {\r\n        if(!Fighter->bGuardDeathObserved)')
gm+='\n#include "DungeonFirstBatchGuardRoomRuntime.inl"\n';files['DungeonGameMode.cpp']=gm

fh=base('DungeonFighterSnapshot.h');fh=edit(fh,'// Call-scoped read-only views of the approved saved aggregate.',
 'struct FDungeonRunRewardSnapshot;\r\n\r\n// Call-scoped read-only views of the approved saved aggregate.')
fh=edit(fh,'    const FDungeonWeaponWorldState* WeaponWorld=nullptr;\r\n','    const FDungeonWeaponWorldState* WeaponWorld=nullptr;\r\n    const FDungeonRunRewardSnapshot* Rewards=nullptr; // Explicit formal Guard settlement owner, never a saved pointer.\r\n')
files['DungeonFighterSnapshot.h']=fh
fc=base('DungeonFighter.cpp');nl='\n' if '\r\n' not in fc else '\r\n'
fc=edit(fc,'#include "DungeonFighter.h"'+nl,'#include "DungeonFighter.h"'+nl+'#include "DungeonGuardRoomRewardsV2.h"'+nl)
fc=edit(fc,'            if(Saved.Schema!=1||!Pure.Restore(G)',
 '            const bool Settled=Saved.Schema==2;FString RewardWhy;\n'
 '            if(Settled&&(!C.Rewards||C.Rewards->Schema!=2||C.Rewards->RunGuid!=C.RunGuid\n'
 '                ||!DungeonGuardRoomRewardsV2::Validate(*C.Rewards,nullptr,RewardWhy)\n'
 '                ||!C.Rewards->Deaths.ContainsByPredicate([&](const auto& D){return D.Death.EntityId==S.EntityId&&D.Death.RoomInstanceId==S.RoomInstanceId&&D.Death.ContentId==S.EnemyContentId;})))\n'
 '                return Reject(TEXT("Formal Guard settlement has no explicit valid schema2 room reward owner"));\n'
 '            if((Saved.Schema!=1&&Saved.Schema!=2)||!Pure.Restore(G)')
fc=edit(fc,'||S.Dead!=(G.Phase==DungeonStoneGuard::EPhase::Dead)||S.DeathReported||Saved.DeathObserved!=S.Dead',
 '||S.Dead!=(G.Phase==DungeonStoneGuard::EPhase::Dead)||S.DeathReported!=Settled||Settled&&!G.RewardClaimed||Saved.DeathObserved!=S.Dead')
fc=edit(fc,'    FDungeonEquipmentRuntimeSnapshot Equipment;FOwnerContext Local;const FOwnerContext* Context=ExplicitStaging;',
 '    FDungeonEquipmentRuntimeSnapshot Equipment;FDungeonRunRewardSnapshot RewardOwner;FOwnerContext Local;const FOwnerContext* Context=ExplicitStaging;')
fc=edit(fc,'        Equipment=Game->EquipmentRuntime->Capture();Local.Equipment=&Equipment;Local.WeaponWorld=&Game->WeaponWorld;',
 '        Equipment=Game->EquipmentRuntime->Capture();RewardOwner=Game->CaptureRunRewardsSnapshot();Local.Rewards=&RewardOwner;Local.Equipment=&Equipment;Local.WeaponWorld=&Game->WeaponWorld;')
fc=edit(fc,'S.Guard=FDungeonStoneGuardOwnerSnapshot{1,StoneGuard->CapturePolicy(),StoneGuard->Capture(),bGuardDeathObserved};',
 'S.Guard=FDungeonStoneGuardOwnerSnapshot{bDeathReported?2u:1u,StoneGuard->CapturePolicy(),StoneGuard->Capture(),bGuardDeathObserved};')
files['DungeonFighter.cpp']=fc

ag=base('DungeonRunAggregate.cpp')
ag=edit(ag,'    if(Candidate.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();}))\r\n',
 '    if(Candidate.Rewards.Schema==2||Candidate.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();}))\r\n')
ag=edit(ag,'    const bool HasGuard=S.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();});\r\n',
 '    const bool HasGuard=S.Rewards.Schema==2||S.Fighters.ContainsByPredicate([](const auto& F){return F.Guard.IsSet();});\r\n')
ag=edit(ag,'FC.SimulationTime=S.SimulationTime;FC.GameOver=S.GameOver;FC.Equipment=&S.Equipment;FC.WeaponWorld=&World;',
 'FC.SimulationTime=S.SimulationTime;FC.GameOver=S.GameOver;FC.Equipment=&S.Equipment;FC.WeaponWorld=&World;FC.Rewards=&S.Rewards;')
ag=edit(ag,'    const auto& Room=S.Scene.CurrentRoom;const auto& Interaction=S.Scene.Interaction;\r\n',
 '    const auto& Room=S.Scene.CurrentRoom;const auto& Interaction=S.Scene.Interaction;\r\n'
 '    if(S.Rewards.Schema==2&&(!Room.Active||V.Config!=EDungeonEquipmentRunConfig::FirstBatch\r\n'
 '        ||S.Rewards.RoomPlans.ContainsByPredicate([&](const auto& P){return P.Seed!=V.CombatSeed;})))\r\n'
 '        return Fail(Diagnostic,TEXT("Formal Bridge plan requires actual FirstBatch Scene and same immutable seed"));\r\n')
files['DungeonRunAggregate.cpp']=ag
ins=base('DungeonRunInstaller.cpp');ins=edit(ins,'C.SimulationTime=S.SimulationTime;C.GameOver=S.GameOver;C.Equipment=&Equipment;C.WeaponWorld=&World;return C;',
 'C.SimulationTime=S.SimulationTime;C.GameOver=S.GameOver;C.Equipment=&Equipment;C.WeaponWorld=&World;C.Rewards=&S.Rewards;return C;')
files['DungeonRunInstaller.cpp']=ins
codec=base('DungeonRunSnapshotCodec.cpp')
codec=edit(codec,'ENUM_DOMAIN(EDungeonRunScope,BoundDevelopmentV2)','ENUM_DOMAIN(EDungeonRunScope,BoundDevelopmentV2)\r\nENUM_DOMAIN(EDungeonGuardRoomSlotStage,Dead)')
marker='void Fields(FObject& O,FDungeonRunRewardSnapshot& S)\r\n'
new='''void Fields(FObject& O,FDungeonGuardRoomSlot& S)
{
 O.Field(TEXT("SlotId"),S.SlotId);O.Field(TEXT("ContentId"),S.ContentId);O.Field(TEXT("Group"),S.Group);O.Field(TEXT("Weight"),S.Weight);O.Field(TEXT("Coins"),S.Coins);
 O.Field(TEXT("EntityId"),S.EntityId);O.Field(TEXT("CoinObjectId"),S.CoinObjectId);O.Field(TEXT("Stage"),S.Stage);O.Field(TEXT("SpawnPosition"),S.SpawnPosition);
 O.Field(TEXT("WarningAt"),S.WarningAt);O.Field(TEXT("MaterializedAt"),S.MaterializedAt);O.Field(TEXT("DeadAt"),S.DeadAt);O.Field(TEXT("RetryAt"),S.RetryAt);O.Field(TEXT("AnchorAttempt"),S.AnchorAttempt);
}
void Fields(FObject& O,FDungeonFirstBatchGuardRoomView& S)
{
 O.Field(TEXT("Version"),S.Version);O.Field(TEXT("RunGuid"),S.RunGuid);O.Field(TEXT("RoomInstanceId"),S.RoomInstanceId);O.Field(TEXT("Seed"),S.Seed);
 O.Field(TEXT("TemplateId"),S.TemplateId);O.Field(TEXT("GoldSourceId"),S.GoldSourceId);O.Field(TEXT("GoldBudget"),S.GoldBudget);
 O.Field(TEXT("EnteredAt"),S.EnteredAt);O.Field(TEXT("OrientationUntil"),S.OrientationUntil);O.Field(TEXT("ClearAt"),S.ClearAt);O.Field(TEXT("Slots"),S.Slots);
}
'''
codec=edit(codec,marker,new+marker)
codec=edit(codec,'    O.Field(TEXT("Collections"),S.Collections);O.Field(TEXT("RetiredEntities"),S.RetiredEntities);O.Field(TEXT("RoomExits"),S.RoomExits);\r\n',
 '    O.Field(TEXT("Collections"),S.Collections);O.Field(TEXT("RetiredEntities"),S.RetiredEntities);O.Field(TEXT("RoomExits"),S.RoomExits);\r\n'
 '    if(S.Schema==2){if(O.CodecVersion()!=2)O.Reject(TEXT("Bridge Rewards schema2 requires bound-run-v2"));else O.Field(TEXT("RoomPlans"),S.RoomPlans);}\r\n'
 '    else if(!S.RoomPlans.IsEmpty())O.Reject(TEXT("Legacy reward schema1 cannot carry Bridge fields"));\r\n')
files['DungeonRunSnapshotCodec.cpp']=codec

patch=''
for name,s in files.items():
 (PROD/name).write_bytes(s.encode());patch+=''.join(difflib.unified_diff(base(name).splitlines(True),s.splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+name,tofile='b/UnrealGame/Source/CodexDungeon/'+name))
for p in (OUT/'new-source').glob('*'):(PROD/p.name).write_bytes(p.read_bytes())
(OUT/'production-from-before-v001.patch').write_bytes(patch.encode())
print(json.dumps({'production_changed_existing':list(files),'new_source_files':[p.name for p in (OUT/'new-source').glob('*')],'tests_unchanged':hashlib.sha256((OUT/'new-tests/DungeonFirstBatchGuardRoomTests.cpp').read_bytes()).hexdigest()},indent=2))
