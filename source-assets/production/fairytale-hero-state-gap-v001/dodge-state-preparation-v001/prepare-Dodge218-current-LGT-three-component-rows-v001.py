from pathlib import Path
import ast, hashlib, json, shutil, subprocess, sys
import numpy as np
from PIL import Image

ROOT=Path('F:/Ourgame')
BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'
HERE=Path(__file__).resolve().parent
OUT=HERE/'armor-standard-input-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge218棕皮三层标准输入_v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
PY=SG/'.venv/Scripts/python.exe'
assert Path(sys.executable).resolve()==PY.resolve()
assert not OUT.exists() and not MEDIA.exists()
OUT.mkdir()

def pin(p):
 b=p.read_bytes(); return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:
  f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p

audit=HERE/'source-retention-audit-v001.json'
source_audit=read(audit)
assert source_audit['own_current_F_E_twoSHA_passes']==2
motion_arrays=[]; motion_sources=[]
for row in source_audit['curated4']:
 p=Path(row['F']['path']); e=Path(row['E']['path'])
 assert pin(p)==row['F'] and p.read_bytes()==e.read_bytes()
 a=np.array(Image.open(p).convert('RGBA')); assert a.shape==(512,512,4)
 assert hashlib.sha256(a.tobytes()).hexdigest()==row['source_RGBA_SHA256']
 motion_arrays.append(a); motion_sources.append(pin(p))
motion=OUT/'references/Dodge218-four-original-RGBA-PAIRED-MOTION-ONLY.png'
motion.parent.mkdir()
Image.fromarray(np.concatenate(motion_arrays,axis=1)).save(motion)
check=np.array(Image.open(motion).convert('RGBA'))
assert all(np.array_equal(check[:,i*512:(i+1)*512],a) for i,a in enumerate(motion_arrays))
proof=write('Dodge218-motion-reference-exact-four-cell-proof-v001.json',{
 'source':motion_sources,'reference':pin(motion),'canvas':[2048,512],
 'all_four_entire_RGBA_cells_exact':True,
 'operation':'Concatenate the four original 512 RGBA arrays only; no crop, rescale, mirror, painting, armor, sword, mask or pose substitution.',
 'authority':'Dodge218 body motion/camera/visible cloth and shoulder orientation only, never armor appearance.',
 'new_media_viewed':False,'new_media_retained_E':False})

LGT=ROOT/'source-assets/production/fairytale-lgt-readability-v003'
manifest_path=LGT/'ready-import-v001/import-leather-ready-v001.json'
manifest=read(manifest_path)
receipt_ref=LGT/'ready-import-v001/actual-import-receipt-ref.json'
ref=read(receipt_ref); receipt_path=Path(ref['path']); assert pin(receipt_path)==ref
receipt=read(receipt_path)
assert receipt['success'] and receipt['actual_count']==12 and receipt['saved_count']==12
assert receipt['manifest_sha256']==pin(manifest_path)['sha256']
assert manifest['namespace']=='/Game/Production/ArtTrials/EV048/v012/HeroLeatherReady'
E278=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-leather-integer-fit-v278')
E278_index=E278/'source-size-SHA256.json'
retained=[]
def collect(x):
 if isinstance(x,dict):
  if 'sha256' in x and 'retained_relative' in x: retained.append(x)
  for v in x.values(): collect(v)
 elif isinstance(x,list):
  for v in x: collect(v)
collect(read(E278_index))

