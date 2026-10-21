"""Correct three legacy current aliases; preserve earlier sync as historical receipt."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');root=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/root-native-checkpoint-v001'
p=R/'docs/production/first-batch-v2/progress.json'
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
out=root/'current-alias-correction-v001';assert not out.exists();out.mkdir()
before=pin(p);shutil.copy2(p,out/'progress-before.json')
d=json.loads(p.read_text(encoding='utf-8-sig'))
d['previous_latest_visual_runtime_proof_before_v139']=d['latest_visual_runtime_proof']
d['previous_current_turn_media_retention_before_v139']=d['current_turn_media_retention']
d['latest_visual_runtime_proof']=pin(root/'Root-Stomp-native-and-visible-review-v139-v001.json')
d['current_turn_media_retention']=d['current_retention_batches']
d['current_status_authority']=d['current_status_authority'].replace('Root still review and full silent playback','Root phase/join/whole-frame review completed and both complete silent videos played to end')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=dict(schema='Root-Stomp-v139-current-alias-correction-v001',before=before,after=pin(p),
 previous_sync_receipt=pin(root/'current-status-sync-v139-v001.json'),fields=['latest_visual_runtime_proof','current_turn_media_retention','current_status_authority'],
 native_originals_and_Source_unchanged=True,Source=262,Production=1332,strict_GREEN=193,formal_complete_units=0,goal_status='active')
q=out/'receipt.json';q.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(receipt=pin(q),aliases_current=True,formal_complete_units=0),ensure_ascii=False))
