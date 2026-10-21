# Bound Run Capture and Restore Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Retain actual RED/GREEN evidence; root alone runs UE/UBT.

**Goal:** Restore the actual bound Run, including in-flight equipment/actions, enemies, projectiles, rewards and exploration, without new-Run initialization or duplicate outcomes.

**Architecture:** Each existing owner captures a versioned value snapshot and validates a complete candidate before installation. The final aggregate records one completed simulation boundary, encodes the whole canonical payload into the existing generation store, reconstructs actors and geometry while paused, and enables fresh input only after all cross-references match. Owner snapshots are necessary work; they do not constitute completed disk Continue.

**Tech Stack:** UE5.5.4 C++, existing pure kernels, Windows generation store, native image generation for separate art trials.

**Spec:** `存档数据与后续合作边界设计.md`, `docs/production/first-batch-v2/evidence/save-generation-store-v001/next-run-snapshot-code-map-v001.md`, active full first-batch objective.

## Constraints and review focus

- Preserve all 5 weapons / 4 armors / 5 ordinary enemies / Boss / 20 combinations / auxiliary15 and full motion/audio/VFX scope; formal0/15 until actual acceptance.
- Existing actual96 baseline and two storage counterexamples remain. No reset, offline catch-up, new RNG draw, starter issuance or old-event replay during restore.
- Reject unknown schema, nonfinite/out-of-range numbers, stale pending plans, conflicting stable IDs, missing referenced sources and malformed fog arrays without mutating the current owner.
- Snapshot normal mid-action states, cancellation residue and spent receipt domains; do not restrict capture to idle just to pass.
- HUD-owned explored memory is a real Run fact. Reconstruct its grid from bounds, preserve exact values, and derive counts.

## Task 1 — equipment owner (scale_tests)

Files: `DungeonEquipmentRuntime.h/.cpp`, new `Tests/DungeonEquipmentSnapshotTests.cpp`.
Interfaces: `FDungeonEquipmentRuntimeSnapshot`, `FDungeonEquipmentCritReceipt`, `Capture() const`, `bool Restore(const FDungeonEquipmentRuntimeSnapshot&, FString&)`.
Snapshot includes schema, complete View, inventory, external Sources, PendingPlan/drop and CritReceipts. Restorer validates a temporary candidate and keeps the live owner unchanged on rejection. Root adds read-only `ADungeonGameMode::CaptureEquipmentSnapshot()` forwarding to the current real runtime so tests capture actual actions, not a separately invented fixture.

- [x] Declare types + failing stub; test actual pending pickup/switch/replacement, IDs, receipts and invalid candidate nonmutation.
- [x] Root build and actual new-test RED; preserve inputs/report (001102 actual0/7, v057).
- [x] Implement only after RED; root full regression (004750 actual103/103, v060) and independent final99a05985 review passed. Active/completed unrelated-registration counterexamples were actualRED before narrow fixes.

## Task 2 — scene and exploration owners (root)

Files: `DungeonSceneObjects.h/.cpp`, `DungeonExploration.h`, new `Tests/DungeonOwnerSnapshotTests.cpp`.
Interfaces: `FDungeonSceneObjectsSnapshot`, `Capture() const`, `bool Restore(const ..., FString&)`; `DungeonExploration::FState`, `Capture() const`, `bool Restore(const FState&)`.
Preserve every room's survey facts and pending confirmation/time; validate known immutable layout and Run/room/object identities before install. Preserve exact interpolated fog values and room identity; grid axes/counts are derived from validated bounds/data.

- [x] Write meaningful failing round-trip and malformed/unknown-schema rejection tests with existing real owners.
- [x] Root actual RED, implement, complete regression; no test-count relaxation (004207 actual numeric counterexamples→004750 full103).

## Task 3 — fighter/world owners complete; aggregate remains required

### 3a — Fighter owner (scale_tests; current Schema2 owner complete)

Files: `DungeonFighter.h/.cpp`, new `DungeonFighterSnapshot.h`, `DungeonStoneBatDriver.h/.cpp`, new `Tests/DungeonFighterSnapshotTests.cpp`.

Use current `fighter-owner-snapshot-contract-v002.md` (retain v001 as historical evidence): full body/protection/presentation/action state, stable identity, saved Bat construction origin/time, legitimate terminal clock/height differences and terminal event queues. `CaptureOwnerSnapshot(Out, Why, ExplicitStaging=nullptr)` reads actual GM by default; explicit staging context must prove saved binding identity without allocating or mutating IDs. `RestoreOwnerSnapshot(S, Context, Why)` validates complete candidate before one installation. Root alone builds/runs new5 actualRED before production implementation. Owner tests do not certify aggregate/new-process Continue.

