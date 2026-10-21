"""Only source-preserving numeric owner candidates; no View/paint/engine calls."""
from pathlib import Path
from collections import deque
from datetime import datetime,timezone
import ast,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

HERE=Path(__file__).resolve().parent;BASE=HERE.parent;PROD=BASE.parent
SELECTION=BASE/'K8-body-selection-v001/source-body-selection.json'
SELECTION_SHA='d81bf3eebfbbd3238359a61a5972ec6f16639b43461d44e00f6b4b38aa30d951'
OLD=BASE/'request260-body-owner-candidate-v001'
OLD_FREEZE=OLD/'four-owner-freeze-v001.json'
READY=PROD/'fairytale-armor-sword-ready-v002/body-partition-v002'
READY_MEASURE=PROD/'fairytale-armor-sword-ready-v002/measurement-candidate-v002.json'
NAMES=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']
ORDER=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','NearHand']
NEAR_TARGETS={4:(345,339),5:(237,313),7:(200,303)}
FAR_TARGETS={4:(140,250),5:(127,287),7:(331,324)}
ARM_ROIS={
 4:[[268,235],[292,232],[313,245],[324,265],[337,290],[342,313],[327,329],[304,322],[291,303],[280,281],[267,261]],
 5:[[196,225],[218,220],[242,232],[256,252],[258,276],[248,290],[225,291],[205,279],[190,260],[186,240]],
}
HELPERS=['pin','bbox','components','summary','nearest','hull','polygon','grow','premultiplied','clearance']
# Reuse only the frozen builder's numeric helper definitions, never its top-level
# loops/output/HERE. All new writes below are exclusively within this directory.
old_blob=(OLD/'build-four-owners-v001.py').read_bytes();old_tree=ast.parse(old_blob)
definitions=[n for n in old_tree.body if isinstance(n,ast.FunctionDef) and n.name in HELPERS]
assert len(definitions)==len(HELPERS)
exec(compile(ast.Module(body=definitions,type_ignores=[]),'<frozen260-numeric-functions-only>','exec'),globals())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,value):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f:f.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 return p
def save(name,array):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(array).save(p)
 assert np.array_equal(np.asarray(Image.open(p)),array);return p
def byte_copy(source,name):
 p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(Path(source).read_bytes())
 assert pin(p)['sha256']==pin(source)['sha256'];return p

assert pin(SELECTION)['sha256']==SELECTION_SHA
selection=read(SELECTION);assert selection['frame6_reuses0'] and selection['frame7_uses_original_ready']
assert pin(OLD_FREEZE)['sha256']=='821b2526704e99846df56d422d645a7148806dad84061d8c4188e34d92bd1b50'
old_freeze=read(OLD_FREEZE)
for row in old_freeze['members']+old_freeze['dependency_pins']:assert pin(row['path'])==row
deps=[pin(SELECTION),pin(OLD_FREEZE),pin(OLD/'build-four-owners-v001.py'),pin(READY/'proof-v001.json'),pin(READY_MEASURE),pin(BASE/'request263-single-extraction-qc-v001/single-extraction-freeze-v001.json'),pin(BASE/'request261-extraction-qc-v001/extraction-freeze-v001.json')]
ready_proof=read(READY/'proof-v001.json');ready_frame=ready_proof['frames'][0];ready_measure=read(READY_MEASURE)['frames'][0]
assert ready_proof['owner_names']==['BodyRest','NearArmWithoutHand','NearHand'],'No false existing four-owner claim'
assert ready_frame['source']['sha256']==selection['frames'][7]['source']['sha256']
ready_layer_sources={r['owner']:Path(r['file']['path']) for r in ready_frame['layers']}
ready_mask_sources={r['owner']:Path(r['file']['path']) for r in ready_frame['masks']}
for row in ready_frame['layers']+ready_frame['masks']:assert pin(row['file']['path'])==row['file'];deps.append(pin(row['file']['path']))
ready_layers={n:np.asarray(Image.open(p)) for n,p in ready_layer_sources.items()}
ready_masks={n:np.asarray(Image.open(p))==255 for n,p in ready_mask_sources.items()}
ready_master=np.asarray(Image.open(selection['frames'][7]['source']['path']))
assert np.array_equal(np.sum(np.stack(list(ready_layers.values())),axis=0,dtype=np.uint16),ready_master.astype(np.uint16))
assert np.all(np.sum(np.stack(list(ready_masks.values())),axis=0)==1)

