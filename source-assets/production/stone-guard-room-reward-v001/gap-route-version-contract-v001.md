# Guard003 room/reward candidate contract

Facts: exact v127 before-source and design pins are in exact-before-pins-v001.json.
Current normal Scene is one hardcoded Knight. Bat/Guard public spawns are native
development seams. Rewards schema1 allows STN001/002/QA only and fixed five-coin
deaths; Guard Owner schema1 refuses DeathReported. Scene clear roots in its one
Knight, and CoinAllocation is only a pure largest-remainder calculation. The
original D07 RSEQ001 has six slots including three unavailable STN004 instances;
implementing that original template by relabeling Knight would be false.

Root approved the explicit new `NATIVE-FIRSTBATCH-GUARD-BRIDGE-V001` proposal.
It uses only native001/002/003, each a finite required slot and separate serial
group. This is a new three-enemy Bridge, not original RSEQ001 or the whole D07.
D07 capability_profiles give weights3/2/4. D08 reward-sources standard REG01-N03
gold quantity20 and BUD013 support the room-budget/largest-remainder method;
Root explicitly accepted applying20 to this new proposal. Its distinct source is
`RWD-NATIVE-GUARD-BRIDGE-V001-GOLD`, with full-manifest shares7/4/9. It does not
claim that the original six-slot node was shipped or paid twice.

Normal game route: URL `/Game/Maps/FirstRoom?DungeonFirstBatchGuardRoom`, Blueprint
StartFirstBatchGuardRoom, or the candidate .cmd/PowerShell launcher. No QA flag is
the sole route. Existing default/preview routes stay unchanged. Initial Knight
binds to the full plan before the first combat Tick. R starts a fresh Run; normal
Scene E/Enter room exit retires exact original objects and actors, then commits a
new finite plan in the same Run without resetting wallet/resources.

Future groups begin only after the prior actual settled death plus2s. `Warning`
means no actor/HP/collision/coin; deadline is `WarningAt+1.2`. `MaterializedAt`
remains-1 until native birth. Seeded anchor candidates are checked against native
body extents, bounds, barrier, live body overlap, actual player distance350 at
warning/220 at materialization, wall LOS, and current exact visibility>.05.
Materialization rejection returns that same SlotID to Future, clears WarningAt,
waits RetryAt=now+1, advances deterministic AnchorAttempt, then starts a complete
new1.2s warning after another valid anchor. Slot identity/share never changes.
The deterministic pool is a35-point room grid (seven X by five Y positions),
and each search visits the complete grid. This avoids a discovered edge-only
pool failure after the player actually moves to kill the second enemy. Blocked
searches remain finite:420 attempts plus at most one final complete-grid scan.
Retries have an explicit finite attempt bound leading to technical pause without
fake death/clear/refund. This is not the complete original D07 fallback/depth
protocol: the Bridge trigger is serial predecessor death, not RSEQ001 depth.

Native wake remains unchanged and may run during emergence; attack-start
admission additionally waits initial orientation1s and materialization+.6s, then
the original kernel owns full windup/shape/hit/IDs. At most one Bridge enemy is
alive/materializing, so its known actor/threat/special caps fit the D07 maxima.

Same-time damage drains before formal settlement or future admission. Player
death blocks new payouts and materializations. Each surviving-Run true native
death resolves a complete reward candidate before claiming/reporting its actor;
exact retries add nothing. Coin object allocation is once-only and wallet credit
remains the existing actual range/ground/LOS pickup transaction. Room clear needs
all three required slot terminals, not an empty current actor set.

Version boundaries: Rewards schema2 adds conditional RoomPlans fields in existing
explicit bound-run-v2. Old Rewards schema1 omits them and rejects nonempty plans,
preserving old V1/V2 wire fields. RootV2 is selected for a complete future Guard
plan even before Guard exists. Guard inner Owner schema2 is only a settled death,
cross-checked against the explicit valid schema2 reward owner; schema1 retains
historical local eligibility semantics. Root/codec/installer carry that context.
No kernel definition, native damage/hit IDs, HUD or disk-V1 code is changed.
Current DiskV2 already consumes exact Root2/BoundV2 through the normal codec; a
new two-process Bridge continuation proof is still needed before claiming it.

Root owns actual UE/UBT/native/proof. Candidate tests use genuine new FirstBatch
entry, fresh Enter, accepted native incoming-damage adapter (not a normal-J proof),
actual normal movement for pickup, and real grouped install. The three frozen
tests cover pending-plan RootV2 restore; the actual settled-Guard Owner2 and
post-pickup/room-exit continuation need Root proof or follow-up acceptance cases.
Root is separately adding world warning rendering/RenderedSlotID; this candidate
only supplies real Warning state and exact visibility gate, and does not claim
the ring is visible until Root records/reviews it. Enemy final art/audio and
complete normal-J encounter acceptance remain outside these unrun logic claims.

Admission: production-source contains9 existing candidates and4 new files.
Apply production-from-stage0-v001.patch to the frozen Room Stage0 baseline, then
copy four new sources. Root's concurrent feedback additions to GM.cpp/h must be
merged; never overwrite them with the full candidate copies. Original3 tests and
Stage0 remain frozen. All author writes are limited to this candidate subtree.
