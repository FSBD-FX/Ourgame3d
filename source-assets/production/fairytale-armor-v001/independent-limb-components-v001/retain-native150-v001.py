"""Freeze the actual native150 original before any explicit image inspection."""
from pathlib import Path
from PIL import Image
import datetime,hashlib,json,shutil
root=Path('F:/Ourgame');base=Path(__file__).resolve().parent;control=base/'generation-control-v001'
raw=Path('C:/Users/22499/.codex/generated_images/01a0f834-7bb4-7eb1-a91b-b0d45a166798/exec-73cfff49-c1d1-4712-8a24-8e8d6e586dfe.png')
target=base/'run-shoulder-far-idle-v001/raw/armor_shoulder_far_idle.png'
archive=root/'过程图稿与视频/2026-10-16_怪诞远侧肩甲四帧原稿_v003'
assert raw.is_file() and not target.exists() and not archive.exists()
target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(raw,target);assert raw.read_bytes()==target.read_bytes()
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
request=json.loads((control/'generation-request150-v003.json').read_text(encoding='utf-8'))
receipt=dict(request,status='generated_retained_pending_component_review',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 actual_native_original=desc(raw),canonical_raw=desc(target),raw_mode=Image.open(raw).mode,raw_size=list(Image.open(raw).size),
 source_pixels_modified=False,runtime_imported=False,complete_armor=False)
(control/'generation-receipt150-v003.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=root/'source-assets/production/first-unit-animation-v003/generation-ledger.json';l=json.loads(ledger.read_text(encoding='utf-8-sig'))
assert l['requested_count']==150 and l['requests'][-1]['request_number']==150
l['requests'][-1]=receipt;ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(control/'ledger-after-request150-generated.json').write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(archive/'原件').mkdir(parents=True);(archive/'展示副本').mkdir()
rows=[]
files=[raw,target,control/'generation-request150-v003.json',control/'generation-receipt150-v003.json',
 control/'ledger-before-request150.json',control/'ledger-after-request150-generated.json',Path(request['prompt_path']),Path(__file__)]
for n,p in enumerate(files):
 dst=archive/'原件'/f'{n:02d}-{p.name}';shutil.copy2(p,dst);assert p.read_bytes()==dst.read_bytes();rows.append(dict(desc(p),retained_relative=dst.relative_to(archive).as_posix()))
shutil.copy2(raw,archive/'展示副本/far-shoulder-native150-original.png')
(archive/'source-version-status-index.json').write_text(json.dumps({'files':rows,'status':'actual raw candidate, not extracted/reviewed/imported/accepted','formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(archive/'README.md').write_text('Actual native150 original plus exact presentation copy. Four far shoulder caps requested, outcome pending review. No existing131body changed; no formal armor completion.\n',encoding='utf-8')
print(json.dumps({'request':150,'raw':desc(raw),'size':receipt['raw_size'],'mode':receipt['raw_mode'],'archive':archive.as_posix()},ensure_ascii=False))
