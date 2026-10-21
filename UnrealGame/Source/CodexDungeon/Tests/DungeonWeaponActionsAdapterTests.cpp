#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"

namespace
{
struct FWeaponAdapterWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    ~FWeaponAdapterWorld() { if (World) World->DestroyWorld(false); }
    bool Create()
    {
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true,
            ERHIFeatureLevel::Num, &Settings);
        if (!World) return false;
        auto Instance = NewObject<UGameInstance>(GEngine);
        World->SetGameInstance(Instance);
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game = World->GetAuthGameMode<ADungeonGameMode>();
        Player = World->SpawnActor<ADungeonFighter>();
        if (!Game || !Player) return false;
        Player->WeaponId = TEXT("WPN-SWD-001");
        Player->ResetFighter({0,0});
        Game->PlayerFighter = Player; Game->bWaitingForStart = false; Game->bGameOver = false;
        return true;
    }
    ADungeonFighter* AddKnight(FVector2D Position, uint64 Id = 12001)
    {
        auto Enemy = World->SpawnActor<ADungeonFighter>();
        if (!Enemy) return nullptr;
        Enemy->ResetFighter(Position); Game->Enemies.Add(Enemy);
        return Enemy->InitializeStoneKnight(Id) ? Enemy : nullptr;
    }
    ADungeonFighter* AddPrototype(FVector2D Position)
    {
        auto Enemy = World->SpawnActor<ADungeonFighter>();
        if (!Enemy) return nullptr;
        Enemy->bEnemy = true; Enemy->bAIEnabled = false; Enemy->MaxHealth = 100.f;
        Enemy->ResetFighter(Position); Game->Enemies.Add(Enemy);
        return Enemy;
    }
    bool AddWall()
    {
        auto Wall = World->SpawnActor<AActor>();
        if (!Wall) return false;
        auto Box = NewObject<UBoxComponent>(Wall);
        Wall->SetRootComponent(Box); Box->SetBoxExtent({5,80,50});
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly); Box->SetCollisionObjectType(ECC_WorldStatic);
        Box->SetCollisionResponseToAllChannels(ECR_Block); Box->RegisterComponentWithWorld(World);
        Wall->SetActorLocation({50,0,0});
        return true;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSwordSecondaryRealWindowAndBlockedStep,
    "CodexDungeon.Content.WeaponActionsAdapter.SwordSecondaryRealWindowAndBlockedStep",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonSwordSecondaryRealWindowAndBlockedStep::RunTest(const FString& Parameters)
{
    {
        FWeaponAdapterWorld F;
        if (!TestTrue(TEXT("Authoritative sword skill world"), F.Create())) return false;
        auto Target = F.AddKnight({170,0});
        if (!TestNotNull(TEXT("Real armor45 stone target"), Target)) return false;
        F.Player->SpendFocus(50.f);
        TestTrue(TEXT("Fresh ground SWD secondary is accepted"), F.Player->TryBeginWeaponSkill());
        const auto Start = F.Player->GetWeaponSkillAction();
        TestTrue(TEXT("Skill owns its .20/.10/.38 full timeline"), Start.Active
            && Start.Type == DungeonWeaponActions::EAction::Skill && FMath::IsNearlyEqual(Start.LockAt,.08,1.e-9)
            && FMath::IsNearlyEqual(Start.ActiveAt,.20,1.e-9) && FMath::IsNearlyEqual(Start.ActiveEnd,.30,1.e-9)
            && FMath::IsNearlyEqual(Start.End,.68,1.e-9));
        F.Game->Tick(.079f);
        TestFalse(TEXT("Skill remains unlocked before .08"), F.Player->GetWeaponSkillAction().Locked);
        TestEqual(TEXT("No pre-lock skill cooldown"), F.Player->GetWeaponSkillCooldownRemaining(), 0.0);
        F.Game->Tick(.002f);
        TestTrue(TEXT("Real .08 lock freezes skill and starts deadline4.08"), F.Player->GetWeaponSkillAction().Locked
            && FMath::IsNearlyEqual(F.Game->GetSimulationTime()+F.Player->GetWeaponSkillCooldownRemaining(),4.08,1.e-6));
        F.Game->Tick(.12f);
        TestTrue(TEXT("Actual .20 forward step moves only once by30cm"), FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,30.0,.001));
        TestTrue(TEXT("Skill uses32 physical damage through stone armor45"), FMath::IsNearlyEqual(Target->Health,110.f-32.f/1.45f,.001f));
        TestEqual(TEXT("Skill uses its own presentation name"), F.Player->AnimationName, FString(TEXT("secondary")));
        const float HP = Target->Health;
        F.Game->Tick(.05f);
        TestEqual(TEXT("The same target is not damaged twice within one continuous skill window"), Target->Health, HP);
        TestTrue(TEXT("Forward step is not replayed by the active-window scan"), FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,30.0,.001));
        TestEqual(TEXT("Zero-cost SWD skill does not alter the authoritative fighter focus"), F.Player->Focus, 50.f);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        auto Target = F.AddPrototype({250,0});
        if (!TestNotNull(TEXT("Late-entry target"), Target)) return false;
        TestTrue(TEXT("Late-entry skill starts"), F.Player->TryBeginWeaponSkill());
        F.Game->Tick(.21f);
        TestEqual(TEXT("Target initially outside the active window stays unharmed"), Target->Health,100.f);
        Target->SetActorLocation({160,0,0});
        F.Game->Tick(.02f);
        TestEqual(TEXT("Target entering during [.20,.30) receives the one real32 hit"), Target->Health,68.f);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        auto Target = F.AddKnight({170,39});
        if (!TestNotNull(TEXT("Forward-ellipse corner target"),Target)) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.31f);
        TestEqual(TEXT("Bounding-rectangle corner outside145x40 forward ellipse cannot be hit"),Target->Health,110.f);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        auto Blocker = F.AddKnight({50,0});
        auto Far = F.AddPrototype({170,0});
        if (!TestNotNull(TEXT("Real24x20 blocking stone"),Blocker) || !TestNotNull(TEXT("Beyond actual step origin target"),Far)) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.21f);
        TestTrue(TEXT("Player18+stone24 body sweep truncates30cm step to8cm"), FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,8.0,.001));
        TestEqual(TEXT("Blocked step does not query from fictitious30cm origin"),Far->Health,100.f);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create() || !TestTrue(TEXT("Registered real blocking wall"),F.AddWall())) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.21f);
        TestTrue(TEXT("Real world wall front45 minus player half18 stops step at27"), FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,27.0,.01));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSkillRespectsFullRecoveryAndClearsOnlyAcceptedChain,
    "CodexDungeon.Content.WeaponActionsAdapter.SkillRespectsFullRecoveryAndClearsOnlyAcceptedChain",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonSkillRespectsFullRecoveryAndClearsOnlyAcceptedChain::RunTest(const FString& Parameters)
{
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        F.Player->BeginAttack(); F.Game->Tick(.5f);
        F.Player->BeginAttack(); // Legal final .12s primary buffer.
        TestTrue(TEXT("Fixture really holds the accepted primary input buffer"), F.Player->GetMeleeCombatState().PendingPrimary);
        TestFalse(TEXT("Skill cannot cancel the primary full recovery"), F.Player->TryBeginWeaponSkill());
        TestTrue(TEXT("Rejected skill keeps the original pending primary"), F.Player->GetMeleeCombatState().PendingPrimary);
        F.Game->Tick(.101f);
        TestEqual(TEXT("Untouched buffer starts second stage after complete first recovery"), F.Player->ComboStage,2);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        F.Player->BeginAttack(); F.Game->Tick(.60f);
        TestTrue(TEXT("Completed first primary really has a live second-stage chain"),
            F.Player->GetMeleeCombatState().ComboReady && F.Player->GetMeleeCombatState().NextComboStage == 1);
        TestFalse(TEXT("Held skill is not a fresh press"), F.Player->TryBeginWeaponSkill(false));
        TestTrue(TEXT("Denied held request keeps the current chain"), F.Player->GetMeleeCombatState().ComboReady);
        TestTrue(TEXT("Skill may start only after the full .60 primary"),F.Player->TryBeginWeaponSkill());
        TestTrue(TEXT("Accepted skill immediately clears ground chain and unexecuted buffer"),
            !F.Player->GetMeleeCombatState().ComboReady && F.Player->GetMeleeCombatState().NextComboStage == 0
            && !F.Player->GetMeleeCombatState().PendingPrimary);
        const uint64 SkillId = F.Player->GetWeaponSkillAction().ActionId;
        F.Game->Tick(.1f);
        F.Player->bHasAxe = true;
        F.Player->StartJump(); F.Player->SwitchWeapon(); F.Player->BeginAttack();
        TestEqual(TEXT("Skill does not allow jump cancel"),F.Player->GetVerticalVelocity(),0.f);
        TestEqual(TEXT("Skill does not allow switch cancel"),F.Player->WeaponId,FString(TEXT("WPN-SWD-001")));
        TestFalse(TEXT("Skill does not allow armor overlap"),F.Player->BeginArmorChange(TEXT("ARM-LGT-001")));
        TestTrue(TEXT("Other action requests do not replace the accepted skill"),
            F.Player->GetWeaponSkillAction().Active && F.Player->GetWeaponSkillAction().ActionId == SkillId
            && !F.Player->GetMeleeCombatState().Action.Active);
        F.Game->Tick(.579f);
        TestTrue(TEXT("Skill is still active just before its complete .68 cycle"),F.Player->GetWeaponSkillAction().Active);
        F.Game->Tick(.002f);
        TestFalse(TEXT("Skill completes only after full .68 cycle"),F.Player->GetWeaponSkillAction().Active);
        TestFalse(TEXT("Skill's original cooldown still denies a second skill"),F.Player->TryBeginWeaponSkill());
        F.Player->BeginAttack();
        TestEqual(TEXT("Primary after completed skill starts stage1"),F.Player->ComboStage,1);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.1f);
        const uint64 SkillId = F.Player->GetWeaponSkillAction().ActionId;
        F.Player->ApplyCombatHit(1.f,nullptr,0.f);
        TestTrue(TEXT("Ordinary positive HP loss without poise break preserves skill"),
            F.Player->GetWeaponSkillAction().Active && F.Player->GetWeaponSkillAction().ActionId == SkillId);
    }
    {
        FWeaponAdapterWorld F;
        if (!F.Create()) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.1f);
        F.Player->ApplyCombatHit(1.f,nullptr,30.f);
        TestFalse(TEXT("True threshold break interrupts skill"),F.Player->GetWeaponSkillAction().Active);
        TestTrue(TEXT("True break never resets the already locked4.08 deadline"),
            FMath::IsNearlyEqual(F.Game->GetSimulationTime()+F.Player->GetWeaponSkillCooldownRemaining(),4.08,1.e-6));
        F.Game->Tick(.3f);
        TestTrue(TEXT("Interrupted pre-emission skill never performs its future forward step"),F.Player->GetGroundPosition().IsNearlyZero());
    }
    return true;
}
#endif
