from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-leather-input-v001';A=R/'过程图稿与视频/2026-10-17_软皮轻甲第一刀三组件输入_v001';assert not A.exists()
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'input-freeze-v001.json';assert desc(f)['sha256']=='ae539d6c13aa32dfd451590f6666e553753392e11bb89d8f59317fa0aba321bb'
for row in json.loads(f.read_text(encoding='utf-8'))['files']:
 p=Path(row['path']);p=p if p.is_absolute() else B/p;d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),copy=q.relative_to(A).as_posix()))
v=json.loads((B/'primary1-leather-native-input-draft-v001.json').read_text(encoding='utf-8'))
for row in v['rows']:
 for i,ref in enumerate(row['reference_images_in_order']):
  p=Path(ref['file']['path']);assert desc(p)==ref['file'];q=A/'展示副本'/f'{row["component"]}-{i}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,reference_roles='old same-component Primary1 row edit target plus actual new Ready component appearance anchor; no full-body base',status='Root input review pending; generation false; all new A/B null',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('三组件六相输入标准prepare实0；旧同组件第一刀raw仅编辑目标/动作几何，新Ready组件是外观身份。旧fullbodybase未附；新挂点/fit/运行未验收。先E282留存再Root看参考。\n',encoding='utf-8')
print(A.as_posix())
