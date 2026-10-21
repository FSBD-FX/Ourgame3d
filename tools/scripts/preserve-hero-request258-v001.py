"""Keep builtin output unchanged, retain F originals/display and generation accounting."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil
R=Path('F:/Ourgame')
C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction'
S=Path('C:/Users/22499/.codex/generated_images/01a0f834-7bb4-7eb1-a91b-b0d45a166798/exec-ec87b0ca-9471-40ab-8cd4-a2e3895f6adc.png')
O=R/'过程图稿与视频/2026-10-19_钟盔攻击起手修片_request258_v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert S.is_file() and not O.exists() and not (C/'raw').exists()
(C/'raw').mkdir();raw=C/'raw/primary1-bridge-correction.png';shutil.copy2(S,raw)
assert pin(raw)['sha256']==pin(S)['sha256']
with Image.open(raw) as im:im.load();size=list(im.size);mode=im.mode
used=C/'submitted-prompt.txt';used.write_text((C/'prompt.txt').read_text(encoding='utf-8').rstrip(),encoding='utf-8')
ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
d=json.loads(ledger.read_text(encoding='utf-8-sig'));assert d['requested_count']==258 and d['requests'][-1]['request_number']==258
shutil.copy2(ledger,C/'generation-ledger-before-result258.json')
row=d['requests'][-1];row.update(status='raw_saved_before_root_visual_review',generated_utc=datetime.now(timezone.utc).isoformat(),actual_native_original=pin(S),canonical_raw=pin(raw),raw_size=size,raw_mode=mode,submitted_prompt_pin=pin(used),source_pixels_modified=False,runtime_imported=False,complete_content_unit=False)
ledger.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir()
for part in ('原件','展示副本'):
 dst=O/part/'primary1-bridge-body-request258.png';shutil.copy2(raw,dst);assert pin(dst)['sha256']==pin(raw)['sha256']
for p in (C/'prompt.txt',used,C/'request258-reservation.json'):
 shutil.copy2(p,O/'原件'/p.name)
receipt=dict(schema='Root-builtin-hero-primary-bridge-generation258-v001',utc=row['generated_utc'],builtin_request_number=258,window11_requested=18,window11_remaining=6,lifetime_requested=282,initial3_separate=True,native_original=pin(S),canonical_raw=pin(raw),display_height_px=72,raw_size=size,raw_mode=mode,submitted_prompt_pin=pin(used),reference_archive=(R/'过程图稿与视频/2026-10-19_钟盔四姿态修片参考_v001').as_posix(),external_API_calls=0,host_fee_usd=None,new_generation_actual=True,Root_visual_reviewed=False,UE_imported=False,FinalAccepted=False)
for p in (C/'generation258-result-v001.json',O/'原件/generation258-result-v001.json'):
 with p.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
(O/'README.md').write_text('内置生成request258：攻击起手J0/J1身体动作新候选，六格只作动作表上下文；其他原运行帧不替换。保持72px与既有钟盔轻甲身份。未经Root审图／提取／分层／导入，不算美术或内容单元完成。完整生成原件与展示副本逐字节留存，沿用自动授权，无外部API调用，内置费用未知。\n',encoding='utf-8')
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-hero-primary-bridge258-source-version-status-v001',result=pin(O/'原件/generation258-result-v001.json'),files=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()],Root_visual_reviewed=False,UE_imported=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(receipt,ensure_ascii=False))
