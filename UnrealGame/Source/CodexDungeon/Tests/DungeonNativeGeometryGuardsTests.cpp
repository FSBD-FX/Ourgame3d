#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonNativeGeometryGuards.h"
#include "../DungeonGameMode.h"
#include "../DungeonFighter.h"
#include "../DungeonHUD.h"
#include "Components/BoxComponent.h"
#include "Debug/DebugDrawComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "GameFramework/PlayerState.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/BodySetup.h"

namespace
{
// Separate local native fixture. It does not include another test translation
// unit, disable GameplayDebugger, synthesize a renderer, or write private state.
struct FNativeGeometryWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;
    UGameInstance* Instance=nullptr;
    UGameViewportClient* Viewport=nullptr;
    ULocalPlayer* LocalPlayer=nullptr;
    ADungeonGameMode* Game=nullptr;
    APlayerController* Controller=nullptr;
    explicit FNativeGeometryWorld(FAutomationTestBase& InTest):Test(InTest){}
    ~FNativeGeometryWorld()
    {
        if(World)World->EndPlay(EEndPlayReason::Quit);
        if(Instance&&LocalPlayer)Instance->RemoveLocalPlayer(LocalPlayer);
        if(World)
        {
            World->DestroyWorld(false);
            if(Instance)Instance->OnWorldChanged(World,nullptr);
            if(GEngine)GEngine->DestroyWorldContext(World);
        }
    }
    bool Create()
    {
        if(!Test.TestNotNull(TEXT("Geometry regression has actual Engine"),GEngine))return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!Test.TestNotNull(TEXT("Geometry regression creates actual independent native World"),World))return false;
        auto& Context=GEngine->CreateNewWorldContext(EWorldType::Game);
        Instance=NewObject<UGameInstance>(GEngine);World->SetGameInstance(Instance);
        Context.OwningGameInstance=Instance;Context.SetCurrentWorld(World);
        Viewport=NewObject<UGameViewportClient>(GEngine);Context.GameViewport=Viewport;Viewport->Init(Context,Instance,false);
        FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));URL.AddOption(TEXT("DungeonContinuePristine"));
        if(!Test.TestTrue(TEXT("Real native SetGameMode selects project GameMode"),World->SetGameMode(URL)))return false;
        World->InitializeActorsForPlay(URL,true);Game=World->GetAuthGameMode<ADungeonGameMode>();
        if(!Test.TestTrue(TEXT("Native InitGame really initializes GM and GameState before Login"),
            Game&&Game->IsActorInitialized()&&World->AreActorsInitialized()&&World->GetGameState()))return false;
        LocalPlayer=NewObject<ULocalPlayer>(GEngine,GEngine->LocalPlayerClass);
        if(!Test.TestTrue(TEXT("Real LocalPlayer is joined to independent native GameInstance and viewport"),LocalPlayer
            &&Instance->AddLocalPlayer(LocalPlayer,FPlatformUserId::CreateFromInternalId(0))!=INDEX_NONE
            &&LocalPlayer->GetGameInstance()==Instance&&LocalPlayer->GetWorld()==World))return false;
        FString Error;
        if(!Test.TestTrue(TEXT("Real native LocalPlayer performs Login SetPlayer and PostLogin"),LocalPlayer->SpawnPlayActor(URL.ToString(1),Error,World)))
        {Test.AddInfo(TEXT("Native geometry Login diagnosis: ")+Error);return false;}
        Controller=LocalPlayer->PlayerController;
        if(!Test.TestTrue(TEXT("Native local PC Input PlayerState and project HUD are genuinely present"),
            Controller&&Controller->GetWorld()==World&&Controller->HasAuthority()&&Controller->IsLocalController()
            &&Controller->GetLocalPlayer()==LocalPlayer&&Controller->PlayerInput&&Controller->PlayerState
            &&Cast<ADungeonHUD>(Controller->GetHUD())&&UGameplayStatics::GetPlayerController(Game,0)==Controller))return false;
        World->BeginPlay();
        return Test.TestTrue(TEXT("Actual BeginPlay leaves pristine startup with no new Run and no Pawn"),
            World->GetBegunPlay()&&Game->HasActorBegunPlay()&&Controller->HasActorBegunPlay()
            &&!Controller->GetPawn()&&!Controller->GetSpectatorPawn()&&!Game->PlayerFighter&&Game->Enemies.IsEmpty()
            &&Game->GetRunRestartSerial()==0&&Game->GetSimulationTime()==0.&&!Game->GetEquipmentView().Bound
            &&Game->IsRunInstallGated());
    }
};

