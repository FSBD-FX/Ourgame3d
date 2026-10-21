#pragma once
#include "CoreMinimal.h"
#include "DungeonEquipmentRuntime.h"
#include "DungeonSceneObjects.h"
#include "DungeonWorldSnapshot.h"
#include "DungeonFighterSnapshot.h"
#include "DungeonRunRewards.h"
#include "DungeonRunExploration.h"
#include "DungeonActionAudioFeedback.h"

// Complete values for the presently implemented bound-development owners.
// This is not a canonical disk bundle, Account/Settings/Journal, or Continue.
enum class EDungeonRunScope:uint8 { Unsupported, BoundDevelopmentV1 };
enum class EDungeonRunGeometryKind:uint8 { Unsupported, FlatBoundsV1, SceneExplorationV1 };
struct FDungeonRunGeometrySnapshot
{
    uint32 Schema=1;
    // Only known geometry may be reconstructed from its validated Scene layout.
    // An external collision object must not be silently omitted from Capture.
    EDungeonRunGeometryKind Kind=EDungeonRunGeometryKind::Unsupported;
};
struct FDungeonRunPickupSnapshot
{
    FVector2D Position=FVector2D::ZeroVector;
    FName Kind=NAME_None;
    bool Consumed=false;
    FGuid RunGuid;
    uint64 ObjectId=0,SourceId=0,RoomInstanceId=0;
};
struct FDungeonRunWeaponAudioCursor
{
    uint64 OwnerId=0;
    FDungeonActionAudioWeaponCursor Cursor;
};
struct FDungeonRunStoneAudioSeed
{
    uint64 EntityId=0,NextEventId=1;
};
struct FDungeonRunAudioContinuation
{
    uint32 Schema=1;
    FGuid RunGuid;
    uint64 RoomInstanceId=0;
    // Producer continuation and new-consumer history seeds, never a sound queue.
    uint64 NextActionSequence=1,WorldHistoryThrough=0;
    TArray<FDungeonRunWeaponAudioCursor> WeaponCursors;
    TArray<FDungeonRunStoneAudioSeed> StoneSeeds;
    // No FDungeonActionAudioState::Records, playback receipts/counts, assets,
    // sound UObjects or local wall-clock/display epoch are serialized here.
};
struct FDungeonRunSnapshot
{
    uint32 Schema=1;
    EDungeonRunScope Scope=EDungeonRunScope::Unsupported;
    FGuid RunGuid;
    uint64 OwnerId=0,RoomInstanceId=0;
    int32 RoomNumber=0;
    double SimulationTime=0.,LastStoneWakeStartedAt=-1.;
    bool RoomCleared=false,GameOver=false,WaitingForStart=false;
    bool SceneCommitRequested=false,SceneEquipmentTargetLost=false;
    FString LastMessage;
    uint64 SceneEncounterEntityId=0;
    FDungeonRunGeometrySnapshot Geometry;
    FDungeonEquipmentRuntimeSnapshot Equipment;
    FDungeonSceneObjectsSnapshot Scene;
    FDungeonWeaponWorldSnapshot WeaponWorld;
    // Player first, then the actual current Enemies order, including dead actors.
    // Historical World bindings/tombstones are not respawn requests.
    TArray<FDungeonFighterOwnerSnapshot> Fighters;
    TArray<uint64> EnemyOrder;
    FDungeonRunRewardSnapshot Rewards;
    // Full current physical projection order, including consumed objects.
    TArray<FDungeonRunPickupSnapshot> Pickups;
    FDungeonRunExplorationSnapshot Exploration;
    FDungeonRunAudioContinuation Audio;
};
