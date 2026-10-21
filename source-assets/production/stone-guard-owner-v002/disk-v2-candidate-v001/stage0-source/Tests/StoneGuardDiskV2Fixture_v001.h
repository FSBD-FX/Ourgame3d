#pragma once
#include "StoneGuardOwnerFixture_v002.h"
#include "../DungeonRunSaveAdapterV2.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Engine/GameViewportClient.h"
#include "Engine/LocalPlayer.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/SpectatorPawn.h"
namespace DiskV2Tests
{
namespace Save=DungeonRunSaveAdapterV2;
namespace Store=DungeonSaveGenerationStore;
namespace Codec=DungeonRunSnapshotCodec;
using namespace GuardOwnerTests;
TArray<uint8> GenerationSig(const Store::FGeneration& G)
{
 FSignature S;S.V(G.ProfileId.A,G.ProfileId.B,G.ProfileId.C,G.ProfileId.D,G.GenerationId,G.ParentGeneration,G.RestoredFromGeneration);
 S.String(G.Versions.Schema);S.String(G.Versions.ContentRules);S.String(G.Versions.Coordinates);S.String(G.BuildId);S.V(G.RunSimulationTime.IsSet());
 if(G.RunSimulationTime.IsSet())S.V(G.RunSimulationTime.GetValue());S.V(G.CanonicalPayload.Num());S.Bytes.Append(G.CanonicalPayload);return S.Bytes;
}
TArray<uint8> LoadedSig(const Save::FLoadedRun& L)
{FSignature S;S.Bytes.Append(GenerationSig(L.Generation));S.V(L.Run.IsValid(),L.Slot,L.ObservedHeadGeneration);if(L.Run.IsValid())S.Bytes.Append(RunSig(*L.Run.Get()));return S.Bytes;}
// Independent complete fixed-shape envelope; uses the frozen named-field Run
// oracle, never new adapter output or production Encode to create expectations.
Store::FGeneration Expected(const FDungeonRunSnapshot& S,const Save::FWriteRequest& R,bool V1=false)
{
 Store::FGeneration G;G.ProfileId=R.Context.ProfileId;G.GenerationId=R.GenerationId;G.ParentGeneration=R.ParentGeneration;G.BuildId=R.BuildId;G.RunSimulationTime=S.SimulationTime;
 G.Versions=V1?DungeonRunSaveAdapter::CurrentVersions:Save::CurrentVersions;
 auto O=FCodecOracle::Obj();O->SetStringField(TEXT("adapter"),V1?TEXT("bound-run-only-v1"):TEXT("bound-run-only-v2"));O->SetStringField(TEXT("buildId"),G.BuildId);
 O->SetField(TEXT("generationId"),FCodecOracle::Value(G.GenerationId));O->SetField(TEXT("parentGeneration"),FCodecOracle::Value(G.ParentGeneration));O->SetStringField(TEXT("profileId"),G.ProfileId.ToString(EGuidFormats::Digits).ToLower());
 O->SetObjectField(TEXT("run"),V1?FCodecOracle::Document(S):FGuardWire::DocumentV2(S));O->SetStringField(TEXT("runGuid"),S.RunGuid.ToString(EGuidFormats::Digits).ToLower());O->SetField(TEXT("runSimulationTime"),FCodecOracle::Value(S.SimulationTime));O->SetStringField(TEXT("scope"),V1?TEXT("BoundDevelopmentRunV1"):TEXT("BoundDevelopmentRunV2"));
 auto V=FCodecOracle::Obj();V->SetStringField(TEXT("contentRules"),G.Versions.ContentRules);V->SetStringField(TEXT("coordinates"),G.Versions.Coordinates);V->SetStringField(TEXT("schema"),G.Versions.Schema);O->SetObjectField(TEXT("versions"),V);G.CanonicalPayload=FCodecOracle::Bytes(O);return G;
}
struct FDisk
{
 FAutomationTestBase& Test;FString Root;Save::FReadContext Context;
 explicit FDisk(FAutomationTestBase& T):Test(T)
 {Root=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Automation/StoneGuardDiskV2")/FGuid::NewGuid().ToString(EGuidFormats::Digits));Context.ProfilesDirectory=Root/Save::DirectoryName;Context.ProfileId=FGuid::NewGuid();Test.AddInfo(TEXT("Retained real isolated V2 IO: ")+Root);}
 Save::FWriteRequest Request(const FDungeonRunSnapshot& S,uint64 Id=1,uint64 Parent=0)const
 {Save::FWriteRequest R;R.Context=Context;R.RunGuid=S.RunGuid;R.OwnerId=S.OwnerId;R.GenerationId=Id;R.ParentGeneration=Parent;R.BuildId=TEXT("actual-guard-disk-v2-proof");return R;}
 bool IO()
 {TArray<uint8> B{0x11,0x27,0x93},Read;return Test.TestTrue(TEXT("Real independent V2 namespace write/read premise"),IFileManager::Get().MakeDirectory(*Context.ProfilesDirectory,true)&&FFileHelper::SaveArrayToFile(B,*(Root/TEXT("io-proof.bin")))&&FFileHelper::LoadFileToArray(Read,*(Root/TEXT("io-proof.bin")))&&Read==B);}
};
// This validator is fixture-only and stronger than nonempty/transport acceptance:
// all actual header bytes and full independent payload bytes must match, and
// the independently captured genuine CodecV2 Run must actually decode/seal.
bool Seed(FDisk& F,Store::FGenerationStore& Disk,const FDungeonRunSnapshot& S,const Store::FGeneration& G)
{
 const auto Header=GenerationSig(G),RunBytes=FCodecOracle::Bytes(FGuardWire::DocumentV2(S)),Exact=RunSig(S);
 const Store::FPayloadValidator Validator=[&](const Store::FGeneration& In,FString& Why)
 {FDungeonValidatedRun V;return GenerationSig(In)==Header&&In.RunSimulationTime.IsSet()&&In.RunSimulationTime.GetValue()==S.SimulationTime&&Codec::Decode(RunBytes,V,Why)&&V.IsValid()&&RunSig(*V.Get())==Exact;};
 if(!F.Test.TestEqual(TEXT("Real isolated writer opens before new adapter semantics"),int32(Disk.OpenWriter()),int32(Store::EStatus::Ok)))return false;
 const auto Result=Disk.Commit(G,Validator);if(!F.Test.TestEqual(TEXT("Independent complete legal V2 fixture really publishes through Store mandatorycallback"),int32(Result.Status),int32(Store::EStatus::Ok)))return false;
 const auto Read=Disk.Load(Validator);return F.Test.TestTrue(TEXT("Published fixture header/payload and sealed current Guard actually read exact"),Read.Status==Store::EStatus::Ok&&Read.ObservedHeadGeneration==G.GenerationId&&GenerationSig(Read.Generation)==Header);
}
bool Source(FGuardWorld& W,FDungeonRunSnapshot& V2,FDungeonValidatedRun& Sealed,FDungeonRunSnapshot* OutLegacy=nullptr)
{
 if(!W.Test.TestTrue(TEXT("Genuine Scene/normalEnter source before DiskV2"),W.Create()))return false;FDungeonRunSnapshot Legacy;FDungeonValidatedRun V1;
 if(!CodecSeal(W,Legacy,V1,TEXT("Independent real V1 complete aggregate control before GuardV2")))return false;
 TArray<uint8> Bytes;FString Why;if(!W.Test.TestTrue(TEXT("Existing V1 codec exact immutablebyteoracle positive"),Codec::Encode(Legacy,Bytes,Why)&&Bytes==FCodecOracle::Bytes(Legacy)))return false;
 if(OutLegacy)*OutLegacy=Legacy;
 return W.Rich()&&SealGuard(W,V2,Sealed)&&W.Test.TestTrue(TEXT("Source fullRoot2 has every actual producer history independently of new DiskAdapter"),Codec::Encode(V2,Bytes,Why)&&Bytes==FCodecOracle::Bytes(FGuardWire::DocumentV2(V2)));
}
struct FV2PristineNativeWorld
{
    FAutomationTestBase& Test;
    UWorld* World=nullptr;UGameInstance* Instance=nullptr;UGameViewportClient* Viewport=nullptr;
    ULocalPlayer* LocalPlayer=nullptr;ADungeonGameMode* Game=nullptr;APlayerController* Controller=nullptr;ADungeonHUD* HUD=nullptr;
    int32 FightersBeforeBeginPlay=0,PawnsBeforeBeginPlay=0;
    explicit FV2PristineNativeWorld(FAutomationTestBase& T):Test(T){}
    ~FV2PristineNativeWorld()
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
bool NoPublishedRun(const FV2PristineNativeWorld& Target)
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

}
