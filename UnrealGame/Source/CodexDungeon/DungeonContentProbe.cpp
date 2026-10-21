#include "DungeonContentProbe.h"
#include "DungeonProofScreenshots.h"
#include "DungeonXBWBodyPose.h"
#include "DungeonGameMode.h"
#include "DungeonFighter.h"
#include "DungeonHUD.h"
#include "DungeonRoomLayout.h"
#include "AudioDeviceManager.h"
#include "AudioMixerBlueprintLibrary.h"
#include "AudioMixerDevice.h"
#include "Sound/SoundSubmix.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "UnrealClient.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"

namespace
{
enum EUnitPhase { UnitInit, UnitArmor, UnitApproach, UnitWake, UnitCharge, UnitRecovery,
    UnitWaitShield, UnitEvadeShield, UnitReturnLine, UnitWaitFightShield, UnitFirstChain,
    UnitSecondChain, UnitTakeoff, UnitDescend, UnitAirAction, UnitLeftWalk, UnitGroundFollow, UnitDone,
    UnitSkillBeginPhase, UnitSkillAction, UnitSkillSinglePrimary,
    UnitExploreWalkToU, UnitExploreRetreat, UnitExploreWalkToExit, UnitExploreAwaitRoom,
    UnitExploreNewRoomHold };
const TCHAR* UnitPhaseName(int32 Phase)
{
    static const TCHAR* Names[] = {TEXT("initialize_development_fixture"),TEXT("qa_light_armor_action"),TEXT("approach_dormant_knight"),TEXT("observe_full_wake"),TEXT("locked_charge_and_jump"),TEXT("full_charge_recovery"),TEXT("await_first_shield"),TEXT("escape_shield_in_y"),TEXT("return_to_locked_line"),TEXT("await_second_shield"),TEXT("normal_sword_chain_and_real_nonpoise_hit"),TEXT("second_normal_sword_chain"),TEXT("normal_jump"),TEXT("descending_air_primary_input"),TEXT("air_primary_landing_and_natural_kill"),TEXT("normal_left_walk"),TEXT("ground_primary_after_air_completion"),TEXT("completed"),TEXT("normal_k_swd_skill_input"),TEXT("swd_skill_real_window_and_full_recovery"),TEXT("single_normal_ground_primary_after_skill"),TEXT("explore_normal_a_to_unknown_u"),TEXT("explore_normal_d_retreat_with_memory"),TEXT("explore_normal_d_to_old_exit"),TEXT("explore_fresh_e_await_actual_new_room"),TEXT("explore_new_room_idle_reset_observation")};
    return Phase>=0&&Phase<int32(UE_ARRAY_COUNT(Names))?Names[Phase]:TEXT("invalid");
}
FVector2D ExploreU() { return {DungeonRoomLayout::MinX+3.*64.,DungeonRoomLayout::MinY+7.*64.}; }
FVector2D ExploreV() { return {DungeonRoomLayout::MinX+40.*64.,DungeonRoomLayout::MinY+7.*64.}; }
FVector2D ExploreR() { return {DungeonRoomLayout::MinX+2.*64.,DungeonRoomLayout::MinY+7.*64.}; }
TArray<FString> RequiredProofChecks(bool FirstUnit,bool FirstUnitSkill=false,bool FirstUnitExplore=false,bool Equipment=false,bool ArmorLayers=false,bool ArmorCombo=false,bool Ranged=false,bool Sleeves=false,bool XBWReady=false,bool HeldIdentity=false,bool XBWPrimary=false,bool Scene=false,bool XBWReloadSocket=false,bool XBWArmorSocket=false)
{
    if(XBWArmorSocket)return FXBWArmorSocketProofState::RequiredChecks();
    if(XBWReloadSocket)return FXBWReloadSocketProofState::RequiredChecks();
    if(Scene) return FSceneProofState::RequiredChecks();
    if(XBWReady) return FRangedProofState::ReadyChecks(HeldIdentity,XBWPrimary);
    if(Ranged) return FRangedProofState::RequiredChecks();
    if(ArmorLayers)
    {
        TArray<FString> Names={TEXT("armor_layer_real_starter_no_armor")};
        for(const FString Armor:{TEXT("none"),TEXT("LGT"),TEXT("MED"),TEXT("HVY"),TEXT("ROB")})
        {
            Names.Add(TEXT("armor_")+Armor+TEXT("_idle_both_facings"));
            Names.Add(TEXT("armor_")+Armor+TEXT("_walk_both_facings_all6"));
            Names.Add(TEXT("armor_")+Armor+TEXT("_primary1_both_facings_all6"));
            if(ArmorCombo)
            {
                Names.Add(TEXT("armor_")+Armor+TEXT("_primary2_both_facings_all6"));
                Names.Add(TEXT("armor_")+Armor+TEXT("_primary3_both_facings_all6"));
                Names.Add(TEXT("armor_")+Armor+TEXT("_three_stage_chain_continuous_both_facings"));
                if(Sleeves && Armor==TEXT("ROB"))
                {
                    Names.Add(TEXT("armor_ROB_primary2_near_after_weapon_before_hand_both_facings"));
                    Names.Add(TEXT("armor_ROB_primary3_near_after_weapon_before_hand_both_facings"));
                }
            }
            if(Armor!=TEXT("none")) Names.Add(TEXT("armor_")+Armor+TEXT("_normal_e_050_commit"));
        }
        Names.Add(ArmorCombo?TEXT("armor_combo_completed_within_55s"):TEXT("armor_layer_completed_within_40s"));return Names;
    }
    if(Equipment) return {TEXT("equipment_real_run_starter_and_registered_sources"),TEXT("normal_k_lock_single_crit_and_real_cooldown"),TEXT("normal_e_weapon_035_kept_old_until_commit"),TEXT("normal_q_035_kept_instances_and_cooldown"),TEXT("normal_e_armor_050_single_stats_and_hp_cap"),TEXT("full_slots_e_requires_explicit_fresh_selection"),TEXT("normal_enter_backup_replacement_dropped_old_instance"),TEXT("normal_e_repickup_preserved_old_instance"),TEXT("equipment_completed_within_40s")};
    if (!FirstUnit) return {TEXT("player_uses_only_game_mode_simulation_clock"),TEXT("sword_normal_key_chain_all_three_stages"),TEXT("sword_three_hits_total_78_no_duplicate_damage"),TEXT("jump_apex_matches_630_1800"),TEXT("up_input_increases_ground_y"),TEXT("greatsword_normal_key_chain_all_three_stages"),TEXT("greatsword_three_hits_total_138"),TEXT("spear_normal_key_chain_all_three_stages"),TEXT("spear_nearest_target_three_hits_total_63")};
    TArray<FString> Required = {TEXT("first_unit_single_development_knight_and_default_sword"),TEXT("qa_light_armor_completed_after_half_second"),TEXT("stone_proximity_wake_completed_full_085"),TEXT("charge_direction_locked_after_player_y_change"),TEXT("charge_jump_avoided_real_damage"),TEXT("charge_full_160_recovery_before_next_attack"),TEXT("shield_y_escape_avoided_real_damage"),TEXT("sword_normal_input_all_three_stages"),TEXT("sword_first_chain_real_damage_without_stone_poise_break"),TEXT("player_nonpoise_hit_did_not_interrupt_primary"),TEXT("air_primary_rejected_second_start_and_continued_after_landing"),TEXT("stone_naturally_killed_by_accepted_air_primary"),TEXT("normal_left_walk_changes_position_and_facing"),TEXT("ground_primary_after_landed_air_action_completion"),TEXT("real_death_single_receipt_and_stable_prototype_rewards"),TEXT("first_unit_completed_within_30s")};
    if (FirstUnitSkill) Required.Append({TEXT("swd_skill_normal_k_accepted_real_timeline_and_lock_cooldown"),TEXT("swd_skill_one_real_armored_hit_without_repeat"),TEXT("swd_skill_full_recovery_and_fresh_k_rejected_same_action")});
    if (FirstUnitExplore) Required.Append({TEXT("explore_initial_u_v_r_unknown"),TEXT("explore_normal_a_revealed_u_r_and_memory_grew"),TEXT("explore_normal_d_retreat_kept_u_memory_outside_visibility"),TEXT("explore_unvisited_v_stayed_unknown_through_retreat"),TEXT("explore_fresh_e_changed_room_and_hud_reset_once"),TEXT("explore_new_room_cleared_r_and_u_matches_fresh_visibility"),TEXT("explore_completed_within_45s")});
    return Required;
}
}

ADungeonContentProbe::ADungeonContentProbe() { PrimaryActorTick.bCanEverTick = true; }
void ADungeonContentProbe::BeginPlay()
{
    Super::BeginPlay();
    bEquipmentProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonEquipmentAdapterProof"));
    bSceneProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonSceneExplorationProof"));
    bXBWReloadSocketProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWReloadSocketProof"));
    bXBWArmorSocketProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWArmorSocketProof"));
    bXBWPrimaryProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWPrimaryProof"));
    bXBWHeldIdentityProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWHeldIdentityProof")) || bXBWPrimaryProof;
    bXBWReadyProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWReadyProof")) || bXBWHeldIdentityProof;
    bRangedProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonRangedWeaponsProof")) || bXBWReadyProof;
    bArmorSleevesProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorSleevesProof"));
    bArmorComboProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorComboProof")) || bArmorSleevesProof;
    bArmorLayerProof = FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorLayerProof")) || bArmorComboProof;
    bFirstUnitExplore = FParse::Param(FCommandLine::Get(),TEXT("DungeonFirstUnitExploreProof"));
    bFirstUnitSkill = FParse::Param(FCommandLine::Get(),TEXT("DungeonFirstUnitSkillProof")) || bFirstUnitExplore;
    bFirstUnit = FParse::Param(FCommandLine::Get(),TEXT("DungeonFirstUnitProof")) || bFirstUnitSkill;
    FParse::Value(FCommandLine::Get(), TEXT("DungeonContentProofDir="), Directory);
    if (Directory.IsEmpty()) Directory = FPaths::ProjectSavedDir()/TEXT("ContentProof");
    Directory = FPaths::ConvertRelativePathToFull(Directory);
    if (IFileManager::Get().FileExists(*(Directory/TEXT("runtime-mix.wav")))
        || IFileManager::Get().FileExists(*(Directory/TEXT("runtime-mix-engine-export.wav")))
        || IFileManager::Get().FileExists(*(Directory/TEXT("prewarm-viewport.png")))
        || IFileManager::Get().FileExists(*(Directory/TEXT("runtime-report.json"))))
    {
        UE_LOG(LogTemp, Error, TEXT("ContentProof refuses to overwrite prior evidence: %s"), *Directory);
        bSaved = true;
        GIsDumpingMovie = 0;
        FPlatformMisc::RequestExit(false);
        return;
    }
    IFileManager::Get().MakeDirectory(*Directory, true);
    GetMutableDefault<UEngine>()->GameScreenshotSaveDirectory.Path=Directory;
    if (auto Controller = UGameplayStatics::GetPlayerController(this,0)) Controller->AddTickPrerequisiteActor(this);
    if (IConsoleVariable* MaxFPS = IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS")))
        MaxFPS->Set((bXBWReloadSocketProof||bXBWArmorSocketProof)?60.f:30.f, ECVF_SetByCode);
    // Do not let startup frames and asset warm-up contaminate the capture origin.
    GIsDumpingMovie = 0;
    WarmupStartWall = FPlatformTime::Seconds();
    FScreenshotRequest::OnScreenshotRequestProcessed().AddUObject(this, &ADungeonContentProbe::ScreenshotProcessed);
    if (auto Game = Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)))
        Game->bWaitingForStart = true;
    if (IConsoleVariable* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume")))
    {
        PreviousDisableAppVolume = AppVolume->GetInt();
        AppVolume->Set(1, ECVF_SetByCode); // This process only; no FApp setter or INI write.
        bAudioControlsConfigured = true;
    }
    if (Audio::FMixerDevice* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(this))
    {
        RecordingSubmix = &Mixer->GetMainSubmixObject();
        bPreviousSubmixAutoDisable = RecordingSubmix->bAutoDisable;
        // UE5.5's auto-disable early return skips the recorder's silent buffers.
        // Keep the main instance processing continuously during this QA capture.
        Mixer->SetSubmixAutoDisable(RecordingSubmix, false);
        bSubmixAutoDisableRequestQueued = true;
        RecordingSubmix->OnSubmixRecordedFileDone.AddDynamic(this, &ADungeonContentProbe::AudioExported);
    }
    else AudioFailure = TEXT("audio_mixer_unavailable");
}

