"""Report actual alpha components for manual semantic mask cleanup, no art edits."""
from pathlib import Path
from collections import Counter,deque
from PIL import Image
import json
P=Path(__file__).resolve().parent
im=Image.open(P/'decomposition-trials/keypose86-v002/body_far.png').convert('RGBA');alpha=im.getchannel('A');seen=set();rows=[]
for y in range(512):
 for x in range(512):
  if (x,y) in seen or not alpha.getpixel((x,y)):continue
  todo=deque([(x,y)]);seen.add((x,y));points=[]
  while todo:
   p=todo.popleft();points.append(p)
   for q in [(p[0]-1,p[1]),(p[0]+1,p[1]),(p[0],p[1]-1),(p[0],p[1]+1)]:
    if 0<=q[0]<512 and 0<=q[1]<512 and q not in seen and alpha.getpixel(q):seen.add(q);todo.append(q)
  xs=[p[0]for p in points];ys=[p[1]for p in points];rows.append({'pixels':len(points),'bbox':[min(xs),min(ys),max(xs)+1,max(ys)+1],'dominant_RGBA':Counter(im.getpixel(p)for p in points).most_common(3)})
rows.sort(key=lambda x:-x['pixels']);print(json.dumps(rows,ensure_ascii=False))
