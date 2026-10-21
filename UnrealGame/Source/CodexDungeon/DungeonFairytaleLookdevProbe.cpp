#include "DungeonFairytaleLookdevProbe.h"
#include "DungeonFairytaleLookdevState.h"
#include "DungeonProofScreenshots.h"
#include "DungeonHUD.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "UnrealClient.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/App.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
TArray<TSharedPtr<FJsonValue>> XY(FVector2D P)
{return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y)};}
TSharedPtr<FJsonObject> DrawRecord(const FFairytaleLookdevActorDraw& D)
{
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("path"),D.TexturePath);
    R->SetStringField(TEXT("clip"),D.Clip);
    R->SetNumberField(TEXT("frame"),D.Frame);R->SetStringField(TEXT("sample"),FString::Printf(TEXT("%lld"),(long long)D.Sample));
    R->SetNumberField(TEXT("native_facing"),D.NativeFacing);R->SetNumberField(TEXT("facing"),D.Facing);
    R->SetBoolField(TEXT("flipped"),D.Flipped);R->SetBoolField(TEXT("texture_ready"),D.TextureReady);
    R->SetStringField(TEXT("chest_path"),D.ChestTexturePath);
    R->SetBoolField(TEXT("chest_texture_ready"),D.ChestTextureReady);R->SetBoolField(TEXT("chest_drawn"),D.ChestDrawn);
    R->SetStringField(TEXT("near_shoulder_path"),D.NearShoulderTexturePath);R->SetStringField(TEXT("far_shoulder_path"),D.FarShoulderTexturePath);
    R->SetBoolField(TEXT("near_shoulder_ready"),D.NearShoulderReady);R->SetBoolField(TEXT("far_shoulder_ready"),D.FarShoulderReady);
    R->SetBoolField(TEXT("near_shoulder_drawn"),D.NearShoulderDrawn);R->SetBoolField(TEXT("far_shoulder_drawn"),D.FarShoulderDrawn);
    R->SetStringField(TEXT("near_bracer_path"),D.NearBracerTexturePath);R->SetStringField(TEXT("near_shin_path"),D.NearShinTexturePath);
    R->SetNumberField(TEXT("near_bracer_frame"),D.NearBracerFrame);R->SetNumberField(TEXT("near_shin_frame"),D.NearShinFrame);
    R->SetBoolField(TEXT("near_bracer_ready"),D.NearBracerReady);R->SetBoolField(TEXT("near_shin_ready"),D.NearShinReady);
    R->SetBoolField(TEXT("near_bracer_drawn"),D.NearBracerDrawn);R->SetBoolField(TEXT("near_shin_drawn"),D.NearShinDrawn);
    R->SetNumberField(TEXT("canvas_size"),D.CanvasSize);R->SetArrayField(TEXT("root"),XY(D.Root));
    R->SetArrayField(TEXT("ground"),XY(D.Ground));R->SetArrayField(TEXT("ground_screen"),XY(D.GroundScreen));
    R->SetArrayField(TEXT("top_screen"),XY(D.TopScreen));return R;
}
TSharedPtr<FJsonObject> FrozenGame(ADungeonGameMode* G)
{
    auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("available"),G&&G->GetPlayerFighter());
    if(!G||!G->GetPlayerFighter())return R;
    auto P=G->GetPlayerFighter();R->SetBoolField(TEXT("mode"),G->IsFairytaleLookdevPreview());
    R->SetBoolField(TEXT("waiting"),G->bWaitingForStart);R->SetNumberField(TEXT("simulation_time"),G->GetSimulationTime());
    R->SetNumberField(TEXT("restart_serial"),double(G->GetRunRestartSerial()));
    R->SetArrayField(TEXT("player_ground"),XY(P->GetGroundPosition()));R->SetNumberField(TEXT("player_facing"),P->Facing);
    R->SetBoolField(TEXT("player_tick_enabled"),P->IsActorTickEnabled());R->SetNumberField(TEXT("player_health"),P->Health);
    R->SetNumberField(TEXT("player_jump"),P->JumpHeight);R->SetNumberField(TEXT("player_animation_time"),P->AnimationTime);
    R->SetStringField(TEXT("player_weapon"),P->WeaponId);R->SetStringField(TEXT("player_armor"),P->ArmorId);
    R->SetNumberField(TEXT("player_coins"),P->Coins);
    const auto& Equipment=G->GetEquipmentView();const auto& World=G->GetWeaponWorldState();
    R->SetBoolField(TEXT("equipment_bound"),Equipment.Bound);R->SetStringField(TEXT("run_guid"),Equipment.RunGuid.ToString());
    R->SetStringField(TEXT("room_instance"),FString::Printf(TEXT("%llu"),(unsigned long long)Equipment.RoomInstanceId));
    R->SetStringField(TEXT("equipment_revision"),FString::Printf(TEXT("%llu"),(unsigned long long)Equipment.Revision));
    R->SetStringField(TEXT("equipment_next_operation"),FString::Printf(TEXT("%llu"),(unsigned long long)Equipment.NextOperationId));
    R->SetStringField(TEXT("equipment_next_crit"),FString::Printf(TEXT("%llu"),(unsigned long long)Equipment.NextCritDraw));
    R->SetNumberField(TEXT("world_time"),World.Time);
    R->SetStringField(TEXT("world_next_entity"),FString::Printf(TEXT("%llu"),(unsigned long long)World.NextEntityId));
    R->SetStringField(TEXT("world_next_sequence"),FString::Printf(TEXT("%llu"),(unsigned long long)World.NextEventSequence));
    R->SetNumberField(TEXT("world_events"),World.Events.Num());R->SetNumberField(TEXT("world_bindings"),World.ActorBindings.Num());
    R->SetNumberField(TEXT("action_audio_facts"),G->GetActionAudioState().Records.Num());
    R->SetNumberField(TEXT("projectiles"),G->GetWeaponWorldState().Projectiles.Num());
    TArray<TSharedPtr<FJsonValue>> Enemies;
    for(auto E:G->Enemies)if(IsValid(E))
    {
        auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("id"),E->GetUniqueID());
        Row->SetArrayField(TEXT("ground"),XY(E->GetGroundPosition()));Row->SetNumberField(TEXT("facing"),E->Facing);
        Row->SetNumberField(TEXT("health"),E->Health);Row->SetBoolField(TEXT("tick_enabled"),E->IsActorTickEnabled());
        Row->SetBoolField(TEXT("ai_enabled"),E->bAIEnabled);Enemies.Add(MakeShared<FJsonValueObject>(Row));
    }
    R->SetArrayField(TEXT("enemies"),Enemies);return R;
}
}

