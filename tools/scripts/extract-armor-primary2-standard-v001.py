"""Candidate: standard four-stage armor row extraction. Root executes it.
No generation/import/ledger mutation or explicit image viewing. Default validates only.
"""
from pathlib import Path
from datetime import datetime
import argparse,difflib,hashlib,json,subprocess,sys
from PIL import Image
ROOT=Path('F:/Ourgame')
BASE=ROOT/'source-assets/production/fairytale-armor-sword-primary2-v001'
CONTROL=BASE/'generation-control-v001'
LEDGER=ROOT/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
HANDOFF=BASE/'primary2-macro-native-handoff-approved-v002.json'
HANDOFF_SHA='0342bbf095edec2d5d973bc28ed33f54a141827bf4c5d126238d9124043d5148'
DURATIONS=[75,75,60,60,135,135]
TOOLS=[('extract-shared-row',ROOT/'tools/scripts/extract-sprite-shared-row-scale.py','2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'),('compose-atlas',SG/'scripts/compose_sprite_atlas.py','a7475830b99720b69bc645423a2f9aee40d03dad0e7d589ad4756526648a61aa'),('export-curated',SG/'scripts/export_curated_pngs.py','dcf7910f44a3f43006a43379c0464c88ed7cc3213e3a8062edd59b9009960e1e'),('preview',SG/'scripts/preview_animation.py','ff4aa5d1bcfae4731a09732da96d24f540707b834df5cba85b910f88df016496')]

def require(v,msg):
 if not v:raise ValueError(msg)
def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def unchanged(rows):
 return [r['Path'] for r in rows if not Path(r['Path']).is_file() or (fact(r['Path'])['bytes'],fact(r['Path'])['sha256'])!=(r['Bytes'],r['SHA256'])]

