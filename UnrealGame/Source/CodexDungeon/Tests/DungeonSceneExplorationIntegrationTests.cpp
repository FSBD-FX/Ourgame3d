#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "Components/BoxComponent.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
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
struct FSceneActorWorld
{
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    FAutomationTestBase* Test=nullptr;
    explicit FSceneActorWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FSceneActorWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage){Test->AddError(FString::Printf(TEXT("Scene actual Actor fixture failed at %s"),Stage));return false;}
    bool Create()
    {
        if(!GEngine)return Fail(TEXT("GEngine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("CreateWorld"));GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("GameMode"));Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return Fail(TEXT("Actual player and controller"));
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(UGameplayStatics::GetPlayerController(Game,0)!=Controller||!Controller->IsLocalController())return Fail(TEXT("Registered local controller"));
        Game->PlayerFighter=Player;
        if(!Game->BeginSceneExplorationPreview())return Fail(TEXT("Real initial Scene Run"));
        if(Game->GetSimulationTime()!=0.||Game->Enemies.Num()!=1||!Game->Enemies[0]->GetStoneKnightDriver())return Fail(TEXT("Initial unique actual knight"));
        // Explicit time-zero fixture only. All later clear/death facts come from
        // normal SWD input; live HP/position/equipment are never assigned here.
        Game->Enemies[0]->bAIEnabled=false;
        return true;
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);
        TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);
    }
    bool Key(FKey K,bool Down)
    {
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(K)==Down;
    }
    bool Pulse(FKey K)
    {
        if(!Key(K,true)||!Controller->WasInputKeyJustPressed(K))return Fail(TEXT("Fresh input edge"));
        Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;
    }
    bool Start(){return Pulse(EKeys::Enter)&&!Game->bWaitingForStart&&Game->GetSimulationTime()>0.;}
    bool Advance(double Seconds)
    {
        for(int32 I=0;I<10000&&Seconds>0.;++I){const float Dt=float(FMath::Min(Seconds,.02));Frame(Dt);Seconds-=double(Dt);}
        return Seconds<=1.e-8&&!Game->bGameOver;
    }
    bool MoveAxis(double Target,bool X)
    {
        const auto InitialPosition=Player->GetGroundPosition();FVector2D LastFrom=InitialPosition,LastAfter=InitialPosition;
        double LastDelta=0.;float LastDt=0.f;int32 StalledSteps=0;
        for(int32 I=0;I<1600;++I)
        {
            const auto P=Player->GetGroundPosition();const double Delta=Target-(X?P.X:P.Y);
            if(FMath::Abs(Delta)<.002)return true;
            const FKey Direction=X?(Delta>0.?EKeys::D:EKeys::A):(Delta>0.?EKeys::W:EKeys::S);
            if(!Key(Direction,true))return false;
            const float Dt=float(FMath::Min(.02,FMath::Abs(Delta)/double(Player->GetMoveSpeed())));
            Frame(Dt);if(!Key(Direction,false))return false;
            LastFrom=P;LastAfter=Player->GetGroundPosition();LastDelta=Delta;LastDt=Dt;
            if(LastAfter.Equals(LastFrom,1.e-9))++StalledSteps;
            if(Game->bGameOver)return false;
        }
        const auto Requested=LastFrom+(X?FVector2D(FMath::Sign(LastDelta),0.):FVector2D(0.,FMath::Sign(LastDelta)))
            *double(Player->GetMoveSpeed())*double(LastDt);
        FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
        FCollisionQueryParams Query(SCENE_QUERY_STAT(SceneWaypointDiagnostic),false);Query.AddIgnoredActor(Player);TArray<FHitResult> Hits;
        World->SweepMultiByObjectType(Hits,FVector(LastFrom.X,LastFrom.Y,0.),FVector(Requested.X,Requested.Y,0.),FQuat::Identity,
            Objects,FCollisionShape::MakeBox(FVector(18.,16.,1.)),Query);
        for(const auto& Hit:Hits)if(Hit.bBlockingHit)
            Test->AddInfo(FString::Printf(TEXT("Waypoint sweep observation: to=(%.17g,%.17g) time=%.17g penetrating=%d depth=%.17g impactNormal=(%.17g,%.17g,%.17g) normal=(%.17g,%.17g,%.17g) deltaDotImpact=%.17g"),
                Requested.X,Requested.Y,double(Hit.Time),int32(Hit.bStartPenetrating),double(Hit.PenetrationDepth),
                Hit.ImpactNormal.X,Hit.ImpactNormal.Y,Hit.ImpactNormal.Z,Hit.Normal.X,Hit.Normal.Y,Hit.Normal.Z,
                FVector2D::DotProduct(Requested-LastFrom,FVector2D(Hit.ImpactNormal.X,Hit.ImpactNormal.Y))));
        Test->AddError(FString::Printf(TEXT("Normal movement waypoint failed: axis=%s target=%.17g initial=(%.17g,%.17g) lastFrom=(%.17g,%.17g) lastAfter=(%.17g,%.17g) delta=%.17g dt=%.17g stalledSteps=%d sim=%.17g"),
            X?TEXT("X"):TEXT("Y"),Target,InitialPosition.X,InitialPosition.Y,LastFrom.X,LastFrom.Y,LastAfter.X,LastAfter.Y,
            LastDelta,double(LastDt),StalledSteps,Game->GetSimulationTime()));
        return false;
    }
    bool Hold(FKey K,double Seconds)
    {if(!Key(K,true))return false;const bool Result=Advance(Seconds);Key(K,false);Frame(.005f);return Result;}
    const FDungeonSceneObjectView* Object(uint64 Id)const
    {for(const auto& O:Game->GetSceneRoomView().Objects)if(O.ObjectId==Id)return &O;return nullptr;}
    bool KillKnightNormally()
    {
        if(!MoveAxis(220.,true))return false;
        auto Knight=Game->Enemies[0].Get();
        for(int32 I=0;I<12&&!Knight->bDead;++I)
        {
            if(!Pulse(EKeys::J)||!Advance(.8))return false;
        }
        return Knight->bDead&&Knight->Health<=0.f&&Game->bRoomCleared;
    }
    AActor* InitialWall(FVector2D Position,FVector Extent)
    {
        if(Game->GetSimulationTime()!=0.)return nullptr;
        auto Actor=World->SpawnActor<AActor>();if(!Actor)return nullptr;
        auto Box=NewObject<UBoxComponent>(Actor);Actor->SetRootComponent(Box);Box->SetBoxExtent(Extent);
        Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Box->SetCollisionObjectType(ECC_WorldStatic);
        Box->SetCollisionResponseToAllChannels(ECR_Block);Box->RegisterComponentWithWorld(World);
        Actor->SetActorLocation(FVector(Position.X,Position.Y,40.));return Actor;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneActualLayout,
    "CodexDungeon.Content.SceneExplorationIntegration.RealLayoutBlocksAndGroundBypass",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneActualLayout::RunTest(const FString& Parameters)
{
    FSceneActorWorld F(this);if(!F.Create())return false;
    const auto Initial=F.Game->GetSceneRoomView();const auto Equipment=F.Game->GetEquipmentView();
    if(!TestTrue(TEXT("Scene genuinely initializes bound SWD Run, single old knight and explicit layout behind Enter"),Initial.Active
        &&Initial.RunGuid==Equipment.RunGuid&&Initial.RoomInstanceId==Equipment.RoomInstanceId&&Equipment.Bound
        &&Equipment.Slots[0].ContentId==TEXT("WPN-SWD-001")&&!Equipment.Slots[1].InstanceId&&!Equipment.Slots[2].InstanceId
        &&F.Game->GetEquipmentSources().IsEmpty()&&F.Game->Enemies[0]->Health==110.f&&F.Game->bWaitingForStart
        &&F.Player->GetGroundPosition()==Initial.Layout.Entry&&Initial.Layout.Entry==FVector2D(-1180.,0.)
        &&Initial.Layout.Exit==FVector2D(1180.,0.)&&Initial.Layout.Barrier.Min==FVector2D(-1100.,60.)
        &&Initial.Layout.Barrier.Max==FVector2D(-700.,160.)&&Initial.Layout.Survey==FVector2D(-920.,300.)&&Initial.Objects.Num()==2))return false;
    const auto NextInstance=Equipment.NextInstanceId,NextSource=Equipment.NextSourceId,NextActor=F.Game->GetWeaponWorldState().NextEntityId;
    for(int32 I=0;I<12;++I){F.Game->GetSceneRoomView();F.Game->FindSceneRoomView(Initial.RoomInstanceId);F.Game->GetSceneInteractionView();}
    TestTrue(TEXT("Duplicate Scene admission and readonly observations allocate no Run identities"),F.Game->BeginSceneExplorationPreview()
        &&F.Game->GetEquipmentView().RunGuid==Equipment.RunGuid&&F.Game->GetEquipmentView().NextInstanceId==NextInstance
        &&F.Game->GetEquipmentView().NextSourceId==NextSource&&F.Game->GetWeaponWorldState().NextEntityId==NextActor);
    if(!F.Start()||!F.MoveAxis(-920.,true)||!F.Hold(EKeys::W,1.))return false;
    const auto Blocked=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("Actual WorldStatic side wall stops continuous ground movement at its near face"),FMath::Abs(Blocked.X+920.)<.01
        &&Blocked.Y>35.&&Blocked.Y<=44.01&&F.Player->JumpHeight==0.f))return false;
    if(!F.MoveAxis(-940.,true))return false;const auto AlongLeft=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("Native zero-depth contact permits real tangential movement left along the same face"),FMath::Abs(AlongLeft.X+940.)<.01
        &&FMath::Abs(AlongLeft.Y-Blocked.Y)<.01&&F.Player->JumpHeight==0.f))return false;
    if(!F.MoveAxis(-920.,true))return false;const auto AlongRight=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("Normal opposite tangent returns along the face without crossing into the wall"),FMath::Abs(AlongRight.X+920.)<.01
        &&FMath::Abs(AlongRight.Y-Blocked.Y)<.01&&AlongRight.Y<=44.01))return false;
    if(!F.Hold(EKeys::W,.1))return false;const auto Inward=F.Player->GetGroundPosition();
    if(!TestTrue(TEXT("A new inward request at the same contact remains actually blocked"),FMath::Abs(Inward.X+920.)<.01
        &&FMath::Abs(Inward.Y-Blocked.Y)<.01&&Inward.Y<=44.01&&F.Player->JumpHeight==0.f))return false;
    if(!F.MoveAxis(0.,false)||!F.MoveAxis(Initial.Layout.Entry.X,true)||!F.MoveAxis(300.,false)||!F.MoveAxis(-920.,true))return false;
    TestTrue(TEXT("West bypass is actually reachable with ground input and no jump or paid resource"),F.Player->GetGroundPosition().Equals(Initial.Layout.Survey,.01)
        &&F.Player->JumpHeight==0.f&&F.Player->Coins==0&&!F.Game->bGameOver&&F.Object(1)&&!F.Object(1)->Surveyed);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneActualSurvey,
    "CodexDungeon.Content.SceneExplorationIntegration.SurveyRequiresFreshInteractionAndNeverPays",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneActualSurvey::RunTest(const FString& Parameters)
{
    FSceneActorWorld F(this);if(!F.Create())return false;
    if(!TestNotNull(TEXT("Declared initial LOS fixture wall"),F.InitialWall({-960.,300.},FVector(2.,30.,80.))))return false;
    const auto Initial=F.Game->GetSceneRoomView();const auto Gear=F.Game->GetEquipmentView();
    if(!F.Start()||!F.MoveAxis(300.,false)||!F.MoveAxis(-980.,true))return false;
    if(!TestTrue(TEXT("Physical proximity and walking do not themselves survey the no-income board"),F.Object(1)&&!F.Object(1)->Surveyed
        &&F.Object(1)->SurveyCount==0&&FMath::Abs(F.Object(1)->Position.X-F.Player->GetGroundPosition().X)<=80.
        &&FMath::Abs(F.Object(1)->Position.Y-F.Player->GetGroundPosition().Y)<=40.))return false;
    if(!F.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("True close-range E cannot investigate through a real WorldStatic blocker"),!F.Object(1)->Surveyed
        &&F.Object(1)->SurveyCount==0&&F.Game->GetSceneInteractionView().LastFailure==EDungeonSceneFailure::NoLineOfSight))return false;
    if(!F.MoveAxis(360.,false)||!F.MoveAxis(-920.,true)||!F.MoveAxis(300.,false)||!F.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Actual fresh E commits exactly one survey to this Run and Room"),F.Object(1)->Surveyed&&F.Object(1)->SurveyCount==1
        &&F.Object(1)->RoomInstanceId==Initial.RoomInstanceId&&F.Game->GetSceneRoomView().RunGuid==Initial.RunGuid))return false;
    if(!F.Pulse(EKeys::E)||!F.MoveAxis(360.,false)||!F.MoveAxis(300.,false)||!F.Pulse(EKeys::E))return false;
    const auto After=F.Game->GetEquipmentView();
    TestTrue(TEXT("Repeated interaction and return never pays, equips, allocates or duplicates the survey"),F.Object(1)->SurveyCount==1
        &&F.Player->Coins==0&&F.Player->Health==100.f&&After.NextInstanceId==Gear.NextInstanceId&&After.NextSourceId==Gear.NextSourceId
        &&After.Slots[0].InstanceId==Gear.Slots[0].InstanceId&&!After.Slots[1].InstanceId&&!After.Slots[2].InstanceId
        &&F.Game->GetEquipmentSources().IsEmpty()&&F.Game->Pickups.IsEmpty()&&!F.Game->bRoomCleared);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneActualExit,
    "CodexDungeon.Content.SceneExplorationIntegration.BoundExitUsesActualAnchorAndKeepsRoomScope",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneActualExit::RunTest(const FString& Parameters)
{
    FSceneActorWorld F(this);if(!F.Create()||!F.Start())return false;
    const auto Initial=F.Game->GetSceneRoomView();const auto Gear=F.Game->GetEquipmentView();
    if(!TestTrue(TEXT("Real SWD input kills the actual admitted knight before any clear exit"),F.KillKnightNormally()))return false;
    if(!F.MoveAxis(665.,true)||!F.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Old prototype X665 is no longer a Scene exit or confirmation target"),F.Game->RoomNumber==1
        &&F.Game->GetEquipmentView().RoomInstanceId==Initial.RoomInstanceId&&!F.Game->GetSceneInteractionView().Pending))return false;
    if(!F.MoveAxis(Initial.Layout.Exit.X,true)||!F.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Bound E at the actual endpoint opens one free-exit confirmation without changing rooms"),F.Game->RoomNumber==1
        &&F.Game->GetSceneInteractionView().Pending&&F.Game->GetSceneInteractionView().NeedsConfirmation
        &&F.Game->GetSceneInteractionView().Kind==EDungeonSceneInteractionKind::Exit
        &&F.Game->GetSceneInteractionView().RoomInstanceId==Initial.RoomInstanceId&&F.Game->GetSceneInteractionView().ObjectId==2))return false;
    const int32 CoinsBeforeExit=F.Player->Coins;
    TestEqual(TEXT("Actual D04 automatic death currency credits exactly5 coins before the free exit"),CoinsBeforeExit,5);
    if(!F.Pulse(EKeys::Enter))return false;
    const auto Next=F.Game->GetSceneRoomView();const auto After=F.Game->GetEquipmentView();const auto* Old=F.Game->FindSceneRoomView(Initial.RoomInstanceId);
    TestTrue(TEXT("Fresh Enter transfers the same Run and player into a newly scoped room at the same layout entry"),F.Game->RoomNumber==2
        &&Next.Active&&Next.RoomInstanceId==Initial.RoomInstanceId+1&&After.RoomInstanceId==Next.RoomInstanceId
        &&Next.RunGuid==Initial.RunGuid&&After.RunGuid==Gear.RunGuid&&After.Slots[0].InstanceId==Gear.Slots[0].InstanceId
        &&F.Player->GetGroundPosition().Equals(Next.Layout.Entry,.01)&&F.Player->Health==100.f&&F.Player->Coins==CoinsBeforeExit
        &&F.Game->GetSimulationTime()>0.&&!F.Game->GetSceneInteractionView().Pending&&F.Game->Enemies.Num()==1
        &&F.Game->Enemies[0]->GetStoneKnightDriver()&&!F.Game->Enemies[0]->bDead&&!F.Game->bRoomCleared);
    TestTrue(TEXT("History stays in its old Room while the current board is a fresh no-income object"),Old&&Old->RunGuid==Initial.RunGuid
        &&Old->RoomInstanceId==Initial.RoomInstanceId&&Old->Objects.Num()==2&&Next.Objects.Num()==2
        &&Old->Objects[0].RoomInstanceId==Initial.RoomInstanceId&&Next.Objects[0].RoomInstanceId==Next.RoomInstanceId
        &&!Old->Objects[0].Surveyed&&!Next.Objects[0].Surveyed&&Old->Objects[0].SurveyCount==0&&Next.Objects[0].SurveyCount==0);
    return true;
}
#endif
