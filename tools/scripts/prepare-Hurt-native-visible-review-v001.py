"""Retain real native samples and compare both facings/adjacent joins with crops only."""
from pathlib import Path
import json,math,hashlib,shutil
from PIL import Image,ImageDraw
R=Path('F:/Ourgame');O=R/'过程图稿与视频/2026-10-18_钟盔轻甲受击双侧八相与回接实景对照_v001'
assert not O.exists();(O/'原件').mkdir(parents=True);(O/'展示副本').mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
items=[];joinrows=[];crops=[]
def get(side,x,report):
 p=Path(x['presentation']['path']);assert p.stat().st_size==x['presentation']['bytes'] and sha(p)==x['presentation']['sha256']
 q=O/'原件'/(side+'-'+p.name);assert not q.exists();shutil.copy2(p,q);assert sha(q)==sha(p)
 obs=report['observations'][x['observation']];g=obs['ground'];c=obs['camera_ground']
 gx,gy=640+(g[0]-c[0])*.65,490-g[1]*.38
 if obs['hurt_draw']['drawn']:
  actual=obs['hurt_draw']['context_ground'];assert abs(actual[0]-gx)<.001 and abs(actual[1]-gy)<.001
 rect=[math.floor(gx)-150,math.floor(gy)-184,math.floor(gx)+150,math.floor(gy)+80]
 crops.append(dict(side=side,observation=x['observation'],original=p.as_posix(),copy=q.name,crop_rect=rect,pixels_edited=False))
 return Image.open(q).convert('RGB').crop(rect)
for side,label in [('left','L'),('right','R')]:
 A=R/('过程图稿与视频/2026-10-18_钟盔轻甲真实受击与回接'+('左' if side=='left' else '右')+'侧实录_v001')
 i=read(A/'source-version-status-index.json');r=read(Path(i['native_bindings']['report']['path']))
 assert len(i['samples'])==4 and len(i['joins'])==2
 for x in i['samples']:items.append((f'{label} Hurt{x["frame"]} n{x["observation"]} age{x["actual_query"]["elapsed"]:.3f}',get(side,x,r)))
 for j in i['joins']:
  pair=[]
  for n,x in enumerate(j['pair']):pair.append((f'{label} {j["join"]} {"before" if n==0 else "after"} n{x["observation"]}',get(side,x,r)))
  joinrows.append(pair)
def plate(name,rows,columns):
 out=Image.new('RGB',(300*columns,288*math.ceil(len(rows)/columns)),(24,28,32));draw=ImageDraw.Draw(out)
 for n,(label,im) in enumerate(rows):
  x,y=(n%columns)*300,(n//columns)*288;out.paste(im,(x,y+24));draw.text((x+4,y+6),label,fill='white')
 out.save(O/'展示副本'/(name+'-1x.png'))
 out.resize((out.width*2,out.height*2),Image.Resampling.NEAREST).save(O/'展示副本'/(name+'-2x-nearest.png'))
plate('Hurt4-both-sides-native',items,4)
plate('Hurt-Ready-Walk-both-sides-adjacent-native',[j[s] for s in [0,1] for j in joinrows],4)
files=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.rglob('*')) if p.is_file()]
(O/'index.json').write_text(json.dumps(dict(schema='Root-Hurt4-both-sides-native-visual-crops-v001',files=files,crops=crops,originals=16,integer_nearest_presentation_only=True,visual_reviewed=False,FinalAccepted=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('# 钟盔轻甲受击双侧八相与真实回接 v001\n\n左右各四张原受击相，以及各两组严格相邻Hurt3→Ready/Ready→Walk，按真实主角地面投影裁图、2倍最近邻放大。16张原尺寸副本保持源SHA。没有修姿态像素、补帧或改时间；需先F/E保全再Root查看，不作最终美术/足锁/音效结论。\n',encoding='utf-8')
print(json.dumps(dict(output=O.as_posix(),files=len(files)+2,originals=16,plates=4,bytes=sum(p.stat().st_size for p in O.rglob('*') if p.is_file()))))
