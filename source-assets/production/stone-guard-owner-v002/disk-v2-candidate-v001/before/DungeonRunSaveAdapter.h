#pragma once
#include "DungeonRunSnapshotCodec.h"
#include "DungeonRunInstaller.h"
#include "DungeonSaveGenerationStore.h"

// Explicitly isolated current-owner save namespace. This is NOT a complete
// D13 Account/activeRun/settings/read-history/journal profile bundle. Missing
// owners cannot be invented as empty JSON. Full-profile scope is refused.
namespace DungeonRunSaveAdapter
{
namespace Store=DungeonSaveGenerationStore;
inline constexpr TCHAR DirectoryName[]=TEXT("BoundRunOnly-v1");
inline const Store::FVersions CurrentVersions{
    TEXT("bound-run-generation-v1"),TEXT("bound-development-v1"),TEXT("world-cm-v1")};
enum class EScope:uint8 { Unsupported,BoundDevelopmentRunV1,CompleteProfileV1 };
struct FReadContext
{
    EScope Scope=EScope::BoundDevelopmentRunV1;
    // Absolute normalized directory ending in DirectoryName. Its ProfileGUID
    // child must equal Store.GetProfileDirectory(); never target full profiles.
    FString ProfilesDirectory;
    FGuid ProfileId;
    // Optional caller identity expectations; a pristine reader may not know
    // the Run yet. Header/envelope/Codec root still bind each other exactly.
    FGuid ExpectedRunGuid;
    uint64 ExpectedOwnerId=0;
};
struct FWriteRequest
{
    FReadContext Context;
    FGuid RunGuid;
    uint64 OwnerId=0,GenerationId=0,ParentGeneration=0;
    FString BuildId;
};
struct FLoadedRun
{
    Store::FGeneration Generation;
    FDungeonValidatedRun Run;
    Store::ESlot Slot=Store::ESlot::A;
    uint64 ObservedHeadGeneration=0;
};
struct FReadResult
{
    Store::EStatus Status=Store::EStatus::NotImplemented;
    Store::ESlot Slot=Store::ESlot::A;
    uint64 ObservedHeadGeneration=0;
    FString Diagnostic;
};

// Canonical run-only envelope includes exact header Profile/Generation/Parent/
// Build/versions, original Codec object, root RunGuid and IEEE simulation time.
// No live capture/clock/RNG mutation. Failure preserves Out byte for byte.
CODEXDUNGEON_API bool MakeGeneration(const FDungeonRunSnapshot& Saved,
    const FWriteRequest& Request,Store::FGeneration& Out,FString& Diagnostic);
// Pure mandatory Store validator. Entire header/envelope/Codec references and
// caller identity/version/scope must pass before sealed Out is replaced.
CODEXDUNGEON_API bool ValidateGeneration(const Store::FGeneration& Generation,
    const FReadContext& Context,FDungeonValidatedRun& Out,FString& Diagnostic);
// Caller owns the opened writer lease. Commit never substitutes a permissive
// callback or retries under new IDs; a lost published acknowledgement remains
// PublicationMayHaveSucceeded and is resolved through the actual marker/head.
CODEXDUNGEON_API Store::FCommitResult Commit(Store::FGenerationStore& Disk,
    const FDungeonRunSnapshot& Saved,const FWriteRequest& Request,
    Store::EFaultPoint Fault=Store::EFaultPoint::None);
// Highest head is selected/validated as a whole; no semantic fallback to old A.
// On all failures Out remains untouched, with observed head in the result.
CODEXDUNGEON_API FReadResult Load(const Store::FGenerationStore& Disk,
    const FReadContext& Context,FLoadedRun& Out);
// Load then prepare independently through existing atomic Installer. Success
// leaves Game Preparing; caller explicitly Install, neutralize and fresh Enter.
// This currently needs an existing valid target Run. Pristine bootstrap and
// real new-process/menu integration are separate required root work.
CODEXDUNGEON_API FReadResult LoadAndPrepare(ADungeonGameMode& Game,
    const Store::FGenerationStore& Disk,const FReadContext& Context,
    FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded);
}
