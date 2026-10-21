#pragma once
#include "DungeonRunRewards.h"
namespace DungeonGuardRoomRewardsV2
{
inline constexpr uint32 AnchorCount=35;
inline constexpr uint32 MaxAnchorAttempts=AnchorCount*12;
FDungeonFirstBatchGuardRoomView Plan(FGuid Run,uint64 Room,uint64 Seed,double EnteredAt);
FVector2D Anchor(uint64 Seed,int32 Slot,uint32 Attempt);
bool Validate(const FDungeonRunRewardSnapshot&,const FDungeonRunRewardValidationContext*,FString&);
FDungeonRunRewardDeathResult ResolveDeath(FDungeonRunRewardSnapshot&,const FDungeonRunRewardDeathRequest&,FString&);
}
