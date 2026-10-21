#include "DungeonRunRewards.h"
#include <limits>

namespace
{
using FS=FDungeonRunRewardSnapshot;
bool Fail(FString& Why,const TCHAR* Message){Why=Message;return false;}
bool Time(double X){return FMath::IsFinite(X)&&X>=0.;}
bool Point(FVector2D P){return FMath::IsFinite(P.X)&&FMath::IsFinite(P.Y);}
bool EnemyContent(const FString& X)
{return X==TEXT("ENM-STN-001")||X==TEXT("ENM-STN-002")||X==TEXT("QA-PROTOTYPE-ENEMY");}
bool SameDeath(const FDungeonRunRewardDeathRequest& A,const FDungeonRunRewardDeathRequest& B)
{return A.EntityId==B.EntityId&&A.RoomInstanceId==B.RoomInstanceId&&A.ContentId==B.ContentId
    &&A.AtTime==B.AtTime&&A.Position==B.Position&&A.FirstDeath==B.FirstDeath&&A.RoomCleared==B.RoomCleared;}
bool SameCollect(const FDungeonRunRewardCollectRequest& A,const FDungeonRunRewardCollectRequest& B)
{return A.OperationId==B.OperationId&&A.ObjectId==B.ObjectId&&A.SourceId==B.SourceId&&A.OwnerId==B.OwnerId
    &&A.RoomInstanceId==B.RoomInstanceId&&A.AtTime==B.AtTime&&A.BeforeCoins==B.BeforeCoins;}
bool SameActor(const FDungeonRunRewardActorFact& A,const FDungeonRunRewardActorFact& B)
{return A.EntityId==B.EntityId&&A.RoomInstanceId==B.RoomInstanceId&&A.ContentId==B.ContentId
    &&A.Enemy==B.Enemy&&A.Dead==B.Dead&&A.DeathReported==B.DeathReported&&A.RewardClaimed==B.RewardClaimed;}
const FDungeonRunRewardObject* Object(const FS& S,uint64 Id)
{return S.Objects.FindByPredicate([Id](const auto& X){return X.ObjectId==Id;});}
const FDungeonRunRewardDeathFact* Death(const FS& S,uint64 Id)
{return S.Deaths.FindByPredicate([Id](const auto& X){return X.Death.EntityId==Id;});}
const FDungeonRunRewardRoomExit* Exit(const FS& S,uint64 Room)
{return S.RoomExits.FindByPredicate([Room](const auto& X){return X.RoomInstanceId==Room;});}
double EnteredAt(const FS& S,uint64 Room)
{const auto* Previous=Room>1?Exit(S,Room-1):nullptr;return Previous?Previous->AtTime:0.;}
int32 Wallet(const FS& S){return S.Collections.IsEmpty()?S.InitialCoins:S.Collections.Last().AfterCoins;}
FDungeonRunRewardCollectResult Collected(const FDungeonRunRewardCollection& C,bool Replayed)
{
    FDungeonRunRewardCollectResult R;R.Status=EDungeonRunRewardStatus::Ok;R.Replayed=Replayed;
    R.OperationId=C.Request.OperationId;R.ObjectId=C.Request.ObjectId;
    R.BeforeCoins=C.Request.BeforeCoins;R.AfterCoins=C.AfterCoins;return R;
}

// Pure value validation. No pointer enters State and no result is installed here.
bool Validate(const FS& S,const FDungeonRunRewardValidationContext* C,FString& Why)
{
    if(S.Schema!=1||!S.Bound||!S.RunGuid.IsValid()||!S.OwnerId||!S.CurrentRoomInstanceId
        ||S.CurrentRoomInstanceId==std::numeric_limits<uint64>::max()||S.InitialCoins<0)
        return Fail(Why,TEXT("Unsupported or unbound reward schema/scope"));
    if(S.Sources.Num()!=S.Objects.Num()||S.NextSourceId!=uint64(S.Sources.Num())+1
        ||S.NextObjectId!=uint64(S.Objects.Num())+1||S.NextOperationId!=uint64(S.Collections.Num())+1
        ||S.CurrentRoomInstanceId!=uint64(S.RoomExits.Num())+1)
        return Fail(Why,TEXT("Reward ID cursors or room lineage are not exact"));
    double PreviousExit=0.;
    for(int32 I=0;I<S.RoomExits.Num();++I)
    {
        const auto& E=S.RoomExits[I];
        if(E.RoomInstanceId!=uint64(I)+1||E.NextRoomInstanceId!=E.RoomInstanceId+1
            ||!Time(E.AtTime)||E.AtTime<PreviousExit)return Fail(Why,TEXT("Invalid reward room-exit chain"));
        PreviousExit=E.AtTime;
        TSet<uint64> Entities,Objects;
        for(uint64 Id:E.EntityIds)if(!Id||Id==S.OwnerId||Entities.Contains(Id))return Fail(Why,TEXT("Duplicate retired entity scope"));else Entities.Add(Id);
        for(uint64 Id:E.ObjectIds)if(!Id||Objects.Contains(Id))return Fail(Why,TEXT("Duplicate retired object scope"));else Objects.Add(Id);
        for(const auto& O:S.Objects)if(O.RoomInstanceId==E.RoomInstanceId)
            if(!Objects.Remove(O.ObjectId))return Fail(Why,TEXT("Room exit omitted an original resolved object"));
        if(!Objects.IsEmpty())return Fail(Why,TEXT("Room exit names an unknown or foreign object"));
        for(const auto& R:S.RetiredEntities)if(R.Actor.RoomInstanceId==E.RoomInstanceId)
            if(!Entities.Remove(R.Actor.EntityId)||R.RetiredAt!=E.AtTime)return Fail(Why,TEXT("Retirement identity or time differs from its exit"));
        if(!Entities.IsEmpty())return Fail(Why,TEXT("Room exit omitted its original actor tombstone"));
    }
    TSet<uint64> DeathIds,SourceIds;
    TSet<uint64> DeathRooms,ClearSourceRooms;
    uint64 SourceCursor=1;
    for(const auto& D:S.Deaths)
    {
        const auto& Q=D.Death;const auto* E=Exit(S,Q.RoomInstanceId);
        if(!Q.EntityId||Q.EntityId==S.OwnerId||DeathIds.Contains(Q.EntityId)||!EnemyContent(Q.ContentId)
            ||!Q.RoomInstanceId||Q.RoomInstanceId>S.CurrentRoomInstanceId||!Time(Q.AtTime)||!Point(Q.Position)
            ||Q.AtTime<EnteredAt(S,Q.RoomInstanceId)||(E&&Q.AtTime>E->AtTime)
            ||Q.FirstDeath==DeathRooms.Contains(Q.RoomInstanceId))
            return Fail(Why,TEXT("Invalid, duplicated or chronologically inconsistent death fact"));
        DeathIds.Add(Q.EntityId);DeathRooms.Add(Q.RoomInstanceId);
        const bool NewClear=Q.RoomCleared&&!ClearSourceRooms.Contains(Q.RoomInstanceId);
        if(NewClear)ClearSourceRooms.Add(Q.RoomInstanceId);
        const uint64 Count=1+uint64(Q.FirstDeath)+uint64(NewClear);
        if(uint64(D.SourceIds.Num())!=Count)return Fail(Why,TEXT("Death omitted or invented a resolved result"));
        for(uint64 Local=0;Local<Count;++Local,++SourceCursor)
        {
            if(SourceCursor>uint64(S.Sources.Num())||D.SourceIds[int32(Local)]!=SourceCursor||SourceIds.Contains(SourceCursor))
                return Fail(Why,TEXT("Death/source allocation order is not exact"));
            SourceIds.Add(SourceCursor);const auto& X=S.Sources[int32(SourceCursor-1)];const auto& O=S.Objects[int32(SourceCursor-1)];
            const bool Potion=Local==1&&Q.FirstDeath;
            const auto Kind=Local==0?EDungeonRunRewardKind::Coin:Potion?EDungeonRunRewardKind::Potion:EDungeonRunRewardKind::Axe;
            const auto SourceKind=Local==0?EDungeonRunRewardSourceKind::EnemyCoin:Potion?EDungeonRunRewardSourceKind::FirstDeathPotion:EDungeonRunRewardSourceKind::RoomClearAxe;
            const FVector2D Offset=Local==0?FVector2D(-18.,-12.):Potion?FVector2D(25.,15.):FVector2D(34.,14.);
            const int32 Amount=Local==0?5:Potion?30:1;
            if(X.SourceId!=SourceCursor||X.ObjectId!=SourceCursor||X.EntityId!=Q.EntityId||X.RoomInstanceId!=Q.RoomInstanceId
                ||X.Kind!=SourceKind||X.AtTime!=Q.AtTime||O.ObjectId!=SourceCursor||O.SourceId!=SourceCursor
                ||O.RoomInstanceId!=Q.RoomInstanceId||O.Kind!=Kind||O.Position!=Q.Position+Offset||O.ResolvedAmount!=Amount)
                return Fail(Why,TEXT("Resolved source/object value differs from its original death"));
            if(O.Retired!=(Q.RoomInstanceId<S.CurrentRoomInstanceId)||O.RetiredAt!=(E?E->AtTime:0.))
                return Fail(Why,TEXT("Resolved object retirement differs from its room"));
        }
    }
    if(SourceCursor!=S.NextSourceId)return Fail(Why,TEXT("Unreferenced reward source or object"));
    int64 Coins=S.InitialCoins;TSet<uint64> Consumed;
    double PreviousCollection=0.;
    for(int32 I=0;I<S.Collections.Num();++I)
    {
        const auto& R=S.Collections[I];const auto& Q=R.Request;const auto* O=Object(S,Q.ObjectId);
        if(Q.OperationId!=uint64(I)+1||Q.OwnerId!=S.OwnerId||!O||O->Kind!=EDungeonRunRewardKind::Coin
            ||Q.SourceId!=O->SourceId||Q.RoomInstanceId!=O->RoomInstanceId||Consumed.Contains(Q.ObjectId)
            ||!Time(Q.AtTime)||Q.AtTime<PreviousCollection||Q.AtTime<S.Sources[int32(O->SourceId-1)].AtTime
            ||Q.AtTime<EnteredAt(S,Q.RoomInstanceId)||(O->Retired&&Q.AtTime>O->RetiredAt)
            ||Q.BeforeCoins!=Coins||Coins>int64(MAX_int32)-O->ResolvedAmount||R.AfterCoins!=Coins+O->ResolvedAmount
            ||!O->Consumed||O->CollectionOperationId!=Q.OperationId)
            return Fail(Why,TEXT("Currency source/operation/time/wallet chain is inconsistent"));
        Coins=R.AfterCoins;PreviousCollection=Q.AtTime;Consumed.Add(Q.ObjectId);
    }
    for(const auto& O:S.Objects)if(O.Consumed!=Consumed.Contains(O.ObjectId)
        ||(!O.Consumed&&O.CollectionOperationId)||O.Kind!=EDungeonRunRewardKind::Coin&&O.Consumed)
        return Fail(Why,TEXT("Object consumption has no exact supported currency receipt"));
    TSet<uint64> RetiredIds;
    for(const auto& R:S.RetiredEntities)
    {
        const auto& A=R.Actor;const auto* E=Exit(S,A.RoomInstanceId);const auto* D=Death(S,A.EntityId);
        if(!A.EntityId||A.EntityId==S.OwnerId||RetiredIds.Contains(A.EntityId)||!A.Enemy||!EnemyContent(A.ContentId)
            ||!E||!Time(R.RetiredAt)||R.RetiredAt!=E->AtTime||A.DeathReported!=A.RewardClaimed
            ||A.DeathReported&&!A.Dead||bool(D)!=A.DeathReported
            ||D&&(D->Death.RoomInstanceId!=A.RoomInstanceId||D->Death.ContentId!=A.ContentId))
            return Fail(Why,TEXT("Invalid retired actor/death/claimed tombstone"));
        RetiredIds.Add(A.EntityId);
    }
    for(const auto& D:S.Deaths)if(D.Death.RoomInstanceId<S.CurrentRoomInstanceId&&!RetiredIds.Contains(D.Death.EntityId))
        return Fail(Why,TEXT("Historical death lost its retired actor"));
    if(C)
    {
        const auto* W=C->WeaponWorld;
        if(C->RunGuid!=S.RunGuid||C->OwnerId!=S.OwnerId||C->RoomInstanceId!=S.CurrentRoomInstanceId
            ||!Time(C->SimulationTime)||C->PlayerCoins!=Coins||!W||W->RunGuid!=S.RunGuid
            ||W->RoomInstanceId!=S.CurrentRoomInstanceId||W->Time!=C->SimulationTime
            ||PreviousExit>C->SimulationTime||PreviousCollection>C->SimulationTime)
            return Fail(Why,TEXT("Approved Run/world/room/time/wallet context differs"));
        for(const auto& D:S.Deaths)if(D.Death.AtTime>C->SimulationTime)return Fail(Why,TEXT("Death comes from the future"));
        TSet<uint64> BindingIds,CurrentIds;bool HasPlayer=false;
        for(const auto& A:C->CurrentActors)
        {
            if(!A.EntityId||CurrentIds.Contains(A.EntityId)||A.RoomInstanceId!=S.CurrentRoomInstanceId)
                return Fail(Why,TEXT("Ambiguous or wrong-room current actor"));
            CurrentIds.Add(A.EntityId);
            const auto* B=W->ActorBindings.FindByPredicate([&](const auto& X){return X.EntityId==A.EntityId;});
            if(!B||B->ContentId!=A.ContentId||!B->RoomInstanceId||B->RoomInstanceId>S.CurrentRoomInstanceId)
                return Fail(Why,TEXT("Current actor has no approved stable world binding"));
            if(A.EntityId==S.OwnerId)
            {
                if(A.Enemy||A.ContentId!=TEXT("player")||HasPlayer)return Fail(Why,TEXT("Invalid reward wallet owner"));
                HasPlayer=true;
            }
            else
            {
                const auto* D=Death(S,A.EntityId);
                if(A.ContentId==TEXT("ENM-STN-003"))
                {
                    // The real Guard local eligibility may be true, but formal settlement is absent.
                    // Do not add003 to EnemyContent/ResolveDeath or fixed5coin source allocation.
                    if(!A.Enemy||B->RoomInstanceId!=S.CurrentRoomInstanceId||A.DeathReported||D
                        ||A.RewardClaimed&&!A.Dead)
                        return Fail(Why,TEXT("Current Guard contains unsupported formal settlement or premature eligibility"));
                }
                else if(!A.Enemy||!EnemyContent(A.ContentId)||B->RoomInstanceId!=S.CurrentRoomInstanceId
                    ||A.DeathReported!=A.RewardClaimed||A.DeathReported&&!A.Dead||bool(D)!=A.DeathReported
                    ||D&&(D->Death.RoomInstanceId!=A.RoomInstanceId||D->Death.ContentId!=A.ContentId))
                    return Fail(Why,TEXT("Current enemy death/source/claim facts disagree"));
            }
        }
        if(!HasPlayer)return Fail(Why,TEXT("Missing approved wallet actor"));
        for(const auto& B:W->ActorBindings)
        {
            if(!B.EntityId||BindingIds.Contains(B.EntityId)||!B.RoomInstanceId||B.RoomInstanceId>S.CurrentRoomInstanceId)
                return Fail(Why,TEXT("Ambiguous or future world actor binding"));
            BindingIds.Add(B.EntityId);
            if(B.EntityId==S.OwnerId)
            {if(B.ContentId!=TEXT("player"))return Fail(Why,TEXT("Wrong player binding content"));continue;}
            const bool CurrentUnsettledGuard=B.ContentId==TEXT("ENM-STN-003")&&B.RoomInstanceId==S.CurrentRoomInstanceId;
            if(!EnemyContent(B.ContentId)&&!CurrentUnsettledGuard)return Fail(Why,TEXT("Unsupported world actor content"));
            if(B.RoomInstanceId==S.CurrentRoomInstanceId)
            {if(!CurrentIds.Contains(B.EntityId))return Fail(Why,TEXT("Missing current world enemy"));continue;}
            const auto* R=S.RetiredEntities.FindByPredicate([&](const auto& X){return X.Actor.EntityId==B.EntityId;});
            if(!R||R->Actor.RoomInstanceId!=B.RoomInstanceId||R->Actor.ContentId!=B.ContentId)
                return Fail(Why,TEXT("Old world binding lost its exact tombstone"));
        }
        for(const auto& R:S.RetiredEntities)if(!BindingIds.Contains(R.Actor.EntityId)||CurrentIds.Contains(R.Actor.EntityId))
            return Fail(Why,TEXT("Retired actor is absent from history or resurrected as current"));
        for(const auto& D:S.Deaths)if(!BindingIds.Contains(D.Death.EntityId))
            return Fail(Why,TEXT("Death has no approved world identity"));
    }
    Why.Reset();return true;
}
}

