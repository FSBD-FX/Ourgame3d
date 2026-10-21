"""Standard SG whole-component/shared-row Death237–239 extraction; NEW runs/archive only."""
from pathlib import Path
import argparse,json,hashlib,subprocess,shutil,sys
from PIL import Image
import numpy as np
C=Path(__file__).resolve().parent;BASE=C.parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
WRAPPER=ROOT/'source-assets/production/fairytale-hero-state-gap-v001/lgt-hurt4-process-runs-v001/process-inputs-v001/shared-HD-fit-explicit-component-min-UNCHANGED.py'
IDS={'Chest':237,'ShoulderNear':238,'ShoulderFar':239}

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists(),str(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str)else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def need(v,why):
 if not v:raise ValueError(why)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--component',choices=list(IDS),required=True);ap.add_argument('--admission',required=True);ap.add_argument('--version',default='v001');a=ap.parse_args()
 need(Path(sys.executable).resolve()==PY.resolve(),'Use skill SG .venv interpreter, no fallback')
 need(a.version.startswith('v')and a.version[1:].isdigit(),'Version must be vNNN')
 for row in read(C/'standard-process-freeze-v001.json')['files']:
  p=C/row['path'];f=pin(p);need(f['bytes']==row['bytes']and f['sha256']==row['sha256'],'Frozen process helper differs')
 contract=read(C/'process-contract-v001.json');need(pin(WRAPPER)==contract['shared_row_wrapper'],'Project shared-row wrapper changed')
 adm=read(a.admission);need(adm['schema']=='Death5-actual-Root-E-raw-admission-v001'and adm['component']==a.component and adm['native_id']==IDS[a.component] and adm['Root_actual_E_authorized']is True and adm['raw_actually_Viewed_after_E']is True,'Actual Root E authority and real raw View required; templates cannot execute')
 raw=Path(adm['F_raw']['path']);eraw=Path(adm['E_raw']['path']);need(pin(raw)==adm['F_raw']and pin(eraw)==adm['E_raw']and raw.read_bytes()==eraw.read_bytes(),'Actual raw F/E source pins differ')
 need(pin(Path(adm['E_manifest']['path']))==adm['E_manifest'],'Actual E manifest pin differs')
 matches=[];emanifest=Path(adm['E_manifest']['path'])
 def retained(z):
  if isinstance(z,dict):
   if z.get('sha256')==adm['F_raw']['sha256']and z.get('bytes')==adm['F_raw']['bytes']and 'retained_relative'in z and (emanifest.parent/Path(z['retained_relative'])).resolve()==eraw.resolve():matches.append(z)
   for v in z.values():retained(v)
  elif isinstance(z,list):
   for v in z:retained(v)
 retained(read(emanifest));need(matches,'Raw is not a matching retained member of its actual E manifest')
 packet_path=BASE/'armor-input-Far-tiny-floor-amendment-v002/Root-Death5-three-armor-inputpacket-v002.json';need(pin(packet_path)==contract['Root_inputpacket'],'Actual frozen processing packet changed');packet=read(packet_path);entry=next(x for x in packet['components']if x['component']==a.component);prepared=Path(entry['prepared_run']);state=entry['state'];floor=entry['minimum_used_pixels_extract_and_compose'];need(floor==(256 if a.component=='ShoulderFar'else 512),'Wrong predeclared component floor')
 for role in ['request','prompt','references','official_guide']:need(pin(Path(entry[role]['path']))==entry[role],'Frozen official input differs: '+role)
 run=BASE/'process-runs-v001'/f'run-Death5-{a.component}-native{IDS[a.component]}-shared-HD-{a.version}';media=ROOT/'过程图稿与视频'/f'2026-10-18_钟盔Death5_{a.component}{IDS[a.component]}标准提取_{a.version}'
 need(not run.exists()and not media.exists(),'Preserve earlier/failed output; choose a NEW version')
 run.parent.mkdir(exist_ok=True);shutil.copytree(prepared,run)
 q=read(run/'sprite-request.json');need(list(q['states'])==[state]and q['states'][state]['frames']==5 and q['states'][state]['durations_ms']==[200]*5 and q['states'][state]['loop']is False,'Actual standard5 nonloop state changed')
 need(q['fit']['shared_row_scale']and q['fit']['pixel_unfake']is False and q['chroma']=={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005},'Actual shared HD/chroma defaults must be explicit')
 target=run/f'raw/{state}.png';target.parent.mkdir(exist_ok=True);need(not target.exists(),'Prepared run must not contain previous raw');shutil.copy2(raw,target)
 with Image.open(raw)as im:raw_dimensions=list(im.size)
 commands=[('extract-whole-components-shared',[str(PY),'-B','-X','utf8',str(WRAPPER),'--run-dir',str(run),'--min-used-pixels',str(floor)]),('compose-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels',str(floor)]),('curated-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state]),('preview-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]),('inspect-official',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run)])]
 receipt=dict(schema='Death5-official-shared-component-processing-receipt-v001',native_id=IDS[a.component],component=a.component,state=state,actual_admission=pin(Path(a.admission)),F_raw=pin(raw),E_raw=pin(eraw),raw_dimensions=raw_dimensions,Root_E_authorized=True,source_raw_actually_Viewed=True,prepared_source=pin(Path(entry['request']['path'])),request_copy_byte_exact=pin(run/'sprite-request.json')['sha256']==entry['request']['sha256'],whole_component=True,shared_row_scale=True,per_frame_normalization=False,extract_compose_min_used_pixels=floor,commands=[],new_curated_Viewed=False,Source_Content_tools_ledger_UE_modified=False,TrialAllowed=False)
 write(run/'extraction-start-v001.json',receipt);failure=None
 try:
  for stage,argv in commands:
   result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=run/f'pipeline-logs/{stage}-v001.log';write(log,result.stdout+result.stderr);receipt['commands'].append(dict(stage=stage,argv=argv,exit_code=result.returncode,log=pin(log)))
   need(result.returncode==0,'Official stage failed: '+stage)
  manifest=read(run/'frames/frames-manifest.json');row=next(x for x in manifest['rows']if x['state']==state);fit=row['shared_row_fit'];need(row['method']=='components'and row['frames']==5 and fit['per_frame_scale_normalization']is False,'Actual shared-row wholecomponent contract failed')
  receipt['shared_row_fit']=fit;receipt['frames']=[]
  for i in range(5):
   p=run/f'curated/frame-{i}.png'
   with Image.open(p)as im:need(im.mode=='RGBA'and im.size==(512,512),'Wrong curated dimensions/mode');rgba=np.asarray(im)
   alpha=rgba[:,:,3];need(np.count_nonzero(alpha)>=floor,'Actual frame failed predeclared source floor')
   receipt['frames'].append(dict(frame=i,source=pin(p),RGBA_sha256=hashlib.sha256(rgba.tobytes()).hexdigest(),alpha_nonzero=int(np.count_nonzero(alpha)),alpha128=int(np.count_nonzero(alpha>=128)),bbox=Image.fromarray(rgba).getbbox()))
  inspect=read(run/'sprite-inspect.report.json');receipt['official_inspect']=pin(run/'sprite-inspect.report.json');receipt['inspect_errors']=inspect.get('errors',[]);receipt['inspect_warnings']=inspect.get('warnings',[]);receipt['source_pose_or_density_accepted']=False;receipt['status']='FIVE_OFFICIAL_STAGES_EXIT0_SOURCE_REVIEW_PENDING'if not receipt['inspect_warnings']else'FIVE_OFFICIAL_STAGES_EXIT0_ORIGINAL_WARNING_RETAINED_SOURCE_REVIEW_PENDING'
 except Exception as exc:failure=str(exc);receipt['status']='FAILED_PRESERVED';receipt['failure']=failure
 final=run/'extraction-receipt-v001.json';write(final,receipt)
 original=media/'原件/官方处理run完整包';original.parent.mkdir(parents=True);shutil.copytree(run,original);show=media/'展示副本';show.mkdir()
 for d in ['curated','qa']:
  if (run/d).exists():shutil.copytree(run/d,show/d)
 write(media/'README.md','Original shared-row/whole-component official processing; all logs/QA and failures/warnings retained. NEWcurated/QA media UNVIEWED awaitingRootE beforeView. No local recolor/paint/resize workaround, no sourcefit/native/Trial acceptance.\n')
 write(media/'source-version-status-index.json',dict(schema='Death5-standard-process-F-index-v001',status=receipt['status'],receipt=pin(final),files=[pin(p)for p in sorted(media.rglob('*'))if p.is_file()],new_curated_Viewed=False,TrialAllowed=False))
 write(run/'extracted-files-freeze-v001.json',dict(files=[pin(p)for p in sorted(run.rglob('*'))if p.is_file()],new_curated_Viewed=False,TrialAllowed=False))
 print(json.dumps(dict(F_canonical=media.as_posix(),receipt=pin(final),status=receipt['status'],commands=[{'stage':x['stage'],'exit_code':x['exit_code']}for x in receipt['commands']],frames=receipt.get('frames'),failure=failure,new_curated_View=False),ensure_ascii=False))
 if failure:raise SystemExit(3)
if __name__=='__main__':main()
