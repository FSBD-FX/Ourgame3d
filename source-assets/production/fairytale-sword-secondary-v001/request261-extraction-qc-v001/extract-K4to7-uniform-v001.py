"""Deterministic grid crop/chroma/shared627→512 scale/integer-Y alignment QC only.
No bbox-fit, per-frame scale, x translation, anatomical warp, art, armor or sword creation.
Run with sprite-gen's pinned local venv; all outputs must be NEW.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,sys
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

ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--raw-sha',required=True);ap.add_argument('--out-dir',required=True);ap.add_argument('--ready-reference',required=True);ap.add_argument('--identity-reference',required=True);ap.add_argument('--source-label',required=True);ap.add_argument('--root-decision',default='PENDING_visual_review');args=ap.parse_args()
raw=Path(args.raw).resolve();out=Path(args.out_dir).resolve();ready=Path(args.ready_reference).resolve();identity=Path(args.identity_reference).resolve()
assert raw.is_file() and pin(raw)['sha256']==args.raw_sha
assert out.is_dir() and not (out/'extraction-qc-v001.json').exists() and not (out/'extraction-freeze-v001.json').exists()
folders=('source-cells627','chroma627','uniform-resize512','aligned512','alpha512','edge-cleanup-masks512')
assert all(not (out/n).exists() for n in folders)
for n in folders:(out/n).mkdir()
inputs=[pin(raw),pin(ready),pin(identity),pin(SKILL/'sprite_gen/frames/extract.py'),pin(SKILL/'sprite_gen/_deps.py')]
im=Image.open(raw);assert im.mode=='RGB' and im.size==(1254,1254),'This version intentionally requires exact1254/2x2/627 cells; never guess requested1024'
original=np.asarray(im).copy();reconstructed=np.zeros_like(original);frames=[];S=512/627
references={}
for name,p in [('Ready',ready),('accepted_J1',identity)]:
 ref=Image.open(p);assert ref.mode=='RGBA' and ref.size==(512,512)
 a=np.asarray(ref);references[name]=dict(pin=pin(p),stats=stats(a),proxies=proxies(a))
assert references['Ready']['stats']['bbox_alpha1']==[149,49,362,464]
for local_frame in range(4):
 frame=local_frame+4
 x,y=(local_frame%2)*627,(local_frame//2)*627;box=(x,y,x+627,y+627);cell=im.crop(box);source=np.asarray(cell).copy();reconstructed[y:y+627,x:x+627]=source
 save(cell,out/'source-cells627'/f'K{frame}-source-RGB.png')
 rgba=remove_chroma_background(cell,(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=0.)
 keyed=np.asarray(rgba).copy();save(rgba,out/'chroma627'/f'K{frame}-chroma-RGBA.png')
 # One identical full-cell resample; no component/subject fitting or cell-specific scale.
 resized=rgba.resize((512,512),Image.Resampling.LANCZOS);res=np.asarray(resized).copy();save(resized,out/'uniform-resize512'/f'K{frame}-unshifted-RGBA.png')
 cleaned=res.copy();low=(cleaned[...,3]>0)&(cleaned[...,3]<=8);clear=cleaned[...,3]<=8;cleaned[clear]=0
 assert np.array_equal(cleaned[res[...,3]>8],res[res[...,3]>8])
 assert np.array_equal(cleaned[...,3]>=128,res[...,3]>=128)
 before=stats(cleaned);dy=464-before['bbox_alpha1'][3];assert before['bbox_alpha1'][1]+dy>=0 and before['bbox_alpha1'][3]+dy<=512
 aligned=np.zeros_like(cleaned);src0=max(0,-dy);src1=min(512,512-dy);aligned[src0+dy:src1+dy]=cleaned[src0:src1]
 assert int(np.sum(aligned[...,3],dtype=np.uint64))==int(np.sum(cleaned[...,3],dtype=np.uint64))
 assert bbox(aligned,1)[3]==464
 save(Image.fromarray(aligned),out/'aligned512'/f'K{frame}-body-footline464-RGBA.png');save(Image.fromarray(aligned[...,3]),out/'alpha512'/f'K{frame}-alpha.png');save(Image.fromarray(low.astype(np.uint8)*255),out/'edge-cleanup-masks512'/f'K{frame}-unshifted-low-alpha-zeroed.png')
 rgb=source.astype(np.int32);dist=np.sqrt(((rgb-np.array([255,0,255],dtype=np.int32))**2).sum(axis=-1));hard=dist<=96
 near=np.asarray(Image.fromarray(hard.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(9)))>0
 changed=np.any(keyed[...,:3]!=source,axis=-1)&(keyed[...,3]>0);deep=(~near)&(keyed[...,3]==255)
 deep_changed=int(np.count_nonzero(changed&deep));assert deep_changed==0
 box128=bbox(aligned,128);W=box128[2]-box128[0];H=box128[3]-box128[1];pr=proxies(aligned)
 def ratio(ref):
  rb=references[ref]['stats']['bbox_alpha128'];rp=references[ref]['proxies']
  return dict(solid_width_ratio=W/(rb[2]-rb[0]),solid_height_ratio=H/(rb[3]-rb[1]),lower6_span_ratio=pr['lower6_solid_span_width']/rp['lower6_solid_span_width'])
 frames.append(dict(frame=frame,raw_crop_box=list(box),raw_pixel_sha256=hashlib.sha256(source.tobytes()).hexdigest(),raw627=stats(keyed),uniform512_before_edge=stats(res),edgeclean512_before_shift=before,aligned512=stats(aligned),
 transform=dict(scale_numerator=512,scale_denominator=627,scale=S,resampler='Pillow LANCZOS RGBA premultiplied-alpha resize',source_center_mapping='source=(destination+0.5)*627/512-0.5',x_shift=0,y_integer_shift=dy,subject_bbox_fit=False,per_frame_scale=False,anatomical_warp=False),
 raw_graphic_foot_boundary_alpha1=bbox(keyed,1)[3],raw_graphic_foot_boundary_alpha128=bbox(keyed,128)[3],ideal_scaled_raw_alpha1_boundary=bbox(keyed,1)[3]*S,
 aligned_graphic_foot_boundary_alpha1=464,aligned_graphic_foot_boundary_alpha128=box128[3],raw_RGB_unmixed_foreground_pixels=int(np.count_nonzero(changed)),deep_opaque_RGB_changed=deep_changed,low_alpha_1to8_pixels_zeroed=int(np.count_nonzero(low)),opaque_footprint_unchanged_by_edgecleanup=True,alpha_mass_preserved_by_y_translation=True,
 actual_solid_width=W,actual_solid_height=H,proxies=pr,comparison_to_Ready=ratio('Ready'),comparison_to_accepted_J1=ratio('accepted_J1'),
 width_pose_or_scale_drift_warning=W>1.15*213,authored_x90_422_safe_envelope_violation=box128[0]<90 or box128[2]>422,visual_or_runtime_accepted=False))
assert np.array_equal(original,reconstructed)
for p in inputs:assert pin(p['path'])==p
report=dict(schema='request261-uniform-extraction-numeric-QC-v001',created_utc=datetime.now(timezone.utc).isoformat(),source_label=args.source_label,actual_raw_size=[1254,1254],requested_raw_size=[1254,1254],actual_grid=[2,2],actual_raw_cell=[627,627],output_cell=[512,512],
 inputs=inputs,runtime=dict(interpreter=sys.executable,python=sys.version,Pillow=PIL.__version__,numpy=np.__version__),
 crop_reassembly_RGB_pixel_exact=True,original_RGB_pixel_sha256=hashlib.sha256(original.tobytes()).hexdigest(),all_frames_same_scale=S,all_x_shifts_zero=True,only_per_frame_y_integer_translation=True,
 chroma=dict(key=[255,0,255],threshold=96.,fringe_threshold=180.,fringe_delta=18.,unmix_reach=4,spill_max_fraction=0.,deep_opaque_RGB_changed=0,verified_original_sprite_gen_primitive=True),
 edge_cleanup=dict(policy='uniform alpha1..8→RGBA0 only, no RGB/alpha change above8',alpha128_geometry_unchanged=True),
 references=references,frames=frames,technical_extraction_completed=True,technical_derivative_PNG_count=24,creative_image_generation_calls=0,images_viewed=False,armor_or_sword_drawn=False,
 Root_runtime_art_decision=args.root_decision,scale_or_anatomy_acceptance=False,physical_helmet_boot_dimensions='OPEN_heuristic_proxies_only',visual_review='PENDING_Root_after_F_E_retention',runtime_imported=False,FinalAccepted=False)
write(out/'extraction-qc-v001.json',report)
notes=['# Request261 K4to7 technical extraction QC','',f'Root decision: {args.root_decision}. Technical candidate only; not runtime/art approval.','',
 'Actual raw is1254×1254,2×2 cells627. Each full cell uses the same512/627 LANCZOS RGBA scale; no bbox-fit, variable scale, x shift or anatomical warp. Only uniform alpha1..8 cleanup then recorded integer-Y alignment of alpha>0 graphical bottom to464. Raw627 crops, chroma627, unshifted512, final512, separate alpha and cleanup masks are preserved.','',
 'Widths/heights below use alpha≥128. These are exact contours, not anatomical measurements. Helmet warm-core and lower60 components are explicit heuristics; physical helmet/boot dimensions remain OPEN.','']
for f in frames:notes.append(f"K{f['frame']}: width{f['actual_solid_width']},height{f['actual_solid_height']}; vs Ready width{f['comparison_to_Ready']['solid_width_ratio']:.4f}x; lower6 span{f['proxies']['lower6_solid_span_width']} vs Ready184; raw graphical foot boundary{f['raw_graphic_foot_boundary_alpha1']}; dy{f['transform']['y_integer_shift']}; final alpha1/128 bottoms464/{f['aligned_graphic_foot_boundary_alpha128']}.")
notes+=['','K4to7 contour metrics remain unmodified by Y alignment. Every alpha128 footprint remains unchanged by edge cleanup. No material RGB change beyond4 source pixels from keyed background. Four original RGB crops reassemble every raw pixel exactly.','',
 'No View, imagegen, new art, armor/sword drawing, actual Source/Content/tools/E/status/ledger change, import or native run. Root must preserve F/E before viewing. Candidate outputs are technical PNG derivatives, not newly generated art.','',
 'Derived from frozen259 technical pixel algorithm; only global frame names offset4 and truthful261 metadata changed. All older outputs remain immutable.']
with (out/'HANDOFF-v001.md').open('x',encoding='utf-8') as f:f.write('\n'.join(notes)+'\n')
# Small closure: all actual local outputs/script, just five exact immutable inputs.
freeze=out/'extraction-freeze-v001.json';members=[pin(p) for p in sorted(out.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
for _ in range(2):
 for p in members+inputs:assert pin(p['path'])==p
write(freeze,dict(schema='request261-uniform-extraction-QC-freeze-v001',members=members,dependency_pins=inputs,member_count=len(members),dependency_count=len(inputs),verification_passes=2,twoSHA_mismatches=0,technical_derivative_PNG_count=24,creative_image_generation_calls=0,images_viewed=False,Root_runtime_art_decision=args.root_decision,scale_or_anatomy_acceptance=False,runtime_imported=False,FinalAccepted=False))
print(json.dumps(pin(freeze)))
print(json.dumps(dict(widths=[f['actual_solid_width'] for f in frames],heights=[f['actual_solid_height'] for f in frames],y_shifts=[f['transform']['y_integer_shift'] for f in frames],lower6_spans=[f['proxies']['lower6_solid_span_width'] for f in frames],Root_runtime_art_decision=args.root_decision),ensure_ascii=False))