components=[
 {'token':'chest','runtime':'Chest','native_identity':184,'window':[128,100],'min_used_pixels':512,
  'specific':'''ONLY the same warm brown supple leather jerkin with the same small round golden front fastening, integrated waist belt and attached small pouch. Preserve the pouch on its original physical side: image LEFT in this native-right view. Do not swap pouch and front fastening. The neckline and side arm apertures are TRUE background green negative space; absolutely no opaque black cavity/backing, no black filled inner shirt, no gray lining or torso. Retain the actual dark edge ink only. The armhole must reveal the unchanged gray source undercloth after compositing. Match actual Dodge218 visible torso orientations: phase0 compact forward brace, phase1 deeply crouched and folded forward under the low helmet, phase2 rising forward lean, phase3 upright return. In phase1 the collar is mostly occluded by the helmet; do not invent a visible front-facing tall vest or lift the collar through the helmet. Put the belt/fastening along the source waist. Generate the complete connected jerkin for this orientation, with upper portions allowed to be hidden later by the actual helmet/near-arm. No shoulder caps, arms, hands, head, helmet, trousers, sword, detached pouch, detached buckle, extra straps or new decorations.''',
  'style':'Same accepted Chest184 brown leather, coarse dark ink, same small golden fastening and original connected pouch/belt construction. Large readable planes. True green apertures, no opaque black backing.'},
 {'token':'nearshoulder','runtime':'ShoulderNear','native_identity':186,'window':[60,44],'min_used_pixels':512,
  'specific':'''ONLY the same short rounded foreground brown leather shoulder cap with its existing tiny diamond stitch detail. Physical NEAR shoulder is the image LEFT foreground shoulder in every Dodge218 source. Follow this actual arm/shoulder compression: phase0 forward brace, phase1 folded forward behind the lowered helmet, phase2 forward rise, phase3 upright return. Keep the same cap construction and physical side; no mirror substitution. Do not broaden into a chest plate or long ring. No far tab, vest, belt, pouch, gray sleeve/lining, arm/hand, head/helmet, sword or new gold rivets.''',
  'style':'Same accepted Near186 short rounded brown leather cap and existing diamond stitch detail; coarse ink and large low-detail planes, no new construction.'},
 {'token':'farshoulder','runtime':'ShoulderFar','native_identity':187,'window':[32,30],'min_used_pixels':256,
  'specific':'''ONLY the tiny narrow curved recessed brown leather FAR tab in reference1 and its exact enlarged view reference2. Physical FAR shoulder is image RIGHT, recessed behind the torso/head in all four Dodge218 poses. Preserve the sole thin curved tab silhouette and perspective; foreshorten it to the actual four source shoulders without changing it into the near cap. NO GOLD, no rivet, buckle, strap, lining, cup, padded broad cap, long oval ring, gray cloth, full sleeve, arm, hand, chest, head/helmet or sword. One complete connected thin tab per slot. It may later be occluded by unchanged source body pixels, but do not draw those body pixels or add a backing to it.''',
  'style':'Sole accepted Far187 thin curved brown tab, coarse dark outline, restrained brown fill. NO gold, rivet, buckle, strap, lining, cup, broad cap or new fastening.'}
]
identities=[]
for c in components:
 a=next(a for a in manifest['assets'] if a['component']==c['runtime'] and a['frame']==0)
 p=Path(a['source']); assert pin(p)['sha256']==a['source_sha256'] and pin(p)['bytes']==a['source_bytes']
 rr=next(r for r in retained if r['sha256']==a['source_sha256']); e=E278/rr['retained_relative']
 for _ in range(2): assert p.read_bytes()==e.read_bytes() and pin(p)['sha256']==pin(e)['sha256']
 rec=next(r for r in receipt['assets'] if r['component']==c['runtime'] and r['frame']==0)
 assert rec['source_sha256']==a['source_sha256'] and rec['actual_object_type']=='Texture2D'
 c['source']=p; c['runtime_asset']=a
 identities.append({'component':c['runtime'],'accepted_native_identity':c['native_identity'],'source_F':pin(p),'retained_E':pin(e),'current_F_E_twoSHA_equal':True,'actual_current_object_path':a['object_path']})
identity_evidence=write('current-LGT-three-identities-and-Dodge-source-authority-v001.json',{
 'actual_three_components':['Chest','ShoulderNear','ShoulderFar'],'current_import_manifest':pin(manifest_path),
 'actual_import_receipt':pin(receipt_path),'E278_retention_index':pin(E278_index),'identities':identities,
 'Dodge218_motion_source_audit':pin(audit),'body_source_four':motion_sources,
 'Hurt227_used_as_Dodge':False,'Hurt233_used_as_armor_identity':False,'old_gray_armor_used':False,
 'appearance_authority':'Each own currently imported brown Ready component alone. Dodge218 owns only pose/perspective and later overlay coordinates.',
 'component_count':3,'future_source_A_B_delta':None,'native_or_equipment_accepted':False})

# Reuse only the proven explicit text adapter. The older prepared runs stay untouched.
adapter_src=BASE/'lgt-hurt4-standard-input-v001/prepare-three-current-leather-Hurt4-rows-v001.py'
adapter_text=adapter_src.read_text(encoding='utf-8-sig')
node=next(n for n in ast.parse(adapter_text).body if isinstance(n,ast.FunctionDef) and n.name=='adapt')
adapter=ast.get_source_segment(adapter_text,node).replace('Hurt227','Dodge218').replace('Hurtperspective','Dodgeperspective')
adapter_ns={}; exec(compile(adapter,'explicit-prompt-adapter','exec'),adapter_ns); adapt=adapter_ns['adapt']

