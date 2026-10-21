# Equipment-bound sword candidate — Stage0 v001

Only this new source-assets family was written. Nothing has been admitted to Unreal Source, compiled, run or visually accepted. The resolver is intentionally **honest false stub**; it changes Diagnostic only and preserves Out. Root owns UBT/UE and must distinguish compilation/fixture failures from semantic RED. This follows the approved two-stage TDD handoff; implementation follows actual clean semantic RED, not a static assertion that tests would fail.

## Intended admission (only three new files)

- `candidate-source/DungeonFairytaleSwordEquipmentBinding.h` → `UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordEquipmentBinding.h`
- matching `.cpp` → module root
- `candidate-source/Tests/DungeonFairytaleSwordEquipmentBindingTests.cpp` → module Tests

The test includes the existing immutable `Tests/RunCodecFixture_v001.h`; its actual Scene / ordinary Enter fixture and independent signature are reused. No test modifies that fixture, old tests, runner, GM, Installer, Codec, Store or Adapter. The only explicit QA registration is actual existing RegisterEquipmentSource; this proves committed inventory transactions, **not lawful drop/shop availability**.

## Public contract

`Resolve(const ADungeonGameMode&, const ADungeonFighter&, FBinding&, FString&)`: production authoritative actor/world entry. It must independently check actual AuthGameMode and Game.PlayerFighter, then use committed owners. This API must reject wrong actor/world and unsupported committed armor/weapon; it must not mistake the pending source for equipped gear. It does not begin/reset a Run, consume RNG/IDs, write equipment, alter clocks or open Continue.

`ValidateCommitted(const FDungeonEquipmentView&, const FState&, const FCombatState&, const FString& WeaponMirror, const FString& ArmorMirror, FBinding&, FString&)`: pure complete-value validation; no fake “approved”/“ownerOK” flag. This API validates committed value consistency only, **not native Actor authority**. Tests derive its control values from real admitted/equipped/attacking owners before changing one copy; copied bad readbacks are not described as actual live corrupted inventories.

Success: valid RunGuid, matching nonzero RunAlias/OwnerId/Revision/active slot; actual active SWD instance, unique matching item and slot version/content, current Fighter mirror and Melee instance/action owner. Armor slot2 matches actual Inventory.Armor: zero with empty mirror is NoArmor; a real ARM-LGT-001 with current item/slot version is LightArmor; other armor/unknown family rejects rather than becoming LightArmor or NoArmor. Legitimate grade and good/bad affixes keep their base skin. Failure preserves all Out identity and enum fields. Diagnostic is nonempty on failure, empty on success.

An already-installed legal AwaitExplicitContinue can be resolved without opening that gate or advancing the saved clock; generic “any closed gate means no gear” is forbidden. Prepare remains the normal existing-Run path; this test does not claim to test new-process pristine Continue.

## Exactly three new registrations

Filter: `CodexDungeon.Content.FairytaleEquipmentBinding`

1. `CommittedNoArmorLightCancelReplaceAndRetake`: normal starter NoArmor; actual pending light .50s still None; actual movement cancel never late-commits; restart commits LGT; pending medium retains old LGT; committed medium explicitly unsupported; actual old light drop/re-pick retains ID and reads its current version. Both starter and committed-light positives must fail at the stub, not before it.
2. `RealGradedCursedOwnershipAndAtomicBadReadbacks`: actual grade3 beneficial SWD and cursed LGT admission, current real attacking instance, live and pure positive controls; independent bad copies check unbound/guid/run/owner/revision/slot/ID/version/missing/duplicate/mirrors/Melee/current action/content. Actual second Fighter is rejected through authoritative Resolve. Pure false cases alone cannot establish progress because real complete positive controls precede them.
3. `InstalledAwaitExplicitContinueRetainsCommittedSkin`: actual full source Capture/Aggregate sealing plus unchanged Installer Prepare→Install onto an existing legal target; complete saved values independently equal before resolver; paused LGT resolves without changing gate/IDs/clock; real neutral tick/fresh Enter alone resumes and preserves identities.

Expected Stage0: semantic positive failures due solely to honest stub. Actual count/result unknown until Root runs. Negative stub passes are not implementation success. Tests assert resolver read-only behavior for the measured equipment/IDs/mirrors/Combat/clock/gate domains; only the third group additionally checks the full actual canonical Run signature before/after paused ticks. No blanket claim of full Profile atomicity.

## Later consumption patch, deliberately deferred

Approved command-line name: `DungeonFairytaleSwordEquipmentBoundPreview`.

Old art trial alone stays unchanged. Bound mode wins any mixture of flags. It independently enables current P2 V003 marker/body/grip axes and warms current Ready/P1/P2 plus42 P2 armor resources. Asset preload permission is distinct from armor draw permission. After resolver GREEN, small HUD/Presentation hunks will select NoArmor/LightArmor according to the same resolver result and preserve existing texture readiness/failclosed ownership, actual eight-layer order/sameUV NearHand, scales, combat/audio/UI/input.

`before/` preserves only the exact two presentation consumption baselines. `baseline-pins-v001.json` pins 11 related Source/fixture dependencies. Root may change Presentation/HUD for P3. Those changes must be manually rebased as small hunks; **never overwrite actual Source with a whole saved candidate or before file**. No consumption patch or integration proof is claimed in this Stage0.

No generation, media view/playback, UE/UBT/test run, ledger/progress edits, source import or asset updates occurred. Formal0/15active remains.
