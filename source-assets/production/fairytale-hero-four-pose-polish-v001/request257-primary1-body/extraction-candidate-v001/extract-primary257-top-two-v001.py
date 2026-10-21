"""Deterministic candidate-only two-cell alpha extraction. No View/UE/generation.

RGB is never decontaminated or repainted. No resize. One shared (0,-19) integer
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
RAW = REQUEST / 'raw/primary1-bridge-body.png'
EXPECTED = '61cc190baf284d696971f152f373c8882708849982b7ecaed00b841ccef40d22'
OLD_ROOT = PROD / 'fairytale-sword-v001'
OLD = {'old_J0': OLD_ROOT/'run-primary1-v003/curated/frame-0.png',
       'old_J1': OLD_ROOT/'run-primary1-v003/curated/frame-1.png',
       'Ready0': OLD_ROOT/'run-ready-v002/curated/frame-0.png'}
MARKERS = [OLD_ROOT/'primary1-measurement-v003/primary1-marker-proposal-v003.json',
           OLD_ROOT/'ready-measurement-v002/ready-marker-proposal-v002.json']
SHIFT = (0, -19)
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
    return {'canvas':[512,512], 'alpha_bbox_exclusive':box,
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
assert pin(RAW)['sha256']==EXPECTED and RAW.stat().st_size==1580964
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
    # No foreground is cropped away by the shared integer footline alignment.
    assert not np.any(alpha[:19])
    aligned=np.zeros_like(before)
    aligned[:493]=before[19:]
    assert np.array_equal(aligned[:493],before[19:])
    assert np.count_nonzero(aligned[:,:,3])==np.count_nonzero(alpha)
    png=save(f'transparent-cells/frame-{frame}-RGBA-footline464-candidate.png',Image.fromarray(aligned))
    assert np.array_equal(np.array(Image.open(png)),aligned)
    rawmetrics=metrics(before); alignedmetrics=metrics(aligned)
    compare={}
    for label,old in old_metrics.items():
        b=alignedmetrics['alpha_bbox_size'];o=old['alpha_bbox_size']
        compare[label]={'width_ratio':b[0]/o[0],'height_ratio':b[1]/o[1],
          'bbox_top_delta_source_px':alignedmetrics['alpha_bbox_exclusive'][1]-old['alpha_bbox_exclusive'][1],
          'bottom_delta_before_alignment_source_px':rawmetrics['foot_bottom_last_nonzero_y']-old['foot_bottom_last_nonzero_y'],
          'bottom_delta_after_alignment_source_px':alignedmetrics['foot_bottom_last_nonzero_y']-old['foot_bottom_last_nonzero_y'],
          'footprint_midpoint_delta_after_source_px':alignedmetrics['lowest20rows_alpha128_x_midpoint']-old['lowest20rows_alpha128_x_midpoint']}
    grip_raw=[217,350] if frame==0 else [129,190]
    axis=[.94,-.341] if frame==0 else [-.2,-.98]
    markers={'status':'PROVISIONAL_NOT_APPROVED_NOT_ANATOMICAL',
      'display_root_aligned':[256,464], 'physical_foot_root':None,
      'display_root_semantics':'Inherited display pivot; not a measured pelvis/foot contact root.',
      'visible_closed_hand_grip_center_raw_cell_proposal':grip_raw,
      'visible_closed_hand_grip_center_aligned_proposal':[grip_raw[0],grip_raw[1]-19],
      'grip_uncertainty_source_px_each_axis':12,
      'grip_semantics':'Coarse visible fist-center proposal from E628-retained RGB sheet, not measured socket; Root must confirm weapon-hand ownership and grip.',
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

dependencies=[pin(RAW),pin(REQUEST/'submitted-prompt.txt'),pin(REQUEST/'generation257-result-v001.json')]
dependencies += [pin(p) for p in OLD.values()] + [pin(p) for p in MARKERS]
closure={'schema':'request257-two-body-cell-source-closure-v001','utc':dt.datetime.now(dt.timezone.utc).isoformat(),
 'generation_request':257,'source_image':pin(RAW),'generator_called_by_this_script':False,
 'grid':{'canvas':[1536,1024],'cell':[512,512],'rows':2,'columns':3,'extracted_cells':[0,1]},
 'matte_algorithm':{'name':'RGB-preserving magenta dominance alpha v001','dominance':'min(R,B)-G',
  'background':'dominance>=220 => alpha0','soft_edge':'48<=dominance<220 and min(R,B)>=96 => alpha=255-dominance',
  'other_pixels':'alpha255','RGB':'Unchanged; no unmix, fill, repaint or color retouch.',
  'limitation':'Semi-transparent edge RGB can retain original magenta mixture. No visual halo acceptance is claimed.'},
 'shared_alignment':{'integer_translation_xy':list(SHIFT),'resample':False,'resize':False,
  'reason':'Both selected cells have last nonzero alpha y482; shared dy-19 yields old source y463.',
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
    rows.append(f"| J{f['frame']} | {f['raw_cell_metrics']['alpha_bbox_exclusive']} | {f['aligned_metrics']['alpha_bbox_exclusive']} | {c['width_ratio']:.4f} | {c['height_ratio']:.4f} | {c['footprint_midpoint_delta_after_source_px']:+.1f}px |")
report='''# request257 J0/J1 确定性提取候选 v001

状态：两张透明身体候选已保存；未查看派生图片、未分层、未配甲、未导入或运行。源图 request257 在 Root 确认 F/E628 留存后才被查看。新派生图仍待 Root F/E 留存，不能视为美术/原生验收。

事实：原图为 1536×1024 RGB，按不可见 2×3 网格精确裁取左上与上中两个 512 格。背景并非全为精确 #FF00FF；两格 20px 外边框的 min(R,B)-G 均大于220。按记录阈值只改变 alpha，RGB 原样保留。没有缩放、重绘、补洞、颜色修正或再生成。保留两张原始 RGB 裁格以供逐像素追溯。

两格非零 alpha 原脚线最后一行都是482，旧 J0/J1/Ready0 为463。因此仅作同一整数位移 (0,-19)，没有独立横向居中；所有非透明像素及其 RGB/alpha 在位移后逐字节保留，未裁去前景。

| 帧 | 原格 alpha bbox | 对齐后 bbox | 宽/旧同帧 | 高/旧同帧 | 脚底20行轮廓中点/旧同帧 |
|---|---|---|---:|---:|---:|
'''+ '\n'.join(rows)+'''

这些是轮廓包围盒比例，不是头盔或骨骼缩放测量。新 J0 的站姿压缩与新 J1 的较高起势已经体现在数值里；新生成身体较宽，不得自动逐格缩小来掩盖体积差异。统一 dy 只解决源脚线，左右脚地面分布和身体横向漂移仍需 Root 看图决定。72/416 显示比例下，19源像素约3.29显示像素。

透明边缘采用原 RGB，不做去洋红混色，因此存在边缘色污染的可能；JSON记录了半透明边缘与剩余洋红优势像素数。未看派生图，不能声称无毛边、无晕边或轮廓已认可。所有像素/裁格/RGBA SHA、alpha bbox/计数、脚底轮廓中点、opaque色彩统计均见 source-closure-v001.json。

Root/Grip/Axis 仅是显式带不确定性的提案：显示 Root 沿用(256,464)，物理脚根为空；J0原格拳心暂取(217,350)、J1暂取(129,190)，对齐后分别(217,331)/(129,171)，各轴±12源像素。方向暂沿旧设计(.94,-.341)/(-.2,-.98)，不是测得的刀轴，角度不确定性±25°。身体源没有刀柄，手部遮挡多边形和 owner 分割均为空，等待 Root 可见测量；不可把这些写作已批准 socket。

当前旧身体比较来源是 run-primary1-v003/curated/frame-{0,1}.png 和 run-ready-v002/curated/frame-0.png；只读核对确认它们与当前导入身体 owner 重组 RGBA 完全一致。旧 Root 是显示枢轴而非物理脚关节，旧 Grip±4px，Axis也是艺术方向提案。

下一步限于：Root 先留存并查看这两格，确认背景边缘、头盔/肩体积、脚分布、J1与保留旧J2的衔接，再测手/握点和必要的身体分割。现有运行2–5帧未修改、未复制为新验收素材。本候选不包含 owner、护甲或实际导入清单。FinalAccepted=false。
'''
write('extraction-report-v001.md',report)
members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
freeze={'schema':'request257-two-cell-extraction-freeze-v001','members':members,'source_dependencies':dependencies,
        'scope':'Only two transparent candidates and two original RGB crop witnesses plus deterministic script, metrics and report.',
        'derived_images_viewed':False,'E_retention':'PENDING_ROOT','native_or_art_acceptance':False,'FinalAccepted':False}
write('extraction-freeze-v001.json',freeze)
assert pin(RAW)['sha256']==EXPECTED
print(json.dumps({'source_unchanged':True,'only_frames':[0,1],'output':OUT.as_posix(),
 'metrics':[{'frame':f['frame'],'bbox':f['aligned_metrics']['alpha_bbox_exclusive'],
 'partial_alpha':f['aligned_metrics']['alpha_partial'],'comparison_same_old':f['comparison_to_old']['old_J'+str(f['frame'])]} for f in frames],
 'closure':pin(OUT/'source-closure-v001.json'),'freeze':pin(OUT/'extraction-freeze-v001.json')},ensure_ascii=False))
