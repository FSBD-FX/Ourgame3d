"""Standard component-row extraction of retained native217; no native generation or installed-tool edits."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame'); SG=Path('C:/Users/22499/.codex/skills/sprite-gen'); PY=SG/'.venv/Scripts/python.exe'
PREP=HERE/'interrupted-recovery4-generation-ready-v001'
SOURCE=PREP/'run-guard-interrupted-recovery4-v001'
READY=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
OUT=HERE/'interrupted217-extraction-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫217中断恢复4透明提取候选_v001'
assert Path(sys.executable).resolve()==PY.resolve()
assert not OUT.exists() and not MEDIA.exists()
OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,obj):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(obj if isinstance(obj,str) else json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 return p
def call(name,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
 log=write('logs/'+name+'.log',r.stdout+r.stderr)
 result={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)}
 write('logs/'+name+'-command.json',result)
 assert r.returncode==0,result
 return result
raw=SOURCE/'raw/right/interrupted_recovery.png';rawpin=pin(raw)
assert rawpin['sha256']=='0e48ef7024058d142588eb978b67add1afd43f17add13e616f1fec0f7416d9fc'
assert Image.open(raw).size==(1774,887)
run=OUT/'run-interrupted-recovery4-shared-HD-v001'
shutil.copytree(SOURCE,run)
bridge=OUT/'shared-HD-fit-existing-exact.py'
shutil.copyfile(HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
commands=[]
commands.append(call('extract',[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(run),'--min-used-pixels','512']))
state='right_interrupted_recovery';pose='interrupted_recovery';count=4
commands.append(call('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states','right_idle,'+state,'--report',str(run/'inspect-report.json')]))
commands.append(call('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']))
sys.path.insert(0,str(SG))
from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
assert load_curation(run) is None
curation=stamp_curation(run,{'version':1,'kind':'sprite-gen-curation','states':{'right_idle':{'selected':[0,1,2,3],'transforms':{}},state:{'selected':[0,1,2,3],'transforms':{}}}})
write(run.relative_to(OUT)/'curation.json',curation)
assert state_plan(load_curation(run),state,count)==([0,1,2,3],{})
commands.append(call('export-curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state,'--selected-only']))
commands.append(call('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]))
fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'))
ir=json.loads((run/'inspect-report.json').read_text(encoding='utf-8'))
assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok'] and ir['errors']==ir['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=run/f'frames/right/idle/frame-{i}.png'
 assert np.array_equal(np.asarray(Image.open(old)),np.asarray(Image.open(new)))
 carried.append({'frame':i,'accepted':pin(old),'reextracted':pin(new),'RGBA_equal':True})
rows=[]
for i in range(4):
 p=run/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.asarray(im);al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2)
 assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(run/f'frames/right/{pose}/frame-{i}.png')))
 box=list(im.getbbox());margins=[box[0],box[1],512-box[2],512-box[3]]
 rows.append({'frame':i,'file':pin(p),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'curated_RGBA_equal':True,'alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT':box,'safe_canvas_margins_ltrb':margins,'alpha_nonzero_pixels':int((al>0).sum()),'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'actual_body_markers_grip_continuity':None})
keyed=native.remove_chroma_background(Image.open(raw),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
ka=np.array(keyed)[:,:,3]
edges={k:{'nonzero_alpha_pixels':int((v>0).sum()),'core128_pixels':int((v>=128).sum())} for k,v in {'left':ka[:,0],'right':ka[:,-1],'top':ka[0,:],'bottom':ka[-1,:]}.items()}
assert all(v['nonzero_alpha_pixels']==0 for v in edges.values()),'Actual raw-edge foreground: reject crop rather than curate around it'
shared=next(r['shared_row_fit'] for r in fm['rows'] if r['state']==state)
index=write('interrupted-recovery4-curated-source-index-v001.json',{'schema':'Guard217-four-curated-standard-source-index-v001','state':state,'native_raw':rawpin,'raw_retention':'Root E383 two-copy SHA zero difference then Root actual whole-row View; worker standard extraction authorized.','raw_size':[1774,887],'raw_keyed_bbox':list(keyed.getbbox()),'raw_outer_edge_pixel_checks':edges,'raw_layout_guide_pass':'Not asserted by successful component extraction; independent complete poses only.','frames':rows,'shared_row_fit':shared,'exact_existingReady209_four_RGBA':carried,'native_interval_contract':pin(PREP/'native-interval-consumer-contract-v001.json'),'actual_kernel_witness':pin(PREP/'actual-kernel-interval-proof-v001.json'),'SG_preview_timing_label':'Four equal 100ms preview frames only. Native interrupted Recovery uses normalized actual positive [StunUntil,OccupiedUntil), never a new fixed400ms timer. Empty interval consumes no row. Dead/Stunned priority remains.','status':'Unviewed transparent four-pose candidate; all4 actual visible grip/body/floor review after Root E retention, not runtime acceptance.','source_art_unchanged':pin(raw)==rawpin,'new_images_viewed':False})
proof=write('interrupted-recovery4-standard-pipeline-proof-v001.json',{'schema':'Guard217-standard-row-proof-v001','commands':commands,'source_index':pin(index),'native_calls':0,'new_images_viewed':False,'source_art_modified':False,'installed_skill_modified':False})
write('HANDOFF.md','Native217 Interrupt Recovery4 standard shared-row component extract, inspect, compose, curated PNG export and preview all exit0. One shared scale, no per-frame height normalization, no artwork redraw or transforms. Carried Ready209 all4 re-extracted RGBA exactly equal. Four new transparent512 candidates remain unviewed until Root E retention. Four100ms preview is not a new gameplay timer: actual interrupted recovery only exists during the positive original remaining interval after Stunned. Original Dead/Stunned priorities and attack deadlines remain. No UE/nativecalls/actual Source/Content/tools/ledger edits.\n')
write('extraction-freeze-v001.json',{'schema':'Guard217-standard-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'native_calls':0,'new_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in sorted((run/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:
 json.dump({'date':'2026-10-18','topic':'裂岩守卫217中断恢复4透明提取候选','version':'v001','status':'standard-independent-transparent-candidate-unviewed','source':OUT.as_posix(),'source_index':pin(index),'proof':pin(proof),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'source_index':pin(index),'proof':pin(proof),'shared_scale':shared['scale'],'curated_dir':(run/'curated').as_posix()},ensure_ascii=False,indent=2))
