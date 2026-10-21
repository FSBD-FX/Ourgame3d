"""Readonly optical spot proof from actual PNGs + exact source RGBA + native quad arguments.
Predeclared conservative gates; no alignment search, painting, generated media or replay.
This complements exact native CRC and Root/Grip/axis quad-pixel geometry, not taste acceptance.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image

def need(v,why):
 if not v:raise ValueError(why)
def linear(rgb):return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
def srgb(rgb):
 rgb=np.clip(rgb,0.,1.);return np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055)
def sample(source,slot,xx,yy):
 top=np.asarray(slot['top']);size=np.asarray(slot['size']);pivot=top+np.asarray(slot['rotation_pivot'])*size
 a=math.radians(slot['rotation']);c,s=math.cos(a),math.sin(a)
 dx=xx+.5-pivot[0];dy=yy+.5-pivot[1]
 tx=(c*dx+s*dy+pivot[0]-top[0])/size[0];ty=(-s*dx+c*dy+pivot[1]-top[1])/size[1]
 valid=(tx>=0)&(tx<1)&(ty>=0)&(ty<1)
 x=np.clip((slot['uv'][0]+tx*slot['uv_size'][0])*512-.5,0,511);y=np.clip((slot['uv'][1]+ty*slot['uv_size'][1])*512-.5,0,511)
 x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);x1=np.minimum(x0+1,511);y1=np.minimum(y0+1,511);fx=(x-x0)[...,None];fy=(y-y0)[...,None]
 result=(source[y0,x0]*(1-fx)+source[y0,x1]*fx)*(1-fy)+(source[y1,x0]*(1-fx)+source[y1,x1]*fx)*fy
 result[~valid]=0;return result
def verify_source_pixels(archive,profile,manifest,death_observations):
 original=Path(archive)/'原件';report=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'))
 receipts=[json.loads(l)for l in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if l]
 movie=[r for r in receipts if r['file'].startswith('MovieFrame')]
 need(len(movie)==len(report['observations']),'Actual PNG FIFO must map one original observation to one movie frame')
 # The caller parsed its own JSON, so use original unique wall offsets as exact FIFO keys.
 byoffset={o['wall_offset_s']:i for i,o in enumerate(report['observations'])};need(len(byoffset)==len(movie),'Original offsets repeat')
 source_paths={r['object_path']:r['source']for r in manifest['assets']};source_paths[profile['weapon_native_texture_path']]=profile['weapon_source']['path']
 sources={}
 for name,path in source_paths.items():
  with Image.open(path)as im:rgba=np.asarray(im.convert('RGBA'),dtype=np.float64)/255.
  rgba[...,:3]=linear(rgba[...,:3]);sources[name]=rgba
 # One actual middle-in-time witness per real phase; selection changes no pixels or clock.
 chosen=[]
 for frame in range(5):
  candidates=[o for o in death_observations if o['death_draw']['frame']==frame]
  need(candidates,'Actual Death phase lacks source-pixel witness');chosen.append(candidates[len(candidates)//2])
 results=[]
 for o in chosen:
  i=byoffset[o['wall_offset_s']];d=o['death_draw'];slots=d['slots']
  # Bound by submitted quads including rotated sword, not a fitted target image.
  xs=[];ys=[]
  for slot in slots:
   if not slot['drawn']:continue
   top=np.asarray(slot['top']);size=np.asarray(slot['size']);pivot=top+np.asarray(slot['rotation_pivot'])*size;a=math.radians(slot['rotation']);c,s=math.cos(a),math.sin(a)
   for uv in [(0,0),(1,0),(0,1),(1,1)]:
    q=top+np.asarray(uv)*size-pivot;xs.append(pivot[0]+c*q[0]-s*q[1]);ys.append(pivot[1]+s*q[0]+c*q[1])
  x0=max(0,int(math.floor(min(xs)))-1);x1=min(1280,int(math.ceil(max(xs)))+1);y0=max(0,int(math.floor(min(ys)))-1);y1=min(720,int(math.ceil(max(ys)))+1)
  yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);sword_visible=np.zeros(xx.shape)
  tint=np.asarray(d['tint']);need(tint.shape==(4,)and np.all(np.isfinite(tint)),'Actual tint invalid')
  for slot in slots:
   if not slot['drawn']:continue
   rgba=sample(sources[slot['texture']],slot,xx,yy);a=np.clip(rgba[...,3]*tint[3],0,1);rgb=rgba[...,:3]*tint[:3]
   color=rgb*a[...,None]+color*(1-a[...,None]);alpha=a+alpha*(1-a)
   sword_visible=a if slot['component']==8 else sword_visible*(1-a)
  expected=np.rint(srgb(color)*255).astype(np.uint8)
  with Image.open(original/movie[i]['file'])as im:
   need(im.size==(1280,720),'Actual native viewport size differs');actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
  err=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1)
  # Opaque colored interiors avoid unknown room background and antialiased seams.
  opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);blade=(sword_visible>=.98)&(np.min(expected,axis=-1)>=45)
  body_count=int(np.count_nonzero(opaque));blade_count=int(np.count_nonzero(blade))
  need(body_count>=150 and blade_count>=8,'Too few actual source-projected opaque body/blade pixels; preserve failed native trial')
  body_median=float(np.median(err[opaque]));body_good=float(np.mean(err[opaque]<=55));blade_median=float(np.median(err[blade]));blade_good=float(np.mean(err[blade]<=65))
  need(body_median<=40 and body_good>=.60 and blade_median<=50 and blade_good>=.60,'Actual native pixels do not support source projection at fixed registration; preserve failure without alignment/tolerance edits')
  results.append({'frame':d['frame'],'original_PNG':movie[i]['file'],'native_draw_id':d['draw_id'],'body_opaque_pixels':body_count,'body_median_RGB_error':body_median,'body_fraction_RGB_error_le55':body_good,'exposed_blade_pixels':blade_count,'blade_median_RGB_error':blade_median,'blade_fraction_RGB_error_le65':blade_good})
 return {'passed':True,'source_registered_native_witnesses':results,'registration_search_used':False,'actual_pixels_modified':False,'native_quad_pixel_geometry_separately_required':True,'optical_threshold_authority':'Predeclared candidate gates, not calibrated native acceptance; failure stays failed for Root diagnosis.','FinalAccepted':False}
