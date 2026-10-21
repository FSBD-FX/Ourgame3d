"""Read retained native158 pixels and freeze manual trial markers; never alter any image."""
from pathlib import Path
import datetime,hashlib,json
from PIL import Image
R=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
ex=json.loads((R/'ready-extraction-v002/extraction-receipt-v001.json').read_text(encoding='utf-8'))
grips=[[212,313],[212,312],[207,316],[214,312]]
polys=[
 [[192,290],[207,290],[218,295],[226,302],[233,311],[235,317],[231,324],[224,330],[216,330],[208,333],[198,334],[190,329],[183,321],[180,309],[184,298]],
 [[193,289],[209,289],[220,294],[227,302],[234,310],[234,318],[230,325],[223,330],[215,330],[207,332],[197,333],[189,328],[183,321],[181,308],[185,297]],
 [[187,292],[203,293],[213,297],[221,304],[229,313],[229,319],[225,328],[218,332],[211,335],[202,335],[192,336],[184,331],[178,324],[176,311],[180,301]],
 [[194,288],[211,289],[221,294],[229,301],[236,310],[236,317],[232,324],[225,329],[218,329],[210,332],[200,334],[191,329],[185,322],[183,309],[187,298]]]
def foot(im,roi):
 a=im.getchannel('A');x0,y0,x1,y1=roi
 ys=[y for y in range(y0,y1) if any(a.getpixel((x,y))>=128 for x in range(x0,x1))];last=max(ys)
 xs=[x for x in range(x0,x1) if a.getpixel((x,last))>=128]
 low=[(x,y) for y in range(last-3,last+1) for x in range(x0,x1) if a.getpixel((x,y))>=128]
 return {'roi_px':roi,'alpha_threshold':128,'last_contact_pixel_y':last,'span_inclusive_px':[min(xs),max(xs)],'last_span_center_x':(min(xs)+max(xs))/2,
  'lower_pixel_boundary_y':last+1,'bottom_four_rows_centroid_x':sum(x for x,y in low)/len(low),'bottom_four_rows_pixel_count':len(low),
  'meaning':'Observed visible boot sole in an explicit boot ROI. Does not infer a hidden shoe or a shared depth plane.'}
rows=[]
for i,f in enumerate(ex['frames']):
 p=Path(f['file']['path']);assert desc(p)==f['file'];im=Image.open(p).convert('RGBA')
 near=foot(im,[140,425,240,464]);far=foot(im,[255,415,375,464]);mean=(near['last_span_center_x']+far['last_span_center_x'])/2
 assert near['lower_pixel_boundary_y']==464
 rgba=list(im.getpixel(tuple(grips[i])));assert rgba[3]>=128
 rows.append({'frame':i,'source':desc(p),'source_root_px':[256,464],
  'root_role':'Fixed display pivot candidate. Actual near-sole lower edge is464 in every frame; fixed x256 is close to observed two-sole centers, not an exact physical joint/feet center.',
  'actual_physical_feet_root_px':None,'near_boot':near,'far_boot':far,'two_last_span_mean_x':mean,'two_span_mean_minus_fixed_x':mean-256,
  'grip_candidate_px':grips[i],'grip_sample_original_rgba':rgba,'grip_uncertainty_px':4,
  'grip_basis':'Manual trial handle center estimated inside the visible closed-finger/palm area from this retained original source, not the withdrawn275315/155design. Invisible handle center is not directly observed.',
  'actual_handle_axis_xy':None,'actual_blade_end_direction_xy':None,
  'handle_axis_candidate_xy':[.94,-.341],'axis_is_measured':False,'axis_role':'Explicit root trial design choice; neither directed blade end nor exact invisible cylinder axis can be measured from these body-only pixels.',
  'observed_axis_evidence':'Diagonal curled-finger strokes are visible and support a roughly transverse grip orientation. The wrapped3D surface does not uniquely determine a cylinder or blade-end sign.',
  'visible_fist_replay_polygon_candidate_px':polys[i],
  'polygon_basis':'New manual visible-fist/ink outline traced from this frame and checked against original boundary pixels. Approximate1-3px edge uncertainty; excludes belt/cuff as far as visible. Not a certified binary semantic mask.',
  'thumb_visible_status':'Partial short hooked contour/crease near upper-inner finger region is more readable than155, but cannot certify a complete opposable thumb across four fingers in every pose.',
  'thumb_anatomy_accepted':False,'formal_hand_acceptance':False,'near_far_hands_visually_separate':True,
  'body_pose_note':('Torso has more pronounced breast/waist fold and slight side-turn shading than frames0/2; no clear head twist or near/far arm exchange. Running volume/breathing seam remains unreviewed.' if i in [1,3] else 'Near arm remains short and low at the near/image-left waist; distinct relaxed far hand. No clear body/helmet twist.')})
