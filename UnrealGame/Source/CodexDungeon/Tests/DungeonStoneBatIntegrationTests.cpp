#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonRoomLayout.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include <cmath>
#include <limits>

namespace
{
namespace Bat=DungeonStoneBat;
struct FBatGameWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;ADungeonFighter* Enemy=nullptr;
    FAutomationTestBase* Test=nullptr;
    explicit FBatGameWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FBatGameWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage){Test->AddError(FString::Printf(TEXT("StoneBat actual Actor fixture failed at %s"),Stage));return false;}
    bool Create(FVector2D Position={100,0},bool SpawnBat=true)
    {
        if(!GEngine)return Fail(TEXT("GEngine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("CreateWorld"));GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("GameMode"));Game=World->GetAuthGameMode<ADungeonGameMode>();
        Player=World->SpawnActor<ADungeonFighter>();if(!Game||!Player)return Fail(TEXT("Player"));
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;Game->bWaitingForStart=false;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("BeginEquipmentRun"));
        if(!SpawnBat)return true;
        Enemy=Game->SpawnStoneBat(Position);
        return Enemy&&Enemy->GetStoneBatDriver()?true:Fail(TEXT("SpawnStoneBat initial configuration"));
    }
    const Bat::FState& State()const{return Enemy->GetStoneBatDriver()->State();}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
        for(int32 N=0;N<64&&Game->GetSimulationTime()<At;++N)
        {
            const double Remaining=At-Game->GetSimulationTime();float Step=float(Remaining);
            if(double(Step)>Remaining)Step=std::nextafter(Step,0.f);if(!(Step>0))return false;
            const double Before=Game->GetSimulationTime();Game->Tick(Step);if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
    bool AwaitAction()
    {for(int32 N=0;N<700&&!State().Action.InProgress&&!Game->bGameOver;++N)Game->Tick(.01f);return State().Action.InProgress;}
    bool AwaitLow()
    {for(int32 N=0;N<500&&State().LowStartedAt<0&&!Game->bGameOver;++N)Game->Tick(.005f);return State().LowStartedAt>=0;}
    AActor* Wall(FVector2D Position,FVector Extent={2,80,120})
    {
        auto A=World->SpawnActor<AActor>();if(!A)return nullptr;auto B=NewObject<UBoxComponent>(A);A->SetRootComponent(B);
        B->SetBoxExtent(Extent);B->SetCollisionEnabled(ECollisionEnabled::QueryOnly);B->SetCollisionObjectType(ECC_WorldStatic);
        B->SetCollisionResponseToAllChannels(ECR_Block);B->RegisterComponentWithWorld(World);A->SetActorLocation({Position.X,Position.Y,50});return A;
    }
    int32 Events(Bat::EEventKind Kind)const{int32 N=0;for(const auto& E:State().Issued)if(E.Kind==Kind)++N;return N;}
};
bool BatNear(double A,double B,double Tolerance=1.e-5){return std::abs(A-B)<=Tolerance;}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoneBatRunIdentity,
    "CodexDungeon.Content.StoneBatGameIntegration.RunIdentityInitialConfigurationAndDefense",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoneBatRunIdentity::RunTest(const FString& Parameters)
{
    FBatGameWorld F(this);if(!F.Create())return false;
    auto Second=F.Game->SpawnStoneBat({200,160});if(!TestNotNull(TEXT("Second real admitted stone bat"),Second))return false;
    const uint64 Id=F.Enemy->GetRuntimeEntityId(),Other=Second->GetRuntimeEntityId();const auto& Initial=F.State();
    TestTrue(TEXT("Actual Run allocator owns distinct non-pointer identities"),Id>1&&Other>Id&&Other<(uint64(1)<<63)
        &&Initial.EntityId==Id&&Second->GetStoneBatDriver()->State().EntityId==Other);
    TestTrue(TEXT("Real initial Actor matches frozen55HP/Z90/Dormant without invented events"),F.Enemy->EnemyContentId==TEXT("ENM-STN-002")
        &&F.Enemy->Health==55&&F.Enemy->MaxHealth==55&&F.Enemy->JumpHeight==90&&Initial.Position.Z==90
        &&Initial.Phase==Bat::EPhase::Dormant&&Initial.Issued.empty()&&!F.Enemy->IsActorTickEnabled());
    TestTrue(TEXT("Formal stats come from actual bat rather than generic enemy"),F.Enemy->GetArmorRating()==15
        &&F.Enemy->GetArmorRating(true)==10&&F.Enemy->GetMoveSpeed()==220&&F.Enemy->GetPoiseThreshold()==25);
    const auto Cursor=F.Game->GetWeaponWorldState().NextEntityId;
    for(int32 I=0;I<20;++I){F.Enemy->GetRuntimeEntityId();F.Enemy->GetStoneBatDriver()->State();}
    TestEqual(TEXT("Readonly identity and state allocate no actor IDs"),F.Game->GetWeaponWorldState().NextEntityId,Cursor);
    TestNull(TEXT("Out-of-room spawn is rejected"),F.Game->SpawnStoneBat({DungeonRoomLayout::MaxX+1,0}));
    TestEqual(TEXT("Rejected spawn consumes no Run identity"),F.Game->GetWeaponWorldState().NextEntityId,Cursor);
    F.Game->Tick(.02f);
    TestTrue(TEXT("Central clock advances real bat and preserves actual height"),F.State().Time==F.Game->GetSimulationTime()
        &&F.Enemy->JumpHeight==90&&F.State().Phase==Bat::EPhase::Waking);
    F.Enemy->ApplyCombatHit(5.75f,F.Player,0.f);
    TestTrue(TEXT("Actual physical armor15 commits5 HP loss into the same kernel"),BatNear(F.Enemy->Health,50,.0002)
        &&BatNear(F.State().HP,50,.0002)&&F.State().ReceivedHits.size()==1);
    TestFalse(TEXT("Second initialization is not a healing/reset operation"),F.Enemy->InitializeStoneBat(Id,F.Game->GetSimulationTime()));
    TestTrue(TEXT("Rejected initialization preserves real HP and identity"),BatNear(F.Enemy->Health,50,.0002)&&F.State().EntityId==Id);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoneBatDynamicEndpoint,
    "CodexDungeon.Content.StoneBatGameIntegration.LockedEndpointWorldWallCannotFakeLowArrival",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoneBatDynamicEndpoint::RunTest(const FString& Parameters)
{
    FBatGameWorld F(this);if(!F.Create({170,0}))return false;
    if(!TestTrue(TEXT("Real central AI eventually accepts a legal descent"),F.AwaitAction()))return false;
    const auto A=F.State().Action;if(!TestTrue(TEXT("First descent is legal Peck implementation choice"),A.Kind==Bat::EAttack::Peck))return false;
    if(!F.AdvanceTo(A.LockAt))return false;const auto Endpoint=F.State().Action.Endpoint;
    if(!TestTrue(TEXT("Actual lock chooses original ordered legal endpoint"),F.State().Action.Locked&&F.State().Action.EndpointFound&&Endpoint.Z==20))return false;
    if(!TestNotNull(TEXT("Real later WorldStatic blocker"),F.Wall({120,0})))return false;
    if(!F.AdvanceTo(A.ActiveAt+.1))return false;
    TestTrue(TEXT("Lost sweep legality misses without fake low arrival or damage"),F.State().Action.Missed&&F.State().PendingLow
        &&F.State().LowStartedAt<0&&F.State().Position.Z>20&&F.Player->Health==100&&F.Events(Bat::EEventKind::ActiveWindow)==0);
    TestTrue(TEXT("Locked target and accepted cooldown survive real blocker"),F.State().Action.Endpoint.X==Endpoint.X
        &&F.State().Action.Endpoint.Y==Endpoint.Y&&F.State().PeckReadyAt==A.CooldownDeadline);
    if(!TestTrue(TEXT("Real swept fallback reaches some legal low point"),F.AwaitLow()))return false;
    const auto Low=F.State();
    TestTrue(TEXT("Low clock begins only at legal actual Z20"),Low.Position.Z==20&&F.Enemy->JumpHeight==20
        &&Low.LowStartedAt>=A.ActiveAt&&Low.LowReadyAt==Low.LowStartedAt+1.8&&Low.PendingLow);
    const double X=Low.Position.X;F.AdvanceTo(Low.LowReadyAt-.001);
    TestTrue(TEXT("Blocked attack still owes full anchored low recovery"),F.State().Position.X==X&&F.State().Position.Z==20
        &&F.State().PendingLow&&F.State().NextAttackId==2&&F.Player->Health==100);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoneBatFramePartition,
    "CodexDungeon.Content.StoneBatGameIntegration.CentralLongFrameMatchesSplitMotionAndSingleHit",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoneBatFramePartition::RunTest(const FString& Parameters)
{
    FBatGameWorld Long(this),Split(this);if(!Long.Create()||!Split.Create())return false;
    if(!TestTrue(TEXT("Both genuine central AIs accept their first action"),Long.AwaitAction()&&Split.AwaitAction()))return false;
    const auto A=Long.State().Action;const auto B=Split.State().Action;
    if(!TestTrue(TEXT("Same source observations yield same accepted action time"),A.Start==B.Start&&A.Kind==B.Kind))return false;
    const double End=A.NominalEnd;
    if(!Long.AdvanceTo(End))return false;
    while(Split.Game->GetSimulationTime()+.017<End)Split.Game->Tick(.017f);
    if(!Split.AdvanceTo(End))return false;
    TestTrue(TEXT("Actual motion/recovery/attack identity is frame-partition invariant"),Long.State().Phase==Bat::EPhase::HighIdle
        &&Split.State().Phase==Bat::EPhase::HighIdle&&BatNear(Long.State().Position.X,Split.State().Position.X,1.e-7)
        &&Long.State().Position.Z==90&&Split.State().Position.Z==90&&Long.Enemy->JumpHeight==90&&Split.Enemy->JumpHeight==90
        &&Long.State().LowStartedAt==Split.State().LowStartedAt&&Long.State().LowReadyAt==Split.State().LowReadyAt
        &&Long.State().NextAttackId==Split.State().NextAttackId);
    TestTrue(TEXT("Moving Peck commits one real fractional-time player hit in either frame split"),Long.Player->Health==88
        &&Split.Player->Health==88&&Long.State().HitReceipts.size()==1&&Split.State().HitReceipts.size()==1
        &&Long.Events(Bat::EEventKind::Hit)==1&&Split.Events(Bat::EEventKind::Hit)==1
        &&BatNear(Long.State().HitReceipts[0].AtTime,Split.State().HitReceipts[0].AtTime,1.e-7));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoneBatInterruptedObligation,
    "CodexDungeon.Content.StoneBatGameIntegration.RealPoiseBreakKeepsUnfinishedLowObligation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoneBatInterruptedObligation::RunTest(const FString& Parameters)
{
    FBatGameWorld F(this);if(!F.Create())return false;
    if(!TestTrue(TEXT("Normal central AI accepts actual air action"),F.AwaitAction()))return false;
    const auto A=F.State().Action;if(!F.AdvanceTo(A.Start+.2))return false;
    F.Enemy->ApplyCombatHit(1.15f,F.Player,1.f);
    TestTrue(TEXT("Nonpoise actual HP loss preserves accepted air attack"),BatNear(F.State().HP,54,.0002)
        &&F.State().Action.InProgress&&!F.State().Action.Interrupted&&F.State().PendingLow);
    if(!F.AdvanceTo(F.Game->GetSimulationTime()+.01))return false;F.Enemy->ApplyCombatHit(1.15f,F.Player,25.f);
    const auto Broken=F.State();
    if(!TestTrue(TEXT("Actual accumulated poise25 interrupts without clearing low debt"),Broken.Phase==Bat::EPhase::Stunned
        &&Broken.Action.Interrupted&&Broken.PendingLow&&Broken.LowStartedAt<0&&Broken.Position.Z==90&&BatNear(Broken.HP,53,.0002)))return false;
    F.AdvanceTo(Broken.StunUntil-.001);
    TestTrue(TEXT("High hurt time cannot masquerade as a low recovery clock"),F.State().Position.Z==90&&F.State().LowStartedAt<0&&F.State().PendingLow);
    if(!TestTrue(TEXT("After real hurt the same actor continuously reaches legal low"),F.AwaitLow()))return false;
    const auto Low=F.State();
    TestTrue(TEXT("Delayed actual arrival starts a fresh full1.8 low obligation with old CD"),Low.Position.Z==20
        &&Low.LowStartedAt>=Broken.StunUntil&&Low.LowReadyAt==Low.LowStartedAt+1.8&&Low.PeckReadyAt==A.CooldownDeadline
        &&Low.Action.AttackId==A.AttackId&&Low.Action.Interrupted&&!Low.Action.Emitted);
    F.AdvanceTo(Low.LowReadyAt-.001);
    TestTrue(TEXT("One millisecond before real low end actor remains anchored and pending"),F.State().PendingLow
        &&F.State().Position.X==Low.Position.X&&F.State().Position.Y==Low.Position.Y&&F.State().Position.Z==20);
    F.AdvanceTo(Low.LowReadyAt+.3);
    TestTrue(TEXT("Only fulfilled low plus rise completes original interrupted attack"),!F.State().PendingLow&&!F.State().Action.InProgress
        &&F.State().Position.Z==90&&F.State().NextAttackId==2&&F.Player->Health==100&&F.Events(Bat::EEventKind::PoiseBroken)==1);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FStoneBatMixedGroundBodyAdmission,
    "CodexDungeon.Content.StoneBatGameIntegration.MixedChargeCannotBlockBeforeActualBatZ40",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FStoneBatMixedGroundBodyAdmission::RunTest(const FString& Parameters)
{
    FBatGameWorld F(this);if(!F.Create({170,0}))return false;
    F.Game->Tick(.001f);
    if(!TestTrue(TEXT("Real first bat wake supplies the actual encounter clock"),F.State().Phase==Bat::EPhase::Waking&&F.State().WakeEnd>=0.))return false;
    // Initial encounter admission, not a clock or action edit. The formal wake
    // and eligible-idle durations predict when to admit the second real actor.
    const double AdmissionAt=F.State().WakeEnd+2.4+.8-1.75+.15;
    if(!TestTrue(TEXT("Reach ordinary late enemy admission"),F.AdvanceTo(AdmissionAt)))return false;
    auto Knight=F.World->SpawnActor<ADungeonFighter>();if(!TestNotNull(TEXT("Real mixed encounter knight actor"),Knight))return false;
    Knight->bEnemy=true;Knight->bAIEnabled=false;Knight->SetActorTickEnabled(false);Knight->ResetFighter({155,0});F.Game->Enemies.Add(Knight);
    F.Game->Tick(.001f); // Existing normal central admission allocates this Run ID.
    const uint64 KnightId=Knight->GetRuntimeEntityId();
    if(!TestTrue(TEXT("Mixed knight receives existing Run allocator identity and genuine initial kernel"),KnightId>F.Enemy->GetRuntimeEntityId()
        &&KnightId<(uint64(1)<<63)&&Knight->InitializeStoneKnight(KnightId,F.Game->GetSimulationTime())))return false;
    for(int32 I=0;I<220&&(!F.State().Action.InProgress||!Knight->GetStoneKnightDriver()->State().Action.InProgress);++I)F.Game->Tick(.01f);
    if(!TestTrue(TEXT("Both real AIs choose normal Peck and charge without forced driver starts"),F.State().Action.InProgress
        &&F.State().Action.Kind==Bat::EAttack::Peck&&Knight->GetStoneKnightDriver()->State().Action.InProgress
        &&Knight->GetStoneKnightDriver()->State().Action.Kind==DungeonStoneKnight::EAttack::Charge))return false;
    if(!F.AdvanceTo(FMath::Max(F.State().Action.LockAt,Knight->GetStoneKnightDriver()->State().Action.LockAt)))return false;
    const auto Peck=F.State().Action;const auto Charge=Knight->GetStoneKnightDriver()->State().Action;
    const double Gate=Peck.ActiveAt+(Peck.ActiveEnd-Peck.ActiveAt)*(90.-40.)/70.;
    const double Begin=FMath::Max(Peck.ActiveAt,Charge.ActiveAt);
    const double BatSpeed=(Peck.Endpoint.X-Peck.Origin.X)/(Peck.ActiveEnd-Peck.ActiveAt);
    const double BatAtBegin=Peck.Origin.X+BatSpeed*(Begin-Peck.ActiveAt);
    const double KnightAtBegin=Charge.Origin.X+Charge.Direction.X*620.*(Begin-Charge.ActiveAt);
    const double RelativeSpeed=-(Charge.Direction.X*620.-BatSpeed);
    const double XYEntry=Begin+(KnightAtBegin-BatAtBegin-40.)/RelativeSpeed;
    const double HeightAtXY=90.-70.*(XYEntry-Peck.ActiveAt)/(Peck.ActiveEnd-Peck.ActiveAt);
    if(!TestTrue(TEXT("Actual locked paths cross40-wide XY body sum while the bat is still legally above40"),Peck.Locked&&Charge.Locked
        &&Charge.Direction.X==-1.&&RelativeSpeed>0.&&XYEntry>Begin&&XYEntry<Gate&&HeightAtXY>40.&&Gate<Peck.ActiveEnd))return false;
    if(!TestTrue(TEXT("Reach the ordinary interval preceding the body-height gate"),F.AdvanceTo(Gate-.004)))return false;
    const double Before=F.Game->GetSimulationTime();const bool Advanced=F.AdvanceTo(Gate+.001);
    const auto& Actual=Knight->GetStoneKnightDriver()->State().Action;
    AddInfo(FString::Printf(TEXT("Mixed body: before=%.17g after=%.17g xyEntry=%.17g batHeightAtXY=%.17g z40Gate=%.17g batZ=%.17g knightStop=%d stopAt=%.17g"),
        Before,F.Game->GetSimulationTime(),XYEntry,HeightAtXY,Gate,F.State().Position.Z,int32(Actual.Stop),Actual.ActiveEnd));
    TestTrue(TEXT("Real central mixed sweep advances across the bat height boundary without a repeated zero-time phantom contact"),Advanced&&F.Game->GetSimulationTime()>Before);
    TestTrue(TEXT("A real knight body stop cannot precede the bat actual ground-body admission"),Actual.Stop!=DungeonStoneKnight::EStop::Body||Actual.ActiveEnd>=Gate);
    {
        // Independent positive control added after the preserved mixed RED:
        // ignoring every bat body must never make the new guard pass.
        FBatGameWorld Low(this);if(!Low.Create({60,0})||!TestTrue(TEXT("Positive control starts a genuine normal bat action"),Low.AwaitAction()))return false;
        if(!Low.AdvanceTo(Low.State().Action.ActiveEnd))return false;
        if(!TestTrue(TEXT("Positive control observes real legal low20 and full recovery"),Low.State().Position.Z==20.&&Low.State().PendingLow
            &&Low.State().LowStartedAt>=0.&&Low.State().LowReadyAt==Low.State().LowStartedAt+1.8))return false;
        const auto Start=Low.Player->GetGroundPosition(),Body=Low.Enemy->GetGroundPosition();
        Low.Player->MoveOnGround({1,0},.4f);const auto End=Low.Player->GetGroundPosition();
        TestTrue(TEXT("Actual low20 bat blocks normal player movement at formal16+18 body half widths"),End.X>Start.X
            &&End.X<=Body.X-34.&&End.X<Start.X+Low.Player->GetMoveSpeed()*.4&&Low.State().Position.Z==20.);
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FDungeonManualWeaponPreviewAdmission,
    "CodexDungeon.Content.ManualWeaponPreview.RealSourceEnterPickupAndRestart",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FDungeonManualWeaponPreviewAdmission::RunTest(const FString& Parameters)
{
    FBatGameWorld F(this);if(!F.Create({0,0},false))return false;
    auto Controller=F.World->SpawnActor<APlayerController>();if(!TestNotNull(TEXT("Actual manual player controller"),Controller))return false;
    const auto BeforeRegistration=UGameplayStatics::GetPlayerController(F.Game,0);
    AddInfo(FString::Printf(TEXT("Manual controller registration: actorsInitialized=%d beforeResolverIsNull=%d beforeResolverIsSpawned=%d"),
        int32(F.World->AreActorsInitialized()),int32(BeforeRegistration==nullptr),int32(BeforeRegistration==Controller)));
    // This isolated physics world has not run InitializeActorsForPlay. Match
    // the real AController::PostInitializeComponents registration, so the
    // GameMode and the possessed Fighter observe the same actual controller.
    F.World->AddController(Controller);
    if(!TestTrue(TEXT("Normal GameMode controller resolver sees the registered manual controller"),UGameplayStatics::GetPlayerController(F.Game,0)==Controller))return false;
    Controller->Possess(F.Player);if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
    if(!TestTrue(TEXT("Actual local controller possesses the bound player"),Controller->IsLocalController()&&F.Player->GetController()==Controller))return false;
    const auto InputFrame=[&](float Dt)
    {F.Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);};
    const auto Key=[&](FKey K,bool Down)
    {Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));Controller->PlayerInput->Tick(.005f);
        TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);return Controller->IsInputKeyDown(K)==Down;};
    if(!TestTrue(TEXT("Explicit manual preview API admits a real QA Run"),F.Game->BeginManualWeaponPreview()))return false;
    const auto Initial=F.Game->GetEquipmentView();
    if(!TestTrue(TEXT("Manual preview begins bound starterSWD without armor and preserves the Enter gate"),Initial.Bound
        &&Initial.Config==EDungeonEquipmentRunConfig::IntegrationPreview&&Initial.ActiveSlot==0&&Initial.Slots[0].ContentId==TEXT("WPN-SWD-001")
        &&Initial.Slots[0].InstanceId==1&&!Initial.Slots[1].InstanceId&&!Initial.Slots[2].InstanceId&&F.Player->ArmorId.IsEmpty()
        &&F.Game->bWaitingForStart&&F.Game->GetSimulationTime()==0.))return false;
    if(!TestTrue(TEXT("Exactly one explicit QA source and one existing stone knight are admitted"),F.Game->GetEquipmentSources().Num()==1&&F.Game->Enemies.Num()==1))return false;
    const auto Source=F.Game->GetEquipmentSources()[0];auto Knight=F.Game->Enemies[0].Get();
    if(!TestTrue(TEXT("Manual source is genuinely registered loadedXBW at a legal normal E position"),Source.LogicalKey==TEXT("qa.manual.weapon.xbw")
        &&Source.Item.ContentId=="WPN-XBW-001"&&Source.Item.Ammo==1.&&Source.Settled&&!Source.Consumed&&Source.InstanceId>1
        &&FMath::Abs(Source.Position.X-F.Player->GetGroundPosition().X)<=80.&&FMath::Abs(Source.Position.Y-F.Player->GetGroundPosition().Y)<=40.))return false;
    if(!TestTrue(TEXT("Only the actual old knight uses the current Run allocator and no bat appears"),IsValid(Knight)&&Knight->GetStoneKnightDriver()
        &&!Knight->GetStoneBatDriver()&&Knight->GetRuntimeEntityId()>Initial.OwnerId&&Knight->GetRuntimeEntityId()<(uint64(1)<<63)
        &&Knight->GetStoneKnightDriver()->State().EntityId==Knight->GetRuntimeEntityId()&&Knight->Health==110&&!Knight->IsActorTickEnabled()))return false;
    const auto NextActor=F.Game->GetWeaponWorldState().NextEntityId;
    for(int32 I=0;I<8;++I){F.Game->GetEquipmentView();F.Game->GetEquipmentSources();Knight->GetRuntimeEntityId();}
    TestTrue(TEXT("Duplicate manual initialization and reads allocate no instance, source or actor identity"),F.Game->BeginManualWeaponPreview()
        &&F.Game->GetEquipmentView().RunGuid==Initial.RunGuid&&F.Game->GetEquipmentView().NextInstanceId==Initial.NextInstanceId
        &&F.Game->GetEquipmentView().NextSourceId==Initial.NextSourceId&&F.Game->GetWeaponWorldState().NextEntityId==NextActor
        &&F.Game->GetEquipmentSources().Num()==1&&F.Game->Enemies.Num()==1);
    if(!Key(EKeys::E,true))return false;InputFrame(.005f);Key(EKeys::E,false);InputFrame(.005f);
    TestTrue(TEXT("Normal E before Enter cannot consume a source or advance the manual clock"),F.Game->bWaitingForStart
        &&F.Game->GetSimulationTime()==0.&&!F.Game->GetEquipmentView().Action.Active&&!F.Game->GetEquipmentSources()[0].Consumed);
    if(!Key(EKeys::Enter,true))return false;
    if(!TestTrue(TEXT("Actual registered controller has a fresh Enter edge before the GameMode tick"),Controller->WasInputKeyJustPressed(EKeys::Enter)
        &&UGameplayStatics::GetPlayerController(F.Game,0)==Controller))return false;
    InputFrame(.005f);Key(EKeys::Enter,false);InputFrame(.005f);
    TestTrue(TEXT("Normal Enter opens the actual manual simulation"),!F.Game->bWaitingForStart&&F.Game->GetSimulationTime()>0.);
    if(!Key(EKeys::E,true))return false;InputFrame(.005f);Key(EKeys::E,false);InputFrame(.005f);
    const auto Pickup=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Normal E accepts genuine .35 empty-slot weapon pickup"),Pickup.Active&&Pickup.Kind==EDungeonEquipmentActionKind::PickupWeapon
        &&Pickup.SourceId==Source.SourceId&&Pickup.InstanceId==Source.InstanceId&&Pickup.Slot==1&&Pickup.Deadline==Pickup.Start+.35))return false;
    F.AdvanceTo(std::nextafter(Pickup.Deadline,-std::numeric_limits<double>::infinity()));
    TestTrue(TEXT("Last representable time before pickup deadline preserves ground source and starter"),F.Game->GetEquipmentView().Action.Active
        &&!F.Game->GetEquipmentSources()[0].Consumed&&F.Game->GetEquipmentView().ActiveSlot==0&&!F.Game->GetEquipmentView().Slots[1].InstanceId);
    if(!TestTrue(TEXT("Reach actual normal pickup endpoint"),F.AdvanceTo(Pickup.Deadline)))return false;
    const auto Acquired=F.Game->GetEquipmentView();
    TestTrue(TEXT("Exact .35 endpoint transfers the same loaded instance and keeps original sword slot0"),!Acquired.Action.Active&&Acquired.ActiveSlot==1
        &&Acquired.Slots[0].InstanceId==Initial.Slots[0].InstanceId&&Acquired.Slots[1].InstanceId==Source.InstanceId
        &&Acquired.Slots[1].ContentId==TEXT("WPN-XBW-001")&&Acquired.Slots[1].Ammo==1.&&F.Game->GetEquipmentSources()[0].Consumed
        &&F.Player->GetWeaponActionsState().EquippedId==Source.InstanceId);
    if(!Key(EKeys::R,true))return false;InputFrame(.005f);Key(EKeys::R,false);InputFrame(.005f);
    const auto Restarted=F.Game->GetEquipmentView();
    TestTrue(TEXT("Normal R creates one fresh Run, restores starter and registers the QA source once behind Enter"),Restarted.RunGuid!=Initial.RunGuid
        &&Restarted.Bound&&Restarted.ActiveSlot==0&&Restarted.Slots[0].InstanceId==1&&!Restarted.Slots[1].InstanceId&&!Restarted.Slots[2].InstanceId
        &&F.Game->bWaitingForStart&&F.Game->GetSimulationTime()==0.&&F.Game->GetEquipmentSources().Num()==1&&!F.Game->GetEquipmentSources()[0].Consumed
        &&F.Game->GetEquipmentSources()[0].Item.Ammo==1.&&F.Game->Enemies.Num()==1&&F.Game->Enemies[0]->GetStoneKnightDriver()
        &&!F.Game->Enemies[0]->GetStoneBatDriver()&&F.Game->GetWeaponWorldState().NextEntityId==NextActor);
    return true;
}
#endif
