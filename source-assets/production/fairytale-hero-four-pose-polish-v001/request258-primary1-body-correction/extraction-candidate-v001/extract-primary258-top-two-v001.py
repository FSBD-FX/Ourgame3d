"""Deterministic candidate-only two-cell alpha extraction. No View/UE/generation.

RGB is never decontaminated or repainted. No resize. One shared (0,0) integer
translation aligns the observed bottom alpha row to the old source footline.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import sys

import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
REQUEST = OUT.parent
PROD = REQUEST.parents[1]
RAW = REQUEST / 'raw/primary1-bridge-correction.png'
EXPECTED = '959b58c9a3150505e68e3a2a0235822de8f7a698f5a3929c735aa9bc7fd7b449'
OLD_ROOT = PROD / 'fairytale-sword-v001'
OLD = {'old_J0': OLD_ROOT/'run-primary1-v003/curated/frame-0.png',
       'old_J1': OLD_ROOT/'run-primary1-v003/curated/frame-1.png',
       'Ready0': OLD_ROOT/'run-ready-v002/curated/frame-0.png'}
MARKERS = [OLD_ROOT/'primary1-measurement-v003/primary1-marker-proposal-v003.json',
           OLD_ROOT/'ready-measurement-v002/ready-marker-proposal-v002.json']
SHIFT = (0, 0)
SCALE = 72/416


def pin(p):
    b = p.read_bytes()
    return {'path':p.as_posix(), 'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest()}


def write(rel, value):
    p = OUT/rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return p


def save(rel, im):
    p = OUT/rel
    p.parent.mkdir(parents=True, exist_ok=True)
    assert not p.exists(), p
    im.save(p)
    return p


def bbox(mask):
    y,x = np.where(mask)
    return None if len(x)==0 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]


def metrics(a):
    alpha=a[:,:,3]
    box=bbox(alpha>0)
    core=bbox(alpha>=128)
    y0=core[3]-20
    yy,xx=np.where((alpha>=128)&(np.arange(512)[:,None]>=y0))
    foot=[int(xx.min()),int(xx.max()+1)]
    c=a[:,:,:3][alpha==255]
    z=a[:,:,:3].astype(np.int16); yy,xx=np.indices((512,512))
    helmet=(alpha>=128)&(xx>=170)&(xx<375)&(yy<box[1]+190)&(z[:,:,1]>=110)&(z[:,:,2]>=75)&((z[:,:,0]-z[:,:,1])>=8)&((z[:,:,1]-z[:,:,2])>=10)
    hb=bbox(helmet)
    return {'canvas':[512,512], 'helmet_tan_color_core_proxy_bbox':hb, 'helmet_tan_color_core_proxy_width_height':[hb[2]-hb[0],hb[3]-hb[1]],
      'helmet_proxy_rule':'alpha>=128; x[170,375); y<subject_top+190; G>=110; B>=75; R-G>=8; G-B>=10. Color-core diagnostic, not complete outer helmet mask or approved socket.',
      'canvas':[512,512], 'alpha_bbox_exclusive':box,
      'alpha_bbox_size':[box[2]-box[0],box[3]-box[1]], 'alpha128_bbox_exclusive':core,
      'alpha_nonzero':int(np.count_nonzero(alpha)), 'alpha128':int(np.count_nonzero(alpha>=128)),
      'alpha255':int(np.count_nonzero(alpha==255)),
      'alpha_partial':int(np.count_nonzero((alpha>0)&(alpha<255))),
      'foot_bottom_last_nonzero_y':box[3]-1, 'foot_bottom_last_alpha128_y':core[3]-1,
      'lowest20rows_alpha128_x_range':foot, 'lowest20rows_alpha128_x_midpoint':sum(foot)/2,
      'lowest20rows_semantics':'Silhouette-only projected boot footprint proxy; not anatomical foot sockets.',
      'opaque_RGB_mean':np.mean(c,axis=0).tolist(), 'opaque_RGB_median':np.median(c,axis=0).tolist(),
      'display_scale_assumed':SCALE,'display_bbox_size_at_72_rule':[(box[2]-box[0])*SCALE,(box[3]-box[1])*SCALE]}


assert set(p.name for p in OUT.iterdir()) == {Path(__file__).name}, 'Fresh exclusive output required.'
assert pin(RAW)['sha256']==EXPECTED and RAW.stat().st_size==1526081
im=Image.open(RAW)
assert im.mode=='RGB' and im.size==(1536,1024)
raw=np.array(im)
old_metrics={name:metrics(np.array(Image.open(p).convert('RGBA'))) for name,p in OLD.items()}
frames=[]
for frame in (0,1):
    cropbox=[frame*512,0,(frame+1)*512,512]
    rgb=raw[0:512,frame*512:(frame+1)*512].copy()
    cropfile=save(f'original-cells/frame-{frame}-RGB-crop.png',Image.fromarray(rgb))
    assert np.array_equal(np.array(Image.open(cropfile)),rgb)
    z=rgb.astype(np.int16)
    dominance=np.minimum(z[:,:,0],z[:,:,2])-z[:,:,1]
    background=dominance>=220
    soft=(dominance>=48)&(dominance<220)&(np.minimum(z[:,:,0],z[:,:,2])>=96)
    alpha=np.full((512,512),255,np.uint8)
    alpha[background]=0
    alpha[soft]=np.clip(255-dominance[soft],1,254).astype(np.uint8)
    before=np.dstack((rgb,alpha))
    border=np.concatenate([alpha[:20].ravel(),alpha[-20:].ravel(),alpha[:,:20].ravel(),alpha[:,-20:].ravel()])
    assert not np.any(border), 'Unremoved 20px outer background.'
    assert np.array_equal(before[:,:,:3],rgb), 'RGB must remain exact.'
    # Both measured raw footlines already equal old y463. Shared translation is zero.
    assert metrics(before)['foot_bottom_last_nonzero_y']==463
    aligned=before.copy()
    assert np.array_equal(aligned,before)
    assert np.count_nonzero(aligned[:,:,3])==np.count_nonzero(alpha)
    png=save(f'transparent-cells/frame-{frame}-RGBA-footline464-candidate.png',Image.fromarray(aligned))
    assert np.array_equal(np.array(Image.open(png)),aligned)
    rawmetrics=metrics(before); alignedmetrics=metrics(aligned)
    compare={}
    for label,old in old_metrics.items():
        b=alignedmetrics['alpha_bbox_size'];o=old['alpha_bbox_size']
        compare[label]={'width_ratio':b[0]/o[0],'height_ratio':b[1]/o[1],
          'helmet_tan_proxy_width_ratio':alignedmetrics['helmet_tan_color_core_proxy_width_height'][0]/old['helmet_tan_color_core_proxy_width_height'][0],
          'helmet_tan_proxy_height_ratio':alignedmetrics['helmet_tan_color_core_proxy_width_height'][1]/old['helmet_tan_color_core_proxy_width_height'][1],
          'footspan_width_ratio':(alignedmetrics['lowest20rows_alpha128_x_range'][1]-alignedmetrics['lowest20rows_alpha128_x_range'][0])/(old['lowest20rows_alpha128_x_range'][1]-old['lowest20rows_alpha128_x_range'][0]),
          'bbox_top_delta_source_px':alignedmetrics['alpha_bbox_exclusive'][1]-old['alpha_bbox_exclusive'][1],
          'bottom_delta_before_alignment_source_px':rawmetrics['foot_bottom_last_nonzero_y']-old['foot_bottom_last_nonzero_y'],
          'bottom_delta_after_alignment_source_px':alignedmetrics['foot_bottom_last_nonzero_y']-old['foot_bottom_last_nonzero_y'],
          'footprint_midpoint_delta_after_source_px':alignedmetrics['lowest20rows_alpha128_x_midpoint']-old['lowest20rows_alpha128_x_midpoint']}
    grip_raw=[211,343] if frame==0 else [159,213]
    axis=[.94,-.341] if frame==0 else [-.2,-.98]
    markers={'status':'PROVISIONAL_NOT_APPROVED_NOT_ANATOMICAL',
      'display_root_aligned':[256,464], 'physical_foot_root':None,
      'display_root_semantics':'Inherited display pivot; not a measured pelvis/foot contact root.',
      'visible_closed_hand_grip_center_raw_cell_proposal':grip_raw,
      'visible_closed_hand_grip_center_aligned_proposal':[grip_raw[0],grip_raw[1]],
      'grip_uncertainty_source_px_each_axis':12,
      'grip_semantics':'Coarse visible fist-center proposal from E636-retained RGB sheet, not measured socket; Root must confirm weapon-hand ownership and grip.',
      'weapon_axis_artist_starting_proposal':axis,
      'weapon_axis_measured':False,'weapon_axis_angle_uncertainty_degrees':25,
      'weapon_axis_semantics':'Inherited prior action artist direction only; no blade/handle exists in this body-only source.',
      'root_grip_axis_approved':False, 'hand_polygon':None,'owner_partition':None}
    frames.append({'frame':frame,'source_crop_box_exclusive':cropbox,'source_RGB_crop':pin(cropfile),
      'source_crop_RGB_sha256':hashlib.sha256(rgb.tobytes()).hexdigest(),
      'transparent_candidate':pin(png),'aligned_RGBA_sha256':hashlib.sha256(aligned.tobytes()).hexdigest(),
      'matting':{'background_zero_alpha_pixels':int(background.sum()),'partial_key_edge_pixels':int(soft.sum()),
        'RGB_pixels_modified_before_alignment':0,'nontransparent_RGB_pixels_modified_after_alignment':0,
        'RGB_decontamination_or_despill':False,'alpha_border20_all_zero':True,
        'key_dominance_range_border20':[int(np.concatenate([dominance[:20].ravel(),dominance[-20:].ravel(),dominance[:,:20].ravel(),dominance[:,-20:].ravel()]).min()),int(np.concatenate([dominance[:20].ravel(),dominance[-20:].ravel(),dominance[:,:20].ravel(),dominance[:,-20:].ravel()]).max())],
        'remaining_magenta_dominance_ge48_with_alpha128':int(np.count_nonzero((dominance>=48)&(alpha>=128)))},
      'raw_cell_metrics':rawmetrics,'aligned_metrics':alignedmetrics,'comparison_to_old':compare,
      'provisional_markers':markers})

dependencies=[pin(RAW),pin(REQUEST/'submitted-prompt.txt'),pin(REQUEST/'generation258-result-v001.json')]
dependencies += [pin(p) for p in OLD.values()] + [pin(p) for p in MARKERS]
dependencies += [pin(Path('F:/Ourgame/source-assets/production/fairytale-hero-four-pose-polish-v001/request257-primary1-body/extraction-candidate-v001/extract-primary257-top-two-v001.py')),pin(Path('F:/Ourgame/过程图稿与视频/2026-10-19_钟盔攻击修片尺寸锚点_v002/展示副本/primary1-original-six-curated-512-guide-v002.png'))]
closure={'schema':'request258-two-body-cell-source-closure-v001','utc':dt.datetime.now(dt.timezone.utc).isoformat(),
 'generation_request':258,'source_image':pin(RAW),'generator_called_by_this_script':False,
 'grid':{'canvas':[1536,1024],'cell':[512,512],'rows':2,'columns':3,'extracted_cells':[0,1]},
 'matte_algorithm':{'name':'RGB-preserving magenta dominance alpha v001','dominance':'min(R,B)-G',
  'background':'dominance>=220 => alpha0','soft_edge':'48<=dominance<220 and min(R,B)>=96 => alpha=255-dominance',
  'other_pixels':'alpha255','RGB':'Unchanged; no unmix, fill, repaint or color retouch.',
  'limitation':'Semi-transparent edge RGB can retain original magenta mixture. No visual halo acceptance is claimed.'},
 'shared_alignment':{'integer_translation_xy':list(SHIFT),'resample':False,'resize':False,
  'reason':'Both selected raw cells have last nonzero alpha y463, matching old J0/J1/Ready0. Measured shared dy=0; no +1/+2 assumption.',
  'foreground_clipped':False,'per_pose_horizontal_registration':False},
 'old_reference_metrics':old_metrics,'frames':frames,'dependency_pins':dependencies,
 'only_two_new_body_cells':True,'other_generated_cells_not_extracted':True,
 'old_runtime_frames_2_to_5':'Unchanged and not copied or admitted by this candidate.',
 'partition_or_armor_created':False,'native_run_performed':False,'derived_images_viewed':False,
 'E_retention_of_new_derivatives':'PENDING_ROOT','source_pixels_accepted':False,'art_accepted':False,'FinalAccepted':False}
write('source-closure-v001.json',closure)

rows=[]
for f in frames:
    c=f['comparison_to_old']['old_J'+str(f['frame'])]
    n=f['aligned_metrics']
    rows.append(f"| J{f['frame']} | {n['alpha_bbox_exclusive']} | {c['width_ratio']:.4f}/{c['height_ratio']:.4f} | {n['helmet_tan_color_core_proxy_width_height']} | {c['helmet_tan_proxy_width_ratio']:.4f}/{c['helmet_tan_proxy_height_ratio']:.4f} | {n['lowest20rows_alpha128_x_range']} | {c['footspan_width_ratio']:.4f} | {c['footprint_midpoint_delta_after_source_px']:+.1f}px |")
report = """# request258 J0/J1 修正素材确定性提取候选 v001

