#pragma once

#include "CoreMinimal.h"

class UWorld;
class AActor;
class UPrimitiveComponent;

namespace DungeonNativeGeometryGuards
{
// A narrow native rendering-only exception, not a generic no-body exemption.
// Read-only: never changes registration, collision, physics or actor ownership.
// Shared by pristine eligibility and normal Aggregate geometry capture. Only
// the exact native sole-root Debugger renderer with no body/setup/weld qualifies.
CODEXDUNGEON_API bool IsNativeGameplayDebuggerDrawOnly(const UWorld* World,
    const AActor* Actor,const UPrimitiveComponent* Component);
}
