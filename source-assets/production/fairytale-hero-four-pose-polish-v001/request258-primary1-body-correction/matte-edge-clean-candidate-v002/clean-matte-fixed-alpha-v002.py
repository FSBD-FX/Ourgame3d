"""Bounded fixed-alpha chroma RGB decontamination; candidate only, no View.
Only semitransparent magenta-tinted pixels within four Chebyshev source pixels
of alpha0 are eligible. Original alpha, opaque RGB and all coordinates stay.
"""
from pathlib import Path
import ast
import datetime as dt
import hashlib
import json
import math
import sys
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
REQ=OUT.parent
PROD=REQ.parents[1]
EX=REQ/'extraction-candidate-v001'
PART=REQ/'body-partition-fit-candidate-v001'
SKILL=Path('C:/Users/22499/.codex/skills/sprite-gen')
EXTRACTOR=SKILL/'sprite_gen/frames/extract.py'
SKILL_DOC=Path('C:/Users/22499/.codex/skills/generate2dsprite/SKILL.md')
SWORD=PROD/'first-unit-animation-v002/components/military-sword-clean-v001.png'
NAMES=['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']
ORDER=['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','HelmetForeground','IndependentSword','NearHand']
SCALE=72/416
KEY=(255,0,255)
sys.path.insert(0,str(SKILL))
from sprite_gen.frames.extract import despill_color, _grow_chebyshev

def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,a):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p)
 assert np.array_equal(np.array(Image.open(p)),a);return p
def rgba(p):
 im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);return np.array(im)
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

assert set(p.name for p in OUT.iterdir())=={Path(__file__).name},'Fresh candidate output only.'
assert pin(EXTRACTOR)['sha256']=='f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539'
assert pin(PART/'body-partition-fit-freeze-v001.json')['sha256']=='aee3ae97b08fe0f7cc1382531176a8f3d00b8ea7e50dc93d606ab0242dc45c0b'
# Reuse only pure QC functions from frozen prior builder, never its top-level IO.
tree=ast.parse((PART/'build-two-body-owner-fit-v001.py').read_text(encoding='utf-8'))
helpers=ast.Module(body=[v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name in ['premultiplied','sword_layer','compose','display']],type_ignores=[])
assert len(helpers.body)==4
exec(compile(helpers,'frozen-partition-QC-pure-functions','exec'),globals())

