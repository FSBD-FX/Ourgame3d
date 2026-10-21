from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction'
L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
d=json.loads(L.read_text(encoding='utf-8-sig'));assert d['requested_count']==257 and d['current_window']['requested_count']==17 and d['remaining_batch_requests']==7
shutil.copy2(L,C/'generation-ledger-before-request258.json');prompt=C/'prompt.txt'
refs=[R/'过程图稿与视频/2026-10-19_钟盔攻击修片尺寸锚点_v002/展示副本/primary1-original-six-curated-512-guide-v002.png',R/'过程图稿与视频/2026-10-19_钟盔攻击起手修片_request257_v001/展示副本/primary1-bridge-body-request257.png',R/'过程图稿与视频/2026-10-19_钟盔四姿态修片参考_v001/展示副本/ready-original-frame0.png',R/'过程图稿与视频/2026-10-19_钟盔四姿态修片参考_v001/展示副本/air-original-six.png']
row=dict(request_number=258,asset='hero-primary1-J0-J1-volume-footprint-correction',status='reserved_before_builtin_call',source_event='EV048',authorization_events=d['authorization_events'],window_number=11,requested_utc=datetime.now(timezone.utc).isoformat(),prompt_path=prompt.as_posix(),prompt=prompt.read_text(encoding='utf-8'),prompt_file_sha256=pin(prompt)['sha256'],reference_images=[pin(p) for p in refs],transparent_background=False,backend='builtin-imagegen',external_api_calls=0,host_fee_usd=None,raw_destination_planned=(C/'raw/primary1-bridge-correction.png').as_posix(),scope='Correct request257 enlargedhelmet/widenedstance; onlyJ0/J1 candidates; exact accepted512guide/72px remain authority',formal_complete_units=0,runtime_imported=False,complete_content_unit=False)
d['requests'].append(row);d['requested_count']=258;d['current_window']['requested_count']=18;d['remaining_batch_requests']=6;d['lifetime_requested_count']=282
L.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (C/'request258-reservation.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
print('Reserved258/window11used18/remaining6/lifetime282; existingautomaticbuiltin authorization; externalAPI0')
