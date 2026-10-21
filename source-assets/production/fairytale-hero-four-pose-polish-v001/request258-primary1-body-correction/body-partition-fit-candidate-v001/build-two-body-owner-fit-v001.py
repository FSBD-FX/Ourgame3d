"""Two-pose candidate only. Exact RGBA partition, integer old-armor fit, QC.
No generation/UE/View/Source/Content/tools/media/E mutation. No art painting.
"""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

OUT=Path(__file__).resolve().parent
REQ=OUT.parent
PROD=REQ.parents[1]
EXTRACT=REQ/'extraction-candidate-v001'
OLD=PROD/'fairytale-armor-sword-primary1-v001'
LGT=PROD/'fairytale-lgt-readability-v003/primary1-integer-assembly-v002'
SWORD=PROD/'first-unit-animation-v002/components/military-sword-clean-v001.png'
OLD_SCRIPT=OLD/'build-primary1-body-partition-v001.py'
MARKERS=PROD/'fairytale-sword-v001/primary1-measurement-v003/primary1-marker-proposal-v003.json'
MOUNTS=PROD/'fairytale-lgt-readability-v003/primary1-visible-mounts-v001/all18-mounts-v002.json'
NAMES=['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']
ORDER=['BodyRest','FarShoulder','Chest','NearArmWithoutHand','NearShoulder','HelmetForeground','IndependentSword','NearHand']
SCALE=72/416
DELTAS=[{'Chest':[-7,22],'NearShoulder':[-5,40],'FarShoulder':[8,35]},
        {'Chest':[-3,12],'NearShoulder':[-15,24],'FarShoulder':[7,18]}]
SPECS=[
 {'helmet':[[165,85],[379,85],[379,289],[358,286],[342,285],[320,284],[299,281],[277,278],[254,272],[231,268],[211,262],[190,254],[176,247],[165,244]],
  'arm':[[193,267],[206,270],[217,279],[222,291],[216,303],[208,314],[201,317],[190,309],[181,307],[173,311],[164,322],[159,315],[163,299],[171,286],[183,275]],
  'hand':[[163,316],[170,307],[184,304],[195,309],[207,317],[215,321],[227,327],[234,335],[240,345],[237,353],[231,358],[226,364],[214,367],[203,370],[192,366],[182,359],[176,347],[168,337],[162,330]],
  'collar':[[176,247],[190,254],[211,262],[231,268],[254,272],[277,278],[299,281],[320,284],[342,285],[358,286]],
  'cuff':[[163,316],[170,307],[184,304],[195,309],[207,317],[215,321]],
  'risk':'J0 collar/sleeve/glove limits newly traced from E637 retained RGB crop; adjacent ink/AA can be assigned differently after Root semantic review.'},
 {'helmet':[[175,75],[365,75],[365,267],[342,266],[319,264],[299,261],[278,256],[257,252],[234,248],[213,244],[194,240],[181,236],[174,232]],
  'arm':[[181,240],[197,242],[212,249],[220,260],[211,273],[195,278],[174,281],[153,282],[145,275],[140,260],[138,249],[151,252],[166,252],[176,247]],
  'hand':[[131,187],[148,183],[162,185],[173,189],[181,194],[186,204],[185,217],[180,227],[179,240],[176,249],[164,253],[150,252],[140,248],[135,241],[135,231],[132,220],[131,205]],
  'collar':[[181,236],[194,240],[213,244],[234,248],[257,252],[278,256],[299,261],[319,264],[342,266]],
  'cuff':[[135,241],[140,248],[150,252],[164,253],[176,249]],
  'risk':'J1 raised cuff/helmet edge touch in source. Full visible cuff/glove owns foreground, no hidden anatomy reconstructed.'}
]

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
def polygon(points):
 # Same binary polygon algorithm as proven old Primary1 builder; new outlines.
 im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)!=0
def premultiplied(x):
 return np.concatenate((x[:,:,:3].astype(np.uint32)*x[:,:,3:4],x[:,:,3:4].astype(np.uint32)*255),axis=2)
def translate(a,dx,dy):
 result=np.zeros_like(a);x0=max(0,-dx);x1=min(512,512-dx);y0=max(0,-dy);y1=min(512,512-dy)
 retained=np.zeros((512,512),bool);retained[y0:y1,x0:x1]=True
 assert not np.any(a[~retained]),'Integer translation clips source RGBA, including hidden RGB.'
 result[y0+dy:y1+dy,x0+dx:x1+dx]=a[y0:y1,x0:x1]
 assert np.array_equal(result[y0+dy:y1+dy,x0+dx:x1+dx],a[y0:y1,x0:x1])
 assert np.count_nonzero(result[:,:,3])==np.count_nonzero(a[:,:,3]);return result
