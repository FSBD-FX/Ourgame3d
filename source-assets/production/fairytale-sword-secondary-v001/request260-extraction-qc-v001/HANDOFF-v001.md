# Request259 technical extraction QC

Root decision: PENDING_Root_visual_review. Technical candidate only; not runtime/art approval.

Actual raw is1254×1254,2×2 cells627. Each full cell uses the same512/627 LANCZOS RGBA scale; no bbox-fit, variable scale, x shift or anatomical warp. Only uniform alpha1..8 cleanup then recorded integer-Y alignment of alpha>0 graphical bottom to464. Raw627 crops, chroma627, unshifted512, final512, separate alpha and cleanup masks are preserved.

Widths/heights below use alpha≥128. These are exact contours, not anatomical measurements. Helmet warm-core and lower60 components are explicit heuristics; physical helmet/boot dimensions remain OPEN.

K0: width242,height414; vs Ready width1.1362x; lower6 span178 vs Ready184; raw graphical foot boundary572; dy-3; final alpha1/128 bottoms464/464.
K1: width273,height414; vs Ready width1.2817x; lower6 span176 vs Ready184; raw graphical foot boundary572; dy-3; final alpha1/128 bottoms464/464.
K2: width275,height412; vs Ready width1.2911x; lower6 span185 vs Ready184; raw graphical foot boundary562; dy5; final alpha1/128 bottoms464/464.
K3: width283,height398; vs Ready width1.3286x; lower6 span205 vs Ready184; raw graphical foot boundary562; dy5; final alpha1/128 bottoms464/464.

K0/K1 wide lower contour is not repaired or hidden by Y alignment. Every alpha128 footprint remains unchanged by edge cleanup. No material RGB change beyond4 source pixels from keyed background. Four original RGB crops reassemble every raw pixel exactly.

No View, imagegen, new art, armor/sword drawing, actual Source/Content/tools/E/status/ledger change, import or native run. Root must preserve F/E before viewing. Candidate outputs are technical PNG derivatives, not newly generated art.

Reuse this exact script for a NEW request260 candidate with explicit new raw SHA/output directory and references; never overwrite this frozen259 version.
