#pragma once
#include "CoreMinimal.h"
#include "DungeonFairytaleGuardFullPoseV003.h"
// Read-only completed Guard producer facts. No clock, reset, save schema or
// historical sweep cause is introduced. Failure must preserve caller Out.
struct FDungeonGuardMoveSample
{
 bool Valid=false,BlockKnown=false;
 uint64 EntityId=0,AcceptedPathOwnerId=0,RoomInstanceId=0,PresentationEpoch=0,MovementEventId=0;
 FGuid RunGuid;
 FString EnemyContentId;
 double SampleTime=0.,MovementAtTime=0.,AcceptedDistance=0.,CurrentAcceptedDistance=0.;
 FVector2D GroundPosition=FVector2D::ZeroVector,MovementFrom=FVector2D::ZeroVector,MovementTo=FVector2D::ZeroVector,MovementDirection=FVector2D::ZeroVector;
 int32 Facing=0;
 DungeonFairytaleGuardFullV003::FSelection NativeSelection;
};
