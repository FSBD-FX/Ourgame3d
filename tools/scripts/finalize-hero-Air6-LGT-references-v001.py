"""Only after actual E585 retention: pin usable exact references, no generation."""
from pathlib import Path
import hashlib,json
R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-hero-state-gap-v001/air-state-preparation-v001/armor-standard-input-v001'
E=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-本项目E585-钟盔跳跃六相棕皮三层输入-v001/E-retention-index-v001.json')
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
assert E.is_file(); retained=json.loads(E.read_text(encoding='utf-8-sig'))
for token in ['chest','nearshoulder','farshoulder']:
 p=O/token/'references-pending-E-v001.json';q=json.loads(p.read_text(encoding='utf-8'));out=O/token/'references-AFTER-E585-v001.json';assert not out.exists()
 for row in q['references_in_order']:
  assert pin(Path(row['file']['path']))==row['file'];row['already_retained']=True;row['actual_retention_receipt']=pin(E)
 q.update(requires_actual_E_twoSHA_before_use=False,actual_E585_retained_twoSHA_zero_mismatch=True,root_source_and_identity_images_reviewed=True,retention_receipt=pin(E))
 out.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(success=True,references=3,E=pin(E)),ensure_ascii=False))
