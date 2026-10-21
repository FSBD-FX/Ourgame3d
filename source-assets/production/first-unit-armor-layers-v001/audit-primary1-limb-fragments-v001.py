"""Heuristic flagged native pixel clusters, for manual review, never acceptance."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('trace',P/'extract-primary1-LGT-v005.py');tr=importlib.util.module_from_spec(s);s.loader.exec_module(tr)
d=r.read(P/'manifests/primary1-other-armors-candidate-v004.json');rows=[]
for key,frames in d['armors'].items():
 for row in frames:
  i=row['index'];im=Image.open(row['armor_front']['path']).convert('RGBA');p=tr.POSES[i]
  guard=ImageChops.lighter(tr.mask(p['weapon_hand']),tr.mask(p['other_hand'])).filter(ImageFilter.MaxFilter(21))
  points=set()
  for y in range(512):
   for x in range(512):
    a,b,c,alpha=im.getpixel((x,y))
    if alpha and guard.getpixel((x,y)) and a>180 and b>130 and c>65 and a>b*1.15 and b>c*1.25:points.add((x,y))
  clusters=[]
  while points:
   seed=points.pop();stack=[seed];group=[seed]
   while stack:
    x,y=stack.pop()
    for n in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if n in points:points.remove(n);stack.append(n);group.append(n)
   xs=[p[0] for p in group];ys=[p[1] for p in group]
   clusters.append({'pixels':len(group),'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'sample_point':list(seed),'sample_rgba':list(im.getpixel(seed))})
  clusters=sorted(clusters,key=lambda x:x['pixels'],reverse=True)
  rows.append({'armor':key,'frame':i,'skin_color_like_clusters_in_limb_guard':clusters})
  print(key,i,clusters[:5])
f=P/'reviews/P1-limb-fragment-audit-v001.json';r.write(f,{'heuristic_only_not_semantic_truth':True,'frames':rows});r.archive(f,f.relative_to(P),'native_material_color_cluster_candidates_for_manual_review')
