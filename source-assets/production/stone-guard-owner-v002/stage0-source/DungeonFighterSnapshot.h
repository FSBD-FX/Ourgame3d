#pragma once
#include "CoreMinimal.h"
#include "DungeonContentCombat.h"
#include "DungeonWeaponActions.h"
#include "DungeonDodge.h"
#include "DungeonStoneKnight.h"
#include "DungeonStoneBat.h"
#include "DungeonStoneGuard.h"
#include "DungeonWeaponPoseSocket.h"
#include "DungeonEquipmentRuntime.h"
#include "DungeonWorldProjectiles.h"

// Versioned owner values only. None of these fields is an Actor/Controller,
// component, weak pointer, simulation-batch query cache or replay command.
enum class EDungeonFighterOwnerKind : uint8 { Unsupported, BoundPlayer, StoneKnight, StoneBat, StoneGuard };
struct FDungeonFighterEmissionPoseSnapshot
{
    uint64 EventId=0, ActionId=0;
    uint32 SubhitId=0;
    DungeonWeaponPoseSocket::FResolved Pose;
};
struct FDungeonFighterSkillHitSnapshot
{
    uint64 ActionId=0;
    uint32 SubhitId=0;
    uint64 TargetId=0;
};
struct FDungeonPlayerKernelSnapshot
{
    DungeonContentCombat::FCombatState Combat;
    DungeonWeaponActions::FState WeaponActions;
    DungeonDodge::FState Dodge;
};
// Guard schema1 preserves explicit policy outside FState, and a native
// observer independently from local eligibility and formal reward settlement.
struct FDungeonStoneGuardOwnerSnapshot
{
    uint32 Schema=1;
    DungeonStoneGuard::FPolicy Policy;
    DungeonStoneGuard::FState Kernel;
    bool DeathObserved=false;
};
struct FDungeonFighterOwnerSnapshot
{
    // Development schema2 adds actual native height-anchor values; schema1 is rejected.
    uint32 Schema=2;
    FGuid RunGuid;
    uint64 RoomInstanceId=0, EntityId=0;
    EDungeonFighterOwnerKind Kind=EDungeonFighterOwnerKind::Unsupported;
    FVector2D GroundPosition=FVector2D::ZeroVector;
    float Health=0, MaxHealth=0, JumpHeight=0, JumpVelocity=0, Facing=1;
    bool Enemy=false, AIEnabled=false, Dead=false, DeathReported=false;
    int32 Coins=0;
    FString EnemyContentId, WeaponId, ArmorId;
    float FocusMirror=0;
    float InvulnerableTime=0, HurtTime=0, AttackCooldown=0;
    float PoiseAccumulation=0, PoiseDecayDelay=0, PoiseProtection=0;
    bool AirPrimarySpent=false;
    FDungeonWorldWeaponKey HurtProtectionSource;
    uint64 LastSkillEventId=0;
    std::vector<FDungeonFighterEmissionPoseSnapshot> EmissionPoseSockets;
    // Retain raw inert legacy fields; schema2 rejects an active unsupported
    // legacy operation instead of silently dropping its obligations.
    std::vector<DungeonWeaponActions::FEvent> SkillWindows;
    std::vector<FDungeonFighterSkillHitSnapshot> SkillHitReceipts;
    float AttackElapsed=0, ArmorChangeRemaining=0, FocusConsumeAge=1;
    bool AttackResolved=false, HasAxe=false;
    FString PendingArmorId;
    // Display continuity is preserved. AnimationTime also selects authored
    // native muzzle geometry; terminal display height may differ from combat Z.
    float AttackTime=0, HitFlash=0, AnimationTime=0, LandingVisualAge=0;
    int32 ComboStage=0;
    bool Moving=false;
    FString AnimationName, AttackPhase;
    // Native numerical fact, independent of JumpHeight/Facing: ordinary component
    // updates can retain a prior transform inside the engine update predicate.
    FTransform HeightAnchorRelative=FTransform::Identity;
    bool CustomMuzzle=false;
    FTransform CustomMuzzleRelative=FTransform::Identity;
    double BatObservedHeight=90;
    // Exactly one is present, according to Kind. Accepted state/history is
    // copied whole; only unaccepted physical input buffers may be cleared.
    TOptional<FDungeonPlayerKernelSnapshot> Player;
    TOptional<DungeonStoneKnight::FState> Knight;
    TOptional<DungeonStoneBat::FState> Bat;
    // Only Guard uses owner schema3. Old schema2 layouts/wire remain V1.
    TOptional<FDungeonStoneGuardOwnerSnapshot> Guard;
};

// Call-scoped read-only views of the approved saved aggregate. Pointers here
// never enter a payload. The target Actor need not belong to the live GM map.
struct FDungeonFighterRestoreContext
{
    FGuid RunGuid;
    uint64 RoomInstanceId=0, EntityId=0;
    double SimulationTime=0;
    bool GameOver=false;
    const FDungeonEquipmentRuntimeSnapshot* Equipment=nullptr;
    const FDungeonWeaponWorldState* WeaponWorld=nullptr;
};
