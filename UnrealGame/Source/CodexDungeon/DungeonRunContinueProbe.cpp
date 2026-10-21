#include "DungeonRunContinueProbe.h"
#include "DungeonGameMode.h"
#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonRunSaveAdapter.h"
#include "DungeonRunSnapshotCodec.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/SpectatorPawn.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"
#include "HAL/PlatformMisc.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
namespace ProofWA=DungeonWeaponActions;
namespace ProofStore=DungeonSaveGenerationStore;
namespace ProofAdapter=DungeonRunSaveAdapter;
FString ProofBits(double Value)
{uint64 Bits=0;FMemory::Memcpy(&Bits,&Value,sizeof(Bits));return FString::Printf(TEXT("%016llx"),(unsigned long long)Bits);}
void ProofId(const TSharedPtr<FJsonObject>& Object,const TCHAR* Key,uint64 Value)
{Object->SetStringField(Key,LexToString(Value));}
TSharedPtr<FJsonObject> ProofCounts(ADungeonHUD& HUD)
{
    auto Value=MakeShared<FJsonObject>();
    Value->SetNumberField(TEXT("draw"),HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01")));
    Value->SetNumberField(TEXT("insert"),HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01")));
    Value->SetNumberField(TEXT("complete"),HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01")));
    return Value;
}
bool ProofAudioCounts(ADungeonHUD& HUD,int32 Draw,int32 Insert,int32 Complete)
{return HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_DRAW_01"))==Draw
    &&HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_INSERT_01"))==Insert
    &&HUD.GetActionAudioPlayRequests(TEXT("XBW_RELOAD_COMPLETE_01"))==Complete;}
}

struct FDungeonRunContinueProofState
{
    FString Directory,ProfilesDirectory,ProfileDirectory,BuildId,Role;
    FGuid ProfileId;
    int32 Phase=0,PhaseTicks=0;
    bool Stopped=false,Restore=false;
    double StartedWall=0.,PhaseWall=0.,InstalledWall=0.,CompletionWall=0.;
    TWeakObjectPtr<ADungeonGameMode> Game;
    TWeakObjectPtr<APlayerController> Controller;
    TWeakObjectPtr<ADungeonHUD> HUD;
    TMap<FKey,bool> Keys;
    TSharedPtr<FJsonObject> Report=MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Steps,InputRequests;
    FDungeonRunSnapshot Saved;
    ProofWA::FAction Reload;
    FDungeonEquipmentActionView EquipmentAction;
    uint64 RegisteredSourceId=0,RegisteredInstanceId=0;
    bool EquipmentAccepted=false;
    FDungeonPreparedRun Prepared;
    ProofAdapter::FLoadedRun Loaded;
    TArray<uint8> SavedCodec;

    void Key(FKey Code,bool Down)
    {
        if(Keys.FindRef(Code)==Down)return;
        if(auto* NativeController=Controller.Get())
        {
            NativeController->InputKey(FInputKeyParams(Code,Down?IE_Pressed:IE_Released,Down?1.:0.));
            Keys.Add(Code,Down);
            auto Entry=MakeShared<FJsonObject>();Entry->SetStringField(TEXT("key"),Code.ToString());
            Entry->SetBoolField(TEXT("down"),Down);ProofId(Entry,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());
            Entry->SetNumberField(TEXT("wall_elapsed_s"),FPlatformTime::Seconds()-StartedWall);
            InputRequests.Add(MakeShared<FJsonValueObject>(Entry));
        }
    }
    void Finish(const FString& Failure=FString())
    {
        if(Stopped)return;Stopped=true;
        TArray<FKey> Released;Keys.GetKeys(Released);for(const FKey& Code:Released)Key(Code,false);
        Report->SetBoolField(TEXT("passed"),Failure.IsEmpty());Report->SetStringField(TEXT("failure"),Failure);
        Report->SetArrayField(TEXT("steps"),Steps);Report->SetArrayField(TEXT("normal_input_requests"),InputRequests);
        Report->SetNumberField(TEXT("wall_elapsed_s"),FPlatformTime::Seconds()-StartedWall);
        Report->SetBoolField(TEXT("game_tick_called_manually"),false);Report->SetBoolField(TEXT("audio_device_auditioned"),false);
        Report->SetBoolField(TEXT("visual_running_proof_reviewed"),false);Report->SetNumberField(TEXT("formal_complete_units"),0);
        if(auto* NativeGame=Game.Get())
        {
            auto Boundary=MakeShared<FJsonObject>();ProofId(Boundary,TEXT("phase"),Phase);
            ProofId(Boundary,TEXT("gate"),uint64(NativeGame->GetRunInstallGate()));
            ProofId(Boundary,TEXT("restart_serial"),NativeGame->GetRunRestartSerial());
            Boundary->SetStringField(TEXT("sim_bits"),ProofBits(NativeGame->GetSimulationTime()));
            Boundary->SetBoolField(TEXT("waiting"),NativeGame->bWaitingForStart);
            Boundary->SetBoolField(TEXT("equipment_bound"),NativeGame->GetEquipmentView().Bound);
            const auto& Equipment=NativeGame->GetEquipmentView().Action;
            Boundary->SetBoolField(TEXT("equipment_action_active"),Equipment.Active);
            ProofId(Boundary,TEXT("equipment_action_id"),Equipment.ActionId);ProofId(Boundary,TEXT("equipment_operation_id"),Equipment.OperationId);
            Boundary->SetStringField(TEXT("equipment_deadline_bits"),ProofBits(Equipment.Deadline));
            if(auto* Player=NativeGame->PlayerFighter.Get())
            {
                Boundary->SetStringField(TEXT("weapon"),Player->WeaponId);
                const auto& Action=Player->GetWeaponActionsState().Action;
                Boundary->SetBoolField(TEXT("weapon_action_active"),Action.Active);ProofId(Boundary,TEXT("weapon_action_type"),uint64(Action.Type));
                ProofId(Boundary,TEXT("weapon_action_id"),Action.ActionId);ProofId(Boundary,TEXT("weapon_instance_id"),Action.InstanceId);
                Boundary->SetStringField(TEXT("reload_start_bits"),ProofBits(Action.Start));Boundary->SetStringField(TEXT("reload_end_bits"),ProofBits(Action.End));
            }
            if(HUD.IsValid())Boundary->SetObjectField(TEXT("actual_hud_counts"),ProofCounts(*HUD.Get()));
            Report->SetObjectField(TEXT("last_completed_boundary_diagnostic"),Boundary);
        }
        // Release failed staging while its real native world/GameMode is still alive.
        if(Prepared.IsReady())Prepared=FDungeonPreparedRun();
        FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),Writer);
        const FString Path=Directory/(Restore?TEXT("restore-report.json"):TEXT("source-report.json"));
        const bool Written=!Directory.IsEmpty()&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
        if(!Failure.IsEmpty()||!Written)
        {UE_LOG(LogTemp,Error,TEXT("Run two-process proof failed: %s reportWritten=%d"),*Failure,Written);}
        else
        {UE_LOG(LogTemp,Display,TEXT("Run two-process %s proof complete: %s"),*Role,*Path);}
        FPlatformMisc::RequestExitWithStatus(false,Failure.IsEmpty()&&Written?0:3);
    }
    bool Require(bool Value,const FString& Why)
    {if(!Value){Finish(Why);return false;}return true;}
    void Next(int32 Value,const TCHAR* Name)
    {
        Phase=Value;PhaseTicks=0;PhaseWall=FPlatformTime::Seconds();
        auto Step=MakeShared<FJsonObject>();Step->SetStringField(TEXT("name"),Name);
        Step->SetNumberField(TEXT("wall_elapsed_s"),PhaseWall-StartedWall);
        if(auto* NativeGame=Game.Get())
        {Step->SetStringField(TEXT("sim_bits"),ProofBits(NativeGame->GetSimulationTime()));ProofId(Step,TEXT("gate"),uint64(NativeGame->GetRunInstallGate()));}
        Steps.Add(MakeShared<FJsonValueObject>(Step));
    }
    TSharedPtr<FJsonObject> SaveBytes(const TCHAR* Filename,const TArray<uint8>& Bytes)
    {
        const FString Path=Directory/Filename;
        if(!Require(!IFileManager::Get().FileExists(*Path)&&FFileHelper::SaveArrayToFile(Bytes,*Path),TEXT("Cannot create exact Codec evidence: ")+Path))return nullptr;
        TArray<uint8> ReadBack;
        if(!Require(FFileHelper::LoadFileToArray(ReadBack,*Path)&&ReadBack==Bytes,TEXT("Codec evidence readback differs")))return nullptr;
        auto Facts=MakeShared<FJsonObject>();Facts->SetStringField(TEXT("path"),Path);
        Facts->SetNumberField(TEXT("bytes"),Bytes.Num());Facts->SetStringField(TEXT("sha256"),ProofStore::FGenerationStore::Sha256(Bytes));return Facts;
    }
    bool CaptureBytes(TArray<uint8>& Bytes,FDungeonRunSnapshot* Snapshot=nullptr)
    {
        auto* NativeGame=Game.Get();FDungeonRunSnapshot Actual;FString Why;
        if(!Require(NativeGame&&NativeGame->CaptureRunSnapshot(Actual,Why),TEXT("Completed-boundary Aggregate Capture failed: ")+Why))return false;
        if(!Require(DungeonRunSnapshotCodec::Encode(Actual,Bytes,Why),TEXT("Full Codec Encode failed: ")+Why))return false;
        if(Snapshot)*Snapshot=MoveTemp(Actual);return true;
    }
    TSharedPtr<FJsonObject> NoRunFacts()
    {
        auto Value=MakeShared<FJsonObject>();auto* NativeGame=Game.Get();auto* NativeController=Controller.Get();FString Why;
        const auto Equipment=NativeGame->CaptureEquipmentSnapshot();const auto Rewards=NativeGame->CaptureRunRewardsSnapshot();
        const auto Fog=NativeGame->CaptureRunExplorationSnapshot();const auto& World=NativeGame->GetWeaponWorldState();const auto& Audio=NativeGame->GetActionAudioState();
        int32 PawnCount=0,FighterCount=0;
        for(TActorIterator<APawn> It(NativeGame->GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++PawnCount;
        for(TActorIterator<ADungeonFighter> It(NativeGame->GetWorld());It;++It)if(!It->IsActorBeingDestroyed())++FighterCount;
        Value->SetBoolField(TEXT("pristine_api"),NativeGame->IsPristineContinueBootstrap(Why));
        Value->SetBoolField(TEXT("controller_local"),NativeController->IsLocalController());
        Value->SetBoolField(TEXT("controller_authoritative"),NativeController->HasAuthority());
        Value->SetBoolField(TEXT("controller_input_present"),NativeController->PlayerInput!=nullptr);
        Value->SetBoolField(TEXT("controller_player_state_present"),NativeController->PlayerState!=nullptr);
        Value->SetBoolField(TEXT("controller_only_spectator"),NativeController->PlayerState&&NativeController->PlayerState->IsOnlyASpectator());
        Value->SetBoolField(TEXT("default_pawn_class_null"),!NativeGame->DefaultPawnClass);
        Value->SetBoolField(TEXT("spectator_class_null"),!NativeGame->SpectatorClass);
        Value->SetBoolField(TEXT("world_begun_play"),NativeGame->GetWorld()->GetBegunPlay());
        Value->SetStringField(TEXT("api_diagnostic"),Why);
        Value->SetBoolField(TEXT("player_null"),!NativeGame->PlayerFighter);Value->SetBoolField(TEXT("controller_pawn_null"),!NativeController->GetPawn());
        Value->SetBoolField(TEXT("inventory_null"),!NativeGame->GetEquipmentInventoryState());Value->SetBoolField(TEXT("equipment_bound"),Equipment.View.Bound);
        Value->SetBoolField(TEXT("run_guid_invalid"),!Equipment.View.RunGuid.IsValid());Value->SetBoolField(TEXT("scene_active"),NativeGame->GetSceneRoomView().Active);
        Value->SetBoolField(TEXT("rewards_bound"),Rewards.Bound);Value->SetBoolField(TEXT("world_run_valid"),World.RunGuid.IsValid());
        Value->SetBoolField(TEXT("audio_run_valid"),Audio.RunGuid.IsValid());
        ProofId(Value,TEXT("native_pawns"),PawnCount);ProofId(Value,TEXT("native_fighters"),FighterCount);
        ProofId(Value,TEXT("restart_serial"),NativeGame->GetRunRestartSerial());ProofId(Value,TEXT("combat_seed"),Equipment.View.CombatSeed);
        ProofId(Value,TEXT("next_crit_draw"),Equipment.View.NextCritDraw);ProofId(Value,TEXT("fog_rooms"),Fog.Rooms.Num());
        ProofId(Value,TEXT("world_bindings"),World.ActorBindings.Num());ProofId(Value,TEXT("audio_records"),Audio.Records.Num());
        ProofId(Value,TEXT("gate"),uint64(NativeGame->GetRunInstallGate()));Value->SetStringField(TEXT("simulation_time_bits"),ProofBits(NativeGame->GetSimulationTime()));
        return Value;
    }
    bool NoRunValid(const TSharedPtr<FJsonObject>& Facts)
    {
        for(const TCHAR* KeyName:{TEXT("pristine_api"),TEXT("player_null"),TEXT("controller_pawn_null"),TEXT("inventory_null"),TEXT("run_guid_invalid")})
            if(!Facts->GetBoolField(KeyName))return false;
        for(const TCHAR* KeyName:{TEXT("controller_local"),TEXT("controller_authoritative"),TEXT("controller_input_present"),TEXT("controller_player_state_present"),TEXT("default_pawn_class_null"),TEXT("spectator_class_null"),TEXT("world_begun_play")})
            if(!Facts->GetBoolField(KeyName))return false;
        if(Facts->GetBoolField(TEXT("controller_only_spectator")))return false;
        for(const TCHAR* KeyName:{TEXT("equipment_bound"),TEXT("scene_active"),TEXT("rewards_bound"),TEXT("world_run_valid"),TEXT("audio_run_valid")})
            if(Facts->GetBoolField(KeyName))return false;
        for(const TCHAR* KeyName:{TEXT("native_pawns"),TEXT("native_fighters"),TEXT("restart_serial"),TEXT("combat_seed"),TEXT("next_crit_draw"),TEXT("fog_rooms"),TEXT("world_bindings"),TEXT("audio_records")})
            if(Facts->GetStringField(KeyName)!=TEXT("0"))return false;
        return Facts->GetStringField(TEXT("gate"))==TEXT("3")&&Facts->GetStringField(TEXT("simulation_time_bits"))==TEXT("0000000000000000");
    }
    void RecordStoreFiles()
    {
        TArray<FString> Files;IFileManager::Get().FindFilesRecursive(Files,*ProfileDirectory,TEXT("*"),true,false);
        Files.Sort();TArray<TSharedPtr<FJsonValue>> Values;
        for(const FString& File:Files)
        {
            TArray<uint8> Bytes;if(!FFileHelper::LoadFileToArray(Bytes,*File))continue;
            auto Value=MakeShared<FJsonObject>();Value->SetStringField(TEXT("path"),File);Value->SetNumberField(TEXT("bytes"),Bytes.Num());
            Value->SetStringField(TEXT("sha256"),ProofStore::FGenerationStore::Sha256(Bytes));Values.Add(MakeShared<FJsonValueObject>(Value));
        }
        Report->SetArrayField(TEXT("actual_store_files"),Values);
    }
    bool OpenAndSaveSource()
    {
        if(!CaptureBytes(SavedCodec,&Saved))return false;
        auto CodecFact=SaveBytes(TEXT("source-codec.json"),SavedCodec);if(!CodecFact)return false;Report->SetObjectField(TEXT("codec"),CodecFact);
        ProofStore::FGenerationStore Disk(ProfilesDirectory,ProfileId,ProofAdapter::CurrentVersions);
        const auto Lease=Disk.OpenWriter();ProofId(Report,TEXT("writer_status"),uint64(Lease));
        if(!Require(Lease==ProofStore::EStatus::Ok,TEXT("Source cannot acquire actual writer lease")))return false;
        ProofAdapter::FWriteRequest Request;Request.Context.ProfilesDirectory=ProfilesDirectory;Request.Context.ProfileId=ProfileId;
        Request.Context.ExpectedRunGuid=Saved.RunGuid;Request.Context.ExpectedOwnerId=Saved.OwnerId;
        Request.RunGuid=Saved.RunGuid;Request.OwnerId=Saved.OwnerId;Request.GenerationId=1;Request.ParentGeneration=0;Request.BuildId=BuildId;
        const auto Result=ProofAdapter::Commit(Disk,Saved,Request);Disk.CloseWriter();
        auto Commit=MakeShared<FJsonObject>();ProofId(Commit,TEXT("status"),uint64(Result.Status));ProofId(Commit,TEXT("generation_id"),Result.GenerationId);
        Commit->SetBoolField(TEXT("replayed"),Result.Replayed);Commit->SetBoolField(TEXT("publication_may_have_succeeded"),Result.PublicationMayHaveSucceeded);
        Commit->SetStringField(TEXT("diagnostic"),Result.Diagnostic);Commit->SetStringField(TEXT("bundle_sha256"),Result.BundleSha256);
        ProofId(Commit,TEXT("bundle_crc32"),Result.BundleCrc32);Commit->SetNumberField(TEXT("bundle_byte_length"),double(Result.BundleByteLength));Report->SetObjectField(TEXT("commit"),Commit);
        if(!Require(Result.Status==ProofStore::EStatus::Ok&&!Result.Replayed&&Result.GenerationId==1,TEXT("Actual gen1parent0 Commit failed: ")+Result.Diagnostic))return false;
        ProofAdapter::FLoadedRun ReadBack;const auto Read=ProofAdapter::Load(Disk,Request.Context,ReadBack);FString Why;TArray<uint8> ReadCodec;
        if(!Require(Read.Status==ProofStore::EStatus::Ok&&ReadBack.Run.IsValid()&&Read.ObservedHeadGeneration==1
            &&DungeonRunSnapshotCodec::Encode(*ReadBack.Run.Get(),ReadCodec,Why)&&ReadCodec==SavedCodec,TEXT("Actual source disk Load/full Codec readback differs: ")+Read.Diagnostic+Why))return false;
        ProofId(Report,TEXT("store_generation_id"),ReadBack.Generation.GenerationId);ProofId(Report,TEXT("store_observed_head"),Read.ObservedHeadGeneration);
        Report->SetStringField(TEXT("save_readback_codec_sha256"),ProofStore::FGenerationStore::Sha256(ReadCodec));
        auto ReloadFact=MakeShared<FJsonObject>();ProofId(ReloadFact,TEXT("action_id"),Reload.ActionId);ProofId(ReloadFact,TEXT("instance_id"),Reload.InstanceId);
        ReloadFact->SetStringField(TEXT("start_bits"),ProofBits(Reload.Start));ReloadFact->SetStringField(TEXT("end_bits"),ProofBits(Reload.End));
        ReloadFact->SetStringField(TEXT("capture_time_bits"),ProofBits(Saved.SimulationTime));Report->SetObjectField(TEXT("reload"),ReloadFact);
        Report->SetObjectField(TEXT("audio_counts"),ProofCounts(*HUD.Get()));RecordStoreFiles();return true;
    }
    bool LoadAndInstall()
    {
        auto* NativeGame=Game.Get();ProofStore::FGenerationStore Disk(ProfilesDirectory,ProfileId,ProofAdapter::CurrentVersions);
        ProofAdapter::FReadContext Context;Context.ProfilesDirectory=ProfilesDirectory;Context.ProfileId=ProfileId;
        const auto Result=ProofAdapter::Load(Disk,Context,Loaded);
        ProofId(Report,TEXT("load_status"),uint64(Result.Status));ProofId(Report,TEXT("store_observed_head"),Result.ObservedHeadGeneration);
        if(!Require(Result.Status==ProofStore::EStatus::Ok&&Loaded.Run.IsValid()&&Result.ObservedHeadGeneration==1
            &&Loaded.Generation.GenerationId==1&&Loaded.Generation.ParentGeneration==0,TEXT("Pristine actual highest-head Load failed: ")+Result.Diagnostic))return false;
        ProofId(Report,TEXT("store_generation_id"),Loaded.Generation.GenerationId);Saved=*Loaded.Run.Get();FString Why;
        if(!Require(!Saved.Fighters.IsEmpty()&&Saved.Fighters[0].Player.IsSet(),TEXT("Loaded complete player absent")))return false;
        Reload=Saved.Fighters[0].Player.GetValue().WeaponActions.Action;
        if(!Require(Reload.Active&&Reload.Type==ProofWA::EAction::Reload,TEXT("Loaded accepted original reload absent")))return false;
        if(!Require(FDungeonRunInstaller::PreparePristine(*NativeGame,Loaded.Run,Prepared,Why)&&Prepared.IsReady(),TEXT("PreparePristine failed: ")+Why))return false;
        bool AllHidden=!Prepared.GetStagedActors().IsEmpty();
        for(const auto& Staged:Prepared.GetStagedActors())AllHidden=AllHidden&&Staged.IsValid()&&Staged->IsHidden()&&!Staged->GetActorEnableCollision()&&!Staged->IsActorTickEnabled();
        Report->SetBoolField(TEXT("all_staged_hidden_tick_collision_off"),AllHidden);ProofId(Report,TEXT("staged_actor_count"),Prepared.GetStagedActors().Num());
        if(!Require(AllHidden&&!NativeGame->PlayerFighter&&!NativeGame->GetEquipmentView().Bound&&!Controller->GetPawn()
            &&NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::Preparing,TEXT("Staging published a Run or native resources were live")))return false;
        if(!Require(FDungeonRunInstaller::Install(*NativeGame,Prepared,Why)&&!Prepared.IsReady(),TEXT("Pristine full Install failed: ")+Why))return false;
        Report->SetBoolField(TEXT("controller_possesses_restored_player"),Controller->GetPawn()==NativeGame->PlayerFighter);
        ProofId(Report,TEXT("installed_gate"),uint64(NativeGame->GetRunInstallGate()));
        if(!Require(NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue&&NativeGame->GetRunRestartSerial()==0
            &&Controller->GetPawn()==NativeGame->PlayerFighter,TEXT("Install did not stay paused/or restarted a Run")))return false;
        if(!CaptureBytes(SavedCodec))return false;TArray<uint8> LoadedCodec;
        if(!Require(DungeonRunSnapshotCodec::Encode(Saved,LoadedCodec,Why)&&SavedCodec==LoadedCodec,TEXT("Installed full native owner Codec differs from loaded whole Run")))return false;
        auto Fact=SaveBytes(TEXT("restored-codec.json"),SavedCodec);if(!Fact)return false;Report->SetObjectField(TEXT("installed_codec"),Fact);
        InstalledWall=FPlatformTime::Seconds();RecordStoreFiles();return true;
    }
    bool CompleteValid()
    {
        auto* NativeGame=Game.Get();auto* Player=NativeGame->PlayerFighter.Get();auto* Inventory=NativeGame->GetEquipmentInventoryState();
        if(!Player||!Inventory)return false;const auto& Weapons=Player->GetWeaponActionsState();
        if(Weapons.Action.Active||Weapons.Action.ActionId!=Reload.ActionId||Weapons.Action.InstanceId!=Reload.InstanceId
            ||Weapons.Action.Terminal!=ProofWA::EEvent::ReloadCompleted||Inventory->RuntimeUpdates.size()!=Saved.Equipment.InventoryState.RuntimeUpdates.size()+1)return false;
        const auto& Update=Inventory->RuntimeUpdates.back();
        const auto& Audio=NativeGame->GetActionAudioState();
        if(Audio.Records.Num()!=1||Audio.NextSequence!=Saved.Audio.NextActionSequence+1)return false;
        const auto& Completion=Audio.Records[0];
        if(Completion.Cue!=TEXT("XBW_RELOAD_COMPLETE_01")||Completion.Sequence!=Saved.Audio.NextActionSequence
            ||Completion.AtTime!=Reload.End||Completion.ActionId!=Reload.ActionId||Completion.InstanceId!=Reload.InstanceId
            ||Completion.RunGuid!=Saved.RunGuid||Completion.RoomInstanceId!=Saved.RoomInstanceId||Completion.OwnerId!=Saved.OwnerId)return false;
        return Update.InstanceId==Reload.InstanceId&&Update.AtTime==Reload.End&&Update.BeforeAmmo==0.&&Update.Ammo==1.
            &&NativeGame->GetEquipmentView().RunGuid==Saved.RunGuid&&NativeGame->GetEquipmentView().NextCritDraw==Saved.Equipment.View.NextCritDraw
            &&NativeGame->GetRunRestartSerial()==0&&ProofAudioCounts(*HUD.Get(),0,0,1);
    }
    void RecordFinalAudio()
    {
        TArray<TSharedPtr<FJsonValue>> Records;
        for(const auto& Audio:Game->GetActionAudioState().Records)
        {
            auto Value=MakeShared<FJsonObject>();ProofId(Value,TEXT("sequence"),Audio.Sequence);Value->SetStringField(TEXT("cue"),Audio.Cue);
            Value->SetStringField(TEXT("at_time_bits"),ProofBits(Audio.AtTime));ProofId(Value,TEXT("action_id"),Audio.ActionId);
            ProofId(Value,TEXT("instance_id"),Audio.InstanceId);ProofId(Value,TEXT("owner_id"),Audio.OwnerId);Records.Add(MakeShared<FJsonValueObject>(Value));
        }
        Report->SetArrayField(TEXT("final_audio_records"),Records);
    }
    void Tick(ADungeonRunContinueProbe& Owner)
    {
        if(Stopped)return;const double Wall=FPlatformTime::Seconds();++PhaseTicks;
        if(Wall-StartedWall>45.){Finish(TEXT("Native proof45s timeout at phase ")+LexToString(Phase));return;}
        auto* NativeGame=Owner.GetWorld()->GetAuthGameMode<ADungeonGameMode>();auto* NativeController=UGameplayStatics::GetPlayerController(&Owner,0);
        auto* NativeHUD=NativeController?Cast<ADungeonHUD>(NativeController->GetHUD()):nullptr;
        if(!NativeGame||!NativeController||!NativeController->PlayerInput||!NativeHUD)return;
        if(!Game.IsValid())
        {
            Game=NativeGame;Controller=NativeController;HUD=NativeHUD;Owner.AddTickPrerequisiteActor(NativeGame);Owner.AddTickPrerequisiteActor(NativeHUD);
            // Wait for the prerequisite graph on the next actual frame, never run GM manually.
            return;
        }
        if(!Require(Game.Get()==NativeGame&&Controller.Get()==NativeController&&HUD.Get()==NativeHUD,TEXT("Actual world/controller/HUD changed during proof")))return;
        if(!Restore)
        {
            switch(Phase)
            {
            case 0:
                if(!Require(NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::Open&&NativeGame->PlayerFighter
                    &&NativeController->GetPawn()==NativeGame->PlayerFighter&&NativeGame->GetSceneRoomView().Active&&NativeGame->bWaitingForStart,
                    TEXT("Source ordinary Scene native startup premise failed")))return;
                Key(EKeys::Enter,true);Next(1,TEXT("source_real_Enter_down"));return;
            case 1:
                if(Wall-PhaseWall<.07)return;Key(EKeys::Enter,false);Next(2,TEXT("source_real_Enter_up"));return;
            case 2:
            {
                if(NativeGame->bWaitingForStart)return;
                auto* Player=NativeGame->PlayerFighter.Get();if(!Require(Player&&NativeGame->GetEquipmentView().Bound,TEXT("Enter did not admit real bound source")))return;
                DungeonEquipmentInventory::FItem Empty;Empty.ContentId="WPN-XBW-001";Empty.Ammo=0.;
                const auto Receipt=NativeGame->RegisterEquipmentSource(TEXT("two-process.proof.real.empty-xbw"),Empty,Player->GetGroundPosition()+FVector2D(30.,0.),true);
                if(!Require(Receipt.Ok()&&!Receipt.Replayed,TEXT("Actual emptyXBW Register failed")))return;
                RegisteredSourceId=Receipt.SourceId;RegisteredInstanceId=Receipt.InstanceId;
                ProofId(Report,TEXT("registered_source_id"),Receipt.SourceId);ProofId(Report,TEXT("registered_instance_id"),Receipt.InstanceId);
                Key(EKeys::E,true);Next(3,TEXT("source_real_E_down"));return;
            }
            case 3:
                if(!EquipmentAccepted&&NativeGame->GetEquipmentView().Action.Active)
                {
                    EquipmentAction=NativeGame->GetEquipmentView().Action;EquipmentAccepted=true;
                    if(!Require(EquipmentAction.SourceId==RegisteredSourceId&&EquipmentAction.InstanceId==RegisteredInstanceId
                        &&EquipmentAction.OperationId>0&&EquipmentAction.Deadline>EquipmentAction.Start,TEXT("Real E accepted a different source or invalid deadline")))return;
                    auto Facts=MakeShared<FJsonObject>();ProofId(Facts,TEXT("action_id"),EquipmentAction.ActionId);
                    ProofId(Facts,TEXT("operation_id"),EquipmentAction.OperationId);ProofId(Facts,TEXT("source_id"),EquipmentAction.SourceId);
                    ProofId(Facts,TEXT("instance_id"),EquipmentAction.InstanceId);Facts->SetStringField(TEXT("start_bits"),ProofBits(EquipmentAction.Start));
                    Facts->SetStringField(TEXT("deadline_bits"),ProofBits(EquipmentAction.Deadline));Report->SetObjectField(TEXT("equipment_action"),Facts);
                }
                if(Wall-PhaseWall<.07)return;Key(EKeys::E,false);Next(4,TEXT("source_real_E_up_wait_equipment_deadline"));return;
            case 4:
                if(NativeGame->GetEquipmentView().Action.Active)return;
                if(!Require(EquipmentAccepted&&NativeGame->GetSimulationTime()>=EquipmentAction.Deadline
                    &&NativeGame->PlayerFighter->WeaponId==TEXT("WPN-XBW-001"),TEXT("Normal original equipment deadline did not acquire XBW")))return;
                Report->SetStringField(TEXT("equipment_completion_observed_sim_bits"),ProofBits(NativeGame->GetSimulationTime()));
                Key(EKeys::T,true);Next(5,TEXT("source_real_T_down"));return;
            case 5:
                if(Wall-PhaseWall<.07)return;Key(EKeys::T,false);Next(6,TEXT("source_real_T_up"));return;
            case 6:
            {
                Reload=NativeGame->PlayerFighter->GetWeaponActionsState().Action;
                if(!Require(Reload.Active&&Reload.Type==ProofWA::EAction::Reload,TEXT("Real T did not start accepted reload")))return;
                auto* Muzzle=NativeGame->PlayerFighter->GetWeaponMuzzleComponent();
                if(!Require(Muzzle!=nullptr,TEXT("Source native muzzle absent")))return;
                Muzzle->SetRelativeLocation(FVector(24.,7.,65.));Next(7,TEXT("source_actual_native_muzzle24_7_65"));return;
            }
            case 7:
                if(NativeGame->GetSimulationTime()<Reload.Start+.65)return;
                if(!Require(NativeGame->GetSimulationTime()<Reload.End&&NativeGame->PlayerFighter->GetWeaponActionsState().Action.Active,
                    TEXT("Native completed source boundary missed pre-complete window")))return;
                if(!ProofAudioCounts(*NativeHUD,1,1,0))return;
                if(OpenAndSaveSource())Finish();return;
            default:Finish(TEXT("Unknown source phase"));return;
            }
        }
        switch(Phase)
        {
        case 0:
        {
            auto Facts=NoRunFacts();Report->SetObjectField(TEXT("initial_pristine"),Facts);
            if(!Require(NoRunValid(Facts),TEXT("Actual pristine InitGame-origin completed boundary is not empty/closed")))return;
            Key(EKeys::R,true);Next(1,TEXT("restore_real_R_down_behind_pristine_gate"));return;
        }
        case 1:
            if(Wall-PhaseWall<.07)return;Key(EKeys::R,false);Next(2,TEXT("restore_real_R_up"));return;
        case 2:
        {
            if(PhaseTicks<3)return;auto Facts=NoRunFacts();Report->SetObjectField(TEXT("after_real_R"),Facts);
            if(!Require(NoRunValid(Facts),TEXT("Real R opened/mutated pristine no-Run origin")))return;
            if(LoadAndInstall())Next(3,TEXT("restore_actual_Load_PreparePristine_Install"));return;
        }
        case 3:
        {
            if(Wall-InstalledWall<.2)return;TArray<uint8> Paused;
            if(!CaptureBytes(Paused)||!Require(Paused==SavedCodec&&NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue,
                TEXT("Paused whole Codec/clock mutated")))return;
            auto Fact=SaveBytes(TEXT("restored-paused-codec.json"),Paused);if(!Fact)return;Report->SetObjectField(TEXT("paused_codec"),Fact);
            Report->SetNumberField(TEXT("paused_wall_seconds"),Wall-InstalledWall);Report->SetObjectField(TEXT("paused_audio_counts"),ProofCounts(*NativeHUD));
            if(!Require(ProofAudioCounts(*NativeHUD,0,0,0)&&NativeGame->GetActionAudioState().Records.IsEmpty(),TEXT("Installed pause replayed historical sounds")))return;
            const bool Neutral=!NativeController->IsInputKeyDown(EKeys::Enter)&&!NativeController->IsInputKeyDown(EKeys::R)
                &&!NativeController->IsInputKeyDown(EKeys::J)&&!NativeController->IsInputKeyDown(EKeys::E)&&!NativeController->IsInputKeyDown(EKeys::T);
            Report->SetBoolField(TEXT("neutral_before_fresh_enter"),Neutral);
            if(!Require(Neutral,TEXT("Proof input not neutral before fresh Continue")))return;
            Key(EKeys::Enter,true);Next(4,TEXT("restore_real_fresh_Enter_down"));return;
        }
        case 4:
            if(Wall-PhaseWall<.07)return;Key(EKeys::Enter,false);Next(5,TEXT("restore_real_Enter_up_wait_original_reload_deadline"));return;
        case 5:
            if(NativeGame->GetSimulationTime()<Reload.End+.1)return;
            if(!Require(CompleteValid(),TEXT("Original reload deadline/identity/unique inventory refill or future-only completion failed")))return;
            Report->SetObjectField(TEXT("final_audio_counts"),ProofCounts(*NativeHUD));RecordFinalAudio();CompletionWall=Wall;
            Next(6,TEXT("restore_original_reload_completed_once"));return;
        case 6:
        {
            if(Wall-CompletionWall<.2||NativeGame->GetSimulationTime()<Reload.End+.3)return;
            if(!Require(CompleteValid(),TEXT("Late native ticks duplicated/lost original refill/audio")))return;
            TArray<uint8> Continued;if(!CaptureBytes(Continued))return;auto Fact=SaveBytes(TEXT("continued-codec.json"),Continued);if(!Fact)return;
            Report->SetObjectField(TEXT("continued_codec"),Fact);Report->SetObjectField(TEXT("late_audio_counts"),ProofCounts(*NativeHUD));
            Report->SetNumberField(TEXT("late_wait_seconds"),Wall-CompletionWall);
            ProofId(Report,TEXT("late_inventory_runtime_updates"),NativeGame->GetEquipmentInventoryState()->RuntimeUpdates.size());
            ProofId(Report,TEXT("restart_serial"),NativeGame->GetRunRestartSerial());ProofId(Report,TEXT("final_gate"),uint64(NativeGame->GetRunInstallGate()));
            Finish();return;
        }
        default:Finish(TEXT("Unknown restore phase"));return;
        }
    }
};

void FDungeonRunContinueProofDeleter::operator()(FDungeonRunContinueProofState* State) const {delete State;}
ADungeonRunContinueProbe::ADungeonRunContinueProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonRunContinueProbe::~ADungeonRunContinueProbe()=default;
void ADungeonRunContinueProbe::BeginPlay()
{
    Super::BeginPlay();Proof.Reset(new FDungeonRunContinueProofState());Proof->StartedWall=FPlatformTime::Seconds();
    const bool Save=FParse::Param(FCommandLine::Get(),TEXT("DungeonRunSaveProof"));
    const bool Restore=FParse::Param(FCommandLine::Get(),TEXT("DungeonRunRestoreProof"));Proof->Restore=Restore;Proof->Role=Restore?TEXT("restore"):TEXT("source");
    FString ProfileText;
    FParse::Value(FCommandLine::Get(),TEXT("DungeonRunProofDir="),Proof->Directory);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonRunProofProfiles="),Proof->ProfilesDirectory);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonRunProofProfile="),ProfileText);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonRunProofBuildId="),Proof->BuildId);
    const bool HasAbsolutePaths=!Proof->Directory.IsEmpty()&&!Proof->ProfilesDirectory.IsEmpty()
        &&!FPaths::IsRelative(Proof->Directory)&&!FPaths::IsRelative(Proof->ProfilesDirectory);
    if(HasAbsolutePaths)
    {Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);Proof->ProfilesDirectory=FPaths::ConvertRelativePathToFull(Proof->ProfilesDirectory);}
    else Proof->Directory.Reset(); // Never turn a missing proof path into cwd output.
    Proof->Report->SetStringField(TEXT("schema"),TEXT("run-pristine-two-process-role-v1"));Proof->Report->SetStringField(TEXT("role"),Proof->Role);
    ProofId(Proof->Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Proof->Report->SetStringField(TEXT("build_id"),Proof->BuildId);
    if(!Proof->Require(HasAbsolutePaths&&Save!=Restore&&!ProfileText.IsEmpty()&&FGuid::Parse(ProfileText,Proof->ProfileId)&&Proof->ProfileId.IsValid()
        &&!Proof->Directory.IsEmpty()&&FPaths::GetCleanFilename(Proof->ProfilesDirectory)==TEXT("BoundRunOnly-v1")&&!Proof->BuildId.IsEmpty(),TEXT("Missing/mutually conflicting proof parameters")))return;
    Proof->ProfileDirectory=Proof->ProfilesDirectory/Proof->ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower);
    Proof->Report->SetStringField(TEXT("profile_id"),Proof->ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower));
    Proof->Report->SetStringField(TEXT("profiles_directory"),Proof->ProfilesDirectory);Proof->Report->SetStringField(TEXT("profile_directory"),Proof->ProfileDirectory);
    const FString ReportPath=Proof->Directory/(Restore?TEXT("restore-report.json"):TEXT("source-report.json"));
    if(IFileManager::Get().FileExists(*ReportPath)){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}
    IFileManager::Get().MakeDirectory(*Proof->Directory,true);
    if(!Proof->Require(Restore?IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory):!IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory),
        TEXT("Source requires unused profile; Restore requires actual committed profile")))return;
    if(auto* NativeGame=GetWorld()->GetAuthGameMode<ADungeonGameMode>())AddTickPrerequisiteActor(NativeGame);
}
void ADungeonRunContinueProbe::Tick(float DeltaSeconds)
{Super::Tick(DeltaSeconds);if(Proof)Proof->Tick(*this);}
void ADungeonRunContinueProbe::EndPlay(const EEndPlayReason::Type Reason)
{if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("World ended before native proof finished"));Super::EndPlay(Reason);}
