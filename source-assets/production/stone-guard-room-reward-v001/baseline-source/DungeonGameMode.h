#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "DungeonStoneKnightDriver.h"
#include "DungeonWeaponActions.h"
#include "DungeonDodge.h"
#include "DungeonEquipmentRuntime.h"
#include "DungeonWorldProjectiles.h"
#include "DungeonSceneObjects.h"
#include "DungeonActionAudioFeedback.h"
#include "DungeonRunRewards.h"
#include "DungeonRunExploration.h"
#include "DungeonGameMode.generated.h"

class ADungeonFighter;
struct FDungeonKnightFrame;
struct FDungeonKnightBody;
struct FDungeonKnightBatch;
struct FDungeonBatBatch;
struct FDungeonGuardBatch;
struct FDungeonRunSnapshot;
class FDungeonRunAggregate;
class FDungeonRunInstaller;
struct FDungeonRunInstallGroup;
enum class EDungeonRunInstallGate : uint8;

USTRUCT(BlueprintType)
struct CODEXDUNGEON_API FDungeonPickup
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly) FVector2D Position = FVector2D::ZeroVector;
    UPROPERTY(BlueprintReadOnly) FName Kind = NAME_None;
    UPROPERTY(BlueprintReadOnly) bool bConsumed = false;
    // Native stable identity assigned by normal bound death resolution, never Capture.
    FGuid RunGuid;
    uint64 ObjectId=0,SourceId=0,RoomInstanceId=0;
};

UCLASS()
class CODEXDUNGEON_API ADungeonGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ADungeonGameMode();
    virtual void InitGame(const FString& MapName,const FString& Options,FString& ErrorMessage) override;
    virtual void StartPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(BlueprintReadOnly, Category="Dungeon") TObjectPtr<ADungeonFighter> PlayerFighter;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") TArray<TObjectPtr<ADungeonFighter>> Enemies;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") TArray<FDungeonPickup> Pickups;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") int32 RoomNumber = 1;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") bool bRoomCleared = false;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") bool bGameOver = false;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") bool bWaitingForStart = true;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString LastMessage;

    UFUNCTION(BlueprintPure, Category="Dungeon") ADungeonFighter* GetPlayerFighter() const;
    ADungeonFighter* SpawnStoneBat(FVector2D GroundPosition);
    ADungeonFighter* SpawnStoneGuard(FVector2D GroundPosition);
    UFUNCTION(BlueprintCallable, Category="Dungeon") void RestartRun();
    UFUNCTION(BlueprintCallable, Category="Dungeon") void TryAttack(ADungeonFighter* Attacker);
    UFUNCTION(BlueprintCallable, Category="Dungeon") void TryInteract();
    UFUNCTION(BlueprintCallable, Category="Dungeon") void OnFighterDied(ADungeonFighter* Fighter);
    void ResolveAttack(ADungeonFighter* Attacker);
    double GetSimulationTime() const { return SimulationTime; }
    uint64 GetRunRestartSerial() const { return RunRestartSerial; }
    bool BeginEquipmentRun(EDungeonEquipmentRunConfig Config = EDungeonEquipmentRunConfig::IntegrationPreview, uint64 CombatSeed = 1);
    bool BeginManualWeaponPreview(); // Explicit QA entry; duplicate calls in the same manual Run are observations.
    bool BeginSceneExplorationPreview(); // Explicit development layout, not a formal D07/D08/D13 entry.
    const FDungeonSceneRoomView& GetSceneRoomView() const;
    const FDungeonSceneRoomView* FindSceneRoomView(uint64 RoomInstanceId) const;
    const FDungeonSceneInteractionView& GetSceneInteractionView() const;
    bool ConfirmSceneInteraction(bool FreshPress = true);
    void CancelSceneInteraction();
    FDungeonEquipmentRegistration RegisterEquipmentSource(const FString& LogicalKey,
        const DungeonEquipmentInventory::FItem& Prototype, FVector2D Position, bool Settled = true);
    const FDungeonEquipmentView& GetEquipmentView() const;
    const TArray<FDungeonEquipmentSourceView>& GetEquipmentSources() const;
    const DungeonEquipmentInventory::FState* GetEquipmentInventoryState() const;
    FDungeonEquipmentRuntimeSnapshot CaptureEquipmentSnapshot() const;
    FDungeonRunRewardSnapshot CaptureRunRewardsSnapshot() const;
    FDungeonRunExplorationSnapshot CaptureRunExplorationSnapshot() const;
    const DungeonExploration::FExploration* GetCurrentRunExplorationView() const;
    bool CaptureRunSnapshot(FDungeonRunSnapshot& Out,FString& Why) const;
    // Separate process-only no-Run origin, never inferred by resetting owners.
    // Opt-in URL: DungeonContinuePristine. A successful install consumes it.
    bool IsPristineContinueBootstrap(FString& Why) const;
    EDungeonRunInstallGate GetRunInstallGate() const { return RunInstallGate; }
    bool IsRunInstallGated() const { return uint8(RunInstallGate)!=0; }
    uint64 GetRunPresentationEpoch() const { return RunPresentationEpoch; }
    bool RequestExplicitContinue(FString& Why);
    FDungeonRunRewardCollectResult TryCollectRunReward(uint64 ObjectId,uint64 OperationId=0);
    bool SelectEquipmentSource(uint64 SourceId);
    bool CycleEquipmentTarget();
    bool TryInteractEquipment();
    bool ConfirmEquipmentSlot(int32 Slot, bool FreshPress = true);
    void CancelEquipmentSelection();
    bool TrySwitchEquipment();
    const FDungeonWeaponWorldState& GetWeaponWorldState() const { return WeaponWorld; }
    const FDungeonActionAudioState& GetActionAudioState() const { return ActionAudioState; }
    bool IsFairytaleLookdevPreview() const { return bFairytaleLookdevPreview; }
    int32 GetFairytaleLookdevFacing() const { return FairytaleLookdevFacing; }
    double GetFairytaleLookdevEpoch() const { return FairytaleLookdevEpoch; }

