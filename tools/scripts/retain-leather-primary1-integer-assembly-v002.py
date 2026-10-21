from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-lgt-readability-v003/primary1-integer-assembly-v002'
A=R/'过程图稿与视频/2026-10-17_软皮轻甲首刀六帧整数试装_v002'
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=B/'delivery-freeze-v002.json';assert desc(f)['sha256']=='d97d35bebcf85d3f054377262912c1319a933cd8f325d622e579cb27978b5257'
v=json.loads(f.read_text(encoding='utf-8'))
for row in v['files']:
 p=B/row['path'];d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():
  q=A/'原件'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();rows.append(dict(source=desc(p),retained=q.relative_to(A).as_posix()))
for side,folder in [('right','right'),('left','left-whole-image-mirror')]:
 for i in range(6):
  p=B/'diagnostics/static-no-sword'/folder/f'frame-{i}.png';q=A/'展示副本'/f'{side}-{i}.png';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,presentation='twelve exact static composite diagnostic copies; source armor integer translated only, actual Body159v003 four layers unchanged; left is whole-image mirror',status='Root static fit/mask review pending; no sword, no runtime, no full animation acceptance',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text('新胸衣/近肩/远肩各六帧按Root实际可见A与artist设计B仅做整数平移，实际Body159v003四身体层逐字节保持。展示为无剑静态组合，左面只整图镜像；不冒充新绘朝向/全动作。数值归属交集不等语义头盔/眼/颈/手/腰保护通过。尚未导入或实机。\n',encoding='utf-8')
print(json.dumps(dict(archive=A.as_posix(),originals=len(rows),presentation_pngs=8),ensure_ascii=False))
