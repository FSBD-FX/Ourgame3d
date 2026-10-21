#include "DungeonGuardRunContinueProbe.h"
#include "DungeonGameMode.h"
#include "DungeonHUD.h"
#include "DungeonFighter.h"
#include "DungeonRunSaveAdapterV2.h"
#include "DungeonStoneGuardDriver.h"
#include "DungeonProofScreenshots.h"
#include "Engine/Engine.h"
#include "UnrealClient.h"
#include "Misc/App.h"
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
namespace ProofStore=DungeonSaveGenerationStore;
namespace ProofAdapter=DungeonRunSaveAdapterV2;
namespace Guard=DungeonStoneGuard;
FString ProofBits(double Value)
{uint64 Bits=0;FMemory::Memcpy(&Bits,&Value,sizeof(Bits));return FString::Printf(TEXT("%016llx"),(unsigned long long)Bits);}
void ProofId(const TSharedPtr<FJsonObject>& Object,const TCHAR* Key,uint64 Value)
{Object->SetStringField(Key,LexToString(Value));}

}

struct FDungeonGuardRunContinueProofState
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
    TWeakObjectPtr<ADungeonFighter> LiveGuard,DeadGuard;
    uint64 LiveId=0,DeadId=0,FirstAttack=0;
    Guard::FState SavedLive,SavedDead;
    int32 SavedCoins=0,SavedPickups=0;
    bool Prewarm=false,Capturing=false,FinishOnFrame=false;
    double CaptureStart=0.,CaptureStop=0.;
    TArray<TSharedPtr<FJsonValue>> Observations,Offsets;
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
        if(Stopped)return;Stopped=true;CaptureStop=FPlatformTime::Seconds();GIsDumpingMovie=0;
        const bool Flushed=FlushFastLosslessProofScreenshots();
        TArray<FKey> Released;Keys.GetKeys(Released);for(const FKey& Code:Released)Key(Code,false);
        Report->SetBoolField(TEXT("passed"),Failure.IsEmpty()&&Flushed&&!Observations.IsEmpty());
        Report->SetBoolField(TEXT("silent_video"),true);Report->SetBoolField(TEXT("audio_recorded"),false);
        Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);
        Report->SetArrayField(TEXT("observations"),Observations);
        Report->SetNumberField(TEXT("duration_s"),Capturing?CaptureStop-CaptureStart:0.);
        auto Timing=MakeShared<FJsonObject>();Timing->SetNumberField(TEXT("capture_start_monotonic_s"),CaptureStart);Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),CaptureStop);
        Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());Timing->SetArrayField(TEXT("frame_wall_offsets_s"),Offsets);Report->SetObjectField(TEXT("capture_timing"),Timing);Report->SetStringField(TEXT("failure"),Failure);
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
            Report->SetObjectField(TEXT("last_completed_boundary_diagnostic"),Boundary);
        }
        // Release failed staging while its real native world/GameMode is still alive.
        if(Prepared.IsReady())Prepared=FDungeonPreparedRun();
        FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Report.ToSharedRef(),Writer);
        const FString Path=Directory/TEXT("runtime-report.json");
        const bool Written=!Directory.IsEmpty()&&FFileHelper::SaveStringToFile(Text,*Path,FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
        if(!Failure.IsEmpty()||!Written)
        {UE_LOG(LogTemp,Error,TEXT("Guard DiskV2 two-process proof failed: %s reportWritten=%d"),*Failure,Written);}
        else
        {UE_LOG(LogTemp,Display,TEXT("Guard DiskV2 two-process %s proof complete: %s"),*Role,*Path);}
        FPlatformMisc::RequestExitWithStatus(false,Failure.IsEmpty()&&Written&&Flushed&&!Observations.IsEmpty()?0:3);
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
        RecordStoreFiles();return true;
    }

    bool LoadAndInstall()
    {
        auto* NativeGame=Game.Get();ProofStore::FGenerationStore Disk(ProfilesDirectory,ProfileId,ProofAdapter::CurrentVersions);
        ProofAdapter::FReadContext Context;Context.ProfilesDirectory=ProfilesDirectory;Context.ProfileId=ProfileId;
        const auto Result=ProofAdapter::LoadAndPreparePristine(*NativeGame,Disk,Context,Prepared,Loaded);
        ProofId(Report,TEXT("load_status"),uint64(Result.Status));ProofId(Report,TEXT("store_observed_head"),Result.ObservedHeadGeneration);
        if(!Require(Result.Status==ProofStore::EStatus::Ok&&Loaded.Run.IsValid()&&Prepared.IsReady()&&Result.ObservedHeadGeneration==1
            &&Loaded.Generation.GenerationId==1&&Loaded.Generation.ParentGeneration==0,TEXT("Pristine actual highest-head LoadAndPreparePristine failed: ")+Result.Diagnostic))return false;
        ProofId(Report,TEXT("store_generation_id"),Loaded.Generation.GenerationId);Saved=*Loaded.Run.Get();FString Why;
        for(const auto& F:Saved.Fighters)if(F.Guard.IsSet())
        {
            const auto& K=F.Guard.GetValue().Kernel;
            if(K.HP>0){LiveId=F.EntityId;SavedLive=K;}else{DeadId=F.EntityId;SavedDead=K;}
        }
        ProofId(Report,TEXT("live_guard_id"),LiveId);ProofId(Report,TEXT("dead_guard_id"),DeadId);
        if(!Require(Saved.Schema==2&&LiveId&&DeadId&&LiveId!=DeadId&&SavedLive.Action.InProgress
            &&SavedLive.Action.WindowIssued&&SavedLive.Phase==Guard::EPhase::Active
            &&Saved.SimulationTime>=SavedLive.Action.ActiveAt&&Saved.SimulationTime<SavedLive.Action.ActiveEnd
            &&SavedDead.RewardClaimed,TEXT("Loaded actual two-Guard live-active/dead-localclaim premise absent")))return false;
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
        for(auto Enemy:NativeGame->Enemies)if(Enemy)
        {if(Enemy->GetRuntimeEntityId()==LiveId)LiveGuard=Enemy;if(Enemy->GetRuntimeEntityId()==DeadId)DeadGuard=Enemy;}
        if(!Require(LiveGuard.IsValid()&&DeadGuard.IsValid()&&LiveGuard->GetStoneGuardDriver()&&DeadGuard->GetStoneGuardDriver(),TEXT("Installed actual Guard actors not found by stable IDs")))return false;
        SavedCoins=NativeGame->PlayerFighter->Coins;SavedPickups=NativeGame->Pickups.Num();
        InstalledWall=FPlatformTime::Seconds();RecordStoreFiles();return true;
    }
    TSharedPtr<FJsonObject> GuardFacts(ADungeonFighter* Fighter)
    {
        auto O=MakeShared<FJsonObject>();if(!Fighter||!Fighter->GetStoneGuardDriver())return O;
        const auto& K=Fighter->GetStoneGuardDriver()->State();const auto& A=K.Action;
        ProofId(O,TEXT("entity_id"),K.EntityId);ProofId(O,TEXT("phase"),uint64(K.Phase));
        O->SetStringField(TEXT("time_bits"),ProofBits(K.Time));O->SetStringField(TEXT("hp_bits"),ProofBits(K.HP));
        ProofId(O,TEXT("attack_id"),A.AttackId);O->SetBoolField(TEXT("in_progress"),A.InProgress);
        O->SetStringField(TEXT("active_at_bits"),ProofBits(A.ActiveAt));O->SetStringField(TEXT("active_end_bits"),ProofBits(A.ActiveEnd));
        O->SetStringField(TEXT("recovery_end_bits"),ProofBits(A.RecoveryEnd));
        ProofId(O,TEXT("next_event_id"),K.NextEventId);ProofId(O,TEXT("last_damage_receipt_id"),K.LastDamageReceiptId);
        ProofId(O,TEXT("windows"),K.Windows.size());ProofId(O,TEXT("closures"),K.Closures.size());ProofId(O,TEXT("hits"),K.HitReceipts.size());ProofId(O,TEXT("received"),K.ReceivedHits.size());ProofId(O,TEXT("issued"),K.Issued.size());
        O->SetBoolField(TEXT("dead"),Fighter->bDead);O->SetBoolField(TEXT("death_observed"),Fighter->IsStoneGuardDeathObserved());O->SetBoolField(TEXT("local_reward_claimed"),K.RewardClaimed);O->SetBoolField(TEXT("formal_death_reported"),Fighter->bDeathReported);
        const auto P=Fighter->GetGroundPosition();O->SetStringField(TEXT("actor_x_bits"),ProofBits(P.X));O->SetStringField(TEXT("actor_y_bits"),ProofBits(P.Y));
        O->SetStringField(TEXT("kernel_x_bits"),ProofBits(K.Position.X));O->SetStringField(TEXT("kernel_y_bits"),ProofBits(K.Position.Y));
        return O;
    }
    void CaptureProcessed()
    {
        if(Stopped)return;
        if(Prewarm&&!Capturing)
        {
            if(!Require(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))>8,TEXT("Synchronous native prewarm was not saved")))return;
            CaptureStart=FPlatformTime::Seconds();Capturing=true;GIsDumpingMovie=-1;return;
        }
        if(!Capturing)return;
        const double Wall=FPlatformTime::Seconds();auto O=MakeShared<FJsonObject>();
        O->SetNumberField(TEXT("index"),Observations.Num());O->SetNumberField(TEXT("wall_offset_s"),Wall-CaptureStart);
        ProofId(O,TEXT("phase"),Phase);ProofId(O,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());
        if(auto* G=Game.Get()){O->SetStringField(TEXT("simulation_time_bits"),ProofBits(G->GetSimulationTime()));ProofId(O,TEXT("gate"),uint64(G->GetRunInstallGate()));}
        O->SetObjectField(TEXT("live_guard"),GuardFacts(LiveGuard.Get()));O->SetObjectField(TEXT("dead_guard"),GuardFacts(DeadGuard.Get()));
        Observations.Add(MakeShared<FJsonValueObject>(O));Offsets.Add(MakeShared<FJsonValueNumber>(Wall-CaptureStart));
        // Finish in the processed native viewport frame of the saved/final boundary,
        // before a later GameMode tick. No synthetic frame or manual clock step.
        if(FinishOnFrame)Finish();
    }
    bool DeadUnchanged()
    {
        if(!DeadGuard.IsValid()||!DeadGuard->GetStoneGuardDriver())return false;const auto& D=DeadGuard->GetStoneGuardDriver()->State();
        return DeadGuard->bDead&&DeadGuard->IsStoneGuardDeathObserved()&&!DeadGuard->bDeathReported&&D.RewardClaimed
            &&D.NextEventId==SavedDead.NextEventId&&D.LastDamageReceiptId==SavedDead.LastDamageReceiptId
            &&D.Issued.size()==SavedDead.Issued.size()&&D.ReceivedHits.size()==SavedDead.ReceivedHits.size()
            &&Game->PlayerFighter->Coins==SavedCoins&&Game->Pickups.Num()==SavedPickups;
    }

    void Tick(ADungeonGuardRunContinueProbe& Owner)
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
        if(!Capturing)
        {
            if(!Prewarm&&Wall-StartedWall>=2.){Prewarm=true;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
            return;
        }
        if(FinishOnFrame)return;
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
                if(NativeGame->bWaitingForStart)return;auto* P=NativeGame->PlayerFighter.Get();
                if(!Require(P&&NativeGame->GetEquipmentView().Bound,TEXT("Normal Enter did not bind source Run")))return;
                const auto Pos=P->GetGroundPosition();
                LiveGuard=NativeGame->SpawnStoneGuard(Pos-FVector2D(150.,0.));
                DeadGuard=NativeGame->SpawnStoneGuard(Pos+FVector2D(300.,-200.));
                if(!Require(LiveGuard.IsValid()&&DeadGuard.IsValid()&&LiveGuard->GetStoneGuardDriver()&&DeadGuard->GetStoneGuardDriver(),TEXT("Public SpawnStoneGuard failed in actual screen Run")))return;
                LiveId=LiveGuard->GetRuntimeEntityId();DeadId=DeadGuard->GetRuntimeEntityId();
                ProofId(Report,TEXT("live_guard_id"),LiveId);ProofId(Report,TEXT("dead_guard_id"),DeadId);
                DeadGuard->ApplyCombatHit(100000.f,P,85.f);
                if(!Require(DeadGuard->bDead&&DeadGuard->IsStoneGuardDeathObserved()&&!DeadGuard->bDeathReported
                    &&DeadGuard->ClaimStoneGuardDeathEligibility()&&!DeadGuard->ClaimStoneGuardDeathEligibility(),TEXT("Actual lethal death/localeligibility/independent native observer premise failed")))return;
                SavedDead=DeadGuard->GetStoneGuardDriver()->Capture();SavedCoins=P->Coins;SavedPickups=NativeGame->Pickups.Num();
                Report->SetObjectField(TEXT("initial_dead_guard"),GuardFacts(DeadGuard.Get()));
                Next(3,TEXT("source_two_public003_spawns_one_real_lethal_localclaim"));return;
            }
            case 3:
            {
                const auto& K=LiveGuard->GetStoneGuardDriver()->State();
                if(!K.Action.InProgress)return;
                if(!Require(K.Action.Kind==Guard::EAttack::AxeSweep,TEXT("Genuine wake did not choose first axe")))return;
                FirstAttack=K.Action.AttackId;Next(4,TEXT("source_genuine_wake_first_axe"));return;
            }
            case 4:
            {
                const auto& K=LiveGuard->GetStoneGuardDriver()->State();
                if(K.Phase!=Guard::EPhase::Active)return;
                if(!Require(K.Action.AttackId==FirstAttack&&!K.Windows.empty()&&!K.HitReceipts.empty()&&NativeGame->PlayerFighter->Health<100.f,
                    TEXT("Actual first axe window/native outgoing hit absent")))return;
                LiveGuard->ApplyCombatHit(1.6f,NativeGame->PlayerFighter.Get(),85.f);
                const auto& After=LiveGuard->GetStoneGuardDriver()->State();
                if(!Require(After.HP==184.&&After.ReceivedHits.size()==1&&After.ReceivedHits.back().ActualHPLoss==1.
                    &&After.Closures.size()==1&&After.Phase==Guard::EPhase::Stunned,TEXT("Actual mitigated1HP/85poise receipt and interrupt closure absent")))return;
                Report->SetObjectField(TEXT("first_actual_interrupt"),GuardFacts(LiveGuard.Get()));Next(5,TEXT("source_public_native_mitigation_and_interrupt"));return;
            }
            case 5:
            {
                const auto& K=LiveGuard->GetStoneGuardDriver()->State();
                if(K.Action.AttackId<=FirstAttack||K.Phase!=Guard::EPhase::Active)return;
                if(!Require(K.Action.InProgress&&K.Action.WindowIssued&&K.Time==NativeGame->GetSimulationTime()
                    &&K.Time<K.Action.ActiveEnd&&!K.Windows.empty()&&!K.Closures.empty()&&!K.HitReceipts.empty()&&!K.ReceivedHits.empty()&&!K.Issued.empty()
                    &&DeadUnchanged(),TEXT("Real second active action/five histories/dead observer premise failed")))return;
                SavedLive=K;Report->SetObjectField(TEXT("saved_live_guard"),GuardFacts(LiveGuard.Get()));Report->SetObjectField(TEXT("saved_dead_guard"),GuardFacts(DeadGuard.Get()));
                if(OpenAndSaveSource()){Next(6,TEXT("source_original_live_deadline_and_deadobserver_committed"));FinishOnFrame=true;}return;
            }
            default:Finish(TEXT("Unknown source phase"));return;
            }
        }
        switch(Phase)
        {
        case 0:
        {
            auto Facts=NoRunFacts();Report->SetObjectField(TEXT("initial_pristine"),Facts);
            if(!Require(NoRunValid(Facts),TEXT("Actual pristine InitGame no-Run completed boundary failed")))return;
            Key(EKeys::R,true);Next(1,TEXT("restore_real_R_down_behind_pristine_gate"));return;
        }
        case 1:
            if(Wall-PhaseWall<.07)return;Key(EKeys::R,false);Next(2,TEXT("restore_real_R_up"));return;
        case 2:
        {
            if(PhaseTicks<3)return;auto Facts=NoRunFacts();Report->SetObjectField(TEXT("after_real_R"),Facts);
            if(!Require(NoRunValid(Facts),TEXT("Actual R created a Run behind pristine gate")))return;
            if(LoadAndInstall())Next(3,TEXT("restore_actual_V2_LoadAndPreparePristine_Install"));return;
        }
        case 3:
        {
            if(Wall-InstalledWall<.2)return;TArray<uint8> Paused;
            if(!CaptureBytes(Paused)||!Require(Paused==SavedCodec&&NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::AwaitExplicitContinue,
                TEXT("Paused whole Codec/clock mutated")))return;
            auto Fact=SaveBytes(TEXT("restored-paused-codec.json"),Paused);if(!Fact)return;Report->SetObjectField(TEXT("paused_codec"),Fact);
            Report->SetNumberField(TEXT("paused_wall_seconds"),Wall-InstalledWall);
            const bool Neutral=!NativeController->IsInputKeyDown(EKeys::Enter)&&!NativeController->IsInputKeyDown(EKeys::R)&&!NativeController->IsInputKeyDown(EKeys::J)&&!NativeController->IsInputKeyDown(EKeys::E)&&!NativeController->IsInputKeyDown(EKeys::T);
            Report->SetBoolField(TEXT("neutral_before_fresh_enter"),Neutral);if(!Require(Neutral,TEXT("Input not neutral before fresh Continue")))return;
            Key(EKeys::Enter,true);Next(4,TEXT("restore_real_fresh_Enter_down"));return;
        }
        case 4:
            if(Wall-PhaseWall<.07)return;Key(EKeys::Enter,false);Next(5,TEXT("restore_real_Enter_up_wait_original_active_end"));return;
        case 5:
        {
            const auto& K=LiveGuard->GetStoneGuardDriver()->State();if(NativeGame->GetSimulationTime()<SavedLive.Action.ActiveEnd+.04)return;
            if(!Require(NativeGame->GetRunInstallGate()==EDungeonRunInstallGate::Open&&NativeGame->GetRunRestartSerial()==0
                &&K.Action.AttackId==SavedLive.Action.AttackId&&K.Action.ActiveEnd==SavedLive.Action.ActiveEnd&&K.Phase==Guard::EPhase::Recovery
                &&K.HitReceipts.size()==SavedLive.HitReceipts.size()&&K.LastDamageReceiptId==SavedLive.LastDamageReceiptId&&DeadUnchanged(),TEXT("Original deadline/recovery/once hit/deadobserver continuity failed")))return;
            TArray<uint8> AtDeadline;if(!CaptureBytes(AtDeadline))return;auto Fact=SaveBytes(TEXT("deadline-codec.json"),AtDeadline);if(!Fact)return;Report->SetObjectField(TEXT("deadline_codec"),Fact);
            Report->SetObjectField(TEXT("original_deadline_observed"),GuardFacts(LiveGuard.Get()));
            LiveGuard->ApplyCombatHit(1.6f,NativeGame->PlayerFighter.Get(),0.f);
            const auto& After=LiveGuard->GetStoneGuardDriver()->State();
            if(!Require(After.HP==SavedLive.HP-1.&&After.LastDamageReceiptId==SavedLive.LastDamageReceiptId+1
                &&After.ReceivedHits.size()==SavedLive.ReceivedHits.size()+1&&After.ReceivedHits.back().ActualHPLoss==1.,TEXT("Next real mitigation receipt did not continue saved cursor exactly")))return;
            const FString BeforeMessage=NativeGame->LastMessage;
            NativeGame->OnFighterDied(DeadGuard.Get());NativeGame->OnFighterDied(DeadGuard.Get());
            const bool NoClaim=!DeadGuard->ClaimStoneGuardDeathEligibility();
            Report->SetBoolField(TEXT("explicit_dead_observer_reentry_unchanged"),NoClaim&&NativeGame->LastMessage==BeforeMessage&&DeadUnchanged());
            if(!Require(NoClaim&&NativeGame->LastMessage==BeforeMessage&&DeadUnchanged(),TEXT("Saved dead observer/localclaim replayed")))return;
            CompletionWall=Wall;Next(6,TEXT("restore_next_actual_receipt_and_twice_deadobserver_reentry"));return;
        }
        case 6:
        {
            if(Wall-CompletionWall<.2)return;const auto& K=LiveGuard->GetStoneGuardDriver()->State();
            if(!Require(K.LastDamageReceiptId==SavedLive.LastDamageReceiptId+1&&K.ReceivedHits.size()==SavedLive.ReceivedHits.size()+1
                &&K.HitReceipts.size()==SavedLive.HitReceipts.size()&&DeadUnchanged()&&!NativeGame->bGameOver,TEXT("Late native ticks duplicated receipt/hit/death or lost living player")))return;
            TArray<uint8> Continued;if(!CaptureBytes(Continued))return;auto Fact=SaveBytes(TEXT("continued-codec.json"),Continued);if(!Fact)return;Report->SetObjectField(TEXT("continued_codec"),Fact);
            Report->SetNumberField(TEXT("late_wait_seconds"),Wall-CompletionWall);ProofId(Report,TEXT("restart_serial"),NativeGame->GetRunRestartSerial());ProofId(Report,TEXT("final_gate"),uint64(NativeGame->GetRunInstallGate()));
            Report->SetObjectField(TEXT("final_live_guard"),GuardFacts(LiveGuard.Get()));Report->SetObjectField(TEXT("final_dead_guard"),GuardFacts(DeadGuard.Get()));
            Next(7,TEXT("restore_original_deadline_next_receipt_deadobserver_late_once"));FinishOnFrame=true;return;
        }
        default:Finish(TEXT("Unknown restore phase"));return;
        }
    }
};

