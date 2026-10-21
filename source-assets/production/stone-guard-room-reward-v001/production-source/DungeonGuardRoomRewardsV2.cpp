#include "DungeonGuardRoomRewardsV2.h"
#include "DungeonRoomCoinAllocation.h"
#include "DungeonRoomLayout.h"
#include <limits>
namespace DungeonGuardRoomRewardsV2
{
namespace
{
bool Fail(FString& W,const TCHAR* X){W=X;return false;}
bool Time(double X){return FMath::IsFinite(X)&&X>=0.;}
bool Point(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y)&&DungeonRoomLayout::CenterBounds().IsInsideOrOn(P);}
const TCHAR* Contents[]={TEXT("ENM-STN-001"),TEXT("ENM-STN-002"),TEXT("ENM-STN-003")};
const int32 Weights[]={3,2,4};
const FDungeonGuardRoomSlot* FindSlot(const FDungeonRunRewardSnapshot& S,uint64 Room,uint64 Entity)
{for(const auto& P:S.RoomPlans)if(P.RoomInstanceId==Room)for(const auto& X:P.Slots)if(X.EntityId==Entity)return &X;return nullptr;}
bool SameDeath(const FDungeonRunRewardDeathRequest& A,const FDungeonRunRewardDeathRequest& B)
{return A.EntityId==B.EntityId&&A.RoomInstanceId==B.RoomInstanceId&&A.ContentId==B.ContentId&&A.AtTime==B.AtTime
 &&A.Position==B.Position&&A.FirstDeath==B.FirstDeath&&A.RoomCleared==B.RoomCleared;}
}
FVector2D Anchor(uint64 Seed,int32 Slot,uint32 Attempt)
{
 // Cover the same room on both sides of any normal combat position. A pool
 // concentrated at the edges can satisfy distance OR visibility, but not both.
 static const double X[]={-1200,-800,-400,0,400,800,1200},Y[]={-320,-160,0,160,320};
 const uint64 Index=(Seed%AnchorCount+uint64(Slot)*3+Attempt)%AnchorCount;
 return {X[Index%UE_ARRAY_COUNT(X)],Y[Index/UE_ARRAY_COUNT(X)]};
}
FDungeonFirstBatchGuardRoomView Plan(FGuid Run,uint64 Room,uint64 Seed,double At)
{
 FDungeonFirstBatchGuardRoomView P;P.RunGuid=Run;P.RoomInstanceId=Room;P.Seed=Seed;
 P.TemplateId=TEXT("NATIVE-FIRSTBATCH-GUARD-BRIDGE-V001");P.GoldSourceId=TEXT("RWD-NATIVE-GUARD-BRIDGE-V001-GOLD");
 P.GoldBudget=20;P.EnteredAt=At;P.OrientationUntil=At+1.;
 DungeonRoomCoinAllocation::FRequest Q;Q.RoomInstanceId=Room;Q.SourceId="RWD-NATIVE-GUARD-BRIDGE-V001-GOLD";Q.Budget=20;
 for(int32 I=0;I<3;++I)Q.Slots.push_back({"NATIVE-GUARD-BRIDGE-S0"+std::to_string(I+1),Weights[I]});
 DungeonRoomCoinAllocation::FAllocation A;
 if(DungeonRoomCoinAllocation::TryAllocate(Q,A)!=DungeonRoomCoinAllocation::EStatus::Ok)return {};
 for(int32 I=0;I<3;++I)
 {
  FDungeonGuardRoomSlot X;X.SlotId=UTF8_TO_TCHAR(A.Slots[I].SlotId.c_str());X.ContentId=Contents[I];X.Group=I;
  X.Weight=Weights[I];X.Coins=int32(A.Slots[I].Coins);X.SpawnPosition=I==0?FVector2D(300,0):Anchor(Seed,I,0);P.Slots.Add(X);
 }
 return P;
}
bool Validate(const FDungeonRunRewardSnapshot& S,const FDungeonRunRewardValidationContext* C,FString& W)
{
 if(S.Schema!=2||!S.Bound||!S.RunGuid.IsValid()||!S.OwnerId||!S.CurrentRoomInstanceId||S.InitialCoins!=20
  ||S.CurrentRoomInstanceId!=uint64(S.RoomPlans.Num())||S.RoomExits.Num()!=S.RoomPlans.Num()-1)
  return Fail(W,TEXT("Invalid explicit Bridge reward schema2 scope/plan lineage"));
 if(S.Sources.Num()!=S.Objects.Num()||S.NextSourceId!=uint64(S.Objects.Num())+1||S.NextObjectId!=S.NextSourceId
  ||S.NextOperationId!=uint64(S.Collections.Num())+1)return Fail(W,TEXT("Bridge reward ID cursor differs from exact resolved history"));
 TSet<uint64> Entities;int32 DeadSlots=0;
 for(int32 R=0;R<S.RoomPlans.Num();++R)
 {
  const auto& P=S.RoomPlans[R];const auto Literal=Plan(S.RunGuid,uint64(R)+1,P.Seed,P.EnteredAt);
  if(P.Version!=1||P.RunGuid!=S.RunGuid||P.RoomInstanceId!=uint64(R)+1||P.TemplateId!=Literal.TemplateId||P.GoldSourceId!=Literal.GoldSourceId
   ||P.GoldBudget!=20||!Time(P.EnteredAt)||P.OrientationUntil!=P.EnteredAt+1.||P.Slots.Num()!=3
   ||(R==0?P.EnteredAt!=0.:P.EnteredAt!=S.RoomExits[R-1].AtTime))return Fail(W,TEXT("Bridge complete finite manifest/seed/budget/timing changed"));
  double LastDeath=-1.;bool AllDead=true;
  for(int32 I=0;I<3;++I)
  {
   const auto& X=P.Slots[I];const auto& L=Literal.Slots[I];
   if(X.SlotId!=L.SlotId||X.ContentId!=L.ContentId||X.Group!=uint32(I)||X.Weight!=L.Weight||X.Coins!=L.Coins||!Point(X.SpawnPosition)
    ||X.AnchorAttempt>MaxAnchorAttempts+AnchorCount-1||(X.RetryAt!=-1.&&(!Time(X.RetryAt)||X.RetryAt<P.EnteredAt||(C&&X.RetryAt>C->SimulationTime+1.)))
    ||X.SpawnPosition!=(I==0?FVector2D(300,0):Anchor(P.Seed,I,X.AnchorAttempt)))return Fail(W,TEXT("Bridge slot identity/allocation/seeded anchor changed"));
   if(X.Stage==EDungeonGuardRoomSlotStage::Future)
   {if(X.EntityId||X.CoinObjectId||X.WarningAt!=-1.||X.MaterializedAt!=-1.||X.DeadAt!=-1.)return Fail(W,TEXT("Unborn slot has actor, payout or entered warning"));}
   else if(X.Stage==EDungeonGuardRoomSlotStage::Warning)
   {if(I==0||X.EntityId||X.CoinObjectId||X.RetryAt!=-1.||!Time(X.WarningAt)||P.Slots[I-1].Stage!=EDungeonGuardRoomSlotStage::Dead
     ||X.WarningAt<P.Slots[I-1].DeadAt+2.||X.MaterializedAt!=-1.||X.DeadAt!=-1.)return Fail(W,TEXT("Future warning bypassed real predecessor terminal/breather"));}
   else if(X.Stage==EDungeonGuardRoomSlotStage::Materialized||X.Stage==EDungeonGuardRoomSlotStage::Dead)
   {
    if(!X.EntityId||X.EntityId==S.OwnerId||Entities.Contains(X.EntityId)||!Time(X.MaterializedAt)
     ||(I==0?(X.MaterializedAt!=P.EnteredAt||X.WarningAt!=-1.):(!Time(X.WarningAt)||P.Slots[I-1].Stage!=EDungeonGuardRoomSlotStage::Dead
      ||X.WarningAt<P.Slots[I-1].DeadAt+2.||X.MaterializedAt<X.WarningAt+1.2)))return Fail(W,TEXT("Materialized slot missing unique actual identity or full warning"));
    Entities.Add(X.EntityId);
    if(X.Stage==EDungeonGuardRoomSlotStage::Dead)
    {if(!Time(X.DeadAt)||X.DeadAt<X.MaterializedAt||!X.CoinObjectId)return Fail(W,TEXT("Terminal slot lacks original death/payout identity"));LastDeath=FMath::Max(LastDeath,X.DeadAt);++DeadSlots;}
    else if(X.DeadAt!=-1.||X.CoinObjectId)return Fail(W,TEXT("Live slot invented death reward"));
   }
   else return Fail(W,TEXT("Unknown Bridge slot stage"));
   AllDead&=X.Stage==EDungeonGuardRoomSlotStage::Dead;
   if(C&&(X.WarningAt>C->SimulationTime||X.MaterializedAt>C->SimulationTime||X.DeadAt>C->SimulationTime))return Fail(W,TEXT("Bridge slot event comes from future"));
  }
  if(P.ClearAt!=(AllDead?LastDeath:-1.)||(R<S.RoomPlans.Num()-1&&!AllDead))return Fail(W,TEXT("Room clear precedes all finite required slot terminals"));
  if(R<S.RoomExits.Num())
  {
   const auto& E=S.RoomExits[R];if(E.RoomInstanceId!=P.RoomInstanceId||E.NextRoomInstanceId!=P.RoomInstanceId+1||!Time(E.AtTime)||E.AtTime<P.ClearAt
    ||E.EntityIds.Num()!=3||E.ObjectIds.Num()!=3)return Fail(W,TEXT("Bridge exit lost exact full-room entities/objects"));
   for(const auto& X:P.Slots)if(!E.EntityIds.Contains(X.EntityId)||!E.ObjectIds.Contains(X.CoinObjectId))return Fail(W,TEXT("Exit differs from admitted room plan"));
  }
 }
 if(DeadSlots!=S.Deaths.Num()||S.Objects.Num()!=DeadSlots)return Fail(W,TEXT("Every true settled slot requires exactly one original gold stack"));
 TSet<uint64> Deaths;double PreviousDeath=0.;
 for(int32 I=0;I<S.Deaths.Num();++I)
 {
  const auto& D=S.Deaths[I];const auto& Q=D.Death;const auto* X=FindSlot(S,Q.RoomInstanceId,Q.EntityId);
  if(!X||X->Stage!=EDungeonGuardRoomSlotStage::Dead||X->ContentId!=Q.ContentId||X->DeadAt!=Q.AtTime||!Time(Q.AtTime)||Q.AtTime<PreviousDeath
   ||Deaths.Contains(Q.EntityId)||!Point(Q.Position)||D.SourceIds.Num()!=1||D.SourceIds[0]!=uint64(I)+1||X->CoinObjectId!=uint64(I)+1)
   return Fail(W,TEXT("Bridge death differs from one true admitted slot settlement"));
  const auto& P=S.RoomPlans[int32(Q.RoomInstanceId)-1];
  if(Q.FirstDeath!=(X->Group==0)||Q.RoomCleared!=(X->Group==2))return Fail(W,TEXT("Bridge first/whole-room clear death claim invalid"));
  const auto& A=S.Sources[I];const auto& O=S.Objects[I];const bool Retired=Q.RoomInstanceId<S.CurrentRoomInstanceId;
  const double RetiredAt=Retired?S.RoomExits[int32(Q.RoomInstanceId)-1].AtTime:0.;
  if(A.SourceId!=uint64(I)+1||A.ObjectId!=A.SourceId||A.EntityId!=Q.EntityId||A.RoomInstanceId!=Q.RoomInstanceId||A.Kind!=EDungeonRunRewardSourceKind::EnemyCoin||A.AtTime!=Q.AtTime
   ||O.ObjectId!=A.SourceId||O.SourceId!=A.SourceId||O.RoomInstanceId!=Q.RoomInstanceId||O.Kind!=EDungeonRunRewardKind::Coin||O.ResolvedAmount!=X->Coins
   ||O.Position!=Q.Position+FVector2D(-18,-12)||O.Retired!=Retired||O.RetiredAt!=RetiredAt)return Fail(W,TEXT("Original preallocated coin object/source altered"));
  Deaths.Add(Q.EntityId);PreviousDeath=Q.AtTime;
 }
 int64 Wallet=S.InitialCoins;TSet<uint64> Collected;double LastCollect=0.;
 for(int32 I=0;I<S.Collections.Num();++I)
 {
  const auto& A=S.Collections[I];const auto& Q=A.Request;
  if(Q.OperationId!=uint64(I)+1||Q.OwnerId!=S.OwnerId||!Q.ObjectId||Q.ObjectId>uint64(S.Objects.Num()))return Fail(W,TEXT("Invalid Bridge pickup identity/cursor"));
  const auto& O=S.Objects[int32(Q.ObjectId)-1];
  if(Collected.Contains(Q.ObjectId)||Q.SourceId!=O.SourceId||Q.RoomInstanceId!=O.RoomInstanceId||!Time(Q.AtTime)||Q.AtTime<LastCollect
   ||Q.AtTime<S.Sources[int32(O.SourceId)-1].AtTime||(O.Retired&&Q.AtTime>O.RetiredAt)||Q.BeforeCoins!=Wallet
   ||Wallet>MAX_int32-O.ResolvedAmount||A.AfterCoins!=Wallet+O.ResolvedAmount||!O.Consumed||O.CollectionOperationId!=Q.OperationId)
   return Fail(W,TEXT("Bridge wallet requires exact once-only physical pickup chain"));
  Wallet=A.AfterCoins;LastCollect=Q.AtTime;Collected.Add(Q.ObjectId);
 }
 for(const auto& O:S.Objects)if(O.Consumed!=Collected.Contains(O.ObjectId)||(!O.Consumed&&O.CollectionOperationId))return Fail(W,TEXT("Coin consumed without wallet receipt"));
 if(S.RetiredEntities.Num()!=3*S.RoomExits.Num())return Fail(W,TEXT("Historical Bridge actor tombstones incomplete"));
 TSet<uint64> Retired;
 for(const auto& A:S.RetiredEntities)
 {
  const auto* X=FindSlot(S,A.Actor.RoomInstanceId,A.Actor.EntityId);
  if(!X||A.Actor.RoomInstanceId>=S.CurrentRoomInstanceId||Retired.Contains(A.Actor.EntityId)||A.Actor.ContentId!=X->ContentId||!A.Actor.Enemy
   ||!A.Actor.Dead||!A.Actor.DeathReported||!A.Actor.RewardClaimed||A.RetiredAt!=S.RoomExits[int32(A.Actor.RoomInstanceId)-1].AtTime)
   return Fail(W,TEXT("Historical settled Bridge actor identity changed"));Retired.Add(A.Actor.EntityId);
 }
 if(C)
 {
  const auto* World=C->WeaponWorld;
  if(C->RunGuid!=S.RunGuid||C->OwnerId!=S.OwnerId||C->RoomInstanceId!=S.CurrentRoomInstanceId||!Time(C->SimulationTime)||C->PlayerCoins!=Wallet
   ||!World||World->RunGuid!=S.RunGuid||World->RoomInstanceId!=S.CurrentRoomInstanceId||World->Time!=C->SimulationTime
   ||PreviousDeath>C->SimulationTime||LastCollect>C->SimulationTime)return Fail(W,TEXT("Bridge aggregate clock/scope/wallet context differs"));
  const auto* OwnerActor=C->CurrentActors.FindByPredicate([&](const auto& A){return A.EntityId==S.OwnerId;});
  const bool OwnerDead=OwnerActor&&OwnerActor->Dead;
  TSet<uint64> Current;bool HasPlayer=false;
  for(const auto& A:C->CurrentActors)
  {
   if(!A.EntityId||Current.Contains(A.EntityId)||A.RoomInstanceId!=S.CurrentRoomInstanceId)return Fail(W,TEXT("Duplicate/foreign current Bridge actor"));Current.Add(A.EntityId);
   const auto* B=World->ActorBindings.FindByPredicate([&](const auto& V){return V.EntityId==A.EntityId;});
   if(!B||B->ContentId!=A.ContentId)return Fail(W,TEXT("Current Bridge actor lacks actual world binding"));
   if(A.EntityId==S.OwnerId){if(A.Enemy||A.ContentId!=TEXT("player"))return Fail(W,TEXT("Invalid Bridge wallet owner"));HasPlayer=true;continue;}
   const auto* X=FindSlot(S,S.CurrentRoomInstanceId,A.EntityId);
   if(!X||B->RoomInstanceId!=S.CurrentRoomInstanceId||X->ContentId!=A.ContentId||!A.Enemy||A.DeathReported!=(X->Stage==EDungeonGuardRoomSlotStage::Dead)
    ||A.Dead&&!A.DeathReported&&!OwnerDead
    ||A.DeathReported&&(!A.Dead||!A.RewardClaimed))return Fail(W,TEXT("Current native actor and settled slot disagree"));
  }
  if(!HasPlayer)return Fail(W,TEXT("Bridge missing current player"));
  for(const auto& P:S.RoomPlans)for(const auto& X:P.Slots)if(X.EntityId)
  {
   const auto* B=World->ActorBindings.FindByPredicate([&](const auto& V){return V.EntityId==X.EntityId;});
   if(!B||B->ContentId!=X.ContentId||B->RoomInstanceId!=P.RoomInstanceId||(P.RoomInstanceId==S.CurrentRoomInstanceId&&!Current.Contains(X.EntityId)))
    return Fail(W,TEXT("Born Bridge slot lost exact current/historical world identity"));
  }
  for(const auto& B:World->ActorBindings)if(B.EntityId!=S.OwnerId&&!FindSlot(S,B.RoomInstanceId,B.EntityId))return Fail(W,TEXT("Unknown actor injected outside finite Bridge manifest"));
 }
 W.Reset();return true;
}
FDungeonRunRewardDeathResult ResolveDeath(FDungeonRunRewardSnapshot& State,const FDungeonRunRewardDeathRequest& Q,FString& W)
{
 FDungeonRunRewardDeathResult R;R.Status=EDungeonRunRewardStatus::InvalidRequest;
 if(const auto* Old=State.Deaths.FindByPredicate([&](const auto& D){return D.Death.EntityId==Q.EntityId;}))
 {if(!SameDeath(Old->Death,Q)){Fail(W,TEXT("Bridge death retry changed original facts"));return R;}R.Status=EDungeonRunRewardStatus::Ok;R.Replayed=true;R.ObjectIds=Old->SourceIds;return R;}
 auto Candidate=State;
 if(Q.RoomInstanceId!=State.CurrentRoomInstanceId||Candidate.RoomPlans.IsEmpty())return R;
 auto& P=Candidate.RoomPlans.Last();auto* X=P.Slots.FindByPredicate([&](const auto& V){return V.EntityId==Q.EntityId;});
 if(!X||X->Stage!=EDungeonGuardRoomSlotStage::Materialized||X->ContentId!=Q.ContentId||!Time(Q.AtTime)||Q.AtTime<X->MaterializedAt)return R;
 if(Candidate.NextObjectId>uint64(MAX_int32))return R;
 const uint64 Id=Candidate.NextObjectId++;++Candidate.NextSourceId;X->Stage=EDungeonGuardRoomSlotStage::Dead;X->DeadAt=Q.AtTime;X->CoinObjectId=Id;
 FDungeonRunRewardDeathFact D;D.Death=Q;D.SourceIds.Add(Id);Candidate.Deaths.Add(D);
 Candidate.Sources.Add({Id,Id,Q.EntityId,Q.RoomInstanceId,EDungeonRunRewardSourceKind::EnemyCoin,Q.AtTime});
 FDungeonRunRewardObject O;O.ObjectId=O.SourceId=Id;O.RoomInstanceId=Q.RoomInstanceId;O.Kind=EDungeonRunRewardKind::Coin;O.Position=Q.Position+FVector2D(-18,-12);O.ResolvedAmount=X->Coins;Candidate.Objects.Add(O);
 if(!P.Slots.ContainsByPredicate([](const auto& V){return V.Stage!=EDungeonGuardRoomSlotStage::Dead;}))P.ClearAt=Q.AtTime;
 if(!Validate(Candidate,nullptr,W))return R;State=MoveTemp(Candidate);R.Status=EDungeonRunRewardStatus::Ok;R.ObjectIds.Add(Id);return R;
}
}
