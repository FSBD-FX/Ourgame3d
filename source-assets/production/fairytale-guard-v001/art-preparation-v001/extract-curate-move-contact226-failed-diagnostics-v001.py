from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe';assert Path(sys.executable).resolve()==PY.resolve()
PREP=HERE/'move-contact-pair-generation-ready-v001';SRC=PREP/'run-guard-move-contact-pair-v001';READY=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001';OUT=HERE/'move226-contact-pair-failed-diagnostics-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫226触地双关键姿态失败诊断_v001';assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def cmd(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
raw=SRC/'raw/right/move_contact_pair.png';rawpin=pin(raw);assert rawpin['sha256']=='18c36f256112be9c46e54b1a33b7147e748ce1925fd58563571a066520c9cefc' and rawpin['bytes']==1610492 and Image.open(raw).size==(1774,887)
run=OUT/'run-move226-contact-pair-shared-HD-v001';shutil.copytree(SRC,run);bridge=OUT/'shared-HD-fit-existing-exact.py';shutil.copyfile(HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py',bridge)
commands=[cmd('extract',[str(PY),'-B','-X','utf8',str(bridge),'--run-dir',str(run),'--min-used-pixels','512'])]
commands.append(cmd('inspect',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states','right_idle,right_move_contact_pair','--report',str(run/'inspect-report.json')]))
commands.append(cmd('compose',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512']))
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
from sprite_gen.frames import extract as native
assert load_curation(run) is None
pay=stamp_curation(run,{'version':1,'kind':'sprite-gen-curation','states':{'right_idle':{'selected':[0,1,2,3],'transforms':{}},'right_move_contact_pair':{'selected':[0,1],'transforms':{}}}});write(run.relative_to(OUT)/'curation.json',pay);assert state_plan(load_curation(run),'right_move_contact_pair',2)==([0,1],{})
commands.append(cmd('export-curated',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state','right_move_contact_pair','--selected-only']))
commands.append(cmd('preview',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)]))
fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((run/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok'] and ir['errors']==ir['warnings']==[]
carried=[]
for i in range(4):
 old=READY/f'frames/right/idle/frame-{i}.png';new=run/f'frames/right/idle/frame-{i}.png';assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(new)));carried.append({'frame':i,'accepted':pin(old),'reextracted':pin(new),'RGBA_equal':True})
rows=[]
for i in range(2):
 p=run/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');a=np.array(im);al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);assert a.shape==(512,512,4) and np.array_equal(a,np.array(Image.open(run/f'frames/right/move_contact_pair/frame-{i}.png')));box=list(im.getbbox());rows.append({'frame':i,'file':pin(p),'curated_RGBA_equal':True,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT':box,'safe_canvas_margins_ltrb':[box[0],box[1],512-box[2],512-box[3]],'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'curated_actual_View':False})
keyed=native.remove_chroma_background(Image.open(raw),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);a=np.array(keyed);edges={k:{'nonzero_alpha_pixels':int((v>0).sum()),'core128_pixels':int((v>=128).sum())} for k,v in {'left':a[:,0,3],'right':a[:,-1,3],'top':a[0,:,3],'bottom':a[-1,:,3]}.items()}
near=[[[371,619],[297,657],[216,695],[246,733]],[[1268,618],[1175,657],[1080,695],[1109,735]]];far=[[[481,598],[514,646],[529,704],[572,737]],[[1370,598],[1410,644],[1437,704],[1468,737]]];trace=[]
for i in range(2):
 chains=[]
 for side,pp in [('NEAR_left_foreground_hip_to_rear_left_foot',near[i]),('FAR_right_recessed_hip_to_front_right_foot',far[i])]:
  points=[]
  for role,xy in zip(['visible_hip_region_plate','visible_knee_region_plate','visible_shin_region_plate','visible_shoe_surface'],pp):
   rgba=a[xy[1],xy[0]].tolist();assert rgba[3]>=128,(i,side,xy,rgba);points.append({'artist_visible_region':role,'raw_xy':xy,'actual_keyed_RGBA':rgba,'uncertainty_px':6,'not_hidden_bone_or_joint':True})
  chains.append({'physical_leg':side,'visible_surface_chain':points})
 trace.append({'keypose':i,'chains':chains,'verdict':'FAR leg remains front-right, NEAR remains rear-left in both keyposes; required physical-leg exchange failed.'})
reject=write('Move226-independent-raw-leg-chain-semantic-rejection-v001.json',{'schema':'Guard226-oppositecontact-semantic-rejection-v001','source':rawpin,'retention_actual_View':'Root E407 twice SHA zero then Root and worker actual whole2raw View. Newtransparentoutputs unviewed pendingE.','rows':trace,'source_semantic_pass':False,'source_complete_edge_clear':all(e['nonzero_alpha_pixels']==0 for e in edges.values()),'required_pair':'0NEAR physicalLEFTforegroundhip leads / FAR trails;1FAR physicalRIGHTrecessedhip leads / NEAR trails.','observed':'Both keyposes FAR leads and NEAR trails despite separatehip/occlusion productionguide. Stop same wholebody generation strategy, no further identical retry.','TrialAllowed':False,'not_a_runtime_Move2_row':True,'no_new_Move6_accepted':True,'source_art_modified_or_local_paint_mirror_patch':False})
shared=next(r['shared_row_fit'] for r in fm['rows'] if r['state']=='right_move_contact_pair')
index=write('move226-contact-pair-curated-diagnostic-source-index-v001.json',{'schema':'Guard226-contactpair-two-curated-SEMANTIC-REJECTED-diagnostic-index-v001','state':'right_move_contact_pair','native_raw':rawpin,'frames':rows,'shared_row_fit':shared,'exact_existingReady209_four_RGBA':carried,'raw_outer_edge_checks':edges,'semantic_rejection':pin(reject),'technical_QA_pass':True,'source_motion_semantic_pass':False,'TrialAllowed':False,'status':'SEMANTIC-REJECTED diagnostics only; two same physical FAR-leading contact poses. No accepted motionreference or runtimeMove source.','source_art_unchanged':pin(raw)==rawpin,'new_images_viewed':False,'bad221_223_pixels_used':False})
proof=write('move226-contact-pair-standard-proof-and-semantic-rejection-v001.json',{'schema':'Guard226-standard-QA-plus-independent-semantic-rejection-v001','standard_commands':commands,'standard_QA_pass':True,'semantic_motion_pass':False,'source_index':pin(index),'native_calls':0,'source_modified':False,'new_curated_View':False})
write('HANDOFF.md','Native226 contactpair standardshared extract/inspect/compose/curated/preview technicalQA passes, but actualE407raw physicalhip-leg trace rejects bothsameFAR-leading keyposes. Transparent2 are failure diagnostics only, TrialAllowed=false; not Move2runtime or acceptedMove6motionref. Stop same generation strategy. Ready2094 carriedRGBAexact, no bad221/223 pixels. New F batch needsRootE beforecuratedView. Future true2D leg-rig feasibility separate; no nativecalls/Source/Content/tools/ledger/UE edits.\n')
write('diagnostic-freeze-v001.json',{'schema':'Guard226-contactpair-failed-diagnostic-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'native_calls':0,'source_motion_pass':False,'TrialAllowed':False,'new_curated_View':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/失败诊断包');(MEDIA/'展示副本').mkdir()
for p in sorted((run/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫226触地双关键姿态失败诊断','version':'v001','status':'SEMANTIC-REJECTED-transparent-diagnostics-unviewed','source':OUT.as_posix(),'source_index':pin(index),'proof':pin(proof),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'source_index':pin(index),'rejection':pin(reject),'shared_scale':shared['scale'],'TrialAllowed':False},ensure_ascii=False,indent=2))
