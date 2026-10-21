"""Native175 fresh four-owner original-RGBA partition candidate; do not view outputs.
Semantic contours remain candidates even when numerical reconstruction is exact.
"""
from pathlib import Path
from datetime import datetime
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
FAMILY=Path('F:/Ourgame/source-assets/production/fairytale-sword-primary3-v001')
SOURCE=FAMILY/'run-primary3-v001/curated'
MEASURE=FAMILY/'primary3-measurement-v001/primary3-measurement-candidate-v001.json'
NAMES=['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']

# Fresh175 manual lower-shell/visible collar boundaries, not a horizontal band.
# Original RGBA samples in the output evidence expose each uncertain ink choice.
LOWER=[
 [[170,203],[180,209],[190,213],[200,217],[210,219],[220,220],[230,223],[240,224],[250,226],[260,228],[270,230],[280,234],[290,237],[300,239],[310,240],[320,240],[330,240],[340,239],[350,234],[360,226]],
 [[200,207],[210,211],[220,215],[230,217],[240,219],[250,221],[260,223],[270,225],[280,228],[290,231],[300,234],[310,236],[320,237],[330,237],[340,237],[350,235],[360,229],[370,221]],
 [[175,202],[185,207],[195,211],[205,215],[215,218],[225,218],[235,220],[245,220],[255,222],[265,224],[275,226],[285,230],[295,232],[305,235],[315,238],[325,239],[335,239],[345,238],[355,234],[365,224]],
 [[195,210],[205,217],[215,220],[225,223],[235,226],[245,227],[255,230],[265,233],[275,235],[285,238],[295,240],[305,243],[315,247],[325,250],[335,252],[345,252],[355,252],[365,252],[375,248],[385,240]],
 [[205,219],[215,225],[225,228],[235,231],[245,234],[255,237],[265,239],[275,241],[285,244],[295,247],[305,250],[315,255],[325,258],[335,259],[345,261],[355,262],[365,262],[375,260],[385,255],[400,246]],
 [[160,199],[170,206],[180,210],[190,214],[200,217],[210,220],[220,221],[230,222],[240,223],[250,224],[260,226],[270,229],[280,231],[290,232],[300,233],[310,234],[320,234],[330,234],[340,230],[350,223]],
]
# Explicit external top/side silhouette enclosures, with margin only on transparent
# side of the observed shell/knob. No bbox anatomy or material-threshold selector.
OUTER=[
 [[170,198],[186,186],[196,168],[186,163],[191,150],[204,148],[211,132],[228,116],[250,106],[251,96],[242,88],[239,79],[265,60],[282,59],[298,82],[285,96],[302,101],[305,110],[325,121],[343,142],[350,155],[361,164],[363,180],[350,185],[347,207],[357,211],[362,225]],
 [[195,201],[205,184],[204,171],[199,161],[201,147],[214,144],[223,125],[240,110],[267,102],[268,93],[253,84],[250,73],[277,55],[296,55],[312,80],[299,94],[308,99],[310,107],[333,120],[350,142],[358,155],[370,163],[372,180],[360,185],[354,209],[366,215],[372,221]],
 [[170,196],[190,185],[199,168],[191,161],[194,147],[208,144],[215,127],[233,110],[261,102],[262,93],[251,84],[249,72],[273,53],[295,53],[310,79],[298,94],[306,99],[307,109],[331,124],[348,145],[357,158],[372,167],[374,183],[361,187],[355,212],[366,218],[369,225]],
 [[190,203],[211,192],[220,175],[212,168],[215,155],[228,154],[236,137],[253,122],[279,113],[280,104],[271,94],[269,81],[296,63],[317,63],[331,90],[320,106],[328,113],[329,121],[351,138],[366,158],[373,170],[389,177],[390,192],[378,197],[373,221],[386,229],[390,240]],
 [[200,212],[220,201],[229,184],[221,178],[225,164],[239,163],[245,147],[263,131],[290,123],[291,114],[281,103],[280,92],[306,73],[328,73],[343,99],[330,115],[339,122],[339,130],[360,145],[376,166],[385,180],[401,187],[404,203],[388,207],[383,231],[397,238],[404,246]],
 [[150,192],[177,182],[187,164],[177,157],[181,143],[194,142],[200,124],[220,108],[243,100],[244,90],[229,81],[227,70],[251,54],[272,54],[289,79],[278,94],[285,101],[286,108],[309,123],[325,143],[334,156],[349,165],[351,181],[338,185],[334,208],[347,216],[354,224]],
]
ARM=[
 [[208,231],[220,233],[231,242],[236,252],[230,265],[221,278],[216,290],[210,283],[201,277],[189,274],[180,277],[170,286],[165,285],[170,269],[177,255],[188,242],[199,235]],
 [[201,225],[215,225],[228,235],[231,247],[224,260],[211,264],[198,263],[185,265],[169,263],[158,256],[155,246],[158,238],[167,240],[179,244],[194,238]],
 [[220,222],[235,224],[247,233],[262,245],[282,252],[300,259],[317,270],[309,279],[304,290],[303,303],[293,297],[284,284],[270,279],[251,272],[232,263],[216,256],[204,247],[202,236],[208,226]],
 [[239,235],[252,238],[264,250],[270,266],[279,285],[290,303],[300,314],[289,315],[282,323],[277,333],[278,343],[286,351],[274,347],[261,334],[252,317],[244,301],[235,284],[229,266],[228,250],[232,240]],
 [[238,243],[251,243],[263,254],[270,269],[271,284],[273,301],[276,315],[263,316],[255,323],[249,334],[249,345],[256,353],[244,349],[233,339],[230,323],[228,306],[223,287],[222,270],[228,255]],
 [[204,229],[216,230],[229,240],[234,252],[228,266],[220,280],[215,291],[207,284],[198,277],[186,273],[176,279],[165,288],[160,286],[167,267],[176,251],[186,238],[196,231]],
]
# Newly traced FULL original brown cuff + glove + outer ink/AA, independently
# wider than the measurement's glove-only polygon; no old source contour reused.
HAND=[
 [[165,287],[173,281],[183,276],[194,275],[205,278],[213,285],[219,294],[228,300],[236,309],[241,318],[239,328],[232,337],[221,342],[209,344],[196,342],[185,336],[178,327],[175,316],[167,309],[162,301],[161,294]],
 [[155,211],[164,204],[166,188],[169,176],[178,167],[190,163],[203,164],[215,171],[223,181],[226,192],[222,204],[214,212],[204,218],[202,229],[195,239],[181,243],[167,242],[155,234],[152,224]],
 [[314,269],[324,269],[335,275],[344,279],[358,279],[372,282],[385,289],[391,300],[391,310],[385,318],[375,324],[365,328],[354,329],[343,325],[333,320],[321,319],[309,313],[302,306],[299,295],[302,281],[307,273]],
 [[291,315],[306,314],[317,322],[324,335],[338,338],[351,346],[362,357],[364,368],[357,380],[341,390],[323,388],[311,380],[302,369],[294,362],[283,354],[276,344],[275,334],[281,323]],
 [[261,320],[274,315],[286,318],[298,328],[304,338],[319,343],[331,350],[340,359],[344,370],[342,381],[333,388],[319,393],[304,391],[293,384],[282,375],[273,367],[261,360],[252,352],[248,344],[250,333],[255,325]],
 [[164,286],[172,280],[183,276],[194,275],[205,278],[213,285],[217,293],[225,298],[234,307],[239,315],[237,327],[229,335],[216,342],[203,343],[190,339],[180,332],[175,320],[167,312],[160,304],[159,295]],
]
CUFF=[
 [[165,287],[173,281],[183,276],[194,275],[205,278],[213,285],[219,294]],
 [[155,211],[164,204],[204,218],[202,229],[195,239],[181,243],[167,242],[155,234]],
 [[314,269],[307,273],[302,281],[299,295],[302,306],[309,313]],
 [[291,315],[281,323],[275,334],[276,344],[283,354],[294,362]],
 [[261,320],[255,325],[250,333],[248,344],[252,352],[261,360]],
 [[164,286],[172,280],[183,276],[194,275],[205,278],[213,285],[217,293]],
]
INNER_ARM=[
 [[220,233],[231,242],[236,252],[230,265],[221,278],[216,290]],
 [[215,225],[228,235],[231,247],[224,260],[211,264],[198,263]],
 [[216,256],[232,263],[251,272],[270,279],[284,284],[293,297],[303,303]],
 [[252,238],[264,250],[270,266],[279,285],[290,303],[300,314]],
 [[251,243],[263,254],[270,269],[271,284],[273,301],[276,315]],
 [[216,230],[229,240],[234,252],[228,266],[220,280],[215,291]],
]
HAND_INNER=[
 [[228,300],[236,309],[241,318],[239,328],[232,337],[221,342],[209,344],[196,342],[185,336],[178,327]],
 [[215,171],[223,181],[226,192],[222,204],[214,212],[204,218]],
 [[375,324],[365,328],[354,329],[343,325],[333,320],[321,319],[309,313]],
 [[351,346],[362,357],[364,368],[357,380],[341,390],[323,388],[311,380],[302,369]],
 [[319,343],[331,350],[340,359],[344,370],[342,381],[333,388],[319,393],[304,391],[293,384],[282,375]],
 [[225,298],[234,307],[239,315],[237,327],[229,335],[216,342],[203,343],[190,339],[180,332]],
]
RISKS=[
 'Low cuff/glove edge meets belt and trousers. Full original brown cuff is NearHand; shared low ink split remains uncertain.',
 'Near closed fist touches helmet side. Hand takes priority on shared ink; no hidden shell is reconstructed. Raised gray sleeve and cuff seam need retained-image review.',
 'Near glove/cuff overlaps far hand. Full visible near cuff and glove only; far fingers remain BodyRest. The lower near-glove ink/upper far-hand boundary is uncertain by several pixels.',
 'Downward gray sleeve crosses torso and brown cuff is beside low fist/thigh. Sleeve-to-torso and glove-to-pants shared ink remain candidates, not accepted masks.',
 'Low cuff/glove lies against front thigh/knee and close to belt. Full brown outer AA belongs NearHand, but adjacent pants/belt must remain BodyRest; no inferred hidden wrist/cloth.',
 'Return guard is a different source from phase0. Its cuff/glove outer edge and collar seam are independently defined; no copied pose mask or foot-lock acceptance.',
]

