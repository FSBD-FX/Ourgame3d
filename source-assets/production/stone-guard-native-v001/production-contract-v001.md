# STN003 native production candidate v001

This is an unapplied native integration candidate after Root's real Stage0 UE RED. It is not a completed enemy content unit. The author has not run UE/UBT, imported assets, changed ActualSource, or captured media.

## Concrete behavior

- ENM-STN-003 is the large ordinary two-handed stone-axe Guard, not a shield unit or renamed generic chaser. The admitted pure kernel owns185HP,60physical armor,15ward,85poise,160movement; body and projectile-hurt half extents are separately read as40×28.
- GameMode admits a real Fighter into the current Run/room and stable entity binding before initialization. Spawn requires an open run gate, a live bound player and a valid position. It uses the existing central SimulationTime and native game tick; there is no new RNG, owner clock, reset-based restore or fabricated combat state.
- Direct incoming damage is mitigated once by the existing combat rule. The incoming-only Driver API commits the actual clamped HP loss and monotone receipt at the current clock without consuming outgoing hits while the PendingDamage batch is closed. Central accepted hit batches perform the same once mitigation, apply all Guard incoming receipts before pumping its windows, and skip generic HP/iframe/push handling.
- Driver value-copy staging keeps its state unchanged on rejected StepTo. Its immutable issued windows, locks, cancellation/death and once target receipts come from the Guard kernel. Actual native wall LOS,40×28body sweeps, frozen Fighter trajectories and separate projectile hurt extents are used. The Actor position, HP and phase mirror are synchronized from the kernel after accepted central steps.
- A1 uses1s windup/0.5s lock/0.2s active/1.4s recovery,24physical/30stagger, forward180×±65. A2 uses0.9/0.45/0.15/1.5,18/25, center ellipse160×90. The warning/wake is1s; mirrors and native procedural warning geometry read real state. No active blocking/shield was invented.
- Death yields only a once local eligibility API and one death observation. Formal reward allocation/consumer is intentionally not connected: no5coin fallback, no settlement flag, no room-clear. Repeated dead ticks do not repeat the death message. Current unknown Guard snapshot owner remains rejected by the unchanged Fighter/Aggregate/Installer boundary.
- HUD adds one early Guard-only procedural rock/two-handed-axe/telegraph placeholder and a real hit-flash tint, then returns before the old generic enemy sprite and sword effects. This is not authored Guard animation, completed VFX, SFX or audio evidence.

## Apply order and baseline

1. Root already admitted the frozen Stage0 headers, Driver and3tests. Preserve all3test bytes and header interfaces.
2. Replace only the new ActualSource DungeonStoneGuardDriver.cpp with candidate-source/DungeonStoneGuardDriver.cpp. Its h is byte-identical to Stage0.
3. Apply patches/production-after-stage0-v001.patch: four existing CPP files only, Fighter/GameMode/WorldProjectiles/HUD. git apply --check currently exits0 against Root's actual Stage0. The HUD is one isolated hunk so concurrent visual work can be manually rebased; do not overwrite complete existing files.
4. Root should refresh copied-source mtimes without changing bytes, compile, run CodexDungeon.Content.StoneGuardNative3 first, then the actual full suite. Expected total with Root's independent allocator3 would be154, not an author-observed result.

## Evidence and unchanged contracts

Root actual build-editor-20261016-235751.log exit0 and FirstRoom-20261017-000138/index.json registered3, failed3, succeeded0, errors3, warnings0, notRun0, inProcess0. Each error is the honest null Spawn stub. Actual Run/room and native LOS/wide-sweep positive premises ran before that failure. The frozen tests remain14672B/SHA406892b287684c00e753b39e36c8eee62722e68717af37a53c6b23bb3732a93d.

All13 files in the original Stage0 manifest are rehashed unchanged. The entire Fighter owner Capture/Validate/Restore prefix preceding InitializeStoneKnight is byte-identical to Stage0; no Codec/Store/Adapter/Installer/reward implementation is patched. Independent source-only seam review found no definite API/type or new shadowing issue, but is not a compiler or native GREEN result.

## Remaining limits

- Actual native build and all3positive integration groups have not yet run against this production candidate. Their failure details must be preserved and corrected without weakening frozen tests.
- The existing native LOS search policy is retained: exact geometric entry is tested, then at most16samples/64bisections seek later clear admission. Every accepted point is queried again natively, but a very brief clear interval may be missed. This is not exhaustive moving-occluder topology proof.
- Driver rejection is state-atomic, but this minimal integration follows the existing batch ensure/zero-loss pattern on an unexpected rejected frame. It introduces no full GameMode rollback/retry protocol or technical-pause recovery. Long-run history-copy cost and bound exhaustion have no performance acceptance.
- The candidate exposes specific hit/wake/axe/stomp/recovery/death phase tags; authored sprites, frame transitions, final telegraphs, audio/SFX, complete statuses/forces, formal drop settlement and serializable Guard owner/restore are still incomplete. Unknown/untested behavior is not accepted by this handoff.
