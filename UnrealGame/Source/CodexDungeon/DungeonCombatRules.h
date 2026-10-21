#pragma once

#include <cmath>

namespace DungeonCombatRules
{
    inline bool CanHit(float DeltaX, float DeltaY, float Facing, float Range,
        float DepthTolerance, float AttackerHeight, float TargetHeight)
    {
        const float ForwardDistance = DeltaX * Facing;
        return ForwardDistance >= 0.f && ForwardDistance <= Range
            && std::abs(DeltaY) <= DepthTolerance
            && std::abs(TargetHeight - AttackerHeight) <= 65.f;
    }

    inline float RestoreHealth(float Health, float MaxHealth, float Amount)
    {
        return std::fmin(MaxHealth, Health + std::fmax(0.f, Amount));
    }
}