COMMON='''Create exactly FOUR isolated views of ONLY the specified CURRENT brown leather armor component, in the exact Dodge218 source order 0,1,2,3. The first reference is this same accepted current Ready component and is the SOLE appearance identity. Preserve its construction, palette, broad shapes, ink, material, physical side and existing details only. Do not borrow armor from another component or body outfit. The exact Dodge218 four-cell original RGBA strip supplies ONLY camera, torso lean, visible gray-cloth region and physical shoulder orientation. The official guide supplies ONLY four-cell count, spacing and the maximum safe window. Never draw the source character or any part of the guide.
Use the SAME shallow elevated three-quarter side view facing SCREEN RIGHT as the actual Dodge218 sources and accepted Ready identity. Do not change into a pure 90-degree side profile, front view, rear view or mirrored physical side. Pose order: 0 forward compact brace; 1 deepest low forward crouch with helmet over the folded torso; 2 rising forward lean; 3 upright return. These are Dodge218, not Hurt227 recoil poses. Keep one actual garment density and construction across all four views; do not use four copies of Ready, and do not make each view fill the same bounding box. The numerical safe window is an upper bound, not a request to enlarge every pose to fill it. Camera and garment density stay coherent while perspective changes.
One complete connected specified armor component per invisible equal cell with generous flat #00FF00 green surround. No whole character, gray undercloth, head, helmet, arms, hands, legs, shoes, sword, extra armor parts, colored guide, labels, grid, scene, shadows, loose fragments, effects or blur. Do not use green or key-adjacent material colors. Dark outline is allowed; solid black filled cavities/backing are forbidden. Neck/arm apertures that are holes must be genuine green background connected negative space.
Actual Dodge218 body and hand RGBA stay unchanged. Armor will later be placed by integer translations and own-source occlusion partitions, so follow the actual source perspectives rather than painting corrective body/hand pixels. There are no measured hidden bones or grip/axes in these refs. Do not draw markers. The real dodge remains 400ms with four 100ms samples; do not alter movement, invulnerability, collision, binding or action priority. Output only four component views, left to right, on flat green.'''

