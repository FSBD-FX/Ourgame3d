# K56 Exclusive Texture Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Prepare Root-run exclusive native import of56 frozen512RGBA textures and read-only verification, without starting UE or modifying actual Content during preparation.

**Architecture:** A small common validator pins actual K8 SourceContract/manifest and current CM. A Python importer uses only APIs proven by the old14 import; a PowerShell launcher first runs host decoding/no-UE preflight, then retains native log/claim/import/launch/exit receipts. Independent read-only receipt verification checks exact1495Production/303Source and saved Texture2D lineage.

**Tech Stack:** Python stdlib + Pillow for host source decoding; installed UE5.5 Python APIs for native import; PowerShell5-compatible launch/exit records.

**Spec:** Parent scoped task message 2026-10-19: only NEW UE-K56-texture-import-candidate-v001; Source303/Production1439 CM ae00569b; new56 Texture2D only.

## Global Constraints

- Parent-only actual execution. This candidate never starts UE in preparation and never writes actual Source/Content/tools/status/ledger/E.
- CM421789B ae00569bad81eae953b989b964ed2592e6f1e8e0dff43b81163358c43bb3007a; exact303Source,1439Production,203GREEN. After import1495Production.
-56keys=8frames×7owners; namespace /Game/Production/ArtTrials/SWDSecondary/v001; no sword import. K6 uses K0 source but has its own new names.
- Old14 script and actual receipt both prove srgb=true, TC_EDITOR_ICON, TMGS_NO_MIPMAPS, TEXTUREGROUP_UI, TF_BILINEAR, never_stream=true. Parent explicitly corrected initialfalse totrue.
- No overwrite/reimport/delete/rollback/Material or extra packages; every target must be absent. Nonzero/error outcomes retained, never success or auto-retry.

## Review Focus

- Changed source/contract/digest or missing owner must fail before UE.
- Duplicate/escaped target and existing namespace must fail before mutation.
- Old Source/Production/other Content membership or SHA drift must fail.
- Native imported class/settings/dimensions/filenames and full registry membership must match56.
- Missing import receipt/nonzero OS exit must never count as acceptance.

### Task1: Host contract and baseline gates

- [x] Write small malformed-manifest tests, observe missing-function RED, then implement shape/lineage and pinned baseline validation.
- [x] Run actual56 host preflight after builder freezes real inputs; retain proof only under NEW candidate.

### Task2: Native-only import and launcher

- [x] Adapt proven AssetImportTask/settings/compilation/save API calls; verify before/after exact membership and source pins, retain failure receipt in finally.
- [x] Prepare parameterized PS wrapper, no active UE/UBT gate, host proof pin, explicit argv/log, same PID OS exit receipt and nonzero exit propagation.

### Task3: Read-only proof and freeze

- [x] Add read-only verifier requiring actual import success + exact saved files/source lineage + valid same-PID exit0; preserve native-render acceptanceOPEN.
- [x] Run host tests, actual preflight, PS parse and source syntax checks. Native import remainsUNEXECUTED.
- [x] Freeze own members + necessary actual input pins, hand off exact Root command. No commit or actual application in this scoped candidate task.