void ADungeonContentProbe::BeginAudioCapture()
{
    CaptureStartWall = FPlatformTime::Seconds();
    BeginActionAudioEvidence();
    if (IConsoleVariable* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume")))
        DisableAppVolumeAtCapture = AppVolume->GetInt();
    if (Audio::FMixerDevice* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(this))
    {
        AudioClockStart = Mixer->GetAudioTime();
        PrimaryVolumeAtCapture = Mixer->GetPrimaryVolume();
    }
    bAudioStartRequested = true;
    // nullptr here is the main game output. No AudioCapture/microphone API is used.
    UAudioMixerBlueprintLibrary::StartRecordingOutput(this, bFirstUnitExplore||bEquipmentProof||bArmorLayerProof||bRangedProof||bSceneProof||bXBWReloadSocketProof||bXBWArmorSocketProof?64.f:(bFirstUnit?32.f:12.f), nullptr);
    GIsDumpingMovie = -1;
    UE_LOG(LogTemp, Display, TEXT("ContentProof recording after warmup: au.DisableAppVolume=%d, primary=%f"), DisableAppVolumeAtCapture, PrimaryVolumeAtCapture);
}

void ADungeonContentProbe::ScreenshotProcessed()
{
    if (bSaved) return;
    if (bWarmupScreenshotRequested && !bAudioStartRequested)
    {
        WarmupScreenshotCompletedWall = FPlatformTime::Seconds();
        bWarmupScreenshotCompleted = IFileManager::Get().FileSize(*(Directory/TEXT("prewarm-viewport.png"))) > 8;
        if (!bWarmupScreenshotCompleted)
        {
            AudioFailure = TEXT("prewarm_screenshot_callback_without_preserved_file");
            RestoreAudioControls();
            Save();
            FPlatformMisc::RequestExit(false);
            return;
        }
        // Start the real recording only after the expensive first PNG/readback
        // has actually finished. The preserved prewarm PNG has no audio stamp.
        BeginAudioCapture();
        return;
    }
    if (bAudioStartRequested && !bAudioStopRequested && !bSaved)
        FrameWallOffsets.Add(MakeShared<FJsonValueNumber>(FPlatformTime::Seconds()-CaptureStartWall));
}

void ADungeonContentProbe::RestoreAudioControls()
{
    if (bAudioControlsRestoreRequested) return;
    bAudioControlsRestoreRequested = true;
    if (bAudioControlsConfigured)
        if (IConsoleVariable* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume")))
        {
            AppVolume->Set(PreviousDisableAppVolume, ECVF_SetByCode);
            bAppVolumeRestored = AppVolume->GetInt() == PreviousDisableAppVolume;
        }
    if (RecordingSubmix)
        if (Audio::FMixerDevice* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(this))
            Mixer->SetSubmixAutoDisable(RecordingSubmix, bPreviousSubmixAutoDisable);
    UE_LOG(LogTemp, Display, TEXT("ContentProof QA audio control restore: app=%s, submix restore queued=%s"), bAppVolumeRestored?TEXT("restored"):TEXT("not_changed_or_failed"), RecordingSubmix?TEXT("yes"):TEXT("no"));
}

void ADungeonContentProbe::FinishAudioCapture()
{
    bAudioStopRequested = true;
    CaptureStopWall = FPlatformTime::Seconds();
    FreezeActionAudioEvidence();
    if (Audio::FMixerDevice* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(this))
    {
        AudioClockStop = Mixer->GetAudioTime();
        PrimaryVolumeAtStop = Mixer->GetPrimaryVolume();
    }
    GIsDumpingMovie = 0;
    FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);
    if (!bAudioStartRequested || !RecordingSubmix)
    {
        if (AudioFailure.IsEmpty()) AudioFailure = TEXT("main_submix_recording_not_started");
        RestoreAudioControls();
        Save();
        FPlatformMisc::RequestExit(false);
        return;
    }
    AudioExportDeadlineWall = CaptureStopWall + 10.0;
    // UE's WavFile path is asynchronous and normally returns nullptr. Passing the
    // explicit main submix lets its export delegate notify us after the write.
    UAudioMixerBlueprintLibrary::StopRecordingOutput(this, EAudioRecordingExportType::WavFile,
        TEXT("runtime-mix-engine-export"), Directory, RecordingSubmix, nullptr);
}

void ADungeonContentProbe::AudioExported(const USoundWave* ResultingSoundWave)
{
    if (bSaved) return;
    bAudioExportCallbackReceived = true;
    TArray<uint8> Original;
    if (FFileHelper::LoadFileToArray(Original, *(Directory/TEXT("runtime-mix-engine-export.wav"))) && Original.Num() > 44)
    {
        const auto U16 = [&Original](int32 Offset) { return uint32(Original[Offset]) | uint32(Original[Offset+1])<<8; };
        const auto U32 = [&Original](int32 Offset) { return uint32(Original[Offset]) | uint32(Original[Offset+1])<<8 | uint32(Original[Offset+2])<<16 | uint32(Original[Offset+3])<<24; };
        const uint32 Channels = U16(22), Rate = U32(24), ExpectedAlign = Channels*2;
        // Preserve UE's original forever. Only its confirmed BlockAlign=2 bug
        // is corrected in a separate standards-compliant header copy; PCM is unchanged.
        const bool Valid = FMemory::Memcmp(Original.GetData(),"RIFF",4)==0
            && FMemory::Memcmp(Original.GetData()+8,"WAVE",4)==0
            && FMemory::Memcmp(Original.GetData()+12,"fmt ",4)==0 && U32(16)==16 && U16(20)==1
            && Channels>=1 && Channels<=8 && Rate>=8000 && Rate<=192000 && U16(34)==16
            && (U16(32)==ExpectedAlign || U16(32)==2) && U32(28)==Rate*ExpectedAlign
            && FMemory::Memcmp(Original.GetData()+36,"data",4)==0
            && uint64(U32(4))+8==uint64(Original.Num()) && uint64(U32(40))+44==uint64(Original.Num())
            && U32(40)%ExpectedAlign==0;
        if (Valid)
        {
            TArray<uint8> Canonical = Original;
            bHeaderBlockAlignRepaired = U16(32)!=ExpectedAlign;
            Canonical[32] = uint8(ExpectedAlign & 255); Canonical[33] = uint8(ExpectedAlign >> 8);
            bPCMPayloadUnchanged = FMemory::Memcmp(Canonical.GetData()+44,Original.GetData()+44,Original.Num()-44)==0;
            bAudioRecorded = bPCMPayloadUnchanged && FFileHelper::SaveArrayToFile(Canonical,*(Directory/TEXT("runtime-mix.wav")));
        }
    }
    if (!bAudioRecorded) AudioFailure = TEXT("export_callback_without_valid_preserved_PCM_WAV");
    // Full PCM decode and non-silence are deliberately checked by the capture script.
    RestoreAudioControls();
    Save();
    FPlatformMisc::RequestExit(false);
}

void ADungeonContentProbe::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    RestoreAudioControls();
    FScreenshotRequest::OnScreenshotRequestProcessed().RemoveAll(this);
    if (RecordingSubmix)
        RecordingSubmix->OnSubmixRecordedFileDone.RemoveDynamic(this, &ADungeonContentProbe::AudioExported);
    if (!bSaved)
    {
        bAudioRecorded = false;
        AudioFailure = TEXT("capture_interrupted_before_completed_export");
        if (CaptureStopWall == 0) CaptureStopWall = FPlatformTime::Seconds();
        Save();
    }
    Super::EndPlay(EndPlayReason);
}
void ADungeonContentProbe::Key(FKey Code, bool Down)
{
    if (Keys.FindRef(Code) == Down) return;
    if (auto Controller = UGameplayStatics::GetPlayerController(this,0))
        Controller->InputKey(FInputKeyParams(Code, Down?IE_Pressed:IE_Released, Down?1.0:0.0));
    Keys.Add(Code, Down);
    if (bFirstUnit || bEquipmentProof || bArmorLayerProof || bRangedProof)
    {
        auto Row=MakeShared<FJsonObject>();
        Row->SetStringField(TEXT("record_type"),TEXT("normal_controller_key_edge_requested"));
        Row->SetStringField(TEXT("key"),Code.ToString());
        Row->SetBoolField(TEXT("down"),Down);
        Row->SetStringField(TEXT("fixture_stage"),bRangedProof?FString::Printf(TEXT("ranged_%02d"),RangedProof.Phase):bArmorLayerProof?FString::Printf(TEXT("armor_%d_%02d"),ArmorVariant,UnitPhase):bEquipmentProof?FString::Printf(TEXT("equipment_%02d"),UnitPhase):UnitPhaseName(UnitPhase));
        Row->SetNumberField(TEXT("wall_offset_s"),FPlatformTime::Seconds()-CaptureStartWall);
        if (const auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this)))
            Row->SetNumberField(TEXT("sim_time_s"),Game->GetSimulationTime());
        Trace.Add(MakeShared<FJsonValueObject>(Row));
    }
}
void ADungeonContentProbe::Check(const FString& Name, bool Passed)
{
    auto Row = MakeShared<FJsonObject>();
    Row->SetStringField(TEXT("name"),Name); Row->SetBoolField(TEXT("passed"),Passed);
    Results.Add(MakeShared<FJsonValueObject>(Row));
    UE_LOG(LogTemp,Display,TEXT("ContentProof %s: %s"),*Name,Passed?TEXT("PASS"):TEXT("FAIL"));
}
void ADungeonContentProbe::Setup(ADungeonGameMode* Game, const FString& Weapon, int32 Index)
{
    auto Player = Game->GetPlayerFighter();
    if (!Player || Game->Enemies.Num() < 1) return;
    Key(EKeys::J,false);
    Player->WeaponId = Weapon;
    Player->ResetFighter({-170,0});
    Player->Facing = 1;
    auto Target = Game->Enemies[0];
    Target->MaxHealth = 1000;
    Target->ResetFighter({-90,0});
    for (int32 I=0; I<Game->Enemies.Num(); ++I)
    {
        Game->Enemies[I]->bAIEnabled = false;
        if (I>0) Game->Enemies[I]->ResetFighter({600.f, I==1?-180.f:200.f});
    }
    Stages = 0; Fixture = Index;
    if (Index == 0) Check(TEXT("player_uses_only_game_mode_simulation_clock"),!Player->IsActorTickEnabled());
    Game->bWaitingForStart = false;
    Game->LastMessage = FParse::Param(FCommandLine::Get(),TEXT("DungeonCandidateSprites"))
        ? (Weapon==TEXT("WPN-SWD-001")
            ? TEXT("军剑候选英雄：连段与空中／纵深动作QA，视觉待审阅")
            : TEXT("重剑／枪：当前武器仍用占位图，连段与空间动作QA"))
        : TEXT("动作QA：三种近战连段与空中／纵深检查（现用原型画面）");
}

