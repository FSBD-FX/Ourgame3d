#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "CollisionQueryParams.h"

namespace
{
struct FSkillBoundaryReviewWorld
{
    UWorld* World = nullptr;
    ADungeonGameMode* Game = nullptr;
    ADungeonFighter* Player = nullptr;
    APlayerController* Controller = nullptr;
    ~FSkillBoundaryReviewWorld() { if (World) World->DestroyWorld(false); }
    bool Create(bool WithController = false)
    {
        const auto Settings = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true,
            ERHIFeatureLevel::Num, &Settings);
        if (!World) return false;
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL; URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game = World->GetAuthGameMode<ADungeonGameMode>();
        Player = World->SpawnActor<ADungeonFighter>();
        if (!Game || !Player) return false;
        Player->WeaponId = TEXT("WPN-SWD-001");
        Player->ResetFighter({0,0});
        Game->PlayerFighter = Player; Game->bWaitingForStart = false; Game->bGameOver = false;
        if (WithController)
        {
            Controller = World->SpawnActor<APlayerController>();
            if (!Controller) return false;
            Controller->Possess(Player);
            if (!Controller->PlayerInput) Controller->PlayerInput = NewObject<UPlayerInput>(Controller);
            if (!Controller->IsLocalController() || Player->GetController() != Controller) return false;
        }
        return true;
    }
    ADungeonFighter* AddKnight(FVector2D Position, uint64 Id)
    {
        auto Knight = World->SpawnActor<ADungeonFighter>();
        if (!Knight) return nullptr;
        Knight->ResetFighter(Position); Game->Enemies.Add(Knight);
        return Knight->InitializeStoneKnight(Id) ? Knight : nullptr;
    }
    bool AdvanceTo(double Time)
    {
        const double Delta = Time-Game->GetSimulationTime();
        if (!FMath::IsFinite(Delta) || Delta < 0.0) return false;
        if (Delta > 0.0) Game->Tick(float(Delta));
        // A fixture precision guard, not an altered production event boundary.
        return FMath::Abs(Game->GetSimulationTime()-Time) < 1.e-5;
    }
    bool SetHeldKey(FKey Key, bool Down)
    {
        if (!Controller || !Controller->PlayerInput) return false;
        Controller->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.0:0.0));
        Controller->PlayerInput->Tick(.005f);
        TArray<UInputComponent*> EmptyStack;
        Controller->PlayerInput->ProcessInputStack(EmptyStack,.005f,false);
        return Controller->IsInputKeyDown(Key) == Down;
    }
    bool AddLastWindowOccluder()
    {
        auto Wall = World->SpawnActor<AActor>();
        if (!Wall) return false;
        auto Box = NewObject<UBoxComponent>(Wall);
        Wall->SetRootComponent(Box); Box->SetBoxExtent({5,50,50});
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Box->SetCollisionObjectType(ECC_WorldStatic);
        Box->SetCollisionResponseToAllChannels(ECR_Block);
        Box->RegisterComponentWithWorld(World);
        // XY: [75,85] x [-99.95,.05]. Neither body touches this wall.
        Wall->SetActorLocation({80,-49.95,0});
        return true;
    }
    bool LineBlocked(ADungeonFighter* Target) const
    {
        FCollisionObjectQueryParams Objects;
        Objects.AddObjectTypesToQuery(ECC_WorldStatic);
        Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
        FCollisionQueryParams Params(SCENE_QUERY_STAT(SkillBoundaryReviewLOS),false);
        Params.AddIgnoredActor(Player); Params.AddIgnoredActor(Target);
        const auto From = Player->GetGroundPosition(), To = Target->GetGroundPosition();
        return World->LineTraceTestByObjectType(FVector(From.X,From.Y,0),FVector(To.X,To.Y,0),Objects,Params);
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkillBoundaryPoiseBeforeEmission,
    "CodexDungeon.Content.WeaponSkillBoundaryReview.RealPoiseContactBeforeEmissionSameBatch",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkillBoundaryPoiseBeforeEmission::RunTest(const FString& Parameters)
{
    FSkillBoundaryReviewWorld F;
    if (!TestTrue(TEXT("SETUP: isolated real game/physics world"),F.Create())) return false;
    auto Knight = F.AddKnight({-50,0},23001);
    if (!TestNotNull(TEXT("SETUP: real natural stone-knight driver"),Knight)) return false;
    F.Game->Tick(.8f);
    F.Player->ApplyCombatHit(1.f,nullptr,12.f); // Real nonbreaking loss; no private poise/HP edits.
    if (!TestTrue(TEXT("SETUP: actual12 stagger stays below player threshold30"),
        F.Player->Health == 99.f && F.Player->GetPoiseThreshold() == 30.f && F.Player->CanStartAttack())) return false;
    F.Game->Tick(.1f);
    const auto Driver = Knight->GetStoneKnightDriver();
    if (!TestTrue(TEXT("SETUP: natural proximity wake has led to first real shield"),Driver
        && Driver->State().Awakened && Driver->State().Action.Kind == DungeonStoneKnight::EAttack::Shield
        && Driver->State().Action.InProgress)) return false;
    const auto Shield = Driver->State().Action;
    if (!TestTrue(TEXT("SETUP: reach normal skill start199ms before actual shield contact"),
        F.AdvanceTo(Shield.ActiveAt-.199))) return false;
    F.Player->Facing = -1.f;
    if (!TestTrue(TEXT("SETUP: real grounded skill API accepted"),F.Player->TryBeginWeaponSkill())) return false;
    const auto Skill = F.Player->GetWeaponSkillAction();
    if (!TestTrue(TEXT("SETUP: real skill emission is1ms after shield begins"),
        Shield.ActiveAt < Skill.ActiveAt && FMath::Abs((Skill.ActiveAt-Shield.ActiveAt)-.001) < 1.e-5)) return false;
    if (!TestTrue(TEXT("SETUP: stop1ms before actual shield active boundary"),F.AdvanceTo(Shield.ActiveAt-.001))) return false;
    if (!TestTrue(TEXT("SETUP: old hurt iframe expired; skill locked but not emitted"),
        F.Player->CanReceiveDirectHit() && F.Player->GetWeaponSkillAction().Locked
        && !F.Player->GetWeaponSkillAction().ForwardStepIssued && Knight->Health == 110.f)) return false;

    const double From = F.Game->GetSimulationTime(), To = From+double(.005f);
    const auto PlayerBefore = F.Player->GetGroundPosition();
    const float HPBefore = F.Player->Health;
    if (!TestTrue(TEXT("SETUP: one5ms batch strictly contains contact then emission"),
        From < Shield.ActiveAt && Shield.ActiveAt < Skill.ActiveAt && Skill.ActiveAt < To)) return false;
    // A real driver copy with the captured state performs its actual world query.
    // It cannot mutate either Actor or the owned driver. Both possible player
    // endpoints (0 and body-truncated-8) are inside the shield from its onset,
    // so the exact first contact stays Shield.ActiveAt without relying on the
    // known instantaneous-step/linear-path approximation.
    FDungeonStoneKnightDriver Witness(Knight,Driver->State().EntityId,From);
    if (!TestTrue(TEXT("SETUP: actual captured driver state restores in read-only witness"),Witness.Restore(Driver->Capture()))) return false;
    FDungeonKnightFrame Frame; Frame.FromTime = From; Frame.ToTime = To; Frame.Target = F.Player;
    Frame.bCanStartAttack = false;
    FDungeonKnightBody PlayerBody;PlayerBody.Fighter = F.Player;PlayerBody.EntityId = F.Player->GetRuntimeEntityId();
    PlayerBody.Start = PlayerBody.End = PlayerBefore;Frame.Bodies.Add(PlayerBody);
    const auto Contact = Witness.StepTo(To,Frame);
    if (!TestTrue(TEXT("SETUP: actual driver query finds one13/18 contact before emission"),
        Contact.Accepted && Contact.Hits.Num() == 1 && Contact.Hits[0].TargetId == F.Player->GetRuntimeEntityId()
        && Contact.Hits[0].Damage == 13.0 && Contact.Hits[0].Stagger == 18.0
        && Contact.Hits[0].AtTime == Shield.ActiveAt && Contact.Hits[0].AtTime < Skill.ActiveAt
        && F.Player->Health == HPBefore && Knight->Health == 110.f)) return false;
    AddInfo(FString::Printf(TEXT("Real contact=%.12f, skill emission=%.12f, batch=[%.12f,%.12f]"),
        Contact.Hits[0].AtTime,Skill.ActiveAt,From,To));

    F.Game->Tick(.005f);
    bool ActualDriverHit = false;
    for (const auto& Hit:Knight->GetStoneKnightDriver()->State().HitReceipts)
        ActualDriverHit |= Hit.AttackId == Shield.AttackId && Hit.TargetId == F.Player->GetRuntimeEntityId();
    const auto& After = F.Player->GetWeaponSkillAction();
    if (!TestTrue(TEXT("SETUP: owned driver hit committed real HP loss and a live-player poise interrupt"),
        ActualDriverHit && FMath::IsNearlyEqual(F.Player->Health,HPBefore-13.f,.001f) && !F.Player->bDead
        && !After.Active && After.ActionId == Skill.ActionId && After.Terminal == DungeonWeaponActions::EEvent::Interrupted)) return false;
    TestFalse(TEXT("Earlier actual poise break prevents future .20 forward-step emission"),After.ForwardStepIssued);
    TestTrue(TEXT("Earlier actual poise break leaves actor at pre-emission position"),F.Player->GetGroundPosition().Equals(PlayerBefore,.001));
    TestEqual(TEXT("Earlier actual poise break prevents future skill damage to knight"),Knight->Health,110.f);
    TestTrue(TEXT("Real interruption preserves the locked original skill cooldown"),
        FMath::IsNearlyEqual(F.Game->GetSimulationTime()+F.Player->GetWeaponSkillCooldownRemaining(),Skill.LockAt+4.0,1.e-5));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSkillBoundaryLastWindowLOS,
    "CodexDungeon.Content.WeaponSkillBoundaryReview.LastWindowBatchLOSBecomesClear",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkillBoundaryLastWindowLOS::RunTest(const FString& Parameters)
{
    FSkillBoundaryReviewWorld F;
    if (!TestTrue(TEXT("SETUP: real game world with local possessed input controller"),F.Create(true))) return false;
    auto Knight = F.AddKnight({130,0},23002);
    if (!TestNotNull(TEXT("SETUP: real dormant armor45 knight target"),Knight)
        || !TestTrue(TEXT("SETUP: registered real wall occluder"),F.AddLastWindowOccluder())) return false;
    if (!TestTrue(TEXT("SETUP: actual normal grounded skill accepted"),F.Player->TryBeginWeaponSkill())) return false;
    const auto Skill = F.Player->GetWeaponSkillAction();
    if (!TestTrue(TEXT("SETUP: advance into last4ms of actual active window"),F.AdvanceTo(Skill.ActiveEnd-.004))) return false;
    if (!TestTrue(TEXT("SETUP: actual forward step30 complete; target protected only by real LOS"),
        FMath::IsNearlyEqual(F.Player->GetGroundPosition().X,30.0,.001)
        && FMath::IsNearlyEqual(F.Player->GetGroundPosition().Y,0.0,.001)
        && Knight->Health == 110.f && F.LineBlocked(Knight)
        && F.Player->GetWeaponSkillAction().Active)) return false;
    const double From = F.Game->GetSimulationTime(), To = From+double(.005f);
    if (!TestTrue(TEXT("SETUP: last single5ms batch crosses actual half-open window end"),
        From < Skill.ActiveEnd && To > Skill.ActiveEnd)) return false;
    if (!TestTrue(TEXT("SETUP: actual Controller W input becomes held"),F.SetHeldKey(EKeys::W,true))) return false;
    F.Game->Tick(.005f);
    const bool Released = F.SetHeldKey(EKeys::W,false);
    const auto P = F.Player->GetGroundPosition();
    if (!TestTrue(TEXT("SETUP: real normal motion clears actual wall LOS while geometry remains inside range"),
        Released && P.Y > .6 && P.Y < .7 && FMath::IsNearlyEqual(P.X,30.0,.001)
        && !F.LineBlocked(Knight) && Knight->GetGroundPosition().Equals({130,0},.001)
        && F.Game->GetSimulationTime() > Skill.ActiveEnd)) return false;
    // At wall's far X85, ray height is .45*playerY. It clears Y=.05 once
    // playerY>.1111111. Real endpoint>.6 after5ms and>3.9ms of that motion
    // occurs before the read-out End: the clear portion is genuinely in-window.
    // This is fixture geometry, not a copy of the game's hit/LOS algorithm.
    const double MotionDuration = F.Game->GetSimulationTime()-From;
    const double ClearAt = From+MotionDuration*(.05/.45)/P.Y;
    if (!TestTrue(TEXT("SETUP: actual continuous motion makes LOS clear strictly before skill end"),
        ClearAt > From && ClearAt < Skill.ActiveEnd-.001)) return false;
    AddInfo(FString::Printf(TEXT("Actual last batch [%.12f,%.12f], LOS clear before %.12f, active end %.12f, playerY %.6f"),
        From,F.Game->GetSimulationTime(),ClearAt,Skill.ActiveEnd,P.Y));
    TestTrue(TEXT("Skill hits a target whose real LOS becomes clear in the remaining legal final window"),
        FMath::IsNearlyEqual(Knight->Health,110.f-32.f/1.45f,.001f));
    const float After = Knight->Health;
    F.Game->Tick(.02f);
    TestEqual(TEXT("Window ending still prevents any second target damage"),Knight->Health,After);
    return true;
}
#endif
