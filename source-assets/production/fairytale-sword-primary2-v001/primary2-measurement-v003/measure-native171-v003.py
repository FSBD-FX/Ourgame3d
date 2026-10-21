from __future__ import annotations
import datetime, hashlib, json, pathlib
import numpy as np
from PIL import Image

HERE=pathlib.Path(__file__).resolve().parent
FAMILY=HERE.parent
SOURCE=FAMILY/'run-primary2-v004/curated'

def fact(p):
    p=pathlib.Path(p); b=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def rgba(a,xy):
    x,y=xy; return {'xy':list(xy),'rgba':a[y,x].tolist()}

def samples(a,xy,r=3):
    x,y=xy
    return [rgba(a,[x+dx,y+dy]) for dx,dy in [(0,0),(-r,0),(r,0),(0,-r),(0,r)]]

# Manually proposed from the six actual retained 512 sources. These are not
# derived from an alpha bounding box, old169 markers or a generated design guide.
PALMS=[[207,313],[167,333],[281,318],[311,253],[280,275],[207,313]]
HAND=[
 [[194,289],[207,292],[220,298],[230,305],[235,313],[231,320],[229,325],[223,330],[215,331],[208,329],[202,335],[194,334],[184,328],[179,320],[178,310],[180,301],[186,295]],
 [[157,311],[168,311],[177,315],[184,321],[190,327],[193,336],[189,345],[182,352],[170,356],[159,353],[151,348],[146,340],[145,330],[148,320]],
 [[270,293],[282,294],[293,300],[302,307],[307,315],[304,323],[297,329],[292,333],[286,337],[276,340],[267,337],[259,333],[253,324],[251,316],[255,305],[262,297]],
 [[301,226],[312,227],[322,230],[329,238],[334,246],[335,254],[331,263],[325,270],[315,276],[305,278],[294,274],[288,267],[286,257],[290,244],[292,233]],
 [[275,248],[286,248],[295,254],[301,262],[304,273],[301,283],[295,289],[290,294],[282,298],[271,298],[260,292],[256,282],[260,267],[264,258],[269,252]],
 [[194,289],[207,291],[219,297],[230,305],[235,313],[231,320],[229,325],[223,331],[215,333],[207,331],[201,335],[193,334],[184,328],[179,320],[178,309],[181,300],[187,294]],
]
SLEEVE=[
 [[215,225],[203,227],[190,237],[178,252],[169,269],[166,281],[177,276],[191,276],[204,280],[211,289],[220,278],[225,262],[229,248],[228,235]],
 [[221,239],[209,241],[198,247],[185,257],[172,271],[158,282],[153,293],[166,289],[179,290],[188,297],[197,284],[208,278],[223,264],[229,251]],
 [[224,229],[213,234],[208,243],[208,256],[210,275],[216,290],[228,302],[230,290],[241,285],[253,287],[251,277],[243,266],[242,250],[238,238]],
 [[224,226],[214,228],[209,236],[210,247],[217,262],[229,273],[243,283],[256,285],[268,278],[266,263],[268,252],[257,253],[249,249],[241,237],[232,229]],
 [[222,229],[211,234],[207,242],[204,259],[202,277],[201,292],[205,301],[214,307],[228,308],[240,303],[235,294],[233,282],[237,274],[241,273],[241,255],[236,242],[229,233]],
 [[215,225],[203,228],[190,237],[179,251],[170,268],[167,281],[178,276],[191,276],[204,280],[212,289],[220,279],[225,262],[229,248],[228,235]],
]
SLEEVE_CUFF=[
 [[165,282],[174,276],[186,274],[199,277],[207,284],[210,291]],
 [[148,295],[159,291],[171,291],[181,294],[188,302],[187,313]],
 [[230,293],[235,286],[244,285],[253,290],[261,300]],
 [[279,249],[269,250],[265,258],[266,270],[273,282],[284,289]],
 [[243,272],[235,274],[231,282],[233,295],[240,306],[253,314]],
 [[166,281],[176,276],[187,275],[200,278],[208,286],[211,292]],
]
CUFF_GLOVE=[
 [[194,289],[186,295],[180,302],[178,311]],
 [[157,311],[168,311],[177,315],[181,319]],
 [[262,297],[255,305],[251,316],[253,324]],
 [[293,239],[290,247],[286,257],[288,267],[296,275]],
 [[269,252],[264,258],[260,267],[256,282],[260,292]],
 [[194,289],[187,294],[181,300],[178,309]],
]
DESIGN_A=[
 {'Chest':[261,268],'NearShoulder':[210,246],'FarShoulder':[305,271]},
 {'Chest':[261,275],'NearShoulder':[211,257],'FarShoulder':[305,275]},
 {'Chest':[267,266],'NearShoulder':[218,248],'FarShoulder':[305,271]},
 {'Chest':None,'NearShoulder':[221,237],'FarShoulder':None},
 {'Chest':None,'NearShoulder':[213,246],'FarShoulder':[307,275]},
 {'Chest':[261,268],'NearShoulder':[210,246],'FarShoulder':[305,271]},
]
NULL_REASON={
 (3,'Chest'):'Near sleeve/forearm and brown cuff cross central chest; exposed grey pixels cannot be asserted to be an uncovered chest attachment surface.',
 (4,'Chest'):'Raised near glove covers central chest; the sampled former central zone is brown glove, not visible shirt.',
 (3,'FarShoulder'):'Raised near fist covers the otherwise expected far upper-shoulder zone. Its actual samples are glove/outline or transparent, not a distinguishable far cloth attachment surface.'
}
VISUAL=[
 '紧凑低位闭拳；近手指缝与腰带黑线邻接，不能据此确认握柄孔。远手张开，不能混作持剑近手。',
 '近手已闭合并形成短的侧向拳轮廓；不再像170相1张开下垂。右缘小棕回钩/暗隙可读为拇指，但精确绕柄结构未证。',
 '近拳位于腹前，袖明显折转，与169水平伸臂不同；指缝、近袖口和拳外线仍有共享暗线。',
 '近拳抬到盔下胸前，短折肘轮廓可辨；拳上缘可见小棕形/暗缝，未见明确独立柄片，拇指轮廓仍不唯一。',
 '胸前收腕，紧凑闭拳；拳顶暗环与小棕形可作折指解释，不能认证持柄孔或独立拇指。胸面遮挡。',
 '低位闭拳返回，盔衣棕手靴身份延续；与相0近似，但不是相同像素/连续衔接或足锁证明。'
]

