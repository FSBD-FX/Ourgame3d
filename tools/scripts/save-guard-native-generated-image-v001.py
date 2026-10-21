"""Save one already-generated native image without touching pixels or request counts."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/generation-control-v001'
p=argparse.ArgumentParser();p.add_argument('--number',type=int,required=True);p.add_argument('--native-original',required=True);a=p.parse_args();n=a.number
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def new(q,d):
 with q.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
rec=read(C/f'generation-request{n}-v001.json');q=Path(a.native_original).resolve()
assert q.is_relative_to(Path('C:/Users/22499/.codex/generated_images').resolve()) and q.is_file()
target=Path(rec['raw_destination_planned']);assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target);assert pin(q)['sha256']==pin(target)['sha256']
with Image.open(q)as im:size=list(im.size);mode=im.mode
rec.update(status='generated_retained_pending_review',generated_utc=datetime.now(timezone.utc).isoformat(),actual_native_original=pin(q),canonical_raw=pin(target),raw_size=size,raw_mode=mode,source_pixels_modified=False,runtime_imported=False,complete_enemy=False)
new(C/f'generation-receipt{n}-v001.json',rec)
lp=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';ledger=read(lp)
matches=[i for i,x in enumerate(ledger['requests'])if x['request_number']==n];assert len(matches)==1 and ledger['requests'][matches[0]]['status']=='requested_pending'
ledger['requests'][matches[0]]=rec;lp.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');new(C/f'ledger-after-request{n}-generated.json',ledger)
archive=R/f'过程图稿与视频/2026-10-18_GuardMove-native{n}-raw-v001';assert not archive.exists()
for leaf in ['原件','展示副本']:(archive/leaf).mkdir(parents=True)
for src,name in [(target,f'native{n}-original.png'),(C/f'generation-receipt{n}-v001.json',f'generation-receipt{n}-v001.json'),(Path(rec['prompt_path']),f'exact-prompt{n}.txt')]:
 for leaf in ['原件','展示副本']:shutil.copy2(src,archive/leaf/name)
new(archive/'index.json',dict(schema='native-GuardMove-component-raw-version-status-v001',request=n,status='generated_not_reviewed_or_extracted',native_original=pin(q),canonical_raw=pin(target),files=[pin(x)for x in sorted(archive.rglob('*'))if x.is_file()],runtime_imported=False,FinalAccepted=False))
(archive/'README.md').write_text('原生静态组件原图；尚未提取／审阅／组合／接入。原件与展示副本按原字节保存，不是完整步态。\n',encoding='utf-8')
print(json.dumps(dict(request=n,raw=pin(target),size=size,mode=mode,archive=archive.as_posix(),requested=ledger['requested_count'],remaining=ledger['remaining_batch_requests']),ensure_ascii=False))
