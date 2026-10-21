#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonRunExploration.h"
#include "../DungeonRoomLayout.h"
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
#include <map>
#include <limits>

namespace
{
struct FExplorationWorld
{
    UWorld* World=nullptr;
    ADungeonGameMode* Game=nullptr;
    ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;
    FAutomationTestBase* Test=nullptr;
    explicit FExplorationWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FExplorationWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
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
    std::map<uint64,DungeonExploration::FExploration> Expected;
    void Frame(float Dt)
    {
        Game->Tick(Dt);
        const auto& V=Game->GetEquipmentView();
        auto It=Expected.try_emplace(V.RoomInstanceId,DungeonExploration::FBounds{
            DungeonRoomLayout::MinX,DungeonRoomLayout::MaxX,DungeonRoomLayout::MinY,DungeonRoomLayout::MaxY},Game->RoomNumber).first;
        const auto P=Player->GetGroundPosition();It->second.Reveal({P.X,P.Y});
        Controller->PlayerInput->Tick(Dt);
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
            const FKey Toward=Knight->GetGroundPosition().X<Player->GetGroundPosition().X?EKeys::A:EKeys::D;
            if(!Key(Toward,true))return false;Frame(.005f);if(!Key(Toward,false))return false;Frame(.005f);
            if(!Pulse(EKeys::J)||!Advance(.8))return false;
        }
        return Knight->bDead&&Knight->Health<=0.f&&Game->bRoomCleared;
    }
};
bool Same(const FDungeonRunExplorationSnapshot& A,const FDungeonRunExplorationSnapshot& B)
{
    if(A.Schema!=B.Schema||A.RunGuid!=B.RunGuid||A.CurrentRoomInstanceId!=B.CurrentRoomInstanceId||A.Rooms.Num()!=B.Rooms.Num())return false;
    for(int32 I=0;I<A.Rooms.Num();++I)
    {
        const auto& X=A.Rooms[I];const auto& Y=B.Rooms[I];const auto& P=X.State;const auto& Q=Y.State;
        if(X.RoomInstanceId!=Y.RoomInstanceId||X.RoomNumber!=Y.RoomNumber||P.Schema!=Q.Schema||P.RoomId!=Q.RoomId
            ||P.Bounds.MinX!=Q.Bounds.MinX||P.Bounds.MaxX!=Q.Bounds.MaxX||P.Bounds.MinY!=Q.Bounds.MinY||P.Bounds.MaxY!=Q.Bounds.MaxY||P.Memory!=Q.Memory)return false;
    }
    return true;
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunExplorationActualRooms,"CodexDungeon.Content.RunExploration.ActualRouteAndRoomHistory",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunExplorationActualRooms::RunTest(const FString& Parameters)
{
    FExplorationWorld F(this);if(!F.Create()||!F.Start())return false;
    if(!F.MoveAxis(-650.,true)||!F.MoveAxis(300.,false)||!F.MoveAxis(-650.,true)||!F.MoveAxis(0.,false)
        ||!F.KillKnightNormally()||!F.MoveAxis(F.Game->GetSceneRoomView().Layout.Exit.X,true)||!F.Pulse(EKeys::E)||!F.Pulse(EKeys::Enter))return false;
    const auto Saved=F.Game->CaptureRunExplorationSnapshot();const auto& V=F.Game->GetEquipmentView();
    if(!TestTrue(TEXT("Actual bound route and free exit produce both nonempty Run-owned room memories without a Canvas"),Saved.RunGuid==V.RunGuid
        &&Saved.CurrentRoomInstanceId==V.RoomInstanceId&&Saved.Rooms.Num()==2&&F.Expected.size()==2))return false;
    for(const auto& R:Saved.Rooms)
    {
        auto It=F.Expected.find(R.RoomInstanceId);if(!TestTrue(TEXT("Every saved room has an independently observed actual route"),It!=F.Expected.end()))return false;
        const auto Expected=It->second.Capture();
        TestTrue(TEXT("Entire interpolated memory exactly equals the existing Reveal algorithm at each actual completed Tick"),R.State.Memory==Expected.Memory
            &&R.State.RoomId==Expected.RoomId&&R.RoomNumber==Expected.RoomId&&!R.State.Memory.empty());
    }
    TestTrue(TEXT("Current entrance starts its own observed room rather than inheriting the entire prior room"),Saved.Rooms[0].State.Memory!=Saved.Rooms[1].State.Memory);
    auto Changed=Saved;Changed.Rooms[0].State.Memory[0]=.123;
    TestTrue(TEXT("Repeated Capture is readonly and caller copies cannot replace the live memory"),Same(Saved,F.Game->CaptureRunExplorationSnapshot()));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunExplorationRestore,"CodexDungeon.Content.RunExploration.ExactRestoreAndAtomicRejection",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunExplorationRestore::RunTest(const FString& Parameters)
{
    FExplorationWorld F(this);if(!F.Create()||!F.Start()||!F.MoveAxis(-650.,true)||!F.MoveAxis(300.,false))return false;
    const auto Saved=F.Game->CaptureRunExplorationSnapshot();
    if(!TestTrue(TEXT("Source is genuine nonempty observed bound Run exploration"),Saved.RunGuid==F.Game->GetEquipmentView().RunGuid&&Saved.Rooms.Num()==1&&!Saved.Rooms[0].State.Memory.empty()))return false;
    FDungeonRunExploration Target;FString Why;
    if(!TestTrue(TEXT("A separate Run exploration owner restores the entire actual source"),Target.Restore(Saved,Why)))return false;
    TestTrue(TEXT("Capture after Restore exactly preserves all source fields"),Same(Saved,Target.Capture()));
    DungeonExploration::FExploration Expected(Saved.Rooms[0].State.Bounds,Saved.Rooms[0].RoomNumber);Expected.Restore(Saved.Rooms[0].State);
    TestTrue(TEXT("Restored interpolation and derived count match, including original fractional values"),Target.MemoryAt({-900.,220.})==Expected.MemoryAt({-900.,220.})
        &&Target.ExploredVertexCount()==int32(Expected.ExploredVertexCount()));
    const auto Reject=[&](FDungeonRunExplorationSnapshot Bad,const TCHAR* Label){TestFalse(Label,Target.Restore(Bad,Why));TestTrue(TEXT("Rejected candidate leaves entire old bank unchanged"),Same(Saved,Target.Capture()));};
    auto Bad=Saved;Bad.Schema=2;Reject(Bad,TEXT("Unknown bank schema rejected"));
    Bad=Saved;Bad.RunGuid.Invalidate();Reject(Bad,TEXT("Missing stable Run rejected"));
    Bad=Saved;++Bad.CurrentRoomInstanceId;Reject(Bad,TEXT("Missing current room rejected"));
    Bad=Saved;Bad.Rooms[0].State.Memory[0]=std::numeric_limits<double>::quiet_NaN();Reject(Bad,TEXT("Nonfinite memory rejected"));
    Bad=Saved;Bad.Rooms[0].State.Memory[0]=-1.e-12;Reject(Bad,TEXT("Out of range original memory rejected"));
    Bad=Saved;Bad.Rooms[0].State.Memory.pop_back();Reject(Bad,TEXT("Truncated grid rejected"));
    Bad=Saved;auto Duplicate=Bad.Rooms[0];Bad.Rooms.Add(Duplicate);Reject(Bad,TEXT("Duplicate room rejected"));
    Bad=Saved;Bad.Rooms[0].RoomNumber=2;Reject(Bad,TEXT("Display room label mismatch rejected"));
    Bad=Saved;Bad.Rooms[0].State.Bounds.MinX-=1.;Reject(Bad,TEXT("Unknown layout bounds rejected"));
    const auto Point=F.Player->GetGroundPosition();F.Frame(.02f);
    TestTrue(TEXT("Restoring a separate owner cannot mutate the real actor or issue gameplay"),F.Player->GetGroundPosition()==Point&&!F.Game->bGameOver);
    return true;
}
#endif