verification=json.loads((HERE/'source-verification-v003.json').read_text(encoding='utf-8'))
assert verification['all_verified'] and not verification['errors']
frames=[]
for i in range(6):
    p=SOURCE/f'frame-{i}.png'; f=fact(p); expected=verification['frames'][i]['source']; assert f==expected
    im=Image.open(p); assert im.mode=='RGBA' and im.size==(512,512)
    a=np.asarray(im); current_rgba=rgba(a,PALMS[i])['rgba']; assert current_rgba[3]==255 and current_rgba[0]>current_rgba[1]+40
    attachments={}
    for name,pt in DESIGN_A[i].items():
        attachments[name]={
          'point':pt,'kind':('manual visible cloth attachment DESIGN; not measured joint' if pt is not None else 'occluded/not distinguishable; no measured design A'),
          'uncertainty_source_px':(5 if name=='FarShoulder' else 3) if pt is not None else None,
          'source_rgba_at_design_point':rgba(a,pt)['rgba'] if pt is not None else None,
          'local_cross_rgba':samples(a,pt) if pt is not None else [],
          'hidden_joint':None,'future_component_feature_A':None,'measured_bone':False,
          'reason':NULL_REASON.get((i,name),'Candidate on actual visible grey cloth; location is an attachment design choice, not an anatomical measurement.')
        }
    null_diagnostics=[]
    for name in ['Chest','FarShoulder']:
        if DESIGN_A[i][name] is None:
            points=([[261,268],[268,264],[277,263]] if name=='Chest' else [[305,260],[305,271],[307,277],[310,287]])
            null_diagnostics.append({'component':name,'source_samples': [rgba(a,pt) for pt in points],'null_not_filled_with_old_pose':True})
    feet={}
    for name,lo,hi in [('near_visible_shoe',110,250),('far_visible_shoe',260,400)]:
        q=a[400:480,lo:hi,3]>=128; yy,xx=np.where(q); bottom=int(yy.max()+400)
        row_x=np.flatnonzero(q[bottom-400])+lo; mid=int(row_x[len(row_x)//2]); band=q[bottom-403:bottom-399]; by,bx=np.where(band)
        feet[name]={
          'manually_selected_shoe_roi':[lo,400,hi,480],'alpha_threshold':128,'lowest_solid_row_y':bottom,
          'visible_sole_sourcepoint':rgba(a,[mid,bottom]),'point_method':'Actual solid pixel at median x of lowest solid-alpha row; not bbox centre, bone, 3D contact or foot lock.',
          'bottom_four_rows_x_centroid':float((bx+lo).mean()),'bottom_four_rows_solid_pixel_count':int(band.sum()),
          'bottom_four_rows_x_min':int(bx.min()+lo),'bottom_four_rows_x_max_inclusive':int(bx.max()+lo),
          'hidden_ankle_bone':None,'actual_ground_contact':None
        }
    helmet={}
    for name,y0,y1 in [('upper_brim_front_band',145,185),('lower_brim_front_band',205,236)]:
        roi=[300,y0,400,y1]; mask=a[y0:y1,300:400,3]>=128; yy,xx=np.where(mask); x=int(xx.max()+300); ys=yy[xx==xx.max()]+y0; y=int(ys[len(ys)//2])
        helmet[name]={'manual_band_roi':roi,'alpha_threshold':128,'visible_foremost_sourcepoint':rgba(a,[x,y]),'meaning':'Rightmost solid silhouette pixel in actual observed helmet-front band; not bone, socket or entire helmet ownership mask.'}
    prior=np.asarray(Image.open(FAMILY/f'run-primary2-v003/curated/frame-{i}.png').convert('RGBA'))
    changed=np.any(a!=prior,axis=2)
    frames.append({
       'frame':i,'duration_from_kernel_ms':[75,75,60,60,135,135][i],'source':f,
       'all_E209_matching_copies':verification['frames'][i]['all_E209_matching_copies'],
       'source_nonzero_alpha_bbox_diagnostic_only':verification['frames'][i]['nonzero_alpha_bbox'],
       'viewed_original_512':True,'visual_observation':VISUAL[i],
       'grip_candidate':{'xy':PALMS[i],'uncertainty_plus_minus_px':3,'type':'MANUAL actual visible glove palm patch candidate; not measured handle centre or whole-hand bbox centre','selection_basis':'Opaque brown palm patch beside visible finger/knuckle seams, selected separately in each actual171 phase. No sword in source; final handle placement remains a fit trial.','source_rgba_samples':samples(a,PALMS[i]),'actual_handle_axis':None,'actual_thumb_contour':None},
       'visible_near_hand_polygon_candidate':{'points':HAND[i],'uncertainty_plus_minus_px':4,'scope':'Visible glove/fingers including outer ink approximately, cuff transition separately listed; not complete AA ownership.','vertices_source_rgba':[rgba(a,pt) for pt in HAND[i]],'binary_ownership_or_complete_reconstruction':False,'uncertainties':'Shared black seams with cuff/belt/forearm and curved finger lobes; vertices may fall a few pixels either side. Must retrace for exact pixel layering; do not use directly as an accepted body mask.'},
       'visible_near_sleeve_contour_candidate':{'points':SLEEVE[i],'uncertainty_plus_minus_px':5,'vertices_source_rgba':[rgba(a,pt) for pt in SLEEVE[i]],'kind':'Manual visible grey sleeve outline proposal, not hidden upper-arm/elbow reconstruction or binary ownership.'},
       'visible_sleeve_to_brown_cuff_boundary_candidate':{'points':SLEEVE_CUFF[i],'uncertainty_plus_minus_px':4,'source_rgba':[rgba(a,pt) for pt in SLEEVE_CUFF[i]],'kind':'Manual seam curve; shared dark border uncertain; no alpha ownership assigned.'},
       'visible_cuff_to_glove_boundary_candidate':{'points':CUFF_GLOVE[i],'uncertainty_plus_minus_px':4,'source_rgba':[rgba(a,pt) for pt in CUFF_GLOVE[i]],'kind':'Manual seam curve; same brown material may merge, no proof of hidden wrist.'},
       'body_design_A_candidates':attachments,'occlusion_diagnostic_samples':null_diagnostics,
       'visible_feet':feet,'visible_helmet':helmet,
       'same_phase_170_to_171_changed_rgba_pixel_count':int(changed.sum()),
       'comparison_scope':'Whole512 raw RGBA difference count only; no transform applied. Nonzero count is not a semantic identity/change-area measurement.',
       'actual_elbow_bones':None,'actual_elbow_angle':None,'actual_blade_axis':None,'accepted_grip_or_thumb':False,
    })

near=[x['visible_feet']['near_visible_shoe']['bottom_four_rows_x_centroid'] for x in frames]
far=[x['visible_feet']['far_visible_shoe']['bottom_four_rows_x_centroid'] for x in frames]
report={
 'schema':'fairytale-native171-primary2-visible-feature-candidates-v3','created_local':datetime.datetime.now().astimezone().isoformat(),
 'status':'Actual visible-feature / attachment-design candidates only; not body-motion, grip, armour, foot-lock or formal-unit acceptance',
 'source_native':171,'source_canvas':[512,512],'source_mode':'RGBA','frame_count':6,
 'coordinate_convention':'Original512 image x right / y down; integer pixel indices. ROIs half-open. Hand contour lists are manual candidate polygons with source-pixel uncertainty, not binary ownership.',
 'source_verification':fact(HERE/'source-verification-v003.json'),'extraction_freeze':verification['extraction_freeze'],
 'raw':fact(FAMILY/'run-primary2-v004/raw/sword_primary_2.png'),
 'known_standard_timing_diagnosis':fact(FAMILY/'primary2-extraction-v004/standard-timing-diagnosis-v004.json'),
 'source_shared_ratio':0.8702928870292888,
 'display_contract':{'root':[256,464],'maximum_body_height':72,'reference_visible_height':416,'canvas':72*512/416,'source_to_screen':72/416,'runtime_observed_this_source':False,'root_is_measured_bone_or_contact':False,'per_frame_fit_or_foot_shift':False},
 'frames':frames,
 'independent_findings':{
    'six_near_hands_read_as_closed':True,'phase1_open_hand_correction_visible':True,
    'fingers_and_thumb_fully_resolved':False,'definite_independent_handle_fragment_seen':False,
    'phase1_thumb_risk':'Small dark notch and brown hook on glove right edge; closed glove silhouette is clear, exact cylindrical grip/short thumb wrap is not established.',
    'phase3_4_thumb_risk':'Top brown folds and dark gaps are ambiguous glove details; no clear foreign handle, but no accepted real thumb contour or grip channel.',
    'motion_direction':'Belly-height phase2 to chest/helmet-under phase3 gives a rising static sequence with compact sleeve; only future actual blade fit / native paired inputs can judge the strike.',
    'helmet_identity':'Bell silhouette, top bolt and two amber eyes remain visible throughout; source tilt/shading changes, no exact-pixel identity or continuous head stability claim.',
    'near_shoe_lowest_solid_y':[x['visible_feet']['near_visible_shoe']['lowest_solid_row_y'] for x in frames],
    'far_shoe_lowest_solid_y':[x['visible_feet']['far_visible_shoe']['lowest_solid_row_y'] for x in frames],
    'near_sole_centroid_span_source_px':max(near)-min(near),'far_sole_centroid_span_source_px':max(far)-min(far),
    'near_sole_centroid_span_planned_screen_px':(max(near)-min(near))*72/416,'far_sole_centroid_span_planned_screen_px':(max(far)-min(far))*72/416,
    'source_details_changed_in_all_six_phases':all(x['same_phase_170_to_171_changed_rgba_pixel_count']>0 for x in frames),
    'changes_not_pixel_locked':'171 is not a patch preserving all five unrequested phases pixel-exact; every source SHA differs. Similar appearance is not pixel identity.'
 },
 'attachment_visibility_limits':{'Chest_hidden_frames':[3,4],'FarShoulder_hidden_frames':[3],'NearShoulder_hidden_frames':[],'hidden_bones_all':None,'future_generated_component_A_all':None,'hidden_mounts_require_separate_explicit_design_choice':True},
 'timing':{'kernel':[75,75,60,60,135,135],'kernel_total':540,'standard_preview':[100]*6,'standard_preview_total':600,'retimed':False,'timing_QA_passed':False},
 'acceptance_limits':['No new crop/media generated or viewed; all six actual original512s were retained E209 before review.','No UE/UBT/generation/import/Source/tools/ledger modifications.','Not a complete hand/sleeve/helmet pixel ownership partition; no reconstruction claim.','No hidden bones, actual elbow angle, actual blade axis or actual handle centre asserted.','No continuous animation/video playback,72px running readability,sword/armour fit,hit alignment,P1 transition,foot lock or sound acceptance.'],
 'accepted':False,'formal_complete_units':0,
}
for name in ['measurement-v003.json']:
    p=HERE/name
    if p.exists(): raise RuntimeError('No overwrite: '+str(p))
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for i in range(6): assert fact(SOURCE/f'frame-{i}.png')==verification['frames'][i]['source']
print(json.dumps({'measurement':fact(HERE/'measurement-v003.json'),'palms':PALMS,'nullable_design_A':[{'frame':i,'A':v} for i,v in enumerate(DESIGN_A)],'near_span':max(near)-min(near),'far_span':max(far)-min(far),'changed_pixel_counts':[x['same_phase_170_to_171_changed_rgba_pixel_count'] for x in frames]},ensure_ascii=False))