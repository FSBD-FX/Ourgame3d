"""Native159 retained original-pixel trial measurements; no image mutation or display."""
from pathlib import Path
import datetime, hashlib, json
from PIL import Image

O = Path(__file__).resolve().parent
R = O.parent

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(p, value):
    assert not p.exists(), p
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

ex_path = R / 'primary1-extraction-v003/extraction-receipt-v001.json'
ex = json.loads(ex_path.read_text(encoding='utf-8'))
assert ex['raw']['sha256'] == '1a29c97a5d8bb33e4921402675a41dc0c09fd8b398a4cafa2198d2e4f440880a'
grips = [[212,312],[165,189],[340,286],[280,352],[211,312],[211,312]]
# Directed blade-end choices for the next trial, not measured hidden handles.
axes = [[.94,-.341],[-.2,-.98],[.95,.31],[.95,.31],[.94,-.341],[.94,-.341]]
polys = [
    [[194,288],[210,290],[221,295],[228,302],[236,308],[240,316],[237,324],[230,330],[220,332],[212,335],[201,335],[191,330],[185,323],[181,313],[184,300]],
    [[154,167],[165,166],[176,169],[182,174],[186,181],[187,190],[183,199],[179,207],[169,211],[158,211],[150,208],[145,203],[143,195],[143,184],[147,175]],
    [[331,264],[344,265],[354,269],[362,276],[365,285],[363,295],[357,302],[350,306],[342,307],[334,309],[325,307],[318,303],[314,296],[314,284],[318,272]],
    [[261,329],[275,329],[288,334],[296,341],[301,350],[305,359],[302,367],[296,372],[288,374],[281,375],[272,374],[264,372],[257,366],[252,358],[251,347],[254,337]],
    [[193,289],[208,290],[220,295],[228,302],[236,309],[240,317],[236,325],[229,331],[219,333],[211,335],[200,335],[190,330],[184,323],[180,312],[184,300]],
    [[193,289],[209,290],[221,295],[229,302],[237,309],[240,317],[237,325],[230,331],[220,333],[212,335],[200,335],[191,330],[185,323],[181,312],[184,300]],
]

def foot(im, roi):
    a = im.getchannel('A')
    x0,y0,x1,y1 = roi
    last = max(y for y in range(y0,y1) if any(a.getpixel((x,y)) >= 128 for x in range(x0,x1)))
    xs = [x for x in range(x0,x1) if a.getpixel((x,last)) >= 128]
    low = [(x,y) for y in range(last-3,last+1) for x in range(x0,x1) if a.getpixel((x,y)) >= 128]
    return {'roi_px': roi, 'alpha_threshold': 128, 'last_contact_pixel_y': last,
            'span_inclusive_px': [min(xs),max(xs)], 'last_span_center_x': (min(xs)+max(xs))/2,
            'lower_pixel_boundary_y': last+1,
            'bottom_four_rows_centroid_x': sum(x for x,y in low)/len(low),
            'bottom_four_rows_pixel_count': len(low),
            'meaning': 'Observed visible boot pixels within this explicit ROI; no hidden foot, physical joint or shared depth plane inferred.'}

notes = [
    'Low near/image-left waist guard. Short sleeve-wrist-fist connection; separated relaxed far hand. Close to158 low guard, not identical pixels.',
    'Near fist is raised at the image-left side of the helmet, not the design140210. Near elbow bends outside the torso; visible far hand remains at waist. Feet shift right relative to fixed pivot.',
    'Near sleeve crosses chest and extends toward image-right; actual fist is much farther right than design291300. Fist is below the helmet. Far hand stays visibly separate below/right, not a two-handed clasp.',
    'Near fist drops before the thigh, far hand remains separate. Torso/helmet lean and apparent body height differs from the other frames; running followthrough/return must be reviewed.',
    'Already very close to low guard, not a strongly distinct extended return pose. Frame4 and5 similar appearance does not prove or disprove runtime recovery continuity.',
    'Low guard return is close to0 and158. Original native pixels are distinct; not a locally cloned frame. Transition remains unplayed by this reviewer.',
]
rows=[]
for i,f in enumerate(ex['frames']):
    p=Path(f['file']['path'])
    assert desc(p)==f['file']
    with Image.open(p) as source:
        im=source.convert('RGBA')
        near=foot(im,[140,425,240,464]);far=foot(im,[255,415,380,464])
        assert near['lower_pixel_boundary_y']==464 and far['lower_pixel_boundary_y']==459
        rgba=list(im.getpixel(tuple(grips[i])))
        assert rgba[3]==255 and rgba[0]>rgba[1]>rgba[2]
    mean=(near['last_span_center_x']+far['last_span_center_x'])/2
    rows.append({'frame':i,'source':desc(p),'source_root_px':[256,464],
        'root_role':'Fixed display pivot candidate on the actual near-sole lower edge464. No per-frame registration; x256 is not claimed to be the exact two-foot center.',
        'actual_physical_feet_root_px':None,'near_boot':near,'far_boot':far,
        'two_last_span_mean_x':mean,'two_span_mean_minus_fixed_x':mean-256,
        'grip_candidate_px':grips[i],'grip_sample_original_rgba':rgba,'grip_uncertainty_px':4,
        'grip_basis':'Manually located trial center inside the actual visible curled-finger/palm area of this retained frame. Body-only source does not show a physical handle center.',
        'actual_handle_axis_xy':None,'actual_blade_end_direction_xy':None,
        'handle_axis_candidate_xy':axes[i],'axis_is_measured':False,
        'axis_role':'Explicit next-runtime-trial directed blade-end design choice, not observed cylinder geometry. Copied as authored without normalization.',
        'observed_axis_evidence':'Finger crease and palm orientation are visible, but the absent handle/weapon prevents unique axis or blade-end sign measurement.',
        'visible_fist_replay_polygon_candidate_px':polys[i],
        'polygon_basis':'New frame-specific manual visible fist/ink boundary approximation from the retained original pixels. Approximately1-3px edge uncertainty; not an exact binary semantic mask and may include a small cuff edge.',
        'thumb_visible_status':'Curled fingers and short thumb-like crease/edge are partly visible; complete opposable-thumb-over-four-fingers anatomy cannot be certified. Frame3 is particularly ambiguous.',
        'thumb_anatomy_accepted':False,'formal_hand_acceptance':False,
        'near_far_hands_visually_separate':True,'body_pose_note':notes[i]})

