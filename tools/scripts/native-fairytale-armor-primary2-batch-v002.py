"""Candidate ONLY. Root-owned accounting; never calls an image generator.
Default is readonly plan. --execute required for ledger/archive/raw writes.
Reservations are sequential; completions select unique request_number, any order.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil
from contextlib import contextmanager
from PIL import Image
ROOT=Path('F:/Ourgame').resolve()
BASE=ROOT/'source-assets/production/fairytale-armor-sword-primary2-v001'
CONTROL=BASE/'generation-control-v001'
LEDGER=ROOT/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
DRAFT=BASE/'generation-prompts-v002/draft-handoff-v002.json'
DRAFT_SHA='edbcba5b714791d72dfbd02d14891a08497be9a06009b92aebde30bc30ffc500'
COMPONENTS={'Chest','NearShoulder','FarShoulder'}

def require(ok,why):
    if not ok:raise ValueError(why)
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def desc(p):
    p=Path(p).resolve();data=p.read_bytes();return {'path':p.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def write_new(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(encoded(v));f.flush();os.fsync(f.fileno())
def copy_new(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(source.read_bytes());f.flush();os.fsync(f.fileno())
    require(source.read_bytes()==target.read_bytes(),'Exact copy mismatch')
def counters(l):
    return {k:copy.deepcopy(l[k]) for k in ['requested_count','batch_requested_count','remaining_batch_requests','lifetime_requested_count','current_window']}
def validate_ledger(l):
    w=l['current_window'];nums=[r['request_number'] for r in l['requests']]
    require(all(type(n) is int for n in nums) and len(nums)==len(set(nums)),'Duplicate/non-integer request number')
    require(sorted(nums)==list(range(1,l['requested_count']+1)),'Missing request history')
    require(w['request_limit']==l['batch_request_limit']==24,'Unknown quota contract')
    require(0<=w['requested_count']<=24 and l['batch_requested_count']==w['requested_count'],'Window/batch count mismatch')
    require(l['remaining_batch_requests']==24-w['requested_count'],'Remaining count mismatch')
    require(l['requested_count']==w['first_request_number']+w['requested_count']-1,'Window/global number mismatch')
    require(l['lifetime_requested_count']==l['lifetime_prior_EV038_requests']+l['requested_count'],'Lifetime count mismatch')
def unique(l,n):
    found=[i for i,r in enumerate(l['requests']) if r['request_number']==n]
    require(len(found)==1,'Request must occur exactly once');return found[0]
def reserve_state(l,request):
    validate_ledger(l);n=request['request_number'];w=l['current_window']
    require(w['number']==8 and w['status']=='auto_authorized_active','Window008 must already be authorized')
    require(n in (172,173,174) and n==l['requested_count']+1,'Reserve sequential planned172..174 only')
    require(w['first_request_number']<=n<=w['last_request_number'] and l['remaining_batch_requests']>0,'Window exhausted')
    require(request['status']=='requested_pending' and request['component'] in COMPONENTS,'Invalid pending row')
    require(not any(r.get('raw_destination_planned')==request['raw_destination_planned'] for r in l['requests']),'Row destination already requested; no automatic paid retry')
    require(not any(r.get('source_handoff')==request['source_handoff'] and r.get('component')==request['component'] for r in l['requests']),'Component already reserved from same approval')
    result=copy.deepcopy(l);result['requests'].append(copy.deepcopy(request));result['requested_count']=n
    result['batch_requested_count']+=1;result['current_window']['requested_count']+=1
    result['remaining_batch_requests']=24-result['current_window']['requested_count']
    result['lifetime_requested_count']=result['lifetime_prior_EV038_requests']+n
    validate_ledger(result);return result

def finish_state(l,request,receipt):
    validate_ledger(l);i=unique(l,request['request_number'])
    require(l['requests'][i]==request and request['status']=='requested_pending','Not exact unique pending request')
    require(receipt['request_number']==request['request_number'] and receipt['component']==request['component'],'Completion identity mismatch')
    require(receipt['status'] in ('generated_retained_pending_extraction','failed_native_no_image_preserved'),'Unknown completion status')
    for key,value in request.items():
        if key!='status':require(receipt.get(key)==value,'Completion changed reserved '+key)
    result=copy.deepcopy(l);result['requests'][i]=copy.deepcopy(receipt)
    require(counters(result)==counters(l),'Completion cannot change quota/count/window')
    validate_ledger(result);return result

def approved_row(path,component):
    path=Path(path).resolve();require(path.is_relative_to(BASE) and path!=DRAFT,'Approved handoff must be a separate family file')
    document=load(path);require(document.get('generation_ready') is True and document.get('root_review_required_before_generation') is False,'Root approval required; draft cannot reserve')
    review=document['root_input_review'];require(desc(review['path'])==review,'Root review pin mismatch')
    reviewed=load(review['path']);require(reviewed.get('geometry_design_only') is True and reviewed.get('future_feature_A_measured') is False and bool(reviewed.get('approval_scope')),'Root design-only / unmeasured feature approval required')
    require(desc(DRAFT)['sha256']==DRAFT_SHA,'Frozen prompt draft changed')
    draft=load(DRAFT);rows=[r for r in document['rows'] if r['component']==component];ds=[r for r in draft['rows'] if r['component']==component]
    require(len(rows)==len(ds)==1 and {r['component'] for r in document['rows']}==COMPONENTS and len(document['rows'])==3,'Exactly three unique component rows required')
    row,d=rows[0],ds[0];require(row.get('standard_prepare_exit_code')==0 and row.get('generation_ready') is True,'Row prepare/approval invalid')
    measured=document['measurement'];require(desc(measured['path'])==measured,'Native171 measurement pin mismatch')
    measurement=load(measured['path']);mounts=row['mount_candidates']
    require(len(mounts)==6 and [v['frame'] for v in mounts]==list(range(6)) and row['future_generated_component_A']==[None]*6,'Exactly six ordered mounts with null future features required')
    trials=document['hidden_trial_decision'];require(desc(trials['path'])==trials,'Independent hiddenTRIAL pin mismatch');trial_rows=load(trials['path'])['trials']
    for v in mounts:
        visible=v['visible_cloth_design_A'];hidden=v['hidden_trial_design_A'];i=v['frame']
        require(visible==measurement['frames'][i]['body_design_A_candidates'][component] and visible['measured_bone'] is False and visible['future_component_feature_A'] is None and v['future_generated_component_A'] is None,'Visible mount must preserve measured design-only source/null')
        if visible['point'] is None:
            matching=[t for t in trial_rows if t['component']==component and t['frame']==i]
            require(len(matching)==1 and hidden is not None and 'HIDDEN TRIAL' in hidden['kind'],'Occluded mount needs separate explicit hiddenTRIAL')
            trial=matching[0];require(hidden['point']==trial['point'] and hidden['uncertainty_source_px']==trial['uncertainty_source_px'] and trial['source_visible_cloth_A'] is None and trial['future_generated_feature_A'] is None,'HiddenTRIAL cannot replace visible observation/feature')
        else:require(hidden is None,'Visible mount must not invent hiddenTRIAL')
    require(row['prompt']==d['prompt'] and desc(row['prompt']['path'])==row['prompt'],'Exact approved v002 prompt required')
    require(row['state']==d['state'] and Path(row['run_dir']).resolve()==Path(d['existing_run_dir']).resolve(),'Run/state mismatch')
    raw=Path(row['raw_output_planned']).resolve();require(raw.is_relative_to(BASE) and raw==Path(d['raw_output_planned']).resolve(),'Raw row destination mismatch')
    refs=row['reference_images_in_order'];require(len(refs)==5 and [r['file'] for r in refs]==[r['file'] for r in d['reference_images_in_order']],'Exact ordered five reference files required')
    for ref in refs:require(Path(ref['file']['path']).resolve().is_relative_to(ROOT) and desc(ref['file']['path'])==ref['file'],'Reference size/SHA mismatch')
    return document,row,raw

def archive_path(topic):
    parent=ROOT/'过程图稿与视频';out=(parent/topic).resolve();require(out.parent==parent and not out.exists(),'Archive topic must be fresh direct child');return out

def archive(out,files,present,status):
    (out/'原件').mkdir(parents=True,exist_ok=False);(out/'展示副本').mkdir();rows=[]
    for i,p in enumerate(dict.fromkeys(Path(x).resolve() for x in files)):
        target=out/'原件'/f'{i:03d}-{p.name}';copy_new(p,target);rows.append(dict(desc(p),retained_relative=target.relative_to(out).as_posix()))
    for i,p in enumerate(present):copy_new(Path(p).resolve(),out/'展示副本'/f'{i:02d}-{Path(p).name}')
    write_new(out/'source-version-status-index.json',{'files':rows,'status':status,'formal_complete_units':0})
    with (out/'README.md').open('x',encoding='utf-8') as f:f.write(status+'\nExact originals/presentation copies. Not acceptance or publication.\n')

@contextmanager
def writer_lock():
    CONTROL.mkdir(parents=True,exist_ok=True);p=CONTROL/'.native-armor-primary2-writer.lock'
    fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        os.write(fd,encoded({'pid':os.getpid(),'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}));os.close(fd);fd=None
        yield
    finally:
        if fd is not None:os.close(fd)
        p.unlink() # Crash leaves stale lock: no automatic lock stealing/retry.

def publish_ledger(expected_sha,new,number,mode):
    require(desc(LEDGER)['sha256']==expected_sha,'Ledger changed after plan; stop, no overwrite')
    tmp=CONTROL/f'ledger-publish-request{number}-{mode}.tmp'
    write_new(tmp,new);require(desc(LEDGER)['sha256']==expected_sha,'Concurrent ledger change; preserve candidate')
    os.replace(tmp,LEDGER) # Only canonical ledger is replaced; all evidence/raw files are exclusive-create.
    require(load(LEDGER)==new,'Ledger readback mismatch')

def plan(args):
    initial=desc(LEDGER);l=load(LEDGER);validate_ledger(l);number=args.number
    require(number in (172,173,174),'This candidate is scoped to planned172..174')
    request_path=CONTROL/f'generation-request{number}-v001.json';out=archive_path(args.archive_topic)
    if args.mode=='reserve':
        doc,row,raw=approved_row(args.handoff,args.component);prompt=Path(row['prompt']['path']).resolve()
        require(not raw.exists(),'Raw destination exists')
        request={'request_number':number,'asset':'fairytale-'+args.component+'-'+Path(row['run_dir']).name,'component':args.component,'status':'requested_pending','source_event':'EV-048','authorization_events':['EV-040','EV-041'],'window_number':l['current_window']['number'],'requested_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt_path':prompt.as_posix(),'prompt':prompt.read_text(encoding='utf-8'),'prompt_file_sha256':row['prompt']['sha256'],'reference_images':row['reference_images_in_order'],'transparent_background':False,'backend':'image_gen.imagegen','external_api_calls':0,'host_fee_usd':None,'raw_destination_planned':raw.as_posix(),'source_handoff':desc(args.handoff),'scope':load(doc['root_input_review']['path'])['approval_scope']+'; state='+row['state']+'; feature='+row['feature_contract']+'; fit-design='+json.dumps(row['fit_window_design_px'])+'; geometry design-only, future actual feature A unmeasured','formal_complete_units':0}
        new=reserve_state(l,request);before=CONTROL/f'ledger-before-request{number}.json';after=CONTROL/f'ledger-after-request{number}-reserved.json';evidence=request_path
        for p in [request_path,before,after,CONTROL/f'generation-receipt{number}-v001.json',CONTROL/f'generation-failure{number}-v001.json']:require(not p.exists(),'Refuse existing request/evidence '+str(p))
        files=[Path(args.handoff),Path(doc['root_input_review']['path']),DRAFT,prompt,evidence,before,after,Path(__file__)]+[Path(r['file']['path']) for r in row['reference_images_in_order']]
        return locals()
    request=load(request_path);i=unique(l,number);require(l['requests'][i]==request and request['status']=='requested_pending','Not matching unique pending request')
    handoff=request['source_handoff'];require(desc(handoff['path'])==handoff,'Reserved handoff changed')
    doc,row,raw=approved_row(handoff['path'],request['component'])
    require(raw.as_posix()==request['raw_destination_planned'] and row['prompt']['path']==request['prompt_path'] and row['prompt']['sha256']==request['prompt_file_sha256'],'Reserved row/prompt mismatch')
    require(request['prompt']==Path(request['prompt_path']).read_text(encoding='utf-8') and request['reference_images']==row['reference_images_in_order'],'Reserved prompt text/orderedrefs changed')
    require(request['window_number']==8 and not raw.exists(),'Wrong reservation window or raw exists; manual recovery only')
    if args.mode=='retain':
        original=Path(args.original).resolve();require(original.is_file(),'Native original absent')
        with Image.open(original) as im:
            mode=im.mode;size=list(im.size);require(im.format=='PNG' and mode in ('RGB','RGBA'),'Native PNG RGB/RGBA required');im.verify()
        receipt=dict(request,status='generated_retained_pending_extraction',generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_native_original=desc(original),canonical_raw={'path':raw.as_posix(),'bytes':original.stat().st_size,'sha256':desc(original)['sha256']},raw_mode=mode,raw_size=size,source_pixels_modified=False,runtime_imported=False,complete_armor=False)
        evidence=CONTROL/f'generation-receipt{number}-v001.json';after=CONTROL/f'ledger-after-request{number}-generated.json';present=[original];files=[original,raw,request_path,evidence,after,Path(request['prompt_path']),Path(__file__)]
    else:
        error=Path(args.error_file).resolve();require(error.is_file(),'Failure error evidence required')
        receipt=dict(request,status='failed_native_no_image_preserved',finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=error.read_text(encoding='utf-8-sig'),error_evidence=desc(error),returned_raw_image=None,native_image_returned=False,automatic_retry=False,quota_refunded=False)
        evidence=CONTROL/f'generation-failure{number}-v001.json';after=CONTROL/f'ledger-after-request{number}-failed.json';present=[];files=[error,request_path,evidence,after,Path(request['prompt_path']),Path(__file__)]
    require(not evidence.exists() and not after.exists(),'Already finished/partial evidence; no overwrite or automatic retry')
    new=finish_state(l,request,receipt);return locals()

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    for mode in ['reserve','retain','fail']:
        a=sub.add_parser(mode);a.add_argument('--number',type=int,required=True);a.add_argument('--archive-topic',required=True);a.add_argument('--execute',action='store_true',help='Root only: mutate after explicit approval; omitted = readonly plan')
        if mode=='reserve':a.add_argument('--handoff',required=True);a.add_argument('--component',choices=sorted(COMPONENTS),required=True)
        elif mode=='retain':a.add_argument('--original',required=True)
        else:a.add_argument('--error-file',required=True)
    args=p.parse_args()
    if not args.execute:
        s=plan(args);print(json.dumps({'executed':False,'mode':args.mode,'request':args.number,'prospective_counters':counters(s['new']),'archive_planned':str(s['out'])},ensure_ascii=False));return
    with writer_lock():
        s=plan(args)
        if args.mode=='reserve':
            write_new(s['before'],s['l']);write_new(s['evidence'],s['request']);write_new(s['after'],s['new'])
        else:
            if args.mode=='retain':copy_new(s['original'],s['raw'])
            write_new(s['evidence'],s['receipt']);write_new(s['after'],s['new'])
        publish_ledger(s['initial']['sha256'],s['new'],args.number,args.mode)
        archive(s['out'],s['files'],[Path(s['row']['reference_images_in_order'][-1]['file']['path'])] if args.mode=='reserve' else s['present'],'Input reservation, no generated acceptance' if args.mode=='reserve' else 'Native result/failure preserved; extraction/fit/runtime pending')
        print(json.dumps({'executed':True,'mode':args.mode,'request':args.number,'archive':s['out'].as_posix(),'evidence':desc(s['evidence']),'counters':counters(s['new'])},ensure_ascii=False))

if __name__=='__main__':main()