- [x] Stage0 types/stubs and5 actual-flow tests; actual013639RED/v061.
- [x] Production owner/driver schema2; actual023434 anchor/bodyRED →024633/default024800111GREEN/v070, independent final linked in proof.

### 3b — weapon-world owner (root; current Schema1 owner complete)

Files: new `DungeonWorldSnapshot.h/.cpp`, new `Tests/DungeonWorldSnapshotTests.cpp`. Existing projectile/gameplay methods stay unchanged.

Capture all fields of `FDungeonWeaponWorldState` by value. Restore context supplies approved Run/room/owner/simulation boundary and the saved player's complete validated `DungeonWeaponActions::FState`. Validate IDs, historical entity bindings, original issued emissions and frozen sockets/range anchors, live/stopped projectiles, windows, one-hit receipts, burn refresh/tick phase and event sequence before installing an independent value candidate. Historical actors need not remain alive; prior-room inactive attacks and burn history remain. Do not require the appended world journal's timestamps to be globally sorted: actual per-projectile traversal can append earlier contact times after later ones. Do not recompute an old emission from the current actor.

- [x] Stage0 pure interface/stubs and3 real GM world-state tests, prefix `CodexDungeon.Content.WorldOwnerSnapshot`; root actualRED.
- [x] Implement after actualRED; reviewer intrinsic counterexamples reproduced then fixed; full/default111GREEN/v070, original103 retained.
- [x] Independent World final94212f37 plus actual111GREEN; state-only restore remains distinct from GM actor map installation and disk Continue.

- [x] Actual cross-room owner counterexample031105112=111/1RED, retain player birth binding and currentenemy room rule; narrowfix031713/default031901112GREEN/v072. Full aggregate still below.

- [x] Bounded typed current-owner Capture/Validate inclpickup/rewards/audio/room/input: actual0655384GREEN→065641full122GREEN/v089. Existing owner primitives reused; pausedInstall/codec/newprocessContinue remain separate below.
- [x] Bounded aggregate cross-reference validation and transactional paused installation; actual4semanticRED/v095 → full126/v096 → extra primitive actualRED/v097 → narrowfix/full126/v098. Geometry reconstruction is separate from SpawnRoom/new-Run semantics; this does not complete disk Continue.
- [ ] Encode/decode complete canonical payload with exact IDs and known schema; wire semantic commits and existing generation store with failure retention.
- [ ] New-process normal-input Continue proof: mid-reload, pending equip, enemy action, live projectile/burn, consumed reward and revealed fog. Preserve original state and subsequent outcomes, then record/review real video before claiming Continue works.

## Separate art task (clean_frame_review prepares, root generates)

- [x] Prepare two opposite passing poses as standalone trials, canonical131 sole identity. Explicit support foot beneath pelvis and opposite knee/boot passing forward, no rear-kick substitute.
- [x] Preserve F/E before viewing; native requests140/141 only after input review. 141 static near-passing compatible;140 rejected as far passing. Neither imported or a completed cycle; next targeted hip/thigh correction keeps originals.
- [x] Targeted142 hip/thigh correction retained F/E before viewing; root+independent static far-passing compatible with141. Explicit green alpha v002 passes numeric QA; wrong-key v001 rejected preserved. No fullcycle/runtime acceptance.
- [x] Assemble the six original sources into a shared-scale source trial; v005 baseline and v008 native-cell-X registration retain originalorder/83ms. v006/v007 tool failures preserved; this is source assembly, not motion acceptance.
- [x] Import6source frames into independent72px UE lookdev and capture bothfacings (v001/E089);15uniqueoriginals actually reviewed. This closes import/recording only.
- [ ] Review continuous motion, stride/footlock and real movement/transition; fixed observation and selectedPNG review do not grant fullwalk approval.
- [x] EV048 keepgrotesque/boostarmorreadability; native146 assembledcompactarmor reference retainedE090, actualroot/peer reviewE091; noequipmentID/runtimecomponent acceptance.
- [ ] Produce separate sameidentity armor components and test72px darkground/facings/action continuity.

Incidental verified correction: bounded041814Knight endpoint actualRED → singlepostMoveXexhaustion →042628 old112+Knight113Success. Historical full116 then had3RunRewardsStage0Fail; that report remains preserved.