def fact(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,value):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 return p
def mask(points):
 im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
def sample(a,p):return {'xy':p,'rgba':a[p[1],p[0]].tolist()}
def pm(a):return np.concatenate((a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255),axis=2)
def save(p,a):
 assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(p)
 assert np.array_equal(np.asarray(Image.open(p)),a)

assert not (HERE/'layers').exists() and not (HERE/'proof-v001.json').exists(),'Never overwrite partition outputs'
assert fact(MEASURE)['sha256']=='474be5e1b1046ee59a28e0be3141f9785c56c8e94975665f0297264b44b045f9'
measurement=json.loads(MEASURE.read_text(encoding='utf-8'))
mf=MEASURE.parent/'measurement-freeze-v001.json';assert fact(mf)['sha256']=='c8eb0317572f26ae6a03943e2228c41d3435e215a7dab082ce23a46abb594c11'
for f in json.loads(mf.read_text(encoding='utf-8'))['files']:assert fact(f['path'])==f
staged=[]
# First validate all local control assignments before writing ANY PNG.
for i,m in enumerate(measurement['rows']):
 p=SOURCE/f'frame-{i}.png';assert fact(p)==m['source']
 with Image.open(p) as im:
  assert im.mode=='RGBA' and im.size==(512,512);a=np.asarray(im).copy()
 head_points=OUTER[i]+list(reversed(LOWER[i]));helmet=mask(head_points);arm=mask(ARM[i]);hand=mask(HAND[i])
 assert HAND[i]!=m['near_glove_visible_polygon_candidate']['points'],'Do not use glove-only measurement polygon as complete hand mask'
 labels=np.zeros((512,512),dtype=np.uint8);labels[helmet]=1;labels[arm&~helmet]=2;labels[hand]=3
 controls=[('actual_palm',m['near_palm_candidate']['point'],3),('near_gray_shoulder_design',m['body_design_A_candidates']['NearShoulder']['point'],2),
  ('visible_gray_collar',[[260,236],[260,234],[260,235],[283,247],[283,258],[260,235]][i],0),
  ('visible_far_glove',[[349,345],[367,335],[350,341],[369,333],[373,342],[349,344]][i],0),
  ('visible_belt',[[270,310],[265,311],[260,310],[223,312],[219,313],[267,309]][i],0),
  ('visible_gray_leg',[[240,365],[204,356],[203,355],[202,356],[198,351],[215,355]][i],0),('full_brown_cuff',[[192,289],[181,221],[319,294],[297,338],[271,340],[188,291]][i],3)]
 cr=[]
 for role,point,expected in controls:
  x,y=point;assert int(labels[y,x])==expected,(i,role,point,NAMES[int(labels[y,x])],NAMES[expected])
  assert a[y,x,3]>0,(i,role,'control must sample actual visible original RGBA')
  cr.append({'role':role,'source_sample':sample(a,point),'selected_owner':NAMES[expected],'scope':'Local sanity only, not full semantic contour proof'})
 staged.append((p,a,head_points,helmet,arm,hand,labels,cr))

