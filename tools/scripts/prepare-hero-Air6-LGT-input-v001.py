"""Prepare three isolated current LGT component rows paired with source253."""
from pathlib import Path
import ast, hashlib, json, shutil, subprocess, sys
import numpy as np
from PIL import Image
R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-hero-state-gap-v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen'); PY=SG/'.venv/Scripts/python.exe'
assert Path(sys.executable).resolve()==PY.resolve()
O=B/'air-state-preparation-v001/armor-standard-input-v001'
M=R/'过程图稿与视频/2026-10-18_钟盔跳跃六相棕皮三层输入_v001'
assert not O.exists() and not M.exists();O.mkdir(parents=True)
def pin(p):
 d=p.read_bytes();return dict(path=p.as_posix(),bytes=len(d),sha256=hashlib.sha256(d).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=O/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
source=B/'air-state-preparation-v001/extraction-v001/run-Air6-shared-HD-v001/frames/jump_nonattack'
frames=[source/f'frame-{i}.png' for i in range(6)]
arrays=[np.array(Image.open(p).convert('RGBA')) for p in frames]
assert all(a.shape==(512,512,4) for a in arrays)
motion=O/'references/Air253-six-EXACT-RGBA-motion-only.png';motion.parent.mkdir();Image.fromarray(np.concatenate(arrays,axis=1)).save(motion)
assert all(np.array_equal(np.array(Image.open(motion))[:,512*i:512*(i+1)],a) for i,a in enumerate(arrays))
manifest=R/'source-assets/production/fairytale-lgt-readability-v003/ready-import-v001/import-leather-ready-v001.json'
eindex=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-integer-fit-v278/source-size-SHA256.json')
retained=[]
def collect(v):
 if isinstance(v,dict):
  if 'sha256' in v and 'retained_relative' in v:retained.append(v)
  for z in v.values():collect(z)
 elif isinstance(v,list):
  for z in v:collect(z)
collect(read(eindex))
parts=[
 dict(token='chest',component='Chest',native=184,window=[128,100],minimum=512,specific='ONLY the current warm brown supple leather jerkin: same small round golden front fastening, connected waist belt and small pouch on image LEFT. Genuine green negative-space neck and arm openings; no black filled cavity, gray lining or opaque backing. Match the actual gray-cloth torso in each Air253 pose: subtle extended rise, compressed late rise, compact apex, reopened descent, deep landing compression, upright settle. Keep the waist at the source belt and openings around the source shoulder. The helmet and unchanged near arm later occlude it. No shoulder caps, sleeves, limbs, head, weapon, detached pieces or new decorations.'),
 dict(token='nearshoulder',component='ShoulderNear',native=186,window=[60,44],minimum=512,specific='ONLY the current short rounded foreground brown leather shoulder cap with the same tiny diamond stitch. NEAR means the image LEFT foreground upper sleeve, beside the larger image-left glove, in all six Air253 sources. Follow its actual six shoulder inclinations; retain coherent cap density and construction. No chest, far tab, gray sleeve or lining, limbs, head, weapon, new rivets or straps.'),
 dict(token='farshoulder',component='ShoulderFar',native=187,window=[32,30],minimum=256,specific='ONLY the current tiny narrow curved recessed brown leather FAR tab. FAR means image RIGHT, recessed behind actual torso/helmet in every Air253 source. Preserve the same thin tab construction, coherent density and physical side across six genuine perspectives. No gold, rivets, buckle, strap, broad near cap, oval ring, lining, gray sleeve, body, head, weapon or backing. Natural body occlusion happens later; do not paint the body into this component.')]
common='''Exactly SIX isolated complete views of ONLY the named current brown leather component. Reference1 is the sole accepted Ready component APPEARANCE identity. Reference2 is six exact original Air253 body cells for camera, pose, gray-cloth and shoulder orientation ONLY; it is not armor identity. Reference3 is the official six-slot layout guide ONLY. Never draw the reference character or guide. Pose order 0 early rise, 1 late rise, 2 compact apex, 3 descent, 4 deep landing impact, 5 landing settle. Use the same shallow elevated three-quarter view facing screen RIGHT as these actual sources. Retain anatomical near/far physical sides, material, construction and coherent garment density; perspective changes naturally, never enlarge each view to fill its safe window. One complete connected named component in every equal invisible cell, on flat #00FF00. No character, hands, limbs, head, helmet, weapons, other armor, shadows, scene, markers, labels, grid, guide or effects. True neck/arm openings are flat green negative space, no opaque black interior or lining. Later fitting uses integer translation and own-source occlusion, without altering body pixels. These six views sample actual ballistic/landing presentation, not a new gameplay clock.'''
adapter_source=B/'lgt-hurt4-standard-input-v001/prepare-three-current-leather-Hurt4-rows-v001.py'
text=adapter_source.read_text(encoding='utf-8-sig');node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='adapt')
code=ast.get_source_segment(text,node).replace('Hurt227','Air253').replace('Hurtperspective','Airperspective').replace('fourmatching','sixmatching').replace('Exactly 4 full-body frames','Exactly 6 full-body frames').replace('Exactly4 isolated','Exactly6 isolated')
ns={};exec(compile(code,'explicit-Air6-component-prompt-adapter','exec'),ns)
rows=[]
for c in parts:
 entry=next(x for x in read(manifest)['assets'] if x['component']==c['component'] and x['frame']==0)
 identity=Path(entry['source']);assert pin(identity)['sha256']==entry['source_sha256']
 ep=eindex.parent/next(x['retained_relative'] for x in retained if x['sha256']==entry['source_sha256'])
 for _ in range(2):assert identity.read_bytes()==ep.read_bytes()
 token=c['token'];state='leather_'+token+'_hero_air6';w,h=c['window']
 seed=dict(cell=dict(shape='square',width=512,height=512,safe_margin_x=(512-w)//2,safe_margin_y=(512-h)//2),states={state:dict(frames=6,fps=10,loop=False,action=common+'\n'+c['specific'])},style='Current accepted '+c['component']+' native'+str(c['native'])+' only; coarse ink, broad readable brown planes, same construction and physical side.',motion_phase_guides=False,fit=dict(pixel_unfake=False,resample='lanczos',align_x='bbox-center',align_y='bottom',ground_frames=False,segmentation='components',shared_row_scale=True))
 seedpath=write(token+'/standard-request-input-v001.json',seed);run=O/token/('run-LGT-'+token+'-Air6-v001')
 argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','current-brown-LGT-'+token+'-Air253-overlay','--base-image',str(identity),'--chroma-key','#00FF00','--request',str(seedpath)]
 r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write(token+'/prepare.log',r.stdout+r.stderr);assert r.returncode==0,r.stderr
 request=run/'sprite-request.json';q=read(request);write(token+'/official-original-request.json',q)
 q['chroma']=dict(mode='rgb',unmix_reach=4,spill_max_fraction=.005);request.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 prompt=run/'prompts'/f'{state}.txt';old=prompt.read_text(encoding='utf-8');write(token+'/official-original-prompt.txt',old)
 adapted,changes=ns['adapt'](old)
 adapted=adapted.replace('pure side profile view facing camera-right','same shallow elevated three-quarter view facing screen right as the exact Air253 sources')
 adapted=adapted.replace('- Accepted idle/direction anchors own character identity, outfit details, colors, face design, asymmetric markings, and side-specific accessories for final action rows.','- Reference1 owns ONLY this armor component appearance; Air253 owns ONLY pose and camera. No body, face, outfit or accessory generation.')
 prompt.write_text(adapted,encoding='utf-8',newline='\n')
 full=write(token+'/Root-native-fullprompt-v001.txt','REFERENCE ORDER: 1 current accepted own Ready armor component ONLY; 2 exact Air253 body6 for motion ONLY; 3 official guide for layout ONLY.\n'+adapted+'\n\nCOMPONENT FINAL AUTHORITY:\n'+c['specific']+'\n')
 guide=run/'references/layout-guides'/f'{state}.png'
 refs=[dict(file=pin(p),role=role,already_retained=False) for p,role in [(identity,'sole component appearance identity'),(motion,'six exact Air253 RGBA cells, pose/camera only'),(guide,'official six-slot safe-window layout only')]]
 plan=write(token+'/references-pending-E-v001.json',dict(references_in_order=refs,requires_actual_E_twoSHA_before_use=True))
 rows.append(dict(component=c['component'],native_identity=c['native'],state=state,run=run.as_posix(),source_identity=pin(identity),source_identity_E=pin(ep),prompt=pin(full),reference_plan=pin(plan),request=pin(request),guide=pin(guide),window=c['window'],min_used_pixels=c['minimum'],preview_fps_not_gameplay_clock=True,shared_scale=True,adapter_changes=changes,output=(B/f'air-state-preparation-v001/armor-generation-v001/{token}/raw/{state}.png').as_posix(),accepted=False))
handoff=write('input-handoff-v001.json',dict(schema='Root-Air253-LGT-three-inputs-v001',rows=rows,source_body=[pin(p) for p in frames],motion_reference=pin(motion),exact_RGBA_concatenation=True,appearance_manifest=pin(manifest),identity_E_index=pin(eindex),generated=False,fit_metadata=None,native_imported=False,viewed=False))
(M/'原件').mkdir(parents=True);shutil.copytree(O,M/'原件/输入完整包');shutil.copy2(Path(__file__),M/'原件'/Path(__file__).name)
(M/'展示副本').mkdir();shutil.copy2(motion,M/'展示副本'/motion.name)
for row in rows:
 shutil.copy2(row['guide']['path'],M/'展示副本'/(row['component']+'-guide.png'))
 shutil.copy2(row['source_identity']['path'],M/'展示副本'/(row['component']+'-accepted-identity.png'))
(M/'index.json').write_text(json.dumps(dict(status='unviewed inputs only; E before reference use',handoff=pin(handoff),files=[pin(p) for p in sorted(M.rglob('*')) if p.is_file()],generation_calls=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(M/'README.md').write_text('钟盔Air253六相配套棕皮轻甲三组件输入。现用Chest184/Near186/Far187各自为唯一外观身份；六相角色只供姿态与镜头参考。正式sprite-gen prepare，原始提示词及显式组件适配均保留；未生成、未适配、未导入或接受。E两SHA后才能引用新图。\n',encoding='utf-8')
print(json.dumps(dict(input=O.as_posix(),archive=M.as_posix(),rows=len(rows)),ensure_ascii=False))
