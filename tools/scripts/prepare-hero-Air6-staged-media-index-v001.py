from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');M=R/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_right_v004';S=R/'Playables/钟盔轻甲-v142-CM52f906'
def pin(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
assert json.loads((M/'staged-native-supplement-v001.json').read_text(encoding='utf-8-sig'))['passed'] is True
O=M/'展示副本/staged-provenance-tools-v001';O.mkdir(exist_ok=False)
sources=[R/'tools/scripts'/n for n in ['run-hero-Air6-staged-v001.ps1','prepare-hero-Air6-staged-launch-v001.py','verify-hero-Air6-staged-runtime-v001.py']]+[S/'_proof/stage-copy-receipt-v001.json',S/'_proof/runtime-snapshot-manifest-v001.json',R/'source-assets/production/fairytale-hero-air-v001/stable-preview-candidate-v001/HeroAir6-stable-preview-candidate-freeze-v001.json']
copies=[]
for p in sources:
 dst=O/p.name;assert not dst.exists();shutil.copy2(p,dst)
 for n in range(2):assert (pin(dst)['bytes'],pin(dst)['sha256'])==(pin(p)['bytes'],pin(p)['sha256'])
 copies.append(dict(source=pin(p),copy=pin(dst)))
files=[pin(p) for p in sorted(M.rglob('*')) if p.is_file()]
write(M/'来源-版本-状态索引-staged-v004.json',dict(schema='Root-staged-Air6-media-index-v004',utc=datetime.now(timezone.utc).isoformat(),status='NATIVE_VERIFIED_PENDING_E_RETENTION_AND_ROOT_REVIEW',actual_staged_project_root=S.as_posix(),process_id=51516,actual_native_callbacks=174,independent_native=pin(M/'native-independent-verification-v004.json'),staged_runtime_supplement=pin(M/'staged-native-supplement-v001.json'),provenance_copies=copies,files=files,View=False,full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False))
print(json.dumps(dict(files_before_index=len(files),bytes_before_index=sum(x['bytes'] for x in files),index=pin(M/'来源-版本-状态索引-staged-v004.json')),ensure_ascii=False))
