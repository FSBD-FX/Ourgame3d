#pragma once
#include <cstdint>
#include <functional>
#include <vector>

namespace DungeonStoneGuard
{
struct FPoint { double X=0, Y=0, Z=0; };
enum class EAttack { None, AxeSweep, Stomp };
enum class EPhase { Dormant, Waking, Idle, Windup, Active, Recovery, Stunned, Dead };
enum class EStop { None, Wall, Body };
enum class EEventKind
{
    WakeStarted, WakeCompleted, AttackStarted, AimLocked, ActiveWindow,
    RecoveryStarted, AttackCompleted, Movement, Damaged, PoiseBroken,
    AttackInterrupted, Hit, Died, RewardClaimed
};
struct FDefinition
{
    const char* ContentId="ENM-STN-003";
    double HP=185, Armor=60, Ward=15, Poise=85, MoveSpeed=160;
    double BodyHalfX=40, BodyHalfY=28, HurtHalfX=40, HurtHalfY=28;
    double WakeRadiusX=235, WakeRadiusY=110, WakeWarning=1;
};
struct FAttackDefinition
{
    const char* ContentId="";
    double Windup=0, LockDelay=0, Active=0, Recovery=0, Cooldown=0;
    double Damage=0, Stagger=0, ReachX=0, HalfY=0, HeightTolerance=65;
};
// Proposal: the design says "extremely close" without a numeric threshold.
// Policy is outside FState; Native Owner must explicitly save and reconstruct it.
struct FPolicy { double ExtremelyCloseRadius=70; };
struct FAction
{
    std::uint64_t AttackId=0;
    EAttack Kind=EAttack::None;
    bool InProgress=false, Locked=false, WindowIssued=false, Interrupted=false;
    double Start=0, LockAt=0, ActiveAt=0, ActiveEnd=0, RecoveryEnd=0, CooldownEnd=0;
    double InterruptedAt=-1, CompletedAt=-1, Damage=0, Stagger=0;
    FPoint Origin, LockedCenter, Target;
    int Facing=1;
};
// Issued facts never change. Cancellation is an independent closing receipt.
struct FDamageWindow
{
    std::uint64_t AttackId=0, EventId=0;
    EAttack Kind=EAttack::None;
    double Start=0, End=0, Damage=0, Stagger=0;
    FPoint Center;
    int Facing=1;
};
struct FWindowClosure { std::uint64_t AttackId=0; double AtTime=0; };
struct FHitReceipt { std::uint64_t AttackId=0, TargetId=0; double AtTime=0; };
struct FIncomingHit { std::uint64_t ReceiptId=0; double AtTime=0, HPLoss=0, Stagger=0; };
struct FReceivedHit { std::uint64_t ReceiptId=0; double AtTime=0, ActualHPLoss=0, Stagger=0; };
struct FEvent
{
    std::uint64_t EventId=0, EntityId=0, TargetId=0;
    EEventKind Kind=EEventKind::Movement;
    double AtTime=0, EndTime=0, Amount=0;
    FPoint From, To;
    FAction Action;
};
struct FSweepRequest
{
    double FromTime=0, ToTime=0;
    FPoint From, To;
    double BodyHalfX=40, BodyHalfY=28;
};
struct FSweepResult { bool Accepted=true; double Fraction=1; EStop Stop=EStop::None; };
struct FWorldInput
{
    bool HasTarget=false, TargetAlive=true, LOS=true, CanBeginWake=true, CanStartAttack=true;
    FPoint Target;
    // A query, never an actor move or HP write. Only idle locomotion uses it.
    std::function<FSweepResult(const FSweepRequest&)> Sweep;
};
struct FTarget
{
    std::uint64_t EntityId=0;
    FPoint Position;
    bool Alive=true, Hostile=true, LOS=true, Invulnerable=false;
};
struct FResult { bool Accepted=false; std::vector<FEvent> Events; };
struct FState
{
    std::uint32_t Version=1;
    std::uint64_t EntityId=0, NextAttackId=1, NextEventId=1, LastDamageReceiptId=0;
    double InitialTime=0, Time=0, HP=185;
    double PoiseAccum=0, PoiseDecayOrigin=0, LastPoiseAt=-1, ProtectionUntil=0, StunUntil=0;
    double CombatStartedAt=-1, WakeStartedAt=-1, WakeEnd=-1;
    double AxeReadyAt=0, StompReadyAt=0, OccupiedUntil=0, IdleReadyAt=0;
    bool WakeQueued=false, Awakened=false, RewardClaimed=false;
    EPhase Phase=EPhase::Dormant;
    FPoint InitialPosition, Position;
    int Facing=1;
    FAction Action;
    std::vector<FDamageWindow> Windows;
    std::vector<FWindowClosure> Closures;
    std::vector<FHitReceipt> HitReceipts;
    std::vector<FReceivedHit> ReceivedHits;
    std::vector<FEvent> Issued;
};
class FGuardKernel
{
public:
    explicit FGuardKernel(std::uint64_t EntityId, double StartTime=0, FPoint Position={}, int Facing=1, FPolicy Policy={});
    static FDefinition Definition();
    static FAttackDefinition AttackDefinition(EAttack Kind);
    const FState& State() const { return S; }
    FState Capture() const { return S; }
    FPolicy CapturePolicy() const { return Policy; }
    // Same entity and immutable birth only; retains this receiver's validated policy.
    bool Restore(const FState& Saved);
    bool IsValid() const { return Initialized; }
    EAttack ChooseAttack(const FWorldInput& World) const;
    FResult StepTo(double Now, const FWorldInput& World, const std::vector<FIncomingHit>& Hits={});
    FResult TryStartAttack(EAttack Kind, const FWorldInput& World);
    FResult ApplyResolvedHit(std::uint64_t ReceiptId, double HPLoss, double Stagger, const FWorldInput& World);
    FResult TryHit(const FTarget& Target);
    bool BeginCombat();
    bool NotifyOtherAcceptedEnemiesCleared();
    FResult ClaimDeathReward();
    bool GroundBodyEnabled() const;
    bool CounterWindowOpen() const;
    // Explicit new spawn only. Never a leash heal or a same-identity reward reset.
    bool ResetForNewEntity(std::uint64_t NewEntityId, double Now, FPoint Position={}, int Facing=1);
private:
    FState S;
    FPolicy Policy;
    bool Initialized=false;
    bool Visible(const FWorldInput& World) const;
    bool NearWake(const FWorldInput& World) const;
    bool Eligible(EAttack Kind, const FWorldInput& World) const;
    bool Advance(double To);
    bool Emit(FResult& Out, EEventKind Kind, double End=0, double Amount=0, std::uint64_t Target=0, FPoint From={}, FPoint To={});
    bool BeginWake(FResult& Out);
    bool Pump(const FWorldInput& World, FResult& Out, bool& Changed);
    bool MoveIdle(double To, const FWorldInput& World, FResult& Out);
    bool ApplyHits(const std::vector<FIncomingHit>& Hits, std::size_t& Index, const FWorldInput& World, FResult& Out);
    bool Interrupt(FResult& Out);
    bool CapacityValid() const;
};
}