## Current continuation — rewards, exploration bank and aggregate

- [x] Actual legal reward fixtures0459013RED → stable reward owner/GM integration. Old Scene exit expected0 conflicts with actual5; readonly052607 proves other fields true, narrow old test correction checks actual5 before exit and preserves it.052952full116GREEN/v079, independent source/final reviews retained; no aggregate/Continue completion claimed.
- [x] Root bounded bank implementation/actualUE owner tests:0605392RED→0615461GREEN/Restore1RED→0616582GREEN/v082. CompletedTick originalReveal, exact per-room values and atomicRestore; HUD consumes Run authority, unbound lookdev unchanged. Visible running migration evidence and independent final review still required before whole integration acceptance.
- [x] scale_tests typed Capture/Validate: admittedbank2GREEN→061737aggregate4semanticRED; nativegeometry diagnostics preserved, exactresponse/defaultbuilder correction andnegativecontrols→0655384GREEN/065641full122GREEN. Scope isCapture/Validate only; finalindependentreview addedseparately.
- [ ] Root and worker: transactional paused Prepare/Install, complete codec and existing generation-store semantic commits, then actual new-process normal-input Continue and reviewed running evidence. Capture/Validate alone does not complete this plan or the full first-batch goal.

## EV048 Ready-only armor visible checkpoint — 2026-10-16

- [x] Native158/159 revised body sources and161/162/163 separate chest/shoulders with exact source-body split; actual24 newtextures/old917 unchanged, no equipment-ID claim.
- [x] Preserve v100/E164 actualfirst-usebody disappearance (3 of137Ready), add visible-pixel gate, startup24preload/targetedcompilewait/existingrenderflush.111349build0→111515full126GREEN, v1011399files/2798endpoints0diff, freshsameEnter/A/J5.80775s174obs175PNG/137Ready0visiblefail, nativeCRC/phase/stack/flush/decode; E165/E166/E167 retained, root and independent original-frame reviews.
- [ ] Match armor/body partition to actual159 first-attack six phases; then fullstates, three-stage/four-armors/20mix, sounds and actual equipment binding. Current Ready-to-attack armor disappears; full silhouette/motion acceptance pending.
- [ ] Complete codecs/disk semantic commits and new-process normal Continue. Bounded in-memory Prepare/Install is complete as earlier126 evidence; whole save plan remains open.

## EV048 first-cut armor and Codec checkpoint — 2026-10-16

- [x] Matching Primary1 six-pose body/armor42Texture and bounded actual72px dual-facing real-input trial; originalv103movie retainedE181/E182.
- [x] Canonical typed Codec transport: actual4RED→3GREEN1RED→narrow scalarNULfix→target4GREEN/full130GREEN; tests unchanged, currentv104.
- [ ] Art acceptance: far shoulder/chest, thin windup blade, continuous motion/grip/footlock, Primary2/3/allstates/actual equipment20mix, enemies/Boss/VFX/SFX.
- [ ] Existing generation-store full semantic adapter plus disk commit and fresh-process normal-input Continue; transport alone does not close the save plan.


2026-10-16 v107实际续行：SaveAdapter Stage0 140235编译0→140335真实4RED/12errors（v106状态14error旧文字另有erratum）；只生产CPP后141911编译0→142054四组GREEN→142409完整134GREEN，旧130名集保留/default134。v1071545files91947864B/3090current+frozen端点SHA0；旧146Source、美术5Source与983包和原v105剑50录像一致。独立审查实际4及10slot文件，不冒full134独立审查。run-only真实disk/head/fault/atomicPrepare/既有World原reload未来行为闭合；外层特殊metadata和badhead→下一commit未单测，pristine新进程Continue及完整D13未完。EV048 art：168源姿态拒绝；169标准6帧提取/真实掌心足底测量中，未导入/未接受motion，preview600≠kernel540保留。ledger169/window0081of24/remaining23/lifetime193/external0/费用未知。正式0/15active，下一pristine InitGame封门和独立Prepare，不削弱正常Capture目标前提。

2026-10-16 v113续行（EV048，无新人类要求）：实际full138及真正两个UE进程Run-only原装填继续通过，3178端点SHA0/E210152files2SHA0；完整D13/菜单/设备试听待。ArcB真实连续输入无Ready桥但旧身体/缺甲不接受；170短肘p1开手失败后171闭握六帧提取/测量完成/E208209，未导入，正在独立剑与三甲row准备。ledger171/window0083of24/rem21/lifetime195/external0/费用未知。正式0/15active。
