#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "DungeonContentCombat.h"
#include "DungeonStoneKnightDriver.h"
#include "DungeonStoneBatDriver.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonStoneFeedback.h"
#include "DungeonStoneGuardFeedback.h"
#include "DungeonWeaponActions.h"
#include "DungeonWeaponPoseSocket.h"
#include "DungeonDodge.h"
#include "DungeonWorldProjectiles.h"
#include "DungeonFighterSnapshot.h"
#include "DungeonCompletedGroundMotion.h"
#include "DungeonHurtPresentation.h"
#include "DungeonDeathPresentation.h"
#include "DungeonDodgePresentation.h"
#include "DungeonGuardMovePresentation.h"
#include "DungeonFighter.generated.h"

class ADungeonGameMode;
class USceneComponent;

UCLASS()
class CODEXDUNGEON_API ADungeonFighter : public APawn
{
    GENERATED_BODY()

public:
    ADungeonFighter();
    bool CaptureOwnerSnapshot(FDungeonFighterOwnerSnapshot& Out, FString& Diagnostic,
        const FDungeonFighterRestoreContext* ExplicitStaging = nullptr) const;
    bool RestoreOwnerSnapshot(const FDungeonFighterOwnerSnapshot& Snapshot,
        const FDungeonFighterRestoreContext& Context, FString& Diagnostic);
    static bool ValidateOwnerSnapshot(const FDungeonFighterOwnerSnapshot& Snapshot,
        const FDungeonFighterRestoreContext& Context, FString& Diagnostic);
    virtual void Tick(float DeltaSeconds) override;
    // Native completed-commit witness, never a saved owner field or HUD estimate.
    bool QueryCompletedGroundMotion(FDungeonCompletedGroundMotion& Out) const;
    bool IsOrdinaryGroundWalkPose() const;
    // Read-only actual non-dead Hurt facts; reject atomically. No new timer or gameplay gate.
    bool QueryHurtPresentation(FDungeonHurtPresentationSample& Out) const;
    // Read-only actual terminal display age, including paused/continued dead owners.
    bool QueryDeathPresentation(FDungeonDeathPresentationSample& Out) const;
    // Actual same-owner/action Dodge clock; read-only and atomic, including paused published owners.
    bool QueryDodgePresentation(FDungeonDodgePresentationSample& Out) const;
    // Actual Guard-only completed Move facts; read-only and atomic.
    bool QueryCompletedGuardMove(FDungeonGuardMoveSample& Out) const;

    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float Health = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float MaxHealth = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float JumpHeight = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float Facing = 1.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float AttackTime = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float HitFlash = 0.f;
    UPROPERTY(BlueprintReadWrite, Category="Dungeon") bool bEnemy = false;
    UPROPERTY(BlueprintReadWrite, Category="Dungeon") bool bAIEnabled = true;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") bool bDead = false;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString AnimationName = TEXT("idle");
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float AnimationTime = 0.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") int32 Coins = 0;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString WeaponId = TEXT("sword");
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") bool bHasAxe = false;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") int32 ComboStage = 0;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString AttackPhase = TEXT("idle");
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString ArmorId;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") float Focus = 100.f;
    UPROPERTY(BlueprintReadOnly, Category="Dungeon") FString EnemyContentId;

    UFUNCTION(BlueprintPure, Category="Dungeon") FVector2D GetGroundPosition() const;
    UFUNCTION(BlueprintCallable, Category="Dungeon") void MoveOnGround(FVector2D Direction, float DeltaSeconds);
    UFUNCTION(BlueprintCallable, Category="Dungeon") void StartJump();
    UFUNCTION(BlueprintPure, Category="Dungeon") bool CanStartAttack() const;
    UFUNCTION(BlueprintCallable, Category="Dungeon") void ApplyCombatHit(float Damage, ADungeonFighter* Attacker, float Stagger = -1.f, bool Magic = false);
    UFUNCTION(BlueprintCallable, Category="Dungeon") void ResetFighter(FVector2D GroundPosition);
    UFUNCTION(BlueprintCallable, Category="Dungeon") void SwitchWeapon();

    static bool CanHitTarget(FVector2D Delta, float InFacing, float Range,
        float DepthTolerance, float AttackerHeight, float TargetHeight);

    void BeginAttack();
    float GetAttackRange() const;
    float GetAttackDamage() const;
    float GetAttackStagger() const;
    float GetAttackDepth() const;
    float GetAttackMinRange() const;
    bool IsContentMelee() const;
    bool IsAttackActive() const;
    bool CanContentHit(ADungeonFighter* Target) const;
    bool MarkContentHit(ADungeonFighter* Target);
    float GetActionProgress() const;
    int32 GetPrimaryPoseFrame() const;
    void ClearPendingAttackInput();
    bool TryBeginWeaponSkill(bool FreshPress = true);
    bool TryBeginReload(bool FreshPress = true);
    DungeonWeaponActions::FOrigin GetWeaponMuzzleOrigin() const;
    USceneComponent* GetWeaponMuzzleComponent() const { return WeaponMuzzle; }
    DungeonWeaponPoseSocket::FResolved GetWeaponPoseSocket() const;
    const DungeonWeaponPoseSocket::FResolved* FindWeaponEmissionPoseSocket(uint64 ActionId,uint32 SubhitId=0) const;
    void UseAuthoredWeaponPoseSocket();
    const DungeonWeaponActions::FAction& GetWeaponSkillAction() const { return WeaponSkills.State().Action; }
    double GetWeaponSkillCooldownRemaining() const;
    double GetWeaponSkillTime() const { return WeaponSkills.State().Time; }
    const DungeonContentCombat::FCombatState& GetMeleeCombatState() const { return Combat.State(); }
    const DungeonWeaponActions::FState& GetWeaponActionsState() const { return WeaponSkills.State(); }
    bool IsEquipmentBound() const;
    double GetEquipmentActionDeadline() const;
    bool TryBeginDodge(FVector2D MoveIntent = FVector2D::ZeroVector, bool FreshPress = true);
    const DungeonDodge::FState& GetDodgeState() const { return Dodge.State(); }
    bool IsDodgeInvulnerableAt(double HitTime) const;
    bool CanReceiveDirectHit() const;
    void SimulateMotion(float DeltaSeconds, bool ConsumeInputEdges);
    void SimulateActions(float DeltaSeconds);
    bool BeginArmorChange(const FString& TemplateId);
    bool SpendFocus(float Amount);
    float RestoreFocus(float Amount);
    float GetArmorRating(bool Magic = false) const;
    float GetMoveSpeed() const;
    float GetPoiseThreshold() const;
    float GetArmorChangeRemaining() const { return ArmorChangeRemaining; }
    float GetVerticalVelocity() const { return JumpVelocity; }
    double GetCombatHeight() const { return StoneBat ? BatObservedHeight : double(JumpHeight); }
    bool IsCurrentPrimaryAirborne() const { return IsContentMelee() && Combat.State().Action.Active && Combat.State().Action.StartedAirborne; }
    float GetLandingVisualAge() const { return LandingVisualAge; }
    bool InitializeStoneKnight(uint64 EntityId, double StartTime = 0.0);
    const FDungeonStoneKnightDriver* GetStoneKnightDriver() const { return StoneKnight.Get(); }
    bool InitializeStoneBat(uint64 EntityId,double StartTime=0.0);
    const FDungeonStoneBatDriver* GetStoneBatDriver() const { return StoneBat.Get(); }
    bool InitializeStoneGuard(uint64 EntityId,double StartTime=0.0);
    const FDungeonStoneGuardDriver* GetStoneGuardDriver() const { return StoneGuard.Get(); }
    bool IsStoneGuardDeathObserved() const {return StoneGuard && bGuardDeathObserved;}
    bool ClaimStoneGuardDeathEligibility(); // Explicit local once marker; not reward settlement.
    bool IsStoneGuardDeathSettled() const { return StoneGuard && bDeathReported; }
    FVector2D GetCombatBodyHalfExtent() const;
    FVector2D GetProjectileHurtHalfExtent() const;
    const DungeonStoneFeedback::FJournal& GetStoneFeedback() const { return StoneFeedback; }
    const DungeonGuardFeedback::FJournal& GetGuardFeedback() const { return GuardFeedback; }
    // Bound player uses Run-scoped OwnerId; enemy/legacy IDs remain QA-only. No D13 IO yet.
    uint64 GetRuntimeEntityId() const;
    bool bDeathReported = false;

