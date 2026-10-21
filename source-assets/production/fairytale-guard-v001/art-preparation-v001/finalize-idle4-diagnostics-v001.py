"""Finish preserved successful SG output; record the failed extra alpha assertion honestly."""
from pathlib import Path
from datetime import datetime
import hashlib, importlib.util, json, shutil, sys
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
OUT=HERE/'idle4-extraction-v001'; RUN=OUT/'run-idle207-shared-HD-v001'
SRC=HERE/'idle4-camera-fixed-generation-ready-v002/run-guard-right-idle-camera-v002'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
MEDIA=Path('F:/Ourgame/过程图稿与视频/2026-10-18_裂岩守卫207Idle4透明提取与锚候选_v001')
assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
assert not MEDIA.exists()
def pin(p):
 b=p.read_bytes(); return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,v):
 p=OUT/n; p.parent.mkdir(parents=True,exist_ok=True)
 content=v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n'
 if p.exists(): assert p.read_text(encoding='utf-8')==content; return p
 with p.open('x',encoding='utf-8',newline='\n') as f: f.write(content)
 return p
def stats(im):
 a=np.asarray(im.convert('RGBA')); al=a[:,:,3]; mag=np.all(a[:,:,:3]==[255,0,255],axis=2)
 yy,xx=np.where(mag&(al>0))
 return {'pure_magenta_any_alpha':int((mag&(al>0)).sum()),'pure_magenta_core128':int((mag&(al>=128)).sum()),'magenta_pixels_xy_rgba':[[int(x),int(y),a[y,x].tolist()] for x,y in zip(xx,yy)]}
