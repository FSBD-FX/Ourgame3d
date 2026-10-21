# Hero landing priority native proof implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Prove that normal grounded J/Shift admitted during original landing preempt nonattack Air and render their real equipped actions in both facings.

**Architecture:** Add one opt-in native observer class with a J/Shift CLI case. It observes completed native screenshot callbacks and uses real Controller.InputKey queues, the existing game simulation and native capture/audio helpers. Keep it separate from the frozen three-jump scenario and all gameplay code.

**Tech Stack:** UE5.5.4 C++, Python/PowerShell, existing PNG/Submix capture.

**Spec:** F:/Ourgame/docs/superpowers/specs/2026-10-19-hero-landing-priority-v143.md

## Global Constraints

- Source296/Production1419/CM52f906/strict full203 is the admission predecessor. Preserve every old assertion, frozen candidate and failure.
- Root alone mutates actual Source/Content/tools/E/ledger/UE. Workers own NEW candidate files only and accommodate others.
- Original630/1800/.12/.70/72px, inventory/save and action timing are unchanged. No actor/HP/HV/clock repair.
- Existing valid LGT binding and brown Ready/Primary flags required; no None Dodge substitution.
- F/E exact retention before View. Actual playback and listening remain distinct from decode/PCM checks.

## Review Focus

- First rendered action may follow enqueue by a Tick: verify real input and actualStartTime within landing, not synchronous InputKey output.
- Completed Land4 and action draw must be fresh same owner/run/epoch; stale HUD Tick data cannot satisfy proof.
- J/Shift preemption must make Air return false with unchanged Out and submit zero Air parts.
- Left dodge can meet a real wall: choose a valid route by normal movement, retain actual collision outcome, never reposition.
- Every capture/Stop/PNG flush/audio sample needs its real timeline; metadata-only success does not pass.

### Task 1: frozen opt-in observer candidate

**Files:** Create in `source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001/new-source/`: `DungeonHeroLandingPriorityProbeV001.h` and `.cpp`. Prepare GameMode include/spawn/exclusion and HUD proof-capture exclusion fragments separately; Root combines them, no whole shared file overwrite.

**Interfaces:** Consumes existing Fighter/GameMode public queries, HUD actual Air/legacy/Dodge records, Controller.InputKey and `DungeonNativeMainSubmixCaptureV001`. Produces normal-input/physical/action/draw/capture runtime JSON with scenario and J/Shift/facing parameters and explicit OPEN fields.

- [ ] Read actual API types and existing capture/priority kernels; declare exact CLI flags and JSON protocol before implementation.
- [ ] Implement Enter/E/completed-brown-Ready/Space/completed-Land4/queued-J-or-Shift/action/Ready2 flow, no fixed sleep or physics writes.
- [ ] Audit source: fresh callback identities, real actionStart in landing, no old proof co-run, no hidden player/Guard writes.

### Task 2: independent host native verifier

**Files:** `landing-priority-observer-candidate-v001/tooling/verify-landing-priority-native-v001.py`, protocol and meaningful small negative cases.

**Interfaces:** Consumes actual fresh Root prereg/compiled manifest/runtime/capture files; emits exclusive-create independent JSON, never UE execution or approval.

- [ ] Pin synthetic causal cases: queue vs immediate, wrong owner/epoch, stale draw, actionStart at/outside .12, Air partial draw, wrong armor/clip and absent Ready2. Demonstrate rejection before completing verifier.
- [ ] Reuse immutable PNG/audio/geometry/source provenance functions where compatible; record exact dependencies and real frame mappings.
- [ ] Freeze source/checker/negative-case results and handoff; Root independently reviews exact delta.

### Task 3: Root actual native integration and review

**Files:** Actual `UnrealGame/Source/CodexDungeon/DungeonGameMode.cpp` registration and `DungeonHUD.cpp` proof exclusion plus the two admitted observer files; Root-owned new launch/prereg/evidence paths only.

- [ ] Preserve current stable preview before Source admission, review/backup/admit exact frozen source; derive actual new count rather than guess.
- [ ] Build and run `tools/scripts/test-first-room-native-rhi-v001.ps1`; strict203 Success, zero warnings/errors/notRun/inProcess.
- [ ] Record four fresh PID cases with all brown-armor flags and independent verification; preserve every failure.
- [ ] Prepare complete native AV/adjacent action joins, F/E before View, review actual poses and update README/ledger/status. Do not count this as a complete unit or claim unperformed playback/listening.

Execution follows the user's existing automatic authorization and active goal; no commit or external publication is requested.
