#include "DungeonEquipmentRuntime.h"
#include "DungeonRoomLayout.h"
#include <cmath>
#include <limits>

namespace
{
namespace OwnerInv = DungeonEquipmentInventory;
namespace OwnerStats = DungeonEquipmentStats;
bool SameOwnerItem(const OwnerInv::FItem& A,const OwnerInv::FItem& B)
{
    if(A.InstanceId!=B.InstanceId||A.Version!=B.Version||A.ContentId!=B.ContentId||A.Grade!=B.Grade
        ||A.Package!=B.Package||A.Tier!=B.Tier||A.Ammo!=B.Ammo||A.SkillCooldownDeadline!=B.SkillCooldownDeadline
        ||A.Affixes.size()!=B.Affixes.size())return false;
    for(std::size_t I=0;I<A.Affixes.size();++I)
    {
        const auto& X=A.Affixes[I];const auto& Y=B.Affixes[I];
        if(X.Id!=Y.Id||X.Magnitude!=Y.Magnitude||X.OriginalQ.Numerator!=Y.OriginalQ.Numerator
            ||X.OriginalQ.Denominator!=Y.OriginalQ.Denominator)return false;
    }
    return true;
}
bool SameOwnerPlan(const OwnerInv::FPlan& A,const OwnerInv::FPlan& B,bool CompareBase=true)
{
    return A.Action==B.Action&&A.Slot==B.Slot&&(!CompareBase||A.BaseRevision==B.BaseRevision)&&A.SourceId==B.SourceId
        &&A.SourceVersion==B.SourceVersion&&A.InstanceId==B.InstanceId&&A.InstanceVersion==B.InstanceVersion&&A.ReplacedId==B.ReplacedId;
}
bool SameOwnerPlanAfterRegistrations(const OwnerInv::FPlan& Original,const OwnerInv::FPlan& Reprepared,const OwnerInv::FState& Validated)
{
    if(Original.BaseRevision>Reprepared.BaseRevision||!SameOwnerPlan(Original,Reprepared,false))return false;
    // Inventory::Restore already proved that each revision has exactly one
    // replayable cause. Between prepare and commit, public source registration
    // can add an unrelated item while leaving every affected plan fact intact.
    // Another equipment operation or ammo/CD update is not that exception.
    for(const auto& O:Validated.Operations)
        if(O.Result.Revision>Original.BaseRevision&&O.Result.Revision<=Reprepared.BaseRevision)return false;
    for(const auto& R:Validated.RuntimeUpdates)
        if(R.BaseRevision>=Original.BaseRevision&&R.BaseRevision<Reprepared.BaseRevision)return false;
    return true;
}
bool SameOwnerSlot(const FDungeonEquipmentSlotView& A,const FDungeonEquipmentSlotView& B)
{
    if(A.InstanceId!=B.InstanceId||A.Version!=B.Version||A.ContentId!=B.ContentId||A.Grade!=B.Grade
        ||A.Tier!=B.Tier||A.Package!=B.Package||A.Ammo!=B.Ammo||A.CooldownDeadline!=B.CooldownDeadline
        ||A.Affixes.Num()!=B.Affixes.Num())return false;
    for(int32 I=0;I<A.Affixes.Num();++I)
    {
        const auto& X=A.Affixes[I];const auto& Y=B.Affixes[I];
        if(X.Id!=Y.Id||X.Magnitude!=Y.Magnitude||X.OriginalQ.Numerator!=Y.OriginalQ.Numerator
            ||X.OriginalQ.Denominator!=Y.OriginalQ.Denominator)return false;
    }
    return true;
}
bool SameOwnerStats(const OwnerStats::FResolved& A,const OwnerStats::FResolved& B)
{
    if(!A.Ok()||!B.Ok()||A.RawBonus.Values!=B.RawBonus.Values||A.Final.Values!=B.Final.Values)return false;
    const double X[]={A.DamageMultiplier,A.StaggerMultiplier,A.ActionTimeScale,A.ReachMultiplier,A.CritChancePct,A.CritMultiplier,
        A.SkillCooldownMultiplier,A.FocusCostMultiplier,A.ReloadSeconds,A.PrimaryFocusCost,A.SkillFocusCost,A.Armor,A.Ward,A.Poise,
        A.PhysicalMitigation,A.MagicMitigation,A.MaxHP,A.CurrentHP,A.IdleMoveMultiplier,A.MoveSpeed,A.FocusRegen,A.FocusDelay,
        A.HealingMultiplier,A.PhysicalVulnerabilityMultiplier,A.MagicVulnerabilityMultiplier};
    const double Y[]={B.DamageMultiplier,B.StaggerMultiplier,B.ActionTimeScale,B.ReachMultiplier,B.CritChancePct,B.CritMultiplier,
        B.SkillCooldownMultiplier,B.FocusCostMultiplier,B.ReloadSeconds,B.PrimaryFocusCost,B.SkillFocusCost,B.Armor,B.Ward,B.Poise,
        B.PhysicalMitigation,B.MagicMitigation,B.MaxHP,B.CurrentHP,B.IdleMoveMultiplier,B.MoveSpeed,B.FocusRegen,B.FocusDelay,
        B.HealingMultiplier,B.PhysicalVulnerabilityMultiplier,B.MagicVulnerabilityMultiplier};
    for(std::size_t I=0;I<UE_ARRAY_COUNT(X);++I)if(!std::isfinite(X[I])||!std::isfinite(Y[I])||X[I]!=Y[I])return false;
    return true;
}
bool OwnerGroundPoint(FVector2D P)
{
    return std::isfinite(P.X)&&std::isfinite(P.Y)&&P.X>=DungeonRoomLayout::MinX&&P.X<=DungeonRoomLayout::MaxX
        &&P.Y>=DungeonRoomLayout::MinY&&P.Y<=DungeonRoomLayout::MaxY;
}
uint64 ResolvedOwnerCritBits(uint64 Seed,uint64 Draw)
{
    // Verify a saved resolved draw. No cursor increment, live owner or RNG call.
    uint64 Value=(Seed^0x435249545f763031ULL)+(Draw+1)*0x9e3779b97f4a7c15ULL;
    Value=(Value^(Value>>30))*0xbf58476d1ce4e5b9ULL;
    Value=(Value^(Value>>27))*0x94d049bb133111ebULL;
    return Value^(Value>>31);
}
}