def sword_layer(grip,axis):
 # Independent sword only; source-positive-X axis, source grip99,256, scale.5.
 theta=math.atan2(axis[1],axis[0]);c=math.cos(theta);s=math.sin(theta);k=.5;gx,gy=grip
 inv=(c/k,s/k,99-(c*gx+s*gy)/k,-s/k,c/k,256+(s*gx-c*gy)/k)
 im=Image.open(SWORD).convert('RGBa').transform((512,512),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC).convert('RGBA')
 return np.array(im),{'source':pin(SWORD),'component_grip':[99,256],'weapon_scale':.5,'artist_axis':axis,'source_to_canvas_rotation_degrees':math.degrees(theta),'inverse_affine':list(inv),'resample':'BICUBIC premultiplied RGBa; QC only, independent source not changed'}
def compose(layers,with_armor=True,with_sword=True):
 im=Image.new('RGBA',(512,512))
 for name in ORDER:
  if name in ['FarShoulder','Chest','NearShoulder'] and not with_armor:continue
  if name=='IndependentSword' and not with_sword:continue
  im=Image.alpha_composite(im,Image.fromarray(layers[name]))
 return np.array(im)
def display(a,bg):
 # Exact source-to-display factor72/416; ground(root256,464) at50,90.
 inv=(1/SCALE,0,256-50/SCALE,0,1/SCALE,464-90/SCALE)
 x=Image.fromarray(a).convert('RGBa').transform((100,100),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC).convert('RGBA')
 canvas=Image.new('RGBA',(100,100),bg+(255,));return np.array(Image.alpha_composite(canvas,x).convert('RGB'))

