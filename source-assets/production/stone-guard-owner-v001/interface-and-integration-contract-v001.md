# STN003 native owner / Codec continuation draft v001

Status: concrete unapplied design and delta drafts against current v124 core sources, not Stage0-admitted, not a frozen test package, not compilation or native acceptance. Only this new asset family is written. Root owns actual Source/UE/UBT/Store execution. The pure Restore author owns the independent Guard kernel changes.

## Facts, inference and risk

Facts: current FDungeonFighterOwnerSnapshot has only Player/Knight/Bat variants (DungeonFighterSnapshot.h14,71–75). Fighter.cpp111 accepts only owner schema2;136–142 binds exact Run/room/entity/content;362–364 captures Guard as Unsupported. Guard's full FState includes33fields and five histories; its private FPolicy is separate (DungeonStoneGuard.h33,86–103,128). Native policy currently defaults70, and kernel constructors accept finite [0,160] (DungeonStoneGuard.cpp79–81). Restore must not choose70 again for a saved custom value.

Inference grounded in the actual paths: merely adding a Guard optional to the Codec cannot produce a sealed Run. RunAggregate.cpp238 feeds every current actor to RunRewards, whose155/169 whitelist also rejects a live003. A minimal current-room unsettled-actor admission is necessary; formal death allocation and historical retirement remain separate.

Risk: mutating bound-run-v1's required fields globally would invalidate old canonical bytes and frozen tests. Another risk is equating pure RewardClaimed with native DeathReported; on Guard the first is already explicitly only local death eligibility, while GameMode.cpp2255–2269 leaves formal settlement false. This draft preserves both facts and never invokes the old fixed5coin rule.

## Exact proposed interfaces

Pure dependency, agreed with /root/guard_kernel_review: FPolicy CapturePolicy() const; bool FGuardKernel::Restore(const FState& Saved). Restore validates complete state against the receiver's immutable entity/InitialTime/InitialPosition and preserves its constructor's validated Policy. No StepTo, ResetForNewEntity, BeginCombat, heal or event emission. No new static Validate API is required: an independently constructed pure candidate performs validation.

Native Driver keeps the existing3argument constructor for normal births. Add an explicit5argument constructor(Owner,EntityId,InitialTime,InitialPosition,SavedPolicy), CapturePolicy() const and Restore(const FState&). Restore delegates to the already correctly bound pure receiver; it never reads current weak-owner geometry or a live GM. Staging can therefore construct a native Actor still at its independent default position, restore kernel values, and publish the saved native transform only after every validation succeeds.

FDungeonFighterOwnerSnapshot appends Kind StoneGuard without renumbering old kinds. Guard-only owner schema3 contains exactly one new optional wrapper:

- FDungeonStoneGuardOwnerSnapshot.Schema=1;
- Policy.ExtremelyCloseRadius as original finite IEEE double, including a valid custom value;
- Kernel: the complete Guard FState, every scalar, Window, Closure, outgoing HitReceipt, incoming ReceivedHit and Issued event in original order;
- DeathObserved: the native once-observer flag bGuardDeathObserved, not settlement or a sound-playback receipt.

Player/Knight/Bat remain owner schema2. Exactly one variant is present; Guard binds actual ENM-STN-003, current room stable entity and enemy team. Native HP185/max, passive defense60/15, facing and40×28body are not reconstructed from a generic enemy. The native body XY and precise kernel XY retain the existing explicit native-position projection predicate. Full State HP/Time/Poise/dead facts must agree with native mirrors. LastDamageReceiptId and complete ReceivedHits remain unchanged, so the next normal native accepted receipt uses exactly saved last+1 and actual once-mitigated HP loss.

At a stable Guard capture LastGuardSyncTime must equal Kernel.Time. It is a derivable consumed boundary, so Restore assigns it to the saved kernel time without a new payload field. Native display fields/actual HeightAnchor/CustomMuzzle are already fully saved and must be copied unchanged; do not call SyncStoneGuardState during restore because that could change animation age/native tiny-transform facts. The draft explicitly clears any old StoneGuard pointer when restoring a different variant.

## Wake, death and feedback continuation

Aggregate already saves LastStoneWakeStartedAt; add Guard.WakeStartedAt to its cross-owner lower-bound check. Guard's WakeQueued/CombatStartedAt/WakeEnd and all event/cooldown/action clocks are in the copied Kernel. No notification is replayed while preparing/installing. Native DeathObserved is restored before opening the gate, so an already-dead Guard neither rewrites LastMessage nor notifies other enemies again on every tick.

There is currently NO Guard feedback journal or Guard audio consumer: AcceptGuardBatch only updates wake throttle and queues real hits (GameMode.cpp2458–2464). DungeonStoneFeedback::FJournal is typed to Knight events (DungeonStoneFeedback.h7–9,26). Therefore no fake Guard seed is added to Audio.StoneSeeds; its existing exact Knight-only cardinality remains. Full Guard Issued history/NextEventId is saved as producer state, and a future real Guard consumer must attach at saved NextEventId without replaying Issued. Any future Guard audio journal requires its own tested consumer/type/schema; this slice does not pretend that consumer exists.

Guard Kernel.RewardClaimed is retained verbatim even when local eligibility was consumed. RewardContext carries that true raw flag, and the new current003 branch permits it separately from DeathReported, requiring no formal Death record and no premature alive eligibility. The old EnemyContent whitelist, ResolveDeath, fixed5validator, retired003 rejection and normal room-clear contract remain unchanged. No actor or binding is omitted to make sealing pass. Current003 may survive disk; historical003/room transfer remains fail-closed until the real allocator/settlement consumer is connected. This is a named current-owner capability boundary, not completed enemy rewards.

