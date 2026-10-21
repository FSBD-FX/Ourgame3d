#pragma once
#include "CoreMinimal.h"
#include "DungeonWorldProjectiles.h"
#include "DungeonFirstBatchGuardRoom.h"

// Bound-development reward facts only. This is not formal D08 allocation,
// equipment loot, account progression, a disk payload or completed Run Continue.
enum class EDungeonRunRewardKind:uint8 { Coin, Potion, Axe };
enum class EDungeonRunRewardSourceKind:uint8 { EnemyCoin, FirstDeathPotion, RoomClearAxe };
enum class EDungeonRunRewardStatus:uint8
{
    Ok, NotImplemented, Unbound, InvalidRequest, WrongScope, NotFound,
    Retired, AlreadyConsumed, Unsupported, AdmissionRejected, Conflict
};
struct FDungeonRunRewardActorFact
{
    uint64 EntityId=0,RoomInstanceId=0;
    FString ContentId;
    bool Enemy=false,Dead=false,DeathReported=false,RewardClaimed=false;
};
struct FDungeonRunRewardDeathRequest
{
    uint64 EntityId=0,RoomInstanceId=0;
    FString ContentId;
    double AtTime=0.;
    FVector2D Position=FVector2D::ZeroVector;
    // RoomCleared records the real last-enemy decision. A later last-enemy
    // death in this room still records true but cannot allocate a second axe.
    bool FirstDeath=false,RoomCleared=false;
};
struct FDungeonRunRewardDeathFact
{
    FDungeonRunRewardDeathRequest Death;
    TArray<uint64> SourceIds;
};
struct FDungeonRunRewardSource
{
    uint64 SourceId=0,ObjectId=0,EntityId=0,RoomInstanceId=0;
    EDungeonRunRewardSourceKind Kind=EDungeonRunRewardSourceKind::EnemyCoin;
    double AtTime=0.;
};
struct FDungeonRunRewardObject
{
    uint64 ObjectId=0,SourceId=0,RoomInstanceId=0;
    EDungeonRunRewardKind Kind=EDungeonRunRewardKind::Coin;
    FVector2D Position=FVector2D::ZeroVector;
    int32 ResolvedAmount=0;
    // Orthogonal facts: an already collected object can later leave its room.
    bool Consumed=false,Retired=false;
    uint64 CollectionOperationId=0;
    double RetiredAt=0.;
};
struct FDungeonRunRewardCollectRequest
{
    uint64 OperationId=0,ObjectId=0,SourceId=0,OwnerId=0,RoomInstanceId=0;
    double AtTime=0.;
    int32 BeforeCoins=0;
};
struct FDungeonRunRewardCollection
{
    FDungeonRunRewardCollectRequest Request;
    int32 AfterCoins=0;
};
struct FDungeonRunRewardRetiredEntity
{
    FDungeonRunRewardActorFact Actor;
    double RetiredAt=0.;
};
struct FDungeonRunRewardRoomExit
{
    uint64 RoomInstanceId=0,NextRoomInstanceId=0;
    double AtTime=0.;
    TArray<uint64> EntityIds,ObjectIds;
};
struct FDungeonRunRewardSnapshot
{
    uint32 Schema=1;
    bool Bound=false;
    FGuid RunGuid;
    uint64 OwnerId=0,CurrentRoomInstanceId=0;
    uint64 NextSourceId=1,NextObjectId=1,NextOperationId=1;
    int32 InitialCoins=0;
    TArray<FDungeonRunRewardDeathFact> Deaths;
    TArray<FDungeonRunRewardSource> Sources;
    TArray<FDungeonRunRewardObject> Objects;
    TArray<FDungeonRunRewardCollection> Collections;
    TArray<FDungeonRunRewardRetiredEntity> RetiredEntities;
    TArray<FDungeonRunRewardRoomExit> RoomExits;
    TArray<FDungeonFirstBatchGuardRoomView> RoomPlans; // Schema2 only; legacy schema1 stays empty. 
};
struct FDungeonRunRewardDeathResult
{
    EDungeonRunRewardStatus Status=EDungeonRunRewardStatus::NotImplemented;
    bool Replayed=false;
    TArray<uint64> ObjectIds;
    bool Ok() const {return Status==EDungeonRunRewardStatus::Ok;}
};
struct FDungeonRunRewardCollectResult
{
    EDungeonRunRewardStatus Status=EDungeonRunRewardStatus::NotImplemented;
    bool Replayed=false;
    uint64 OperationId=0,ObjectId=0;
    int32 BeforeCoins=0,AfterCoins=0;
    bool Ok() const {return Status==EDungeonRunRewardStatus::Ok;}
};
struct FDungeonRunRewardValidationContext
{
    FGuid RunGuid;
    uint64 OwnerId=0,RoomInstanceId=0;
    double SimulationTime=0.;
    int32 PlayerCoins=0;
    const FDungeonWeaponWorldState* WeaponWorld=nullptr;
    TArray<FDungeonRunRewardActorFact> CurrentActors;
};
class CODEXDUNGEON_API FDungeonRunRewards
{
public:
    bool Begin(FGuid RunGuid,uint64 OwnerId,uint64 RoomInstanceId,int32 InitialCoins,FString& Diagnostic);
    bool BeginFirstBatchGuardPlan(uint64 Seed,uint64 InitialEntity,double AtTime,FString& Diagnostic);
    bool CommitFirstBatchGuardPlan(const FDungeonFirstBatchGuardRoomView& Plan,FString& Diagnostic);
    FDungeonRunRewardDeathResult ResolveDeath(const FDungeonRunRewardDeathRequest&,FString& Diagnostic);
    // GameMode checks real survival/ground/range/LOS, with no idle/attack gate.
    // An exact committed request may be read again after death/room exit.
    FDungeonRunRewardCollectResult CollectCoin(const FDungeonRunRewardCollectRequest&,FString& Diagnostic);
    bool RetireRoom(const FDungeonRunRewardRoomExit&,const TArray<FDungeonRunRewardActorFact>& Actors,FString& Diagnostic);
    FDungeonRunRewardSnapshot Capture() const;
    bool Restore(const FDungeonRunRewardSnapshot&,const FDungeonRunRewardValidationContext&,FString& Diagnostic);
private:
    FDungeonRunRewardSnapshot State;
};
