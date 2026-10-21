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
namespace GuardWakeEntryV003
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
{return F.Bodies[0].Start+(F.Bodies[0].End-F.Bodies[0].Start)*((T-F.FromTime)/(F.ToTime-F.FromTime));}
int Count(const Guard::FState& S,Guard::EEventKind Kind){int N=0;for(const auto& E:S.Issued)N+=E.Kind==Kind;return N;}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonGuardWakeRoundedEntryReplannedEndpoint,
 "CodexDungeon.Content.StoneGuardNative.WakeEntryReplannedEndpointNeverRejectsLegalInterval",
 EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonGuardWakeRoundedEntryReplannedEndpoint::RunTest(const FString& Parameters)
{
    (void)Parameters;using namespace GuardWakeEntryV003;FWorld W(*this);if(!W.Create())return false;
    // Original PID55804: last Dormant t9.600689999759197, P=(-1036.8992209173477,-162.2042858545901).
    // Its next5ms batch commits this From. EarliestContact previews the wider next5ms,
    // then recomputes player endpoint at this first wake time. Both are legal observations.
    constexpr double Begin=9.605689999759198,WideEnd=9.610689999759199,ReplannedEnd=9.607490869337335;
    const FVector2D From(-1035.4682208563124,-162.2042858545901);
    const double Speed=double(float(286.2));
    auto WideFrame=W.Frame(Begin,WideEnd,From,From+FVector2D(Speed*(WideEnd-Begin),0.));
    auto NarrowFrame=W.Frame(Begin,ReplannedEnd,From,From+FVector2D(Speed*(ReplannedEnd-Begin),0.));
    if(!TestTrue(TEXT("Independent positive premise: real path begins outside and replanned endpoint inside unchanged235x110 ellipse"),
        R2(From)>1.&&R2(NarrowFrame.Bodies[0].End)<=1.&&Begin<ReplannedEnd&&ReplannedEnd<WideEnd))return false;
    auto Wide=W.Driver(Begin),Narrow=W.Driver(Begin);
    if(!Wide.BeginCombat()||!Narrow.BeginCombat())return false;
    const auto Before=Narrow.Capture();const auto B=Wide.StepTo(WideEnd,WideFrame);
    if(!TestTrue(TEXT("Original wider native-driver preview accepts real continuous wake entry"),B.Accepted))return false;
    const auto N=Narrow.StepTo(ReplannedEnd,NarrowFrame);
    // Stage0 semantic RED: baseline loops at rounded outside root and returns !Accepted.
    // No ensure suppression/AddExpectedError: the test calls the actual driver directly.
    if(!TestTrue(TEXT("Replanned legal endpoint must be accepted; rounded analytic entry must not collapse Next to Cursor"),N.Accepted))return false;
    const auto& S=Narrow.State();
    TestTrue(TEXT("Accepted driver reaches exact endpoint and wakes exactly once without a receipt or actor mutation"),
        S.Time==ReplannedEnd&&S.WakeStartedAt>Begin&&S.WakeStartedAt<=ReplannedEnd&&S.WakeEnd==S.WakeStartedAt+1.
        &&S.Phase==Guard::EPhase::Waking&&Count(S,Guard::EEventKind::WakeStarted)==1&&S.Issued.size()==1
        &&S.HP==185.&&S.ReceivedHits.empty()&&S.HitReceipts.empty()&&S.Windows.empty()&&S.Action.AttackId==0
        &&W.Owner->Health==185.&&W.Owner->GetGroundPosition()==FVector2D(-800.,-160.)&&W.Game->GetSimulationTime()==0.);
    const auto Prior=std::nextafter(S.WakeStartedAt,Begin);
    TestTrue(TEXT("First actual representable legal sample; preceding representable time remains outside, no epsilon admits an early wake"),
        R2(At(NarrowFrame,S.WakeStartedAt))<=1.&&R2(At(NarrowFrame,Prior))>1.);
    TestTrue(TEXT("Wider preview and shorter committed driver preserve the same one-second warning and initial identity"),
        Wide.State().WakeStartedAt==S.WakeStartedAt&&Wide.State().WakeEnd==S.WakeEnd&&S.InitialTime==Before.InitialTime
        &&S.EntityId==Before.EntityId&&S.InitialPosition.X==Before.InitialPosition.X&&S.NextAttackId==Before.NextAttackId);
    const auto HoldFrame=W.Frame(S.Time,S.WakeEnd-.01,NarrowFrame.Bodies[0].End,NarrowFrame.Bodies[0].End);
    const double OriginalWakeEnd=S.WakeEnd;
    TestTrue(TEXT("Native warning still lasts its original full second; no duplicate wake or early Active"),
        Narrow.StepTo(HoldFrame.ToTime,HoldFrame).Accepted&&Narrow.State().Phase==Guard::EPhase::Waking
        &&Narrow.State().WakeEnd==OriginalWakeEnd&&Count(Narrow.State(),Guard::EEventKind::WakeStarted)==1&&Narrow.State().Windows.empty());
    // Neighboring stationary outside path is accepted without waking. This guards
    // against an epsilon/forced-Wake repair that would pass only the positive case.
    FVector2D Outside(-1034.9528119610668,-162.2042858545901);
    Outside.X=std::nextafter(Outside.X,-std::numeric_limits<double>::infinity());
    if(!TestTrue(TEXT("Exact outside-neighbor premise"),R2(Outside)>1.))return false;
    auto Miss=W.Driver(Begin);Miss.BeginCombat();const auto MissFrame=W.Frame(Begin,WideEnd,Outside,Outside);
    TestTrue(TEXT("Legal outside near miss advances unchanged Dormant with no fabricated Wake/HP/event"),
        Miss.StepTo(WideEnd,MissFrame).Accepted&&Miss.State().Time==WideEnd&&Miss.State().Phase==Guard::EPhase::Dormant
        &&Miss.State().WakeStartedAt<0.&&Miss.State().Issued.empty()&&Miss.State().HP==185.);
    // Queue eligibility remains owned by the native kernel/whole-room warning gate.
    auto Queued=W.Driver(Begin);Queued.BeginCombat();auto GatedFrame=NarrowFrame;GatedFrame.bCanBeginWake=false;
    TestTrue(TEXT("Existing whole-room gate can queue the same real entry without starting or rejecting it"),
        Queued.StepTo(ReplannedEnd,GatedFrame).Accepted&&Queued.State().WakeQueued&&Queued.State().WakeStartedAt<0.
        &&Queued.State().Phase==Guard::EPhase::Dormant&&Queued.State().HP==185.&&Queued.State().Issued.empty());
    return true;
}
#endif
