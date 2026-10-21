from pathlib import Path
import hashlib,json,shutil,subprocess,sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame'); HERE=Path(__file__).resolve().parent
BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen'); PY=SG/'.venv/Scripts/python.exe'
STATE='leather_farshoulder_hero_hurt'
RUN=HERE/'run-Hurt4-far-native231-shared-HD-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt远肩薄tab231共享四相标准提取_v001'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return p
def bbox(m):
 y,x=np.where(m);return None if len(x)==0 else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def main():
 assert Path(sys.executable).resolve()==PY.resolve()
 assert not RUN.exists() and not MEDIA.exists()
 inp=BASE/'lgt-hurt4-far-correction-standard-input-v002/prepared-input-v002'
 hand=json.loads((inp/'Root-Far-Hurt4-thin-tab-no-gold-correction-input-handoff-v002.json').read_text(encoding='utf-8'))
 reqpath=BASE/'generation-control-v001/generation-request231-v001.json';gen=json.loads(reqpath.read_text(encoding='utf-8'))
 raw=Path(gen['raw_destination_planned']);assert pin(raw)['sha256']=='b853ac48f3e446eb7809e0f12608dc058b129826db43f136924db918584627ce' and raw.stat().st_size==1212294
 ep=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-LGT-Hurt-far231-raw-v437/source-size-SHA256.json')
 hits=[]
 def walk(v):
  if isinstance(v,dict):
   if v.get('sha256')==pin(raw)['sha256'] and 'retained_relative' in v:hits.append(v)
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(json.loads(ep.read_text(encoding='utf-8')));assert hits
 eraw=ep.parent/hits[0]['retained_relative'];assert raw.read_bytes()==eraw.read_bytes()
 assert pin(Path(hand['request']['path']))==hand['request']
 prompt=Path(gen['prompt_path']);assert pin(prompt)['sha256']==gen['prompt_file_sha256']
 for ref in gen['reference_images']:assert pin(Path(ref['file']['path']))==ref['file'] and ref['already_retained']
 prepared=Path(hand['prepared_run']);copies=[]
 for p in sorted(prepared.rglob('*')):
  if not p.is_file() or 'prompts' in p.relative_to(prepared).parts:continue
  dst=RUN/p.relative_to(prepared);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);assert p.read_bytes()==dst.read_bytes();copies.append({'source':pin(p),'copy':pin(dst)})
 dst=RUN/f'prompts/{STATE}.txt';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prompt,dst);copies.append({'source':pin(prompt),'copy':pin(dst),'role':'Exact Root v003 prompt used by actual native231, not stale v002 ordinal prelude'})
 rawcopy=RUN/f'raw/{STATE}.png';rawcopy.parent.mkdir();shutil.copyfile(raw,rawcopy)
 wrapper=BASE/'lgt-hurt4-process-runs-v001/process-inputs-v001/shared-HD-fit-explicit-component-min-UNCHANGED.py'
 assert pin(wrapper)['sha256']=='61085b282e1f18d0195cad5f65355b67eda287a98e54a19f27c8d662f9d079f4'
 commands=[('extract-shared-whole-components',[str(PY),'-B','-X','utf8',str(wrapper),'--run-dir',str(RUN),'--min-used-pixels','256']),('compose-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','256']),('curated-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state',STATE]),('preview-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)]),('inspect-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN)])]
 receipt={'schema':'Far231-original32x30-shared-extraction-v001','native':231,'state':STATE,'F_raw':pin(raw),'E_raw':pin(eraw),'E_manifest':pin(ep),'F_E_raw_exact':True,'Root_E437_notification_received':True,'Root_twoSHA_retention':True,'raw_actual_worker_View_after_E':True,'raw_semantic_review':'Correct narrow curved brown thin tab; no230 gold rivet, broad cup or strap. Source candidate only, fit and QA unknown before commands.','native_request_actual':pin(reqpath),'actual_native_prompt':pin(prompt),'original_v002_prompt_preserved':hand['prompt'],'copied_inputs':copies,'shared_fit_wrapper_unchanged':pin(wrapper),'request_byte_exact':True,'fit_window':[32,30],'extract_and_compose_min_used_pixels':256,'no_new_threshold_reduction':True,'commands':[],'status':'STARTED','TrialAllowed':False,'Source_Content_tools_ledger_UE_modified':False,'new_curated_Viewed':False,'future_A_B_delta_coverage':None}
 requestbytes=(RUN/'sprite-request.json').read_bytes()
 failed=None
 try:
  with Image.open(raw) as im:receipt['raw_actual_size_mode']={'size':list(im.size),'mode':im.mode};assert im.size==(2172,724)
  for stage,argv in commands:
   r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',errors='replace')
   log=write(RUN/f'pipeline-logs/{stage}-v001.log',r.stdout+r.stderr);receipt['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode,'log':pin(log)})
   assert (RUN/'sprite-request.json').read_bytes()==requestbytes
   if r.returncode:raise RuntimeError(stage+' failed; original256 gate retained')
  fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));qa=json.loads((RUN/'sprite-inspect.report.json').read_text(encoding='utf-8'))
  row=fm['rows'][0];assert row['frames']==4 and row['method']=='components' and row['shared_row_fit']['per_frame_scale_normalization'] is False
  receipt.update({'shared_row_fit':row['shared_row_fit'],'extract_errors':fm['errors'],'extract_warnings':fm['warnings'],'inspect_errors':qa['errors'],'inspect_warnings':qa['warnings'],'official_inspect_ok':qa['ok']})
  frames=[]
  for i in range(4):
   p=RUN/f'curated/frame-{i}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);a=np.array(im)
   frames.append({'frame':i,'source':pin(p),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox':bbox(a[:,:,3]>0),'core128_bbox':bbox(a[:,:,3]>=128),'used_pixels':int(np.count_nonzero(a[:,:,3])),'core128_used_pixels':int(np.count_nonzero(a[:,:,3]>=128)),'A':None,'B':None,'integer_delta':None,'fit_accepted':False})
  receipt['frames']=frames
  assert not fm['errors'] and not qa['errors']
  receipt['status']='STANDARD_FIVE_STEPS_0_INSPECT_WARNINGS_RETAINED_WAIT_ROOT_E_AND_SEMANTIC_FIT_REVIEW' if qa['warnings'] else 'STANDARD_FIVE_STEPS_0_NUMERIC_QA0_WAIT_ROOT_E_AND_SEMANTIC_FIT_REVIEW'
 except BaseException as e:
  failed=e;receipt.update({'status':'FAILED_ORIGINAL_GATE_PRESERVED_NO_ACCEPTANCE','failure':repr(e)})
 finally:
  for report in ['frames/frames-manifest.json','sprite-sheet-alpha.report.json','sprite-inspect.report.json']:
   p=RUN/report
   if p.exists():receipt.setdefault('original_reports',[]).append({'file':pin(p),'data':json.loads(p.read_text(encoding='utf-8'))})
  rp=write(RUN/'extraction-receipt-v001.json',receipt)
  write(RUN/'extracted-files-freeze-v001.json',{'schema':'Far231-extracted-files-freeze-v001','status':receipt['status'],'files':[pin(p) for p in sorted(RUN.rglob('*')) if p.is_file()],'new_curated_View':False,'TrialAllowed':False})
  (MEDIA/'原件').mkdir(parents=True);shutil.copytree(RUN,MEDIA/'原件/独立标准process-run');(MEDIA/'展示副本').mkdir()
  for folder in ['curated','qa']:
   for p in sorted((RUN/folder).glob('*')):
    if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copyfile(p,MEDIA/'展示副本'/p.name)
  write(MEDIA/'来源-版本-状态索引.json',{'date':'2026-10-18','topic':'Hurt远肩薄tab231共享四相标准提取','version':'v001','source':RUN.as_posix(),'receipt':pin(rp),'status':receipt['status'],'new_curated_View':False,'TrialAllowed':False,'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]})
  print(json.dumps({'F_canonical':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'receipt':pin(rp),'status':receipt['status'],'commands':[{k:c[k] for k in ['stage','exit_code']} for c in receipt['commands']],'frames':receipt.get('frames'),'shared_row_fit':receipt.get('shared_row_fit'),'failure':receipt.get('failure'),'newmedia_View':False},ensure_ascii=False,indent=2))
 if failed:raise failed
if __name__=='__main__':main()
