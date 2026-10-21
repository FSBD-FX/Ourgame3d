#pragma once
#include "CoreMinimal.h"

// Read-only actual Fighter facts. No independent timer, saved schema, event or owner.
// Query failure must leave every caller field unchanged.
struct FDungeonHurtPresentationSample
{
 bool Active=false;
 float Elapsed=0.f;
 float Remaining=0.f;
};
