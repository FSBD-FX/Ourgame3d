"""Single cross-directory image ledger; counting/retention only, no generation."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT.parent/'first-unit-animation-v003/generation-ledger.json'
TOPIC='2026-10-15_遗迹地牢环境分层_v001'
ARCHIVES=[Path('F:/Ourgame/过程图稿与视频')/TOPIC,Path('E:/OurGame/Knight/过程图稿与视频')/TOPIC]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def archive(source,relative,status):
 relative=Path(relative)
 if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe path')
 digest=sha(source);outputs=[]
 for folder in ARCHIVES:
  for category in ['原件','展示副本']:
   d=folder/category/relative
   if d.exists():
    if sha(d)!=digest:raise ValueError(f'No overwrite: {d}')
   else:d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,d)
   assert sha(d)==digest;outputs.append(str(d))
  ip=folder/'index.json';idx=read(ip) if ip.exists() else {'schema':'production-media-retention-v1','topic':TOPIC,'source_root':str(ROOT),'status':'work_in_progress_not_complete_map','files':[]}
  if not any(e['relative']==relative.as_posix() for e in idx['files']):idx['files'].append({'source':str(source),'relative':relative.as_posix(),'sha256':digest,'bytes':Path(source).stat().st_size,'status':status,'archived_utc':now()})
  write(ip,idx)
 return outputs
def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['register','complete','review','archive'])
 p.add_argument('--number',type=int);p.add_argument('--asset');p.add_argument('--prompt-file',type=Path)
 p.add_argument('--references',nargs='*',default=[]);p.add_argument('--source',type=Path);p.add_argument('--relative');p.add_argument('--status');p.add_argument('--notes')
 a=p.parse_args();l=read(LEDGER)
 if a.operation=='archive':print(json.dumps({'paths':archive(a.source,a.relative,a.status)},ensure_ascii=False));return
 if a.operation=='register':
  w=l['current_window'];assert w['requested_count']<w['request_limit'] and w['status'].startswith('active')
  assert l['single_visual_writer']=='/root/assets_prepare'
  n=l['requested_count']+1;assert n==w['first_request_number']+w['requested_count']
  e={'request_number':n,'window_number':w['number'],'asset':a.asset,'source_directory':str(ROOT),'status':'requested',
   'requested_utc':now(),'prompt_path':str(a.prompt_file),'prompt':a.prompt_file.read_text('utf-8'),
   'references':[{'path':str(Path(f)),'sha256':sha(f)} for f in a.references],
   'transparent_background':False,'backend':'image_gen.imagegen','host_fee_usd':None}
  l['requests'].append(e);l['requested_count']=n;w['requested_count']+=1
  l['batch_requested_count']=w['requested_count'];l['remaining_batch_requests']=w['request_limit']-w['requested_count']
  l['lifetime_requested_count']=l['lifetime_prior_EV038_requests']+n
  write(LEDGER,l);print(json.dumps({'registered_request':n,'current_window':w['number'],'window_used':w['requested_count'],'remaining':l['remaining_batch_requests'],'cumulative_EV039_onward':n,'lifetime':l['lifetime_requested_count']}));return
 e=next(e for e in l['requests'] if e['request_number']==a.number)
 assert e.get('source_directory')==str(ROOT)
 if a.operation=='complete':
  from PIL import Image
  t=ROOT/'raw'/f'{a.number:02}-{e["asset"]}-v001.png'
  if t.exists():raise ValueError('No overwrite')
  shutil.copy2(a.source,t);copies=archive(t,Path('raw')/t.name,'native_generated_pending_review')
  with Image.open(t) as im:size,mode=list(im.size),im.mode
  e.update(status='generated_dual_archived_pending_review',completed_utc=now(),tool_original_path=str(a.source),raw_path=str(t),sha256=sha(t),image_size=size,mode=mode,archive_paths=copies)
 else:e.update(status=a.status,review_notes=a.notes,reviewed_utc=now())
 write(LEDGER,l)
 for folder in ARCHIVES:write(folder/'generation-ledger-snapshot.json',l)
 print(json.dumps({k:e[k] for k in ['request_number','status','raw_path'] if k in e},ensure_ascii=False))
if __name__=='__main__':main()
