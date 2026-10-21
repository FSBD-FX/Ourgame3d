"""Existing retained native208 -> standard single component prop candidate; no generation."""
from pathlib import Path
from datetime import datetime
import hashlib,json,subprocess,shutil,sys
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent; ROOT=Path('F:/Ourgame')
OUT=HERE/'heavyaxe-extraction-v001'; RUN=OUT/'run-axe208-shared-HD-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen'); PY=SG/'.venv/Scripts/python.exe'
RAW=HERE/'heavyaxe-reference-ready-v001/raw/guard-heavyaxe-identity.png'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫208固定重斧透明提取_v001'
assert Path(sys.executable).resolve()==PY.resolve(); OUT.mkdir(exist_ok=False); assert not MEDIA.exists()
def pin(p):
 b=p.read_bytes(); return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n; p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f: f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def command(name,args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8'); log=write('logs/'+name+'.log',r.stdout+r.stderr)
 rec={'argv':args,'actual_exit_code':r.returncode,'log':pin(log)};write('logs/'+name+'-command.json',rec);assert r.returncode==0,rec;return rec
rawpin=pin(RAW);assert rawpin['sha256']=='9cff2c33ad3d3b7f03dfe50eef71807a0bac6cdd2795aa414dc0d4b16303f632'
assert Image.open(RAW).size==(1254,1254)
q={'cell':{'shape':'square','width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},'states':{'idle':{'frames':1,'fps':1,'loop':False,'action':'Existing retained native208 single fixed heavyaxe prop identity. One complete continuous straight wood haft, single stone axe head and buttcap. No body or hands. This run is extraction of retained source, not a request to generate another image.'}},'style':'Match retained208 exactly, coarse stone planes and ink. Fixed enemy equipment, not hero modular rig.','motion_phase_guides':False,'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
inp=write('standard-request-input-v001.json',q)
prepare=command('prepare-axe208',[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),'--character-id','ENM-STN-003-heavyaxe-prop-v001','--base-image',str(RAW),'--chroma-key','#FF00FF','--request',str(inp)])
assert json.loads((RUN/'sprite-request.json').read_text(encoding='utf-8'))['states']['idle']['frames']==1
(RUN/'raw').mkdir(exist_ok=True); shutil.copyfile(RAW,RUN/'raw/idle.png')
bridge=HERE/'idle4-extraction-v001/shared-HD-fit-existing-exact.py';shutil.copyfile(bridge,OUT/'shared-HD-fit-existing-exact.py')
extract=command('extract-axe208',[str(PY),'-B','-X','utf8',str(OUT/'shared-HD-fit-existing-exact.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
inspect=command('inspect-axe208',[str(PY),'-B','-X','utf8',str(SG/'scripts/inspect_sprite_run.py'),'--run-dir',str(RUN),'--states','idle','--report',str(RUN/'inspect-report.json')])
compose=command('compose-axe208',[str(PY),'-B','-X','utf8',str(SG/'scripts/compose_sprite_atlas.py'),'--run-dir',str(RUN),'--min-used-pixels','512'])
sys.path.insert(0,str(SG));from sprite_gen.curate.curation import stamp_curation,load_curation,state_plan
assert load_curation(RUN) is None
payload=stamp_curation(RUN,{'version':1,'kind':'sprite-gen-curation','states':{'idle':{'selected':[0],'transforms':{}}}});write(RUN.relative_to(OUT)/'curation.json',payload)
assert state_plan(load_curation(RUN),'idle',1)==([0],{})
export=command('export-curated-axe208',[str(PY),'-B','-X','utf8',str(SG/'scripts/export_curated_pngs.py'),'--run-dir',str(RUN),'--state','idle','--selected-only'])
preview=command('preview-axe208',[str(PY),'-B','-X','utf8',str(SG/'scripts/preview_animation.py'),'--run-dir',str(RUN)])
p=RUN/'curated/frame-0.png';im=Image.open(p);a=np.asarray(im);assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(RUN/'frames/idle/frame-0.png')))
al=a[:,:,3];mag=np.all(a[:,:,:3]==[255,0,255],axis=2);fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'));assert fm['ok'] and fm['errors']==fm['warnings']==[]
index=write('axe208-curated-source-index-v001.json',{'schema':'Guard208-prop-standard-curated-source-index-v001','raw':rawpin,'raw_retention_and_actual_View':'Root E355 twoSHA0; worker actual source View after permission.','curated':pin(p),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'curated_RGBA_equal':True,'canvas':[512,512],'alpha_nonzero_bbox_DIAGNOSTIC_NOT_AXIS':list(im.getbbox()),'alpha_nonzero_pixels':int((al>0).sum()),'core128_pixels':int((al>=128).sum()),'partial_alpha_pixels':int(((al>0)&(al<255)).sum()),'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'shared_fit':fm['rows'][0]['shared_row_fit'],'actual_curated_axis_grip_ranges':None,'measurement_gate':'After new transparent output E retained and actual View. Visible wood range and artist shaft axis only, no bone inference.','role':'Independent retained prop identity, future optional prop use. Armed enemy rows bake this fixed axe with actual closed-hand poses.','runtime_or_final_art_accepted':False,'new_output_images_viewed':False})
proof=write('axe208-standard-pipeline-proof-v001.json',{'schema':'Guard208-standard-prop-pipeline-proof-v001','commands':[prepare,extract,inspect,compose,export,preview],'source_index':pin(index),'source_unchanged':pin(RAW)==rawpin,'native_calls':0,'Source_tools_UE_changes':False})
write('HANDOFF.md','Native208 retained original has passed standard single-component prepare/extract/inspect/compose/curated/preview. Independent prop candidate only. Fixed enemy Ready/actions will bake the same axe into each complete transparent frame so two hands and weight are generated as true poses. Neutral207 fists cannot receive a pasted shaft. No local painting, grip guessing, native call, UE or actual Source/tools changes. Final512 shaft axis/visible wood/grip ranges need new-output E retention then actual View.\n')
write('extraction-freeze-v001.json',{'schema':'Guard208-prop-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'raw_source':rawpin,'source_mismatches':0,'new_output_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/提取包');(MEDIA/'展示副本').mkdir()
for p in sorted((RUN/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump({'date':'2026-10-18','topic':'裂岩守卫208固定重斧透明提取','version':'v001','status':'transparent-prop-candidate-unviewed','source':OUT.as_posix(),'proof':pin(proof),'source_index':pin(index),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'index':pin(index),'curated':pin(RUN/'curated/frame-0.png'),'shared_scale':fm['rows'][0]['shared_row_fit']['scale'],'new_images_viewed':False},ensure_ascii=False,indent=2))
