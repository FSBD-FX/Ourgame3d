# K pilot prereg helper v002 optional-interface repair

ONLY this new directory was written. Original helper v001/freeze remain unchanged. This addresses the single Important finding in `F:/Ourgame/.superpowers/sdd/2026-10-19-swd-secondary-v147/K8-pilot-prereg-preparer-review-v001.md`,4697 bytes / `fb2baae283f034c54a0625bbd860fbb06b231838edc3507943746d6f5fd40e0a`.

## Exact change

`freeze_member_pins` explicitly supports two actual path conventions and rejects other/mixed shapes:

- Root's three existing schemas (`Root-K8-import-backed-compound-source-candidate-freeze-v002`, `observer-local-name-only-fix-candidate-freeze-v003`, `observer-v002-current81-unadmitted-candidate-freeze-v002`) use `members[].path`, required absolute, without relative_path, confined to the freeze's directory.
- Actual `K8-native-pixel-checker-candidate-freeze-v002` uses `files[].relative_path`, required canonical forward-slash relative names based on the **freeze directory**, never the project root. Absolute/rooted/driven/colon/backslash/empty/dot/dotdot aliases and duplicate/escaped member paths reject. All materialized members receive actual bytes/SHA verification.

Unknown schema names and mixed members/files reject. Historical dependency pins that refer to pre-admission actual Source are still not revalidated as current; unchanged actualSource/AD/NEWCM gates remain authoritative. A future checker freeze schema requires a separately reviewed helper change instead of guessed fallback rules.

`pixel_dependencies` retains all-or-none four optional arguments and actual checker membership. Both `K_pixel_composition` and `K_pixel_composition_freeze` now belong inside `checker_dependencies`. No obsolete top-level freeze is written. Default gives two nested nulls; native route/pixel/formal acceptance remains pending/false.

`mechanical-delta-v002.json` proves the entire original helper is recovered by reversing only the schema-adapter block and two optional-configuration blocks. Every other original function is byte-identical, including `validate_green203`, `validate_output`, `validate_current`, `validate_resources`, `main`. The source/CM/AD308/1495/203/binary/chronology gates and route/capture behavior were not weakened.

## Actual checks performed

Six new finite optional schema/interface tests ran RED6 → GREEN6; all six original gate tests were retained and passed. They include actual corrected pixel freeze/script, direct real pixel `own_freeze` consumption of the two nested fields, default null/incomplete pair, unknown/mixed shape, bad relative path forms and duplicate/relative Root member cases. No simulated native runtime report was created.

Actual corrected pixel script **23039 / `aa677a9c15fb5dcf2414c22b7b5940870db4711d8d566e22122d942d6ee08188`**, freeze **6601 / `fb14b809e95a53cb4b318f1e9cd97d5e8a68c1c53c1ba4ffa14d7eda7d57e28a`**, were used. Its independent review is3071 / `1cc7a7676b3e3c0880dcd26659d8d057c787b03bf0263cbe0f885e257ee69046`; this helper task does not replace that review or prove native pixels.

Root's actual NEW CM is `F:/Ourgame/source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001/compiled-source-manifest.json`, **436892 / `8936717c38f67a3bb08791537f38a60d953fd5df8132c642112a507f4eeb8772`**, with1808 pinned files (Source308/Production1495+5). Actual AD remains5916 / `fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67`. Both actual positive CLI paths (default null and optional pixel) completed **--validate-only EXIT0**, retained under `actual-new-CM-*-validate-only-v002.json`. This executes the original frozen driver's real preflight read-only. Both results retain output_written=false/output=null, native_run_attempted=false/archive_created=false; the intended prereg files and actual planned capture archive are absent. No ready=true preregistration was written.

## Root CLI

Use the same CLI and evidence requirements documented in the frozen v001 handoff, substituting this new helper path. This real NEW CM and AD are now available:

```powershell
$pilotPython = 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$pilotHelper = 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-pilot-prereg-preparer-candidate-v002/prepare-first-K-pilot-prereg-v002.py'
$pilotEditor = 'G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe'
$pilotDLL = 'F:/Ourgame/UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
$pilotProject = 'F:/Ourgame/UnrealGame/CodexDungeon.uproject'
$pilotArchive = 'F:/Ourgame/过程图稿与视频/2026-10-19_军剑K右侧前踏首次原生试验_v001'
$pilotPrereg = 'F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-first-K-pilot-prereg-v001/full-right.json'
& $pilotPython -B -X utf8 $pilotHelper `
 --compiled-manifest 'F:/Ourgame/source-assets/production/backups/v148-SWDSecondary8-308-1495-203GREEN-v001/compiled-source-manifest.json' `
 --compiled-manifest-sha '8936717c38f67a3bb08791537f38a60d953fd5df8132c642112a507f4eeb8772' `
 --source-admission 'F:/Ourgame/docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-K8-source-admission-v001/actual-source-admission.json' `
 --source-admission-sha 'fe3adc65ffb903fb8b2dfdc9f7d57ca72ee0ac7d31844ac29a0259a898d01a67' `
 --editor-executable $pilotEditor --editor-sha (Get-FileHash -LiteralPath $pilotEditor -Algorithm SHA256).Hash.ToLowerInvariant() `
 --game-dll $pilotDLL --game-dll-sha (Get-FileHash -LiteralPath $pilotDLL -Algorithm SHA256).Hash.ToLowerInvariant() `
 --uproject $pilotProject --uproject-sha (Get-FileHash -LiteralPath $pilotProject -Algorithm SHA256).Hash.ToLowerInvariant() `
 --pixel-checker 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-native-pixel-checker-candidate-v002/verify-K8-native-pixels-v002.py' `
 --pixel-checker-sha 'aa677a9c15fb5dcf2414c22b7b5940870db4711d8d566e22122d942d6ee08188' `
 --pixel-freeze 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-native-pixel-checker-candidate-v002/candidate-freeze-v002.json' `
 --pixel-freeze-sha 'fb14b809e95a53cb4b318f1e9cd97d5e8a68c1c53c1ba4ffa14d7eda7d57e28a' `
 --archive $pilotArchive --output $pilotPrereg --validate-only
```

Root removes --validate-only only after fresh independent helper review to create the single new prereg JSON. The printed original V002 driver argv uses exactly the same prereg/archive; Root executes it separately. Helper never creates archive/原件 or launches UE. As before, unchanged driver itself does not enforce the extra planned_archive metadata; execute the printed matching command.

This candidate is author-verified and frozen for fresh independent review, not self-approved. Normal route_native_verified remainsfalse, first pilot exploratory, checker/formal/FinalAccepted false; native pixels/audio/action continuity still require the actual later run and inspection.