colors=np.array([[70,155,230],[75,190,100],[215,70,185],[240,190,40]],dtype=np.uint8)
receipts=[];boundaries=[]
for i,(source_path,source,head_points,helmet,arm,hand,labels,controls) in enumerate(staged):
 owners=[labels==k for k in range(4)];assert np.all(np.sum(np.stack(owners),axis=0)==1)
 visible=source[:,:,3]>0;partial=visible&(source[:,:,3]<255);invisible_rgb=(source[:,:,3]==0)&np.any(source[:,:,:3]!=0,axis=2)
 layers=[];lr=[];mr=[]
 for k,name in enumerate(NAMES):
  layer=np.zeros_like(source);layer[owners[k]]=source[owners[k]]
  assert np.array_equal(layer[owners[k]],source[owners[k]]) and not np.any(layer[~owners[k]])
  path=HERE/'layers'/name/f'frame-{i}.png';save(path,layer)
  mp=HERE/'masks'/name/f'frame-{i}.png';save(mp,(owners[k]*255).astype(np.uint8))
  lr.append({'owner':name,'file':fact(path),'owned_coordinates':int(owners[k].sum()),'source_visible_pixels':int((owners[k]&visible).sum()),'source_partial_alpha_pixels':int((owners[k]&partial).sum()),'source_alpha0_nonzeroRGB_pixels':int((owners[k]&invisible_rgb).sum()),'visible_alpha_bbox_diagnostic_only':Image.fromarray(layer).getbbox()})
  mr.append({'owner':name,'file':fact(mp),'binary_assignment':True});layers.append(layer)
 recovered=np.sum(np.stack(layers),axis=0,dtype=np.uint16);assert np.array_equal(recovered,source.astype(np.uint16));recovered=recovered.astype(np.uint8)
 composed=Image.new('RGBA',(512,512),(0,0,0,0))
 for layer in layers:composed=Image.alpha_composite(composed,Image.fromarray(layer))
 assert np.array_equal(pm(np.asarray(composed)),pm(source))
 rp=HERE/f'diagnostics/frame-{i}-reconstructed-source.png';save(rp,recovered)
 labeled=np.full((512,512,3),245,dtype=np.uint8);labeled[visible]=colors[labels[visible]]
 cp=HERE/f'diagnostics/frame-{i}-ownership-colors.png';save(cp,labeled)
 overlay=source.copy();overlay[visible,:3]=((source[visible,:3].astype(np.uint16)*2+colors[labels[visible]].astype(np.uint16))//3).astype(np.uint8)
 op=HERE/f'diagnostics/frame-{i}-ownership-overlay.png';save(op,overlay)
 band=Image.new('L',(512,512),0);draw=ImageDraw.Draw(band)
 specs={'helmet_collar_boundary':{'points':LOWER[i],'uncertainty_source_px':2},'arm_torso_boundary':{'points':INNER_ARM[i],'uncertainty_source_px':3},'sleeve_cuff_boundary':{'points':CUFF[i],'uncertainty_source_px':3},'hand_other_body_boundary':{'points':HAND_INNER[i],'uncertainty_source_px':3}}
 if i==1:specs['fist_helmet_shared_ink']={'points':[[215,171],[223,181],[226,192],[222,204],[214,212]],'uncertainty_source_px':3}
 if i==2:specs['near_far_hand_shared_ink']={'points':[[375,324],[365,328],[354,329],[343,325],[333,320]],'uncertainty_source_px':3}
 for s in specs.values():draw.line([tuple(p) for p in s['points']],fill=255,width=2*s['uncertainty_source_px']+1,joint='curve')
 bp=HERE/f'diagnostics/frame-{i}-uncertainty-review-band.png';save(bp,np.asarray(band))
 boundaries.append({'frame':i,'source':fact(source_path),'manual_polygons':{'helmet':head_points,'near_arm':ARM[i],'full_brown_cuff_and_near_hand':HAND[i]},'candidate_boundaries':specs,'source_boundary_rgba_samples':{key:[sample(source,p) for p in s['points']] for key,s in specs.items()},'source_controls':controls,'risk':RISKS[i],'actual_hidden_bones':None,'semantic_ownership_accepted':False})
 receipts.append({'frame':i,'source':fact(source_path),'layers':lr,'masks':mr,'reconstructed_source':fact(rp),'ownership_colors':fact(cp),'ownership_overlay':fact(op),'uncertainty_review_band':fact(bp),'source_rgba_bytes_sha256':hashlib.sha256(source.tobytes()).hexdigest(),'reconstructed_rgba_bytes_sha256':hashlib.sha256(recovered.tobytes()).hexdigest(),'rgba_all_bytes_equal':True,'premultiplied_composite_equal':True,'source_alpha0_nonzeroRGB_pixels':int(invisible_rgb.sum()),'multiple_owner_coordinates':0,'unowned_coordinates':0,'candidate_polygon_visible_overlap_counts':{'helmet_arm':int((helmet&arm&visible).sum()),'helmet_hand':int((helmet&hand&visible).sum()),'arm_hand':int((arm&hand&visible).sum())},'source_controls':controls,'semantic_ownership_accepted':False,'new_outputs_viewed':False})

boundary_file=write('candidate-boundaries-v001.json',{'schema':'native175-four-owner-manual-boundary-candidate-v1','created_local':datetime.now().astimezone().isoformat(),'frames':boundaries,'owner_names':NAMES,'measurement':fact(MEASURE),'measurement_freeze':fact(mf),'source_retention':'Root E227 raw / E228 six original512 source retained before original views; no new derived output viewed.','assignment_priority':'NearHand > HelmetForeground > NearArmWithoutHand > BodyRest; each phase has fresh manual visible contour choices.','transparent_coordinates':'Exactly one bookkeeping owner for every alpha0 coordinate including nonzero invisible RGB; no anatomy claim from transparent enclosure.','helmet_scope':'Observed original shell/eyes/top knob and external AA enclosed by phase-specific full outer silhouette; explicit lower-rim curve excludes low gray collar. No y-band/bbox or material segmentation.','near_hand_scope':'Fresh full brown cuff/glove/outer ink/AA enclosure, not the earlier uncertain glove-only measurement polygon.','body_rest_scope':'Visible far sleeve/hand, torso/low collar/belt/buckle/pants/boots; no hidden skeleton or painted body repair.','future_layer_order_candidate':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','NearHand'],'semantic_accepted':False,'new_outputs_viewed':False})
proof_file=write('proof-v001.json',{'schema':'native175-four-owner-original-RGBA-proof-v1','created_local':datetime.now().astimezone().isoformat(),'script':fact(Path(__file__)),'candidate_boundaries':fact(boundary_file),'frames':receipts,'owner_names':NAMES,'frame_count':6,'layer_count':24,'source_canvas':[512,512],'all_source_coordinates_exactly_one_owner':True,'all_source_RGBA_reconstructions_byte_exact':True,'all_premultiplied_alpha_composites_exact':True,'alpha0_nonzeroRGB_preserved':True,'source_coordinates_shifted_resampled_mirrored':False,'source_originals_changed':False,'new_anatomy_or_hidden_pixels_painted':False,'old_masks_reused':False,'measurement_uncertain_polygon_used_directly_as_owner':False,'semantic_ownership_accepted':False,'new_outputs_explicitly_viewed':False,'armor_generated_imported':False,'UE_called':False,'formal_complete_units':0})
for i,m in enumerate(measurement['rows']):assert fact(SOURCE/f'frame-{i}.png')==m['source']
write('README.md','''# Native175四owner候选\n\n以已E228保全并实际view过的175六原512重新描各相完整brown cuff+glove、灰近袖和完整钟盔；没有直接把测量glove polygon冒充完整手mask，没有复用171坐标/层或用bbox/yband/材质阈值替语义。NearHand优先，其次Helmet、NearArm，其余及farhand/低领/腰带/裤靴归BodyRest。Helmet各相独立外侧包络与下盔沿控制；隐藏轮廓/骨不补。\n\n24原RGBA层、24坐标assignment masks、24技术诊断。原每坐标恰一owner；PNG读回各值相同，四层uint16求和还原整张RGBA逐字节，premultiplied合成相同，alpha0非零RGB也完整保留。这仅证明数值保全，不接受语义/外沿/握柄/甲剑遮挡。局部控制点只是sanity，无法替代Root图审。\n\n重点风险：1拳盔共享墨线，2近远手交叠，3/4低腕与裤/膝以及袖口边缘。每相保留±2/3px原RGBA边界采样与技术风险带。新图未view/emit/display；先RootF/E保全再审24层。无Source/公共tools/台账/媒体/UE/生成/导入改动，正式0/15。\n''')
files=[fact(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
fp=write('partition-freeze-v001.json',{'schema':'native175-four-owner-partition-candidate-freeze-v1','created_local':datetime.now().astimezone().isoformat(),'file_count':len(files),'total_bytes':sum(f['bytes'] for f in files),'files':files,'layer_count':24,'source_count':6,'rgba_reconstruction_exact':True,'premultiplied_composite_exact':True,'semantic_accepted':False,'new_outputs_viewed':False,'formal_complete_units':0})
for f in files:assert fact(f['path'])==f
print(json.dumps({'freeze':fact(fp),'proof':fact(proof_file),'boundaries':fact(boundary_file),'files_including_freeze':len(files)+1,'bytes_including_freeze':sum(f['bytes'] for f in files)+fp.stat().st_size,'layers':24,'RGBA_exact':True,'premultiplied_exact':True,'semantic_accepted':False,'new_outputs_viewed':False,'owner_visible_counts':[{x['owner']:x['source_visible_pixels'] for x in r['layers']} for r in receipts]},ensure_ascii=False))
