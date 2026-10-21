from pathlib import Path
import argparse,hashlib,importlib.util,json
import numpy as np
from PIL import Image
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003'
parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);args=parser.parse_args()
O=B/'walk-profile-root-v001';assert not O.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
checks_path=R/'tools/scripts/ue_walk48_checks_v001.py';spec=importlib.util.spec_from_file_location('walk48checks',checks_path);checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
receipt=Path(args.receipt).resolve();result=checks.verify_receipt(receipt)
manifest=B/'walk-import-candidate-v001/import-walk48-v001.json';d=read(manifest);proof=read(Path(d['references']['source_pixel_proof']['path']))
def pixels(p):return np.array(Image.open(p).convert('RGBA'),dtype=np.uint8)
rows=[]
for i in range(6):
 assets={x['component']:x for x in d['assets'] if x['frame']==i}
 whole=pixels(assets['Body']['source']);parts=[pixels(assets[c]['source']) for c in ('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand')]
 overlap=int(np.count_nonzero(np.sum([p[:,:,3]>0 for p in parts],axis=0)>1));assert overlap==0
 rebuilt=np.sum(parts,axis=0,dtype=np.uint16);different=int(np.count_nonzero(np.any(rebuilt!=whole,axis=2)));assert different==0
 old=proof['body6'][i];original=pixels(old['source_body']['path']);mask=np.array(Image.open(old['old_nearhand_mask']['path']).convert('L'))>0
 allowed=mask|(parts[-1][:,:,3]>0);outside=int(np.count_nonzero(np.any(original!=whole,axis=2)&~allowed));assert outside==0
 phase=d['phases'][i];gx,gy=phase['grip_artist_design_canvas_px'];assert parts[-1][gy,gx,3]>0
 rows.append(dict(frame=i,exclusive_alpha_overlap=overlap,exact_RGBA_four_layer_reconstruction_mismatch=different,outside_allowed_hand_union_mismatch=outside,Grip_RGBA=parts[-1][gy,gx].tolist(),body_png=desc(Path(assets['Body']['source']))))
O.mkdir()
write(O/'root-direct-pixel-verification-v001.json',dict(frames=rows,actual_read_pngs=48,source_mask_closure_verified=True,root_display_pivot_is_authored_not_physical=True,actual_weapon_grasp_not_yet_verified=True))
scope=dict(schema='ground-walk-runtime-trial-scope-v001',source_event='EV-048',unchanged_user_style='grotesque cartoon dark fairy tale, armor silhouette readable, body72/sword.50/HUDhidden',prior_contract_retained=desc(B/'walk-runtime-candidate-v001/contract-v001.md'),supersedes_only_trial_physical_stride_prerequisite=True,reason='Source frames do not track one stationary material point. Use an explicit art-tuned immutable distance cycle for the native visual trial; judge grip/transitions/slip from running game instead of asserting a physical measurement.',CycleDistanceWorld=80.,CycleSeconds=.498,DurationsSeconds=[.083]*6,movement_speed_changed=False,stride_role='Root art tuning initialized near 73.89/81.08 outline contact proxies; not physical stride or statistical estimate',support_foot_lock_implemented=False,zero_slip_claim=False,diagonal_physical_stance_accepted=False,Root_display_canvas=[256,464],Grip_role='visible fist artist handle attachment',Axis_artist_design=[.8,-.6],SourceClosureVerified_means='Root directly reread 48 PNG and verified exclusive four-layer closure and unchanged old pixels outside allowed hand union; not motion/grasp/foot acceptance',runtime_label='walk_distance_v001',label_profile_immutable=True,changing_stride_in_future_requires_new_label_or_explicit_migration=True,formal_complete_units=0,import_receipt=desc(receipt),unique_source_manifest=desc(manifest))
write(O/'scope-contract-v001.json',scope)
lines=['#pragma once','// Root-authored immutable native visual trial. Source/data pins in walk-profile-root-v001.',f'// Unique import manifest SHA256 {desc(manifest)["sha256"]}',f'// Native import receipt SHA256 {desc(receipt)["sha256"]}','// 80 is art-tuned cycle distance, never movement speed or proof of foot locking.','// Root256,464 is a display pivot. Grip/Axis are artist attachment design.','namespace DungeonFairytaleSwordWalkV001','{','inline const FProfile& Profile()','{','    static const FProfile Frozen=[]','    {','        FProfile P;','        P.Gait.CycleDistance=80.; P.Gait.CycleSeconds=.498;','        P.Gait.Durations={.083,.083,.083,.083,.083,.083};']
for phase in d['phases']:
 i=phase['frame'];lines.append(f'        {{ auto& F=P.Frames[{i}];')
 for component,path in phase['object_paths'].items():lines.append(f'          F.{component}=TEXT("{path}");')
 root=phase['root_display_canvas_px'];grip=phase['grip_artist_design_canvas_px'];axis=phase['axis_artist_design_screen_xy']
 lines.append(f'          F.Marker= DungeonFairytaleSwordBodyV001::FMarker{{FVector2D({root[0]}.,{root[1]}.),FVector2D({grip[0]}.,{grip[1]}.),FVector2D({axis[0]},{axis[1]}),TArray<FVector2D>{{}}}};')
 lines.append('          F.MeasurementsSupplied=true; }')
lines+=['        P.SourceClosureVerified=true; return P;','    }();','    return Frozen;','}','}']
data=O/'DungeonFairytaleSwordWalkDataV001.inl';data.write_text('\n'.join(lines)+'\n',encoding='utf-8')
write(O/'profile-freeze-v001.json',dict(schema='Root-ground-walk-compiled-profile-freeze-v001',files=[desc(p) for p in O.iterdir() if p.is_file()],source_marker=d['references']['markers'],import_manifest=desc(manifest),native_import=desc(receipt),old1151_plus_new48_verified=result,actual_Source_admitted=False,actual_native_visual_trial=False,formal_complete_units=0))
print(json.dumps(dict(profile_candidate=desc(data),root_direct_six_closure_passed=True,old1151_plus48=result,foot_lock=False,actual_Source_admitted=False),ensure_ascii=False))
