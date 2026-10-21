"""Source-only native157 diagnostics. Unscaled crops and visible boot pixels only."""
from pathlib import Path
import datetime, hashlib, json
from PIL import Image
R=Path(__file__).resolve().parent;out=R/'primary1-measurement-v002';assert not out.exists();out.mkdir()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def foot(im,roi):
 a=im.getchannel('A');x0,y0,x1,y1=roi
 ys=[y for y in range(y0,y1) if any(a.getpixel((x,y))>=128 for x in range(x0,x1))];last=max(ys)
 xs=[x for x in range(x0,x1) if a.getpixel((x,last))>=128]
 return {'roi_px':roi,'alpha_threshold':128,'last_contact_pixel_y':last,'span_inclusive_px':[min(xs),max(xs)],'center_x':(min(xs)+max(xs))/2,'boundary_below_pixel_y':last+1,'meaning':'Visible sole edge only, excluding no hidden inferred foot.'}
handrois=[[218,247,286,313],[164,94,235,174],[250,231,323,296],[285,283,389,375],[218,247,286,313],[218,247,286,313]]
rows=[]
for i in range(6):
 p=R/'run-primary1-v002/curated'/f'frame-{i}.png';im=Image.open(p).convert('RGBA')
 crops=[]
 for role,roi in [('near_hand_and_local_occlusion',handrois[i]),('feet',[128,420,386,465])]:
  q=out/f'frame-{i}-{role}-diagnostic.png';im.crop(roi).save(q)
  crops.append({'role':role,'roi_px':roi,'file':desc(q),'resampled':False,'art_asset':False})
 near=foot(im,[128,430,230,464]);far=foot(im,[250,430,386,464])
 rows.append({'frame':i,'source':desc(p),'diagnostic_crops':crops,'near_boot':near,'far_boot':far,
              'dual_visible_contact_center_x':(near['center_x']+far['center_x'])/2,
              'display_pivot_design_px':[256,464],'grip_actual_px':None,'axis_actual_xy':None,'polygon':None,
              'status':'Await E-retained crop review. Do not turn planned grip or fixed display pivot into measured physical facts.'})
q=out/'pixel-evidence-v001.json';q.write_text(json.dumps({'schema':'fairytale-primary1-native157-readonly-diagnostics-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'frames':rows,'new_diagnostics_viewed':False,'images_modified':False,'ue_called':False,'native_called':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=sorted(out.iterdir())+[Path(__file__).resolve()]
f=out/'diagnostic-freeze-v001.json';f.write_text(json.dumps({'file_count':len(files),'total_bytes':sum(x.stat().st_size for x in files),'files':[desc(x) for x in files],'new_diagnostics_viewed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'freeze':desc(f),'feet':[{'frame':r['frame'],'near':r['near_boot'],'far':r['far_boot'],'mean_x':r['dual_visible_contact_center_x']} for r in rows]},ensure_ascii=False))