ADungeonFairytaleLookdevProbe::ADungeonFairytaleLookdevProbe(){PrimaryActorTick.bCanEverTick=true;}
void ADungeonFairytaleLookdevProbe::BeginPlay()
{
    Super::BeginPlay();GIsDumpingMovie=0;WarmStart=FPlatformTime::Seconds();
    if(!FParse::Value(FCommandLine::Get(),TEXT("DungeonContentProofDir="),Directory)||Directory.IsEmpty())
    {Saved=true;UE_LOG(LogTemp,Error,TEXT("Lookdev requires its independent capture directory"));FPlatformMisc::RequestExit(false);return;}
    Directory=FPaths::ConvertRelativePathToFull(Directory);
    TArray<FString> Prior;
    IFileManager::Get().FindFiles(Prior,*(Directory/TEXT("MovieFrame*.png")),true,false);
    if(Directory.IsEmpty()||Prior.Num()||IFileManager::Get().FileExists(*(Directory/TEXT("runtime-report.json")))
        ||IFileManager::Get().FileExists(*(Directory/TEXT("prewarm-viewport.png"))))
    {Saved=true;UE_LOG(LogTemp,Error,TEXT("Lookdev refuses prior evidence/invalid directory"));FPlatformMisc::RequestExit(false);return;}
    IFileManager::Get().MakeDirectory(*Directory,true);
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Directory;
    if(auto C=UGameplayStatics::GetPlayerController(this,0))C->AddTickPrerequisiteActor(this);
    if(auto V=IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS")))
        V->Set((FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleWalkLookdev"))
            ||FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleChestLookdev")))?30.f:60.f,ECVF_SetByCode);
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this,&ADungeonFairytaleLookdevProbe::ScreenshotProcessed);
}
void ADungeonFairytaleLookdevProbe::Key(FKey Code,bool Down)
{
    if(Keys.FindRef(Code)==Down)return;
    if(auto C=UGameplayStatics::GetPlayerController(this,0))
    {
        C->InputKey(FInputKeyParams(Code,Down?IE_Pressed:IE_Released,Down?1.:0.));Keys.Add(Code,Down);
        auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("key"),Code.ToString());R->SetBoolField(TEXT("down"),Down);
        R->SetNumberField(TEXT("wall_offset_s"),CaptureStart>0?FPlatformTime::Seconds()-CaptureStart:0.);
        Inputs.Add(MakeShared<FJsonValueObject>(R));
    }
}
void ADungeonFairytaleLookdevProbe::ScreenshotProcessed()
{
    if(Saved||Stopped)return;
    const double Wall=FPlatformTime::Seconds();
    auto C=UGameplayStatics::GetPlayerController(this,0);
    auto G=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto H=C?Cast<ADungeonHUD>(C->GetHUD()):nullptr;
    if(PrewarmPending&&!Started)
    {
        if(IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png")))<=8)
        {Finish(TEXT("prewarm_callback_without_file"));return;}
        PrewarmCompleted=Wall;CaptureStart=FPlatformTime::Seconds();Baseline=FrozenGame(G);
        Started=true;GIsDumpingMovie=-1;return;
    }
    if(!Started)return;
    FrameOffsets.Add(MakeShared<FJsonValueNumber>(Wall-CaptureStart));
    auto R=MakeShared<FJsonObject>();R->SetNumberField(TEXT("wall_offset_s"),Wall-CaptureStart);
    R->SetObjectField(TEXT("game"),FrozenGame(G));
    R->SetBoolField(TEXT("input_A"),C&&C->IsInputKeyDown(EKeys::A));R->SetBoolField(TEXT("input_D"),C&&C->IsInputKeyDown(EKeys::D));
    R->SetBoolField(TEXT("input_W"),C&&C->IsInputKeyDown(EKeys::W));R->SetBoolField(TEXT("input_C"),C&&C->IsInputKeyDown(EKeys::C));
    R->SetBoolField(TEXT("input_N"),C&&C->IsInputKeyDown(EKeys::N));R->SetBoolField(TEXT("input_F"),C&&C->IsInputKeyDown(EKeys::F));
    R->SetBoolField(TEXT("input_L"),C&&C->IsInputKeyDown(EKeys::L));
    R->SetBoolField(TEXT("input_B"),C&&C->IsInputKeyDown(EKeys::B));R->SetBoolField(TEXT("input_G"),C&&C->IsInputKeyDown(EKeys::G));
    R->SetBoolField(TEXT("hud_available"),H!=nullptr);
    if(H)
    {
        const auto& D=H->GetFairytaleLookdevDraw();R->SetBoolField(TEXT("active"),D.Active);
        R->SetBoolField(TEXT("hero_walk_active"),D.HeroWalkActive);
        R->SetBoolField(TEXT("hero_chest_active"),D.HeroChestActive);
        R->SetBoolField(TEXT("hero_shoulder_active"),D.HeroShoulderActive);
        R->SetBoolField(TEXT("hero_near_limb_active"),D.HeroNearLimbActive);
        R->SetBoolField(TEXT("limb_visible_choice"),D.LimbVisibleChoice);
        R->SetBoolField(TEXT("near_bracer_only"),D.NearBracerOnly);R->SetBoolField(TEXT("near_shin_only"),D.NearShinOnly);
        R->SetBoolField(TEXT("near_shoulder_only"),D.NearShoulderOnly);R->SetBoolField(TEXT("far_shoulder_only"),D.FarShoulderOnly);
        R->SetBoolField(TEXT("hero_dark_position"),D.HeroDarkPosition);R->SetBoolField(TEXT("chest_visible_choice"),D.ChestVisibleChoice);
        R->SetBoolField(TEXT("configuration_confirmed"),D.ConfigurationConfirmed);
        R->SetStringField(TEXT("draw_serial"),FString::Printf(TEXT("%llu"),(unsigned long long)D.Serial));
        R->SetNumberField(TEXT("draw_wall"),D.Wall);R->SetNumberField(TEXT("animation_elapsed_s"),D.AnimationElapsed);
        R->SetNumberField(TEXT("ui_scale"),D.UIScale);R->SetArrayField(TEXT("viewport"),XY(D.Viewport));
        R->SetArrayField(TEXT("camera_ground_center"),XY(H->GetCameraGroundCenter()));
        R->SetBoolField(TEXT("interface_visible"),H->GetInterfaceVisible());R->SetNumberField(TEXT("text_draw_calls"),H->GetRenderedTextDrawCalls());
        R->SetNumberField(TEXT("legacy_stack_count"),H->GetRenderedPlayerDrawStack().Num());
        R->SetBoolField(TEXT("legacy_weapon_used"),H->GetRenderedWeaponBodyUsed());
        R->SetNumberField(TEXT("action_audio_requests"),H->GetActionAudioPlayReceipts().Num());
        R->SetObjectField(TEXT("hero"),DrawRecord(D.Hero));R->SetObjectField(TEXT("stone"),DrawRecord(D.Stone));
    }
    Observations.Add(MakeShared<FJsonValueObject>(R));
}
void ADungeonFairytaleLookdevProbe::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);if(Saved||Stopped)return;
    const double Wall=FPlatformTime::Seconds();
    if(!Started)
    {
        if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLimbLookdev")))Key(EKeys::C,true);
        if(!PrewarmPending&&Wall-WarmStart>=2.)
        {PrewarmPending=true;PrewarmRequested=Wall;FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);}
        else if(Wall-WarmStart>17.)Finish(TEXT("prewarm_timeout"));
        return;
    }
    const double Elapsed=Wall-CaptureStart;
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLimbLookdev")))
    {
        constexpr double SegmentSeconds=1.5;
        if(Elapsed>=SegmentSeconds*16.){Finish();return;}
        Key(EKeys::C,true);Key(EKeys::N,false);Key(EKeys::F,false);
        if(FrameOffsets.Num()==0)return;
        const int32 Segment=FMath::Clamp(int32(FMath::FloorToDouble(Elapsed/SegmentSeconds)),0,15);
        const bool Isolated=Segment>=8;const int32 Choice=Isolated?Segment-8:Segment;
        const bool Left=Choice%4>=2;
        Key(EKeys::A,Left);Key(EKeys::D,!Left);Key(EKeys::W,Choice>=4);
        Key(EKeys::L,Isolated||Choice%2==1);
        Key(EKeys::B,Isolated&&Choice%2==0);Key(EKeys::G,Isolated&&Choice%2==1);
        const bool Blocked=Elapsed>=1.&&Elapsed<1.12;
        for(const auto K:{EKeys::S,EKeys::J,EKeys::K,EKeys::E,EKeys::Q,EKeys::T,EKeys::R,EKeys::Enter,EKeys::SpaceBar,EKeys::LeftShift})Key(K,Blocked);
        return;
    }
    if(FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleChestLookdev")))
    {
        const bool Shoulders=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleShoulderLookdev"));
        const double SegmentSeconds=Shoulders?2.1:1.4;
        if(Elapsed>=SegmentSeconds*(Shoulders?12.:8.)){Finish();return;}
        if(FrameOffsets.Num()==0)return;
        const int32 Segment=FMath::Clamp(int32(FMath::FloorToDouble(Elapsed/SegmentSeconds)),0,Shoulders?11:7);
        const bool Isolated=Shoulders&&Segment>=8;
        const bool Left=Isolated?Segment>=10:Segment%4>=2;
        Key(EKeys::A,Left);Key(EKeys::D,!Left);
        Key(EKeys::W,!Isolated&&Segment>=4);Key(EKeys::C,Isolated||Segment%2==1);
        if(Shoulders){Key(EKeys::N,Isolated&&Segment%2==0);Key(EKeys::F,Isolated&&Segment%2==1);}
        const bool Blocked=Elapsed>=1.&&Elapsed<1.12;
        for(const auto K:{EKeys::S,EKeys::J,EKeys::K,EKeys::E,EKeys::Q,EKeys::T,EKeys::R,EKeys::Enter,EKeys::SpaceBar,EKeys::LeftShift})Key(K,Blocked);
        return;
    }
    const bool Walk=FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleWalkLookdev"));
    const double FacingSpan=Walk?1.4:2.4;
    if(Elapsed>=FacingSpan*3.){Finish();return;}
    if(FrameOffsets.Num()==0)return; // Preserve one real initial frame before normal key requests.
    const bool Left=Elapsed>=FacingSpan&&Elapsed<FacingSpan*2.;
    Key(EKeys::A,Left);Key(EKeys::D,!Left);
    // Normal input stress: all these must remain inert in the isolated mode.
    const bool Blocked=Elapsed>=1.&&Elapsed<1.12;
    for(const auto K:{EKeys::W,EKeys::S,EKeys::J,EKeys::K,EKeys::E,EKeys::Q,EKeys::T,EKeys::R,EKeys::Enter,EKeys::SpaceBar,EKeys::LeftShift})Key(K,Blocked);
}
void ADungeonFairytaleLookdevProbe::Finish(const FString& Failure)
{
    if(Saved||Stopped)return;Stopped=true;CaptureStop=FPlatformTime::Seconds();GIsDumpingMovie=0;
    if(!Failure.IsEmpty())Failures.Add(Failure);
    TArray<FKey> Held;Keys.GetKeys(Held);for(const auto K:Held)Key(K,false);
    const bool Flushed=FlushFastLosslessProofScreenshots();FlushCompleted=FPlatformTime::Seconds();
    if(!Flushed)Failures.Add(TEXT("native_writer_flush_failed"));
    if(!Started||!Observations.Num())Failures.Add(TEXT("no_recorded_observations"));
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("schema"),TEXT("fairytale-lookdev-capture-v1"));
    R->SetStringField(TEXT("profile"),FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleLimbLookdev"))
        ?TEXT("fairytale_near_limb_observation_silent_v001"):FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleShoulderLookdev"))
        ?TEXT("fairytale_shoulder_observation_silent_v001"):FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleChestLookdev"))
        ?TEXT("fairytale_chest_observation_silent_v001"):FParse::Param(FCommandLine::Get(),TEXT("DungeonFairytaleWalkLookdev"))
        ?TEXT("fairytale_walk_observation_silent_v001"):TEXT("fairytale_idle_observation_silent"));R->SetBoolField(TEXT("passed"),Failures.IsEmpty());
    R->SetBoolField(TEXT("silent_video"),true);R->SetBoolField(TEXT("audio_capture_started"),false);
    R->SetBoolField(TEXT("native_async_capture_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonAsyncLosslessCapture")));
    R->SetBoolField(TEXT("native_async_capture_writes_flushed"),Flushed);
    R->SetBoolField(TEXT("native_async_flush_after_audio_stop"),false); // No audio recording was started/stopped.
    R->SetBoolField(TEXT("capture_stop_before_flush"),CaptureStop<=FlushCompleted);
    R->SetNumberField(TEXT("flush_completed_monotonic_s"),FlushCompleted);
    R->SetNumberField(TEXT("formal_complete_units"),0);R->SetBoolField(TEXT("new_style_accepted"),false);
    R->SetBoolField(TEXT("motion_reviewed"),false);R->SetBoolField(TEXT("auditioned"),false);
    auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("capture_start_monotonic_s"),CaptureStart);
    T->SetNumberField(TEXT("capture_stop_monotonic_s"),CaptureStop);T->SetNumberField(TEXT("requested_video_wall_duration_s"),CaptureStop-CaptureStart);
    T->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());T->SetArrayField(TEXT("frame_wall_offsets_s"),FrameOffsets);R->SetObjectField(TEXT("capture_timing"),T);
    auto P=MakeShared<FJsonObject>();P->SetBoolField(TEXT("requested"),PrewarmPending);
    P->SetBoolField(TEXT("completed_file_received"),PrewarmCompleted>0.);P->SetNumberField(TEXT("request_monotonic_s"),PrewarmRequested);
    P->SetNumberField(TEXT("complete_monotonic_s"),PrewarmCompleted);P->SetBoolField(TEXT("used_as_recording_frame"),false);R->SetObjectField(TEXT("prewarm_screenshot"),P);
    if(Baseline)R->SetObjectField(TEXT("baseline_game"),Baseline);
    R->SetArrayField(TEXT("observations"),Observations);R->SetArrayField(TEXT("normal_input_requests"),Inputs);
    TArray<TSharedPtr<FJsonValue>> F;for(const auto& E:Failures)F.Add(MakeShared<FJsonValueString>(E));R->SetArrayField(TEXT("failures"),F);
    FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(R,Writer);
    const bool Written=FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("runtime-report.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    Saved=true;if(!Written)UE_LOG(LogTemp,Error,TEXT("Lookdev report write failed; original frames retained"));
    FPlatformMisc::RequestExit(false);
}
void ADungeonFairytaleLookdevProbe::EndPlay(const EEndPlayReason::Type Reason)
{
    FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);Super::EndPlay(Reason);
}