void ADungeonContentProbe::UnitReleaseInputs()
{
    TArray<FKey> Codes; Keys.GetKeys(Codes);
    for (const auto& Code:Codes) Key(Code,false);
    bUnitEdgeDown=false;
}
void ADungeonContentProbe::UnitMove(float X,float Y)
{
    Key(EKeys::A,X<0); Key(EKeys::D,X>0); Key(EKeys::W,Y>0); Key(EKeys::S,Y<0);
}
bool ADungeonContentProbe::UnitPulse(FKey Code,double Now)
{
    if (bUnitEdgeDown || Now<=UnitReleasedAt) return false;
    Key(Code,true);UnitEdgeKey=Code;UnitEdgeAt=Now;bUnitEdgeDown=true;return true;
}
void ADungeonContentProbe::UnitGo(int32 Phase,double Now)
{
    UnitMove(0,0);UnitPhase=Phase;UnitPhaseAt=Now;
    if (Phase==UnitFirstChain || Phase==UnitSecondChain)
    { UnitComboMask=0;UnitQueuedStage=0;bUnitChainStarted=false; }
    UE_LOG(LogTemp,Display,TEXT("FirstUnit stage %s at sim %.6f / wall %.6f"),UnitPhaseName(Phase),Now,Elapsed);
}
void ADungeonContentProbe::UnitFail(const FString& Reason)
{
    UnitFailure=Reason;UnitReleaseInputs();
    if (!bFirstUnitExplore) Check(TEXT("first_unit_completed_within_30s"),false);
    else
    {
        const FString FailureCheck=bUnitCombatCompleted?TEXT("explore_completed_within_45s"):TEXT("first_unit_completed_within_30s");
        if (!Results.ContainsByPredicate([&FailureCheck](const TSharedPtr<FJsonValue>& Value)
            { return Value->AsObject()->GetStringField(TEXT("name"))==FailureCheck; })) Check(FailureCheck,false);
    }
    UE_LOG(LogTemp,Error,TEXT("FirstUnit preserved failure at %s: %s"),UnitPhaseName(UnitPhase),*Reason);
    FinishAudioCapture();
}
void ADungeonContentProbe::UnitExploreSample(const FString& Label,ADungeonGameMode* Game,ADungeonFighter* Player)
{
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    const auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    if (!HUD || !Game || !Player) return;
    auto Sample=MakeShared<FJsonObject>();const auto P=Player->GetGroundPosition();
    Sample->SetStringField(TEXT("label"),Label);
    Sample->SetNumberField(TEXT("sim_time_s"),Game->GetSimulationTime());Sample->SetNumberField(TEXT("wall_offset_s"),Elapsed);
    Sample->SetNumberField(TEXT("player_x"),P.X);Sample->SetNumberField(TEXT("player_y"),P.Y);
    Sample->SetNumberField(TEXT("game_room"),Game->RoomNumber);Sample->SetNumberField(TEXT("hud_room"),HUD->GetExplorationRoomNumber());
    Sample->SetNumberField(TEXT("hud_reset_serial"),double(HUD->GetExplorationResetSerial()));
    Sample->SetNumberField(TEXT("explored_vertex_count"),HUD->GetExploredVertexCount());
    for (const FString Name:{TEXT("u"),TEXT("v"),TEXT("r")})
    {
        const auto Point=Name==TEXT("u")?ExploreU():(Name==TEXT("v")?ExploreV():ExploreR());
        Sample->SetNumberField(Name+TEXT("_x"),Point.X);Sample->SetNumberField(Name+TEXT("_y"),Point.Y);
        Sample->SetNumberField(Name+TEXT("_memory"),HUD->GetExplorationMemoryAt(Point));
        Sample->SetNumberField(Name+TEXT("_current_visibility"),HUD->GetCurrentVisibilityAt(Point));
    }
    const auto Camera=HUD->GetCameraGroundCenter();
    Sample->SetNumberField(TEXT("camera_ground_x"),Camera.X);Sample->SetNumberField(TEXT("camera_ground_y"),Camera.Y);
    Sample->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
    Sample->SetNumberField(TEXT("rendered_player_sprite_size"),HUD->GetRenderedPlayerSpriteSize());
    Sample->SetStringField(TEXT("player_animation"),Player->AnimationName);
    UnitExploreSamples.Add(MakeShared<FJsonValueObject>(Sample));
}
void ADungeonContentProbe::TickFirstUnit()
{
    auto Game=Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player=Game?Game->GetPlayerFighter():nullptr;
    if (!Game || !IsValid(Player) || Game->Enemies.Num()!=1 || !IsValid(Game->Enemies[0]))
    { UnitFail(TEXT("missing_single_development_encounter"));return; }
    auto Knight=Game->Enemies[0].Get();
    const auto Driver=Knight->GetStoneKnightDriver();
    if (!Driver) { UnitFail(TEXT("development_enemy_has_no_real_stone_driver"));return; }
    const auto& S=Driver->State();const auto& A=S.Action;
    const double Now=Game->GetSimulationTime();const FVector2D P=Player->GetGroundPosition();
    using KPhase=DungeonStoneKnight::EPhase;
    using KAttack=DungeonStoneKnight::EAttack;
    if (bUnitEdgeDown && Now>UnitEdgeAt)
    { Key(UnitEdgeKey,false);bUnitEdgeDown=false;UnitReleasedAt=Now; }
    auto Row=MakeShared<FJsonObject>();
    Row->SetStringField(TEXT("record_type"),TEXT("post_batch_state_observation"));
    Row->SetStringField(TEXT("fixture_stage"),UnitPhaseName(UnitPhase));
    Row->SetNumberField(TEXT("sim_time_s"),Now);Row->SetNumberField(TEXT("wall_offset_s"),Elapsed);
    Row->SetNumberField(TEXT("player_x"),P.X);Row->SetNumberField(TEXT("player_y"),P.Y);
    Row->SetNumberField(TEXT("player_hp"),Player->Health);Row->SetNumberField(TEXT("player_focus"),Player->Focus);
    Row->SetNumberField(TEXT("player_height"),Player->JumpHeight);Row->SetNumberField(TEXT("player_vz"),Player->GetVerticalVelocity());
    Row->SetNumberField(TEXT("player_attack_remaining"),Player->AttackTime);
    Row->SetNumberField(TEXT("player_combo_stage"),Player->ComboStage);
    Row->SetStringField(TEXT("player_attack_phase"),Player->AttackPhase);
    Row->SetNumberField(TEXT("player_facing"),Player->Facing);
    Row->SetNumberField(TEXT("knight_hp"),S.HP);Row->SetNumberField(TEXT("knight_phase"),int32(S.Phase));
    Row->SetNumberField(TEXT("knight_x"),S.Position.X);Row->SetNumberField(TEXT("knight_y"),S.Position.Y);
    Row->SetNumberField(TEXT("knight_attack_id"),double(A.AttackId));Row->SetNumberField(TEXT("knight_attack_kind"),int32(A.Kind));
    Row->SetBoolField(TEXT("knight_attack_locked"),A.Locked);
    Row->SetNumberField(TEXT("knight_lock_at"),A.LockAt);Row->SetNumberField(TEXT("knight_active_at"),A.ActiveAt);
    Row->SetNumberField(TEXT("knight_active_end"),A.ActiveEnd);Row->SetNumberField(TEXT("knight_recovery_end"),A.RecoveryEnd);
    Row->SetNumberField(TEXT("knight_direction_x"),A.Direction.X);Row->SetNumberField(TEXT("knight_direction_y"),A.Direction.Y);
    Row->SetNumberField(TEXT("knight_wake_started"),S.WakeStartedAt);Row->SetNumberField(TEXT("knight_wake_end"),S.WakeEnd);
    Row->SetNumberField(TEXT("knight_poise_accum"),S.PoiseAccum);Row->SetNumberField(TEXT("knight_stun_until"),S.StunUntil);
    Row->SetBoolField(TEXT("knight_reward_claimed"),S.RewardClaimed);
    Row->SetBoolField(TEXT("knight_death_reported"),Knight->bDeathReported);
    Row->SetNumberField(TEXT("prototype_pickup_count"),Game->Pickups.Num());
    if (bFirstUnitSkill)
    {
        const auto& Skill=Player->GetWeaponSkillAction();
        Row->SetNumberField(TEXT("swd_skill_action_id"),double(Skill.ActionId));
        Row->SetNumberField(TEXT("swd_skill_action_type"),int32(Skill.Type));
        Row->SetNumberField(TEXT("swd_skill_phase"),int32(Skill.Phase));
        Row->SetBoolField(TEXT("swd_skill_active"),Skill.Active);Row->SetBoolField(TEXT("swd_skill_locked"),Skill.Locked);
        Row->SetNumberField(TEXT("swd_skill_start"),Skill.Start);Row->SetNumberField(TEXT("swd_skill_lock_at"),Skill.LockAt);
        Row->SetNumberField(TEXT("swd_skill_active_at"),Skill.ActiveAt);Row->SetNumberField(TEXT("swd_skill_active_end"),Skill.ActiveEnd);
        Row->SetNumberField(TEXT("swd_skill_end"),Skill.End);Row->SetNumberField(TEXT("swd_skill_next_subhit"),Skill.NextSubhit);
        Row->SetBoolField(TEXT("swd_skill_forward_step_issued"),Skill.ForwardStepIssued);
        Row->SetNumberField(TEXT("swd_skill_cooldown_remaining"),Player->GetWeaponSkillCooldownRemaining());
        Row->SetStringField(TEXT("player_animation"),Player->AnimationName);Row->SetNumberField(TEXT("player_animation_age"),Player->AnimationTime);
    }
    const auto Controller=UGameplayStatics::GetPlayerController(this,0);
    const auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
    if (bFirstUnitExplore && HUD)
    {
        Row->SetNumberField(TEXT("game_room"),Game->RoomNumber);Row->SetNumberField(TEXT("hud_room"),HUD->GetExplorationRoomNumber());
        Row->SetNumberField(TEXT("hud_reset_serial"),double(HUD->GetExplorationResetSerial()));
        Row->SetNumberField(TEXT("explored_vertex_count"),HUD->GetExploredVertexCount());
        Row->SetNumberField(TEXT("u_memory"),HUD->GetExplorationMemoryAt(ExploreU()));
        Row->SetNumberField(TEXT("u_current_visibility"),HUD->GetCurrentVisibilityAt(ExploreU()));
        Row->SetNumberField(TEXT("v_memory"),HUD->GetExplorationMemoryAt(ExploreV()));
        Row->SetNumberField(TEXT("v_current_visibility"),HUD->GetCurrentVisibilityAt(ExploreV()));
        Row->SetNumberField(TEXT("r_memory"),HUD->GetExplorationMemoryAt(ExploreR()));
        Row->SetNumberField(TEXT("r_current_visibility"),HUD->GetCurrentVisibilityAt(ExploreR()));
        const auto Camera=HUD->GetCameraGroundCenter();
        Row->SetNumberField(TEXT("camera_ground_x"),Camera.X);Row->SetNumberField(TEXT("camera_ground_y"),Camera.Y);
        Row->SetStringField(TEXT("rendered_player_texture_path"),HUD->GetRenderedPlayerTexturePath());
        Row->SetNumberField(TEXT("rendered_player_sprite_size"),HUD->GetRenderedPlayerSpriteSize());
        if (!HUD->GetRenderedPlayerTexturePath().IsEmpty()) UnitRenderedTexturePaths.Add(HUD->GetRenderedPlayerTexturePath());
        if (bUnitExploreInitialized && Game->RoomNumber==UnitExploreRoom && HUD->GetExplorationRoomNumber()==UnitExploreRoom)
        {
            bUnitExploreMemoryMonotonic &= HUD->GetExploredVertexCount()>=UnitExploreLastCount
                && HUD->GetExplorationResetSerial()==UnitExploreResetSerial;
            UnitExploreLastCount=HUD->GetExploredVertexCount();
        }
    }
    Trace.Add(MakeShared<FJsonValueObject>(Row));
    if (Elapsed>=(bFirstUnitExplore&&bUnitCombatCompleted?45.0:30.0))
    { UnitFail(bFirstUnitExplore&&bUnitCombatCompleted?TEXT("forty_five_second_explore_deadline"):TEXT("thirty_second_fixture_deadline"));return; }
    if (Player->bDead || Game->bGameOver) { UnitFail(TEXT("player_died_during_normal_input_fixture"));return; }
    if (UnitPhase!=UnitInit && Now<UnitPhaseAt) { UnitFail(TEXT("simulation_clock_reversed"));return; }
    switch (UnitPhase)
    {
    case UnitInit:
    {
        if (bFirstUnitExplore)
        {
            // Read the state used by DrawHUD; querying never reveals a point.
            if (!HUD || HUD->GetExplorationRoomNumber()!=Game->RoomNumber || HUD->GetExplorationResetSerial()==0) break;
            UnitExploreRoom=Game->RoomNumber;UnitExploreResetSerial=HUD->GetExplorationResetSerial();
            UnitExploreInitialCount=HUD->GetExploredVertexCount();UnitExploreLastCount=UnitExploreInitialCount;
            UnitExplorePlayer=Player;bUnitExploreInitialized=true;
            const bool Unknown=UnitExploreInitialCount>0 && HUD->GetExplorationMemoryAt(ExploreU())==0.
                &&HUD->GetExplorationMemoryAt(ExploreV())==0.&&HUD->GetExplorationMemoryAt(ExploreR())==0.
                &&HUD->GetCurrentVisibilityAt(ExploreU())==0.&&HUD->GetCurrentVisibilityAt(ExploreV())==0.
                &&HUD->GetCurrentVisibilityAt(ExploreR())==0.;
            UnitExploreSample(TEXT("initial_unknown_world_vertices"),Game,Player);
            Check(TEXT("explore_initial_u_v_r_unknown"),Unknown);
            if (!Unknown) { UnitFail(TEXT("explore_initial_witness_already_revealed"));return; }
            Game->LastMessage=FParse::Param(FCommandLine::Get(),TEXT("DungeonCandidateSprites"))
                ?TEXT("探索QA：圆盔角色候选；记录实测TexturePath／尺寸及揭雾／记忆／E换房；全动作、分层与音效另行验收")
                :TEXT("探索QA：当前原型画面；正常战斗后检验世界揭雾／记忆／E换房");
        }
        const bool Valid=FParse::Param(FCommandLine::Get(),TEXT("DungeonStoneKnightPreview"))
            && (Player->WeaponId==TEXT("sword") || Player->WeaponId==TEXT("WPN-SWD-001"))
            && !Player->IsActorTickEnabled() && S.Phase==KPhase::Dormant && !Knight->bDead;
        Check(TEXT("first_unit_single_development_knight_and_default_sword"),Valid);
        if (!Valid) { UnitFail(TEXT("unexpected_initial_fixture_state"));return; }
        UnitInitialHP=Player->Health;UnitStartSim=Now;Game->bWaitingForStart=false;
        // Explicit QA assignment action, not a pickup/source or acquisition proof.
        if (!Player->BeginArmorChange(TEXT("ARM-LGT-001"))) { UnitFail(TEXT("qa_light_armor_action_rejected"));return; }
        UnitGo(UnitArmor,Now);break;
    }
    case UnitArmor:
        if (Player->GetArmorChangeRemaining()<=0)
        {
            const bool Valid=Player->ArmorId==TEXT("ARM-LGT-001")&&Now-UnitPhaseAt>=.5-1.e-5&&Player->Health==UnitInitialHP;
            Check(TEXT("qa_light_armor_completed_after_half_second"),Valid);
            if (!Valid) { UnitFail(TEXT("qa_armor_did_not_finish_original_half_second_action"));return; }
            UnitGo(UnitApproach,Now);
        }
        break;
    case UnitApproach:
        if (S.WakeStartedAt>=0)
        {
            UnitWakeAt=S.WakeStartedAt;UnitWakeEnd=S.WakeEnd;
            const double X=(P.X-S.Position.X)/260.,Y=(P.Y-S.Position.Y)/110.;
            if (X*X+Y*Y>1.01 || UnitWakeAt-UnitStartSim>=12.0)
            { UnitFail(TEXT("wake_was_not_observed_from_real_proximity"));return; }
            UnitGo(UnitWake,Now);
        }
        else UnitMove(P.X<S.Position.X?1:-1,0);
        break;
    case UnitWake:
        if (S.Awakened)
        {
            Check(TEXT("stone_proximity_wake_completed_full_085"),FMath::Abs(UnitWakeEnd-UnitWakeAt-.85)<1.e-8&&Now>=UnitWakeEnd);
            UnitChargeHP=Player->Health;UnitGo(UnitCharge,Now);
        }
        break;
    case UnitCharge:
        if (A.Kind!=KAttack::Charge || !A.InProgress) break;
        if (!UnitChargeId) UnitChargeId=A.AttackId;
        if (A.AttackId!=UnitChargeId) { UnitFail(TEXT("charge_replaced_before_observed_completion"));return; }
        if (A.Locked)
        {
            if (UnitChargeDirection.IsNearlyZero())
            { UnitChargeDirection={A.Direction.X,A.Direction.Y};UnitLockedPlayerY=P.Y; }
            bUnitLineStable &= UnitChargeDirection.Equals(FVector2D(A.Direction.X,A.Direction.Y),1.e-9);
            if (!bUnitChargeNudgeIssued && Now<A.ActiveAt-.08)
            { UnitMove(1,1);bUnitChargeNudgeIssued=true; }
            else UnitMove(0,0);
            bUnitYChangedAfterLock |= P.Y-UnitLockedPlayerY>=5;
            if (!bUnitJumpIssued && Now>=A.ActiveAt-.04 && Player->CanStartAttack())
                bUnitJumpIssued=UnitPulse(EKeys::SpaceBar,Now);
        }
        bUnitJumpHigh |= Player->JumpHeight>65;
        if (S.Phase==KPhase::Recovery)
        {
            bool PlayerHit=false;
            for (const auto& Hit:S.HitReceipts) PlayerHit|=Hit.AttackId==UnitChargeId&&Hit.TargetId==Player->GetRuntimeEntityId();
            const double Across=(P.X-S.Position.X)*-UnitChargeDirection.Y+(P.Y-S.Position.Y)*UnitChargeDirection.X;
            const bool StillInNarrowLine=FMath::Abs(Across)<=24;
            Check(TEXT("charge_direction_locked_after_player_y_change"),bUnitLineStable&&bUnitYChangedAfterLock);
            Check(TEXT("charge_jump_avoided_real_damage"),bUnitJumpIssued&&bUnitJumpHigh&&Player->JumpHeight>65&&StillInNarrowLine
                &&A.Stop==DungeonStoneKnight::EStop::Body&&!PlayerHit&&Player->Health==UnitChargeHP);
            UnitChargeEnd=A.ActiveEnd;UnitRecoveryEnd=A.RecoveryEnd;UnitGo(UnitRecovery,Now);
        }
        break;
    case UnitRecovery:
        if (Now<UnitRecoveryEnd)
        {
            bUnitEarlyNextAttack |= A.AttackId!=UnitChargeId;
            bUnitRecoveryHeld |= A.AttackId==UnitChargeId&&S.Phase==KPhase::Recovery;
        }
        else
        {
            Check(TEXT("charge_full_160_recovery_before_next_attack"),bUnitRecoveryHeld&&!bUnitEarlyNextAttack&&FMath::Abs(UnitRecoveryEnd-UnitChargeEnd-1.6)<1.e-8);
            UnitGo(UnitWaitShield,Now);
        }
        break;
    case UnitWaitShield:
        if (A.Kind==KAttack::Shield&&A.InProgress)
        {
            UnitEscapeShieldId=A.AttackId;UnitShieldEnd=A.ActiveEnd;UnitShieldOriginY=A.Origin.Y;
            UnitEscapeHP=Player->Health;UnitGo(UnitEvadeShield,Now);
        }
        break;
    case UnitEvadeShield:
        if (A.AttackId!=UnitEscapeShieldId) { UnitFail(TEXT("shield_changed_before_escape_observation"));return; }
        if (A.Locked && P.Y-UnitShieldOriginY<80) UnitMove(0,1);
        else UnitMove(0,0);
        if (Now>=UnitShieldEnd)
        {
            const bool Valid=Player->Health==UnitEscapeHP&&FMath::Abs(P.Y-UnitShieldOriginY)>32;
            Check(TEXT("shield_y_escape_avoided_real_damage"),Valid);
            if (!Valid) { UnitFail(TEXT("normal_y_input_did_not_avoid_first_shield"));return; }
            UnitGo(UnitReturnLine,Now);
        }
        break;
    case UnitReturnLine:
        if (FMath::Abs(P.Y-UnitShieldOriginY)<=5) UnitGo(UnitWaitFightShield,Now);
        else UnitMove(0,P.Y>UnitShieldOriginY?-1:1);
        break;
    case UnitWaitFightShield:
        if (A.Kind==KAttack::Shield&&A.InProgress&&A.AttackId!=UnitEscapeShieldId)
        {
            UnitFightShieldId=A.AttackId;UnitFightHP=Player->Health;UnitChainStartHP=float(S.HP);
            UnitGo(UnitFirstChain,Now);
        }
        break;
    case UnitFirstChain: case UnitSecondChain:
    {
        const bool First=UnitPhase==UnitFirstChain;
        if (First)
        {
            bUnitStonePoiseBreak |= S.StunUntil>0 || S.Phase==KPhase::Stunned;
            if (Player->Health<UnitFightHP && Player->ComboStage>0 && Player->AttackTime>0
                && A.AttackId==UnitFightShieldId && A.Stagger<Player->GetPoiseThreshold()) bUnitNonPoiseHit=true;
        }
        if (Player->ComboStage>0) UnitComboMask|=1<<(Player->ComboStage-1);
        const bool ReadyToStart=!First || (A.AttackId==UnitFightShieldId&&A.Locked&&Now>=A.LockAt+.02);
        if (!bUnitChainStarted && ReadyToStart && Player->CanStartAttack() && UnitPulse(EKeys::J,Now))
        { bUnitChainStarted=true;UnitQueuedStage=1; }
        else if (bUnitChainStarted && Player->ComboStage>=1 && Player->ComboStage<=2
            && Player->AttackPhase==TEXT("recovery") && Player->AttackTime>0 && Player->AttackTime<=.10f
            && UnitQueuedStage==Player->ComboStage && UnitPulse(EKeys::J,Now)) ++UnitQueuedStage;
        if (bUnitChainStarted && UnitComboMask!=0 && Player->AttackTime<=0)
        {
            if (First)
            {
                Check(TEXT("sword_normal_input_all_three_stages"),UnitComboMask==7);
                Check(TEXT("sword_first_chain_real_damage_without_stone_poise_break"),!bUnitStonePoiseBreak&&FMath::Abs((UnitChainStartHP-S.HP)-78./1.45)<.05);
                Check(TEXT("player_nonpoise_hit_did_not_interrupt_primary"),bUnitNonPoiseHit&&Player->Health<UnitFightHP);
                UnitGo(bFirstUnitSkill?UnitSkillBeginPhase:UnitSecondChain,Now);
            }
            else
            {
                if (Knight->bDead || S.HP<=0 || S.HP>26./1.45+.05)
                { UnitFail(TEXT("normal_second_chain_did_not_leave_a_real_air_finisher_target"));return; }
                UnitAirStartHP=float(S.HP);UnitGo(UnitTakeoff,Now);
            }
        }
        break;
    }
    case UnitSkillBeginPhase: case UnitSkillAction:
    {
        const auto& Skill=Player->GetWeaponSkillAction();
        using SkillType=DungeonWeaponActions::EAction;
        using SkillPhase=DungeonContentCombat::EPhase;
        if (!bUnitSkillInputIssued)
        {
            if (Player->CanStartAttack() && UnitPulse(EKeys::K,Now))
            {
                bUnitSkillInputIssued=true;UnitSkillRequestedAt=Now;
                UnitSkillStartHP=S.HP;UnitSkillPreviousHP=S.HP;
            }
            break;
        }
        if (!bUnitSkillAccepted)
        {
            if (Skill.Active && Skill.Type==SkillType::Skill && Skill.Weapon==DungeonContentCombat::EWeapon::SWD001
                && Skill.ActionId!=0 && Skill.Start>=UnitSkillRequestedAt && !Skill.StartedAirborne)
            {
                bUnitSkillAccepted=true;UnitSkillId=Skill.ActionId;UnitSkillStart=Skill.Start;UnitSkillLockAt=Skill.LockAt;
                UnitSkillActiveAt=Skill.ActiveAt;UnitSkillActiveEnd=Skill.ActiveEnd;UnitSkillEnd=Skill.End;
                UnitGo(UnitSkillAction,Now);
            }
            else if (Now-UnitSkillRequestedAt>1.0) { UnitFail(TEXT("normal_k_was_not_accepted_as_real_swd_skill"));return; }
            else break;
        }
        if (Skill.ActionId!=UnitSkillId || Skill.Start!=UnitSkillStart || Skill.LockAt!=UnitSkillLockAt
            || Skill.ActiveAt!=UnitSkillActiveAt || Skill.ActiveEnd!=UnitSkillActiveEnd || Skill.End!=UnitSkillEnd)
        { UnitFail(TEXT("normal_skill_input_replaced_or_retimed_original_action"));return; }
        if (S.HP<UnitSkillPreviousHP)
        {
            ++UnitSkillDamageObservations;
            bUnitSkillDamageTimingValid &= Now>=UnitSkillActiveAt;
        }
        UnitSkillPreviousHP=S.HP;
        if (!Skill.Locked)
        {
            bUnitSkillUnlockedObserved |= Now<UnitSkillLockAt;
            bUnitSkillCooldownValid &= Player->GetWeaponSkillCooldownRemaining()==0.0;
        }
        else
        {
            bUnitSkillLockedObserved=true;
            const double Deadline=Now+Player->GetWeaponSkillCooldownRemaining();
            if (UnitSkillCooldownDeadline==0) UnitSkillCooldownDeadline=Deadline;
            bUnitSkillCooldownValid &= FMath::Abs(Deadline-(UnitSkillLockAt+4.0))<1.e-5;
        }
        bUnitSkillActiveObserved |= Skill.Active&&Skill.Phase==SkillPhase::Active;
        bUnitSkillRecoveryObserved |= Skill.Active&&Skill.Phase==SkillPhase::Recovery&&Now<UnitSkillEnd;
        if (bUnitSkillExtraIssued && Now>UnitSkillExtraAt)
            bUnitSkillExtraRejected |= Skill.ActionId==UnitSkillId&&Skill.Start==UnitSkillStart&&Skill.Active;
        if (Now<UnitSkillEnd)
        {
            bUnitSkillNoEarlyEnd &= Skill.Active&&!Player->CanStartAttack();
            if (!Skill.Active) { UnitFail(TEXT("swd_skill_ended_before_full_068_action"));return; }
            if (!bUnitSkillExtraIssued && Skill.Phase==SkillPhase::Recovery && Now>=UnitSkillActiveEnd+.03
                && Now<UnitSkillEnd-.06 && UnitPulse(EKeys::K,Now))
            { bUnitSkillExtraIssued=true;UnitSkillExtraAt=Now; }
            break;
        }
        UnitSkillCompletedAt=Now;UnitSkillEndHP=S.HP;
        const bool Timeline=bUnitSkillAccepted&&bUnitSkillUnlockedObserved&&bUnitSkillLockedObserved&&bUnitSkillCooldownValid
            &&FMath::Abs(UnitSkillLockAt-UnitSkillStart-.08)<1.e-8&&FMath::Abs(UnitSkillActiveAt-UnitSkillStart-.20)<1.e-8
            &&FMath::Abs(UnitSkillActiveEnd-UnitSkillStart-.30)<1.e-8&&FMath::Abs(UnitSkillEnd-UnitSkillStart-.68)<1.e-8
            &&FMath::Abs(UnitSkillCooldownDeadline-UnitSkillStart-4.08)<1.e-5;
        const bool OneDamage=bUnitSkillActiveObserved&&Skill.NextSubhit==1&&Skill.ForwardStepIssued&&bUnitSkillDamageTimingValid
            &&UnitSkillDamageObservations==1&&FMath::Abs((UnitSkillStartHP-S.HP)-32./1.45)<.05&&!Knight->bDead;
        const bool Recovery=bUnitSkillRecoveryObserved&&bUnitSkillNoEarlyEnd&&bUnitSkillExtraIssued&&bUnitSkillExtraRejected
            &&!Skill.Active&&Skill.Terminal==DungeonWeaponActions::EEvent::Completed&&Now>=UnitSkillEnd;
        Check(TEXT("swd_skill_normal_k_accepted_real_timeline_and_lock_cooldown"),Timeline);
        Check(TEXT("swd_skill_one_real_armored_hit_without_repeat"),OneDamage);
        Check(TEXT("swd_skill_full_recovery_and_fresh_k_rejected_same_action"),Recovery);
        if (!Timeline || !OneDamage || !Recovery) { UnitFail(TEXT("real_swd_skill_timeline_damage_or_recovery_check_failed"));return; }
        UnitSingleStartHP=S.HP;UnitGo(UnitSkillSinglePrimary,Now);break;
    }
    case UnitSkillSinglePrimary:
    {
        const auto& Primary=Player->GetMeleeCombatState().Action;
        if (!bUnitSingleInputIssued && Player->CanStartAttack() && UnitPulse(EKeys::J,Now))
        { bUnitSingleInputIssued=true;UnitSingleRequestedAt=Now; }
        if (!UnitSinglePrimaryId && bUnitSingleInputIssued && Primary.Active && Primary.Start>=UnitSingleRequestedAt)
        {
            if (Primary.Stage!=0 || Primary.StartedAirborne) { UnitFail(TEXT("skill_did_not_clear_chain_for_single_ground_stage_one"));return; }
            UnitSinglePrimaryId=Primary.AttackId;
        }
        if (!UnitSinglePrimaryId && bUnitSingleInputIssued && Now-UnitSingleRequestedAt>1.0)
        { UnitFail(TEXT("single_normal_j_after_skill_not_accepted"));return; }
        if (UnitSinglePrimaryId && (Primary.AttackId!=UnitSinglePrimaryId || Primary.Stage!=0))
        { UnitFail(TEXT("single_j_after_skill_started_additional_chain_action"));return; }
        if (UnitSinglePrimaryId && !Primary.Active && Player->AttackTime<=0)
        {
            UnitSingleEndHP=S.HP;
            if (Now<Primary.End || Knight->bDead || S.HP<=0 || S.HP>26./1.45+.05
                || FMath::Abs((UnitSingleStartHP-S.HP)-26./1.45)>.05)
            { UnitFail(TEXT("single_real_j_after_skill_did_not_leave_natural_air_finisher"));return; }
            UnitAirStartHP=float(S.HP);UnitGo(UnitTakeoff,Now);
        }
        break;
    }
    case UnitTakeoff:
        if (Player->CanStartAttack()&&Player->JumpHeight<=0&&UnitPulse(EKeys::SpaceBar,Now)) UnitGo(UnitDescend,Now);
        break;
    case UnitDescend:
        if (Player->JumpHeight>0&&Player->JumpHeight<=75&&Player->GetVerticalVelocity()<0
            && Player->CanStartAttack()&&UnitPulse(EKeys::J,Now)) UnitGo(UnitAirAction,Now);
        break;
    case UnitAirAction:
        bUnitAirAccepted |= Player->IsCurrentPrimaryAirborne()&&Player->ComboStage==1&&Player->AttackTime>0;
        bUnitLandingContinued |= bUnitAirAccepted&&Player->JumpHeight<=0&&Player->IsCurrentPrimaryAirborne()&&Player->AttackTime>0;
        if (bUnitAirAccepted&&!bUnitAirExtraIssued&&Player->JumpHeight>0&&UnitPulse(EKeys::J,Now))
        { bUnitAirExtraIssued=true;UnitAirExtraAt=Now;UnitAirExtraAttackTime=Player->AttackTime;UnitAirExtraProgress=Player->GetActionProgress(); }
        if (bUnitAirExtraIssued&&Now>UnitAirExtraAt&&Player->IsCurrentPrimaryAirborne())
            bUnitAirExtraRejected |= Player->AttackTime<=UnitAirExtraAttackTime+.005f&&Player->GetActionProgress()>=UnitAirExtraProgress;
        if (bUnitAirAccepted&&Player->JumpHeight<=0&&Player->AttackTime<=0)
        {
            Check(TEXT("air_primary_rejected_second_start_and_continued_after_landing"),bUnitAirExtraIssued&&bUnitAirExtraRejected&&bUnitLandingContinued);
            const bool Killed=UnitAirStartHP>0&&Knight->bDead&&S.HP==0&&Game->bRoomCleared;
            Check(TEXT("stone_naturally_killed_by_accepted_air_primary"),Killed);
            if (!Killed) { UnitFail(TEXT("real_air_finisher_missed_or_did_not_kill"));return; }
            UnitRewardCount=Game->Pickups.Num();UnitCoinsAtDeath=Player->Coins;UnitLeftStartX=float(P.X);UnitGo(UnitLeftWalk,Now);
        }
        break;
    case UnitLeftWalk:
        if (P.X>UnitLeftStartX-90) UnitMove(-1,0);
        else
        {
            Check(TEXT("normal_left_walk_changes_position_and_facing"),P.X<UnitLeftStartX-80&&Player->Facing<0);
            UnitGo(UnitGroundFollow,Now);
        }
        break;
    case UnitGroundFollow:
        if (!bUnitGroundPrimary&&Player->ComboStage>0&&Player->AttackTime>0&&!Player->IsCurrentPrimaryAirborne()&&Player->JumpHeight<=0)
            bUnitGroundPrimary=true;
        if (!bUnitGroundPrimary&&Player->CanStartAttack()) UnitPulse(EKeys::J,Now);
        if (bUnitGroundPrimary&&Player->AttackTime<=0)
        {
            Check(TEXT("ground_primary_after_landed_air_action_completion"),bUnitLandingContinued&&Player->JumpHeight<=0);
            int32 Coins=0,Potions=0,Axes=0;
            for (const auto& Pickup:Game->Pickups)
            { Coins+=Pickup.Kind==TEXT("coin");Potions+=Pickup.Kind==TEXT("potion");Axes+=Pickup.Kind==TEXT("axe"); }
            Check(TEXT("real_death_single_receipt_and_stable_prototype_rewards"),S.RewardClaimed&&Knight->bDeathReported&&Knight->bDead
                &&Game->Pickups.Num()==UnitRewardCount&&UnitRewardCount==3&&Coins==1&&Potions==1&&Axes==1&&Player->Coins==UnitCoinsAtDeath);
            Check(TEXT("first_unit_completed_within_30s"),Elapsed<30.0);
            UnitReleaseInputs();
            if (bFirstUnitExplore)
            { bUnitCombatCompleted=true;UnitGo(UnitExploreWalkToU,Now); }
            else { UnitGo(UnitDone,Now);FinishAudioCapture(); }
        }
        break;
    case UnitExploreWalkToU:
        if (!HUD || !Game->bRoomCleared || !Knight->bDead || Player->AttackTime>0 || Player->JumpHeight>0
            || Player->GetWeaponSkillAction().Active || !Player->CanStartAttack())
        { UnitFail(TEXT("explore_requires_real_clear_and_completed_actions"));return; }
        if (P.X>ExploreU().X+16.) UnitMove(-1,0);
        else
        {
            UnitMove(0,0);
            if (HUD->GetExplorationMemoryAt(ExploreU())!=1. || HUD->GetExplorationMemoryAt(ExploreR())!=1.) break;
            UnitExploreRevealedCount=HUD->GetExploredVertexCount();
            UnitExploreOldUMemory=HUD->GetExplorationMemoryAt(ExploreU());UnitExploreOldRMemory=HUD->GetExplorationMemoryAt(ExploreR());
            const bool Revealed=Game->RoomNumber==UnitExploreRoom&&HUD->GetExplorationRoomNumber()==UnitExploreRoom
                &&HUD->GetExplorationResetSerial()==UnitExploreResetSerial&&bUnitExploreMemoryMonotonic
                &&UnitExploreRevealedCount>UnitExploreInitialCount&&P.X<=ExploreU().X+16.&&Player->Facing<0
                &&HUD->GetCurrentVisibilityAt(ExploreU())==1.&&HUD->GetCurrentVisibilityAt(ExploreR())==1.;
            UnitExploreSample(TEXT("normal_a_revealed_u_and_r"),Game,Player);
            Check(TEXT("explore_normal_a_revealed_u_r_and_memory_grew"),Revealed);
            if (!Revealed) { UnitFail(TEXT("normal_a_did_not_reveal_strict_world_witnesses"));return; }
            UnitGo(UnitExploreRetreat,Now);
        }
        break;
    case UnitExploreRetreat:
        if (!HUD || Game->RoomNumber!=UnitExploreRoom || !Game->bRoomCleared)
        { UnitFail(TEXT("explore_room_changed_before_normal_exit"));return; }
        if (P.X<-300.) UnitMove(1,0);
        else
        {
            UnitMove(0,0);UnitExploreRetreatCount=HUD->GetExploredVertexCount();
            const bool Kept=HUD->GetExplorationRoomNumber()==UnitExploreRoom&&HUD->GetExplorationResetSerial()==UnitExploreResetSerial
                &&bUnitExploreMemoryMonotonic&&UnitExploreRetreatCount>=UnitExploreRevealedCount
                &&P.X>=-300.&&P.X<-280.&&Player->Facing>0
                &&HUD->GetCurrentVisibilityAt(ExploreU())==0.&&HUD->GetExplorationMemoryAt(ExploreU())==UnitExploreOldUMemory
                &&HUD->GetExplorationMemoryAt(ExploreR())==UnitExploreOldRMemory;
            const bool Unvisited=HUD->GetExplorationMemoryAt(ExploreV())==0.&&HUD->GetCurrentVisibilityAt(ExploreV())==0.;
            UnitExploreSample(TEXT("normal_d_retreat_memory_vs_unknown"),Game,Player);
            Check(TEXT("explore_normal_d_retreat_kept_u_memory_outside_visibility"),Kept);
            Check(TEXT("explore_unvisited_v_stayed_unknown_through_retreat"),Unvisited);
            if (!Kept || !Unvisited) { UnitFail(TEXT("retreat_lost_memory_or_revealed_unvisited_v"));return; }
            UnitGo(UnitExploreWalkToExit,Now);
        }
        break;
    case UnitExploreWalkToExit:
        if (!HUD || Game->RoomNumber!=UnitExploreRoom || !Game->bRoomCleared || !Knight->bDead
            || !bUnitExploreMemoryMonotonic || HUD->GetExplorationResetSerial()!=UnitExploreResetSerial)
        { UnitFail(TEXT("explore_old_room_state_changed_before_exit"));return; }
        if (P.X<=610.) UnitMove(1,0);
        else
        {
            UnitMove(0,0);
            if (FMath::Abs(P.Y)>=100. || Player->JumpHeight>0 || !Player->CanStartAttack())
            { UnitFail(TEXT("normal_walk_did_not_reach_legal_old_exit"));return; }
            if (UnitPulse(EKeys::E,Now))
            {
                UnitExploreExitInputAt=Now;UnitExploreExitHP=Player->Health;UnitExploreExitCoins=Player->Coins;
                UnitExploreSample(TEXT("old_exit_before_fresh_normal_e"),Game,Player);
                UnitGo(UnitExploreAwaitRoom,Now);
            }
        }
        break;
    case UnitExploreAwaitRoom:
    {
        UnitMove(0,0);
        if (Game->RoomNumber==UnitExploreRoom)
        {
            if (Now-UnitExploreExitInputAt>2.) { UnitFail(TEXT("fresh_normal_e_did_not_change_real_room"));return; }
            break;
        }
        if (Game->RoomNumber!=UnitExploreRoom+1 || UnitExplorePlayer.Get()!=Player)
        { UnitFail(TEXT("normal_exit_changed_unexpected_room_or_character"));return; }
        if (!HUD || HUD->GetExplorationRoomNumber()!=Game->RoomNumber || HUD->GetExplorationResetSerial()<=UnitExploreResetSerial)
        {
            if (Now-UnitExploreExitInputAt>2.) { UnitFail(TEXT("actual_next_room_hud_reset_not_observed"));return; }
            break;
        }
        const bool Changed=UnitExploreExitInputAt>=0&&Now>UnitExploreExitInputAt
            &&HUD->GetExplorationResetSerial()==UnitExploreResetSerial+1&&FMath::Abs(P.X+580.)<1.e-5&&FMath::Abs(P.Y)<1.e-5
            &&Player->Health==UnitExploreExitHP&&Player->Coins==UnitExploreExitCoins;
        // U is just inside the new spawn's visibility ellipse, so it must match
        // that fresh reveal rather than zero. R is a separate exact grid vertex
        // outside the ellipse and is required to return strictly to zero.
        const double FreshU=DungeonExploration::FExploration::VisibilityAt({ExploreU().X,ExploreU().Y},{P.X,P.Y});
        const bool Reset=UnitExploreOldUMemory==1.&&UnitExploreOldRMemory==1.&&FreshU>0.&&FreshU<1.
            &&HUD->GetCurrentVisibilityAt(ExploreR())==0.&&HUD->GetExplorationMemoryAt(ExploreR())==0.
            &&FMath::Abs(HUD->GetExplorationMemoryAt(ExploreU())-FreshU)<1.e-9
            &&HUD->GetExploredVertexCount()>0&&HUD->GetExploredVertexCount()<UnitExploreRetreatCount;
        UnitExploreSample(TEXT("actual_next_room_first_hud_reset"),Game,Player);
        Check(TEXT("explore_fresh_e_changed_room_and_hud_reset_once"),Changed);
        Check(TEXT("explore_new_room_cleared_r_and_u_matches_fresh_visibility"),Reset);
        if (!Changed || !Reset) { UnitFail(TEXT("new_room_retained_old_memory_or_changed_character_resources"));return; }
        UnitGo(UnitExploreNewRoomHold,Now);break;
    }
    case UnitExploreNewRoomHold:
        UnitMove(0,0);
        if (!HUD || Game->RoomNumber!=UnitExploreRoom+1 || HUD->GetExplorationRoomNumber()!=Game->RoomNumber
            || HUD->GetExplorationResetSerial()!=UnitExploreResetSerial+1 || HUD->GetExplorationMemoryAt(ExploreR())!=0.
            || FMath::Abs(P.X+580.)>=1.e-5 || FMath::Abs(P.Y)>=1.e-5 || Player->Health!=UnitExploreExitHP)
        { UnitFail(TEXT("new_room_idle_observation_changed_reset_witness"));return; }
        if (Now-UnitPhaseAt>=1.)
        {
            UnitExploreSample(TEXT("new_room_idle_hold_complete"),Game,Player);
            Check(TEXT("explore_completed_within_45s"),Elapsed<45.);
            UnitReleaseInputs();UnitGo(UnitDone,Now);FinishAudioCapture();
        }
        break;
    default: UnitFail(TEXT("invalid_first_unit_stage"));return;
    }
}
#include "DungeonEquipmentProof.inl"
#include "DungeonArmorLayerProof.inl"
#include "DungeonRangedProof.inl"
#include "DungeonSceneProof.inl"
#include "DungeonXBWReloadSocketProof.inl"
#include "DungeonXBWArmorSocketProof.inl"
#include "DungeonActionAudioCaptureProbe.inl"

