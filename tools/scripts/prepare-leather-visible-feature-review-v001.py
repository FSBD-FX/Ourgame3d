from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw
R=Path('F:/Ourgame');S=R/'source-assets/production/fairytale-lgt-readability-v003/far187-extraction-v001/ready-three-component-source-list-v001.json'
A=R/'过程图稿与视频/2026-10-17_软皮组件可见挂点测量_v001';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
v=json.loads(S.read_text(encoding='utf-8'));rows=[]
for f in v['frames']:
 i=f['frame'];pieces=[('Body',f['common_body158'],(160,205,320,350))]+[(c['component'],c['diagnostic_png'],(205,205,305,310)) for c in f['armor_candidates_for_root_measurement']]
 sheet=Image.new('RGB',(1280,620),(34,36,42));d=ImageDraw.Draw(sheet)
 for n,(name,pin,box) in enumerate(pieces):
  p=Path(pin['path']);assert desc(p)==pin;q=A/'原件'/f'{name}-{i}.png';shutil.copy2(p,q);rows.append(pin)
  im=Image.open(p).convert('RGBA');crop=im.crop(box);bg=Image.new('RGBA',crop.size,(102,108,118,255));bg.alpha_composite(crop);bg=bg.convert('RGB').resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST)
  x=10+n*315;y=40;sheet.paste(bg,(x,y));d.text((x,8),f'{name} frame {i} / crop {box} / 3x',fill='white')
  if name!='Body':
   # Diagnostic grid only, never written into candidate textures.
   for xx in range(220,301,10):
    gx=x+(xx-box[0])*3;d.line((gx,y,gx,y+bg.height),fill=(75,82,90));d.text((gx,y+bg.height+4),str(xx),fill='white')
   for yy in range(220,301,10):
    gy=y+(yy-box[1])*3;d.line((x,gy,x+bg.width,gy),fill=(75,82,90));d.text((x,gy),str(yy),fill='white')
  else:
   d.text((x,500),'Body attachment B remains artist placement; not a skeleton measurement',fill='white')
 sheet.save(A/'展示副本'/f'visible-features-{i}.png')
shutil.copy2(S,A/'原件'/S.name)
(A/'source-version-status-index.json').write_text(json.dumps(dict(source_index=desc(S),source_pins=rows,status='diagnostic visible-feature coordinate review only; source textures untouched; no fit/mask/runtime acceptance',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('源RGBA完整复制；展示图为裁剪、最近邻3倍与独立坐标网格，仅用于逐帧可见扣件/针脚/窄片尖端定位。未修改源贴图，不作最终美术。B是身体表面的设计放置点，不冒充关节测量。\n',encoding='utf-8')
print(A.as_posix())