void FDungeonGuardRunContinueProofDeleter::operator()(FDungeonGuardRunContinueProofState* State) const {delete State;}
ADungeonGuardRunContinueProbe::ADungeonGuardRunContinueProbe(){PrimaryActorTick.bCanEverTick=true;}
ADungeonGuardRunContinueProbe::~ADungeonGuardRunContinueProbe()=default;
void ADungeonGuardRunContinueProbe::BeginPlay()
{
    Super::BeginPlay();Proof.Reset(new FDungeonGuardRunContinueProofState());Proof->StartedWall=FPlatformTime::Seconds();
    const bool Save=FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRunSaveProof"));
    const bool Restore=FParse::Param(FCommandLine::Get(),TEXT("DungeonGuardRunRestoreProof"));Proof->Restore=Restore;Proof->Role=Restore?TEXT("restore"):TEXT("source");
    FString ProfileText;
    FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardRunProofDir="),Proof->Directory);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardRunProofProfiles="),Proof->ProfilesDirectory);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardRunProofProfile="),ProfileText);
    FParse::Value(FCommandLine::Get(),TEXT("DungeonGuardRunProofBuildId="),Proof->BuildId);
    const bool HasAbsolutePaths=!Proof->Directory.IsEmpty()&&!Proof->ProfilesDirectory.IsEmpty()
        &&!FPaths::IsRelative(Proof->Directory)&&!FPaths::IsRelative(Proof->ProfilesDirectory);
    if(HasAbsolutePaths)
    {Proof->Directory=FPaths::ConvertRelativePathToFull(Proof->Directory);Proof->ProfilesDirectory=FPaths::ConvertRelativePathToFull(Proof->ProfilesDirectory);}
    else Proof->Directory.Reset(); // Never turn a missing proof path into cwd output.
    Proof->Report->SetStringField(TEXT("schema"),TEXT("guard-disk-v2-two-process-role-v1"));Proof->Report->SetStringField(TEXT("role"),Proof->Role);
    ProofId(Proof->Report,TEXT("process_id"),FPlatformProcess::GetCurrentProcessId());Proof->Report->SetStringField(TEXT("build_id"),Proof->BuildId);
    if(!Proof->Require(HasAbsolutePaths&&Save!=Restore&&!ProfileText.IsEmpty()&&FGuid::Parse(ProfileText,Proof->ProfileId)&&Proof->ProfileId.IsValid()
        &&!Proof->Directory.IsEmpty()&&FPaths::GetCleanFilename(Proof->ProfilesDirectory)==TEXT("BoundRunOnly-v2")&&!Proof->BuildId.IsEmpty(),TEXT("Missing/mutually conflicting proof parameters")))return;
    Proof->ProfileDirectory=Proof->ProfilesDirectory/Proof->ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower);
    Proof->Report->SetStringField(TEXT("profile_id"),Proof->ProfileId.ToString(EGuidFormats::DigitsWithHyphensLower));
    Proof->Report->SetStringField(TEXT("profiles_directory"),Proof->ProfilesDirectory);Proof->Report->SetStringField(TEXT("profile_directory"),Proof->ProfileDirectory);
    const FString ReportPath=Proof->Directory/TEXT("runtime-report.json");
    if(IFileManager::Get().FileExists(*ReportPath)){Proof->Stopped=true;FPlatformMisc::RequestExitWithStatus(false,3);return;}
    IFileManager::Get().MakeDirectory(*Proof->Directory,true);
    if(!Proof->Require(Restore?IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory):!IFileManager::Get().DirectoryExists(*Proof->ProfileDirectory),
        TEXT("Source requires unused profile; Restore requires actual committed profile")))return;
    if(!Proof->Require(FParse::Param(FCommandLine::Get(),TEXT("DungeonContentProof"))&&FParse::Param(FCommandLine::Get(),TEXT("DungeonFastLosslessCapture"))
        &&FParse::Param(FCommandLine::Get(),TEXT("DungeonAsyncLosslessCapture"))&&!FApp::UseFixedTimeStep(),TEXT("Guard process proof requires existing native async lossless capture and ordinary pacing")))return;
    FString CaptureDirectory;FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),CaptureDirectory);
    FPaths::NormalizeDirectoryName(CaptureDirectory);FString ExpectedDirectory=Proof->Directory;FPaths::NormalizeDirectoryName(ExpectedDirectory);
    if(!Proof->Require(CaptureDirectory.Equals(ExpectedDirectory,ESearchCase::IgnoreCase),TEXT("Capture/proof original directories differ")))return;
    TArray<FString> OldFrames;IFileManager::Get().FindFiles(OldFrames,*(Proof->Directory/TEXT("MovieFrame*.png")),true,false);
    if(!Proof->Require(OldFrames.IsEmpty()&&!IFileManager::Get().FileExists(*(Proof->Directory/TEXT("prewarm-viewport.png"))),TEXT("Native capture originals already exist")))return;
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Proof->Directory;GIsDumpingMovie=0;
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonGuardRunContinueProbe::ScreenshotProcessed);
    Proof->Report->SetStringField(TEXT("scope"),TEXT("Two actual UE processes, real screen world public003 spawns, public native damage setup, exact V2 Run-only disk/pristine restore/clock/next receipt and independent saved dead observer; placeholder Guard visual. Not formal room encounter/spawn, reward amounts/pickup, Guard audio, full Profile/D13, art or complete-unit acceptance."));
    if(auto* NativeGame=GetWorld()->GetAuthGameMode<ADungeonGameMode>())AddTickPrerequisiteActor(NativeGame);
}
void ADungeonGuardRunContinueProbe::ScreenshotProcessed(){if(Proof)Proof->CaptureProcessed();}
void ADungeonGuardRunContinueProbe::Tick(float DeltaSeconds)
{Super::Tick(DeltaSeconds);if(Proof)Proof->Tick(*this);}
void ADungeonGuardRunContinueProbe::EndPlay(const EEndPlayReason::Type Reason)
{FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);if(Proof&&!Proof->Stopped)Proof->Finish(TEXT("World ended before native proof finished"));GIsDumpingMovie=0;Super::EndPlay(Reason);}
