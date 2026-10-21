# K8 pixel checker v002: production ContentId correction

Only behavior change: `typed_slots()` now requires the actual production weapon ContentId `WPN-SWD-001`. `DungeonFairytaleSwordEquipmentBinding.cpp`107 checks this inventory/mirror ID, and121 copies the actual active slot ContentId into the serialized binding. The previous short alias `SWD-001` is rejected. No UE was launched by this worker and this is not a native pass.

The complete independent review is pinned by delta-closure-v002.json: Critical0 / Important1, sole blocking ID mismatch. Original v001 remains frozen and unchanged. New host fixtures use the true production ID; explicit positive/negative tests failed before the fix, then pass after it. The 27 prior tests remain in the new 29-test suite.

The script is byte-identical to its predecessor after inverse substitution of four single-occurrence strings: the one ID comparison and three self-freeze/result version strings. All geometry, actual Source/CM binding, 81 GPU readbacks, original PNG FIFO/CRC, sampler/blend/raster, optical thresholds, component ROI gates, and OPEN fields remain unchanged. Original pure helpers/provenance and nominal host projection report are byte copies. See delta-closure-v002.json for exact old/new pins and substitutions.

API remains `audit(archive, prereg)`. Root's new prereg must use:

- `checker_dependencies.K_pixel_composition`: this directory's verify-K8-native-pixels-v002.py pin.
- `checker_dependencies.K_pixel_composition_freeze`: this directory's candidate-freeze-v002.json pin.

CLI (write its output outside this frozen directory):

```powershell
& 'F:/Ourgame/tools/runtime/asset-gen/Scripts/python.exe' -B -X utf8 'F:/Ourgame/source-assets/production/fairytale-sword-secondary-v001/K8-native-pixel-checker-candidate-v002/verify-K8-native-pixels-v002.py' --archive '<actual absolute archive>' --prereg '<actual launched prereg file>'
```

The existing v001 handoff explains the unchanged detailed gates. In particular the >=8 visible-owner ROI applicability is not native calibrated; fractional origin can move farShoulder across that boundary. Do not tune thresholds or ownership to obtain GREEN. A failed real run stays failed for diagnosis.

Scope is K0–7 fixed-registration composite source-pixel witnesses, actual ordered eight-slot float submissions, and full K57/Ready24 source/GPU closure. Unique individual-owner attribution, small/occluded farShoulder evidence, Ready optical composition, independent UI-hidden measurement, placement/route causality, audio/MainMix/listening/device onset, final art and unit acceptance remain OPEN or separate. Host tests and source preflight do not establish native/GPU evidence. FinalAccepted remains false.
