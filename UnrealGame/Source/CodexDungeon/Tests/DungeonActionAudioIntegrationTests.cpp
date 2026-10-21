#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonHUD.h"
#include "../DungeonActionAudioFeedback.h"
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
namespace AudioWA=DungeonWeaponActions;
namespace AudioInventory=DungeonEquipmentInventory;
namespace AudioStats=DungeonEquipmentStats;
constexpr const TCHAR* DrawCue=TEXT("XBW_RELOAD_DRAW_01");
constexpr const TCHAR* InsertCue=TEXT("XBW_RELOAD_INSERT_01");
constexpr const TCHAR* CompleteCue=TEXT("XBW_RELOAD_COMPLETE_01");
constexpr const TCHAR* ClothCue=TEXT("EQUIP_ARMOR_CLOTH_01");
constexpr const TCHAR* MetalCue=TEXT("EQUIP_ARMOR_METAL_01");

struct FActionAudioWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;ADungeonHUD* HUD=nullptr;FAutomationTestBase* Test=nullptr;
    uint64 AcquiredInstance=0;
    explicit FActionAudioWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FActionAudioWorld()
    {if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage)
    {Test->AddError(FString::Printf(TEXT("Action-audio real fixture %s failed; equipment=%s"),Stage,
        Game?*Game->GetEquipmentView().FailureText:TEXT("No GameMode")));return false;}
    const AudioWA::FState& Actions()const{return Player->GetWeaponActionsState();}
    const AudioInventory::FState& Inventory()const{return *Game->GetEquipmentInventoryState();}
    const AudioWA::FInstance* Instance(uint64 Id=0)const
    {for(const auto& I:Actions().Instances)if(I.InstanceId==(Id?Id:Actions().EquippedId))return &I;return nullptr;}
    const FDungeonEquipmentSourceView* Source(uint64 Id)const
    {for(const auto& S:Game->GetEquipmentSources())if(S.SourceId==Id)return &S;return nullptr;}
    bool Key(FKey K,bool Down)
    {
        if(!Controller||!Controller->PlayerInput)return Fail(TEXT("input controller"));
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(K)==Down;
    }
    void Frame(float Dt)
    {
        Game->Tick(Dt);
        Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;
        Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);
        // The public actor tick is the actual production consumer. These tests
        // never create a Canvas, call DrawHUD, or inject a sound/journal entry.
        if(HUD)HUD->Tick(Dt);
    }
    bool Pulse(FKey K)
    {if(!Key(K,true))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return Fail(TEXT("monotonic exact deadline"));
        for(int32 N=0;N<64&&Game->GetSimulationTime()<At;++N)
        {
            const double Remaining=At-Game->GetSimulationTime();float Dt=float(Remaining);
            if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return Fail(TEXT("positive representable tick"));
            const double Before=Game->GetSimulationTime();Frame(Dt);
            if(Game->GetSimulationTime()<=Before)return Fail(TEXT("clock progress"));
        }
        return Game->GetSimulationTime()==At;
    }
    bool FinishEquipment(){return AdvanceTo(Player->GetEquipmentActionDeadline());}
    bool Face(double Facing)
    {const FKey K=Facing<0?EKeys::A:EKeys::D;if(!Key(K,true))return false;Frame(.01f);return Key(K,false)&&Player->Facing==Facing;}
    FDungeonEquipmentRegistration Register(const AudioInventory::FItem& Item)
    {
        const FString Name=FString::Printf(TEXT("qa.action-audio.source.%llu"),Game->GetEquipmentView().NextSourceId);
        return Game->RegisterEquipmentSource(Name,Item,Player->GetGroundPosition()+FVector2D(40,0));
    }
    bool Pickup(uint64 SourceId)
    {
        if(!Game->SelectEquipmentSource(SourceId)||!Pulse(EKeys::E))return Fail(TEXT("normal E source pickup"));
        if(Game->GetEquipmentView().NeedsSlotSelection&&!Pulse(EKeys::Enter))return Fail(TEXT("normal Enter replacement"));
        return Game->GetEquipmentView().Action.Active;
    }
    bool AcquireCrossbow(double Ammo,double ReloadSpeed=0.)
    {
        AudioInventory::FItem Item;Item.ContentId="WPN-XBW-001";Item.Ammo=Ammo;
        if(ReloadSpeed!=0.)
        {
            Item.Tier=5;Item.Package=ReloadSpeed>0?AudioStats::EPackage::Beneficial:AudioStats::EPackage::Cursed;
            Item.Affixes={{ReloadSpeed>0?"AFF-P-008":"AFF-N-006",25,{9,10}}};
        }
        const auto S=Register(Item);
        if(!S.Ok()||!Pickup(S.SourceId)||!FinishEquipment())return Fail(TEXT("real crossbow acquisition transaction"));
        AcquiredInstance=S.InstanceId;
        return Player->WeaponId==TEXT("WPN-XBW-001")&&Actions().EquippedId==AcquiredInstance
            &&Instance()&&Instance()->Ammo==Ammo&&Game->GetEquipmentView().Slots[1].InstanceId==AcquiredInstance;
    }
    bool Create(double Ammo=0.,double ReloadSpeed=0.)
    {
        if(!GEngine)return Fail(TEXT("engine"));
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
            .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false)
            .ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!World)return Fail(TEXT("real world"));
        GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
        World->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;
        URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(!World->SetGameMode(URL))return Fail(TEXT("authoritative game mode"));
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
        Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return Fail(TEXT("actors"));
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||UGameplayStatics::GetPlayerController(Game,0)!=Controller)return Fail(TEXT("registered real local controller"));
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        Game->bWaitingForStart=false;Game->bGameOver=false;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("fresh bound run"));
        HUD=World->SpawnActor<ADungeonHUD>();if(!HUD)return Fail(TEXT("actual HUD actor"));
        HUD->SetOwner(Controller);if(!HUD->HasActorBegunPlay())HUD->DispatchBeginPlay();
        // The normal first-tick tail seed happens before any tested action.
        HUD->Tick(0.f);
        if(!Test->TestTrue(TEXT("HUD initially observes this fresh run before inputs"),
            Game->GetActionAudioState().RunGuid==Game->GetEquipmentView().RunGuid
            &&Game->GetActionAudioState().Records.IsEmpty()&&HUD->GetActionAudioPlayReceipts().IsEmpty()))return false;
        return AcquireCrossbow(Ammo,ReloadSpeed);
    }
    int32 Facts(const FString& Cue,uint64 Action,uint64 InstanceId,uint64 Operation=0)const
    {
        int32 Count=0;for(const auto& R:Game->GetActionAudioState().Records)
            if(R.Cue==Cue&&R.ActionId==Action&&R.InstanceId==InstanceId&&R.OperationId==Operation)++Count;
        return Count;
    }
    int32 Requests(const FString& Cue,uint64 Action,uint64 InstanceId,uint64 Operation=0)const
    {
        int32 Count=0;for(const auto& R:HUD->GetActionAudioPlayReceipts())
            if(R.Source.Cue==Cue&&R.Source.ActionId==Action&&R.Source.InstanceId==InstanceId&&R.Source.OperationId==Operation)++Count;
        return Count;
    }
    void ExpectAudio(const FString& Cue,uint64 Action,uint64 InstanceId,double At,uint64 Operation=0,uint64 Revision=0)
    {
        Test->TestEqual(*(Cue+TEXT(" one actual authoritative fact")),Facts(Cue,Action,InstanceId,Operation),1);
        Test->TestEqual(*(Cue+TEXT(" one actual PlaySound2D request")),Requests(Cue,Action,InstanceId,Operation),1);
        const FDungeonActionAudioRecord* Fact=nullptr;
        const FDungeonActionAudioPlayRequest* Request=nullptr;
        for(const auto& R:Game->GetActionAudioState().Records)
            if(R.Cue==Cue&&R.ActionId==Action&&R.InstanceId==InstanceId&&R.OperationId==Operation)Fact=&R;
        for(const auto& R:HUD->GetActionAudioPlayReceipts())
            if(R.Source.Cue==Cue&&R.Source.ActionId==Action&&R.Source.InstanceId==InstanceId&&R.Source.OperationId==Operation)Request=&R;
        if(!Fact||!Request)return;
        const auto& V=Game->GetEquipmentView();const auto& P=Request->Source;
        const FString Name=TEXT("SW_AUD_")+Cue+TEXT("_v002");
        const FString ExpectedPath=TEXT("/Game/Production/FirstBatch/v024/AudioDedicated/")+Name+TEXT(".")+Name;
        Test->TestTrue(*(Cue+TEXT(" real run/room/owner and independent accepted deadline")),
            Fact->Sequence>0&&Fact->Sequence<Game->GetActionAudioState().NextSequence&&Fact->RunGuid==V.RunGuid
            &&Fact->RoomInstanceId==V.RoomInstanceId&&Fact->OwnerId==V.OwnerId&&Fact->AtTime==At
            &&Fact->Revision>0&&Fact->Revision<=V.Revision&&(!Revision||Fact->Revision==Revision));
        Test->TestTrue(*(Cue+TEXT(" request retains this exact source and new SoundWave path")),
            P.Sequence==Fact->Sequence&&P.Cue==Fact->Cue&&P.AtTime==Fact->AtTime&&P.RunGuid==Fact->RunGuid
            &&P.RoomInstanceId==Fact->RoomInstanceId&&P.OwnerId==Fact->OwnerId&&P.ActionId==Fact->ActionId
            &&P.InstanceId==Fact->InstanceId&&P.OperationId==Fact->OperationId&&P.Revision==Fact->Revision
            &&Request->SoundPath==ExpectedPath&&std::isfinite(Request->RequestedAt)&&Request->RequestedAt>=At
            &&Request->RequestedAt-At<=.25&&std::isfinite(Request->Volume)&&Request->Volume>0.f
            &&std::isfinite(Request->Pitch)&&Request->Pitch>0.f);
    }
    void ExpectNoAudio(const FString& Cue,const AudioWA::FAction& A)
    {
        Test->TestEqual(*(Cue+TEXT(" has no fact for the cancelled/unreached action")),Facts(Cue,A.ActionId,A.InstanceId),0);
        Test->TestEqual(*(Cue+TEXT(" has no request for the cancelled/unreached action")),Requests(Cue,A.ActionId,A.InstanceId),0);
    }
    void ExpectCompletedResource(const AudioWA::FAction& A)
    {
        int32 Count=0;
        for(const auto& R:Actions().WeaponRuntimeHistory)if(R.Kind==AudioWA::EWeaponMutation::ReloadCompleted
            &&R.Action.ActionId==A.ActionId&&R.Action.InstanceId==A.InstanceId)
        {
            ++Count;Test->TestTrue(TEXT("Complete sound is backed by a real successful same-action resource receipt"),
                R.AtTime==A.End&&R.Action.Type==AudioWA::EAction::Reload&&!R.Action.Active
                &&R.Action.Terminal==AudioWA::EEvent::ReloadCompleted&&R.BeforeAmmo==0.&&R.AfterAmmo==1.);
        }
        Test->TestEqual(TEXT("One actual ammo-refill receipt for the completed reload"),Count,1);
        Test->TestTrue(TEXT("Real same instance and inventory ammo commit exactly once"),Instance(A.InstanceId)
            &&Instance(A.InstanceId)->Ammo==1.&&Game->GetEquipmentView().Slots[1].InstanceId==A.InstanceId
            &&Game->GetEquipmentView().Slots[1].Ammo==1.);
    }
    void ExpectRepeatedHUDReadOnly()
    {
        const auto Before=Actions();const auto InvBefore=Inventory();const double At=Game->GetSimulationTime();
        const uint64 Sequence=Game->GetActionAudioState().NextSequence;
        const int32 FactsBefore=Game->GetActionAudioState().Records.Num(),RequestsBefore=HUD->GetActionAudioPlayReceipts().Num();
        for(int32 I=0;I<8;++I)HUD->Tick(0.f);
        Test->TestTrue(TEXT("Repeated production HUD consumption cannot spend, allocate, advance or replay"),
            Game->GetSimulationTime()==At&&Actions().NextActionId==Before.NextActionId&&Actions().NextEventId==Before.NextEventId
            &&Actions().NextImportReceiptId==Before.NextImportReceiptId&&Actions().NextFocusMutationId==Before.NextFocusMutationId
            &&Actions().Budget.Focus==Before.Budget.Focus&&Actions().Budget.ReservedFocus==Before.Budget.ReservedFocus
            &&Actions().Action.ActionId==Before.Action.ActionId&&Actions().Action.Active==Before.Action.Active
            &&Actions().WeaponRuntimeHistory.size()==Before.WeaponRuntimeHistory.size()
            &&Inventory().Revision==InvBefore.Revision&&Inventory().Operations.size()==InvBefore.Operations.size()
            &&Inventory().RuntimeUpdates.size()==InvBefore.RuntimeUpdates.size()
            &&Game->GetActionAudioState().NextSequence==Sequence&&Game->GetActionAudioState().Records.Num()==FactsBefore
            &&HUD->GetActionAudioPlayReceipts().Num()==RequestsBefore);
        for(const auto& I:Before.Instances)
            Test->TestTrue(TEXT("Repeated audio presentation preserves every actual instance ammo/cooldown"),Instance(I.InstanceId)
                &&Instance(I.InstanceId)->Ammo==I.Ammo&&Instance(I.InstanceId)->CooldownDeadline==I.CooldownDeadline);
    }
    bool ManualReload(AudioWA::FAction& Out)
    {
        if(!Pulse(EKeys::T))return false;Out=Actions().Action;
        return Out.Active&&Out.Type==AudioWA::EAction::Reload&&Out.InstanceId==AcquiredInstance;
    }
    bool AutoReload(AudioWA::FAction& Out)
    {
        if(!Pulse(EKeys::J))return false;const auto Shot=Actions().Action;
        if(!Shot.Active||Shot.Type!=AudioWA::EAction::Primary||!AdvanceTo(Shot.End))return false;
        Out=Actions().Action;
        return Out.Active&&Out.Type==AudioWA::EAction::Reload&&Out.Start==Shot.End&&Out.InstanceId==AcquiredInstance;
    }
    bool CompleteWithAudio(const AudioWA::FAction& A)
    {
        // Independent binding specification, not a production mapping helper.
        const double DrawAt=A.Start+(A.End-A.Start)*(.20/1.10);
        const double InsertAt=A.Start+(A.End-A.Start)*(.60/1.10);
        if(!AdvanceTo(std::nextafter(DrawAt,A.Start)))return false;ExpectNoAudio(DrawCue,A);
        if(!AdvanceTo(DrawAt))return false;ExpectAudio(DrawCue,A.ActionId,A.InstanceId,DrawAt);
        ExpectNoAudio(InsertCue,A);ExpectNoAudio(CompleteCue,A);ExpectRepeatedHUDReadOnly();
        if(!AdvanceTo(std::nextafter(InsertAt,A.Start)))return false;ExpectNoAudio(InsertCue,A);
        if(!AdvanceTo(InsertAt))return false;ExpectAudio(InsertCue,A.ActionId,A.InstanceId,InsertAt);
        Test->TestTrue(TEXT("An audible insert phase cannot refill the real crossbow"),Instance(A.InstanceId)&&Instance(A.InstanceId)->Ammo==0.);
        ExpectNoAudio(CompleteCue,A);ExpectRepeatedHUDReadOnly();
        if(!AdvanceTo(std::nextafter(A.End,A.Start)))return false;
        ExpectNoAudio(CompleteCue,A);Test->TestTrue(TEXT("Last actual reload instant is still empty"),Instance(A.InstanceId)&&Instance(A.InstanceId)->Ammo==0.);
        if(!AdvanceTo(A.End))return false;
        ExpectAudio(CompleteCue,A.ActionId,A.InstanceId,A.End);ExpectCompletedResource(A);ExpectRepeatedHUDReadOnly();
        return true;
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioReloadBoundaries,
    "CodexDungeon.Content.ActionAudioIntegration.RealReloadCueBoundariesManualAutoBothFacingsAndSpeed",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioReloadBoundaries::RunTest(const FString& Parameters)
{
    for(const double Speed:{0.,25.,-25.})for(const double Facing:{1.,-1.})for(const bool Auto:{false,true})
    {
        FActionAudioWorld F(this);if(!TestTrue(TEXT("Real E acquisition with authored ammo/speed"),F.Create(Auto?1.:0.,Speed))||!F.Face(Facing))return false;
        AudioWA::FAction A;if(!TestTrue(TEXT("Normal T or actual empty-shot recovery admits genuine reload"),Auto?F.AutoReload(A):F.ManualReload(A)))return false;
        TestTrue(TEXT("Accepted reload uses independently expected real modified duration"),std::abs((A.End-A.Start)-1.1/(1.+Speed/100.))<1.e-9);
        if(!F.CompleteWithAudio(A))return false;
        TestEqual(TEXT("One draw request for this real reload"),F.HUD->GetActionAudioPlayRequests(DrawCue),1);
        TestEqual(TEXT("One insert request for this real reload"),F.HUD->GetActionAudioPlayRequests(InsertCue),1);
        TestEqual(TEXT("One actual completion request for this real reload"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
        TestTrue(TEXT("Audio works while the current interface remains hidden"),!F.HUD->GetInterfaceVisible());
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioCancelAfterInsert,
    "CodexDungeon.Content.ActionAudioIntegration.InsertThenFreshTCancelNeverCompletesOldDeadline",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioCancelAfterInsert::RunTest(const FString& Parameters)
{
    FActionAudioWorld F(this);if(!F.Create())return false;AudioWA::FAction Cancelled;
    if(!F.ManualReload(Cancelled))return false;
    const double DrawAt=Cancelled.Start+(Cancelled.End-Cancelled.Start)*(.20/1.10);
    const double InsertAt=Cancelled.Start+(Cancelled.End-Cancelled.Start)*(.60/1.10);
    if(!F.AdvanceTo(DrawAt)||!F.AdvanceTo(InsertAt))return false;
    F.ExpectAudio(DrawCue,Cancelled.ActionId,Cancelled.InstanceId,DrawAt);
    F.ExpectAudio(InsertCue,Cancelled.ActionId,Cancelled.InstanceId,InsertAt);
    if(!F.Pulse(EKeys::T))return false;
    TestTrue(TEXT("Fresh normal T actually cancels after insertion without refilling"),!F.Actions().Action.Active
        &&F.Actions().Action.ActionId==Cancelled.ActionId&&F.Actions().Action.Terminal==AudioWA::EEvent::ReloadCancelled
        &&F.Instance()->Ammo==0.&&F.Game->GetEquipmentView().Slots[1].Ammo==0.);
    if(!F.AdvanceTo(Cancelled.End+.1))return false;
    F.ExpectNoAudio(CompleteCue,Cancelled);F.ExpectRepeatedHUDReadOnly();
    int32 OldReceipts=0;for(const auto& R:F.Actions().WeaponRuntimeHistory)
        if(R.Kind==AudioWA::EWeaponMutation::ReloadCompleted&&R.Action.ActionId==Cancelled.ActionId)++OldReceipts;
    TestEqual(TEXT("Cancelled reload never creates a later completion resource receipt"),OldReceipts,0);
    AudioWA::FAction Next;if(!F.ManualReload(Next)||!F.CompleteWithAudio(Next))return false;
    TestTrue(TEXT("A new real reload has a distinct accepted action identity"),Next.ActionId>Cancelled.ActionId&&Next.InstanceId==Cancelled.InstanceId);
    TestEqual(TEXT("Two different actual draw phases"),F.HUD->GetActionAudioPlayRequests(DrawCue),2);
    TestEqual(TEXT("Two different actual insert phases"),F.HUD->GetActionAudioPlayRequests(InsertCue),2);
    TestEqual(TEXT("Only the truly completed second action sounds complete"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioSwitchHistory,
    "CodexDungeon.Content.ActionAudioIntegration.QRoundTripKeepsInstanceHistoryWithoutReplayingOldSounds",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioSwitchHistory::RunTest(const FString& Parameters)
{
    FActionAudioWorld F(this);if(!F.Create())return false;AudioWA::FAction First;
    if(!F.ManualReload(First)||!F.CompleteWithAudio(First))return false;
    const uint64 SameInstance=F.AcquiredInstance;
    if(!F.Pulse(EKeys::Q)||!F.FinishEquipment()||!F.Pulse(EKeys::Q)||!F.FinishEquipment())return false;
    TestTrue(TEXT("Both actual Q transactions return to the exact completed crossbow instance"),F.Actions().EquippedId==SameInstance&&F.Instance()->Ammo==1.);
    TestEqual(TEXT("Returning to its persistent completion history does not replay draw"),F.HUD->GetActionAudioPlayRequests(DrawCue),1);
    TestEqual(TEXT("Returning to its persistent completion history does not replay insert"),F.HUD->GetActionAudioPlayRequests(InsertCue),1);
    TestEqual(TEXT("Returning to its persistent completion history does not replay completion"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
    AudioWA::FAction Cancelled;if(!F.AutoReload(Cancelled))return false;
    const double DrawAt=Cancelled.Start+(Cancelled.End-Cancelled.Start)*(.20/1.10);
    const double InsertAt=Cancelled.Start+(Cancelled.End-Cancelled.Start)*(.60/1.10);
    if(!F.AdvanceTo(DrawAt)||!F.AdvanceTo(InsertAt))return false;
    F.ExpectAudio(DrawCue,Cancelled.ActionId,SameInstance,DrawAt);F.ExpectAudio(InsertCue,Cancelled.ActionId,SameInstance,InsertAt);
    if(!F.Pulse(EKeys::Q)||!F.FinishEquipment())return false;
    TestTrue(TEXT("Actual Q leaves a cancelled empty crossbow, not a future refill"),F.Actions().EquippedId!=SameInstance&&F.Instance(SameInstance)&&F.Instance(SameInstance)->Ammo==0.);
    if(F.Game->GetSimulationTime()<Cancelled.End+.1&&!F.AdvanceTo(Cancelled.End+.1))return false;
    F.ExpectNoAudio(CompleteCue,Cancelled);
    if(!F.Pulse(EKeys::Q)||!F.FinishEquipment())return false;
    TestTrue(TEXT("Return still selects the same empty instance after its old deadline"),F.Actions().EquippedId==SameInstance&&F.Instance()->Ammo==0.);
    F.ExpectNoAudio(CompleteCue,Cancelled);F.ExpectAudio(CompleteCue,First.ActionId,SameInstance,First.End);
    TestEqual(TEXT("Old completed history remains one completion across later switches"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
    TestEqual(TEXT("Exactly the two real accepted draw phases have sounded"),F.HUD->GetActionAudioPlayRequests(DrawCue),2);
    TestEqual(TEXT("Exactly the two real accepted insert phases have sounded"),F.HUD->GetActionAudioPlayRequests(InsertCue),2);
    F.ExpectRepeatedHUDReadOnly();return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioArmorCommit,
    "CodexDungeon.Content.ActionAudioIntegration.FourArmorMaterialsRequireRealCommitAndCancelIsSilent",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioArmorCommit::RunTest(const FString& Parameters)
{
    for(const FString Armor:{TEXT("ARM-LGT-001"),TEXT("ARM-MED-001"),TEXT("ARM-HVY-001"),TEXT("ARM-ROB-001")})for(const bool Cancel:{false,true})
    {
        FActionAudioWorld F(this);if(!F.Create(1.))return false;
        AudioInventory::FItem Initial;Initial.ContentId=Armor==TEXT("ARM-ROB-001")?"ARM-LGT-001":"ARM-ROB-001";
        const auto Baseline=F.Register(Initial);if(!Baseline.Ok()||!F.Pickup(Baseline.SourceId)||!F.FinishEquipment())return false;
        const uint64 OldArmor=F.Inventory().Armor;const FString OldArmorId=F.Player->ArmorId;
        AudioInventory::FItem Incoming;Incoming.ContentId=TCHAR_TO_UTF8(*Armor);const auto S=F.Register(Incoming);
        if(!S.Ok()||!F.Game->SelectEquipmentSource(S.SourceId)||!F.Pulse(EKeys::E))return false;
        const int32 BeforeCloth=F.HUD->GetActionAudioPlayRequests(ClothCue),BeforeMetal=F.HUD->GetActionAudioPlayRequests(MetalCue);
        TestTrue(TEXT("E opens actual occupied-body replacement selection before any commit"),F.Game->GetEquipmentView().NeedsSlotSelection&&!F.Game->GetEquipmentView().Action.Active&&F.Inventory().Armor==OldArmor);
        if(!F.Pulse(EKeys::Escape))return false;
        TestTrue(TEXT("Normal Esc cancels selection with no material sound"),!F.Game->GetEquipmentView().NeedsSlotSelection
            &&F.HUD->GetActionAudioPlayRequests(ClothCue)==BeforeCloth&&F.HUD->GetActionAudioPlayRequests(MetalCue)==BeforeMetal);
        if(!F.Pickup(S.SourceId))return false;const auto A=F.Game->GetEquipmentView().Action;
        const auto OperationsBefore=F.Inventory().Operations.size();
        TestTrue(TEXT("Real E/Enter armor action retains the full .5 accepted transaction"),A.Kind==EDungeonEquipmentActionKind::PickupArmor
            &&A.InstanceId==S.InstanceId&&A.Deadline==A.Start+.5&&A.OperationId!=0);
        if(!F.AdvanceTo(A.Deadline-.05))return false;
        TestTrue(TEXT("Before real armor commit the old armor, source and audio remain unchanged"),F.Inventory().Armor==OldArmor&&F.Player->ArmorId==OldArmorId
            &&F.Source(S.SourceId)&&!F.Source(S.SourceId)->Consumed&&F.HUD->GetActionAudioPlayRequests(ClothCue)==BeforeCloth
            &&F.HUD->GetActionAudioPlayRequests(MetalCue)==BeforeMetal);
        if(Cancel)
        {
            if(!F.Key(EKeys::D,true))return false;F.Frame(.005f);if(!F.Key(EKeys::D,false)||!F.AdvanceTo(A.Deadline+.1))return false;
            TestTrue(TEXT("Normal movement cancels armor action without accepting an operation or consuming source"),!F.Game->GetEquipmentView().Action.Active
                &&F.Inventory().Armor==OldArmor&&F.Player->ArmorId==OldArmorId&&F.Inventory().Operations.size()==OperationsBefore
                &&F.Source(S.SourceId)&&!F.Source(S.SourceId)->Consumed);
            TestTrue(TEXT("Cancelled armor deadline emits neither material request"),F.HUD->GetActionAudioPlayRequests(ClothCue)==BeforeCloth
                &&F.HUD->GetActionAudioPlayRequests(MetalCue)==BeforeMetal
                &&F.Facts(ClothCue,A.ActionId,A.InstanceId,A.OperationId)==0&&F.Facts(MetalCue,A.ActionId,A.InstanceId,A.OperationId)==0);
        }
        else
        {
            if(!F.AdvanceTo(A.Deadline))return false;
            const AudioInventory::FOperation* Operation=nullptr;
            for(const auto& O:F.Inventory().Operations)if(O.OperationId==A.OperationId)Operation=&O;
            if(!TestNotNull(TEXT("Actual successful inventory operation exists independently of sound journal"),Operation))return false;
            TestTrue(TEXT("Actual body commit consumes exactly this source and installs its same armor instance"),Operation->Result.Ok()
                &&Operation->Request.Action==AudioInventory::EAction::Pickup&&Operation->Request.Slot==2
                &&Operation->Request.InstanceId==S.InstanceId&&Operation->Result.AcquiredId==S.InstanceId
                &&F.Inventory().Armor==S.InstanceId&&F.Player->ArmorId==Armor&&F.Source(S.SourceId)&&F.Source(S.SourceId)->Consumed);
            const bool Cloth=Armor==TEXT("ARM-LGT-001")||Armor==TEXT("ARM-ROB-001");
            F.ExpectAudio(Cloth?ClothCue:MetalCue,A.ActionId,S.InstanceId,A.Deadline,A.OperationId,Operation->Result.Revision);
            TestEqual(TEXT("Only the independently selected incoming material gains one request"),F.HUD->GetActionAudioPlayRequests(Cloth?ClothCue:MetalCue),(Cloth?BeforeCloth:BeforeMetal)+1);
            TestEqual(TEXT("The other material does not sound for this commit"),F.HUD->GetActionAudioPlayRequests(Cloth?MetalCue:ClothCue),Cloth?BeforeMetal:BeforeCloth);
        }
        F.ExpectRepeatedHUDReadOnly();
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioFreshRun,
    "CodexDungeon.Content.ActionAudioIntegration.FreshRRunReusesNumericIdsWithoutOldAudioOrDeadlineLeak",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioFreshRun::RunTest(const FString& Parameters)
{
    FActionAudioWorld F(this);if(!F.Create())return false;AudioWA::FAction Old;
    if(!F.ManualReload(Old))return false;
    const double DrawAt=Old.Start+(Old.End-Old.Start)*(.20/1.10),InsertAt=Old.Start+(Old.End-Old.Start)*(.60/1.10);
    if(!F.AdvanceTo(DrawAt)||!F.AdvanceTo(InsertAt))return false;
    F.ExpectAudio(DrawCue,Old.ActionId,Old.InstanceId,DrawAt);F.ExpectAudio(InsertCue,Old.ActionId,Old.InstanceId,InsertAt);
    const FGuid OldRun=F.Game->GetEquipmentView().RunGuid;const uint64 OldRestartSerial=F.Game->GetRunRestartSerial();
    ADungeonHUD* SameHUD=F.HUD;
    if(!F.Pulse(EKeys::R))return false;
    // R genuinely creates the normal room. Disable only fixture adversary AI;
    // no HP, damage, action, timer, audio record or resource fact is patched.
    for(auto E:F.Game->Enemies)if(IsValid(E)){E->bAIEnabled=false;E->SetActorTickEnabled(false);}
    const FGuid NewRun=F.Game->GetEquipmentView().RunGuid;
    TestTrue(TEXT("Normal R genuinely creates a distinct Run while retaining the same HUD actor"),NewRun.IsValid()&&NewRun!=OldRun
        &&F.Game->GetRunRestartSerial()>OldRestartSerial&&F.HUD==SameHUD&&F.Game->GetActionAudioState().RunGuid==NewRun);
    TestTrue(TEXT("Fresh run has no prior WA histories or action-audio records"),F.Actions().WeaponRuntimeHistory.empty()
        &&F.Actions().Action.ActionId==0&&F.Game->GetActionAudioState().Records.IsEmpty()&&F.Game->GetActionAudioState().NextSequence==1
        &&F.HUD->GetActionAudioPlayReceipts().IsEmpty());
    for(const TCHAR* Cue:{DrawCue,InsertCue,CompleteCue,ClothCue,MetalCue})
        TestEqual(TEXT("Same HUD new-run request scope resets instead of replaying old facts"),F.HUD->GetActionAudioPlayRequests(Cue),0);
    if(!F.AdvanceTo(Old.End+.1))return false;
    TestTrue(TEXT("Crossing an old-run reload deadline cannot create a new-run completion"),F.Game->GetActionAudioState().Records.IsEmpty()
        &&F.HUD->GetActionAudioPlayReceipts().IsEmpty()&&F.Actions().WeaponRuntimeHistory.empty());
    if(!F.AcquireCrossbow(0.))return false;AudioWA::FAction Current;
    if(!F.ManualReload(Current))return false;
    TestTrue(TEXT("New real inputs deliberately reuse the old numeric instance/action IDs under a different RunGuid"),Current.ActionId==Old.ActionId
        &&Current.InstanceId==Old.InstanceId&&F.Game->GetEquipmentView().RunGuid!=OldRun);
    if(!F.CompleteWithAudio(Current))return false;
    for(const auto& R:F.HUD->GetActionAudioPlayReceipts())TestTrue(TEXT("Every actual new-run request belongs to the new RunGuid"),R.Source.RunGuid==NewRun);
    TestEqual(TEXT("Fresh same-ID reload emits one new draw request"),F.HUD->GetActionAudioPlayRequests(DrawCue),1);
    TestEqual(TEXT("Fresh same-ID reload emits one new insert request"),F.HUD->GetActionAudioPlayRequests(InsertCue),1);
    TestEqual(TEXT("Only the actually completed new-run action emits completion"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
    F.ExpectRepeatedHUDReadOnly();return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioLateHUD,
    "CodexDungeon.Content.ActionAudioIntegration.RebuiltHUDSeedsRecentHistoryButPlaysFutureReloadStages",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioLateHUD::RunTest(const FString& Parameters)
{
    FActionAudioWorld F(this);if(!F.Create())return false;AudioWA::FAction A;
    if(!F.ManualReload(A))return false;
    const double DrawAt=A.Start+(A.End-A.Start)*(.20/1.10),InsertAt=A.Start+(A.End-A.Start)*(.60/1.10);
    if(!F.AdvanceTo(DrawAt))return false;
    F.ExpectAudio(DrawCue,A.ActionId,A.InstanceId,DrawAt);
    if(!F.AdvanceTo(DrawAt+.01))return false;
    const double AttachAt=F.Game->GetSimulationTime();const auto Before=F.Actions();
    const uint64 BeforeSequence=F.Game->GetActionAudioState().NextSequence;
    const int32 BeforeFacts=F.Game->GetActionAudioState().Records.Num();
    if(!TestTrue(TEXT("Rebuild occurs while the real old draw is still inside the ordinary playback-age window"),
        AttachAt>DrawAt&&AttachAt-DrawAt<=.25&&AttachAt<InsertAt
        &&F.HUD->GetActionAudioPlayRequests(DrawCue)==1&&F.Facts(DrawCue,A.ActionId,A.InstanceId)==1))return false;
    ADungeonHUD* OriginalHUD=F.HUD;ADungeonHUD* Replacement=F.World->SpawnActor<ADungeonHUD>();
    if(!TestNotNull(TEXT("Second actual HUD actor is created through the ordinary lifecycle"),Replacement))return false;
    Replacement->SetOwner(F.Controller);if(!Replacement->HasActorBegunPlay())Replacement->DispatchBeginPlay();
    F.HUD=Replacement;OriginalHUD->Destroy();F.HUD->Tick(0.f);
    TestTrue(TEXT("New HUD seeds the recent actual history without an age-drop shortcut or an old request"),
        F.HUD!=OriginalHUD&&F.HUD->GetActionAudioPlayReceipts().IsEmpty()
        &&F.HUD->GetActionAudioPlayRequests(DrawCue)==0&&F.HUD->GetActionAudioPlayRequests(InsertCue)==0
        &&F.HUD->GetActionAudioPlayRequests(CompleteCue)==0);
    TestTrue(TEXT("HUD recreation cannot change the live accepted reload, resource clock, or source journal"),
        F.Game->GetSimulationTime()==AttachAt&&F.Actions().Action.Active&&F.Actions().Action.ActionId==A.ActionId
        &&F.Actions().Action.InstanceId==A.InstanceId&&F.Actions().Action.Start==A.Start&&F.Actions().Action.End==A.End
        &&F.Actions().NextActionId==Before.NextActionId&&F.Actions().NextEventId==Before.NextEventId
        &&F.Instance()->Ammo==0.&&F.Game->GetActionAudioState().NextSequence==BeforeSequence
        &&F.Game->GetActionAudioState().Records.Num()==BeforeFacts);
    F.ExpectRepeatedHUDReadOnly();
    if(!F.AdvanceTo(std::nextafter(InsertAt,A.Start)))return false;F.ExpectNoAudio(InsertCue,A);
    if(!F.AdvanceTo(InsertAt))return false;F.ExpectAudio(InsertCue,A.ActionId,A.InstanceId,InsertAt);
    TestTrue(TEXT("Future insertion on the same real action stays empty"),F.Instance()->Ammo==0.);
    if(!F.AdvanceTo(std::nextafter(A.End,A.Start)))return false;F.ExpectNoAudio(CompleteCue,A);
    if(!F.AdvanceTo(A.End))return false;
    F.ExpectAudio(CompleteCue,A.ActionId,A.InstanceId,A.End);F.ExpectCompletedResource(A);
    TestEqual(TEXT("Replacement HUD never replays the recent old draw"),F.HUD->GetActionAudioPlayRequests(DrawCue),0);
    TestEqual(TEXT("Replacement HUD accepts the future insertion once"),F.HUD->GetActionAudioPlayRequests(InsertCue),1);
    TestEqual(TEXT("Replacement HUD accepts the future real completion once"),F.HUD->GetActionAudioPlayRequests(CompleteCue),1);
    TestEqual(TEXT("Seeded source draw remains exactly one actual fact"),F.Facts(DrawCue,A.ActionId,A.InstanceId),1);
    F.ExpectRepeatedHUDReadOnly();return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FActionAudioSamePointShield,
    "CodexDungeon.Content.ActionAudioIntegration.RealShieldPoiseOrDeathPreemptsExactDrawAndInsertSoundBoundary",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FActionAudioSamePointShield::RunTest(const FString& Parameters)
{
    for(const bool Insert:{false,true})for(const bool Lethal:{false,true})
    {
        FActionAudioWorld F(this);if(!F.Create())return false;
        if(Lethal)F.Player->Health=11.f; // Explicit initial missing HP, before any incoming hit.
        auto Knight=F.World->SpawnActor<ADungeonFighter>();
        if(!TestNotNull(TEXT("Real proximity-waking stone Shield enemy"),Knight))return false;
        Knight->SetActorTickEnabled(false);Knight->ResetFighter(F.Player->GetGroundPosition()+FVector2D(80,0));
        F.Game->Enemies.Add(Knight);
        if(!TestTrue(TEXT("Ordinary initial stone admission uses the actual current simulation time"),
            Knight->InitializeStoneKnight(98001,F.Game->GetSimulationTime())))return false;
        F.Frame(.86f);const auto Shield=Knight->GetStoneKnightDriver()->State().Action;
        if(!TestTrue(TEXT("Real proximity wake accepted a normally scheduled Shield with time for either sound phase"),
            Shield.InProgress&&Shield.Kind==DungeonStoneKnight::EAttack::Shield
            &&Shield.ActiveAt>F.Game->GetSimulationTime()+.60))return false;
        // Reuse the established public QA poise setup. The real non-breaking
        // hit contributes29, then the actual Shield contributes18. Its .65s
        // protection expires naturally; no damage/WA/audio receipt is edited.
        F.Player->ApplyCombatHit(1.f,Knight,29.f);
        if(!TestTrue(TEXT("Actual public preload hit leaves a living unbroken empty crossbow owner"),
            !F.Player->bDead&&F.Player->AttackTime==0.f&&F.Instance()->Ammo==0.
            &&F.Player->Health==(Lethal?10.f:99.f)))return false;
        const double Impact=Shield.ActiveAt,ReloadStart=Impact-(Insert?.60:.20);
        if(!F.AdvanceTo(ReloadStart))return false;AudioWA::FAction Reload;
        if(!F.ManualReload(Reload))return false;
        const double DrawAt=Reload.Start+(Reload.End-Reload.Start)*(.20/1.10);
        const double InsertAt=Reload.Start+(Reload.End-Reload.Start)*(.60/1.10);
        const double StageAt=Insert?InsertAt:DrawAt;
        if(!TestTrue(TEXT("Independently scheduled real reload sound and real Shield share an identical double endpoint"),
            Reload.Start==ReloadStart&&StageAt==Impact&&Reload.InstanceId==F.AcquiredInstance))return false;
        if(Insert)
        {
            // Present the earlier real draw normally, not after a long tick
            // that would intentionally drop it as an aged playback backlog.
            if(!F.AdvanceTo(DrawAt))return false;F.ExpectAudio(DrawCue,Reload.ActionId,Reload.InstanceId,DrawAt);
        }
        if(!F.AdvanceTo(Impact-.001))return false;
        if(!TestTrue(TEXT("Real preload protection naturally ends before the actual Shield admission"),F.Player->CanReceiveDirectHit()))return false;
        if(!TestTrue(TEXT("Player retains exactly the preloaded HP immediately before the real Shield endpoint"),
            F.Player->Health==(Lethal?10.f:99.f)))return false;
        F.ExpectNoAudio(Insert?InsertCue:DrawCue,Reload);F.ExpectNoAudio(CompleteCue,Reload);
        if(!F.AdvanceTo(Impact))return false;
        int32 HitReceipts=0,ActiveEvents=0;
        for(const auto& H:Knight->GetStoneKnightDriver()->State().HitReceipts)
            if(H.AttackId==Shield.AttackId&&H.TargetId==F.Player->GetRuntimeEntityId())++HitReceipts;
        // This presentation journal deliberately excludes Hit events. Shield
        // contact is proven by the actual attack/target receipt and HP change;
        // its retained ActiveWindow independently proves the exact activation.
        for(const auto& R:Knight->GetStoneFeedback().Entries())if(R.Event.Kind==DungeonStoneKnight::EEventKind::ActiveWindow
            &&R.Event.EntityId==Knight->GetStoneKnightDriver()->State().EntityId&&R.Event.Action.AttackId==Shield.AttackId)
        {
            ++ActiveEvents;TestTrue(TEXT("Actual retained Shield activation has the exact shared time and frozen13 damage18 stagger"),
                R.Event.AtTime==Impact&&R.Event.Action.ActiveAt==Impact&&R.Event.Action.Kind==DungeonStoneKnight::EAttack::Shield
                &&R.Event.Action.Damage==13.&&R.Event.Action.Stagger==18.);
        }
        TestEqual(TEXT("One independent actual Shield hit receipt"),HitReceipts,1);
        TestEqual(TEXT("One independent retained Shield activation journal event"),ActiveEvents,1);
        TestTrue(TEXT("Damage-first poise break or death cancels the real reload before that sound phase"),
            !F.Actions().Action.Active&&F.Actions().Action.ActionId==Reload.ActionId
            &&F.Actions().Action.Terminal==AudioWA::EEvent::ReloadCancelled&&F.Actions().LastReloadCancelTime==Impact
            &&F.Player->bDead==Lethal&&F.Player->Health==(Lethal?0.f:86.f)&&F.Instance()->Ammo==0.
            &&F.Game->GetEquipmentView().Slots[1].Ammo==0.);
        F.ExpectNoAudio(Insert?InsertCue:DrawCue,Reload);F.ExpectNoAudio(CompleteCue,Reload);
        TestEqual(TEXT("Only the strictly earlier observed draw can survive the shared endpoint"),F.HUD->GetActionAudioPlayRequests(DrawCue),Insert?1:0);
        TestEqual(TEXT("Insertion at or after the terminal endpoint remains silent"),F.HUD->GetActionAudioPlayRequests(InsertCue),0);
        int32 Completed=0;for(const auto& R:F.Actions().WeaponRuntimeHistory)
            if(R.Kind==AudioWA::EWeaponMutation::ReloadCompleted&&R.Action.ActionId==Reload.ActionId)++Completed;
        TestEqual(TEXT("Terminal same-point damage cannot create an actual refill receipt"),Completed,0);
        AddInfo(FString::Printf(TEXT("ActionAudio exact Shield insert=%d lethal=%d impact=%.17g stage=%.17g sim=%.17g hp=%.9g hitReceipts=%d activeEvents=%d drawRequests=%d insertRequests=%d completeRequests=%d"),
            int32(Insert),int32(Lethal),Impact,StageAt,F.Game->GetSimulationTime(),F.Player->Health,HitReceipts,ActiveEvents,
            F.HUD->GetActionAudioPlayRequests(DrawCue),F.HUD->GetActionAudioPlayRequests(InsertCue),F.HUD->GetActionAudioPlayRequests(CompleteCue)));
        if(Lethal)
        {
            const double Stopped=F.Game->GetSimulationTime();F.Frame(2.f);
            TestTrue(TEXT("Ordinary dead-run frames keep the stopped clock and cannot force an old reload deadline"),
                F.Game->bGameOver&&F.Game->GetSimulationTime()==Stopped&&Stopped==Impact);
        }
        else if(!F.AdvanceTo(Reload.End+.1))return false;
        F.ExpectNoAudio(Insert?InsertCue:DrawCue,Reload);F.ExpectNoAudio(CompleteCue,Reload);
        TestEqual(TEXT("No later frame or old deadline generates completion playback"),F.HUD->GetActionAudioPlayRequests(CompleteCue),0);
        F.ExpectRepeatedHUDReadOnly();
    }
    return true;
}
#endif