raw=SRC/'raw/right/idle.png'
assert pin(raw)['sha256']=='1f44fb362265ad5af6a7dda18cd9c3b8ed3948ff13a482540770581a0f8c124f'
sys.path.insert(0,str(SG)); import sprite_gen.frames.extract as native
keyed=native.remove_chroma_background(Image.open(raw),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
components=native.extract_component_images(keyed,4); assert len(components)==4
spec=importlib.util.spec_from_file_location('existing_shared_fit',OUT/'shared-HD-fit-existing-exact.py'); bridge=importlib.util.module_from_spec(spec); spec.loader.exec_module(bridge)
fitted, shared=bridge.fit_components_shared(components,512,512,48,48)
rows=[]
for i in range(4):
 p=RUN/f'curated/frame-{i}.png'; before=RUN/f'frames/right/idle/frame-{i}.png'; im=Image.open(p); a=np.asarray(im); al=a[:,:,3]
 assert a.shape==(512,512,4) and np.array_equal(a,np.asarray(Image.open(before))) and np.array_equal(a,np.asarray(fitted[i]))
 rows.append({'frame':i,'source':pin(p),'precuration':pin(before),'curated_RGBA_equal':True,'in_memory_replay_RGBA_equal':True,'canvas':[512,512],'duration_ms':250,'alpha_nonzero_bbox_DIAGNOSTIC_ONLY':list(im.getbbox()),'alpha_nonzero_pixels':int((al>0).sum()),'core128_pixels':int((al>=128).sum()),'partial_alpha_pixels':int(((al>0)&(al<255)).sum()),'chroma_diagnostic':stats(im),'RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'hidden_bones_or_grips_measured':False})
diag=write('extra-postcheck-failure-and-stage-trace-v001.json',{'schema':'Guard207-extra-absolute-alpha-check-diagnostic-v001','preserved_failure':{'script':pin(HERE/'extract-curate-idle4-v001.py'),'line':45,'assertion':'pure_magenta_any_alpha == 0','actual_result':'failed on frame1 after all standard pipeline commands had exit0','standard_QA_was_not_relaxed':True},'keyed_raw':stats(keyed),'components_before_shared_fit':[stats(p) for p in components],'fitted_frames':[r['chroma_diagnostic'] for r in rows],'inference':'The exact magenta low-alpha pixels first occur after the existing LANCZOS shared fit. This is an edge diagnostic, not missing core material. No repaint, erasure or re-generation was performed.','Root_scope_decision':'Root explicitly accepts SG QA0/motion no warnings/core128magenta0 as a production candidate; any-alpha1 diagnostic remains recorded, pending actual transparent review.'})
anchor=OUT/'right-idle-anchor-CANDIDATE/frame-0.png'; anchor.parent.mkdir(exist_ok=True)
if not anchor.exists(): shutil.copyfile(RUN/'curated/frame-0.png',anchor)
assert pin(anchor)['sha256']==pin(RUN/'curated/frame-0.png')['sha256']
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8')); ins=json.loads((RUN/'inspect-report.json').read_text(encoding='utf-8'))
assert fm['ok'] and fm['errors']==fm['warnings']==[] and ins['ok']
sourcepins=[]
for rel in ['sprite-request.json','base-source.png','raw/right/idle.png','prompts/right/idle.txt','references/layout-guides/right/idle.png']:
 p=SRC/rel; q=RUN/rel
 if rel=='sprite-request.json':
  original=json.loads(p.read_text(encoding='utf-8')); actual=json.loads(q.read_text(encoding='utf-8'))
  assert actual.pop('chroma')=={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005} and actual==original
 else: assert pin(p)['sha256']==pin(q)['sha256']
 sourcepins.append(pin(p))
index=write('idle207-four-curated-source-index-v001.json',{'schema':'Guard207-Idle4-shared-curated-source-index-v001','created_local':datetime.now().astimezone().isoformat(),'native207_raw':pin(raw),'raw_review':'Root E353 bothSHA0 then actualView and extraction authorization','rows':rows,'one_shared_row_fit':fm['rows'][0]['shared_row_fit'],'durations_ms':[250]*4,'anchor_frame0_candidate':pin(anchor),'anchor_status':'Pending E-retained transparent and motion actual review and Root internal production lock; not user final aesthetic acceptance.','role':'Empty neutral body identity / dormant or unarmed idle candidate. NOT armed idle: its two fists do not share the 208 shaft axis.','future_identity_flow':'After accepted curated207Idle0, ArmedReady uses that body identity plus separate208 prop; after acceptedArmedReady0, armed rows use that identity, never206base.','new_output_images_viewed':False})
commands=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((OUT/'logs').glob('*-command.json'))]; assert len(commands)==5 and all(c['actual_exit_code']==0 for c in commands)
proof=write('idle207-extraction-proof-v001.json',{'schema':'Guard207-Idle4-standard-pipeline-proof-v001','commands':commands,'standard_extract_and_inspect_ok':True,'source_index':pin(index),'extra_diagnostic':pin(diag),'native_generation_calls':0,'runtime_or_final_art_accepted':False,'images_viewed':False,'source_mismatches':0})
write('HANDOFF.md','207 completed standard component extraction → inspect → compose → curated4 → preview, all exit0. One shared scale 0.7415329768270945; four transparent512 cells,250ms each. The original extra absolute-any-alpha-magenta assertion failed honestly: frames1/2 each have one RGBA[255,0,255,1] edge pixel after shared LANCZOS; core128magenta0, unchanged SG QA0 and no motion warnings. Pixels are preserved. Idle0 is an exact candidate copy, not yet accepted. Empty neutral body identity cannot be treated as armed Ready. New fixed-208-axe whole-sprite rows replace the prior unnecessary enemy hand-rig plan. No native generation, UE, actual Source/tools/ledger/README writes. Canonical F media requires Root E retention before View.\n')
write('extraction-freeze-v001.json',{'schema':'Guard207-Idle4-extraction-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'sourcepins':sourcepins,'source_mismatches':0,'new_output_images_viewed':False})
(MEDIA/'原件').mkdir(parents=True); shutil.copytree(OUT,MEDIA/'原件/提取包'); (MEDIA/'展示副本').mkdir()
for p in sorted((RUN/'qa').rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.gif','.json'): shutil.copyfile(p,MEDIA/'展示副本'/p.name)
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f: json.dump({'date':'2026-10-18','topic':'裂岩守卫207Idle4透明提取与锚候选','version':'v001','status':'transparent-curated-candidate-unviewed','source':OUT.as_posix(),'proof':pin(proof),'source_index':pin(index),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]},f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps({'canonical_media':MEDIA.as_posix(),'source_index':pin(index),'anchor':pin(anchor),'standard_commands':len(commands),'standard_all_exit0':True,'new_images_viewed':False},ensure_ascii=False,indent=2))
