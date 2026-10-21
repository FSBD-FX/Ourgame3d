#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include <cmath>

namespace
{
namespace SocketWA=DungeonWeaponActions;
namespace SocketPose=DungeonWeaponPoseSocket;
bool SocketNear(double A,double B,double T=1.e-7){return std::abs(A-B)<=T;}

struct FSocketActorWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;FAutomationTestBase* Test=nullptr;
    explicit FSocketActorWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FSocketActorWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage){Test->AddError(FString::Printf(TEXT("Pose socket fixture failed at %s"),Stage));return false;}
    bool Create(double Ammo=1.)
    {
        if(!GEngine)return Fail(TEXT("engine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("world"));GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("authority"));Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return Fail(TEXT("actors"));
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||UGameplayStatics::GetPlayerController(Game,0)!=Controller)return Fail(TEXT("registered controller"));
        Game->bWaitingForStart=false;Game->bGameOver=false;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("real bound run"));
        DungeonEquipmentInventory::FItem Item;Item.ContentId="WPN-XBW-001";Item.Ammo=Ammo;
        const auto Source=Game->RegisterEquipmentSource(TEXT("qa.pose-socket.xbw"),Item,{40,0});
        if(!Source.Ok()||!Pulse(EKeys::E))return Fail(TEXT("normal E source"));
        const auto& Pickup=Game->GetEquipmentView().Action;
        if(!Pickup.Active||!AdvanceTo(Pickup.Deadline))return Fail(TEXT("real pickup deadline"));
        if(!Player->IsEquipmentBound()||Player->WeaponId!=TEXT("WPN-XBW-001")
            ||Actions().EquippedId!=Source.InstanceId||!Instance()||Instance()->Ammo!=Ammo)return Fail(TEXT("bound source identity"));
        return true;
    }
    const SocketWA::FState& Actions()const{return Player->GetWeaponActionsState();}
    const SocketWA::FInstance* Instance()const
    {for(const auto& I:Actions().Instances)if(I.InstanceId==Actions().EquippedId)return &I;return nullptr;}
    const SocketWA::FEvent* Emission(uint64 ActionId)const
    {for(const auto& E:Actions().Issued)if(E.ActionId==ActionId&&E.Kind==SocketWA::EEvent::ProjectileEmitted)return &E;return nullptr;}
    bool Key(FKey K,bool Down)
    {
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);return Controller->IsInputKeyDown(K)==Down;
    }
    void Frame(float Dt)
    {Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);}
    bool Pulse(FKey K){if(!Key(K,true))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
        for(int32 I=0;I<64&&Game->GetSimulationTime()<At;++I)
        {
            const double Before=Game->GetSimulationTime(),Remaining=At-Before;float Dt=float(Remaining);
            if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);if(!(Dt>0))return false;
            Frame(Dt);if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonPoseSocketCurrentPrimary,
    "CodexDungeon.Content.WeaponPoseSocketIntegration.PrimaryUsesCurrentActorAndAcceptedPhase",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonPoseSocketCurrentPrimary::RunTest(const FString&)
{
    FSocketActorWorld F(this);if(!TestTrue(TEXT("Real source/controller setup"),F.Create()))return false;
    if(!TestTrue(TEXT("Normal J accepts genuine loaded crossbow action"),F.Pulse(EKeys::J)&&F.Actions().Action.Active))return false;
    const auto A=F.Actions().Action;const auto Initial=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("Normal D moves during unlocked windup"),F.Key(EKeys::D,true)))return false;
    F.Frame(.02f);if(!F.Key(EKeys::D,false))return false;
    const auto Moved=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("Actual position moved and action identity is unchanged"),Moved.X>Initial.X&&F.Actions().Action.ActionId==A.ActionId))return false;
    if(!TestTrue(TEXT("Reach actual emission endpoint"),F.AdvanceTo(A.ActiveAt)))return false;
    const auto* Issued=F.Emission(A.ActionId);
    if(!TestTrue(TEXT("Existing real kernel/world emission prerequisites"),Issued&&Issued->AtTime==A.ActiveAt
        &&Issued->InstanceId==A.InstanceId&&Issued->SubhitId==0&&F.Instance()->Ammo==0
        &&F.Game->GetWeaponWorldState().Projectiles.Num()==1))return false;
    const auto E=*Issued;const auto* Snapshot=F.Player->FindWeaponEmissionPoseSocket(A.ActionId);
    if(!TestNotNull(TEXT("Actor retains actual pre-spend emission socket"),Snapshot))return false;
    const auto P=*Snapshot;const auto Current=F.Player->GetWeaponPoseSocket();const auto XY=F.Player->GetGroundPosition();
    // Frozen primary frame2 emit is independently measured in import79fd2508.
    // 120/512 maps source to logical pixels, then /0.65 maps logical X to world cm.
    const double ExpectedX=XY.X+(423.5311940307165-256.)*(120./512.)/.65;
    const double ExpectedHeight=(472.-224.3741693502523)*(120./512.)/.7;
    TestTrue(TEXT("Actor admits native active frame2 at the exact accepted emission clock"),P.Supported&&!P.CustomOverride
        &&P.Clip==SocketPose::EClip::Primary&&P.Frame==2&&P.SampleTime==A.ActiveAt
        &&P.InstanceId==A.InstanceId&&P.ActionId==A.ActionId&&P.Facing==1.);
    TestTrue(TEXT("Actual emitted XY uses the current hand socket, never accepted-start feet"),SocketNear(E.Origin.X,ExpectedX)
        &&SocketNear(E.Origin.Y,XY.Y)&&SocketNear(P.CombatOrigin.X,E.Origin.X)&&SocketNear(P.CombatOrigin.Y,E.Origin.Y));
    TestTrue(TEXT("Ground combat height stays zero while native hand presentation is elevated"),E.Origin.Height==0.
        &&P.CombatOrigin.Height==0.&&SocketNear(P.PresentationOrigin.X,E.Origin.X)
        &&SocketNear(P.PresentationOrigin.Y,E.Origin.Y)&&SocketNear(P.PresentationOrigin.Height,ExpectedHeight));
    const auto Component=F.Player->GetWeaponMuzzleComponent()->GetComponentLocation();
    TestTrue(TEXT("Post-emission real component is current empty0, independently of frozen neutral shot"),P.WeaponStateIndex==-1
        &&Current.WeaponStateIndex==0&&SocketNear(Current.EmitX,429.06255345651954)&&SocketNear(Current.EmitY,229.980044783978)
        &&SocketNear(Component.X,Current.PresentationOrigin.X)&&SocketNear(Component.Y,Current.PresentationOrigin.Y)
        &&SocketNear(Component.Z,Current.PresentationOrigin.Height));
    const auto Flight=F.Game->GetWeaponWorldState().Projectiles[0];
    TestTrue(TEXT("Frozen Actor anchor deducts the independently measured forward mouth from external range"),Flight.UsesActorRangeAnchor
        &&SocketNear(Flight.RangeAnchor.X,XY.X)&&SocketNear(Flight.RangeAnchor.Y,XY.Y)
        &&SocketNear(Flight.LaunchForwardDistance,(423.5311940307165-256.)*120./512./.65));
    const double RangeEnd=E.AtTime+(420.-Flight.LaunchForwardDistance)/950.;
    if(!F.AdvanceTo(std::nextafter(RangeEnd,E.AtTime)))return false;
    TestTrue(TEXT("External flight remains active at the last representable instant before its remaining range ends"),F.Game->GetWeaponWorldState().Projectiles[0].Active);
    if(!F.AdvanceTo(RangeEnd))return false;
    const auto& Stopped=F.Game->GetWeaponWorldState().Projectiles[0];
    const FDungeonWorldWeaponEvent* RangeStop=nullptr;
    for(const auto& Event:F.Game->GetWeaponWorldState().Events)if(Event.Kind==EDungeonWorldWeaponEventKind::ProjectileStopped)RangeStop=&Event;
    TestTrue(TEXT("Exact external range endpoint stops once at Actor420 without borrowing the forward60.41cm"),!Stopped.Active
        &&Stopped.Stop==EDungeonWorldProjectileStop::Range&&!Stopped.LaunchObstructed&&RangeStop&&RangeStop->AtTime==RangeEnd
        &&SocketNear(Stopped.Traveled,420.-Flight.LaunchForwardDistance)&&SocketNear(Stopped.Position.X,XY.X+420.)
        &&SocketNear(Stopped.Position.Y,XY.Y)&&F.Actions().Issued.size()==1&&F.Instance()->Ammo==0.);
    // Separate actual K fixture: ground skill uses the declared ready fallback
    // and its own real emission identity, not the primary animation counter.
    FSocketActorWorld Skill(this);if(!Skill.Create()||!Skill.Pulse(EKeys::K))return false;
    const auto K=Skill.Actions().Action;
    if(!TestTrue(TEXT("Normal K accepts the genuine crossbow skill"),K.Active&&K.Type==SocketWA::EAction::Skill))return false;
    if(!Skill.AdvanceTo(K.ActiveAt))return false;const auto* SkillEvent=Skill.Emission(K.ActionId);
    const auto* SkillPose=Skill.Player->FindWeaponEmissionPoseSocket(K.ActionId);
    TestTrue(TEXT("Skill freezes its own actual ready fallback mouth, ammo spend and action identity"),SkillEvent&&SkillPose
        &&SkillPose->Supported&&SkillPose->GroundPoseFallback&&SkillPose->Clip==SocketPose::EClip::Ready
        &&SkillPose->WeaponStateIndex==-1&&SkillPose->ActionId==K.ActionId&&SkillPose->SampleTime==SkillEvent->AtTime
        &&SocketNear(SkillPose->EmitX,395.40740934629025)&&SocketNear(SkillPose->EmitY,287.0306226992487)
        &&SocketNear(SkillEvent->Origin.X,Skill.Player->GetGroundPosition().X+(395.40740934629025-256.)*120./512./.65)
        &&SkillEvent->Origin.Height==0.&&Skill.Instance()->Ammo==0.&&Skill.Actions().Issued.size()==1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonPoseSocketClockAndReload,
    "CodexDungeon.Content.WeaponPoseSocketIntegration.ClockAndPendingReloadNeverCommitFromPose",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonPoseSocketClockAndReload::RunTest(const FString&)
{
    FSocketActorWorld F(this);if(!TestTrue(TEXT("Real clock/reload setup"),F.Create()))return false;
    if(!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
    if(!TestTrue(TEXT("Normal primary accepted before sampling"),A.Active&&A.Type==SocketWA::EAction::Primary))return false;
    const double Times[]={(A.Start+A.ActiveAt)*.5,A.ActiveAt,(A.ActiveAt+A.ActiveEnd)*.5,A.ActiveEnd,(A.ActiveEnd+A.End)*.5};
    const int Frames[]={1,2,3,4,5};
    for(int32 I=0;I<5;++I)
    {
        if(!TestTrue(TEXT("Reach genuine half-open phase sample"),F.AdvanceTo(Times[I])))return false;
        const auto Before=F.Actions();const auto P=F.Player->GetWeaponPoseSocket();
        for(int32 N=0;N<8;++N)F.Player->GetWeaponPoseSocket();
        TestTrue(FString::Printf(TEXT("Actual phase pose %d uses its own accepted clock"),I),P.Supported
            &&P.Clip==SocketPose::EClip::Primary&&P.Frame==Frames[I]&&P.SampleTime==Times[I]);
        TestTrue(TEXT("Readonly pose allocates no action/event/import/Focus or ammo receipt"),F.Actions().NextActionId==Before.NextActionId
            &&F.Actions().NextEventId==Before.NextEventId&&F.Actions().NextImportReceiptId==Before.NextImportReceiptId
            &&F.Actions().NextFocusMutationId==Before.NextFocusMutationId
            &&F.Actions().WeaponRuntimeHistory.size()==Before.WeaponRuntimeHistory.size());
    }
    if(!F.AdvanceTo(A.End))return false;const auto R=F.Actions().Action;
    if(!TestTrue(TEXT("Real empty instance starts full automatic reload after primary recovery"),R.Active
        &&R.Type==SocketWA::EAction::Reload&&R.Start==A.End&&SocketNear(R.End-R.Start,1.1)&&F.Instance()->Ammo==0))return false;
    const double Sample[]={.1,.4,.725,.975};
    const double EmitX[]={393.48933690844393,395.6988278143776,385.14028602652445,399.65331495751};
    const double EmitY[]={281.75100976363717,288.13924379537974,273.21958953005856,300.32525083826124};
    for(int32 I=0;I<4;++I)
    {
        const double At=R.Start+(R.End-R.Start)*(Sample[I]/1.1);
        if(!F.AdvanceTo(At))return false;const auto P=F.Player->GetWeaponPoseSocket();
        TestTrue(FString::Printf(TEXT("Reload source support-anchored pose %d inside actual normalized interval"),I),P.Supported
            &&P.Clip==SocketPose::EClip::Reload&&P.Frame==I&&P.SampleTime==At
            &&SocketNear(P.EmitX,EmitX[I])&&SocketNear(P.EmitY,EmitY[I]));
        TestTrue(TEXT("Visual insertion including stage3 cannot refill or issue a projectile"),F.Instance()->Ammo==0
            &&F.Actions().Issued.size()==1&&F.Game->GetWeaponWorldState().Projectiles.Num()==1);
    }
    if(!F.AdvanceTo(std::nextafter(R.End,R.Start)))return false;
    TestTrue(TEXT("Last representable reload instant remains empty"),F.Instance()->Ammo==0);
    if(!F.AdvanceTo(R.End))return false;const auto Ready=F.Player->GetWeaponPoseSocket();
    // Contract v00294f2: a real completion selects loaded3, not the old
    // neutral component. The actual80 RED version is preserved separately.
    TestTrue(TEXT("Only actual completion refills once and returns to loaded3 ready geometry"),F.Instance()->Ammo==1
        &&!F.Actions().Action.Active&&Ready.Supported&&Ready.Clip==SocketPose::EClip::Ready&&Ready.WeaponStateIndex==3
        &&Ready.ComponentGripX==138.&&Ready.ComponentGripY==274.
        &&SocketNear(Ready.EmitX,400.44488607361376)&&SocketNear(Ready.EmitY,292.86016900516665));

    // Newly admitted counterexample, not part of the actual80 RED evidence:
    // reload's unused default Action.Facing must not turn a real left shooter.
    FSocketActorWorld Left(this);if(!Left.Create()||!Left.Key(EKeys::A,true))return false;
    Left.Frame(.01f);if(!Left.Key(EKeys::A,false)||!Left.Pulse(EKeys::J))return false;
    const auto LeftShot=Left.Actions().Action;
    if(!TestTrue(TEXT("Normal A and J establish a real accepted left shot"),LeftShot.Active&&LeftShot.Facing==-1.
        &&Left.Player->Facing==-1.f))return false;
    if(!Left.AdvanceTo(LeftShot.End))return false;const auto LeftReload=Left.Actions().Action;
    if(!TestTrue(TEXT("Left primary fully recovers into a genuine automatic reload"),LeftReload.Active&&LeftReload.Type==SocketWA::EAction::Reload))return false;
    for(int32 I=0;I<4;++I)
    {
        if(!Left.AdvanceTo(LeftReload.Start+(LeftReload.End-LeftReload.Start)*(Sample[I]/1.1)))return false;
        const auto LeftPose=Left.Player->GetWeaponPoseSocket();
        TestTrue(FString::Printf(TEXT("Actual left reload stage %d preserves physical and socket facing"),I),Left.Player->Facing==-1.f
            &&LeftPose.Supported&&LeftPose.Facing==-1.&&LeftPose.Clip==SocketPose::EClip::Reload&&LeftPose.Frame==I);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonPoseSocketLifecycle,
    "CodexDungeon.Content.WeaponPoseSocketIntegration.RealReloadLifecycleSurvivesSwitchAndCancellation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonPoseSocketLifecycle::RunTest(const FString&)
{
    FSocketActorWorld F(this);if(!TestTrue(TEXT("Real lifecycle source/controller setup"),F.Create()))return false;
    if(!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
    if(!F.AdvanceTo(A.End))return false;const auto R=F.Actions().Action;
    if(!TestTrue(TEXT("Actual initial shot entered full reload"),R.Active&&R.Type==SocketWA::EAction::Reload&&F.Instance()->Ammo==0.))return false;
    if(!F.AdvanceTo(R.End))return false;
    if(!TestTrue(TEXT("Only real ReloadCompleted establishes loaded3 instance state"),F.Instance()->Ammo==1.
        &&F.Player->GetWeaponPoseSocket().WeaponStateIndex==3))return false;
    const auto LoadedInstance=F.Actions().EquippedId;
    if(!F.Pulse(EKeys::Q)||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline())
        ||!F.Pulse(EKeys::Q)||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    auto Current=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Real Q round trip retains the loaded3 state on the same instance"),F.Actions().EquippedId==LoadedInstance
        &&F.Instance()->Ammo==1.&&Current.WeaponStateIndex==3&&Current.Clip==SocketPose::EClip::Ready);
    if(!F.Pulse(EKeys::J))return false;const auto Second=F.Actions().Action;
    if(!F.AdvanceTo(Second.ActiveAt))return false;
    const auto* SecondEvent=F.Emission(Second.ActionId);const auto* SecondPose=F.Player->FindWeaponEmissionPoseSocket(Second.ActionId);
    Current=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Next true emission freezes loaded3 before spending, then current becomes empty0"),SecondEvent&&SecondPose
        &&SecondPose->WeaponStateIndex==3&&SecondPose->SampleTime==SecondEvent->AtTime
        &&SocketNear(SecondPose->EmitX,429.06255345651954)&&SocketNear(SecondPose->EmitY,229.980044783978)
        &&SocketNear(SecondEvent->Origin.X,SecondPose->CombatOrigin.X)&&Current.WeaponStateIndex==0
        &&F.Instance()->Ammo==0.&&F.Actions().Issued.size()==2);
    if(!F.AdvanceTo(Second.End))return false;const auto CancelReload=F.Actions().Action;
    if(!TestTrue(TEXT("Second actual empty-shot recovery starts another real reload"),CancelReload.Active&&CancelReload.Type==SocketWA::EAction::Reload))return false;
    if(!F.AdvanceTo(CancelReload.Start+(CancelReload.End-CancelReload.Start)*(.95/1.1)))return false;
    Current=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Stage3 cosmetic bolt is pending while actual instance remains empty"),Current.WeaponStateIndex==3
        &&Current.Clip==SocketPose::EClip::Reload&&F.Instance()->Ammo==0.);
    if(!F.Pulse(EKeys::T))return false;Current=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Normal T cancel discards pending insertion without refund or loading"),!F.Actions().Action.Active
        &&F.Actions().Action.Terminal==SocketWA::EEvent::ReloadCancelled&&F.Instance()->Ammo==0.
        &&Current.Clip==SocketPose::EClip::Ready&&Current.WeaponStateIndex==0&&F.Actions().Issued.size()==2);
    if(!F.Pulse(EKeys::Q)||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline())
        ||!F.Pulse(EKeys::Q)||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    Current=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Switching after cancel preserves the same empty0 instance and both original emissions"),F.Actions().EquippedId==LoadedInstance
        &&F.Instance()->Ammo==0.&&Current.WeaponStateIndex==0&&F.Actions().Issued.size()==2
        &&F.Player->FindWeaponEmissionPoseSocket(A.ActionId)&&F.Player->FindWeaponEmissionPoseSocket(A.ActionId)->WeaponStateIndex==-1
        &&F.Player->FindWeaponEmissionPoseSocket(Second.ActionId)&&F.Player->FindWeaponEmissionPoseSocket(Second.ActionId)->WeaponStateIndex==3);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonPoseSocketResourceAndSwitch,
    "CodexDungeon.Content.WeaponPoseSocketIntegration.EmptyAndSwitchCannotRetainAnotherInstanceSocket",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonPoseSocketResourceAndSwitch::RunTest(const FString&)
{
    FSocketActorWorld F(this);if(!TestTrue(TEXT("Explicit empty genuine crossbow source"),F.Create(0.)))return false;
    const auto Before=F.Actions();const uint64 Instance=Before.EquippedId;
    if(!F.Pulse(EKeys::J)||!F.Pulse(EKeys::K))return false;
    TestTrue(TEXT("Empty normal J/K create no accepted attack, emission, ammo or Focus receipt"),!F.Actions().Action.Active
        &&F.Actions().NextActionId==Before.NextActionId&&F.Actions().NextEventId==Before.NextEventId
        &&F.Actions().NextFocusMutationId==Before.NextFocusMutationId&&F.Actions().Issued.empty()
        &&F.Game->GetWeaponWorldState().Events.IsEmpty()&&F.Instance()->Ammo==0.);
    auto P=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("An empty owned crossbow still has a read-only ready socket without granting ammo"),P.Supported
        &&P.Clip==SocketPose::EClip::Ready&&P.InstanceId==Instance&&P.ActionId==0);
    if(!TestTrue(TEXT("Normal Q accepts a real .35 switch transaction"),F.Pulse(EKeys::Q)&&F.Game->GetEquipmentView().Action.Active))return false;
    if(!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    P=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Actual SWD equip rejects stale crossbow pose and stale instance"),F.Player->WeaponId==TEXT("WPN-SWD-001")
        &&!P.Supported&&P.InstanceId==F.Actions().EquippedId&&P.InstanceId!=Instance);
    if(!F.Pulse(EKeys::Q)||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    P=F.Player->GetWeaponPoseSocket();
    TestTrue(TEXT("Normal switch back restores the same empty instance socket with no replay"),F.Actions().EquippedId==Instance
        &&F.Instance()->Ammo==0.&&P.Supported&&P.InstanceId==Instance&&P.Clip==SocketPose::EClip::Ready
        &&F.Actions().Issued.empty()&&F.Game->GetWeaponWorldState().Events.IsEmpty());
    return true;
}
#endif
