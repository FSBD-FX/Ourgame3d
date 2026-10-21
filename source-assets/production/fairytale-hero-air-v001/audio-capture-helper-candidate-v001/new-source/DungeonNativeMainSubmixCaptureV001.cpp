#include "DungeonNativeMainSubmixCaptureV001.h"
#include "DungeonContentProbe.h"
#include "AudioDeviceManager.h"
#include "AudioMixerBlueprintLibrary.h"
#include "AudioMixerDevice.h"
#include "AudioThread.h"
#include "Dom/JsonObject.h"
#include "Dom/JsonValue.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Sound/SoundSubmix.h"
#include "UObject/UObjectIterator.h"
#if PLATFORM_WINDOWS
#include "Windows/WindowsHWrapper.h"
#endif

namespace
{
TWeakObjectPtr<UDungeonNativeMainSubmixCaptureV001> ActiveNativeMixCapture;
// The Blueprint writer has one process-global pending export. A failed async
// export must not be abandoned by a second recorder in the same QA process.
bool NativeMixExportPoisonedUntilProcessExit = false;

bool CompleteEarlierAudioCommands()
{
    // StartRecording queues itself to the audio thread; StopRecording is
    // synchronous. A same-frame Abort must retire Start before it drains Stop.
    FAudioCommandFence Fence; Fence.BeginFence(); Fence.Wait(false);
    return Fence.IsFenceComplete();
}
bool SameNativeMixer(Audio::FMixerDevice* Mixer, USoundSubmix* Submix, uint32 DeviceId)
{
    // A default USoundSubmix asset can be shared by multiple devices. Bind the
    // actual device ID too; never let StopRecording fall back to a foreign main.
    return Mixer && Mixer->DeviceID == DeviceId && &Mixer->GetMainSubmixObject() == Submix;
}

const TCHAR* PhaseName(EDungeonNativeMixCapturePhaseV001 P)
{
    using E = EDungeonNativeMixCapturePhaseV001;
    switch(P)
    {
    case E::Idle: return TEXT("Idle"); case E::Arming: return TEXT("Arming"); case E::Recording: return TEXT("Recording");
    case E::ExportPending: return TEXT("ExportPending"); case E::Complete: return TEXT("Complete");
    case E::Aborted: return TEXT("Aborted"); default: return TEXT("Failed");
    }
}
bool ExclusivelyCreateDirectory(const FString& Directory)
{
#if PLATFORM_WINDOWS
    // CREATE_NEW-equivalent directory ownership. Existing topic/version fails;
    // never turn a reused directory into a new capture or delete a failed one.
    return ::CreateDirectoryW(*Directory, nullptr) != 0;
#else
    return false; // This Windows project does not silently weaken exclusivity.
#endif
}
bool WriteNewCanonical(const FString& Filename, const TArray<uint8>& Bytes)
{
#if PLATFORM_WINDOWS
    // UE5.5's generic FILEWRITE_NoReplaceExisting is not implemented by its
    // Windows writer. Match the project's proven screenshot CREATE_NEW policy.
    const HANDLE H = ::CreateFileW(*Filename, GENERIC_WRITE, FILE_SHARE_READ, nullptr,
        CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
    if(H == INVALID_HANDLE_VALUE) return false;
    DWORD Written = 0;
    const bool Wrote = ::WriteFile(H, Bytes.GetData(), DWORD(Bytes.Num()), &Written, nullptr)
        && Written == DWORD(Bytes.Num());
    const bool Flushed = Wrote && ::FlushFileBuffers(H);
    const bool Closed = ::CloseHandle(H) != 0;
    return Wrote && Flushed && Closed; // Partial failure is retained, never retried.
#else
    return false;
#endif
}
}

UWorld* UDungeonNativeMainSubmixCaptureV001::GetWorld() const { return CaptureWorld.Get(); }
bool UDungeonNativeMainSubmixCaptureV001::IsTerminal() const
{
    using E = EDungeonNativeMixCapturePhaseV001;
    return CaptureStatus.Phase == E::Complete || CaptureStatus.Phase == E::Failed || CaptureStatus.Phase == E::Aborted;
}
bool UDungeonNativeMainSubmixCaptureV001::HasOldContentProbe() const
{
    // Blueprint WavFile export ownership is process-global, not per World.
    for(TObjectIterator<ADungeonContentProbe> It; It; ++It)
        if(IsValid(*It) && !It->IsTemplate() && !It->IsActorBeingDestroyed()) return true;
    return false;
}
bool UDungeonNativeMainSubmixCaptureV001::Begin(UWorld* World, const FString& NewOutputDirectory)
{
    using E = EDungeonNativeMixCapturePhaseV001;
    if(!IsInGameThread() || CaptureStatus.Phase != E::Idle) return false;
    CaptureWorld = World;
    if(!IsValid(World) || HasOldContentProbe()) { Fail(TEXT("invalid_world_or_old_ContentProbe_present")); return false; }
    if(NativeMixExportPoisonedUntilProcessExit || ActiveNativeMixCapture.IsValid())
    { Fail(TEXT("another_capture_or_failed_async_export_requires_fresh_process")); return false; }
    if(NewOutputDirectory.IsEmpty() || FPaths::IsRelative(NewOutputDirectory))
    { Fail(TEXT("absolute_NEW_output_directory_required")); return false; }
    FString Directory = FPaths::ConvertRelativePathToFull(NewOutputDirectory);
    FPaths::NormalizeDirectoryName(Directory);
    if(!IFileManager::Get().DirectoryExists(*FPaths::GetPath(Directory)) || !ExclusivelyCreateDirectory(Directory))
    { Fail(TEXT("existing_or_unclaimable_output_directory_preserved")); return false; }
    CaptureStatus.OutputDirectory = Directory;
    CaptureStatus.NewDirectoryExclusivelyCreated = true;
    CaptureStatus.EngineWav = Directory / TEXT("runtime-mix-engine-export.wav");
    CaptureStatus.CanonicalWav = Directory / TEXT("runtime-mix.wav");
    auto* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(World);
    auto* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume"));
    if(!Mixer || !AppVolume) { Fail(TEXT("native_mixer_or_process_app_volume_control_unavailable")); return false; }
    RecordingSubmix = &Mixer->GetMainSubmixObject();
    CaptureStatus.AudioDeviceId = Mixer->DeviceID;
    if(RecordingSubmix->OnSubmixRecordedFileDone.IsBound())
    { Fail(TEXT("main_submix_export_delegate_already_owned")); return false; }
    ActiveNativeMixCapture = this; OwnsLease = true;
    CaptureStatus.PreviousDisableAppVolume = AppVolume->GetInt();
    CaptureStatus.PreviousAppVolumeSetBy = uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask);
    PreviousSubmixAutoDisable = RecordingSubmix->bAutoDisable;
    CaptureStatus.ControlsConfigured = true;
    AppVolume->SetWithCurrentPriority(1); // Preserve value priority; no FApp setter or INI.
    Mixer->SetSubmixAutoDisable(RecordingSubmix, false);
    CaptureStatus.SubmixDisableRequestQueued = true; // No getter/ack claim.
    if(AppVolume->GetInt() != 1 || (uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask)) != CaptureStatus.PreviousAppVolumeSetBy)
    { Fail(TEXT("native_audio_control_value_or_priority_not_preserved")); return false; }
    RecordingSubmix->OnSubmixRecordedFileDone.AddDynamic(this, &UDungeonNativeMainSubmixCaptureV001::AudioExported);
    CaptureStatus.ArmingStartedMonotonic = FPlatformTime::Seconds();
    CaptureStatus.ArmingDeadlineMonotonic = CaptureStatus.ArmingStartedMonotonic + 5.;
    CaptureStatus.Phase = E::Arming;
    Poll();
    return !IsTerminal(); // Accepted arming, not necessarily started recording.
}
void UDungeonNativeMainSubmixCaptureV001::Poll()
{
    if(!IsInGameThread() || IsTerminal() || CaptureStatus.Phase == EDungeonNativeMixCapturePhaseV001::Idle) return;
    if(!CaptureWorld.IsValid() || HasOldContentProbe()) { Fail(TEXT("world_lost_or_old_ContentProbe_appeared")); return; }
    if(!SameNativeMixer(FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(CaptureWorld.Get()),
        RecordingSubmix.Get(), CaptureStatus.AudioDeviceId))
    { Fail(TEXT("actual_audio_device_or_main_submix_changed")); return; }
    if(CaptureStatus.Phase == EDungeonNativeMixCapturePhaseV001::Arming)
    {
        auto* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(CaptureWorld.Get());
        auto* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume"));
        if(!SameNativeMixer(Mixer, RecordingSubmix.Get(), CaptureStatus.AudioDeviceId) || !AppVolume)
        { Fail(TEXT("same_main_mixer_missing_while_arming")); return; }
        CaptureStatus.DisableAppVolumeStart = AppVolume->GetInt();
        CaptureStatus.AppVolumeSetByStart = uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask);
        CaptureStatus.PrimaryVolumeStart = Mixer->GetPrimaryVolume();
        CaptureStatus.AudioClockStart = Mixer->GetAudioTime();
        if(CaptureStatus.DisableAppVolumeStart != 1 || CaptureStatus.AppVolumeSetByStart != CaptureStatus.PreviousAppVolumeSetBy
            || !FMath::IsFinite(CaptureStatus.PrimaryVolumeStart) || CaptureStatus.PrimaryVolumeStart < 0.f
            || !FMath::IsFinite(CaptureStatus.AudioClockStart) || CaptureStatus.AudioClockStart < 0.)
        { Fail(TEXT("native_audio_arming_controls_or_clock_invalid")); return; }
        if(FPlatformTime::Seconds() >= CaptureStatus.ArmingDeadlineMonotonic)
        { Fail(TEXT("native_primary_volume_arming_timeout_preserved")); return; }
        // Device Update recomputes PrimaryVolume after the CVar change. Wait for
        // the real value; arming frames are not recording frames or audio time.
        if(CaptureStatus.PrimaryVolumeStart > 0.f)
        {
            CaptureStatus.StartMonotonic = FPlatformTime::Seconds();
            CaptureStatus.StartRequested = true;
            CaptureStatus.Phase = EDungeonNativeMixCapturePhaseV001::Recording;
            UAudioMixerBlueprintLibrary::StartRecordingOutput(CaptureWorld.Get(), 64.f, nullptr);
        }
        return;
    }
    if(CaptureStatus.Phase == EDungeonNativeMixCapturePhaseV001::ExportPending
        && FPlatformTime::Seconds() >= CaptureStatus.ExportDeadlineMonotonic)
        Fail(TEXT("async_original_WAV_export_timeout_preserved"));
}
bool UDungeonNativeMainSubmixCaptureV001::Stop()
{
    using E = EDungeonNativeMixCapturePhaseV001;
    if(!IsInGameThread()) return false;
    if(CaptureStatus.Phase == E::ExportPending || CaptureStatus.Phase == E::Complete) return true;
    if(IsTerminal()) return false;
    if(CaptureStatus.Phase != E::Recording) { Fail(TEXT("Stop_before_successful_Begin")); return false; }
    if(!CaptureWorld.IsValid() || HasOldContentProbe()) { Fail(TEXT("invalid_world_or_old_ContentProbe_at_Stop")); return false; }
    auto* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(CaptureWorld.Get());
    auto* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume"));
    if(!SameNativeMixer(Mixer, RecordingSubmix.Get(), CaptureStatus.AudioDeviceId) || !AppVolume)
    { Fail(TEXT("same_main_mixer_missing_at_Stop")); return false; }
    // The engine's async writer offers no no-overwrite flag. It writes only in
    // our atomically NEW private leaf; recheck both paths immediately before it.
    if(IFileManager::Get().FileExists(*CaptureStatus.EngineWav) || IFileManager::Get().FileExists(*CaptureStatus.CanonicalWav))
    { Fail(TEXT("output_collision_before_Stop_preserved_without_export")); return false; }
    CaptureStatus.StopAudioCommandFenceCompleted = CompleteEarlierAudioCommands();
    if(!CaptureStatus.StopAudioCommandFenceCompleted)
    { Fail(TEXT("pending_audio_Start_not_completed_before_Stop")); return false; }
    CaptureStatus.DisableAppVolumeStop = AppVolume->GetInt();
    CaptureStatus.AppVolumeSetByStop = uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask);
    CaptureStatus.PrimaryVolumeStop = Mixer->GetPrimaryVolume();
    CaptureStatus.AudioClockStop = Mixer->GetAudioTime();
    if(CaptureStatus.DisableAppVolumeStop != 1 || CaptureStatus.AppVolumeSetByStop != CaptureStatus.PreviousAppVolumeSetBy
        || !FMath::IsFinite(CaptureStatus.PrimaryVolumeStop)
        || CaptureStatus.PrimaryVolumeStop <= 0.f || !FMath::IsFinite(CaptureStatus.AudioClockStop)
        || CaptureStatus.AudioClockStop < CaptureStatus.AudioClockStart)
    { Fail(TEXT("native_audio_Stop_controls_or_clock_invalid")); return false; }
    CaptureStatus.StopMonotonic = FPlatformTime::Seconds();
    CaptureStatus.StopRequested = true;
    CaptureStatus.ExportDeadlineMonotonic = CaptureStatus.StopMonotonic + 10.;
    CaptureStatus.Phase = E::ExportPending;
    // WavFile normally returns nullptr. Only the explicit main-submix delegate
    // and actual preserved bytes finish this asynchronous operation.
    UAudioMixerBlueprintLibrary::StopRecordingOutput(CaptureWorld.Get(), EAudioRecordingExportType::WavFile,
        TEXT("runtime-mix-engine-export"), CaptureStatus.OutputDirectory, RecordingSubmix.Get(), nullptr);
    return true;
}
void UDungeonNativeMainSubmixCaptureV001::AudioExported(const USoundWave* ResultingSoundWave)
{
    using E = EDungeonNativeMixCapturePhaseV001;
    if(!IsInGameThread() || CaptureStatus.Phase != E::ExportPending) return;
    CaptureStatus.ExportCallbackReceived = true;
    if(!CaptureWorld.IsValid() || HasOldContentProbe())
    { Fail(TEXT("export_callback_world_lost_or_old_ContentProbe_present")); return; }
    TArray<uint8> Original;
    if(!FFileHelper::LoadFileToArray(Original, *CaptureStatus.EngineWav) || Original.Num() <= 44)
    { Fail(TEXT("export_callback_without_complete_original_WAV")); return; }
    CaptureStatus.EngineWavPresent = true;
    const auto U16 = [&Original](int32 O) { return uint32(Original[O]) | uint32(Original[O+1]) << 8; };
    const auto U32 = [&Original](int32 O) { return uint32(Original[O]) | uint32(Original[O+1]) << 8
        | uint32(Original[O+2]) << 16 | uint32(Original[O+3]) << 24; };
    const uint32 Channels = U16(22), Rate = U32(24), Align = Channels * 2;
    // Same fixed native UE PCM16 parser as ContentProbe; preserve engine bytes.
    const bool Valid = FMemory::Memcmp(Original.GetData(), "RIFF", 4) == 0
        && FMemory::Memcmp(Original.GetData()+8, "WAVE", 4) == 0
        && FMemory::Memcmp(Original.GetData()+12, "fmt ", 4) == 0 && U32(16) == 16 && U16(20) == 1
        && Channels >= 1 && Channels <= 8 && Rate >= 8000 && Rate <= 192000 && U16(34) == 16
        && (U16(32) == Align || U16(32) == 2) && U32(28) == Rate * Align
        && FMemory::Memcmp(Original.GetData()+36, "data", 4) == 0
        && uint64(U32(4))+8 == uint64(Original.Num()) && uint64(U32(40))+44 == uint64(Original.Num())
        && U32(40) > 0 && U32(40) % Align == 0;
    if(!Valid) { Fail(TEXT("native_original_PCM16_WAV_structure_invalid")); return; }
    TArray<uint8> Canonical = Original;
    CaptureStatus.HeaderBlockAlignRepaired = U16(32) != Align;
    Canonical[32] = uint8(Align & 255); Canonical[33] = uint8(Align >> 8);
    CaptureStatus.PCMPayloadUnchanged = FMemory::Memcmp(Canonical.GetData()+44, Original.GetData()+44, Original.Num()-44) == 0;
    if(!CaptureStatus.PCMPayloadUnchanged || !WriteNewCanonical(CaptureStatus.CanonicalWav, Canonical))
    { Fail(TEXT("canonical_CREATE_NEW_or_exact_PCM_preservation_failed")); return; }
    CaptureStatus.CanonicalWavReady = true;
    CaptureStatus.Channels = Channels; CaptureStatus.SampleRate = Rate;
    CaptureStatus.PCMFrames = U32(40) / Align;
    RestoreControls();
    const bool Restored = CaptureStatus.AppVolumeRestored && CaptureStatus.SubmixRestoreRequestQueued;
    CaptureStatus.Phase = Restored ? E::Complete : E::Failed;
    if(!Restored)
    { CaptureStatus.Failure = TEXT("process_audio_controls_restore_incomplete"); NativeMixExportPoisonedUntilProcessExit = true; }
    ReleaseLeaseAndDelegate();
}
void UDungeonNativeMainSubmixCaptureV001::RestoreControls()
{
    if(CaptureStatus.ControlsRestoreRequested) return;
    CaptureStatus.ControlsRestoreRequested = true;
    if(CaptureStatus.ControlsConfigured)
    {
        if(auto* AppVolume = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume")))
        {
            CaptureStatus.AppVolumeSetByRestored = uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask);
            // An unexpected foreign priority owner is preserved and reported,
            // never forcibly demoted or overwritten to make QA look restored.
            if(CaptureStatus.AppVolumeSetByRestored == CaptureStatus.PreviousAppVolumeSetBy)
                AppVolume->SetWithCurrentPriority(CaptureStatus.PreviousDisableAppVolume);
            CaptureStatus.AppVolumeSetByRestored = uint32(AppVolume->GetFlags()) & uint32(ECVF_SetByMask);
            CaptureStatus.AppVolumeRestored = AppVolume->GetInt() == CaptureStatus.PreviousDisableAppVolume
                && CaptureStatus.AppVolumeSetByRestored == CaptureStatus.PreviousAppVolumeSetBy;
        }
        if(RecordingSubmix && CaptureWorld.IsValid())
            if(auto* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(CaptureWorld.Get()))
            {
                if(SameNativeMixer(Mixer, RecordingSubmix.Get(), CaptureStatus.AudioDeviceId))
                {
                    Mixer->SetSubmixAutoDisable(RecordingSubmix.Get(), PreviousSubmixAutoDisable);
                    CaptureStatus.SubmixRestoreRequestQueued = true; // Queue, not effective-value ack.
                }
            }
    }
}
void UDungeonNativeMainSubmixCaptureV001::ReleaseLeaseAndDelegate()
{
    if(RecordingSubmix) RecordingSubmix->OnSubmixRecordedFileDone.RemoveDynamic(this,
        &UDungeonNativeMainSubmixCaptureV001::AudioExported);
    if(OwnsLease && ActiveNativeMixCapture.Get() == this) ActiveNativeMixCapture.Reset();
    OwnsLease = false;
}
void UDungeonNativeMainSubmixCaptureV001::Fail(const FString& Reason, bool Aborted)
{
    using E = EDungeonNativeMixCapturePhaseV001;
    if(IsTerminal()) return;
    if(CaptureStatus.Phase == E::Recording)
    {
        CaptureStatus.StopAudioCommandFenceCompleted = CompleteEarlierAudioCommands();
        CaptureStatus.StopMonotonic = FPlatformTime::Seconds();
        if(CaptureWorld.IsValid())
            if(auto* Mixer = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(CaptureWorld.Get()))
            {
                if(SameNativeMixer(Mixer, RecordingSubmix.Get(), CaptureStatus.AudioDeviceId))
                {
                    float Channels = 0.f, Rate = 0.f;
                    Mixer->StopRecording(RecordingSubmix.Get(), Channels, Rate); // Drain only, no export.
                    CaptureStatus.AbortDrainRequested = true;
                }
            }
        // Any active-recording failure requires a fresh isolated process, even
        // when the ordered drain completed; never infer safe retry from a flag.
        NativeMixExportPoisonedUntilProcessExit = true;
    }
    if(CaptureStatus.Phase == E::ExportPending) NativeMixExportPoisonedUntilProcessExit = true;
    CaptureStatus.Failure = Reason.IsEmpty() ? TEXT("capture_aborted_without_reason") : Reason;
    CaptureStatus.Phase = Aborted ? E::Aborted : E::Failed;
    RestoreControls(); ReleaseLeaseAndDelegate();
}
void UDungeonNativeMainSubmixCaptureV001::Abort(const FString& Reason)
{
    if(IsInGameThread()) Fail(Reason, true);
}
void UDungeonNativeMainSubmixCaptureV001::BeginDestroy()
{
    if(IsInGameThread() && !IsTerminal()) Abort(TEXT("capture_owner_destroyed_before_completed_export"));
    Super::BeginDestroy();
}
TSharedRef<FJsonObject> UDungeonNativeMainSubmixCaptureV001::SerializeReport() const
{
    const auto& S = CaptureStatus; auto R = MakeShared<FJsonObject>();
    const auto Number = [&R](const TCHAR* Key, double Value)
    {
        if(FMath::IsFinite(Value)) R->SetNumberField(Key, Value);
        else R->SetField(Key, MakeShared<FJsonValueNull>()); // Failed observations remain valid JSON.
    };
    R->SetStringField(TEXT("schema"), TEXT("native-main-submix-capture-v001"));
    R->SetStringField(TEXT("phase"), PhaseName(S.Phase)); R->SetStringField(TEXT("failure"), S.Failure);
    R->SetStringField(TEXT("output_directory"), S.OutputDirectory);
    R->SetStringField(TEXT("engine_original_wav"), S.EngineWav); R->SetStringField(TEXT("canonical_wav"), S.CanonicalWav);
    Number(TEXT("start_monotonic_s"), S.StartMonotonic); Number(TEXT("stop_monotonic_s"), S.StopMonotonic);
    Number(TEXT("arming_started_monotonic_s"), S.ArmingStartedMonotonic);
    Number(TEXT("requested_wall_duration_s"), S.StopMonotonic > S.StartMonotonic ? S.StopMonotonic-S.StartMonotonic : 0.);
    Number(TEXT("audio_clock_start_s"), S.AudioClockStart); Number(TEXT("audio_clock_stop_s"), S.AudioClockStop);
    Number(TEXT("primary_volume_start"), S.PrimaryVolumeStart); Number(TEXT("primary_volume_stop"), S.PrimaryVolumeStop);
    R->SetNumberField(TEXT("previous_disable_app_volume"), S.PreviousDisableAppVolume);
    R->SetNumberField(TEXT("previous_disable_app_volume_set_by"), S.PreviousAppVolumeSetBy);
    R->SetNumberField(TEXT("disable_app_volume_set_by_start"), S.AppVolumeSetByStart);
    R->SetNumberField(TEXT("disable_app_volume_set_by_stop"), S.AppVolumeSetByStop);
    R->SetNumberField(TEXT("disable_app_volume_set_by_restored"), S.AppVolumeSetByRestored);
    R->SetNumberField(TEXT("disable_app_volume_start"), S.DisableAppVolumeStart); R->SetNumberField(TEXT("disable_app_volume_stop"), S.DisableAppVolumeStop);
    R->SetNumberField(TEXT("channels"), S.Channels); R->SetNumberField(TEXT("sample_rate_hz"), S.SampleRate); R->SetNumberField(TEXT("pcm_frames"), S.PCMFrames);
    R->SetNumberField(TEXT("native_audio_device_id"), S.AudioDeviceId);
    R->SetBoolField(TEXT("start_requested"), S.StartRequested); R->SetBoolField(TEXT("stop_requested"), S.StopRequested);
    R->SetBoolField(TEXT("export_callback_received"), S.ExportCallbackReceived);
    R->SetBoolField(TEXT("new_directory_exclusively_created"), S.NewDirectoryExclusivelyCreated);
    R->SetBoolField(TEXT("engine_wav_present"), S.EngineWavPresent); R->SetBoolField(TEXT("canonical_wav_ready"), S.CanonicalWavReady);
    R->SetBoolField(TEXT("header_block_align_repaired"), S.HeaderBlockAlignRepaired); R->SetBoolField(TEXT("PCM_payload_unchanged"), S.PCMPayloadUnchanged);
    R->SetBoolField(TEXT("controls_configured"), S.ControlsConfigured); R->SetBoolField(TEXT("controls_restore_requested"), S.ControlsRestoreRequested);
    R->SetBoolField(TEXT("app_volume_restored"), S.AppVolumeRestored);
    R->SetBoolField(TEXT("submix_auto_disable_request_queued"), S.SubmixDisableRequestQueued);
    R->SetBoolField(TEXT("submix_restore_request_queued"), S.SubmixRestoreRequestQueued);
    R->SetBoolField(TEXT("abort_drain_requested"), S.AbortDrainRequested);
    R->SetBoolField(TEXT("stop_audio_command_fence_completed"), S.StopAudioCommandFenceCompleted);
    R->SetStringField(TEXT("source"), TEXT("UE native game main output submix only; no microphone, desktop loopback or offline sample assembly"));
    R->SetStringField(TEXT("timing_scope"), TEXT("Actual monotonic game-thread request boundaries; not sample-accurate device onset or measured audio render latency"));
    R->SetStringField(TEXT("overwrite_scope"), TEXT("Windows atomic NEW directory plus immediate pre-export file checks; canonical CREATE_NEW. Engine async writer has no independent no-replace flag; exclusive QA directory ownership required."));
    R->SetBoolField(TEXT("submix_effective_auto_disable_read_back"), false);
    R->SetBoolField(TEXT("non_silence_checked_by_helper"), false); R->SetBoolField(TEXT("auditioned"), false);
    R->SetBoolField(TEXT("final_mix_accepted"), false); R->SetNumberField(TEXT("formal_complete_units"), 0);
    return R;
}
