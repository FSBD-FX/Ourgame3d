"""Copy retained real native samples and make labelled crops only; no asset editing."""
from pathlib import Path
import json,hashlib,shutil,math
from PIL import Image,ImageDraw
R=Path('F:/Ourgame');A=R/'过程图稿与视频/2026-10-18_石守卫正常军剑死亡与自动金币试样_native_left_v001'
O=R/'过程图稿与视频/2026-10-18_守卫正常死亡六相与五处相邻转场实景对照_v001'
assert not O.exists();(O/'原件').mkdir(parents=True);(O/'展示副本').mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
i=read(A/'source-version-status-index.json');r=read(A/'原件/runtime-report.json')
assert i['required_sample_count']==6 and i['required_adjacent_join_count']==5
copied=[];crops=[]
def original(x):
 p=Path(x['presentation']['path']);assert p.stat().st_size==x['presentation']['bytes'] and sha(p)==x['presentation']['sha256']
 q=O/'原件'/p.name;shutil.copy2(p,q);copied.append(q)
 d=r['observations'][x['frame_index']]['guard_draws'][0];gx,gy=d['GroundScreen']
 box=[math.floor(gx)-150,math.floor(gy)-184,math.floor(gx)+150,math.floor(gy)+80]
 crops.append(dict(native_frame=x['frame_index'],original=p.as_posix(),crop_box=box,body_or_pixel_edit=False))
 return Image.open(q).convert('RGB').crop(box)
def plate(name,items,columns):
 out=Image.new('RGB',(300*columns,288*math.ceil(len(items)/columns)),(24,28,32));draw=ImageDraw.Draw(out)
 for n,(label,x) in enumerate(items):
  col,row=n%columns,n//columns;im=original(x);out.paste(im,(col*300,row*288+24));draw.text((col*300+4,row*288+6),label,fill='white')
 p=O/'展示副本'/(name+'-1x.png');out.save(p)
 out.resize((out.width*2,out.height*2),Image.Resampling.NEAREST).save(O/'展示副本'/(name+'-2x-nearest.png'))
plate('Death6-native',[(f'Death{x["frame"]} native{x["frame_index"]} age{x["DeathAge"]:.3f}',x) for x in i['samples']],3)
joinitems=[]
for side in [0,1]:
 for j in i['joins']:
  x=j['pair'][side];joinitems.append((f'{j["join"]} {"before" if side==0 else "after"} n{x["frame_index"]}',x))
plate('Death-five-adjacent-joins-native',joinitems,5)
for x in i['automatic_coin']['original_callback_states']:
 p=Path(x['presentation']['path']);q=O/'原件'/p.name;shutil.copy2(p,q);copied.append(q)
p=A/'展示副本/decoded-final-frame-Death-v001.png';q=O/'原件'/p.name;shutil.copy2(p,q);copied.append(q)
for p in copied:
 assert sha(p)==sha(A/'展示副本'/p.name)
files=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.rglob('*')) if p.is_file()]
(O/'index.json').write_text(json.dumps(dict(schema='Root-Death6-and-native-adjacent-join-crops-v001',source=A.as_posix(),crop_rects=crops,files=files,scaled_presentation_only='2x nearest',visual_reviewed=False,final_accepted=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('# 守卫正常死亡六相与五处真实相邻转场 v001\n\n只复制原尺寸实景、按真实GroundScreen裁图及整数最近邻放大；没有修改角色或姿态像素，没有补帧。原尺寸金币前后状态及解码末帧一并保留。金额只见真实ledger；需E两遍保全后Root查看，非最终美术或音效验收。\n',encoding='utf-8')
print(json.dumps(dict(folder=O.as_posix(),files=len(files)+2,originals=len(copied),plates=4,bytes=sum(p.stat().st_size for p in O.rglob('*') if p.is_file()))))
