#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "InputCoreTypes.h"
#include "DungeonRangedProofState.h"
#include "DungeonSceneProofState.h"
#include "DungeonXBWReloadSocketProofState.h"
#include "DungeonXBWArmorSocketProofState.h"
#include "DungeonContentProbe.generated.h"
class ADungeonGameMode;
class ADungeonFighter;
class FJsonValue;
class FJsonObject;
class USoundSubmix;
class USoundWave;
struct FActionAudioCaptureSnapshot;

/** Explicit QA fixture: exercises normal key edges, never a production acquisition source. */
UCLASS()
class CODEXDUNGEON_API ADungeonContentProbe : public AActor
{
    GENERATED_BODY()
public:
    ADungeonContentProbe();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
private:
    double Elapsed = 0;
    int32 Fixture = -1;
    int32 Stages = 0;
    bool bSwordChecked = false, bHeavyChecked = false, bSpearChecked = false, bSaved = false;
    float MaxJump = 0, DepthStart = 0;
    FString Directory;
    TMap<FKey,bool> Keys;
    TArray<TSharedPtr<FJsonValue>> Results;
    TArray<TSharedPtr<FJsonValue>> Trace;
    // The game's own main submix, not a desktop loopback or an input device.
    UPROPERTY(Transient)
    TObjectPtr<USoundSubmix> RecordingSubmix;
    bool bGameplayFinished = false, bAudioStartRequested = false;
    bool bAudioStopRequested = false, bAudioExportCallbackReceived = false;
    bool bAudioRecorded = false;
    double CaptureStartWall = 0, CaptureStopWall = 0, WarmupStartWall = 0;
    double WarmupScreenshotRequestedWall = 0, WarmupScreenshotCompletedWall = 0;
    bool bWarmupScreenshotRequested = false, bWarmupScreenshotCompleted = false;
    double AudioClockStart = 0, AudioClockStop = 0;
    int32 WarmupFrames = 0, PreviousDisableAppVolume = 0;
    int32 DisableAppVolumeAtCapture = 0;
    float PrimaryVolumeAtCapture = 0, PrimaryVolumeAtStop = 0;
    bool bPreviousSubmixAutoDisable = true, bAudioControlsConfigured = false;
    bool bSubmixAutoDisableRequestQueued = false;
    bool bAudioControlsRestoreRequested = false, bAppVolumeRestored = false;
    bool bHeaderBlockAlignRepaired = false, bPCMPayloadUnchanged = false;
    double AudioExportDeadlineWall = 0;
    FString AudioFailure;
    TArray<TSharedPtr<FJsonValue>> FrameWallOffsets;
    // Probe-only native copies; serialization never reads live gameplay after stop.
    TSharedPtr<FActionAudioCaptureSnapshot> ActionAudioCaptureSnapshot;
    bool bFirstUnit = false, bFirstUnitSkill = false, bFirstUnitExplore = false;
    bool bEquipmentProof = false;
    bool bRangedProof = false;
    bool bXBWReadyProof = false;
    bool bXBWHeldIdentityProof = false;
    bool bXBWPrimaryProof = false;
    FRangedProofState RangedProof;
    bool bSceneProof = false;
    FSceneProofState SceneProof;
    bool bXBWReloadSocketProof = false;
    FXBWReloadSocketProofState XBWReloadSocketProof;
    bool bXBWArmorSocketProof = false;
    FXBWArmorSocketProofState XBWArmorSocketProof;
    bool bArmorLayerProof = false;
    bool bArmorComboProof = false;
    bool bArmorSleevesProof = false;
    int32 ArmorSleeveOrderFrameMask[2][2]={{0,0},{0,0}};
    bool bArmorSleeveOrderValid[2][2]={{true,true},{true,true}};
    int32 ArmorVariant=0,ArmorPrimaryMask[2]={0,0};
    int32 ArmorComboFrameMask[2][3]={{0,0,0},{0,0,0}};
    int32 ArmorComboStageMask[2]={0,0};
    uint64 ArmorComboLastId[2]={0,0};
    uint64 ArmorComboWeaponInstance[2]={0,0};
    double ArmorComboLastEnd[2]={0,0};
    bool bArmorComboContinuous[2]={true,true};
    int32 ArmorWalkMask[2]={0,0};
    bool bArmorIdleRight=false,bArmorPrimaryAccepted=false,bArmorPickupAccepted=false,bArmorOldHeld=true,bArmorDuration=true;
    FString ArmorOldId;
    uint64 ArmorSourceId=0,ArmorSourceInstance=0,ArmorOldInstance=0;
    FVector2D ArmorPickupPosition=FVector2D::ZeroVector;
    uint64 EquipmentStarter=0, EquipmentHeavy=0, EquipmentArmor=0, EquipmentSecondSword=0;
    uint64 EquipmentHeavySource=0, EquipmentArmorSource=0, EquipmentSecondSwordSource=0;
    uint64 EquipmentDropSource=0, EquipmentRevisionBeforeSelection=0;
    uint64 EquipmentCritBefore=0;
    double EquipmentSwordCooldown=0;
    bool bEquipmentOldHeld=true, bEquipmentDuration=true, bEquipmentStarted=false;
    int32 UnitPhase = 0, UnitComboMask = 0, UnitQueuedStage = 0, UnitRewardCount = 0;
    double UnitPhaseAt = 0, UnitStartSim = 0, UnitEdgeAt = -1, UnitReleasedAt = -1;
    double UnitWakeAt = -1, UnitWakeEnd = -1, UnitChargeEnd = 0, UnitRecoveryEnd = 0;
    double UnitShieldEnd = 0, UnitShieldOriginY = 0, UnitAirExtraAt = -1;
    uint64 UnitChargeId = 0, UnitEscapeShieldId = 0, UnitFightShieldId = 0;
    FVector2D UnitChargeDirection = FVector2D::ZeroVector;
    double UnitLockedPlayerY = 0;
    float UnitInitialHP = 0, UnitChargeHP = 0, UnitEscapeHP = 0, UnitFightHP = 0;
    float UnitChainStartHP = 0, UnitAirStartHP = 0, UnitLeftStartX = 0;
    float UnitAirExtraAttackTime = 0, UnitAirExtraProgress = 0;
    int32 UnitCoinsAtDeath = 0;
    FKey UnitEdgeKey;
    bool bUnitEdgeDown = false, bUnitJumpIssued = false, bUnitJumpHigh = false;
    bool bUnitYChangedAfterLock = false, bUnitChargeNudgeIssued = false, bUnitLineStable = true, bUnitRecoveryHeld = false;
    bool bUnitEarlyNextAttack = false, bUnitChainStarted = false, bUnitNonPoiseHit = false;
    bool bUnitStonePoiseBreak = false, bUnitAirAccepted = false, bUnitAirExtraIssued = false;
    bool bUnitAirExtraRejected = false, bUnitLandingContinued = false, bUnitGroundPrimary = false;
    uint64 UnitSkillId = 0, UnitSinglePrimaryId = 0;
    double UnitSkillRequestedAt = -1, UnitSkillStart = 0, UnitSkillLockAt = 0;
    double UnitSkillActiveAt = 0, UnitSkillActiveEnd = 0, UnitSkillEnd = 0;
    double UnitSkillCooldownDeadline = 0, UnitSkillExtraAt = -1, UnitSkillCompletedAt = -1;
    double UnitSkillStartHP = 0, UnitSkillPreviousHP = 0, UnitSkillEndHP = 0;
    double UnitSingleStartHP = 0, UnitSingleRequestedAt = -1, UnitSingleEndHP = 0;
    int32 UnitSkillDamageObservations = 0;
    bool bUnitSkillInputIssued = false, bUnitSkillAccepted = false;
    bool bUnitSkillUnlockedObserved = false, bUnitSkillLockedObserved = false;
    bool bUnitSkillActiveObserved = false, bUnitSkillRecoveryObserved = false;
    bool bUnitSkillCooldownValid = true, bUnitSkillDamageTimingValid = true, bUnitSkillNoEarlyEnd = true;
    bool bUnitSkillExtraIssued = false, bUnitSkillExtraRejected = false;
    bool bUnitSingleInputIssued = false;
    bool bUnitCombatCompleted = false, bUnitExploreInitialized = false;
    bool bUnitExploreMemoryMonotonic = true;
    int32 UnitExploreRoom = 0, UnitExploreInitialCount = 0, UnitExploreLastCount = 0;
    int32 UnitExploreRevealedCount = 0, UnitExploreRetreatCount = 0, UnitExploreExitCoins = 0;
    uint64 UnitExploreResetSerial = 0;
    double UnitExploreExitInputAt = -1, UnitExploreOldUMemory = 0, UnitExploreOldRMemory = 0;
    float UnitExploreExitHP = 0;
    TWeakObjectPtr<ADungeonFighter> UnitExplorePlayer;
    TArray<TSharedPtr<FJsonValue>> UnitExploreSamples;
    TSet<FString> UnitRenderedTexturePaths;
    FString UnitFailure;
    void Key(FKey Code, bool Down);
    void Check(const FString& Name, bool Passed);
    void Setup(ADungeonGameMode* Game, const FString& Weapon, int32 Index);
    void ScreenshotProcessed();
    void BeginAudioCapture();
    void FinishAudioCapture();
    void BeginActionAudioEvidence();
    void PollActionAudioEvidence(bool Initial=false);
    void FreezeActionAudioEvidence();
    TSharedPtr<FJsonObject> SerializeActionAudioEvidence() const;
    void RestoreAudioControls();
    void TickFirstUnit();
    void TickSceneProof();
    void TickXBWReloadSocketProof();
    void TickXBWArmorSocketProof();
    void TickEquipmentProof();
    void TickArmorLayerProof();
    void TickRangedProof();
    bool UnitPulse(FKey Code, double SimulationTime);
    void UnitMove(float X, float Y);
    void UnitGo(int32 Phase, double SimulationTime);
    void UnitFail(const FString& Reason);
    void UnitReleaseInputs();
    void UnitExploreSample(const FString& Label, ADungeonGameMode* Game, ADungeonFighter* Player);
    UFUNCTION()
    void AudioExported(const USoundWave* ResultingSoundWave);
    void Save();
};
