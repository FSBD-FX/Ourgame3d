"""Numeric, source-preserving owner proposal only. No View/art/engine mutation."""
from pathlib import Path
from collections import deque
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'request260-extraction-qc-v001'
FREEZE=SRC/'request260-extraction-final-freeze-v001.json'
EXPECTED='ed5d05b49fc4c0123e26f608e6f5f4025de385d7d43936c58d41b463c6ca723b'
NAMES=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']
ORDER=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','NearHand']
NEAR_TARGETS=[(198,300),(151,181),(163,161),(287,294)]
FAR_TARGETS=[(345,316),(339,317),(351,321),(135,258)]
ARM_ROIS=[
 [[156,235],[172,220],[194,218],[215,230],[224,252],[222,275],[207,287],[186,284],[172,275],[157,264]],
 [[124,207],[182,205],[184,223],[202,231],[220,244],[222,264],[209,279],[179,284],[151,277],[133,263],[124,242]],
 [[128,184],[195,183],[195,207],[208,224],[224,240],[224,263],[211,279],[179,286],[153,279],[135,263],[128,236]],
 [[238,221],[264,218],[288,225],[307,239],[313,263],[311,280],[295,286],[273,277],[258,260],[241,249]],
]
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def save(name,a):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists()
 Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
def bbox(mask):
 y,x=np.nonzero(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def components(mask):
 seen=np.zeros(mask.shape,bool);rows=[]
 for y,x in zip(*np.nonzero(mask)):
  if seen[y,x]:continue
  seen[y,x]=True;q=deque([(int(y),int(x))]);pts=[]
  while q:
   a,b=q.popleft();pts.append((a,b))
   for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
    yy,xx=a+dy,b+dx
    if 0<=yy<512 and 0<=xx<512 and mask[yy,xx] and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
  p=np.asarray(pts);m=np.zeros(mask.shape,bool);m[p[:,0],p[:,1]]=True
  rows.append({'area':len(pts),'bbox':bbox(m),'centroid':[float(p[:,1].mean()),float(p[:,0].mean())],'mask':m,'points_xy':p[:,::-1]})
 return sorted(rows,key=lambda v:v['area'],reverse=True)
def summary(c):return {k:c[k] for k in ['area','bbox','centroid']}
def nearest(rows,target):
 def dist(c):
  x0,y0,x1,y1=c['bbox'];return max(x0-target[0],0,target[0]-x1+1)**2+max(y0-target[1],0,target[1]-y1+1)**2
 return min((r for r in rows if r['area']>=128),key=lambda c:(dist(c),-c['area']))
def hull(points):
 p=sorted(set(map(tuple,points.tolist())))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for q in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>=2 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return [[int(x),int(y)] for x,y in lo[:-1]+hi[:-1]]
def polygon(points):
 im=Image.new('L',(512,512));ImageDraw.Draw(im).polygon([tuple(q) for q in points],fill=255);return np.asarray(im)>0
def grow(mask,radius):return np.asarray(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(radius*2+1)))>0
def premultiplied(a):return np.concatenate([a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255],axis=2)
def clearance(a,b):
 if np.any(a&b):return 0
 for r in range(1,33):
  if np.any(grow(a,r)&b):return r
 return '>32'

