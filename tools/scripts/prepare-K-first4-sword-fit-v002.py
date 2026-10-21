from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
from PIL import Image
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-sword-secondary-v001';O=C/'K0to3-marker-fit-candidate-v002';assert not O.exists();O.mkdir();(O/'source-render-only').mkdir()
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
swordpath=R/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png';assert pin(swordpath)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a';sword=Image.open(swordpath).convert('RGBA')
body=C/'request260-body-owner-candidate-v001/body-layers';armor=C/'request260-LGT-fit-candidate-v001/armor-layers';components=['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
points=[(212.,313.),(162.,180.),(163.,143.),(294.,301.)];directions=[(.94,-.341),(-.35,-.937),(-.45,-.893),(.966,-.259)];rows=[];inputs={swordpath:pin(swordpath)};pad=256
for i,(grip,v) in enumerate(zip(points,directions)):
 n=math.hypot(*v);axis=(v[0]/n,v[1]/n);near=Image.open(body/'NearHand'/f'K{i}.png').convert('RGBA');color=near.getpixel(tuple(map(int,grip)));assert color[3]>=128,(i,grip,color)
 a,b=axis[0]/.50,axis[1]/.50;d,e=-axis[1]/.50,axis[0]/.50;gx,gy=grip[0]+pad,grip[1]+pad
 coeff=(a,b,99.-a*gx-b*gy,d,e,256.-d*gx-e*gy);blade=sword.transform((1024,1024),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC)
 frame=dict(frame=i,Root=[256.,464.],Grip=list(grip),Axis=list(axis),provisional=True,axis_is_direction_design_not_measured_hidden_blade=True,Grip_pixel_RGBA=list(color),sword_source_pin=pin(swordpath),sword_source_pivot=[99.,256.],sword_scale=.50,preview_padding=[256,256],outputs=[])
 for gear in ('None','LGT'):
  canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
  for name in components:
   if name in ('ShoulderFar','Chest','ShoulderNear'):
    if gear=='None':continue
    p=armor/name/f'K{i}.png'
   else:p=body/name/f'K{i}.png'
   inputs[p]=pin(p)
   if name=='NearHand':canvas.alpha_composite(blade)
   canvas.alpha_composite(Image.open(p).convert('RGBA'),(pad,pad))
  p=O/'source-render-only'/f'K{i}-{gear}-right-source-fit.png';canvas.save(p,compress_level=6);frame['outputs'].append(pin(p))
 rows.append(frame)
p=O/'marker-proposal-source-fit-v002.json';p.write_text(json.dumps(dict(schema='Root-K-first4-independent-sword-source-fit-proposal-v002',utc=datetime.now(timezone.utc).isoformat(),frames=rows,input_pins=list(inputs.values()),scope='Source-only raster attachment preview; no UE, no runtime evidence, no style acceptance',render_method='Existing genuine layer pixels + independent genuine sword, shared .50 rigid rotation around99,256; PillowBICUBIC preview only, no source painting/fill/scale/body fitting',sword_source_size=list(sword.size),new_image_generation_calls=0,actual_runtime_imported=False,GripAxis_accepted=False,formal_complete_units=0,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for row in inputs.values():assert pin(Path(row['path']))==row
print(json.dumps(dict(proposal=pin(p),pngs=8,Grip_pixels_all_alpha_ge128=True,source_pins_unchanged=True),ensure_ascii=False))
