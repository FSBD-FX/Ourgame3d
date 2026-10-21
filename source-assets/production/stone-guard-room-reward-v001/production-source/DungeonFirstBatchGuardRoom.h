#pragma once
#include "CoreMinimal.h"

// Explicit native Bridge slice, never the unimplemented six-slot RSEQ-001.
// Persisted through Rewards schema2 in bound-run-v2; schema1 has no plans.
enum class EDungeonGuardRoomSlotStage:uint8 { Future, Warning, Materialized, Dead };
struct FDungeonGuardRoomSlot
{
 FString SlotId,ContentId;
 uint32 Group=0;
 int32 Weight=0,Coins=0;
 uint64 EntityId=0,CoinObjectId=0;
 EDungeonGuardRoomSlotStage Stage=EDungeonGuardRoomSlotStage::Future;
 FVector2D SpawnPosition=FVector2D::ZeroVector;
 double WarningAt=-1.,MaterializedAt=-1.,DeadAt=-1.,RetryAt=-1.;
 uint32 AnchorAttempt=0;
};
struct FDungeonFirstBatchGuardRoomView
{
 uint32 Version=1;
 FGuid RunGuid;
 uint64 RoomInstanceId=0,Seed=0;
 FString TemplateId,GoldSourceId;
 int32 GoldBudget=0;
 double EnteredAt=0.,OrientationUntil=0.,ClearAt=-1.;
 TArray<FDungeonGuardRoomSlot> Slots;
};