out={'schema':'fairytale-low-ready-native158-source-marker-proposal-v2','created_local':datetime.datetime.now().astimezone().isoformat(),
 'component':'SwordReady','state':'sword_ready_idle','native_request':158,'frame_count':4,'durations_ms':[167]*4,'loop':True,
 'source_native_facing':1,'source_canvas_px':[512,512],'shared_row_ratio':ex['shared_row_ratio'],'per_frame_scale':False,
 'visible_body_heights_source_px':[415,415,415,416],'fixed_display_canvas_at1280x720':72*512/416,'max_visible_body_height_px':72,
 'raw':ex['raw'],'extraction_receipt':desc(R/'ready-extraction-v002/extraction-receipt-v001.json'),'frames':rows,
 'actual_viewed_files':[desc(R/f'run-ready-v002/curated/frame-{i}.png') for i in range(4)]+[desc(R/f'ready-extraction-v002/diagnostics-v001/frame-{i}-{role}.png') for i in range(4) for role in ['near_hand_inspection','feet']],
 'new_diagnostics_created_or_viewed':False,'raw_explicitly_viewed_by_reviewer':False,'continuous_GIF_or_video_played':False,'ue_imported_or_run':False,
 'trial_candidate_only':True,'art_or_motion_or_thumb_accepted':False,'formal_complete_units':0,
 'transition_limit':'157 Primary1 still has old across-chest near-face guard. This proposal does not modify or accept those transitions.'}
p=O/'ready-marker-proposal-v002.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=O/'actual-static-review-v001.md';assert not review.exists();review.write_text('''# Native158低位Ready实际源量测候选

2026-10-16。root确认E141后，实际逐帧查看4个原512RGBA、4个原像素近手宽ROI、4个脚部裁剪；共12文件。未看新建诊断、wholebbox四裁剪、连续GIF/视频或UE。全部已看文件的原SHA记录在候选JSON。

实际近拳位于image-left近腰侧，并未到设计275315；新候选Grip为[212313]/[212312]/[207316]/[214312]，误差约±4sourcepx。四帧握点均落在实际不透明棕手像素内。近臂短、袖腕拳连接可见，远手在右下独立垂放，没有155跨胸竖拳或156双手合握。并未为了执行设计点而移动/拟合源图。

纯拳无真实柄/刃，无法唯一测出轴或剑刃正方向。JSON实际轴和实际blade-direction均null；[.94,-.341]只保留为root明确的试装设计选择。可见斜向指褶不等于精确圆柱轴。近拳有比155更可读的短钩状拇指候选线，但仍不足以逐帧确认完整对掌拇指压在四指上，thumb未验收。新15点拳面polygon来自每帧原像素边界人工描测，约1–3px不确定，绝非旧155/V007或精确二元语义mask；scale的真实ownership应另按原源划分。

每帧近靴alpha≥128最后行463/下边464；远靴分别459/459/459/458，下边460/460/460/459，固定3/4视图不能强制双足同一源Y。双最后接触span中心均值255.25/258.25/258.5/259.5。保留[256464]可作为与真实近足下边一致的固定显示pivot，但不是每帧物理足根；最大X差3.5sourcepx约0.61screenpx，最后一行窄span还存在像素取样歧义，JSON另附底四行重心。没有逐帧平移/缩放消除漂移。

头盔、头身和near/far角色整体仍可辨，没有明显伸长上臂或扭头。1/3胸腰折线/凸起与侧转明暗比0/2更明显，可能在循环中形成体块跳变；静帧不能把它判成自然呼吸，标准QA0也不解决这个问题。实际高度415/415/415/416在同一sharedratio下保留，max72只是显示大小事实。

结论：可供root低位剑源试装，必须用本实际握点而非275315；真实剑alpha清盔/手覆盖、拇指、呼吸连续性和新Primary起止衔接均未通过。旧157没有被本量测改成匹配新guard。未生成、改图、注册/导入、写Source或台账。
''',encoding='utf-8')
files=[p,review,Path(__file__).resolve()];fp=O/'measurement-freeze-v001.json';assert not fp.exists();fp.write_text(json.dumps({'file_count':len(files),'total_bytes':sum(q.stat().st_size for q in files),'files':[desc(q) for q in files],'status':'Original-pixel lowReady trial measurements; axis is explicit design choice; no acceptance.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proposal':desc(p),'review':desc(review),'freeze':desc(fp),'grips':grips,'feet_mean':[r['two_last_span_mean_x'] for r in rows]},ensure_ascii=False))
