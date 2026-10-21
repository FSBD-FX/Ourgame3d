# K5 owner seam correction v002

Candidate only: semantic_accepted=false, wear_fit_accepted=false, runtime_ready=false, FinalAccepted=false. No View performed. Root F/E retention and review required.

Only K5 changes. K4/K7/260, all old freezes, source art, armor, Source/Content/tools/E/status/ledger remain untouched. New output: body-layers/{BodyRest,NearArmWithoutHand,HelmetForeground,NearHand}/K5.png; matching binary owner-masks. Original 512 canvas, root256,464, alpha1 foot464 and native alpha128 foot463 remain exact.

The old source-preserving arm partition incorrectly included frontal torso. correctedNearArm=oldNearArm intersect the source-ink-seam polygon recorded in proof; 1,165 original visible pixels move to BodyRest. Arm owned coordinates3,174→2,009; no new arm pixels claimed. Helmet and NearHand PNGs AND masks copied byte-for-byte. Far hand warm-hull heuristic mask copied byte-for-byte and stays in BodyRest.

NearHand remains the old warm-hull+4 candidate. No independent source-semantic evidence establishes a belt subregion inside that warm component, so no glove pixels are relabeled to force the chest visible. Warm ROI is not an official GripAxis or accepted anatomical contour. Root should inspect the cuff/chest relationship in the retained new board and unchanged-armor assembly.

The exact old seven-layer armor stack reproduces Chest positive contribution602/half392; corrected body with the same three armor PNGs gives positive1,342/half1,048 (effective alpha394.445721→1,049.622191). Both shoulder contributions unchanged. This numerical increase is not a wear/readability approval. Independent armor worker owns NEW K5-LGT-depth-correction-v002 for the actual identical-armor diagnostic reassembly.

Full onehot closure, raw RGBA sum including hiddenRGB and premultiplied alpha composite exact. No art/fill/shift/scale/warp. Numeric source gray/ink row-run evidence and moved-pixel mask are preserved for review. Board columns at native512: source, BodyRest, NearArmWithoutHand, HelmetForeground, NearHand.
