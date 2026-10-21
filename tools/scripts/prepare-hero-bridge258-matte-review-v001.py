from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/matte-edge-clean-candidate-v002';O=R/'过程图稿与视频/2026-10-19_钟盔起手258边缘清理_v002'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=C/'matte-edge-clean-freeze-v002.json';f=json.loads(freeze.read_text(encoding='utf-8'))
assert pin(freeze)['sha256']=='961d240b874a148f170684aa795bb6e03e0638427806472054fe338560f389cf'
deps=[v for k,v in f.items() if k!='members' and isinstance(v,list) and v and isinstance(v[0],dict) and 'sha256' in v[0]]
assert len(f['members'])==23 and len(deps)==1 and len(deps[0])==32
for _ in range(2):
 for row in f['members']+deps[0]: assert pin(row['path'])==row
assert not O.exists();O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir();rows=[]
for p in sorted(C.rglob('*')):
 if p.is_file():
  dst=O/'原件/candidate'/p.relative_to(C);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),copy=pin(dst)))
for p in sorted((C/'qc').glob('*.png')):
 dst=O/'展示副本'/p.name;shutil.copy2(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),copy=pin(dst)))
(O/'README.md').write_text('request258两格身体边缘颜色清理候选。固定Alpha、轮廓、脚线、握点、甲片与独立剑不变；仅半透明边缘RGB去洋红。原件与全部确定性处理／QC／依赖保留；展示是无损副本。尚未游戏实装，目视与实际动作衔接待审。\n',encoding='utf-8')
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as out:json.dump(dict(schema='Root-primary258-matte-review-v002',utc=datetime.now(timezone.utc).isoformat(),source_freeze=pin(freeze),member_count=23,dependency_count=32,verification_passes=2,mismatches=0,copies=rows,Root_viewed=False,UE_imported=False,FinalAccepted=False),out,ensure_ascii=False,indent=2)
print(json.dumps(dict(archive=O.as_posix(),files=len([p for p in O.rglob('*') if p.is_file()])),ensure_ascii=False))
