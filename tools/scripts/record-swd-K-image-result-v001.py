from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
from PIL import Image
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-sword-secondary-v001';L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
ap=argparse.ArgumentParser();ap.add_argument('--request',type=int,required=True);ap.add_argument('--native',required=True);ap.add_argument('--raw-name',required=True);ap.add_argument('--topic',required=True);a=ap.parse_args()
def d(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
P=C/f'requests/request{a.request}-v001';pre=P/'request-prereg-v001.json';rec=json.loads(pre.read_text(encoding='utf-8-sig'));assert rec['request_number']==a.request
native=Path(a.native);raw=P/'raw'/a.raw_name;assert raw.as_posix()==rec['raw_destination_planned'] and not raw.exists();raw.parent.mkdir();shutil.copy2(native,raw);assert d(native)['sha256']==d(raw)['sha256']
im=Image.open(raw);result=dict(schema='builtin-K-body-image-result-v001',request_number=a.request,utc=datetime.now(timezone.utc).isoformat(),native_original=d(native),raw=d(raw),actual_size=list(im.size),mode=im.mode,backend='builtin-imagegen',external_api_calls=0,host_fee_usd=None,reviewed=False,runtime_imported=False,formal_complete_units=0)
rp=P/f'generation{a.request}-result-v001.json';assert not rp.exists();rp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=json.loads(L.read_text(encoding='utf-8-sig'));assert ledger['requested_count']==a.request and ledger['requests'][-1]['request_number']==a.request
ledger['requests'][-1].update(status='generated_raw_not_reviewed_not_runtime',actual_native_original=d(native),actual_raw=d(raw),actual_size=list(im.size),generation_result=d(rp));L.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
A=R/'过程图稿与视频'/a.topic;assert A.parent==R/'过程图稿与视频' and not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir();rows=[]
for p in [raw,pre,P/'prompt.txt',rp,P/f'generation-ledger-before-request{a.request}.json']:
 t=A/'原件'/p.name;shutil.copy2(p,t);assert d(t)['sha256']==d(p)['sha256'];rows.append(dict(source=d(p),retained=d(t)))
v=A/'展示副本'/raw.name;shutil.copy2(raw,v);assert d(v)['sha256']==d(raw)['sha256']
(A/'source-version-status-index.json').write_text(json.dumps(dict(files=rows,presentation=d(v),status='Raw generated; E exact-byte retention required before Root View; no art/runtime acceptance',formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'README.md').write_text(f'内置生成request{a.request}原图、提示词、请求和计数前快照保留。实际画布{im.width}x{im.height}，未改原图。原件/展示副本逐字节一致；先E保全再Root审阅，不表示导入、动作或正式单元验收。\n',encoding='utf-8')
print(json.dumps(dict(result=result,archive=A.as_posix()),ensure_ascii=False))
