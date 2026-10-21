#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonWorldProjectiles.h"
#include "../DungeonRoomLayout.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include <cmath>

namespace
{
namespace RangedWA = DungeonWeaponActions;
namespace RangedInventory = DungeonEquipmentInventory;
namespace RangedStats = DungeonEquipmentStats;
using RangedEvent = EDungeonWorldWeaponEventKind;

RangedInventory::FItem RangedPrototype(const char* Id)
{
    RangedInventory::FItem I; I.ContentId=Id;
    if (I.ContentId=="WPN-XBW-001") I.Ammo=1; // Authored initial source, never a pickup refill.
    return I;
}

struct FRangedAdapterWorld
{
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    FAutomationTestBase* Test=nullptr;
    explicit FRangedAdapterWorld(FAutomationTestBase* InTest=nullptr):Test(InTest) {}
    bool Fail(const TCHAR* Stage)
    {
        if (Test) Test->AddError(FString::Printf(TEXT("Ranged fixture stage '%s' failed. Equipment: %s"),Stage,
            Game?*Game->GetEquipmentView().FailureText:TEXT("No GameMode")));
        return false;
    }
    ~FRangedAdapterWorld()
    {
        if (World) { World->DestroyWorld(false); if (GEngine) GEngine->DestroyWorldContext(World); }
    }
    bool Create(const RangedInventory::FItem& Weapon, uint64 Seed=1, FVector2D Initial={0,0}, bool WithController=false)
    {
        if (!GEngine) return Fail(TEXT("GEngine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if (!World) return Fail(TEXT("CreateWorld"));
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return Fail(TEXT("SetGameMode"));
        Game=World->GetAuthGameMode<ADungeonGameMode>(); Player=World->SpawnActor<ADungeonFighter>();
        if (!Game||!Player) return Fail(TEXT("SpawnPlayer"));
        Player->SetActorTickEnabled(false); Player->ResetFighter(Initial);
        Game->PlayerFighter=Player; Game->bWaitingForStart=false; Game->bGameOver=false;
        if (!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,Seed)) return Fail(TEXT("BeginEquipmentRun"));
        const auto Source=Game->RegisterEquipmentSource(TEXT("qa.ranged.weapon"),Weapon,Initial+FVector2D(40,0));
        if (!Source.Ok()) return Fail(TEXT("RegisterSource"));
        if (!Game->SelectEquipmentSource(Source.SourceId)||!Game->TryInteractEquipment()
            ||!Game->GetEquipmentView().Action.Active||!FinishEquipment()) return Fail(TEXT("E pickup"));
        // Empty-slot E already activates the acquired instance. Exercise both real
        // Q transactions and finish back on that same acquired instance.
        if (!Game->TrySwitchEquipment()||!FinishEquipment()
            ||!Game->TrySwitchEquipment()||!FinishEquipment()) return Fail(TEXT("Q round trip"));
        if (!Player->IsEquipmentBound()||Player->WeaponId!=UTF8_TO_TCHAR(Weapon.ContentId.c_str())
            ||Game->GetEquipmentView().Slots[1].InstanceId!=Source.InstanceId) return Fail(TEXT("Final active instance"));
        if (WithController)
        {
            Controller=World->SpawnActor<APlayerController>(); if (!Controller) return Fail(TEXT("SpawnController"));
            Controller->Possess(Player);
            if (!Controller->PlayerInput) Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
            if (!Controller->IsLocalController()||Player->GetController()!=Controller) return Fail(TEXT("PossessController"));
        }
        return World->GetAuthGameMode<ADungeonGameMode>()==Game;
    }
    bool AdvanceTo(double At)
    {
        if (!std::isfinite(At)||At<Game->GetSimulationTime()) return false;
        for (int32 N=0;N<32&&Game->GetSimulationTime()<At;++N)
        {
            const double Remaining=At-Game->GetSimulationTime(); float Step=float(Remaining);
            if (double(Step)>Remaining) Step=std::nextafter(Step,0.f);
            if (!(Step>0.f)) return false;
            const double Before=Game->GetSimulationTime(); Frame(Step);
            if (Game->GetSimulationTime()<=Before) return false;
        }
        return Game->GetSimulationTime()==At;
    }
    bool FinishEquipment() { return AdvanceTo(Player->GetEquipmentActionDeadline()); }
    const RangedWA::FState& Actions() const { return Player->GetWeaponActionsState(); }
    const FDungeonWeaponWorldState& State() const { return Game->GetWeaponWorldState(); }
    const RangedWA::FInstance* ActiveInstance() const
    { for (const auto& I:Actions().Instances) if (I.InstanceId==Actions().EquippedId) return &I; return nullptr; }
    const RangedWA::FEvent* Issued(uint64 ActionId) const
    { for (const auto& E:Actions().Issued) if (E.ActionId==ActionId) return &E; return nullptr; }
    ADungeonFighter* Target(FVector2D Position,float HP=1000.f,bool AI=false)
    {
        auto E=World->SpawnActor<ADungeonFighter>(); if (!E) return nullptr;
        E->SetActorTickEnabled(false); E->bEnemy=true; E->bAIEnabled=AI; E->MaxHealth=HP;
        E->ResetFighter(Position); Game->Enemies.Add(E); return E;
    }
    ADungeonFighter* Knight(FVector2D Position,uint64 Id=71001)
    {
        auto E=World->SpawnActor<ADungeonFighter>(); if (!E) return nullptr;
        E->SetActorTickEnabled(false); E->ResetFighter(Position); Game->Enemies.Add(E);
        if (!E->InitializeStoneKnight(Id,Game->GetSimulationTime())) return nullptr;
        E->bAIEnabled=false; return E;
    }
    AActor* Wall(FVector2D Position,FVector Extent={5,80,50})
    {
        auto A=World->SpawnActor<AActor>(); if (!A) return nullptr;
        auto B=NewObject<UBoxComponent>(A); A->SetRootComponent(B); B->SetBoxExtent(Extent);
        B->SetCollisionEnabled(ECollisionEnabled::QueryOnly); B->SetCollisionObjectType(ECC_WorldStatic);
        B->SetCollisionResponseToAllChannels(ECR_Block); B->RegisterComponentWithWorld(World);
        A->SetActorLocation({Position.X,Position.Y,0}); return A;
    }
    int32 Events(RangedEvent Kind,uint64 TargetId=0) const
    { int32 N=0; for (const auto& E:State().Events) if (E.Kind==Kind&&(!TargetId||E.TargetId==TargetId)) ++N; return N; }
    const FDungeonWorldWeaponEvent* Event(RangedEvent Kind,uint64 TargetId=0) const
    { for (const auto& E:State().Events) if (E.Kind==Kind&&(!TargetId||E.TargetId==TargetId)) return &E; return nullptr; }
    const FDungeonWorldBurn* Burn(uint64 TargetId) const
    { for (const auto& B:State().Burns) if (B.TargetId==TargetId) return &B; return nullptr; }
    bool Key(FKey K,bool Down)
    {
        if (!Controller||!Controller->PlayerInput) return false;
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.0:0.0));
        Controller->PlayerInput->Tick(.005f); TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(K)==Down;
    }
    void Frame(float Delta)
    {
        Game->Tick(Delta);
        // A physical edge lives for one player-input frame. Advancing game time
        // alone would leave the fixture's last WasJustPressed result stale.
        if (Controller&&Controller->PlayerInput)
        {
            Controller->PlayerInput->Tick(Delta); TArray<UInputComponent*> Stack;
            Controller->PlayerInput->ProcessInputStack(Stack,Delta,false);
        }
    }
};
bool Near(double A,double B,double Tolerance=1.e-5) { return std::abs(A-B)<=Tolerance; }
double CriticalMultiplier(const RangedWA::FAction& A) { return A.Critical?A.CritMultiplier:1.; }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedCrossbowPrimaryTimeline,
    "CodexDungeon.Content.RangedWeaponsAdapter.CrossbowPrimaryTimelineWorldAndReload",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedCrossbowPrimaryTimeline::RunTest(const FString& Parameters)
{
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Real E/Q crossbow fixture"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
    auto T=F.Target({180,0}); if (!TestNotNull(TEXT("Actual world target"),T)) return false;
    const auto BeforeDraw=F.Game->GetEquipmentView().NextCritDraw;
    F.Player->BeginAttack(); const auto A=F.Actions().Action;
    if (!TestTrue(TEXT("Primary admitted into WA domain, not prototype sword"),A.Active&&A.Type==RangedWA::EAction::Primary&&A.Weapon==DungeonContentCombat::EWeapon::XBW001)) return false;
    TestTrue(TEXT("Definition full .16/.04/.48 timeline"),Near(A.LockAt,A.Start+.064)&&Near(A.ActiveAt,A.Start+.16)&&Near(A.ActiveEnd,A.Start+.20)&&Near(A.End,A.Start+.68));
    F.AdvanceTo(A.LockAt-.001);
    TestTrue(TEXT("No early draw, ammo spend, emission or damage"),F.Game->GetEquipmentView().NextCritDraw==BeforeDraw&&F.ActiveInstance()->Ammo==1&&F.State().Projectiles.Num()==0&&T->Health==1000.f);
    F.AdvanceTo(A.LockAt);
    TestTrue(TEXT("Real lock reserves sole bolt and draws once"),F.Actions().Action.Locked&&F.ActiveInstance()->Ammo==1&&F.ActiveInstance()->ReservedAmmo==1&&F.Game->GetEquipmentView().NextCritDraw==BeforeDraw+1);
    F.AdvanceTo(A.ActiveAt);
    const auto* Emitted=F.Issued(A.ActionId); if (!TestNotNull(TEXT("Real WA emission fact"),Emitted)) return false;
    const auto E=*Emitted;
    TestTrue(TEXT("One real world projectile consumes one bolt exactly at emission"),E.Kind==RangedWA::EEvent::ProjectileEmitted&&Near(E.Damage,34*CriticalMultiplier(E.Action))&&E.Stagger==12&&E.ProjectileSpeed==950&&F.ActiveInstance()->Ammo==0&&F.ActiveInstance()->ReservedAmmo==0&&F.State().Projectiles.Num()==1&&F.Events(RangedEvent::ProjectileEmitted)==1);
    TestTrue(TEXT("World scope and event receipt use real Run/room/owner/action"),F.State().RunGuid==F.Game->GetEquipmentView().RunGuid&&F.State().RoomInstanceId==F.Game->GetEquipmentView().RoomInstanceId&&F.State().Projectiles[0].Key.OwnerId==F.Player->GetRuntimeEntityId()&&F.State().Projectiles[0].Key.RoomInstanceId==F.Game->GetEquipmentView().RoomInstanceId&&F.State().Projectiles[0].Key.ActionId==A.ActionId&&F.State().Projectiles[0].Key.EventId==E.EventId);
    F.AdvanceTo(A.End-.001);
    TestTrue(TEXT("Single actual hit, complete recovery before automatic reload"),Near(1000-T->Health,E.Damage,.0002)&&F.Events(RangedEvent::DirectHitCommitted,T->GetRuntimeEntityId())==1&&F.Actions().Action.Type==RangedWA::EAction::Primary&&F.Actions().Action.Active);
    TestFalse(TEXT("T cannot skip last-shot recovery"),F.Player->TryBeginReload());
    F.AdvanceTo(A.End); const auto R=F.Actions().Action;
    TestTrue(TEXT("Automatic reload starts at exact full recovery deadline"),R.Active&&R.Type==RangedWA::EAction::Reload&&R.Start==A.End&&Near(R.End,R.Start+1.10)&&F.ActiveInstance()->Ammo==0);
    const uint64 ActionCursor=F.Actions().NextActionId;
    F.Player->BeginAttack(); TestFalse(TEXT("Reload excludes skill"),F.Player->TryBeginWeaponSkill());
    TestTrue(TEXT("Denied fire during reload creates no action or emission"),F.Actions().NextActionId==ActionCursor&&F.Events(RangedEvent::ProjectileEmitted)==1);
    F.AdvanceTo(R.End-.001); TestEqual(TEXT("Unfinished reload never refills"),F.ActiveInstance()->Ammo,0.0);
    F.AdvanceTo(R.End);
    TestTrue(TEXT("One completion refills actual instance and inventory mirror"),!F.Actions().Action.Active&&F.ActiveInstance()->Ammo==1&&F.Game->GetEquipmentView().Slots[1].Ammo==1);
    F.Game->Tick(.31f); TestTrue(TEXT("Late steps do not replay emission or damage"),F.Events(RangedEvent::ProjectileEmitted)==1&&F.Events(RangedEvent::DirectHitCommitted)==1&&F.Game->GetEquipmentView().NextCritDraw==BeforeDraw+1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedCrossbowPierce,
    "CodexDungeon.Content.RangedWeaponsAdapter.CrossbowSkillNearestTwoAndPhysicalDefense",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedCrossbowPierce::RunTest(const FString& Parameters)
{
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Piercing skill E/Q fixture"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
        auto Third=F.Target({300,0}),Second=F.Target({220,0}),First=F.Target({140,0});
        if (!Third||!Second||!First) return false;
        if (!TestTrue(TEXT("Actual K skill accepts loaded bolt"),F.Player->TryBeginWeaponSkill())) return false;
        const auto A=F.Actions().Action; const auto Draw=F.Game->GetEquipmentView().NextCritDraw;
        F.AdvanceTo(A.LockAt);
        TestTrue(TEXT("Lock .22 sets six-second instance CD, reserves no Focus"),Near(A.LockAt,A.Start+.22)&&Near(F.ActiveInstance()->CooldownDeadline,A.LockAt+6)&&F.ActiveInstance()->ReservedAmmo==1&&F.Actions().Budget.ReservedFocus==0&&F.Game->GetEquipmentView().NextCritDraw==Draw+1);
        F.AdvanceTo(A.Start+.9); const auto* P=F.Issued(A.ActionId); if (!P) return false; const auto E=*P;
        TestTrue(TEXT("Actual one-bolt skill payload"),E.ProjectileSpeed==1100&&E.MaxTargets==2&&E.SecondTargetRatio==.6&&Near(E.Damage,50*CriticalMultiplier(E.Action))&&E.Stagger==24);
        TestTrue(TEXT("Contacts sort by path, not reverse Enemies order; second gets .6 only"),Near(1000-First->Health,E.Damage,.0002)&&Near(1000-Second->Health,E.Damage*.6,.0002)&&Third->Health==1000.f&&F.Events(RangedEvent::DirectHitCommitted)==2);
        const auto* H1=F.Event(RangedEvent::DirectHitCommitted,First->GetRuntimeEntityId());
        const auto* H2=F.Event(RangedEvent::DirectHitCommitted,Second->GetRuntimeEntityId());
        TestTrue(TEXT("Real hit journal preserves physical 24 then14.4 stagger and causal order"),H1&&H2&&!H1->Magic&&!H2->Magic&&H1->Stagger==24&&Near(H2->Stagger,14.4)&&H1->AtTime<H2->AtTime&&H1->Key.EventId==H2->Key.EventId);
        TestTrue(TEXT("Projectile terminates after exactly two targets"),F.State().Projectiles.Num()==1&&!F.State().Projectiles[0].Active&&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::TargetLimit);
    }
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Real physical-defense fixture"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
        auto K=F.Knight({180,0}); if (!K) return false;
        F.Player->BeginAttack(); const auto A=F.Actions().Action; if (!A.Active) return false;
        F.AdvanceTo(A.Start+.6); const auto* E=F.Issued(A.ActionId); if (!E) return false;
        TestTrue(TEXT("Crossbow uses actual stone Armor45, not Ward20"),Near(110-K->Health,E->Damage*100/145.,.0002));
        const auto* H=F.Event(RangedEvent::DirectHitCommitted,K->GetRuntimeEntityId());
        TestTrue(TEXT("Committed journal records actual mitigated HP loss"),H&&!H->Magic&&Near(H->ActualHPLoss,E->Damage*100/145.,.0002));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedProjectileBlockers,
    "CodexDungeon.Content.RangedWeaponsAdapter.ProjectileWallsCenterBoundsAndHeight",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedProjectileBlockers::RunTest(const FString& Parameters)
{
    for (int32 Case=0;Case<4;++Case)
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Collision fixture E/Q binding"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
        auto T=F.Target(Case==1?FVector2D(430,0):Case==2?FVector2D(180,14.001):FVector2D(180,0)); if (!T) return false;
        if (Case==0&&!F.Wall({80,0})) return false;
        if (Case==3) T->StartJump();
        F.Player->BeginAttack(); const auto A=F.Actions().Action;
        if (!TestTrue(TEXT("Actual projectile primary starts for collision test"),A.Active&&A.Type==RangedWA::EAction::Primary)) return false;
        F.AdvanceTo(A.Start+.65);
        TestTrue(*FString::Printf(TEXT("Case%d: wall / center range / center depth / actual high jump rejects damage"),Case),T->Health==1000.f&&F.Events(RangedEvent::DirectHitCommitted)==0);
        if (Case==0) TestTrue(TEXT("Registered WorldStatic wall physically stops projectile"),F.State().Projectiles.Num()==1&&!F.State().Projectiles[0].Active&&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::Wall);
        if (Case==1) TestTrue(TEXT("Hurtbox reaching into range cannot expand center hard420"),F.State().Projectiles.Num()==1&&!F.State().Projectiles[0].Active);
    }
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Room hard-bound fixture"),F.Create(RangedPrototype("WPN-XBW-001"),1,{DungeonRoomLayout::MaxX-90,0}))) return false;
        F.Player->BeginAttack(); const auto A=F.Actions().Action; if (!A.Active) return false;
        F.AdvanceTo(A.Start+.6);
        TestTrue(TEXT("World projectile stops at hard room boundary before its range"),F.State().Projectiles.Num()==1&&!F.State().Projectiles[0].Active&&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::HardBounds&&F.State().Projectiles[0].Position.X<=DungeonRoomLayout::MaxX&&F.State().Projectiles[0].Traveled<420);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedFractionalContacts,
    "CodexDungeon.Content.RangedWeaponsAdapter.FractionalContactsUseActualMuzzleAndCausalTime",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedFractionalContacts::RunTest(const FString& Parameters)
{
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Muzzle/contact fixture"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
    auto M=F.Player->GetWeaponMuzzleComponent(); if (!TestNotNull(TEXT("Actual emitter component"),M)) return false;
    M->SetRelativeLocation({24,7,0}); // QA authors a real component; no fabricated kernel origin.
    auto T=F.Target({185.123,7}); if (!T) return false;
    const auto NextEntity=F.State().NextEntityId;
    for (int32 N=0;N<8;++N) { T->GetRuntimeEntityId();F.Game->GetWeaponWorldState(); }
    TestEqual(TEXT("Readonly identity queries allocate no IDs"),F.State().NextEntityId,NextEntity);
    F.Player->BeginAttack(); const auto A=F.Actions().Action; if (!A.Active) return false;
    F.AdvanceTo(A.LockAt); F.Player->MoveOnGround({0,1},.03f);
    const auto AtEmission=F.Player->GetWeaponMuzzleOrigin();
    F.AdvanceTo(A.ActiveAt); const auto* P=F.Issued(A.ActionId); if (!P) return false; const auto E=*P;
    TestTrue(TEXT("Emission samples actual moved muzzle, not start or Actor center"),Near(E.Origin.X,AtEmission.X)&&Near(E.Origin.Y,AtEmission.Y)&&Near(E.Origin.Height,AtEmission.Height)&&Near(E.Origin.X,F.Player->GetGroundPosition().X+24)&&Near(E.Origin.Y,F.Player->GetGroundPosition().Y+7));
    // Move the actual target into the emitted parallel line before contact, then leave it stationary.
    T->MoveOnGround({0,1},float((E.Origin.Y-T->GetGroundPosition().Y)/T->GetMoveSpeed()));
    F.AdvanceTo(A.Start+.5);
    const auto* H=F.Event(RangedEvent::DirectHitCommitted,T->GetRuntimeEntityId());
    const double Contact=E.AtTime+(T->GetGroundPosition().X-18-E.Origin.X)/950.;
    TestTrue(TEXT("Actual hurtbox contact retains fractional simulation time"),H&&Near(H->AtTime,Contact,1.e-7)&&H->AtTime>E.AtTime&&H->AtTime<F.Game->GetSimulationTime()&&Near(H->Position.Y,E.Origin.Y)&&Near(H->Height,E.Origin.Height));
    TestTrue(TEXT("One world hit and stable Run-owned target identity"),F.State().HitReceipts.Num()==1&&F.Events(RangedEvent::DirectHitCommitted)==1&&T->GetRuntimeEntityId()!=0&&T->GetRuntimeEntityId()<(uint64(1)<<63));
    const auto Sequence=F.State().NextEventSequence; F.Game->Tick(.1f);
    TestTrue(TEXT("Consumed projectile and immutable original emission do not replay"),F.Events(RangedEvent::ProjectileEmitted)==1&&F.Events(RangedEvent::DirectHitCommitted)==1&&F.State().NextEventSequence==Sequence);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedStaffPrimary,
    "CodexDungeon.Content.RangedWeaponsAdapter.StaffPrimaryMagicFocusAndNoImplicitBurn",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedStaffPrimary::RunTest(const FString& Parameters)
{
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Actual staff E/Q fixture"),F.Create(RangedPrototype("WPN-STF-001")))) return false;
    auto T=F.Knight({180,0}); if (!T) return false;
    F.Player->BeginAttack(); const auto A=F.Actions().Action;
    if (!TestTrue(TEXT("Staff primary enters real WA"),A.Active&&A.Type==RangedWA::EAction::Primary&&A.Weapon==DungeonContentCombat::EWeapon::STF001)) return false;
    TestTrue(TEXT("Frozen .22/.05/.40 primary"),Near(A.LockAt,A.Start+.088)&&Near(A.ActiveAt,A.Start+.22)&&Near(A.End,A.Start+.67));
    F.AdvanceTo(A.LockAt); TestTrue(TEXT("Ten Focus reserved without an early spend"),F.Actions().Budget.Focus==100&&F.Actions().Budget.ReservedFocus==10&&!F.Actions().Budget.HasActualSpend);
    F.AdvanceTo(A.ActiveAt); const auto* P=F.Issued(A.ActionId); if (!P) return false; const auto E=*P;
    TestTrue(TEXT("Actual slow600 fireball24/8 spends10 once; primary contains no burn"),E.ProjectileSpeed==600&&Near(E.Damage,24*CriticalMultiplier(E.Action))&&E.Stagger==8&&E.BurnDps==0&&E.BurnDuration==0&&F.Actions().Budget.Focus==90&&F.Player->Focus==90&&F.Actions().Budget.ReservedFocus==0&&F.Actions().Budget.LastActualSpend==E.AtTime);
    F.AdvanceTo(A.Start+.85);
    TestTrue(TEXT("Fireball is magic against stone Ward20, not Armor45"),Near(110-T->Health,E.Damage*100/120.,.0002)&&F.Events(RangedEvent::DirectHitCommitted)==1&&F.State().Burns.Num()==0&&F.Events(RangedEvent::BurnApplied)==0);
    const auto* H=F.Event(RangedEvent::DirectHitCommitted,T->GetRuntimeEntityId()); TestTrue(TEXT("Actual magic journal has actual HP loss"),H&&H->Magic&&Near(H->ActualHPLoss,E.Damage*100/120.,.0002));
    F.AdvanceTo(E.AtTime+1); TestTrue(TEXT("Spend waits one full simulation second before regen"),Near(F.Actions().Budget.Focus,90));
    F.AdvanceTo(E.AtTime+1.25); TestTrue(TEXT("Single authority regens12/s and mirrors once"),Near(F.Actions().Budget.Focus,93)&&Near(F.Player->Focus,93)&&F.Events(RangedEvent::ProjectileEmitted)==1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedFirelineBurn,
    "CodexDungeon.Content.RangedWeaponsAdapter.FirelineFixedBurnIgnoresDirectMultipliersAndIframes",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedFirelineBurn::RunTest(const FString& Parameters)
{
    auto Weapon=RangedPrototype("WPN-STF-001"); Weapon.Grade=3; Weapon.Tier=5;
    Weapon.Package=RangedStats::EPackage::Beneficial; Weapon.Affixes={{"AFF-P-001",25,{9,10}}};
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Real enchanted staff, seed22 first draw critical"),F.Create(Weapon,22))) return false;
    auto T=F.Target({160,0}); auto K=F.Knight({220,30}); if (!T||!K) return false;
    if (!TestTrue(TEXT("Actual fireline skill accepted"),F.Player->TryBeginWeaponSkill())) return false;
    const auto A=F.Actions().Action; const auto Draw=F.Game->GetEquipmentView().NextCritDraw;
    F.AdvanceTo(A.LockAt);
    TestTrue(TEXT("Skill lock reserves24 and CD begins at .18+7"),F.Actions().Budget.ReservedFocus==24&&F.Actions().Budget.Focus==100&&Near(F.ActiveInstance()->CooldownDeadline,A.Start+.18+7)&&F.Game->GetEquipmentView().NextCritDraw==Draw+1);
    F.AdvanceTo(A.ActiveAt); const auto* P=F.Issued(A.ActionId); if (!P) return false; const auto E=*P;
    TestTrue(TEXT("Actual direct grade+affix40% and real crit1.5; burn remains intrinsic2x3"),E.Action.Critical&&Near(E.Damage,37.8)&&E.Stagger==6&&E.BurnDps==2&&E.BurnDuration==3&&F.Actions().Budget.Focus==76&&F.Actions().Budget.ReservedFocus==0);
    const uint64 Tid=T->GetRuntimeEntityId(),Kid=K->GetRuntimeEntityId(); const auto* B=F.Burn(Tid);
    if (!TestNotNull(TEXT("Burn follows positive actual direct loss"),B)) return false;
    const double Applied=B->AppliedAt;
    TestTrue(TEXT("Each legal target hit once; one status slot and next tick+1"),F.Events(RangedEvent::DirectHitCommitted)==2&&F.Events(RangedEvent::BurnApplied)==2&&B->Active&&B->Dps==2&&Near(B->ExpiresAt,Applied+3)&&Near(B->NextTickAt,Applied+1)&&Near(1000-T->Health,37.8,.0002)&&Near(110-K->Health,37.8*100/120.,.0002));
    F.AdvanceTo(Applied+1-.01); TestEqual(TEXT("Burn has no immediate or early tick"),F.Events(RangedEvent::BurnTickCommitted),0);
    T->ApplyCombatHit(1,F.Player,0); // A real independent direct hit supplies live hurt iframes over tick1.
    const float Before=T->Health; TestFalse(TEXT("Actual direct protection exists before DoT"),T->CanReceiveDirectHit());
    F.AdvanceTo(Applied+1);
    TestTrue(TEXT("Fixed tick bypasses actual direct protection without new stagger"),Near(Before-T->Health,2,.0002)&&F.Events(RangedEvent::BurnTickCommitted,Tid)==1&&!T->CanReceiveDirectHit());
    const auto* Tick=F.Event(RangedEvent::BurnTickCommitted,Kid);
    TestTrue(TEXT("Each burn tick reads magic defense, never direct crit/grade or stagger"),Tick&&Tick->Magic&&Tick->Damage==2&&Tick->Stagger==0&&Near(Tick->ActualHPLoss,2*100/120.,.0002));
    F.AdvanceTo(Applied+1.3); TestTrue(TEXT("DoT creates no new hurt immunity or hurt action"),T->CanReceiveDirectHit()&&T->AttackPhase!=TEXT("hurt"));
    F.AdvanceTo(Applied+3);
    TestTrue(TEXT("Expiry-inclusive three ticks total6, then status ends"),F.Events(RangedEvent::BurnTickCommitted,Tid)==3&&F.Events(RangedEvent::BurnTickCommitted,Kid)==3&&Near(1000-T->Health,37.8+1+6,.0003)&&Near(110-K->Health,(37.8+6)*100/120.,.0003)&&F.Burn(Tid)&&!F.Burn(Tid)->Active);
    const auto* Driver=K->GetStoneKnightDriver(); TestTrue(TEXT("Burn zero stagger never renews stone LastPoiseAt"),Driver&&Near(Driver->State().LastPoiseAt,E.AtTime)&&Near(Driver->State().PoiseAccum,0));
    F.Game->Tick(.4f); TestTrue(TEXT("Visual embers and late steps cause no extra direct hit/tick"),F.Events(RangedEvent::DirectHitCommitted)==2&&F.Events(RangedEvent::BurnTickCommitted)==6&&F.Game->GetEquipmentView().NextCritDraw==Draw+1);
    {
        FRangedAdapterWorld R(this); if (!TestTrue(TEXT("Equal-refresh real second-instance fixture"),R.Create(RangedPrototype("WPN-STF-001")))) return false;
        auto Target=R.Target({160,0}); if (!Target||!R.Player->TryBeginWeaponSkill()) return false;
        const auto First=R.Actions().Action; R.AdvanceTo(First.ActiveAt);
        const uint64 TargetId=Target->GetRuntimeEntityId(); const auto* InitialBurn=R.Burn(TargetId); if (!InitialBurn) return false;
        const double FirstApplied=InitialBurn->AppliedAt;
        R.AdvanceTo(First.End);
        const auto Source=R.Game->RegisterEquipmentSource(TEXT("qa.ranged.second-staff"),RangedPrototype("WPN-STF-001"),R.Player->GetGroundPosition()+FVector2D(40,0));
        if (!Source.Ok()||!R.Game->SelectEquipmentSource(Source.SourceId)) return false;
        R.Game->TryInteractEquipment();
        if (!R.Game->GetEquipmentView().NeedsSlotSelection||!R.Game->ConfirmEquipmentSlot(0)
            ||!R.FinishEquipment()||!R.Game->TrySwitchEquipment()||!R.FinishEquipment()
            ||!R.Player->TryBeginWeaponSkill()) return false;
        const auto Second=R.Actions().Action; R.AdvanceTo(Second.ActiveAt);
        const auto* Refreshed=R.Burn(TargetId);
        TestTrue(TEXT("Actual second staff uses one shared target slot and equal refresh preserves tick phase"),Refreshed&&Refreshed->Active&&R.State().Burns.Num()==1&&R.Events(RangedEvent::BurnApplied,TargetId)==1&&R.Events(RangedEvent::BurnRefreshed,TargetId)==1&&Near(Refreshed->NextTickAt,FirstApplied+2)&&Near(Refreshed->ExpiresAt,Second.ActiveAt+3)&&R.Events(RangedEvent::BurnTickCommitted,TargetId)==1);
        R.AdvanceTo(FirstApplied+2);
        TestEqual(TEXT("Equal refresh cannot push second original-phase tick later"),R.Events(RangedEvent::BurnTickCommitted,TargetId),2);
        R.AdvanceTo(FirstApplied+3);
        TestTrue(TEXT("Old expiry does not end refreshed status or duplicate third tick"),R.Burn(TargetId)&&R.Burn(TargetId)->Active&&R.Events(RangedEvent::BurnTickCommitted,TargetId)==3);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedFirelineWindow,
    "CodexDungeon.Content.RangedWeaponsAdapter.FirelineFullWindowLateEntryLOSAndGroundHeight",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedFirelineWindow::RunTest(const FString& Parameters)
{
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Moving fireline fixture"),F.Create(RangedPrototype("WPN-STF-001")))) return false;
        auto Moving=F.Target({180,75},1000,true),Corner=F.Target({240,35}),Outside=F.Target({240.001,0});
        if (!Moving||!Corner||!Outside) return false;
        if (!F.Player->TryBeginWeaponSkill()) return false; const auto A=F.Actions().Action;
        F.AdvanceTo(A.ActiveAt); TestEqual(TEXT("Moving target starts outside active ground corridor"),Moving->Health,1000.f);
        F.AdvanceTo(A.ActiveEnd+.02); const auto* E=F.Issued(A.ActionId); if (!E) return false;
        const auto* H=F.Event(RangedEvent::DirectHitCommitted,Moving->GetRuntimeEntityId());
        TestTrue(TEXT("Full active window accepts actual late entry once after emission"),H&&H->AtTime>A.ActiveAt&&H->AtTime<A.ActiveEnd&&Near(1000-Moving->Health,E->Damage,.0002)&&F.Events(RangedEvent::DirectHitCommitted,Moving->GetRuntimeEntityId())==1);
        TestTrue(TEXT("Fireline is authored rectangle with hard center edge"),Near(1000-Corner->Health,E->Damage,.0002)&&Outside->Health==1000.f&&E->Origin.Height==0&&E->Shape==DungeonContentCombat::EShape::GroundRectangle);
    }
    for (int32 Case=0;Case<2;++Case)
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Fireline wall/air fixture"),F.Create(RangedPrototype("WPN-STF-001")))) return false;
        auto T=F.Target({180,0}); if (!T) return false;
        if (Case==0&&!F.Wall({80,0})) return false;
        if (Case==1) T->StartJump();
        if (!F.Player->TryBeginWeaponSkill()) return false; const auto A=F.Actions().Action;
        F.AdvanceTo(A.ActiveEnd);
        TestTrue(TEXT("Actual LOS wall or height>65 through entire window rejects direct and status"),T->Health==1000.f&&F.Events(RangedEvent::DirectHitCommitted)==0&&F.Events(RangedEvent::BurnApplied)==0);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedReloadCancellation,
    "CodexDungeon.Content.RangedWeaponsAdapter.ReloadCancellationNoRefillAndFreshRestart",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedReloadCancellation::RunTest(const FString& Parameters)
{
    auto Weapon=RangedPrototype("WPN-XBW-001"); Weapon.Tier=5;Weapon.Package=RangedStats::EPackage::Beneficial;
    Weapon.Affixes={{"AFF-P-008",25,{9,10}}};
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Actual reload-speed enchanted E/Q fixture"),F.Create(Weapon))) return false;
    F.Player->BeginAttack(); const auto A=F.Actions().Action; if (!A.Active) return false;
    F.AdvanceTo(A.End); const auto R=F.Actions().Action;
    if (!TestTrue(TEXT("Actual reload uses final+25 speed after full primary"),R.Active&&R.Type==RangedWA::EAction::Reload&&Near(R.End,R.Start+1.1/1.25))) return false;
    F.AdvanceTo(R.Start+.2); TestFalse(TEXT("Held T does not cancel reload"),F.Player->TryBeginReload(false));
    TestTrue(TEXT("Fresh T cancels unfinished reload"),F.Player->TryBeginReload(true));
    const uint64 Cursor=F.Actions().NextActionId,Draw=F.Game->GetEquipmentView().NextCritDraw;
    TestTrue(TEXT("Cancellation discards progress and preserves spent bolt"),!F.Actions().Action.Active&&F.Actions().Action.Terminal==RangedWA::EEvent::ReloadCancelled&&F.ActiveInstance()->Ammo==0&&F.Game->GetEquipmentView().Slots[1].Ammo==0);
    F.Player->BeginAttack(); TestFalse(TEXT("Empty skill is refused in same cancelled point"),F.Player->TryBeginWeaponSkill());
    TestFalse(TEXT("Cancellation point cannot also restart T"),F.Player->TryBeginReload());
    TestTrue(TEXT("All failed same-point starts preserve action/draw/resource domains"),F.Actions().NextActionId==Cursor&&F.Game->GetEquipmentView().NextCritDraw==Draw&&F.ActiveInstance()->Ammo==0);
    F.Game->Tick(.01f); if (!TestTrue(TEXT("Later fresh T starts new full reload"),F.Player->TryBeginReload())) return false;
    const auto R2=F.Actions().Action; TestTrue(TEXT("Restart has full duration and no retained progress"),Near(R2.End-R2.Start,1.1/1.25));
    F.AdvanceTo(R2.Start+.1); TestTrue(TEXT("Legal dodge cancels reload without refill"),F.Player->TryBeginDodge({0,1})&&!F.Actions().Action.Active&&F.ActiveInstance()->Ammo==0);
    F.Game->Tick(.41f); if (!F.Player->TryBeginReload()) return false;
    TestTrue(TEXT("Real Q cancels reload into normal .35 switch"),F.Game->TrySwitchEquipment()&&F.Game->GetEquipmentView().Action.Active&&!F.Actions().Action.Active&&F.ActiveInstance()->Ammo==0);
    if (!F.FinishEquipment()||!F.Game->TrySwitchEquipment()||!F.FinishEquipment()) return false;
    TestTrue(TEXT("Q round trip preserves empty instance, never fills magazine"),F.Player->WeaponId==TEXT("WPN-XBW-001")&&F.ActiveInstance()->Ammo==0);
    if (!F.Player->TryBeginReload()) return false; const auto R3=F.Actions().Action;
    F.AdvanceTo(R3.End); TestTrue(TEXT("Only completed actual reload refills one bolt"),F.ActiveInstance()->Ammo==1&&F.Game->GetEquipmentView().Slots[1].Ammo==1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedFailedAdmission,
    "CodexDungeon.Content.RangedWeaponsAdapter.FailedResourceReloadAndAirSkillPreserveDomains",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedFailedAdmission::RunTest(const FString& Parameters)
{
    auto Weapon=RangedPrototype("WPN-STF-001"); Weapon.Tier=5;Weapon.Package=RangedStats::EPackage::Beneficial;
    Weapon.Affixes={{"AFF-P-009",20,{9,10}}};
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Actual Focus-cost staff fixture"),F.Create(Weapon))) return false;
    if (!F.Player->SpendFocus(93)) return false;
    const auto Before=F.Actions(); const auto View=F.Game->GetEquipmentView();
    F.Player->BeginAttack(); TestFalse(TEXT("Insufficient full8 Focus primary does not start"),F.Actions().Action.Active);
    TestFalse(TEXT("Insufficient19.2 Focus skill does not start"),F.Player->TryBeginWeaponSkill());
    TestFalse(TEXT("Staff has no reload action"),F.Player->TryBeginReload());
    TestTrue(TEXT("Failed requests consume no action/event/crit/focus/import/runtime domain"),F.Actions().NextActionId==Before.NextActionId&&F.Actions().NextEventId==Before.NextEventId&&F.Actions().NextFocusMutationId==Before.NextFocusMutationId&&F.Actions().Budget.Focus==7&&F.Game->GetEquipmentView().NextCritDraw==View.NextCritDraw&&F.Game->GetEquipmentView().NextRuntimeReceiptId==View.NextRuntimeReceiptId&&F.Game->GetEquipmentView().NextFocusReceiptId==View.NextFocusReceiptId&&F.State().Events.Num()==0);
    if (F.Player->RestoreFocus(1)!=1) return false;
    F.Player->StartJump(); const auto Air=F.Actions();
    TestFalse(TEXT("Air skill rejects even with resource restored"),F.Player->TryBeginWeaponSkill());
    TestFalse(TEXT("Air reload rejects without new facts"),F.Player->TryBeginReload());
    TestTrue(TEXT("Rejected air actions do not spend shared token or cursor"),!F.Actions().Budget.Grounded&&!F.Actions().Budget.AirPrimarySpent&&F.Actions().NextActionId==Air.NextActionId&&F.Actions().NextEventId==Air.NextEventId);
    F.Player->BeginAttack(); const auto A=F.Actions().Action;
    if (!TestTrue(TEXT("Exact discounted8 Focus permits one actual airborne primary"),A.Active&&A.StartedAirborne&&F.Actions().Budget.AirPrimarySpent)) return false;
    F.AdvanceTo(A.LockAt); TestTrue(TEXT("Actual lock reserves discounted whole trigger"),Near(F.Actions().Budget.ReservedFocus,8)&&Near(F.Actions().Budget.Focus,8));
    F.AdvanceTo(A.ActiveAt); TestTrue(TEXT("Real emission consumes only8, records actual spend"),Near(F.Actions().Budget.Focus,0)&&F.Actions().Budget.ReservedFocus==0&&F.Events(RangedEvent::ProjectileEmitted)==1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedAirTokenCancellation,
    "CodexDungeon.Content.RangedWeaponsAdapter.AirPrimaryCancellationDoesNotRefundToken",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedAirTokenCancellation::RunTest(const FString& Parameters)
{
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Air cancellation actual staff fixture"),F.Create(RangedPrototype("WPN-STF-001")))) return false;
    F.Player->StartJump(); F.Game->Tick(.03f); F.Player->BeginAttack(); const auto A=F.Actions().Action;
    if (!TestTrue(TEXT("Actual airborne admission spends one shared token before lock"),A.Active&&A.StartedAirborne&&F.Actions().Budget.AirPrimarySpent)) return false;
    F.Player->MoveOnGround({-1,0},.001f);
    TestTrue(TEXT("Legal reverse before40% cancels actual WA primary"),!F.Actions().Action.Active&&F.Actions().Action.Terminal==RangedWA::EEvent::Interrupted);
    const uint64 Cursor=F.Actions().NextActionId;
    F.Player->BeginAttack(); TestTrue(TEXT("Canceled air primary cannot open another before land"),!F.Actions().Action.Active&&F.Actions().NextActionId==Cursor&&F.Actions().Budget.AirPrimarySpent&&F.Actions().Budget.Focus==100&&F.Events(RangedEvent::ProjectileEmitted)==0);
    F.Game->Tick(.7f); F.Player->StartJump(); F.Player->BeginAttack();
    TestTrue(TEXT("Only next real takeoff grants a new single token"),F.Actions().Action.Active&&F.Actions().Action.ActionId==A.ActionId+1&&F.Actions().Action.StartedAirborne&&F.Actions().Budget.AirPrimarySpent);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedAirEmissionHeight,
    "CodexDungeon.Content.RangedWeaponsAdapter.AirEmissionUsesActualHeightWithoutDownAim",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedAirEmissionHeight::RunTest(const FString& Parameters)
{
    for (int32 Case=0;Case<2;++Case)
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Air actual-emission fixture"),F.Create(RangedPrototype("WPN-STF-001")))) return false;
        auto T=F.Target({180,0}); if (!T) return false;
        F.Player->StartJump(); F.Game->Tick(.2f); if (Case==1) T->StartJump();
        const float StartHeight=F.Player->JumpHeight; F.Player->BeginAttack(); const auto A=F.Actions().Action;
        if (!TestTrue(TEXT("One actual airborne staff primary accepted"),A.Active&&A.StartedAirborne)) return false;
        F.AdvanceTo(A.ActiveAt); const auto* P=F.Issued(A.ActionId); if (!P) return false; const auto E=*P;
        TestTrue(TEXT("Muzzle height is actual ballistic height at emission, not accepted start"),E.Origin.Height>65&&Near(E.Origin.Height,F.Player->GetWeaponMuzzleOrigin().Height,.0001)&&std::abs(E.Origin.Height-StartHeight)>5);
        F.AdvanceTo(A.Start+.6);
        if (Case==0) TestTrue(TEXT("High horizontal fireball never auto aims down at ground enemy"),T->Health==1000.f&&F.Events(RangedEvent::DirectHitCommitted)==0);
        else TestTrue(TEXT("Same fixed emitted height hits actually jumping target once"),Near(1000-T->Health,E.Damage,.0002)&&F.Events(RangedEvent::DirectHitCommitted)==1);
        TestTrue(TEXT("Real world projectile retains immutable source height and no Y tracking"),F.State().Projectiles.Num()==1&&Near(F.State().Projectiles[0].Source.Origin.Height,E.Origin.Height)&&Near(F.State().Projectiles[0].Position.Y,E.Origin.Y));
    }
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Air crossbow landing-reload actual fixture"),F.Create(RangedPrototype("WPN-XBW-001")))) return false;
        const double Takeoff=F.Game->GetSimulationTime();
        F.Player->StartJump(); F.Player->BeginAttack(); const auto A=F.Actions().Action;
        if (!TestTrue(TEXT("Immediate real takeoff accepts one crossbow primary"),A.Active&&A.StartedAirborne&&A.Start==Takeoff&&!F.Actions().Budget.Grounded)) return false;
        if (!TestTrue(TEXT("Reach full airborne crossbow recovery, not only its emission"),F.AdvanceTo(A.End))) return false;
        if (!TestTrue(TEXT("Last shot completes while airborne and leaves only pending automatic reload"),
            F.Player->JumpHeight>0.f&&F.Player->GetVerticalVelocity()<0.f&&!F.Actions().Budget.Grounded
            &&!F.Actions().Action.Active&&F.Actions().Action.Terminal==RangedWA::EEvent::Completed
            &&F.Actions().AutoReloadPendingId==F.Actions().EquippedId&&F.ActiveInstance()->Ammo==0
            &&F.Actions().Issued.size()==1&&F.Events(RangedEvent::ProjectileEmitted)==1)) return false;

        double Landing=-1,BeforeLanding=-1,BeforeClock=-1; float BeforeHeight=0,BeforeVelocity=0;
        for (int32 N=0;N<128&&Landing<0;++N)
        {
            const double Before=F.Game->GetSimulationTime();
            const double H=F.Player->JumpHeight,V=F.Player->GetVerticalVelocity();
            const double Remaining=(V+std::sqrt(V*V+3600.0*H))/1800.0;
            const double Adjacent=std::nextafter(Before,INFINITY)-Before;
            float Step=float(FMath::Min(.005,Remaining));
            if (double(Step)>Remaining) Step=std::nextafter(Step,0.f);
            if (!(Step>0.f)||Before+double(Step)==Before) Step=float(Adjacent);
            const double FrameEnd=Before+double(Step),Root=Before+Remaining;
            // A normal Tick ends no later than its observed ballistic root. If that
            // root rounds to the current clock, one adjacent-double step admits the
            // first representable landing. Neither case hides a later internal batch.
            if (!TestTrue(TEXT("Landing observation uses one bounded real motion interval"),
                FrameEnd>Before&&(FrameEnd<=Root||FrameEnd==std::nextafter(Before,INFINITY)))) return false;
            BeforeClock=F.Actions().Time; BeforeHeight=F.Player->JumpHeight; BeforeVelocity=F.Player->GetVerticalVelocity();
            F.Frame(Step);
            if (!TestTrue(TEXT("Actual motion observation makes clock progress"),F.Game->GetSimulationTime()==FrameEnd)) return false;
            if (F.Actions().Budget.Grounded)
            {
                Landing=F.Game->GetSimulationTime();BeforeLanding=Before;
                if (!TestTrue(TEXT("First grounded observation is the actual final landing batch"),
                    BeforeHeight>0.f&&F.Player->JumpHeight==0.f&&F.Player->GetVerticalVelocity()==0.f
                    &&F.Player->GetLandingVisualAge()==0.f)) return false;
            }
            else if (!TestTrue(TEXT("Air pending reload never starts or refills before actual landing"),
                !F.Actions().Action.Active&&F.Actions().AutoReloadPendingId==F.Actions().EquippedId
                &&F.ActiveInstance()->Ammo==0&&F.Actions().Issued.size()==1)) return false;
        }
        if (!TestTrue(TEXT("Actual crossbow takeoff reaches an observed landing after full recovery"),Landing>A.End&&Landing<Takeoff+.71)) return false;
        const auto R=F.Actions().Action; const double FullReloadEnd=Landing+1.10;
        AddInfo(FString::Printf(TEXT("Air XBW landing: before=%.17g preClock=%.17g preH=%.9g preV=%.9g landed=%.17g reloadStart=%.17g reloadEnd=%.17g expectedEnd=%.17g age=%.9g ammo=%.9g"),
            BeforeLanding,BeforeClock,double(BeforeHeight),double(BeforeVelocity),Landing,R.Start,R.End,FullReloadEnd,double(F.Player->GetLandingVisualAge()),F.ActiveInstance()->Ammo));
        TestTrue(TEXT("Pending automatic reload begins at actual landing, never at the prior air clock"),
            R.Active&&R.Type==RangedWA::EAction::Reload&&R.Start==Landing&&R.End==FullReloadEnd
            &&F.Actions().AutoReloadPendingId==0&&F.ActiveInstance()->Ammo==0);
        if (!TestTrue(TEXT("Reach last representable point before one full grounded reload"),F.AdvanceTo(std::nextafter(FullReloadEnd,0.0)))) return false;
        TestTrue(TEXT("No airborne progress or early refill shortens the full1.10 grounded reload"),
            F.Actions().Action.Active&&F.Actions().Action.Type==RangedWA::EAction::Reload&&F.ActiveInstance()->Ammo==0);
        if (!TestTrue(TEXT("Reach exact full grounded reload endpoint"),F.AdvanceTo(FullReloadEnd))) return false;
        int32 ReloadReceipts=0;
        for (const auto& Receipt:F.Actions().WeaponRuntimeHistory)
            if (Receipt.Kind==RangedWA::EWeaponMutation::ReloadCompleted)
            { ++ReloadReceipts;TestTrue(TEXT("Single actual refill receipt has the full landing-relative deadline"),Receipt.AtTime==FullReloadEnd&&Receipt.Action.ActionId==R.ActionId); }
        TestTrue(TEXT("Actual landing reload refills once without re-emitting the air primary"),
            !F.Actions().Action.Active&&F.Actions().Action.Terminal==RangedWA::EEvent::ReloadCompleted
            &&F.ActiveInstance()->Ammo==1&&F.Game->GetEquipmentView().Slots[1].Ammo==1&&ReloadReceipts==1
            &&F.Actions().Issued.size()==1&&F.Events(RangedEvent::ProjectileEmitted)==1);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedSpearNearest,
    "CodexDungeon.Content.RangedWeaponsAdapter.SpearSkillNearestOnePerIndependentSubhit",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedSpearNearest::RunTest(const FString& Parameters)
{
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Actual spear source and Q fixture"),F.Create(RangedPrototype("WPN-SPR-001")))) return false;
        auto Far=F.Target({210,0},12),Middle=F.Target({150,0},12),NearTarget=F.Target({90,0},12);
        auto Deadzone=F.Target({40,0}),OffLine=F.Target({100,16.001}); if (!Far||!Middle||!NearTarget||!Deadzone||!OffLine) return false;
        if (!F.Player->TryBeginWeaponSkill()) return false; const auto A=F.Actions().Action;
        F.AdvanceTo(A.Start+.23);
        TestTrue(TEXT("First .18-.22 chooses nearest legal center only"),NearTarget->bDead&&Middle->Health==12&&Far->Health==12&&Deadzone->Health==1000&&OffLine->Health==1000&&F.Events(RangedEvent::DirectHitCommitted)==1);
        F.AdvanceTo(A.Start+.27); TestEqual(TEXT("No damage in first retract gap"),F.Events(RangedEvent::DirectHitCommitted),1);
        F.AdvanceTo(A.Start+.33);
        TestTrue(TEXT("Second .28-.32 reselects current nearest living target"),Middle->bDead&&Far->Health==12&&F.Events(RangedEvent::DirectHitCommitted)==2);
        F.AdvanceTo(A.Start+.43);
        TestTrue(TEXT("Third .38-.42 independently chooses remaining target"),Far->bDead&&F.Events(RangedEvent::DirectHitCommitted)==3&&Deadzone->Health==1000&&OffLine->Health==1000);
        bool Independent=true; for (const auto& H:F.State().HitReceipts) Independent=Independent&&H.Key.ActionId==A.ActionId&&H.Key.SubhitId<3&&H.Damage==12&&H.Stagger==6;
        TestTrue(TEXT("Exactly three actual subhit receipts preserve12/6 and independent IDs"),Independent&&F.State().HitReceipts.Num()==3);
    }
    {
        FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Same-target triple fixture"),F.Create(RangedPrototype("WPN-SPR-001")))) return false;
        auto T=F.Target({100,0}); if (!T||!F.Player->TryBeginWeaponSkill()) return false; const auto A=F.Actions().Action;
        F.AdvanceTo(A.Start+.44); const auto* E=F.Issued(A.ActionId); if (!E) return false;
        TestTrue(TEXT("Own first-hit hurt protection cannot swallow same accepted action's later subhits"),Near(1000-T->Health,36*CriticalMultiplier(E->Action),.0002)&&F.Events(RangedEvent::DirectHitCommitted,T->GetRuntimeEntityId())==3);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedControllerInput,
    "CodexDungeon.Content.RangedWeaponsAdapter.ControllerAliasesHeldEdgesAndManualT",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedControllerInput::RunTest(const FString& Parameters)
{
    FRangedAdapterWorld F(this); if (!TestTrue(TEXT("Actual local controller with E/Q-equipped crossbow"),F.Create(RangedPrototype("WPN-XBW-001"),1,{0,0},true))) return false;
    if (!F.Key(EKeys::J,true)||!F.Key(EKeys::LeftMouseButton,true)) return false; F.Frame(.005f);
    const auto A=F.Actions().Action;
    if (!TestTrue(TEXT("J and mouse alias edges admit one real primary"),A.Active&&A.Type==RangedWA::EAction::Primary)) return false;
    const uint64 Cursor=F.Actions().NextActionId;
    F.Frame(.1f); TestEqual(TEXT("Held alias keys do not create repeat action"),F.Actions().NextActionId,Cursor);
    if (!F.Key(EKeys::J,false)||!F.Key(EKeys::LeftMouseButton,false)) return false;
    F.AdvanceTo(A.End+.1); if (!TestTrue(TEXT("Real shot entered automatic reload"),F.Actions().Action.Active&&F.Actions().Action.Type==RangedWA::EAction::Reload)) return false;
    if (!F.Key(EKeys::T,true)) return false; F.Frame(.005f);
    TestTrue(TEXT("Actual fresh T cancels reload with no refill"),!F.Actions().Action.Active&&F.ActiveInstance()->Ammo==0);
    F.Frame(.1f); TestFalse(TEXT("Held T does not rebegin canceled reload"),F.Actions().Action.Active);
    if (!F.Key(EKeys::T,false)||!F.Key(EKeys::T,true)) return false; F.Frame(.005f);
    if (!TestTrue(TEXT("Released and fresh T begins a real full reload"),F.Actions().Action.Active&&F.Actions().Action.Type==RangedWA::EAction::Reload)) return false;
    const auto R=F.Actions().Action; F.Key(EKeys::T,false); F.AdvanceTo(R.End);
    if (!F.Key(EKeys::K,true)||!F.Key(EKeys::RightMouseButton,true)) return false; F.Frame(.005f);
    TestTrue(TEXT("K/right mouse alias admits one actual ranged skill"),F.Actions().Action.Active&&F.Actions().Action.Type==RangedWA::EAction::Skill&&F.Actions().NextActionId==R.ActionId+2);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRangedSamePointInterruptedEmission,
    "CodexDungeon.Content.RangedWeaponsAdapter.SamePointPoiseOrDeathPreventsUnemittedCost",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRangedSamePointInterruptedEmission::RunTest(const FString& Parameters)
{
    for (const bool Staff:{false,true}) for (const bool Lethal:{false,true})
    {
        FRangedAdapterWorld F(this);
        if (!TestTrue(TEXT("Endpoint fixture uses actual loaded XBW or full-Focus STF through E/Q"),
            F.Create(RangedPrototype(Staff?"WPN-STF-001":"WPN-XBW-001")))) return false;
        auto K=F.Knight({80,0}); if (!TestNotNull(TEXT("Real proximity-waking shield source"),K)) return false;
        K->bAIEnabled=true;
        F.Game->Tick(.86f);
        const auto EnemyAction=K->GetStoneKnightDriver()->State().Action;
        if (!TestTrue(TEXT("Actual wake produced a normally admitted Shield with a future exact active deadline"),
            EnemyAction.InProgress&&EnemyAction.Kind==DungeonStoneKnight::EAttack::Shield
            &&EnemyAction.ActiveAt>F.Game->GetSimulationTime()+.5)) return false;
        // Establish sub-threshold poise through the public damage path. Its real
        // .65s direct protection must expire before the independently scheduled
        // shield; no kernel state, hit receipt, or iframe deadline is fabricated.
        F.Player->ApplyCombatHit(1,K,29);
        if (Lethal) F.Player->Health=10; // Explicit initial QA HP, like DamageBatch fixtures.
        if (!TestTrue(TEXT("Initial public hit is non-breaking and leaves full ranged resources"),
            !F.Player->bDead&&F.Actions().Budget.Focus==100&&F.Player->AttackTime==0)) return false;
        const auto Weapon=Staff?DungeonContentCombat::EWeapon::STF001:DungeonContentCombat::EWeapon::XBW001;
        const double Windup=DungeonContentCombat::GetWeaponDefinition(Weapon)->Primary[0].Windup;
        const double Impact=EnemyAction.ActiveAt;
        if (!TestTrue(TEXT("Reach actual shield deadline minus the frozen primary windup"),F.AdvanceTo(Impact-Windup))) return false;
        F.Player->BeginAttack();const auto A=F.Actions().Action;
        if (!TestTrue(TEXT("Accepted actual primary emission and real shield share the identical double boundary"),
            A.Active&&A.Type==RangedWA::EAction::Primary&&A.ActiveAt==Impact)) return false;
        F.AdvanceTo(A.LockAt);
        TestTrue(TEXT("Real lock reserves the full trigger before endpoint damage"),F.Actions().Action.Locked
            &&(Staff?F.Actions().Budget.ReservedFocus==10:F.ActiveInstance()->ReservedAmmo==1)
            &&F.Events(RangedEvent::ProjectileEmitted)==0);
        const uint64 Draw=F.Game->GetEquipmentView().NextCritDraw;
        if (!TestTrue(TEXT("Reach one millisecond before the common endpoint"),F.AdvanceTo(Impact-.001))) return false;
        if (!TestTrue(TEXT("Actual old direct protection has naturally ended before shield admission"),F.Player->CanReceiveDirectHit())) return false;
        if (!TestTrue(TEXT("Advance to exact shared endpoint, not a neighboring approximate tick"),F.AdvanceTo(Impact))) return false;
        const auto& Knight=K->GetStoneKnightDriver()->State();bool EnemyHit=false;
        for (const auto& H:Knight.HitReceipts)
            EnemyHit|=H.AttackId==EnemyAction.AttackId&&H.TargetId==F.Player->GetRuntimeEntityId();
        AddInfo(FString::Printf(TEXT("Endpoint %s lethal=%d: sim=%.17g shield=%.17g emission=%.17g hp=%.9g enemyHit=%d playerId=%llu action=%llu terminal=%d active=%d dead=%d canReceive=%d worldEmissions=%d ammo=%.9g focus=%.9g issued=%d"),
            Staff?TEXT("STF"):TEXT("XBW"),Lethal,F.Game->GetSimulationTime(),Impact,A.ActiveAt,
            F.Player->Health,EnemyHit,F.Player->GetRuntimeEntityId(),EnemyAction.AttackId,
            int32(F.Actions().Action.Terminal),F.Actions().Action.Active,F.Player->bDead,F.Player->CanReceiveDirectHit(),
            F.Events(RangedEvent::ProjectileEmitted),F.ActiveInstance()->Ammo,F.Actions().Budget.Focus,int32(F.Actions().Issued.size())));
        TestTrue(TEXT("Actual Shield receipt addresses the bound player at this endpoint"),EnemyHit);
        TestTrue(TEXT("Actual Shield reads its frozen13 damage"),Near(F.Player->Health,Lethal?0:86,.0002));
        TestFalse(TEXT("Actual Shield ended the interrupted weapon action"),F.Actions().Action.Active);
        TestEqual(TEXT("Actual lethal endpoint death state matches initial QA HP"),F.Player->bDead,Lethal);
        TestTrue(TEXT("Real shield contact was accepted and caused poise interruption or death"),EnemyHit
            &&Near(F.Player->Health,Lethal?0:86,.0002)&&!F.Actions().Action.Active
            &&F.Actions().Action.Terminal==RangedWA::EEvent::Interrupted&&F.Player->bDead==Lethal);
        TestTrue(TEXT("Damage-first endpoint creates no physical projectile or emission journal"),
            F.State().Projectiles.Num()==0&&F.Events(RangedEvent::ProjectileEmitted)==0);
        TestTrue(TEXT("An uncreated endpoint projectile cannot consume an actual-emission receipt"),
            F.Actions().Issued.empty()&&F.Actions().FocusHistory.empty()
            &&F.Actions().Budget.Focus==100&&!F.Actions().Budget.HasActualSpend
            &&F.Actions().Budget.ReservedFocus==0&&F.ActiveInstance()->ReservedAmmo==0
            &&(Staff?F.ActiveInstance()->Ammo==0:F.ActiveInstance()->Ammo==1));
        TestTrue(TEXT("Interrupted but genuinely locked primary keeps its one prior crit draw"),
            F.Game->GetEquipmentView().NextCritDraw==Draw);
    }
    return true;
}
#endif
