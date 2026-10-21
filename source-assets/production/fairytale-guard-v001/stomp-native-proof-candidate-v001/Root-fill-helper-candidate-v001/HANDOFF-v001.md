# Root native prereg fill helper

Candidate only. The worker has not executed this helper, written Root inputs, launched UE, decoded PNGs or changed any original whole-freeze member. Root executes it after actual new6 import, approved Data admission and fresh full193 GREEN.

The helper accepts the peer Root-fill helper's NEW `Native-Stomp50-profile-contract-v001.json`, using the exact normalized schema already required by frozen `verify-Stomp-native-v001.py`. It checks actual non-template Root approval,50unique/13rows, successful native6 import and independent old1326/new6 two-SHA receipt, fresh193/1332 snapshot, and controlled Data admission. It derives the current ten Source pins from the actual compiled snapshot; no fixed Source count is invented. No asset/source/native ID is supplied by this candidate.

Data admission fields are `schema=Root-GuardStomp-approved-Data-admission-v001`, `is_template=false`, `RootApproved=true`, `success=true`, `FinalAccepted=false`, actual `Source_count`, `previous_Data_pin`, and one current `admitted` Data pin. The previous pin is compared to the immutable Stage0 manifest's historical value, not the overwritten current Data file. Current Data is checked against actual disk and the fresh compiled pin.

Root invocation from F:/Ourgame:

```powershell
.\tools\runtime\asset-gen\Scripts\python.exe -B -X utf8 "source-assets/production/fairytale-guard-v001/stomp-native-proof-candidate-v001/Root-fill-helper-candidate-v001/fill-Root-native-Stomp50-prereg-v001.py" --snapshot "<fresh snapshot directory>" --profile "<NEW actual Native-Stomp50-profile-contract-v001.json>" --import-manifest "<actual import-manifest.json>" --native-import "<actual native6 receipt.json>" --independent-import "<actual independent twoSHA receipt.json>" --observer-admission "docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/observer-admission-v001/admission-receipt-v001.json" --data-admission "<actual approved Data admission.json>"
```

Default NEW output directory is `source-assets/production/fairytale-guard-v001/root-Stomp-native-prereg-v139-v001`. An existing directory is refused; use `--output-dir` with a new version if needed. It publishes `Root-Stomp-native-left-prereg-v139-v001.json`, `Root-Stomp-native-right-prereg-v139-v001.json` and a fill receipt. Root approval flags are set only after the actual input gates; the full frozen source-only checker validates both private temporary documents before any output directory is created, and validates both published files again. Source-only success is not native success. Every output keeps native_started/native_passed/visual_reviewed/FinalAccepted false.

Then Root may run the frozen launcher sequentially for side-1 and+1 with the matching NEW prereg; this helper never invokes the launcher or UE. If any prepublication input is pending, stale, unapproved, missing import/193 GREEN, or fails the frozen source-only gate, no prereg directory is published. A postpublication readback failure preserves the new attempted files and a success=false/failure receipt. Original frozen candidate SHA523b70ca… remains authoritative. Subsequent corrections require a new helper version.