def admit(component,number,version):
 require(Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve(),'Use sprite-gen dedicated venv')
 require(number in (172,173,174) and 1<=version<=999,'This candidate targets Root172..174 trial only')
 require(fact(HANDOFF)['sha256']==HANDOFF_SHA,'Approved handoff changed')
 doc=load(HANDOFF);rows=[r for r in doc['rows'] if r['component']==component];require(len(rows)==1,'Unique component row required');row=rows[0]
 run=Path(row['run_dir']).resolve();require(run.is_relative_to(BASE),'Run escapes armor family')
 state=row['state'];raw=Path(row['raw_output_planned']).resolve();require(raw.parent==run/'raw','Wrong run raw destination')
 receipt_path=CONTROL/f'generation-receipt{number}-v001.json';receipt=load(receipt_path)
 require(receipt['request_number']==number and receipt['component']==component and receipt['status']=='generated_retained_pending_extraction','Unique generated matching receipt required')
 require(receipt['source_handoff']==fact(HANDOFF) and receipt['canonical_raw']==fact(raw) and receipt['raw_destination_planned']==raw.as_posix(),'Receipt/raw sizeSHA/path mismatch')
 require(receipt['prompt_file_sha256']==row['prompt']['sha256'] and fact(row['prompt']['path'])==row['prompt'],'Prompt changed')
 require(receipt['reference_images']==row['reference_images_in_order'],'Reserved orderedrefs changed')
 for r in row['reference_images_in_order']:require(fact(r['file']['path'])==r['file'],'Reference file changed')
 ledger=load(LEDGER);matches=[r for r in ledger['requests'] if r['request_number']==number]
 require(len(matches)==1 and matches[0]['component']==component and matches[0]['canonical_raw']==receipt['canonical_raw'] and matches[0]['prompt_file_sha256']==receipt['prompt_file_sha256'],'Ledger selected receipt binding mismatch')
 require(row['frame_count']==6 and row['durations_ms']==DURATIONS and row['shared_row_scale'] is True and row['per_frame_normalization'] is False,'Unchanged6/sharedrow/timing contract required')
 request=run/'sprite-request.json';before=request.read_bytes();req=json.loads(before)
 require(req['states'][state]['frames']==6 and req['states'][state]['durations_ms']==DURATIONS and req['states'][state]['loop'] is False and req['fit']['shared_row_scale'] is True,'Standard request contract changed')
 out=BASE/f'{component.lower()}-extraction-v{version:03d}';require(not out.exists(),'Fresh extraction evidence dir required; no retry/overwrite')
 for d in ['frames','qa','curated']:require(not any(p.is_file() for p in (run/d).rglob('*')),'Prior derived files exist: '+d)
 for name in ['sprite-sheet-alpha.png','sprite-sheet-alpha.report.json','manifest.json']:require(not (run/name).exists(),'Prior derived artifact exists: '+name)
 source_freeze=BASE/'input-freeze-v001.json';f=load(source_freeze);require(f['FileCount']==40 and not unchanged(f['Files']),'Original40 prepared inputs changed')
 for _,tool,pin in TOOLS:require(fact(tool)['sha256']==pin,'Pinned standard/shared tool changed')
 return doc,row,run,state,raw,receipt_path,out,request,before,f

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--component',choices=['Chest','NearShoulder','FarShoulder'],required=True);p.add_argument('--number',type=int,required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--execute',action='store_true');a=p.parse_args()
 doc,row,run,state,raw,native_receipt,out,request,before,original_freeze=admit(a.component,a.number,a.version)
 if not a.execute:
  print(json.dumps({'executed':False,'component':a.component,'native_request':a.number,'raw':fact(raw),'native_receipt':fact(native_receipt),'out_planned':out.as_posix(),'standard_steps':[x[0] for x in TOOLS]},ensure_ascii=False));return 0
 out.mkdir();backup=out/'sprite-request-before-extraction-exact.json'
 with backup.open('xb') as f:f.write(before)
 commands=[];frames=[];failure=None;metadata={};request_changed=False
 try:
  for name,tool,_ in TOOLS:
   argv=[sys.executable,'-X','utf8','-B',str(tool),'--run-dir',str(run)]+(['--state',state] if name=='export-curated' else [])
   result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=out/(name+'.log');write(log,result.stdout+result.stderr)
   commands.append({'name':name,'argv':argv,'tool':fact(tool),'exit_code':result.returncode,'log':fact(log)})
   after=request.read_bytes()
   if after!=before:
    request_changed=True
    with (out/'sprite-request-after-auto-change-exact.json').open('xb') as f:f.write(after)
    write(out/'request-auto-change.patch',''.join(difflib.unified_diff(before.decode('utf-8-sig').splitlines(True),after.decode('utf-8-sig').splitlines(True),fromfile='frozen-before',tofile='native-auto-change')))
    raise RuntimeError('Standard tool changed original request; preserved before/after, STOPPED. No restoration/continuation.')
   require(not unchanged(original_freeze['Files']),'Standard tool changed another frozen prepared input; STOPPED')
   require(result.returncode==0,name+' failed; no following stage or QA relaxation')
  manifest=load(run/'frames/frames-manifest.json');atlas=load(run/'sprite-sheet-alpha.report.json')
  require(manifest['ok'] and not manifest['errors'] and not manifest['warnings'] and atlas['ok'],'Unmodified strict shapeQA rejected')
  require(len(manifest['rows'])==1,'Exactly one isolated component row required')
  shared=manifest['rows'][0]['shared_row_fit'];require(shared['per_frame_scale_normalization'] is False,'No per-frame fit')
  runtime=load(run/'manifest.json');timing=runtime['animation']['rows'][state]['durations_ms'];require(runtime['animation']['rows'][state]['loop'] is False,'No loop substitution')
  with Image.open(run/f'qa/{state}.gif') as gif:
   gif_timing=[]
   for i in range(gif.n_frames):gif.seek(i);gif_timing.append(gif.info.get('duration'))
  require(gif.n_frames==6,'Six standardpreview frames required')
  for i in range(6):
   q=run/f'curated/frame-{i}.png'
   with Image.open(q) as im:
    require(im.mode=='RGBA' and im.size==(512,512),'Actual512RGBA required');alpha=im.getchannel('A');bbox=alpha.getbbox();require(bbox is not None and alpha.getextrema()==(0,255),'Nonempty nativealpha required')
    width,height=bbox[2]-bbox[0],bbox[3]-bbox[1];require(width<=row['fit_window_design_px'][0] and height<=row['fit_window_design_px'][1],'Actual bbox exceeds unchanged shared fit design window')
   frames.append({'frame':i,'source':fact(q),'source_canvas':[512,512],'alpha_bbox_diagnostic_only':list(bbox),'alpha_bbox_size_diagnostic_only':[width,height],'actual_component_feature_A':None,'actual_facing':None,'semantic_or_bone_measurement':False,'new_output_viewed':False})
  require(len({r['source']['sha256'] for r in frames})==6,'Six unique source frames required; no clone workaround')
  metadata={'frames_manifest':fact(run/'frames/frames-manifest.json'),'atlas_report':fact(run/'sprite-sheet-alpha.report.json'),'QA_errors':manifest['errors'],'QA_warnings':manifest['warnings'],'shared_row_ratio':shared['scale'],'shared_row_fit':shared,'unique_source_pngs':6,'actual_atlas_durations_ms':timing,'actual_gif_durations_ms':gif_timing,'timing_contract_passed':timing==DURATIONS and gif_timing==DURATIONS}
  write(out/'standard-timing-diagnosis-v001.json',{'requested_ms':DURATIONS,'requested_total_ms':540,'actual_atlas_ms':timing,'actual_atlas_total_ms':sum(timing),'actual_gif_ms':gif_timing,'actual_gif_total_ms':sum(gif_timing),'timing_contract_passed':metadata['timing_contract_passed'],'known_boundary':'Standard fps10 commonly yields600ms, different from existing540ms kernel. No retime or timing acceptance.','compose_impl':fact(SG/'sprite_gen/compose/compose_atlas.py'),'preview_impl':fact(SG/'sprite_gen/qa/preview.py'),'shared_tools_modified':False,'motion_accepted':False})
 except Exception as error:failure={'type':type(error).__name__,'message':str(error)}
 final_request=request.read_bytes();mismatches=unchanged(original_freeze['Files'])
 receipt={'schema':'native171-armor-primary2-standard-extraction-trial-v1','created_local':datetime.now().astimezone().isoformat(),'component':a.component,'native_request':a.number,'native_receipt':fact(native_receipt),'raw':fact(raw),'approved_handoff':fact(HANDOFF),'original40_input_freeze':fact(BASE/'input-freeze-v001.json'),'request_before':fact(backup),'request_after':fact(request),'request_exact_unchanged':final_request==before,'request_auto_changed':request_changed,'frozen_preparation_mismatches':mismatches,'commands':commands,'frames':frames,'metadata':metadata,'failure':failure,'shape_pipeline_passed':failure is None,'future_actual_component_A':[None]*6,'feature_contract_not_yet_verified':row['feature_contract'],'fit_window_design_only':row['fit_window_design_px'],'new_outputs_viewed':False,'registration_or_motion_accepted':False,'timing_contract_passed':metadata.get('timing_contract_passed',False),'native_called':False,'UE_import_called':False,'formal_complete_units':0}
 rp=out/'extraction-receipt-v001.json';write(rp,receipt)
 files=sorted(set(p.resolve() for p in list(run.rglob('*'))+list(out.rglob('*')) if p.is_file()))+[Path(__file__).resolve()]
 fp=out/('extracted-freeze-v001.json' if failure is None else 'extracted-failure-freeze-v001.json')
 write(fp,{'schema':'armor-primary2-standard-extracted-trial-freeze-v1','created_local':datetime.now().astimezone().isoformat(),'files':[fact(p) for p in files],'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'failure':failure,'shape_pipeline_passed':failure is None,'timing_contract_passed':metadata.get('timing_contract_passed',False),'new_outputs_viewed':False,'feature_A_measured':False,'accepted':False,'formal_complete_units':0})
 print(json.dumps({'freeze':fact(fp),'receipt':fact(rp),'failure':failure,'shape_pipeline_passed':failure is None,'timing_contract_passed':metadata.get('timing_contract_passed',False),'request_exact_unchanged':final_request==before,'new_outputs_viewed':False},ensure_ascii=False));return 0 if failure is None else 1

if __name__=='__main__':raise SystemExit(main())