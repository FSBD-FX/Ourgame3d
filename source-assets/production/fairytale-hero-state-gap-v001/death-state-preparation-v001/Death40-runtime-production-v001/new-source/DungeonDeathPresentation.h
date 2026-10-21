#pragma once
#include "CoreMinimal.h"

// Actual terminal display facts only. No new timer, event, saved field or owner.
// A failed query leaves every caller field unchanged.
struct FDungeonDeathPresentationSample
{
 bool Active=false,Dead=false,DeathReported=false;
 float Health=0.f,Elapsed=0.f;
 FString AnimationName;
};
