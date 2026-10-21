from pathlib import Path
from collections import deque
import json,hashlib
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;SRC=HERE.parent/'request260-extraction-qc-v001'
def comps(mask):
 seen=np.zeros(mask.shape,bool);out=[]
 for y,x in zip(*np.nonzero(mask)):
  if seen[y,x]:continue
  seen[y,x]=True;q=deque([(int(y),int(x))]);pts=[]
  while q:
   a,b=q.popleft();pts.append((a,b))
   for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
    yy,xx=a+dy,b+dx
    if 0<=yy<512 and 0<=xx<512 and mask[yy,xx] and not seen[yy,xx]:seen[yy,xx]=True;q.append((yy,xx))
  p=np.asarray(pts);out.append({'area':len(pts),'bbox':[int(p[:,1].min()),int(p[:,0].min()),int(p[:,1].max()+1),int(p[:,0].max()+1)],'centroid':[float(p[:,1].mean()),float(p[:,0].mean())]})
 return sorted(out,key=lambda v:v['area'],reverse=True)
rows=[]
for f in range(4):
 p=SRC/f'aligned512/K{f}-body-footline464-RGBA.png';a=np.asarray(Image.open(p));rgb=a[:,:,:3].astype(int);solid=a[:,:,3]>=128
 warm=solid&(rgb[:,:,0]-rgb[:,:,1]>=18)&(rgb[:,:,1]-rgb[:,:,2]>=14)&(rgb[:,:,0]>=70)
 gray=solid&(np.max(rgb,axis=2)-np.min(rgb,axis=2)<=24)&(np.mean(rgb,axis=2)>=48)
 sample=[]
 for y in range(220,321,10):
  cs=[]
  for x in range(150,361,20):cs.append([x,*a[y,x].tolist()])
  sample.append({'y':y,'rgba':cs})
 rows.append({'frame':f,'warm_top12':comps(warm)[:12],'gray_top12':comps(gray)[:12],'collar_samples':sample,'heuristic_only':True,'images_viewed':False})
out={'schema':'request260-owner-numeric-probe-v001','frames':rows,'images_viewed':False,'semantic_accepted':False}
(HERE/'numeric-owner-probe-v001.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'frame':r['frame'],'warm':r['warm_top12'][:8],'gray':r['gray_top12'][:5]} for r in rows],indent=2))
