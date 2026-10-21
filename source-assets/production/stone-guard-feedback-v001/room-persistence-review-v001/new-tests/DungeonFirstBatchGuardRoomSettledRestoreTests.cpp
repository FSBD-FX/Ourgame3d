#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "RunCodecFixture_v001.h"
#include "../DungeonFirstBatchGuardRoom.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "../DungeonStoneGuard.h"
namespace
{
namespace RG=DungeonStoneGuard;
ADungeonFighter* ReviewEnemy(FCodecWorld& W,const TCHAR* Content)
{for(const auto E:W.Game->Enemies)if(IsValid(E)&&E->EnemyContentId==Content)return E.Get();return nullptr;}
bool ReviewBridge(FCodecWorld& W)
{
 if(!W.Create()||!W.Game->BeginFirstBatchGuardRoom(71))return false;
 for(const auto E:W.Game->Enemies)E->bAIEnabled=false; // Same accepted test-source AI control; no HP/identity/position write.
 return W.Pulse(EKeys::Enter)&&!W.Game->bWaitingForStart&&W.Player->Coins==20;
}
bool ReviewDeath(FCodecWorld& W,ADungeonFighter* Enemy)
{
 if(!Enemy)return false;Enemy->ApplyCombatHit(100000.f,W.Player,85.f);W.Frame(.005f);
 return W.Test.TestTrue(TEXT("Native resolved-damage death is actually formally settled before snapshot"),Enemy->bDead&&Enemy->bDeathReported);
}
bool ReviewBorn(FCodecWorld& W,const TCHAR* Content,double PredecessorDeath)
{
 // Observe actual completed ticks until birth, immediately apply the accepted AI source control.
 // The legacy fixture's AdvanceTo is limited to64*.05=3.2s; never ask it for a longer single segment.
 for(int32 I=0;I<180&&!ReviewEnemy(W,Content)&&!W.Game->bGameOver;++I)W.Frame(.025f);
 auto* E=ReviewEnemy(W,Content);if(!E)return W.Test.TestTrue(TEXT("Same required future slot genuinely materializes through native warning lifecycle"),false);
 E->bAIEnabled=false;
 FDungeonFirstBatchGuardRoomView P;if(!W.Game->QueryFirstBatchGuardRoom(P))return false;
 const auto* X=P.Slots.FindByPredicate([E](const auto& S){return S.EntityId==E->GetRuntimeEntityId();});
 return W.Test.TestTrue(TEXT("Actual birth retains predecessor breather and full1.2s warning; no forced deadline"),X&&X->MaterializedAt>=PredecessorDeath+3.2&&X->MaterializedAt>=X->WarningAt+1.2);
}
bool ReviewCapture(FCodecWorld& W,FDungeonRunSnapshot& S,TArray<uint8>& Bytes)
{
 FString Why;if(!W.Game->CaptureRunSnapshot(S,Why)||!DungeonRunSnapshotCodec::Encode(S,Bytes,Why))
 {W.Test.AddInfo(Why);return W.Test.TestTrue(TEXT("Actual settled/post-exit complete RootV2 captures and encodes"),false);}return true;
}
bool ReviewInstall(FCodecWorld& W,const TArray<uint8>& Bytes)
{
 FString Why;FDungeonValidatedRun V;FDungeonPreparedRun P;
 if(!W.Create()||!DungeonRunSnapshotCodec::Decode(Bytes,V,Why)||!FDungeonRunInstaller::Prepare(*W.Game,V,P,Why)||!FDungeonRunInstaller::Install(*W.Game,P,Why))
 {W.Test.AddInfo(Why);return W.Test.TestTrue(TEXT("Actual complete RootV2 decodes/prepares/installs without a new Run"),false);}
 W.Player=W.Game->PlayerFighter;FDungeonRunSnapshot Back;TArray<uint8> Again;
 if(!ReviewCapture(W,Back,Again)||!W.Test.TestTrue(TEXT("Immediate grouped install is whole Codec byte-identical, including rewards/owner2/future plans"),Again==Bytes))return false;
 W.Frame(.25f);if(!ReviewCapture(W,Back,Again)||!W.Test.TestTrue(TEXT("Technical install pause cannot collect/reroll/advance any saved obligation"),Again==Bytes))return false;
 W.Frame(.005f);return W.Pulse(EKeys::Enter)&&W.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFirstBatchGuardSettledPickupExitRestore,
 "CodexDungeon.Content.FirstBatchGuardRoom.SettledGuardPhysicalWalletAndCrossRoomRootV2",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFirstBatchGuardSettledPickupExitRestore::RunTest(const FString&)
{
 // Independent legacy wire oracle still proves actual V1 bytes, before any Bridge fixture.
 FCodecWorld Legacy(*this);FDungeonRunSnapshot L;FString Why;TArray<uint8> OldWire;
 if(!Legacy.Create()||!Legacy.Game->CaptureRunSnapshot(L,Why)||!DungeonRunSnapshotCodec::Encode(L,OldWire,Why))return false;
 if(!TestTrue(TEXT("Unchanged old Scene Root1/Rewards1 matches separate immutable named-field V1 wire oracle"),L.Schema==1&&L.Rewards.Schema==1&&L.Rewards.RoomPlans.IsEmpty()&&OldWire==FCodecOracle::Bytes(L)))return false;
 FCodecWorld W(*this);if(!ReviewBridge(W))return false;
 if(!ReviewDeath(W,ReviewEnemy(W,TEXT("ENM-STN-001"))))return false;
 auto R=W.Game->CaptureRunRewardsSnapshot();const double KD=R.Deaths.Last().Death.AtTime;
 if(!ReviewBorn(W,TEXT("ENM-STN-002"),KD)||!ReviewDeath(W,ReviewEnemy(W,TEXT("ENM-STN-002"))))return false;
 R=W.Game->CaptureRunRewardsSnapshot();const double BD=R.Deaths.Last().Death.AtTime;
 if(!ReviewBorn(W,TEXT("ENM-STN-003"),BD))return false;
 auto* Guard=ReviewEnemy(W,TEXT("ENM-STN-003"));const uint64 GuardId=Guard->GetRuntimeEntityId();
 if(!ReviewDeath(W,Guard))return false;R=W.Game->CaptureRunRewardsSnapshot();
 if(!TestTrue(TEXT("Three actual terminal slots make exactly three7/4/9 stacks, without crediting death wallet"),W.Game->bRoomCleared&&W.Player->Coins==20&&R.Schema==2&&R.Deaths.Num()==3&&R.Objects.Num()==3
  &&R.Objects[0].ResolvedAmount==7&&R.Objects[1].ResolvedAmount==4&&R.Objects[2].ResolvedAmount==9&&R.Collections.IsEmpty()))return false;
 // Normal A/D/W/S movement collects actual original objects; no direct CollectCoin or coin writes.
 const TArray<FDungeonRunRewardObject> OriginalObjects=R.Objects;
 for(const auto& O:OriginalObjects)if(!W.Move(O.Position.Y,false)||!W.Move(O.Position.X,true))return false;
 W.Frame(.005f);R=W.Game->CaptureRunRewardsSnapshot();
 if(!TestTrue(TEXT("Real normal proximity pickups alone commit20→40 with three exact physical collection receipts"),W.Player->Coins==40&&R.Collections.Num()==3&&R.NextOperationId==4
  &&R.Objects[0].Consumed&&R.Objects[1].Consumed&&R.Objects[2].Consumed))return false;
 FDungeonRunSnapshot Settled;TArray<uint8> SettledBytes;if(!ReviewCapture(W,Settled,SettledBytes))return false;
 const auto* Owner=Settled.Fighters.FindByPredicate([GuardId](const auto& F){return F.EntityId==GuardId;});
 if(!TestTrue(TEXT("Actual paid Guard is captured as inner Owner2 with original claimed dead kernel"),Owner&&Owner->Guard.IsSet()&&Owner->Guard.GetValue().Schema==2&&Owner->Dead&&Owner->DeathReported&&Owner->Guard.GetValue().DeathObserved&&Owner->Guard.GetValue().Kernel.RewardClaimed))return false;
 // A legal alternate kernel timeline is not the original paid death: same birth/entity/body,
 // but a later resolved185HP death. Complete pure kernel validity is a precondition, not the expected rejection.
 const auto& GK=Owner->Guard.GetValue();const auto& Original=GK.Kernel;
 const auto* Paid=Settled.Rewards.Deaths.FindByPredicate([GuardId](const auto& D){return D.Death.EntityId==GuardId;});if(!Paid)return false;
 const double LaterDeath=Paid->Death.AtTime+.05;
 if(!TestTrue(TEXT("Actual movement/pickup clock leaves room for independent later legal death timeline"),LaterDeath<Settled.SimulationTime))return false;
 RG::FGuardKernel Alternate(GuardId,Original.InitialTime,Original.InitialPosition,1,GK.Policy);RG::FWorldInput World;
 World.CanStartAttack=false;World.Sweep=[](const RG::FSweepRequest&){return RG::FSweepResult{};};
 if(!Alternate.BeginCombat()||!Alternate.StepTo(LaterDeath,World).Accepted||!Alternate.ApplyResolvedHit(1,185.,85.,World).Accepted
   ||!Alternate.ClaimDeathReward().Accepted||!Alternate.StepTo(Settled.SimulationTime,World).Accepted)return false;
 const auto Different=Alternate.Capture();RG::FGuardKernel Independent(GuardId,Original.InitialTime,Original.InitialPosition,1,GK.Policy);
 if(!TestTrue(TEXT("Alternate death kernel is independently legal under unchanged native Guard restore, not malformed history"),Independent.Restore(Different)&&Different.HP==0&&Different.RewardClaimed&&Different.Time==Settled.SimulationTime&&Different.Position.X==Original.Position.X&&Different.Position.Y==Original.Position.Y))return false;
 auto Bad=Settled;auto* BadGuard=Bad.Fighters.FindByPredicate([GuardId](const auto& F){return F.EntityId==GuardId;});BadGuard->Guard.GetValue().Kernel=Different;
 FDungeonValidatedRun Sentinel;if(!FDungeonRunAggregate::Validate(Settled,Sentinel,Why))return false;const auto* Before=Sentinel.Get();
 const bool AcceptedForgery=FDungeonRunAggregate::Validate(Bad,Sentinel,Why);
 TestFalse(TEXT("Owner2 rejects a different legal Guard death timeline attached to already-paid original reward (review regression)"),AcceptedForgery);
 if(!AcceptedForgery)TestTrue(TEXT("Death-history refusal preserves previous sealed root"),Sentinel.Get()==Before&&!Why.IsEmpty());
 Bad=Settled;Bad.Fighters[0].Coins+=1;TestFalse(TEXT("Wallet cannot mint a coin beyond original three physical collection receipts"),FDungeonRunAggregate::Validate(Bad,Sentinel,Why));
 FCodecWorld T(*this);if(!ReviewInstall(T,SettledBytes))return false;
 auto* RestoredGuard=ReviewEnemy(T,TEXT("ENM-STN-003"));if(!RestoredGuard)return false;const uint64 Cursor=RestoredGuard->GetStoneGuardDriver()->State().NextEventId;
 T.Game->OnFighterDied(RestoredGuard);T.Game->OnFighterDied(RestoredGuard);T.Frame(.05f);
 TestTrue(TEXT("Restored settled Guard cannot repay/reissue death/claim after actual resume"),RestoredGuard->bDeathReported&&RestoredGuard->GetStoneGuardDriver()->State().NextEventId==Cursor
  &&T.Player->Coins==40&&T.Game->CaptureRunRewardsSnapshot().Deaths.Num()==3&&T.Game->CaptureRunRewardsSnapshot().Collections.Num()==3);
 if(!T.ReachExit()||!T.Pulse(EKeys::Enter))return false;
 if(!TestTrue(TEXT("Real E confirmation and fresh Enter leave room normally without wallet loss"),T.Game->RoomNumber==2&&T.Game->GetEquipmentView().RoomInstanceId==2&&T.Player->Coins==40))return false;
 for(const auto E:T.Game->Enemies)E->bAIEnabled=false;
 FDungeonRunSnapshot Exited;TArray<uint8> ExitBytes;if(!ReviewCapture(T,Exited,ExitBytes))return false;
 const auto& ER=Exited.Rewards;
 if(!TestTrue(TEXT("Room2 keeps original paid/collected/retired room1 history plus new future Bat/Guard obligations"),Exited.Schema==2&&ER.Schema==2&&ER.RoomPlans.Num()==2&&ER.RoomExits.Num()==1&&ER.RetiredEntities.Num()==3
  &&ER.Objects.Num()==3&&ER.Collections.Num()==3&&ER.Objects[0].Consumed&&ER.Objects[0].Retired&&ER.Objects[1].Consumed&&ER.Objects[1].Retired&&ER.Objects[2].Consumed&&ER.Objects[2].Retired
  &&ER.RoomPlans[1].Slots[0].Stage==EDungeonGuardRoomSlotStage::Materialized&&ER.RoomPlans[1].Slots[1].Stage==EDungeonGuardRoomSlotStage::Future&&ER.RoomPlans[1].Slots[2].Stage==EDungeonGuardRoomSlotStage::Future
  &&ER.RoomPlans[1].Slots[2].EntityId==0&&!Exited.RoomCleared&&Exited.Pickups.IsEmpty()))return false;
 Bad=Exited;Bad.Fighters.Add(*Owner);Bad.EnemyOrder.Add(GuardId);
 TestFalse(TEXT("Historical paid room1 Guard cannot be reinstalled as a current room2 actor"),FDungeonRunAggregate::Validate(Bad,Sentinel,Why));
 Bad=Exited;Bad.Rewards.RoomPlans[1].Slots.RemoveAt(2);
 TestFalse(TEXT("Future unmaterialized Guard obligation cannot be erased after ordinary room exit"),FDungeonRunAggregate::Validate(Bad,Sentinel,Why));
 FCodecWorld U(*this);if(!ReviewInstall(U,ExitBytes))return false;
 for(const auto E:U.Game->Enemies)E->bAIEnabled=false;
 if(!ReviewDeath(U,ReviewEnemy(U,TEXT("ENM-STN-001"))))return false;
 const auto UR=U.Game->CaptureRunRewardsSnapshot();const double NextDeath=UR.Deaths.Last().Death.AtTime;
 if(!ReviewBorn(U,TEXT("ENM-STN-002"),NextDeath))return false;
 const auto Last=U.Game->CaptureRunRewardsSnapshot();
 TestTrue(TEXT("Restored room2 future wave advances exactly once while historical wallet/deaths remain original"),Last.RoomPlans.Num()==2&&Last.Deaths.Num()==4&&Last.Objects.Num()==4&&Last.Objects.Last().ObjectId==4
  &&Last.Objects.Last().ResolvedAmount==7&&Last.Collections.Num()==3&&U.Player->Coins==40&&Last.RoomPlans[1].Slots[2].Stage==EDungeonGuardRoomSlotStage::Future&&!U.Game->bRoomCleared);
 TArray<uint8> LegacyAgain;TestTrue(TEXT("Bridge settlement/restore/exit does not change old V1 encoder bytes or legacy sealed values"),DungeonRunSnapshotCodec::Encode(L,LegacyAgain,Why)&&LegacyAgain==OldWire&&LegacyAgain==FCodecOracle::Bytes(L));
 return true;
}
#endif
