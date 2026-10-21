# K5 near-shoulder integer comparison v003

Body frozen08185… is unchanged. Three original K5 armor PNGs are retained as exact byte reference copies; only ShoulderNear is translated into A/B. Far/Chest/body/hand/helmet pixels and positions remain unchanged.

A: relative current(-45,-15), originalJ2(-16,-19). B: relative current(-50,-21), originalJ2(-21,-25). Full512 canvas, original RGBA exactly reversible, original alpha histogram exact, nonzeroRGBA clipping0, no scaling/rotation/painting or body-mask expansion.

A: bbox[190, 218, 241, 258]; arm solid overlap1226/1469; body solid overshoot0; head raw overlap0px; final near/far mask sourceRGBA changes0/0; Chest positive contribution2374 (v002 baseline1342, oldv001602).
B: bbox[185, 212, 236, 252]; arm solid overlap1077/1469; body solid overshoot0; head raw overlap1px; final near/far mask sourceRGBA changes0/0; Chest positive contribution2459 (v002 baseline1342, oldv001602).

Both have real existing arm support and no whole-body overshoot; no extraC was created. A/B still need silhouette/perspective and sleeve-chest junction review. Numerical 0 is not wear acceptance.

qc/K5-original-v002-left-A-middle-B-right-unscaled.png: left originalv002, middleA, rightB; three full512 images pasted without resize. Root must retain F originals/presentation and E672 indexed copy before View. This agent did not View or runUE, generate art, alter old freezes or actual Source/Content/tools/E/status/ledger.

Read-only repeat: build-two-shoulder-candidates-v003.py --check-only. All fit/runtime/FinalAccepted=false.
