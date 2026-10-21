from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
PREP=HERE/'stomp-far-active2-recovery4-generation-ready-v002';SRC=PREP/'run-guard-far-stomp-active2-v002';READY=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001';OUT=HERE/'stomp224-active2-extraction-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫224Far跺击Active2透明提取候选_v001'
assert Path(sys.executable).resolve()==PY.resolve();assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def cmd(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
raw=SRC/'raw/right/stomp_active.png';rawpin=pin(raw);assert rawpin['sha256']=='956d62bbea094472973831d3038b9753d97613b17750c44d1e5d2a74e12735d4' and rawpin['bytes']==1625017 and Image.open(raw).size==(1774,887)
run=OUT/'run-stomp224-active2-shared-HD-v001';shutil.copytree(SRC,run);bridge=OUT/'shared-HD-fit-existing-exact.py';shutil.copyfile(HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
commands=[cmd('extract',[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(run),'--min-used-pixels','512'])]
commands.append(cmd('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states','right_idle,right_stomp_active','--report',str(run/'inspect-report.json')]))
commands.append(cmd('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']))
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
assert load_curation(run) is None
pay=stamp_curation(run,{'version':1,'kind':'sprite-gen-curation','states':{'right_idle':{'selected':[0,1,2,3],'transforms':{}},'right_stomp_active':{'selected':[0,1],'transforms':{}}}});write(run.relative_to(OUT)/'curation.json',pay);assert state_plan(load_curation(run),'right_stomp_active',2)==([0,1],{})
commands.append(cmd('export-curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state','right_stomp_active','--selected-only']))
commands.append(cmd('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]))
fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((run/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok'] and ir['errors']==ir['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=run/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)));carried.append({'frame':i,'accepted':pin(old),'reextracted':pin(new),'RGBA_equal':True})
rows=[]
for i in range(2):
 p=run/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.array(im);al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);assert a.shape==(512,512,4) and np.array_equal(a,np.array(Image.open(run/f'frames/right/stomp_active/frame-{i}.png')));box=list(im.getbbox());rows.append({'frame':i,'file':pin(p),'curated_RGBA_equal':True,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT':box,'safe_canvas_margins_ltrb':[box[0],box[1],512-box[2],512-box[3]],'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'actual_body_floor_grip_and_Active_Rec_join':None})
keyed=native.remove_chroma_background(Image.open(raw),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);ka=np.array(keyed)[:,:,3];edges={k:{'nonzero_alpha_pixels':int((v>0).sum()),'core128_pixels':int((v>=128).sum())} for k,v in {'left':ka[:,0],'right':ka[:,-1],'top':ka[0,:],'bottom':ka[-1,:]}.items()};assert all(v['nonzero_alpha_pixels']==0 for v in edges.values()),'Actual raw source edge foreground requires explicit rejection diagnostic.'
shared=next(r['shared_row_fit'] for r in fm['rows'] if r['state']=='right_stomp_active')
index=write('stomp224-active2-curated-source-index-v001.json',{'schema':'Guard224-two-curated-standard-source-index-v001','state':'right_stomp_active','native_raw':rawpin,'raw_retention':'Root E398 two-copy SHA zero; Root actual whole-row View and worker extraction authorization.','frames':rows,'shared_row_fit':shared,'exact_existingReady209_four_RGBA':carried,'native_phase_contract':pin(PREP/'stomp-active2/native-phase-contract-v002.json'),'SG_preview_timing_label':'2×77ms154ms uniform SG preview; actual StompActive150ms=2×75ms from actualActiveAt; no changed kernel deadline.','source_keyed_bbox':list(keyed.getbbox()),'source_outer_edge_checks':edges,'status':'Unviewed transparent2 candidate, source far-contact/near-support/closed-grip/body registration and finalframe1 motionref need Root E then actual View.','source_art_unchanged':pin(raw)==rawpin,'new_images_viewed':False})
proof=write('stomp224-active2-standard-pipeline-proof-v001.json',{'schema':'Guard224-standard-row-proof-v001','commands':commands,'source_index':pin(index),'native_calls':0,'source_art_modified':False,'new_images_viewed':False})
write('HANDOFF.md','Native224 FarStompActive2 standard shared component extract/inspect/compose/curated/preview all exit0. ONE row scale, Ready2094 carriedRGBAexact, rawouteredgesclear. Two transparent512 candidates await Root E then actual View/farcontact/near-support-delta registration. Actual finalActive1 only becomes Recovery motionreference after source pose review; Ready209 stays uniqueidentity. Native150ms=2×75 separate fromSG154ms preview. No UE/nativecalls/actual Source/Content/tools/ledger edits.\n')
write('extraction-freeze-v001.json',{'schema':'Guard224-standard-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'native_calls':0,'new_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in sorted((run/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫224Far跺击Active2透明提取候选','version':'v001','status':'standard-transparent-candidate-unviewed','source':OUT.as_posix(),'source_index':pin(index),'proof':pin(proof),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'source_index':pin(index),'proof':pin(proof),'shared_scale':shared['scale'],'curated_dir':(run/'curated').as_posix()},ensure_ascii=False,indent=2))
