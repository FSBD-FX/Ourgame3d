from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from PIL import Image
import numpy as np
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent;INPUT=HERE/'process-inputs-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--token',choices=['chest','nearshoulder','farshoulder'],required=True);parser.add_argument('--E-version',type=int,required=True);parser.add_argument('--expected-sha',required=True);parser.add_argument('--expected-bytes',type=int,required=True);parser.add_argument('--root-notification',required=True);parser.add_argument('--raw-whole-viewed',action='store_true');args=parser.parse_args()
 assert Path(sys.executable).resolve()==PY.resolve()
 plan=json.loads((INPUT/'three-independent-process-run-and-gated-command-plan-v001.json').read_text(encoding='utf-8'));row=next(r for r in plan['rows'] if r['token']==args.token);run=Path(row['independent_process_run']);raw=Path(row['raw_canonical_expected_from_Root']);native=row['native_request_planned']
 assert pin(raw)['sha256']==args.expected_sha and raw.stat().st_size==args.expected_bytes
 ep=list(Path('E:/OurGame/Knight/过程图稿与视频').glob(f'*v{args.E_version}/source-size-SHA256.json'));assert len(ep)==1;ep=ep[0]
 records=[]
 def walk(v):
  if isinstance(v,dict):
   if v.get('sha256')==args.expected_sha and 'retained_relative' in v:records.append(v)
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(json.loads(ep.read_text(encoding='utf-8')));assert records
 eraw=ep.parent/records[0]['retained_relative'];assert raw.read_bytes()==eraw.read_bytes()
 for f in row['copied_inputs_all_byte_exact']:
  assert pin(Path(f['source']['path']))==f['source'] and pin(Path(f['copy']['path']))==f['copy']
 for t in plan['official_tool_pins']:assert pin(Path(t['path']))==t
 assert pin(Path(plan['shared_fit_wrapper']['path']))==plan['shared_fit_wrapper']
 assert not any(p.is_file() for p in (run/'frames').rglob('*')) and not (run/'extraction-receipt-v001.json').exists()
 target=Path(row['process_raw_copy_after_E_gate_only']);assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,target);assert raw.read_bytes()==target.read_bytes()
 reqbytes=(run/'sprite-request.json').read_bytes();receipt={'schema':'Hurt227-LGT-one-row-standard-extraction-v001','component':row['component'],'native_request':native,'Root_notification':args.root_notification,'root_explicit_E_gate_received':True,'Root_reported_retention_SHA_passes':2,'actual_F_E_raw_exact':True,'F_raw':pin(raw),'E_original':pin(eraw),'E_manifest':pin(ep),'copied_process_raw':pin(target),'raw_whole_worker_Viewed_after_E':args.raw_whole_viewed,'process_input_request_unchanged':True,'minimum_used_pixels':row['explicit_min_used_pixels'],'subject_is_effect':False,'commands':[],'status':'STARTED','new_transparent_outputs_viewed':False,'future_A_B_delta_coverage':None}
 media=ROOT/f'过程图稿与视频/2026-10-18_钟盔Hurt轻甲{args.token}{native}共享四相标准提取_v001';assert not media.exists()
 failed=None
 try:
  with Image.open(target) as im:receipt['actual_raw_size_mode']={'size':list(im.size),'mode':im.mode}
  for command in row['commands_PLAN_NOT_EXECUTED']:
   r=subprocess.run(command['argv'],capture_output=True,text=True,encoding='utf-8',errors='replace');log=write(run/f'pipeline-logs/{command["stage"]}-v001.log',r.stdout+r.stderr);receipt['commands'].append({'stage':command['stage'],'argv':command['argv'],'actual_exit_code':r.returncode,'log':pin(log)})
   assert (run/'sprite-request.json').read_bytes()==reqbytes,'Requestchanged'
   assert r.returncode==0,command['stage']+'FAILED'
  fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));qa=json.loads((run/'sprite-inspect.report.json').read_text(encoding='utf-8'));manifest=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
  assert fm['errors']==fm['warnings']==[] and qa['errors']==[] and len(fm['rows'])==1
  fr=fm['rows'][0];fit=fr['shared_row_fit'];assert fr['state']==row['state'] and fr['frames']==4 and fr['method']=='components' and fit['per_frame_scale_normalization'] is False
  am=manifest['animation']['rows'][row['state']];assert (am['frames'],am['fps'],am['loop'])==(4,10,False)
  frames=[]
  for i in range(4):
   p=run/f'curated/frame-{i}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512);a=np.array(im);assert np.any(a[:,:,3])
   frames.append({'frame':i,'source':pin(p),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox':bbox(a[:,:,3]>0),'core128_bbox':bbox(a[:,:,3]>=128),'used_pixels':int(np.count_nonzero(a[:,:,3])),'core128_used_pixels':int(np.count_nonzero(a[:,:,3]>=128)),'visible_component_A':None,'body_surface_target_B':None,'integer_delta':None,'coverage_accepted':False,'identity_motion_semantics_accepted':False})
  sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native_extractor
  keyed=native_extractor.remove_chroma_background(Image.open(target),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);a=np.array(keyed);edge=np.zeros(a.shape[:2],bool);edge[0]=edge[-1]=True;edge[:,0]=edge[:,-1]=True
  rawedge={'outer1_alpha_nonzero':int(np.count_nonzero((a[:,:,3]>0)&edge)),'outer1_core128':int(np.count_nonzero((a[:,:,3]>=128)&edge)),'outermost_content_is_source_completeness_gate':True,'source_slot_layout_full_semantic_pass':None}
  receipt.update({'frames':frames,'shared_row_fit':fit,'extract_errors':fm['errors'],'extract_warnings':fm['warnings'],'inspect_errors':qa['errors'],'inspect_warnings':qa['warnings'],'raw_outer_edge_QC':rawedge,'unique_RGBA_count':len({f['RGBA_sha256'] for f in frames}),'frames_manifest':pin(run/'frames/frames-manifest.json'),'manifest':pin(run/'manifest.json'),'inspect':pin(run/'sprite-inspect.report.json')})
  assert rawedge['outer1_core128']==0,'SOURCECROPPINGedgecore'
  assert qa['warnings']==[],'INSPECT_WARNINGS_PRESERVED_NO_QA0_ADMISSION'
  with Image.open(run/f'qa/{row["state"]}.gif') as im:receipt['official_QA_GIF']={'actual_frames':im.n_frames,'encoded_loop':im.info.get('loop'),'not_native_nonloop_proof':True}
  receipt['status']='STANDARD_5STEPS_0_AND_NUMERIC_QA0_WAIT_ROOT_E_BEFORE_CURATED_VIEW'
 except BaseException as e:
  failed=e;receipt['status']='FAILED_PRESERVED_NO_ACCEPTANCE';receipt['failure']=repr(e)
 finally:
  rp=write(run/'extraction-receipt-v001.json',receipt)
  write(run/'extracted-files-freeze-v001.json',{'schema':'Hurt-LGT-one-extracted-run-freeze-v001','status':receipt['status'],'files':[pin(p) for p in sorted(run.rglob('*')) if p.is_file()],'newmedia_View':False,'Source_or_Runtime_accepted':False})
  (media/'原件').mkdir(parents=True);shutil.copytree(run,media/'原件/独立标准process-run');(media/'展示副本').mkdir()
  for p in sorted((run/'curated').glob('frame-*.png')):shutil.copyfile(p,media/'展示副本'/p.name)
  for p in sorted((run/'qa').glob('*')):
   if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copyfile(p,media/'展示副本'/p.name)
  idx={'date':'2026-10-18','topic':f'钟盔Hurt轻甲{args.token}{row["native_request_planned"]}共享四相标准提取','version':'v001','status':receipt['status'],'source':run.as_posix(),'receipt':pin(rp),'newmedia_View':False,'LGT_native_accepted':False,'files':[pin(p) for p in sorted(media.rglob('*')) if p.is_file()]}
  write(media/'来源-版本-状态索引.json',idx)
  print(json.dumps({'canonical_F_media':media.as_posix(),'receipt':pin(rp),'status':receipt['status'],'exit_codes':[c['actual_exit_code'] for c in receipt['commands']],'shared_scale':receipt.get('shared_row_fit',{}).get('scale'),'frames':receipt.get('frames'),'raw_outer_edge_QC':receipt.get('raw_outer_edge_QC'),'F_files':sum(p.is_file() for p in media.rglob('*')),'F_bytes':sum(p.stat().st_size for p in media.rglob('*') if p.is_file()),'newmedia_View':False},ensure_ascii=False,indent=2))
 if failed:raise failed
if __name__=='__main__':main()
