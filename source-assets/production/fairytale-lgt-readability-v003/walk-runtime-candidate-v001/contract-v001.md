# Walk runtime candidate contract

This directory is a candidate only. Actual Source, UE compilation, native tests,
imports, proof capture, media, README and ledgers have not been changed here.

## Facts and chosen scope

The retained baseline is byte-pinned to v126-combo-161G in baseline-pins-v001.json.
The actual bound GameMode commits resolved movement itself while suppressing
MoveOnGround. Both paths must record the actor endpoint after SetActorLocation.
Three frozen new native groups exercise normal real input, actual Scene barrier
clipping, action/equipment transitions, and capture/install boundaries. Their
Stage0 implementation returns false from QueryCompletedGroundMotion; each group
is expected to stop at its first positive witness assertion. They have not been
compiled or executed by this candidate author.

The compiled runtime profile is deliberately unconfigured. The numeric native
fixture's 120-world-unit/.6-second policy is solely a calculation fixture, never
the production stride or an art acceptance. A verified art/marker input must
replace DungeonFairytaleSwordWalkDataV001.inl before Walk can be enabled.

## Motion, phase and save boundary

An ordinary ground commit records accepted actor XY distance after collision and
room-bound clipping. It does not use requested input distance, speed*time, a HUD
position, a screenshot delta or wall time. A read-only frame witness aggregates
all actual GameMode microbatches and binds RunGuid/OwnerId/RoomInstanceId/time and
the actual endpoint. Changed scope, an external placement or an intervening skill
movement invalidates that witness; it is not added as a stride. Enemy kernels,
dodge, airborne movement, primary/skill actions, hurt, death and equipment changes
do not contribute WalkDistance. Held blocked input can cancel an equipment
transaction as before, but its zero completed distance produces an Idle pose.

No new OwnerSnapshot, Codec or disk field is introduced. The explicit new saved
AnimationName="walk_distance_v001" uses the existing float AnimationTime as
equivalent cycle seconds under ONE immutable compiled Gait profile. Legacy
AnimationName="walk" retains historical wall-time semantics. Accepted ordinary distance advances the new label by the
fraction of CycleDistance; six explicitly authored durations select the image.
The clock is reduced before division and never converted to an unbounded int.
All non-Walk action clocks retain their existing update paths. The new label
begins only in bound SWD with the explicit new Walk preview flag and a verified
profile. A restored new label continues distance semantics under the same frozen
profile even if presentation opt-in is absent. A legacy "walk" save is restored
exactly and its first actual opted-in distance starts the new label from zero;
its saved wall-time is never used as a cycle phase. When a verified profile is
unavailable, existing movement/animation behavior remains but the new selector is
closed. A saved new distance label without its verified profile, an unknown
walk_distance_ version/case, or inconsistent ordinary ground state is rejected
atomically. Entering new Walk from a different animation starts its phase at zero
plus the first completed distance; leaving Walk enters
the existing next-animation clock. No second hidden Walk phase is retained.

Pending distance is process-local staging, not persistent state. Both owner
Capture and direct owner Restore reject while a ground frame is open, a motion
commit is unconsumed, or a numeric fault is present. Actions commits consume the
pending distance into Walk AnimationTime or finish the existing transition to a
different pose before clearing it. BeginFrame never erases a previously pending
public MoveOnGround commit. Successful Restore retains the saved animation and
clears only transient staging/witness data; failed Restore changes nothing.
Install gating cannot tick the saved phase or publish placement as movement.
Reset/restart/room relocation reseed or invalidate the transient witness.

The actual current Owner validator checks AnimationTime only for finite/nonnegative
values (DungeonFighter.cpp:143-147), has no AnimationName allowlist, and imposes no
AnimationTime<=SimulationTime bound. Codec.cpp:727-728 encodes those same named
float/string fields without interpreting them. Therefore the explicit label is
enough to distinguish semantics without creating a codec/schema migration. The
new reserved label's added validator does not tighten unrelated legacy labels.

The saved clock is a float, as in the current schema. Numeric standalone phase
calculations use doubles, but runtime phase equality is bounded by float rounding
and microbatch conversion. This candidate does not claim exact bit equality of
all frame subdivisions or compatibility between builds with different compiled
stride/marker tables. A future changed profile needs its own explicit versioned
label or a reviewed migration; the final snapshot must bind the one profile source.

## Presentation and preload

The added DungeonFairytaleSwordWalkPreview opt-in requires the actual committed
equipment-bound resolver. Existing Ready/P1/P2/P3 opt-ins retain their selectors.
Walk uses six phases and explicit paths for Body reference plus four exclusive
body partitions and three matching leather pieces. A phase emits either:

* SWD with no armor: BodyRest, NearArmWithoutHand, HelmetForeground, SWORD, NearHand.
* SWD/LGT: BodyRest, ShoulderFar, Chest, NearArmWithoutHand, ShoulderNear,
  HelmetForeground, SWORD, NearHand.

Whole Body is a source/reference readiness pin, never an additional emitted
body layer. NearHand closes over the independent sword. All eight component
references in every phase preload before the existing editor texture compilation
and startup render flush. Every texture/resource and marker is checked before
any draw quad; a missing resource has no old Walk/Ready/gray-armor fallback.
The existing sword uniform scale .50 and single facing mirror remain unchanged.
The body canvas remains 72*512/416; no combat/body scale changes are proposed.

## Measured stride input and limits

Actual DungeonHUD.cpp:295-296 projects local ground as
Ground=(640+.65*(WorldX-CameraX),490-.38*WorldY), then
Screen=Origin+UIScale*Ground. UIScale=min(viewWidth/1280,viewHeight/720), with centered
Origin (actual lines 1562-1563). A source sprite pixel projects at
(72/416)*UIScale. Jump display adds -.70*JumpHeight*UIScale in screen Y.

For a verified fixed-root contact moving along pure world X, a measured source
contact displacement d pixels corresponds to d*(72/416)/.65 world units over that
contact interval. A full CycleDistance additionally needs that interval's known
cycle fraction and verified same-foot stance. For direction u=(ux,uy), ground
projection magnitude per world distance is sqrt((.65*ux)^2+(.38*uy)^2), but the
side-view source contact trajectory cannot automatically prove a longitudinal
or diagonal stance with that scalar substitution.

Distance-phase fixes blocked empty walking and uses real completed path length.
It does not provide continuous support-foot locking, root compensation between
six held images, directional foot anchoring, audio contacts, or proof of zero
slip. Those remain separate measured design and native visual acceptance work.

## Root handoff sequence

1. Preserve the frozen Stage0 tests/headers/patch and compile the false witness
   stub in actual Source; run the three groups and preserve real clean RED.
2. Review/admit the production candidate patch and new sources with the identical
   test bytes. No actual Native GREEN is claimed by this directory.
3. Fill the profile from the retained closed-hand Walk assembly, matching LGT
   armor receipts, actual Root/Grip/Axis, six phase durations and measured physical
   stride. Re-freeze that new table and rebuild all changed translation units.
4. Run native groups and the current exact full registry (161 is the historical
   baseline; concurrent DiskV2 adds 3 and Walk adds 3, so 167 is only a projection).
   These three frozen logic groups run without the new art preview flag; they
   preserve legacy "walk" controls while the profile is pending. New configured
   label/profile state and visual framing still require additional real native
   acceptance cases; this candidate does not claim those unrun cases passed.
5. Make new proof tooling/capture with exact current Source/DLL/profile/assets.
   The existing Combo/Ready/P1 historical proof does not certify new Walk art.
