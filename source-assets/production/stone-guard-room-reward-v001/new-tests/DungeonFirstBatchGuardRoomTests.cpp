#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFirstBatchGuardRoom.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"

namespace
{
bool Bridge(FCodecWorld& W,uint64 Seed=71)
{
 if(!W.Create()||!W.Game->BeginFirstBatchGuardRoom(Seed))return false;
 const auto& V=W.Game->GetEquipmentView();
 if(!W.Test.TestTrue(TEXT("Legal real FirstBatch new Run, Scene geometry and unchanged wallet before combat"),
  V.Bound&&V.Config==EDungeonEquipmentRunConfig::FirstBatch&&V.RoomInstanceId==1&&V.CombatSeed==Seed
  &&W.Game->GetSceneRoomView().Active&&W.Player->Coins==20&&W.Game->GetSimulationTime()==0.))return false;
 for(auto E:W.Game->Enemies)E->bAIEnabled=false; // Explicit time-zero source control, no HP/identity/room mutation.
 return W.Pulse(EKeys::Enter)&&!W.Game->bWaitingForStart;
}
ADungeonFighter* Enemy(FCodecWorld& W,const TCHAR* Content)
{for(auto E:W.Game->Enemies)if(IsValid(E)&&E->EnemyContentId==Content)return E.Get();return nullptr;}
bool AcceptedDeath(FCodecWorld& W,ADungeonFighter* E)
{
 if(!E)return false;
 // Existing actual incoming-damage adapter, as accepted Guard native tests use.
 // This does not claim a normal-J weapon/hit-geometry or visual proof.
 E->ApplyCombatHit(100000.f,W.Player,85.f);W.Frame(.005f);
 return E->bDead;
}
bool Future(FCodecWorld& W,const TCHAR* Content,double After)
{
 if(!W.AdvanceTo(After+3.21))return false;
 auto E=Enemy(W,Content);if(!E)return false;E->bAIEnabled=false;return true;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFirstBatchGuardCompleteManifest,
 "CodexDungeon.Content.FirstBatchGuardRoom.SeededFullManifestAndPreallocation",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFirstBatchGuardCompleteManifest::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!Bridge(W))return false;FDungeonFirstBatchGuardRoomView P;
 if(!TestTrue(TEXT("Expected committed complete native Bridge slot plan after real FirstBatch room entry"),W.Game->QueryFirstBatchGuardRoom(P)))return false;
 TestTrue(TEXT("Versioned Bridge is explicitly distinct from six-slot RSEQ001 and has one room budget"),P.Version==1
  &&P.TemplateId==TEXT("NATIVE-FIRSTBATCH-GUARD-BRIDGE-V001")&&P.GoldSourceId==TEXT("RWD-NATIVE-GUARD-BRIDGE-V001-GOLD")
  &&P.RunGuid==W.Game->GetEquipmentView().RunGuid&&P.RoomInstanceId==1&&P.Seed==71&&P.GoldBudget==20&&P.Slots.Num()==3&&P.ClearAt<0.);
 const TCHAR* Contents[]={TEXT("ENM-STN-001"),TEXT("ENM-STN-002"),TEXT("ENM-STN-003")};
 const int32 Weights[]={3,2,4},Coins[]={7,4,9};
 if(P.Slots.Num()!=3)return false;
 for(int32 I=0;I<3;++I)
  TestTrue(TEXT("Whole finite manifest weights and hand-calculated shares fixed before future waves"),P.Slots[I].ContentId==Contents[I]
   &&P.Slots[I].Weight==Weights[I]&&P.Slots[I].Coins==Coins[I]&&P.Slots[I].Group==uint32(I)
   &&P.Slots[I].Stage==(I==0?EDungeonGuardRoomSlotStage::Materialized:EDungeonGuardRoomSlotStage::Future)
   &&(I==0?P.Slots[I].EntityId!=0:P.Slots[I].EntityId==0)&&P.Slots[I].CoinObjectId==0);
 FDungeonFirstBatchGuardRoomView Again;
 TestTrue(TEXT("Read-only observations never reroll seed, reallocate or materialize future slots"),W.Game->QueryFirstBatchGuardRoom(Again)
  &&Again.Seed==P.Seed&&Again.Slots[0].EntityId==P.Slots[0].EntityId&&Again.Slots[2].SpawnPosition==P.Slots[2].SpawnPosition);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFirstBatchGuardDeathCoinsAndClear,
 "CodexDungeon.Content.FirstBatchGuardRoom.FutureWavesDeathCoinPickupAndClearOnce",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFirstBatchGuardDeathCoinsAndClear::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!Bridge(W))return false;auto K=Enemy(W,TEXT("ENM-STN-001"));
 if(!TestTrue(TEXT("Initial slot is real admitted Knight with native driver"),K&&K->GetStoneKnightDriver()))return false;
 if(!AcceptedDeath(W,K))return false;
 if(!TestTrue(TEXT("Expected future required slots prevent room-clear after initial true death"),!W.Game->bRoomCleared))return false;
 TestTrue(TEXT("Death does not credit wallet before physical pickup"),W.Player->Coins==20);
 const double KnightDeath=W.Game->GetSimulationTime();W.Frame(1.f);
 TestTrue(TEXT("Breather owns future obligation without prematurely spawning Bat"),!Enemy(W,TEXT("ENM-STN-002"))&&!W.Game->bRoomCleared);
 if(!TestTrue(TEXT("Real future Bat materializes after predecessor terminal + breather + full warning"),Future(W,TEXT("ENM-STN-002"),KnightDeath)))return false;
 if(!AcceptedDeath(W,Enemy(W,TEXT("ENM-STN-002"))))return false;
 const double BatDeath=W.Game->GetSimulationTime();
 if(!TestTrue(TEXT("Real future Guard materializes from the same finite room plan"),Future(W,TEXT("ENM-STN-003"),BatDeath)))return false;
 auto G=Enemy(W,TEXT("ENM-STN-003"));if(!AcceptedDeath(W,G))return false;
 TestTrue(TEXT("Guard true death settles once and final full manifest alone clears room"),G->bDeathReported&&W.Game->bRoomCleared&&W.Player->Coins==20);
 auto R=W.Game->CaptureRunRewardsSnapshot();const int32 Deaths=R.Deaths.Num(),Objects=R.Objects.Num();
 W.Game->OnFighterDied(G);W.Frame(.005f);auto Retry=W.Game->CaptureRunRewardsSnapshot();
 TestTrue(TEXT("Repeated death observation cannot create a second coin/clear source"),Deaths==3&&Retry.Deaths.Num()==Deaths&&Retry.Objects.Num()==Objects&&R.Schema==2);
 TArray<uint64> CoinIds;int32 Total=0;
 for(const auto& O:R.Objects)if(O.Kind==EDungeonRunRewardKind::Coin){CoinIds.Add(O.ObjectId);Total+=O.ResolvedAmount;}
 TestTrue(TEXT("Exactly whole-room20 preallocated ground coins, with no death wallet credit"),CoinIds.Num()==3&&Total==20&&W.Player->Coins==20);
 for(uint64 Id:CoinIds)
 {
  auto Live=W.Game->CaptureRunRewardsSnapshot();const auto* O=Live.Objects.FindByPredicate([Id](const auto& X){return X.ObjectId==Id;});if(!O)return false;
  if(!W.Move(O->Position.Y,false)||!W.Move(O->Position.X,true))return false;W.Frame(.005f);
 }
 TestTrue(TEXT("Only actual normal movement into coin pickup commits full wallet increment"),W.Player->Coins==40
  &&W.Game->CaptureRunRewardsSnapshot().Collections.Num()==3);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFirstBatchGuardPlanSaveResume,
 "CodexDungeon.Content.FirstBatchGuardRoom.RootV2PendingPlanAndSettlementContinuity",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FFirstBatchGuardPlanSaveResume::RunTest(const FString&)
{
 FCodecWorld W(*this);if(!Bridge(W))return false;FDungeonRunSnapshot S;FString Why;
 if(!TestTrue(TEXT("Legal original Scene boundary captures before any future Guard exists"),W.Game->CaptureRunSnapshot(S,Why)))return false;
 if(!TestTrue(TEXT("Expected RootV2 and explicit Rewards schema2 for complete pending Guard-room plan"),S.Schema==2
  &&S.Scope==EDungeonRunScope::BoundDevelopmentV2&&S.Rewards.Schema==2))return false;
 TArray<uint8> B;FDungeonValidatedRun V;
 if(!TestTrue(TEXT("Actual RootV2 codec retains pending complete plan without born hidden enemies"),DungeonRunSnapshotCodec::Encode(S,B,Why)
  &&DungeonRunSnapshotCodec::Decode(B,V,Why)&&V.IsValid()&&V.Get()->EnemyOrder==S.EnemyOrder))return false;
 FCodecWorld T(*this);if(!T.Create())return false;FDungeonPreparedRun P;
 if(!TestTrue(TEXT("Real grouped install restores existing plan rather than restarting waves"),FDungeonRunInstaller::Prepare(*T.Game,V,P,Why)
  &&FDungeonRunInstaller::Install(*T.Game,P,Why)))return false;T.Player=T.Game->PlayerFighter;
 FDungeonFirstBatchGuardRoomView Before,After;
 if(!T.Game->QueryFirstBatchGuardRoom(Before))return false;T.Frame(.5f);
 TestTrue(TEXT("Technical install pause preserves future obligations, seed and exact deadlines"),T.Game->QueryFirstBatchGuardRoom(After)
  &&Before.Seed==After.Seed&&Before.Slots.Num()==After.Slots.Num()&&After.Slots[2].EntityId==0
  &&After.Slots[2].Stage==EDungeonGuardRoomSlotStage::Future&&T.Game->GetSimulationTime()==S.SimulationTime);
 if(!TestTrue(TEXT("Saved plan is the one complete three-slot room manifest"),S.Rewards.RoomPlans.Num()==1&&S.Rewards.RoomPlans[0].Slots.Num()==3))return false;
 auto Bad=S;Bad.Rewards.RoomPlans[0].Slots[2].Coins+=1;FDungeonValidatedRun Sentinel=V;const auto* Original=Sentinel.Get();
 TestFalse(TEXT("Forged per-slot share cannot bypass explicit reward validator"),FDungeonRunAggregate::Validate(Bad,Sentinel,Why));
 TestTrue(TEXT("Failed plan validation leaves prior sealed RootV2 untouched"),Sentinel.Get()==Original);
 return true;
}
#endif
