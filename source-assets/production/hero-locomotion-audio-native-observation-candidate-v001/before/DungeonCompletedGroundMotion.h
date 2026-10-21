#pragma once
#include "CoreMinimal.h"

// Read-only native movement witness. This is not an Owner save value: pending
// distance must be consumed at Actions or Capture must reject its open boundary.
struct FDungeonCompletedGroundMotion
{
    bool Published=false, Grounded=false, OrdinaryEligible=false, HadMoveIntent=false;
    FGuid RunGuid;
    uint64 OwnerId=0, RoomInstanceId=0;
    double FromTime=0.,ToTime=0.,AcceptedDistance=0.,WalkDistance=0.;
    FVector2D From=FVector2D::ZeroVector,To=FVector2D::ZeroVector;
};
