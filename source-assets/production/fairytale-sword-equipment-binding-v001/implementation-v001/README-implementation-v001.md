# Resolver implementation candidate v001 — not admitted or run

Root actual `build-editor-20261016-191250.log` exit0 → `FirstRoom-20261016-191319/index.json`: 3 Fail / 11 errors (Transactions6 / Installed3 / Graded2), 0 warnings; every error is an implemented-binding positive call against the two honest Stage0 false APIs. The original fixture failure remains preserved separately; corrected MED replacement / original LGT re-pick now pass their real public Slot2-confirm premises. This report was independently read, not rerun by this agent.

This candidate implements only the existing public resolver interface. Header is byte-identical. Frozen corrected tests (19798B / SHA174593b8…8877) are unchanged and actual Source still contains Root's Stage0 stub. Root may admit only the new CPP from this version for actual targeted3 GREEN; no result is claimed yet. No HUD/Presentation/flags/draw changes in this version.

## Read-only behavior

Resolve checks game thread; live native actors; same actual World and AuthGameMode; authority; real Game.PlayerFighter; nonenemy/nonstone player; current committed inventory; current WeaponActions equipped ID and active weapon-action instance. It does not infer authority from a supplied bool. Then the same ValidateCommitted used by tests checks RunGuid and nonzero run/owner/room/revision, native schema, matching owner/revision/active slot, all three committed slot IDs, unique relevant owned items, versions/content and slot copies, selected grade/enchant/quantile validity using existing Stats rules, exact Fighter mirrors and current SWD Melee/action owner/timeline.

NoArmor needs genuinely empty armor inventory, slot and mirror. LightArmor needs the actual ARM-LGT-001 item/version. Other legitimate armor is explicitly unsupported; wrong/stale equipment is diagnosed rather than turned into None/LGT. Graded, beneficial, mixed and cursed valid gear uses the same base identity. Backup weapon may be any legitimate existing weapon family: it does not gain a SWD skin or alter the active selection.

Neither pending/selected source nor install gate is used to authorize another item. The actual committed old gear remains eligible during a pending pickup; a valid already-installed AwaitExplicitContinue remains statically resolvable. There are no BeginRun/Restore/Commit/clock/RNG/ID/audio mutations. Success builds a local FBinding and publishes Out once, then clears Diagnostic. Every failure changes only Diagnostic.

MatchesItem reuses real Stats validation/OriginalQ mapping, not a new roll or balance implementation. This is bounded rendering eligibility, **not whole Inventory history or Profile validation**. It checks all displayed/committed slots and unique items for those IDs; it intentionally does not replay the entire Run's operation history each draw. Actual Inventory and Aggregate remain the authoritative history owners. Whole codec/installer/static pause equality belongs to the existing real test control. Native current fields used for rendering are finite and range checked; no extra mutable cache or saved schema is added.

## Static review and remaining scope

Guard active slot before indexing; empty slots cannot retain stale values. Definition lookup precedes conversion of known catalogue ContentId. Affix count must equal the native TArray count before size_t→int32 indexing; known quantile/range rules validate each affix, including negatives. Inactive historical Melee action can belong to the older weapon, while active action must own the current SWD instance. The actor check precedes reading its state and pure seam cannot authorize a World by itself.

Static local delimiter/header/test/SHA checks are not C++ compiler or test results. Root alone builds/runs targeted3 and regression. Current P3/HUD/Presentation source work is independent. Actual same-draw Bound-mode consumption/flag priority/currentV003/prewarm/draw proof remains future work: implementation here does not claim art integration, lawful drops/shop, full unit, UI/audio acceptance or full D13. Formal goal remains active0/15.
