# Guard wholebody partial trial v001

This is a Source candidate, not an accepted enemy or a UE result. Root baseline is v128 / 213 Source / 1210 Content / 176GREEN as reported by Root. Worker did not run UE, UBT, import textures, view new media or change actual Source/Content/tools/README/status. Pure actual DungeonStoneGuard.cpp C++17 selector Stage0 compiled exit0 then semantic RED exit1; production selector compiled/run exit0. These are kernel selector checks only.

## Root admission order

1. Preserve this freeze. Stage0: copy `stage0/DungeonFairytaleGuardPose.h` to actual module; copy production `DungeonFairytaleGuardProfile.h` and `DungeonFairytaleGuardDataV001.inl`; copy the identical `stage0/DungeonFairytaleGuardPresentationTests.cpp` to module `Tests/`. Do not apply HUD patch or presentation cpp in this stage. Compile, then run exact filter below. Each of three groups should fail its first selector witness after legal kernel preconditions. Record actual results; no claim of three native RED has been made here.
2. Production: replace only Pose.h with production header, add DrawState.h / Presentation.cpp, apply the minimal two-file HUD patch. Profile/Data already present. Keep the same automation tests. Only candidate files are supplied, never a complete HUD/Fighter replacement.
3. Root independently retains/imports the 16 exact source PNGs in `registration-proposals-and-import-map-v001.json`. Namespace proposal `/Game/Production/FirstBatch/GuardWhole_v001/{Ready,Wake,AxeWindup}/T_Guard{209,210,212}_{Clip}_{00..}`. Ready4 + Wake6 + AxeWindup6 = 16 unique textures; Dormant adds zero. Suggested import: PNG RGBA untouched 512square, UI compression, mipgen NoMipmaps, sRGB true, alpha preserved, bilinear filtering, NeverStream true. Root must verify actual loaded texture object paths, dimensions and source-to-import provenance; a 64-character pin in Source does not itself prove import bytes.
4. Create a NEW independent Root trial-registration record with exact source hashes, evidence hashes, per-frame pivots, row scale and scoped purpose. In actual admitted Data rows set `TrialAllowed=true`, record nonempty `TrialApprovalRecord`; leave `FinalAccepted=false`. Default candidate values are false. Approval is for opt-in trial only, final unit acceptance needs actual recorded world transitions and play review.
5. Build and run the same3, then full expected179 (176 old +3 new) if no other Source was added. Run a real world trial with `-DungeonFairytaleGuardPartialPreview`. No flag means no candidate load/draw. Flag alone plus closed registration also draws no candidate sprites.

Root commands from F:/Ourgame (not executed by worker):

```powershell
pwsh -File .\tools\scripts\unreal-build.ps1 -Target Editor
pwsh -File .\tools\scripts\test-first-room.ps1 -TestFilter CodexDungeon.Content.FairytaleGuardPresentation -ExpectedTests 3
pwsh -File .\tools\scripts\test-first-room.ps1 -ExpectedTests 179
git apply -p0 --check --ignore-space-change .\source-assets\production\fairytale-guard-v001\presentation-candidate-v001\patches\minimal-HUD-partial-trial-v001.patch
```

`git apply -p0 --check` passed against the independently pinned current HUD on worker freeze. Apply only after Stage0 evidence and merge any newer Root changes. Stage0 Pose header is an intentional empty selector, not a production fallback. Candidate tests exercise actual kernel producers plus compiled presentation policy; they do not create a Canvas and cannot certify actual sprite submissions, imported assets, complete animation or visible fit.

## Registration and geometry

ONE body-only standing-equivalent scale per row: Ready 100.8/415 (canvas124.3604819277), Wake100.8/398 (canvas129.6723618090), AxeWindup212100.8/273 (canvas189.0461538462). Raised axe alpha never defines crown/height; natural per-frame body compression is preserved. Per-frame pivot source pixels: Ready X=[235,234,244,236], Wake X=[242,239,233,239,237,242], Axe212 X=[242,241,253,268,273,292], all Y464. These come from independently pinned measured visible shoes, rounded midpoint; they are presentation support proposals, not bones, COM or foot-lock proof. Ready old [256,464] is rejected as physical foot pivot.

For source width W, floor pivot (Px,Py), shared row scale s and projected native ground G: right Top=(Gx-Px*s,Gy-Py*s); left Top=(Gx-(W-Px)*s,Gy-Py*s), UV U=1,DU=-1. Apply existing Screen/UIScale after this calculation. Current square FActorQuad is retained; non-512square assets explicitly fail gate instead of stretching. The fixed axe and both grips belong to ONE source layer. The successful branch returns before the old procedural axe/body. Existing finite Guard feedback draws once after wholebody, and renderer never emits audio.

## State authority and exact gaps

