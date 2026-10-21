"""Root native-only reservation for a pinned component packet; no provider call."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/generation-control-v001'
p=argparse.ArgumentParser();p.add_argument('--packet',required=True);p.add_argument('--retention',required=True);a=p.parse_args()
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x):q=Path(x['path']);assert pin(q)==x;return q
def new(q,d):
 with q.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
packet=Path(a.packet);packet=packet if packet.is_absolute()else R/packet;d=read(packet)
prompt=check(d['prompt']);refs=read(check(d['references_json']))['references_in_order']
e=Path(a.retention);ret=read(e);assert ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0
for x in refs:
 q=check(x['file']);assert any(z['sha256']==x['file']['sha256']and z['bytes']==x['file']['bytes']for z in ret['files'])
out=Path(d['output']);assert not out.exists()
ledgerpath=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';ledger=read(ledgerpath)
assert ledger['automatic_follow_on_batches_authorized'] and ledger['external_api_calls']==0 and ledger['remaining_batch_requests']>0
n=ledger['requested_count']+1;assert 249<=n<=264 and ledger['current_window']['number']==11
before=C/f'ledger-before-request{n}.json';assert not before.exists();shutil.copy2(ledgerpath,before)
rec=dict(request_number=n,asset='fairytale-guard003-Move-static-component',status='requested_pending',source_event='EV-048',
 authorization_events=['EV-040','EV-041'],window_number=11,requested_utc=datetime.now(timezone.utc).isoformat(),packet=pin(packet),
 prompt_path=prompt.as_posix(),prompt=prompt.read_text(encoding='utf-8'),prompt_file_sha256=pin(prompt)['sha256'],reference_images=refs,
 transparent_background=False,backend='image_gen.imagegen',external_api_calls=0,host_fee_usd=None,
 raw_destination_planned=out.as_posix(),E_inputs=pin(e),scope=d['current_call_scope'],formal_complete_units=0)
ledger['requests'].append(rec);ledger['requested_count']=n;ledger['batch_requested_count']+=1;ledger['remaining_batch_requests']-=1;ledger['lifetime_requested_count']+=1;ledger['current_window']['requested_count']+=1
new(C/f'generation-request{n}-v001.json',rec);ledgerpath.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');new(C/f'ledger-after-request{n}-reserved.json',ledger)
print(json.dumps(dict(request=n,window_used=ledger['batch_requested_count'],remaining=ledger['remaining_batch_requests'],lifetime=ledger['lifetime_requested_count'],record=pin(C/f'generation-request{n}-v001.json'),tool_called=False),ensure_ascii=False))
