# Guard DiskV2: dedicated two-process candidate v001

Facts: this folder adds one opt-in actor, a minimal HUD include/startup patch, and isolated launcher/verifier tooling. The previous partial draft under `disk-v2-candidate-v001/two-process-candidate-v001` remains untouched. The real V2 adapter is 19299 bytes / SHA256 `14a8472acd3e9018db6a32d2886b8e214cdcfde989234d470a63d29e36a56065`. Existing V1 adapter and V1 probe bytes are pinned. This candidate has not been compiled or run in UE; its offline source and verifier checks are only preparation evidence.

Reasoning: the source process uses the actual FirstRoom GameMode, a genuine Controller Enter edge, two public legal ENM-STN-003 spawns (live at player+150 X), the real wake/first outgoing attack, a public 1.6 raw physical /85 stagger hit yielding one HP loss and a real interruption, then a later naturally active action. It captures/commits the whole V2 Run and exits. A distinct process starts at the actual native no-Run pristine bootstrap, checks R cannot restart it, calls V2 LoadAndPreparePristine/Install, compares every full Codec byte immediately and after a real paused wall interval, then continues through neutral fresh Enter. It verifies the original absolute active end, one recovery event, a next public mitigated receipt and late native ticks. One saved Guard is actually dead, independently native-observed, locally claimed, and formally unsettled. Two explicit observer reentries and another claim must leave the entire Run Codec byte-identical.

Risk and boundary: this is public spawn setup and native persistence proof. Formal room encounter/spawn, formal reward allocation/pickup/room settlement, Guard audio, full Profile/D13, complete visual content, device audition and human visual review remain incomplete. The Guard currently has placeholder visuals. A hitch that skips a required active observation must fail and retain the session; do not change the clock or synthesize proof frames. Root is the sole Source/UE/UBT integrator.

## Admission

Copy only `candidate-source/DungeonGuardRunContinueProbe.h` and `.cpp` into actual `UnrealGame/Source/CodexDungeon`. Merge `patches/hud-guard-process-spawn-v001.patch` into the current HUD. `before/DungeonHUD.cpp` and `candidate-source/DungeonHUD.cpp` are v126 reference context only: **do not overwrite the new Walk HUD with either whole file**. The patch adds the new include and gives the dedicated Guard flags priority inside the existing DungeonContentProof branch, avoiding the old ContentProbe. It does not modify the V1 probe path. No Walk opt-in flag is used. Root compiles/tests the actual integrated Source and retains failures independently; if the two dedicated files need repair, preserve v001 and prepare another frozen candidate version.

## Tools and commands

From `F:/Ourgame`, default tooling check (no UE):

```powershell
& .\source-assets\production\stone-guard-owner-v002\guard-two-process-candidate-v001\tooling\verify-guard-pristine-two-process-v001.ps1
```

After Root source admission/build and no other UE/UBT, execute sequential native roles:

```powershell
& .\source-assets\production\stone-guard-owner-v002\guard-two-process-candidate-v001\tooling\verify-guard-pristine-two-process-v001.ps1 -Run -Version 1
```

Optional parameters: `-EngineRoot G:\UE_5.5`, `-WorkspaceRoot F:\Ourgame`, and an unused absolute `-SessionRoot`. The launcher creates a fresh Profile GUID under its own `BoundRunOnly-v2`, checks candidate files and the V1/V2 protocol pins, binds the actual post-admission DLL SHA, hashes all actual Source before/after, excludes existing UE/UBT, and records real PIDs/nonoverlapping lifetimes/native log hashes. It uses a shared coordinator mutex, hidden helper windows and real ordinary frame pacing at max30 FPS. The restore URL is `/Game/Maps/FirstRoom?DungeonContinuePristine`. Failed sessions remain intact and cannot be reused.

Standalone independent recheck (read-only; creates a new receipt only with the explicit write flag):

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 .\source-assets\production\stone-guard-owner-v002\guard-two-process-candidate-v001\tooling\verify-guard-pristine-two-process-v001.py --session <absolute-session>
```

Runtime actor parameters are `-DungeonGuardRunSaveProof` XOR `-DungeonGuardRunRestoreProof`, `-DungeonGuardRunProofDir=<role-directory>`, `-DungeonGuardRunProofProfiles=<absolute-normalized-BoundRunOnly-v2>`, `-DungeonGuardRunProofProfile=<fresh-guid>`, and `-DungeonGuardRunProofBuildId=<actual-DLL-SHA256>`. Both roles require `-DungeonContentProof -DungeonFastLosslessCapture -DungeonAsyncLosslessCapture`; `-DungeonContentProofDir` must also equal the role directory. Source adds `-DungeonSceneExplorationPreview`.

## Exact output contract

See `expected-outputs-v001.json`. Each role writes `runtime-report.json`, exact original whole Codec evidence, synchronous native prewarm and native async movie PNG/CRC/FIFO/flush evidence. The independent verifier inspects the original committed Store bundle/marker, extracts the exact nested Codec byte slice, checks all deadline/receipt/death facts against whole snapshot values, and decodes every PNG back to native BGRA CRC. Runtime flags and queue-enqueue counts alone are insufficient. The source must fully exit before restore launches.

Before showing any resulting native PNG, movie, review page or derivative, Root must retain originals and presentation copies with source/version/status index under `E:/OurGame/Knight/过程图稿与视频` and follow that directory's README. Root must encode a short silent proof recording from actual captured frames/timestamps and review it before claiming visible runtime completion. This candidate itself creates no media and makes no runtime/visual acceptance claim.
