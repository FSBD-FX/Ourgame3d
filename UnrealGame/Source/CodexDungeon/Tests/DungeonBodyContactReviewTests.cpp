#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"

namespace
{
struct FBodyContactReviewWorld
{
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    ADungeonFighter* Knight=nullptr;
    APlayerController* Controller=nullptr;
    ~FBodyContactReviewWorld() { if (World) World->DestroyWorld(false); }
    bool Create(double InitialX)
    {
        if (!GEngine) return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if (!World) return false;
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if (!World->SetGameMode(URL)) return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        Knight=World->SpawnActor<ADungeonFighter>();
        if (!Game || !Player || !Controller || !Knight) return false;
        Player->WeaponId=TEXT("WPN-SWD-001");Player->ResetFighter({InitialX,0});
        Game->PlayerFighter=Player;Game->bWaitingForStart=false;Game->bGameOver=false;
        Controller->Possess(Player);
        if (!Controller->PlayerInput) Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        Knight->ResetFighter({300,0});Game->Enemies.Add(Knight);
        return Controller->IsLocalController() && Player->GetController()==Controller
            && Knight->InitializeStoneKnight(24001);
    }
    bool AdvanceTo(double Time)
    {
        const double Delta=Time-Game->GetSimulationTime();
        if (!FMath::IsFinite(Delta) || Delta<0.) return false;
        if (Delta>0.) Game->Tick(float(Delta));
        return FMath::Abs(Game->GetSimulationTime()-Time)<1.e-5;
    }
    bool Held(FKey Key,bool Down)
    {
        Controller->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);
        TArray<UInputComponent*> EmptyStack;Controller->PlayerInput->ProcessInputStack(EmptyStack,.005f,false);
        return Controller->IsInputKeyDown(Key)==Down;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonBodyContactEscapeAfterRealCharge,
    "CodexDungeon.Content.BodyContactReview.RealChargeRoundoffAllowsTangentAndEscapeButBlocksInward",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FDungeonBodyContactEscapeAfterRealCharge::RunTest(const FString& Parameters)
{
    // Finite initial-spawn samples, not offsets injected into the contact result.
    // The first is the actual Explore v001 player X; the other two are nearby
    // ordinary decimal positions. Every sample must use a real natural charge.
    TUniquePtr<FBodyContactReviewWorld> F;
    TUniquePtr<FBodyContactReviewWorld> OutsideContact;
    for (const double InitialX:{42.18300203853069,42.183,42.1})
    {
        auto Candidate=MakeUnique<FBodyContactReviewWorld>();
        if (!TestTrue(TEXT("SETUP: actual game, physics, player/controller and stone driver"),Candidate->Create(InitialX))) return false;
        Candidate->Game->Tick(.86f);
        const auto Driver=Candidate->Knight->GetStoneKnightDriver();
        if (!TestTrue(TEXT("SETUP: natural proximity wake led to a real charge"),Driver
            && Driver->State().Awakened && Driver->State().Action.Kind==DungeonStoneKnight::EAttack::Charge
            && Driver->State().Action.InProgress)) return false;
        const auto Charge=Driver->State().Action;
        if (!TestTrue(TEXT("SETUP: reach actual charge activation minus40ms"),Candidate->AdvanceTo(Charge.ActiveAt-.04))) return false;
        Candidate->Player->StartJump(); // Real production jump; not damage immunity or a Z edit.
        if (!TestTrue(TEXT("SETUP: normal jump API accepted before actual charge"),Candidate->Player->GetVerticalVelocity()>0.f)) return false;
        if (!TestTrue(TEXT("SETUP: advance through real physical charge/body stop"),Candidate->AdvanceTo(Charge.ActiveAt+.45))) return false;
        if (!TestTrue(TEXT("SETUP: actual body stop without a valid damaging charge hit"),
            Driver->State().Action.Stop==DungeonStoneKnight::EStop::Body && Candidate->Player->Health==100.f)) return false;
        if (!TestTrue(TEXT("SETUP: real jump landed during original full recovery"),Candidate->AdvanceTo(Charge.ActiveAt+.78)
            &&Candidate->Player->JumpHeight==0.f&&Candidate->Player->CanStartAttack()
            &&Driver->State().Phase==DungeonStoneKnight::EPhase::Recovery)) return false;
        const double Gap=Candidate->Knight->GetGroundPosition().X-Candidate->Player->GetGroundPosition().X;
        AddInfo(FString::Printf(TEXT("Real charge sample initialX=%.17g, playerX=%.17g, knightX=%.17g, gap=%.17g, inward roundoff=%.17g"),
            InitialX,Candidate->Player->GetGroundPosition().X,Candidate->Knight->GetGroundPosition().X,Gap,42.-Gap));
        // Keep the original1e-9 near-face classification window for SETUP only.
        // Prefer a naturally generated inside sample over every outside sample,
        // so the old production bug cannot hide behind the first safe endpoint.
        // A corrected conservative sweep need not reproduce the original bug.
        if (Gap<42. && Gap>42.-1.e-9)
        {
            if (!F) F=MoveTemp(Candidate);
        }
        else if (Gap>=42. && Gap<42.+1.e-9 && !OutsideContact)
            OutsideContact=MoveTemp(Candidate);
    }
    if (!F) F=MoveTemp(OutsideContact);
    if (!TestTrue(TEXT("SETUP: a real charge generated a measured near-contact face without post-contact teleport"),F.IsValid())) return false;
    const double SelectedGap=F->Knight->GetGroundPosition().X-F->Player->GetGroundPosition().X;
    AddInfo(FString::Printf(TEXT("Selected real BodyStop classification=%s, playerX=%.17g, knightX=%.17g, rawGap=%.17g, signedInwardRoundoff=%.17g"),
        SelectedGap<42.?TEXT("tiny_inside_preferred"):SelectedGap==42.?TEXT("exact_face"):TEXT("near_outside_conservative"),
        F->Player->GetGroundPosition().X,F->Knight->GetGroundPosition().X,SelectedGap,42.-SelectedGap));
    const FVector2D Contact=F->Player->GetGroundPosition();
    const double ReadyAt=F->Player->GetDodgeState().ReadyAt;
    const uint64 NextAction=F->Player->GetDodgeState().NextActionId;
    const uint64 PositionReceipt=F->Player->GetDodgeState().NextPositionReceiptId;
    if (!TestTrue(TEXT("SETUP: real Controller holds W for tangent motion"),F->Held(EKeys::W,true))) return false;
    F->Game->Tick(.05f);
    if (!TestTrue(TEXT("SETUP: W release observed by real Controller"),F->Held(EKeys::W,false))) return false;
    const FVector2D Tangent=F->Player->GetGroundPosition();
    TestTrue(TEXT("Tiny real contact roundoff cannot lock normal W tangent movement"),Tangent.Y>Contact.Y+10.);
    TestTrue(TEXT("Tangent movement keeps the contacted X face"),FMath::Abs(Tangent.X-Contact.X)<1.e-9);
    TestTrue(TEXT("Actually resolved tangent position enters the existing position receipt domain"),
        F->Player->GetDodgeState().NextPositionReceiptId>PositionReceipt
        &&F->Player->GetDodgeState().Position.X==Tangent.X&&F->Player->GetDodgeState().Position.Y==Tangent.Y);

    // Extend the same real contact: leave the Y body interval, then return
    // alongside its contacted X face. Never overwrite either actor position.
    if (!TestTrue(TEXT("SETUP: real Controller holds W to leave the body depth"),F->Held(EKeys::W,true))) return false;
    F->Game->Tick(.1f);
    if (!TestTrue(TEXT("SETUP: W release after leaving body depth"),F->Held(EKeys::W,false))) return false;
    const FVector2D OutsideDepth=F->Player->GetGroundPosition();
    if (!TestTrue(TEXT("SETUP: real W reached Y beyond the combined36cm body depth without changing the X face"),
        OutsideDepth.Y>36.&&FMath::Abs(OutsideDepth.X-Contact.X)<1.e-9)) return false;
    if (!TestTrue(TEXT("SETUP: real Controller holds S to return alongside the contacted face"),F->Held(EKeys::S,true))) return false;
    F->Game->Tick(.14f);
    if (!TestTrue(TEXT("SETUP: S release observed by real Controller"),F->Held(EKeys::S,false))) return false;
    AddInfo(FString::Printf(TEXT("Normal W-out/S-back: outsideY=%.17g, returnedY=%.17g, gapX=%.17g, recoveryEnd=%.17g, actualTime=%.17g"),
        OutsideDepth.Y,F->Player->GetGroundPosition().Y,F->Knight->GetGroundPosition().X-F->Player->GetGroundPosition().X,
        F->Knight->GetStoneKnightDriver()->State().Action.RecoveryEnd,F->Game->GetSimulationTime()));
    if (!TestTrue(TEXT("Normal S returns below Y5 after real W passed Y36; touching X face is not a new inward entry"),
        F->Player->GetGroundPosition().Y<5.&&FMath::Abs(F->Player->GetGroundPosition().X-Contact.X)<1.e-9)) return false;

    if (!TestTrue(TEXT("SETUP: real Controller holds D toward the still-overlapping body face"),F->Held(EKeys::D,true))) return false;
    F->Game->Tick(.05f);F->Held(EKeys::D,false);
    TestTrue(TEXT("Normal inward D remains blocked while Y lies within the body depth"),
        FMath::Abs(F->Player->GetGroundPosition().X-Tangent.X)<1.e-9);
    if (!TestTrue(TEXT("SETUP: real Controller holds A away from the contacted body"),F->Held(EKeys::A,true))) return false;
    F->Game->Tick(.05f);F->Held(EKeys::A,false);
    TestTrue(TEXT("Normal A can separate from a tiny real contact roundoff"),F->Player->GetGroundPosition().X<Tangent.X-10.);
    if (!TestTrue(TEXT("SETUP: real Controller again holds D toward the body"),F->Held(EKeys::D,true))) return false;
    F->Game->Tick(.2f);F->Held(EKeys::D,false);
    TestTrue(TEXT("Separating and returning never grants passage through the knight"),
        F->Player->GetGroundPosition().X<=F->Knight->GetGroundPosition().X-42.+1.e-9);
    TestTrue(TEXT("Movement handoff preserves the same dodge identity, cooldown and absolute clock"),
        F->Player->GetDodgeState().NextActionId==NextAction&&F->Player->GetDodgeState().ReadyAt==ReadyAt
        &&F->Player->GetDodgeState().Time==F->Game->GetSimulationTime());
    TestTrue(TEXT("No fabricated damage, death or reward was needed for body escape"),
        F->Player->Health==100.f&&!F->Player->bDead&&F->Knight->Health==110.f&&!F->Knight->bDead&&F->Game->Pickups.IsEmpty());
    return true;
}
#endif