- Dormant uses explicit Wake0 resource alias, no invented frame.
- Wake six authored offsets0/.167/.333/.500/.667/.833 from actual WakeStartedAt, interval ends actual WakeEnd.
- Ready four1s artist-loop phases from kernel Time-WakeEnd. It cannot cover a missing action.
- Move six phases from sum of actual immutable accepted Movement XY lengths, cycle128world. A positive Movement at current completed kernel boundary is required. Wall/no-move/paused elapsed time cannot advance gait. Existing feedback journal64world stride emits native footstep crossings at move phase3/0; renderer creates no duplicate footstep.
- AxeWindup212 uses real Action.Start / ActiveAt and latched facing. Native211 entire row is rejected. AxeFollow and all Stomp rows are explicit gaps with exact requested clip retained.
- Ordinary positive Damaged receipt permits recent material tint only. Poise85 real PoiseBroken / StunUntil owns Stunned .4. Stunned art and InterruptedRecovery art are gaps.
- InterruptedRecovery selects only after actual stun ends, only while interrupted original action is unfinished and Time < original OccupiedUntil. No extra Active or extended occupied deadline.
- Death derives from original unique Died event; only existing terminal game-over presentation may additionally use Fighter.AnimationTime. Death6 art is a gap. The v002 Death visual eye amendment and collapse standing-root propagation remain separate art review, not silently implemented by this candidate.

Known available but unadmitted later art: Stun213 / Death214 metadata from art agent; this freeze does not turn them on. Death2+ pile support points must not be silently used as paired feet or actor root; preserve actual collapse translation with a separately approved standing-root registration.

Any missing row, closed trial record, failed all-frame load, wrong dimensions, wrong actual object path or invalid native selection records an explicit `MissingReason` and `ProceduralFallback=true` in `GetFairytaleGuardDraws()`. It then renders the existing actual procedural003. This is deliberately visible in proof metadata; it does not declare all Guard rows complete. There are 54 unique requested images in 10 real rows plus Dormant alias;16 sources are mapped here and38 remain unregistered.

## Real capture gates; normal native time only

Prefer the actual formal room URL option `?DungeonFirstBatchGuardRoom` (InitGame reads the URL option, not an invented CLI flag). Normal Enter starts; normal combat clears Knight and Bat; native future warning1.2 + admission creates Guard slot2. Existing `DungeonGuardRoomFlowProbe` automatically kills Guard about.9s after its birth and has a diagnostic public damage scope, so its unchanged capture is too short to prove full Wake/Windup. Do not label it full normal-play or reuse its old scope string as an art acceptance report.

For manual trial use the formal room and ordinary controller keys with the partial flag. Keep player outside native Wake ellipse and do not hit during initial Dormant capture; anchor birth only guarantees >=220world, so inspect actual phase rather than assuming Dormant lasts. Camera visibility and safe floor route must also hold. If native birth is already Waking, report Dormant unobserved; do not freeze the kernel to manufacture it. Approach through normal A/D/W/S into the actual235x110 wake ellipse, keep no J hit, and collect all six Wake frame IDs from actual draws before WakeEnd. Move into an actual axe-admissible distance (> extremely-close70 to avoid Stomp, <=180X and <=65Y with LOS); capture Action.Kind=AxeSweep, phaseWindup and all actual six native offsets. Remain at safe normal attack distance or dodge the actual active area. Active/Recovery will be procedural gaps in this trial. Ready follows actual completed action; a single idle window may be shorter than a1s art loop, so collect across real repeated intervals instead of holding the clock or extending cooldown. Both facing trials require ordinary player movement to opposite sides through a legal route; no enemy teleport. Show feet/crown and the exact SourceFrame / ONErowScale / SourcePivot / mirrored TopScreen.

A fallback dedicated public-spawn setup may be useful only if formal-room timing makes a state unobservable; it must disclose one public SpawnStoneGuard outside formal wave obligations, use actual normal Enter/controller input and native GameMode ticks, and cannot claim formal spawn/reward proof. No manual Tick/StepTo/SetState/SetActorLocation/AnimationTime override in a real capture.

Real proof should serialize `GetFairytaleGuardDraws()` after completed DrawHUD: DrawId, exact entity/attack/event IDs, kernel sample/interval clocks, accepted distance, requested/asset clip (Dormant alias), actual object path and source pin, SourceFloorPivot/TopScreen/GroundScreen, TrialAllowed/FinalAccepted, DrawStack and MissingReason. Successful actual wholebody DrawStack must contain exactly one actual Texture2D path, with no independent axe/grip submission; all missing states must preserve their requested clip and explicit procedural gap. Existing native async CRC/FIFO capture should bind report observations to original frame offsets. Preserve all media in E before View; record silent viewport separately from already imported trial sound playback, never claim recorded audio without capture.
