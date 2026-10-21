#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonStoneGuardDriver.h"
#include "../DungeonRoomLayout.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include <cmath>
#include <limits>
namespace GuardWakeEntryV005
{
namespace Guard=DungeonStoneGuard;
struct FWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;ADungeonFighter* Owner=nullptr;
    FAutomationTestBase& Test;explicit FWorld(FAutomationTestBase& T):Test(T){}
    ~FWorld(){if(World){if(World->HasBegunPlay())World->EndPlay(EEndPlayReason::Quit);World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Create()
    {
        if(!Test.TestNotNull(TEXT("Real Engine prerequisite"),GEngine))return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!Test.TestNotNull(TEXT("Real native physics world"),World))return false;
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!Test.TestTrue(TEXT("Real project GameMode"),World->SetGameMode(URL)))return false;
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
        if(!Game||!Player)return false;
        Player->SetActorTickEnabled(false);Player->ResetFighter({-1035.4682208563124,-162.2042858545901});
        Game->PlayerFighter=Player;Game->bWaitingForStart=false;
        if(!Test.TestTrue(TEXT("Real admitted integration Run"),Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1)))return false;
        Owner=Game->SpawnStoneGuard({-800.,-160.});
        return Test.TestTrue(TEXT("Actual public Guard owner identity/185HP/driver"),Owner&&Owner->GetStoneGuardDriver()
            &&Owner->GetRuntimeEntityId()!=Player->GetRuntimeEntityId()&&Owner->EnemyContentId==TEXT("ENM-STN-003")&&Owner->Health==185.);
    }
    FDungeonKnightFrame Frame(double Begin,double End,FVector2D From,FVector2D To)const
    {
        FDungeonKnightFrame F;F.FromTime=Begin;F.ToTime=End;F.Target=Player;F.CenterBounds=DungeonRoomLayout::CenterBounds();
        F.bCanStartAttack=false; // Isolate Dormant->Wake; no combat damage is required for this geometry regression.
        FDungeonKnightBody P;P.Fighter=Player;P.EntityId=Player->GetRuntimeEntityId();P.Start=From;P.End=To;
        P.BodyHalfExtent=Player->GetCombatBodyHalfExtent();F.Bodies.Add(P);
        FDungeonKnightBody O;O.Fighter=Owner;O.EntityId=Owner->GetRuntimeEntityId();O.Start=O.End=Owner->GetGroundPosition();
        O.BodyHalfExtent=Owner->GetCombatBodyHalfExtent();O.bSameTeam=true;F.Bodies.Add(O);return F;
    }
    FDungeonStoneGuardDriver Driver(double Begin)const
    {return FDungeonStoneGuardDriver(Owner,Owner->GetRuntimeEntityId(),Begin,{-800.,-160.,0.},{});}
};
double R2(FVector2D P){const double X=(P.X+800.)/235.,Y=(P.Y+160.)/110.;return X*X+Y*Y;}
FVector2D At(const FDungeonKnightFrame& F,double T)
{return FMath::Lerp(F.Bodies[0].Start,F.Bodies[0].End,FMath::Clamp((T-F.FromTime)/(F.ToTime-F.FromTime),0.,1.));}
int Count(const Guard::FState& S,Guard::EEventKind Kind){int N=0;for(const auto& E:S.Issued)N+=E.Kind==Kind;return N;}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardWakeRoundedEntryReplannedEndpoint,
 "CodexDungeon.Content.StoneGuardNative.WakeEntryReplannedEndpointNeverRejectsLegalInterval",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardWakeRoundedEntryReplannedEndpoint::RunTest(const FString& Parameters)
{
    (void)Parameters;using namespace GuardWakeEntryV005;FWorld W(*this);if(!W.Create())return false;
    // v003 original native test failed its geometric premise under actual UE/MSVC.
    // Keep that failure. This test derives each short end from the ACTUAL native
    // driver's wider accepted preview, then re-evaluates real native geometry.
    constexpr double OriginalLastTime=9.600689999759197;
    const double Begin=OriginalLastTime+.005,WideEnd=Begin+.005;
    const FVector2D OriginalLast(-1036.8992209173477,-162.2042858545901);
    const double Speed=double(float(286.2));const FVector2D Direction(1.,0.);
    const auto Shift=[](double Value,int Ulps)
    {for(int I=0;I<FMath::Abs(Ulps);++I)Value=std::nextafter(Value,Ulps<0?-std::numeric_limits<double>::infinity():std::numeric_limits<double>::infinity());return Value;};
    const auto NativeInside=[&](double Time,FVector2D P)
    {
        Guard::FGuardKernel Probe(W.Owner->GetRuntimeEntityId(),Time,{-800.,-160.,0.});
        Guard::FWorldInput Input;Input.HasTarget=true;Input.Target={P.X,P.Y,0.};Input.CanStartAttack=false;
        const auto Result=Probe.StepTo(Time,Input);
        return Result.Accepted&&Probe.State().WakeStartedAt==Time; // Real production NearWake, not test/Python R2 oracle.
    };
    int32 LegalShortIntervals=0,WideIntervals=0;
    for(int Construction=0;Construction<2;++Construction)for(int InitialXUlps=-2;InitialXUlps<=2;++InitialXUlps)
    {
        FVector2D From=Construction==0?OriginalLast+Direction*Speed*(Begin-OriginalLastTime)
            :FVector2D(-1035.4682208563124,-162.2042858545901);
        From.X=Shift(From.X,InitialXUlps);
        // These are real finite observation candidates around the retained input,
        // not manually edited kernel State or a forced Wake time.
        const auto Replan=[&](double End)
        {return From+Direction*Speed*(End-Begin);};
        const auto WideFrame=W.Frame(Begin,WideEnd,From,Replan(WideEnd));
        if(!TestTrue(TEXT("Actual native geometry confirms each finite wide trajectory begins outside and ends inside"),
            !NativeInside(Begin,At(WideFrame,Begin))&&NativeInside(WideEnd,At(WideFrame,WideEnd))))return false;
        auto Wide=W.Driver(Begin);if(!Wide.BeginCombat())return false;
        const auto B=Wide.StepTo(WideEnd,WideFrame);
        AddInfo(FString::Printf(TEXT("v005 wide construction=%d initialXulps=%d FromTime=%.17g ToTime=%.17g From=(%.17g,%.17g) To=(%.17g,%.17g) R2=%.17g accepted=%d wake=%.17g"),
            Construction,InitialXUlps,Begin,WideEnd,From.X,From.Y,WideFrame.Bodies[0].End.X,WideFrame.Bodies[0].End.Y,R2(At(WideFrame,WideEnd)),B.Accepted,Wide.State().WakeStartedAt));
        if(!TestTrue(TEXT("Every legal continuous wide native observation is accepted before replanning"),B.Accepted))return false;
        ++WideIntervals;const double PreviewWake=Wide.State().WakeStartedAt;
        if(!TestTrue(TEXT("Actual wider driver emits one original Wake within its real observation interval"),
            PreviewWake>Begin&&PreviewWake<=WideEnd&&Count(Wide.State(),Guard::EEventKind::WakeStarted)==1&&Wide.State().WakeEnd==PreviewWake+1.))return false;
        int32 ThisWideLegal=0;
        for(int EndUlps=-16;EndUlps<=32;++EndUlps)
        {
            const double End=Shift(PreviewWake,EndUlps);if(!(End>Begin&&End<=WideEnd))continue;
            const auto Frame=W.Frame(Begin,End,From,Replan(End));
            const FVector2D ActualEndpoint=At(Frame,End);
            // Endpoints outside the unchanged production predicate are explicitly
            // diagnostic only, never accepted as the positive regression premise.
            if(!NativeInside(End,ActualEndpoint))
            {
                if(EndUlps>=-2&&EndUlps<=2)AddInfo(FString::Printf(TEXT("v005 outside diagnostic construction=%d initialXulps=%d endUlps=%d t=%.17g P=(%.17g,%.17g) R2=%.17g"),
                    Construction,InitialXUlps,EndUlps,End,ActualEndpoint.X,ActualEndpoint.Y,R2(ActualEndpoint)));
                continue;
            }
            ++LegalShortIntervals;++ThisWideLegal;auto Narrow=W.Driver(Begin);if(!Narrow.BeginCombat())return false;
            const auto N=Narrow.StepTo(End,Frame);
            if(!N.Accepted)
            {
                AddInfo(FString::Printf(TEXT("v005 LEGAL REPLANNED REJECTION construction=%d initialXulps=%d endUlps=%d FromTime=%.17g ToTime=%.17g From=(%.17g,%.17g) Endpoint=(%.17g,%.17g) R2=%.17g actualNativeInside=1 originalWideWake=%.17g checked=%d"),
                    Construction,InitialXUlps,EndUlps,Begin,End,From.X,From.Y,ActualEndpoint.X,ActualEndpoint.Y,R2(ActualEndpoint),PreviewWake,LegalShortIntervals));
                // Precise expected baseline semantic RED after all real legal
                // prerequisites. Production must keep every matrix case and pass.
                return TestTrue(TEXT("Actual legal replanned interval must be accepted; no zero-progress rejection at rounded ellipse entry"),N.Accepted);
            }
            const auto& S=Narrow.State();
            if(!TestTrue(TEXT("Every accepted short interval reaches exact endpoint with one one-second native Wake and unchanged HP/receipts"),
                S.Time==End&&S.WakeStartedAt>Begin&&S.WakeStartedAt<=End&&S.WakeEnd==S.WakeStartedAt+1.
                &&S.Phase==Guard::EPhase::Waking&&Count(S,Guard::EEventKind::WakeStarted)==1&&S.Issued.size()==1
                &&S.HP==185.&&S.ReceivedHits.empty()&&S.HitReceipts.empty()&&S.Windows.empty()&&S.Action.AttackId==0
                &&S.InitialTime==Begin&&S.EntityId==W.Owner->GetRuntimeEntityId()&&S.InitialPosition.X==-800.&&S.InitialPosition.Y==-160.))return false;
            const double Prior=std::nextafter(S.WakeStartedAt,Begin);
            if(!TestTrue(TEXT("Accepted wake point satisfies actual native NearWake; preceding representable time remains outside without epsilon"),
                NativeInside(S.WakeStartedAt,At(Frame,S.WakeStartedAt))&&!NativeInside(Prior,At(Frame,Prior))))return false;
        }
        if(!TestTrue(TEXT("Every wider control must supply a nonempty real legal short-endpoint matrix; no empty search passes"),ThisWideLegal>=16))return false;
        if(Construction==0&&InitialXUlps==-2)
        {
            const double OriginalWakeEnd=Wide.State().WakeEnd;
            const auto HoldFrame=W.Frame(Wide.State().Time,OriginalWakeEnd-.01,WideFrame.Bodies[0].End,WideFrame.Bodies[0].End);
            if(!TestTrue(TEXT("The original full one-second warning still holds, with no second Wake or early Active"),
                Wide.StepTo(HoldFrame.ToTime,HoldFrame).Accepted&&Wide.State().Phase==Guard::EPhase::Waking
                &&Wide.State().WakeEnd==OriginalWakeEnd&&Count(Wide.State(),Guard::EEventKind::WakeStarted)==1&&Wide.State().Windows.empty()))return false;
            auto Queued=W.Driver(Begin);Queued.BeginCombat();auto GatedFrame=WideFrame;GatedFrame.bCanBeginWake=false;
            if(!TestTrue(TEXT("Original whole-room gate queues real entry without starting, rejecting or inventing a receipt"),
                Queued.StepTo(WideEnd,GatedFrame).Accepted&&Queued.State().WakeQueued&&Queued.State().WakeStartedAt<0.
                &&Queued.State().Phase==Guard::EPhase::Dormant&&Queued.State().HP==185.&&Queued.State().Issued.empty()))return false;
        }
    }
    TestTrue(TEXT("Both real construction paths and all nearby valid short intervals were exercised"),WideIntervals==10&&LegalShortIntervals>=160);
    TestTrue(TEXT("Driver previews never mutate owner actor or root clock"),W.Owner->Health==185.&&W.Owner->GetGroundPosition()==FVector2D(-800.,-160.)&&W.Game->GetSimulationTime()==0.);
    // Exact actual-native outside neighbor remains Dormant. Construct outside
    // geometrically; only the production predicate decides the final premise.
    FVector2D Outside(-1035.4682208563124,-162.2042858545901);
    if(!TestTrue(TEXT("Unchanged production predicate confirms stationary outside near-miss premise"),!NativeInside(Begin,Outside)))return false;
    auto Miss=W.Driver(Begin);Miss.BeginCombat();const auto MissFrame=W.Frame(Begin,WideEnd,Outside,Outside);
    TestTrue(TEXT("Outside legal interval advances Dormant with no invented Wake/HP/event"),
        Miss.StepTo(WideEnd,MissFrame).Accepted&&Miss.State().Time==WideEnd&&Miss.State().Phase==Guard::EPhase::Dormant
        &&Miss.State().WakeStartedAt<0.&&Miss.State().Issued.empty()&&Miss.State().HP==185.);
    return true;
}
#endif