private:
    friend class FDungeonRunAggregate;
    friend class FDungeonRunInstaller;
    friend class ADungeonFighter;
    EDungeonRunInstallGate RunInstallGate=static_cast<EDungeonRunInstallGate>(0);
    uint64 NextRunInstallToken=1,ActiveRunInstallToken=0,RunPresentationEpoch=0;
    bool RunInstallNeutralArmed=false,RunInstallPreviousEnter=false,SuppressRestoreContinueEnter=false;
    bool bRunInitGameSeen=false,bPristineContinueOrigin=false,bPristineContinueConsumed=false;
    bool ActivePreparationPristine=false;
    bool BeginRunInstallPreparation(uint64& Token,FString& Why);
    bool BeginPristineRunInstallPreparation(uint64& Token,FString& Why);
    bool CheckPristineUnpublishedState(const FDungeonRunInstallGroup* Staged,FString& Why) const;
    void AbortRunInstallPreparation(uint64 Token);
    bool CommitPreparedRunGroup(FDungeonRunInstallGroup& Group,FString& Why);
    void ObserveRunInstallInput();
    bool bRunTickActive=false; // Technical completed-Tick capture gate, not saved state.
    struct FPendingDamage
    {
        ADungeonFighter* Attacker;
        ADungeonFighter* Target;
        float Damage;
        float Stagger;
        double AtTime = 0.0;
        bool Magic = false;
        bool DamageOverTime = false;
        FDungeonWorldWeaponKey Source;
        FVector2D ImpactPosition = FVector2D::ZeroVector;
        double ImpactHeight = 0.0;
        double BurnDps = 0.0;
        double BurnDuration = 0.0;
    };
    TArray<FPendingDamage> PendingDamage;
    bool bSimulationBatch = false;
    bool bFairytaleLookdevPreview = false;
    int32 FairytaleLookdevFacing = 1;
    double FairytaleLookdevEpoch = 0.;
    double SimulationTime = 0.0;
    uint64 RunRestartSerial = 0; // In-memory presentation invalidation, never a D13 RunID.
    TUniquePtr<FDungeonEquipmentRuntime> EquipmentRuntime;
    TUniquePtr<FDungeonRunRewards> RunRewards;
    TUniquePtr<FDungeonRunExploration> RunExploration;
    void ObserveRunExploration();
    void CollectAutomaticRunRewards();
    bool RetireRunRewardRoom();
    FDungeonWeaponWorldState WeaponWorld;
    FDungeonActionAudioState ActionAudioState;
    TMap<uint64,FDungeonActionAudioWeaponCursor> ActionAudioWeaponCursors;
    void SeedActionAudioWeapon(ADungeonFighter* Fighter);
    void ObserveActionAudio(ADungeonFighter* Fighter, const std::vector<DungeonWeaponActions::FEvent>& Events,
        bool RuntimeSynchronized = false);
    void ObservePendingActionAudio(ADungeonFighter* Fighter);
    void AppendActionAudio(const TCHAR* Cue, double AtTime, uint64 OwnerId, uint64 ActionId,
        uint64 InstanceId, uint64 OperationId, uint64 Revision);
    TMap<TWeakObjectPtr<ADungeonFighter>,uint64> WorldEntityIds;
    uint64 FindWorldEntityId(const ADungeonFighter* Fighter) const;
    ADungeonFighter* FindWorldFighter(uint64 EntityId) const;
    void AdmitWorldFighters();
    FDungeonWorldWeaponKey WorldWeaponKey(ADungeonFighter* Fighter, const DungeonWeaponActions::FEvent& Event) const;
    void AppendWeaponWorldEvent(FDungeonWorldWeaponEvent Event);
    bool WorldDamageAdmission(const FDungeonKnightBody& Body, double AtTime, const FDungeonWorldWeaponKey& Key) const;
    void ConsumeBoundWeaponEvents(ADungeonFighter* Fighter, const std::vector<DungeonWeaponActions::FEvent>& Events);
    void ResolveWorldProjectiles(double FromTime, double ToTime, const TArray<FDungeonKnightBody>& Bodies);
    void QueueWorldBurnTicks(double AtTime);
    void ApplyWorldBurn(const FPendingDamage& Hit);
    void ExpireWorldBurns(double AtTime);
    void CancelWorldWeaponWindows(uint64 OwnerId);
    void ClearWorldRoomAttacks();
    bool CanBeginEquipmentAction(bool Switching = false) const;
    EDungeonEquipmentFailure EquipmentSourceAdmission(const FDungeonEquipmentSourceView& Source) const;
    bool StartEquipmentPickup(int32 Slot);
    void CancelEquipmentAction();
    void CommitEquipmentAction();
    bool SyncEquipmentRuntime();
    void UpdateEquipmentMirrors();
    void UpdateEquipmentTarget();
    bool FindEquipmentDropPoint(FVector2D& Position) const;
    bool IsEquipmentDropPointLegal(FVector2D Position) const;
    double LastStoneWakeStartedAt = -1.0;
    bool bManualWeaponPreview = false;
    FGuid ManualWeaponPreviewRunGuid; // In-memory preview lifecycle only, never a D13 field.
    bool SetupManualWeaponPreviewRun();
    TUniquePtr<FDungeonSceneObjects> SceneObjects;
    bool SetupSceneExplorationPreviewRun();
    bool SpawnSceneExplorationRoom();
    void ClearSceneWorldActors();
    TArray<TWeakObjectPtr<AActor>> SceneWorldActors;
    uint64 SceneEncounterEntityId = 0;
    bool bSceneCommitRequested = false;
    bool bSceneEquipmentTargetLost = false;
    bool CanBeginSceneInteraction() const;
    EDungeonSceneFailure SceneObjectAdmission(const FDungeonSceneObjectView& Object) const;
    bool TryInteractScene();
    void CommitSceneInteraction();
    void ValidateSceneConfirmation();
    TArray<FDungeonKnightBody> CaptureKnightBodies() const;
    FDungeonKnightFrame MakeKnightFrame(ADungeonFighter* Knight, double FromTime, double ToTime,
        const TArray<FDungeonKnightBody>& Bodies) const;
    FDungeonKnightFrame MakeKnightDamageFrame(ADungeonFighter* Knight) const;
    void AcceptKnightBatch(ADungeonFighter* Knight, const FDungeonKnightBatch& Batch);
    void AcceptBatBatch(ADungeonFighter* Bat, const FDungeonBatBatch& Batch);
    void AcceptGuardBatch(ADungeonFighter* Guard,const FDungeonGuardBatch& Batch);
    TArray<FDungeonKnightBody> SkillBatchBodies;
    TArray<FDungeonKnightBody> MotionBatchBodies;
    bool bSimulatingMotion = false;
    TMap<uint64,double> SkillOldIframeUntil;
    double SkillBatchFrom = 0.0, SkillBatchTo = 0.0;
    FVector2D SkillPositionAt(ADungeonFighter* Fighter, double AtTime) const;
    FVector2D SweepWeaponStep(ADungeonFighter* Fighter, double SignedDistance, double AtTime) const;
    DungeonDodge::FSweepResult QueryResolvedMovement(ADungeonFighter* Fighter, FVector2D From, FVector2D To,
        double FromTime, double ToTime, const TArray<FDungeonKnightBody>& Bodies) const;
    TArray<FDungeonKnightBody> PredictMotionBodies(double FromTime, double ToTime) const;
    double NextSimulationBoundary(double Limit) const;
    double EarliestContact(double ToTime, const TArray<FDungeonKnightBody>& Bodies);
    void CommitPendingDamage();
    bool FindWeaponSkillContact(ADungeonFighter* Fighter, ADungeonFighter* Target,
        const DungeonWeaponActions::FEvent& Window, double& HitTime) const;
    void ConsumeWeaponSkillEvents(ADungeonFighter* Fighter, const std::vector<DungeonWeaponActions::FEvent>& Events);
    void ResolveWeaponSkillWindows(ADungeonFighter* Fighter);
    void SpawnRoom();
    void NextRoom();
};
