# Native main Submix capture helper v001 — frozen candidate only

Two proposed new Source files, one reusable UObject, one independent read-only checker. Root owns actual Source admission, UHT/build/native execution, retention and audition. This worker has not changed actual Source/Content/tools/E/ledger or run UE/audio playback/external APIs.

## API and observer contract

Include DungeonNativeMainSubmixCaptureV001.h. The observing AActor must own a UPROPERTY(Transient) TObjectPtr<UDungeonNativeMainSubmixCaptureV001>, created by NewObject<...>(this). A weak delegate or static weak lease does not keep it alive.

- Begin(GetWorld(), OriginalDir / TEXT("audio-v001")): the absolute audio-v001 leaf MUST NOT exist; its parent must exist. The helper claims a Windows atomic NEW directory. true means arming accepted, not proven recording or sound.
- Poll() each game-thread Tick. Arming waits actual native PrimaryVolume>0 after the process CVar takes effect. StartRequested and StartMonotonic are published only when it dispatches the real main-submix StartRecordingOutput. Arming times out after5s and is not recording time.
- Start screenshots/normal input only when Status().Phase==Recording && StartRequested && StartMonotonic>0. Copy that exact actual monotonic value as the frame wall-offset origin; do not reset it to the next Tick or use simulation time.
- After the last real original screenshot callback: stop requesting screenshots, freeze observer gameplay/event/request facts once, call Stop(), THEN flush queued screenshot writes. Stop stamps the real audio request boundary after retiring pending audio commands. ExportPending/Complete repeated Stop returns true without reissue or changing timestamps.
- Continue Poll() until IsTerminal(). Complete means original/canonical PCM export and control restore requests completed, not a verified non-silent recording or listening acceptance. Failed/Aborted preserve all partial files. Keep the object/World alive through async export; EndPlay before terminal calls Abort(reason).
- Put SerializeReport() at runtime-report.main_submix_capture. capture_timing starts/stops must copy Status().StartMonotonic/StopMonotonic exactly; one real frame_wall_offsets_s value and observation per actual callback. Save frozen event facts, never live game facts read during the async export wait.

Exact machine-readable agreement: observer-interface-protocol-v001.json. No old ADungeonContentProbe may exist in ANY World; another helper lease or failed active/export capture rejects same-process reuse. Use a fresh isolated QA process after failure.

## Actual recording and safety boundary

Uses the actual installed UE5.5 APIs already demonstrated by DungeonContentProbe: main output StartRecordingOutput(World,64,nullptr), asynchronous WavFile Stop with the SAME explicit native main submix, OnSubmixRecordedFileDone.64s is preallocation advice, not retiming or an imposed recording duration. No microphone, desktop loopback, offline sample assembly, new PlaySound or gameplay events.

Preserves runtime-mix-engine-export.wav verbatim. A separate runtime-mix.wav accepts only the known native PCM16 fixed44 header and corrects bytes32/33 BlockAlign if needed; all PCM bytes and all other header bytes must match. Canonical writes use Windows CREATE_NEW. The engine's original async writer has no no-replace option: original-file protection explicitly relies on the atomically NEW private directory, exclusive ownership and immediate pre-export collision checks. This is not a claim that the engine writer itself gained CREATE_NEW.

Process app-volume value AND original SetBy priority are preserved; a foreign priority owner is not forcibly overridden. Submix auto-disable is queued on its instance and later restore is queued; there is no effective-value getter/ack claim. Native DeviceID plus main-submix asset identify the same mixer. Mismatch/world loss skips foreign drain/restore, keeps failure/poison and never pretends cleanup succeeded. AudioCommandFence retires the queued Start before synchronous Stop/drain, including same-frame Abort. No Run/position/HP/input/clock/asset-default/INI writes or gameplay audio journal consumption.

## Checker

```powershell
& './tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'source-assets/production/fairytale-hero-air-v001/audio-capture-helper-candidate-v001/tooling/check-native-main-submix-v001.py' --report 'ACTUAL_NATIVE_ARCHIVE/原件/runtime-report.json' --capture-field main_submix_capture --require-frame-timing --output 'NEW_INDEPENDENT_RECEIPT.json'
```

Reads original and canonical from that same report's own helper directory. Full independent WAV decode, exact original/canonical PCM identity, required actual capture/control/priority/fence receipts, unchanged recorded-signal peak>=-60dBFS/RMS>=-100dBFS, first frame<=100ms and WAV/wall difference<=150ms. No gain, silence fill, stretching, replacing or writing audio. Optional output is a NEW JSON receipt only. A passing file/signal checker does NOT identify each cue, certify device onset/latency, prove source provenance independently of Root's compiled native chain, or accept timbre/mix. Other sounds can make a recording non-silent while Jump itself remains silent; per-cue proof and listening remain required.

## Verification actually performed

host-verification-v003.json:45 host checks pass. Two real historical UE original/canonical WAV pairs fully decode and retain identical PCM; old v003 actual all-zero recording remains rejected. Real byte corruption/truncation/header mutations and memory-only fake phase/boolean/NaN/Inf/priority/fence/timing gates reject. Synthetic receipts remain gate fixtures, not game records. No audio file was written or played. v001/v002 host reports preserve earlier draft verification.

Independent source review closed queued-Start/Abort ordering, CVar SetBy priority, background Arming and mixer-replacement failure boundaries; its final two source size/SHA passes match the frozen files. Read-only local project and engine API evidence is pinned in source-basis-pins-v001.json and source-basis-additional-pins-v002.json. This is static review and Python evidence only: no UHT/C++ build or new native capture has run. Root must still check normal export, repeated Stop, occupied path preservation, same-frame Abort and device/world loss in the actual admitted build.

Dependencies already present: Core/CoreUObject/Engine/Json/AudioMixer in CodexDungeon.Build.cs; project Python with numpy and standard wave. No dependency installation, provider API or paid generation.
