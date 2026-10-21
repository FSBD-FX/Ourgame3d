"""Reuse the existing fixed-ROI rivet-ring method; integer translation only."""
from pathlib import Path
import argparse, datetime, hashlib, json, math, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');sys.path.insert(0,str(SG))
import sprite_gen.frames.extract as native
parser=argparse.ArgumentParser();parser.add_argument('--component',choices=['near-bracer','near-shin'],required=True)
key=parser.parse_args().component
row=json.loads((ROOT/f'handoffs/{key}-native-input-v001.json').read_text(encoding='utf-8'))['rows'][0]
run=Path(row['run_dir']);OUT=ROOT/f'{key}-registration-proposed-v002';assert not OUT.exists()
OUT.mkdir();(OUT/'registered').mkdir();(OUT/'rivet-source-crops').mkdir()
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
 assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def components(mask):
 seen=np.zeros(mask.shape,bool);result=[]
 for y,x in zip(*np.where(mask)):
  if seen[y,x]:continue
  queue=[(int(y),int(x))];seen[y,x]=True;pts=[]
  while queue:
   cy,cx=queue.pop();pts.append((cx,cy))
   for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
    ny,nx=cy+dy,cx+dx
    if 0<=ny<mask.shape[0] and 0<=nx<mask.shape[1] and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;queue.append((ny,nx))
  if len(pts)>8:
   xx=[p[0] for p in pts];yy=[p[1] for p in pts];result.append({'count':len(pts),'bbox':[min(xx),min(yy),max(xx)+1,max(yy)+1]})
 return result
manifest=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));assert manifest['ok'] and manifest['errors']==manifest['warnings']==[]
fit=manifest['rows'][0]['shared_row_fit'];raw=Path(row['raw_output_path'])
keyed=native.remove_chroma_background(Image.open(raw),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
pieces=native.extract_component_images(keyed,4);assert len(pieces)==4
roi_fraction=(.57,.22,.90,.80) if key=='near-bracer' else (.52,.08,.98,.55)
frames=[]
for i,piece in enumerate(pieces):
 assert hashlib.sha256(piece.tobytes()).hexdigest()==fit['raw_component_RGBA_sha256'][i]
 a=np.array(piece.convert('RGBA'));h,w=a.shape[:2];x0,y0,x1,y1=[int(v*n) for v,n in zip(roi_fraction,[w,h,w,h])]
 roi=a[y0:y1,x0:x1];dark=(roi[:,:,:3].mean(axis=2)<60.)&(roi[:,:,3]>=250);candidates=[]
 for c in components(dark):
  l,t,r,b=c['bbox'];cw,ch=r-l,b-t
  if l==0 or t==0 or r==dark.shape[1] or b==dark.shape[0]:continue
  if .08*w<=min(cw,ch) and max(cw,ch)<=.30*w and .70<=cw/ch<=1.30:candidates.append({**c,'bbox_component_px':[l+x0,t+y0,r+x0,b+y0]})
 assert len(candidates)==1,(key,i,candidates)
 l,t,r,b=candidates[0]['bbox_component_px'];center=[(l+r-1)/2.,(t+b-1)/2.]
 record=fit['frame_records'][i];px,py=record['placement_xy'];fw,fh=record['resampled_size']
 mapped=[px+(center[0]+.5)*fw/w-.5,py+(center[1]+.5)*fh/h-.5];A=[int(math.floor(v+.5)) for v in mapped]
 target=row['target_mounts'][i]['A'];shift=[target[j]-A[j] for j in range(2)]
 source=run/f'curated/frame-{i}.png';im=Image.open(source).convert('RGBA');bbox=im.getbbox()
 assert im.getpixel(tuple(A))[3]>=250
 assert 0<=bbox[0]+shift[0]<bbox[2]+shift[0]<=512 and 0<=bbox[1]+shift[1]<bbox[3]+shift[1]<=512
 layer=Image.new('RGBA',(512,512),(0,0,0,0));layer.paste(im,tuple(shift));assert im.crop(bbox).tobytes()==layer.crop(layer.getbbox()).tobytes()
 dest=OUT/f'registered/frame-{i}.png';layer.save(dest)
 crop=OUT/f'rivet-source-crops/frame-{i}.png';piece.crop((max(0,l-5),max(0,t-5),min(w,r+5),min(h,b+5))).save(crop)
 frames.append({'frame':i,'source':desc(source),'raw_component_size_px':[w,h],'fixed_rivet_roi_px':[x0,y0,x1,y1],
  'unique_actual_ring':candidates[0],'actual_ring_center_component_px':center,'mapped_center_frame_px':mapped,
  'A_measured_integer_px':A,'A_target_body_design_px':target,'integer_translation_px':shift,
  'registered':desc(dest),'registered_alpha_bbox_px':list(layer.getbbox()),'cropped_RGBA_byte_identical':True,
  'clipped':False,'confidence':'Actual circular dark outline center; approximately1px feature/quantization ambiguity. Pending post-E visual review.',
  'rivet_diagnostic_crop':desc(crop)})
composites=[]
if key=='near-shin':
 (OUT/'composite-preview').mkdir()
 base=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v001')
 chest=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front')
 body=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated')
 for i in range(4):
  sources=[body/f'frame-{i}.png',base/f'far150-registration-proposed-v001/armor-far/frame-{i}.png',chest/f'frame-{i}.png',
    base/f'near149-registration-proposed-v001/armor-near/frame-{i}.png',ROOT/f'near-bracer-registration-proposed-v001/registered/frame-{i}.png',OUT/f'registered/frame-{i}.png']
  im=Image.open(sources[0]).convert('RGBA')
  for p in sources[1:]:im=Image.alpha_composite(im,Image.open(p).convert('RGBA'))
  dest=OUT/f'composite-preview/frame-{i}.png';im.save(dest)
  composites.append({'frame':i,'layer_sources_in_order':[desc(p) for p in sources],'composite':desc(dest),'old151_152_layers_used':False})
write(OUT/'registration-receipt-v001.json',{'schema':'fairytale-wide-near-integer-rivet-registration-v1',
 'created_local':datetime.datetime.now().astimezone().isoformat(),'component':row['component'],'raw':desc(raw),
 'frames_manifest':desc(run/'frames/frames-manifest.json'),'shared_scale':fit['scale'],'QA_errors':manifest['errors'],'QA_warnings':manifest['warnings'],
 'method':'Existing fixed-ROI opaque dark circular rivet outline center, native component hash verified; map through exact integer shared-fit dimensions, round-half-up then integer translation. No full-plate bbox or off-center black-dot substitution, no second landmark gate.',
 'frames':frames,'composites':composites,'new_outputs_viewed':False,'no_art_redraw':True,'timing_modified':False,
 'semantic_mask_exists':False,'accepted':False,'runtime_imported':False,'formal_complete_units':0})
files=sorted(p for p in OUT.rglob('*') if p.is_file())+[Path(__file__)]
freeze=OUT/'registered-freeze-v001.json';write(freeze,{'schema':'fairytale-wide-near-registration-freeze-v1',
 'created_local':datetime.datetime.now().astimezone().isoformat(),'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),
 'files':[desc(p) for p in files],'viewed_before_root_retention':False,'accepted':False})
print(json.dumps({'freeze':desc(freeze),'files':len(files),'bytes':sum(p.stat().st_size for p in files),
 'A':[f['A_measured_integer_px'] for f in frames],'shifts':[f['integer_translation_px'] for f in frames],
 'registered_bbox':[f['registered_alpha_bbox_px'] for f in frames]},ensure_ascii=False))
