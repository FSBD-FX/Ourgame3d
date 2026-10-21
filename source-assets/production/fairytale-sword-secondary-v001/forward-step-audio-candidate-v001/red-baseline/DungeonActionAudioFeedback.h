#pragma once
#include "CoreMinimal.h"
#include "DungeonWeaponActions.h"

// Transient presentation facts only. This journal is not serialized D13 state
// and never starts an action, changes its deadline, or owns an inventory fact.
struct FDungeonActionAudioRecord
{
    uint64 Sequence = 0;
    FString Cue;
    double AtTime = 0.0;
    FGuid RunGuid;
    uint64 RoomInstanceId = 0, OwnerId = 0, ActionId = 0, InstanceId = 0;
    uint64 OperationId = 0, Revision = 0;
};

struct FDungeonActionAudioState
{
    FGuid RunGuid;
    uint64 RoomInstanceId = 0, NextSequence = 1;
    TArray<FDungeonActionAudioRecord> Records;
};

// Incremental adapter cursor. A new attachment seeds already elapsed phases;
// these transient observations never restore or mutate the weapon kernel.
struct FDungeonActionAudioWeaponCursor
{
    bool Attached = false, DrawObserved = false, InsertObserved = false;
    uint64 LastEventId = 0;
    std::size_t RuntimeReceiptCount = 0;
    double LastObservedTime = 0.0;
    DungeonWeaponActions::FAction Reload;
};

namespace DungeonHeroForwardStepAudioV001
{
inline bool Eligible(const DungeonWeaponActions::FEvent&,const DungeonWeaponActions::FAction&,uint64,uint64,bool,double,FVector2D,FVector2D){return false;}
}