oldmap=read(PART/'six-frame-candidate-map-v001.json');oldproof=read(PART/'body-owner-fit-proof-v001.json')
dependencies=[pin(EXTRACTOR),pin(SKILL_DOC),pin(PART/'build-two-body-owner-fit-v001.py'),pin(PART/'body-partition-fit-freeze-v001.json'),pin(PART/'six-frame-candidate-map-v001.json'),pin(PART/'body-owner-fit-proof-v001.json'),pin(EX/'source-closure-v001.json'),pin(SWORD)]
records=[];before_wholes=[];after_wholes=[];before_fits=[];after_fits=[];newmap=oldmap.copy();newmap['frames']=[v.copy() for v in oldmap['frames']]
for i in [0,1]:
 src=Path(oldproof['frames'][i]['source']['path']);assert pin(src)==oldproof['frames'][i]['source'];dependencies.append(pin(src));a=rgba(src)
 alpha=a[:,:,3];z=a[:,:,:3].astype(np.int16);dominance=np.minimum(z[:,:,0],z[:,:,2])-z[:,:,1]
 depth=np.full((512,512),255,np.uint8);reached=alpha==0;depth[reached]=0
 for k in range(1,5):
  grown=_grow_chebyshev(reached);depth[grown&~reached]=k;reached=grown
 selected=(alpha>0)&(alpha<255)&(dominance>=48)&(depth>=1)&(depth<=4)
 cleaned=a.copy();unclamped_low=0;unclamped_high=0
 for y,x in zip(*np.nonzero(selected)):
  av=int(alpha[y,x]);coverage,RGB=despill_color(tuple(int(v) for v in a[y,x,:3]),KEY,255.,255.-av)
  assert abs(coverage-av/255.)<1e-12
  unbounded=(a[y,x,:3].astype(float)-(1-av/255.)*np.array(KEY))/(av/255.)
  unclamped_low+=int(np.count_nonzero(unbounded<0));unclamped_high+=int(np.count_nonzero(unbounded>255))
  cleaned[y,x,:3]=RGB
 changed=np.any(cleaned[:,:,:3]!=a[:,:,:3],axis=2)
 assert np.all(~changed|selected)
 assert np.array_equal(cleaned[:,:,3],alpha)
 assert np.array_equal(cleaned[:,:,:3][alpha==255],a[:,:,:3][alpha==255])
 assert np.array_equal(cleaned[:,:,:3][alpha==0],a[:,:,:3][alpha==0])
 assert bbox(cleaned[:,:,3]>0)==bbox(alpha>0)
 cleanfile=save(f'cleaned-body/frame-{i}-RGBA-fixed-alpha-candidate.png',cleaned)
 maskfile=save(f'change-masks/frame-{i}-RGB-changed-only.png',(changed*255).astype(np.uint8))
 source_masks=[];owners=[];layers={};layerpins={}
 for name in NAMES:
  mp=PART/'owner-masks'/name/f'frame-{i}.png';dependencies.append(pin(mp));m=np.array(Image.open(mp))==255;owners.append(m);source_masks.append({'owner':name,'source_mask':pin(mp)})
  v=np.zeros_like(cleaned);v[m]=cleaned[m];layers[name]=v;layerpins[name]=pin(save(f'body-layers/{name}/frame-{i}.png',v))
 assert np.array_equal(sum(m.astype(np.uint8) for m in owners),np.ones((512,512),np.uint8))
 recovered=np.sum(np.stack(list(layers.values())),axis=0,dtype=np.uint16).astype(np.uint8);assert np.array_equal(recovered,cleaned)
 im=Image.new('RGBA',(512,512))
 for name in NAMES:im=Image.alpha_composite(im,Image.fromarray(layers[name]))
 assert np.array_equal(premultiplied(np.array(im)),premultiplied(cleaned))
 for armor in oldproof['frames'][i]['armor_trials']:
  name=armor['component'];p=Path(armor['candidate']['path']);assert pin(p)==armor['candidate'];dependencies.append(pin(p));layers[name]=rgba(p);layerpins[name]=pin(p)
 marker=oldmap['frames'][i];grip=marker['Grip'];axis=marker['Axis'];layers['IndependentSword'],sw=sword_layer(grip,axis)
 oldlayers={}
 for name in NAMES:
  p=PART/'body-layers'/name/f'frame-{i}.png';dependencies.append(pin(p));oldlayers[name]=rgba(p)
 for name in ['Chest','NearShoulder','FarShoulder','IndependentSword']:oldlayers[name]=layers[name]
 before_fit=compose(oldlayers,True,True);after_fit=compose(layers,True,True)
 save(f'qc/after-LGT-independent-sword-{i}-512.png',after_fit)
 save(f'qc/before-after-LGT-independent-sword-{i}-512.png',np.concatenate([before_fit,after_fit],axis=1))
 before_wholes.append(a);after_wholes.append(cleaned);before_fits.append(before_fit);after_fits.append(after_fit)
 delta=cleaned[:,:,:3].astype(np.int16)-z
 before_min=(np.minimum(z[:,:,0],z[:,:,2])-z[:,:,1])[changed]
 zz=cleaned[:,:,:3].astype(np.int16);after_min=(np.minimum(zz[:,:,0],zz[:,:,2])-zz[:,:,1])[changed]
 rec={'frame':i,'input':pin(src),'cleaned':pin(cleanfile),'changed_pixel_mask':pin(maskfile),'changed_pixels':int(changed.sum()),'selected_pixels':int(selected.sum()),'all_partial_pixels':int(np.count_nonzero((alpha>0)&(alpha<255))),
  'untouched_partial_deeper_than4':int(np.count_nonzero((alpha>0)&(alpha<255)&(depth>4))),
  'changed_alpha_minmax':[int(alpha[changed].min()),int(alpha[changed].max())],
  'changed_distance_to_alpha0_histogram':{str(k):int(np.count_nonzero(changed&(depth==k))) for k in [1,2,3,4]},
  'changed_RGB_delta_min':np.min(delta[changed],axis=0).tolist(),'changed_RGB_delta_max':np.max(delta[changed],axis=0).tolist(),
  'changed_RGB_mean_abs_delta':np.mean(np.abs(delta[changed]),axis=0).tolist(),
  'before_changed_minRB_minusG_minmax':[int(before_min.min()),int(before_min.max())],
  'after_changed_minRB_minusG_minmax':[int(after_min.min()),int(after_min.max())],
  'unclamped_inverse_RGB_channels_below0':unclamped_low,'unclamped_inverse_RGB_channels_above255':unclamped_high,
  'source_keyed_background_RGB_median':np.median(a[:,:,:3][alpha==0],axis=0).tolist(),
  'alpha_all_bytes_equal':True,'alpha_minmax':[int(alpha.min()),int(alpha.max())],'alpha_bbox_before_after':bbox(alpha>0),'opaque_RGB_all_bytes_equal':True,'alpha0_RGB_all_bytes_equal':True,'source_positions_changed':False,
  'cleaned_RGBA_sha256':hashlib.sha256(cleaned.tobytes()).hexdigest(),'recovered_RGBA_sha256':hashlib.sha256(recovered.tobytes()).hexdigest(),'reconstruction_target':'CLEANED_RGBA, not original generated RGB','all_owner_coordinates_unique_and_exhaustive':True,'owner_reconstruction_exact':True,'premultiplied_composite_exact':True,'unchanged_owner_masks':source_masks,'cleaned_body_layers':layerpins,'unchanged_sword_QC_transform':sw,'semantic_accepted':False}
 records.append(rec)
 newmap['frames'][i]['body_source']=pin(cleanfile);newmap['frames'][i]['component_sources']=layerpins
 newmap['frames'][i]['source_RGB_status']='Only declared semitransparent magenta edge colors decontaminated; NOT original-generation RGB byte-equal.'
 assert newmap['frames'][i]['Root']==oldmap['frames'][i]['Root'] and newmap['frames'][i]['Grip']==oldmap['frames'][i]['Grip'] and newmap['frames'][i]['Axis']==oldmap['frames'][i]['Axis']

