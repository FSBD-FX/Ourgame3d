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
struct FDodgeAdapterWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    ~FDodgeAdapterWorld() { if (World) World->DestroyWorld(false); }
    bool Create()
    {
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if (!World) return false;
        auto Instance = NewObject<UGameInstance>(GEngine); World->SetGameInstance(Instance);
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game = World->GetAuthGameMode<ADungeonGameMode>(); Player = World->SpawnActor<ADungeonFighter>();
        if (!Game || !Player) return false;
        Player->WeaponId = TEXT("WPN-SWD-001"); Player->ResetFighter({0,0});
        Game->PlayerFighter = Player; Game->bWaitingForStart = false; Game->bGameOver = false;
        return true;
    }
    ADungeonFighter* AddKnight(FVector2D Position)
    {
        auto Knight = World->SpawnActor<ADungeonFighter>();
        if (!Knight) return nullptr;
        Knight->ResetFighter(Position); Game->Enemies.Add(Knight);
        return Knight->InitializeStoneKnight(14001) ? Knight : nullptr;
    }
    bool AddWall()
    {
        auto Wall = World->SpawnActor<AActor>(); if (!Wall) return false;
        auto Box = NewObject<UBoxComponent>(Wall); Wall->SetRootComponent(Box);
        Box->SetBoxExtent({5,80,50}); Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Box->SetCollisionObjectType(ECC_WorldStatic); Box->SetCollisionResponseToAllChannels(ECR_Block);
        Box->RegisterComponentWithWorld(World); Wall->SetActorLocation({50,0,0}); return true;
    }
};
FDungeonKnightFrame TimedKnightFrame(ADungeonFighter* Player,double From,double To)
{
    FDungeonKnightFrame F; F.FromTime=From; F.ToTime=To; F.Target=Player;
    FDungeonKnightBody B; B.Fighter=Player; B.EntityId=99; B.Start=B.End=Player->GetGroundPosition();
    B.bUseTimedDamageAdmission=true; F.Bodies.Add(B); return F;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonDodgeFixedMotionAndIdlePositionHandoff,
    "CodexDungeon.Content.DodgeAdapter.FixedMotionAndIdlePositionHandoff",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonDodgeFixedMotionAndIdlePositionHandoff::RunTest(const FString& Parameters)
{
    for (const auto Armor : {TEXT(""),TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")})
    {
        FDodgeAdapterWorld F; if (!TestTrue(TEXT("Dodge authority world"),F.Create())) return false;
        if (*Armor) { F.Player->BeginArmorChange(Armor); F.Game->Tick(.51f); }
        F.Player->SpendFocus(50.f); const double Start=F.Game->GetSimulationTime();
        TestTrue(TEXT("Fresh grounded dodge starts with every armor"),F.Player->TryBeginDodge({1,0}));
        F.Game->Tick(.401f);
        TestTrue(TEXT("Every armor keeps fixed185cm dodge distance"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,185.0,.001));
        TestTrue(TEXT("Full dodge ends at.4 and keeps start+1.2 cooldown"),
            F.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Idle
            && FMath::IsNearlyEqual(F.Player->GetDodgeState().ReadyAt,Start+1.2,1.e-9));
        TestEqual(TEXT("Dodge neither spends nor restores the real fighter Focus"),F.Player->Focus,50.f);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->TryBeginDodge({1,1}); F.Game->Tick(.401f);
        const auto P=F.Player->GetGroundPosition();
        TestTrue(TEXT("Diagonal normalized path has185 total length"),FMath::IsNearlyEqual(P.Size(),185.0,.001)&&FMath::IsNearlyEqual(P.X,P.Y,.001));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->Facing=-1.f; F.Player->TryBeginDodge(); F.Game->Tick(.401f);
        TestTrue(TEXT("No-input dodge uses its start facing"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,-185.0,.001));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->MoveOnGround({1,0},.1f);
        TestTrue(TEXT("Real idle movement first moves26.5cm"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,26.5,.001));
        TestTrue(TEXT("Resolved idle position is handed off with a real dedicated receipt"),
            F.Player->GetDodgeState().LastPositionReceipt.Id>0
            && FMath::IsNearlyEqual(F.Player->GetDodgeState().Position.X,26.5,.001));
        TestTrue(TEXT("Dodge accepts the resolved new actor origin"),F.Player->TryBeginDodge({1,0}));
        F.Game->Tick(.401f);
        TestTrue(TEXT("First dodge starts at26.5 rather than reconstructing at zero"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,211.5,.001));
        F.Player->MoveOnGround({1,0},.1f); const auto NewOrigin=F.Player->GetGroundPosition();
        const double Ready=F.Player->GetDodgeState().ReadyAt;
        TestTrue(TEXT("Post-dodge idle movement changes position without washing cooldown"),
            FMath::IsNearlyEqual(F.Player->GetDodgeState().Position.X,NewOrigin.X,.001)&&Ready==1.2);
        F.Game->Tick(.801f);
        TestTrue(TEXT("Next dodge reuses the same persistent kernel"),F.Player->TryBeginDodge({-1,0}));
        const auto& S=F.Player->GetDodgeState();
        TestTrue(TEXT("Second action freezes latest handed-off origin and monotonic IDs"),
            S.Records.size()==2&&S.NextActionId==3&&FMath::IsNearlyEqual(S.Records.back().Origin.X,NewOrigin.X,.001));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()||!TestNotNull(TEXT("Actual blocking24cm stone"),F.AddKnight({100,0}))) return false;
        F.Player->TryBeginDodge({1,0}); F.Game->Tick(.401f);
        const auto& S=F.Player->GetDodgeState();
        TestTrue(TEXT("Real player18+stone24 body stops dodge at58"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,58.0,.001));
        TestTrue(TEXT("Body block retains original full action and CD"),S.Records.size()==1
            &&S.Records.back().Block==DungeonDodge::EBlock::Body&&S.Records.back().End==.4&&S.ReadyAt==1.2);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()||!F.AddWall()) return false;
        F.Player->TryBeginDodge({1,0}); F.Game->Tick(.401f);
        TestTrue(TEXT("Registered world wall stops swept dodge at27"),FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,27.0,.01));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonDodgeCompositeCancelAndActionExclusion,
    "CodexDungeon.Content.DodgeAdapter.CompositeCancelAndActionExclusion",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonDodgeCompositeCancelAndActionExclusion::RunTest(const FString& Parameters)
{
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->BeginArmorChange(TEXT("ARM-LGT-001")); F.Game->Tick(.25f);
        TestTrue(TEXT("Legal dodge atomically replaces uncommitted armor action"),F.Player->TryBeginDodge({1,0}));
        TestEqual(TEXT("Successful dodge cancels pending equip time"),F.Player->GetArmorChangeRemaining(),0.f);
        F.Game->Tick(.401f); TestTrue(TEXT("Canceled armor cannot later commit"),F.Player->ArmorId.IsEmpty());
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        TestTrue(TEXT("Initial dodge establishes cooldown"),F.Player->TryBeginDodge({1,0})); F.Game->Tick(.401f);
        F.Player->BeginArmorChange(TEXT("ARM-MED-001")); F.Game->Tick(.1f);
        const float Remaining=F.Player->GetArmorChangeRemaining();
        TestFalse(TEXT("Cooldown-invalid dodge cannot cancel armor"),F.Player->TryBeginDodge({-1,0}));
        TestEqual(TEXT("Failed dodge keeps pending armor progress"),F.Player->GetArmorChangeRemaining(),Remaining);
        F.Game->Tick(.401f); TestEqual(TEXT("Undisturbed pending armor commits normally"),F.Player->ArmorId,FString(TEXT("ARM-MED-001")));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->BeginAttack(); F.Game->Tick(.5f); F.Player->BeginAttack();
        TestTrue(TEXT("Primary fixture really has its one pending input"),F.Player->GetMeleeCombatState().PendingPrimary);
        TestFalse(TEXT("Dodge cannot cancel primary recovery"),F.Player->TryBeginDodge({1,0}));
        TestTrue(TEXT("Rejected dodge keeps primary buffer"),F.Player->GetMeleeCombatState().PendingPrimary);
        F.Game->Tick(.101f); TestEqual(TEXT("Buffered primary still starts stage2"),F.Player->ComboStage,2);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->TryBeginWeaponSkill(); F.Game->Tick(.1f); const auto Id=F.Player->GetWeaponSkillAction().ActionId;
        TestFalse(TEXT("Dodge cannot cancel active skill"),F.Player->TryBeginDodge({1,0}));
        TestTrue(TEXT("Skill keeps its original accepted action"),F.Player->GetWeaponSkillAction().Active&&F.Player->GetWeaponSkillAction().ActionId==Id);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->BeginAttack(); F.Game->Tick(.6f);
        TestFalse(TEXT("Held Shift does not create a dodge"),F.Player->TryBeginDodge({1,0},false));
        TestTrue(TEXT("Rejected held request preserves ground chain"),F.Player->GetMeleeCombatState().ComboReady);
        TestTrue(TEXT("Fresh dodge accepts after complete primary"),F.Player->TryBeginDodge({1,0}));
        TestFalse(TEXT("Only accepted dodge clears ground primary chain"),F.Player->GetMeleeCombatState().ComboReady);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->StartJump(); TestFalse(TEXT("Air dodge is illegal"),F.Player->TryBeginDodge({1,0}));
        TestEqual(TEXT("Illegal air dodge does not cancel jump"),F.Player->GetVerticalVelocity(),630.f);
        TestFalse(TEXT("Illegal air dodge does not consume an air primary token"),F.Player->GetMeleeCombatState().AirPrimarySpent);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonDodgeDirectIntervalsAndResolvedInterrupt,
    "CodexDungeon.Content.DodgeAdapter.DirectIntervalsAndResolvedInterrupt",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonDodgeDirectIntervalsAndResolvedInterrupt::RunTest(const FString& Parameters)
{
    for (const float At : {.059f,.061f,.199f,.201f})
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        TestTrue(TEXT("Damage-boundary dodge accepted"),F.Player->TryBeginDodge({1,0})); F.Game->Tick(At);
        F.Player->ApplyCombatHit(1.f,nullptr,0.f);
        TestEqual(TEXT("Actual direct contact respects inside/outside dodge interval"),F.Player->Health,(At>.06f&&At<.20f)?100.f:99.f);
        TestTrue(TEXT("Nonbreaking direct HP loss does not cancel dodge"),F.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Dodging);
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->TryBeginDodge({1,0}); F.Game->Tick(.25f);
        TestTrue(TEXT("Historical exact .06 endpoint is protected"),F.Player->IsDodgeInvulnerableAt(.06));
        TestFalse(TEXT("Historical exact .20 endpoint is unprotected"),F.Player->IsDodgeInvulnerableAt(.20));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->TryBeginDodge({1,0}); F.Game->Tick(.03f); F.Player->ApplyCombatHit(1.f,nullptr,30.f);
        const auto P=F.Player->GetGroundPosition(); const auto& S=F.Player->GetDodgeState();
        TestTrue(TEXT("True early break records interruption without refunding cooldown"),S.Phase==DungeonDodge::EPhase::Idle&&S.ReadyAt==1.2
            &&S.Records.size()==1&&S.Records.back().Finish==DungeonDodge::EFinish::PoiseBreak);
        TestFalse(TEXT("Broken early dodge cannot grant its unestablished future .10 protection"),F.Player->IsDodgeInvulnerableAt(.10));
        F.Game->Tick(.1f); TestTrue(TEXT("Broken dodge cannot continue old movement"),F.Player->GetGroundPosition().Equals(P,.001));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->TryBeginDodge({1,0}); F.Game->Tick(.03f); F.Player->ApplyCombatHit(1000.f,nullptr,0.f);
        TestTrue(TEXT("Actual death closes dodge and preserves its cooldown"),F.Player->GetDodgeState().Phase==DungeonDodge::EPhase::Dead&&F.Player->GetDodgeState().ReadyAt==1.2);
        const double Clock=F.Game->GetSimulationTime(),DodgeClock=F.Player->GetDodgeState().Time;
        F.Game->Tick(.3f);
        TestTrue(TEXT("Terminal presentation never advances dodge or run clock"),F.Game->GetSimulationTime()==Clock&&F.Player->GetDodgeState().Time==DodgeClock);
        TestFalse(TEXT("Dead early dodge does not retain future protection"),F.Player->IsDodgeInvulnerableAt(.1));
    }
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        F.Player->ApplyCombatHit(1.f,nullptr,0.f); F.Player->TryBeginDodge({1,0}); F.Game->Tick(.25f);
        F.Player->ApplyCombatHit(1.f,nullptr,0.f); TestEqual(TEXT("Old hurt protection remains after dodge protection ends"),F.Player->Health,99.f);
        F.Game->Tick(.41f); F.Player->ApplyCombatHit(1.f,nullptr,0.f);
        TestEqual(TEXT("Hurt and dodge union does not add durations"),F.Player->Health,98.f);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonStoneTimedWindowResumesAfterProtection,
    "CodexDungeon.Content.DodgeAdapter.StoneTimedWindowResumesAfterProtection",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FDungeonStoneTimedWindowResumesAfterProtection::RunTest(const FString& Parameters)
{
    for (const bool CoversWholeWindow : {false,true})
    {
        FDodgeAdapterWorld F; if (!F.Create()) return false;
        auto Owner=F.World->SpawnActor<ADungeonFighter>(); if (!Owner) return false;
        Owner->bEnemy=true; Owner->ResetFighter({0,0}); F.Player->SetActorLocation({50,0,0});
        FDungeonStoneKnightDriver Driver(Owner,15001);
        auto WakeFrame=TimedKnightFrame(F.Player,0,0);
        if (!TestTrue(TEXT("Real driver accepts resolved wake fact"),Driver.ApplyResolvedHit(1,0,WakeFrame).Accepted)) return false;
        if (!TestTrue(TEXT("Real driver crosses warning and starts close shield attack"),Driver.StepTo(.85,TimedKnightFrame(F.Player,0,.85)).Accepted)) return false;
        const auto A=Driver.State().Action;
        TestTrue(TEXT("Close actual target chose shield"),A.Kind==DungeonStoneKnight::EAttack::Shield);
        const double ProtectionEnd=CoversWholeWindow?A.PlannedActiveEnd+.1:A.ActiveAt+.07;
        auto Frame=TimedKnightFrame(F.Player,.85,A.ActiveAt+.10);
        Frame.Bodies[0].DirectInvulnerabilityIntervals.Add({A.ActiveAt-.07,ProtectionEnd});
        const auto Batch=Driver.StepTo(Frame.ToTime,Frame);
        TestTrue(TEXT("Timed observation batch is accepted"),Batch.Accepted);
        if (CoversWholeWindow) TestEqual(TEXT("Real A2 geometry cannot hit through a fully protected window"),Batch.Hits.Num(),0);
        else
        {
            TestEqual(TEXT("Protected entry leaves one legal hit in remaining active window"),Batch.Hits.Num(),1);
            if (!Batch.Hits.IsEmpty()) TestTrue(TEXT("First real legal hit is protection end, not geometric entry"),FMath::IsNearlyEqual(Batch.Hits[0].AtTime,ProtectionEnd,1.e-9));
            auto Later=TimedKnightFrame(F.Player,Frame.ToTime,A.PlannedActiveEnd);
            Later.Bodies[0].DirectInvulnerabilityIntervals=Frame.Bodies[0].DirectInvulnerabilityIntervals;
            TestEqual(TEXT("Remaining same A2 window cannot duplicate its accepted target"),Driver.StepTo(Later.ToTime,Later).Hits.Num(),0);
        }
        TestEqual(TEXT("Continuous driver query itself does not deduct actual Actor HP"),F.Player->Health,100.f);
    }
    return true;
}
#endif
