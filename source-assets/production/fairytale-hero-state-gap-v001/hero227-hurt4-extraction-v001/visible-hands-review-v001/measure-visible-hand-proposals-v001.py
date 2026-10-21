"""Visible-source hand proposals only, never actual hilt/bones or image editing."""
from pathlib import Path
import hashlib,json
from PIL import Image
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
RUN=BASE/"runs/run-hurt227-shared-HD-v001"
SEEDS=[{"grip":[236,303],"thumb":[241,283],"gloveROI":[202,270,264,337],"wristROI":[174,273,215,326]},
 {"grip":[194,289],"thumb":[201,269],"gloveROI":[155,258,222,326],"wristROI":[136,269,175,315]},
 {"grip":[205,289],"thumb":[219,274],"gloveROI":[169,261,237,320],"wristROI":[148,259,187,301]},
 {"grip":[218,303],"thumb":[233,290],"gloveROI":[181,278,249,335],"wristROI":[164,276,200,318]}]
def pin(p):
 b=p.read_bytes();return {"path":p.as_posix(),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def main():
 gate=json.loads((BASE/"E415-before-curated-View-check-v001.json").read_text(encoding="utf-8"));assert gate["root_explicit_View_allowed"] and gate["differences"]==0
 rows=[]
 for i,s in enumerate(SEEDS):
  p=RUN/"curated"/("frame-"+str(i)+".png");q=pin(p);assert q==gate["frames"][i]["F"]
  e=Path(gate["frames"][i]["E"]["path"]);assert (pin(e)["bytes"],pin(e)["sha256"])==(q["bytes"],q["sha256"])
  with Image.open(p) as opened:
   im=opened.convert("RGBA");assert im.size==(512,512)
   features={}
   for name in ["grip","thumb"]:
    xy=s[name];rgba=list(im.getpixel(tuple(xy)));assert rgba[3]>=192 and rgba[0]>1.4*rgba[1] and rgba[1]>rgba[2]
    features[name]={"author_selected_visible_surface_xy":xy,"actual_RGBA":rgba,"integer_point_is_source_pixel_not_measured_bone":True}
   alpha=im.getchannel("A");core=alpha.point(lambda v:255 if v>=128 else 0).getbbox()
   rows.append({"frame":i,"source":q,"source_facing":"nativeRight3quarter","source_pose_candidate_approved_independently":True,"near_hand_closed_visible":True,"visible_thumb_opposition_plausible":True,"thumb_review_scope":"visible opposing brown lobe/curled finger division; no hidden thumb joint/tendon or grasp force inferred","near_wrist_forearm_visible_continuity":True,"nearhand_author_ROI_xyxy":s["gloveROI"],"wrist_cuff_interface_author_ROI_xyxy":s["wristROI"],"wrist_ROI_is_not_wrist_bone":True,"sampled_visible_features":features,"visibleGrip_PROPOSAL_ONLY_xy":s["grip"],"visibleGrip_author_uncertainty_source_px":8,"uncertainty_role":"author conservative search window, not statistical confidence or fitted actual hilt centre","actual_hilt_contact_grip_px":None,"actual_handle_axis_xy":None,"author_hilt_axis_proposal":None,"axis_null_reason":"No real handle/two exposed shaft ends in body source. Glove fold or wrist direction doesnot uniquely determine a military-sword axis. Supply artist axis then realprop composite review, never derive hidden axis/bone.","actual_hand_replay_mask":None,"actual_hidden_bones":None,"floor":None,"Root":None,"armor_attachment_or_depth":None,"alpha128_bbox":list(core),"true_SWD_contact_accepted":False,"LGT_armor_accepted":False,"native_or_trial_accepted":False})
 out={"schema":"hero227-visible-nearhand-author-proposals-v001","scope":"PostE415 original512 stills review and actualRGBA surface samples only. No images/masks generated, no hand pixels edited; coordinates are authored candidate seeds not true hilt geometry.","retention_gate":pin(BASE/"E415-before-curated-View-check-v001.json"),"frames":rows,"QA_animation_played":False,"all_four_original_stills_viewed":True,"all_true_Grip_Axis_masks_null":True,"source_pose_candidate_only":True,"runtime_or_equipment_acceptance":False}
 p=HERE/"visible-hand-proposals-v001.json";assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"output":pin(p),"Grip_proposals":[z["visibleGrip_PROPOSAL_ONLY_xy"] for z in rows],"all_actual_axes_null":True,"new_images":0},ensure_ascii=False))
if __name__=="__main__":main()
