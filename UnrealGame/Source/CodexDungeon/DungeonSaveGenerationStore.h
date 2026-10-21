#pragma once

#include "CoreMinimal.h"

// D13 disk container only. No Actor/Run capture, gameplay restore, account
// mutation, random draw or success sound is performed by this primitive.
namespace DungeonSaveGenerationStore
{
enum class EStatus : uint8
{
    Ok, Empty, NotImplemented, InvalidRequest, ValidatorRejected, WriterBusy,
    IoFailure, RecoveryRequired, Conflict, InjectedFailure, UnsupportedPlatform
};
enum class ESlot : uint8 { A, B };
enum class EFaultPoint : uint8
{
    None, PartialBundleWrite, BundleWrittenBeforeFlush, BundleFlushed,
    BundleReadBack, BundleInstalled, PartialMarkerWrite, MarkerWrittenBeforeFlush,
    MarkerFlushed, MarkerReadBack, BeforeMarkerPublish, AfterMarkerPublish
};

struct FVersions
{
    FString Schema, ContentRules, Coordinates;
    bool operator==(const FVersions& Other) const
    { return Schema==Other.Schema && ContentRules==Other.ContentRules && Coordinates==Other.Coordinates; }
};

struct FGeneration
{
    FGuid ProfileId;
    uint64 GenerationId=0, ParentGeneration=0;
    FVersions Versions;
    FString BuildId;
    TOptional<double> RunSimulationTime;
    // Complete, caller-owned canonical UTF-8 JSON object, retained byte for byte.
    // The caller validates all account/Run/settings/journal cross-references.
    TArray<uint8> CanonicalPayload;
    uint64 RestoredFromGeneration=0;
};

// Pure validation only: do not mutate the live world, reenter this store, draw
// random numbers, publish a receipt, or perform a gameplay restore here.
using FPayloadValidator=TFunction<bool(const FGeneration&,FString&)>;

struct FLoadResult
{
    EStatus Status=EStatus::NotImplemented;
    FGeneration Generation;
    ESlot Slot=ESlot::A;
    uint64 ObservedHeadGeneration=0;
    FString Diagnostic;
};

struct FCommitResult
{
    EStatus Status=EStatus::NotImplemented;
    uint64 GenerationId=0;
    FString BundleSha256;
    uint32 BundleCrc32=0;
    int64 BundleByteLength=0;
    bool Replayed=false;
    // A lost acknowledgement must be resolved by inspecting the marker, never
    // by assuming an error means nothing was committed.
    bool PublicationMayHaveSucceeded=false;
    FString RecoveryArchiveDirectory, Diagnostic;
};

class CODEXDUNGEON_API FGenerationStore
{
public:
    FGenerationStore(const FString& ProfilesDirectory,const FGuid& ProfileId,const FVersions& SupportedVersions);
    ~FGenerationStore();
    FGenerationStore(const FGenerationStore&)=delete;
    FGenerationStore& operator=(const FGenerationStore&)=delete;

    EStatus OpenWriter();
    void CloseWriter();
    FString GetProfileDirectory() const;
    // Read-only selection: highest trustworthy published marker first, then
    // exact bytes and version checks. Never silently falls back to an old slot.
    FLoadResult Load(const FPayloadValidator& Validator) const;
    FCommitResult Commit(const FGeneration& Candidate,const FPayloadValidator& Validator,
        EFaultPoint Fault=EFaultPoint::None);
    // Explicit whole-generation rollback only. Archives originals before any
    // slot mutation; publishes a new generation greater than observed head.
    FCommitResult Recover(ESlot SelectedBackup,const FPayloadValidator& Validator,
        EFaultPoint Fault=EFaultPoint::None);
    static FString Sha256(const TArray<uint8>& Bytes);

private:
    struct FImpl;
    TUniquePtr<FImpl> Impl;
};
}
