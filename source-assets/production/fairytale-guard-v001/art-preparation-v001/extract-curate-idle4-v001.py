"""Native207 standard shared component extraction + real curated4, no generation."""
from pathlib import Path
from datetime import datetime
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
SRC=HERE/'idle4-camera-fixed-generation-ready-v002/run-guard-right-idle-camera-v002'
OUT=HERE/'idle4-extraction-v001';RUN=OUT/'run-idle207-shared-HD-v001';STATE='right_idle'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫207Idle4透明提取与锚候选_v001'
assert Path(sys.executable).resolve()==PY.resolve();OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
WATCH={}
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def copy(p,q):
 assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True);WATCH[p]=pin(p);shutil.copyfile(p,q);assert pin(p)['sha256']==pin(q)['sha256']
def cmd(name,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');p=write('logs/'+name+'.log',r.stdout+r.stderr);record={'argv':args,'actual_exit_code':r.returncode,'log':pin(p)};write('logs/'+name+'-command.json',record);assert r.returncode==0,record;return record
raw=SRC/'raw/right/idle.png';assert pin(raw)['sha256']=='1f44fb362265ad5af6a7dda18cd9c3b8ed3948ff13a482540770581a0f8c124f';im=Image.open(raw);assert im.mode=='RGB' and im.size==(2172,724)
for rel in ['sprite-request.json','base-source.png','raw/right/idle.png','prompts/right/idle.txt','references/layout-guides/right/idle.png']:copy(SRC/rel,RUN/rel)
q=json.loads((RUN/'sprite-request.json').read_text(encoding='utf-8'));assert q['states'][STATE]['frames']==4 and q['fit']['shared_row_scale'] is True and q['chroma_key']['rgb']==[255,0,255]
bridge=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-hand204-extraction-v001/shared-HD-fit-existing-exact.py';copy(bridge,OUT/'shared-HD-fit-existing-exact.py')
ex=cmd('extract-idle207-shared-HD-v001',[str(PY),'-B','-X','utf8',str(OUT/'shared-HD-fit-existing-exact.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
ins=cmd('inspect-idle207-shared-HD-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN),'--states',STATE,'--report',str(RUN/'inspect-report.json')])
co=cmd('compose-idle207-shared-HD-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import load_curation,stamp_curation,state_plan,frame_variant
assert load_curation(RUN) is None
payload=stamp_curation(RUN,{'version':1,'kind':'sprite-gen-curation','states':{STATE:{'selected':list(range(4)),'transforms':{}}}})
write(RUN.relative_to(OUT)/'curation.json',payload)
order,transforms=state_plan(load_curation(RUN),STATE,4);assert order==list(range(4)) and not transforms and frame_variant(load_curation(RUN),STATE)=='pixel'
export=cmd('export-curated-idle207-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state',STATE,'--selected-only'])
preview=cmd('preview-idle207-v001',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)])
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));shared=fm['rows'][0]['shared_row_fit'];assert len(shared['frame_records'])==4 and len({r['shared_scale'] for r in shared['frame_records']})==1
manifest=json.loads((RUN/'manifest.json').read_text(encoding='utf-8'));assert manifest['animation']['rows'][STATE]['durations_ms']==[250]*4
rows=[]
for i in range(4):
 p=RUN/f'curated/frame-{i}.png';a=np.asarray(Image.open(p));before=RUN/f'frames/right/idle/frame-{i}.png';assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(before)))
 al=a[:,:,3];bb=Image.open(p).getbbox();assert bb;core=al>=128
 pure=int(((al>0)&np.all(a[:,:,:3]==[255,0,255],axis=2)).sum());assert pure==0
 rows.append({'frame':i,'source':pin(p),'precuration':pin(before),'curated_RGBA_equal':True,'canvas':[512,512],'duration_ms':250,'alpha_nonzero_bbox_DIAGNOSTIC_ONLY':list(bb),'alpha_nonzero_pixels':int((al>0).sum()),'core128_pixels':int(core.sum()),'partial_alpha_pixels':int(((al>0)&(al<255)).sum()),'pure_magenta_alpha_pixels':pure,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'visible_root_crown_nearGrip_farGrip_actualbones':None,'identity_or_motion_accepted':False})
anchor=OUT/'right-idle-anchor-CANDIDATE/frame-0.png';copy(RUN/'curated/frame-0.png',anchor)
index=write('idle207-four-curated-source-index-v001.json',{'schema':'Guard207-Idle4-shared-curated-source-index-v001','created_local':datetime.now().astimezone().isoformat(),'native207_raw':pin(raw),'Root_raw_review_authority':'Root E353 bothSHA0 then actualView fourclosedfist3/4settle poses; explicit extract/inspect/compose/curated authorization.','source206_base_role':'Pre-idle only; after actualcuratedIdle lock useanchor forfutureWake/Axe, not206base.','rows':rows,'one_shared_row_scale':shared,'durations_ms':[250]*4,'anchor_frame0_candidate':pin(anchor),'Root_requested_pick_frame0':True,'anchor_status':'Pending E-retained transparent/motion actualreview and Rootlock; not userfinalaestheticacceptance.','actual_hiddenbone_grip_measured':False,'new_output_images_viewed':False})
report=write('idle207-extraction-proof-v001.json',{'schema':'Guard207-Idle4-standard-pipeline-proof-v001','extract':ex,'inspect':ins,'compose':co,'curated_export':export,'preview_generation':preview,'source_index':pin(index),'warnings':json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8')).get('warnings'),'runtime_or_final_art_accepted':False,'native_generation_calls':0,'shared_row_only_not_perframe_normalize':True})
for p,b in WATCH.items():assert pin(p)==b
write('HANDOFF.md','Native207 raw is intermediate only. Actualstandardsharedextract/inspect/compose/curated4/preview all exit0; one sharedscale, no perframe normalize. Transparent5124frames250msx4. RootpickIdle0 candidate exactcurated0, pending E and actualtransparent/motion review beforeacceptedanchor. SGpreviewuniform250msmatchesartistIdle1s, no nativeIdledeadline. Base206pre-idle ownership ends onceIdleanchoraccepted. Newtransparent/qaimages unviewed: canonicalmedia→RootE→actualView. No newgeneration/API/UE/tools/Source changes.\n')
write('extraction-freeze-v001.json',{'schema':'Guard207-Idle4-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'sourcepins':[v for v in WATCH.values()],'source_mismatches':0,'new_output_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in sorted((RUN/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫207Idle4透明提取与锚候选','version':'v001','status':'transparent-curated-candidate-unviewed','source':OUT.as_posix(),'proof':pin(report),'index':pin(index),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'curated':(RUN/'curated').as_posix(),'index':pin(index),'anchor':pin(anchor),'shared_scale':shared['scale'],'warnings':json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8')).get('warnings'),'new_images_viewed':False},ensure_ascii=False,indent=2))