两张透明512格已保存，沿用257完全相同的洋红alpha算法，无RGB修改、去色、缩放、重绘、独立居中。原始两格RGB裁图亦保留。仅在Root确认F/E636留存后查看raw258；尺寸锚点guide已E634留存。新派生图未View，待Root留存/审阅。

实际测得两格alpha最后非零行均为463，与旧J0/J1/Ready0相同，因此唯一共享整数位移是(0,0)，不是预设+1/+2。所有像素坐标和RGB均保持原样。背景不是完全恒定#FF00FF，alpha阈值、边缘计数、色彩统计及像素hash见source-closure-v001.json。

| 帧 | 身体alpha bbox | 身体宽/高比旧同帧 | 盔褐色芯宽/高 | 褐色芯宽/高比旧 | 脚底20行轮廓x范围 | 脚跨度比旧 | 脚跨度中点偏移 |
|---|---|---|---|---|---|---:|---:|
""" + '\n'.join(rows) + """

头盔数值是固定阈值下的暖褐色芯代理，排除了黑轮廓/面罩和部分阴影，不是完整盔壳外沿测量。代理规则在JSON逐项记录；其尺寸近似相同不代表盔壳旋转、形状或体积已接受。身体bbox也不是骨骼尺度：J0更低、J1部分起身是姿势变化。

