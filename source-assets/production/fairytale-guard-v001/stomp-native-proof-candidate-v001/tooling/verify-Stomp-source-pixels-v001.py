"""Fixed source optical spot proof for actual twelve single-wholebody Stomp quads.
No alignment search, art painting, frame synthesis or hidden-contact inference.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
def need(v,w):
 if not v:raise ValueError(w)
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
def verify_source_pixels(archive,rows,coverage):
 original=Path(archive)/'原件';report=json.loads((original/'runtime-report.json').read_text(encoding='utf-8-sig'));receipts=[json.loads(x)for x in(original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if x];movie=[x for x in receipts if x['file'].startswith('MovieFrame')];need(len(movie)==len(report['observations']),'Original PNG/FIFO observation count differs');results=[]
 for clip,count in [('StompWindup',6),('StompActive',2),('StompRecovery',4)]:
  for frame in range(count):
   options=[x for x in coverage if x['clip']==clip and x['frame']==frame];need(options,'Same original attack lacks optical witness');chosen=options[len(options)//2];d=chosen['draw'];i=chosen['observation'];f=rows[clip]['frames'][frame]
   source=Path(f['source']['path']);source=source if source.is_absolute()else Path('F:/Ourgame')/source
   with Image.open(source)as im:rgba=np.asarray(im.convert('RGBA'),dtype=np.float64)/255.
   need(rgba.shape==(512,512,4),'Actual source canvas differs');rgba[...,:3]=linear(rgba[...,:3]);q=dict(top=d['QuadTop'],size=d['QuadSize'],uv=d['QuadUV'],uv_size=d['QuadUVSize'],rotation=d['QuadRotationDegrees'],rotation_pivot=d['QuadRotationPivot'])
   x0=max(0,math.floor(q['top'][0])-1);x1=min(1280,math.ceil(q['top'][0]+q['size'][0])+1);y0=max(0,math.floor(q['top'][1])-1);y1=min(720,math.ceil(q['top'][1]+q['size'][1])+1);need(x1>x0 and y1>y0,'Actual native quad outside viewport');yy,xx=np.mgrid[y0:y1,x0:x1];projected=sample(rgba,q,xx,yy);tint=np.asarray(d['QuadTint']);alpha=np.clip(projected[...,3]*tint[3],0,1);color=projected[...,:3]*tint[:3]*alpha[...,None];predicted=np.rint(srgb(color)*255).astype(np.uint8)
   with Image.open(original/movie[i]['file'])as im:need(im.size==(1280,720),'Actual viewport size differs');actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
   error=np.mean(np.abs(actual.astype(float)-predicted.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(predicted,axis=-1)>=32);pixels=int(np.count_nonzero(opaque));need(pixels>=150,'Too few native source-projected opaque pixels; preserve failure');median=float(np.median(error[opaque]));good=float(np.mean(error[opaque]<=55));need(median<=40 and good>=.60,'Actual fixed-source wholebody projection unsupported; no alignment or gate edits')
   results.append(dict(clip=clip,frame=frame,original_PNG=movie[i]['file'],observation=i,native_draw_id=d['DrawId'],AttackId=d['Selection']['AttackId'],source_opaque_pixels=pixels,median_RGB_error=median,fraction_RGB_error_le55=good))
 return dict(passed=True,source_registered_native_witnesses=results,registration_search_used=False,actual_pixels_modified=False,single_wholebody_including_axe_texture_and_quad_separately_verified=True,individual_grip_bone_or_contact_or_axe_only_mask_verified=False,optical_gate='Predeclared source-opaque >=150, medianRGB<=40, fractionRGBerror<=55 >=.60; same retained Hurt body gates, no native calibration',FinalAccepted=False)
