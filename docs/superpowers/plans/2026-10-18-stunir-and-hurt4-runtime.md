# StunIR and Hurt4 Runtime Implementation Plan

> **For agentic workers:** Use executing-plans or subagent-driven-development task by task. Root owns actual Source/Content; workers own separate candidates.

**Goal:** Verify real-J Guard Stun/InterruptedRecovery and integrate the reviewed SWD/LGT Hurt4 assets without replacing equipment or gameplay timing.
**Architecture:** Separate read-only observer from production presentation. Reuse real Fighter state and committed equipment binding, with explicit texture profiles and deterministic source transforms.
**Tech Stack:** UE5.5.4 C++, native automation and retained viewport PNG/video.
**Spec:** docs/production/first-batch-v2/continuation-v133.md and frozen StunIR-v004/Hurt32 profiles.

## Constraints and review focus

- Preserve Source/Content versions and failed evidence; no gameplay time/HP/poise writes by probes.
- Real J must face inward and land inside the existing melee ellipse. Exactly one real break owns Stun4/IR4.
- IR SourceEventId0 is legal; original occupied end remains unchanged.
- Hurt has five body owners plus three armor layers and one reused independent sword; only FarHand1–3 are explicitly empty.
- Real state/float boundary, incomplete texture rows, equipment replacement, mirrored attachment and paused restoration must be verified. No final art/audio/full-unit claim from compilation.

## Task 1: Actual StunIR

- [x] Verify frozen Source4 and current v133 inputs; admit two new observer files and minimal HUD startup patch.
- [x] Build Editor, run the actual full184 suite and freeze the new compiled inputs.
- [x] Fill source-profile and combat Root preregistrations from those inputs; capture one fresh left process.
- [x] Diagnose real failures without weakening the original clocks or receipts. Retain and review original eight state frames and video before accepting this milestone.

## Task 2: Actual Hurt4 presentation

- [x] Test the real Hurt/committed-equipment production selector before implementing the new presentation path.
- [x] Add a read-only real-state query, complete32 profile and HUD preload; preserve nine slots/optional empties and independent sword.
- [x] Prove actual RED→GREEN, full regression, real damage, both facings and return-to-Ready. Preserve pose/buckle residuals separately from runtime correctness.

Actual Death-v006 also compiled/full184 and normal-J native left PASS; media/review pending. Hurt Stage0 six files plus narrow query admitted; real semantic RED still pending actual compilation/test.

Death native left original1s6phases and normal automatic coin verified, Root actual visual review recorded with hard pose joins/placeholder markers still OPEN; E460–E462. Hurt Stage0 compiled and three intended semantic RED retained, native32 import PASS1286; production candidate in progress.

Task2 functional/native milestone passed: actual3GREEN/full187/Source246+Production1286 snapshot2172, realAxeHurt bothfresh processes359/388,4phase+Ready/Walk/sourceoptical/quad32+Sword verified; E463–E468 actualRoot review. Art fit/no-pop/audio/fullunits stillOPEN. Next: remove the default world-range debug rectangles acrossfull/partial/procedural, then Dodge/Death gear and GuardMove/Stomp.