新J0/J1顶端分别y100/y85，旧保留J2的原身体顶端约y50；未用缩放制造这个高度顺序。是否与旧J2连续仍待Root看实际并审阅。旧J0/J1/Ready0整体bbox为[146,48,366,464]/[139,49,372,464]/[149,49,362,464]。与257相比主要宽距漂移已有数值收敛，但不得把这一点当美术或原生验收。

握点是可见拳心的粗略未批准提案：J0(211,343)、J1(159,213)，各轴±12源像素；显示Root沿用(256,464)，物理脚根为空；剑轴暂沿旧艺术方向(.94,-.341)/(-.2,-.98)，±25度且未实测。原图没有刀柄，Root需确认持剑手和精确手部遮挡/轴线。owner分割与护甲暂不制作。

透明算法没有RGB去洋红混色，半透明边缘保留原混色RGB，可能有边缘色污染；未查看派生图，不能声称无晕边。只提取上排前两格，原运行2–5未改、未复制成新验收素材。来源闭包与freeze包含257提取器和E634尺寸锚点的pin。FinalAccepted=false。
"""
write('extraction-report-v001.md',report)
members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
freeze={'schema':'request258-two-cell-extraction-freeze-v001','members':members,'source_dependencies':dependencies,
        'scope':'Only two transparent candidates and two original RGB crop witnesses plus deterministic script, metrics and report.',
        'derived_images_viewed':False,'E_retention':'PENDING_ROOT','native_or_art_acceptance':False,'FinalAccepted':False}
write('extraction-freeze-v001.json',freeze)
assert pin(RAW)['sha256']==EXPECTED
print(json.dumps({'source_unchanged':True,'only_frames':[0,1],'output':OUT.as_posix(),
 'metrics':[{'frame':f['frame'],'bbox':f['aligned_metrics']['alpha_bbox_exclusive'],
 'partial_alpha':f['aligned_metrics']['alpha_partial'],'comparison_same_old':f['comparison_to_old']['old_J'+str(f['frame'])]} for f in frames],
 'closure':pin(OUT/'source-closure-v001.json'),'freeze':pin(OUT/'extraction-freeze-v001.json')},ensure_ascii=False))
