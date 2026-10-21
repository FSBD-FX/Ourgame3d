from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/near183-extraction-v001'
A=R/'过程图稿与视频/2026-10-16_软皮近肩183共同缩放提取诊断_v001'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'extraction-freeze-v001.json';assert desc(f)['sha256']=='d44cff7680b49be2fc57016c965278e4cfc13240d9fd10c25e252db9a716b626'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),retained=q.relative_to(A).as_posix()))
frames=list((B/'run-shared-diagnostic-v001/frames').rglob('*.png'));assert len(frames)==4
for i,p in enumerate(sorted(frames)):
 q=A/'展示副本'/f'frame-{i}.png';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,presentation='four exact shared-scale diagnostic PNG copies; no redraw/resampling',status='diagnostic only; lining/mask/A/actual mount/runtime unaccepted',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('183真实纠错原图标准色键/连通体提取+既有共同行缩放扩展；四512RGBA，非量化、不逐帧缩放。数值QA通过不等于开口内衬语义/A/fit/mask通过，未导入。Root在E归档后看图。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),originals=len(rows),presentation_pngs=4),ensure_ascii=False))