assert set(p.name for p in OUT.iterdir())=={Path(__file__).name},'Exclusive new output only.'
ex=read(EXTRACT/'source-closure-v001.json');oldmarkers=read(MARKERS);mounts=read(MOUNTS)
assert pin(EXTRACT/'extraction-freeze-v001.json')['sha256']=='016aacc3acf84b359f1664ab463113d7d17d58a7bca4302546aa6795facbed62'
dependencies=[pin(EXTRACT/'source-closure-v001.json'),pin(EXTRACT/'extraction-freeze-v001.json'),pin(OLD_SCRIPT),pin(MARKERS),pin(MOUNTS),pin(SWORD)]
frame_receipts=[];mapframes=[];new_wholes=[];trial_wholes=[];boundaries=[]
for i,spec in enumerate(SPECS):
 src=Path(ex['frames'][i]['transparent_candidate']['path']);assert pin(src)==ex['frames'][i]['transparent_candidate'];dependencies.append(pin(src));a=rgba(src)
 helmet,arm,hand=(polygon(spec[k]) for k in ['helmet','arm','hand'])
 labels=np.zeros((512,512),np.uint8);labels[helmet]=1;labels[arm&~helmet]=2;labels[hand]=3
 owners=[labels==k for k in range(4)];assert np.array_equal(sum(m.astype(np.uint8) for m in owners),np.ones((512,512),np.uint8))
 layers={};files={};owner_metrics=[]
 for k,name in enumerate(NAMES):
  v=np.zeros_like(a);v[owners[k]]=a[owners[k]];layers[name]=v
  files[name]=pin(save(f'body-layers/{name}/frame-{i}.png',v));mask=pin(save(f'owner-masks/{name}/frame-{i}.png',(owners[k]*255).astype(np.uint8)))
  owner_metrics.append({'owner':name,'source':files[name],'mask':mask,'owned_coordinates':int(owners[k].sum()),'alpha_nonzero':int(np.count_nonzero(v[:,:,3])),'alpha_bbox':bbox(v[:,:,3]>0)})
 recovered=np.sum(np.stack(list(layers.values())),axis=0,dtype=np.uint16).astype(np.uint8);assert np.array_equal(recovered,a)
 im=Image.new('RGBA',(512,512))
 for name in NAMES:im=Image.alpha_composite(im,Image.fromarray(layers[name]))
 assert np.array_equal(premultiplied(np.array(im)),premultiplied(a))
 labelcolor=np.array([[70,155,230],[75,190,100],[215,70,185],[240,190,40]],np.uint8)[labels]
 labelcolor[a[:,:,3]==0]=[245,245,245];labelpath=save(f'qc/ownership-labels-{i}.png',labelcolor)
 boundary=Image.new('L',(512,512));d=ImageDraw.Draw(boundary)
 for key in ['collar','cuff']:d.line([tuple(v) for v in spec[key]],fill=255,width=7,joint='curve')
 bandpath=save(f'qc/semantic-boundary-band-{i}.png',np.array(boundary))
 grip=[211,343] if i==0 else [159,213];axis=[.94,-.341] if i==0 else [-.2,-.98]
 assert labels[grip[1],grip[0]]==3,'Candidate grip must belong to NearHand.'
 armored=[]
 for name in ['Chest','NearShoulder','FarShoulder']:
  ap=LGT/'armor-layers'/name/f'frame-{i}.png';dependencies.append(pin(ap));original=rgba(ap);dx,dy=DELTAS[i][name];fitted=translate(original,dx,dy);layers[name]=fitted
  files[name]=pin(save(f'armor-integer-fit/{name}/frame-{i}.png',fitted))
  row=next(v for v in mounts['rows'] if v['frame']==i and v['component']==name)
  oldB=row['B_body_design_source_px'];newB=[oldB[0]+dx,oldB[1]+dy]
  opaque=fitted[:,:,3]>=128
  armored.append({'component':name,'original_source':pin(ap),'candidate':files[name],'integer_delta_xy':[dx,dy],'old_visible_mount_B':oldB,'new_visible_mount_B_proposal':newB,'new_B_uncertainty_source_px_each_axis':8,'rotation':0,'extra_scale':1,'RGBA_translation_reversible':True,'nonzero_RGBA_clipped':0,'alpha128_bbox':bbox(opaque),'alpha128_pixels':int(opaque.sum()),'alpha128_outside_body_silhouette':int(np.count_nonzero(opaque&(a[:,:,3]==0))),'alpha128_intersect_HelmetForeground_owner':int(np.count_nonzero(opaque&owners[1])),'alpha128_intersect_NearHand_owner':int(np.count_nonzero(opaque&owners[3])),'fit_accepted':False})
 layers['IndependentSword'],sw=sword_layer(grip,axis)
 body_sword=compose(layers,False,True);trial=compose(layers,True,True)
 bodypath=save(f'qc/body-independent-sword-{i}-candidate.png',body_sword);trialpath=save(f'qc/LGT-independent-sword-{i}-candidate.png',trial)
 new_wholes.append(a);trial_wholes.append(trial)
 boundaries.append({'frame':i,'fresh_source_trace':pin(src),'polygons':{k:spec[k] for k in ['helmet','arm','hand']},'boundary_uncertainty_source_px':3,'risk':spec['risk'],'semantic_accepted':False,'ownership_labels':pin(labelpath),'uncertainty_band':pin(bandpath)})
 frame_receipts.append({'frame':i,'source':pin(src),'source_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'recovered_RGBA_sha256':hashlib.sha256(recovered.tobytes()).hexdigest(),'all_RGBA_equal':True,'premultiplied_composite_equal':True,'overlapping_owner_coordinates':0,'unowned_coordinates':0,'hidden_RGB_preserved':True,'source_pixel_coordinates_changed':False,'layers':owner_metrics,'armor_trials':armored,'sword_QC_transform':sw,'body_sword_QC':pin(bodypath),'armor_sword_QC':pin(trialpath),'new_images_viewed':False})
 mapframes.append({'frame':i,'duration_ms':[85,85][i],'body_source':pin(src),'component_sources':files,'Root':[256,464],'Grip':grip,'Axis':axis,'marker_status':'Root-approved for bounded candidate test only; not final socket/art/native acceptance','Grip_uncertainty_source_px_each_axis':12,'Axis_measured':False,'Axis_uncertainty_degrees':25,'IndependentSword':pin(SWORD),'slot_order':ORDER,'armor_mounts_approved':False})

# Keep actual old runtime frames2..5 as pinned references, not new accepted copies.
for i in range(2,6):
 refs={}
 for name in NAMES:
  p=OLD/'macro-registration-primary1-v001/textures'/name/f'frame-{i}.png';refs[name]=pin(p);dependencies.append(pin(p))
 for name in ['Chest','NearShoulder','FarShoulder']:
  p=LGT/'armor-layers'/name/f'frame-{i}.png';refs[name]=pin(p);dependencies.append(pin(p))
 m=oldmarkers['frames'][i]
 mapframes.append({'frame':i,'status':'EXACT_OLD_RUNTIME_REUSED_REFERENCE_ONLY','newly_accepted':False,'files_copied':False,'component_sources':refs,'old_marker_record':m,'slot_order':ORDER})

oldbase=PROD/'fairytale-sword-v001';compare=[]
for label,p in [('Ready0',oldbase/'run-ready-v002/curated/frame-0.png'),('old_J0',oldbase/'run-primary1-v003/curated/frame-0.png'),('old_J1',oldbase/'run-primary1-v003/curated/frame-1.png')]:
 dependencies.append(pin(p));compare.append((label,rgba(p)))
compare += [('new_J0',new_wholes[0]),('new_J1',new_wholes[1])]
board=np.zeros((200,500,3),np.uint8)
for row,bg in enumerate([(24,28,30),(220,216,202)]):
 for col,(_,a) in enumerate(compare):board[row*100:(row+1)*100,col*100:(col+1)*100]=display(a,bg)
boardpath=save('qc/body-only-72rule-dark-light-comparison.png',board)
fitboard=np.zeros((200,200,3),np.uint8)
for row,bg in enumerate([(24,28,30),(220,216,202)]):
 for col,a in enumerate(trial_wholes):fitboard[row*100:(row+1)*100,col*100:(col+1)*100]=display(a,bg)
fitpath=save('qc/LGT-sword-72rule-dark-light-candidate.png',fitboard)
qcmap={'body_comparison':pin(boardpath),'columns':[v[0] for v in compare],'rows':['darkRGB24,28,30','lightRGB220,216,202'],'cell':[100,100],'exact_source_to_display_scale':SCALE,'ground_display':[50,90],'source_root':[256,464],'sampling':'BICUBIC premultiplied RGBa; QC image only','armor_sword_comparison':pin(fitpath),'armor_columns':['new_J0_integer_armor_trial','new_J1_integer_armor_trial'],'source_RGBA_unchanged':True,'halos_accepted':False,'images_viewed':False}
write('comparison-map-v001.json',qcmap)
write('fresh-owner-boundaries-v001.json',{'frames':boundaries,'algorithm_reused_from':pin(OLD_SCRIPT),'assignment':'All coordinates default BodyRest; fresh helmet; fresh near sleeve excluding helmet; full cuff/hand overrides as NearHand. Background ownership preserves hidden RGB, not anatomy.','final_render_order':ORDER,'semantic_accepted':False})
write('six-frame-candidate-map-v001.json',{'frames':mapframes,'source_canvas':[512,512],'standing_extent':416,'standing_display':72,'weapon_scale':.5,'candidate_Content_namespace':None,'source_or_Content_changed':False,'native_accepted':False,'FinalAccepted':False})

# Three exact component requests if source-preserving trials fail Root visual review.
requests=[]
for name in ['Chest','NearShoulder','FarShoulder']:
 requests.append({'component':name,'scope':'TWO poses J0/J1 only, one2-cell component row','frame_count':2,'cell':[512,512],'durations_ms':[85,85],'body_reference_frames':[pin(Path(ex['frames'][i]['transparent_candidate']['path'])) for i in [0,1]],'style_reference_component_frames':[pin(LGT/'armor-layers'/name/f'frame-{i}.png') for i in [0,1]],'body_root':[256,464],'new_visible_mount_targets':[next(r for r in frame_receipts[i]['armor_trials'] if r['component']==name)['new_visible_mount_B_proposal'] for i in [0,1]],'mount_targets_status':'Artist candidate ±8px, require Root confirmation before generation','requirements':f'Only {name} brown light-leather armor; same current LGT color/material/ink and volume. Match the two exact258 body poses without modifying bodies. Separate transparent neckline/arm aperture when applicable; no body, glove, helmet, sword, filler backing, heavy steel redesign or enlarged shoulders. Preserve identity; fresh geometry only if existing rigid pieces fail actual review.','paid_generation_invoked':False})
write('three-armor-generation-inputs-if-needed-v001.json',{'status':'CONTINGENCY_NOT_EXECUTED_NOT_GENERATION_APPROVAL','requests':requests,'reason':'Integer translations are legal source-preserving trials; geometric cleanliness is unproven without Root viewing retained candidate composites. Do not force fitting or substitute merged whole body.'})

unique={v['path']:v for v in dependencies};dependencies=list(unique.values())
proof={'schema':'request258-two-four-owner-LGT-fit-candidate-v001','utc':dt.datetime.now(dt.timezone.utc).isoformat(),'frames':frame_receipts,'dependency_pins':dependencies,'all_source_RGBA_reconstructed_exact':True,'body_pixels_painted_or_resampled':False,'hidden_anatomy_reconstructed':False,'new_partition_count':8,'new_integer_armor_trial_count':6,'armor_fit_accepted':False,'new_derivatives_viewed':False,'E_retention_of_derivatives':'PENDING_ROOT','UE_called':False,'Source_Content_tools_media_E_ledger_changed':False,'native_or_final_art_accepted':False,'FinalAccepted':False}
write('body-owner-fit-proof-v001.json',proof)
table=[]
for f in frame_receipts:
 for a in f['armor_trials']:
  table.append(f"| J{f['frame']} {a['component']} | {a['integer_delta_xy']} | {a['alpha128_bbox']} | {a['alpha128_outside_body_silhouette']} | {a['alpha128_intersect_HelmetForeground_owner']} | {a['alpha128_intersect_NearHand_owner']} |")
report='''# request258 两姿势四owner与旧轻甲整数试装候选 v001

仅新增本候选目录。8张身体owner层逐像素重组等于已E637留存的两张258透明源图；全画布每个坐标恰有一个owner，包括alpha0隐藏RGB。RGBA总和与预乘合成都精确；没有重绘、补洞、重建隐藏身体或改变源坐标。NearHand包括完整可见袖口/手套，并位于独立军剑之后。新边界取自E637原格可见轮廓，盔沿/袖口±3px语义边界仍待Root看图，不把代数重组等同语义认可。

Root/Grip/Axis采用Root授权候选值：(256,464)；J0(211,343)/(.94,-.341)，J1(159,213)/(-.2,-.98)。两Grip均落在NearHand。Grip±12px、Axis±25°且未测；仅用于候选试装。旧运行2–5仅引用原7层及marker记录，逐项pin，不复制为新验收素材。

现有Chest/NearShoulder/FarShoulder各作一次整数平移，无旋转/额外缩放，原RGBA可逆且无裁失。新挂点由旧可见挂点加声明delta得到，是±8px待确认的艺术提案。下列交集是遮挡诊断，不是坏点自动判定：盔/手后画可合法遮盖甲片；外轮廓肩甲也可超出原内衣。不能据此声称贴合干净。

| 试装 | 整数delta | alpha128 bbox | 甲像素在身体轮廓外 | 交盔owner | 交手owner |
|---|---|---|---:|---:|---:|
'''+ '\n'.join(table)+'''

新qc图未View，待Root F/E留存后审阅。body-only对照为Ready0/旧J0/旧J1/新J0/新J1五列，暗/亮两行；按固定72/416比例、共同Root投影，不逐格归一化。另有两格旧甲+独立剑原尺度及512试装。比较图只作声明的预乘采样和排布，所有生产源层原RGBA保持。背景透明RGB可能含洋红，工具直接显示RGB不代表alpha不透明；真正晕边需看暗/亮合成。

结论：四owner候选已准备；旧三甲只达到可逆整数试装，尚不能确认清洁贴合。若Root看图认为胸腰/袖口/肩帽不合，不拉伸或补画：three-armor-generation-inputs-if-needed-v001.json给出Chest、NearShoulder、FarShoulder三份各含J0/J1两格的准确源/样式参考和挂点提案。未调用生成，未提交导入，更未做原生或最终美术验收。FinalAccepted=false。
'''
write('body-partition-fit-report-v001.md',report)
members=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
write('body-partition-fit-freeze-v001.json',{'schema':'request258-two-body-partition-fit-freeze-v001','members':members,'dependency_pins':dependencies,'new_derivatives_viewed':False,'E_retention':'PENDING_ROOT','FinalAccepted':False})
for r in dependencies:assert pin(Path(r['path']))==r
print(json.dumps({'new_body_layers':8,'new_armor_integer_trials':6,'RGBA_partition_exact':True,'premultiplied_exact':True,'semantic_accepted':False,'armor_fit_accepted':False,'new_images_viewed':False,'source_dependencies':len(dependencies),'freeze':pin(OUT/'body-partition-fit-freeze-v001.json'),'report':pin(OUT/'body-partition-fit-report-v001.md')},ensure_ascii=False))
