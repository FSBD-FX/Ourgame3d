# First K pilot preregistration preparer

Candidate helper only. No UE process/native evidence/archive or ready=true preregistration was created while preparing it. Source/Content/tools/E/status/ledger were not changed by this task. The 6 finite host tests moved from RED (6 tests,16 failed assertions/subcases) to GREEN (6/0), and the actual historical AE303/1439 CM was rejected with exit2 before output creation. Host inputs do not count as a new K test run.

The helper supports only the first **full_right / exploratory_pilot**. It consumes the original V002 driver/checker entrypoints and original current81 template; source names/JSON/flags stay V002 despite the separately admitted namefix. `normal_route_native_verified=false`, `route_native_verification=null`, `actual_native_K_run=false`, pixel verification false and formal/checker acceptance false remain explicit. `ready=true` means validated prerequisites for exploratory collection, never route/native acceptance.

## Required actual evidence

Supply a **NEW** complete compiled manifest and its SHA, the exact actual source admission and SHA, and actual editor/DLL/uproject SHA pairs. The real source admission is currently `F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-K8-source-admission-v001/actual-source-admission.json`,5916 bytes / `fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67`.

New CM requirements: `source_files:308`, `production_files:1495`, `registered_tests:203`, `passed:203`, `failed:0`, **`notRun:0`, `inProcess:0`, `warnings:0`** (missing counters reject), `regression_GREEN:true`, verification_passes2/twoSHA_mismatches0, `source_admission_pin`, actual `build`/`build_log` pins, actual new `full_suite` index pin, and `files` covering exactly all current Source308 and Production1495 plus actual game DLL and uproject. Extra non-Source/Production pinned entries are accepted but all entries must match their real current file. Duplicate CM paths reject.

The helper checks actual all203 rows/state/unique IDs against the historical203 ID set, top-level succeeded203 and zero succeededWithWarnings/failed/notRun/inProcess, zero row warnings/errors and no Error/Warning/Fatal entries. A real new full-suite report is mandatory; the old historical full_suite itself is rejected. Its reportCreatedOn must follow successful Editor build Utc, which must follow actual admission utc. `build` uses the existing Root last-build schema `Target:CodexDungeonEditor`, `ExitCode:0`, `Utc`, `Log`; the Log path must match the pinned build_log. The historical report establishes IDs only.

Current source is verified through actual AD + new CM, including all12 exact reviewed source rows and fixed Probe CPP5f0d…; obsolete actualSource pins in old freezes are **not** required to match after legitimate admission. Immutable candidate member bytes and fixed freeze JSON identities remain checked. The independent source review is exactly8226 / `4d357efa022c48ebed703225a72b56aaab607555ec559a686fc2a55b25fc78c0` with one `Decision: Approved` line. Compound/source/namefix pins are tied to it; no empty profile flip is substituted.

The real81 resource table is72590 / `b5f3d6689ed3cb43ded9f4bbbd25036352bf948270b123bae3c21e1521574961`; the helper checks all81 source byte/SHA/512RGBA hashes and current uasset pins with exact object-to-package paths. The K57/Ready24 distinct object closure remains81, including separate phase06 packages despite source reuse. It does not claim GPU readback from those files.

## Root CLI

Run after actual new build/regression/CM evidence exists. Replace only the NEW CM and actual binary hashes with real pins; no placeholder hash is valid. First use `--validate-only`; it writes neither output nor archive. Remove that option once the complete input set validates. Output must be unused absolute JSON under this candidate or the explicitly supplied `F:/Ourgame/docs/production/first-batch-v2/evidence` path.

```powershell
$pilotPython = 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$pilotHelper = 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-pilot-prereg-preparer-candidate-v001/prepare-first-K-pilot-prereg-v001.py'
$pilotCM = '<NEW complete actual compiled manifest absolute path>'
$pilotCMSHA = '<real SHA256>'
$pilotEditor = 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe'
$pilotDLL = 'F:/Ourgame/UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
$pilotProject = 'F:/Ourgame/UnrealGame/CodexDungeon.uproject'
$pilotArchive = 'F:/Ourgame/过程图稿与视频/2026-10-19_军剑K右侧前踏首次原生试验_v001'
$pilotPrereg = 'F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-first-K-pilot-prereg-v001/full-right.json'
& $pilotPython -B -X utf8 $pilotHelper `
 --compiled-manifest $pilotCM --compiled-manifest-sha $pilotCMSHA `
 --source-admission 'F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-K8-source-admission-v001/actual-source-admission.json' `
 --source-admission-sha 'fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67' `
 --editor-executable $pilotEditor --editor-sha (Get-FileHash -LiteralPath $pilotEditor -Algorithm SHA256).Hash.ToLowerInvariant() `
 --game-dll $pilotDLL --game-dll-sha (Get-FileHash -LiteralPath $pilotDLL -Algorithm SHA256).Hash.ToLowerInvariant() `
 --uproject $pilotProject --uproject-sha (Get-FileHash -LiteralPath $pilotProject -Algorithm SHA256).Hash.ToLowerInvariant() `
 --archive $pilotArchive --output $pilotPrereg --validate-only
```

The frozen original driver's **real preflight** is exercised read-only before writing: its initial prereg load is supplied the validated in-memory object; all CM/resources/binary/route/checker checks still execute. It launches nothing. After final current CM recheck, the helper exclusively writes one UTF8 JSON. Existing output/archive paths fail. It prints exact `driver_argv` and a correctly quoted PowerShell command using the **same** prereg and planned archive. Root should execute that printed command. Existing frozen driver CLI itself does not consume the extra `planned_archive` metadata; a manually altered archive CLI would be a different Root choice, not an invariant this helper can impose on unchanged driver code.

Equivalent actual driver command after successful preparation:

```powershell
& $pilotPython -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/forward-step-native-observer-candidate-v002/drive-swd-forward-step-native-v002.py' --prereg $pilotPrereg --mode exploratory_pilot --case full_right --run --archive $pilotArchive
```

The driver alone creates that new archive and `原件`; helper never creates either. Native witness, pixels, MainMix and process outcome will come from that later real execution.

## Optional independent pixel checker

Default `checker_dependencies.K_pixel_composition` and `K_pixel_composition_freeze` stay null/pending. After Root's separate checker review, optionally pass **all four** `--pixel-checker <absolute.py> --pixel-checker-sha <SHA> --pixel-freeze <absolute.json> --pixel-freeze-sha <SHA>`. The helper verifies both pins, frozen checker membership and immutable members; it does not approve checker quality or native pixels. This deliberately accepts the later reviewed fix version instead of hardcoding the superseded v001 checker ID bug. Collection and formal acceptance remain separate.

## Ownership and limitations

All changes belong only to this new helper directory. This helper has not been independently approved merely because its author froze it. Current real input checks verified AD12 and resource81 and retained the negative CLI outcome, but the full positive new-CM preparation path remains for Root after new evidence exists. The candidate freeze excludes future output JSON; do not add output to the old freeze. No generated synthetic native runtime report or ready=true preregistration is included.
