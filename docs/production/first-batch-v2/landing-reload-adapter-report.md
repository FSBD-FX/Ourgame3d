# Bound airborne crossbow landing reload clock

Date: 2026-10-15 (Asia/Shanghai). Narrow investigation only; the complete first-batch content goal remains open.

## Read-only baseline

- Authoritative UE report: `UnrealGame/Saved/Automation/FirstRoom-20261015-080108/index.json`: 52 succeeded, 0 succeededWithWarnings, 0 failed, 0 notRun, 0 inProcess.
- Frozen source/assets: `source-assets/production/backups/2026-10-15_ranged-endpoint-UE52-GREEN-v018` (root-reported 544 files).
- Frozen `DungeonWeaponActions.h` SHA-256: `e5a24e9e1637aacd17ac85232a6e3954bd16a4b39ae1febfa5cb253ec581fa3e`.
- Owned source copies and their hash manifest: `docs/production/first-batch-v2/evidence/2026-10-15_landing-reload-v001-081233/`.

## Facts

D02 `jump` specifies a 0.70 s flat flight, forbids airborne reload, and requires landing to preserve the accepted primary timeline and attack/subhit identity. The existing crossbow primary lasts 0.68 s; its last shot can complete while airborne and set `AutoReloadPendingId`.

The bound actor's motion batch currently notifies `WeaponSkills.NotifyLand()` before the weapon clock advances. After old world damage has committed, `AdvanceWeaponSkillTo(ToTime)` calls `StepTo(ToTime)`. Its opening pending-reload branch starts at the old `S.Time`, which is the interval's earlier endpoint. `NextSimulationBoundary` already includes the current height/velocity ballistic root; this investigation does not require replacing physics or widening tolerances.

`WeaponSkillContext` also derives grounding from `JumpHeight <= KINDA_SMALL_NUMBER`, while the kernel receives its landing notification only at actual zero height. A very small positive height can therefore disagree with the kernel and make `StepTo` reject that context. The independent actor counterexample records both clocks so that this cannot be mistaken for a test-only timestamp error.

## Inference and risk

The real actor counterexample reproduced the early start/refill in `UnrealGame/Saved/Automation/FirstRoom-20261015-081524/index.json` (SHA-256 `c90bb0bc865ca0d86541e9c11b8ff75f3547ba399fdde487e408526c659a5e9d`): 51 succeeded, 1 failed, 0 warnings/notRun/inProcess. The sole failed group is `CodexDungeon.Content.RangedWeaponsAdapter.AirEmissionUsesActualHeightWithoutDownAim`; its three errors are the early start, early refill, and wrong refill-receipt time. All first-grounded observation prerequisites passed.

Immediately before landing, game time was `1.7500000080812781`, WA time was `1.7449999996647239`, height was `1.59857479e-15`, and vertical velocity was `-630`. The first actual grounded batch was `1.7500000080812783` with landing age zero. Reload incorrectly started at `1.7449999996647239` and ended at `2.8449999996647239`; the required full landing-relative end is `2.8500000080812784`. This confirms both the premature grounded context and the old-clock pending-reload start. Root then authorized the minimal correction. Its actual-RED backup `source-assets/production/backups/2026-10-15_air-XBW-landing-actualRED-v019` retains the original `e5a24e9e...` header, independently hash-checked here.

A candidate repair now applies bound weapon grounding at the post-damage endpoint, with explicit validated clock ordering, preserves active air primaries and all existing resource/event identities, and measures the full 1.10 s reload from that endpoint. Snapshot patch/restore, refunds, epsilon-time workarounds, stat widening, and movement-distance widening are excluded. The previous samepoint `InterruptAt` correction remains unchanged.

## Candidate implementation and standalone checks

`FWeaponActionsKernel::LandAt(Now, AirContext)` rejects nonfinite/backward clocks, invalid or already-grounded contexts/states, duplicate landing, and attempts to skip an earlier real lock/emission/action-end deadline. A copied live kernel advances through the endpoint using the pre-landing air context; only then does it set grounding and start any legal pending reload at `Now`. It installs the candidate only after full state validation and returns the actual events. An action still active on landing keeps its accepted start, air-start flag, end, action ID, reservation, and event cursors. No persisted field or version changed (`FState.Version` remains 3).

The bound actor defers both old motion-time WA notifications, retains the kernel's real grounding in its context through endpoint damage, and invokes `LandAt` only for actual zero height and zero vertical velocity. The old unbound QA notification path remains available. `InterruptAt` thus still sees the legal pre-landing context during samepoint damage and can clear an empty pending reload or preempt an unemitted attack before landing is committed.

Separate opt-in `Tests/DungeonWeaponActionsLandingStandalone.cpp` was run first against an explicit rejection-only `LandAt` stub: compile exit 0, 43 checks / 23 expected failures, runtime exit 1. The completed candidate yields 43 checks / 0 failures, compile/runtime exit 0. Coverage includes full landing-relative reload and last representable time before refill, unique action/event/ammo/Focus/crit identity, active air primary persistence and valid capture/restore, exact lock/emission/action-end landing, invalid clocks/contexts/deadline skips and atomic retries, and damage/death before samepoint landing. It exercises real kernel behavior; no fabricated snapshot is used to obtain a positive result.

Unchanged original tests also pass freshly: 179/0 and endpoint 45/0. All three standalone sources compiled using MSVC C++17 `/W4 /WX`. The new test translation unit preprocesses to empty without its opt-in macro. Logs, the RED stub, unchanged test copy, candidate source copies/diffs, and hashes are in the evidence folder above. No UE/UBT was run by this subagent; the root owns the fresh actor build/run.

Candidate freeze:

| File | SHA-256 |
| --- | --- |
| `DungeonWeaponActions.h` | `e8d6d2366c26b87eecc14b660b8020b31a4e7c674c7256479a536ba8d2b91586` |
| `DungeonFighter.cpp` | `4e7dda66120687bdd5cfa5c1fce058676e18e58b6dd8704a305bcf155260b6db` |
| `DungeonGameMode.cpp` | `8ec527b159d9bf0b2a034850237e570e52b885dc5db17f12e77339d49b75d1c6` |
| New landing standalone | `38b6e57b939e9c19134ea7d4c5f271794d09950d9b594b9621826f904f74e393` |

Original pure 179/45 and the independent UE test source remain untouched. The UE test SHA remains `88fecbea5fa633f22dabd060e457e080f1e52bcfc77a51a94e01dc2f1e6046b3`.

Independent ranged reviewer read the frozen candidate, checked the deadline guards/atomic install, active-air identity, post-damage ordering, real zero-height muzzle, and the retained test hashes/logs; it reported no new concrete P1/P2 finding. Actor GREEN remains pending at this checkpoint. This narrow correction does not certify art, complete first-batch content, D13 disk persistence, or final gameplay acceptance.
