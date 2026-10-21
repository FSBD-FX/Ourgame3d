"""Freeze native157 visible-pixel marker estimates, without changing art or old evidence."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parent;M=R/'primary1-measurement-v002'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
e=json.loads((M/'pixel-evidence-v001.json').read_text(encoding='utf-8'))
grips=[[258,281],[202,125],[291,264],[352,330],[258,280],[258,281]]
axes=[[0,-1],[.5,-.8660254],[.65,-.7599342],[.94,-.3411744],[0,-1],[0,-1]]
polys=[
 [[243,255],[264,256],[275,262],[280,270],[278,282],[274,286],[272,298],[266,303],[246,305],[232,301],[225,295],[225,278],[231,267]],
 [[193,102],[205,101],[217,106],[226,113],[229,120],[225,129],[221,135],[215,143],[204,148],[192,147],[179,141],[176,132],[180,120],[186,109]],
 [[282,241],[300,242],[310,249],[317,259],[315,269],[310,279],[303,287],[294,290],[280,285],[269,280],[262,271],[264,257],[271,247]],
 [[341,307],[362,308],[374,313],[380,322],[378,335],[372,344],[365,349],[362,354],[353,357],[345,352],[335,345],[326,337],[325,325],[330,314]],
 [[243,254],[264,255],[275,261],[280,269],[279,281],[274,286],[272,297],[266,302],[246,304],[232,300],[225,294],[225,277],[231,266]],
 [[243,255],[264,256],[275,262],[280,270],[279,282],[274,287],[272,298],[266,303],[246,305],[232,301],[225,295],[225,278],[231,267]]]
rows=[]
for i,r in enumerate(e['frames']):
 assert desc(Path(r['source']['path']))==r['source']
 rows.append({'frame':i,'source':r['source'],'diagnostic_crops':r['diagnostic_crops'],
  'source_root_px':[256,464],'root_role':'Fixed display pivot for trial, not a claim of exact per-pose sole center.',
  'near_boot':r['near_boot'],'far_boot':r['far_boot'],'two_contact_mean_x':r['dual_visible_contact_center_x'],
  'two_contact_x_minus_fixed_pivot':r['dual_visible_contact_center_x']-256,
  'grip_candidate_px':grips[i],'grip_uncertainty_px':3 if i!=3 else 4,
  'handle_axis_candidate_xy':axes[i],'axis_uncertainty_degrees':15 if i in [1,2,3] else 10,
  'axis_evidence':'New estimate perpendicular to the visible curled-finger crease direction. Invisible cylindrical handle and blade-end sign are not directly observable. Axis sign is chosen only for an initial overlay trial; do not certify exact sword orientation from body-only art.',
  'visible_fist_replay_polygon_candidate_px':polys[i],
  'polygon_basis':'New manual outline of the visible active near fist in this E133-retained unscaled crop. Approximately1-2px boundary error; includes original hand/ink only as a trial polygon, not a certified binary semantic mask. No old V007 polygon or designed guide coordinates reused.',
  'far_hand_role':'Separate relaxed far-waist hand, not assisting the active grip.',
  'far_hand_local_occlusion':('Near fist is in front; far fingers emerge beneath/behind it. Their two forearm paths remain distinguishable. Crowded overlap must be checked with actual sword pixels, especially the lower-left fist boundary.' if i==3 else 'Far hand is visually separate from the active fist.'),
  'thumb_status':'Some finger/palm overlap is visible, but an independently traceable opposable thumb across the grip is not established for the complete state. Thumb anatomy remains unaccepted.',
  'formal_hand_acceptance':False})
out={'schema':'fairytale-sword-primary1-source-marker-proposal-v2','created_local':datetime.datetime.now().astimezone().isoformat(),
 'component':'SwordPrimary1','state':'sword_primary_1','native_request':157,'source_native_facing':1,'source_canvas_px':[512,512],
 'durations_ms':[85,85,60,60,155,155],'phase_boundaries_ms':[0,85,170,230,290,445,600],
 'runtime_sampler':'Existing GetPrimaryPoseFrame on accepted Action deadlines; phase durations are source contract, not an override of ActionSpeed.',
 'shared_row_ratio':.832,'per_frame_scale':False,'visible_source_heights_px':[409,416,410,407,412,410],
 'fixed_display_canvas_at1280x720':72*512/416,'maximum_visible_body_height_px':72,
 'ready_marker_proposal':desc(R/'ready-measurement-v001/ready-marker-proposal-v001.json'),
 'frames':rows,'actual_static_viewed':[f'run-primary1-v002/curated/frame-{i}.png' for i in range(6)]+[f'primary1-measurement-v002/frame-{i}-{role}-diagnostic.png' for i in range(6) for role in ['near_hand_and_local_occlusion','feet']],
 'continuous_motion_played':False,'ue_imported':False,'art_or_action_accepted':False,'trial_candidate_only':True,'formal_complete_units':0}
p=M/'primary1-marker-proposal-v002.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=R/'primary1-extraction-v002/actual-static-review-v001.md';assert not review.exists()
review.write_text('''# Native157 Primary1: limited ordinary-input trial candidate

2026-10-16. Actual review of the E131-retained raw, all six E132-retained512RGBA frames and all twelve E133-retained unscaled near-hand/foot crops. No GIF/video playback or UE action review occurred. Original/extracted files, timing and all previous failed outputs remain unchanged.

The six frames now use one active larger near arm. The far arm remains down beside the waist, and frames0/4/5 return to the single across-chest guard close to native155 Ready. The blue/purple thigh/knee patches visible in rejected156 are absent. Canonical bell-helmet volume, cloth and brown gloves/boots remain broadly recognizable at the fixed three-quarter camera; this visual assessment is separate from the bbox/layout gate. Frame1 is a genuine raised-arm load, frame2 crosses the chest, and frame3 lowers/extends the near fist. The body alone cannot prove the final blade arc or impact; actual sword overlay is required.

Frame3's large near fist lies in front of the far hand. Far fingers emerge below/behind it and the far sleeve path remains distinguishable; this is compatible with depth overlap rather than156's mutually clasped hands. It is still crowded, and the lower-left near-fist polygon can overlap the visible far fingers within1-2px tracing uncertainty. Do not certify zero hand collision or exact finger ownership without the actual sword replay. Distinct thumb anatomy is not established for the complete sequence.

The source-bound marker proposal contains new grip estimates [258,281], [202,125], [291,264], [352,330], [258,280], [258,281], approximate finger-derived cylinder axes and visible-fist polygons. Grip uncertainty is±3px (±4px atframe3), axis uncertainty approximately±10-15°. Invisible handle/blade-end direction is not measured; the chosen sign is only for initial overlay. These are not old V007/root472/HandPolygon/socket values. A vertical sword at the guard or raised frame can approach the helmet/eye area; inspect actual blade/guard occlusion at72px in both facings before accepting it.

Native components share one .832 extraction ratio. Visible heights409/416/410/407/412/410 remain their actual drawing/pose variation, with no individual fit. Fixed display canvas88.6153846154 gives a maximum72px body; first/last are about71px, slightly different from native155's approximately72px. Frame5→Ready0 therefore still needs running seam review, rather than an identity claim based on matching bboxes.

All near soles reach last alpha≥128 pixel463, far soles462. Mean two-contact X values are256.75/253.75/254.5/248.5/256.5/257. Fixed[256,464] is defensible as a common display pivot tied to the near lower edge, but is not the exact foot center for every pose. Frame3 is7.5sourcepx left of it (about1.3screenpx at72px), from stance and bbox-centered registration together. Preserve and observe this drift; do not silently translate/normalize individual frames or claim planted feet have been dynamically certified.

Conclusion: suitable for a clearly marked ordinary-J source/weapon alignment trial. Single-hand role correction and source file gates have evidence. Complete thumb anatomy, blade path, continuous motion, hit timing alignment, weapon occlusion, armor/action combinations and the content unit remain unaccepted. No new fallback to old human bodies is implied.
''',encoding='utf-8')
files=[p,review,Path(__file__).resolve()]
f=M/'review-marker-freeze-v001.json';assert not f.exists();f.write_text(json.dumps({'file_count':len(files),'total_bytes':sum(x.stat().st_size for x in files),'files':[desc(x) for x in files],'status':'Native157 trial marker estimates and limited static review only.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposal':desc(p),'review':desc(review),'freeze':desc(f)},ensure_ascii=False))
