"""Bind previously pending references to actual E471 bytes without editing originals."""
from pathlib import Path
import json,hashlib
R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
E=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-Death5-armor-inputs-v471')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
q=read(B/'armor-input-preparation-v001/Root-Death5-three-armor-inputpacket-v001.json')
out=B/'Root-native-armor-Death5-v001/input';assert not out.exists();out.mkdir(parents=True)
Efiles=[(p,pin(p)) for p in (E/'F盘原批次副本').rglob('*') if p.is_file()]
for row in q['components']:
 refs=read(Path(row['references']['path']))
 for ref in refs['references_in_order']:
  f=Path(ref['file']['path']);assert pin(f)==ref['file']; matches=[p for p,x in Efiles if x['bytes']==ref['file']['bytes'] and x['sha256']==ref['file']['sha256']];assert matches
  for _ in range(2): assert pin(f)==ref['file'] and pin(matches[0])['sha256']==ref['file']['sha256']
  ref.update(already_retained=True,actual_E_retained_file=pin(matches[0]))
 refs.update(actual_E_index=pin(E/'source-size-SHA256.json'),Root_actual_twoSHA_passes=2,source_retention_mismatches=0,not_native_called=True)
 f=out/(row['component']+'-Root-native-references-AFTER-E471-v001.json');f.write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f.as_posix())
