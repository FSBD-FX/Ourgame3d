"""NEW K5 binary ownership correction. No art, relocation, View or runtime writes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
OLD=BASE/'K4K5K7-body-owner-candidate-v001';ARMOR=BASE/'K4K5K7-LGT-fit-candidate-v001'
NAMES=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']
STACK=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
POLYGON=[[175,210],[220,210],[225,219],[232,226],[231,238],[231,241],[229,247],[227,253],[227,260],[226,267],[230,274],[224,279],[215,281],[208,289],[175,300]]
def pin(p):
 p=Path(p).resolve();v=p.read_bytes();return {'path':p.as_posix(),'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def bbox(m):
 y,x=np.nonzero(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def write(rel,obj):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,a):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return p
def copy(rel,src):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(src.read_bytes())
 assert pin(p)['sha256']==pin(src)['sha256'];return p
def premul(a):return np.concatenate([a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255],axis=2)
def runs(v,offset):
 out=[]
 for x in np.where(v)[0]+offset:
  if not out or x>out[-1][1]+1:out.append([int(x),int(x)])
  else:out[-1][1]=int(x)
 return out
oldfreeze=OLD/'four-owner-freeze-v001.json';assert pin(oldfreeze)['sha256']=='f149cd1fc12d0025d5443a16be92d7aec73417d91d824389497d728e6f9ceef0'
of=read(oldfreeze)
for row in of['members']+of['dependency_pins']:assert pin(row['path'])==row
oldproof=read(OLD/'four-owner-proof-v001.json');fp=next(f for f in oldproof['frames'] if f['frame']==5)
src=Path(fp['source']['path']);assert pin(src)==fp['source'];assert pin(src)['sha256']=='88f0e001fec16e0c7481a1cfb56ebc242cf05c5c62de62ccb5dda90540e2b1e6'
a=np.asarray(Image.open(src));assert a.shape==(512,512,4);visible=a[:,:,3]>0;solid=a[:,:,3]>=128
assert bbox(visible)==[86,50,356,464] and bbox(solid)==[87,50,355,463]
oldm=[np.asarray(Image.open(OLD/f'owner-masks/{n}/K5.png'))==255 for n in NAMES]
assert np.all(np.stack(oldm).sum(0)==1)
oldlayers={n:np.asarray(Image.open(OLD/f'body-layers/{n}/K5.png')) for n in NAMES}
assert np.array_equal(np.stack(list(oldlayers.values())).sum(0,dtype=np.uint16),a.astype(np.uint16))
clipim=Image.new('L',(512,512));ImageDraw.Draw(clipim).polygon([tuple(p) for p in POLYGON],fill=255);clip=np.asarray(clipim)>0
m=[q.copy() for q in oldm];moved=oldm[1]&~clip;m[0]|=moved;m[1]&=clip
assert np.all(np.stack(m).sum(0)==1) and int(moved.sum())==1165
assert np.array_equal(m[2],oldm[2]) and np.array_equal(m[3],oldm[3])
assert np.array_equal(m[1],oldm[1]&clip) and not np.any(m[1]&~oldm[1])
far=OLD/'protection-masks/FarHandWarmHullHeuristic/K5.png';farm=np.asarray(Image.open(far))>0
assert np.all(m[0][farm])
layers={};receipts=[]
for i,n in enumerate(NAMES):
 layer=np.zeros_like(a);layer[m[i]]=a[m[i]];layers[n]=layer
 if n in ['HelmetForeground','NearHand']:
  assert np.array_equal(layer,oldlayers[n]);lp=copy(f'body-layers/{n}/K5.png',OLD/f'body-layers/{n}/K5.png');mp=copy(f'owner-masks/{n}/K5.png',OLD/f'owner-masks/{n}/K5.png')
 else:lp=save(f'body-layers/{n}/K5.png',layer);mp=save(f'owner-masks/{n}/K5.png',(m[i]*255).astype(np.uint8))
 receipts.append({'owner':n,'layer':pin(lp),'binary_mask':pin(mp),'owner_coordinates':int(m[i].sum()),'alpha1_pixels':int((layer[:,:,3]>0).sum()),'alpha128_pixels':int((layer[:,:,3]>=128).sum()),'bbox_alpha1':bbox(layer[:,:,3]>0),'bbox_alpha128':bbox(layer[:,:,3]>=128),'source_RGBA_equal_inside_mask':bool(np.array_equal(layer[m[i]],a[m[i]])),'outside_mask_all_channels_zero':bool(not np.any(layer[~m[i]])),'old_mask_and_layer_bytes_equal':n in ['HelmetForeground','NearHand']})
reassembled=np.stack(list(layers.values())).sum(0,dtype=np.uint16);assert np.array_equal(reassembled,a.astype(np.uint16))
comp=Image.new('RGBA',(512,512))
for n in NAMES:comp=Image.alpha_composite(comp,Image.fromarray(layers[n]))
assert np.array_equal(premul(np.asarray(comp)),premul(a))
reassembledp=save('qc/K5-reassembled-exact-RGBA.png',reassembled.astype(np.uint8));farp=copy('protection-masks/FarHandWarmHullHeuristic/K5.png',far)
nearprotect=copy('protection-masks/NearHandActualOwner/K5.png',OLD/'owner-masks/NearHand/K5.png')
movep=save('correction-masks/OldNearArmToBodyRest/K5.png',(moved*255).astype(np.uint8));clipp=save('correction-masks/NearArmSourceSeamClip/K5.png',(clip*255).astype(np.uint8))
labels=np.zeros((512,512),np.uint8)
for i,q in enumerate(m):labels[q]=i
palette=np.asarray([[70,155,230],[215,70,185],[75,190,100],[240,190,40]],np.uint8);color=palette[labels];color[~visible]=245
labelp=save('qc/K5-ownership-labels.png',color)
board=Image.new('RGB',(2560,512),(24,28,36))
for col,tile in enumerate([a]+[layers[n] for n in NAMES]):
 bg=Image.alpha_composite(Image.new('RGBA',(512,512),(24,28,36,255)),Image.fromarray(tile));board.paste(bg.convert('RGB'),(col*512,0))
boardp=save('qc/K5-five-column-unscaled.png',np.asarray(board))
armor={n:np.asarray(Image.open(ARMOR/f'armor-layers/{n}/K5.png')) for n in ['ShoulderFar','Chest','ShoulderNear']}
def contributions(body):
 all_layers={**body,**armor};transmit=np.ones((512,512),np.float64);out={}
 for n in reversed(STACK):
  alpha=all_layers[n][:,:,3]/255.;v=alpha*transmit
  if n in armor:out[n]={'positive_source_contribution_pixels':int((v>0).sum()),'at_least_half_contribution_pixels':int((v>=.5).sum()),'effective_alpha_sum':round(float(v.sum()),6),'positive_bbox':bbox(v>0)}
  transmit*=1-alpha
 return out
oldvis=contributions(oldlayers);newvis=contributions(layers)
assert oldvis['Chest']['positive_source_contribution_pixels']==602 and oldvis['Chest']['at_least_half_contribution_pixels']==392
assert newvis['Chest']['positive_source_contribution_pixels']==1342 and newvis['Chest']['at_least_half_contribution_pixels']==1048
assert oldvis['ShoulderNear']==newvis['ShoulderNear'] and oldvis['ShoulderFar']==newvis['ShoulderFar']
rgb=a[:,:,:3].astype(int);gray=solid&(rgb.max(2)-rgb.min(2)<=24)&(rgb.mean(2)>=48);ink=solid&(rgb.mean(2)<35)
scan=[{'y':y,'x_range_halfopen':[170,285],'gray_runs_inclusive':runs(gray[y,170:285],170),'dark_ink_runs_inclusive':runs(ink[y,170:285],170)} for y in range(214,291,3)]
scanp=write('evidence/source-gray-ink-row-runs-v002.json',{'role':'Numeric source material runs that support, but do not independently accept, the manual sleeve/chest seam. No image View performed.','gray_rule':{'alpha_min':128,'rgb_max_minus_min_max':24,'mean_rgb_min':48},'dark_ink_rule':{'alpha_min':128,'mean_rgb_lt':35},'rows':scan})
roi=np.zeros((512,512),bool);roi[235:286,236:276]=True
roi_counts={label:{n:int((mm[i]&roi&visible).sum()) for i,n in enumerate(NAMES)} for label,mm in [('old',oldm),('corrected',m)]}
visp=write('evidence/unchanged-armor-depth-contribution-v002.json',{'schema':'K5-source-owner-correction-fixed-armor-contribution-v002','formula':'Per layer: source_alpha * product(1 - alpha of every later layer), float64; positive>0, half>=0.5. Seven-layer no-sword stack.','stack':STACK,'armor_layers_unchanged_inputs':{n:pin(ARMOR/f'armor-layers/{n}/K5.png') for n in armor},'old':oldvis,'corrected':newvis,'delta_chest_positive':740,'delta_chest_half':656,'new_diagnostic_armor_assembly_produced_here':False,'armor_independent_worker_directory':(BASE/'K5-LGT-depth-correction-v002').as_posix(),'wear_fit_accepted':False})
proof={'schema':'K5-four-owner-source-seam-correction-v002','created_utc':datetime.now(timezone.utc).isoformat(),'source':pin(src),'source_raw_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'old_four_owner_freeze':pin(oldfreeze),'old_proof':pin(OLD/'four-owner-proof-v001.json'),'scope':'K5 only; restrict old NearArm owner at actual source sleeve/chest ink seam. No changes to K4/K7/260 or source art.','owners':NAMES,'canvas':[512,512],'author_root':[256,464],'foot_boundary_alpha1':464,'foot_boundary_alpha128':463,'layers':receipts,'recipe':{'method':'correctedNearArm = oldNearArm intersect manually authored source-seam clip; removed oldNearArm pixels reassigned to BodyRest; other owners byte-identical','near_arm_clip_polygon':POLYGON,'clip_mask':pin(clipp),'manual_polygon_provenance':'Root retained-View reports chest wrongly in old arm. Source gray/dark-ink numeric row runs follow boundary around x230 at y235-241, x226 at y250-262, x225 at y265-271 and the cuff upper edge near y276. Root suggested coordinates are context, not asserted measurements. This polygon is a candidate boundary, not final anatomy acceptance.','source_gray_ink_row_runs':pin(scanp),'old_arm_polygon':fp['recipe']['arm']['polygon'],'old_arm_owned_coordinates':int(oldm[1].sum()),'corrected_arm_owned_coordinates':int(m[1].sum()),'old_arm_to_BodyRest_coordinates':int(moved.sum()),'old_arm_to_BodyRest_alpha1_pixels':int((moved&visible).sum()),'old_arm_to_BodyRest_bbox_alpha1':bbox(moved&visible),'arm_newly_claimed_coordinates':0,'moved_mask':pin(movep),'source_front_chest_diagnostic_ROI_halfopen':[236,235,276,286],'front_chest_ROI_owner_counts':roi_counts,'boundary_uncertainty_source_px':3,'no_armor_target_driven_hand_cut':True},'near_hand':{'method':'preserve original K5 NearHand mask and source layer PNG bytes unchanged','old_and_new_layer':pin(OLD/'body-layers/NearHand/K5.png'),'old_and_new_mask':pin(OLD/'owner-masks/NearHand/K5.png'),'actual_owner_protection_mask':pin(nearprotect),'warm_ROI_heuristic':fp['near_hand_warm_ROI_heuristic'],'belt_pixels_reassigned':0,'reason':'No independent source-semantic evidence identifies a belt subregion inside the connected warm component. Do not relabel glove by contribution target. Original warm-hull/cuff border remains explicitly open for Root retained-View.','official_GripAxis':False,'anatomical_contour_accepted':False},'far_hand':{'mask':pin(farp),'byte_equal_old':True,'all_protected_coordinates_BodyRest':True,'heuristic_only':True,'official_GripAxis':False},'helmet':{'mask_and_layer_byte_equal_old':True,'complete_bronze_helmet_and_top_knob_pixels_unchanged':True,'semantic_status':'inherited candidate; no new acceptance claim'},'closure':{'one_owner_per_canvas_coordinate':True,'overlap_pixels':0,'unowned_coordinates':0,'all_RGBA_reconstructed_exact':True,'premultiplied_composite_exact':True,'source_RGBA_all_channels_never_painted':True,'translation':[0,0],'scale':[1,1],'resampling':False,'new_art':False},'fixed_armor_contribution_comparison':pin(visp),'exact_reassembly':pin(reassembledp),'ownership_labels':pin(labelp),'five_column_unscaled_board':pin(boardp),'images_viewed':False,'image_generation_calls':0,'Source_Content_tools_E_status_ledger_mutations':False,'Root_F_E_retention':'PENDING_ROOT','semantic_accepted':False,'wear_fit_accepted':False,'official_GripAxis':False,'runtime_ready':False,'FinalAccepted':False}
write('four-owner-proof-v002.json',proof)
write('HANDOFF-v002.md','''# K5 owner seam correction v002

Candidate only: semantic_accepted=false, wear_fit_accepted=false, runtime_ready=false, FinalAccepted=false. No View performed. Root F/E retention and review required.

Only K5 changes. K4/K7/260, all old freezes, source art, armor, Source/Content/tools/E/status/ledger remain untouched. New output: body-layers/{BodyRest,NearArmWithoutHand,HelmetForeground,NearHand}/K5.png; matching binary owner-masks. Original 512 canvas, root256,464, alpha1 foot464 and native alpha128 foot463 remain exact.

The old source-preserving arm partition incorrectly included frontal torso. correctedNearArm=oldNearArm intersect the source-ink-seam polygon recorded in proof; 1,165 original visible pixels move to BodyRest. Arm owned coordinates3,174→2,009; no new arm pixels claimed. Helmet and NearHand PNGs AND masks copied byte-for-byte. Far hand warm-hull heuristic mask copied byte-for-byte and stays in BodyRest.

NearHand remains the old warm-hull+4 candidate. No independent source-semantic evidence establishes a belt subregion inside that warm component, so no glove pixels are relabeled to force the chest visible. Warm ROI is not an official GripAxis or accepted anatomical contour. Root should inspect the cuff/chest relationship in the retained new board and unchanged-armor assembly.

The exact old seven-layer armor stack reproduces Chest positive contribution602/half392; corrected body with the same three armor PNGs gives positive1,342/half1,048 (effective alpha394.445721→1,049.622191). Both shoulder contributions unchanged. This numerical increase is not a wear/readability approval. Independent armor worker owns NEW K5-LGT-depth-correction-v002 for the actual identical-armor diagnostic reassembly.

Full onehot closure, raw RGBA sum including hiddenRGB and premultiplied alpha composite exact. No art/fill/shift/scale/warp. Numeric source gray/ink row-run evidence and moved-pixel mask are preserved for review. Board columns at native512: source, BodyRest, NearArmWithoutHand, HelmetForeground, NearHand.
''')
depfiles=[src,oldfreeze,OLD/'four-owner-proof-v001.json',ARMOR/'LGT-fit-freeze-v001.json',ARMOR/'LGT-fit-final-metrics-v001.json',far]+[OLD/f'{kind}/{n}/K5.png' for kind in ['body-layers','owner-masks'] for n in NAMES]+[ARMOR/f'armor-layers/{n}/K5.png' for n in armor]
deps=[pin(p) for p in depfiles];members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='four-owner-freeze-v002.json']
for _ in range(2):
 for r in members+deps:assert pin(r['path'])==r
freeze=write('four-owner-freeze-v002.json',{'schema':'K5-body-owner-correction-candidate-freeze-v002','members':members,'dependency_pins':deps,'verification_passes':2,'twoSHA_mismatches':0,'RGBA_exact':True,'premultiplied_exact':True,'onehot_exact':True,'new_body_layers':4,'new_owner_masks':4,'old_arm_to_BodyRest_visible_pixels':1165,'Helmet_NearHand_and_far_protect_byte_equal_old':True,'armor_PNGs_altered':False,'old_chest_contribution_positive':602,'corrected_chest_contribution_positive':1342,'new_other_K_frames':0,'images_viewed':False,'Root_F_E_retention':'PENDING_ROOT','semantic_accepted':False,'wear_fit_accepted':False,'runtime_ready':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(freeze),'members':len(members),'deps':len(deps),'source_RGBA_exact':True,'chest_before_after':[602,1342],'near_hand_unchanged':True,'moved_pixels':1165,'layers':receipts},ensure_ascii=False))
