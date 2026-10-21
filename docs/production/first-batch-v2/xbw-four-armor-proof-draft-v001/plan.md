# XBW four armor recorder draft implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans when the root opens a Source window. This directory is a reviewable draft and is not compiled or connected.

**Goal:** Record four actual armor instances acquired through normal inputs, with both facings of XBW ready6/primary6/reload4 and real immutable hand-origin emissions, under one 55-second deadline.

**Architecture:** `State.h` owns observations and exactly 29 unique required check names. `Proof.inl` supplies `ADungeonContentProbe::TickXBWArmorSocketProof()` and expects a `FXBWArmorSocketProofState XBWArmorSocketProof` member. The future root connection owns the flag, header/include, dispatch, report profile and PS capture routing; no Actor, HUD, combat kernel or existing normal20 behavior changes are proposed.

**Tech Stack:** UE5.5.4 existing ContentProbe input pulses, equipment transactions, Actor/World read-only snapshots and HUD last-draw observations.

**Spec:** Root-approved independent 29-gate scope in the 2026-10-15 task message. Existing contracts: `DungeonXBWReloadSocketProof.inl`, `DungeonEquipmentRuntime.h`, frozen primary/ready/reload/lifecycle manifests and the four-armor import manifests.

## Global constraints

- Only phase0 initializes one IntegrationPreview Run, starter SWD, one QA XBW Ammo1, four QA armor sources and two non-AI generic targets with initial HP2000. It restores one start gate for the normal fresh Enter.
- After phase0, only ordinary Enter/E/Tab/A/D/J input changes gameplay. No SelectEquipmentSource, live transform/HP/armor/ammo changes or direct attack/hit calls.
- All five sources start at the same legal `Origin+(32,0)` anchor; actual Tab cycles to the intended SourceId, including when replaced armor creates extra ground sources. E is issued only after the actual source is displayed and settled; replacement armor requires a separate fresh Enter with default slot2.
- The original armor and instance remain held throughout each actual .50 pickup. Weapon/Run/Room identity stays fixed; all armor and projectile IDs are real allocator outputs.
- Masks count only actual HUD draws, with prior draw time preserved. No synthetic frames. Exactly eight mandatory shots and at most two additional shots globally; missing frames after this budget fail.
- Exactly29 gates: common3 + per armor6×4 + final history1 + deadline1. This is separate from the no-armor20 profile and all independent Actor automation tests.
- No UE/UBT from this owner. Draft files remain outside Source until root authorizes the connection and runs verification.

## Read-only findings and risks

Facts: normal Tab uses `CycleEquipmentTarget`; occupied armor E sets SelectionSlot2 and does not start an action. Normal Enter starts .50 armor pickup. The six required draw paths are body_far → armor_far → independent_weapon → body_support → armor_near → body_near. All three armor contracts remain source runtime_verified=false / semantic_full_armor_acceptance=false despite successful imports.

Inference: eight mandatory direction samples need 8×(1.1 ready+.68 primary+1.10 reload)=23.04 simulation seconds, plus2 seconds of armor transactions, fresh-key gaps and turns. Two global repeat shots add3.56 action seconds. A55-second wall deadline allows ordinary capture overhead, but does not guarantee every20ms active pose gets a draw; failure is retained rather than expanding the budget.

Risks: initially overlapping sources need Tab; dropped old armor changes the cycle. A prior GPU draw can belong to the old armor or action, so the recorder requires draw time at/after the current armor pickup deadline and matches historical action identity. Armor-specific movement speed changes the small real A/D turns; target range is measured from each immutable actual Actor anchor and is rechecked. Initial HP2000 prevents ten legal shots from exhausting a target; it is never healed. This proof establishes actual six-layer use, clocks, resources and sockets; it does not accept full garment coverage, walk/skill/air states, all20 equipment combinations, mechanical art, sound quality, formal sources or D13.

## Review focus

- Wrong highlighted source: wait for actual intended ID or fresh Tab; never silently E the closest item.
- Occupied armor: opening E must expose slot2 without action; only a later Enter starts pickup, old identity held until deadline.
- Stale draw: match HUD instance/action/sample time and exact six paths; count no inferred frame.
- Reload state2/3: visual images cannot refill; require original1.10 duration and exactly one actual ReloadCompleted receipt.
- Retry/history: at most10 real shots, each exactly one ammo spend, emission, hit, stop and refill; retained emission snapshots survive later armors.

## Connection and actual validation sequence

- [x] Read real Tab, armor transaction, clip clock and draw path APIs; create the isolated State/Proof draft.
- [x] Root reviewed frozen draft and opened the two-file producer Source window after the no-armor20v002 capture/F-E/26raw reviews finished.
- [x] Root connected independent `DungeonXBWArmorSocketProof` flag / `xbw_four_armor_socket_normal_inputs` profile, state member and tick dispatch, mutually exclusive with every other proof. Required existing HUD flags are `DungeonCandidateSprites`, `DungeonWeaponBodyPreview`, `DungeonXBWReloadBodyPreview`, `DungeonArmorLayerPreview`; the reload flag already enables primary sampling. Capture at60fps as the existing no-armor20 does: primary active poses each last20ms, so30fps is not an adequate default for the two-shot global retry budget.
- [ ] Root compiles and runs strict83 first, preserving source/DLL provenance. No old test or no-armor20 gate is changed.
- [ ] Root records the independent29 profile with actual draw masks and normal keys. If a fixture or actual behavior fails, retain the failed report and diagnose before changing it.
- [ ] Preserve F/E originals and presentation copies, verify all frame CRC/audio-video gates, inspect both facings of each armor's ready/primary/reload, then append actual results and remaining visual defects.

Source reference hashes: ready armor manifest `093d6b15a44dadc485b28584784c888b2df7f1a88261891632ef836e128925a1`; primary `0acc811b8633f8d3b165ea588ad38c8f95372f4bd13ab37ec7ece7174ecc0a82`; reload `963d74e304894088492b205fb9b113b0e5b6d9acf52785724c6d400271722002`; lifecycle `94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe`.

Static self-review: checked actual DTO names against World/WA/Equipment headers; initialization mutations occur only in phase0; actual gate expansion has29 unique names and every suffix is implemented; C++ delimiters balance after comments/strings are removed. Independent ranged_review found no concrete blocker in normal Tab/slot2/.50, stale-draw exclusion or the two-retry bound. These are static checks, not UE compilation or a29-pass claim. World/Fighter/GM remain respectively `0bc43aaf55c8576b93f8fde87cd8db92f04153d682ba332aa2620ac547687fb9`, `e36cc2915b1367057f32e25054eb6356c37e4569cddc3d619738afaa52df9a60`, `930d3ae95684e8f8893b507e394f65daf00beef4fa740c7d2fff1285651bd3e6`.

Root connection snapshot: root-hook-source-freeze-v001.json. Producer Source State62b580/Proof731838 adds real ActionSpeedPct/ReloadSpeedPct0 gates for these four unenchanted ARM001; no armor property mutation. Current root build handle75284 is live; no compilation/83/29 outcome asserted yet. Earlier no-armor20Source/DLLv042 and F/E originals remain separate.
