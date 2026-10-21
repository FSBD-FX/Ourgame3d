"""Read actual E394-approved RGBA; write TEXT ONLY visible registration proposals.

Artist-selected ROIs describe visible shoes/supports, not anatomy/bones. Empty
hands cannot establish a handle axis. No new images, masks, edits, UE, or trial.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
EXTRACTION = HERE.parent

SPECS = [
 ("dodge",218,0,[[90,400,195,466],[250,400,365,466]], [183,298],"closed visible foreground glove",[]),
 ("dodge",218,1,[[88,400,182,466],[230,400,333,466]], [143,309],"closed visible foreground glove",[]),
 ("dodge",218,2,[[80,400,181,466],[236,400,363,466]], [139,292],"closed visible foreground glove",[]),
 ("dodge",218,3,[[100,400,197,466],[266,400,383,466]], [162,312],"closed visible foreground glove",[]),
 ("hurt",219,0,[[138,400,216,466],[270,400,373,466]], [236,296],"foreground glove curled; both hands close to abdomen, depth mask needs review",[]),
 ("hurt",219,1,[[146,400,228,466],[295,400,403,466]], [163,301],"foreground glove opened during recoil; no retained cylindrical grip proven",[]),
 ("hurt",219,2,[[124,400,202,466],[256,400,361,466]], [169,294],"closed visible foreground glove",[]),
 ("hurt",219,3,[[133,400,215,466],[260,400,370,466]], [207,310],"closed visible foreground glove",[]),
 ("death",220,0,[[130,400,207,466],[242,400,343,466]], [183,311],"foreground fingers relaxed/open; no retained cylindrical grip proven",[]),
 ("death",220,1,[[100,400,176,466],[237,400,338,466]], [237,335],"foreground glove curled during weakening; handle axis remains unknown",[]),
 ("death",220,2,[],[300,439],"foreground palm/fingers supporting body on ground",[
   ("visible_single_rotated_boot",[80,380,150,464]),("foreground_glove",[268,416,337,466]),
   ("other_visible_glove",[359,408,424,464]),("visible_knee_cloth_support_region",[154,415,237,458])]),
 ("death",220,3,[],[266,441],"foreground palm/fingers resting against ground",[
   ("visible_single_rotated_boot",[60,400,126,462]),("foreground_glove",[228,425,316,466]),
   ("other_glove_and_lower_head_boundary",[395,420,444,464]),("visible_lower_helmet_edge",[312,436,399,464])]),
 ("death",220,4,[],[260,444],"foreground palm/fingers resting against ground",[
   ("visible_single_rotated_boot",[65,400,133,462]),("foreground_glove",[227,427,310,466]),
   ("other_glove_and_lower_head_boundary",[395,419,443,464]),("visible_lower_helmet_edge",[313,437,397,463])]),
]


def pin(path):
 data=path.read_bytes()
 return {"path":path.as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}


def band(pixels,roi,threshold=128):
 x0,y0,x1,y1=roi
 points=[(x,y,pixels[x,y][3]) for y in range(y0,y1) for x in range(x0,x1) if pixels[x,y][3]>=threshold]
 if not points:return None
 bottom=max(point[1] for point in points)
 bottom_band=[point for point in points if point[1]>=bottom-3]
 centroid=sum(point[0]*point[2] for point in bottom_band)/sum(point[2] for point in bottom_band)
 edge_candidates=[point for point in bottom_band if point[1]==bottom]
 edge=min(edge_candidates,key=lambda point:abs(point[0]-centroid))
 xs=[point[0] for point in bottom_band]
 return {"core_bottom_y":bottom,"floor_edge_y_proposal":bottom+1,
         "bottom4row_xrange_inclusive":[min(xs),max(xs)],"bottom4row_alpha_centroid_x":centroid,
         "actual_edge_sample_xy":[edge[0],edge[1]],"actual_edge_RGBA":list(pixels[edge[0],edge[1]]),
         "bottom_band_clear_of_ROI_horizontal_edges":min(xs)>x0 and max(xs)<x1-1}


def main():
 before=json.loads((EXTRACTION/'E394-before-curated-View-check-v001.json').read_text(encoding='utf-8'))
 assert len(before['verified_curated_files'])==13 and before['mismatches']==0
 frames=[]
 for state,native,index,shoe_rois,surface,hand_pose,supports in SPECS:
  path=EXTRACTION/'runs'/f'run-{state}{native}-shared-HD-v002/curated'/f'frame-{index}.png'
  file=pin(path);expected=next(record for record in before['verified_curated_files'] if record['state']==state and record['frame']==index)
  assert file['sha256']==expected['sha256'] and file['bytes']==expected['bytes']
  with Image.open(path) as opened:
   assert opened.mode=='RGBA' and opened.size==(512,512)
   pixels=opened.load();alpha=opened.getchannel('A');core=alpha.point(lambda value:255 if value>=128 else 0);bbox=core.getbbox();assert bbox
   top=bbox[1];top_band=[(x,y,pixels[x,y][3]) for y in range(top,min(top+4,bbox[3])) for x in range(512) if pixels[x,y][3]>=128]
   top_x=sum(point[0]*point[2] for point in top_band)/sum(point[2] for point in top_band)
   crown=min([point for point in top_band if point[1]==top],key=lambda point:abs(point[0]-top_x))
   hand_rgba=list(pixels[surface[0],surface[1]])
   assert hand_rgba[3]>=128 and hand_rgba[0]>hand_rgba[1]>hand_rgba[2],(state,index,surface,hand_rgba)
   shoes=[]
   for shoe_index,roi in enumerate(shoe_rois):
    measured=band(pixels,roi);assert measured and measured['bottom_band_clear_of_ROI_horizontal_edges']
    shoes.append({"visible_role":"image_left_shoe" if shoe_index==0 else "image_right_shoe",
                  "anatomical_leg_id":None,"artist_ROI_xyxy":roi,"actual_alpha128_measurement":measured,
                  "threshold_sweep":[{"threshold":threshold,"measurement":band(pixels,roi,threshold)} for threshold in [64,128,192]]})
   support_data=[]
   for label,roi in supports:
    measured=band(pixels,roi);assert measured
    support_data.append({"visible_role":label,"artist_ROI_xyxy":roi,"actual_alpha128_measurement":measured,
                         "physical_contact_or_hidden_joint_proven":False})
   pair_x=sum(shoe['actual_alpha128_measurement']['bottom4row_alpha_centroid_x'] for shoe in shoes)/2 if len(shoes)==2 else None
   floor=max(region['actual_alpha128_measurement']['floor_edge_y_proposal'] for region in (shoes or support_data))
   proposal=[int(pair_x+.5),floor] if pair_x is not None else None
   frames.append({"state":state,"native_request_number":native,"frame":index,"source":file,
     "visible_body_alpha128_bbox":list(bbox),"visible_body_crown_core_top_y":top,
     "crown_definition":"Highest visible body/helmet/knob core pixel, no weapon/effect; not head bone or anatomical crown",
     "visible_crown_actual_pixel_xy":[crown[0],crown[1]],"visible_crown_actual_RGBA":list(pixels[crown[0],crown[1]]),
     "top4row_alpha_centroid_x":top_x,"visible_shoes":shoes,"visible_support_regions":support_data,
     "paired_shoe_midpoint_x_DIAGNOSTIC":pair_x,"visible_support_floor_edge_y_proposal":floor,
     "display_root_from_paired_visible_shoes_PROPOSAL_ONLY":proposal,
     "standing_root_px":proposal if state!='death' or index==0 else None,
     "death_standing_root_propagation_status":"NOT_PROVEN: per-component bbox-centering plus articulated collapse prevents inferring stationary standing root from pile/contact centroid" if state=='death' and index>0 else "visible paired-shoe support proposal only; not bone/COM or foot lock",
     "artist_registration_uncertainty_px":2,"physical_floor_or_world_footlock_proven":False,
     "visible_foreground_glove_surface_candidate_xy":surface,"actual_glove_surface_RGBA":hand_rgba,
     "visible_glove_pose":hand_pose,"glove_surface_point_role":"Visible brown leather surface only; not hidden palm center, handle center, grip socket or wrist bone",
     "artist_glove_surface_uncertainty_px":6,"actual_grip_px":None,"actual_handle_axis_xy":None,
     "actual_hidden_bones":None,"actual_hand_replay_mask":None,"armor_attachment_or_occlusion":None,
     "source_pose_candidate_approved_by_Root":True,"trial_accepted":False,"runtime_or_equipment_accepted":False})
 out=HERE/'visible-crown-shoe-support-glove-proposals-v001.json';assert not out.exists()
 out.write_text(json.dumps({"schema":"hero218-220-visible-registration-proposals-v001","scope":"13 actual E394-approved curated images; TEXT_ONLY pixel measurements and visible support proposals; no images/masks drawn",
  "Root_source_pose_approval":"Parent Root independently Viewed all13 and authorized source-pose candidates only; no registration/equipment/native trial acceptance. Persistent amber eyes are allowed by current hero rule.",
  "frames":frames,"runtime_canvas_display_proposal":72.*512./416.,"scale_role":"One unchanged canvas scale per row at existing authored416 standing-equivalent basis; NOT per-frame alpha height normalization",
  "Death_last_frame_original_alpha_bbox_height_px":156,"Death_no_per_frame_resizing":True,
  "late_Death_root_is_null_not_pile_center":True,"no_actual_Grip_Axis_or_hidden_bone_inferred":True,
  "Source_Content_UE_tools_ledger_changes":False,"new_annotation_images":0,"automatic_trial_acceptance":False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({"proposal":pin(out),"roots":[{"state":frame['state'],"frame":frame['frame'],"visible_shoe_root_proposal":frame['display_root_from_paired_visible_shoes_PROPOSAL_ONLY'],"standing_root":frame['standing_root_px'],"floor_edge":frame['visible_support_floor_edge_y_proposal'],"crown_y":frame['visible_body_crown_core_top_y']} for frame in frames]},ensure_ascii=False))


if __name__=='__main__':main()
