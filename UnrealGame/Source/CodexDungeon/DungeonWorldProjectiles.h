#pragma once

#include "CoreMinimal.h"
#include "DungeonWeaponActions.h"
#include "DungeonWeaponPoseSocket.h"

// All keys belong to the fixed weapon-actions-v1 domain in the enclosing Run.
// Actor addresses and display template names never identify a consumed hit.
struct FDungeonWorldWeaponKey
{
    uint64 OwnerId = 0;
    uint64 ActionId = 0;
    uint64 EventId = 0;
    uint32 SubhitId = 0;
    uint64 RoomInstanceId = 0;
};

// Transient actual post-placement facts, including a fully blocked zero commit.
// Not audio eligibility, a movement request, saved state, or a new event domain.
struct FDungeonWeaponForwardStepPlacementV001
{
    bool Present=false, GroundedAtCommit=false;
    FGuid RunGuid;
    uint64 RoomInstanceId=0,OwnerId=0,ActionId=0,InstanceId=0,EventId=0;
    uint32 SubhitId=0;
    uint64 PresentationEpoch=0,RunRestartSerial=0,EquipmentRevisionAtCommit=0;
    DungeonWeaponActions::EEvent Kind=DungeonWeaponActions::EEvent::Started;
    DungeonContentCombat::EWeapon Weapon=DungeonContentCombat::EWeapon::SWD001;
    double ActionStart=0.,AtTime=0.,ObservedSimulationTime=0.,RequestedSignedDistance=0.;
    FVector2D Before=FVector2D::ZeroVector,After=FVector2D::ZeroVector,CommittedDelta=FVector2D::ZeroVector;
};

enum class EDungeonWorldProjectileStop : uint8
{
    None, TargetLimit, Wall, Range, HardBounds, RoomExit, BlockedBody
};

struct FDungeonWorldProjectile
{
    FDungeonWorldWeaponKey Key;
    // Immutable facts from the real emission, including its own muzzle XY/height.
    DungeonWeaponActions::FEvent Source;
    FVector2D Position = FVector2D::ZeroVector;
    double Traveled = 0.0;
    bool Active = false;
    EDungeonWorldProjectileStop Stop = EDungeonWorldProjectileStop::None;
    // Immutable emission-time presentation and range facts; never follow Owner.
    bool HasPoseSocket = false;
    DungeonWeaponPoseSocket::FResolved PoseSocket;
    DungeonWeaponActions::FOrigin RangeAnchor;
    bool UsesActorRangeAnchor = false;
    double LaunchForwardDistance = 0.;
    // A blocked Actor-to-socket launch segment is not external ballistic travel.
    bool LaunchClearancePending = false;
    bool LaunchObstructed = false;
};

struct FDungeonWorldWeaponWindow
{
    FDungeonWorldWeaponKey Key;
    DungeonWeaponActions::FEvent Source;
    bool Active = false;
};

struct FDungeonWorldWeaponHitReceipt
{
    FDungeonWorldWeaponKey Key;
    uint64 TargetId = 0;
    double AtTime = 0.0;
    double Damage = 0.0;
    double Stagger = 0.0;
    bool Magic = false;
    bool HasPoseSocket = false;
    DungeonWeaponPoseSocket::FResolved PoseSocket;
    DungeonWeaponActions::FOrigin RangeAnchor;
    bool LaunchObstructed = false;
};

struct FDungeonWorldBurn
{
    FDungeonWorldWeaponKey Key;
    uint64 TargetId = 0;
    double Dps = 0.0;
    double AppliedAt = 0.0;
    double ExpiresAt = 0.0;
    double NextTickAt = 0.0;
    bool Active = false;
};

struct FDungeonWorldActorBinding
{
    uint64 EntityId = 0;
    uint64 RoomInstanceId = 0;
    FString ContentId;
};

enum class EDungeonWorldWeaponEventKind : uint8
{
    ProjectileEmitted, WindowCreated, DirectHitCommitted, ProjectileStopped,
    BurnApplied, BurnRefreshed, BurnTickCommitted, BurnExpired
};

struct FDungeonWorldWeaponEvent
{
    uint64 Sequence = 0;
    EDungeonWorldWeaponEventKind Kind = EDungeonWorldWeaponEventKind::ProjectileEmitted;
    FDungeonWorldWeaponKey Key;
    uint64 TargetId = 0;
    double AtTime = 0.0;
    FVector2D Position = FVector2D::ZeroVector;
    double Height = 0.0;
    double Damage = 0.0;
    double Stagger = 0.0;
    double ActualHPLoss = 0.0;
    bool Magic = false;
    bool HasPoseSocket = false;
    DungeonWeaponPoseSocket::FResolved PoseSocket;
    DungeonWeaponActions::FOrigin RangeAnchor;
    bool LaunchObstructed = false;
};

// GameMode owns this Run-local world batch. The public API only observes it.
// This is not a D13 disk format or a completed persistence transaction.
struct FDungeonWeaponWorldState
{
    FGuid RunGuid;
    uint64 RoomInstanceId = 0;
    double Time = 0.0;
    uint64 NextEventSequence = 1;
    uint64 NextEntityId = 2; // OwnerId 1 is reserved by a newly bound Run.
    TArray<FDungeonWorldActorBinding> ActorBindings;
    TArray<FDungeonWorldProjectile> Projectiles;
    TArray<FDungeonWorldWeaponWindow> Windows;
    TArray<FDungeonWorldWeaponHitReceipt> HitReceipts;
    TArray<FDungeonWorldBurn> Burns;
    TArray<FDungeonWorldWeaponEvent> Events;
};

class ADungeonFighter;
class UWorld;
struct FDungeonKnightBody;

struct FDungeonWorldProjectileContact
{
    bool Found = false;
    bool LegalDamage = false;
    double AtTime = 0.0;
    FVector2D Position = FVector2D::ZeroVector;
    TWeakObjectPtr<ADungeonFighter> Target;
    EDungeonWorldProjectileStop Stop = EDungeonWorldProjectileStop::None;
    bool LaunchSegment = false;
};

namespace DungeonWorldProjectiles
{
CODEXDUNGEON_API FVector2D PositionAt(const FDungeonWorldProjectile& Projectile, double AtTime);
CODEXDUNGEON_API FDungeonWorldProjectileContact QueryContact(const FDungeonWorldProjectile& Projectile,
    double FromTime, double ToTime, const TArray<FDungeonKnightBody>& Bodies,
    const TArray<FDungeonWorldWeaponHitReceipt>& Receipts, ADungeonFighter* Owner, UWorld* World,
    TFunctionRef<bool(const FDungeonKnightBody&,double)> DamageAdmission);
}
