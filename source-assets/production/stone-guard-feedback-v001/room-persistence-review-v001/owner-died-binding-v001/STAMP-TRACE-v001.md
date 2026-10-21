# Original Guard death stamp binding, candidate v001

Facts

Root build100944 actually completed77 actions with exit0. Actual full FirstRoom-20261018-101315 has174 GREEN/2 RED,0 warnings: feedback3 GREEN; original Room Future failed to materialize Guard (fixture waiting bound); new settled regression accepted the different legal late-death kernel (one TestFalse failure). `actual-RED-input.json` pins the original report and exact two errors. This reviewer did not run UE/UBT.

Normal J: DungeonGameMode.cpp ResolveAttack queues PendingDamage with AtTime=SkillBatchTo. That is the current accepted subbatch endpoint. Direct public Guard ApplyCombatHit outside a simulation batch calls the native driver zero-span resolved-hit entry at existing Guard.State.Time. Both ordinary paths usually have Died at the local endpoint. This is an explanation of those source paths, not a claim that every native damage source must share that endpoint.

General accepted contact path: CommitPendingDamage keeps each original H.AtTime in Guard FIncomingHit, builds one actual driver StepTo(SimulationTime, Frame, Hits), then SyncStoneGuardState and OnFighterDied. Driver StepTo accepts ordered original hit stamps between its old State.Time and Now; it steps each receipt at its exact stamp, appends all issued events, and ultimately commits State.Time=Now. Kernel ApplyHits emits Damaged/Died at that current receipt time; Emit copies S.Time into immutable E.AtTime. The enclosing Room OnFighterDied defers formal settlement while bSimulationBatch is true. AdvanceFirstBatchGuardRoom runs after the complete same-timestamp damage transaction, so the current State.Time is not an intrinsic death timestamp.

The real unchanged pure Guard kernel was compiled/run locally to verify this distinction: a legal185HP receipt at0.125 in StepTo0.4 gives unique Died.AtTime0.125 and final State.Time0.4; full native kernel Restore accepts it. This is NOT a UE/OnFighterDied runtime proof. Local source and output notes are under local-stamp-check. It demonstrates why exact Owner binding must also choose the original Died source for actual payment, rather than add a tolerance or force clocks.

Inference and minimal change

Current Bridge Settle Q.AtTime reads Guard.State.Time. For a legally accepted earlier receipt inside a driver interval this can pay at a later endpoint. The candidate changes only Guard payment clock to its unique original Issued.Died.AtTime, retaining existing source entity/room/content/position and no reward before complete batch survival admission. Knight/Bat payment and all legacy paths remain untouched. Missing or duplicate Died sources refuse settlement before any reward candidate publication.

Settled inner GuardOwner2 still requires an internally valid same-Run Rewards2 owner. Its existing same entity/room/content death match now additionally requires unique native Died and exact original timestamp, plus Death.Position==saved native GroundPosition. The original pure kernel Restore, bound context and native component projection checks remain. Guard corpse position does not advance after Died. The native body may retain a coordinate within SceneComponent update tolerance relative to high-precision kernel position; the patch compares the paid body position to saved native body position and does not tighten that existing kernel projection tolerance.

Scope and risks

Two small production hunks only: Fighter owner validation and the new Bridge runtime inl. No full Fighter/GM replacement, kernel edits, clock advance, schema change, codec/wire edit or old V1 migration. Old unsettled GuardOwner1 and legacy Rewards1 behavior skip this new Owner2 binding. The real176 suite, including current settled and legacy-wire checks, must be rerun by Root. Original paid Bridge snapshots that actually used a later endpoint rather than their Died source would be rejected; this unaccepted new feature has no migration added by this candidate.

Apply settled-guard-died-binding.patch (combined two files). Individual owner/source patches are alternatives for inspection, not additional patches to apply twice. git apply --check is exit0 on the pinned actual merged source. Apply fixture-admission-v002.patch separately: it only splits the same absolute After+3.21 wait into<=2-second pieces and moves through X300 lower lane before the inherited Y80 exit waypoint. All original assertions and the late-death rejection remain unchanged. The originals and both prior freeze versions remain intact.

Root follow-up validation: compile actual merged source, exact FirstBatchGuardRoom4 + StoneGuardFeedback3, then full176 with zero errors/warnings/notRun/inProcess. Device timbre, true two-process Bridge disk continuity and normal-J visual proof remain separate work; this patch does not claim them.
