# Request260 K0–K3 four-owner candidate

FinalAccepted=false; semantic_accepted=false. No images View, no art generation, no UE/Source/Content/tools/E/ledger/status writes.

16 RGBA owner layers in body-layers/{BodyRest,NearArmWithoutHand,HelmetForeground,NearHand}/K0..3.png, and16 corresponding binary owner masks. Each full512 canvas coordinate has one owner; original RGBA sum and premultiplied alpha composition reconstruct source exactly. No paint, fill, translation, scaling or hidden anatomy. Foot464 and author Root256,464 unchanged.

The numeric segmentation recipe and actual hull polygons/arm ROIs are in four-owner-proof-v001.json. Helmet uses the actual bronze warm core plus top knob, a9px hull neighborhood, and suppresses connected gray cloth; sleeve uses gray neighborhood in explicit pose ROIs. NearHand uses the individual warm closed-fist hull +4px cuff/ink neighborhood, with helmet bronze core protected. Far open-hand warm hull +4px stays BodyRest, with a separate heuristic protection mask; it is NOT an accepted full hand contour.

These semantic boundaries were NOT viewed. Source pixel closure does not prove anatomical owner correctness. K1 fist/helmet separation, complete helmet dark outline, gray sleeve/torso split and K3 closed fist over the sword need Root retained visual review. No formal Grip or Axis: heuristic_grip_ROI contains only source warm-cluster bbox/centroid/polygon, never copied J markers.

Future stack: BodyRest -> ShoulderFar -> Chest -> NearArmWithoutHand -> ShoulderNear -> HelmetForeground -> IndependentSword -> NearHand. All copper head warm-core and knob pixels belong HelmetForeground; all near/far hand warm-core pixels belong NearHand/BodyRest respectively.

QC exact RGBA reassembly is qc/Kx-reassembled-exact-RGBA.png. Five-column512-native diagnostic boards are source body, BodyRest, NearArmWithoutHand, HelmetForeground, NearHand on dark background, no resampling; ownership-label images show only numerical labels. Root must retain full packet F/E before View. No independent sword/armor composite is fabricated here.
