#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/EngineBaseTypes.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"

namespace
{
// Local UE 5.5 source contract:
// World.cpp UWorld::SetGameMode -> GameInstance::CreateGameModeForURL.
// The explicit game URL loads this native class and stores it in AuthorityGameMode;
// spawning an unrelated GameMode actor would not provide GetAuthGameMode().
struct FDamageBatchWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    FString SetupError;

    ~FDamageBatchWorld()
    {
        if (World) World->DestroyWorld(false);
    }

    bool Create()
    {
        if (!GEngine)
        {
            SetupError = TEXT("Damage batch setup: GEngine is unavailable.");
            return false;
        }
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false)
            .CreatePhysicsScene(false).RequiresHitProxies(false).CreateNavigation(false)
            .CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr,
            true, ERHIFeatureLevel::Num, &Settings);
        if (!World)
        {
            SetupError = TEXT("Damage batch setup: CreateWorld failed.");
            return false;
        }
        UGameInstance* Instance = NewObject<UGameInstance>(GEngine);
        World->SetGameInstance(Instance);
        FURL URL;
        URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL))
        {
            SetupError = TEXT("Damage batch setup: SetGameMode failed for the explicit native URL.");
            return false;
        }
        Game = World->GetAuthGameMode<ADungeonGameMode>();
        if (!Game)
        {
            SetupError = TEXT("Damage batch setup: real AuthorityGameMode is not ADungeonGameMode.");
            return false;
        }
        Player = World->SpawnActor<ADungeonFighter>();
        if (!Player)
        {
            SetupError = TEXT("Damage batch setup: player spawn failed.");
            return false;
        }
        Player->SetActorTickEnabled(false);
        Player->WeaponId = TEXT("WPN-SWD-001");
        Player->ResetFighter(FVector2D::ZeroVector);
        Game->PlayerFighter = Player;
        Game->bWaitingForStart = false;
        Game->bGameOver = false;
        return true;
    }

    ADungeonFighter* AddEnemy(FVector2D Position)
    {
        auto Enemy = World->SpawnActor<ADungeonFighter>();
        if (!Enemy) return nullptr;
        Enemy->SetActorTickEnabled(false);
        Enemy->bEnemy = true;
        Enemy->bAIEnabled = false;
        Enemy->MaxHealth = 100.f;
        Enemy->ResetFighter(Position);
        Game->Enemies.Add(Enemy);
        return Enemy;
    }

    bool StartThreeSimultaneousEnemyAttacks()
    {
        for (const auto Position : {FVector2D(80, 0), FVector2D(80, 2), FVector2D(80, -2)})
        {
            auto Enemy = AddEnemy(Position);
            if (!Enemy)
            {
                SetupError = TEXT("Damage batch setup: enemy spawn failed.");
                return false;
            }
            Enemy->BeginAttack(); // Existing enemy primary: .46s windup, 13 damage.
            if (Enemy->AttackTime <= 0.f)
            {
                SetupError = TEXT("Damage batch setup: enemy attack was not accepted.");
                return false;
            }
        }
        return true;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonAllDueDamageBatchTest,
    "CodexDungeon.Content.DamageBatch.AllDueHitsResolve",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonAllDueDamageBatchTest::RunTest(const FString& Parameters)
{
    {
        FDamageBatchWorld CountControl;
        if (!CountControl.Create() || !CountControl.StartThreeSimultaneousEnemyAttacks())
        {
            AddError(CountControl.SetupError);
            return false;
        }
        CountControl.Game->Tick(.47f);
        TestEqual(TEXT("The nonlethal control counts all three 13 damage hits, not merely two lethal hits"),
            CountControl.Player->Health, 61.f);
    }
    FDamageBatchWorld Fixture;
    if (!Fixture.Create() || !Fixture.StartThreeSimultaneousEnemyAttacks())
    {
        AddError(Fixture.SetupError);
        return false;
    }
    TestTrue(TEXT("Fixture uses the world's actual authority game mode"),
        Fixture.World->GetAuthGameMode<ADungeonGameMode>() == Fixture.Game);
    Fixture.Player->Health = 20.f;
    // Execute the production all-actor motion -> actions -> damage path.
    // Do not replace this with Player::Tick or manual ResolveAttack calls.
    Fixture.Game->Tick(.47f);
    TestEqual(TEXT("Three already-due 13 damage hits exhaust 20 HP in the same batch"),
        Fixture.Player->Health, 0.f);
    TestTrue(TEXT("New iframes from the first hit cannot suppress the other accepted due hits"),
        Fixture.Player->bDead);
    TestTrue(TEXT("The real authority game mode receives the resulting player death"),
        Fixture.Game->bGameOver);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonOldIframesDamageBatchTest,
    "CodexDungeon.Content.DamageBatch.PreexistingIframesStillBlock",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonOldIframesDamageBatchTest::RunTest(const FString& Parameters)
{
    FDamageBatchWorld Fixture;
    if (!Fixture.Create() || !Fixture.StartThreeSimultaneousEnemyAttacks())
    {
        AddError(Fixture.SetupError);
        return false;
    }
    Fixture.Player->ApplyCombatHit(1.f, nullptr, 0.f);
    TestEqual(TEXT("A real initial hit established the old iframe interval"),
        Fixture.Player->Health, 99.f);
    Fixture.Player->Health = 20.f; // Keep that interval; set only the public QA HP fixture.
    Fixture.Player->ApplyCombatHit(1.f, nullptr, 0.f);
    TestEqual(TEXT("The fixture really has old iframes before advancing the batch"),
        Fixture.Player->Health, 20.f);
    Fixture.Game->Tick(.47f); // .65s old iframes still cover the .46s enemy windows.
    TestEqual(TEXT("Preexisting iframes reject all three due hits"), Fixture.Player->Health, 20.f);
    TestFalse(TEXT("Rejecting hits under old iframes leaves the player alive"), Fixture.Player->bDead);
    TestFalse(TEXT("Old-iframe rejection does not end the run"), Fixture.Game->bGameOver);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonLowFpsAirDamageWindowTest,
    "CodexDungeon.Content.DamageBatch.LowFpsAirWindowUsesMotionTime",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonLowFpsAirDamageWindowTest::RunTest(const FString& Parameters)
{
    {
        FDamageBatchWorld Fixture;
        if (!Fixture.Create())
        {
            AddError(Fixture.SetupError);
            return false;
        }
        auto Target = Fixture.AddEnemy({80, 0});
        if (!TestNotNull(TEXT("Air-window target spawn"), Target)) return false;
        Fixture.Player->StartJump();
        Fixture.Player->BeginAttack(); // Sword active [.17,.29): ballistic height is >65cm.
        TestTrue(TEXT("Air primary was accepted before the slow render frame"),
            Fixture.Player->AttackTime > .59f);
        Fixture.Game->Tick(.60f); // One slow render frame crosses the full attack window.
        TestTrue(TEXT("The jump really advanced along the production motion path"),
            Fixture.Player->JumpHeight > 50.f && Fixture.Player->JumpHeight < 58.f);
        TestEqual(TEXT("A high airborne sword window cannot use takeoff/late-frame ground geometry"),
            Target->Health, 100.f);
    }
    {
        FDamageBatchWorld Fixture;
        if (!Fixture.Create())
        {
            AddError(Fixture.SetupError);
            return false;
        }
        auto Target = Fixture.AddEnemy({80, 0});
        if (!TestNotNull(TEXT("Ground positive-control target spawn"), Target)) return false;
        Fixture.Player->BeginAttack();
        Fixture.Game->Tick(.60f);
        TestEqual(TEXT("Ground control proves the same GameMode.Tick path emits and applies the window"),
            Target->Health, 74.f);
    }
    return true;
}

#endif

