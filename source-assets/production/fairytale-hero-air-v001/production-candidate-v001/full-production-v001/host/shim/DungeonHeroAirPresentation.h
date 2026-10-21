#pragma once
#include "CoreMinimal.h"

// A completed real hero-owner read, never a new jump clock, event or save schema.
// On failure QueryHeroNonAttackAir leaves every caller-owned field unchanged.
struct FDungeonHeroAirSample
{
 bool Valid=false;
 FGuid RunGuid;
 uint64 OwnerId=0,RoomInstanceId=0,PresentationEpoch=0;
 double NativeTime=0.;
 FVector2D GroundPosition=FVector2D::ZeroVector;
 float Facing=0.f,JumpHeight=0.f,VerticalVelocity=0.f,LandingVisualAge=.12f;
};
