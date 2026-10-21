# Guard feedback production candidate v001

Root observed real Stage0: UBT095321 exit0/68 actions; native `FirstRoom-20261018-095718` exact3 semantic RED, each1 error/0 warnings. The preserved evidence is `docs/production/first-batch-v2/evidence/guard-feedback-v001/root-threeRED-v001/manifest.json`. The production candidate below has NOT been compiled or run in UE by this child. No actual Source/tools/README/status/ledger was edited here.

Integration, in order:

1. Keep the exact frozen3 tests from `stage0-v002-source/Tests/DungeonStoneGuardFeedbackTests.cpp`; do not replace them with a relaxed verifier.
2. Root imports the11 native SoundWaves via candidate `tooling/ue-import-guard-audio-v001.py`. Its actual fresh target is `/Game/Production/FirstBatch/v028/GuardAudio`; old17 and old5 resources are untouched. `--validate-only` is already exit0 in local project Python. Root uses its existing `-ExecutePythonScript` import flow, with this candidate script as the path. No overwrite/reimport is allowed into an occupied destination.
3. Copy the3 files under `production-source` to Source/CodexDungeon. Apply or manually merge `patches/production-after-stage0-v002.patch` against the already-admitted feedback Stage0 interfaces. `git apply --check` was exit0 when frozen. It is intentionally only6 small files, never whole Fighter/GM/HUD replacements.
4. Merge the room agent owner/death changes independently; this candidate adds no owner/Codec/Rewards field. `FPendingDamage.GuardFeedbackEventId` is transient and appended after existing fields. Map real batch Hit to original EventId, then call ConfirmHit only after actual Loss>0 in CommitPendingDamage.
5. Root compiles Editor, runs strict3 filter, then complete registry with exact current count. Example commands from F:/Ourgame:

```powershell
& .\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 source-assets/production/stone-guard-feedback-v001/tooling/ue-import-guard-audio-v001.py --validate-only
pwsh -NoProfile -File .\tools\scripts\unreal-build.ps1
pwsh -NoProfile -File .\tools\scripts\test-first-room.ps1 -TestFilter CodexDungeon.Content.StoneGuardFeedback -ExpectedTests 3
```

Expected three GREEN witnesses: native Wake/Axe/Stomp + actual HUD play/spawn requests + real material HP commit; pre-window85 interrupt/no release and issued-window closure/no replay + death once; full actual existing installer pause byte-preservation + future1HP only + late HUD rebuild + native movement stride remainder. No test writes actor positions or advances the GM clock outside the existing accepted fixture.

HUD hook interface: LoadGuardFeedbackSounds in real BeginPlay; UpdateGuardFeedback once in real Tick after gate checks; ResetGuardFeedback during actual restored presentation attachment; DrawGuardFeedback(F) once in the real Guard branch (Root may position this before/after its new armed whole-body sprite). This independent CPP does not rig the weapon, alter action selection, edit GameMode clocks or draw constant ambient rings. Requests have bounded history; active effects have finite expiration. Windup components stop on matching cancellation or owner death.

Material identity is equipment/body derived, not a physical-material collision query. Known stone owners use Stone; medium/heavy armor use Metal; other targets use FleshLeather. Incoming Guard chips use the existing Damaged.Amount actual mitigation result; outgoing requests retain original source Hit ID, target/time and positive actual loss. Axe dust/grit is an accepted-window accent, not proof of ground collision. See EVENT-MAP-v001.md.

Audio/visual acceptance remains open.11 original procedural voices are trials; native import, sound request correctness and numeric headroom do not approve stone timbre or device mix. The new canonical F topic `过程图稿与视频/2026-10-18_石守卫十一声音原创合成试听候选_v001` has11 originals,11 identical presentation copies, Chinese listening notes and an HTML playlist. Root must retain it to E before opening or audition. This child did not View/play it.

Local limited checks: the pure header plus Root-frozen real Guard kernel compiled with MSVC C++17 and ran accepted native movement/restore stride and explicit real axe TryHit/positive-loss-only confirmation/dedup checks. This is NOT UE HUD or device proof. First cl include-path invocation failure and first standalone fixture missing explicit TryStartAttack failure were retained under local-cpp-check-v001; neither changed production or softened any native Stage0 assertion. Numeric audio checks reproduce11 decoded PCM arrays exactly, format48k mono PCM16/no clipped samples.

An offline `tooling/mix-actual-guard-timeline-v001.py` accepts only concrete native request schema and exact imported object paths. Its result must be called a dry request-timeline reconstruction, never captured UE audio. Root can add a native report export at the end of its real Guard proof. The silent MP4 is only visual proof.
