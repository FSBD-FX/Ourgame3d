"""Rearrange exact accepted body cells as a layout/identity input, no creative redraw."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageChops
import hashlib,json,shutil
R=Path('F:/Ourgame');O=R/'过程图稿与视频/2026-10-19_钟盔攻击修片尺寸锚点_v002'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert not O.exists();O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir()
sources=[R/f'source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-{i}.png' for i in range(6)]
board=Image.new('RGBA',(1536,1024),(255,0,255,255));rows=[]
for i,p in enumerate(sources):
 with Image.open(p) as im:
  im=im.convert('RGBA');assert im.size==(512,512)
  matte=Image.new('RGBA',(512,512),(255,0,255,255));matte.alpha_composite(im)
  x=(i%3)*512;y=(i//3)*512;board.paste(matte,(x,y));rows.append(dict(frame=i,source=pin(p),rect=[x,y,x+512,y+512]))
guide=O/'原件/primary1-original-six-curated-512-guide-v002.png';board.convert('RGB').save(guide)
with Image.open(guide) as reread:
 for row in rows:
  with Image.open(row['source']['path']) as im:
   matte=Image.new('RGBA',(512,512),(255,0,255,255));matte.alpha_composite(im.convert('RGBA'))
   assert ImageChops.difference(reread.crop(row['rect']),matte.convert('RGB')).getbbox() is None
shutil.copy2(guide,O/'展示副本'/guide.name)
(O/'README.md').write_text('既有六张512×512身体帧的原像素排版参考。仅背景合成洋红并排列为两行三列，无缩放／重绘／姿势变化。用于修正request257横向变宽及脚位漂移，保持现有主角72px和头盔体积；不是新的游戏美术。\n',encoding='utf-8')
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary-six-exact-curated-layout-guide-v002',utc=datetime.now(timezone.utc).isoformat(),guide=pin(guide),sources=rows,creative_redraw=False,source_pixels_resized=False,exact_each_cell_matte_pixels_redecoded_equal=True,game_display_height_px=72,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(pin(guide),ensure_ascii=False))
