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
struct FArmorAdmissionWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    ~FArmorAdmissionWorld() { if (World) World->DestroyWorld(false); }

    bool Create()
    {
        if (!GEngine) return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(false)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if (!World) return false;
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();
        if (!Game) return false;
        Player=World->SpawnActor<ADungeonFighter>();
        if (!Player) return false;
        Player->SetActorTickEnabled(false); Player->WeaponId=TEXT("WPN-SWD-001");
        Player->ResetFighter({0,0}); Game->PlayerFighter=Player;
        Game->bWaitingForStart=false; Game->bGameOver=false;
        return true;
    }

    ADungeonFighter* AddPrototypeTarget()
    {
        auto Target=World->SpawnActor<ADungeonFighter>();
        if (!Target) return nullptr;
        Target->SetActorTickEnabled(false); Target->bEnemy=true; Target->bAIEnabled=false;
        Target->MaxHealth=100.f; Target->ResetFighter({80,0}); Game->Enemies.Add(Target);
        return Target;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FArmorAdmissionExpiredIframeTest,
    "CodexDungeon.Content.ArmorAdmission.ExpiredIframesDoNotConsumeReceipt",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FArmorAdmissionExpiredIframeTest::RunTest(const FString& Parameters)
{
    {
        FArmorAdmissionWorld Control;
        if (!TestTrue(TEXT("Positive control uses actual authority game mode"),Control.Create())) return false;
        auto Target=Control.AddPrototypeTarget(); if (!TestNotNull(TEXT("Control target"),Target)) return false;
        Control.Player->BeginAttack(); Control.Game->Tick(.30f);
        TestEqual(TEXT("Same production geometry and primary route cause one26 damage hit"),Target->Health,74.f);
    }
    FArmorAdmissionWorld F;
    if (!TestTrue(TEXT("Review world uses actual authority game mode"),F.Create())) return false;
    auto Target=F.AddPrototypeTarget(); if (!TestNotNull(TEXT("Iframe target"),Target)) return false;
    Target->ApplyCombatHit(1.f,nullptr,0.f); // Real old enemy interval [0,.18); primary window [.17,.29).
    TestFalse(TEXT("Old invulnerability is established by actual damage"),Target->CanReceiveDirectHit());
    TestEqual(TEXT("Setup costs exactly one HP"),Target->Health,99.f);
    F.Player->BeginAttack(); F.Game->Tick(.30f);
    TestEqual(TEXT("Denied contact at .17 must not spend receipt: same window may hit once after old iframes expire"),Target->Health,73.f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FArmorAdmissionMovementCancelTest,
    "CodexDungeon.Content.ArmorAdmission.MovementCancelsPendingArmor",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FArmorAdmissionMovementCancelTest::RunTest(const FString& Parameters)
{
    FArmorAdmissionWorld F; if (!TestTrue(TEXT("Review world created"),F.Create())) return false;
    TestTrue(TEXT("Half-second light armor change accepted"),F.Player->BeginArmorChange(TEXT("ARM-LGT-001")));
    F.Game->Tick(.25f);
    TestTrue(TEXT("Old armor still owns the incomplete change"),F.Player->ArmorId.IsEmpty()&&F.Player->GetArmorChangeRemaining()>0.f);
    F.Player->MoveOnGround({1,0},.1f); // D02: a real movement intent cancels uncommitted equip.
    TestTrue(TEXT("Movement cancels remaining armor action"),F.Player->GetArmorChangeRemaining()<=0.f);
    F.Game->Tick(.30f);
    TestEqual(TEXT("Canceled change never later equips its pending armor"),F.Player->ArmorId,FString());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FArmorAdmissionRoomPersistenceTest,
    "CodexDungeon.Content.ArmorAdmission.RoomTransitionPreservesFocusAndIframes",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FArmorAdmissionRoomPersistenceTest::RunTest(const FString& Parameters)
{
    FArmorAdmissionWorld F; if (!TestTrue(TEXT("Review world created"),F.Create())) return false;
    F.Player->ApplyCombatHit(1.f,nullptr,0.f); // Actual .65s player hurt iframe, no poise break.
    F.Player->Health=60.f; // Explicit QA initial missing HP; preserve that real iframe interval.
    TestTrue(TEXT("Real focus spend starts recovery delay"),F.Player->SpendFocus(50.f));
    F.Game->Tick(.10f);
    TestTrue(TEXT("Old iframes still active at free exit"),!F.Player->CanReceiveDirectHit());
    TestEqual(TEXT("Focus has not regenerated before one second"),F.Player->Focus,50.f);
    F.Game->bRoomCleared=true; // Cleared empty-room fixture, not a substitute for testing encounter clear logic.
    F.Game->Pickups.Reset(); F.Player->SetActorLocation({650,0,0});
    const int32 OldRoom=F.Game->RoomNumber;
    F.Game->TryInteract(); // Real public free-exit route -> NextRoom; do not call ResetFighter in this test.
    TestEqual(TEXT("The real free exit reached the next ordinary room"),F.Game->RoomNumber,OldRoom+1);
    TestEqual(TEXT("Ordinary room exit does not give prototype25 HP healing"),F.Player->Health,60.f);
    TestEqual(TEXT("Ordinary room exit does not refill focus"),F.Player->Focus,50.f);
    TestFalse(TEXT("Ordinary room exit does not clear existing hurt iframe deadline"),F.Player->CanReceiveDirectHit());
    F.Game->Tick(.50f); // Total last actual focus consumption age .60s, still before1.0s.
    TestEqual(TEXT("Preserved last consumption deadline prevents early focus regen after exit"),F.Player->Focus,50.f);
    return true;
}
#endif
