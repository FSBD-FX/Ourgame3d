#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "DungeonNativeMainSubmixCaptureV001.generated.h"

class FJsonObject;
class USoundSubmix;
class USoundWave;
class UWorld;

enum class EDungeonNativeMixCapturePhaseV001 : uint8
{
    Idle, Arming, Recording, ExportPending, Complete, Failed, Aborted
};

// Probe-only output facts. Never a saved Run state or audio-device onset receipt.
struct FDungeonNativeMixCaptureStatusV001
{
    EDungeonNativeMixCapturePhaseV001 Phase = EDungeonNativeMixCapturePhaseV001::Idle;
    FString Failure, OutputDirectory, EngineWav, CanonicalWav;
    double StartMonotonic = 0., StopMonotonic = 0., ExportDeadlineMonotonic = 0.;
    double ArmingStartedMonotonic = 0., ArmingDeadlineMonotonic = 0.;
    double AudioClockStart = 0., AudioClockStop = 0.;
    float PrimaryVolumeStart = 0.f, PrimaryVolumeStop = 0.f;
    int32 PreviousDisableAppVolume = 0, DisableAppVolumeStart = 0, DisableAppVolumeStop = 0;
    uint32 PreviousAppVolumeSetBy = 0, AppVolumeSetByStart = 0, AppVolumeSetByStop = 0, AppVolumeSetByRestored = 0;
    uint32 AudioDeviceId = MAX_uint32;
    uint32 Channels = 0, SampleRate = 0, PCMFrames = 0;
    bool StartRequested = false, StopRequested = false, ExportCallbackReceived = false;
    bool NewDirectoryExclusivelyCreated = false, EngineWavPresent = false;
    bool HeaderBlockAlignRepaired = false, PCMPayloadUnchanged = false, CanonicalWavReady = false;
    bool ControlsConfigured = false, ControlsRestoreRequested = false, AppVolumeRestored = false;
    bool SubmixDisableRequestQueued = false, SubmixRestoreRequestQueued = false;
    bool AbortDrainRequested = false;
    bool StopAudioCommandFenceCompleted = false;
};

/** One-shot native main-output capture, owned strongly by ONE isolated QA Probe.
 * Begin only after prewarm. OutputDirectory must be absolute, NEW, and have an
 * existing parent. Begin accepts arming; Poll until Recording/StartRequested
 * before using StartMonotonic as the movie origin. Stop after the last real frame.
 * Repeated Stop is idempotent. Complete means preserved PCM export, not audition.
 * No game input, gameplay/event/time/volume-asset/INI or microphone operations.
 */
UCLASS(Transient)
class CODEXDUNGEON_API UDungeonNativeMainSubmixCaptureV001 : public UObject
{
    GENERATED_BODY()
public:
    bool Begin(UWorld* World, const FString& NewOutputDirectory);
    void Poll();
    bool Stop();
    void Abort(const FString& Reason);
    bool IsTerminal() const;
    const FDungeonNativeMixCaptureStatusV001& Status() const { return CaptureStatus; }
    TSharedRef<FJsonObject> SerializeReport() const;
    virtual UWorld* GetWorld() const override;
    virtual void BeginDestroy() override;

private:
    UFUNCTION()
    void AudioExported(const USoundWave* ResultingSoundWave);
    void RestoreControls();
    void ReleaseLeaseAndDelegate();
    void Fail(const FString& Reason, bool Aborted = false);
    bool HasOldContentProbe() const;

    FDungeonNativeMixCaptureStatusV001 CaptureStatus;
    TWeakObjectPtr<UWorld> CaptureWorld;
    UPROPERTY(Transient)
    TObjectPtr<USoundSubmix> RecordingSubmix;
    bool PreviousSubmixAutoDisable = true;
    bool OwnsLease = false;
};
