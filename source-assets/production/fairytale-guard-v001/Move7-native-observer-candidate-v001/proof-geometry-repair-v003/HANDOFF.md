# Move7 numerical proof repair v003 — candidate only

The actual left_v001 native trial completed, but the v002 independent checker rejected a frozen host numpy.float64 vector component even when residual was exactly zero. The failed archive remains failed and unchanged. This candidate does not rewrite it or claim complete native PASS.

The only numerical change is near(): accept numbers.Real scalars, explicitly reject bool, retain math.isfinite on both arguments and retain abs(a-b)<=tol with the exact original defaults/call tolerances. Complete native verify_rig, all optical thresholds, PNG CRC/FIFO/stop flush, fixed source geometry and five ordered Source admissions stay unchanged. Extra metadata gates explicitly bind this supplemental freeze/checker while tool_contract_fix_freeze_pin and tool_contract_fix_checker_pin continue binding the immutable v002 milestone.

Host evidence: 59 real JSON Move observations × 7 actual components pass the unchanged verify_rig after the type repair. Original rejection reproduced at observation 307; 5 finite-real positives, 16 bool/nonfinite/nonreal/just-outside-threshold negatives and 6 mutated actual geometry/resource negatives tested. No PNG was read, no View, UE or actual Source writes. Full native check has not run. Draft newline-normalization failure and exact byte-copy correction are retained under diagnostics/.

Root must create NEW preregs and fresh left_v002/right_v002 archives. Use the same Source283/Production1371/full200 snapshot; rebuilding Source is not needed for this Python-only proof correction.

```powershell
$py = './tools/runtime/asset-gen/Scripts/python.exe'
$tool = 'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001/proof-geometry-repair-v003/tooling'
& $py -B -X utf8 "$tool/fill-Move7-native-prereg-v001.py" --snapshot 'source-assets/production/backups/v141-GuardMove7-Observer200G-v003' --production-admission 'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/production-admission-v001/admission-receipt-v001.json' --observer-admission 'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/observer-compile-repair-v003/admission-receipt-v003.json' --runtime-approval 'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json' --output 'NEW_ROOT_PREREG_LEAF' --approve-prereg
& "$tool/capture-Move7-native-v001.ps1" -Version left_v002 -Snapshot 'source-assets/production/backups/v141-GuardMove7-Observer200G-v003' -RootPrereg 'NEW_ROOT_PREREG_LEAF/Root-Move7-left-prereg-v001.json' -ApproachSide -1
# Only after Root source-only PASS, repeat with -ExecuteNative. Right is sequential, side +1, fresh right_v002.
```

Dependencies: existing project Python 3.12 with numpy/Pillow, real UE G:/UE_5.5 source pins, unchanged actual283/1371/full200 and all historical source/import/profile/runtime approval closures. No external API, image generation, audio or acceptance.