bool FDungeonRunRewards::Begin(FGuid RunGuid,uint64 OwnerId,uint64 RoomInstanceId,int32 InitialCoins,FString& Diagnostic)
{
    if(State.Bound)return Fail(Diagnostic,TEXT("Reward owner already belongs to a Run"));
    if(RoomInstanceId!=1)return Fail(Diagnostic,TEXT("A new reward Run must begin in room1"));
    FS Candidate;Candidate.Bound=true;Candidate.RunGuid=RunGuid;Candidate.OwnerId=OwnerId;
    Candidate.CurrentRoomInstanceId=RoomInstanceId;Candidate.InitialCoins=InitialCoins;
    if(!Validate(Candidate,nullptr,Diagnostic))return false;State=MoveTemp(Candidate);return true;
}
FDungeonRunRewardDeathResult FDungeonRunRewards::ResolveDeath(const FDungeonRunRewardDeathRequest& Q,FString& Diagnostic)
{
    FDungeonRunRewardDeathResult R;R.Status=EDungeonRunRewardStatus::InvalidRequest;
    if(!State.Bound){R.Status=EDungeonRunRewardStatus::Unbound;Fail(Diagnostic,TEXT("No bound reward Run"));return R;}
    if(const auto* Old=Death(State,Q.EntityId))
    {
        if(!SameDeath(Old->Death,Q)){R.Status=EDungeonRunRewardStatus::Conflict;Fail(Diagnostic,TEXT("Death retry changed its original facts"));return R;}
        R.Status=EDungeonRunRewardStatus::Ok;R.Replayed=true;
        for(uint64 Id:Old->SourceIds)R.ObjectIds.Add(State.Sources[int32(Id-1)].ObjectId);Diagnostic.Reset();return R;
    }
    if(Q.RoomInstanceId!=State.CurrentRoomInstanceId){R.Status=EDungeonRunRewardStatus::WrongScope;Fail(Diagnostic,TEXT("Death belongs to another room"));return R;}
    FS Candidate=State;FDungeonRunRewardDeathFact D;D.Death=Q;
    const auto Add=[&](EDungeonRunRewardKind Kind,EDungeonRunRewardSourceKind SourceKind,FVector2D Offset,int32 Amount)
    {
        const uint64 SourceId=Candidate.NextSourceId++,ObjectId=Candidate.NextObjectId++;
        Candidate.Sources.Add({SourceId,ObjectId,Q.EntityId,Q.RoomInstanceId,SourceKind,Q.AtTime});
        FDungeonRunRewardObject O;O.ObjectId=ObjectId;O.SourceId=SourceId;O.RoomInstanceId=Q.RoomInstanceId;
        O.Kind=Kind;O.Position=Q.Position+Offset;O.ResolvedAmount=Amount;Candidate.Objects.Add(O);
        D.SourceIds.Add(SourceId);R.ObjectIds.Add(ObjectId);
    };
    if(Candidate.NextSourceId>uint64(MAX_int32)-3||Candidate.NextObjectId>uint64(MAX_int32)-3)
    {Fail(Diagnostic,TEXT("Reward ID storage domain exhausted"));return R;}
    Add(EDungeonRunRewardKind::Coin,EDungeonRunRewardSourceKind::EnemyCoin,{-18.,-12.},5);
    if(Q.FirstDeath)Add(EDungeonRunRewardKind::Potion,EDungeonRunRewardSourceKind::FirstDeathPotion,{25.,15.},30);
    const bool HasClear=State.Sources.ContainsByPredicate([&](const auto& X)
        {return X.RoomInstanceId==Q.RoomInstanceId&&X.Kind==EDungeonRunRewardSourceKind::RoomClearAxe;});
    if(Q.RoomCleared&&!HasClear)Add(EDungeonRunRewardKind::Axe,EDungeonRunRewardSourceKind::RoomClearAxe,{34.,14.},1);
    Candidate.Deaths.Add(MoveTemp(D));if(!Validate(Candidate,nullptr,Diagnostic)){R.ObjectIds.Reset();return R;}
    State=MoveTemp(Candidate);R.Status=EDungeonRunRewardStatus::Ok;return R;
}
FDungeonRunRewardCollectResult FDungeonRunRewards::CollectCoin(const FDungeonRunRewardCollectRequest& Q,FString& Diagnostic)
{
    FDungeonRunRewardCollectResult R;R.Status=EDungeonRunRewardStatus::InvalidRequest;
    if(!State.Bound){R.Status=EDungeonRunRewardStatus::Unbound;Fail(Diagnostic,TEXT("No bound reward Run"));return R;}
    if(const auto* Old=State.Collections.FindByPredicate([&](const auto& X){return X.Request.OperationId==Q.OperationId;}))
    {
        if(!SameCollect(Old->Request,Q)){R.Status=EDungeonRunRewardStatus::Conflict;Fail(Diagnostic,TEXT("Currency operation retry changed its original request"));return R;}
        Diagnostic.Reset();return Collected(*Old,true);
    }
    const auto* O=Object(State,Q.ObjectId);
    if(!O){R.Status=EDungeonRunRewardStatus::NotFound;Fail(Diagnostic,TEXT("Unknown resolved reward object"));return R;}
    if(Q.OwnerId!=State.OwnerId||Q.RoomInstanceId!=State.CurrentRoomInstanceId||O->RoomInstanceId!=Q.RoomInstanceId||Q.SourceId!=O->SourceId)
    {R.Status=EDungeonRunRewardStatus::WrongScope;Fail(Diagnostic,TEXT("Currency source/owner/room differs"));return R;}
    if(O->Retired){R.Status=EDungeonRunRewardStatus::Retired;Fail(Diagnostic,TEXT("Reward object left its room"));return R;}
    if(O->Consumed){R.Status=EDungeonRunRewardStatus::AlreadyConsumed;Fail(Diagnostic,TEXT("Reward object already consumed"));return R;}
    if(O->Kind!=EDungeonRunRewardKind::Coin){R.Status=EDungeonRunRewardStatus::Unsupported;Fail(Diagnostic,TEXT("Only actual currency collection is implemented"));return R;}
    if(Q.OperationId!=State.NextOperationId||Q.BeforeCoins!=Wallet(State)||Q.BeforeCoins>MAX_int32-O->ResolvedAmount)
    {R.Status=EDungeonRunRewardStatus::Conflict;Fail(Diagnostic,TEXT("Currency operation cursor/wallet changed or overflowed"));return R;}
    FS Candidate=State;auto& Changed=Candidate.Objects[int32(Q.ObjectId-1)];
    Changed.Consumed=true;Changed.CollectionOperationId=Q.OperationId;
    FDungeonRunRewardCollection Receipt{Q,Q.BeforeCoins+O->ResolvedAmount};Candidate.Collections.Add(Receipt);++Candidate.NextOperationId;
    if(!Validate(Candidate,nullptr,Diagnostic))return R;State=MoveTemp(Candidate);return Collected(Receipt,false);
}
bool FDungeonRunRewards::RetireRoom(const FDungeonRunRewardRoomExit& Q,const TArray<FDungeonRunRewardActorFact>& Actors,FString& Diagnostic)
{
    if(!State.Bound)return Fail(Diagnostic,TEXT("No bound reward Run"));
    if(const auto* Old=Exit(State,Q.RoomInstanceId))
    {
        if(Old->NextRoomInstanceId!=Q.NextRoomInstanceId||Old->AtTime!=Q.AtTime||Old->EntityIds!=Q.EntityIds||Old->ObjectIds!=Q.ObjectIds
            ||Actors.Num()!=Q.EntityIds.Num())return Fail(Diagnostic,TEXT("Room-exit retry changed its original facts"));
        TSet<uint64> RetryIds;
        for(const auto& A:Actors)
        {
            const auto* Original=State.RetiredEntities.FindByPredicate([&](const auto& X){return X.Actor.EntityId==A.EntityId;});
            if(RetryIds.Contains(A.EntityId)||!Q.EntityIds.Contains(A.EntityId)||!Original||!SameActor(Original->Actor,A))
                return Fail(Diagnostic,TEXT("Room-exit retry changed an actor tombstone"));
            RetryIds.Add(A.EntityId);
        }
        Diagnostic.Reset();return true;
    }
    if(Q.RoomInstanceId!=State.CurrentRoomInstanceId||Q.NextRoomInstanceId!=Q.RoomInstanceId+1||Actors.Num()!=Q.EntityIds.Num())
        return Fail(Diagnostic,TEXT("Room exit does not follow current scope"));
    FS Candidate=State;Candidate.RoomExits.Add(Q);Candidate.CurrentRoomInstanceId=Q.NextRoomInstanceId;
    for(const auto& A:Actors)
    {if(A.RoomInstanceId!=Q.RoomInstanceId)return Fail(Diagnostic,TEXT("Retired actor came from another room"));Candidate.RetiredEntities.Add({A,Q.AtTime});}
    for(auto& O:Candidate.Objects)if(O.RoomInstanceId==Q.RoomInstanceId){O.Retired=true;O.RetiredAt=Q.AtTime;}
    if(!Validate(Candidate,nullptr,Diagnostic))return false;State=MoveTemp(Candidate);return true;
}
FDungeonRunRewardSnapshot FDungeonRunRewards::Capture() const {return State;}
bool FDungeonRunRewards::Restore(const FDungeonRunRewardSnapshot& Saved,const FDungeonRunRewardValidationContext& Context,FString& Diagnostic)
{
    FS Candidate=Saved;if(!Validate(Candidate,&Context,Diagnostic))return false;State=MoveTemp(Candidate);return true;
}
