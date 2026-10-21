"""Existing art plus geometric lever-radius guide, never runtime raw art."""
from pathlib import Path
import importlib.util,math,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
wc=P.parent/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json';w=r.read(wc)['weapons']['WPN-XBW-001'];weapon=Image.open(w['path']).convert('RGBA')
scale=.48;a=math.radians(-5);co=math.cos(a);si=math.sin(a);g=[224,316]
def point(p):
    x=p[0]-128;y=p[1]-253;return[g[0]+scale*(co*x-si*y),g[1]+scale*(si*x+co*y)]
render=weapon.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,128-(co*g[0]+si*g[1])/scale,-si/scale,co/scale,253-(-si*g[0]+co*g[1])/scale),resample=Image.Resampling.BICUBIC)
pivot=[192,224];handle=[137,205];targets=[]
for deg in [0,-70,-110]:
    b=math.radians(deg);x=handle[0]-pivot[0];y=handle[1]-pivot[1];targets.append(point([pivot[0]+math.cos(b)*x-math.sin(b)*y,pivot[1]+math.sin(b)*x+math.cos(b)*y]))
targets += [[300,275],[254,290],[224,316]]
sheet=Image.new('RGB',(1536,1024),(255,0,255));rows=[]
for i,target in enumerate(targets):
    src=P/'processed/call81-fixed-canvas-v001/frame-0.png';body=Image.open(src).convert('RGBA');im=body.copy();im.alpha_composite(render);d=ImageDraw.Draw(im)
    pivotbody=point(pivot);rad=math.dist(point(handle),pivotbody)
    d.ellipse((pivotbody[0]-rad,pivotbody[1]-rad,pivotbody[0]+rad,pivotbody[1]+rad),outline='cyan',width=2)
    d.ellipse((target[0]-5,target[1]-5,target[0]+5,target[1]+5),outline='red',width=2);d.line((target[0]-8,target[1],target[0]+8,target[1]),fill='red',width=1);d.line((target[0],target[1]-8,target[0],target[1]+8),fill='red',width=1)
    d.ellipse((320,316,330,326),outline='lime',width=2);d.text((25,35),f'{i}: near({target[0]:.1f},{target[1]:.1f}) support(325,321)',fill='white')
    ox=i%3*512;oy=i//3*512;sheet.paste(im,(ox,oy),im);rows.append({'index':i,'near_target_px':target,'support_target_px':[325,321],'component_lever_pivot_px':pivot,'component_handle_px':handle,'source_body':str(src),'source_body_sha256':r.sha(src)})
q=P/'references/XBW-reload-short-lever-geometry-v001.png';assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'existing_art_plus_numeric_short_lever_radius_layout_guide_not_runtime_art')
j=q.with_suffix('.json');r.write(j,{'kind':'reference_geometry_only','sheet':str(q),'sha256':r.sha(q),'scale':scale,'angle_image_clockwise_deg':-5,'frames':rows,'creative_body_art_generated':False,'limbs_transformed':False,'circle_and_marks_are_not_output_art':True});r.archive(j,j.relative_to(P),'short_lever_geometry_provenance');print(json.dumps({'path':str(q),'targets':targets,'radius_body_px':rad}))
