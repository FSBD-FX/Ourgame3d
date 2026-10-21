#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonKnightGameIntegration,"CodexDungeon.Content.StoneKnightGameIntegration",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonKnightGameIntegration::RunTest(const FString& Parameters)
{
    const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
    auto World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
    if(!TestNotNull(TEXT("Knight integration world"),World))return false;
    auto Instance=NewObject<UGameInstance>(GEngine);World->SetGameInstance(Instance);
    FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
    if(!TestTrue(TEXT("Real authoritative GameMode"),World->SetGameMode(URL))){World->DestroyWorld(false);return false;}
    auto Game=World->GetAuthGameMode<ADungeonGameMode>();
    auto Player=World->SpawnActor<ADungeonFighter>();Player->ResetFighter({0,0});
    Game->PlayerFighter=Player;Game->bWaitingForStart=false;Game->bGameOver=false;
    auto Knight=World->SpawnActor<ADungeonFighter>();Knight->ResetFighter({300,0});
    Game->Enemies.Add(Knight);
    if(!TestTrue(TEXT("Stone content config attaches real driver"),Knight->InitializeStoneKnight(1001)))
    {World->DestroyWorld(false);return false;}
    TestEqual(TEXT("Stone knight template identity"),Knight->EnemyContentId,FString(TEXT("ENM-STN-001")));
    TestEqual(TEXT("Stone knight actual HP"),Knight->Health,110.f);
    TestEqual(TEXT("Stone knight actual physical armor"),Knight->GetArmorRating(),45.f);
    Game->Tick(.1f);
    TestTrue(TEXT("Distant statue remains dormant"),Knight->GetStoneKnightDriver()->State().Phase==DungeonStoneKnight::EPhase::Dormant);
    // Actual incoming HP loss, not a fake trigger, begins the same statue's warning.
    Knight->ApplyCombatHit(14.5f,Player,0.f);
    TestTrue(TEXT("Armor45 reduces actual hit14.5 to10"),FMath::IsNearlyEqual(Knight->Health,100.f,.001f));
    TestTrue(TEXT("Actual damage wakes dormant statue"),Knight->GetStoneKnightDriver()->State().Phase==DungeonStoneKnight::EPhase::Waking);
    Game->Tick(.84f);
    TestTrue(TEXT("Warning cannot end early"),Knight->GetStoneKnightDriver()->State().Phase==DungeonStoneKnight::EPhase::Waking);
    Game->Tick(.02f);
    TestTrue(TEXT("Warning completes without resetting HP"),Knight->GetStoneKnightDriver()->State().Awakened&&FMath::IsNearlyEqual(Knight->Health,100.f,.001f));
    Game->Tick(1.8f);
    TestTrue(TEXT("Actual charge movement approaches player"),Knight->GetGroundPosition().X<300.f);
    TestTrue(TEXT("Charge hit commits real player damage"),Player->Health<100.f);
    TestTrue(TEXT("Driver HP and actor HP stay identical"),FMath::IsNearlyEqual(float(Knight->GetStoneKnightDriver()->State().HP),Knight->Health,.001f));
    Knight->ApplyCombatHit(1000.f,Player,100.f);
    TestTrue(TEXT("Kernel death commits actual actor death"),Knight->bDead);
    const int32 Rewards=Game->Pickups.Num();
    Game->OnFighterDied(Knight);Game->Tick(.1f);
    TestEqual(TEXT("Dead statue cannot duplicate pickups"),Game->Pickups.Num(),Rewards);
    World->DestroyWorld(false);return true;
}
#endif
