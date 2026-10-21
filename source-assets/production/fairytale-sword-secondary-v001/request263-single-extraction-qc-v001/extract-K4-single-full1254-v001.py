"""Request263 SINGLE1254 ->512 technical extraction; no crop/bboxfit/pose normalization."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
sys.dont_write_bytecode=True
SKILL=Path('C:/Users/22499/.codex/skills/sprite-gen');sys.path.insert(0,str(SKILL))
from sprite_gen.frames.extract import remove_chroma_background,connected_components
from PIL import Image,ImageFilter
import PIL,numpy as np
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def bbox(a,threshold):
 y,x=np.nonzero(a[...,3]>=threshold)
 return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def stats(a):
 return dict(bbox_alpha1=bbox(a,1),bbox_alpha128=bbox(a,128),alpha_nonzero=int(np.count_nonzero(a[...,3])),alpha_ge128=int(np.count_nonzero(a[...,3]>=128)),soft_alpha=int(np.count_nonzero((a[...,3]>0)&(a[...,3]<255))),edge_nonzero=int(np.count_nonzero(a[0,:,3])+np.count_nonzero(a[-1,:,3])+np.count_nonzero(a[:,0,3])+np.count_nonzero(a[:,-1,3])))
def components(mask):
 rgba=np.zeros((*mask.shape,4),dtype=np.uint8);rgba[...,3]=mask.astype(np.uint8)*255
 rows=sorted(connected_components(Image.fromarray(rgba)),key=lambda x:x['area'],reverse=True)
 return [dict(area=x['area'],bbox=list(x['bbox']),width=x['bbox'][2]-x['bbox'][0],height=x['bbox'][3]-x['bbox'][1]) for x in rows]
def proxies(a):
 b=bbox(a,128);rgb=a[...,:3].astype(np.int32);yy=np.arange(a.shape[0])[:,None];solid=a[...,3]>=128
 warm=solid&(rgb[...,0]-rgb[...,1]>=18)&(rgb[...,1]-rgb[...,2]>=14)&(rgb[...,0]>=70)&(yy<b[1]+.55*(b[3]-b[1]))
 helmet=components(warm);lower=components(solid&(yy>=b[3]-60));y,x=np.nonzero(solid&(yy>=b[3]-6))
 return dict(heuristic_only=True,helmet_warm_upper55_largest3=helmet[:3],lower60_silhouette_largest2=lower[:2],lower6_solid_span=[int(x.min()),int(x.max()+1)],lower6_solid_span_width=int(x.max()+1-x.min()),lower6_pixels=len(x),physical_helmet_boot_size='OPEN_not_segmented',physical_sole_contact='OPEN_graphic_lower_contour_only')
def save(image,path):
 with path.open('xb') as f:image.save(f,format='PNG',compress_level=6,optimize=False)
def write(path,value):
 with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')


HERE=Path(__file__).resolve().parent;BASE=HERE.parent
RAW=BASE/'requests/request263-v001/raw/K4-single-corrected-raw.png'
EXPECTED={'bytes':1423628,'sha256':'1e3b07a0a80c0dd2c0774f69844ccfcaadfa3d80b3213729b20d8b4d3ac7c20c'}
REFS={'Ready':BASE/'references/ready-body-master.png','260K3':BASE/'request260-extraction-qc-v001/aligned512/K3-body-footline464-RGBA.png','261K4':BASE/'request261-extraction-qc-v001/aligned512/K4-body-footline464-RGBA.png'}
INPUTS=[RAW,*REFS.values(),BASE/'request259-extraction-qc-v001/extract-uniform-grid-qc-v001.py',SKILL/'sprite_gen/frames/extract.py',SKILL/'sprite_gen/_deps.py',BASE/'requests/request263-v001/prompt.txt',BASE/'request260-extraction-qc-v001/request260-extraction-final-freeze-v001.json',BASE/'request261-extraction-qc-v001/extraction-freeze-v001.json']
inputs=[pin(p) for p in INPUTS]
assert inputs[0]['bytes']==EXPECTED['bytes'] and inputs[0]['sha256']==EXPECTED['sha256']
def cc_centers(mask):
 z=np.zeros((*mask.shape,4),np.uint8);z[:,:,3]=mask*255
 rows=sorted(connected_components(Image.fromarray(z)),key=lambda r:r['area'],reverse=True)
 result=[]
 for r in rows[:4]:
  ys,xs=np.divmod(np.asarray(r['pixels'],dtype=np.int64),mask.shape[1]);b=list(r['bbox']);result.append({'area':r['area'],'bbox':b,'width':b[2]-b[0],'height':b[3]-b[1],'bbox_center':[(b[0]+b[2])/2,(b[1]+b[3])/2],'pixel_centroid':[float(xs.mean()),float(ys.mean())]})
 return result
def added(a):
 b=bbox(a,128);rgb=a[:,:,:3].astype(int);yy,xx=np.indices(a.shape[:2]);solid=a[:,:,3]>=128
 warm=solid&(rgb[:,:,0]-rgb[:,:,1]>=18)&(rgb[:,:,1]-rgb[:,:,2]>=14)&(rgb[:,:,0]>=70)&(yy<b[1]+.55*(b[3]-b[1]))
 head=cc_centers(warm)
 # Fixed central lower-tunic/trouser neutral-color ROI: a reference proxy, never anatomical pelvis segmentation.
 neutral=solid&(rgb.max(2)-rgb.min(2)<=35)&(rgb[:,:,0]>=30)&(rgb[:,:,0]<=170)
 pelvis_roi=(xx>=176)&(xx<336)&(yy>=304)&(yy<384)
 p=cc_centers(neutral&pelvis_roi);y,x=np.where(solid)
 return {'heuristic_only':True,'helmet_warm_upper55_components':head,'head_center_heuristic':head[0]['pixel_centroid'] if head else None,'pelvis_reference_heuristic':{'method':'Fixed x[176,336),y[304,384) neutral-color lower tunic/trouser ROI; largest4 connected components. Not anatomical pelvis or root measurement.','RGB_rule':'alpha>=128,maxRGB-minRGB<=35,30<=R<=170','components':p,'largest_component_centroid':p[0]['pixel_centroid'] if p else None,'authoring_root_fixed':[256,464],'true_anatomical_pelvis':'OPEN'},'whole_alpha128_centroid':[float(x.mean()),float(y.mean())],'whole_bbox_center':[(b[0]+b[2])/2,(b[1]+b[3])/2]}
for folder in ['source1254','chroma1254','uniform-resize512','aligned512','alpha1254','alpha512','edge-cleanup-masks512']:(HERE/folder).mkdir()
im=Image.open(RAW);assert im.mode=='RGB' and im.size==(1254,1254),'single full1254 only; never use627 grid cells'
original=np.asarray(im).copy();save(im,HERE/'source1254/K4-source-full-RGB.png')
keyed_im=remove_chroma_background(im,(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=0.)
keyed=np.asarray(keyed_im).copy();save(keyed_im,HERE/'chroma1254/K4-chroma-full-RGBA.png');save(Image.fromarray(keyed[:,:,3]),HERE/'alpha1254/K4-keyed-alpha.png')
resized=keyed_im.resize((512,512),Image.Resampling.LANCZOS);res=np.asarray(resized).copy();save(resized,HERE/'uniform-resize512/K4-unshifted-RGBA.png');save(Image.fromarray(res[:,:,3]),HERE/'alpha512/K4-unshifted-alpha.png')
cleaned=res.copy();low=(res[:,:,3]>0)&(res[:,:,3]<=8);cleaned[res[:,:,3]<=8]=0
assert np.array_equal(cleaned[res[:,:,3]>8],res[res[:,:,3]>8]);assert np.array_equal(cleaned[:,:,3]>=128,res[:,:,3]>=128)
before=stats(cleaned);dy=464-before['bbox_alpha1'][3];assert before['bbox_alpha1'][1]+dy>=0
aligned=np.zeros_like(cleaned);sy=max(0,-dy);ey=min(512,512-dy);aligned[sy+dy:ey+dy]=cleaned[sy:ey]
restored=np.zeros_like(cleaned);restored[sy:ey]=aligned[sy+dy:ey+dy];assert np.array_equal(restored,cleaned)
assert bbox(aligned,1)[3]==464
save(Image.fromarray(aligned),HERE/'aligned512/K4-body-footline464-RGBA.png');save(Image.fromarray(aligned[:,:,3]),HERE/'alpha512/K4-aligned-alpha.png');save(Image.fromarray(low.astype(np.uint8)*255),HERE/'edge-cleanup-masks512/K4-unshifted-low-alpha-zeroed.png')
low_aligned=np.zeros((512,512),np.uint8);low_aligned[sy+dy:ey+dy]=low[sy:ey]*255;save(Image.fromarray(low_aligned),HERE/'edge-cleanup-masks512/K4-aligned-low-alpha-zeroed.png')
rgb=original.astype(np.int32);dist=np.sqrt(((rgb-np.array([255,0,255]))**2).sum(-1));hard=dist<=96;near=np.asarray(Image.fromarray(hard.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9)))>0
changed=np.any(keyed[:,:,:3]!=original,axis=-1)&(keyed[:,:,3]>0);deep=(~near)&(keyed[:,:,3]==255);assert int((changed&deep).sum())==0
references={}
for name,p in REFS.items():
 ref=Image.open(p);assert ref.mode=='RGBA' and ref.size==(512,512);a=np.asarray(ref);references[name]={'pin':pin(p),'stats':stats(a),'proxies':proxies(a),'position_and_pelvis_heuristics':added(a)}
assert references['Ready']['stats']['bbox_alpha1']==[149,49,362,464]
bs=bbox(aligned,128);pr=proxies(aligned);pos=added(aligned);W=bs[2]-bs[0];H=bs[3]-bs[1]
comparisons={}
for name,r in references.items():
 rb=r['stats']['bbox_alpha128'];hp=r['position_and_pelvis_heuristics']['helmet_warm_upper55_components'][0];h=pos['helmet_warm_upper55_components'][0]
 comparisons[name]={'graphic_solid_width_ratio':W/(rb[2]-rb[0]),'graphic_solid_height_ratio':H/(rb[3]-rb[1]),'lower6_span_ratio':pr['lower6_solid_span_width']/r['proxies']['lower6_solid_span_width'],'helmet_warm_core_width_ratio':h['width']/hp['width'],'helmet_warm_core_height_ratio':h['height']/hp['height'],'helmet_warm_core_area_ratio':h['area']/hp['area'],'head_core_centroid_delta':[pos['head_center_heuristic'][i]-r['position_and_pelvis_heuristics']['head_center_heuristic'][i] for i in range(2)],'interpretation':'Contour and color-proxy comparisons only. Lower total height can reflect crouch/lean; no automatic body scale judgment.'}
frame={'frame':4,'raw_full_canvas_box':[0,0,1254,1254],'raw1254':stats(keyed),'uniform512_before_edge':stats(res),'edgeclean512_before_shift':before,'aligned512':stats(aligned),'transform':{'scale_numerator':512,'scale_denominator':1254,'scale':512/1254,'resampler':'Pillow LANCZOS RGBA premultiplied-alpha resize','source_center_mapping':'source=(destination+0.5)*1254/512-0.5','x_shift':0,'y_integer_shift':dy,'subject_bbox_fit':False,'per_component_or_pose_scale':False,'anatomical_warp':False,'crop':False},'raw_graphic_foot_boundary_alpha1':bbox(keyed,1)[3],'raw_graphic_foot_boundary_alpha128':bbox(keyed,128)[3],'final_graphic_foot_boundary_alpha1':bbox(aligned,1)[3],'final_graphic_foot_boundary_alpha128':bs[3],'actual_solid_width':W,'actual_solid_height':H,'proxies':pr,'position_and_pelvis_heuristics':pos,'comparisons':comparisons,'low_alpha_1to8_pixels_zeroed':int(low.sum()),'deep_opaque_RGB_changed':0,'inverse_y_translation_RGBA_exact':True,'alpha128_footprint_unchanged_by_cleanup':True}
report={'schema':'request263-SINGLE-full1254-uniform512-technical-QC-v001','source_label':'request263','pose_label':'K4','created_utc':datetime.now(timezone.utc).isoformat(),'inputs':inputs,'requested_raw_size':[512,512],'actual_raw_size':[1254,1254],'actual_pose_count':1,'actual_grid':None,'entire_canvas_used':True,'raw_RGB_saved_pixel_exact':bool(np.array_equal(np.array(Image.open(HERE/'source1254/K4-source-full-RGB.png')),original)),'raw_original_RGB_pixel_sha256':hashlib.sha256(original.tobytes()).hexdigest(),'runtime':{'interpreter':sys.executable,'python':sys.version,'Pillow':PIL.__version__,'numpy':np.__version__},'chroma':{'key':[255,0,255],'threshold':96.,'fringe_threshold':180.,'fringe_delta':18.,'unmix_reach':4,'spill_max_fraction':0.,'deep_opaque_RGB_changed':0},'edge_cleanup':{'policy':'uniform alpha1..8->RGBA0; all >8 unchanged','alpha128_geometry_unchanged':True},'references':references,'frame':frame,'technical_extraction_completed':True,'technical_derivative_PNG_count':9,'creative_image_generation_calls':0,'images_viewed':False,'actual_Source_Content_tools_E_status_ledger_mutations':0,'scale_or_anatomy_accepted':False,'physical_helmet_boot_pelvis_dimensions':'OPEN_heuristic_proxies_only','visual_review':'PENDING_Root_after_F_E_retention','runtime_imported':False,'FinalAccepted':False}
write(HERE/'K4-single-extraction-qc-v001.json',report)
print(json.dumps({'K4':{'bbox128':bs,'width':W,'height':H,'dy':dy,'raw_foot':bbox(keyed,1)[3],'foot6':pr['lower6_solid_span_width'],'lower60':pr['lower60_silhouette_largest2'],'helmet':pos['helmet_warm_upper55_components'][0],'pelvis_reference':pos['pelvis_reference_heuristic']['largest_component_centroid']},'refs':{k:{'bbox128':v['stats']['bbox_alpha128'],'foot6':v['proxies']['lower6_solid_span_width'],'lower60':v['proxies']['lower60_silhouette_largest2'],'helmet':v['position_and_pelvis_heuristics']['helmet_warm_upper55_components'][0],'pelvis_reference':v['position_and_pelvis_heuristics']['pelvis_reference_heuristic']['largest_component_centroid']} for k,v in references.items()}},ensure_ascii=False))
