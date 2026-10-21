"""Retained210/211 independent row extractions with exact carried Ready209 proof."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame');SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
PREP=HERE/'axe-windup212-correction-generation-ready-v001';READY=HERE/'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
OUT=HERE/'axe-windup212-extraction-v001';MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫212整六蓄力纠错透明提取_v001'
assert Path(sys.executable).resolve()==PY.resolve();OUT.mkdir(exist_ok=True);assert not MEDIA.exists()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def cmd(n,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8');log=write('logs/'+n+'.log',r.stdout+r.stderr);rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+n+'-command.json',rec);assert r.returncode==0,rec;return rec
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
jobs=[('axe-windup-correction','right_axe_windup','axe_windup','504944b8247fbe380383b599cff1cf3afce53c2741b4027ab2a428b44178889d')]
entries=[]
for label,state,pose,sha in jobs:
 src=PREP/f'run-guard-{label}-v001';run=OUT/f'run-{label}-shared-HD-v001';raw=src/f'raw/right/{pose}.png';rawpin=pin(raw);assert rawpin['sha256']==sha and Image.open(raw).size==(2172,724)
 if not run.exists():shutil.copytree(src,run)
 bridge=HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py'
 if not (OUT/'shared-HD-fit-existing-exact.py').exists():shutil.copyfile(bridge,OUT/'shared-HD-fit-existing-exact.py')
 ex=(json.loads((OUT/('logs/extract-'+label+'-command.json')).read_text(encoding='utf-8')) if (OUT/('logs/extract-'+label+'-command.json')).exists() else cmd('extract-'+label,[str(PY),'-B','-X','utf8',str(OUT/'shared-HD-fit-existing-exact.py'),'--run-dir',str(run),'--min-used-pixels','512']))
 ins=cmd('inspect-corrected-cli-v002-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(run),'--states','right_idle,'+state,'--report',str(run/'inspect-report.json')])
 co=cmd('compose-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(run),'--min-used-pixels','512'])
 assert load_curation(run) is None;pay=stamp_curation(run,{'version':1,'kind':'sprite-gen-curation','states':{'right_idle':{'selected':[0,1,2,3],'transforms':{}},state:{'selected':list(range(6)),'transforms':{}}}});write(run.relative_to(OUT)/'curation.json',pay)
 assert state_plan(load_curation(run),state,6)==(list(range(6)),{})
 export=cmd('export-curated-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(run),'--state',state,'--selected-only'])
 preview=cmd('preview-'+label,[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(run)])
 fm=json.loads((run/'frames/frames-manifest.json').read_text(encoding='utf-8'));ir=json.loads((run/'inspect-report.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[] and ir['ok']
 carried=[]
 for i in range(4):
  old=READY/f'frames/right/idle/frame-{i}.png';new=run/f'frames/right/idle/frame-{i}.png';a=np.asarray(Image.open(old));b=np.asarray(Image.open(new));assert np.array_equal(a,b);carried.append({'frame':i,'accepted':pin(old),'reextracted':pin(new),'RGBA_equal':True})
 rows=[]
 for i in range(6):
  p=run/f'curated/frame-{i}.png';a=np.asarray(Image.open(p));al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);before=run/f'frames/right/{pose}/frame-{i}.png';assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(before)))
  rows.append({'frame':i,'file':pin(p),'curated_RGBA_equal':True,'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'alpha_bbox_DIAGNOSTIC_NOT_BODYHEIGHT':list(Image.open(p).getbbox()),'alpha_nonzero_pixels':int((al>0).sum()),'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'actual_body_markers_grip_continuity':None})
 shared=next(r['shared_row_fit'] for r in fm['rows'] if r['state']==state)
 index=write(label+'-six-curated-source-index-v001.json',{'schema':'Guard212-six-curated-standard-source-index-v001','state':state,'native_raw':rawpin,'raw_retention':'RootE371twoSHA0thenRootView; explicitstandardcandidateextractauthorization.','frames':rows,'shared_row_fit':shared,'exact_existingReady209_four_RGBA':carried,'native_timing_sidecar':pin(PREP/'Root-native212-corrected-Windup6-generation-ready-v001.json'),'SG_preview_timing_label':'6×167ms=1002msuniformpreview; native1000ms exactsample mapping separate.','status':'Unviewedtransparentcandidate; CorrectedWindup212pendingall6transparentgriptraceandRootinternallock; notyetacceptedmotionbasis.','source_art_unchanged':pin(raw)==rawpin,'new_images_viewed':False})
 proof=write(label+'-standard-pipeline-proof-v001.json',{'schema':'Guard212-standard-row-proof-v001','commands':[ex,ins,co,export,preview],'source_index':pin(index),'native_calls':0,'source_art_modified':False,'new_images_viewed':False})
 entries.append({'state':state,'index':pin(index),'proof':pin(proof),'curated_dir':(run/'curated').as_posix(),'shared_scale':shared['scale']})
write('HANDOFF.md','212wholecorrectedWindup6 passedstandardsharedcomponentextract/inspect/compose/curated/preview. Eachindependentrun carriesReady209raw4, nowreextractedRGBAexactall4. No perframenormalize orlocaldraw. 6newtransparent512candidates unviewed untilRootE. All6near/fargripsmustbeindependentlytracedafterE; no motionbasislockfromraworQApass. SG6fpspreview1002ms notnative1000ms. No UE/nativecalls oractualSource/tools changes.\n')
write('extraction-freeze-v001.json',{'schema':'Guard212-two-row-standard-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'native_calls':0,'new_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for label,_,_,_ in jobs:
 for p in sorted((OUT/f'run-{label}-shared-HD-v001/qa').rglob('*')):
  if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/f'{label}-{p.name}')
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫212整六蓄力纠错透明提取','version':'v001','status':'two-standard-transparent-candidates-unviewed','source':OUT.as_posix(),'entries':entries,'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'entries':entries},ensure_ascii=False,indent=2))
