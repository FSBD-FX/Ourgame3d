#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneFeedbackGameIntegration,
    "CodexDungeon.Content.StoneFeedbackGameIntegration",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonStoneFeedbackGameIntegration::RunTest(const FString& Parameters)
{
    using DungeonStoneKnight::EEventKind;
    const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
        .ShouldSimulatePhysics(false).SetTransactional(false);
    auto World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true,
        ERHIFeatureLevel::Num, &Settings);
    if (!TestNotNull(TEXT("Stone feedback integration world"), World)) return false;
    auto Instance = NewObject<UGameInstance>(GEngine);
    World->SetGameInstance(Instance);
    FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
    if (!TestTrue(TEXT("Actual authoritative game mode"), World->SetGameMode(URL)))
    { World->DestroyWorld(false); return false; }
    auto Game = World->GetAuthGameMode<ADungeonGameMode>();
    auto Player = World->SpawnActor<ADungeonFighter>();
    auto Knight = World->SpawnActor<ADungeonFighter>();
    if (!TestNotNull(TEXT("Feedback player"), Player) || !TestNotNull(TEXT("Feedback knight"), Knight))
    { World->DestroyWorld(false); return false; }
    Player->ResetFighter({0,0}); Knight->ResetFighter({300,0});
    Game->PlayerFighter = Player; Game->Enemies.Add(Knight);
    Game->bWaitingForStart = false; Game->bGameOver = false;
    if (!TestTrue(TEXT("Real stone knight attaches"), Knight->InitializeStoneKnight(11001)))
    { World->DestroyWorld(false); return false; }
    const auto HasKind = [Knight](EEventKind Kind)
    {
        for (const auto& R : Knight->GetStoneFeedback().Entries()) if (R.Event.Kind == Kind) return true;
        return false;
    };
    TestTrue(TEXT("Initial statue has no synthetic presentation event"), Knight->GetStoneFeedback().Entries().empty());
    Game->Tick(.1f);
    const double BeforeDamage = Game->GetSimulationTime();
    Knight->ApplyCombatHit(14.5f, Player, 0.f);
    TestTrue(TEXT("Actual resolved hit puts Damaged in the actor's one journal"), HasKind(EEventKind::Damaged));
    TestTrue(TEXT("Actual positive HP loss puts WakeStarted in the same journal"), HasKind(EEventKind::WakeStarted));
    TestTrue(TEXT("Recording damage neither advances time nor applies damage twice"),
        Game->GetSimulationTime() == BeforeDamage && Knight->GetStoneKnightDriver()->State().Time == BeforeDamage
        && FMath::IsNearlyEqual(Knight->Health, 100.f, .001f));
    Game->Tick(.86f); // .85 warning completes; real kernel automatically accepts the charge.
    Game->Tick(.45f); // Cross the charge's real .45 lock, still before its active charge.
    TestTrue(TEXT("GameMode StepTo contributes WakeCompleted and AimLocked"),
        HasKind(EEventKind::WakeCompleted) && HasKind(EEventKind::AimLocked));
    const double BeforeBreak = Game->GetSimulationTime();
    Knight->ApplyCombatHit(1.45f, Player, 60.f);
    TestTrue(TEXT("Actual poise threshold puts PoiseBroken in the same journal"), HasKind(EEventKind::PoiseBroken));
    TestTrue(TEXT("Feedback does not add HP loss, time or player damage"),
        FMath::IsNearlyEqual(Knight->Health, 99.f, .001f) && Player->Health == 100.f
        && Game->GetSimulationTime() == BeforeBreak && Knight->GetStoneKnightDriver()->State().Time == BeforeBreak);
    Knight->ApplyCombatHit(1000.f, Player, 0.f);
    TestTrue(TEXT("Real kernel death puts Died in the same journal"), HasKind(EEventKind::Died));
    const auto Count = Knight->GetStoneFeedback().Entries().size();
    const auto Last = Knight->GetStoneFeedback().LastEventId();
    const int32 Rewards = Game->Pickups.Num();
    const auto Frozen = Knight->GetStoneKnightDriver()->Capture();
    std::vector<DungeonStoneKnight::FEvent> AlreadyObserved;
    uint64 Previous = 0;
    bool Ordered = true;
    for (const auto& R : Knight->GetStoneFeedback().Entries())
    {
        Ordered &= R.Event.EntityId == 11001 && R.Event.EventId > Previous;
        Previous = R.Event.EventId;
        AlreadyObserved.push_back(R.Event);
    }
    TestTrue(TEXT("One real journal contains increasing IDs from this same entity"), Ordered && Count > 0);
    // The production getter stays const; replay the actual observed facts into a
    // copy to exercise journal idempotence without adding a mutable HUD/test seam.
    auto PresentationCopy = Knight->GetStoneFeedback();
    TestTrue(TEXT("Reobserving actual batch records does not duplicate presentation"),
        PresentationCopy.Observe(AlreadyObserved, Frozen.Position)
        && PresentationCopy.Entries().size() == Count && PresentationCopy.LastEventId() == Last);
    Game->OnFighterDied(Knight); Knight->ApplyCombatHit(1.f, Player, 0.f);
    TestTrue(TEXT("Repeated actual death requests cannot append duplicate actor feedback"),
        Knight->GetStoneFeedback().Entries().size() == Count && Knight->GetStoneFeedback().LastEventId() == Last);
    TestTrue(TEXT("Reading/replaying presentation cannot mutate authoritative knight facts"),
        Knight->GetStoneKnightDriver()->State().Time == Frozen.Time
        && Knight->GetStoneKnightDriver()->State().NextEventId == Frozen.NextEventId
        && Knight->GetStoneKnightDriver()->State().HP == Frozen.HP && Knight->Health == 0.f
        && Knight->GetStoneKnightDriver()->State().RewardClaimed == Frozen.RewardClaimed
        && Game->GetSimulationTime() == BeforeBreak);
    TestEqual(TEXT("Presentation never duplicates actual rewards"), Game->Pickups.Num(), Rewards);
    World->DestroyWorld(false);
    return true;
}
#endif