## Explicit version plan

Recommended root discriminator: old complete roots remain Schema1/BoundDevelopmentV1. A root containing a current Guard is Schema2/BoundDevelopmentV2 (append scope value, no enum renumber). Old owner schema2 is unchanged. New Guard owner uses3. Capture detects current Guard; Validate forbids cross-discriminator mixing.

Codec old bound-run-v1 remains the exact old field set and canonical bytes, including no Guard field at all. New bound-run-v2 adds a mandatory Guard optional field on every fighter, explicit null for legacy variants. Every Guard field is required, unknown/duplicate fields are rejected, enums are explicitly bounded, arrays stay ordered, and all current transport/typed allocation/UTF8/finite IEEE/decimal-string limits remain. Document must read codec before traversing snapshot, and bind wireversion to root schema/scope. Decode re-emits through that same native root discriminator before Aggregate sealing. The provided03draft implements that exact dispatch, not a permissive v1 upgrade.

Disk recommendation (not implemented in these patches): keep existing BoundRunOnly-v1 context/writer/header/envelope unchanged. Add an explicit BoundDevelopmentRunV2 context in independent BoundRunOnly-v2 namespace, adapter=bound-run-only-v2, scope=BoundDevelopmentRunV2, exact versions=(bound-run-generation-v2,bound-development-guard-v2,world-cm-v1). Both namespace/version triples must be bound to decoded root type; no automatic fallback, empty owner, in-place old generation overwrite or silent migration. The Store transport algorithm and highest-head/no-fallback logic need no change. Existing v1 loads must still pass; v1 writer must reject Schema2 instead of silently using old descriptors. Root can approve native-owner first and diskV2 next, but must not call Guard disk Continue complete between them.

Concrete Adapter hunks needed next: add DirectoryNameV2 and explicit scope; ContextValid chooses exact suffix by scope; VersionsMatch/HeaderValid choose exact triples by scope; RunMatches enforces rootSchema/scope against context; Prefix/Suffix use the explicit adapter/scope string; MakeGeneration chooses VersionsFor(Context), while ValidateGeneration reconstructs the exact matching envelope around Codec's full decode. Commit/Load retain the SAME mandatory callback for both new and existing head and preserve all Out/disk atomicity. No permissive callback and no forward-version relabeling.

## Draft files and apply order

01-native-owner-draft-v001.patch: Snapshot variant/wrapper, native Driver staging interfaces, Fighter pure validation/Capture/Restore. Depends on the independent pure Restore/CapturePolicy implementation.

02-root-current-reward-admission-draft-v001.patch: explicit new root schema/scope, complete Guard wake check, actual local eligibility in both RewardContexts, current003-only no-settlement admission. It does not modify death allocation or historical retirement.

03-codec-versioned-fields-draft-v001.patch: full9Guard value structs plus wrapper and version-dispatched exact schema. guard-wire-field-map-v001.json lists all33State fields.

04-staged-guard-exact-readback-draft-v001.patch adds one new value-only header and one CheckGroup guard. It compares every Guard scalar/history/policy/observer readback, including signed-zero IEEE bits, before group publication; no padding memcmp. Installer's existing hidden/collision-off/staged lifecycle, normal target Capture prerequisite, pristine gate and failure RAII remain unchanged.

All four together pass read-only git apply --check against current ActualSource. That is not a build or authority to apply. These drafts intentionally leave diskAdapterV2 unimplemented and have no registered tests. Do not admit as a completed production package; Root first admits the independent pure Restore Stage0 and obtains actual clean RED/GREEN, then defines native-owner Stage0 with honest support stub and frozen real-flow tests.

## Minimal next test matrix (proposal, no source/tests frozen)

1. Native owner and failure atomicity: real public bound Run + admitted Guard, real Tick/damage to capture rich windup/lock/active/recovery/stun/death states; assert complete independent signature and exact transforms. Wrong room/entity/content/kind/multiple variants, invalid policy/birth/history or future root time must preserve Out and preexisting native owner pointer/content. For a genuine custom native policy fixture, add optional policy to public InitializeStoneGuard/SpawnStoneGuard in that Stage0; no private pointer writes or fabricated source snapshot.
2. Codec compatibility: keep every existing v1 test/oracle unchanged; actual no-Guard Encode bytes equal its old oracle. Real captured Guard uses v2 and exact all-fields independent oracle; v1-with-Guard/v2-with-old-discriminator/missingPolicy/unknownfield/duplicateescapedkey/receipt or closure tamper must fail atomically. Pure Restore tests own exhaustive state semantics; native tests also check historical target IDs against real saved World bindings.
3. Whole install/Continue: actual rich source Capture→Codec→real IO v2 Store→fresh Store/objects→Decode sealed→existing or native pristine Prepare→Install. Readback matches full Guard producer signature before publish. AwaitExplicitContinue keeps original clock/deadlines/HP/IDs; neutral fresh Enter resumes the old active/recovery boundary with at most one outgoing hit and next incoming receipt exactly last+1. Already consumed hit and dead-observer events never replay. Corrupt highest head never falls back; invalid staging/releases preserve current target/no extra Pawn and old published disk bytes.

Actual source/render/audio/media/ledger/progress are unchanged by this work. Formal complete units remain unchanged. Numeric state validity and visual/audio completion are separate required evidence.
