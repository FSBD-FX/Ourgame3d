from pathlib import Path
from collections import deque
import json
import numpy as np
from PIL import Image
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
HERE=Path(__file__).resolve().parent
SEL=HERE.parent/"K8-body-selection-v001/source-body-selection.json"
j=json.loads(SEL.read_text())
rows=[]
for f in [4,5,7]:
 p=Path(j["frames"][f]["source"]["path"]);a=np.asarray(Image.open(p));rgb=a[:,:,:3].astype(int);solid=a[:,:,3]>=128
 warm=solid&(rgb[:,:,0]-rgb[:,:,1]>=18)&(rgb[:,:,1]-rgb[:,:,2]>=14)&(rgb[:,:,0]>=70)
 gray=solid&(np.max(rgb,axis=2)-np.min(rgb,axis=2)<=24)&(np.mean(rgb,axis=2)>=48)
 rows.append({"frame":f,"source":j["frames"][f]["source"],"warm_top12":comps(warm)[:12],"gray_top12":comps(gray)[:12],"images_viewed":False,"semantic_accepted":False})
(HERE/"numeric-owner-probe-v001.json").write_text(json.dumps({"schema":"K4K5K7-owner-numeric-probe-v001","frames":rows,"images_viewed":False},indent=2)+"\n",encoding="utf-8")
print(json.dumps(rows,indent=2))
