#pragma once
#include "DungeonRunSaveAdapter.h"
// Explicit current-owner RunV2 capability. This is a separate disk namespace,
// not a V1 migration and not a complete account/settings/journal Profile.
namespace DungeonRunSaveAdapterV2
{
namespace Store=DungeonSaveGenerationStore;
inline constexpr TCHAR DirectoryName[]=TEXT("BoundRunOnly-v2");
inline const Store::FVersions CurrentVersions{
    TEXT("bound-run-generation-v2"),TEXT("bound-development-guard-v2"),TEXT("world-cm-v1")};
enum class EScope:uint8 { Unsupported,BoundDevelopmentRunV2 };
struct FReadContext
{
    EScope Scope=EScope::BoundDevelopmentRunV2;
    FString ProfilesDirectory;
    FGuid ProfileId,ExpectedRunGuid;
    uint64 ExpectedOwnerId=0;
};
struct FWriteRequest
{
    FReadContext Context;
    FGuid RunGuid;
    uint64 OwnerId=0,GenerationId=0,ParentGeneration=0;
    FString BuildId;
};
// Shared value result types contain no version selection or live state.
using FLoadedRun=DungeonRunSaveAdapter::FLoadedRun;
using FReadResult=DungeonRunSaveAdapter::FReadResult;
CODEXDUNGEON_API bool MakeGeneration(const FDungeonRunSnapshot& Saved,
    const FWriteRequest& Request,Store::FGeneration& Out,FString& Diagnostic);
CODEXDUNGEON_API bool ValidateGeneration(const Store::FGeneration& Generation,
    const FReadContext& Context,FDungeonValidatedRun& Out,FString& Diagnostic);
CODEXDUNGEON_API Store::FCommitResult Commit(Store::FGenerationStore& Disk,
    const FDungeonRunSnapshot& Saved,const FWriteRequest& Request,
    Store::EFaultPoint Fault=Store::EFaultPoint::None);
CODEXDUNGEON_API FReadResult Load(const Store::FGenerationStore& Disk,
    const FReadContext& Context,FLoadedRun& Out);
CODEXDUNGEON_API FReadResult LoadAndPrepare(ADungeonGameMode& Game,
    const Store::FGenerationStore& Disk,const FReadContext& Context,
    FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded);
// Explicit native InitGame no-Run origin only; no provisional BeginRun/reset.
CODEXDUNGEON_API FReadResult LoadAndPreparePristine(ADungeonGameMode& Game,
    const Store::FGenerationStore& Disk,const FReadContext& Context,
    FDungeonPreparedRun& OutPrepared,FLoadedRun& OutLoaded);
}
