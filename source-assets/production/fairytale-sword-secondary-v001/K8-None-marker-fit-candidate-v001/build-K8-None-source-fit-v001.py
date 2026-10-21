"""Source-only K8 None five-slot attachment previews. NEW directory writes only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE.parents[2]
NAMES=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand']
SLOTS=['BodyRest','NearArmWithoutHand','HelmetForeground','IndependentSword','NearHand']
POINTS=[(212.,313.),(162.,180.),(163.,143.),(294.,301.),(363.,347.),(257.,322.),(212.,313.),(212.,313.)]
AXES=[(.94,-.341),(-.35,-.937),(-.45,-.893),(.966,-.259),(.8,.6),(.94,.341),(.94,-.341),(.94,-.341)]
PAD=256;SIZE=1024;PIVOT=(99.,256.);SCALE=.50
FREEZES={
 'first4':(BASE/'request260-body-owner-candidate-v001/four-owner-freeze-v001.json','821b2526704e99846df56d422d645a7148806dad84061d8c4188e34d92bd1b50'),
 'K4K7':(BASE/'K4K5K7-body-owner-candidate-v001/four-owner-freeze-v001.json','f149cd1fc12d0025d5443a16be92d7aec73417d91d824389497d728e6f9ceef0'),
 'K5':(BASE/'K5-body-owner-correction-v002/four-owner-freeze-v002.json','08185a5d8f0f70b5ecd0b43cdf71dbd0b809a6762a25a5e7756ee3d7b713bfe4')}
def pin(p):
 p=Path(p).resolve();v=p.read_bytes();return {'path':p.as_posix(),'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def bbox(mask):
 y,x=np.nonzero(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def premul(a):return np.concatenate([a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255],axis=2)
def write(rel,obj):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,im):
 p=HERE/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();im.save(p,compress_level=6);assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im));return p
inputs={}
def dependency(p):
 r=pin(p);inputs[r['path']]=r;return r
selectionp=BASE/'K8-body-selection-v001/source-body-selection.json';assert pin(selectionp)['sha256']=='d81bf3eebfbbd3238359a61a5972ec6f16639b43461d44e00f6b4b38aa30d951';selection=read(selectionp);dependency(selectionp)
assert len(selection['frames'])==8 and selection['frame6_reuses0'] and selection['frame7_uses_original_ready']
for key,(p,expected) in FREEZES.items():
 assert pin(p)['sha256']==expected;f=read(p);dependency(p)
 for r in f['members']+f['dependency_pins']:assert pin(r['path'])==r
first4proposal=BASE/'K0to3-marker-fit-candidate-v002/marker-proposal-source-fit-v002.json';assert pin(first4proposal)['sha256']=='088aae116f5ccdf7cbb628fa59add31d47f7803a2c1a1fffa731355c9ec6528c';dependency(first4proposal)
dependency(ROOT/'tools/scripts/prepare-K-first4-sword-fit-v002.py')
swordp=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png';assert pin(swordp)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a';dependency(swordp);sword=Image.open(swordp).convert('RGBA');swordarr=np.asarray(sword);swordbox=bbox(swordarr[:,:,3]>0)
rows=[];rights=[];lefts=[]
for i in range(8):
 src=Path(selection['frames'][i]['source']['path']);assert pin(src)==selection['frames'][i]['source'];dependency(src);raw=np.asarray(Image.open(src));assert raw.shape==(512,512,4)
 key='first4' if i in [0,1,2,3,6] else 'K5' if i==5 else 'K4K7';freeze=FREEZES[key][0];body=freeze.parent;layerframe=0 if i==6 else i
 arrays={};masks={};layerpins={};maskpins={}
 for n in NAMES:
  p=body/f'body-layers/{n}/K{layerframe}.png';mp=body/f'owner-masks/{n}/K{layerframe}.png';layerpins[n]=dependency(p);maskpins[n]=dependency(mp);arrays[n]=np.asarray(Image.open(p));mask_raw=np.asarray(Image.open(mp));assert set(np.unique(mask_raw)).issubset({0,255});masks[n]=mask_raw==255
 assert np.all(np.stack(list(masks.values())).sum(0)==1)
 assert np.array_equal(np.stack(list(arrays.values())).sum(0,dtype=np.uint16),raw.astype(np.uint16))
 source_comp=Image.new('RGBA',(512,512))
 for n in NAMES:source_comp=Image.alpha_composite(source_comp,Image.fromarray(arrays[n]))
 assert np.array_equal(premul(np.asarray(source_comp)),premul(raw))
 grip=POINTS[i];rawaxis=AXES[i];length=math.hypot(*rawaxis);assert math.isfinite(length) and length>0;axis=(rawaxis[0]/length,rawaxis[1]/length)
 assert abs(math.hypot(*axis)-1.)<1e-12
 pixel=arrays['NearHand'][int(grip[1]),int(grip[0])].tolist();assert pixel[3]>=128,(i,grip,pixel,'Grip outside genuine NearHand; no auto shift permitted')
 gx,gy=grip[0]+PAD,grip[1]+PAD;aa,bb=axis[0]/SCALE,axis[1]/SCALE;dd,ee=-axis[1]/SCALE,axis[0]/SCALE
 inverse=(aa,bb,PIVOT[0]-aa*gx-bb*gy,dd,ee,PIVOT[1]-dd*gx-ee*gy)
 blade=sword.transform((SIZE,SIZE),Image.Transform.AFFINE,inverse,resample=Image.Resampling.BICUBIC);bladea=np.asarray(blade)
 assert not bladea[0,:,3].any() and not bladea[-1,:,3].any() and not bladea[:,0,3].any() and not bladea[:,-1,3].any()
 canvas=Image.new('RGBA',(SIZE,SIZE),(0,0,0,0));prehand=None
 for n in SLOTS:
  if n=='IndependentSword':canvas.alpha_composite(blade)
  else:
   if n=='NearHand':prehand=canvas.copy()
   canvas.alpha_composite(Image.fromarray(arrays[n]),(PAD,PAD))
 righta=np.asarray(canvas);rightcrop=righta[PAD:PAD+512,PAD:PAD+512];nh=arrays['NearHand'];opaque=nh[:,:,3]==255;active=nh[:,:,3]>=128
 opaquechanged=int(np.count_nonzero(np.any(rightcrop[opaque]!=nh[opaque],axis=1)));assert opaquechanged==0
 expected=prehand.copy();expected.alpha_composite(Image.fromarray(nh),(PAD,PAD));assert np.array_equal(np.asarray(expected),righta)
 left=canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT);lefta=np.asarray(left);assert np.array_equal(lefta,righta[:,::-1]) and np.array_equal(np.asarray(left.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),righta)
 rp=save(f'source-render-only/K{i}-None-right-source-fit.png',canvas);lp=save(f'source-render-only/K{i}-None-left-mirror-preview.png',left);rights.append(righta);lefts.append(lefta)
 existing=None
 if i<4:
  prior=BASE/f'K0to3-marker-fit-candidate-v002/source-render-only/K{i}-None-right-source-fit.png';dependency(prior);priora=np.asarray(Image.open(prior));assert np.array_equal(priora,righta);existing={'prior':pin(prior),'raw_RGBA_equal':True,'different_pixels':0}
 x0,y0,x1,y1=swordbox
 def worldpoint(x,y):
  dx,dy=x-PIVOT[0],y-PIVOT[1];return [gx+SCALE*(axis[0]*dx-axis[1]*dy),gy+SCALE*(axis[1]*dx+axis[0]*dy)]
 near_sword_overlap=int(np.count_nonzero((bladea[PAD:PAD+512,PAD:PAD+512,3]>0)&(nh[:,:,3]>0)))
 rows.append({'frame':i,'alias_layer_frame':layerframe if i==6 else None,'selected_body_source':pin(src),'body_owner_freeze':pin(freeze),'source_layer_pins':layerpins,'source_mask_pins':maskpins,'Root_author':[256.,464.],'Grip_author':list(grip),'Axis_proposed_before_normalization':list(rawaxis),'Axis_unit':list(axis),'Axis_unit_length':math.hypot(*axis),'Grip_pixel_NearHand_RGBA':pixel,'Grip_inside_genuine_NearHand_alpha_ge128':True,'marker_provenance':'Root retained E667 first4 proposal088aae...' if i<4 else 'Root K6 explicit alias to actual K0' if i==6 else 'Root canonical Ready accepted marker supplied; body uses original Ready' if i==7 else 'Root supplied internal-fit proposal; no marker acceptance yet','axis_is_direction_design_not_measurement_of_unpainted_sword':True,'source_only_slot_order':SLOTS,'slot_geometry':{'body_layers_original_canvas':[512,512],'body_translation_canvas':[PAD,PAD],'body_scale':[1,1],'body_rotation_degrees':0,'preview_canvas':[SIZE,SIZE],'right_Root_canvas_author_point':[512.,720.],'right_Grip_canvas': [gx,gy],'left_raster_Grip_pixel_index':[SIZE-1-gx,gy],'left_continuous_edge_Grip_author_point':[SIZE-gx,gy],'left_raster_Root_pixel_index':[511.,720.],'left_continuous_edge_Root_author_point':[512.,720.],'left_Axis_unit':[-axis[0],axis[1]],'sword_source_pivot':list(PIVOT),'sword_uniform_scale':SCALE,'sword_angle_degrees':math.degrees(math.atan2(axis[1],axis[0])),'sword_preview_resampling':'PillowBICUBIC rigid attachment only; body layers not resampled','sword_inverse_affine_output_to_source':list(inverse),'sword_alpha1_source_bbox_corners_in_preview':[worldpoint(x0,y0),worldpoint(x1,y0),worldpoint(x1,y1),worldpoint(x0,y1)],'sword_rendered_alpha1_bbox':bbox(bladea[:,:,3]>0),'sword_touches_preview_edges':False},'closure':{'onehot_owner_masks':True,'canonical_raw_body_vs_four_owner_sum_all_RGBA_exact':True,'no_armor_no_sword_four_owner_premultiplied_reassembly_exact':True,'source_RGBA_painted':False,'body_shift_or_scale':False,'no_source_gap_filled':True},'near_hand_protection':{'actual_owner_mask':maskpins['NearHand'],'NearHand_drawn_after_independent_sword':True,'opaque_NearHand_source_pixels':int(opaque.sum()),'opaque_NearHand_final_RGBA_changed_pixels':opaquechanged,'alpha_ge128_final_vs_source_RGBA_changed_pixels':int(np.count_nonzero(np.any(rightcrop[active]!=nh[active],axis=1))),'semi_transparent_AA_note':'RGBA can change when a source alpha<255 edge is composited above the sword; exact original late-hand alpha compositing is verified, never erase sword by painting hand.','sword_and_NearHand_alpha1_overlap_pixels':near_sword_overlap,'complete_late_hand_alpha_composite_RGBA_exact':True},'prior_first4_right_preview_comparison':existing,'right_output':pin(rp),'left_output':pin(lp),'left_technical_preview_only':True,'left_mirror_operations':1,'left_entire_geometry_mirror_exact':True,'actual_UE_mirror_proven':False,'FinalAccepted':False})
assert np.array_equal(rights[6],rights[0]) and np.array_equal(lefts[6],lefts[0])
proof=write('marker-source-fit-proof-v001.json',{'schema':'K8-None-five-slot-genuine-source-marker-fit-candidate-v001','utc':datetime.now(timezone.utc).isoformat(),'selection':pin(selectionp),'frames':rows,'sword':{'source':pin(swordp),'canvas':list(sword.size),'source_alpha1_bbox':swordbox,'pivot':list(PIVOT),'scale':SCALE},'all8_Grip_inside_real_NearHand_alpha_ge128':True,'all8_axes_normalized':True,'all8_body_exact_source_reconstruction':True,'K6_references_actual_K0_layers_and_both_outputs_raw_RGBA_equal':True,'new_PNG_outputs':16,'preview_canvas':[SIZE,SIZE],'source_body_scale':[1,1],'padding':[PAD,PAD],'five_slots':SLOTS,'left_method':'Exactly one complete rendered-right-image horizontal transpose. Raster pixel indices xLeft=1023-xRight; continuous image edge author points xLeft=1024-xRight. No per-slot mirroring or hand/sword repaint.','left_UE_runtime_mirror_evidence':False,'new_art_generation_calls':0,'images_viewed':False,'actual_Source_Content_tools_E_status_ledger_mutated':False,'E_retention':'PENDING_ROOT','runtime_imported':False,'runtime_ready':False,'GripAxis_accepted':False,'semantic_style_wear_accepted':False,'FinalAccepted':False})
write('HANDOFF-v001.md','''# K8 None source-only marker and sword fit

16 native-size source preview PNGs in source-render-only: K0..K7-None-right-source-fit.png and K0..K7-None-left-mirror-preview.png. Canvas1024×1024, source512×512 placed at256,256 without scaling or rotation. None five slots: BodyRest→NearArmWithoutHand→HelmetForeground→IndependentSword→NearHand.

Exact source selection d81bf3ee...; K0..3 use260 freeze821b2526..., K4/K7 use f149cd1f..., K5 uses corrected owner08185a5d..., K6 references K0. All source RGBA including hiddenRGB reconstructs exactly from onehot owners; no-sword alpha composition equals canonical body in premultiplied RGBA. K6 images equal K0 in both facings. First4 right PNG pixels equal Root proposal088aae... exactly.

All 8 supplied Grips are retained at the requested coordinates and land on actual NearHand alpha255; all proposed axes normalized. K4(363,347)/(.8,.6), K5(257,322)/(.94,.341) remain internal proposals. K7 original Ready uses Root supplied original accepted(212,313)/(.94,-.341). Axis is designed sword direction, not a measurement of an unpainted blade. No marker silently moved.

Military sword source SHA2efb5519..., pivot99,256, uniform.50. Original source unchanged; only the independent sword receives PillowBICUBIC rigid preview transform. Every frame records source pins, 5-slot geometry, inverse affine, source support corners, real hand grip pixel, sword/hand overlap and hand protection. Source opaque hand pixels remain exact; source partially transparent AA pixels are composited honestly over sword, not painted opaque.

Left images are technical previews produced by exactly one full assembled-right transpose. Raster pixel index x'=1023-x; continuous image-edge author points x'=1024-x. This is not UE runtime mirror proof. Both conventions are explicit in the geometry data.

No View, no UE launch/import, no generation, no armor, GIF or video, no actual Source/Content/tools/E/status/ledger mutation. Root F/E retention and retained-View required. runtime_ready=false, GripAxis_accepted=false, semantic_style_wear_accepted=false, FinalAccepted=false; internal fit only.
''')
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='marker-fit-freeze-v001.json'];deps=list(inputs.values())
for _ in range(2):
 for r in members+deps:assert pin(r['path'])==r
fp=write('marker-fit-freeze-v001.json',{'schema':'K8-None-marker-fit-unadmitted-candidate-freeze-v001','members':members,'dependency_pins':deps,'verification_passes':2,'twoSHA_mismatches':0,'pngs':16,'body_RGBA_all_exact':True,'all8_Grip_real_NearHand_alpha_ge128':True,'all8_axes_normalized':True,'opaque_NearHand_final_RGBA_changed_pixels_all8':0,'K6_alias0_raw_outputs_exact':True,'first4_right_raw_RGBA_equal_prior':True,'left_full_render_mirrored_once':True,'left_actual_UE_proof':False,'images_viewed':False,'E_retention':'PENDING_ROOT','runtime_ready':False,'GripAxis_accepted':False,'FinalAccepted':False})
print(json.dumps({'freeze':pin(fp),'proof':pin(proof),'members':len(members),'dependencies':len(deps),'pngs':16,'grip_alphas':[r['Grip_pixel_NearHand_RGBA'][3] for r in rows],'opaque_hand_changed':[r['near_hand_protection']['opaque_NearHand_final_RGBA_changed_pixels'] for r in rows],'AA_hand_changed':[r['near_hand_protection']['alpha_ge128_final_vs_source_RGBA_changed_pixels'] for r in rows]},ensure_ascii=False))