rows=[]
for c in components:
 token=c['token']; state=f'leather_{token}_hero_dodge'; window=c['window']
 seed={'cell':{'shape':'square','width':512,'height':512,'safe_margin_x':(512-window[0])//2,'safe_margin_y':(512-window[1])//2},
  'states':{state:{'frames':4,'fps':10,'loop':False,'action':COMMON+'\n\n'+c['specific']}},
  'style':c['style'],'motion_phase_guides':False,
  'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
 seedpath=write(f'{token}/standard-request-input-v001.json',seed)
 run=OUT/token/f'run-leather-{token}-Dodge4-v001'
 argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',f'current-brown-LGT-{token}-Dodge218-overlay-candidate','--base-image',str(c['source']),'--chroma-key','#00FF00','--request',str(seedpath)]
 result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
 log=write(f'{token}/logs/standard-prepare.log',result.stdout+result.stderr); assert result.returncode==0,(token,result.stderr)
 request=run/'sprite-request.json'; q=read(request)
 write(f'{token}/official-original-request-before-explicit-timing-chroma.json',q)
 q['states'][state]['durations_ms']=[100]*4; q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
 request.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 prompt=run/f'prompts/{state}.txt'; old=prompt.read_text(encoding='utf-8')
 write(f'{token}/official-original-prompt-before-component-adapter.txt',old)
 new,changes=adapt(old)
 camera='pure side profile view facing camera-right'
 if camera in new:
  count=new.count(camera); new=new.replace(camera,'same shallow elevated three-quarter side view facing screen right as the exact Dodge218 source')
  changes.append({'before':camera,'after':'same shallow elevated three-quarter side view facing screen right as the exact Dodge218 source','count':count})
 # This is a component authority clarification, not a sprite-gen source-code edit.
 new=new.replace('- Accepted idle/direction anchors own character identity, outfit details, colors, face design, asymmetric markings, and side-specific accessories for final action rows.',
  '- Reference 1 owns ONLY this armor component identity/material/physical side. Dodge218 owns ONLY pose and camera; generate no face, body, outfit or accessories.')
 prompt.write_text(new,encoding='utf-8',newline='\n')
 identity=run/'references/accepted-current-LGT-Ready-component-frame0.png'; shutil.copyfile(c['source'],identity)
 paired=run/'references/Dodge218-four-original-RGBA-PAIRED-MOTION-ONLY.png'; shutil.copyfile(motion,paired)
 guide=run/f'references/layout-guides/{state}.png'
 refs=[{'file':pin(identity),'role':f'REFERENCE 1: SOLE appearance identity, current accepted brown Ready {c["runtime"]}, native{c["native_identity"]}; retain its physical side and construction only.','already_retained':True}]
 prelude='REFERENCE ORDER: 1 = sole accepted current Ready component appearance identity; 2 = exact Dodge218 four original cells, motion/camera/overlay only; 3 = official four-slot guide, layout only.\n'
 if c['runtime']=='ShoulderFar':
  ai=np.array(Image.open(c['source']).convert('RGBA')); mask=ai[:,:,3]>0; yy,xx=np.where(mask)
  box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]; assert box==[290,249,310,277],box
  crop=Image.fromarray(ai).crop(tuple(box)); aux=run/'references/accepted-Far187-EXACT20x28-crop-nearest12x-IDENTITY-AUX.png'; crop.resize((240,336),Image.Resampling.NEAREST).save(aux)
  aa=np.array(Image.open(aux).convert('RGBA')); assert np.array_equal(aa,np.repeat(np.repeat(np.array(crop),12,axis=0),12,axis=1))
  auxproof=write(f'{token}/exact-identity-crop-nearest-aux-proof-v001.json',{'source':pin(c['source']),'crop_xyxy':box,'nearest_integer_scale':12,'output':pin(aux),'output_RGBA_exact_repeated_source_crop':True,'role':'Reference-only readability aid of the SAME Far187 source, not new identity/native/artwork/final game pixels.','newmedia_E_retained':False,'newmedia_viewed':False})
  refs.append({'file':pin(aux),'role':'REFERENCE 2: Exact same accepted Far187 20x28 RGBA crop, nearest12x readability aid only; no new identity/construction.','already_retained':True})
  prelude='REFERENCE ORDER: 1 = sole accepted current Ready Far187 appearance identity; 2 = exact same Far187 crop nearest12x readability aid; 3 = exact Dodge218 four original cells, motion/camera/overlay only; 4 = official four-slot guide, layout only.\n'
 refs.extend([{'file':pin(paired),'role':f'REFERENCE {len(refs)+1}: Exact Dodge218 source4 body RGBA concatenation; paired pose/camera/visible torso and shoulder orientation ONLY, not armor identity.','already_retained':True},
              {'file':pin(guide),'role':f'REFERENCE {len(refs)+2}: Official four-slot guide, count/spacing/maximum safe window ONLY; do not draw guide or body.','already_retained':True}])
 native_prompt=write(f'{token}/Root-native-fullprompt-v001.txt',prelude+'\n'+new+'\n\nCOMPONENT AUTHORITY FINAL:\n'+c['specific']+'\n')
 refsfile=write(f'{token}/Root-native-references-AFTER-E-v001.json',{'references_in_order':refs,'declaration_timing':'AFTER-E call template only. New motion/guide/aux must first be retained by Root with twoSHA0; no generation invoked by this worker.','currently_new_media_retained_E':False})
 adapter_audit=write(f'{token}/official-prepare-and-component-prompt-adapter-v001.json',{'official_prepare_argv':argv,'exit_code':result.returncode,'log':pin(log),'adapter_source_readonly':pin(adapter_src),'explicit_adapter_replacements':changes,'explicit_postprepare_fields':{'durations_ms':[100]*4,'chroma':q['chroma']},'camera':'Same shallow elevated three-quarter camera as Dodge218, no pure-profile demand.','component_only_authority_clarification':True,'sprite_gen_code_changed':False})
 output=HERE/f'process-batches/2026-10-18-LGT-Dodge4-{token}-native-v001/raw/{state}.png'
 rows.append({'component':c['runtime'],'state':state,'frames':4,'durations_ms':[100]*4,'official_prepared_run':run.as_posix(),'native_prompt':pin(native_prompt),'references_json':pin(refsfile),'official_prompt':pin(prompt),'official_request':pin(request),'official_guide':pin(guide),'official_prepare_audit':pin(adapter_audit),'identity':pin(c['source']),'maximum_window_px':window,'one_shared_row_scale':True,'component_min_used_pixels':c['min_used_pixels'],'min_used_authority':'Existing tiny Far187 physical component: explicit 256 proposal, not a sparse-effect waiver.' if c['runtime']=='ShoulderFar' else 'Standard512 component minimum, unchanged.','canonical_native_output_template':output.as_posix(),'native_source_id':None,'actual_raw':None,'actual_extraction_scale':None,'actual_source_A_body_B_delta':None,'actual_fit_acceptance':False})

handoff=write('Root-Dodge218-three-LGT-official-input-handoff-v001.json',{'schema':'Dodge218-current-LGT-three-official-component-row-input-v001','rows':rows,'identity_and_motion_authority':pin(identity_evidence),'source_motion_exact_proof':pin(proof),'source_retention_audit':pin(audit),'canonical_F_media':MEDIA.as_posix(),'official_prepare_exit_codes':[0,0,0],'output_count_proposed':12,'newmedia_viewed':False,'newmedia_E_retained':False,'generation_calls':0,'quota_changed':False,'TrialAllowed':False,'FinalAccepted':False,'next':'Root retain inputs at E twoSHA0, review references/prompts/guides, then execute built-in generation serial IDs. Do not write generated raw into the frozen official prepared run: use each new process-batch. Sourcefit/coverage after standard five-step extraction and E-retained actual review.'})
write('HANDOFF.md','''Dodge218 的四个原始 512 RGBA cell 已逐像素核对，拼接参考只提供闪避动作/镜头/可见灰布与肩部方向。每个当前棕皮 Ready 组件各自是唯一外观身份：Chest184、Near186、Far187；未使用 Hurt227/233、旧灰甲或其他整身作 Dodge 身份。

三个官方 sprite-gen prepare 均实际 exit0。原始 request/prompt 保留，显式适配为 single-component row；SG 源码未改。Chest128×100 是共同最大安全窗口，Near60×44、Far32×30；不要求逐相填满窗口，不逐帧缩放。Chest/Near 的512与小 Far 的明确256像素门保持。Far 的第二参考是同一187的 exact20×28裁片 nearest12x，四份 refs 的角色序号已统一。胸衣真正的领/腋孔使用绿背景负空间，禁止 opaque black backing。

native output 给新的固定 process-batch 路径，native序号仍null并由Root实际reserve回执记录；绝不往已冻结 prepared run 写原稿。预先 null 的raw/scale/A/B/fit不冒未来事实。400ms四相仅美术采样，不改原400ms/185world/无敌区间或输入逻辑。新媒体未View，先Root E保全后使用 AFTER-E refs。0AI调用、0quota改动、0Source/Content/tools/ledger/README修改。''')
freeze=write('official-three-input-freeze-v001.json',{'schema':'Dodge218-LGT-three-official-input-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'official_prepare_exit_codes':[0,0,0],'newmedia_View':False,'native_calls':0})
(MEDIA/'原件').mkdir(parents=True)
shutil.copytree(OUT,MEDIA/'原件/三组件标准输入完整包')
(MEDIA/'展示副本').mkdir()
shutil.copyfile(motion,MEDIA/'展示副本/Dodge218-exact4-PAIRED-MOTION-ONLY.png')
for c in components:
 row=next(r for r in rows if r['component']==c['runtime'])
 shutil.copyfile(row['official_guide']['path'],MEDIA/'展示副本'/f'{c["token"]}-official-four-slot-guide.png')
 if c['runtime']=='ShoulderFar':
  shutil.copyfile(OUT/c['token']/f'run-leather-{c["token"]}-Dodge4-v001/references/accepted-Far187-EXACT20x28-crop-nearest12x-IDENTITY-AUX.png',MEDIA/'展示副本/Far187-same-RGBA-nearest12x-identity-aux.png')
index={'date':'2026-10-18','topic':'钟盔Dodge218棕皮三层标准输入','version':'v001','status':'3officialprepare0; UNVIEWED new inputs pending Root E twoSHA; generation/fit/native not accepted','candidate_source':OUT.as_posix(),'handoff':pin(handoff),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'handoff':pin(handoff),'freeze':pin(freeze),'rows':[{k:r[k] for k in ['component','native_prompt','references_json','canonical_native_output_template']} for r in rows],'newmedia_View':False,'native_calls':0},ensure_ascii=False,indent=2))
