"""Readonly seven-source optical spot check at six real distance windows.
No fit, image changes, source rendering output, phase replay or time adjustment.
The seven DTO quads are independently checked against the frozen host solver.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
def need(v,why):
 if not v:raise ValueError(why)
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def srgb(v):
 v=np.clip(v,0,1);return np.where(v<=.0031308,v*12.92,1.055*np.power(v,1/2.4)-.055)
def sample(source,q,xx,yy):
 top=np.asarray(q['top']);size=np.asarray(q['size']);pivot=top+np.asarray(q['pivot'])*size
 a=math.radians(q['rotation']);co,si=math.cos(a),math.sin(a);dx=xx+.5-pivot[0];dy=yy+.5-pivot[1]
 tx=(co*dx+si*dy+pivot[0]-top[0])/size[0];ty=(-si*dx+co*dy+pivot[1]-top[1])/size[1];valid=(tx>=0)&(tx<1)&(ty>=0)&(ty<1)
 x=np.clip((q['uv'][0]+tx*q['uv_size'][0])*512-.5,0,511);y=np.clip((q['uv'][1]+ty*q['uv_size'][1])*512-.5,0,511)
 x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);x1=np.minimum(x0+1,511);y1=np.minimum(y0+1,511);fx=(x-x0)[...,None];fy=(y-y0)[...,None]
 out=(source[y0,x0]*(1-fx)+source[y0,x1]*fx)*(1-fy)+(source[y1,x0]*(1-fx)+source[y1,x1]*fx)*fy;out[~valid]=0;return out
def verify_source_pixels(archive,profile,observations):
 original=Path(archive)/'原件';r=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'));receipts=[json.loads(x)for x in(original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if x];movies=[x for x in receipts if x['file'].startswith('MovieFrame')]
 need(len(movies)==len(r['observations']),'Original PNG/observation FIFO differs');byoffset={o['wall_offset_s']:i for i,o in enumerate(r['observations'])};need(len(byoffset)==len(movies),'Duplicate callback offset')
 sources={}
 for x in profile['source7']:
  with Image.open(x['source']['path'])as im:a=np.asarray(im.convert('RGBA'),dtype=float)/255.
  a[...,:3]=linear(a[...,:3]);sources[x['texture_object_path']]=a
 chosen=[]
 for window in range(6):
  rows=[o for o in observations if int(o['rig_draw']['cycle_position']/(128/6))==window];need(rows,'Actual distance window missing optical witness');chosen.append((window,rows[len(rows)//2]))
 results=[]
 for window,o in chosen:
  slots=o['rig_draw']['submitted_parts'];xs=[];ys=[]
  for s in slots:
   q=s['quad'];top=np.asarray(q['top']);size=np.asarray(q['size']);pivot=top+np.asarray(q['pivot'])*size;a=math.radians(q['rotation']);co,si=math.cos(a),math.sin(a)
   for uv in[(0,0),(0,1),(1,0),(1,1)]:
    p=top+np.asarray(uv)*size-pivot;xs.append(pivot[0]+co*p[0]-si*p[1]);ys.append(pivot[1]+si*p[0]+co*p[1])
  x0=max(0,int(math.floor(min(xs)))-1);x1=min(1280,int(math.ceil(max(xs)))+1);y0=max(0,int(math.floor(min(ys)))-1);y1=min(720,int(math.ceil(max(ys)))+1)
  yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);visible={}
  for s in slots:
   q=s['quad'];rgba=sample(sources[s['texture']],q,xx,yy);tint=np.asarray(q['tint']);need(np.array_equal(tint,[1,1,1,1]),'Living undamaged Guard must use white tint')
   a=rgba[...,3];color=rgba[...,:3]*a[...,None]+color*(1-a[...,None]);alpha=a+alpha*(1-a)
   for k in visible:visible[k]*=1-a
   visible[s['component']]=a
  expected=np.rint(srgb(color)*255).astype(np.uint8);i=byoffset[o['wall_offset_s']]
  with Image.open(original/movies[i]['file'])as im:need(im.size==(1280,720),'Viewport differs');actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
  error=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);count=int(np.count_nonzero(opaque));need(count>=150,'Too few actual opaque component pixels')
  median=float(np.median(error[opaque]));good=float(np.mean(error[opaque]<=55));need(median<=40 and good>=.60,'Actual source-projected Move7 pixels fail fixed conservative optical gate')
  parts=[]
  for component,mask in visible.items():
   use=opaque&(mask>=.98);n=int(np.count_nonzero(use))
   # Occlusion is explicit: no claim that a hidden source surface was seen.
   parts.append(dict(component=component,visible_opaque_pixels=n,median_RGB_error=float(np.median(error[use]))if n else None))
  results.append(dict(distance_window=window,observation=i,original_PNG=movies[i]['file'],DrawId=o['rig_draw']['draw_id'],MovementEventId=o['move_query']['movement_event'],accepted_distance=o['move_query']['accepted_distance'],body_opaque_pixels=count,body_median_RGB_error=median,body_fraction_error_le55=good,component_visibility=parts))
 return dict(passed=True,source_registered_native_witnesses=results,registration_search_used=False,actual_pixels_modified=False,all7_geometry_and_submissions_separately_required=True,footlock=False,FinalAccepted=False,optical_threshold_authority='Predeclared conservative fixed-registration gates; first native failure is retained, never fitted')
