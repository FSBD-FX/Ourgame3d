# Independent Walk runtime review, 2026-10-18

This is a candidate/static review and RGBA measurement record. The reviewer did not
edit ActualSource, frozen Stage0/production files, tools, README/status/ledgers, UE
assets or media. No UE/UBT, import, native test or proof capture was run by this
reviewer. Root owns the actual compile/RED/GREEN evidence. No new diagrams were
created or viewed; the six individually viewed source originals were already
retained under E319, and their bytes were checked equal to F originals.

## Facts

* Production freeze SHA256 is `880be8718dd8e07b09d98bfa5ab815aa6f910991f80aa15be4e364b8c958b3a0`.
  Original three-test source remains 10389 bytes, SHA256
  `5324b45a5c5a2a7ce20d4253f0845ab7f3418c1d97d0fecd98b6b22039dd7007`.
* Stage0 test compilation omitted the header defining `FDungeonPreparedRun`,
  `FDungeonRunInstaller` and `EDungeonRunInstallGate`. The compile-only candidate
  adds one 36-byte include; removing it recovers original test bytes exactly.
  Compilation failure alone is not semantic RED.
* Both actual movement paths record actor endpoints after SetActorLocation.
  GameMode aggregates resolved microbatches; ordinary path distance is computed
  from accepted XY endpoints, not input speed*time or HUD positions.
* Capture and direct Restore reject open frames, unconsumed commits and numeric
  faults before output/owner mutation. Query writes Out only after its checks.
  Successful Restore clears transient witness data and retains saved animation.
  Owner/codec schema fields were not added. Reserved label validation distinguishes
  exact `walk_distance_v001` from legacy `walk`, and rejects unknown versions/case.
* The frozen three groups run legacy `walk` with the production profile pending.
  Their synthetic 120/.6 policy verifies numeric phase helper behavior only. They
  cannot certify configured new-label state or rendering acceptance.
* Actual old sprite metadata uses six 83-ms phases (0.498 s) and explicitly leaves
  physical body/foot roots unmeasured. Old engine pivot is (256,464), not a physical
  measured support root. Each image is 512x512; file and actual RGBA hashes and
  alpha>=128 boot-band coordinates are in `old-walk-rgba-measurement-v001.json`.

## Reasoning and corrective candidates

The blocking interval ownership defect is in frozen GameMode motion order. Its
Dodge.StepTo transitions the final interval endpoint to Idle before eligibility
is sampled. With held direction, the final positive dodge displacement can
therefore enter WalkDistance and its saved phase. `production-repair-v002` captures
player eligibility at the interval start before Dodge.StepTo and uses that value
for the committed interval. It changes no movement, collision, speed, body size or
action timeline. A new real Shift completion test retains accepted endpoint
distance while allowing WalkDistance only for the sub-float-ulp ordinary tail
after the dodge deadline. Root is validating this candidate separately.

The same sampling order preserves the other exclusions: air landing fails initial
physical eligibility and the explicit StartHeight/EndHeight test; hurt and legacy
armor expiry sample eligibility before timer decay; combat/skill completion is
advanced after motion; active uncancelled equipment action remains excluded.
Held/fresh cancellation occurs at the start boundary before eligibility, so the
normal movement after cancellation is legitimately ordinary. Endpoint skill
placement invalidates the witness instead of being published as ordinary motion.
These are static ordering conclusions, not new native passes.

The additional single configured-label group explicitly fails when Profile is
pending. With actual compiled profile plus initial actual preview flag, it checks
legacy clock restore/codec, first new-distance zero-based phase, exact saved
label/float codec, paused grouped installation and absence of placement witness,
restored continuation in a newly constructed target whose preview flag is absent,
and unknown version/case atomic rejection. It uses independent modulo from actual
endpoint distance and compiled P values, never a test policy override.

At the fixed old display pivot, apparent near-foot bottom-outline displacement
0→2 is 101.5 source pixels, and far-foot 3→5 is 92.5. Applying
`(72/416)/.65` and an assumed 2/6 cycle interval gives 81.08/73.89 world-unit cycle
proxies. The low-opacity/outline width uncertainty alone spans about 59–97 units.
Heel→sole→toe contact migration, unmeasured physical root and unknown continuous
stance add systematic error that this range does not bound. An art-tuned starting
value around 80, exploratory range 60–100, is defensible only with that label and
native visual iteration; it is not a physical stride measurement or confidence
interval. Directional physical calibration and foot lock are absent.

## Remaining blocking conditions and risks

1. Root must retain actual original-three RED, boundary RED before repair,
   repaired targeted GREEN and current full-registry result. No reviewer static
   assertion or standalone math executable can replace those records.
2. Profile must bind exact six closed-hand body partitions, matching LGT pieces,
   source/import receipts, actual Root/Grip/Axis and source/RGBA hashes. Root chose
   an explicitly art-tuned 80-world initial cycle rather than claiming physical
   stance. The original physical-stride wording in contract/required-art-input
   must therefore be superseded by a new retained version documenting that scope;
   original frozen files must remain historical. SourceClosureVerified can mean
   verified source/layer closure without certifying foot-lock or measured stride.
3. The new single configured-label test is still an uncompiled candidate. It needs
   a real pending-profile prerequisite RED, then actual configured GREEN and full
   registry verification. It changes the process command line only within RAII
   scope to test real flag removal; it never changes the immutable profile.
4. Both-facing actual moving proof must inspect every phase and exact draw stacks,
   clipping/blocked input, action/equipment transitions and save/continue. Root
   must review the retained recording before claiming visible completion. The
   existing historical Walk/Ready/combo proof cannot certify new configured Walk.
5. No continuous support-foot lock/root compensation exists. Six held poses and
   scalar world path length may slide, especially for Y/diagonal movement. The
   proposed art-tuned number cannot justify zero-slip or directional-foot claims.
6. The saved phase float accumulates rounding per microbatch. This candidate makes
   no bit-exact subdivision claim. Same versioned label must remain bound to the
   one immutable compiled profile; a later changed table needs a new label or a
   reviewed migration because existing saved fields contain no profile hash.

No further blocking defect was established in the reviewed motion/capture/label
paths beyond the interval-start dodge issue. That is a bounded static review
conclusion, not whole-game or full visual acceptance.
