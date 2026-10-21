"""Retained native221/222 standard shared component-row extraction; no motion acceptance from QA."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
PREP=HERE/'move6-stomp-W6-A2-R4-generation-ready-v001';READY=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
OUT=HERE/'move221-stomp222-extraction-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫221Move与222跺击蓄力透明候选_v001'
assert Path(sys.executable).resolve()==PY.resolve();assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def cmd(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
jobs=[('move6','right_move','move','3a5ac043fd0914c2593f5aec6b5abf3d2903865e92498cef8d03e8caadb1866f','move6'),('stomp-windup6','right_stomp_windup','stomp_windup','1319905615eae4c1e0f4a8843f45e27a76d555ccb67930b63efbc8561c39e461','stomp-windup6')]
bridge=OUT/'shared-HD-fit-existing-exact.py';shutil.copyfile(HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
entries=[]
for label,state,pose,sha,contractsub in jobs:
 src=PREP/f'run-guard-{label}-v001';run=OUT/f'run-{label}-shared-HD-v001';raw=src/f'raw/right/{pose}.png';rawpin=pin(raw);assert rawpin['sha256']==sha and Image.open(raw).size==(2172,724)
 shutil.copytree(src,run)
 commands=[]
 commands.append(cmd('extract-'+label,[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(run),'--min-used-pixels','512']))
 commands.append(cmd('inspect-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states','right_idle,'+state,'--report',str(run/'inspect-report.json')]))
 commands.append(cmd('compose-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']))
 assert load_curation(run) is None
 pay=stamp_curation(run,{'version':1,'kind':'sprite-gen-curation','states':{'right_idle':{'selected':[0,1,2,3],'transforms':{}},state:{'selected':list(range(6)),'transforms':{}}}});write(run.relative_to(OUT)/'curation.json',pay)
 assert state_plan(load_curation(run),state,6)==(list(range(6)),{})
 commands.append(cmd('export-curated-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state,'--selected-only']))
 commands.append(cmd('preview-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]))
 fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((run/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok'] and ir['errors']==ir['warnings']==[]
 carried=[]
 for i in range(4):
  old=READY/f'frames/right/idle/frame-{i}.png';new=run/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)));carried.append({'frame':i,'accepted':pin(old),'reextracted':pin(new),'RGBA_equal':True})
 rows=[]
 for i in range(6):
  p=run/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.array(im);al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);assert a.shape==(512,512,4) and np.array_equal(a,np.array(Image.open(run/f'frames/right/{pose}/frame-{i}.png')))
  box=list(im.getbbox());rows.append({'frame':i,'file':pin(p),'curated_RGBA_equal':True,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT':box,'safe_canvas_margins_ltrb':[box[0],box[1],512-box[2],512-box[3]],'alpha_nonzero_pixels':int((al>0).sum()),'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'actual_leg_side_phase_and_body_floor':None})
 keyed=native.remove_chroma_background(Image.open(raw),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);ka=np.array(keyed)[:,:,3]
 edges={k:{'nonzero_alpha_pixels':int((v>0).sum()),'core128_pixels':int((v>=128).sum())} for k,v in {'left':ka[:,0],'right':ka[:,-1],'top':ka[0,:],'bottom':ka[-1,:]}.items()};assert all(v['nonzero_alpha_pixels']==0 for v in edges.values()),'Actual native edge foreground: reject crop rather than hide in curation.'
 shared=next(r['shared_row_fit'] for r in fm['rows'] if r['state']==state)
 status=('Move221 NOT accepted: Root raw review suspects same-side three-pose repetition0/3,1/4,2/5. Worker actual transparent six-frame near/far hip→knee→shoe trace after E is required; never label six-phase pass from QA.' if label=='move6' else 'Stomp222 NOT original near-lift spec pass: Root raw review suspects FAR foot lift with NEAR support. Worker actual transparent near/far leg trace after E required, then NEW authorized visual amendment if confirmed. No silent prompt change.')
 timing=('Six×125ms750ms uniform SG preview; native phase only actual accepted collision-resolved path mod128world, near/far opposite contacts0/3 intended but NOT verified.' if label=='move6' else 'Six×143ms858ms uniform SG preview; native Windup900ms exact artist sample mapping independent, no changed kernel lock450ms.')
 index=write(label+'-six-curated-source-index-v001.json',{'schema':'Guard221222-six-curated-standard-source-index-v001','state':state,'native_raw':rawpin,'raw_retention':'Root E387 two-copy SHA zero difference then Root whole-row actual View; worker standard extraction authorized.','frames':rows,'shared_row_fit':shared,'exact_existingReady209_four_RGBA':carried,'phase_or_distance_contract':pin(PREP/contractsub/'native-phase-or-distance-contract-v001.json'),'SG_preview_timing_label':timing,'raw_keyed_bbox':list(keyed.getbbox()),'raw_outer_edge_pixel_checks':edges,'raw_guide_layout_pass_not_inferred':True,'status':status,'source_art_unchanged':pin(raw)==rawpin,'new_images_viewed':False})
 proof=write(label+'-standard-pipeline-proof-v001.json',{'schema':'Guard221222-standard-row-proof-v001','commands':commands,'source_index':pin(index),'native_calls':0,'source_art_modified':False,'new_images_viewed':False})
 entries.append({'state':state,'index':pin(index),'proof':pin(proof),'curated_dir':(run/'curated').as_posix(),'shared_scale':shared['scale'],'status':status})
write('HANDOFF.md','Native221 Move6 and222 StompWindup6 standard shared component extract/inspect/compose/curated/preview. Each row ONE shared scale; carried Ready2094 RGBA exact. Twelve transparent512 candidates unviewed until Root E. Move opposite-leg contacts0/3 are NOT accepted: possible same-side3-pose repetition must be traced through actual near/far hips. Stomp actual lifted leg side may contradict original near-lift spec: preserve prompt deviation and use NEW amendment only after actual View. Technical QA does not prove choreography. Preview timing is separate from actual native path/timing. No source painting, perframe normalization, UE/nativecalls/Source/Content/tools/ledger edits.\n')
write('extraction-freeze-v001.json',{'schema':'Guard221222-standard-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'native_calls':0,'new_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for label,_,_,_,_ in jobs:
 for p in sorted((OUT/f'run-{label}-shared-HD-v001/qa').rglob('*')):
  if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/f'{label}-{p.name}')
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫221Move与222跺击蓄力透明候选','version':'v001','status':'standard-transparent-candidates-unviewed-motion-and-leg-side-not-accepted','source':OUT.as_posix(),'entries':entries,'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'entries':entries},ensure_ascii=False,indent=2))
