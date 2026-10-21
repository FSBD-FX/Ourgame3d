#pragma once
#include "CoreMinimal.h"
#include "DungeonRunAggregate.h"

class AActor;
class ADungeonFighter;
class ADungeonGameMode;
class FDungeonRunInstaller;

// Technical process state, separate from saved WaitingForStart/GameOver.
enum class EDungeonRunInstallGate:uint8 { Open, Preparing, AwaitExplicitContinue, PristineBootstrap };

// Process-only staged resources. The owning PreparedRun keeps this group private;
// saved values stay sealed and are never exposed as writable payload fields.
// GameMode is the sole grouped root-swap implementation.
struct FDungeonRunInstallGroup
{
    TWeakObjectPtr<ADungeonGameMode> Game;
    uint64 Token=0;
    FDungeonValidatedRun Validated;
    TUniquePtr<FDungeonEquipmentRuntime> Equipment;
    TUniquePtr<FDungeonSceneObjects> Scene;
    TUniquePtr<FDungeonRunRewards> Rewards;
    TUniquePtr<FDungeonRunExploration> Exploration;
    FDungeonWeaponWorldState WeaponWorld;
    TArray<TObjectPtr<ADungeonFighter>> Fighters; // saved player first, exact enemy order
    TArray<TWeakObjectPtr<AActor>> GeometryActors;
    TArray<TWeakObjectPtr<AActor>> StagedActors; // RAII owns these until committed
    TMap<TWeakObjectPtr<ADungeonFighter>,uint64> EntityIds;
    FDungeonActionAudioState ActionAudio;
    TMap<uint64,FDungeonActionAudioWeaponCursor> AudioCursors;
    bool Committed=false,PristineOrigin=false;
    const FDungeonRunSnapshot* SavedValues() const {return Validated.Get();}
};

class CODEXDUNGEON_API FDungeonPreparedRun
{
public:
    FDungeonPreparedRun();
    ~FDungeonPreparedRun();
    FDungeonPreparedRun(FDungeonPreparedRun&& Other);
    FDungeonPreparedRun& operator=(FDungeonPreparedRun&& Other);
    FDungeonPreparedRun(const FDungeonPreparedRun&)=delete;
    FDungeonPreparedRun& operator=(const FDungeonPreparedRun&)=delete;
    bool IsReady() const;
    const FDungeonRunSnapshot* GetSavedSnapshot() const;
    const TArray<TWeakObjectPtr<AActor>>& GetStagedActors() const;
private:
    friend class FDungeonRunInstaller;
    friend class ADungeonGameMode;
    TUniquePtr<FDungeonRunInstallGroup> Group;
};

class CODEXDUNGEON_API FDungeonRunInstaller
{
public:
    // Synchronous game-thread preparation at a completed boundary. Failure leaves
    // Out and the old authoritative Run intact; no reset/replay/new logical IDs.
    static bool Prepare(ADungeonGameMode& Game,const FDungeonValidatedRun& Saved,
        FDungeonPreparedRun& Out,FString& Diagnostic);
    // Explicit no-Run startup seam. It must verify the pristine InitGame origin
    // and preserve a closed no-Run gate on failure/RAII release; normal Prepare
    // continues to require Capture of its already valid target Run.
    static bool PreparePristine(ADungeonGameMode& Game,const FDungeonValidatedRun& Saved,
        FDungeonPreparedRun& Out,FString& Diagnostic);
    // Consume only a matching sealed group through GameMode's closed-gate swap.
    // Success remains paused awaiting neutral controls and a fresh real Enter.
    static bool Install(ADungeonGameMode& Game,FDungeonPreparedRun& Prepared,FString& Diagnostic);
private:
    friend class FDungeonPreparedRun;
    static void Release(FDungeonPreparedRun& Prepared);
    // Only the two typed public entry points may reach common staging, after
    // their distinct existing-Run Capture or pristine-origin precondition.
    static bool PrepareValidated(ADungeonGameMode& Game,const FDungeonValidatedRun& Sealed,
        FDungeonPreparedRun& Out,bool Pristine,FString& Diagnostic);
};
