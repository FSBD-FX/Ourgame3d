"""Retained native209 whole Guard+axe -> shared-row standard transparent Ready4."""
from pathlib import Path
from datetime import datetime
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
SRC=HERE/'armed-ready4-generation-ready-v001/run-guard-right-armed-ready-v001';RAW=SRC/'raw/right/idle.png'
OUT=HERE/'armed-ready4-extraction-v001';RUN=OUT/'run-ready209-shared-HD-v001';STATE='right_idle'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫209持斧Ready4透明提取_v001'
assert Path(sys.executable).resolve()==PY.resolve();OUT.mkdir(exist_ok=False);assert not MEDIA.exists()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
rawpin=pin(RAW);assert rawpin['sha256']=='018f7b735794871959d5dc5adc7dc3e040feb159480cde768439d44f92704316';raw=Image.open(RAW);assert raw.size==(1774,887) and raw.mode=='RGB'
sys.path.insert(0,str(SG));from sprite_gen.frames.extract import remove_chroma_background,extract_component_images
keyed=remove_chroma_background(raw,(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005);components=extract_component_images(keyed,4);assert components is not None and len(components)==4
bb=keyed.getbbox();assert bb and bb[0]>0 and bb[1]>0 and bb[2]<raw.width and bb[3]<raw.height
write('raw209-component-boundary-numeric-check-v001.json',{'schema':'Guard209-retained-raw-component-check-v001','source':rawpin,'raw_size':list(raw.size),'raw_source_View':'Root E362 bothSHA0 thenRoot andworker actualView. Fourcompletebodies+axes, closedfists/continuousshaft, finalheadhasclearpadding and isnotcropped.','keyed_all_foreground_bbox_DIAGNOSTIC_ONLY':list(bb),'outside_margin_px':[bb[0],bb[1],raw.width-bb[2],raw.height-bb[3]],'actual_components':len(components),'component_sizes':[list(p.size) for p in components],'no_slot_cutting':True,'component_RGBA_sha256':[hashlib.sha256(p.tobytes()).hexdigest() for p in components],'whole_source_sourcecells':'No exactequalcellclaim: native1774/4=443.5; visibleposes crossinvisibleequalwidths slightly butcomponentsremainseparate. Use actualcomponentpipeline, notgridcropping.'})
pins=[]
for rel in ['sprite-request.json','base-source.png','raw/right/idle.png','references/layout-guides/right/idle.png','references/fixed-heavyaxe208-curated.png']:
 src=SRC/rel;dst=RUN/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);pins.append(pin(src))
prompt=HERE/'armed-ready4-fullprompt-ownership-fixed-v002/root-native-armed-ready4-fullprompt-v002.txt';dst=RUN/'prompts/right/idle.txt';dst.parent.mkdir(parents=True);shutil.copyfile(prompt,dst);pins.append(pin(prompt))
bridge=HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py';shutil.copyfile(bridge,OUT/'shared-HD-fit-existing-exact.py')
ex=command('extract-ready209',[str(PY),'-B','-X','utf8',str(OUT/'shared-HD-fit-existing-exact.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
ins=command('inspect-ready209',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN),'--states',STATE,'--report',str(RUN/'inspect-report.json')])
co=command('compose-ready209',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
from sprite_gen.curate.curation import load_curation,stamp_curation,state_plan
assert load_curation(RUN) is None;payload=stamp_curation(RUN,{'version':1,'kind':'sprite-gen-curation','states':{STATE:{'selected':[0,1,2,3],'transforms':{}}}});write(RUN.relative_to(OUT)/'curation.json',payload)
assert state_plan(load_curation(RUN),STATE,4)==([0,1,2,3],{})
export=command('export-curated-ready209',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state',STATE,'--selected-only'])
preview=command('preview-ready209',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)])
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok']
rows=[]
for i in range(4):
 p=RUN/f'curated/frame-{i}.png';im=Image.open(p);a=np.asarray(im);al=a[:,:,3];assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(RUN/f'frames/right/idle/frame-{i}.png')))
 mag=np.all(a[:,:,:3]==[255,0,255],axis=2)
 rows.append({'frame':i,'file':pin(p),'curated_RGBA_equal':True,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'canvas':[512,512],'alpha_bbox_DIAGNOSTIC_NOT_BODY_SCALE':list(im.getbbox()),'nonzero_alpha_pixels':int((al>0).sum()),'partial_alpha_pixels':int(((al>0)&(al<255)).sum()),'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'duration_ms':250,'actual_body_crown_sole_and_closed_grips':None,'marker_gate':'NEW transparentoutputs EthenactualView. Never usewholeaxealphaextent asbodyheight.'})
anchor=OUT/'right-armed-ready-anchor-CANDIDATE/frame-0.png';anchor.parent.mkdir();shutil.copyfile(RUN/'curated/frame-0.png',anchor)
index=write('ready209-four-curated-source-index-v001.json',{'schema':'Guard209-ArmedReady4-shared-curated-source-index-v001','source_native209':rawpin,'sourcepins':pins,'rows':rows,'shared_row_fit':fm['rows'][0]['shared_row_fit'],'standard_state':STATE,'semantic_state':'right_armed_ready','whole_body_same_fixedaxe':True,'durations_ms':[250]*4,'candidate_Ready0':pin(anchor),'acceptance':'Pending EtransparentRootactualViewandinternalReady0lock; no userfinal/motion/runtimeacceptance.','futureidentity':'AfterReady0lock allarmedactionsownidentityviaacceptedReady0; no206/207neutralorstandalone208reattach ascompetingbodyidentity.','new_images_viewed':False})
proof=write('ready209-standard-pipeline-proof-v001.json',{'schema':'Guard209-whole-ready-standard-pipeline-proof-v001','commands':[ex,ins,co,export,preview],'source_index':pin(index),'raw_source_unchanged':pin(RAW)==rawpin,'native_calls':0,'new_images_viewed':False,'body_scale_registration_gate':'ActualbodycrownsolemarkersafterEView;100.8pxstandingheightcandidate, horizontalaxemustnotshrinkbody.'})
write('HANDOFF.md','209 fourwholebody+fixedaxe poses passed unchanged standardsharedextract/inspect/compose/curated/preview. Raw1774x887,4actualcompletecomponents, no gridcrop; sourceheadboundariesnotcropped. Sharedrowonly,4transparent512250ms. Ready0 exactcandidate pendingRootE/View/internalproductionlock, no finalaesthetic/motionacceptance. Bodycrownsole/gripsourcepixelmeasure afterEbeforefutureWake6/AxeWindup6. No nativecalls, UE, actualSource/tools edits.\n')
write('extraction-freeze-v001.json',{'schema':'Guard209-standard-curated-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'sourcepins':pins,'native_calls':0,'new_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in sorted((RUN/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫209持斧Ready4透明提取','version':'v001','status':'standard-transparent-candidate-unviewed','source':OUT.as_posix(),'proof':pin(proof),'source_index':pin(index),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'index':pin(index),'anchor':pin(anchor),'shared_scale':fm['rows'][0]['shared_row_fit']['scale'],'source_boundary':list(bb),'inspect_ok':ir['ok'],'new_images_viewed':False},ensure_ascii=False,indent=2))
