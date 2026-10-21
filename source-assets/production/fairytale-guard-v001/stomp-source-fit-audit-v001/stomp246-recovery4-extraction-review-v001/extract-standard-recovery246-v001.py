"""Five-step standard shared component processing; no source painting or native call."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
R=Path('F:/Ourgame');A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001';H=R/'source-assets/production/fairytale-guard-v001/stomp-source-fit-audit-v001';OUT=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe';assert Path(sys.executable).resolve()==PY.resolve()
PREP=H/'stomp246-recovery4-input-v001';SRC=PREP/'run-guard-stomp-recovery4-after-active245-v001';READY=A/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
RAW=H/'process-batches/2026-10-18-Guard-StompRecovery4-native246-v001/raw/stomp_recovery.png';RUN=OUT/'run-stomp246-recovery4-shared-HD-v001'
MEDIA=R/'过程图稿与视频/2026-10-18_裂岩守卫246四相收招透明提取候选_v001';assert not RUN.exists() and not MEDIA.exists()
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);record=dict(argv=args,actual_exit_code=r.returncode,log=pin(log));write('logs/'+n+'-command.json',record);assert r.returncode==0,record;return record
rawpin=pin(RAW);assert rawpin['sha256']=='632c1c722dd15d70c61e5a51bbe42420219f9e06ed8a046dce30cf7cb4e465bb' and Image.open(RAW).size==(2172,724)
source_request_pin=pin(SRC/'sprite-request.json');source_freeze_pin=pin(PREP/'official-input-freeze-v001.json')
shutil.copytree(SRC,RUN);(RUN/'raw/right').mkdir(parents=True,exist_ok=True);shutil.copy2(RAW,RUN/'raw/right/stomp_recovery.png');shutil.copy2(READY/'raw/right/idle.png',RUN/'raw/right/idle.png')
# The processing copy records the exact actual native prompt; frozen prepare is read only.
shutil.copy2(PREP/'Root-native-short-recovery-prompt-v001.txt',RUN/'prompts/right/stomp_recovery.txt')
bridge=OUT/'shared-HD-fit-existing-exact.py';shutil.copy2(A/'stomp224-active2-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
commands=[command('extract',[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(RUN),'--min-used-pixels','512'])]
commands.append(command('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN),'--states','right_idle,right_stomp_recovery','--report',str(RUN/'inspect-report.json')]))
commands.append(command('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','512']))
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
assert load_curation(RUN) is None
payload=stamp_curation(RUN,dict(version=1,kind='sprite-gen-curation',states=dict(right_idle=dict(selected=[0,1,2,3],transforms={}),right_stomp_recovery=dict(selected=[0,1,2,3],transforms={}))))
write(RUN.relative_to(OUT)/'curation.json',payload);assert state_plan(load_curation(RUN),'right_stomp_recovery',4)==([0,1,2,3],{})
commands.append(command('export-curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state','right_stomp_recovery','--selected-only']))
commands.append(command('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)]))
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=RUN/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)));carried.append(dict(frame=i,accepted=pin(old),reextracted=pin(new),RGBA_equal=True))
rows=[]
for i in range(4):
 p=RUN/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.array(im);assert im.size==(512,512) and np.array_equal(a,np.array(Image.open(RUN/f'frames/right/stomp_recovery/frame-{i}.png')));al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);box=list(im.getbbox())
 rows.append(dict(frame=i,file=pin(p),curated_RGBA_equal=True,RGBA_sha256=hashlib.sha256(a.tobytes()).hexdigest(),alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT=box,safe_canvas_margins_ltrb=[box[0],box[1],512-box[2],512-box[3]],pure_magenta_any_alpha=int((mag&(al>0)).sum()),pure_magenta_core128=int((mag&(al>=128)).sum()),near_eye_and_body_floor_registration=None,actual_transparent_View=False))
keyed=native.remove_chroma_background(Image.open(RAW),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);ka=np.array(keyed)[:,:,3]
edges={k:dict(nonzero_alpha_pixels=int((v>0).sum()),core128_pixels=int((v>=128).sum())) for k,v in dict(left=ka[:,0],right=ka[:,-1],top=ka[0,:],bottom=ka[-1,:]).items()}
shared=next(x['shared_row_fit'] for x in fm['rows'] if x['state']=='right_stomp_recovery')
index=write('stomp246-recovery4-curated-source-index-v001.json',dict(schema='Guard246-shared-four-curated-source-index-v001',state='right_stomp_recovery',native_raw=rawpin,raw_retention='Root E532 recorded2SHA0 and actual raw View; worker independently compared canonical raw bytes to E532 retained original.',official_prepared_request=source_request_pin,official_prepared_freeze=source_freeze_pin,actual_native_fullprompt=pin(PREP/'Root-native-short-recovery-prompt-v001.txt'),frames=rows,shared_row_fit=shared,exact_existingReady209_four_RGBA=carried,source_outer_edge_checks=edges,source_outer_edges_clear=all(x['nonzero_alpha_pixels']==0 for x in edges.values()),native_durations_ms=[375]*4,SG_uniform_preview_only_ms=[333]*4,QA=dict(extract=fm['ok'],extract_errors=fm['errors'],extract_warnings=fm['warnings'],inspect_ok=ir['ok'],inspect_errors=ir['errors'],inspect_warnings=ir['warnings']),status='Shared512component candidates only; transparent images unviewed pending RootE533. No planted-support/upperbody continuity acceptance inferred.',source_pixels_not_painted=True,perframe_scale_normalization=False,TrialAllowed=False,new_images_viewed=False))
proof=write('standard-five-step-proof-v001.json',dict(schema='Guard246-standard-five-step-proof-v001',commands=commands,source_index=pin(index),native_calls=0,source_raw_unchanged=pin(RAW)==rawpin,prepared_request_unchanged=pin(SRC/'sprite-request.json')==source_request_pin,prepared_freeze_unchanged=pin(PREP/'official-input-freeze-v001.json')==source_freeze_pin,Source_Content_tools_ledger_modified=False,new_images_viewed=False))
freeze=write('extraction-freeze-v001.json',dict(schema='Guard246-standard-shared-extraction-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],new_images_viewed=False,native_called=False,TrialAllowed=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in (RUN/'qa').iterdir():
 if p.is_file() and p.suffix.lower() in ['.png','.gif']:shutil.copy2(p,MEDIA/'展示副本'/p.name)
write_media=MEDIA/'source-version-status-index.json';write_media.write_text(json.dumps(dict(schema='F-dated-source-version-status-v001',source=OUT.as_posix(),source_index=pin(index),proof=pin(proof),files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Unviewed transparent4 awaiting RootE533, not source or runtime acceptance.',Root_E_retention_pending=True,new_images_viewed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(F_batch=MEDIA.as_posix(),source_index=pin(index),proof=pin(proof),freeze=pin(freeze),shared_scale=shared['scale'],curated_dir=(RUN/'curated').as_posix(),QA=ir,raw_source_unchanged=pin(RAW)==rawpin,new_images_viewed=False),ensure_ascii=False))
