"""Observe exact shared-HD fit before unchanged min256 QA; publish no sprite PNG."""
from pathlib import Path
import contextlib,datetime,hashlib,importlib.util,io,json,shutil,sys
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
FAMILY=OUT.parents[1]
SOURCE=FAMILY/'primary2-leather-input-v001/run-farshoulder-primary2-v001'
WRAPPER=OUT.parent/'shared-HD-fit-explicit-component-min-v001.py'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as s:s.write(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return p
def bbox(mask):
 y,x=np.where(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(x) else None
def stats(im):
 a=np.asarray(im.convert('RGBA'));alpha=a[:,:,3];core=alpha>=128;green=np.all(a[:,:,:3]==[0,255,0],axis=2)
 return {'canvas_px':list(im.size),'nonzero_alpha_bbox_ltrb_exclusive':bbox(alpha>0),'core128_bbox_ltrb_exclusive':bbox(core),'nonzero_alpha_pixels':int(np.count_nonzero(alpha)),'core128_pixels':int(np.count_nonzero(core)),'green_nonzero_pixels':int(np.count_nonzero(green&(alpha>0))),'green_core128_pixels':int(np.count_nonzero(green&core)),'RGBA_memory_sha256':hashlib.sha256(a.tobytes()).hexdigest()}
run=OUT/'unchanged-min256-run-v001';state='leather_farshoulder_sword_primary2';copies=[]
for rel in [f'raw/{state}.png','sprite-request.json','base-source.png',f'prompts/{state}.txt']:
 src=SOURCE/rel;dest=run/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 assert src.read_bytes()==dest.read_bytes();copies.append({'source':pin(src),'copy':pin(dest)})
wrapper_pin=pin(WRAPPER)
spec=importlib.util.spec_from_file_location('exact_shared_min256_numeric_observer',WRAPPER);wrapper=importlib.util.module_from_spec(spec);spec.loader.exec_module(wrapper)
sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native
captures=[];native_codes=[]
original_fit=wrapper.fit_components_shared;original_main=native.main;original_argv=sys.argv

def observe_fit(*args,**kwargs):
 frames,record=original_fit(*args,**kwargs)
 captures.append({'shared_row_fit':record,'frame_metrics':[{'frame':i,**stats(im)} for i,im in enumerate(frames)]})
 return frames,record

def observe_native_main():
 code=original_main();native_codes.append(code);return code
wrapper.fit_components_shared=observe_fit;native.main=observe_native_main
log=io.StringIO();exception=None
try:
 sys.argv=[str(WRAPPER),'--run-dir',str(run),'--min-used-pixels','256']
 with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):wrapper.main()
except Exception as exc:
 exception={'type':type(exc).__name__,'message':str(exc)}
finally:
 wrapper.fit_components_shared=original_fit;native.main=original_main;sys.argv=original_argv
assert captures and native_codes==[1] and exception and not list((run/'frames').rglob('*.png'))
log_path=write('unchanged-min256-native.log',log.getvalue())
ready=FAMILY/'far187-extraction-v001/run-shared-smallcomponent-v002'
ready_manifest=ready/'frames/frames-manifest.json';ready_fm=json.loads(ready_manifest.read_text('utf-8-sig'));ready_metrics=[]
for i in range(4):
 path=ready/f'frames/leather_farshoulder_sword_ready/frame-{i}.png'
 with Image.open(path) as im:ready_metrics.append({'frame':i,'source':pin(path),**stats(im)})
report=write('far195-vs-ready187-floor-numeric-v001.json',{'schema':'exact-shared-HD-before-unchanged-sparse-QA-floor-review-v001','created_local':datetime.datetime.now().astimezone().isoformat(),'native_request':195,'source_canvas_preserved':[2171,724],'source_copies':copies,'wrapper':wrapper_pin,'native_extractor':pin(SG/'sprite_gen/frames/extract.py'),'native_min_used_pixels':256,'native_actual_return_codes':native_codes,'wrapper_exception':exception,'log':pin(log_path),'captures':captures,'new_sprite_PNG_published':False,'minimum_changed':False,'shape_or_RGBA_changed':False,'Ready187':{'native_request':187,'shared_frame_manifest':pin(ready_manifest),'shared_row_fit':ready_fm['rows'][0]['shared_row_fit'],'frame_metrics':ready_metrics,'floor_history':'Original standard512 rejected Ready187 at367/347/365/351nonzero; Root explicitly allowed256 only for this tiny isolated attachment, at unchanged30x28 rowfit. This does not authorize a lower floor for195 automatically.'},'interpretation':'191px only reports sparse area, not fit/motion or semantic component quality. Root must judge the exact compressed perspective and attachment design boundary before any new explicit floor. No mask, A/B or bodyfree semantics inferred.','new_media_viewed':False})
files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
freeze=write('numeric-review-freeze-v001.json',{'files':files,'native_still_failed_min256':True,'minimum_changed':False,'new_sprite_PNG_published':False,'new_media_viewed':False})
print(json.dumps({'report':pin(report),'freeze':pin(freeze),'actual195':captures,'Ready187':ready_metrics},indent=2))
