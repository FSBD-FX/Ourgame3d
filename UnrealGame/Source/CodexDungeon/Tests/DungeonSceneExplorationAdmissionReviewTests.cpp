#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonSceneObjects.h"
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
bool SceneNear(double A,double B,double T=.0002){return std::abs(A-B)<=T;}
struct FSceneReviewWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;ADungeonFighter* Knight=nullptr;
    APlayerController* Controller=nullptr;FAutomationTestBase* Test=nullptr;
    explicit FSceneReviewWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FSceneReviewWorld(){if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage){Test->AddError(FString::Printf(TEXT("Scene independent fixture failed at %s"),Stage));return false;}
    bool Create()
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
        if(!Game->BeginSceneExplorationPreview())return Fail(TEXT("real scene initialization"));
        const auto& Scene=Game->GetSceneRoomView();const auto& V=Game->GetEquipmentView();
        if(!Scene.Active||!V.Bound||Scene.RunGuid!=V.RunGuid||Scene.RoomInstanceId!=V.RoomInstanceId
            ||Game->GetSimulationTime()!=0.||!Game->bWaitingForStart||Game->Enemies.Num()!=1
            ||!Player->GetGroundPosition().Equals(Scene.Layout.Entry,1.e-7))return Fail(TEXT("authored initial scene facts"));
        Knight=Game->Enemies[0];
        if(!Knight||!Knight->GetStoneKnightDriver()||Knight->Health!=110.f)return Fail(TEXT("initial knight"));
        // Explicit root-authorized initialization-only fixture. No live HP,
        // position, action, source ownership or room-clear mutation follows.
        Knight->bAIEnabled=false;
        return true;
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);
    }
    bool Key(FKey K,bool Down)
    {
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);return Controller->IsInputKeyDown(K)==Down;
    }
    bool Pulse(FKey K)
    {if(!Key(K,true))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool Start()
    {return Pulse(EKeys::Enter)&&!Game->bWaitingForStart&&Game->GetSimulationTime()>0.;}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return false;
        for(int32 I=0;I<64&&Game->GetSimulationTime()<At;++I)
        {
            const double Before=Game->GetSimulationTime(),Remaining=At-Before;float Dt=float(Remaining);
            if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);if(!(Dt>0))return false;
            Game->Tick(Dt);if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
    bool MoveTo(FVector2D Goal)
    {
        for(int32 Axis=0;Axis<2;++Axis)for(int32 I=0;I<80;++I)
        {
            const auto P=Player->GetGroundPosition();const double D=Axis?Goal.Y-P.Y:Goal.X-P.X;
            if(std::abs(D)<.002)break;
            const float Dt=float(FMath::Min(std::abs(D)/Player->GetMoveSpeed(),.25));
            Player->MoveOnGround(Axis?FVector2D(0,FMath::Sign(D)):FVector2D(FMath::Sign(D),0),Dt);
            if(Player->GetGroundPosition().Equals(P,1.e-8))return false;
        }
        Frame(.005f);return Player->GetGroundPosition().Equals(Goal,.003);
    }
    FDungeonEquipmentRegistration Register(const TCHAR* KeyName,const char* Id,FVector2D Position,double Ammo=0.)
    {DungeonEquipmentInventory::FItem I;I.ContentId=Id;I.Ammo=Ammo;return Game->RegisterEquipmentSource(KeyName,I,Position);}
    const FDungeonEquipmentSourceView* Source(uint64 Id)const
    {for(const auto& S:Game->GetEquipmentSources())if(S.SourceId==Id)return &S;return nullptr;}
    const DungeonWeaponActions::FInstance* Instance(uint64 Id)const
    {for(const auto& I:Player->GetWeaponActionsState().Instances)if(I.InstanceId==Id)return &I;return nullptr;}
    bool FinishEquipment()
    {const double End=Player->GetEquipmentActionDeadline();return End>Game->GetSimulationTime()&&AdvanceTo(End)&&!Game->GetEquipmentView().Action.Active;}
    bool Acquire(uint64 Id)
    {
        if(!Pulse(EKeys::E))return false;const auto A=Game->GetEquipmentView().Action;
        return A.Active&&A.SourceId==Id&&FinishEquipment()&&Source(Id)&&Source(Id)->Consumed;
    }
    bool ClearByRealSword()
    {
        if(Game->GetEquipmentView().ActiveSlot!=0)
            if(!Pulse(EKeys::Q)||!FinishEquipment()||Game->GetEquipmentView().ActiveSlot!=0)return false;
        if(!MoveTo({Knight->GetGroundPosition().X-70.,Knight->GetGroundPosition().Y}))return false;
        for(int32 I=0;I<24&&!Knight->bDead;++I)
        {
            Player->BeginAttack();const auto A=Player->GetMeleeCombatState().Action;
            if(!A.Active||A.StartedAirborne||!AdvanceTo(A.End))return false;
        }
        return Knight->bDead&&Knight->GetStoneKnightDriver()->State().HP==0.&&Game->bRoomCleared;
    }
    const FDungeonSceneObjectView* Object(EDungeonSceneObjectKind Kind)const
    {for(const auto& O:Game->GetSceneRoomView().Objects)if(O.Kind==Kind)return &O;return nullptr;}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneReviewSourcePriority,
    "CodexDungeon.Content.SceneAdmissionReview.BoundSourceSelectionConsumesFreshEBeforeDoor",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneReviewSourcePriority::RunTest(const FString& Parameters)
{
    FSceneReviewWorld F(this);if(!F.Create())return false;const auto Layout=F.Game->GetSceneRoomView().Layout;
    const auto X=F.Register(TEXT("qa.scene-review.entry-xbw"),"WPN-XBW-001",Layout.Entry+FVector2D(40,0),1.);
    const auto G=F.Register(TEXT("qa.scene-review.exit-gsw"),"WPN-GSW-001",Layout.Exit);
    if(!TestTrue(TEXT("Created explicit real QA sources before simulation"),X.Ok()&&G.Ok()&&F.Start()&&F.Acquire(X.SourceId)))return false;
    if(!TestTrue(TEXT("Actual SWD contacts clear the real admitted knight"),F.ClearByRealSword()))return false;
    if(!TestTrue(TEXT("Normal swept movement reaches the actual door and full-slot source"),F.MoveTo(Layout.Exit)))return false;
    const auto Before=F.Game->GetEquipmentView();const int32 RoomNumber=F.Game->RoomNumber;
    if(!F.Pulse(EKeys::E))return false;
    TestTrue(TEXT("Bound E opens real equipment selection before an overlapping cleared exit"),F.Game->GetEquipmentView().NeedsSlotSelection
        &&F.Game->GetEquipmentView().SelectedSourceId==G.SourceId&&!F.Source(G.SourceId)->Consumed
        &&!F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==RoomNumber);
    if(!F.Pulse(EKeys::E))return false;
    TestTrue(TEXT("Another fresh E cannot confirm the slot or also open a scene door"),F.Game->GetEquipmentView().NeedsSlotSelection
        &&!F.Game->GetEquipmentView().Action.Active&&!F.Source(G.SourceId)->Consumed
        &&!F.Game->GetSceneInteractionView().Pending&&F.Game->GetEquipmentView().RoomInstanceId==Before.RoomInstanceId);
    if(!F.Pulse(EKeys::Escape))return false;
    TestTrue(TEXT("Normal cancel preserves actual source and both held instances"),!F.Game->GetEquipmentView().NeedsSlotSelection
        &&!F.Source(G.SourceId)->Consumed&&F.Game->GetEquipmentView().Slots[0].InstanceId==Before.Slots[0].InstanceId
        &&F.Game->GetEquipmentView().Slots[1].InstanceId==Before.Slots[1].InstanceId&&F.Game->RoomNumber==RoomNumber);
    if(!F.Pulse(EKeys::E)||!F.Pulse(EKeys::Right)||!F.Pulse(EKeys::Enter))return false;
    const auto Pickup=F.Game->GetEquipmentView().Action;
    if(!TestTrue(TEXT("Fresh Enter accepts only the chosen real replacement"),Pickup.Active&&Pickup.SourceId==G.SourceId&&Pickup.Slot==1
        &&Pickup.Deadline==Pickup.Start+.35&&!F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==RoomNumber))return false;
    if(!F.FinishEquipment())return false;
    TestTrue(TEXT("Completed replacement consumes the same source without consuming an exit confirmation"),F.Source(G.SourceId)->Consumed
        &&F.Game->GetEquipmentView().Slots[1].InstanceId==G.InstanceId&&F.Game->GetEquipmentView().RoomInstanceId==Before.RoomInstanceId
        &&F.Game->RoomNumber==RoomNumber&&!F.Game->GetSceneInteractionView().Pending);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneReviewConfirmation,
    "CodexDungeon.Content.SceneAdmissionReview.GroundPermissionCancelAndFreshEnterConsumeOneConfirmation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneReviewConfirmation::RunTest(const FString& Parameters)
{
    FSceneReviewWorld F(this);if(!F.Create()||!F.Start()||!TestTrue(TEXT("Real normal sword clear before door permission"),F.ClearByRealSword()))return false;
    const auto Initial=F.Game->GetSceneRoomView();const int32 Number=F.Game->RoomNumber;
    if(!F.MoveTo(Initial.Layout.Exit))return false;
    F.Player->StartJump();if(!TestTrue(TEXT("Actual jump starts before attempted door interaction"),F.Player->GetVerticalVelocity()>0.f))return false;
    if(!F.Pulse(EKeys::E))return false;
    TestTrue(TEXT("Airborne normal E cannot create a cleared-door confirmation"),F.Player->JumpHeight>0.f
        &&!F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==Number);
    if(!F.AdvanceTo(F.Game->GetSimulationTime()+.8)||!F.Pulse(EKeys::E))return false;
    const auto Pending=F.Game->GetSceneInteractionView();
    if(!TestTrue(TEXT("Real grounded idle fresh E opens exactly the current exit confirmation"),Pending.Pending&&Pending.NeedsConfirmation
        &&Pending.Kind==EDungeonSceneInteractionKind::Exit&&Pending.RoomInstanceId==Initial.RoomInstanceId
        &&F.Game->RoomNumber==Number&&F.Player->JumpHeight==0.f))return false;
    TestTrue(TEXT("Nonfresh confirm request cannot consume the pending transaction"),!F.Game->ConfirmSceneInteraction(false)
        &&F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==Number);
    if(!F.Pulse(EKeys::Escape))return false;
    TestTrue(TEXT("Normal Esc cancels pending exit without changing room or object state"),!F.Game->GetSceneInteractionView().Pending
        &&F.Game->GetSceneRoomView().RoomInstanceId==Initial.RoomInstanceId&&F.Game->RoomNumber==Number);
    if(!F.Pulse(EKeys::Enter))return false;
    TestTrue(TEXT("Fresh Enter without a pending object does not open a different door"),!F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==Number);
    if(!F.Pulse(EKeys::E)||!F.Key(EKeys::Enter,true))return false;
    F.Frame(.005f);F.Frame(.1f);if(!F.Key(EKeys::Enter,false))return false;F.Frame(.005f);
    TestTrue(TEXT("One held Enter consumes only the original confirmation and cannot skip another room"),F.Game->RoomNumber==Number+1
        &&F.Game->GetSceneRoomView().RunGuid==Initial.RunGuid&&F.Game->GetSceneRoomView().RoomInstanceId==Initial.RoomInstanceId+1
        &&!F.Game->GetSceneInteractionView().Pending&&F.Player->GetGroundPosition().Equals(Initial.Layout.Entry,.003));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneReviewTransfer,
    "CodexDungeon.Content.SceneAdmissionReview.RealExitKeepsSpentFocusAbsoluteCooldownAndRoomObjectHistory",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneReviewTransfer::RunTest(const FString& Parameters)
{
    FSceneReviewWorld F(this);if(!F.Create())return false;const auto Initial=F.Game->GetSceneRoomView();
    const auto Staff=F.Register(TEXT("qa.scene-review.entry-stf"),"WPN-STF-001",Initial.Layout.Entry+FVector2D(40,0));
    if(!TestTrue(TEXT("Creation-time real staff source and normal initial entry"),Staff.Ok()&&F.Start()&&F.ClearByRealSword()))return false;
    if(!F.MoveTo({Initial.Layout.Entry.X,220.})||!F.MoveTo(Initial.Layout.Survey))return false;
    const int32 Coins=F.Player->Coins;const int32 Pickups=F.Game->Pickups.Num();const auto BeforeSurvey=F.Game->GetEquipmentView();
    if(!F.Pulse(EKeys::E))return false;const auto Survey=F.Object(EDungeonSceneObjectKind::Survey);
    if(!TestTrue(TEXT("Actual optional survey belongs to this room and pays no extra income"),Survey&&Survey->Surveyed&&Survey->SurveyCount==1
        &&Survey->RoomInstanceId==Initial.RoomInstanceId&&F.Player->Coins==Coins&&F.Game->Pickups.Num()==Pickups
        &&F.Game->GetEquipmentView().NextInstanceId==BeforeSurvey.NextInstanceId))return false;
    const uint64 SurveyId=Survey->ObjectId;
    if(!F.MoveTo(Initial.Layout.Entry)||!F.Acquire(Staff.SourceId))return false;
    if(!F.MoveTo({665.,0.})||!F.Pulse(EKeys::E))return false;
    TestTrue(TEXT("The old600 half-plane is not the new actual exit"),F.Game->GetSceneRoomView().RoomInstanceId==Initial.RoomInstanceId
        &&F.Game->RoomNumber==1&&!F.Game->GetSceneInteractionView().Pending);
    if(!F.MoveTo(Initial.Layout.Exit)||!F.Pulse(EKeys::K))return false;
    const auto Action=F.Player->GetWeaponActionsState().Action;
    if(!TestTrue(TEXT("Normal staff K begins on the acquired instance before transfer"),Action.Active
        &&Action.Type==DungeonWeaponActions::EAction::Skill&&Action.InstanceId==Staff.InstanceId))return false;
    if(!F.AdvanceTo(Action.End))return false;
    const auto& WA=F.Player->GetWeaponActionsState();const auto Runtime=F.Instance(Staff.InstanceId);
    if(!TestNotNull(TEXT("Actual staff runtime instance"),Runtime))return false;
    const auto Instance=*Runtime;const double Focus=WA.Budget.Focus,HP=F.Player->Health,Clock=F.Game->GetSimulationTime();
    int32 Spends=0;for(const auto& R:WA.FocusHistory)if(R.Kind==DungeonWeaponActions::EFocusChange::Emission&&R.Requested==24&&R.Applied==24)++Spends;
    if(!TestTrue(TEXT("Real skill emission spent24 and began the instance absolute7s cooldown"),Spends==1&&SceneNear(Focus,76.)
        &&SceneNear(Instance.CooldownDeadline,Action.LockAt+7.,1.e-12)))return false;
    const auto Inventory=F.Game->GetEquipmentView();
    if(!F.Pulse(EKeys::E))return false;
    if(!TestTrue(TEXT("Actual1180 door opens confirmation instead of replacing the Run"),F.Game->GetSceneInteractionView().Pending
        &&F.Game->GetSceneInteractionView().NeedsConfirmation&&F.Game->GetEquipmentView().RunGuid==Inventory.RunGuid
        &&F.Game->GetEquipmentView().RoomInstanceId==Initial.RoomInstanceId))return false;
    if(!F.Pulse(EKeys::Enter))return false;
    const auto& After=F.Game->GetEquipmentView();const auto& Room=F.Game->GetSceneRoomView();const auto Old=F.Game->FindSceneRoomView(Initial.RoomInstanceId);
    const auto AfterRuntime=F.Instance(Staff.InstanceId);const auto NewSurvey=F.Object(EDungeonSceneObjectKind::Survey);
    bool OldSurveyKept=false;if(Old)for(const auto& O:Old->Objects)if(O.ObjectId==SurveyId&&O.Kind==EDungeonSceneObjectKind::Survey)
        OldSurveyKept=O.RoomInstanceId==Initial.RoomInstanceId&&O.Surveyed&&O.SurveyCount==1;
    TestTrue(TEXT("Confirmed free exit keeps same player Run instances HP spentFocus and absoluteCD"),After.RunGuid==Inventory.RunGuid
        &&After.RoomInstanceId==Initial.RoomInstanceId+1&&Room.RunGuid==Inventory.RunGuid&&Room.RoomInstanceId==After.RoomInstanceId
        &&After.ActiveSlot==Inventory.ActiveSlot&&After.Slots[0].InstanceId==Inventory.Slots[0].InstanceId&&After.Slots[1].InstanceId==Staff.InstanceId
        &&AfterRuntime&&AfterRuntime->CooldownDeadline==Instance.CooldownDeadline&&AfterRuntime->Ammo==Instance.Ammo
        &&F.Player->Health==HP&&F.Player->GetWeaponActionsState().Budget.Focus==Focus&&F.Game->GetSimulationTime()>Clock
        &&F.Player->GetGroundPosition().Equals(Room.Layout.Entry,.003));
    TestTrue(TEXT("Old surveyed object remains old-room history while the new room has its own uninvestigated object"),OldSurveyKept
        &&NewSurvey&&NewSurvey->RoomInstanceId==After.RoomInstanceId&&!NewSurvey->Surveyed&&NewSurvey->SurveyCount==0
        &&F.Source(Staff.SourceId)&&F.Source(Staff.SourceId)->RoomInstanceId==Initial.RoomInstanceId&&F.Source(Staff.SourceId)->Consumed
        &&!F.Game->GetSceneInteractionView().Pending);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSceneReviewDodgePriority,
    "CodexDungeon.Content.SceneAdmissionReview.LegalDodgeOutranksPendingExitConfirmation",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSceneReviewDodgePriority::RunTest(const FString& Parameters)
{
    // Both edges enter one actual PlayerInput processing generation. Calling
    // the fixture Key helper twice would erase the first WasJustPressed edge.
    const auto PressPair=[](FSceneReviewWorld& F,FKey Other,FKey First=EKeys::LeftShift)
    {
        F.Controller->InputKey(FInputKeyParams(First,IE_Pressed,1.));
        F.Controller->InputKey(FInputKeyParams(Other,IE_Pressed,1.));
        F.Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        F.Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return F.Controller->WasInputKeyJustPressed(First)&&F.Controller->WasInputKeyJustPressed(Other);
    };
    for(const FKey Other:{EKeys::Enter,EKeys::E})
    {
        FSceneReviewWorld F(this);if(!F.Create()||!F.Start()||!F.ClearByRealSword())return false;
        const auto Scene=F.Game->GetSceneRoomView();const int32 Number=F.Game->RoomNumber;
        if(!F.MoveTo(Scene.Layout.Exit)||!F.Pulse(EKeys::E))return false;
        const auto Pending=F.Game->GetSceneInteractionView();const auto Before=F.Player->GetDodgeState();
        if(!TestTrue(TEXT("Real cleared grounded exit confirmation and ready idle dodge are the counterexample premise"),
            Pending.Pending&&Pending.NeedsConfirmation&&Pending.Kind==EDungeonSceneInteractionKind::Exit
            &&Before.Phase==DungeonDodge::EPhase::Idle&&Before.Time>=Before.ReadyAt
            &&Before.Time==F.Game->GetSimulationTime()&&F.Player->JumpHeight==0.f&&F.Player->CanStartAttack()))return false;
        if(!TestTrue(TEXT("Both Shift and lower-priority UI key are genuinely fresh in the same input batch"),PressPair(F,Other)))return false;
        F.Frame(.005f);
        const auto& After=F.Player->GetDodgeState();
        TestTrue(FString::Printf(TEXT("Legal fresh Shift outranks simultaneous %s and starts one real dodge"),*Other.ToString()),
            After.Phase==DungeonDodge::EPhase::Dodging&&After.NextActionId==Before.NextActionId+1
            &&After.Records.size()==Before.Records.size()+1);
        TestTrue(FString::Printf(TEXT("Legal dodge closes the exit layer without %s also confirming or changing rooms"),*Other.ToString()),
            !F.Game->GetSceneInteractionView().Pending&&F.Game->GetSceneRoomView().RoomInstanceId==Scene.RoomInstanceId
            &&F.Game->GetSceneRoomView().RunGuid==Scene.RunGuid&&F.Game->RoomNumber==Number);
        if(!F.Key(EKeys::LeftShift,false)||!F.Key(Other,false))return false;F.Frame(.005f);
    }
    {
        FSceneReviewWorld F(this);if(!F.Create()||!F.Start()||!F.ClearByRealSword())return false;
        const auto Scene=F.Game->GetSceneRoomView();const int32 Number=F.Game->RoomNumber;
        if(!F.MoveTo(Scene.Layout.Exit)||!F.Pulse(EKeys::LeftShift))return false;
        const auto Started=F.Player->GetDodgeState();
        if(!TestTrue(TEXT("A real normal Shift establishes the invalid-request cooldown fixture"),
            Started.Phase==DungeonDodge::EPhase::Dodging&&!Started.Records.empty()))return false;
        if(!F.AdvanceTo(Started.Records.back().End)||!F.MoveTo(Scene.Layout.Exit)||!F.Pulse(EKeys::E))return false;
        const auto Before=F.Player->GetDodgeState();const auto Pending=F.Game->GetSceneInteractionView();
        if(!TestTrue(TEXT("Actual completed dodge is idle but still on its unmodified cooldown beside the pending exit"),
            Before.Phase==DungeonDodge::EPhase::Idle&&Before.Time<Before.ReadyAt&&Pending.Pending&&Pending.NeedsConfirmation))return false;
        if(!F.Pulse(EKeys::LeftShift))return false;
        TestTrue(TEXT("Cooldown-invalid fresh Shift cannot close the pending exit or issue another dodge"),
            F.Game->GetSceneInteractionView().Pending&&F.Game->GetSceneInteractionView().NeedsConfirmation
            &&F.Game->GetSceneInteractionView().ObjectId==Pending.ObjectId&&F.Player->GetDodgeState().NextActionId==Before.NextActionId
            &&F.Player->GetDodgeState().Records.size()==Before.Records.size()&&F.Game->RoomNumber==Number
            &&F.Game->GetSceneRoomView().RoomInstanceId==Scene.RoomInstanceId);
    }
    for(const FKey WorldKey:{EKeys::SpaceBar,EKeys::J})
    {
        FSceneReviewWorld F(this);if(!F.Create()||!F.Start()||!F.ClearByRealSword())return false;
        const auto Scene=F.Game->GetSceneRoomView();const int32 Number=F.Game->RoomNumber;
        if(!F.MoveTo(Scene.Layout.Exit)||!F.Pulse(EKeys::E))return false;
        if(!TestTrue(TEXT("Real pending exit is grounded and idle before a competing legal jump or primary"),
            F.Game->GetSceneInteractionView().Pending&&F.Game->GetSceneInteractionView().NeedsConfirmation
            &&F.Player->JumpHeight==0.f&&F.Player->CanStartAttack()))return false;
        const auto NextAttack=F.Player->GetMeleeCombatState().NextAttackId;
        if(!TestTrue(TEXT("World request and Enter are genuinely fresh in the same input generation"),PressPair(F,EKeys::Enter,WorldKey)))return false;
        F.Frame(.005f);
        const auto& A=F.Player->GetMeleeCombatState().Action;
        const bool Accepted=WorldKey==EKeys::SpaceBar?(F.Player->JumpHeight>0.f&&F.Player->GetVerticalVelocity()>0.f)
            :(A.Active&&A.AttackId==NextAttack&&A.Stage==1&&A.Weapon==DungeonContentCombat::EWeapon::SWD001&&!A.StartedAirborne);
        TestTrue(FString::Printf(TEXT("Legal %s starts its real world action before simultaneous exit Enter"),*WorldKey.ToString()),Accepted);
        TestTrue(FString::Printf(TEXT("Accepted %s closes the layer without room travel from the same Enter"),*WorldKey.ToString()),
            !F.Game->GetSceneInteractionView().Pending&&F.Game->RoomNumber==Number
            &&F.Game->GetSceneRoomView().RoomInstanceId==Scene.RoomInstanceId&&F.Game->GetSceneRoomView().RunGuid==Scene.RunGuid);
        if(!F.Key(WorldKey,false)||!F.Key(EKeys::Enter,false))return false;F.Frame(.005f);
    }
    return true;
}
#endif