void ADungeonContentProbe::Save()
{
    // CaptureStop/audio stop already happened; draining disk writes cannot extend recorded audio time.
    const bool AsyncPixelWritesRequested=FParse::Param(FCommandLine::Get(),TEXT("DungeonAsyncLosslessCapture"));
    const bool AsyncPixelWritesFlushed=FlushFastLosslessProofScreenshots();
    const auto Required = RequiredProofChecks(bFirstUnit,bFirstUnitSkill,bFirstUnitExplore,bEquipmentProof,bArmorLayerProof,bArmorComboProof,bRangedProof,bArmorSleevesProof,bXBWReadyProof,bXBWHeldIdentityProof,bXBWPrimaryProof,bSceneProof,bXBWReloadSocketProof,bXBWArmorSocketProof);
    bool Passed = Results.Num() == Required.Num();
    for (const auto& Value:Results) Passed &= Value->AsObject()->GetBoolField(TEXT("passed"));
    for (const FString& Name:Required)
    {
        int32 Count = 0;
        for (const auto& Value:Results) if (Value->AsObject()->GetStringField(TEXT("name"))==Name) ++Count;
        Passed &= Count==1;
    }
    auto Report = MakeShared<FJsonObject>();
    const bool Candidates=FParse::Param(FCommandLine::Get(),TEXT("DungeonCandidateSprites"));
    const FString Visual = Candidates
        ? (bFirstUnit?TEXT("Candidate round-helmet armored hero and stone-knight preview requested. Explore records actual last-draw texture paths and sprite sizes together with world reveal, memory and room changes. Full action coverage, visual layering and audio acceptance require separate review; this proof does not approve every visual state.")
            :TEXT("Candidate SWD hero preview requested; GSW/SPR retain placeholder art. Rendered animation/opacity/mirroring awaits visual review."))
        :TEXT("Existing prototype placeholder visuals.");
    const FString FixtureScope=bEquipmentProof?TEXT("Opt-in real inventory adapter fixture: starter plus explicitly registered QA ground sources; normal K/E/Q/Right/Enter requests, .35/.50 commits, full-slot selection, old-item drop/re-pick. Does not certify production loot/shop provenance, armor-layer art, enemy combat or disk save/load. "):bFirstUnitExplore?TEXT("Independent Explore profile: original 19-check normal-input SWD skill encounter, then normal A/D exploration and fresh E at the actual old exit; seven additional world-memory/reset checks and a 45s overall deadline. Combat retains its 30s deadline. Explicit QA light-armor action; prototype rewards, actual acquisition and save/load are not exercised. "):(bFirstUnitSkill?TEXT("State-driven QA single stone-knight encounter: normal K SWD skill, one ground J then original natural air finisher; explicit QA light-armor action. Prototype death rewards; actual acquisition and save/load are not exercised. "):(bFirstUnit?TEXT("State-driven QA single stone-knight development encounter with normal controller inputs and explicit QA light-armor action. Prototype death rewards; actual acquisition and save/load are not exercised. "):TEXT("QA normal key edges: three melee chains, one air primary and positive Y movement. ")));
    Report->SetStringField(TEXT("scope"),bArmorLayerProof?TEXT("Opt-in frozen idle/walk/P1 component preview: real QA ground sources, normal E/Enter .50 armor commits, A/D fullwalk loops and ten normal J first-stage attacks; records actual drawn layer paths. Missing clips still old candidate, not all-state/20-combination/enemy/persistence acceptance. Game-only main-submix recording; analysis is not listening acceptance."):FixtureScope+Visual+TEXT(" Game-only main-submix recording; signal analysis is not listening/mix or full-content acceptance."));
    Report->SetStringField(TEXT("profile"),bArmorLayerProof?TEXT("armor_idle_primary1_layers_normal_inputs"):bEquipmentProof?TEXT("equipment_adapter_sources_and_normal_inputs"):bFirstUnitExplore?TEXT("first_unit_swd_skill_lgt_stone_explore"):(bFirstUnitSkill?TEXT("first_unit_swd_skill_lgt_stone"):(bFirstUnit?TEXT("first_unit_swd_lgt_stone"):TEXT("melee_benchmark"))));
    Report->SetBoolField(TEXT("armor_layer_proof_requested"),bArmorLayerProof);
    Report->SetBoolField(TEXT("armor_combo_proof_requested"),bArmorComboProof);
    Report->SetBoolField(TEXT("armor_sleeves_proof_requested"),bArmorSleevesProof);
    Report->SetBoolField(TEXT("armor_sleeves_preview_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorSleevesPreview")));
    Report->SetBoolField(TEXT("ranged_weapons_proof_requested"),bRangedProof);
    Report->SetBoolField(TEXT("xbw_ready_proof_requested"),bXBWReadyProof);
    Report->SetBoolField(TEXT("xbw_held_identity_proof_requested"),bXBWHeldIdentityProof);
    Report->SetBoolField(TEXT("xbw_primary_body_proof_requested"),bXBWPrimaryProof);
    Report->SetBoolField(TEXT("scene_exploration_proof_requested"),bSceneProof);
    Report->SetBoolField(TEXT("xbw_reload_socket_proof_requested"),bXBWReloadSocketProof);
    Report->SetBoolField(TEXT("xbw_armor_socket_proof_requested"),bXBWArmorSocketProof);
    Report->SetBoolField(TEXT("xbw_reload_body_preview_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonXBWReloadBodyPreview")));
    Report->SetNumberField(TEXT("capture_frame_cap_fps"),(bXBWReloadSocketProof||bXBWArmorSocketProof)?60:30);
    Report->SetBoolField(TEXT("native_async_capture_requested"),AsyncPixelWritesRequested);
    Report->SetBoolField(TEXT("native_async_capture_writes_flushed"),AsyncPixelWritesFlushed);
    Report->SetBoolField(TEXT("native_async_flush_after_audio_stop"),bAudioStopRequested&&CaptureStopWall>0);
    Report->SetBoolField(TEXT("weapon_body_preview_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonWeaponBodyPreview")));
    if(bArmorComboProof)
    {
        Report->SetStringField(TEXT("profile"),TEXT("armor_idle_walk_primary123_layers_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("Opt-in native idle/walk/P1/P2/P3 partial armor components. Real QA armor ground sources, normal E/Enter .50 commits and ten normal J buffered three-stage chains, both facings; actual drawn layer paths and adjacent action End/Start equality. ROB long sleeves, footlock, other clips, full20 combinations, enemy/disk save and listening acceptance remain pending."));
    }
    if(bSceneProof)
    {
        Report->SetStringField(TEXT("profile"),TEXT("scene_exploration_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("Genuine Scene Run initialization; only at time0 disable autonomous attack starts for the unique Knight; tracking movement remains active in this normal-input traversal fixture. Real Enter/WASD/J/E/Escape/freshEnter exercise wall, bypass, no-income survey, fog memory and same-Run room transfer. No live state repairs, D07 graph, D08 hidden rewards, D13 or final art/AI acceptance."));
        Report->SetStringField(TEXT("scene_failure"),UnitFailure);
    }
    if(bXBWReloadSocketProof)
    {
        Report->SetStringField(TEXT("profile"),TEXT("xbw_reload_socket_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("QA initial start gate, single real Ammo1 source and two stationary target fixtures; all subsequent Enter/E/WASD/J/T/Q use normal inputs. Native primary6 and reload4 both facings, real Actor socket/world snapshots, loaded/empty/cancel/restart and instance retention. Real delta60fps cap, no slow motion. Four armor/fullstate/20mix/production loot/D13/listening and full weapon remain unfulfilled."));
        Report->SetStringField(TEXT("xbw_reload_socket_failure"),UnitFailure);
    }
    if(bXBWArmorSocketProof)
    {
        Report->SetStringField(TEXT("profile"),TEXT("xbw_four_armor_socket_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("QA phase0 initializes one real Run, one Ammo1 XBW source, four unenchanted armor sources and two stationary HP2000 targets. All later changes use normal Enter/E/Tab/A/D/J. Real .35 weapon and .50 armor commits, old armor retention, both facings of native ready6/primary6/reload4 exact six layers and immutable actual hand emission/hit/stop/spend/refill. At most eight mandatory plus two extra shots,55s wall deadline, real delta60fps cap. Four-armor walk/skill/air/coverage,20mix,formal loot,D13,listening and full units remain unfulfilled."));
        Report->SetStringField(TEXT("xbw_armor_socket_failure"),UnitFailure);
    }
    if(bRangedProof)
    {
        Report->SetStringField(TEXT("profile"),bXBWPrimaryProof?TEXT("xbw_authored_primary_body_normal_inputs"):bXBWHeldIdentityProof?TEXT("xbw_held_body_identity_normal_inputs"):bXBWReadyProof?TEXT("xbw_ready_body_normal_inputs"):TEXT("ranged_spear_adapter_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("Explicit QA sources and authored stationary target initial positions/HP; normal controller acquisition, switching, XBW/STF main/skill and SPR skill. Actual inventory instances, world projectiles/fireline/burn and readonly HUD audio requests. Production loot, authored sockets/art and listening/mix acceptance, all-state armor and disk save remain pending."));
        auto Ranged=MakeShared<FJsonObject>();
        Ranged->SetStringField(TEXT("failure"),UnitFailure);
        Ranged->SetNumberField(TEXT("final_phase"),RangedProof.Phase);
        Ranged->SetBoolField(TEXT("direct_attack_hit_or_resource_edit_during_proof"),false);
        Ranged->SetBoolField(TEXT("production_loot_art_audio_disk_accepted"),false);
        Report->SetObjectField(TEXT("ranged_weapons"),Ranged);
        if(bXBWReadyProof)
        {
            Report->SetStringField(TEXT("scope"),TEXT("Actual QA source E .35 acquisition, normal A/D and six-frame XBW two-hand ready idle both facings; actual far/weapon/support/near draw stack. Normal J real projectile/hit and complete1.10 reload retain existing combat with unfinished attack/reload art. No four-armor, authored world muzzle, footlock, production loot/D13 or listening acceptance."));
            Ranged->SetStringField(TEXT("ready_manifest_sha256"),TEXT("21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813"));
            Ranged->SetNumberField(TEXT("ready_right_frame_mask"),RangedProof.ReadyFrameMask[0]);
            Ranged->SetNumberField(TEXT("ready_left_frame_mask"),RangedProof.ReadyFrameMask[1]);
            Ranged->SetNumberField(TEXT("held_reload_frame_mask"),RangedProof.HeldReloadFrameMask);
            Ranged->SetBoolField(TEXT("held_firing_seen"),RangedProof.HeldFiringSeen);
            Ranged->SetNumberField(TEXT("primary_actual_frame_mask"),RangedProof.PrimaryFrameMask);
            Ranged->SetNumberField(TEXT("primary_actual_phase_mask"),RangedProof.PrimaryPhaseMask);
            Ranged->SetBoolField(TEXT("primary_clock_stack_valid"),RangedProof.PrimaryClockStackValid);
            Ranged->SetBoolField(TEXT("held_action_identity_valid"),RangedProof.HeldActionIdentityValid);
            Ranged->SetBoolField(TEXT("firing_reload_body_is_ready_pose_placeholder"),!bXBWPrimaryProof);
            Ranged->SetBoolField(TEXT("firing_body_is_ready_pose_placeholder"),!bXBWPrimaryProof);
            Ranged->SetBoolField(TEXT("reload_body_is_ready_pose_placeholder"),true);
        }
    }
    if(bArmorSleevesProof)
    {
        Report->SetStringField(TEXT("profile"),TEXT("armor_idle_walk_primary123_sleeves_normal_inputs"));
        Report->SetStringField(TEXT("scope"),TEXT("Opt-in native P2/P3 body repartition and actual ROB cloth cuff near track. Same normal-input36 chain/equipment checks plus two actual drawn-stack/facing/six-pose near-order checks. Original common body reconstructs unchanged; P3 source has exposed cuff skin. Not complete long sleeves, footlock/fullstate/20 combinations/enemy/production loot/disk or listening acceptance."));
    }
    Report->SetBoolField(TEXT("armor_layer_preview_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonArmorLayerPreview")));
    if(bArmorLayerProof)
    {
        auto Armor=MakeShared<FJsonObject>();Armor->SetStringField(TEXT("failure"),UnitFailure);
        Armor->SetNumberField(TEXT("final_variant"),ArmorVariant);Armor->SetNumberField(TEXT("final_phase"),UnitPhase);
        Armor->SetStringField(TEXT("idle_manifest_sha256"),TEXT("f0cd3c72a1fe0b7ac3ad7416ddde44a0f89dd6f0d5ddc25320aec3c184769ab3"));
        Armor->SetStringField(TEXT("primary1_manifest_sha256"),TEXT("6369db09edb37e08256ef2fe22763846adb2802efc4ea8bdf8ad30a4a8b8ca70"));
        Armor->SetStringField(TEXT("walk_manifest_sha256"),TEXT("fd02fa5de2eb23efba31a0c60167bcaf7482a91666959caf2001949fffae3e58"));
        if(bArmorComboProof)
        {
            Armor->SetStringField(TEXT("primary2_manifest_sha256"),TEXT("1372c8ea3cb5a113dc9e8315a7b5cf51ebafe50359d96d42878a3c70891fa46e"));
            Armor->SetStringField(TEXT("primary3_manifest_sha256"),TEXT("e97f2958f624e8d27c0942931e48a293c5bee6b33ebfd42148956dfd3f288497"));
            if(bArmorSleevesProof)
            {
                Armor->SetStringField(TEXT("primary2_manifest_sha256"),TEXT("04d9dce4c7d1aff12bea9873681c9e759e9032544ca37c7abd33f01939fbb225"));
                Armor->SetStringField(TEXT("primary3_manifest_sha256"),TEXT("3f1dc1ea892ea82535263f0ad170a39cee62af3d892e422dd2628f99b6db4c5c"));
                Armor->SetStringField(TEXT("near_draw_order"),TEXT("actual body_far, armor_front, successful independent sword, armor_near, body_near"));
            }
        }
        Armor->SetBoolField(TEXT("full_armor_all_state_accepted"),false);Report->SetObjectField(TEXT("armor_layers"),Armor);
    }
    Report->SetBoolField(TEXT("first_unit_skill_requested"),bFirstUnitSkill);
    Report->SetBoolField(TEXT("equipment_adapter_requested"),bEquipmentProof);
    Report->SetBoolField(TEXT("first_unit_explore_requested"),bFirstUnitExplore);
    if(bEquipmentProof)
    {
        auto Equipment=MakeShared<FJsonObject>();
        Equipment->SetStringField(TEXT("failure"),UnitFailure);
        Equipment->SetNumberField(TEXT("final_phase"),UnitPhase);
        Equipment->SetStringField(TEXT("source_scope"),TEXT("Explicit QA RegisterEquipmentSource fixtures; actual inventory/world ownership transfer, not N03/N04 production loot"));
        Equipment->SetStringField(TEXT("input_source"),TEXT("normal controller K/E/Q/Right/Enter edges and A/D walking; no direct transfer, confirm or switch API calls"));
        Equipment->SetBoolField(TEXT("disk_save_load_exercised"),false);
        Equipment->SetBoolField(TEXT("armor_layers_accepted"),false);
        Report->SetObjectField(TEXT("equipment_adapter"),Equipment);
    }
    TArray<TSharedPtr<FJsonValue>> RequiredJson;
    for (const auto& Name:Required) RequiredJson.Add(MakeShared<FJsonValueString>(Name));
    Report->SetArrayField(TEXT("required_check_names"),RequiredJson);
    if (bFirstUnit)
    {
        auto Unit=MakeShared<FJsonObject>();
        Unit->SetStringField(TEXT("final_stage"),UnitPhaseName(UnitPhase));
        Unit->SetStringField(TEXT("failure"),UnitFailure);
        Unit->SetNumberField(TEXT("stage_entered_sim_s"),UnitPhaseAt);
        Unit->SetBoolField(TEXT("qa_api_light_armor_change"),true);
        Unit->SetStringField(TEXT("weapon_source"),TEXT("normal opening sword alias maps to SWD001; no QA weapon replacement"));
        Unit->SetStringField(TEXT("reward_scope"),bFirstUnitExplore
            ?TEXT("existing prototype coin/potion/axe only; natural death and post-death attack observed; E is requested only at the distant legal exit, not at loot. No pickup/healing/source-chain acceptance")
            :TEXT("existing prototype coin/potion/axe only; observe natural death and normal post-death attack without invoking death handler again; no E pickup, healing, or source-chain acceptance"));
        Unit->SetBoolField(TEXT("actual_acquisition_exercised"),false);
        Unit->SetBoolField(TEXT("save_load_exercised"),false);
        Unit->SetStringField(TEXT("trace_scope"),TEXT("post-batch actor/driver state observations; exact deadlines read from kernel; not a fabricated event stream, may miss sub-frame transitions"));
        if (bFirstUnitExplore)
        {
            auto Explore=MakeShared<FJsonObject>();
            Explore->SetStringField(TEXT("input_source"),TEXT("normal controller A to U, D to retreat and old exit, one fresh E; no teleport, direct NextRoom, HP edit or exploration writes"));
            Explore->SetStringField(TEXT("memory_source"),TEXT("read-only getters of the same world-grid state used by actual DrawHUD; exact grid vertices U(-1158,28), V(1210,28), R(-1222,28) for current shared room bounds"));
            Explore->SetNumberField(TEXT("combat_deadline_wall_s"),30.);Explore->SetNumberField(TEXT("overall_deadline_wall_s"),45.);
            Explore->SetNumberField(TEXT("audio_preallocation_s"),64.);
            Explore->SetBoolField(TEXT("combat_completed_before_exploration"),bUnitCombatCompleted);
            Explore->SetNumberField(TEXT("initial_room"),UnitExploreRoom);
            Explore->SetNumberField(TEXT("initial_reset_serial"),double(UnitExploreResetSerial));
            Explore->SetNumberField(TEXT("initial_explored_vertex_count"),UnitExploreInitialCount);
            Explore->SetNumberField(TEXT("revealed_explored_vertex_count"),UnitExploreRevealedCount);
            Explore->SetNumberField(TEXT("retreat_explored_vertex_count"),UnitExploreRetreatCount);
            Explore->SetBoolField(TEXT("same_room_explored_count_was_monotonic"),bUnitExploreMemoryMonotonic);
            Explore->SetNumberField(TEXT("fresh_exit_e_requested_sim_s"),UnitExploreExitInputAt);
            Explore->SetStringField(TEXT("reset_geometry"),TEXT("actual next-room spawn is (-580,0); U lies inside its 620x280 visibility ellipse and must match fresh reveal, while R lies outside and must be exactly zero after previously being one"));
            Explore->SetArrayField(TEXT("samples"),UnitExploreSamples);
            TArray<FString> TexturePaths=UnitRenderedTexturePaths.Array();TexturePaths.Sort();
            TArray<TSharedPtr<FJsonValue>> TextureJson;
            for (const FString& Path:TexturePaths) TextureJson.Add(MakeShared<FJsonValueString>(Path));
            Explore->SetArrayField(TEXT("actual_rendered_player_texture_paths"),TextureJson);
            Explore->SetStringField(TEXT("visual_acceptance_limit"),TEXT("Actual last-draw texture paths and sizes are observations of the round-helmet character candidate during reveal, exploration memory and room changes. Full action coverage, visual layering and sound/listening acceptance require separate review; passing this proof does not approve all states."));
            Unit->SetObjectField(TEXT("exploration"),Explore);
        }
        if (bFirstUnitSkill)
        {
            auto Skill=MakeShared<FJsonObject>();
            Skill->SetStringField(TEXT("input_source"),TEXT("normal controller K edge; extra fresh K during real recovery; no direct TryBeginWeaponSkill call"));
            Skill->SetNumberField(TEXT("requested_at_sim_s"),UnitSkillRequestedAt);Skill->SetNumberField(TEXT("action_id"),double(UnitSkillId));
            Skill->SetNumberField(TEXT("start_sim_s"),UnitSkillStart);Skill->SetNumberField(TEXT("lock_at_sim_s"),UnitSkillLockAt);
            Skill->SetNumberField(TEXT("active_at_sim_s"),UnitSkillActiveAt);Skill->SetNumberField(TEXT("active_end_sim_s"),UnitSkillActiveEnd);
            Skill->SetNumberField(TEXT("full_end_sim_s"),UnitSkillEnd);Skill->SetNumberField(TEXT("observed_completed_sim_s"),UnitSkillCompletedAt);
            Skill->SetNumberField(TEXT("cooldown_deadline_sim_s"),UnitSkillCooldownDeadline);
            Skill->SetNumberField(TEXT("extra_fresh_k_requested_sim_s"),UnitSkillExtraAt);
            Skill->SetBoolField(TEXT("extra_fresh_k_rejected_same_action"),bUnitSkillExtraRejected);
            Skill->SetNumberField(TEXT("knight_hp_before_skill"),UnitSkillStartHP);Skill->SetNumberField(TEXT("knight_hp_after_skill"),UnitSkillEndHP);
            Skill->SetNumberField(TEXT("hp_decrease_observation_count"),UnitSkillDamageObservations);
            Skill->SetStringField(TEXT("damage_observation_scope"),TEXT("actual post-batch driver HP deltas during the isolated skill; not a fabricated hit-receipt count or sample-accurate event stream"));
            Skill->SetNumberField(TEXT("single_ground_primary_action_id"),double(UnitSinglePrimaryId));
            Skill->SetNumberField(TEXT("knight_hp_after_single_ground_primary"),UnitSingleEndHP);
            Unit->SetObjectField(TEXT("swd_skill"),Skill);
        }
        const auto Controller=UGameplayStatics::GetPlayerController(this,0);
        const auto HUD=Controller?Cast<ADungeonHUD>(Controller->GetHUD()):nullptr;
        Unit->SetBoolField(TEXT("audio_play_request_counter_available"),HUD!=nullptr);
        if (HUD)
        {
            auto Counts=MakeShared<FJsonObject>();
            for (const FString Cue:{TEXT("AWAKE"),TEXT("ARMOR_SCRAPE"),TEXT("CHARGE_BRAKE"),TEXT("FRACTURE"),TEXT("impact")})
                Counts->SetNumberField(Cue,HUD->GetStoneAudioPlayRequests(Cue));
            Unit->SetObjectField(TEXT("audio_play_request_counts"),Counts);
        }
        Unit->SetStringField(TEXT("audio_play_request_counts_scope"),TEXT("HUD sound lookup plus PlaySound2D requests observed at report time, possibly after export wait; not playback completion, WAV evidence or listening acceptance; no mandatory count threshold"));
        Report->SetObjectField(TEXT("first_unit"),Unit);
    }
    Report->SetBoolField(TEXT("passed"),Passed);
    Report->SetBoolField(TEXT("candidate_sprites_requested"),FParse::Param(FCommandLine::Get(),TEXT("DungeonCandidateSprites")));
    Report->SetArrayField(TEXT("checks"),Results);
    Report->SetArrayField(TEXT("trace"),Trace);
    Report->SetBoolField(TEXT("audio_start_requested"),bAudioStartRequested);
    Report->SetBoolField(TEXT("audio_export_callback_received"),bAudioExportCallbackReceived);
    Report->SetBoolField(TEXT("audio_recorded"),bAudioRecorded);
    Report->SetStringField(TEXT("audio_file"),TEXT("runtime-mix.wav"));
    Report->SetStringField(TEXT("audio_engine_original"),TEXT("runtime-mix-engine-export.wav"));
    Report->SetBoolField(TEXT("audio_header_block_align_repaired"),bHeaderBlockAlignRepaired);
    Report->SetBoolField(TEXT("audio_PCM_payload_unchanged"),bPCMPayloadUnchanged);
    Report->SetStringField(TEXT("audio_source"),TEXT("UE game main output submix only; no microphone, desktop loopback or offline sample assembly"));
    Report->SetStringField(TEXT("audio_failure"),AudioFailure);
    auto Timing = MakeShared<FJsonObject>();
    Timing->SetNumberField(TEXT("capture_start_monotonic_s"),CaptureStartWall);
    Timing->SetNumberField(TEXT("capture_stop_monotonic_s"),CaptureStopWall);
    Timing->SetNumberField(TEXT("requested_audio_wall_duration_s"),CaptureStopWall-CaptureStartWall);
    Timing->SetNumberField(TEXT("fixture_elapsed_wall_s"),Elapsed);
    Timing->SetStringField(TEXT("fixture_clock_source"),TEXT("current monotonic wall time minus actual recording start; prewarm frame DeltaSeconds is not accumulated"));
    Timing->SetNumberField(TEXT("audio_clock_start_s"),AudioClockStart);
    Timing->SetNumberField(TEXT("audio_clock_stop_s"),AudioClockStop);
    Timing->SetNumberField(TEXT("audio_clock_duration_s"),AudioClockStop-AudioClockStart);
    Timing->SetStringField(TEXT("frame_timestamp_source"),TEXT("instant monotonic wall time in screenshot-processed callback; recording origin is set after a separately preserved prewarm screenshot completes; prewarm is excluded"));
    Timing->SetBoolField(TEXT("use_fixed_time_step"),FApp::UseFixedTimeStep());
    Timing->SetArrayField(TEXT("frame_wall_offsets_s"),FrameWallOffsets);
    Timing->SetStringField(TEXT("sync_limit"),TEXT("Game-thread frame/onset request stamps only. Audio-thread start and render latency are not sample-accurate measurements; inspect actual WAV duration and first-frame offset. No audio time stretching."));
    Report->SetObjectField(TEXT("capture_timing"),Timing);
    auto Prewarm = MakeShared<FJsonObject>();
    Prewarm->SetStringField(TEXT("file"),TEXT("prewarm-viewport.png"));
    Prewarm->SetBoolField(TEXT("requested"),bWarmupScreenshotRequested);
    Prewarm->SetBoolField(TEXT("completed_file_received"),bWarmupScreenshotCompleted);
    Prewarm->SetNumberField(TEXT("request_monotonic_s"),WarmupScreenshotRequestedWall);
    Prewarm->SetNumberField(TEXT("complete_monotonic_s"),WarmupScreenshotCompletedWall);
    Prewarm->SetBoolField(TEXT("used_as_recording_frame"),false);
    Prewarm->SetStringField(TEXT("scope"),TEXT("separate startup/readback/PNG warmup evidence; not a recording frame, timestamp, or audio replacement"));
    Report->SetObjectField(TEXT("prewarm_screenshot"),Prewarm);
    auto Controls = MakeShared<FJsonObject>();
    Controls->SetNumberField(TEXT("au_disable_app_volume_at_capture"),DisableAppVolumeAtCapture);
    Controls->SetNumberField(TEXT("primary_volume_at_capture"),PrimaryVolumeAtCapture);
    Controls->SetNumberField(TEXT("primary_volume_at_stop"),PrimaryVolumeAtStop);
    Controls->SetBoolField(TEXT("main_submix_auto_disable_requested"),false);
    Controls->SetBoolField(TEXT("main_submix_auto_disable_request_queued"),bSubmixAutoDisableRequestQueued);
    Controls->SetStringField(TEXT("main_submix_auto_disable_verification"),TEXT("public API queues the instance change; no exported getter/acknowledgement exists. Actual WAV duration remains mandatory evidence against skipped silent buffers."));
    Controls->SetBoolField(TEXT("restore_requested"),bAudioControlsRestoreRequested);
    Controls->SetBoolField(TEXT("app_volume_restored"),bAppVolumeRestored);
    Controls->SetBoolField(TEXT("previous_main_submix_configured_auto_disable"),bPreviousSubmixAutoDisable);
    Controls->SetNumberField(TEXT("previous_au_disable_app_volume"),PreviousDisableAppVolume);
    Controls->SetStringField(TEXT("scope"),TEXT("current isolated QA process only; no user INI or system audio changes; submix instance restore queued"));
    Report->SetObjectField(TEXT("audio_capture_controls"),Controls);
    Report->SetObjectField(TEXT("action_audio_capture"),SerializeActionAudioEvidence());
    FString Json; auto Writer = TJsonWriterFactory<>::Create(&Json);
    FJsonSerializer::Serialize(Report,Writer);
    FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("runtime-report.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    bSaved = true;
}
void ADungeonContentProbe::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bSaved) return;
    if (!bAudioStartRequested)
    {
        // StartPlay may reset the mode after this actor's BeginPlay; keep the
        // QA fixture paused throughout warm-up, then Setup releases it.
        if (auto Game = Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this))) Game->bWaitingForStart = true;
        ++WarmupFrames;
        if (!bWarmupScreenshotRequested && WarmupFrames>=3 && FPlatformTime::Seconds()-WarmupStartWall>=2.0)
        {
            bWarmupScreenshotRequested = true;
            WarmupScreenshotRequestedWall = FPlatformTime::Seconds();
            FScreenshotRequest::RequestScreenshot(Directory/TEXT("prewarm-viewport.png"),false,false,false);
        }
        else if (bWarmupScreenshotRequested && FPlatformTime::Seconds()-WarmupScreenshotRequestedWall>=15.0)
        {
            AudioFailure = TEXT("prewarm_screenshot_timeout_before_recording");
            RestoreAudioControls();
            Save();
            FPlatformMisc::RequestExit(false);
        }
        return;
    }
    if (bAudioStopRequested)
    {
        if (FPlatformTime::Seconds() >= AudioExportDeadlineWall)
        {
            AudioFailure = TEXT("async_WAV_export_timeout");
            RestoreAudioControls();
            Save();
            FPlatformMisc::RequestExit(false);
        }
        return;
    }
    Elapsed = FPlatformTime::Seconds()-CaptureStartWall;
    PollActionAudioEvidence();
    // Preserve a genuine initial idle recording frame before releasing the
    // fixture. This also keeps the first tick's prewarm-inclusive engine delta
    // out of action simulation; recording and timestamps continue normally.
    if (Fixture==-1 && FrameWallOffsets.Num()==0) return;
    if (bXBWArmorSocketProof) { TickXBWArmorSocketProof(); return; }
    if (bSceneProof) { TickSceneProof(); return; }
    if (bXBWReloadSocketProof) { TickXBWReloadSocketProof(); return; }
    if (bRangedProof) { TickRangedProof(); return; }
    if (bArmorLayerProof) { TickArmorLayerProof(); return; }
    if (bEquipmentProof) { TickEquipmentProof(); return; }
    if (bFirstUnit) { TickFirstUnit(); return; }
    if (bGameplayFinished)
    {
        if (Elapsed >= 11.0) FinishAudioCapture();
        return;
    }
    auto Game = Cast<ADungeonGameMode>(UGameplayStatics::GetGameMode(this));
    auto Player = Game ? Game->GetPlayerFighter() : nullptr;
    if (!Player || Game->Enemies.Num()<1) return;
    if (Fixture==-1) Setup(Game,TEXT("WPN-SWD-001"),0);
    if (Elapsed>=4 && Fixture==0) Setup(Game,TEXT("WPN-GSW-001"),1);
    if (Elapsed>=8 && Fixture==1) Setup(Game,TEXT("WPN-SPR-001"),2);
    const auto Pulse = [this](double Start){return Elapsed>=Start && Elapsed<Start+.05;};
    Key(EKeys::J,Pulse(.30)||Pulse(.82)||Pulse(1.35)||Pulse(2.70)
        ||Pulse(4.20)||Pulse(5.33)||Pulse(6.42)||Pulse(8.20)||Pulse(8.55)||Pulse(8.94));
    Key(EKeys::SpaceBar,Pulse(2.50));
    Key(EKeys::W,Elapsed>=3.35 && Elapsed<3.65);
    if (Elapsed>=3.30 && Elapsed<3.35) DepthStart=Player->GetGroundPosition().Y;
    MaxJump=FMath::Max(MaxJump,Player->JumpHeight);
    if (Player->ComboStage>0) Stages |= 1 << (Player->ComboStage-1);
    auto Row=MakeShared<FJsonObject>();
    Row->SetNumberField(TEXT("time"),Elapsed);
    Row->SetStringField(TEXT("weapon"),Player->WeaponId);
    Row->SetNumberField(TEXT("stage"),Player->ComboStage);
    Row->SetStringField(TEXT("phase"),Player->AttackPhase);
    Row->SetNumberField(TEXT("target_hp"),Game->Enemies[0]->Health);
    Row->SetNumberField(TEXT("ground_y"),Player->GetGroundPosition().Y);
    Row->SetNumberField(TEXT("height"),Player->JumpHeight);
    Trace.Add(MakeShared<FJsonValueObject>(Row));
    if (Elapsed>=2.20 && !bSwordChecked)
    {
        Check(TEXT("sword_normal_key_chain_all_three_stages"),Stages==7);
        Check(TEXT("sword_three_hits_total_78_no_duplicate_damage"),FMath::IsNearlyEqual(Game->Enemies[0]->Health,922.f,.01f));
        bSwordChecked=true;
    }
    if (Elapsed>=3.80 && Fixture==0)
    {
        Check(TEXT("jump_apex_matches_630_1800"),MaxJump>109.f && MaxJump<=110.26f);
        Check(TEXT("up_input_increases_ground_y"),Player->GetGroundPosition().Y>DepthStart+60.f);
        Fixture=-2; // Avoid recording the two completed checks again; next fixture starts below.
    }
    if (Fixture==-2 && Elapsed>=4) Setup(Game,TEXT("WPN-GSW-001"),1);
    if (Elapsed>=7.90 && !bHeavyChecked)
    {
        Check(TEXT("greatsword_normal_key_chain_all_three_stages"),Stages==7);
        Check(TEXT("greatsword_three_hits_total_138"),FMath::IsNearlyEqual(Game->Enemies[0]->Health,862.f,.01f));
        bHeavyChecked=true;
    }
    if (Elapsed>=9.70 && !bSpearChecked)
    {
        Check(TEXT("spear_normal_key_chain_all_three_stages"),Stages==7);
        Check(TEXT("spear_nearest_target_three_hits_total_63"),FMath::IsNearlyEqual(Game->Enemies[0]->Health,937.f,.01f));
        bSpearChecked=true;
    }
    if (Elapsed>=10.20) { Key(EKeys::J,false); Key(EKeys::W,false); Key(EKeys::SpaceBar,false); bGameplayFinished=true; }
}
