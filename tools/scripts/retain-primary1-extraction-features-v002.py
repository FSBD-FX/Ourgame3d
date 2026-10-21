from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-chest192-extraction-v001';A=R/'过程图稿与视频/2026-10-17_软皮第一刀192胸衣挂点审阅_v002';assert not A.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'extraction-freeze-v001.json';assert desc(f)['sha256']=='66e58b3a1bae1a5b698a100e0230586bd6a0f82e99b02fbfe5dfca22c64708b0'
for row in json.loads(f.read_text(encoding='utf-8'))['files']:
 p=Path(row['path']);p=p if p.is_absolute() else B/p;d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件/extraction'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=q.relative_to(A).as_posix()))
idx=json.loads((B/'combined-18-source-index-Chest192-Near189-Far190-v001.json').read_text(encoding='utf-8'))
for i in range(6):
 body=R/f'source-assets/production/fairytale-sword-v001/run-primary1-v001/curated/frame-{i}.png';q=A/'原件'/f'Body159-{i}.png';shutil.copy2(body,q);assert body.read_bytes()==q.read_bytes();rows.append(dict(source=desc(body),copy=q.relative_to(A).as_posix()))
 sheet=Image.new('RGB',(1280,560),(32,35,41));d=ImageDraw.Draw(sheet);bg=Image.new('RGBA',(512,512),(95,100,110,255));bg.alpha_composite(Image.open(body).convert('RGBA'));sheet.paste(bg.convert('RGB'),(0,25));d.text((8,6),f'Body159 Primary1 phase {i}; original source coordinates',fill='white')
 for x in range(160,361,20):d.line((x,25,x,537),fill=(70,78,88));d.text((x,540),str(x),fill='white')
 for y in range(180,381,20):d.line((0,y+25,512,y+25),fill=(70,78,88));d.text((2,y+25),str(y),fill='white')
 for j,c in enumerate(idx['components']):
  pin=c['frames'][i]['source'];p=Path(pin['path']);assert desc(p)==pin;im=Image.open(p).convert('RGBA');box=(196,196,316,316);crop=im.crop(box);cb=Image.new('RGBA',crop.size,(95,100,110,255));cb.alpha_composite(crop);out=cb.convert('RGB').resize((240,240),Image.Resampling.NEAREST);x=530+j*250;y=120;sheet.paste(out,(x,y));d.text((x,80),f'{c["component"]} / source crop / 2x',fill='white')
  for xx in range(200,311,10):gx=x+(xx-196)*2;d.line((gx,y,gx,y+240),fill=(70,78,88));d.text((gx,y+244),str(xx),fill='white')
  for yy in range(200,311,10):gy=y+(yy-196)*2;d.line((x,gy,x+240,gy),fill=(70,78,88));d.text((x,gy),str(yy),fill='white')
 sheet.save(A/'展示副本'/f'features-phase-{i}.png')
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='actual18 extracted Source frames; diagnostic Body159/feature crops with grid; A/B/fit not accepted; no runtime import',source_textures_untouched=True,diagnostic_crop_nearest_neighbour_only=True,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('119提取原件及六个原Body159完整复制。六张挂点审阅图：身体保持512原坐标，组件局部仅2x最近邻网格诊断。原RGBA贴图不改；小部件共同scale、默认失败和motion警告保留。A为待Root从实图选择的可见细节，B为artist设计而非骨骼测量；192六相视角已原图初审，但挂点尚未测；189近肩／190远肩保留实际Source。新E295后才Root看新图。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),originals=len(rows),feature_sheets=6),ensure_ascii=False))