frames=[]
for f in [4,5,7]:
 source=Path(selection['frames'][f]['source']['path']);assert pin(source)==selection['frames'][f]['source'];deps.append(pin(source))
 im=Image.open(source);assert im.mode=='RGBA' and im.size==(512,512);a=np.asarray(im);rgb=a[:,:,:3].astype(int);solid=a[:,:,3]>=128;visible=a[:,:,3]>0
 # Selected K4/K5 have native AA down to464 but solid alpha128 only to463.
 # Preserve that actual source instead of painting/moving a solid sole.
 assert bbox(visible)[3]==464
 warm=solid&(rgb[:,:,0]-rgb[:,:,1]>=18)&(rgb[:,:,1]-rgb[:,:,2]>=14)&(rgb[:,:,0]>=70)
 wc=components(warm);head=wc[0];near=nearest(wc,NEAR_TARGETS[f]);far=nearest(wc,FAR_TARGETS[f]);assert near is not head and far is not head and near is not far
 knobs=[c for c in wc[1:] if c['area']>=128 and c['bbox'][3]<=head['bbox'][1] and head['bbox'][0]<=c['centroid'][0]<head['bbox'][2]]
 head_seed=head['mask'].copy()
 for c in knobs:head_seed|=c['mask']
 hp=hull(np.vstack([head['points_xy']]+[c['points_xy'] for c in knobs]));np_=hull(near['points_xy']);fp=hull(far['points_xy'])
 head_envelope=grow(polygon(hp),9);near_envelope=grow(polygon(np_),4);far_protect=grow(polygon(fp),4)&visible
 gray=solid&(np.max(rgb,axis=2)-np.min(rgb,axis=2)<=24)&(np.mean(rgb,axis=2)>=48)
 gray_major=np.zeros((512,512),bool)
 for c in components(gray):
  if c['area']>=64:gray_major|=c['mask']
 gray_neighborhood=grow(gray_major,4);helmet=(head_envelope&~gray_neighborhood)|head_seed
 labels=np.zeros((512,512),np.uint8)
 if f==7:
  # Preserve canonical Ready arm/hand source and old manually authored masks.
  # The existing exact group has THREE owners; only its BodyRest is split.
  assert np.all(ready_masks['BodyRest'][head_seed])
  helmet&=ready_masks['BodyRest'];labels[ready_masks['NearArmWithoutHand']]=1;labels[ready_masks['NearHand']]=3;labels[helmet]=2
  arm_provenance={'method':'exact canonical Ready0 existing visible sleeve mask; not resegmented','source_mask':pin(ready_mask_sources['NearArmWithoutHand']),'source_layer':pin(ready_layer_sources['NearArmWithoutHand']),'polygon':ready_measure['candidate_near_arm_union_polygon']}
  hand_provenance={'method':'exact canonical Ready0 existing visible glove mask; not resegmented','source_mask':pin(ready_mask_sources['NearHand']),'source_layer':pin(ready_layer_sources['NearHand']),'polygon':ready_measure['candidate_near_hand_polygon']}
 else:
  arm=(gray_neighborhood&polygon(ARM_ROIS[f]))&~head_seed
  near_mask=near_envelope&~head_seed
  labels[helmet]=2;labels[arm]=1;labels[near_mask]=3;labels[head_seed]=2
  arm_provenance={'method':'gray neighborhood intersect fresh pose polygon ROI, excluding bronze core','polygon':ARM_ROIS[f]}
  hand_provenance={'method':'fresh near warm component convex hull+4px, excluding bronze head core','polygon':np_}
 labels[far_protect]=0
 masks=[labels==i for i in range(4)];assert np.all(np.sum(np.stack(masks),axis=0)==1)
 assert np.all(labels[head_seed]==2) and np.all(labels[far['mask']]==0)
 if f!=7:assert np.all(labels[near['mask']]==3)
 else:
  assert np.array_equal(masks[1],ready_masks['NearArmWithoutHand']) and np.array_equal(masks[3],ready_masks['NearHand'])
 layers=[];receipts=[]
 for i,name in enumerate(NAMES):
  layer=np.zeros_like(a);layer[masks[i]]=a[masks[i]];layers.append(layer)
  if f==7 and name in ['NearArmWithoutHand','NearHand']:
   assert np.array_equal(layer,ready_layers[name]);lp=byte_copy(ready_layer_sources[name],f'body-layers/{name}/K{f}.png');mp=byte_copy(ready_mask_sources[name],f'owner-masks/{name}/K{f}.png')
  else:lp=save(f'body-layers/{name}/K{f}.png',layer);mp=save(f'owner-masks/{name}/K{f}.png',(masks[i]*255).astype(np.uint8))
  assert np.array_equal(np.asarray(Image.open(lp)),layer)
  receipts.append({'owner':name,'layer':pin(lp),'binary_mask':pin(mp),'owned_coordinates':int(masks[i].sum()),'alpha_nonzero':int(np.count_nonzero(layer[:,:,3])),'alpha128':int(np.count_nonzero(layer[:,:,3]>=128)),'bbox_alpha1':bbox(layer[:,:,3]>0),'bbox_alpha128':bbox(layer[:,:,3]>=128),'inside_source_RGBA_equal':True,'outside_owner_all_channels_zero':bool(not np.any(layer[~masks[i]])),'existing_ready_bytes_reused':f==7 and name in ['NearArmWithoutHand','NearHand']})
 reassembled=np.sum(np.stack(layers),axis=0,dtype=np.uint16).astype(np.uint8);assert np.array_equal(reassembled,a)
 rp=save(f'qc/K{f}-reassembled-exact-RGBA.png',reassembled);composite=Image.new('RGBA',(512,512))
 for layer in layers:composite=Image.alpha_composite(composite,Image.fromarray(layer))
 assert np.array_equal(premultiplied(np.asarray(composite)),premultiplied(a))
 fp_=save(f'protection-masks/FarHandWarmHullHeuristic/K{f}.png',(far_protect*255).astype(np.uint8))
 colors=np.asarray([[70,155,230],[215,70,185],[75,190,100],[240,190,40]],np.uint8)[labels];colors[~visible]=[245,245,245];cp=save(f'qc/K{f}-ownership-labels.png',colors)
 board=Image.new('RGB',(2560,512),(24,28,36))
 for col,tile in enumerate([a]+layers):
  bg=Image.new('RGBA',(512,512),(24,28,36,255));bg=Image.alpha_composite(bg,Image.fromarray(tile));board.paste(bg.convert('RGB'),(512*col,0))
 bp=save(f'qc/K{f}-five-column-unscaled.png',np.asarray(board))
 frames.append({'frame':f,'source':pin(source),'source_raw_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'author_root':[256,464],'canvas':[512,512],'foot_boundary_alpha1':bbox(visible)[3],'foot_boundary_alpha128':bbox(solid)[3],'layer_receipts':receipts,
  'recipe':{'helmet_core':summary(head),'helmet_knob_cores':[summary(c) for c in knobs],'helmet_hull_polygon':hp,'helmet_hull_padding_px':9,'gray_rule':{'max_minus_min_rgb_at_most':24,'mean_rgb_at_least':48,'alpha_at_least':128,'minimum_connected_component_area':64,'neighborhood_Chebyshev_padding_px':4},'arm':arm_provenance,'hand':hand_provenance,'semantic_boundary_accepted':False,'boundary_uncertainty_source_px':4},
  'closure':{'one_owner_per_coordinate':True,'overlap':0,'unowned':0,'all_RGBA_reconstructed_exact':True,'premultiplied_composite_exact':True,'new_pixels_painted':False,'hidden_anatomy_reconstructed':False,'translation':[0,0],'resampling':False},
  'near_hand_warm_ROI_heuristic':{'bbox':near['bbox'],'centroid':near['centroid'],'warm_hull_polygon':np_,'warm_core_pixels':near['area'],'warm_pixels_in_NearHand':int(np.count_nonzero(near['mask']&masks[3])),'warm_pixels_elsewhere':int(np.count_nonzero(near['mask']&~masks[3])),'official_GripAxis':False,'caution':'Warm component may include leather cuff; canonical Ready hand mask remains byte-identical even if some warm cuff is outside it'},
  'far_hand_protection':{'mask':pin(fp_),'component':summary(far),'hull_polygon':fp,'padding_px':4,'warm_core_all_BodyRest':True,'mask_all_BodyRest':True,'full_contour_accepted':False,'heuristic_only':True},
  'risk':{'near_hand_helmet_min_solid_owner_Chebyshev_distance_px':clearance(layers[3][:,:,3]>=128,layers[2][:,:,3]>=128),'helmet_main_and_knob_warm_core_all_HelmetForeground':True,'complete_helmet_dark_outline_semantics':'OPEN_root_retained_View_required','gray_sleeve_torso_boundary_semantics':'OPEN_root_retained_View_required','K7_arm_hand_unchanged_source_bytes':f==7,'K7_armor_not_touched':True},
  'exact_reassembled':pin(rp),'ownership_labels':pin(cp),'unscaled_five_column_board':pin(bp)})