void GeometryReadback(FAutomationTestBase& Test,const TCHAR* Phase,const UWorld* World,
    const AActor* Actor,UPrimitiveComponent* Component)
{
    TInlineComponentArray<UPrimitiveComponent*> Primitives;Actor->GetComponents(Primitives);
    const auto* RawBody=Component->GetBodyInstance(NAME_None,false);
    Test.AddInfo(FString::Printf(TEXT("NativeGeometryReadback phase=%s world=%s actorClass=%s actor=%s actorWorld=%s actorOwner=%s "
        "componentClass=%s component=%s componentWorld=%s componentOwner=%s componentOuter=%s root=%s attachParent=%s "
        "primitiveCount=%d registered=%d actorCollision=%d collisionEnabled=%d objectType=%d componentBodySetup=%s "
        "rawBodyPresent=%d rawBodyValid=%d rawBodySetup=%s rawWeldParentPresent=%d physicsStateCreated=%d"),
        Phase,*GetPathNameSafe(World),*Actor->GetClass()->GetPathName(),*Actor->GetPathName(),*GetPathNameSafe(Actor->GetWorld()),
        *GetPathNameSafe(Actor->GetOwner()),*Component->GetClass()->GetPathName(),*Component->GetPathName(),
        *GetPathNameSafe(Component->GetWorld()),*GetPathNameSafe(Component->GetOwner()),*GetPathNameSafe(Component->GetOuter()),
        *GetPathNameSafe(Actor->GetRootComponent()),*GetPathNameSafe(Component->GetAttachParent()),Primitives.Num(),
        int32(Component->IsRegistered()),int32(Actor->GetActorEnableCollision()),int32(Component->GetCollisionEnabled()),
        int32(Component->GetCollisionObjectType()),*GetPathNameSafe(Component->GetBodySetup()),int32(RawBody!=nullptr),
        int32(RawBody&&RawBody->IsValidBodyInstance()),*GetPathNameSafe(RawBody?RawBody->GetBodySetup():nullptr),
        int32(RawBody&&RawBody->WeldParent!=nullptr),int32(Component->IsPhysicsStateCreated())));
}

UBoxComponent* RegisterBlockingBox(AActor& Owner,const FVector& Location,bool AsRoot)
{
    auto* Box=NewObject<UBoxComponent>(&Owner);Owner.AddInstanceComponent(Box);
    Box->SetMobility(EComponentMobility::Movable);Box->SetBoxExtent(FVector(40.,40.,40.));
    Box->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Box->SetCollisionObjectType(ECC_WorldStatic);
    Box->SetCollisionResponseToAllChannels(ECR_Block);Box->SetGenerateOverlapEvents(false);
    if(AsRoot)Owner.SetRootComponent(Box);else Box->SetupAttachment(Owner.GetRootComponent());
    Box->RegisterComponentWithWorld(Owner.GetWorld());Box->SetWorldLocation(Location);
    return Box;
}
}

