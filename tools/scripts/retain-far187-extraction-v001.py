from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/far187-extraction-v001'
A=R/'过程图稿与视频/2026-10-17_软皮远肩187小部件共同缩放诊断_v001'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'extraction-freeze-v002.json';assert desc(f)['sha256']=='fa624a6e2c717413d17fb5023515fe67ece305bd180625136591e57a24371fe0'
for row in json.loads(f.read_text(encoding='utf-8'))['files']:
 p=B/row['path'];d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),retained=q.relative_to(A).as_posix()))
frames=list((B/'run-shared-smallcomponent-v002/frames').rglob('*.png'));assert len(frames)==4
for i,p in enumerate(sorted(frames)):
 q=A/'展示副本'/f'frame-{i}.png';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,presentation='four exact shared-scale diagnostic PNG copies; no redraw/resampling',status='tiny rigid attachment diagnostic only; actual source mount A/fit/mask/runtime unaccepted; default body minimum failed and preserved, explicit component minimum256, low-motion warning preserved',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('187真实远肩窄片原图标准色键/连通体提取及既有共同行缩放扩展。默认人物512像素面积门失败记录完整保留；小部件显式256面积门，4张512 RGBA共同scale，无量化。低motion警告保留，仅刚性附件微呼吸，非完整动画。标准inspect仅比帧间数据，不读base-source。A/fit/mask及实机未验收，未导入。Root在E归档后看图。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),originals=len(rows),presentation_pngs=4),ensure_ascii=False))
