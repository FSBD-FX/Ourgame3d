#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "../DungeonRunInstaller.h"
#include "../DungeonRunSnapshotCodec.h"
#include "RunCodecFixture_v001.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/SpectatorPawn.h"

namespace
{
// This target really follows native InitGame/Login/PostLogin/BeginPlay. The
// old FCodecWorld is intentionally used only for genuine already-running source
// and ordinary Prepare controls, never as proof of a pristine target startup.
struct FPristineNativeWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;UGameInstance* Instance=nullptr;UGameViewportClient* Viewport=nullptr;
    ULocalPlayer* LocalPlayer=nullptr;ADungeonGameMode* Game=nullptr;APlayerController* Controller=nullptr;ADungeonHUD* HUD=nullptr;
    int32 FightersBeforeBeginPlay=0,PawnsBeforeBeginPlay=0;
    explicit FPristineNativeWorld(FAutomationTestBase& T):Test(T){}
    ~FPristineNativeWorld()
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
    int32 Fighters()const
    {int32 Count=0;for(TActorIterator<ADungeonFighter> It(World);It;++It)if(!It->IsActorBeingDestroyed())++Count;return Count;}
    int32 Pawns()const
    {int32 Count=0;for(TActorIterator<APawn> It(World);It;++It)if(!It->IsActorBeingDestroyed())++Count;return Count;}
    bool Create(bool PristineOption)
    {
        if(!Test.TestNotNull(TEXT("Native startup fixture has actual Engine"),GEngine))return false;
        const auto Settings=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).RequiresHitProxies(false)
            .CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
        World=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&Settings);
        if(!Test.TestNotNull(TEXT("Native startup creates independent actual UWorld"),World))return false;
        auto& Context=GEngine->CreateNewWorldContext(EWorldType::Game);
        Instance=NewObject<UGameInstance>(GEngine);World->SetGameInstance(Instance);
        Context.OwningGameInstance=Instance;Context.SetCurrentWorld(World);
        Viewport=NewObject<UGameViewportClient>(GEngine);Context.GameViewport=Viewport;
        Viewport->Init(Context,Instance,false); // Real headless viewport object; no native window or fake controller.
        FURL URL;URL.AddOption(TEXT("game=/Script/CodexDungeon.DungeonGameMode"));
        if(PristineOption)URL.AddOption(TEXT("DungeonContinuePristine"));
        if(!Test.TestTrue(TEXT("Native World.SetGameMode chooses real project GameMode"),World->SetGameMode(URL)))return false;
        World->InitializeActorsForPlay(URL,true);
        Game=World->GetAuthGameMode<ADungeonGameMode>();
        if(!Test.TestTrue(TEXT("Actual native InitGame and actor initialization create project GM/GameState before Login"),
            Game&&Game->IsActorInitialized()&&World->AreActorsInitialized()&&World->GetGameState()&&Game->OptionsString.Contains(TEXT("game="))))return false;
        LocalPlayer=NewObject<ULocalPlayer>(GEngine,GEngine->LocalPlayerClass);
        if(!Test.TestTrue(TEXT("Actual local player joins this fixture's real GameInstance and viewport"),LocalPlayer
            &&Instance->AddLocalPlayer(LocalPlayer,FPlatformUserId::CreateFromInternalId(0))!=INDEX_NONE&&LocalPlayer->GetGameInstance()==Instance&&LocalPlayer->GetWorld()==World))return false;
        FString Error;
        if(!Test.TestTrue(TEXT("Actual LocalPlayer SpawnPlayActor executes Login, SetPlayer, PostLogin and HandleStartingNewPlayer"),
            LocalPlayer->SpawnPlayActor(URL.ToString(1),Error,World)))
        {Test.AddInfo(TEXT("Native startup Login diagnosis: ")+Error);return false;}
        Controller=LocalPlayer->PlayerController;HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
        if(!Test.TestTrue(TEXT("Native Login positive control has actual authoritative local PC, PlayerState, Input and HUD before StartPlay"),
            Controller&&Controller->GetWorld()==World&&Controller->HasAuthority()&&Controller->IsLocalController()
            &&Controller->GetLocalPlayer()==LocalPlayer&&Controller->PlayerState&&Controller->PlayerInput&&HUD
            &&UGameplayStatics::GetPlayerController(Game,0)==Controller))return false;
        FightersBeforeBeginPlay=Fighters();PawnsBeforeBeginPlay=Pawns();
        World->BeginPlay();
        return Test.TestTrue(TEXT("Native World.BeginPlay really dispatches project StartPlay and actor BeginPlay"),
            World->GetBegunPlay()&&Game->HasActorBegunPlay()&&Controller->HasActorBegunPlay()&&HUD->HasActorBegunPlay());
    }
    void Frame(float Dt)
    {Game->Tick(Dt);Controller->PlayerInput->Tick(Dt);TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,Dt,false);HUD->Tick(Dt);}
    bool Key(FKey K,bool Down)
    {
        Controller->InputKey(FInputKeyParams(K,Down?IE_Pressed:IE_Released,Down?1.:0.));
        Controller->PlayerInput->Tick(.005f);TArray<UInputComponent*> Stack;Controller->PlayerInput->ProcessInputStack(Stack,.005f,false);
        return Controller->IsInputKeyDown(K)==Down;
    }
    bool Pulse(FKey K)
    {if(!Key(K,true)||!Controller->WasInputKeyJustPressed(K))return false;Frame(.005f);if(!Key(K,false))return false;Frame(.005f);return true;}
    bool AdvanceTo(double At)
    {
        if(At<Game->GetSimulationTime())return false;
        for(int32 Index=0;Index<64&&Game->GetSimulationTime()<At;++Index)
        {
            const double Before=Game->GetSimulationTime(),Left=At-Before;float Dt=float(FMath::Min(.05,Left));
            if(double(Dt)>Left)Dt=std::nextafter(Dt,0.f);
            if(!(Dt>0.f))return false;Frame(Dt);if(Game->GetSimulationTime()<=Before)return false;
        }
        return Game->GetSimulationTime()==At;
    }
};
bool NoPublishedRun(const FPristineNativeWorld& Target)
{
    const auto Equipment=Target.Game->CaptureEquipmentSnapshot();const auto Rewards=Target.Game->CaptureRunRewardsSnapshot();
    const auto Fog=Target.Game->CaptureRunExplorationSnapshot();const auto& World=Target.Game->GetWeaponWorldState();const auto& Audio=Target.Game->GetActionAudioState();
    return !Target.Game->PlayerFighter&&Target.Game->Enemies.IsEmpty()&&Target.Game->Pickups.IsEmpty()
        &&Target.Game->GetRunRestartSerial()==0&&Target.Game->GetSimulationTime()==0.&&Target.Game->GetRunPresentationEpoch()==0
        &&!Equipment.View.Bound&&!Equipment.HasInventory&&!Equipment.View.RunGuid.IsValid()
        &&Equipment.View.RunAlias==0&&Equipment.View.OwnerId==0&&Equipment.View.RoomInstanceId==0&&Equipment.View.Revision==0
        &&Equipment.View.CombatSeed==0&&Equipment.View.NextCritDraw==0&&Equipment.Sources.IsEmpty()&&Equipment.CritReceipts.IsEmpty()
        &&!Target.Game->GetEquipmentInventoryState()&&!Target.Game->GetSceneRoomView().Active
        &&!Rewards.Bound&&!Rewards.RunGuid.IsValid()&&Rewards.Deaths.IsEmpty()&&Rewards.Sources.IsEmpty()&&Rewards.Objects.IsEmpty()
        &&Rewards.Collections.IsEmpty()&&Rewards.RetiredEntities.IsEmpty()&&Rewards.RoomExits.IsEmpty()
        &&!Fog.RunGuid.IsValid()&&Fog.Rooms.IsEmpty()&&!World.RunGuid.IsValid()&&World.ActorBindings.IsEmpty()
        &&!Audio.RunGuid.IsValid()&&Audio.Records.IsEmpty();
}
TArray<uint8> NoRunSignature(const FPristineNativeWorld& Target)
{
    FRunSignature Signature;Signature.V(Target.Game->GetRunRestartSerial(),Target.Game->GetSimulationTime(),Target.Game->GetRunPresentationEpoch(),
        Target.Game->RoomNumber,Target.Game->bGameOver,Target.Game->bWaitingForStart,Target.Game->bRoomCleared);
    Signature.String(Target.Game->LastMessage);Signature.Equipment(Target.Game->CaptureEquipmentSnapshot());
    Signature.Rewards(Target.Game->CaptureRunRewardsSnapshot());Signature.Exploration(Target.Game->CaptureRunExplorationSnapshot());
    Signature.World(DungeonWorldSnapshot::Capture(Target.Game->GetWeaponWorldState()));
    const auto& Audio=Target.Game->GetActionAudioState();Signature.Guid(Audio.RunGuid);Signature.V(Audio.RoomInstanceId,Audio.NextSequence,Audio.Records.Num());
    return Signature.Bytes;
}
bool PristineSource(FCodecWorld& Source,FDungeonRunSnapshot& Saved,FDungeonValidatedRun& Sealed)
{
    if(!Source.Test.TestTrue(TEXT("Genuine original source starts ordinary bound Scene through normal Enter"),Source.Create()))return false;
    IV::FItem Empty;Empty.ContentId="WPN-XBW-001";Empty.Ammo=0.;
    const auto Receipt=Source.Game->RegisterEquipmentSource(TEXT("pristine.bootstrap.real.empty-xbw"),Empty,Source.Player->GetGroundPosition()+FVector2D(30.,0.),true);
    if(!Source.Test.TestTrue(TEXT("Original real E and absolute equipment deadline acquire empty crossbow; T starts original reload"),Receipt.Ok()
        &&Source.Pulse(EKeys::E)&&Source.Game->GetEquipmentView().Action.Active&&Source.AdvanceTo(Source.Player->GetEquipmentActionDeadline())
        &&Source.Player->WeaponId==TEXT("WPN-XBW-001")&&Source.Pulse(EKeys::T)))return false;
    const auto Reload=Source.Player->GetWeaponActionsState().Action;Source.Player->GetWeaponMuzzleComponent()->SetRelativeLocation(FVector(24.,7.,65.));
    if(!Source.Test.TestTrue(TEXT("Genuine future reload completion premise includes elapsed draw/insert and native custom muzzle"),
        Reload.Active&&Reload.Type==WA::EAction::Reload&&Source.AdvanceTo(Reload.Start+.65)
        &&Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==1&&Source.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==1))return false;
    FDungeonValidatedRun Captured;
    if(!CodecSeal(Source,Saved,Captured,TEXT("Actual whole saved source for pristine bootstrap")))return false;
    TArray<uint8> Bytes;FString Why;const auto Oracle=FCodecOracle::Bytes(Saved);
    return Source.Test.TestTrue(TEXT("Real Aggregate/Codec source is valid and complete independently of new pristine APIs"),
        DungeonRunSnapshotCodec::Encode(Saved,Bytes,Why)&&Bytes==Oracle&&DungeonRunSnapshotCodec::Decode(Oracle,Sealed,Why)
        &&Sealed.IsValid()&&CodecSignature(*Sealed.Get())==CodecSignature(Saved));
}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunPristineNativeStartup,
    "CodexDungeon.Content.RunPristine.NativeInitLoginStartPlayNoRunAndClosedInputs",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunPristineNativeStartup::RunTest(const FString&)
{
    FPristineNativeWorld Ordinary(*this);
    if(!Ordinary.Create(false))return false;
    if(!TestTrue(TEXT("Ordinary native startup positive control really spawns/possesses project Fighter and executes original RestartRun"),
        Ordinary.Game->DefaultPawnClass==ADungeonFighter::StaticClass()&&Ordinary.FightersBeforeBeginPlay==1
        &&Ordinary.Game->PlayerFighter&&Ordinary.Controller->GetPawn()==Ordinary.Game->PlayerFighter
        &&Ordinary.Game->GetRunRestartSerial()>0&&Ordinary.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open))return false;
    FPristineNativeWorld Target(*this);if(!Target.Create(true))return false;FString Why;
    TestTrue(TEXT("Explicit native InitGame option establishes an actual pristine Continue origin"),Target.Game->IsPristineContinueBootstrap(Why));
    TestTrue(TEXT("InitGame prevents both native default Fighter and native spectator shell before Login finishes"),
        !Target.Game->DefaultPawnClass&&!Target.Game->SpectatorClass&&Target.FightersBeforeBeginPlay==0&&Target.PawnsBeforeBeginPlay==0
        &&Target.Fighters()==0&&Target.Pawns()==0&&Target.Controller->GetPawn()==nullptr&&Target.Controller->GetSpectatorPawn()==nullptr);
    TestTrue(TEXT("Native BeginPlay leaves no new Run, no starter inventory, no logical Run IDs or combat random stream"),NoPublishedRun(Target));
    TestTrue(TEXT("No-Run process is explicitly closed, separate from Preparing and restored Continue arming"),
        Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap&&Target.Game->IsRunInstallGated()
        &&!Target.Controller->PlayerState->IsOnlyASpectator());
    const auto Before=NoRunSignature(Target);
    for(const FKey Key:{EKeys::R,EKeys::E,EKeys::J,EKeys::Enter})
        if(!TestTrue(TEXT("Actual fresh keyboard press/release is delivered through native local Input"),Target.Pulse(Key)))return false;
    TestFalse(TEXT("Public BeginEquipmentRun cannot manufacture a starter behind pristine gate"),Target.Game->BeginEquipmentRun());
    Target.Game->RestartRun();Target.Frame(.2f);
    TestTrue(TEXT("R/E/J/Enter and direct new-Run entry cannot create Pawn, mutate empty owners or open the gate"),
        Target.Game->IsPristineContinueBootstrap(Why)&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap
        &&NoPublishedRun(Target)&&Target.Fighters()==0&&Target.Pawns()==0&&NoRunSignature(Target)==Before);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunPristineReload,
    "CodexDungeon.Content.RunPristine.SealedReloadInstallsWithoutNewRunAndContinuesOriginalDeadline",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunPristineReload::RunTest(const FString&)
{
    FCodecWorld Source(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!PristineSource(Source,Saved,Sealed))return false;
    const auto Reload=Source.Player->GetWeaponActionsState().Action;const auto Updates=Saved.Equipment.InventoryState.RuntimeUpdates.size();
    FPristineNativeWorld Target(*this);if(!Target.Create(true))return false;
    FString Why;TestTrue(TEXT("Actual native target is pristine without first constructing a replacement Run"),Target.Game->IsPristineContinueBootstrap(Why)&&NoPublishedRun(Target));
    FDungeonPreparedRun Prepared;const bool Ready=FDungeonRunInstaller::PreparePristine(*Target.Game,Sealed,Prepared,Why);
    if(!TestTrue(TEXT("New explicit pristine API prepares complete sealed real source into untouched native startup target"),Ready&&Prepared.IsReady()))
    {AddInfo(TEXT("Pristine preparation diagnosis: ")+Why);return false;}
    TestTrue(TEXT("Preparing only owns hidden actors; no starter or authoritative Run is published"),NoPublishedRun(Target)
        &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing&&Prepared.GetSavedSnapshot()
        &&CodecSignature(*Prepared.GetSavedSnapshot())==CodecSignature(Saved)&&Prepared.GetStagedActors().Num()==Saved.Fighters.Num()+1);
    for(const auto& Actor:Prepared.GetStagedActors())TestTrue(TEXT("Every staged native resource is independent, hidden, collision-off and tick-off"),
        Actor.IsValid()&&Actor->IsHidden()&&!Actor->GetActorEnableCollision()&&!Actor->IsActorTickEnabled());
    if(!TestTrue(TEXT("Existing full Installer really possesses and atomically installs pristine prepared group"),
        FDungeonRunInstaller::Install(*Target.Game,Prepared,Why)&&!Prepared.IsReady()))return false;
    FDungeonRunSnapshot Installed;
    if(!TestTrue(TEXT("Actual installed paused owner graph captures through full real Aggregate"),Target.Game->CaptureRunSnapshot(Installed,Why)))return false;
    TestTrue(TEXT("Every native value equals original Run, with zero new-Run restart boundary"),CodecSignature(Installed)==CodecSignature(Saved)
        &&Target.Game->GetRunRestartSerial()==0&&Target.Controller->GetPawn()==Target.Game->PlayerFighter
        &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&!Target.Controller->PlayerState->IsOnlyASpectator());
    Target.Frame(.2f);FDungeonRunSnapshot Paused;
    if(!TestTrue(TEXT("Actual restored Run stays completely paused before fresh Continue"),Target.Game->CaptureRunSnapshot(Paused,Why)))return false;
    TestTrue(TEXT("Wall-time-like ticks neither advance saved clocks nor replay spent audio"),CodecSignature(Paused)==CodecSignature(Saved)
        &&Target.HUD->GetActionAudioPlayReceipts().IsEmpty()&&Target.Game->GetActionAudioState().Records.IsEmpty());
    if(!TestTrue(TEXT("Real neutral and fresh native Enter resumes restored Run"),Target.Pulse(EKeys::Enter)&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open))return false;
    if(!TestTrue(TEXT("Restored player reaches original absolute reload deadline"),Target.AdvanceTo(Reload.End)))return false;
    const auto* Inventory=Target.Game->GetEquipmentInventoryState();const auto& Action=Target.Game->PlayerFighter->GetWeaponActionsState();
    TestTrue(TEXT("Original action/instance refill once, without starter/new IDs/crit draw or elapsed sound replay"),Inventory
        &&Inventory->RuntimeUpdates.size()==Updates+1&&Inventory->RuntimeUpdates.back().InstanceId==Reload.InstanceId
        &&Inventory->RuntimeUpdates.back().BeforeAmmo==0.&&Inventory->RuntimeUpdates.back().Ammo==1.
        &&Action.Action.ActionId==Reload.ActionId&&!Action.Action.Active&&Target.Game->GetEquipmentView().RunGuid==Saved.RunGuid
        &&Target.Game->GetEquipmentView().NextCritDraw==Saved.Equipment.View.NextCritDraw&&Target.Game->GetRunRestartSerial()==0
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==1&&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==0
        &&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==0);
    Target.Frame(.2f);TestTrue(TEXT("Later ordinary ticks cannot duplicate original completion"),
        Target.Game->GetEquipmentInventoryState()->RuntimeUpdates.size()==Updates+1&&Target.HUD->GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==1);
    FDungeonRunSnapshot SourceAfter;if(!Source.Capture(TEXT("Original real source after pristine restore"),SourceAfter))return false;
    TestTrue(TEXT("Pristine recovery never mutates original saved source"),CodecSignature(SourceAfter)==CodecSignature(Saved));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRunPristineRefusal,
    "CodexDungeon.Content.RunPristine.RefusesExistingOrContaminatedTargetAndRollsBackClosed",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FRunPristineRefusal::RunTest(const FString&)
{
    FCodecWorld Source(*this);FDungeonRunSnapshot Saved;FDungeonValidatedRun Sealed;if(!PristineSource(Source,Saved,Sealed))return false;
    FCodecWorld Ordinary(*this);FDungeonRunSnapshot OrdinarySaved;FDungeonValidatedRun OrdinarySealed;
    if(!Ordinary.Create()||!CodecSeal(Ordinary,OrdinarySaved,OrdinarySealed,TEXT("Actual ordinary target positive control")))return false;
    FString Why;
    {
        FDungeonPreparedRun Existing;
        if(!TestTrue(TEXT("Original normal Prepare still genuinely requires and accepts complete existing target"),
            FDungeonRunInstaller::Prepare(*Ordinary.Game,Sealed,Existing,Why)&&Existing.IsReady()))return false;
        const auto* Previous=Existing.GetSavedSnapshot();const auto Actors=Existing.GetStagedActors();
        TestFalse(TEXT("Pristine API cannot bypass normal existing-Run capture or replace its nonempty prepared output"),
            FDungeonRunInstaller::PreparePristine(*Ordinary.Game,Sealed,Existing,Why));
        TestTrue(TEXT("Existing normal prepared group stays exact on pristine-scope refusal"),!Why.IsEmpty()&&Existing.IsReady()
            &&Existing.GetSavedSnapshot()==Previous&&Existing.GetStagedActors()==Actors&&Ordinary.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing);
    }
    FDungeonRunSnapshot OrdinaryAfter;if(!Ordinary.Capture(TEXT("Ordinary target after pristine refusal and normal RAII abort"),OrdinaryAfter))return false;
    TestTrue(TEXT("Normal Prepare old-Run contract and normal abort Open behavior remain unchanged"),Ordinary.Game->GetRunInstallGate()==EDungeonRunInstallGate::Open
        &&CodecSignature(OrdinaryAfter)==CodecSignature(OrdinarySaved));
    FPristineNativeWorld Target(*this);if(!Target.Create(true))return false;const auto Before=NoRunSignature(Target);
    TestTrue(TEXT("New native origin is pristine before real staged resource rollback"),Target.Game->IsPristineContinueBootstrap(Why)&&NoPublishedRun(Target));
    {
        FDungeonPreparedRun Staged;
        if(!TestTrue(TEXT("Pristine positive staging premise creates actual native resources"),
            FDungeonRunInstaller::PreparePristine(*Target.Game,Sealed,Staged,Why)&&Staged.IsReady()))return false;
        TestTrue(TEXT("Staged lifetime is genuinely nonempty and still unpublished"),!Staged.GetStagedActors().IsEmpty()&&NoPublishedRun(Target)
            &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing);
    }
    TestTrue(TEXT("Actual prepared destructor releases all staged Pawns and returns to closed pristine gate, never Open"),
        Target.Game->IsPristineContinueBootstrap(Why)&&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap
        &&NoPublishedRun(Target)&&Target.Fighters()==0&&Target.Pawns()==0&&NoRunSignature(Target)==Before);
    {
        FDungeonPreparedRun Invalidated;
        if(!TestTrue(TEXT("Second real pristine staging succeeds before native invalidation"),
            FDungeonRunInstaller::PreparePristine(*Target.Game,Sealed,Invalidated,Why)&&Invalidated.IsReady()))return false;
        if(!TestTrue(TEXT("Invalidation premise has a real owned staged native actor"),!Invalidated.GetStagedActors().IsEmpty()))return false;
        auto* Victim=Invalidated.GetStagedActors()[0].Get();
        if(!TestTrue(TEXT("Actual native staged actor is destroyed to establish genuine invalidation premise"),Victim&&Victim->Destroy()))return false;
        TestFalse(TEXT("Existing Install detects lost staged resource and cannot publish any partial Run"),FDungeonRunInstaller::Install(*Target.Game,Invalidated,Why));
        TestTrue(TEXT("Failed invalidated group stays behind preparation gate until RAII cleanup"),NoPublishedRun(Target)
            &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::Preparing&&Invalidated.IsReady());
    }
    TestTrue(TEXT("Invalidation rollback releases remaining native resources without opening the empty world"),
        Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap&&Target.Game->IsPristineContinueBootstrap(Why)
        &&NoPublishedRun(Target)&&Target.Fighters()==0&&Target.Pawns()==0&&NoRunSignature(Target)==Before);
    auto* Foreign=Target.World->SpawnActor<ADungeonFighter>();
    if(!TestTrue(TEXT("Real unrelated Fighter contaminates target before pristine eligibility check"),Foreign&&Target.Fighters()==1))return false;
    TestFalse(TEXT("Existing native gameplay actor disqualifies purported pristine world"),Target.Game->IsPristineContinueBootstrap(Why));
    {
        FDungeonPreparedRun Previous;
        if(!TestTrue(TEXT("Independent old normal prepared output is genuinely nonempty before polluted-target refusal"),
            FDungeonRunInstaller::Prepare(*Ordinary.Game,Sealed,Previous,Why)&&Previous.IsReady()))return false;
        const auto* PreviousSnapshot=Previous.GetSavedSnapshot();const auto PreviousActors=Previous.GetStagedActors();
        TestFalse(TEXT("Polluted native target cannot use pristine restore or erase unrelated actor"),FDungeonRunInstaller::PreparePristine(*Target.Game,Sealed,Previous,Why));
        TestTrue(TEXT("Failure keeps nonempty old output identity and unrelated live native actor, with no new Run or publication"),
            Previous.IsReady()&&Previous.GetSavedSnapshot()==PreviousSnapshot&&Previous.GetStagedActors()==PreviousActors
            &&Foreign&&!Foreign->IsActorBeingDestroyed()&&Target.Fighters()==1&&NoPublishedRun(Target)
            &&Target.Game->GetRunInstallGate()==EDungeonRunInstallGate::PristineBootstrap&&NoRunSignature(Target)==Before);
    }
    return true;
}
#endif
