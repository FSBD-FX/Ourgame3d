from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/stable-preview-candidate-v001'
def pin(p):
 b=p.read_bytes();return dict(path=p.resolve().as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=C/'HeroAir6-stable-preview-candidate-freeze-v001.json'
rows=json.loads(freeze.read_text(encoding='utf-8-sig'))['members']
for n in range(2):
 for r in rows:
  p=Path(r['path']);assert (p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())==(r['bytes'],r['sha256']),r['path']
pair=R/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_left_v003/full-native-pair-v003.json'
assert pin(pair)['sha256']=='ad6958ac77142c2e2b2cb059096c68e380063a8318073f8cc89ad613179d1468'
stage=R/'Playables/钟盔轻甲-v142-CM52f906';assert not stage.exists()
request=json.loads((C/'Root-stage-request-TEMPLATE-v001.json').read_text(encoding='utf-8-sig'))
request.update(RootApproved=True,is_template=False,candidate_freeze_pin=pin(freeze),original_native_pair_pin=pin(pair),utc=datetime.now(timezone.utc).isoformat(),review='Root read complete physical copier and stable launcher, runtime manifest totals1778/143122086, source-only independent copy and exact membership gates; no UE or manual approval from copy.')
out=R/'source-assets/production/fairytale-hero-air-v001/root-stable-preview-v001';out.mkdir(exist_ok=False)
with (out/'actual-stage-request-v001.json').open('x',encoding='utf-8') as f:json.dump(request,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out/'actual-stage-request-v001.json'),ensure_ascii=False))
