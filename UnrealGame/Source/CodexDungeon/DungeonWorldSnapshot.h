#pragma once
#include "DungeonWorldProjectiles.h"

// Complete value snapshot of the existing weapon-world owner, not a disk format.
struct FDungeonWeaponWorldSnapshot
{
    uint32 Schema=1;
    FDungeonWeaponWorldState State;
};
struct FDungeonWeaponWorldRestoreContext
{
    FGuid RunGuid;
    uint64 RoomInstanceId=0,OwnerId=0;
    double SimulationTime=0.;
    // Saved validated owner state, never the new actor's default action kernel.
    const DungeonWeaponActions::FState* PlayerActions=nullptr;
};
namespace DungeonWorldSnapshot
{
CODEXDUNGEON_API FDungeonWeaponWorldSnapshot Capture(const FDungeonWeaponWorldState& State);
// Validate an independent complete value candidate before one output install.
// Actor maps, damage-batch admission and durable publication belong to aggregate.
CODEXDUNGEON_API bool Restore(const FDungeonWeaponWorldSnapshot& Snapshot,
    const FDungeonWeaponWorldRestoreContext& Context,FDungeonWeaponWorldState& Out,FString& Diagnostic);
}
