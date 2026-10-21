#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonEquipmentRuntime.h"
#include "../DungeonRoomLayout.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>

namespace
{
namespace Inventory = DungeonEquipmentInventory;
namespace EquipStats = DungeonEquipmentStats;
struct FEquipmentAdapterWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    ~FEquipmentAdapterWorld() { if (World) World->DestroyWorld(false); }
    bool Create()
    {
        if (!GEngine) return false;
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if (!World) return false;
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game = World->GetAuthGameMode<ADungeonGameMode>();
        Player = World->SpawnActor<ADungeonFighter>();
        if (!Game || !Player) return false;
        Player->SetActorTickEnabled(false);
        Player->ResetFighter({0,0}); // Initial QA placement only; transfers never reset any kernel.
        Game->PlayerFighter = Player; Game->bWaitingForStart = false; Game->bGameOver = false;
        return Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)
            && Player->IsEquipmentBound() && Game->GetEquipmentView().Bound
            && Game->GetEquipmentInventoryState() && World->GetAuthGameMode<ADungeonGameMode>() == Game;
    }
    // Decompose positive intervals into representable float ticks. This reaches the
    // shared double boundary, instead of calling two adjacent times "simultaneous".
    bool AdvanceTo(double At)
    {
        for (int32 N=0; N<16 && Game->GetSimulationTime()<At; ++N)
        {
            const double Remaining = At-Game->GetSimulationTime();
            float Step = float(Remaining);
            if (double(Step)>Remaining) Step=std::nextafter(Step,0.f);
            if (!(Step>0.f)) return false;
            const double Before=Game->GetSimulationTime(); Game->Tick(Step);
            if (Game->GetSimulationTime()<=Before) return false;
        }
        return Game->GetSimulationTime()==At;
    }
    bool Finish() { return AdvanceTo(Player->GetEquipmentActionDeadline()); }
    const Inventory::FState& State() const { return *Game->GetEquipmentInventoryState(); }
    uint64 ActiveId() const { const auto& S=State(); return S.Weapons[static_cast<std::size_t>(S.ActiveSlot)]; }
    const Inventory::FItem* Item(uint64 Id) const
    { for (const auto& I:State().Items) if (I.InstanceId==Id) return &I; return nullptr; }
    const FDungeonEquipmentSourceView* Source(uint64 Id) const
    { for (const auto& S:Game->GetEquipmentSources()) if (S.SourceId==Id) return &S; return nullptr; }
    bool SourceAvailable(uint64 Id) const { const auto* S=Source(Id); return S && !S->Consumed; }
    bool SourceConsumed(uint64 Id) const { const auto* S=Source(Id); return S && S->Consumed; }
    uint64 GroundSourceFor(uint64 Id) const
    { for (const auto& S:Game->GetEquipmentSources()) if (!S.Consumed && S.InstanceId==Id) return S.SourceId; return 0; }
    bool StartPickup(uint64 SourceId,int32 Slot=-1)
    {
        if (!Source(SourceId) || !Game->SelectEquipmentSource(SourceId)) return false;
        Game->TryInteractEquipment();
        if (Game->GetEquipmentView().NeedsSlotSelection)
            return Slot>=0 && Game->ConfirmEquipmentSlot(Slot,true) && Game->GetEquipmentView().Action.Active;
        return Game->GetEquipmentView().Action.Active;
    }
    ADungeonFighter* AddPrototype(FVector2D Position)
    {
        auto Enemy=World->SpawnActor<ADungeonFighter>(); if (!Enemy) return nullptr;
        Enemy->SetActorTickEnabled(false); Enemy->bEnemy=true; Enemy->bAIEnabled=false;
        Enemy->MaxHealth=100.f; Enemy->ResetFighter(Position); Game->Enemies.Add(Enemy); return Enemy;
    }
    ADungeonFighter* AddKnight()
    {
        auto Knight=World->SpawnActor<ADungeonFighter>(); if (!Knight) return nullptr;
        Knight->SetActorTickEnabled(false); Knight->ResetFighter({80,0}); Game->Enemies.Add(Knight);
        return Knight->InitializeStoneKnight(91001,Game->GetSimulationTime()) ? Knight : nullptr;
    }
    AActor* AddWall(double CenterX,double HalfY=80)
    {
        auto Wall=World->SpawnActor<AActor>(); if (!Wall) return nullptr;
        auto Box=NewObject<UBoxComponent>(Wall); Wall->SetRootComponent(Box); Box->SetBoxExtent({5,HalfY,50});
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Box->SetCollisionObjectType(ECC_WorldStatic);
        Box->SetCollisionResponseToAllChannels(ECR_Block); Box->RegisterComponentWithWorld(World);
        Wall->SetActorLocation({CenterX,0,0}); return Wall;
    }
};
Inventory::FItem Prototype(const char* Content)
{ Inventory::FItem I; I.ContentId=Content; return I; }
Inventory::FItem HealthArmor(bool Negative=false,bool FasterFocus=false)
{
    auto I=Prototype("ARM-LGT-001"); I.Tier=5;
    if (Negative) { I.Package=EquipStats::EPackage::Cursed; I.Affixes={{"AFF-N-011",20,{9,10}}}; }
    else if (FasterFocus) { I.Package=EquipStats::EPackage::Mixed;
        I.Affixes={{"AFF-N-014",25,{9,10}},{"AFF-P-017",25,{9,10}},{"AFF-P-018",25,{9,10}}}; }
    else { I.Package=EquipStats::EPackage::Beneficial; I.Affixes={{"AFF-P-017",25,{9,10}}}; }
    return I;
}
EquipStats::FInstance StatView(const Inventory::FItem& I)
{
    EquipStats::FInstance R; R.TemplateId=I.ContentId; R.Grade=I.Grade; R.Enchant.Package=I.Package; R.Enchant.Tier=I.Tier;
    for (const auto& A:I.Affixes) R.Enchant.Affixes.push_back({A.Id,A.Magnitude}); return R;
}
EquipStats::FResolved ExpectedStats(const FEquipmentAdapterWorld& F)
{
    EquipStats::FLoadout L; L.PreviousHP=F.Player->Health;
    if (const auto* I=F.Item(F.ActiveId())) L.Weapon=StatView(*I);
    const auto& S=F.State(); if (const auto* I=F.Item(S.Weapons[static_cast<std::size_t>(1-S.ActiveSlot)])) L.BackupWeapon=StatView(*I);
    if (const auto* I=F.Item(S.Armor)) L.Armor=StatView(*I);
    return EquipStats::Resolve(L); // Borrowed strings stay inside this synchronous call.
}
bool SameUnspentDomains(const FDungeonEquipmentView& A,const FDungeonEquipmentView& B)
{
    return A.NextInstanceId==B.NextInstanceId && A.NextSourceId==B.NextSourceId
        && A.NextOperationId==B.NextOperationId && A.NextEquipmentActionId==B.NextEquipmentActionId
        && A.NextRuntimeReceiptId==B.NextRuntimeReceiptId && A.NextImportReceiptId==B.NextImportReceiptId
        && A.NextFocusReceiptId==B.NextFocusReceiptId && A.NextCritDraw==B.NextCritDraw;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentRealPickupTimelinesAndStats,
    "CodexDungeon.Content.EquipmentAdapter.RealPickupTimelinesAndStats",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentRealPickupTimelinesAndStats::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Actual GameMode binds a new equipment run"),F.Create())) return false;
    const uint64 Starter=F.ActiveId(); const auto& Identity=F.Game->GetEquipmentView();
    TestTrue(TEXT("Run GUID and numeric owner/room aliases are explicit nonzero facts"),Identity.RunGuid.IsValid()&&Identity.RunAlias&&Identity.OwnerId&&Identity.RoomInstanceId);
    TestEqual(TEXT("Integration fixture starts with one sword instance only"),F.State().Weapons[1],uint64(0));
    const auto GSW=F.Game->RegisterEquipmentSource(TEXT("test.timeline.heavy"),Prototype("WPN-GSW-001"),{40,0});
    if (!TestTrue(TEXT("Actual ground source registers a stable heavy instance"),GSW.Ok()&&GSW.SourceId&&GSW.InstanceId&&GSW.InstanceId!=Starter)) return false;
    TestTrue(TEXT("Source and inventory publish the same instance and room"),F.Source(GSW.SourceId)&&F.Source(GSW.SourceId)->InstanceId==GSW.InstanceId&&F.Source(GSW.SourceId)->RoomInstanceId==F.Game->GetEquipmentView().RoomInstanceId);
    if (!TestTrue(TEXT("Selected ground heavy begins the normal E action"),F.StartPickup(GSW.SourceId))) return false;
    const double Start=F.Game->GetSimulationTime(),End=F.Player->GetEquipmentActionDeadline();
    TestTrue(TEXT("Weapon pickup takes the full .35 seconds"),End==Start+.35);
    if (!TestTrue(TEXT("Advance just before weapon commit"),F.AdvanceTo(End-.001))) return false;
    TestTrue(TEXT("Old sword and unconsumed ground remain until completion"),F.ActiveId()==Starter&&F.SourceAvailable(GSW.SourceId));
    if (!TestTrue(TEXT("Advance to exact weapon deadline"),F.AdvanceTo(End))) return false;
    TestTrue(TEXT("Empty weapon slot pickup consumes source and activates the actual GSW instance"),F.ActiveId()==GSW.InstanceId&&F.State().Weapons[0]==Starter&&F.SourceConsumed(GSW.SourceId)&&F.Player->WeaponId==TEXT("WPN-GSW-001"));
    const auto Armor=F.Game->RegisterEquipmentSource(TEXT("test.timeline.armor"),Prototype("ARM-LGT-001"),{-40,0});
    if (!TestTrue(TEXT("Real body armor begins E"),Armor.Ok()&&F.StartPickup(Armor.SourceId))) return false;
    const double ArmorEnd=F.Player->GetEquipmentActionDeadline();
    TestTrue(TEXT("Body pickup takes .50 seconds"),ArmorEnd==F.Game->GetSimulationTime()+.5);
    F.AdvanceTo(ArmorEnd-.001); TestTrue(TEXT("No early body stats or source consumption"),F.State().Armor==0&&F.Player->GetArmorRating()==0.f&&F.SourceAvailable(Armor.SourceId));
    if (!TestTrue(TEXT("Armor commits exactly at its deadline"),F.AdvanceTo(ArmorEnd))) return false;
    const auto Expected=ExpectedStats(F);
    TestTrue(TEXT("Player armor/move/poise are one frozen Stats resolution"),Expected.Ok()&&F.State().Armor==Armor.InstanceId&&F.SourceConsumed(Armor.SourceId)
        && FMath::IsNearlyEqual(double(F.Player->GetArmorRating()),Expected.Armor,1.e-5)
        && FMath::IsNearlyEqual(double(F.Player->GetMoveSpeed()),Expected.MoveSpeed,1.e-4)
        && FMath::IsNearlyEqual(double(F.Player->GetPoiseThreshold()),Expected.Poise,1.e-5));
    auto Target=F.AddPrototype({100,0}); if (!TestNotNull(TEXT("Real heavy attack target"),Target)) return false;
    F.Player->BeginAttack(); const auto Heavy=F.Player->GetMeleeCombatState().Action;
    TestTrue(TEXT("GSW uses its real 450/140/600ms primary and acquired identity"),Heavy.Active&&Heavy.Weapon==DungeonContentCombat::EWeapon::GSW001&&Heavy.WeaponInstanceId==GSW.InstanceId
        && FMath::IsNearlyEqual(Heavy.ActiveStart-Heavy.Start,.45,1.e-9)&&FMath::IsNearlyEqual(Heavy.End-Heavy.Start,1.19,1.e-9));
    F.AdvanceTo(Heavy.LockTime); const auto Locked=F.Player->GetMeleeCombatState().Action;
    TestTrue(TEXT("Heavy lock uses46 damage with actual frozen critical outcome"),Locked.Locked&&FMath::IsNearlyEqual(Locked.Damage,46*Expected.DamageMultiplier*(Locked.Critical?Locked.CritMultiplier:1),1.e-7));
    F.AdvanceTo(Heavy.ActiveStart+.001);
    TestTrue(TEXT("GameMode actually applies the heavy primary damage"),FMath::IsNearlyEqual(double(Target->Health),100-Locked.Damage,.001));
    F.AdvanceTo(Heavy.End);
    TestTrue(TEXT("GSW actual secondary starts after full recovery"),F.Player->TryBeginWeaponSkill());
    const auto Skill=F.Player->GetWeaponSkillAction();
    TestTrue(TEXT("Heavy secondary is heavy_press rather than SWD advance_slash"),Skill.Weapon==DungeonContentCombat::EWeapon::GSW001&&Skill.InstanceId==GSW.InstanceId
        && FMath::IsNearlyEqual(Skill.ActiveAt-Skill.Start,.68,1.e-9)&&FMath::IsNearlyEqual(Skill.End-Skill.Start,1.69,1.e-9));
    F.AdvanceTo(Skill.LockAt);
    TestTrue(TEXT("Heavy skill keeps its own eight-second cooldown"),FMath::IsNearlyEqual(F.Player->GetWeaponSkillCooldownRemaining(),Skill.LockAt+8-F.Game->GetSimulationTime(),1.e-7));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentSameTemplateAndBackupReplacement,
    "CodexDungeon.Content.EquipmentAdapter.SameTemplateAndBackupReplacement",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentSameTemplateAndBackupReplacement::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Same-template fixture is a real bound run"),F.Create())) return false;
    const uint64 Starter=F.ActiveId(); const auto GSW=F.Game->RegisterEquipmentSource(TEXT("test.identity.heavy"),Prototype("WPN-GSW-001"),{40,0});
    if (!GSW.Ok()||!F.StartPickup(GSW.SourceId)||!F.Finish()) return false;
    TestTrue(TEXT("Q starts a real .35s action"),F.Game->TrySwitchEquipment()); const double End=F.Player->GetEquipmentActionDeadline();
    TestTrue(TEXT("Q is timed at .35"),End==F.Game->GetSimulationTime()+.35); F.AdvanceTo(End-.001);
    TestEqual(TEXT("Current weapon remains heavy before Q completes"),F.ActiveId(),GSW.InstanceId); F.AdvanceTo(End);
    TestEqual(TEXT("Q activates the existing starter without creating it again"),F.ActiveId(),Starter);
    auto Sword=Prototype("WPN-SWD-001"); Sword.Grade=3; Sword.Package=EquipStats::EPackage::Beneficial; Sword.Tier=5; Sword.Affixes={{"AFF-P-001",25,{9,10}}};
    const auto New=F.Game->RegisterEquipmentSource(TEXT("test.identity.second_sword"),Sword,{-40,0});
    if (!TestTrue(TEXT("Same definition gets a distinct owned instance identity"),New.Ok()&&New.InstanceId!=Starter)) return false;
    const uint64 Operation=F.Game->GetEquipmentView().NextOperationId;
    F.Game->SelectEquipmentSource(New.SourceId); F.Game->TryInteractEquipment();
    TestTrue(TEXT("Full weapons open explicit selection without action/source/operation consumption"),F.Game->GetEquipmentView().NeedsSlotSelection&&!F.Game->GetEquipmentView().Action.Active
        && F.SourceAvailable(New.SourceId)&&F.Game->GetEquipmentView().NextOperationId==Operation);
    if (!TestTrue(TEXT("Explicit backup slot confirmation starts replacement"),F.Game->ConfirmEquipmentSlot(1,true)&&F.Finish())) return false;
    const uint64 Dropped=F.GroundSourceFor(GSW.InstanceId);
    TestTrue(TEXT("Backup replacement keeps active and drops the exact previous heavy"),F.ActiveId()==Starter&&F.State().Weapons[1]==New.InstanceId&&Dropped&&F.Source(Dropped)->Item.ContentId=="WPN-GSW-001");
    F.Player->BeginAttack(); const auto First=F.Player->GetMeleeCombatState().Action; F.AdvanceTo(First.LockTime);
    const auto FirstLocked=F.Player->GetMeleeCombatState().Action;
    TestTrue(TEXT("Backup grade and damage affix do not leak into current starter"),FirstLocked.WeaponInstanceId==Starter&&FMath::IsNearlyEqual(FirstLocked.Damage,26*(FirstLocked.Critical?FirstLocked.CritMultiplier:1),1.e-7)); F.AdvanceTo(First.End);
    if (!F.Game->TrySwitchEquipment()||!F.Finish()) return false;
    F.Player->BeginAttack(); const auto Second=F.Player->GetMeleeCombatState().Action; F.AdvanceTo(Second.LockTime); const auto SecondLocked=F.Player->GetMeleeCombatState().Action;
    TestTrue(TEXT("Switching between identical template names changes the real combat instance and stats"),F.ActiveId()==New.InstanceId&&SecondLocked.WeaponInstanceId==New.InstanceId
        && FMath::IsNearlyEqual(SecondLocked.Damage,26*1.4*(SecondLocked.Critical?SecondLocked.CritMultiplier:1),1.e-7));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentInstanceCooldownSurvivesTransfers,
    "CodexDungeon.Content.EquipmentAdapter.InstanceCooldownSurvivesTransfers",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentInstanceCooldownSurvivesTransfers::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("CD transfer fixture bound"),F.Create())) return false;
    const uint64 Original=F.ActiveId(); if (!TestTrue(TEXT("Original sword performs a real skill"),F.Player->TryBeginWeaponSkill())) return false;
    const auto Skill=F.Player->GetWeaponSkillAction(); F.AdvanceTo(Skill.End);
    const auto* OriginalAction=F.Player->GetWeaponActionsState().Instances.empty()?nullptr:&F.Player->GetWeaponActionsState().Instances[0];
    if (!TestTrue(TEXT("Actual old sword lock recorded4.08 deadline"),OriginalAction&&OriginalAction->InstanceId==Original&&FMath::IsNearlyEqual(OriginalAction->CooldownDeadline,4.08,1.e-9))) return false;
    const double Deadline=OriginalAction->CooldownDeadline;
    const auto Heavy=F.Game->RegisterEquipmentSource(TEXT("test.cd.heavy"),Prototype("WPN-GSW-001"),{40,0});
    if (!Heavy.Ok()||!F.StartPickup(Heavy.SourceId)||!F.Finish()||!F.Game->TrySwitchEquipment()||!F.Finish()) return false;
    TestTrue(TEXT("Q roundtrip retains original deadline and denies early skill"),F.ActiveId()==Original&&F.Item(Original)&&!F.Player->TryBeginWeaponSkill()&&FMath::IsNearlyEqual(F.Item(Original)->SkillCooldownDeadline,Deadline,1.e-9));
    const auto New=F.Game->RegisterEquipmentSource(TEXT("test.cd.replacement"),Prototype("WPN-SWD-001"),{-40,0});
    if (!New.Ok()||!F.StartPickup(New.SourceId,0)||!F.Finish()) return false;
    const uint64 OldSource=F.GroundSourceFor(Original);
    if (!TestTrue(TEXT("Old sword drops as the original instance with full runtime facts"),OldSource&&F.Source(OldSource)->Item.InstanceId==Original&&F.Source(OldSource)->Item.Ammo==0&&FMath::IsNearlyEqual(F.Source(OldSource)->Item.SkillCooldownDeadline,Deadline,1.e-9))) return false;
    if (!TestTrue(TEXT("Original sword may be normally selected and repicked"),F.StartPickup(OldSource,0)&&F.Finish())) return false;
    TestTrue(TEXT("Repick cannot reset CD or recreate same identity"),F.ActiveId()==Original&&F.Item(Original)&&F.Item(Original)->Ammo==0&&FMath::IsNearlyEqual(F.Item(Original)->SkillCooldownDeadline,Deadline,1.e-9)&&!F.Player->TryBeginWeaponSkill());
    int32 Count=0; for (const auto& I:F.Player->GetWeaponActionsState().Instances) if (I.InstanceId==Original) ++Count;
    TestEqual(TEXT("Weapon action registry retains exactly one original instance"),Count,1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentFailedAdmissionPreservesDomains,
    "CodexDungeon.Content.EquipmentAdapter.FailedAdmissionPreservesDomains",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentFailedAdmissionPreservesDomains::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Admission fixture bound"),F.Create())) return false;
    auto Invalid=Prototype("WPN-GSW-001"); Invalid.Grade=99; const auto BeforeInvalid=F.Game->GetEquipmentView();
    TestFalse(TEXT("Illegal prototype cannot create a world source"),F.Game->RegisterEquipmentSource(TEXT("test.failure.correctable"),Invalid,{40,0}).Ok());
    TestTrue(TEXT("Rejected registration consumes no identity or receipt domain"),SameUnspentDomains(BeforeInvalid,F.Game->GetEquipmentView()));
    TestTrue(TEXT("Source beyond bounded floor MaxX rejects without spending domains"),
        !F.Game->RegisterEquipmentSource(TEXT("test.failure.outside_x"),Prototype("WPN-GSW-001"),{DungeonRoomLayout::MaxX+40,0}).Ok()
        && SameUnspentDomains(BeforeInvalid,F.Game->GetEquipmentView()));
    TestTrue(TEXT("Source beyond bounded floor MaxY rejects without spending domains"),
        !F.Game->RegisterEquipmentSource(TEXT("test.failure.outside_y"),Prototype("WPN-GSW-001"),{0,DungeonRoomLayout::MaxY+40}).Ok()
        && SameUnspentDomains(BeforeInvalid,F.Game->GetEquipmentView()));
    TestTrue(TEXT("Nonfinite source position rejects without spending domains"),
        !F.Game->RegisterEquipmentSource(TEXT("test.failure.nan_position"),Prototype("WPN-GSW-001"),{std::numeric_limits<double>::quiet_NaN(),0}).Ok()
        && SameUnspentDomains(BeforeInvalid,F.Game->GetEquipmentView()));
    const auto Legal=F.Game->RegisterEquipmentSource(TEXT("test.failure.correctable"),Prototype("WPN-GSW-001"),{81,0});
    if (!TestTrue(TEXT("Same logical source retries with legal prototype"),Legal.Ok())) return false;
    const auto BeforeRange=F.Game->GetEquipmentView(); F.Game->SelectEquipmentSource(Legal.SourceId); F.Game->TryInteractEquipment();
    TestTrue(TEXT("Out-of-range pickup leaves ownership/source/domains intact"),!F.Game->GetEquipmentView().Action.Active&&F.SourceAvailable(Legal.SourceId)&&SameUnspentDomains(BeforeRange,F.Game->GetEquipmentView()));
    F.Player->SetActorLocation({1,0,0}); // QA positioning, never inventory or clock mutation.
    auto Wall=F.AddWall(30); if (!TestNotNull(TEXT("Actual LOS blocking geometry"),Wall)) return false;
    const auto BeforeWall=F.Game->GetEquipmentView(); F.Game->SelectEquipmentSource(Legal.SourceId); F.Game->TryInteractEquipment();
    TestTrue(TEXT("Wall-blocked source cannot start E or spend domains"),!F.Game->GetEquipmentView().Action.Active&&F.SourceAvailable(Legal.SourceId)&&SameUnspentDomains(BeforeWall,F.Game->GetEquipmentView()));
    Wall->SetActorEnableCollision(false);
    TestTrue(TEXT("Corrected real world admission can use unchanged source"),F.StartPickup(Legal.SourceId)&&F.Finish()&&F.ActiveId()==Legal.InstanceId);
    const auto Corner=F.Game->RegisterEquipmentSource(TEXT("test.failure.rectangle_corner"),Prototype("ARM-LGT-001"),F.Player->GetGroundPosition()+FVector2D(80,40));
    TestTrue(TEXT("80x40 targeting corner is legal rectangle geometry, not an ellipse"),Corner.Ok()&&F.StartPickup(Corner.SourceId)&&F.Finish()&&F.State().Armor==Corner.InstanceId);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentSamePointDamageAndDeathBeforeCommit,
    "CodexDungeon.Content.EquipmentAdapter.SamePointDamageAndDeathBeforeCommit",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentSamePointDamageAndDeathBeforeCommit::RunTest(const FString& Parameters)
{
    for (const bool Lethal:{false,true})
    {
        FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Same-point fixture bound"),F.Create())) return false;
        if (Lethal) F.Player->Health=10.f; // Legal initial missing HP; no fake damage or receipt.
        const auto Armor=F.Game->RegisterEquipmentSource(TEXT("test.samepoint.armor"),Prototype("ARM-LGT-001"),{-40,0});
        auto Knight=F.AddKnight(); if (!TestTrue(TEXT("Real stone shield source and enemy exist"),Armor.Ok()&&Knight)) return false;
        F.Game->Tick(.9f); const auto Attack=Knight->GetStoneKnightDriver()->State().Action;
        if (!TestTrue(TEXT("Normal proximity wake produced a real pending Shield attack"),Attack.InProgress&&Attack.Kind==DungeonStoneKnight::EAttack::Shield&&Attack.ActiveAt>F.Game->GetSimulationTime()+.5)) return false;
        if (!TestTrue(TEXT("Reach actual shield time minus body pickup duration exactly"),F.AdvanceTo(Attack.ActiveAt-.5))) return false;
        const uint64 Operation=F.Game->GetEquipmentView().NextOperationId;
        if (!TestTrue(TEXT("Normal armor pickup starts during shield windup"),F.StartPickup(Armor.SourceId))) return false;
        if (!TestTrue(TEXT("Damage and equipment share the identical absolute boundary"),F.Player->GetEquipmentActionDeadline()==Attack.ActiveAt)) return false;
        F.Game->Tick(.51f);
        TestTrue(TEXT("Same-point positive HP loss cancels before armor ownership or source consumption"),F.State().Armor==0&&F.SourceAvailable(Armor.SourceId)&&!F.Game->GetEquipmentView().Action.Active&&F.Game->GetEquipmentView().NextOperationId==Operation);
        if (Lethal) TestTrue(TEXT("Lethal real shield hit wins over commit and reports run death"),F.Player->Health==0.f&&F.Player->bDead&&F.Game->bGameOver);
        else TestTrue(TEXT("Same-point13 damage reads old unarmored stats, not newly selected armor14"),FMath::IsNearlyEqual(F.Player->Health,87.f,.001f)&&!F.Player->bDead);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentFinalHPAndContinuousFocus,
    "CodexDungeon.Content.EquipmentAdapter.FinalHPAndContinuousFocus",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentFinalHPAndContinuousFocus::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("HP/Focus fixture bound"),F.Create())) return false;
    const uint64 BeforeFullRestore=F.Game->GetEquipmentView().NextFocusReceiptId;
    TestTrue(TEXT("Full Focus restoration applies zero and consumes no receipt"),F.Player->RestoreFocus(10)==0.f&&F.Game->GetEquipmentView().NextFocusReceiptId==BeforeFullRestore);
    if (!TestTrue(TEXT("Spend50 uses actual bound Focus authority"),F.Player->SpendFocus(50))) return false;
    const uint64 BeforeRestore=F.Game->GetEquipmentView().NextFocusReceiptId;
    TestTrue(TEXT("Positive Focus restoration uses one receipt and updates the sole budget"),F.Player->RestoreFocus(10)==10.f&&F.Player->Focus==60.f&&F.Player->GetWeaponActionsState().Budget.Focus==60&&F.Game->GetEquipmentView().NextFocusReceiptId==BeforeRestore+1);
    if (!TestTrue(TEXT("Actual spend10 returns the resource control to50"),F.Player->SpendFocus(10))) return false;
    const auto First=F.Game->RegisterEquipmentSource(TEXT("test.hp.first"),HealthArmor(),{40,0});
    if (!First.Ok()||!F.StartPickup(First.SourceId)||!F.Finish()) return false;
    TestTrue(TEXT("Adding25 percent max HP does not heal missing health"),F.Player->MaxHealth==125.f&&F.Player->Health==100.f&&F.Player->Focus==50.f);
    F.Player->Health=120.f; // QA initial damage level under the now-real125 maximum.
    const auto Second=F.Game->RegisterEquipmentSource(TEXT("test.hp.second"),HealthArmor(false,true),{-40,0});
    if (!Second.Ok()||!F.StartPickup(Second.SourceId,2)||!F.Finish()) return false;
    TestTrue(TEXT("Replacing125max armor with125max armor never transiently truncates HP to100"),F.Player->MaxHealth==125.f&&F.Player->Health==120.f);
    TestTrue(TEXT("Equip at t1 does not reset last Focus spend or give early recovery"),FMath::IsNearlyEqual(F.Game->GetSimulationTime(),1.0,1.e-9)&&F.Player->Focus==50.f&&F.Player->GetWeaponActionsState().Budget.HasActualSpend&&F.Player->GetWeaponActionsState().Budget.LastActualSpend==0);
    const auto Curse=F.Game->RegisterEquipmentSource(TEXT("test.hp.curse"),HealthArmor(true),{40,0});
    if (!Curse.Ok()||!F.StartPickup(Curse.SourceId,2)) return false;
    F.AdvanceTo(1.25);
    TestTrue(TEXT("Pending replacement still integrates old15 Focus per second"),FMath::IsNearlyEqual(F.Player->Focus,53.75f,.001f));
    if (!F.Finish()) return false;
    TestTrue(TEXT("Cursed final max80 truncates once after old-rate recovery through t1.5"),F.Player->MaxHealth==80.f&&F.Player->Health==80.f&&FMath::IsNearlyEqual(F.Player->Focus,57.5f,.001f));
    const uint64 OldSource=F.GroundSourceFor(First.InstanceId);
    if (!TestTrue(TEXT("Earlier plus-health armor exists as the same ground instance"),OldSource!=0&&F.StartPickup(OldSource,2))) return false;
    F.AdvanceTo(1.75); TestTrue(TEXT("Post-commit new armor uses12 Focus per second"),FMath::IsNearlyEqual(F.Player->Focus,60.5f,.001f));
    if (!F.Finish()) return false;
    const auto& Budget=F.Player->GetWeaponActionsState().Budget;
    TestTrue(TEXT("Increasing max again does not heal or reset Focus authority"),F.Player->MaxHealth==125.f&&F.Player->Health==80.f&&FMath::IsNearlyEqual(F.Player->Focus,63.5f,.001f)
        && FMath::IsNearlyEqual(double(F.Player->Focus),Budget.Focus,.001)&&Budget.LastActualSpend==0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentWallBlockedMovementCancels,
    "CodexDungeon.Content.EquipmentAdapter.WallBlockedMovementCancels",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentWallBlockedMovementCancels::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Movement cancellation fixture bound"),F.Create())) return false;
    const auto Armor=F.Game->RegisterEquipmentSource(TEXT("test.movement.armor"),Prototype("ARM-LGT-001"),{-40,0});
    if (!Armor.Ok()||!TestNotNull(TEXT("Wall touches player's real right boundary"),F.AddWall(23))||!F.StartPickup(Armor.SourceId)) return false;
    F.Game->Tick(.2f); const auto Position=F.Player->GetGroundPosition(); const uint64 Operation=F.Game->GetEquipmentView().NextOperationId;
    F.Player->MoveOnGround({1,0},.1f);
    TestTrue(TEXT("Movement is physically blocked at the current position"),F.Player->GetGroundPosition().Equals(Position,.001));
    TestFalse(TEXT("Movement intent cancels before displacement, even against a wall"),F.Game->GetEquipmentView().Action.Active);
    F.Game->Tick(.4f);
    TestTrue(TEXT("Canceled armor cannot late-commit or consume its source/operation"),F.State().Armor==0&&F.SourceAvailable(Armor.SourceId)&&F.Game->GetEquipmentView().NextOperationId==Operation);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentLegalAndFailedDodgeAdmission,
    "CodexDungeon.Content.EquipmentAdapter.LegalAndFailedDodgeAdmission",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentLegalAndFailedDodgeAdmission::RunTest(const FString& Parameters)
{
    {
        FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Dodge cooldown cancellation fixture binds an actual equipment run"),F.Create())) return false;
        if (!TestTrue(TEXT("Initial real dodge is accepted"),F.Player->TryBeginDodge({1,0}))) return false;
        F.Game->Tick(.401f);
        TestTrue(TEXT("Dodge completed but its genuine start+1.2 cooldown remains"),F.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Idle&&F.Game->GetSimulationTime()<F.Player->GetDodgeState().ReadyAt);
        if (!TestTrue(TEXT("Real Focus spend establishes an unchanged resource control"),F.Player->SpendFocus(50))) return false;
        const auto Heavy=F.Game->RegisterEquipmentSource(TEXT("test.dodge.failed"),Prototype("WPN-GSW-001"),F.Player->GetGroundPosition()+FVector2D(40,0));
        if (!Heavy.Ok()||!F.StartPickup(Heavy.SourceId)) return false; const double Deadline=F.Player->GetEquipmentActionDeadline();
        TestFalse(TEXT("Unexpired real dodge cooldown rejects another dodge"),F.Player->TryBeginDodge({1,0}));
        TestTrue(TEXT("Failed dodge preserves accepted pickup deadline and Focus"),F.Game->GetEquipmentView().Action.Active&&F.Player->GetEquipmentActionDeadline()==Deadline&&F.Player->Focus==50.f);
        TestTrue(TEXT("Unaffected pickup still completes normally"),F.Finish()&&F.ActiveId()==Heavy.InstanceId&&F.Player->Focus==50.f);
    }
    {
        FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Zero-resource legal dodge fixture binds an actual equipment run"),F.Create())) return false;
        if (!TestTrue(TEXT("Real zero Focus is legal before resource-free dodge"),F.Player->SpendFocus(100))) return false;
        const auto Heavy=F.Game->RegisterEquipmentSource(TEXT("test.dodge.legal"),Prototype("WPN-GSW-001"),{40,0});
        if (!Heavy.Ok()||!F.StartPickup(Heavy.SourceId)) return false;
        const uint64 Operation=F.Game->GetEquipmentView().NextOperationId;
        TestTrue(TEXT("Legal real dodge cancels pickup without requiring spending or restoring Focus"),F.Player->TryBeginDodge({1,0})&&!F.Game->GetEquipmentView().Action.Active&&F.Player->Focus==0.f);
        F.Game->Tick(.41f);
        TestTrue(TEXT("Dodge-canceled pickup leaves ground instance and inventory operation unconsumed"),F.SourceAvailable(Heavy.SourceId)&&F.Game->GetEquipmentView().NextOperationId==Operation&&F.State().Weapons[1]==0);
    }
    {
        FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Q exclusion fixture binds an actual equipment run"),F.Create())) return false;
        const auto Heavy=F.Game->RegisterEquipmentSource(TEXT("test.dodge.switch"),Prototype("WPN-GSW-001"),{40,0});
        if (!Heavy.Ok()||!F.StartPickup(Heavy.SourceId)||!F.Finish()||!F.Game->TrySwitchEquipment()) return false;
        const double Deadline=F.Player->GetEquipmentActionDeadline();
        TestFalse(TEXT("Q's independent switch action cannot be dodge-canceled"),F.Player->TryBeginDodge({1,0}));
        TestTrue(TEXT("Denied dodge during Q does not spend Focus or change completion"),F.Player->Focus==100.f&&F.Player->GetEquipmentActionDeadline()==Deadline&&F.Finish());
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FEquipmentCritDrawFollowsRealLocks,
    "CodexDungeon.Content.EquipmentAdapter.CritDrawFollowsRealLocks",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FEquipmentCritDrawFollowsRealLocks::RunTest(const FString& Parameters)
{
    FEquipmentAdapterWorld F; if (!TestTrue(TEXT("Critical draw fixture bound"),F.Create())) return false;
    const uint64 Before=F.Game->GetEquipmentView().NextCritDraw;
    for (int32 N=0;N<20;++N) { F.Game->GetEquipmentView(); F.Player->GetArmorRating(); F.Player->GetMoveSpeed(); }
    TestEqual(TEXT("Read-only views and context queries consume no critical draw"),F.Game->GetEquipmentView().NextCritDraw,Before);
    F.Player->BeginAttack(); const auto Primary=F.Player->GetMeleeCombatState().Action;
    if (!TestTrue(TEXT("Real starter primary accepted before lock"),Primary.Active&&!Primary.Locked)) return false;
    F.AdvanceTo(Primary.LockTime-.001);
    TestEqual(TEXT("Uncommitted windup consumes no random cursor"),F.Game->GetEquipmentView().NextCritDraw,Before);
    F.Player->TryBeginWeaponSkill(false); F.AdvanceTo(Primary.LockTime);
    TestTrue(TEXT("Actual successful primary lock consumes exactly one draw"),F.Player->GetMeleeCombatState().Action.Locked&&F.Game->GetEquipmentView().NextCritDraw==Before+1);
    F.AdvanceTo(Primary.ActiveStart); for (int32 N=0;N<20;++N) F.Game->GetEquipmentView();
    TestEqual(TEXT("Subdivisions, emission and repeated queries do not redraw a locked attack"),F.Game->GetEquipmentView().NextCritDraw,Before+1); F.AdvanceTo(Primary.End);
    const auto Heavy=F.Game->RegisterEquipmentSource(TEXT("test.crit.heavy"),Prototype("WPN-GSW-001"),{40,0});
    if (!Heavy.Ok()||!F.StartPickup(Heavy.SourceId)||!F.Finish()||!F.Game->TrySwitchEquipment()||!F.Finish()) return false;
    TestEqual(TEXT("E/Q do not reset or consume combat critical stream"),F.Game->GetEquipmentView().NextCritDraw,Before+1);
    if (!TestTrue(TEXT("Real sword skill accepted after Q"),F.Player->TryBeginWeaponSkill())) return false;
    const auto Skill=F.Player->GetWeaponSkillAction(); F.AdvanceTo(Skill.LockAt-.001);
    TestEqual(TEXT("Skill windup also only peeks until lock succeeds"),F.Game->GetEquipmentView().NextCritDraw,Before+1); F.AdvanceTo(Skill.LockAt);
    TestTrue(TEXT("Weapon action lock uses the same run stream exactly once"),F.Player->GetWeaponSkillAction().Locked&&F.Game->GetEquipmentView().NextCritDraw==Before+2);
    return true;
}
#endif
