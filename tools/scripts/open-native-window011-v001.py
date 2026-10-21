"""Close filled window10 by actual raw hashes; continue existing EV040/041 authority."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/first-unit-animation-v003';L=B/'generation-ledger.json'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,q):assert not p.exists(),p;p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=read(L);assert l['current_window']['number']==10 and l['current_window']['requested_count']==24 and l['requested_count']==240 and l['remaining_batch_requests']==0 and l['automatic_follow_on_batches_authorized'] and l['external_api_calls']==0
rows=[x for x in l['requests'] if 217<=x['request_number']<=240];assert len(rows)==24 and all(x['status']!='requested_pending' for x in rows)
for _ in range(2):
 for row in rows:assert pin(Path(row['canonical_raw']['path']))==row['canonical_raw']
out=B/'reviews/window010-accounting-close-v001';assert not out.exists();out.mkdir(parents=True)
frozen=B/'generation-ledger-window010-frozen.json';assert not frozen.exists();shutil.copy2(L,frozen)
review=dict(schema='window010-filled-accounting-close-v001',UTC=datetime.now(timezone.utc).isoformat(),authorization_events=['EV-040','EV-041'],frozen_ledger=pin(frozen),requests=24,retained_source_hash_passes=2,source_hash_mismatches=0,external_api_calls=0,host_fee_usd=None,source_QC_not_all_complete=True,runtime_acceptance_not_implied=True,formal_complete_units=0,next_work='One targeted native edit of Chest240 near-arm aperture relative to fixed buckle; window opening is accounting only and does not schedule24 calls.',rows=[dict(number=x['request_number'],status=x['status'],raw=x['canonical_raw']) for x in rows])
write(out/'review.json',review)
l['completed_windows'].append(dict(l['current_window'],status='accounting_filled_all_outputs_retained_source_QC_runtime_pending',frozen_ledger=pin(frozen),review=pin(out/'review.json')))
l['current_window']=dict(number=11,first_request_number=241,last_request_number=264,request_limit=24,requested_count=0,status='auto_authorized_active')
l.update(accounting_window_id='window011',batch_requested_count=0,remaining_batch_requests=24)
L.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');write(out/'after-open-window011-ledger.json',l)
print(json.dumps(dict(current_window=l['current_window'],next_request=241,review=pin(out/'review.json'),external_api_calls=0),ensure_ascii=False))
