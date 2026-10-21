"""Candidate-only, read-only native240/241 measurements; no images emitted."""
from pathlib import Path
from collections import deque
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native
OUT=HERE/'Chest241-edit-readonly-measurement-v001';assert not OUT.exists() or not any(OUT.iterdir());OUT.mkdir(exist_ok=True)
OLD=HERE/'process-batches/2026-10-18-LGT-Dodge4-chest-correction-native240-v001/raw/leather_chest_hero_dodge_correction.png'
NEW=HERE/'process-batches/2026-10-18-LGT-Dodge4-chest-local-edit-native241-v001/raw/leather_chest_hero_dodge_correction.png'
PROOF=HERE/'Chest241-local-raw240-edit-input-v001/actual240-raw-curated-inverse-and-outside-target-proof-v001.json'
EINDEX=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-DodgeChest241-edit-native-v507/source-size-SHA256.json')
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def closed(a):
 # Writable PIL copy; flood exterior from every border seed. Regions are enclosed alpha<128 holes only.
 m=Image.fromarray(np.where(a[:,:,3]>=128,255,0).astype(np.uint8)).copy()
 for x in range(m.width):
  for y in [0,m.height-1]:
   if m.getpixel((x,y))==0:ImageDraw.floodfill(m,(x,y),128,thresh=0)
 for y in range(m.height):
  for x in [0,m.width-1]:
   if m.getpixel((x,y))==0:ImageDraw.floodfill(m,(x,y),128,thresh=0)
 rem=np.array(m)==0;parts=[]
 while rem.any():
  y,x=np.argwhere(rem)[0];q=deque([(int(y),int(x))]);rem[y,x]=False;pts=[]
  while q:
   yy,xx=q.popleft();pts.append((xx,yy))
   for ny,nx in [(yy-1,xx),(yy+1,xx),(yy,xx-1),(yy,xx+1)]:
    if 0<=ny<rem.shape[0] and 0<=nx<rem.shape[1] and rem[ny,nx]:rem[ny,nx]=False;q.append((ny,nx))
  if len(pts)>=64:
   v=np.array(pts);parts.append({'area':len(v),'centroid':v.mean(axis=0),'bbox':np.r_[v.min(axis=0),v.max(axis=0)+1]})
 parts.sort(key=lambda x:-x['area']);assert len(parts)==2
 return sorted(parts,key=lambda x:x['centroid'][0])
