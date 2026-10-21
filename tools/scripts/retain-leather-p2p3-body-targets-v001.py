from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003';A=R/'过程图稿与视频/2026-10-17_软皮连招实际身体对位_v001';assert not A.exists()
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
for clip in (2,3):
 D=B/f'primary{clip}-leather-input-v001';mp=D/'actual-runtime-source-version-mapping-v001.json';m=json.loads(mp.read_text(encoding='utf-8-sig'));d=json.loads((D/f'primary{clip}-leather-native-input-approved-v001.json').read_text(encoding='utf-8-sig'))
 pins=[mp]+[Path(x['path']) for x in d['rows'][0]['actual_runtime_body_pins']]+[Path(x['source']['path']) for x in m['actual_import']['verified_assets'] if x['component'] in ('BodyRest','NearArmWithoutHand','HelmetForeground','NearHand')]
 for i,p in enumerate(pins):
  q=A/'原件'/f'P{clip}'/f'{i:02d}-{p.parent.name}-{p.name}';q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert desc(p)['sha256']==desc(q)['sha256'];rows.append(dict(source=desc(p),retained=q.relative_to(A).as_posix()))
 sheet=Image.new('RGBA',(480,320),(0,0,0,0));whole=Image.new('RGBA',(1536,1024),(0,0,0,0))
 for i,pin in enumerate(d['rows'][0]['actual_runtime_body_pins']):
  p=Path(pin['path']);assert desc(p)==pin;im=Image.open(p).convert('RGBA');assert im.size==(512,512);whole.paste(im,((i%3)*512,(i//3)*512));crop=im.crop((176,200,336,360));sheet.paste(crop,((i%3)*160,(i//3)*160))
  q=A/'展示副本'/f'P{clip}-body-{i}.png';shutil.copy2(p,q)
 whole.save(A/'展示副本'/f'P{clip}-six-full-body-unscaled.png');sheet.save(A/'展示副本'/f'P{clip}-six-torso-crops-unscaled.png')
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='Actual current Body171v004 and Body175v001 plus four runtime layers, exact copies and unscaled diagnostic contact sheets. B artist proposal pending, no measured hidden bones; no fit or motion approval.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('实际运行身体与四层原件及等像素展示；仅挂点观察材料。\n',encoding='utf-8');print(A.as_posix())
