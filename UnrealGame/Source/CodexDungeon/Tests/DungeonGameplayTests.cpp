#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonCombatRules.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonDepthHitTest, "CodexDungeon.Combat.DepthFacingAndHeight",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonDepthHitTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("Same depth and forward range hit"), ADungeonFighter::CanHitTarget(FVector2D(90, 0), 1, 120, 45, 0, 0));
    TestTrue(TEXT("Left facing can hit left"), ADungeonFighter::CanHitTarget(FVector2D(-90, 0), -1, 120, 45, 0, 0));
    TestFalse(TEXT("Behind attacker misses"), ADungeonFighter::CanHitTarget(FVector2D(-1, 0), 1, 120, 45, 0, 0));
    TestFalse(TEXT("Horizontal overlap beyond ground depth misses"), ADungeonFighter::CanHitTarget(FVector2D(90, 46), 1, 120, 45, 0, 0));
    TestFalse(TEXT("High jumping target dodges ground attack"), ADungeonFighter::CanHitTarget(FVector2D(90, 0), 1, 120, 45, 0, 100));
    TestTrue(TEXT("Matching airborne heights hit"), ADungeonFighter::CanHitTarget(FVector2D(90, 0), 1, 120, 45, 100, 100));
    TestEqual(TEXT("Potion cannot exceed max health"), DungeonCombatRules::RestoreHealth(97, 100, 30), 100.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonPickupTest, "CodexDungeon.Gameplay.PickupCapAndSingleReward",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonPickupTest::RunTest(const FString& Parameters)
{
    const UWorld::InitializationValues WorldSettings = UWorld::InitializationValues()
        .AllowAudioPlayback(false).CreatePhysicsScene(false).RequiresHitProxies(false)
        .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr,
        true, ERHIFeatureLevel::Num, &WorldSettings);
    if (!TestNotNull(TEXT("Isolated gameplay world"), World))
    {
        return false;
    }
    ADungeonGameMode* GameMode = World->SpawnActor<ADungeonGameMode>();
    ADungeonFighter* Player = World->SpawnActor<ADungeonFighter>();
    ADungeonFighter* Enemy = World->SpawnActor<ADungeonFighter>();
    if (!TestNotNull(TEXT("Game mode"), GameMode) || !TestNotNull(TEXT("Player"), Player) || !TestNotNull(TEXT("Enemy"), Enemy))
    {
        World->DestroyWorld(false);
        return false;
    }
    GameMode->PlayerFighter = Player;
    Player->ResetFighter(FVector2D::ZeroVector);
    Player->Health = 97.f;
    FDungeonPickup Potion;
    Potion.Kind = TEXT("potion");
    GameMode->Pickups.Add(Potion);
    GameMode->TryInteract();
    TestEqual(TEXT("Live pickup caps health at maximum"), Player->Health, 100.f);
    TestTrue(TEXT("Used potion is consumed"), GameMode->Pickups[0].bConsumed);
    Player->Health = 50.f;
    GameMode->TryInteract();
    TestEqual(TEXT("Consumed potion cannot heal twice"), Player->Health, 50.f);

    GameMode->Pickups.Reset();
    FDungeonPickup Coin;
    Coin.Kind = TEXT("coin");
    GameMode->Pickups.Add(Coin);
    GameMode->TryInteract();
    GameMode->TryInteract();
    TestEqual(TEXT("Coin rewards only once"), Player->Coins, 5);

    Enemy->bEnemy = true;
    Enemy->ResetFighter(FVector2D(80,0));
    Enemy->ApplyCombatHit(13.f,Player);
    Enemy->ApplyCombatHit(13.f,Player);
    TestEqual(TEXT("Invulnerability window prevents repeated immediate damage"),Enemy->Health,87.f);
    Enemy->bDead = true;
    GameMode->Enemies.Add(Enemy);
    GameMode->OnFighterDied(Enemy);
    const int32 DropCount = GameMode->Pickups.Num();
    GameMode->OnFighterDied(Enemy);
    TestEqual(TEXT("Repeated death notification cannot duplicate drops"), GameMode->Pickups.Num(), DropCount);
    TestTrue(TEXT("Last enemy death clears room"), GameMode->bRoomCleared);
    World->DestroyWorld(false);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonMeleeChainTest, "CodexDungeon.Content.MeleeChainTiming",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonMeleeChainTest::RunTest(const FString& Parameters)
{
    const UWorld::InitializationValues Settings = UWorld::InitializationValues()
        .AllowAudioPlayback(false).CreatePhysicsScene(false).RequiresHitProxies(false)
        .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr,
        true, ERHIFeatureLevel::Num, &Settings);
    if (!TestNotNull(TEXT("Content test world"), World)) return false;
    ADungeonFighter* Player = World->SpawnActor<ADungeonFighter>();
    if (!TestNotNull(TEXT("Content test fighter"), Player))
    {
        World->DestroyWorld(false);
        return false;
    }
    Player->ResetFighter(FVector2D::ZeroVector);
    Player->BeginAttack();
    TestTrue(TEXT("Sword first segment retains full .60 second action"), FMath::IsNearlyEqual(Player->AttackTime, .60f, .0001f));
    Player->StartJump();
    Player->Tick(.10f);
    TestEqual(TEXT("Ground attack cannot jump away its recovery"), Player->JumpHeight, 0.f);
    Player->Tick(.50f);
    Player->BeginAttack();
    TestTrue(TEXT("Sword second segment lasts .54 seconds"), FMath::IsNearlyEqual(Player->AttackTime, .54f, .0001f));
    Player->Tick(.54f);
    Player->BeginAttack();
    TestTrue(TEXT("Sword third segment lasts .66 seconds"), FMath::IsNearlyEqual(Player->AttackTime, .66f, .0001f));
    World->DestroyWorld(false);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonSpearTargetTest, "CodexDungeon.Content.SpearNearestAndDedup",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonSpearTargetTest::RunTest(const FString& Parameters)
{
    const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false)
        .CreatePhysicsScene(false).RequiresHitProxies(false).CreateNavigation(false)
        .CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
    if (!TestNotNull(TEXT("Spear test world"),World)) return false;
    auto Game=World->SpawnActor<ADungeonGameMode>();
    auto Player=World->SpawnActor<ADungeonFighter>();
    auto Near=World->SpawnActor<ADungeonFighter>();
    auto Far=World->SpawnActor<ADungeonFighter>();
    Game->PlayerFighter=Player; Game->Enemies={Near,Far};
    Near->bEnemy=Far->bEnemy=true; Near->bAIEnabled=Far->bAIEnabled=false;
    Near->ResetFighter({80,0}); Far->ResetFighter({180,0});
    Player->WeaponId=TEXT("WPN-SPR-001"); Player->ResetFighter({0,0});
    Player->BeginAttack(); Player->Tick(.12f);
    Game->ResolveAttack(Player);
    TestEqual(TEXT("Nearest target receives spear damage"),Near->Health,79.f);
    TestEqual(TEXT("Spear does not pierce a second target"),Far->Health,100.f);
    Game->ResolveAttack(Player);
    TestEqual(TEXT("Same active window cannot damage nearest target twice"),Near->Health,79.f);
    Near->MaxHealth=21.f; Near->ResetFighter({80,0}); Far->ResetFighter({180,0});
    Player->ResetFighter({0,0}); Player->BeginAttack(); Player->Tick(.12f);
    Game->ResolveAttack(Player); Game->ResolveAttack(Player);
    TestTrue(TEXT("Nearest target can die from the spear"),Near->bDead);
    TestEqual(TEXT("Killing nearest target cannot admit a second target in the same attack"),Far->Health,100.f);
    World->DestroyWorld(false);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonActionInterruptionTest, "CodexDungeon.Content.HitAndPickupCannotSkipRecovery",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonActionInterruptionTest::RunTest(const FString& Parameters)
{
    const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(false)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    UWorld* World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
    if (!TestNotNull(TEXT("Interruption test world"),World)) return false;
    auto Game=World->SpawnActor<ADungeonGameMode>();
    auto Player=World->SpawnActor<ADungeonFighter>();
    Game->PlayerFighter=Player; Player->ResetFighter({0,0});
    Player->BeginAttack();
    Player->ApplyCombatHit(1.f,nullptr);
    TestEqual(TEXT("A normal hit loses health"),Player->Health,99.f);
    TestTrue(TEXT("A nonbreaking hit preserves full attack action"),Player->AttackTime>.59f);
    FDungeonPickup Axe; Axe.Kind=TEXT("axe"); Game->Pickups.Add(Axe);
    Game->TryInteract();
    TestFalse(TEXT("Active primary cannot consume weapon pickup"),Game->Pickups[0].bConsumed);
    TestEqual(TEXT("Active primary retains its weapon"),Player->WeaponId,FString(TEXT("sword")));
    World->DestroyWorld(false);
    return true;
}

#endif
