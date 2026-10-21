#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonEquipmentRuntime.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>
#include <type_traits>

namespace
{
namespace SnapshotInv = DungeonEquipmentInventory;
namespace SnapshotStats = DungeonEquipmentStats;
using FOwnerSnapshot = FDungeonEquipmentRuntimeSnapshot;

// Test-only, fieldwise byte signature: no padding, production encoder, RNG or
// gameplay helper computes the expected round-trip value.
struct FValueSignature
{
    TArray<uint8> Bytes;
    template<class T> void Scalar(const T& V)
    {
        static_assert(std::is_arithmetic_v<T> || std::is_enum_v<T>);
        Bytes.Append(reinterpret_cast<const uint8*>(&V),sizeof(T));
    }
    void String(const std::string& V) { Scalar(uint64(V.size()));Bytes.Append(reinterpret_cast<const uint8*>(V.data()),int32(V.size())); }
    void String(const FString& V) { FTCHARToUTF8 U(*V);Scalar(uint64(U.Length()));Bytes.Append(reinterpret_cast<const uint8*>(U.Get()),U.Length()); }
    void Item(const SnapshotInv::FItem& I)
    {
        Scalar(I.InstanceId);Scalar(I.Version);String(I.ContentId);Scalar(I.Grade);Scalar(I.Package);Scalar(I.Tier);
        Scalar(uint64(I.Affixes.size()));for(const auto& A:I.Affixes)
        {String(A.Id);Scalar(A.Magnitude);Scalar(A.OriginalQ.Numerator);Scalar(A.OriginalQ.Denominator);}
        Scalar(I.Ammo);Scalar(I.SkillCooldownDeadline);
    }
    void Plan(const SnapshotInv::FPlan& P)
    {Scalar(P.Action);Scalar(P.Slot);Scalar(P.BaseRevision);Scalar(P.SourceId);Scalar(P.SourceVersion);Scalar(P.InstanceId);Scalar(P.InstanceVersion);Scalar(P.ReplacedId);}
    void Result(const SnapshotInv::FResult& R)
    {Scalar(R.Error);Scalar(R.Replayed);Scalar(R.Revision);Scalar(R.AcquiredId);Scalar(R.DroppedId);Scalar(R.DroppedSourceId);Scalar(R.ActiveSlot);}
    void Inventory(const SnapshotInv::FState& S)
    {
        Scalar(S.Schema);Scalar(S.RunId);Scalar(S.OwnerId);Scalar(S.Revision);Scalar(S.StarterId);
        for(auto W:S.Weapons)Scalar(W);Scalar(S.Armor);Scalar(S.ActiveSlot);
        Scalar(uint64(S.Items.size()));for(const auto& I:S.Items)Item(I);
        Scalar(uint64(S.Sources.size()));for(const auto& W:S.Sources)
        {Scalar(W.SourceId);Scalar(W.Version);Scalar(W.InstanceId);Scalar(W.Available);Item(W.SpawnItem);Scalar(W.CreatedRevision);}
        Scalar(uint64(S.Operations.size()));for(const auto& O:S.Operations)
        {Scalar(O.OperationId);Plan(O.Request);Scalar(O.DropSourceId);Result(O.Result);}
        Item(S.InitialStarter);Scalar(S.NextRuntimeReceiptId);Scalar(uint64(S.RuntimeUpdates.size()));
        for(const auto& R:S.RuntimeUpdates)
        {Scalar(R.ReceiptId);Scalar(R.BaseRevision);Scalar(R.InstanceId);Scalar(R.BeforeVersion);Scalar(R.AfterVersion);Scalar(R.AtTime);
            Scalar(R.BeforeAmmo);Scalar(R.Ammo);Scalar(R.BeforeCooldown);Scalar(R.SkillCooldownDeadline);Result(R.Result);}
    }
    void Stats(const SnapshotStats::FResolved& S)
    {
        Scalar(S.Error);for(auto V:S.RawBonus.Values)Scalar(V);for(auto V:S.Final.Values)Scalar(V);
        for(double V:{S.DamageMultiplier,S.StaggerMultiplier,S.ActionTimeScale,S.ReachMultiplier,S.CritChancePct,S.CritMultiplier,
            S.SkillCooldownMultiplier,S.FocusCostMultiplier,S.ReloadSeconds,S.PrimaryFocusCost,S.SkillFocusCost,
            S.Armor,S.Ward,S.Poise,S.PhysicalMitigation,S.MagicMitigation,S.MaxHP,S.CurrentHP,S.IdleMoveMultiplier,
            S.MoveSpeed,S.FocusRegen,S.FocusDelay,S.HealingMultiplier,S.PhysicalVulnerabilityMultiplier,S.MagicVulnerabilityMultiplier})Scalar(V);
    }
    void View(const FDungeonEquipmentView& V)
    {
        Scalar(V.Bound);Scalar(V.Config);Scalar(V.RunGuid.A);Scalar(V.RunGuid.B);Scalar(V.RunGuid.C);Scalar(V.RunGuid.D);
        Scalar(V.RunAlias);Scalar(V.OwnerId);Scalar(V.RoomInstanceId);Scalar(V.Revision);Scalar(V.ActiveSlot);
        for(const auto& S:V.Slots)
        {
            Scalar(S.InstanceId);Scalar(S.Version);String(S.ContentId);Scalar(S.Grade);Scalar(S.Tier);Scalar(S.Package);
            Scalar(uint64(S.Affixes.Num()));for(const auto& A:S.Affixes)
            {String(A.Id);Scalar(A.Magnitude);Scalar(A.OriginalQ.Numerator);Scalar(A.OriginalQ.Denominator);}
            Scalar(S.Ammo);Scalar(S.CooldownDeadline);
        }
        Scalar(V.SelectedSourceId);Scalar(V.NeedsSlotSelection);Scalar(V.SelectionSlot);
        const auto& A=V.Action;Scalar(A.Kind);Scalar(A.Active);Scalar(A.ActionId);Scalar(A.OperationId);Scalar(A.SourceId);
        Scalar(A.InstanceId);Scalar(A.Slot);Scalar(A.Start);Scalar(A.Deadline);Scalar(V.LastFailure);String(V.FailureText);Stats(V.Stats);
        Scalar(V.NextInstanceId);Scalar(V.NextSourceId);Scalar(V.NextOperationId);Scalar(V.NextEquipmentActionId);
        Scalar(V.NextRuntimeReceiptId);Scalar(V.NextImportReceiptId);Scalar(V.NextFocusReceiptId);Scalar(V.CombatSeed);Scalar(V.NextCritDraw);
        Scalar(uint64(V.DeveloperCatalogIds.Num()));for(const auto& Id:V.DeveloperCatalogIds)String(Id);
    }
    void Snapshot(const FOwnerSnapshot& S)
    {
        Scalar(S.Schema);View(S.View);Scalar(S.HasInventory);Inventory(S.InventoryState);
        Scalar(uint64(S.Sources.Num()));for(const auto& W:S.Sources)
        {Scalar(W.SourceId);Scalar(W.InstanceId);Scalar(W.Version);Scalar(W.RoomInstanceId);String(W.LogicalKey);
            Scalar(W.Position.X);Scalar(W.Position.Y);Scalar(W.Settled);Scalar(W.Consumed);Item(W.Item);}
        Plan(S.PendingPlan);Scalar(S.PendingDropPosition.X);Scalar(S.PendingDropPosition.Y);Scalar(S.PendingHasDrop);
        Scalar(uint64(S.CritReceipts.Num()));for(const auto& R:S.CritReceipts)
        {Scalar(R.WeaponAction);Scalar(R.ActionId);Scalar(R.EventId);Scalar(R.Draw);Scalar(R.Bits);Scalar(R.AtTime);Scalar(R.ChancePct);Scalar(R.Critical);}
    }
};
TArray<uint8> Signature(const FOwnerSnapshot& S) { FValueSignature V;V.Snapshot(S);return V.Bytes; }
bool RoundTrip(FAutomationTestBase& T,const FOwnerSnapshot& S,const TCHAR* Label)
{
    FDungeonEquipmentRuntime Other;FString Why;
    if(!T.TestTrue(*(FString(Label)+TEXT(" independently owned runtime accepts complete candidate")),Other.Restore(S,Why)))return false;
    T.TestTrue(*(FString(Label)+TEXT(" all outer/inner fields survive exact value round trip")),Signature(S)==Signature(Other.Capture()));
    return true;
}
struct FSnapshotWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;
    ~FSnapshotWorld(){if(World)World->DestroyWorld(false);}
    bool Create()
    {
        if(!GEngine)return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return false;World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;
        URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));if(!World->SetGameMode(URL))return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();if(!Game||!Player)return false;
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        Game->bWaitingForStart=false;Game->bGameOver=false;
        return Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)&&Player->IsEquipmentBound()
            &&Game->GetEquipmentInventoryState()&&Game->GetEquipmentView().Bound;
    }
    bool AdvanceTo(double At)
    {
        for(int N=0;N<16&&Game->GetSimulationTime()<At;++N)
        {
            const double Left=At-Game->GetSimulationTime();float Step=float(Left);if(double(Step)>Left)Step=std::nextafter(Step,0.f);
            if(!(Step>0.f))return false;const double Before=Game->GetSimulationTime();Game->Tick(Step);
            if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
    const SnapshotInv::FState& Inventory()const{return *Game->GetEquipmentInventoryState();}
    FDungeonEquipmentRegistration Register(const char* Content,double Ammo=0.,bool Affixed=false)
    {
        SnapshotInv::FItem I;I.ContentId=Content;I.Ammo=Ammo;
        if(Affixed){I.Tier=5;I.Package=SnapshotStats::EPackage::Beneficial;I.Affixes={{"AFF-P-017",25,{9,10}}};}
        return Game->RegisterEquipmentSource(FString::Printf(TEXT("snapshot.actual.source.%llu"),Game->GetEquipmentView().NextSourceId),I,{40,0});
    }
    bool Pickup(uint64 Source,int32 Slot=-1)
    {
        if(!Game->SelectEquipmentSource(Source))return false;Game->TryInteractEquipment();
        if(Game->GetEquipmentView().NeedsSlotSelection)
            return Slot>=0&&Game->ConfirmEquipmentSlot(Slot,true)&&Game->GetEquipmentView().Action.Active;
        return Game->GetEquipmentView().Action.Active;
    }
    bool Finish(){return AdvanceTo(Player->GetEquipmentActionDeadline());}
    FOwnerSnapshot Capture()const{return Game->CaptureEquipmentSnapshot();}
    bool CaptureObserved(FAutomationTestBase& T,const FOwnerSnapshot& S,const TCHAR* Label)const
    {
        const auto& V=Game->GetEquipmentView();
        const bool Has=T.TestTrue(*(FString(Label)+TEXT(" captures actual bound owner and inventory")),S.Schema==1&&S.HasInventory&&S.View.Bound
            &&S.View.RunGuid==V.RunGuid&&S.View.OwnerId==V.OwnerId&&S.View.RoomInstanceId==V.RoomInstanceId);
        if(!Has)return false;
        T.TestTrue(*(FString(Label)+TEXT(" capture equals independent live inventory and public source facts")),
            S.InventoryState.Revision==Inventory().Revision&&S.InventoryState.Weapons==Inventory().Weapons
            &&S.InventoryState.Operations.size()==Inventory().Operations.size()&&S.InventoryState.RuntimeUpdates.size()==Inventory().RuntimeUpdates.size()
            &&S.Sources.Num()==Game->GetEquipmentSources().Num()&&S.View.Action.Active==V.Action.Active
            &&S.View.Action.ActionId==V.Action.ActionId&&S.View.Action.Deadline==V.Action.Deadline);
        return true;
    }
    bool ResourcesAndTwoCritDomains(FAutomationTestBase& T)
    {
        Player->BeginAttack();const auto Sword=Player->GetMeleeCombatState().Action;
        if(!T.TestTrue(TEXT("Real starter melee action begins before capture"),Sword.Active&&Sword.AttackId==1)
            ||!T.TestTrue(TEXT("Real melee reaches lock and finishes"),AdvanceTo(Sword.LockTime)&&AdvanceTo(Sword.End)))return false;
        const auto X=Register("WPN-XBW-001",1.);
        if(!T.TestTrue(TEXT("Real E acquires loaded crossbow"),X.Ok()&&Pickup(X.SourceId)&&Finish()))return false;
        Player->BeginAttack();const auto Shot=Player->GetWeaponActionsState().Action;
        if(!T.TestTrue(TEXT("Real crossbow primary begins with acquired instance"),Shot.Active&&Shot.Type==DungeonWeaponActions::EAction::Primary
            &&Shot.InstanceId==X.InstanceId&&Shot.ActionId==1)||!T.TestTrue(TEXT("Real shot/auto reload advances at exact endpoint"),AdvanceTo(Shot.End)))return false;
        const auto Reload=Player->GetWeaponActionsState().Action;
        if(!T.TestTrue(TEXT("Real empty magazine starts automatic reload"),Reload.Active&&Reload.Type==DungeonWeaponActions::EAction::Reload
            &&Reload.Start==Shot.End)||!T.TestTrue(TEXT("Real reload completes through central GameMode tick"),AdvanceTo(Reload.End)))return false;
        const auto* Actual=Player->GetWeaponActionsState().Instances.empty()?nullptr:&Player->GetWeaponActionsState().Instances.back();
        return T.TestTrue(TEXT("Actual WA and inventory refilled same crossbow with runtime history"),Actual&&Actual->InstanceId==X.InstanceId&&Actual->Ammo==1.
            &&Game->GetEquipmentView().Slots[1].Ammo==1.&&!Inventory().RuntimeUpdates.empty()
            &&Game->GetEquipmentView().NextCritDraw==2&&Player->GetWeaponActionsState().WeaponRuntimeHistory.size()>=2);
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentSnapshotPendingActions,
    "CodexDungeon.Content.RunOwnerSnapshot.EquipmentPendingActionsAndDeepValues",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FEquipmentSnapshotPendingActions::RunTest(const FString& Parameters)
{
    FSnapshotWorld F;if(!TestTrue(TEXT("Actual bound GameMode fixture initializes"),F.Create()))return false;
    const auto X=F.Register("WPN-XBW-001",1.);
    if(!TestTrue(TEXT("Normal interaction starts empty-slot weapon pickup"),X.Ok()&&F.Pickup(X.SourceId)))return false;
    const auto A=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Tick reaches real pickup midpoint"),F.AdvanceTo(A.Start+.125)))return false;
    const auto Pick=F.Capture();
    if(F.CaptureObserved(*this,Pick,TEXT("Pending weapon")))
    {
        TestTrue(TEXT("Pending weapon has independent .35 deadline and reserved identities, no premature ownership"),
            Pick.View.Action.Kind==EDungeonEquipmentActionKind::PickupWeapon&&Pick.View.Action.Deadline==A.Start+.35
            &&Pick.PendingPlan.Action==SnapshotInv::EAction::Pickup&&Pick.PendingPlan.SourceId==X.SourceId
            &&Pick.PendingPlan.InstanceId==X.InstanceId&&Pick.PendingPlan.Slot==1&&!Pick.PendingHasDrop
            &&Pick.InventoryState.Weapons[1]==0&&Pick.View.NextOperationId==1&&Pick.View.NextEquipmentActionId==2);
        RoundTrip(*this,Pick,TEXT("Pending weapon"));
    }
    if(!TestTrue(TEXT("Actual weapon finishes normally"),F.Finish()))return false;
    TestTrue(TEXT("Earlier owning snapshot is unchanged after real owner commit"),!Pick.HasInventory||Pick.InventoryState.Weapons[1]==0);
    const auto Armor=F.Register("ARM-LGT-001",0.,true);
    if(!TestTrue(TEXT("Normal interaction starts real affixed body pickup"),Armor.Ok()&&F.Pickup(Armor.SourceId)))return false;
    const auto BodyA=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Tick reaches real armor midpoint"),F.AdvanceTo(BodyA.Start+.25)))return false;
    const auto Body=F.Capture();
    if(F.CaptureObserved(*this,Body,TEXT("Pending armor")))
    {
        TestTrue(TEXT("Armor keeps .50 deadline, body slot and original affix quantile"),Body.View.Action.Kind==EDungeonEquipmentActionKind::PickupArmor
            &&Body.View.Action.Deadline==BodyA.Start+.5&&Body.PendingPlan.Slot==2&&Body.InventoryState.Armor==0
            &&Body.Sources.Last().Item.Affixes.size()==1&&Body.Sources.Last().Item.Affixes[0].OriginalQ.Numerator==9
            &&Body.Sources.Last().Item.Affixes[0].OriginalQ.Denominator==10);
        RoundTrip(*this,Body,TEXT("Pending armor"));
    }
    if(!TestTrue(TEXT("Armor finishes, then normal weapon-switch entry begins"),F.Finish()&&F.Game->TrySwitchEquipment()))return false;
    const auto SwitchA=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Tick reaches weapon-switch midpoint"),F.AdvanceTo(SwitchA.Start+.125)))return false;
    const auto Switch=F.Capture();
    if(F.CaptureObserved(*this,Switch,TEXT("Pending switch")))
    {
        TestTrue(TEXT("Weapon-switch snapshot preserves old active slot until full commit"),Switch.View.Action.Kind==EDungeonEquipmentActionKind::SwitchWeapon
            &&Switch.View.Action.Deadline==SwitchA.Start+.35&&Switch.PendingPlan.Action==SnapshotInv::EAction::Switch
            &&Switch.PendingPlan.Slot==0&&Switch.InventoryState.ActiveSlot==1&&!Switch.PendingHasDrop&&Switch.View.Action.SourceId==0);
        RoundTrip(*this,Switch,TEXT("Pending switch"));
    }
    if(!TestTrue(TEXT("Weapon switch finishes through ordinary tick"),F.Finish()))return false;
    const auto Spear=F.Register("WPN-SPR-001");
    if(!TestTrue(TEXT("Full weapon slots require real selection and confirmation"),Spear.Ok()&&F.Pickup(Spear.SourceId,0)))return false;
    const auto ReplaceA=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Tick reaches confirmed replacement midpoint"),F.AdvanceTo(ReplaceA.Start+.125)))return false;
    const auto Replace=F.Capture();const auto Frozen=Signature(Replace);
    if(F.CaptureObserved(*this,Replace,TEXT("Pending replacement")))
    {
        TestTrue(TEXT("Replacement preserves exact reserved old-instance drop and unspent operation/source domains"),Replace.PendingHasDrop
            &&Replace.PendingDropPosition==F.Player->GetGroundPosition()&&Replace.PendingPlan.ReplacedId==1
            &&Replace.PendingPlan.SourceId==Spear.SourceId&&Replace.View.NextOperationId==4&&Replace.View.NextEquipmentActionId==5
            &&Replace.View.NextSourceId==4&&Replace.View.NextInstanceId==5&&Replace.InventoryState.Weapons[0]==1);
        RoundTrip(*this,Replace,TEXT("Pending replacement"));
    }
    if(!TestTrue(TEXT("Real replacement commits its one ground drop"),F.Finish()))return false;
    TestTrue(TEXT("Whole captured value remains detached from changed source and inventory arrays"),Signature(Replace)==Frozen);
    const auto Complete=F.Capture();
    if(F.CaptureObserved(*this,Complete,TEXT("Completed replacement residue")))
    {
        TestTrue(TEXT("Inactive completed plan may legitimately retain older revision/drop data"),!Complete.View.Action.Active&&Complete.PendingHasDrop
            &&Complete.PendingPlan.BaseRevision<Complete.InventoryState.Revision&&Complete.View.NextOperationId==5
            &&Complete.View.NextSourceId==5&&Complete.InventoryState.Operations.size()==4);
        RoundTrip(*this,Complete,TEXT("Completed replacement residue"));
    }
    // Separate actual owner preserves every earlier fixture's literal ID/domain
    // expectations. A new unrelated source is legal during the existing pickup.
    FSnapshotWorld Rebase;
    if(!TestTrue(TEXT("Actual independent rebase-control Run initializes"),Rebase.Create()))return false;
    const auto OriginalSource=Rebase.Register("WPN-XBW-001",1.);
    if(!TestTrue(TEXT("Rebase control starts normal pickup"),OriginalSource.Ok()&&Rebase.Pickup(OriginalSource.SourceId)))return false;
    const auto OriginalAction=Rebase.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Rebase control reaches original action midpoint"),Rebase.AdvanceTo(OriginalAction.Start+.125)))return false;
    const uint64 OldBase=Rebase.Inventory().Revision;
    TestEqual(TEXT("One real source registration made original pending plan base2"),OldBase,uint64(2));
    const auto Unrelated=Rebase.Register("ARM-LGT-001");
    if(!TestTrue(TEXT("Public unrelated source registration succeeds during active pickup"),Unrelated.Ok()
        &&Rebase.Inventory().Revision==3&&Rebase.Game->GetEquipmentView().Action.Active
        &&Rebase.Game->GetEquipmentView().Action.ActionId==OriginalAction.ActionId
        &&Rebase.Player->GetEquipmentActionDeadline()==OriginalAction.Deadline))return false;
    const auto MidRebase=Rebase.Capture();
    if(Rebase.CaptureObserved(*this,MidRebase,TEXT("Active unrelated registration")))
    {
        TestTrue(TEXT("Real active snapshot retains old base2 while unrelated registration advanced inventory to3"),
            MidRebase.PendingPlan.BaseRevision==OldBase&&MidRebase.InventoryState.Revision==3
            &&MidRebase.PendingPlan.SourceId==OriginalSource.SourceId&&MidRebase.PendingPlan.InstanceId==OriginalSource.InstanceId);
        RoundTrip(*this,MidRebase,TEXT("Active plan survives unrelated source registration without base normalization"));
    }
    if(!TestTrue(TEXT("Original GameMode commits real pickup at unchanged deadline despite unrelated registration"),
        Rebase.AdvanceTo(OriginalAction.Deadline)&&!Rebase.Game->GetEquipmentView().Action.Active
        &&Rebase.Inventory().Weapons[1]==OriginalSource.InstanceId&&Rebase.Inventory().Operations.size()==1))return false;
    const auto CompletedRebase=Rebase.Capture();
    if(Rebase.CaptureObserved(*this,CompletedRebase,TEXT("Completed rebase control")))
    {
        TestTrue(TEXT("Actual completed owner retains old base2 while committed inventory operation records re-prepared base3"),
            CompletedRebase.PendingPlan.BaseRevision==OldBase&&CompletedRebase.InventoryState.Operations[0].Request.BaseRevision==3
            &&CompletedRebase.InventoryState.Operations[0].Result.Revision==4&&!CompletedRebase.View.Action.Active);
        RoundTrip(*this,CompletedRebase,TEXT("Completed rebased operation preserves original inactive plan"));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentSnapshotRuntimeHistory,
    "CodexDungeon.Content.RunOwnerSnapshot.EquipmentRuntimeReceiptsCritAndCancellation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FEquipmentSnapshotRuntimeHistory::RunTest(const FString& Parameters)
{
    FSnapshotWorld F;if(!TestTrue(TEXT("Actual bound world for spent domains initializes"),F.Create())||!F.ResourcesAndTwoCritDomains(*this))return false;
    const auto S=F.Capture();
    if(F.CaptureObserved(*this,S,TEXT("Spent runtime")))
    {
        TestTrue(TEXT("Two accepted lock domains preserve literal seed-one draw facts without a fresh RNG draw"),S.View.CombatSeed==1&&S.View.NextCritDraw==2
            &&S.CritReceipts.Num()==2&&!S.CritReceipts[0].WeaponAction&&S.CritReceipts[1].WeaponAction
            &&S.CritReceipts[0].ActionId==1&&S.CritReceipts[1].ActionId==1&&S.CritReceipts[0].Draw==0&&S.CritReceipts[1].Draw==1
            &&S.CritReceipts[0].Bits==2009361098267089954ULL&&S.CritReceipts[1].Bits==8859251267152808453ULL
            &&S.CritReceipts[0].ChancePct==5.&&S.CritReceipts[1].ChancePct==5.&&!S.CritReceipts[0].Critical&&!S.CritReceipts[1].Critical);
        TestTrue(TEXT("Actual reload refill remains a versioned inventory receipt, not only final ammo"),S.InventoryState.RuntimeUpdates.size()>=2
            &&S.InventoryState.RuntimeUpdates.back().BeforeAmmo==0.&&S.InventoryState.RuntimeUpdates.back().Ammo==1.
            &&S.InventoryState.RuntimeUpdates.back().AfterVersion==S.InventoryState.RuntimeUpdates.back().BeforeVersion+1
            &&S.View.NextRuntimeReceiptId==S.InventoryState.NextRuntimeReceiptId);
        RoundTrip(*this,S,TEXT("Spent runtime"));
    }
    const auto Heavy=F.Register("WPN-GSW-001");
    if(!TestTrue(TEXT("Actual confirmed replacement begins before cancellation"),Heavy.Ok()&&F.Pickup(Heavy.SourceId,1)))return false;
    const auto Before=F.Capture();F.Player->ApplyCombatHit(5.f,nullptr,0.f);
    if(!TestTrue(TEXT("Actual received damage cancels equipment but keeps its spent action identity"),!F.Game->GetEquipmentView().Action.Active
        &&F.Player->Health==95.f&&F.Game->GetEquipmentView().NextOperationId==2&&F.Game->GetEquipmentView().NextEquipmentActionId==3))return false;
    const auto Cancel=F.Capture();
    if(F.CaptureObserved(*this,Cancel,TEXT("Cancelled replacement")))
    {
        TestTrue(TEXT("Legal cancellation residue retains plan/drop but has no active operation or consumed source"),!Cancel.View.Action.Active
            &&Cancel.PendingHasDrop&&Cancel.PendingPlan.SourceId==Heavy.SourceId&&Cancel.PendingPlan.ReplacedId==F.Inventory().Weapons[1]
            &&Cancel.Sources.Last().SourceId==Heavy.SourceId&&!Cancel.Sources.Last().Consumed&&Cancel.View.NextOperationId==2);
        TestTrue(TEXT("Owner Stats current HP mirror is not mistaken for changed Pawn HP authority"),Cancel.View.Stats.CurrentHP==100.&&F.Player->Health==95.f);
        RoundTrip(*this,Cancel,TEXT("Cancelled replacement with old HP mirror"));
    }
    if(Before.HasInventory)TestTrue(TEXT("Cancelling real owner does not mutate previous value snapshot"),Before.View.Action.Active);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentSnapshotAtomicValidation,
    "CodexDungeon.Content.RunOwnerSnapshot.EquipmentInvalidCandidateKeepsOwner",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FEquipmentSnapshotAtomicValidation::RunTest(const FString& Parameters)
{
    FSnapshotWorld F;if(!TestTrue(TEXT("Actual atomic-validation fixture initializes"),F.Create())||!F.ResourcesAndTwoCritDomains(*this))return false;
    const auto Heavy=F.Register("WPN-GSW-001");if(!TestTrue(TEXT("Real pending replacement supplies validated candidate"),Heavy.Ok()&&F.Pickup(Heavy.SourceId,1)))return false;
    const auto S=F.Capture();if(!F.CaptureObserved(*this,S,TEXT("Validation baseline")))return false;
    FDungeonEquipmentRuntime Target;FString Why;
    if(!TestTrue(TEXT("Independent target accepts genuine complete owner baseline"),Target.Restore(S,Why)))return false;
    const auto Unchanged=Signature(Target.Capture());
    const auto Reject=[&](const TCHAR* Label,auto Mutate)
    {
        auto Bad=S;Mutate(Bad);Why.Reset();
        TestFalse(*(FString(Label)+TEXT(" is rejected")),Target.Restore(Bad,Why));
        TestTrue(*(FString(Label)+TEXT(" returns diagnosis")),!Why.IsEmpty());
        TestTrue(*(FString(Label)+TEXT(" cannot partially change current runtime")),Signature(Target.Capture())==Unchanged);
    };
    Reject(TEXT("Unknown owner schema"),[](auto& B){B.Schema=2;});
    Reject(TEXT("Bound owner missing inventory"),[](auto& B){B.HasInventory=false;});
    Reject(TEXT("Missing complete Run identity"),[](auto& B){B.View.RunGuid.Invalidate();});
    Reject(TEXT("Inventory owner disagrees with enclosing owner"),[](auto& B){++B.View.OwnerId;});
    Reject(TEXT("Duplicate inventory instance"),[](auto& B){B.InventoryState.Items.push_back(B.InventoryState.Items[0]);});
    Reject(TEXT("Duplicate external source ID"),[](auto& B){const auto Duplicate=B.Sources[0];B.Sources.Add(Duplicate);});
    Reject(TEXT("Pending source is absent"),[](auto& B){B.Sources.RemoveAt(B.Sources.Num()-1);});
    Reject(TEXT("Nonfinite external source location"),[](auto& B){B.Sources[0].Position.X=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("External source version is stale"),[](auto& B){++B.Sources.Last().Version;});
    Reject(TEXT("External source consumption disagrees with inventory"),[](auto& B){B.Sources[0].Consumed=!B.Sources[0].Consumed;});
    Reject(TEXT("Active pending plan revision is stale"),[](auto& B){++B.PendingPlan.BaseRevision;});
    Reject(TEXT("Active action and plan instance disagree"),[](auto& B){++B.View.Action.InstanceId;});
    Reject(TEXT("Reserved replacement drop is nonfinite"),[](auto& B){B.PendingDropPosition.Y=std::numeric_limits<double>::infinity();});
    Reject(TEXT("Next instance domain aliases an existing instance"),[](auto& B){B.View.NextInstanceId=1;});
    Reject(TEXT("Next operation domain aliases a committed operation"),[](auto& B){B.View.NextOperationId=1;});
    Reject(TEXT("Derived active magazine mirror is forged"),[](auto& B){B.View.Slots[1].Ammo=0.;});
    Reject(TEXT("Resolved stat mirror is forged"),[](auto& B){B.View.Stats.Armor+=1.;});
    Reject(TEXT("Resolved HP mirror is nonfinite"),[](auto& B){B.View.Stats.CurrentHP=std::numeric_limits<double>::quiet_NaN();});
    Reject(TEXT("Resolved crit bits disagree with saved seed/draw"),[](auto& B){B.CritReceipts[0].Bits^=1;});
    Reject(TEXT("Crit cursor has an unrecorded draw"),[](auto& B){++B.View.NextCritDraw;});
    Reject(TEXT("Duplicate lock domain/action receipt"),[](auto& B){B.CritReceipts[1].WeaponAction=false;});
    Reject(TEXT("Crit chance is outside percentage range"),[](auto& B){B.CritReceipts[0].ChancePct=101.;});
    Reject(TEXT("Crit receipt time is nonfinite"),[](auto& B){B.CritReceipts[0].AtTime=std::numeric_limits<double>::quiet_NaN();});
    TestTrue(TEXT("Original valid value still restores after every refused candidate"),Target.Restore(S,Why));
    TestTrue(TEXT("Final complete target still matches original value"),Signature(Target.Capture())==Signature(S));
    return true;
}
#endif
