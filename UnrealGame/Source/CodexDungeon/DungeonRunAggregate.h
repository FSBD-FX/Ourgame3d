#pragma once
#include "DungeonRunSnapshot.h"

class ADungeonGameMode;
class FDungeonRunAggregate;

// A caller cannot forge a validation bit or mutate the installed value.
// Preparation/installation will consume this sealed result in a later slice.
class CODEXDUNGEON_API FDungeonValidatedRun
{
public:
    bool IsValid() const {return Data.IsValid();}
    const FDungeonRunSnapshot* Get() const {return Data.Get();}
private:
    friend class FDungeonRunAggregate;
    TSharedPtr<const FDungeonRunSnapshot> Data;
};
class CODEXDUNGEON_API FDungeonRunAggregate
{
public:
    // Read a single completed boundary; failures leave Out exactly unchanged.
    static bool Capture(const ADungeonGameMode& Game,FDungeonRunSnapshot& Out,FString& Diagnostic);
    // Pure all-owner/cross-reference validation; no actor spawn, clock step,
    // RNG draw, journal replay, live source mutation, or partial Out replacement.
    static bool Validate(const FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Out,FString& Diagnostic);
};
