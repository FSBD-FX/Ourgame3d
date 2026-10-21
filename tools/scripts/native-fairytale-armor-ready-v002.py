"""Single-writer native request accounting and flat pre-view preservation."""
from pathlib import Path
from PIL import Image
import argparse, datetime, hashlib, json, shutil

root=Path('F:/Ourgame').resolve()
base=root/'source-assets/production/fairytale-armor-sword-ready-v002'
control=base/'generation-control-v001'
ledger=root/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
p=sub.add_parser('reserve');p.add_argument('--handoff',required=True);p.add_argument('--component',required=True)
p.add_argument('--number',type=int,required=True);p.add_argument('--archive-topic',required=True)
p=sub.add_parser('retain');p.add_argument('--number',type=int,required=True)
p.add_argument('--original',required=True);p.add_argument('--archive-topic',required=True)
a=parser.parse_args()
def desc(path):
    data=path.read_bytes();return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write(path,value):
    assert not path.exists(),path
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def archive(files,present,status):
    parent=root/'过程图稿与视频';out=(parent/a.archive_topic).resolve()
    assert out.parent==parent and not out.exists()
    (out/'原件').mkdir(parents=True);(out/'展示副本').mkdir();rows=[]
    for i,path in enumerate(dict.fromkeys(files)):
        path=Path(path).resolve();target=out/'原件'/f'{i:03d}-{path.name}'
        shutil.copy2(path,target);assert path.read_bytes()==target.read_bytes()
        rows.append(dict(desc(path),retained_relative=target.relative_to(out).as_posix()))
    for i,path in enumerate(present):
        path=Path(path).resolve();target=out/'展示副本'/f'{i:02d}-{path.name}'
        shutil.copy2(path,target);assert path.read_bytes()==target.read_bytes()
    write(out/'source-version-status-index.json',{'files':rows,'status':status,'formal_complete_units':0})
    (out/'README.md').write_text(status+'\nExact originals and presentation copies. Local retention is not acceptance or publication.\n',encoding='utf-8')
    return out.as_posix()

l=json.loads(ledger.read_text(encoding='utf-8-sig'));number=a.number
request_path=control/f'generation-request{number}-v001.json'
if a.mode=='reserve':
    assert number==l['requested_count']+1 and l['remaining_batch_requests']>0
    handoff=Path(a.handoff).resolve();assert handoff.is_relative_to(base)
    document=json.loads(handoff.read_text(encoding='utf-8-sig'))
    row=next(r for r in document['rows'] if r['component']==a.component)
    assert row.get('standard_prepare_exit_code')==0 and row.get('target_mounts_are_measured') is False
    assert row.get('generation_ready',True) is True
    prompt=Path(row['prompt']['path']).resolve();assert desc(prompt)==row['prompt']
    refs=[r['file'] for r in row['reference_images_in_order']]
    assert 1<=len(refs)<=5
    for ref in refs:
        path=Path(ref['path']).resolve();assert path.is_relative_to(root) and desc(path)==ref
    raw=Path(row['raw_output_path']).resolve();assert raw.is_relative_to(base) and not raw.exists()
    write(control/f'ledger-before-request{number}.json',l)
    request={'request_number':number,'asset':'fairytale-'+a.component+'-'+Path(row['run_dir']).name,
             'component':a.component,'status':'requested_pending','source_event':'EV-048',
             'authorization_events':['EV-040','EV-041'],'window_number':l['current_window']['number'],
             'requested_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'prompt_path':prompt.as_posix(),'prompt':prompt.read_text(encoding='utf-8'),
             'prompt_file_sha256':desc(prompt)['sha256'],'reference_images':row['reference_images_in_order'],
             'transparent_background':False,'backend':'image_gen.imagegen','external_api_calls':0,
             'host_fee_usd':None,'raw_destination_planned':raw.as_posix(),
             'source_handoff':desc(handoff),'scope':'Canonical131 identity and actual158 pose; independent macro armor component Ready4 only. Actual component mount/fit/runtime/full equipment states remain unaccepted',
             'formal_complete_units':0}
    write(request_path,request);l['requests'].append(request)
    l['requested_count']=number;l['batch_requested_count']+=1;l['current_window']['requested_count']+=1
    l['remaining_batch_requests']=24-l['current_window']['requested_count']
    l['lifetime_requested_count']=l['lifetime_prior_EV038_requests']+number
    ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    after=control/f'ledger-after-request{number}-reserved.json';write(after,l)
    files=[handoff,prompt,request_path,control/f'ledger-before-request{number}.json',after,Path(__file__)]+[Path(r['path']) for r in refs]
    out=archive(files,[Path(refs[-1]['path'])],'Input references and reservation; not generated or accepted')
    print(json.dumps({'request':number,'reference_count':len(refs),'archive':out,'request_path':request_path.as_posix()},ensure_ascii=False))
else:
    request=json.loads(request_path.read_text(encoding='utf-8'));assert l['requested_count']==number and l['requests'][-1]['request_number']==number
    original=Path(a.original).resolve();target=Path(request['raw_destination_planned'])
    assert original.is_file() and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
    assert original.read_bytes()==target.read_bytes()
    im=Image.open(original)
    receipt=dict(request,status='generated_retained_pending_extraction',
                 generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 actual_native_original=desc(original),canonical_raw=desc(target),
                 raw_mode=im.mode,raw_size=list(im.size),source_pixels_modified=False,
                 runtime_imported=False,complete_armor=False)
    receipt_path=control/f'generation-receipt{number}-v001.json';write(receipt_path,receipt)
    l['requests'][-1]=receipt;ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    after=control/f'ledger-after-request{number}-generated.json';write(after,l)
    out=archive([original,target,request_path,receipt_path,after,Path(request['prompt_path']),Path(__file__)],[original],
                'Actual native raw original; extraction, fit and runtime review pending')
    print(json.dumps({'request':number,'raw':desc(target),'raw_size':list(im.size),'archive':out},ensure_ascii=False))