// Catches: treating default collision metadata as a real wall, broadly ignoring
// all no-body primitives, or ignoring extra collision attached to the debugger.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNativeGameplayDebuggerGeometryBoundary,
    "CodexDungeon.Content.NativeGeometry.NativeDebuggerDrawOnlyAndForeignBlockers",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FNativeGameplayDebuggerGeometryBoundary::RunTest(const FString&)
{
    FNativeGeometryWorld Native(*this);if(!Native.Create())return false;
    AActor* Replicator=nullptr;int32 Replicators=0;
    for(TActorIterator<AActor> It(Native.World);It;++It)
        if(It->GetClass()->GetPathName()==TEXT("/Script/GameplayDebugger.GameplayDebuggerCategoryReplicator"))
        {Replicator=*It;++Replicators;}
    if(!TestTrue(TEXT("Real native Login BeginPlay produced exactly one actual GameplayDebugger replicator"),Replicators==1&&IsValid(Replicator)))return false;
    auto* Renderer=Cast<UPrimitiveComponent>(Replicator->GetRootComponent());
    if(!TestTrue(TEXT("Real replicator root is exact native rendering class and DebugDraw subtype"),IsValid(Renderer)
        &&Renderer->GetClass()->GetPathName()==TEXT("/Script/GameplayDebugger.GameplayDebuggerRenderingComponent")
        &&Renderer->IsA<UDebugDrawComponent>()))return false;
    GeometryReadback(*this,TEXT("initial-native"),Native.World,Replicator,Renderer);
    TInlineComponentArray<UPrimitiveComponent*> InitialPrimitives;Replicator->GetComponents(InitialPrimitives);
    const auto* RawBody=Renderer->GetBodyInstance(NAME_None,false);
    if(!TestTrue(TEXT("Read-only native renderer premise has exact owner outer World sole root and collision metadata"),
        Replicator->GetWorld()==Native.World&&Renderer->GetWorld()==Native.World&&Renderer->GetOwner()==Replicator
        &&Renderer->GetOuter()==Replicator&&!Renderer->GetAttachParent()&&InitialPrimitives.Num()==1&&InitialPrimitives[0]==Renderer
        &&Renderer->IsRegistered()&&Replicator->GetActorEnableCollision()&&Renderer->GetCollisionEnabled()!=ECollisionEnabled::NoCollision))return false;
    if(!TestTrue(TEXT("Native default metadata renderer has no BodySetup or valid raw native body or weld"),
        !Renderer->GetBodySetup()&&RawBody&&!RawBody->IsValidBodyInstance()&&!RawBody->GetBodySetup()&&!RawBody->WeldParent))return false;
    // IsPhysicsStateCreated is logged, not assumed false: native registration
    // sets the bookkeeping flag even when no BodySetup exists to initialize.
    TestTrue(TEXT("Shared guard recognizes real native render-only component without changing its state"),
        DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(Native.World,Replicator,Renderer));
    FString Why;
    TestTrue(TEXT("Clean native debugger does not prevent actual pristine eligibility"),Native.Game->IsPristineContinueBootstrap(Why));
    AddInfo(TEXT("Clean native eligibility diagnosis: ")+Why);

    auto* Foreign=Native.World->SpawnActor<AActor>();
    if(!TestNotNull(TEXT("Foreign geometry control is an actual native actor"),Foreign))return false;
    auto* ForeignBox=RegisterBlockingBox(*Foreign,FVector(10000.,10000.,10000.),true);
    GeometryReadback(*this,TEXT("foreign-blocker"),Native.World,Foreign,ForeignBox);
    const auto* ForeignBody=ForeignBox->GetBodyInstance(NAME_None,false);
    if(!TestTrue(TEXT("Foreign registered Box really has blocking responses native BodySetup and valid native physics body"),
        ForeignBox->IsRegistered()&&Foreign->GetActorEnableCollision()&&ForeignBox->GetCollisionEnabled()==ECollisionEnabled::QueryAndPhysics
        &&ForeignBox->GetCollisionResponseToChannels()==FCollisionResponseContainer(ECR_Block)&&ForeignBox->GetBodySetup()
        &&ForeignBody&&ForeignBody->IsValidBodyInstance()&&ForeignBody->GetBodySetup()))return false;
    TestFalse(TEXT("Actual registered foreign blocking Box never receives native debugger exemption"),
        DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(Native.World,Foreign,ForeignBox));
    TestFalse(TEXT("Actual pristine consumer rejects foreign blocking geometry"),Native.Game->IsPristineContinueBootstrap(Why));
    TestFalse(TEXT("Foreign blocker refusal includes diagnostic"),Why.IsEmpty());
    Foreign->Destroy();

    auto* Extra=RegisterBlockingBox(*Replicator,Renderer->GetComponentLocation()+FVector(200.,0.,0.),false);
    GeometryReadback(*this,TEXT("native-with-extra-renderer"),Native.World,Replicator,Renderer);
    GeometryReadback(*this,TEXT("native-extra-blocker"),Native.World,Replicator,Extra);
    TInlineComponentArray<UPrimitiveComponent*> ExtraPrimitives;Replicator->GetComponents(ExtraPrimitives);
    if(!TestTrue(TEXT("Actual extra blocking Box really contaminates native replicator ownership"),Extra->IsRegistered()
        &&Extra->GetOwner()==Replicator&&Extra->GetOuter()==Replicator&&ExtraPrimitives.Num()==2
        &&ExtraPrimitives.Contains(Renderer)&&ExtraPrimitives.Contains(Extra)
        &&Extra->GetCollisionEnabled()!=ECollisionEnabled::NoCollision&&Extra->GetBodySetup()))return false;
    TestFalse(TEXT("Renderer on native actor with additional real primitive loses exemption"),
        DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(Native.World,Replicator,Renderer));
    TestFalse(TEXT("Extra blocking Box cannot inherit its actor's native rendering exemption"),
        DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(Native.World,Replicator,Extra));
    TestFalse(TEXT("Actual pristine consumer rejects extra geometry owned by native debugger"),Native.Game->IsPristineContinueBootstrap(Why));
    TestFalse(TEXT("Extra native geometry refusal includes diagnostic"),Why.IsEmpty());

    Replicator->RemoveInstanceComponent(Extra);Extra->DestroyComponent();
    GeometryReadback(*this,TEXT("native-after-extra-removal"),Native.World,Replicator,Renderer);
    TInlineComponentArray<UPrimitiveComponent*> RestoredPrimitives;Replicator->GetComponents(RestoredPrimitives);
    if(!TestTrue(TEXT("Real component teardown leaves original native renderer as sole primitive again"),
        RestoredPrimitives.Num()==1&&RestoredPrimitives[0]==Renderer&&!Extra->IsRegistered()))return false;
    TestTrue(TEXT("Original renderer is recognized again after actual extra Box removal"),
        DungeonNativeGeometryGuards::IsNativeGameplayDebuggerDrawOnly(Native.World,Replicator,Renderer));
    TestTrue(TEXT("Removing actual contaminants restores pristine eligibility without creating any Run"),
        Native.Game->IsPristineContinueBootstrap(Why)&&!Native.Game->PlayerFighter&&Native.Game->Enemies.IsEmpty()
        &&Native.Game->GetRunRestartSerial()==0&&Native.Game->GetSimulationTime()==0.&&!Native.Game->GetEquipmentView().Bound);
    return true;
}
#endif