FDungeonEquipmentRuntimeSnapshot FDungeonEquipmentRuntime::Capture() const
{
    FDungeonEquipmentRuntimeSnapshot S;S.View=View;S.HasInventory=bool(Inventory);
    if(Inventory)S.InventoryState=Inventory->Capture();
    S.Sources=Sources;S.PendingPlan=PendingPlan;S.PendingDropPosition=PendingDropPosition;
    S.PendingHasDrop=PendingHasDrop;S.CritReceipts=CritReceipts;return S;
}
bool FDungeonEquipmentRuntime::Restore(const FDungeonEquipmentRuntimeSnapshot& S,FString& Diagnostic)
{
    const auto Reject=[&Diagnostic](const TCHAR* Why){Diagnostic=Why;return false;};
    // This schema installs a bound owner. An unbound observation is not a reset
    // command and must not erase a currently bound owner.
    if(S.Schema!=1||!S.View.Bound||!S.HasInventory)return Reject(TEXT("Unknown schema or missing bound inventory owner"));
    const auto& V=S.View;const auto& I=S.InventoryState;const auto& A=V.Action;const auto& P=S.PendingPlan;
    if((V.Config!=EDungeonEquipmentRunConfig::IntegrationPreview&&V.Config!=EDungeonEquipmentRunConfig::FirstBatch)
        ||!V.RunGuid.IsValid()||!V.RunAlias||!V.OwnerId||!V.RoomInstanceId||V.RunAlias!=I.RunId||V.OwnerId!=I.OwnerId
        ||static_cast<uint32>(V.LastFailure)>static_cast<uint32>(EDungeonEquipmentFailure::InternalConsistency))
        return Reject(TEXT("Invalid owner identity, configuration or failure domain"));
    if(!V.NextInstanceId||!V.NextSourceId||!V.NextOperationId||!V.NextEquipmentActionId
        ||!V.NextRuntimeReceiptId||!V.NextImportReceiptId||!V.NextFocusReceiptId)
        return Reject(TEXT("A persistent owner ID cursor is zero"));
    const TCHAR* Catalog[]={TEXT("WPN-SWD-001"),TEXT("WPN-GSW-001"),TEXT("WPN-SPR-001"),TEXT("WPN-XBW-001"),TEXT("WPN-STF-001"),
        TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")};
    if(V.DeveloperCatalogIds.Num()!=int32(UE_ARRAY_COUNT(Catalog)))return Reject(TEXT("Unknown bound owner content catalog"));
    for(int32 N=0;N<V.DeveloperCatalogIds.Num();++N)
        if(V.DeveloperCatalogIds[N]!=Catalog[N])return Reject(TEXT("Bound owner catalog differs from this schema"));

    FDungeonEquipmentRuntime Candidate;
    Candidate.View=V;Candidate.Sources=S.Sources;Candidate.PendingPlan=P;
    Candidate.PendingDropPosition=S.PendingDropPosition;Candidate.PendingHasDrop=S.PendingHasDrop;Candidate.CritReceipts=S.CritReceipts;
    // The pure inventory validates its complete revision replay, initial item,
    // instance locations, source history, operations and runtime receipts.
    Candidate.Inventory=MakeUnique<OwnerInv::FEquipmentInventory>(I.RunId,I.OwnerId,I.InitialStarter);
    if(!Candidate.Inventory->Restore(I))return Reject(TEXT("Inventory rejected its complete saved state"));
    uint64 MaxInstance=0,MaxSource=0,LastOperation=0;
    for(const auto& Item:I.Items)
    {
        if(!V.DeveloperCatalogIds.Contains(FString(UTF8_TO_TCHAR(Item.ContentId.c_str()))))return Reject(TEXT("Unknown item in bound owner catalog"));
        MaxInstance=FMath::Max(MaxInstance,uint64(Item.InstanceId));
    }
    for(const auto& Source:I.Sources)MaxSource=FMath::Max(MaxSource,uint64(Source.SourceId));
    for(const auto& Operation:I.Operations)
    {
        if(LastOperation==TNumericLimits<uint64>::Max()||Operation.OperationId!=LastOperation+1)
            return Reject(TEXT("Owner operation history has an unexplained ID gap"));
        LastOperation=Operation.OperationId;
    }
    if(V.NextInstanceId<=MaxInstance||V.NextSourceId<=MaxSource||LastOperation==TNumericLimits<uint64>::Max()
        ||V.NextOperationId!=LastOperation+1||V.NextRuntimeReceiptId!=I.NextRuntimeReceiptId)
        return Reject(TEXT("Owner cursors alias or disagree with committed inventory history"));
    if(S.Sources.Num()!=static_cast<int64>(I.Sources.size()))return Reject(TEXT("External and inventory source sets differ"));
    for(int32 N=0;N<S.Sources.Num();++N)
    {
        const auto& World=S.Sources[N];const OwnerInv::FSource* Known=nullptr;
        for(const auto& Source:I.Sources)if(Source.SourceId==World.SourceId){Known=&Source;break;}
        if(!World.SourceId||!World.InstanceId||!World.Version||!World.RoomInstanceId||World.RoomInstanceId>V.RoomInstanceId
            ||World.LogicalKey.IsEmpty()||!OwnerGroundPoint(World.Position)||!Known||World.InstanceId!=Known->InstanceId
            ||World.Version!=Known->Version||World.Consumed==Known->Available)
            return Reject(TEXT("External source identity, position or availability disagrees with inventory"));
        const auto* Item=Candidate.FindItem(World.InstanceId);
        if(!Item||!SameOwnerItem(World.Item,*Item))return Reject(TEXT("External source item is not its current inventory instance"));
        for(int32 J=0;J<N;++J)
            if(S.Sources[J].SourceId==World.SourceId||(S.Sources[J].RoomInstanceId==World.RoomInstanceId&&S.Sources[J].LogicalKey==World.LogicalKey))
                return Reject(TEXT("External source stable identity or room/logical key is duplicated"));
    }
    Candidate.RefreshView();
    if(Candidate.View.Revision!=V.Revision||Candidate.View.ActiveSlot!=V.ActiveSlot
        ||Candidate.View.NextRuntimeReceiptId!=V.NextRuntimeReceiptId)return Reject(TEXT("Inventory view mirrors are stale"));
    for(int32 Slot=0;Slot<3;++Slot)
        if(!SameOwnerSlot(Candidate.View.Slots[Slot],V.Slots[Slot]))return Reject(TEXT("An equipment slot mirror differs from the owned instance"));
    // CurrentHP is a saved resolution mirror, not an observation of Pawn HP.
    // Re-resolve with that mirror and the existing adapter's default context.
    const auto ExpectedStats=Candidate.Inventory->ResolveStats({},V.Stats.CurrentHP);
    if(!SameOwnerStats(ExpectedStats,V.Stats))return Reject(TEXT("Resolved stats are nonfinite or disagree with inventory/default context"));

    if(!OwnerGroundPoint(S.PendingDropPosition))return Reject(TEXT("Pending drop point is invalid"));
    const auto* Selected=V.SelectedSourceId?Candidate.FindSource(V.SelectedSourceId):nullptr;
    if(V.SelectedSourceId&&!Selected)return Reject(TEXT("Selected equipment source is missing"));
    if(V.NeedsSlotSelection)
    {
        if(A.Active||!Selected||Selected->Consumed||Selected->RoomInstanceId!=V.RoomInstanceId
            ||Candidate.Inventory->PreparePickup(Selected->SourceId).Error!=OwnerInv::EError::SelectionRequired)
            return Reject(TEXT("Slot-selection layer has no valid pending source"));
        const auto* Template=OwnerStats::FindTemplate(Selected->Item.ContentId);
        if(!Template||(Template->Kind==OwnerStats::EKind::Armor?V.SelectionSlot!=2:(V.SelectionSlot<0||V.SelectionSlot>1)))
            return Reject(TEXT("Selection slot is incompatible with the source kind"));
    }
    else if(V.SelectionSlot!=-1)return Reject(TEXT("An inactive selection layer retains a selected slot"));

    if(static_cast<uint32>(A.Kind)>static_cast<uint32>(EDungeonEquipmentActionKind::SwitchWeapon)
        ||!std::isfinite(A.Start)||!std::isfinite(A.Deadline)||A.Start<0||A.Deadline<0)
        return Reject(TEXT("Unknown equipment action or invalid action clock"));
    if(A.Kind==EDungeonEquipmentActionKind::None)
    {
        if(A.Active||A.ActionId||A.OperationId||A.SourceId||A.InstanceId||A.Slot!=-1||A.Start!=0||A.Deadline!=0
            ||V.NextEquipmentActionId!=1||!SameOwnerPlan(P,OwnerInv::FPlan{})||S.PendingHasDrop||S.PendingDropPosition!=FVector2D::ZeroVector)
            return Reject(TEXT("Empty action has unexplained accepted-action residue"));
    }
    else
    {
        const bool Switching=A.Kind==EDungeonEquipmentActionKind::SwitchWeapon;
        const bool Armor=A.Kind==EDungeonEquipmentActionKind::PickupArmor;
        if(!A.ActionId||A.ActionId==TNumericLimits<uint64>::Max()||V.NextEquipmentActionId!=A.ActionId+1
            ||!A.OperationId||A.OperationId>V.NextOperationId||!A.InstanceId||A.InstanceId!=P.InstanceId||A.Slot!=P.Slot
            ||(Armor?A.Slot!=2:(A.Slot<0||A.Slot>1))||A.Deadline!=A.Start+(Armor?.50:.35)
            ||P.Action!=(Switching?OwnerInv::EAction::Switch:OwnerInv::EAction::Pickup)
            ||!P.BaseRevision||P.BaseRevision>I.Revision||!P.InstanceVersion||S.PendingHasDrop!=(P.ReplacedId!=0))
            return Reject(TEXT("Accepted action and its saved pending plan disagree"));
        const auto* Item=Candidate.FindItem(P.InstanceId);const auto* Template=Item?OwnerStats::FindTemplate(Item->ContentId):nullptr;
        if(!Item||P.InstanceVersion>Item->Version||!Template||(Template->Kind==OwnerStats::EKind::Armor)!=Armor)
            return Reject(TEXT("Pending instance/version/kind is missing or incompatible"));
        if(Switching)
        {
            if(A.SourceId||P.SourceId||P.SourceVersion||P.ReplacedId||S.PendingHasDrop)
                return Reject(TEXT("Weapon switch cannot create a source or replacement drop"));
        }
        else
        {
            const OwnerInv::FSource* Source=nullptr;for(const auto& W:I.Sources)if(W.SourceId==P.SourceId){Source=&W;break;}
            if(!A.SourceId||A.SourceId!=P.SourceId||!Source||Source->InstanceId!=P.InstanceId||P.SourceVersion!=1
                ||Source->CreatedRevision>P.BaseRevision||Source->SpawnItem.Version!=P.InstanceVersion)
                return Reject(TEXT("Pending pickup has no matching historical source"));
            if(P.ReplacedId)
            {
                const auto* Replaced=Candidate.FindItem(P.ReplacedId);const auto* Definition=Replaced?OwnerStats::FindTemplate(Replaced->ContentId):nullptr;
                if(!Replaced||P.ReplacedId==P.InstanceId||!Definition||(Definition->Kind==OwnerStats::EKind::Armor)!=Armor)
                    return Reject(TEXT("Pending replacement references an incompatible old instance"));
            }
        }
        const OwnerInv::FOperation* Committed=nullptr;for(const auto& O:I.Operations)if(O.OperationId==A.OperationId){Committed=&O;break;}
        if(A.Active)
        {
            if(A.OperationId!=V.NextOperationId||Committed||V.NeedsSlotSelection)
                return Reject(TEXT("Active equipment action is already committed or conflicts with selection"));
            const auto Prepared=Switching?Candidate.Inventory->PrepareSwitch():Candidate.Inventory->PreparePickup(P.SourceId,P.Slot);
            if(!Prepared.Ok()||!SameOwnerPlanAfterRegistrations(P,Prepared.Plan,I))return Reject(TEXT("Active pending plan affected facts changed beyond unrelated registration"));
            if(!Switching)
            {
                const auto* Source=Candidate.FindSource(A.SourceId);
                if(!Source||Source->Consumed||!Source->Settled||Source->RoomInstanceId!=V.RoomInstanceId||V.SelectedSourceId!=A.SourceId)
                    return Reject(TEXT("Active pickup no longer binds its selected current-room source"));
            }
        }
        else
        {
            // Cancel preserves an unspent OperationId and old plan/drop fields.
            // Commit may record a later prepare revision after only unrelated
            // registrations; the owner's original plan is preserved unchanged.
            // Later registrations/receipts after that commit are also legal.
            if(Committed?!SameOwnerPlanAfterRegistrations(P,Committed->Request,I):A.OperationId!=V.NextOperationId)
                return Reject(TEXT("Inactive action is neither its recorded commit nor an unspent cancellation"));
        }
    }
    if(V.NextCritDraw!=static_cast<uint64>(S.CritReceipts.Num()))return Reject(TEXT("Crit cursor has missing or extra resolved draws"));
    double PreviousTime=-1.;
    for(int32 N=0;N<S.CritReceipts.Num();++N)
    {
        const auto& R=S.CritReceipts[N];
        if(!R.ActionId||!R.EventId||R.ActionId==TNumericLimits<uint64>::Max()||R.EventId==TNumericLimits<uint64>::Max()
            ||R.Draw!=static_cast<uint64>(N)||R.Bits!=ResolvedOwnerCritBits(V.CombatSeed,R.Draw)||!std::isfinite(R.AtTime)
            ||R.AtTime<0||R.AtTime<PreviousTime||!std::isfinite(R.ChancePct)||R.ChancePct<0||R.ChancePct>100
            ||R.Critical!=(double(R.Bits>>11)*(1.0/9007199254740992.0)*100.0<R.ChancePct))
            return Reject(TEXT("Crit receipt has invalid seed/draw/bits/chance/time/outcome"));
        for(int32 J=0;J<N;++J)
        {
            const auto& Old=S.CritReceipts[J];
            if(Old.WeaponAction==R.WeaponAction&&(Old.ActionId>=R.ActionId||Old.EventId>=R.EventId))
                return Reject(TEXT("Crit action/event identity is duplicated or reversed within its domain"));
        }
        PreviousTime=R.AtTime;
    }
    // Every check above owns only Candidate. Install the complete owner once.
    View=MoveTemp(Candidate.View);Sources=MoveTemp(Candidate.Sources);Inventory=MoveTemp(Candidate.Inventory);
    PendingPlan=Candidate.PendingPlan;PendingDropPosition=Candidate.PendingDropPosition;PendingHasDrop=Candidate.PendingHasDrop;
    CritReceipts=MoveTemp(Candidate.CritReceipts);Diagnostic.Reset();return true;
}

const DungeonEquipmentInventory::FItem* FDungeonEquipmentRuntime::FindItem(uint64 Id) const
{
    if (Inventory) for (const auto& Item : Inventory->State().Items) if (Item.InstanceId == Id) return &Item;
    return nullptr;
}
FDungeonEquipmentSourceView* FDungeonEquipmentRuntime::FindSource(uint64 Id)
{
    for (auto& Source : Sources) if (Source.SourceId == Id) return &Source;
    return nullptr;
}
void FDungeonEquipmentRuntime::RefreshView()
{
    if (!Inventory) return;
    const auto& State = Inventory->State();
    View.Revision = State.Revision; View.ActiveSlot = State.ActiveSlot;
    View.NextRuntimeReceiptId = State.NextRuntimeReceiptId;
    for (int32 Slot = 0; Slot < 3; ++Slot)
    {
        auto& Out = View.Slots[Slot]; Out = {};
        const auto* Item = FindItem(Slot == 2 ? State.Armor : State.Weapons[Slot]);
        if (!Item) continue;
        Out.InstanceId = Item->InstanceId; Out.Version = Item->Version;
        Out.ContentId = UTF8_TO_TCHAR(Item->ContentId.c_str()); Out.Grade = Item->Grade;
        Out.Package = Item->Package; Out.Tier = Item->Tier;
        Out.Ammo = Item->Ammo; Out.CooldownDeadline = Item->SkillCooldownDeadline;
        for (const auto& A : Item->Affixes) Out.Affixes.Add({UTF8_TO_TCHAR(A.Id.c_str()),A.Magnitude,A.OriginalQ});
    }
    for (auto& Out : Sources)
        for (const auto& Source : State.Sources) if (Source.SourceId == Out.SourceId)
        {
            Out.Version = Source.Version; Out.Consumed = !Source.Available;
            if (const auto* Item = FindItem(Source.InstanceId)) Out.Item = *Item;
            break;
        }
}
void FDungeonEquipmentRuntime::Fail(EDungeonEquipmentFailure Failure, const TCHAR* Text)
{
    View.LastFailure = Failure; View.FailureText = Text;
}
uint64 FDungeonEquipmentRuntime::PeekCritBits() const
{
    // SplitMix64 counter stream, one explicit combat domain independent of sources.
    uint64 Value = (View.CombatSeed ^ 0x435249545f763031ULL) + (View.NextCritDraw+1)*0x9e3779b97f4a7c15ULL;
    Value = (Value^(Value>>30))*0xbf58476d1ce4e5b9ULL;
    Value = (Value^(Value>>27))*0x94d049bb133111ebULL;
    return Value^(Value>>31);
}
bool FDungeonEquipmentRuntime::PeekCritical() const
{
    const double Unit = double(PeekCritBits() >> 11) * (1.0/9007199254740992.0);
    return Unit*100.0 < View.Stats.CritChancePct;
}
void FDungeonEquipmentRuntime::ObserveCritLock(bool WeaponAction, uint64 ActionId, uint64 EventId, double AtTime, bool Critical)
{
    for (const auto& R : CritReceipts) if (R.WeaponAction == WeaponAction && R.ActionId == ActionId) return;
    ensureMsgf(Critical == PeekCritical(),TEXT("Accepted lock must use the peeked combat draw exactly once."));
    CritReceipts.Add({WeaponAction,ActionId,EventId,View.NextCritDraw,PeekCritBits(),AtTime,View.Stats.CritChancePct,Critical});
    ++View.NextCritDraw;
}
