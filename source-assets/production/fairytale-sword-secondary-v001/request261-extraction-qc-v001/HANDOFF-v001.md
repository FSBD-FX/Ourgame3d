# Request261 K4to7 technical extraction QC

Root decision: PENDING_Root_visual_review. Technical candidate only; not runtime/art approval.

Actual raw is1254×1254,2×2 cells627. Each full cell uses the same512/627 LANCZOS RGBA scale; no bbox-fit, variable scale, x shift or anatomical warp. Only uniform alpha1..8 cleanup then recorded integer-Y alignment of alpha>0 graphical bottom to464. Raw627 crops, chroma627, unshifted512, final512, separate alpha and cleanup masks are preserved.

Widths/heights below use alpha≥128. These are exact contours, not anatomical measurements. Helmet warm-core and lower60 components are explicit heuristics; physical helmet/boot dimensions remain OPEN.

K4: width320,height412; vs Ready width1.5023x; lower6 span242 vs Ready184; raw graphical foot boundary582; dy-12; final alpha1/128 bottoms464/463.
K5: width268,height413; vs Ready width1.2582x; lower6 span215 vs Ready184; raw graphical foot boundary582; dy-12; final alpha1/128 bottoms464/463.
K6: width258,height428; vs Ready width1.2113x; lower6 span203 vs Ready184; raw graphical foot boundary559; dy7; final alpha1/128 bottoms464/463.
K7: width259,height428; vs Ready width1.2160x; lower6 span201 vs Ready184; raw graphical foot boundary559; dy7; final alpha1/128 bottoms464/463.

K4to7 contour metrics remain unmodified by Y alignment. Every alpha128 footprint remains unchanged by edge cleanup. No material RGB change beyond4 source pixels from keyed background. Four original RGB crops reassemble every raw pixel exactly.

No View, imagegen, new art, armor/sword drawing, actual Source/Content/tools/E/status/ledger change, import or native run. Root must preserve F/E before viewing. Candidate outputs are technical PNG derivatives, not newly generated art.

Derived from frozen259 technical pixel algorithm; only global frame names offset4 and truthful261 metadata changed. All older outputs remain immutable.
