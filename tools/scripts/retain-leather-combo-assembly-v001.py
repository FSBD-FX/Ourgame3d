from pathlib import Path
from PIL import Image
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--clip',type=int,choices=[2,3],required=True);p.add_argument('--freeze-sha',required=True);a=p.parse_args();B=R/f'source-assets/production/fairytale-lgt-readability-v003/primary{a.clip}-integer-assembly-v001';A=R/f'过程图稿与视频/2026-10-17_软皮轻甲第{a.clip}刀整数试装_v001'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'delivery-freeze-v001.json';assert desc(f)['sha256']==a.freeze_sha;d=json.loads(f.read_text(encoding='utf-8-sig'))
for v in d['files']:
 p=Path(v['path']);p=p if p.is_absolute() else B/p;q=desc(p);assert(q['bytes'],q['sha256'])==(v['bytes'],v['sha256'])
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),retained=q.relative_to(A).as_posix()))
for side,folder in [('right','right'),('left','left-whole-image-mirror')]:
 sheet=Image.new('RGBA',(1536,1024),(0,0,0,0));crop=Image.new('RGBA',(960,160),(0,0,0,0))
 for i in range(6):
  p=B/'diagnostics/static-no-sword'/folder/f'frame-{i}.png';q=A/'展示副本'/f'{side}-{i}.png';shutil.copy2(p,q);im=Image.open(p).convert('RGBA');assert im.size==(512,512);sheet.paste(im,((i%3)*512,(i//3)*512));crop.paste(im.crop((176,200,336,360)),(160*i,0))
 sheet.save(A/'展示副本'/f'{side}-six-whole-unscaled.png');crop.save(A/'展示副本'/f'{side}-six-torso-unscaled.png')
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='Integer-only armor candidate, 24 old body layers byte exact. No sword static composites; mirrored whole left image. Root fit review pending, no runtime or full motion acceptance.',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(A/'README.md').write_text('整数甲层试装；无剑静态诊断，原件和等像素展示留档，未作实景验收。\n',encoding='utf-8');print(A.as_posix())