assert pin(FREEZE)['sha256']==EXPECTED,'Wrong parent260 freeze'
old=read(FREEZE);dependencies=[pin(FREEZE),pin(SRC/'request260-comparison-qc-v001.json'),pin(SRC/'extraction-qc-v001.json')]
for row in old['members']+old['dependency_pins']:assert pin(row['path'])==row
frames=[]
for f in range(4):
 source=SRC/f'aligned512/K{f}-body-footline464-RGBA.png';dependencies.append(pin(source));im=Image.open(source)
 assert im.mode=='RGBA' and im.size==(512,512);a=np.asarray(im);rgb=a[:,:,:3].astype(int);solid=a[:,:,3]>=128;visible=a[:,:,3]>0
 assert bbox(visible)[3]==464 and bbox(solid)[3]==464
 warm=solid&(rgb[:,:,0]-rgb[:,:,1]>=18)&(rgb[:,:,1]-rgb[:,:,2]>=14)&(rgb[:,:,0]>=70)
 wc=components(warm);head=wc[0];near=nearest(wc,NEAR_TARGETS[f]);far=nearest(wc,FAR_TARGETS[f]);assert near is not head and far is not head and near is not far
 knobs=[c for c in wc[1:] if c['area']>=128 and c['bbox'][3]<=head['bbox'][1] and head['bbox'][0]<=c['centroid'][0]<head['bbox'][2]]
 head_seed=head['mask'].copy()
 for c in knobs:head_seed|=c['mask']
 head_points=np.vstack([head['points_xy']]+[c['points_xy'] for c in knobs]);head_poly=hull(head_points)
 near_poly=hull(near['points_xy']);far_poly=hull(far['points_xy'])
 head_envelope=grow(polygon(head_poly),9)
 near_envelope=grow(polygon(near_poly),4)
 far_envelope=grow(polygon(far_poly),4)
 # Gray connected regions suppress torso/sleeve pixels from the head hull.
 # This is numeric segmentation, not painting or hidden-anatomy reconstruction.
 gray=solid&(np.max(rgb,axis=2)-np.min(rgb,axis=2)<=24)&(np.mean(rgb,axis=2)>=48)
 gray_major=np.zeros((512,512),bool)
 for c in components(gray):
  if c['area']>=64:gray_major|=c['mask']
 gray_neighborhood=grow(gray_major,4)
 arm_roi=polygon(ARM_ROIS[f]);arm=(gray_neighborhood&arm_roi)&~head_seed
 near_mask=near_envelope&~head_seed
 far_protect=far_envelope&visible
 helmet=head_envelope&~gray_neighborhood
 helmet|=head_seed
 labels=np.zeros((512,512),np.uint8);labels[helmet]=2;labels[arm]=1;labels[near_mask]=3;labels[head_seed]=2;labels[far_protect]=0
 masks=[labels==i for i in range(4)];assert np.array_equal(sum(m.astype(np.uint8) for m in masks),np.ones((512,512),np.uint8))
 assert np.all(labels[head_seed]==2) and np.all(labels[near['mask']]==3) and np.all(labels[far['mask']]==0)
 layers=[];receipts=[]
 for index,name in enumerate(NAMES):
  layer=np.zeros_like(a);layer[masks[index]]=a[masks[index]];layers.append(layer)
  lp=save(f'body-layers/{name}/K{f}.png',layer);mp=save(f'owner-masks/{name}/K{f}.png',(masks[index]*255).astype(np.uint8))
  assert not np.any(layer[~masks[index]]) and np.array_equal(layer[masks[index]],a[masks[index]])
  receipts.append({'owner':name,'layer':pin(lp),'binary_mask':pin(mp),'owned_coordinates':int(masks[index].sum()),'alpha_nonzero':int(np.count_nonzero(layer[:,:,3])),'alpha128':int(np.count_nonzero(layer[:,:,3]>=128)),'bbox_alpha1':bbox(layer[:,:,3]>0),'bbox_alpha128':bbox(layer[:,:,3]>=128),'inside_source_rgba_equal':True,'outside_owner_all_channels_zero':True})
 recovered=np.sum(np.stack(layers),axis=0,dtype=np.uint16).astype(np.uint8);assert np.array_equal(recovered,a)
 exact=save(f'qc/K{f}-reassembled-exact-RGBA.png',recovered)
 composite=Image.new('RGBA',(512,512))
 for name in ['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']:composite=Image.alpha_composite(composite,Image.fromarray(layers[NAMES.index(name)]))
 assert np.array_equal(premultiplied(np.asarray(composite)),premultiplied(a))
 mask_far=save(f'protection-masks/FarHandWarmHullHeuristic/K{f}.png',(far_protect*255).astype(np.uint8))
 palette=np.asarray([[70,155,230],[215,70,185],[75,190,100],[240,190,40]],np.uint8)
 visual=palette[labels].copy();visual[~visible]=[245,245,245];label_image=save(f'qc/K{f}-ownership-labels.png',visual)
 # Presentation copies retain each 512x512 tile, without any resampling.
 board=Image.new('RGB',(2560,512),(24,28,36))
 for col,tile in enumerate([a]+layers):
  bg=Image.new('RGBA',(512,512),(24,28,36,255));bg=Image.alpha_composite(bg,Image.fromarray(tile));board.paste(bg.convert('RGB'),(512*col,0))
 board_path=save(f'qc/K{f}-five-column-unscaled.png',np.asarray(board))
 hand_alpha=layers[3][:,:,3]>=128;helmet_alpha=layers[2][:,:,3]>=128
 frames.append({'frame':f,'source':pin(source),'source_raw_rgba_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'author_root':[256,464],'canvas_size':[512,512],'foot_boundary_alpha1':464,'foot_boundary_alpha128':464,'layer_receipts':receipts,
  'recipe':{'head_warm_core':summary(head),'top_knob_warm_cores':[summary(c) for c in knobs],'helmet_hull_polygon':head_poly,'helmet_envelope_Chebyshev_padding_px':9,'near_hand_warm_component':summary(near),'near_hand_hull_polygon':near_poly,'near_hand_envelope_Chebyshev_padding_px':4,'far_hand_warm_component':summary(far),'far_hand_hull_polygon':far_poly,'far_hand_envelope_Chebyshev_padding_px':4,'gray_rule':{'max_minus_min_rgb_at_most':24,'mean_rgb_at_least':48,'alpha_at_least':128,'minimum_connected_component_area':64,'gray_neighborhood_Chebyshev_padding_px':4},'near_arm_polygon_ROI':ARM_ROIS[f],'assignment_order':['BodyRest default','Helmet hull excluding gray neighborhood','NearArm gray neighborhood intersect ROI excluding head warm core','NearHand hull excluding head warm core','Restore all head warm core to HelmetForeground','Force far-hand protection to BodyRest'],'semantic_boundary_uncertainty_px':4,'semantic_accepted':False},
  'closure':{'one_owner_per_canvas_coordinate':True,'mask_values':[0,255],'owner_overlap_count':0,'visible_unowned_pixels':0,'source_rgba_mismatch_channels':0,'source_RGBA_reassembled_exact':True,'premultiplied_alpha_composite_exact':True,'alpha_sum_pixel_exact':True,'resampling':False,'translation':[0,0],'new_pixels_painted':False,'hidden_anatomy_reconstructed':False},
  'heuristic_grip_ROI':{'bbox':near['bbox'],'warm_component_centroid':near['centroid'],'polygon':near_poly,'official_GripAxis':False,'uncertainty':'Warm cluster/hull may include cuff and is NOT a measured sword grip or axis'},
  'far_hand_protection':{'mask':pin(mask_far),'all_mask_visible_pixels_in_BodyRest':True,'warm_core_pixels':far['area'],'warm_core_all_BodyRest':True,'full_hand_contour_accepted':False,'kind':'warm-component convex hull plus4px; source visible-only; heuristic, may include necessary cuff'},
  'risk':{'NearHand_Helmet_minimum_solid_owner_Chebyshev_distance_px':clearance(hand_alpha,helmet_alpha),'raw_hand_envelope_intersect_helmet_warm_core_pixels':int(np.count_nonzero(near_envelope&head_seed)),'head_warm_core_stolen_after_priority':0,'K1_hand_near_helmet_requires_Root_review':f==1,'K3_closed_hand_must_draw_after_independent_sword':f==3,'gray_sleeve_torso_boundary_and_helmet_ink_semantics':'OPEN_not_Viewed'},
  'exact_reassembled':pin(exact),'ownership_labels':pin(label_image),'unscaled_five_column_board':pin(board_path)})
