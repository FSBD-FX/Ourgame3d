# Dodge32 bounded import candidate

Root can run these candidate scripts in place; the Python contract and `input-pins-v001.json` must remain beside both Python entry points. The PowerShell launcher uses its own directory for the importer and the explicit `F:/Ourgame` workspace, so it does not depend on a `tools/scripts` nesting depth. It inherits a task-specific manifest environment variable into UE and restores the caller's value afterward.

Exact source32: five body partitions×4 from E502 plus Chest/ShoulderNear/ShoulderFar×4 from E510. The native-prepared source manifest is frozen schema `frozen-Dodge32-scoped-native-import-prepared-v001`, SHA `78c1ff60ed59e0cf58af8d80504580965c65c386ad0ad437be71aec8f3cf6c9f`. All32 are nonempty512RGBA, including FarHand0..3. Sources, decoded RGBA, retained E bytes and original1332 package membership are checked before Root output is created. Nothing is repainted or transformed.

From `F:/Ourgame`, first validate without writing approval or launching UE:

```powershell
$candidate='F:/Ourgame/source-assets/production/fairytale-hero-state-gap-v001/dodge-import-candidate-v001'
$python='F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe'
$baseline='F:/Ourgame/source-assets/production/backups/v139-Stomp193G'
& $python -B -X utf8 "$candidate/prepare-Dodge32-Root-import-v001.py" --old-snapshot $baseline --validate-only
```

Root's explicit next call creates a NEW `dodge-state-preparation-v001/Root-Dodge32-import-v001` directory and typed import-only trial record:

```powershell
& $python -B -X utf8 "$candidate/prepare-Dodge32-Root-import-v001.py" --old-snapshot $baseline --approve-limited-import
& "$candidate/import-hero-Dodge32-v001.ps1" -ValidateOnly
```

Use a newer Root frozen snapshot with the same exact old1332 package set if required; `--old-snapshot` accepts its manifest or folder. To use a different NEW Root output leaf, pass `--output-dir` to prepare, then the resulting `import-manifest.json` through the launcher's `-Manifest` parameter. Existing output directories and saved packages are refused.

After Root closes UE/UBT, the actual import command is:

```powershell
& "$candidate/import-hero-Dodge32-v001.ps1"
```

The launcher first reruns host validate-only, then launches a hidden UE process and requires exactly one fresh successful native receipt plus the independent saved-byte verification. Native receipt: `UnrealGame/Saved/Bootstrap/hero-Dodge32-v001-import-<UTC>.json`, schema `hero-Dodge32-native-import-v001`. It reads actual Texture2D class/object path,512dimensions,source import filename,UI/sRGB/noMips/never-stream/bilinear settings and saved package pins. Registry must be exactly32 in the new namespace, and disk Production must be exact1332+32=1364. A partial import leaves a failed receipt and outputs for Root review; no rollback or replacement is attempted.

Independent receipt: `Root-Dodge32-import-v001/independent-import-verification-<UTC>.json`, schema `Dodge32-independent-import-twoSHA-v001`. It binds the actual native receipt and manifest, strictly checks all32 native metadata records, and rereads old1332/new32 saved bytes and exact1364 membership twice. This is not a second fresh UE metadata readback. The `actual_*` asset fields and `actual_total`/`total_production_files` aliases follow the existing Death/Stomp tooling shape; see `receipt-contract-v001.json`.

Root can rerun only the independent host check later:

```powershell
& $python -B -X utf8 "$candidate/ue-import-hero-Dodge32-v001.py" --verify-receipt 'F:/Ourgame/UnrealGame/Saved/Bootstrap/<actual-native-receipt>.json'
```

The unchanged E510 preparation record stays TrialAllowed=false. Only Root's explicit CLI grants exact32 import; generated import-trial/native/independent records also keep runtime TrialAllowed=false, FinalAccepted=false and formal_complete_units=0. Sourcefit/EDIT/J-to-buckle residual and motion/Ready-join risks remain. Actual33-resource preload, nine submitted slots, real .4s Dodge and original physics/iframe behavior need separate Root runtime admission and both-side native review.

Author verification: stub produced three expected semantic host failures; implementation passes four host contract tests (including seven malformed-input cases), Python AST and PowerShell parse. Actual source/E32 +old1332 host validate-only passed without outputs or UE. These facts do not claim native import, runtime or a UE regression result. Root alone owns execution, actual Source/Content/tools and documentation updates.