private:
    friend class ADungeonGameMode;
    UPROPERTY() TObjectPtr<USceneComponent> WeaponMuzzleHeightAnchor;
    UPROPERTY() TObjectPtr<USceneComponent> WeaponMuzzle;
    bool bWeaponMuzzleCustomOverride = false;
    FTransform LastAutomaticMuzzleTransform = FTransform::Identity;
    struct FEmissionPoseSocket
    {
        uint64 EventId=0,ActionId=0;uint32 SubhitId=0;
        DungeonWeaponPoseSocket::FResolved Pose;
    };
    std::vector<FEmissionPoseSocket> EmissionPoseSockets;
    void ApplyCombatHitInternal(float Damage, ADungeonFighter* Attacker, float Stagger, bool PreviouslyAccepted,
        bool Magic = false, bool DamageOverTime = false, bool PreserveHurtProtection = false);
    void SyncWeaponMuzzleTransform(double SampleTime=-1.);
    DungeonWeaponPoseSocket::FResolved ResolveWeaponPoseSocketAt(double SampleTime) const;
    void InterruptWeaponActionForHit(DungeonWeaponActions::EInterrupt Reason);
    FDungeonWorldWeaponKey HurtProtectionSource;
    void UpdatePlayerInput(float DeltaSeconds, bool ConsumeInputEdges);
    void UpdateEnemy(float DeltaSeconds);
    void SetAnimation(const FString& Name, float DeltaSeconds);
    void AdvanceTerminalPresentation(float DeltaSeconds);
    float JumpVelocity = 0.f;
    float LandingVisualAge = .12f; // Presentation only; never gates input or simulation.
    float AttackElapsed = 0.f;
    float AttackCooldown = 0.f;
    float InvulnerableTime = 0.f;
    float HurtTime = 0.f;
    bool bAttackResolved = false;
    bool bMoving = false;
    FDungeonCompletedGroundMotion CompletedGroundMotion;
    bool bGroundMotionFrameOpen=false,bUnconsumedGroundMotion=false,bInvalidGroundMotion=false,bGroundMotionDiscontinuous=false;
    double PendingWalkDistance=0.;
    bool CanAccumulateGroundWalk() const;
    void BeginGroundMotionFrame(double FromTime);
    void RecordCompletedGroundMotion(FVector2D From,FVector2D To,double FromTime,double ToTime,
        bool Grounded,bool OrdinaryEligible,bool HadIntent);
    void EndGroundMotionFrame(double ToTime);
    void InvalidateGroundMotion();
    bool bSuppressOrdinaryMovement = false;
    DungeonContentCombat::FCombatKernel Combat;
    // Formal inventory binding makes this budget the sole Focus authority.
    // The old unbound QA path retains its separate historical integration.
    DungeonWeaponActions::FWeaponActionsKernel WeaponSkills;
    DungeonDodge::FDodgeKernel Dodge{1};
    struct FSkillHitReceipt { uint64 ActionId; uint32 SubhitId; uint64 TargetId; };
    std::vector<FSkillHitReceipt> SkillHitReceipts;
    std::vector<DungeonWeaponActions::FEvent> SkillWindows;
    uint64 LastSkillEventId = 0;
    double BatchSkillStepAt = -1.0;
    FVector2D BatchSkillStepDelta = FVector2D::ZeroVector;
    DungeonWeaponActions::FContext WeaponSkillContext() const;
    void AdvanceWeaponSkillTo(double Now, std::vector<DungeonWeaponActions::FEvent>* DeferredEvents = nullptr,
        bool* RuntimeSynchronized = nullptr);
    void SyncWeaponSkillAction();
    DungeonContentCombat::FActionState HitAction;
    bool bResolvingContentWindow = false;
    DungeonContentCombat::FAttackContext CombatContext() const;
    void AdvanceContentActionTo(double Now);
    void SyncContentAction();
    void SimulateActionsTo(double Now, float DeltaSeconds, std::vector<DungeonWeaponActions::FEvent>* DeferredEvents = nullptr);
    FVector2D ReadMoveIntent() const;
    FVector2D PredictGroundPosition(double DeltaSeconds) const;
    void CommitIdleDodgePosition();
    void SyncDodgeAction();
    bool bAirPrimarySpent = false;
    float PoiseAccumulation = 0.f;
    float PoiseDecayDelay = 0.f;
    float PoiseProtection = 0.f;
    FString PendingArmorId;
    float ArmorChangeRemaining = 0.f;
    float FocusConsumeAge = 1.f;
    bool bEquipmentUiArrowLatch = false;
    TUniquePtr<FDungeonStoneKnightDriver> StoneKnight;
    TUniquePtr<FDungeonStoneBatDriver> StoneBat;
    TUniquePtr<FDungeonStoneGuardDriver> StoneGuard;
    double LastGuardSyncTime=0.0;
    bool bGuardDeathObserved=false;
    void SyncStoneGuardState();
    DungeonStoneFeedback::FJournal StoneFeedback;
    DungeonGuardFeedback::FJournal GuardFeedback;
    double LastStoneSyncTime = 0.0;
    void SyncStoneKnightState();
    double LastBatSyncTime = 0.0;
    double BatObservedHeight = 90.0; // Exact frozen motion observation; JumpHeight is the float presentation mirror.
    void SyncStoneBatState();
    DungeonContentCombat::EArmor ContentArmor() const;
    DungeonContentCombat::EWeapon ContentWeapon() const;
};