assert pin(OLD)['sha256']=='fde13431efe56f8922d967e632b4a53a2d7425950fda3370c871a1e833efc9cd'
assert pin(NEW)['sha256']=='d6bd73b025c5268284387f09909173412d3489b8be7a9bffe3d4ebfca03d8f78'
ix=read(EINDEX);assert ix['verification_passes']==2 and ix['source_and_target_hash_mismatches']==0
eraw=EINDEX.parent/next(x['retained_relative'] for x in ix['files'] if x['sha256']==pin(NEW)['sha256'])
for _ in range(2):assert NEW.read_bytes()==eraw.read_bytes()
proof=read(PROOF);raws=[Image.open(x).convert('RGBA') for x in [OLD,NEW]];assert all(x.size==(2172,724) for x in raws)
arrays=[np.array(x) for x in raws]
keys=[native.remove_chroma_background(x,(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005) for x in raws]
ka=[np.array(x) for x in keys]
sets=[]
for k in keys:
 seeds=sorted(sorted(native.connected_components(k),key=lambda x:x['area'],reverse=True)[:4],key=lambda x:x['center_x'])
 imgs=native.extract_component_images(k,4);assert len(imgs)==4;rs=[]
 for seed,im in zip(seeds,imgs):
  assert native.component_group_image(k,[seed]).tobytes()==im.tobytes()
  box=np.array(seed['bbox'],float);origin=box[:2]-np.array(im.getbbox()[:2]);h=closed(np.array(im))
  rs.append({'bbox':box,'holes':[{'area':p['area'],'centroid':p['centroid']+origin,'bbox':p['bbox']+np.tile(origin,2)} for p in h]})
 sets.append(rs)
def gold_buckle(a,center):
 # Deterministic local gold feature oracle, not skeleton or hidden grip inference.
 cx,cy=np.rint(center).astype(int);x0,x1=cx-70,cx+70;y0,y1=cy-45,cy+45
 crop=a[y0:y1,x0:x1].astype(int);r,g,b=crop[:,:,0],crop[:,:,1],crop[:,:,2]
 mask=(r>=135)&(g>=78)&(g<=218)&(b<=115)&(r-g>=25)&(g-b>=25)
 im=Image.fromarray(np.dstack([np.zeros((*mask.shape,3),np.uint8),np.where(mask,255,0).astype(np.uint8)]),'RGBA')
 cs=native.connected_components(im);cs=[v for v in cs if v['area']>=80]
 assert cs
 best=min(cs,key=lambda v:np.linalg.norm(np.array([v['center_x']+x0,(v['bbox'][1]+v['bbox'][3])/2+y0])-center))
 bb=np.array(best['bbox'],int);sel=mask[bb[1]:bb[3],bb[0]:bb[2]];yy,xx=np.where(sel)
 return {'area':int(best['area']),'centroid_xy':[float(xx.mean()+bb[0]+x0),float(yy.mean()+bb[1]+y0)],'bbox_xyxy':(bb+np.array([x0,y0,x0,y0])).tolist(),'method':'nearest connected gold-color feature >=80px inside fixed old buckle +/-70x45 ROI; thresholds retained; visible material feature, not bone'}
rows=[]
for i in range(4):
 sl=np.s_[:,i*543:(i+1)*543];diff=np.any(arrays[0][sl]!=arrays[1][sl],axis=2);fg=(ka[0][sl][:,:,3]>0)|(ka[1][sl][:,:,3]>0)
 row={'frame':i,'protected_cell':i in [0,3],'RGBA_pixel_identical':not bool(diff.any()),'raw240_cell_RGBA_sha256':hashlib.sha256(arrays[0][sl].tobytes()).hexdigest(),'raw241_cell_RGBA_sha256':hashlib.sha256(arrays[1][sl].tobytes()).hexdigest(),'changed_full_cell_pixels':int(diff.sum()),'full_cell_pixels':int(diff.size),'foreground_union_pixels':int(fg.sum()),'changed_foreground_union_pixels':int((diff&fg).sum()),'foreground_union_changed_fraction':float((diff&fg).sum()/fg.sum()),'raw_component_bbox240':sets[0][i]['bbox'].tolist(),'raw_component_bbox241':sets[1][i]['bbox'].tolist()}
 for n,label in enumerate(['near_armhole','neckhole']):
  o=sets[0][i]['holes'][n];v=sets[1][i]['holes'][n]
  row[label]={'raw240':{'centroid_xy':o['centroid'].tolist(),'bbox_xyxy':o['bbox'].tolist(),'area':o['area']},'raw241':{'centroid_xy':v['centroid'].tolist(),'bbox_xyxy':v['bbox'].tolist(),'area':v['area']},'raw_delta_xy':(v['centroid']-o['centroid']).tolist()}
 if i in [1,2]:
  e=proof['rows'][i]['edit'];target=np.array(e['required_raw_point_exact_PIL_inverse_xy']);actual=sets[1][i]['holes'][0]['centroid'];old=sets[0][i]['holes'][0]['centroid'];rem=actual-target
  B=np.array(e['current_buckle_raw_artist_xy_to_keep_fixed']);gold=[gold_buckle(a,B) for a in arrays];bd=np.array(gold[1]['centroid_xy'])-gold[0]['centroid_xy']
  relrem=rem-bd
  effective=np.array(proof['rows'][i]['actual_resize_effective_scale_xy'])
  row['target_comparison']={'desired_raw_centroid_xy':target.tolist(),'actual_raw_remaining_delta_xy':rem.tolist(),'actual_raw_remaining_length_px':float(np.linalg.norm(rem)),'required_raw_shift_xy':(target-old).tolist(),'actual_raw_shift_xy':(actual-old).tolist(),'achieved_required_shift_projection_fraction':float(np.dot(actual-old,target-old)/np.dot(target-old,target-old)),'old_curated_transform_DIAGNOSTIC_remaining_source_xy':(rem*effective).tolist(),'note':'old240 transform is diagnostic only; actual241 standard shared fit is separately pending; no independent per-frame scale'}
  row['fixed_buckle_visible_gold_feature']={'raw240':gold[0],'raw241':gold[1],'feature_delta_raw_xy':bd.tolist(),'artist_buckle_tracking_uncertainty_raw_px':3,'relative_armhole_to_buckle_remaining_raw_xy':relrem.tolist(),'relative_remaining_at_old_curated_density_source_xy':(relrem*effective).tolist()}
 rows.append(row)
out={'schema':'Chest241-local-edit-actual-preservation-and-targets-readonly-v001','source240':pin(OLD),'actual241':pin(NEW),'E507':pin(EINDEX),'E_raw':pin(eraw),'actual_twoSHA_equal':True,'target_proof':pin(PROOF),'installed_extractor':pin(SG/'sprite_gen/frames/extract.py'),'no_source_pixels_written':True,'no_new_media_generated':True,'rows':rows,'protected_cells_pixel_preservation_pass':all(r['RGBA_pixel_identical'] for r in rows if r['protected_cell']),'source_fit_accepted':False,'TrialAllowed':False,'FinalAccepted':False,'conclusion':'Local edit must be judged by measured geometry, not operation name; protected-cell failure remains failure. Remaining geometry at old density is diagnostic pending new shared extraction.'}
p=write(OUT/'Chest241-actual-protectedcells-fixedbuckle-aperture-target-measurement-v001.json',out)
write(OUT/'measurement-files-freeze-v001.json',{'script':pin(Path(__file__)),'files':[pin(p)],'source_read_only':True,'newmedia':False})
print(json.dumps({'report':pin(p),'protected_cells_pixel_preservation_pass':out['protected_cells_pixel_preservation_pass'],'rows':rows},ensure_ascii=False,indent=2))
