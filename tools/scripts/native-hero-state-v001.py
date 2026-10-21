"""Root-only native generation accounting; retains exact originals before review."""
from pathlib import Path
from PIL import Image
import argparse, datetime, hashlib, json, shutil

ROOT = Path('F:/Ourgame').resolve()
BASE = ROOT / 'source-assets/production/fairytale-hero-state-gap-v001'
CONTROL = BASE / 'generation-control-v001'
LEDGER = ROOT / 'source-assets/production/first-unit-animation-v003/generation-ledger.json'
p = argparse.ArgumentParser()
p.add_argument('mode', choices=['reserve', 'retain'])
p.add_argument('--number', type=int, required=True)
p.add_argument('--topic', required=True)
p.add_argument('--prompt')
p.add_argument('--references')
p.add_argument('--output')
p.add_argument('--original')
a = p.parse_args()
def pin(path):
    path = Path(path).resolve(); data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
def write(path, obj):
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def archive(files, images, status):
    parent = ROOT / '过程图稿与视频'; out = (parent / a.topic).resolve()
    assert out.parent == parent and not out.exists(), out
    (out / '原件').mkdir(parents=True); (out / '展示副本').mkdir()
    rows = []
    for i, src in enumerate(dict.fromkeys(Path(f).resolve() for f in files)):
        dst = out / '原件' / f'{i:03d}-{src.name}'
        shutil.copy2(src, dst); assert src.read_bytes() == dst.read_bytes()
        rows.append(dict(pin(src), retained_relative=dst.relative_to(out).as_posix()))
    for i, src in enumerate(images):
        src = Path(src); dst = out / '展示副本' / f'{i:02d}-{src.name}'
        shutil.copy2(src, dst); assert src.read_bytes() == dst.read_bytes()
    write(out / 'source-version-status-index.json', dict(status=status, files=rows, formal_complete_units=0))
    (out / 'README.md').write_text(status+'\n原件与展示副本保留；留档不代表美术或整单元验收。\n', encoding='utf-8')
    return out.as_posix()
l = json.loads(LEDGER.read_text(encoding='utf-8-sig'))
reqpath = CONTROL / f'generation-request{a.number}-v001.json'
if a.mode == 'reserve':
    assert a.number == l['requested_count'] + 1 and l['remaining_batch_requests'] > 0
    prompt = Path(a.prompt).resolve(); refsfile = Path(a.references).resolve()
    assert prompt.is_relative_to(BASE) and refsfile.is_relative_to(BASE)
    refs = json.loads(refsfile.read_text(encoding='utf-8-sig'))['references_in_order']
    assert 1 <= len(refs) <= 5
    for ref in refs:
        assert pin(ref['file']['path']) == ref['file'] and ref['already_retained']
    output = Path(a.output).resolve()
    assert output.is_relative_to(BASE) and not output.exists()
    write(CONTROL / f'ledger-before-request{a.number}.json', l)
    req = dict(request_number=a.number, asset='fairytale-hero-nativeRight-'+output.stem,
               status='requested_pending', source_event='EV-048', authorization_events=['EV-040','EV-041'],
               window_number=l['current_window']['number'], requested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               prompt_path=prompt.as_posix(), prompt=prompt.read_text(encoding='utf-8'), prompt_file_sha256=pin(prompt)['sha256'],
               reference_images=refs, transparent_background=False, backend='image_gen.imagegen',
               external_api_calls=0, host_fee_usd=None, raw_destination_planned=output.as_posix(),
               scope='Current bell-helmet body-only new action candidate; equipment modules and measured source registration remain separate gates',
               formal_complete_units=0)
    write(reqpath, req); l['requests'].append(req)
    l['requested_count']=a.number; l['batch_requested_count']+=1; l['current_window']['requested_count']+=1
    l['remaining_batch_requests']=24-l['current_window']['requested_count']
    l['lifetime_requested_count']=l['lifetime_prior_EV038_requests']+a.number
    LEDGER.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    after=CONTROL / f'ledger-after-request{a.number}-reserved.json'; write(after,l)
    out=archive([prompt,refsfile,reqpath,CONTROL / f'ledger-before-request{a.number}.json',after,Path(__file__)]+[r['file']['path'] for r in refs],
                [r['file']['path'] for r in refs], 'Generation input reservation; not generated or accepted')
    print(json.dumps(dict(request=a.number,archive=out),ensure_ascii=False))
else:
    req=json.loads(reqpath.read_text(encoding='utf-8-sig'))
    ix=[i for i,r in enumerate(l['requests']) if r['request_number']==a.number]
    assert len(ix)==1 and l['requests'][ix[0]]==req and req['status']=='requested_pending'
    original=Path(a.original).resolve(); target=Path(req['raw_destination_planned'])
    assert original.is_file() and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(original,target)
    assert original.read_bytes()==target.read_bytes()
    im=Image.open(target)
    receipt=dict(req,status='generated_retained_pending_review',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 actual_native_original=pin(original),canonical_raw=pin(target),raw_size=list(im.size),raw_mode=im.mode,
                 source_pixels_modified=False,runtime_imported=False,complete_enemy=False)
    recpath=CONTROL / f'generation-receipt{a.number}-v001.json'; write(recpath,receipt)
    l['requests'][ix[0]]=receipt; LEDGER.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    after=CONTROL / f'ledger-after-request{a.number}-generated.json'; write(after,l)
    out=archive([original,target,reqpath,recpath,after,Path(req['prompt_path']),Path(__file__)],[original],
                'Actual native original; base identity/row extraction/runtime review pending')
    print(json.dumps(dict(request=a.number,archive=out,raw=pin(target),size=list(im.size)),ensure_ascii=False))
