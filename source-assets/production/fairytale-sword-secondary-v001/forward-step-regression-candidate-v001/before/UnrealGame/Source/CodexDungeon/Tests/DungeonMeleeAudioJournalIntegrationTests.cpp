// UNAPPLIED candidate. Copy into Source/CodexDungeon/Tests only after root admission.
// Uses existing public APIs and existing audio DTOs; does not synthesize events/audio.
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonFighter.h"
#include "../DungeonGameMode.h"
#include "../DungeonHUD.h"
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
namespace MC=DungeonContentCombat;
namespace MW=DungeonWeaponActions;
const TCHAR* const MeleeIds[]={TEXT("WPN-SWD-001"),TEXT("WPN-GSW-001"),TEXT("WPN-SPR-001")};
const TCHAR* const Families[]={TEXT("SWD_WHOOSH"),TEXT("GSW_WHOOSH"),TEXT("SPR_THRUST")};
FString MeleeCue(int32 Family,uint32 Stage)
{return FString::Printf(TEXT("%s_%02d"),Families[Family],Stage+1);}

struct FMeleeAudioWorld
{
    UWorld* World=nullptr;ADungeonGameMode* Game=nullptr;ADungeonFighter* Player=nullptr;
    APlayerController* Controller=nullptr;ADungeonHUD* HUD=nullptr;FAutomationTestBase* Test=nullptr;
    uint64 AcquiredInstance=0;
    explicit FMeleeAudioWorld(FAutomationTestBase* InTest):Test(InTest){}
    ~FMeleeAudioWorld()
    {if(World){World->DestroyWorld(false);if(GEngine)GEngine->DestroyWorldContext(World);}}
    bool Fail(const TCHAR* Stage)
    {Test->AddError(FString::Printf(TEXT("Melee audio genuine fixture %s; equipment=%s"),Stage,
        Game?*Game->GetEquipmentView().FailureText:TEXT("No GameMode")));return false;}
    bool Key(FKey K,bool Down)
    {
        if(!Controller||!Controller->PlayerInput)return Fail(TEXT("registered controller input"));
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
        HUD->Tick(Dt); // Real public presentation consumer; no Canvas or fake receipt.
    }
    bool Pulse(FKey K)
    {if(!Key(K,true))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool AdvanceTo(double At)
    {
        if(!std::isfinite(At)||At<Game->GetSimulationTime())return Fail(TEXT("monotonic deadline"));
        for(int32 N=0;N<64&&Game->GetSimulationTime()<At;++N)
        {
            const double Remaining=At-Game->GetSimulationTime();float Dt=float(Remaining);
            if(double(Dt)>Remaining)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return Fail(TEXT("representable positive tick"));
            const double Before=Game->GetSimulationTime();Frame(Dt);
            if(Game->GetSimulationTime()<=Before)return Fail(TEXT("real clock progress"));
        }
        return Game->GetSimulationTime()==At;
    }
    bool Create(int32 Family)
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
        if(!World->SetGameMode(URL))return Fail(TEXT("actual GameMode"));
        Game=World->GetAuthGameMode<ADungeonGameMode>();Player=World->SpawnActor<ADungeonFighter>();
        Controller=World->SpawnActor<APlayerController>();
        if(!Game||!Player||!Controller)return Fail(TEXT("actors"));
        World->AddController(Controller);Controller->Possess(Player);
        if(!Controller->PlayerInput)Controller->PlayerInput=NewObject<UPlayerInput>(Controller);
        if(!Controller->IsLocalController()||UGameplayStatics::GetPlayerController(Game,0)!=Controller)
            return Fail(TEXT("real local controller resolver"));
        Player->SetActorTickEnabled(false);Player->ResetFighter({0,0});Game->PlayerFighter=Player;
        Game->bWaitingForStart=true;Game->bGameOver=false;
        if(!Game->BeginEquipmentRun(EDungeonEquipmentRunConfig::IntegrationPreview,1))return Fail(TEXT("fresh bound Run"));
        HUD=World->SpawnActor<ADungeonHUD>();if(!HUD)return Fail(TEXT("actual HUD"));
        HUD->SetOwner(Controller);if(!HUD->HasActorBegunPlay())HUD->DispatchBeginPlay();HUD->Tick(0.f);
        if(!Pulse(EKeys::Enter)||Game->bWaitingForStart)return Fail(TEXT("normal Enter start"));
        DungeonEquipmentInventory::FItem Item;Item.ContentId=TCHAR_TO_UTF8(MeleeIds[Family]);
        const auto Source=Game->RegisterEquipmentSource(TEXT("qa.melee-audio.only-ground-source"),Item,{40,0});
        if(!Source.Ok())return Fail(TEXT("registered genuine QA source"));
        Frame(.005f);
        if(Game->GetEquipmentView().SelectedSourceId!=Source.SourceId||!Pulse(EKeys::E))
            return Fail(TEXT("normal E on actual displayed source"));
        const auto Pickup=Game->GetEquipmentView().Action;
        if(!Pickup.Active||Pickup.Kind!=EDungeonEquipmentActionKind::PickupWeapon
            ||Pickup.InstanceId!=Source.InstanceId||Pickup.Deadline!=Pickup.Start+.35)
            return Fail(TEXT("accepted .35 empty-slot pickup"));
        if(!AdvanceTo(Pickup.Deadline))return Fail(TEXT("actual equipment deadline"));
        AcquiredInstance=Source.InstanceId;
        return Player->WeaponId==MeleeIds[Family]&&Player->GetMeleeCombatState().WeaponInstanceId==AcquiredInstance
            &&Player->GetWeaponActionsState().EquippedId==AcquiredInstance
            &&Game->GetEquipmentView().Slots[Game->GetEquipmentView().ActiveSlot].InstanceId==AcquiredInstance;
    }
    int32 Facts(const FString& Cue,uint64 ActionId,double At)const
    {
        int32 N=0;for(const auto& R:Game->GetActionAudioState().Records)
            if(R.Cue==Cue&&R.ActionId==ActionId&&R.InstanceId==AcquiredInstance&&R.AtTime==At)++N;
        return N;
    }
    int32 Requests(const FString& Cue,uint64 ActionId,double At)const
    {
        int32 N=0;for(const auto& R:HUD->GetActionAudioPlayReceipts())
            if(R.Source.Cue==Cue&&R.Source.ActionId==ActionId&&R.Source.InstanceId==AcquiredInstance&&R.Source.AtTime==At)++N;
        return N;
    }
    bool ExpectOne(const FString& Cue,uint64 ActionId,double At,uint64 Revision)
    {
        const bool Counts=Test->TestEqual(*(Cue+TEXT(" one actual action journal fact")),Facts(Cue,ActionId,At),1)
            &Test->TestEqual(*(Cue+TEXT(" one actual playback request")),Requests(Cue,ActionId,At),1);
        const FDungeonActionAudioRecord* Fact=nullptr;const FDungeonActionAudioPlayRequest* Request=nullptr;
        for(const auto& R:Game->GetActionAudioState().Records)
            if(R.Cue==Cue&&R.ActionId==ActionId&&R.InstanceId==AcquiredInstance&&R.AtTime==At)Fact=&R;
        for(const auto& R:HUD->GetActionAudioPlayReceipts())
            if(R.Source.Cue==Cue&&R.Source.ActionId==ActionId&&R.Source.InstanceId==AcquiredInstance&&R.Source.AtTime==At)Request=&R;
        if(!Counts||!Fact||!Request)return false;
        const auto& V=Game->GetEquipmentView();const auto& P=Request->Source;
        const FString Name=TEXT("SW_AUD_")+Cue+TEXT("_v001");
        const FString ExpectedPath=TEXT("/Game/Production/FirstBatch/v001/Audio/")+Name+TEXT(".")+Name;
        return Test->TestTrue(*(Cue+TEXT(" preserves real identity, accepted clock, actual asset and original gain")),
            Fact->RunGuid==V.RunGuid&&Fact->RoomInstanceId==V.RoomInstanceId&&Fact->OwnerId==V.OwnerId
            &&Fact->Sequence>0&&Fact->Sequence<Game->GetActionAudioState().NextSequence&&Fact->OperationId==0
            &&Fact->Revision==Revision&&Revision>0&&P.Sequence==Fact->Sequence&&P.RunGuid==Fact->RunGuid
            &&P.RoomInstanceId==Fact->RoomInstanceId&&P.OwnerId==Fact->OwnerId&&P.ActionId==ActionId
            &&P.InstanceId==AcquiredInstance&&P.OperationId==0&&P.Revision==Revision&&P.AtTime==At
            &&Request->SoundPath==ExpectedPath&&Request->Volume==.25f&&Request->Pitch==1.f
            &&Request->RequestedAt>=At&&Request->RequestedAt-At<=.25);
    }
    bool NoReplay()
    {
        const auto& C=Player->GetMeleeCombatState();const auto& W=Player->GetWeaponActionsState();
        const uint64 Attack=C.NextAttackId,CombatEvent=C.NextEventId,Action=W.NextActionId,WeaponEvent=W.NextEventId;
        const uint64 Seq=Game->GetActionAudioState().NextSequence,Revision=Game->GetEquipmentView().Revision,Crit=Game->GetEquipmentView().NextCritDraw;
        const double Focus=W.Budget.Focus,ReservedFocus=W.Budget.ReservedFocus;
        const auto Instances=W.Instances;
        const int32 FactsBefore=Game->GetActionAudioState().Records.Num(),RequestsBefore=HUD->GetActionAudioPlayReceipts().Num();
        for(int32 I=0;I<8;++I){Frame(0.f);HUD->Tick(0.f);}
        bool SameInstances=true;
        for(const auto& Before:Instances)
        {
            const MW::FInstance* After=nullptr;for(const auto& I:Player->GetWeaponActionsState().Instances)if(I.InstanceId==Before.InstanceId)After=&I;
            SameInstances&=After&&After->Ammo==Before.Ammo&&After->ReservedAmmo==Before.ReservedAmmo&&After->CooldownDeadline==Before.CooldownDeadline;
        }
        return Test->TestTrue(TEXT("Same point and repeated HUD consume neither duplicates audio nor mutates action/resource identity"),
            Game->GetActionAudioState().NextSequence==Seq&&Game->GetActionAudioState().Records.Num()==FactsBefore
            &&HUD->GetActionAudioPlayReceipts().Num()==RequestsBefore&&Game->GetEquipmentView().Revision==Revision
            &&Player->GetMeleeCombatState().NextAttackId==Attack&&Player->GetMeleeCombatState().NextEventId==CombatEvent
            &&Player->GetWeaponActionsState().NextActionId==Action&&Player->GetWeaponActionsState().NextEventId==WeaponEvent
            &&Game->GetEquipmentView().NextCritDraw==Crit&&Player->GetWeaponActionsState().Budget.Focus==Focus
            &&Player->GetWeaponActionsState().Budget.ReservedFocus==ReservedFocus&&SameInstances);
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMeleeAudioPrimaryThreeFamilies,
    "CodexDungeon.Content.MeleeAudioJournal.NormalPrimaryThreeFamiliesEachStageOnce",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FMeleeAudioPrimaryThreeFamilies::RunTest(const FString&)
{
    for(int32 Family=0;Family<3;++Family)
    {
        FMeleeAudioWorld F(this);if(!F.Create(Family))return false;
        for(uint32 Stage=0;Stage<3;++Stage)
        {
            if(!F.Pulse(EKeys::J))return false;const auto A=F.Player->GetMeleeCombatState().Action;
            if(!TestTrue(TEXT("Normal J accepts real bound melee stage and instance"),A.Active&&A.Stage==Stage&&A.WeaponInstanceId==F.AcquiredInstance))return false;
            if(!F.AdvanceTo(std::nextafter(A.ActiveStart,-std::numeric_limits<double>::infinity())))return false;
            TestEqual(TEXT("No primary sound before its true active boundary"),F.Facts(MeleeCue(Family,Stage),A.AttackId,A.ActiveStart),0);
            if(!F.AdvanceTo(A.ActiveStart))return false;
            int32 Windows=0;for(const auto& W:F.Player->GetMeleeCombatState().IssuedWindows)
                if(W.AttackId==A.AttackId&&W.FrozenAction.Stage==Stage&&W.Start==A.ActiveStart&&W.FrozenAction.WeaponInstanceId==F.AcquiredInstance)++Windows;
            if(!TestEqual(TEXT("Real kernel issued exactly one authoritative active window"),Windows,1))return false;
            if(!F.ExpectOne(MeleeCue(Family,Stage),A.AttackId,A.ActiveStart,F.Game->GetEquipmentView().Revision)||!F.NoReplay())return false;
            if(!F.AdvanceTo(A.End))return false;
        }
        TestEqual(TEXT("A whole real normal chain produces exactly three facts"),F.Game->GetActionAudioState().Records.Num(),3);
        TestEqual(TEXT("A whole real normal chain produces exactly three requests"),F.HUD->GetActionAudioPlayReceipts().Num(),3);
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMeleeAudioSkillsThreeFamilies,
    "CodexDungeon.Content.MeleeAudioJournal.NormalSkillsRealIndependentSubhitsOnce",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FMeleeAudioSkillsThreeFamilies::RunTest(const FString&)
{
    for(int32 Family=0;Family<3;++Family)
    {
        FMeleeAudioWorld F(this);if(!F.Create(Family)||!F.Pulse(EKeys::K))return false;
        const auto A=F.Player->GetWeaponActionsState().Action;const auto* D=MC::GetWeaponDefinition(A.Weapon);
        if(!TestTrue(TEXT("Normal K accepts actual equipped skill, timeline and authored independent windows"),
            A.Active&&A.Type==MW::EAction::Skill&&A.InstanceId==F.AcquiredInstance&&D&&D->Skill.SubhitCount==(Family==2?3u:1u)))return false;
        const FString Cue=MeleeCue(Family,2);
        for(uint32 Sub=0;Sub<D->Skill.SubhitCount;++Sub)
        {
            const double At=A.Start+D->Skill.SubhitTimes[Sub]/(1+A.SpeedPct/100.);
            if(!F.AdvanceTo(std::nextafter(At,-std::numeric_limits<double>::infinity())))return false;
            TestEqual(TEXT("No skill sound before this subhit's actual source boundary"),F.Facts(Cue,A.ActionId,At),0);
            if(!F.AdvanceTo(At))return false;
            int32 Issued=0;for(const auto& E:F.Player->GetWeaponActionsState().Issued)
                if(E.ActionId==A.ActionId&&E.InstanceId==F.AcquiredInstance&&E.Kind==MW::EEvent::ActiveWindow&&E.SubhitId==Sub&&E.AtTime==At)++Issued;
            int32 World=0;for(const auto& E:F.Game->GetWeaponWorldState().Events)
                if(E.Kind==EDungeonWorldWeaponEventKind::WindowCreated&&E.Key.ActionId==A.ActionId&&E.Key.SubhitId==Sub&&E.AtTime==At)++World;
            if(!TestTrue(TEXT("Exactly one real skill emission and world window back this independent subhit"),Issued==1&&World==1))return false;
            if(!F.ExpectOne(Cue,A.ActionId,At,F.Game->GetEquipmentView().Revision)||!F.NoReplay())return false;
        }
        if(!F.AdvanceTo(A.End))return false;
        TestEqual(TEXT("Skill facts count exactly matches real independent window count"),F.Game->GetActionAudioState().Records.Num(),int32(D->Skill.SubhitCount));
        TestEqual(TEXT("Skill requests count exactly matches real independent window count"),F.HUD->GetActionAudioPlayReceipts().Num(),int32(D->Skill.SubhitCount));
    }
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FMeleeAudioInterruptedPrimary,
    "CodexDungeon.Content.MeleeAudioJournal.RealPreActivePoiseCancelIsSilentThenFreshPrimaryOnce",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FMeleeAudioInterruptedPrimary::RunTest(const FString&)
{
    for(int32 Family=0;Family<3;++Family)
    {
        FMeleeAudioWorld F(this);if(!F.Create(Family)||!F.Pulse(EKeys::J))return false;
        const auto Cancelled=F.Player->GetMeleeCombatState().Action;
        if(!Cancelled.Active||!F.AdvanceTo(std::nextafter(Cancelled.ActiveStart,-std::numeric_limits<double>::infinity())))return false;
        const float HP=F.Player->Health;F.Player->ApplyCombatHit(1.f,nullptr,1000.f);
        if(!TestTrue(TEXT("Public real damage and poise break interrupted before the window"),
            F.Player->Health<HP&&!F.Player->GetMeleeCombatState().Action.Active&&F.Player->AnimationName==TEXT("hurt")))return false;
        if(!F.AdvanceTo(Cancelled.End+.7))return false;
        TestTrue(TEXT("Unreached old active deadline has no sound, fact or playback request"),
            F.Game->GetActionAudioState().Records.IsEmpty()&&F.HUD->GetActionAudioPlayReceipts().IsEmpty());
        if(!F.Pulse(EKeys::J))return false;const auto Fresh=F.Player->GetMeleeCombatState().Action;
        if(!TestTrue(TEXT("Fresh real J starts a new first-stage action after actual recovery"),
            Fresh.Active&&Fresh.Stage==0&&Fresh.AttackId!=Cancelled.AttackId))return false;
        if(!F.AdvanceTo(Fresh.ActiveStart)||!F.ExpectOne(MeleeCue(Family,0),Fresh.AttackId,Fresh.ActiveStart,F.Game->GetEquipmentView().Revision)||!F.NoReplay())return false;
    }
    return true;
}
#endif
