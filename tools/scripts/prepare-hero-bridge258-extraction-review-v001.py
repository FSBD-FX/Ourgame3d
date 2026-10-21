from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/extraction-candidate-v001';O=R/'过程图稿与视频/2026-10-19_钟盔起手258两格提取审阅_v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=C/'extraction-freeze-v001.json';f=json.loads(freeze.read_text(encoding='utf-8'))
assert len(f['members'])==17
for _ in range(2):
 for row in f['members']:
  actual=pin(row['path']);assert(actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256'])
assert not O.exists();O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir();rows=[]
for p in sorted(C.rglob('*')):
 if p.is_file():
  dst=O/'原件/candidate'/p.relative_to(C);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),copy=pin(dst)))
for i in (0,1):
 p=C/f'transparent-cells/frame-{i}-RGBA-footline464-candidate.png';dst=O/'展示副本'/p.name;shutil.copy2(p,dst);assert pin(dst)['sha256']==pin(p)['sha256'];rows.append(dict(source=pin(p),copy=pin(dst)))
(O/'README.md').write_text('request258两身体候选的确定性洋红提取。共享位移0,0；源RGB／尺度未改。原始两裁格／处理器／QC／来源闭包完整保留；展示为透明候选逐字节副本。头盔颜色芯是代理指标，非盔壳接受；握点／owner／三甲层／运行未完成。\n',encoding='utf-8')
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as out:json.dump(dict(schema='Root-primary-258-extraction-review-input-v001',utc=datetime.now(timezone.utc).isoformat(),source_freeze=pin(freeze),member_count=17,verification_passes=2,mismatches=0,copies=rows,Root_viewed_new_derived=False,UE_imported=False,FinalAccepted=False),out,ensure_ascii=False,indent=2)
print(json.dumps(dict(archive=O.as_posix(),source_freeze=pin(freeze),files=len([p for p in O.rglob('*') if p.is_file()])),ensure_ascii=False))
