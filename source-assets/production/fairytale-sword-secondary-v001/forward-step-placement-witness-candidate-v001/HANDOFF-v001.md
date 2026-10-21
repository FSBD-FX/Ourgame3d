# Actual ForwardStep placement witness candidate

Candidate only. 3 existing projected files, 5 strict insert ops; Source303→303, no new Source/test files. Actual Source/Content/tools/E/status/ledger untouched. Use exact-seams-v001.json against pinned baselines, compose with later Root runtime changes; do not overwrite current files wholesale. Every original byte is recovered exactly by removing only the 5 inserts. Original motion/de-duplication/audio scope/eligibility/Append and window logic remain byte-identical.

API: `bool ADungeonGameMode::QueryWeaponForwardStepPlacementV001(FDungeonWeaponForwardStepPlacementV001& Out) const`. On false Out is reset. The latest member is private/transient; DTO in existing DungeonWorldProjectiles.h. No serialization, new event ID/sequence, timer, motion, sound or damage call.

Producer sits in the existing de-duplicated bound ForwardStep branch after real SetActorLocation/SyncWeaponMuzzleTransform and existing AudioBefore/AudioAfter reads. It uses the real E EventId/SubhitId/ActionId/InstanceId/AtTime/requested signed distance and current actual Run/Room/Owner. `CommittedDelta=AudioAfter-AudioBefore` even if zero; Present=true does not depend on nonzero movement or audio. GroundedAtCommit, ActionStart, current existing SimulationTime, RunPresentationEpoch, RunRestartSerial and observed equipment revision are captured as provenance. Revision is not a frozen-version validation gate.

Observer must read the real getter every callback WHILE THE SAME ACTION IS STILL ACTIVE and save its own local snapshot. Getter rejects ended/interrupted/new actions, dead owners, changed scopes, restored presentation epochs, restart serials and inconsistent real event cursors. It intentionally cannot return a value at/after End. Compare full genuine event key (including Run/Room/Owner/epoch/Action/Instance/Event/Subhit/AtTime) against the expected real emission and de-duplicate locally. A successful lookup is the latest fact for this active action, not proof a new placement occurred in this callback. Getter failure or absent audio is NOT evidence of zero.

Existing private Fighter BatchSkillStepAt/Delta is a batch accumulator without event key; QueryCompletedGroundMotion only covers ordinary movement. Neither is reused as fake zero evidence. No existing same-event skill placement getter was found.

Restore invalidation uses existing CommitPreparedRunGroup RunPresentationEpoch increment(.cpp354); new run uses existing RunGuid and RunRestartSerial increments(.cpp513 / legacy2122); room exit changes existing room ID. No new reset hooks or lifecycle state machines. Raw field sources and exact boundaries are in field-sources-and-lifecycle-v001.json.

Bounded source-contract checks verify strict inverse, zero has no delta-positive filter, no producer audio/motion/ID/clock side effects, lifecycle guards, and exact preserved original blocks. Per latest Root instruction no new test files. No host C++/UE compile or native full/partial/zero claim. Root independent review, exact-seam composition, actual build and native checks remain required. Actor observer v001 blocked-zero remains HARD_NOT_READY until a NEW observer consumes actual getter; its separate first-run route gate must use explicit exploratory mode, not invented verified=true.

FinalAccepted=false, runtime_ready=false, actual_source_modified=false.
