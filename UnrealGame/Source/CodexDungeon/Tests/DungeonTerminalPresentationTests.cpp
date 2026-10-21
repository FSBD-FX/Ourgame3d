#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonDeathPresentationAfterTerminalFreeze,
    "CodexDungeon.Content.DeathPresentationAfterTerminalFreeze",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonDeathPresentationAfterTerminalFreeze::RunTest(const FString& Parameters)
{
    const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
        .ShouldSimulatePhysics(false).SetTransactional(false);
    auto World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true,
        ERHIFeatureLevel::Num, &Settings);
    if (!TestNotNull(TEXT("Terminal presentation world"), World)) return false;
    auto Instance = NewObject<UGameInstance>(GEngine);
    World->SetGameInstance(Instance);
    FURL URL;
    URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
    if (!TestTrue(TEXT("Actual authoritative game mode"), World->SetGameMode(URL)))
    { World->DestroyWorld(false); return false; }
    auto Game = World->GetAuthGameMode<ADungeonGameMode>();
    auto Player = World->SpawnActor<ADungeonFighter>();
    auto Knight = World->SpawnActor<ADungeonFighter>();
    if (!TestNotNull(TEXT("Terminal player"), Player) || !TestNotNull(TEXT("Terminal knight"), Knight))
    { World->DestroyWorld(false); return false; }
    Player->ResetFighter({0,0});
    Game->PlayerFighter = Player;
    Game->bWaitingForStart = false; Game->bGameOver = false;
    Knight->ResetFighter({300,0});
    Game->Enemies.Add(Knight);
    if (!TestTrue(TEXT("Real knight driver attaches"), Knight->InitializeStoneKnight(9011)))
    { World->DestroyWorld(false); return false; }
    TestTrue(TEXT("Real focus spending before terminal state"), Player->SpendFocus(50.f));
    Player->StartJump();
    Game->Tick(.1f);
    TestTrue(TEXT("Real ballistic motion supplies an airborne death visual"), Player->JumpHeight > 0.f);
    // Production damage/death paths create both death clips and claim the knight reward.
    Knight->ApplyCombatHit(1000.f, Player, 0.f);
    Player->ApplyCombatHit(1000.f, Knight, 0.f);
    if (!TestTrue(TEXT("Player death actually enters terminal game state"), Game->bGameOver && Player->bDead && Knight->bDead))
    { World->DestroyWorld(false); return false; }
    const double Clock = Game->GetSimulationTime();
    const auto KnightBefore = Knight->GetStoneKnightDriver()->Capture();
    const float PlayerAnimation = Player->AnimationTime, KnightAnimation = Knight->AnimationTime;
    const float Height = Player->JumpHeight, Focus = Player->Focus;
    const auto Ground = Player->GetGroundPosition();
    const int32 Rewards = Game->Pickups.Num();
    Game->Tick(.25f); // Real production Tick after terminal; no manual animation mutation.
    TestTrue(TEXT("Death presentation advances player clip after terminal freeze"), Player->AnimationTime > PlayerAnimation+.24f);
    TestTrue(TEXT("Death presentation advances knight clip after terminal freeze"), Knight->AnimationTime > KnightAnimation+.24f);
    TestTrue(TEXT("Airborne dead presentation settles without moving its ground center"),
        Player->JumpHeight >= 0.f && Player->JumpHeight < Height && Player->GetGroundPosition().Equals(Ground));
    TestTrue(TEXT("Authoritative run simulation time stays exactly frozen"), Game->GetSimulationTime() == Clock);
    const auto& KnightAfter = Knight->GetStoneKnightDriver()->State();
    TestTrue(TEXT("Driver clock, event cursor, attacks and cooldowns stay exactly frozen"),
        KnightAfter.Time == KnightBefore.Time && KnightAfter.NextEventId == KnightBefore.NextEventId
        && KnightAfter.NextAttackId == KnightBefore.NextAttackId && KnightAfter.ChargeReadyAt == KnightBefore.ChargeReadyAt
        && KnightAfter.ShieldReadyAt == KnightBefore.ShieldReadyAt && KnightAfter.Phase == KnightBefore.Phase);
    TestEqual(TEXT("Terminal presentation cannot regenerate focus"), Player->Focus, Focus);
    TestEqual(TEXT("Terminal presentation cannot change player HP"), Player->Health, 0.f);
    TestTrue(TEXT("Terminal presentation cannot change knight HP or reward claim"),
        KnightAfter.HP == KnightBefore.HP && KnightAfter.RewardClaimed == KnightBefore.RewardClaimed);
    TestEqual(TEXT("Terminal presentation cannot duplicate drops"), Game->Pickups.Num(), Rewards);
    World->DestroyWorld(false);
    return true;
}
#endif