alias={'frame':6,'alias_frame':0,'new_body_or_masks_created':False,'parent_four_owner_freeze':pin(OLD_FREEZE),'layer_references':{n:pin(OLD/f'body-layers/{n}/K0.png') for n in NAMES},'mask_references':{n:pin(OLD/f'owner-masks/{n}/K0.png') for n in NAMES}}
write('four-owner-proof-v001.json',{'schema':'K4K5K7-source-preserving-four-owner-candidate-v001','utc':datetime.now(timezone.utc).isoformat(),'selection':pin(SELECTION),'frames':frames,'frame6_alias':alias,'four_owners':NAMES,'future_stack':ORDER,'numeric_helpers_reused_functions_only':{'source':pin(OLD/'build-four-owners-v001.py'),'functions':HELPERS,'top_level_not_executed':True},'ready_existing_group_has_three_owners':True,'existing_Ready0_source_exact_reconstruct_verified':True,'K7_existing_arm_and_hand_byte_identical':True,'new_RGBA_body_layers':12,'new_binary_owner_masks':12,'image_generation_calls':0,'images_viewed':False,'Source_Content_tools_E_status_ledger_mutations':False,'E_retention_of_new_derivatives':'PENDING_ROOT','FinalAccepted':False,'semantic_accepted':False,'official_GripAxis':False})
write('HANDOFF-v001.md','# K4/K5/K7 four-owner candidate\n\nFinalAccepted=false; semantic_accepted=false. Root selection d81bf3ee... only: K4=263 bb40889d..., K5=original261 K5 88f0e001..., K7=canonical Ready d3f76650.... No generated261 K4/K6/K7 substitution.\n\n12 RGBA layers and12 binary owner masks: body-layers/{BodyRest,NearArmWithoutHand,HelmetForeground,NearHand}/K4,K5,K7.png and owner-masks same. Every canvas coordinate has one owner; original RGBA sum and premultiplied composition are exact. 512/foot464/author Root256,464 fixed; no painting, hidden fill, shift, resampling or warp.\n\nExisting canonical Ready exact group is THREE owners, not an existing confirmed four-owner group. Its current NearArmWithoutHand and NearHand PNGs AND masks are copied byte-for-byte into K7; only the exact old BodyRest is partitioned into new BodyRest/HelmetForeground. This preserves existing Ready cuff/fist borders and master pixels, without inventing a ready four-owner acceptance.\n\nK6 is only an alias to260 K0 four-owner freeze821b2526..., with explicit references in four-owner-proof-v001.json and NO new K6 body/mask.\n\nHelmet uses source bronze core+knob hull9px and excludes connected gray cloth; fresh K4/K5 arm ROIs and hand warm hull4px are recorded as polygons. Root must retained-View complete helmet dark outline, sleeve/chest split and closed-fist contour; exact reconstruction proves pixel ownership closure, not anatomy. Hand ROI centroids are heuristic only, NOT official Grip/Axis. Canonical Ready warm component may contain cuff outside the preserved NearHand mask; raw count is disclosed, not recolored or moved.\n\nFarHandWarmHullHeuristic masks retain all their visible pixels in BodyRest; they are warm hull+4px proposals, not accepted complete far hand contours. New five-column unscaled boards are source, BodyRest, NearArm, Helmet, NearHand at512 each. No View performed; Root F/E retention required before View.\n\nFuture order BodyRest > ShoulderFar > Chest > NearArmWithoutHand > ShoulderNear > HelmetForeground > IndependentSword > NearHand. No armor/sword produced or altered. K7 canonical armor overhang belongs to the independent armor candidate and is preserved; no numeric-zero masking.\n')
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='four-owner-freeze-v001.json']
for _ in range(2):
 for r in members+deps:assert pin(r['path'])==r
freeze=write('four-owner-freeze-v001.json',{'schema':'K4K5K7-four-owner-source-candidate-freeze-v001','members':members,'dependency_pins':deps,'verification_passes':2,'twoSHA_mismatches':0,'body_layers':12,'owner_masks':12,'RGBA_all_exact':True,'K6_new_layers':0,'K7_Ready_arm_hand_byte_identical':True,'images_viewed':False,'Root_F_E_retention':'PENDING_ROOT','semantic_accepted':False,'official_GripAxis':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(freeze),'members':len(members),'dependencies':len(deps),'images_viewed':False,'RGBA_all_exact':True,'K7_arm_hand_byte_identical':True,'layers':[[f['frame'],[[r['owner'],r['bbox_alpha1']] for r in f['layer_receipts']]] for f in frames]},ensure_ascii=False))
