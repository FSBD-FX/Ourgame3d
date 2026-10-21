#pragma once
#include "CoreMinimal.h"
#include "DungeonEquipmentInventory.h"

class ADungeonFighter;
class ADungeonGameMode;

enum class EDungeonEquipmentRunConfig { IntegrationPreview, FirstBatch };
enum class EDungeonEquipmentActionKind { None, PickupWeapon, PickupArmor, SwitchWeapon };
enum class EDungeonEquipmentFailure
{
    None, Unbound, Busy, NotGrounded, Moving, NoTarget, NotInRange, NoLineOfSight,
    SelectionRequired, InvalidSlot, InvalidSource, SourceConflict, StaleState,
    NoDropPoint, NotSafe, InvalidRequest, Unsupported, InternalConsistency
};

struct FDungeonEquipmentAffixView
{
    FString Id;
    int32 Magnitude = 0;
    DungeonEquipmentStats::FQuantile OriginalQ;
};

struct FDungeonEquipmentSlotView
{
    uint64 InstanceId = 0, Version = 0;
    FString ContentId;
    int32 Grade = 0, Tier = 0;
    DungeonEquipmentStats::EPackage Package = DungeonEquipmentStats::EPackage::None;
    TArray<FDungeonEquipmentAffixView> Affixes;
    double Ammo = 0.0, CooldownDeadline = 0.0;
};

struct FDungeonEquipmentActionView
{
    EDungeonEquipmentActionKind Kind = EDungeonEquipmentActionKind::None;
    bool Active = false;
    uint64 ActionId = 0, OperationId = 0, SourceId = 0, InstanceId = 0;
    int32 Slot = -1;
    double Start = 0.0, Deadline = 0.0;
};

struct FDungeonEquipmentSourceView
{
    uint64 SourceId = 0, InstanceId = 0, Version = 0, RoomInstanceId = 0;
    FString LogicalKey;
    FVector2D Position = FVector2D::ZeroVector;
    bool Settled = false, Consumed = false;
    DungeonEquipmentInventory::FItem Item;
};

struct FDungeonEquipmentRegistration
{
    bool Accepted = false, Replayed = false;
    uint64 SourceId = 0, InstanceId = 0;
    EDungeonEquipmentFailure Failure = EDungeonEquipmentFailure::Unbound;
    bool Ok() const { return Accepted; }
};

struct FDungeonEquipmentView
{
    bool Bound = false;
    EDungeonEquipmentRunConfig Config = EDungeonEquipmentRunConfig::IntegrationPreview;
    FGuid RunGuid;
    uint64 RunAlias = 0, OwnerId = 0, RoomInstanceId = 0, Revision = 0;
    int32 ActiveSlot = 0;
    std::array<FDungeonEquipmentSlotView,3> Slots;
    uint64 SelectedSourceId = 0;
    bool NeedsSlotSelection = false;
    int32 SelectionSlot = -1;
    FDungeonEquipmentActionView Action;
    EDungeonEquipmentFailure LastFailure = EDungeonEquipmentFailure::Unbound;
    FString FailureText;
    DungeonEquipmentStats::FResolved Stats;
    uint64 NextInstanceId = 1, NextSourceId = 1, NextOperationId = 1, NextEquipmentActionId = 1;
    uint64 NextRuntimeReceiptId = 1, NextImportReceiptId = 1, NextFocusReceiptId = 1;
    uint64 CombatSeed = 0, NextCritDraw = 0;
    TArray<FString> DeveloperCatalogIds;
};

// Accepted combat-lock receipts retain the resolved draw; capture/restore must
// never sample the combat stream or collapse melee/weapon-action domains.
struct FDungeonEquipmentCritReceipt
{
    bool WeaponAction = false;
    uint64 ActionId = 0, EventId = 0, Draw = 0, Bits = 0;
    double AtTime = 0, ChancePct = 0;
    bool Critical = false;
};

// Value snapshot of this owner only. It does not restore a Fighter, a world,
// durable semantic transaction or the complete D13 Run.
struct FDungeonEquipmentRuntimeSnapshot
{
    uint32 Schema = 1;
    FDungeonEquipmentView View;
    bool HasInventory = false;
    DungeonEquipmentInventory::FState InventoryState;
    TArray<FDungeonEquipmentSourceView> Sources;
    DungeonEquipmentInventory::FPlan PendingPlan;
    FVector2D PendingDropPosition = FVector2D::ZeroVector;
    bool PendingHasDrop = false;
    TArray<FDungeonEquipmentCritReceipt> CritReceipts;
};

// RunGuid is the complete scope; numeric IDs are separate domains within it.
// This adapter owns Run-local facts, without claiming disk persistence.
class CODEXDUNGEON_API FDungeonEquipmentRuntime
{
public:
    FDungeonEquipmentRuntimeSnapshot Capture() const;
    // Schema 1 installs only a validated bound owner; rejection changes nothing.
    // Actor/clock/cross-owner checks and durable publication belong to the Run adapter.
    bool Restore(const FDungeonEquipmentRuntimeSnapshot& Snapshot, FString& Diagnostic);
    const FDungeonEquipmentView& GetView() const { return View; }
    const TArray<FDungeonEquipmentSourceView>& GetSources() const { return Sources; }
    const DungeonEquipmentInventory::FState* GetInventoryState() const { return Inventory ? &Inventory->State() : nullptr; }
private:
    friend class ADungeonFighter;
    friend class ADungeonGameMode;
    FDungeonEquipmentView View;
    TArray<FDungeonEquipmentSourceView> Sources;
    TUniquePtr<DungeonEquipmentInventory::FEquipmentInventory> Inventory;
    DungeonEquipmentInventory::FPlan PendingPlan;
    FVector2D PendingDropPosition = FVector2D::ZeroVector;
    bool PendingHasDrop = false;
    TArray<FDungeonEquipmentCritReceipt> CritReceipts;
    const DungeonEquipmentInventory::FItem* FindItem(uint64 Id) const;
    FDungeonEquipmentSourceView* FindSource(uint64 Id);
    void RefreshView();
    void Fail(EDungeonEquipmentFailure Failure, const TCHAR* Text);
    uint64 PeekCritBits() const;
    bool PeekCritical() const;
    void ObserveCritLock(bool WeaponAction, uint64 ActionId, uint64 EventId, double AtTime, bool Critical);
};
