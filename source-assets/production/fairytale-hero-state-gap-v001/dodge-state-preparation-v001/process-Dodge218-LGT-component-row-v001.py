"""Candidate-only shared-row standard processing; requires an actual E-retained native raw.

Run with the sprite-gen venv. This script never invokes image generation or UE,
never rewrites the frozen prepared input, and preserves all failed QA reports.
"""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path('F:/Ourgame'); HERE=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
def bbox(m):
 y,x=np.where(m);return None if len(x)==0 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def find_retained(v,sha):
 hits=[]
 def visit(x):
  if isinstance(x,dict):
   if x.get('sha256')==sha and 'retained_relative' in x:hits.append(x)
   for z in x.values():visit(z)
  elif isinstance(x,list):
   for z in x:visit(z)
 visit(v);return hits
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--component',choices=['Chest','ShoulderNear','ShoulderFar'],required=True)
 ap.add_argument('--native-id',type=int,required=True)
 ap.add_argument('--raw',type=Path,required=True)
 ap.add_argument('--sha256',required=True)
 ap.add_argument('--e-index',type=Path,required=True)
 ap.add_argument('--actual-native-prompt',type=Path,required=True)
 ap.add_argument('--generation-receipt',type=Path)
 args=ap.parse_args()
 assert Path(sys.executable).resolve()==PY.resolve()
 handpath=HERE/'armor-standard-input-v001/Root-Dodge218-three-LGT-official-input-handoff-v001.json'
 hand=read(handpath);row=next(r for r in hand['rows'] if r['component']==args.component)
 for field in ['official_request','official_prompt','native_prompt','references_json','official_guide']:
  assert pin(Path(row[field]['path']))==row[field]
 raw=args.raw.resolve();assert raw.is_relative_to(HERE.resolve()) and pin(raw)['sha256']==args.sha256
 hits=find_retained(read(args.e_index),args.sha256);assert hits
 eraw=args.e_index.parent/hits[0]['retained_relative']
 for _ in range(2):assert raw.read_bytes()==eraw.read_bytes() and pin(raw)['sha256']==pin(eraw)['sha256']
 # Actual used prompt is supplied explicitly, rather than silently assuming the prepared prompt was used.
 assert args.actual_native_prompt.is_file()
 token={'Chest':'chest','ShoulderNear':'nearshoulder','ShoulderFar':'farshoulder'}[args.component]
 state=row['state'];run=HERE/f'official-process-runs-v001/{token}-native{args.native_id}/run-shared-HD-v001'
 media=ROOT/f'过程图稿与视频/2026-10-18_钟盔Dodge棕皮{token}{args.native_id}共享四相标准提取_v001'
 assert not run.exists() and not media.exists()
 prepared=Path(row['official_prepared_run']);copies=[]
 for p in sorted(prepared.rglob('*')):
  if not p.is_file() or 'prompts' in p.relative_to(prepared).parts:continue
  dst=run/p.relative_to(prepared);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
  assert p.read_bytes()==dst.read_bytes();copies.append({'source':pin(p),'copy':pin(dst)})
 prompt=run/f'prompts/{state}.txt';prompt.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(args.actual_native_prompt,prompt)
 rawcopy=run/f'raw/{state}.png';rawcopy.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,rawcopy)
 wrapper=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/lgt-hurt4-process-runs-v001/process-inputs-v001/shared-HD-fit-explicit-component-min-UNCHANGED.py'
 assert pin(wrapper)['sha256']=='61085b282e1f18d0195cad5f65355b67eda287a98e54a19f27c8d662f9d079f4'
 minimum=row['component_min_used_pixels'];assert minimum=={'Chest':512,'ShoulderNear':512,'ShoulderFar':256}[args.component]
 commands=[('extract-shared-components',[str(PY),'-B','-X','utf8',str(wrapper),'--run-dir',str(run),'--min-used-pixels',str(minimum)]),
  ('compose-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels',str(minimum)]),
  ('curated-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state]),
  ('preview-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]),
  ('inspect-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run)])]
 receipt={'schema':'Dodge218-LGT-original-gates-shared-row-process-v001','native_id':args.native_id,'component':args.component,'state':state,'prepared_handoff':pin(handpath),'F_raw':pin(raw),'E_raw':pin(eraw),'E_index':pin(args.e_index),'current_F_E_twoSHA_equal':True,'actual_native_prompt':pin(args.actual_native_prompt),'prepared_native_prompt':row['native_prompt'],'generation_receipt':pin(args.generation_receipt) if args.generation_receipt else None,'copied_inputs':copies,'frozen_prepared_inputs_modified':False,'request_byte_exact':True,'fit_window_predeclared':row['maximum_window_px'],'extract_compose_min_used_pixels':minimum,'shared_fit_wrapper_unchanged':pin(wrapper),'commands':[],'status':'STARTED','new_curated_Viewed':False,'source_semantic_fit_accepted':False,'future_A_B_integer_delta_coverage':None,'runtime_import_receipts':None,'TrialAllowed':False,'FinalAccepted':False}
 requestbytes=(run/'sprite-request.json').read_bytes();failure=None
 try:
  with Image.open(raw) as im:receipt['actual_raw_size_mode']={'size':list(im.size),'mode':im.mode}
  for stage,argv in commands:
   result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',errors='replace')
   log=write(run/f'pipeline-logs/{stage}.log',result.stdout+result.stderr)
   receipt['commands'].append({'stage':stage,'argv':argv,'exit_code':result.returncode,'log':pin(log)})
   assert (run/'sprite-request.json').read_bytes()==requestbytes
   if result.returncode:raise RuntimeError(f'{stage} failed: original gate{minimum} retained, no source acceptance')
  fm=read(run/'frames/frames-manifest.json');qa=read(run/'sprite-inspect.report.json');fr=fm['rows'][0]
  assert fr['frames']==4 and fr['method']=='components' and fr['shared_row_fit']['per_frame_scale_normalization'] is False
  receipt.update({'shared_row_fit':fr['shared_row_fit'],'extract_errors':fm['errors'],'extract_warnings':fm['warnings'],'inspect_errors':qa['errors'],'inspect_warnings':qa['warnings'],'official_inspect_ok':qa['ok']})
  frames=[]
  for i in range(4):
   p=run/f'curated/frame-{i}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);a=np.array(im)
   frames.append({'frame':i,'curated':pin(p),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox':bbox(a[:,:,3]>0),'core128_bbox':bbox(a[:,:,3]>=128),'used_pixels':int(np.count_nonzero(a[:,:,3])),'core128_used_pixels':int(np.count_nonzero(a[:,:,3]>=128)),'actual_A_B_integer_delta':None,'sourcefit_accepted':False})
  receipt['frames']=frames;assert not fm['errors'] and not qa['errors']
  receipt['status']='FIVE_STEPS_ZERO_ERRORS_ORIGINAL_WARNINGS_RETAINED_WAIT_E_ACTUAL_REVIEW' if qa['warnings'] else 'FIVE_STEPS_NUMERIC_QA0_WAIT_E_ACTUAL_SOURCE_AND_FIT_REVIEW'
 except BaseException as ex:
  failure=ex;receipt.update({'status':'FAILED_ORIGINAL_GATE_PRESERVED_NO_ACCEPTANCE','failure':repr(ex)})
 finally:
  for name in ['frames/frames-manifest.json','sprite-sheet-alpha.report.json','sprite-inspect.report.json']:
   p=run/name
   if p.exists():receipt.setdefault('original_reports',[]).append({'file':pin(p),'data':read(p)})
  rp=write(run/'extraction-receipt-v001.json',receipt)
  freeze=write(run/'extraction-files-freeze-v001.json',{'schema':'Dodge218-LGT-component-extracted-freeze-v001','script':pin(Path(__file__)),'status':receipt['status'],'files':[pin(p) for p in sorted(run.rglob('*')) if p.is_file()],'new_curated_View':False,'TrialAllowed':False})
  (media/'原件').mkdir(parents=True);shutil.copytree(run,media/'原件/独立标准process-run');(media/'展示副本').mkdir()
  for folder in ['curated','qa']:
   for p in sorted((run/folder).glob('*')):
    if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copyfile(p,media/'展示副本'/p.name)
  write(media/'来源-版本-状态索引.json',{'date':'2026-10-18','topic':f'Dodge棕皮{token}{args.native_id}共享四相标准提取','version':'v001','source':run.as_posix(),'status':receipt['status'],'receipt':pin(rp),'freeze':pin(freeze),'newmedia_View':False,'TrialAllowed':False,'files':[pin(p) for p in sorted(media.rglob('*')) if p.is_file()]})
  print(json.dumps({'canonical_F_media':media.as_posix(),'files':sum(p.is_file() for p in media.rglob('*')),'bytes':sum(p.stat().st_size for p in media.rglob('*') if p.is_file()),'receipt':pin(rp),'status':receipt['status'],'commands':[{k:r[k] for k in ['stage','exit_code']} for r in receipt['commands']],'frames':receipt.get('frames'),'shared_row_fit':receipt.get('shared_row_fit'),'failure':receipt.get('failure'),'newmedia_View':False},ensure_ascii=False,indent=2))
 if failure:raise failure
if __name__=='__main__':main()