columns=[('J0_before',before_wholes[0]),('J0_after',after_wholes[0]),('J1_before',before_wholes[1]),('J1_after',after_wholes[1])]
fits=[('J0_before',before_fits[0]),('J0_after',after_fits[0]),('J1_before',before_fits[1]),('J1_after',after_fits[1])]
boards=[]
for title,data in [('body',columns),('LGT-independent-sword',fits)]:
 board=np.zeros((200,400,3),np.uint8)
 for row,bg in enumerate([(24,28,30),(220,216,202)]):
  for col,(_,a) in enumerate(data):board[row*100:(row+1)*100,col*100:(col+1)*100]=display(a,bg)
 boards.append({'kind':title,'file':pin(save(f'qc/{title}-before-after-72rule-dark-light.png',board)),'columns':[v[0] for v in data],'rows':['dark24,28,30','light220,216,202'],'cell':[100,100]})
write('comparison-map-v002.json',{'boards':boards,'scale':SCALE,'source_root':[256,464],'ground_display':[50,90],'sampling':'Same frozen before/after BICUBIC premultiplied RGBa QC transform','new_images_viewed':False})
write('six-frame-candidate-map-cleaned-v002.json',newmap)
dependencies=list({p['path']:p for p in dependencies}.values())
proof={'schema':'request258-fixed-alpha-edge-decontamination-v002','utc':dt.datetime.now(dt.timezone.utc).isoformat(),'algorithm':{'proven_function':'sprite_gen.frames.extract.despill_color','function_module':pin(EXTRACTOR),'nominal_key':list(KEY),'inverse_model':'C=aF+(1-a)B; F=clamp(round((C-(1-a)B)/a))','fixed_coverage':'Use frozen alpha/255; native function key_tint255 and tint255-alpha; discard returned coverage, preserve alpha byte-exact.','selection':'0<alpha<255 AND min(R,B)-G>=48 AND Chebyshev distance1..4 from alpha0.','no_interior_or_opaque_spill_pass':True,'actual_background_median':'Measured249,4,250, whereas inverse uses requested nominal255,0,255. Coverage/key assumptions may leave dark/colored fringes; Root comparison required.','not_full_native_remove_chroma_background':'That function also changes alpha and performs wider spill cleanup; deliberately not run.'},'frames':records,'dependency_pins':dependencies,'new_clean_body_count':2,'new_owner_layer_count':8,'reused_armor_layers':6,'independent_sword_unchanged':True,'Root_Grip_Axis_unchanged':True,'old_candidates_or_raw_modified':False,'new_derivatives_viewed':False,'E_retention':'PENDING_ROOT','native_accepted':False,'final_art_accepted':False,'FinalAccepted':False}
write('edge-clean-proof-v002.json',proof)
rows=[]
for r in records:rows.append(f"| J{r['frame']} | {r['changed_pixels']} / {r['all_partial_pixels']} | {r['changed_alpha_minmax']} | {r['changed_distance_to_alpha0_histogram']} | {r['changed_RGB_delta_min']}..{r['changed_RGB_delta_max']} | {r['after_changed_minRB_minusG_minmax']} |")
report='''# 258 半透明洋红边缘固定alpha去色候选 v002

只新增本目录；没有生成/API/UE，也未修改raw、旧候选、Source/Content/tools/E/media/ledger。generate2dsprite允许对生成图做确定性洋红清理；实际复用已固定SHA的sprite-gen `despill_color`，只使用其RGB反混色公式，没有运行会重新估alpha的完整背景提取器。

假设边缘观察色C由主体F和背景B按已冻结alpha a混合：C=aF+(1-a)B。仅对半透明、洋红优势≥48、距alpha0为1–4个Chebyshev源像素的边缘，使用F=(C-(1-a)B)/a并四舍五入/夹到8bit。B取原请求的(255,0,255)；所有alpha、bbox、位置、Root/Grip/Axis、不透明RGB及alpha0隐藏RGB逐字节不动。这是受限背景反混色，不是邻域补画、形状重建或新材质。

| 帧 | 改色像素/全部半透明 | 改色处alpha范围 | 距透明区分布 | RGB差值min..max | 改色后min(R,B)-G范围 |
|---|---|---|---|---|---|
'''+ '\n'.join(rows)+'''

J0有1个半透明像素距透明区超过4px，保留原样。记录中的RGB变更量可能较大，因为低alpha像素原本含大量背景；轮廓不因此变大/变小。不把改色后的RGBA宣称为生成原RGB完全一致。

实际透明背景RGB中位数为(249,4,250)，并非完全等于名义键色；alpha也是此前的近似提取结果。因此反解可能带来暗边或少量残余色差，不能从数值消除洋红就认定视觉通过。没有扩大到不透明内部去色，也没有涂改残余点。Root需在留存后看固定72/416暗/亮前后对照及512前后甲剑合成。

使用E638保留的同4owner二值mask重新分配：8层全坐标唯一，无重叠无缺口，RGBA重组及预乘合成严格等于CLEANED目标。原6张LGT整数平移层与军剑仅pin引用，未重新变形或改色；Root/Grip/Axis及旧2–5运行引用不变。source组件FarShoulder/NearShoulder对应运行ShoulderFar/ShoulderNear。

qc两张72规则对照的列均为J0前/J0后/J1前/J1后，暗/亮两行；每姿势另存512甲剑前后对比。所有新派生图片尚未View，待Root F/E留存。最终美术/原生验收均未进行。FinalAccepted=false。
'''
write('matte-edge-clean-report-v002.md',report)
members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
write('matte-edge-clean-freeze-v002.json',{'schema':'request258-matte-edge-clean-freeze-v002','members':members,'dependency_pins':dependencies,'new_derivatives_viewed':False,'E_retention':'PENDING_ROOT','FinalAccepted':False})
for p in dependencies:assert pin(Path(p['path']))==p
print(json.dumps({'frames':[{'frame':r['frame'],'changed_pixels':r['changed_pixels'],'partial_total':r['all_partial_pixels'],'RGB_delta_min':r['changed_RGB_delta_min'],'RGB_delta_max':r['changed_RGB_delta_max'],'alpha_preserved':r['alpha_all_bytes_equal'],'opaque_RGB_preserved':r['opaque_RGB_all_bytes_equal'],'cleaned_owner_reconstruction_exact':r['owner_reconstruction_exact']} for r in records],'new_images_viewed':False,'freeze':pin(OUT/'matte-edge-clean-freeze-v002.json'),'report':pin(OUT/'matte-edge-clean-report-v002.md')},ensure_ascii=False))
