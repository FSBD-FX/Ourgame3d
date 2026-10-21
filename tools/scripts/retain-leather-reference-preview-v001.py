from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/reference-preview-v001'
A=R/'过程图稿与视频/2026-10-16_软皮轻甲72像素参考对照_v001'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'preparation-freeze-v001.json'
assert desc(f)['sha256']=='2208d40bbf9ac1501f5ed34fc722600df91452b43953fd57edd60620911d5efa'
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
rows=[]
for p in B.iterdir():
 if p.is_file():
  q=A/'原件'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=desc(q)))
  q=A/'展示副本'/p.name;shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,status='Reference only, not runtime replacement or full animation. 72 CSS pixel alpha-core height with original PNG bytes.',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('EV048新软皮甲参考与当前158Ready0等alpha核心高度72 CSS像素对照。仅CSS显示，原PNG逐字节不变。参考未替换游戏，非完整动画；另180/181/182三raw均误生成完整背心，已拒绝导入。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),originals=len(rows),presentation=len(rows)),ensure_ascii=False))