viewed=[R/f'run-primary1-v003/curated/frame-{i}.png' for i in range(6)]
viewed += [R/f'primary1-extraction-v003/diagnostics-v001/frame-{i}-{role}.png' for i in range(6) for role in ['hands_inspection','feet']]
out={'schema':'fairytale-low-primary1-native159-source-marker-proposal-v3',
    'created_local':datetime.datetime.now().astimezone().isoformat(),
    'component':'SwordPrimary1','state':'sword_primary_1','native_request':159,
    'frame_count':6,'durations_ms':[85,85,60,60,155,155],'loop':False,
    'source_native_facing':1,'source_canvas_px':[512,512],'shared_row_ratio':ex['shared_row_ratio'],
    'per_frame_scale':False,'visible_body_heights_source_px':[f['alpha_bbox_size_px'][1] for f in ex['frames']],
    'fixed_display_canvas_at1280x720':72*512/416,'max_visible_body_height_px':72,
    'raw':ex['raw'],'extraction_receipt':desc(ex_path),'frames':rows,
    'actual_viewed_files':[desc(p) for p in viewed],
    'new_diagnostics_created_or_viewed':False,'raw_explicitly_viewed_by_reviewer':False,
    'continuous_GIF_or_video_played':False,'ue_imported_or_run':False,
    'standard_preview_timing_gate':False,'standard_preview_actual_durations_ms':[100]*6,
    'standard_preview_scope':'Shape-only. Source request timing remains85/85/60/60/155/155; actual kernel phase must determine combat sampling.',
    'trial_candidate_only':True,'art_or_motion_or_thumb_accepted':False,'formal_complete_units':0,
    'transition_limit':'Static0/4/5 look close to158 low guard; runtime sword silhouette, phase transitions, direction flip and hand occlusion are not accepted by this measurement.'}
p=O/'primary1-marker-proposal-v003.json';write(p,out)
review=O/'actual-static-review-v001.md'
write(review,'''# Native159 Primary1实际源量测候选

2026-10-16，root确认E149完成双SHA保留后，实际查看六个512原RGBA、六手部宽ROI和六足部裁剪，共18文件；文件SHA逐项记录于候选JSON。未看六个wholebbox裁剪、未播放GIF/视频、未运行UE，没有新建诊断图或修改源像素。

新的Grip试装候选分别为[212312]/[165189]/[340286]/[280352]/[211312]/[211312]，约±4sourcepx。均采样于实际不透明棕拳内；设计140210、291300、275328等并非实际执行值，没有被移植为socket。六帧均是近侧单拳，远手独立下垂，未见蓝紫技术色或双手合握。第2帧近拳明显向右伸出，第3帧落于大腿前，手臂保持袖口—腕—拳连接。

纯身体没有真实柄或刃，actual_handle_axis和actual_blade_end_direction均null。导出Axis仅是下一次实景试装的明确设计选择：0/4/5[.94,-.341]、1[-.2,-.98]、2/3[.95,.31]；不归一化、不称从拳像素精确测得。拳面polygon每帧重新人工描测原轮廓，约1–3px边界歧义，未获精确二元语义mask验收。短拇指样线有部分可见，但特别是3不能证明完整四指加对掌拇指结构，thumb未过。

每帧近靴实际alpha≥128最后像素行463、下边464；远靴最后458、下边459，符合深度差但不等于共同物理足平面。双最后行span中心均值258.5/264.5/256.25/256.5/256/257.75；固定[256464]是显示pivot候选而非准确双足根。第1帧均值偏移+8.5sourcepx约1.47screenpx，底四行重心也显示向右漂移；两种统计均保留，不挑一个统计假装稳定。无逐帧移动或缩放修补。

同一共享比例下实际alpha高度416/415/416/409/416/416。第3帧头身有侧转/低伏，约7sourcepx、1.21screenpx高度差；要在真实动作中区分合理跟随与体块跳变。0/4/5近似低guard，接158有希望，但第4帧几乎已回guard，不能凭静帧证明恢复节奏精致。单臂跨胸和第2帧伸距也需实际握剑后看是否自然。

标准SG atlas/GIF原样为6×100ms，因此其timing_gate=false，只作形状用途。原请求85/85/60/60/155/155未改，后续真实GetPrimaryPoseFrame采样才是本次战斗时序依据。结论仅为真实J试装候选：仍需看剑清盔、握持/拳重放、两向、衔接、脚漂与真实节奏。无动作或完整单元验收。
''')
files=[p,review,Path(__file__).resolve()]
fp=O/'measurement-freeze-v001.json'
write(fp,{'schema':'fairytale-native159-trial-measurement-freeze-v1','file_count':len(files),
    'total_bytes':sum(q.stat().st_size for q in files),'files':[desc(q) for q in files],
    'status':'Actual retained original-pixel trial measurements; directed axes are explicit design choices, not physical facts.'})
print(json.dumps({'proposal':desc(p),'review':desc(review),'freeze':desc(fp),'grips':grips,
                  'feet_last_span_mean_x':[f['two_last_span_mean_x'] for f in rows]},ensure_ascii=False))
