"""Trace exact pixel-edge outer contours from FINAL NearHand alpha, never draw art."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent;PACK=HERE/'2026-10-18-closed72-final48-candidate-v002'
OUT=HERE/'2026-10-18-closed72-marker-alpha-addendum-v001'
MEDIA=Path('F:/Ourgame/过程图稿与视频/2026-10-18_Walk闭握72近手实际轮廓marker补充_v001')
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def area(poly):return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))/2
def contours(mask):
 edges=set();h,w=mask.shape
 for y,x in zip(*np.nonzero(mask)):
  x=int(x);y=int(y)
  if y==0 or not mask[y-1,x]:edges.add(((x,y),(x+1,y)))
  if x==w-1 or not mask[y,x+1]:edges.add(((x+1,y),(x+1,y+1)))
  if y==h-1 or not mask[y+1,x]:edges.add(((x+1,y+1),(x,y+1)))
  if x==0 or not mask[y,x-1]:edges.add(((x,y+1),(x,y)))
 original=len(edges);direction={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3};loops=[]
 while edges:
  start,nxt=min(edges);edge=(start,nxt);poly=[start];last=start;current=nxt;edges.remove(edge)
  while current!=start:
   poly.append(current);candidates=[v for u,v in edges if u==current];assert candidates
   d=direction[(current[0]-last[0],current[1]-last[1])]
   def rank(q):
    turn=(direction[(q[0]-current[0],q[1]-current[1])]-d)%4
    return {1:0,0:1,3:2,2:3}[turn]
   q=min(candidates,key=rank);edges.remove((current,q));last,current=current,q
  # Remove collinear vertices only; every retained edge still lies on real pixel boundaries.
  simplified=[]
  for j,b in enumerate(poly):
   a=poly[j-1];c=poly[(j+1)%len(poly)]
   if (b[0]-a[0])*(c[1]-b[1])!=(b[1]-a[1])*(c[0]-b[0]):simplified.append(list(b))
  loops.append({'points':simplified,'signed_area_px2':area(simplified),'unit_edge_count':len(poly)})
 assert sum(l['unit_edge_count'] for l in loops)==original
 return sorted(loops,key=lambda l:abs(l['signed_area_px2']),reverse=True),original

OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
marker_source=PACK/'walk-six-Grip-Axis-ground-display-markers-v001.json';base=json.loads(marker_source.read_text(encoding='utf-8'));sources=[pin(marker_source)];frames=[]
for r in base['frames']:
 i=r['frame'];p=PACK/f'import-candidate-48/BodyLayers/NearHand/frame-{i}.png';sources.append(pin(p));a=np.asarray(Image.open(p));m=a[:,:,3]>0
 loops,n=contours(m);outer=[l for l in loops if l['signed_area_px2']>0];assert outer
 first=outer[0];frames.append({**r,'FistPolygon_px':first['points'],'FistPolygon_source':pin(p),'FistPolygon_role':'EXACT largest visible NearHand alpha>0 outer boundary on source512 pixel edges. Collinear-only simplification, no fitted ellipse, rectangle, mirror or coordinate scale. Artist occlusion candidate, not a wrist/weapon collision proof.','alpha_threshold':'nonzero (>0)','all_boundary_loops':loops,'trace_unit_edge_count':n,'source_nonzero_alpha_pixels':int(m.sum()),'largest_outer_area_px2':first['signed_area_px2'],'all_outer_component_count':len(outer),'source_core128_pixels':int((a[:,:,3]>=128).sum()),'runtime_occlusion_accepted':False})
out=write(OUT/'walk-six-Grip-Axis-ground-FistPolygon-markers-v002.json',{'schema':'Walk6-actual-NearHand-visible-alpha-boundary-marker-addendum-v001','source_frozen_markers':pin(marker_source),'source_frozen48_folder':PACK.as_posix(),'frames':frames,'all_original48_unchanged':True,'image_generation_draw_resample_calls':0,'new_media_images_created':0,'final_semantic_or_runtime_acceptance':False})
for s in sources:assert pin(Path(s['path']))==s
write(OUT/'source-version-status-index-v001.json',{'date':'2026-10-18','topic':'Walk72 NearHand actual visible alpha contour markers','version':'v001','status':'data-addendum-candidate','sourcepins':sources,'output':pin(out),'frozen48_not_modified':True})
(MEDIA/'原件').mkdir(parents=True);(MEDIA/'展示副本').mkdir()
import shutil
for p in OUT.glob('*.json'):
 shutil.copyfile(p,MEDIA/'原件'/p.name);shutil.copyfile(p,MEDIA/'展示副本'/p.name)
write(MEDIA/'来源-版本-状态索引.json',{'date':'2026-10-18','topic':'Walk闭握72近手实际轮廓marker补充','version':'v001','status':'data-candidate-not-runtime-accepted','source':OUT.as_posix(),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]})
print(json.dumps({'out':pin(out),'canonical':MEDIA.as_posix(),'contour_points':[len(f['FistPolygon_px']) for f in frames],'outer_component_counts':[f['all_outer_component_count'] for f in frames],'original48_changed':False},ensure_ascii=False,indent=2))
