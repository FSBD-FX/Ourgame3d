# Ranged and spear normal-input running proof

Date: 2026-10-15 (Asia/Shanghai). This opt-in QA fixture supplies running evidence for the already implemented weapon adapter. It does not certify final art/audio, production loot, balance, D13 persistence, or complete first-batch content.

## Facts, decisions, and limits

XBW001 has one bolt: J lasts .68 s and its ensuing full reload is 1.10 s; K emits at .55 s, lasts 1.15 s, pierces at most two targets, and applies .6 damage/stagger to the second. STF001 J spends 10 Focus on a magic fireball without intrinsic burn; K spends 24 Focus on a ground rectangle with center range 240/depth 35, followed by fixed 2 damage once per second for 3 ticks on each positively damaged target. SPR001 K has independent nearest-one windows [.18,.22), [.28,.32), [.38,.42), each 12 damage/6 stagger and center range [45,240]/depth 16. Generic QA enemies have zero Armor/Ward. Expectations derive from existing definitions and real ranged tests, never from drawn projectile overlap.

Right selects fixed weapon slot 1. Replacing slot 1 twice would lose the staff before the requested final Q back to it. The legal route is XBW into empty slot 1; after both shots and full reloads, Q to starter slot 0; staff E then fresh Enter explicitly replaces current slot 0, retaining XBW1; later spear E/Right/Enter replaces backup slot 1, retaining staff0; Q activates spear1, K performs three thrusts, then Q returns to the same staff0 with its actual absolute cooldown and Focus history preserved.

Sources are explicit RegisterEquipmentSource fixtures: XBW with initial one-bolt magazine at P0+(32,0), staff at P0+(60,0), spear at P0+(95,160). P0 is the actual position at the genuine BeginEquipmentRun(IntegrationPreview,1) boundary. Three ranged targets start at P0+(180,0), +(270,0), +(360,0), each 400 HP; three spear targets at P0+(185,160), +(245,160), +(305,160), each 12 HP. Enemy arrays deliberately list farther actors first. AI is disabled and HP/position configured only at initial creation. No attack, hit, live HP, armor, ammo or Focus write is used. All subsequent actions use UnitMove/UnitPulse controller edges.

After staff J, ordinary D approaches P0+(100,0), with actual distances checked before K: first two targets inside 240, third outside. Ranged targets survive all intended hits, preserving a nonempty room. Spear targets die one per independently reselected thrust without fixture movement between windows. Approach arrival tolerance only controls normal movement; production distances and event receipts remain unchanged.

The fixture has a strict 45 s capture deadline and 6 s per phase. It is mutually exclusive with FirstUnit/Explore, Equipment, ArmorLayer, and ArmorCombo proofs; root owns flag dispatch/rejection. Audio counters prove actual HUD PlaySound requests only; listening and mix quality remain separate.

## Wiring contract

- Flag: DungeonRangedWeaponsProof. Profile: ranged_spear_adapter_normal_inputs.
- Include DungeonRangedProofState.h before DungeonContentProbe.generated.h; add FRangedProofState RangedProof, bool bRangedProof, and void TickRangedProof(). Include DungeonRangedProof.inl beside other proof implementations.
- FRangedProofState::RequiredChecks() is the authoritative 20-name list; each must appear once and pass.
- Dedicated phase/timestamps live in RangedProof.Phase/PhaseAt. Reuse existing input edge fields, Elapsed, UnitFailure, Trace, Results, input helpers and audio lifecycle. Key traces should label RangedProof.Phase.
- Record real world journal sequence/keys/times/HP losses, projectile/window facts, burn phase/ticks, action/instance IDs, ammo reservations/refills, Focus receipts, crit cursor, equipment selection/commit, target HP/position, HUD texture paths and release/launch/burn sound request counts. These observations do not approve presentation.

The fixture author runs no UE/UBT. Root must compile, run, preserve F/E media, inspect report/recording and repair genuine fixture failures before calling this proof complete.

## Initial source handoff

The candidate is 27 finite phases and 20 unique required results. Static name coverage found no missing required check; that is a structural check only. The independent reviewer checked the complete source, center-distance/slot arithmetic, resource history, burn expiry and journal counts. Root reported the initial candidate compiled successfully and the retained actual automation suite remained 52/52 with no warnings/errors, but this does not yet prove the new running profile.

- DungeonRangedProof.inl SHA-256: f3f8ef8e0e17efc4d1e48bb5fe7e0a4032cca05cb39e5f5bd7dd77f359dfdf17.
- DungeonRangedProofState.h SHA-256: 6abc9af082bc6854ec595f11e9a0b1b5e5fcad42f2a82a8d36af7b1f7059d7ab.

The full successful journal would contain 3 projectile emissions, 4 skill windows, 9 direct HP-loss commits, 6 burn HP-loss ticks, 2 Focus emission receipts, and 2 XBW refill receipts. These exact totals are checked against real journals at the end, never synthesized by this fixture. XBW/STF audio requests are observed through the existing HUD getters; spear audio has no equivalent dedicated request getter, so its three world windows and actual runtime recording are retained without inventing a per-cue counter.

The source review identified a concrete false-green gap in the initial fireline check: counting two direct commits did not independently validate each direct HP loss. Root authorized a minimal later revision, without changing the 20 required names or the original tests: each intended target now requires one magic direct commit with actual HP loss matching the real issued payload (the existing .0002 floating-point HP tolerance), matching stagger and exactly one BurnApplied; the third target must retain 400 HP and have no direct commit from that action. Initial compiled v021 evidence is not relabeled with this later source.

Current strengthened DungeonRangedProof.inl SHA-256: d24f3a12ea692ae84ebb41f76ef4fd740b854459024dea9f1dad3965abef9b57. The state header remains 6abc9af082bc6854ec595f11e9a0b1b5e5fcad42f2a82a8d36af7b1f7059d7ab. Root compilation and first normal-input recording of this strengthened revision remain pending. No UE/UBT was run by the author.
