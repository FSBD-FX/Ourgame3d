#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonWeaponPoseSocket.h"
#include "../DungeonWorldProjectiles.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "CollisionQueryParams.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include <cmath>

namespace
{
namespace SocketWA = DungeonWeaponActions;
namespace SocketPose = DungeonWeaponPoseSocket;
using SocketWorldEvent = EDungeonWorldWeaponEventKind;

// Independent expected geometry from the frozen native primary frame2 markers,
// not a call to the socket resolver under test. Ground projection is .65/.38;
// combat height is the real jump plane, separately from native image height.
constexpr double SocketPrimaryEmitX = 423.5311940307165;
constexpr double SocketPrimaryEmitY = 224.3741693502523;
constexpr double SocketPrimaryWorldX = (SocketPrimaryEmitX-256.)*120./512./.65;
constexpr double SocketPrimaryVisualHeight = (472.-SocketPrimaryEmitY)*120./512./.70;
constexpr double SocketEmptyPrimaryEmitX = 429.06255345651954;
constexpr double SocketEmptyPrimaryEmitY = 229.980044783978;
constexpr double SocketEmptyPrimaryWorldX = (SocketEmptyPrimaryEmitX-256.)*120./512./.65;
constexpr double SocketEmptyReadyEmitX = 400.44488607361376;
constexpr double SocketEmptyReadyEmitY = 292.86016900516665;
bool SocketNear(double A,double B,double Tolerance=1.e-5)
{ return std::abs(A-B)<=Tolerance; }

struct FSocketReviewWorld
{
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    FAutomationTestBase* Test=nullptr;
    uint64 AcquiredInstance=0;
    explicit FSocketReviewWorld(FAutomationTestBase* InTest):Test(InTest) {}
    ~FSocketReviewWorld()
    { if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);} }
    bool Fail(const TCHAR* Stage)
    {
        Test->AddError(FString::Printf(TEXT("Pose-socket real fixture '%s' failed; Equipment=%s"),Stage,
            Game?*Game->GetEquipmentView().FailureText:TEXT("No GameMode")));
        return false;
    }
    bool Key(FKey K,bool Down)
    {
        if(!Controller||!Controller->PlayerInput)return false;
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(K)==Down;
    }
    void Frame(float Delta)
    {
        Game->Tick(Delta);
        Controller->PlayerInput->Tick(Delta);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,Delta,false);
    }
    bool Pulse(FKey K)
    { if(!Key(K,true))return false;Frame(.005f);return Key(K,false); }
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
        for(int32 N=0;N<40&&Game->GetSimulationTime()<At;++N)
        {
            const double Remaining=At-Game->GetSimulationTime();float Step=float(Remaining);
            if(double(Step)>Remaining)Step=std::nextafter(Step,0.f);
            if(!(Step>0.f))return Fail(TEXT("Nonpositive exact clock step"));
            const double Before=Game->GetSimulationTime();Frame(Step);
            if(Game->GetSimulationTime()<=Before)return Fail(TEXT("Clock stalled"));
        }
        return Game->GetSimulationTime()==At;
    }
    bool Create()
    {
        if(!GEngine)return Fail(TEXT("GEngine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("CreateWorld"));
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));
        FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("SetGameMode"));
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
        Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return Fail(TEXT("Spawn actors"));
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||Player->GetController()!=Controller)return Fail(TEXT("Real local input controller"));
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        Game->bWaitingForStart=false;Game->bGameOver=false;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("Bound Run"));
        DungeonEquipmentInventory::FItem I;I.ContentId="WPN-XBW-001";I.Ammo=1;
        const auto Source=Game->RegisterEquipmentSource(TEXT("qa.pose-socket.xbw"),I,{40,0});
        if(!Source.Ok()||!Game->SelectEquipmentSource(Source.SourceId))return Fail(TEXT("Registered loaded source"));
        AcquiredInstance=Source.InstanceId;
        if(!Pulse(EKeys::E)||!Game->GetEquipmentView().Action.Active)return Fail(TEXT("Actual fresh E pickup"));
        if(!AdvanceTo(Player->GetEquipmentActionDeadline()))return Fail(TEXT("Pickup deadline"));
        return Player->IsEquipmentBound()&&Player->WeaponId==TEXT("WPN-XBW-001")
            &&Actions().EquippedId==AcquiredInstance&&Game->GetEquipmentView().Slots[1].InstanceId==AcquiredInstance;
    }
    bool Face(double Facing)
    {
        const FKey K=Facing<0?EKeys::A:EKeys::D;
        if(!Key(K,true))return false;Frame(.01f);
        return Key(K,false)&&Player->Facing==Facing;
    }
    const SocketWA::FState& Actions() const{return Player->GetWeaponActionsState();}
    const FDungeonWeaponWorldState& State() const{return Game->GetWeaponWorldState();}
    const SocketWA::FInstance* Instance() const
    {for(const auto& I:Actions().Instances)if(I.InstanceId==Actions().EquippedId)return &I;return nullptr;}
    const SocketWA::FEvent* Issued(uint64 Id) const
    {for(const auto& E:Actions().Issued)if(E.ActionId==Id)return &E;return nullptr;}
    int32 Events(SocketWorldEvent Kind) const
    {int32 N=0;for(const auto& E:State().Events)if(E.Kind==Kind)++N;return N;}
    const FDungeonWorldWeaponEvent* Event(SocketWorldEvent Kind,uint64 Target=0) const
    {for(const auto& E:State().Events)if(E.Kind==Kind&&(!Target||E.TargetId==Target))return &E;return nullptr;}
    ADungeonFighter* Target(FVector2D Position,float InitialHP=1000.f)
    {
        auto T=World->SpawnActor<ADungeonFighter>();if(!T)return nullptr;
        T->SetActorTickEnabled(false);T->bEnemy=true;T->bAIEnabled=false;T->MaxHealth=InitialHP;
        T->ResetFighter(Position);Game->Enemies.Add(T);return T;
    }
    AActor* Wall(FVector2D Position)
    {
        auto A=World->SpawnActor<AActor>();if(!A)return nullptr;
        auto B=NewObject<UBoxComponent>(A);A->SetRootComponent(B);B->SetBoxExtent({4,45,80});
        B->SetCollisionEnabled(ECollisionEnabled::QueryOnly);B->SetCollisionObjectType(ECC_WorldStatic);
        B->SetCollisionResponseToAllChannels(ECR_Block);B->RegisterComponentWithWorld(World);
        A->SetActorLocation({Position.X,Position.Y,0});return A;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketNativeEndpointReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.NativePrimaryEmissionSamplesEndpointAndMirrorsOnce",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketNativeEndpointReview::RunTest(const FString& Parameters)
{
    for(const double Facing:{1.,-1.})
    {
        FSocketReviewWorld F(this);if(!TestTrue(TEXT("Actual E obtains authored one-bolt XBW"),F.Create()))return false;
        if(!TestTrue(TEXT("Facing comes from real directional input"),F.Face(Facing)))return false;
        const auto BeforeDraw=F.Game->GetEquipmentView().NextCritDraw;
        if(!TestTrue(TEXT("Fresh J input delivered"),F.Pulse(EKeys::J)))return false;
        const auto A=F.Actions().Action;
        if(!TestTrue(TEXT("Actual bound primary accepted"),A.Active&&A.Type==SocketWA::EAction::Primary
            &&A.InstanceId==F.AcquiredInstance&&A.Facing==Facing))return false;
        if(!F.AdvanceTo(A.ActiveAt))return false;
        const auto* Actual=F.Issued(A.ActionId);if(!TestNotNull(TEXT("Real WA projectile issued before socket assertions"),Actual))return false;
        const auto E=*Actual;const auto* EmissionPose=F.Player->FindWeaponEmissionPoseSocket(A.ActionId);
        if(!TestNotNull(TEXT("Actual pre-spend immutable emission socket"),EmissionPose))return false;
        const auto P=*EmissionPose;const auto Current=F.Player->GetWeaponPoseSocket();const auto XY=F.Player->GetGroundPosition();
        TestTrue(TEXT("Native socket is an Actor-owned actual primary frame2 at precise emission"),
            P.Supported&&!P.CustomOverride&&!P.GroundPoseFallback&&P.WeaponStateIndex==-1&&P.Clip==SocketPose::EClip::Primary&&P.Frame==2
            &&P.SampleTime==E.AtTime&&P.SampleTime==A.ActiveAt&&P.ActionId==A.ActionId
            &&P.InstanceId==F.AcquiredInstance&&P.Facing==Facing);
        TestTrue(TEXT("Frozen native root, grip and emitter are real frame2 geometry"),
            P.RootX==256&&P.RootY==472&&P.BodySize==120&&P.GripX==255&&P.GripY==267
            &&SocketNear(P.EmitX,SocketPrimaryEmitX)&&SocketNear(P.EmitY,SocketPrimaryEmitY));
        TestTrue(TEXT("Actual projectile uses forward hand socket XY with a single X mirror and ground combat height"),
            SocketNear(E.Origin.X,XY.X+Facing*SocketPrimaryWorldX)&&SocketNear(E.Origin.Y,XY.Y)
            &&E.Origin.Height==0&&SocketNear(P.CombatOrigin.X,E.Origin.X)
            &&SocketNear(P.CombatOrigin.Y,E.Origin.Y)&&P.CombatOrigin.Height==E.Origin.Height);
        TestTrue(TEXT("Presentation socket has its own hand height and the same actual world XY"),
            SocketNear(P.PresentationOrigin.X,E.Origin.X)&&SocketNear(P.PresentationOrigin.Y,E.Origin.Y)
            &&SocketNear(P.PresentationOrigin.Height,SocketPrimaryVisualHeight)&&P.PresentationOrigin.Height>65);
        const auto Physical=F.Player->GetWeaponMuzzleComponent()->GetComponentLocation();
        TestTrue(TEXT("Current empty0 is independently resolved after real spend, without pretending to be the historical neutral mouth"),
            Current.Supported&&!Current.CustomOverride&&Current.WeaponStateIndex==0&&Current.Frame==2
            &&Current.SampleTime==E.AtTime&&SocketNear(Current.EmitX,SocketEmptyPrimaryEmitX)&&SocketNear(Current.EmitY,SocketEmptyPrimaryEmitY)
            &&SocketNear(Current.CombatOrigin.X,XY.X+Facing*SocketEmptyPrimaryWorldX)&&SocketNear(Current.CombatOrigin.Y,XY.Y)
            &&Current.CombatOrigin.Height==0&&SocketNear(Current.PresentationOrigin.Height,(472.-SocketEmptyPrimaryEmitY)*120./512./.70));
        TestTrue(TEXT("Real current component and getter follow empty0 physical socket while combat height remains its jump plane"),
            SocketNear(Physical.X,Current.PresentationOrigin.X)&&SocketNear(Physical.Y,Current.PresentationOrigin.Y)
            &&SocketNear(Physical.Z,Current.PresentationOrigin.Height)&&F.Player->GetWeaponMuzzleOrigin().Height==0
            &&SocketNear(F.Player->GetWeaponMuzzleOrigin().X,Current.CombatOrigin.X)
            &&!SocketNear(Current.CombatOrigin.X,P.CombatOrigin.X));
        if(F.State().Projectiles.Num()==1)
        {
            const auto& World=F.State().Projectiles[0];const auto* Journal=F.Event(SocketWorldEvent::ProjectileEmitted);
            TestTrue(TEXT("World projectile and emission journal freeze real native socket and per-shot Actor range anchor"),
                World.HasPoseSocket&&World.PoseSocket.Supported&&World.PoseSocket.SampleTime==E.AtTime
                &&World.PoseSocket.Frame==2&&World.PoseSocket.ActionId==A.ActionId&&World.UsesActorRangeAnchor
                &&SocketNear(World.RangeAnchor.X,XY.X)&&SocketNear(World.RangeAnchor.Y,XY.Y)&&World.RangeAnchor.Height==0
                &&SocketNear(World.LaunchForwardDistance,SocketPrimaryWorldX)
                &&SocketNear(World.PoseSocket.PresentationOrigin.Height,SocketPrimaryVisualHeight)
                &&Journal&&Journal->HasPoseSocket&&Journal->PoseSocket.SampleTime==E.AtTime
                &&SocketNear(Journal->PoseSocket.CombatOrigin.X,E.Origin.X)&&SocketNear(Journal->RangeAnchor.X,XY.X));
        }
        TestTrue(TEXT("One real emission retains one ammo spend and one crit draw"),
            F.State().Projectiles.Num()==1&&F.Events(SocketWorldEvent::ProjectileEmitted)==1
            &&F.Instance()&&F.Instance()->Ammo==0&&F.Instance()->ReservedAmmo==0
            &&F.Game->GetEquipmentView().Slots[1].Ammo==0&&F.Game->GetEquipmentView().NextCritDraw==BeforeDraw+1);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketPublicOverrideReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.PublicComponentOverrideAndAuthoredReturnRemainReal",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketPublicOverrideReview::RunTest(const FString& Parameters)
{
    for(const double Facing:{1.,-1.})
    {
        FSocketReviewWorld F(this);if(!TestTrue(TEXT("Actual E source for public component authoring"),F.Create()))return false;
        if(!F.Face(Facing))return false;
        auto Component=F.Player->GetWeaponMuzzleComponent();if(!TestNotNull(TEXT("Public real muzzle component"),Component))return false;
        Component->SetRelativeLocation({24,7,0}); // Legal real authored override; no kernel capture/origin mutation.
        if(!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
        if(!TestTrue(TEXT("Custom component still admits actual J primary"),A.Active&&A.Type==SocketWA::EAction::Primary))return false;
        if(!F.AdvanceTo(A.ActiveAt))return false;
        const auto* Actual=F.Issued(A.ActionId);if(!TestNotNull(TEXT("Custom-origin real emission exists"),Actual))return false;
        const auto E=*Actual;const auto P=F.Player->GetWeaponPoseSocket();const auto XY=F.Player->GetGroundPosition();
        TestTrue(TEXT("Direct component authoring is observed as a general explicit override"),P.Supported&&P.CustomOverride
            &&P.SampleTime==A.ActiveAt&&P.InstanceId==F.AcquiredInstance&&P.ActionId==A.ActionId);
        TestTrue(TEXT("Authored component preserves the old24/7 contract and mirrors only its X once"),
            SocketNear(E.Origin.X,XY.X+Facing*24)&&SocketNear(E.Origin.Y,XY.Y+7)&&E.Origin.Height==0
            &&SocketNear(P.CombatOrigin.X,E.Origin.X)&&SocketNear(P.CombatOrigin.Y,E.Origin.Y));
        if(F.State().Projectiles.Num()==1)
        {
            const auto& World=F.State().Projectiles[0];
            TestTrue(TEXT("Custom projectile freezes custom origin-relative range semantics without native forward extension"),
                World.HasPoseSocket&&World.PoseSocket.CustomOverride&&!World.UsesActorRangeAnchor
                &&SocketNear(World.RangeAnchor.X,E.Origin.X)&&SocketNear(World.RangeAnchor.Y,E.Origin.Y));
        }
        const auto Before=F.Actions();const auto BeforeEvents=F.State().NextEventSequence;
        for(int32 N=0;N<8;++N){F.Player->GetWeaponPoseSocket();F.Player->GetWeaponMuzzleOrigin();}
        TestTrue(TEXT("Readonly socket observation cannot allocate or spend"),F.Actions().NextActionId==Before.NextActionId
            &&F.Actions().NextEventId==Before.NextEventId&&F.Instance()->Ammo==0&&F.State().NextEventSequence==BeforeEvents);
        F.Player->UseAuthoredWeaponPoseSocket();const auto Native=F.Player->GetWeaponPoseSocket();
        TestTrue(TEXT("Explicit authored return restores the current real empty0 frame2 socket without firing"),Native.Supported&&!Native.CustomOverride
            &&Native.Clip==SocketPose::EClip::Primary&&Native.Frame==2&&Native.SampleTime==A.ActiveAt
            &&Native.WeaponStateIndex==0&&SocketNear(Native.EmitX,SocketEmptyPrimaryEmitX)&&SocketNear(Native.EmitY,SocketEmptyPrimaryEmitY)
            &&SocketNear(Native.CombatOrigin.X,XY.X+Facing*SocketEmptyPrimaryWorldX)&&SocketNear(Native.CombatOrigin.Y,XY.Y)
            &&Native.CombatOrigin.Height==0&&F.Events(SocketWorldEvent::ProjectileEmitted)==1&&F.Instance()->Ammo==0);
        const auto* Unchanged=F.Issued(A.ActionId);
        TestTrue(TEXT("Returning to native socket cannot rewrite the already issued custom projectile"),Unchanged
            &&SocketNear(Unchanged->Origin.X,E.Origin.X)&&SocketNear(Unchanged->Origin.Y,E.Origin.Y)
            &&Unchanged->Origin.Height==E.Origin.Height&&F.State().Projectiles.Num()==1
            &&SocketNear(F.State().Projectiles[0].Source.Origin.X,E.Origin.X)
            &&SocketNear(F.State().Projectiles[0].Source.Origin.Y,E.Origin.Y)
            &&F.State().Projectiles[0].HasPoseSocket&&F.State().Projectiles[0].PoseSocket.CustomOverride
            &&SocketNear(F.State().Projectiles[0].PoseSocket.CombatOrigin.X,E.Origin.X));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketCombatHeightReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.RealJumpCombatHeightStaysSeparateFromPresentation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketCombatHeightReview::RunTest(const FString& Parameters)
{
    for(int32 Case=0;Case<2;++Case)
    {
        FSocketReviewWorld F(this);if(!TestTrue(TEXT("Bound real source for combat/presentation height"),F.Create()))return false;
        auto Target=F.Target({190,0});if(!Target)return false;
        if(Case==1)
        {
            if(!TestTrue(TEXT("Actual Space input starts a real jump"),F.Pulse(EKeys::SpaceBar)))return false;
            F.Frame(.195f);
            if(!TestTrue(TEXT("Physical player is high before airborne J"),F.Player->JumpHeight>65&&F.Player->GetVerticalVelocity()>0))return false;
        }
        if(!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
        if(!TestTrue(TEXT("Ground/air J accepted through the real WA action gate"),A.Active&&A.Type==SocketWA::EAction::Primary&&A.StartedAirborne==(Case==1)))return false;
        if(!F.AdvanceTo(A.ActiveAt))return false;
        const auto* Actual=F.Issued(A.ActionId);if(!TestNotNull(TEXT("Real emission before height contract assertions"),Actual))return false;
        const auto E=*Actual;const auto* EmissionPose=F.Player->FindWeaponEmissionPoseSocket(A.ActionId);
        if(!TestNotNull(TEXT("Actual ground/air pre-spend emission socket is preserved"),EmissionPose))return false;
        const auto P=*EmissionPose;const auto Current=F.Player->GetWeaponPoseSocket();
        TestTrue(TEXT("Combat emitter height is exactly the actual physical jump plane"),
            SocketNear(E.Origin.Height,F.Player->JumpHeight,.0001)&&SocketNear(P.CombatOrigin.Height,E.Origin.Height,.0001)
            &&(Case==0?E.Origin.Height==0:E.Origin.Height>65));
        const double ExpectedEmitY=Case==0?SocketPrimaryEmitY:287.0306226992487;
        TestTrue(TEXT("Hand presentation offset is independent and never substituted into combat65"),
            P.Supported&&P.WeaponStateIndex==-1&&P.SampleTime==E.AtTime
            &&SocketNear(P.EmitY,ExpectedEmitY)
            &&SocketNear(P.PresentationOrigin.Height,P.CombatOrigin.Height+(472.-ExpectedEmitY)*120./512./.70,.0001)
            &&P.PresentationOrigin.Height>P.CombatOrigin.Height
            &&SocketNear(P.PresentationOrigin.X,E.Origin.X)&&SocketNear(P.PresentationOrigin.Y,E.Origin.Y));
        const double CurrentEmitX=Case==0?SocketEmptyPrimaryEmitX:SocketEmptyReadyEmitX;
        const double CurrentEmitY=Case==0?SocketEmptyPrimaryEmitY:SocketEmptyReadyEmitY;
        const auto Physical=F.Player->GetWeaponMuzzleComponent()->GetComponentLocation();
        TestTrue(TEXT("Current ground/air empty0 physical socket uses its own94f geometry after spend without moving the frozen emission"),
            Current.Supported&&Current.WeaponStateIndex==0&&Current.SampleTime==E.AtTime
            &&SocketNear(Current.EmitX,CurrentEmitX)&&SocketNear(Current.EmitY,CurrentEmitY)
            &&SocketNear(Current.CombatOrigin.Height,E.Origin.Height,.0001)
            &&SocketNear(Current.CombatOrigin.X,F.Player->GetGroundPosition().X+(CurrentEmitX-256.)*120./512./.65)
            &&SocketNear(Current.PresentationOrigin.Height,E.Origin.Height+(472.-CurrentEmitY)*120./512./.70,.0001)
            &&SocketNear(Physical.X,Current.PresentationOrigin.X)&&SocketNear(Physical.Y,Current.PresentationOrigin.Y)
            &&SocketNear(Physical.Z,Current.PresentationOrigin.Height,.0001)
            &&!SocketNear(Current.CombatOrigin.X,P.CombatOrigin.X));
        const auto Frozen=F.State().Projectiles.Num()==1?F.State().Projectiles[0]:FDungeonWorldProjectile{};
        TestTrue(TEXT("World snapshot freezes actual emission socket instead of relying on future Actor/HUD state"),Frozen.HasPoseSocket
            &&Frozen.PoseSocket.Supported&&Frozen.PoseSocket.SampleTime==E.AtTime
            &&SocketNear(Frozen.PoseSocket.CombatOrigin.Height,E.Origin.Height,.0001)
            &&SocketNear(Frozen.PoseSocket.PresentationOrigin.Height,P.PresentationOrigin.Height,.0001));
        if(!F.AdvanceTo(A.Start+.65))return false;
        if(Case==0)
        {
            const auto* Hit=F.Event(SocketWorldEvent::DirectHitCommitted,Target->GetRuntimeEntityId());
            TestTrue(TEXT("Ground native hand socket still damages a ground enemy exactly once"),Target->Health<1000
                &&SocketNear(1000-Target->Health,E.Damage,.0002)&&F.Events(SocketWorldEvent::DirectHitCommitted)==1
                &&Hit&&Hit->HasPoseSocket&&Hit->PoseSocket.SampleTime==E.AtTime
                &&SocketNear(Hit->PoseSocket.PresentationOrigin.Height,P.PresentationOrigin.Height)
                &&F.State().HitReceipts.Num()==1&&F.State().HitReceipts[0].HasPoseSocket
                &&F.State().HitReceipts[0].PoseSocket.SampleTime==E.AtTime);
        }
        else
            TestTrue(TEXT("High emitted bolt keeps65 gate and never aims down to a ground enemy"),Target->Health==1000
                &&F.Events(SocketWorldEvent::DirectHitCommitted)==0);
        F.Frame(.9f);
        const auto* History=F.Issued(A.ActionId);
        TestTrue(TEXT("Landing and subsequent reload cannot move or lower the already issued source"),History
            &&History->AtTime==E.AtTime&&SocketNear(History->Origin.X,E.Origin.X)&&SocketNear(History->Origin.Y,E.Origin.Y)
            &&History->Origin.Height==E.Origin.Height&&F.State().Projectiles.Num()==1
            &&F.State().Projectiles[0].Source.Origin.Height==E.Origin.Height
            &&F.State().Projectiles[0].HasPoseSocket&&F.State().Projectiles[0].PoseSocket.SampleTime==E.AtTime
            &&SocketNear(F.State().Projectiles[0].PoseSocket.PresentationOrigin.Height,Frozen.PoseSocket.PresentationOrigin.Height)
            &&SocketNear(F.State().Projectiles[0].PoseSocket.CombatOrigin.X,Frozen.PoseSocket.CombatOrigin.X)
            &&F.State().Projectiles[0].RangeAnchor.Height==Frozen.RangeAnchor.Height
            &&F.Events(SocketWorldEvent::ProjectileEmitted)==1);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketLaunchAndRangeReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.NativeLaunchCannotSkipNearContactOrExtendActorRange",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketLaunchAndRangeReview::RunTest(const FString& Parameters)
{
    for(const double Facing:{1.,-1.})for(int32 Case=0;Case<4;++Case)
    {
        FSocketReviewWorld F(this);if(!TestTrue(TEXT("Real one-bolt source for native launch/range"),F.Create()))return false;
        if(!F.Face(Facing))return false;
        const auto Anchor=F.Player->GetGroundPosition();
        // Case0/1 straddle the unchanged Actor-relative420 center hard gate.
        // Case2/3 are inside the real Actor->hand launch segment, not behind
        // the actor and not a runtime position/HP edit.
        const double Forward=Case==0?419.999:Case==1?420.001:190.;
        auto Target=F.Target(Anchor+FVector2D(Facing*Forward,0));if(!Target)return false;
        ADungeonFighter* NearTarget=nullptr;
        if(Case==2&&!F.Wall(Anchor+FVector2D(Facing*50,0)))return false;
        if(Case==3){NearTarget=F.Target(Anchor+FVector2D(Facing*50,0));if(!NearTarget)return false;}
        if(!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
        if(!TestTrue(TEXT("Normal J admitted with real wall/nearbody fixture"),A.Active&&A.Type==SocketWA::EAction::Primary))return false;
        if(!F.AdvanceTo(A.ActiveAt))return false;
        const auto* Actual=F.Issued(A.ActionId);if(!TestNotNull(TEXT("Launch has a real issued emission"),Actual))return false;
        const auto E=*Actual;
        TestTrue(TEXT("Native source stays at actual forward hand mouth rather than moving back to the actor"),
            SocketNear(E.Origin.X,Anchor.X+Facing*SocketPrimaryWorldX)&&SocketNear(E.Origin.Y,Anchor.Y)&&E.Origin.Height==0);
        TestTrue(TEXT("The real per-emission range anchor preserves Actor420 while the source remains at the hand"),
            F.State().Projectiles.Num()==1&&F.State().Projectiles[0].HasPoseSocket&&F.State().Projectiles[0].UsesActorRangeAnchor
            &&SocketNear(F.State().Projectiles[0].RangeAnchor.X,Anchor.X)
            &&SocketNear(F.State().Projectiles[0].RangeAnchor.Y,Anchor.Y)
            &&SocketNear(F.State().Projectiles[0].LaunchForwardDistance,SocketPrimaryWorldX));
        if(Case>=2)
        {
            const auto* Stop=F.Event(SocketWorldEvent::ProjectileStopped);
            TestTrue(TEXT("Launch segment resolves first obstruction at the same emission timestamp exactly once"),
                F.State().Projectiles.Num()==1&&!F.State().Projectiles[0].Active&&Stop&&Stop->AtTime==E.AtTime
                &&F.State().Projectiles[0].LaunchObstructed&&F.State().Projectiles[0].Traveled==0
                &&Stop->LaunchObstructed&&Stop->HasPoseSocket&&Stop->PoseSocket.SampleTime==E.AtTime
                &&F.Events(SocketWorldEvent::ProjectileStopped)==1);
            if(Case==2)
                TestTrue(TEXT("A real WorldStatic wall between actor and forward mouth stops launch before the rear enemy"),
                    F.State().Projectiles.Num()==1&&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::Wall
                    &&F.Events(SocketWorldEvent::DirectHitCommitted)==0&&Target->Health==1000);
            else
            {
                const auto* Hit=F.Event(SocketWorldEvent::DirectHitCommitted,NearTarget->GetRuntimeEntityId());
                TestTrue(TEXT("MinRange0 does not skip a near body behind the forward mouth or hit the second body"),
                    Hit&&Hit->AtTime==E.AtTime&&SocketNear(1000-NearTarget->Health,E.Damage,.0002)
                    &&Hit->HasPoseSocket&&Hit->LaunchObstructed&&Hit->PoseSocket.SampleTime==E.AtTime
                    &&F.Events(SocketWorldEvent::DirectHitCommitted)==1&&Target->Health==1000
                    &&F.State().Projectiles.Num()==1&&F.State().Projectiles[0].Stop==EDungeonWorldProjectileStop::TargetLimit);
            }
        }
        if(!F.AdvanceTo(A.Start+.65))return false;
        if(Case==0)
            TestTrue(TEXT("Actor420 minus .001 remains a real legal once-only hit from the native mouth"),
                SocketNear(1000-Target->Health,E.Damage,.0002)&&F.Events(SocketWorldEvent::DirectHitCommitted)==1);
        else if(Case==1)
            TestTrue(TEXT("Actor420 plus .001 remains out of range even though the mouth moved forward"),
                Target->Health==1000&&F.Events(SocketWorldEvent::DirectHitCommitted)==0);
        else if(Case==2)
            TestTrue(TEXT("Blocked launch never reappears beyond the wall later"),Target->Health==1000
                &&F.Events(SocketWorldEvent::DirectHitCommitted)==0&&F.Events(SocketWorldEvent::ProjectileStopped)==1);
        else
            TestTrue(TEXT("Near launch contact never duplicates or proceeds to the farther body later"),Target->Health==1000
                &&SocketNear(1000-NearTarget->Health,E.Damage,.0002)&&F.Events(SocketWorldEvent::DirectHitCommitted)==1
                &&F.Events(SocketWorldEvent::ProjectileStopped)==1);
        TestTrue(TEXT("Every accepted launch spends its one real bolt once without a duplicate emission"),
            F.Instance()&&F.Instance()->Ammo==0&&F.Game->GetEquipmentView().Slots[1].Ammo==0
            &&F.Events(SocketWorldEvent::ProjectileEmitted)==1&&F.State().Projectiles.Num()==1);
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketLaunchWallTieReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.ExactLaunchWallBodyTieStopsAtWall",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketLaunchWallTieReview::RunTest(const FString& Parameters)
{
    for(const double Facing:{1.,-1.})
    {
        FSocketReviewWorld F(this);
        if(!TestTrue(TEXT("Real source/controller fixture for exact launch tie"),F.Create())||!F.Face(Facing))return false;
        // Exact binary initial anchor keeps the independent midpoint fixture representable.
        F.Player->SetActorLocation(FVector(Facing*1024.,0.,0.));
        if(!TestTrue(TEXT("Pre-action fixture starts at an exact binary anchor"),
            F.Player->GetGroundPosition().X==Facing*1024.&&F.Player->GetGroundPosition().Y==0.))return false;
        if(!F.Pulse(EKeys::J))return false;
        const auto A=F.Actions().Action;const auto Anchor=F.Player->GetGroundPosition();
        if(!TestTrue(TEXT("Normal J accepted before creating static launch fixture"),A.Active
            &&A.Type==SocketWA::EAction::Primary&&A.Facing==Facing&&F.Game->GetSimulationTime()<A.ActiveAt))return false;
        SocketPose::FResolved Future;
        if(!TestTrue(TEXT("Readonly actual accepted primary resolves its real emission geometry"),
            SocketPose::Resolve(F.Actions(),A.ActiveAt,double(F.Player->AnimationTime),Future)
            &&Future.Supported&&Future.Clip==SocketPose::EClip::Primary&&Future.Frame==2))return false;
        const double Forward=(Future.EmitX-Future.RootX)*Future.BodySize/512./.65;
        const double EndX=Anchor.X+Facing*Forward,MidX=Anchor.X+(EndX-Anchor.X)*.5;
        auto Wall=F.Wall({MidX+Facing*4.,Anchor.Y});auto Target=F.Target({MidX+Facing*18.,Anchor.Y});
        if(!Wall||!Target||!F.AdvanceTo(A.ActiveAt))return false;
        const auto* Actual=F.Issued(A.ActionId);if(!TestNotNull(TEXT("Actual issued native hand emission exists"),Actual))return false;
        const auto E=*Actual;
        if(!TestTrue(TEXT("Actual world native projectile admitted"),F.State().Projectiles.Num()==1
            &&F.State().Projectiles[0].HasPoseSocket&&F.State().Projectiles[0].UsesActorRangeAnchor))return false;
        const auto& P=F.State().Projectiles[0];
        FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
        FCollisionQueryParams Params(SCENE_QUERY_STAT(ReviewExactWeaponLaunchTie),false);Params.AddIgnoredActor(F.Player);
        TArray<FHitResult> Hits;
        F.World->LineTraceMultiByObjectType(Hits,FVector(P.RangeAnchor.X,P.RangeAnchor.Y,0),FVector(E.Origin.X,E.Origin.Y,0),Objects,Params);
        const FHitResult* WallHit=nullptr;
        for(const auto& H:Hits)if(H.GetActor()==Wall&&H.bBlockingHit&&FMath::Abs(H.ImpactNormal.Z)<.5){WallHit=&H;break;}
        const double X0=Target->GetGroundPosition().X-P.RangeAnchor.X,X1=Target->GetGroundPosition().X-E.Origin.X;
        const double Entry=FMath::Min((-18.-X0)/(X1-X0),(18.-X0)/(X1-X0));
        AddInfo(FString::Printf(TEXT("Exact launch tie Facing=%.0f ActorX=%.17g OriginX=%.17g WallFraction=%.17g BodyEntry=%.17g TargetX=%.17g HP=%.17g"),
            Facing,P.RangeAnchor.X,E.Origin.X,WallHit?double(WallHit->Time):-1.,Entry,Target->GetGroundPosition().X,double(Target->Health)));
        if(!TestTrue(TEXT("Actual physics and actual analytic entry are exactly the same midpoint without epsilon"),
            WallHit&&double(WallHit->Time)==.5&&Entry==.5&&Entry==double(WallHit->Time)
            &&P.RangeAnchor.X==Anchor.X&&P.RangeAnchor.Y==Anchor.Y&&E.Origin.Y==Anchor.Y
            &&Target->GetGroundPosition().Y==Anchor.Y&&E.Origin.Height==0&&Target->JumpHeight==0
            &&Target->GetRuntimeEntityId()!=0))return false;
        const auto* Stop=F.Event(SocketWorldEvent::ProjectileStopped);
        TestTrue(TEXT("Wall wins an exact launch tie at the same emission time and shields the body"),
            !P.Active&&P.Stop==EDungeonWorldProjectileStop::Wall&&P.LaunchObstructed&&P.Traveled==0
            &&Stop&&Stop->AtTime==E.AtTime&&Stop->LaunchObstructed&&Target->Health==1000
            &&F.Events(SocketWorldEvent::DirectHitCommitted)==0&&F.State().HitReceipts.Num()==0
            &&F.Events(SocketWorldEvent::ProjectileEmitted)==1&&F.Events(SocketWorldEvent::ProjectileStopped)==1
            &&F.Instance()->Ammo==0&&F.Game->GetEquipmentView().Slots[1].Ammo==0);
        if(!F.AdvanceTo(A.Start+.65))return false;
        TestTrue(TEXT("The tied wall stop never causes delayed body damage or another bolt"),Target->Health==1000
            &&F.Events(SocketWorldEvent::DirectHitCommitted)==0&&F.Events(SocketWorldEvent::ProjectileEmitted)==1
            &&F.Events(SocketWorldEvent::ProjectileStopped)==1&&F.Instance()->Ammo==0);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSocketOldBurnDeathReview,
    "CodexDungeon.Content.WeaponPoseSocketReview.OldBurnDeathBeforeNewEmissionCannotBlockLiveRearTarget",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSocketOldBurnDeathReview::RunTest(const FString& Parameters)
{
    FSocketReviewWorld F(this);if(!TestTrue(TEXT("Real loaded XBW source/controller for causal death"),F.Create()))return false;
    const auto Anchor=F.Player->GetGroundPosition();
    auto NearTarget=F.Target(Anchor+FVector2D(50,0),22.f),FarTarget=F.Target(Anchor+FVector2D(200,0));
    if(!NearTarget||!FarTarget)return false;
    DungeonEquipmentInventory::FItem Staff;Staff.ContentId="WPN-STF-001";
    const auto StaffSource=F.Game->RegisterEquipmentSource(TEXT("qa.pose-socket.causal-staff"),Staff,Anchor+FVector2D(40,0));
    if(!TestTrue(TEXT("Real additional staff source registered"),StaffSource.Ok()&&F.Game->SelectEquipmentSource(StaffSource.SourceId)))return false;
    if(!F.Pulse(EKeys::E)||!TestTrue(TEXT("Full slots require actual E selection on the currently active XBW slot1"),
        F.Game->GetEquipmentView().NeedsSlotSelection&&F.Game->GetEquipmentView().SelectionSlot==1
        &&F.Game->GetEquipmentView().SelectedSourceId==StaffSource.SourceId))return false;
    if(!F.Pulse(EKeys::Left)||!TestTrue(TEXT("Fresh normal UI Left explicitly selects starter slot0 for the staff"),
        F.Game->GetEquipmentView().NeedsSlotSelection&&F.Game->GetEquipmentView().SelectionSlot==0
        &&F.Game->GetEquipmentView().SelectedSourceId==StaffSource.SourceId&&!F.Game->GetEquipmentView().Action.Active))return false;
    if(!F.Pulse(EKeys::Enter)||!TestTrue(TEXT("Fresh Enter actually starts the staff pickup transaction"),F.Game->GetEquipmentView().Action.Active)
        ||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    if(!TestTrue(TEXT("Normal Enter replaced starter slot0 without discarding loaded XBW1"),
        F.Game->GetEquipmentView().Slots[0].InstanceId==StaffSource.InstanceId
        &&F.Game->GetEquipmentView().Slots[1].InstanceId==F.AcquiredInstance&&F.Instance()->Ammo==1))return false;
    if(!F.Pulse(EKeys::Q)||!TestTrue(TEXT("Actual normal Q starts the staff equip transaction"),F.Game->GetEquipmentView().Action.Active)
        ||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline())
        ||!TestTrue(TEXT("Normal Q equipped that actual staff instance"),F.Actions().EquippedId==StaffSource.InstanceId))return false;
    if(!F.Pulse(EKeys::K))return false;const auto K=F.Actions().Action;
    if(!TestTrue(TEXT("Actual normal K admits full staff fireline"),K.Active&&K.Type==SocketWA::EAction::Skill
        &&K.Weapon==DungeonContentCombat::EWeapon::STF001))return false;
    if(!F.AdvanceTo(K.ActiveAt))return false;
    const auto* Fire=F.Issued(K.ActionId);
    if(!TestTrue(TEXT("Real noncritical18 direct hit leaves initial22HP at4 and applies the2/s burn"),Fire&&!Fire->Action.Critical
        &&Fire->Damage==18&&NearTarget->Health==4&&!NearTarget->bDead))return false;
    const uint64 NearId=NearTarget->GetRuntimeEntityId(),FarId=FarTarget->GetRuntimeEntityId();
    const auto NearBurn=[&F,NearId]()->const FDungeonWorldBurn*
    {for(const auto& B:F.State().Burns)if(B.TargetId==NearId)return &B;return nullptr;};
    const auto* Burn=NearBurn();
    if(!TestTrue(TEXT("Actual old burn slot is active with fixed2 and a real next tick"),Burn&&Burn->Active&&Burn->Dps==2))return false;
    const double FirstTick=Burn->NextTickAt;
    if(!F.AdvanceTo(K.End)||!F.Pulse(EKeys::Q)||!TestTrue(TEXT("Full staff recovery permits the real Q back to XBW"),F.Game->GetEquipmentView().Action.Active)
        ||!F.AdvanceTo(F.Player->GetEquipmentActionDeadline()))return false;
    AddInfo(FString::Printf(TEXT("Causal fixture actual skill cycle=%.17g Qcomplete=%.17g FirstBurn=%.17g NearHP=%.9g"),
        K.End-K.Start,F.Game->GetSimulationTime(),FirstTick,double(NearTarget->Health)));
    if(F.Game->GetSimulationTime()<FirstTick&&!F.AdvanceTo(FirstTick))return false;
    Burn=NearBurn();
    if(!TestTrue(TEXT("Full skill recovery and normal Q preserve loaded XBW; first old burn already leaves nearHP2"),
        F.Actions().EquippedId==F.AcquiredInstance&&F.Instance()->Ammo==1&&NearTarget->Health==2&&!NearTarget->bDead
        &&Burn&&Burn->Active&&Burn->NextTickAt>F.Game->GetSimulationTime()))return false;
    const double SecondTick=Burn->NextTickAt;
    int32 FirstTicks=0;for(const auto& E:F.State().Events)if(E.Kind==SocketWorldEvent::BurnTickCommitted&&E.TargetId==NearId
        &&E.Key.ActionId==K.ActionId&&E.AtTime==FirstTick&&E.ActualHPLoss==2)++FirstTicks;
    const auto* XBWDefinition=DungeonContentCombat::GetWeaponDefinition(DungeonContentCombat::EWeapon::XBW001);
    const double InputTime=SecondTick-XBWDefinition->Primary[0].Windup;
    if(!TestTrue(TEXT("Actual burn phase and legal input time permit an exact same-point emission, without clock tolerance"),
        FirstTicks==1&&SecondTick==FirstTick+1&&InputTime>F.Game->GetSimulationTime()
        &&InputTime+XBWDefinition->Primary[0].Windup==SecondTick))return false;
    if(!F.AdvanceTo(InputTime)||!F.Pulse(EKeys::J))return false;const auto A=F.Actions().Action;
    if(!TestTrue(TEXT("Actual J starts at the planned real clock and its exact deadline equals second old tick"),A.Active
        &&A.Type==SocketWA::EAction::Primary&&A.InstanceId==F.AcquiredInstance&&A.Start==InputTime&&A.ActiveAt==SecondTick))return false;
    if(!F.AdvanceTo(std::nextafter(SecondTick,0.)))return false;
    if(!TestTrue(TEXT("At the last representable point before emission the real near target is still alive at2HP"),
        !NearTarget->bDead&&NearTarget->Health==2&&F.Issued(A.ActionId)==nullptr))return false;
    const double FarBeforeSecond=FarTarget->Health;
    if(!F.AdvanceTo(SecondTick))return false;
    const auto* Emitted=F.Issued(A.ActionId);if(!TestNotNull(TEXT("New real bolt is actually emitted at the death point"),Emitted))return false;
    const auto E=*Emitted;const FDungeonWorldWeaponEvent* DeathTick=nullptr;const FDungeonWorldWeaponEvent* Emission=nullptr;
    for(const auto& Fact:F.State().Events)
    {
        if(Fact.Kind==SocketWorldEvent::BurnTickCommitted&&Fact.TargetId==NearId&&Fact.Key.ActionId==K.ActionId&&Fact.AtTime==SecondTick)DeathTick=&Fact;
        if(Fact.Kind==SocketWorldEvent::ProjectileEmitted&&Fact.Key.ActionId==A.ActionId)Emission=&Fact;
    }
    AddInfo(FString::Printf(TEXT("Old-burn/new-emission causal premise: first=%.17g second=%.17g Jstart=%.17g issued=%.17g nearHP=%.9g nearDead=%d burnSeq=%llu emitSeq=%llu farHP=%.9g"),
        FirstTick,SecondTick,A.Start,E.AtTime,double(NearTarget->Health),int(NearTarget->bDead),DeathTick?DeathTick->Sequence:0,
        Emission?Emission->Sequence:0,double(FarTarget->Health)));
    if(!TestTrue(TEXT("Old actual burn kills first at exactly the new emission timestamp, before its journal emission"),
        NearTarget->bDead&&NearTarget->Health==0&&DeathTick&&DeathTick->ActualHPLoss==2&&DeathTick->AtTime==E.AtTime
        &&E.AtTime==SecondTick&&Emission&&DeathTick->Sequence<Emission->Sequence&&Emission->HasPoseSocket
        &&E.Origin.Height==0&&F.Instance()->Ammo==0))return false;
    bool DeadReceipt=false;for(const auto& H:F.State().HitReceipts)if(H.Key.ActionId==A.ActionId&&H.TargetId==NearId)DeadReceipt=true;
    const FDungeonWorldProjectile* Flight=nullptr;for(const auto& P:F.State().Projectiles)if(P.Key.ActionId==A.ActionId)Flight=&P;
    TestTrue(TEXT("A newly emitted bolt cannot admit a dead near body or be stopped by its stale pre-death observation"),
        !DeadReceipt&&Flight&&Flight->Active&&!Flight->LaunchObstructed);
    if(!F.AdvanceTo(A.Start+.65))return false;
    int32 FarHits=0,NearHits=0,Bolts=0,NearReceipts=0;const FDungeonWorldWeaponEvent* FarHit=nullptr;
    for(const auto& Fact:F.State().Events)if(Fact.Key.ActionId==A.ActionId)
    {
        if(Fact.Kind==SocketWorldEvent::ProjectileEmitted)++Bolts;
        if(Fact.Kind==SocketWorldEvent::DirectHitCommitted&&Fact.TargetId==FarId){++FarHits;FarHit=&Fact;}
        if(Fact.Kind==SocketWorldEvent::DirectHitCommitted&&Fact.TargetId==NearId)++NearHits;
    }
    for(const auto& H:F.State().HitReceipts)if(H.Key.ActionId==A.ActionId&&H.TargetId==NearId)++NearReceipts;
    const double Contact=E.AtTime+(FarTarget->GetGroundPosition().X-18.-E.Origin.X)/E.ProjectileSpeed;
    TestTrue(TEXT("The live rear target receives that one real bolt after old burn death, with no corpse hit or duplicate spend"),
        NearReceipts==0&&NearHits==0&&FarHits==1&&Bolts==1&&FarHit&&SocketNear(FarHit->AtTime,Contact,1.e-7)
        &&SocketNear(FarHit->ActualHPLoss,E.Damage,.0002)&&SocketNear(FarBeforeSecond-FarTarget->Health,2.+E.Damage,.0002)
        &&NearTarget->bDead&&NearTarget->Health==0&&F.Instance()->Ammo==0&&F.Game->GetEquipmentView().Slots[1].Ammo==0);
    return true;
}
#endif
