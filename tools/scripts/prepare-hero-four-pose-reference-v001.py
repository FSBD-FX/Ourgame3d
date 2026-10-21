"""Preserve existing art references before local viewing and bounded image edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,shutil
R=Path('F:/Ourgame')
O=R/'过程图稿与视频/2026-10-19_钟盔四姿态修片参考_v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
sources={
 'primary1-original-six.png':R/'source-assets/production/fairytale-sword-v001/run-primary1-v003/raw/sword_primary_1.png',
 'dodge-original-four.png':R/'source-assets/production/fairytale-hero-state-gap-v001/hero218-220-extraction-v001/runs/run-dodge218-shared-HD-v002/raw/dodge.png',
 'ready-original-frame0.png':R/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png',
 'air-original-six.png':R/'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/extraction-v001/run-Air6-shared-HD-v001/raw/jump_nonattack.png',
 'native-J-right-all-poses.png':R/'过程图稿与视频/2026-10-19_钟盔落地J实录与接续_right_v001/展示副本/Air-Land-action-Ready-all-UNSCALED-crops-v001.png',
 'native-Dodge-right-all-poses.png':R/'过程图稿与视频/2026-10-19_钟盔落地Shift实录与接续_right_v001/展示副本/Air-Land-action-Ready-all-UNSCALED-crops-v001.png',
}
assert not O.exists()
before={name:pin(p) for name,p in sources.items()}
O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir()
rows=[]
for name,source in sources.items():
 for part in ('原件','展示副本'):
  destination=O/part/name;shutil.copy2(source,destination)
  a=pin(destination);b=before[name];assert(a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])
  rows.append(dict(source=b,copy=a))
report=R/'.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/hero-armor-pose-polish-plan-v001.md'
shutil.copy2(report,O/'原件'/report.name)
(O/'README.md').write_text('四姿态修片输入参考；既有原始动作表、Ready锚点及已保全原生动作板的逐字节副本。不是新生成或已经改进的实景。新候选只优先J0/J1、Dodge0/Dodge3；保持72px、轻甲、原输入时机。\n',encoding='utf-8')
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-hero-four-pose-reference-v001',utc=datetime.now(timezone.utc).isoformat(),copies=rows,plan=pin(O/'原件'/report.name),new_image_generations=0,UE_imported=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(archive=O.as_posix(),files=len(list(p for p in O.rglob('*') if p.is_file()))),ensure_ascii=False))