proof={'schema':'request260-four-owner-source-preserving-candidate-v001','created_utc':datetime.now(timezone.utc).isoformat(),'parent260_freeze':pin(FREEZE),'frames':frames,'four_owner_names':NAMES,'future_full_stack':ORDER,'source_RGBA_reassembly_all_exact':True,'binary_onehot_masks_all_exact':True,'source_canvas_foot_root_unchanged':True,'art_generation_calls':0,'images_viewed':False,'Root_F_E_retention_of_new_derivatives':'PENDING_ROOT','armor_created':False,'sword_created':False,'official_GripAxis_proposed':False,'Source_Content_tools_E_ledger_status_modified':False,'FinalAccepted':False,'semantic_accepted':False}
write('four-owner-proof-v001.json',proof)
write('HANDOFF-v001.md','# Request260 K0–K3 four-owner candidate\n\nFinalAccepted=false; semantic_accepted=false. No images View, no art generation, no UE/Source/Content/tools/E/ledger/status writes.\n\n16 RGBA owner layers in body-layers/{BodyRest,NearArmWithoutHand,HelmetForeground,NearHand}/K0..3.png, and16 corresponding binary owner masks. Each full512 canvas coordinate has one owner; original RGBA sum and premultiplied alpha composition reconstruct source exactly. No paint, fill, translation, scaling or hidden anatomy. Foot464 and author Root256,464 unchanged.\n\nThe numeric segmentation recipe and actual hull polygons/arm ROIs are in four-owner-proof-v001.json. Helmet uses the actual bronze warm core plus top knob, a9px hull neighborhood, and suppresses connected gray cloth; sleeve uses gray neighborhood in explicit pose ROIs. NearHand uses the individual warm closed-fist hull +4px cuff/ink neighborhood, with helmet bronze core protected. Far open-hand warm hull +4px stays BodyRest, with a separate heuristic protection mask; it is NOT an accepted full hand contour.\n\nThese semantic boundaries were NOT viewed. Source pixel closure does not prove anatomical owner correctness. K1 fist/helmet separation, complete helmet dark outline, gray sleeve/torso split and K3 closed fist over the sword need Root retained visual review. No formal Grip or Axis: heuristic_grip_ROI contains only source warm-cluster bbox/centroid/polygon, never copied J markers.\n\nFuture stack: BodyRest -> ShoulderFar -> Chest -> NearArmWithoutHand -> ShoulderNear -> HelmetForeground -> IndependentSword -> NearHand. All copper head warm-core and knob pixels belong HelmetForeground; all near/far hand warm-core pixels belong NearHand/BodyRest respectively.\n\nQC exact RGBA reassembly is qc/Kx-reassembled-exact-RGBA.png. Five-column512-native diagnostic boards are source body, BodyRest, NearArmWithoutHand, HelmetForeground, NearHand on dark background, no resampling; ownership-label images show only numerical labels. Root must retain full packet F/E before View. No independent sword/armor composite is fabricated here.\n')
for _ in range(2):
 for row in dependencies:assert pin(row['path'])==row
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='four-owner-freeze-v001.json']
for _ in range(2):
 for row in members+dependencies:assert pin(row['path'])==row
freeze=write('four-owner-freeze-v001.json',{'schema':'request260-four-owner-candidate-freeze-v001','members':members,'dependency_pins':dependencies,'verification_passes':2,'twoSHA_mismatches':0,'body_layer_count':16,'owner_mask_count':16,'source_RGBA_all_exact':True,'Root_F_E_retention':'PENDING_ROOT','images_viewed':False,'semantic_accepted':False,'official_GripAxis':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(freeze),'members':len(members),'dependencies':len(dependencies),'source_RGBA_all_exact':True,'images_viewed':False,'semantic_accepted':False,'layers':[[f['frame'],[(r['owner'],r['alpha_nonzero'],r['bbox_alpha1']) for r in f['layer_receipts']]] for f in frames]},ensure_ascii=False))
