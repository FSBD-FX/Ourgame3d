from pathlib import Path
from PIL import Image
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');p=argparse.ArgumentParser();p.add_argument('--index',required=True);p.add_argument('--topic',required=True);a=p.parse_args();I=(R/a.index).resolve();assert I.is_relative_to(R/'source-assets');d=json.loads(I.read_text(encoding='utf-8-sig'));A=R/'过程图稿与视频'/a.topic;assert A.parent==R/'过程图稿与视频' and not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
for n,q in enumerate(sorted(I.parent.rglob('*'))):
 if q.is_file():
  o=A/'原件'/q.relative_to(I.parent);o.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,o);assert q.read_bytes()==o.read_bytes();rows.append(dict(source=desc(q),retained=o.relative_to(A).as_posix()))
for c in d['components']:
 assert len(c['frames'])==6
 sheet=Image.new('RGBA',(768,128),(0,0,0,0))
 for f in c['frames']:
  q=Path(f['source']['path']);assert desc(q)==f['source'];im=Image.open(q).convert('RGBA');assert im.size==(512,512);sheet.paste(im.crop((192,192,320,320)),(f['frame']*128,0));o=A/'展示副本'/f"{c['component']}-{f['frame']}.png";shutil.copy2(q,o)
 sheet.save(A/'展示副本'/f"{c['component']}-six-unscaled-crops.png")
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,index=desc(I),status='Standard extracted and identity-curated candidates, exact originals and unscaled source512 crop contacts. New A measurement/B design/fit/motion/native acceptance pending.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(A/'README.md').write_text('标准提取候选及等像素组件细节；新挂点与实际动作仍待。\n',encoding='utf-8');print(A.as_posix())
