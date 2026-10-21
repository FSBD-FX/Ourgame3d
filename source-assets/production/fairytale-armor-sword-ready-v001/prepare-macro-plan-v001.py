"""Prepare only: macro armor requests and original envelope diagrams; no art generation/masks/UE."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
READY=Path('F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v001')
PALETTE=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front/frame-0.png')
MARKERS=Path('F:/Ourgame/source-assets/production/fairytale-sword-v001/ready-measurement-v001/ready-marker-proposal-v001.json')
CONTRACT=Path('F:/Ourgame/docs/production/first-batch-v2/fairytale-armor-component-contract-v003.md')
specs=[('Chest','armor_lgt_chest_sword_ready',[104,80]),('NearShoulder','armor_lgt_shoulder_near_sword_ready',[64,48]),('FarShoulder','armor_lgt_shoulder_far_sword_ready',[40,44])]
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,x):
 p=R/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
rows=[]
for label,state,fit in specs:
 run=R/f'run-{label.lower()}-ready-v001';assert not run.exists()
 margins=[(512-fit[0])//2,(512-fit[1])//2]
 action=f'Four genuinely distinct isolated connected ARM-LGT-001 {label} components, matching actual native155 SwordReady0..3; no body pixels, weapon or other armor component.'
 seed={'states':{state:{'frames':4,'fps':6,'loop':True,'action':action}},'cell':{'width':512,'height':512,'safe_margin_x':margins[0],'safe_margin_y':margins[1]},
  'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
 sp=write(f'requests/{label.lower()}-numeric-input-v001.json',seed)
 argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',f'fairytale-lgt-sword-ready-{label.lower()}-v001','--base-image',str(CANON),'--description',action,
  '--style','Canonical131 grotesque hand-inked construction; matte cool-gray broad iron planes and charcoal rim from147 palette. Component-only light armor; do not alter body/helmet scale.','--cell-size','512','--chroma-key','#00FF00','--request',str(sp)]
 result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write(f'logs/prepare-{label.lower()}-v001.log',result.stdout+result.stderr);assert result.returncode==0
 qp=run/'sprite-request.json';q=json.loads(qp.read_text(encoding='utf-8'));write(f'requests/{label.lower()}-standard-before-explicit-fields.json',q)
 q['cell']={'shape':'square','width':512,'height':512,'safe_margin_x':margins[0],'safe_margin_y':margins[1]}
 q['fit'].update(seed['fit']);q['states'][state]['durations_ms']=[167]*4;q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
 qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 assert (run/'base-source.png').read_bytes()==CANON.read_bytes()
 # This diagram is only a local extraction-envelope grid: no invented armor/body/anchor art.
 im=Image.new('RGB',(2048,512),'#eeeeee');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512"><rect width="100%" height="100%" fill="#eeeeee"/>']
 for i in range(4):
  x=i*512;d.rectangle((x+8,8,x+504,504),outline='#555555',width=1)
  d.rectangle((x+margins[0],margins[1],x+512-margins[0],512-margins[1]),outline='#111111',width=2)
  texts=[f'{label} / native155 Ready frame{i}',f'LOCAL component envelope {fit[0]} x {fit[1]} px', 'NO body socket placement or finished shape shown', 'Target mount A = NULL; measure actual body seam first']
  for yy,t in zip([24,46,458,480],texts):d.text((x+12,yy),t,fill='#111111',font=font)
  svg.append(f'<rect x="{x+margins[0]}" y="{margins[1]}" width="{fit[0]}" height="{fit[1]}" fill="none" stroke="#111111" stroke-width="2"/>')
  for yy,t in zip([38,60,472,494],texts):svg.append(f'<text x="{x+12}" y="{yy}" font-size="13">{t}</text>')
 svg.append('</svg>');gp=R/f'guides/{label.lower()}-extraction-envelope-v001.png';gp.parent.mkdir(parents=True,exist_ok=True);im.save(gp)
 write(f'guides/{label.lower()}-extraction-envelope-v001.svg','\n'.join(svg)+'\n')
 prompt=f'''DRAFT ONLY — not ready for generation until source-owned near-arm partition and visible body mounts are measured/reviewed. Prepare exactly four distinct isolated connected {label} components for ARM-LGT-001 SwordReady, pose0..3 matching native155. Four times167ms, no cloned copies, no near/far mirrors.

Reference roles (at most five): canonical131 is sole character identity/construction; actual155 four-pose contact is the only Ready pose/occlusion authority; actual147 isolated plate supplies only cool-gray iron palette/line quality, never its old body placement; the new envelope diagram is local extraction-size planning only, not a final armor shape or body socket; standard4slot layout gives count only. No failed156, old human body or old masks.

Design direction: broad readable cool-gray iron planes, charcoal outside contour, short connected functional straps if needed, minimal large construction shapes. The light set exposes dark cloth and uses short caps/partial breast protection; avoid heavy barrel torso, massive pauldrons, tiny rivet ornament or new helmet. {label} has planned local fit-window{fit[0]}x{fit[1]} on512 source; this is a design envelope, not measured attachment acceptance. One common scale for all four components, no per-frame fit/warp. Source body remains max72px in1280x720 (fixed canvas88.6153846154). Native right-facing3/4 near=image-left larger/front, far=image-right compressed/deeper. Near and far are independently authored actual perspectives.

Only the requested isolated armor component is rendered in a future row, with flat #00FF00 background and opaque clean inked edges. No helmet, neck, cloth/body/arms/hands/legs/boots, blade, eye glow, shadow, FX, labels, axes or other component. Generated attachment feature A must be the same visible physical seam/rivet feature defined on the source/body plan first; at this draft stage target mounts are NULL and must not be guessed from bbox centers or hidden joints.

Future body layering must replay the existing155 source arm/hand pixels from an exact binary ownership partition, so this armor cannot cover the across-chest near arm or turn its fist into new anatomy. That mask is not yet made. Do not bake a whole body into the armor, duplicate wholebody into layers, cut/copy old147/149/150 into four Ready pieces, or claim correct occlusion from a bounding rectangle. Final anatomy, helmet/hand clearance, native4pose fit and72px mirrored runtime contribution remain open.
'''
 pp=write(f'prompts/{label.lower()}-draft-v001.txt',prompt)
 refs=[('sole_identity131',CANON),('actual155_four_ready_poses',READY/'qa/sword_ready_idle-contact.png'),('147_iron_palette_only_not_geometry',PALETTE),('original_local_envelope_only_not_body_mount',gp),('standard_count_layout_only',run/f'references/layout-guides/{state}.png')]
 rows.append({'component':label,'state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),'prompt':desc(pp),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],
  'frame_count':4,'durations_ms':[167]*4,'fit_window_px':fit,'approx_display_envelope_px':[v*72/416 for v in fit],
  'target_mounts':[{'frame':i,'A':None,'meaning':'Authoring socket requires an actual visible body seam/contour measurement; no hidden joint precision implied.'} for i in range(4)],
  'generation_ready':False,'blockers':['Actual155 visible collar/waist/shoulder landmarks not measured','Exact source-owned near-arm/near-hand partition not produced/reviewed'],
  'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode,'new_guides_viewed':False})
landmarks=[]
for i in range(4):
 landmarks.append({'frame':i,'source':desc(READY/f'curated/frame-{i}.png'),'collar_visible_edge_px':None,'waist_upper_seam_px':None,'near_shoulder_visible_mount_px':None,'far_shoulder_visible_mount_px':None,
  'near_arm_cloth_boundary':None,'near_cuff_hand_boundary':None,
  'inspection_ROIs_only':{'collar':[205,222,309,260],'waist':[217,300,303,327],'near_shoulder':[170,232,228,270],'far_shoulder':[285,238,330,287],'near_arm_hand':[160,232,285,315]},
  'ROI_status':'Inspection bounds only, never a semantic mask/accepted collision region/precise joint.',
  'source_root_display_px':[256,464],'display_root_is_exact_two_foot_center':False})
plan={'schema':'fairytale-lgt-sword-ready-macro-preparation-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'armor_id':'ARM-LGT-001','rows':rows,'source_landmark_requirements':landmarks,
 'existing_ready_hand_estimates':desc(MARKERS),'previous_semantic_contract':desc(CONTRACT),
 'near_arm_partition_plan':{'method':'Manual binary pixel ownership from each actual155RGBA. No repaint/warp/recolor, no old mask. NearHand subset of NearArm; split BodyRest / NearArmWithoutHand / NearHand. Every source coordinate assigned once, originalRGBA copied unchanged.','required_proofs':['Source SHA and ownership mask SHA','Binary disjoint ownership and coverage','Reconstruct source by selecting its owned originalRGBA at every coordinate and compare all bytes','Rendered premultipliedRGBA/alpha reconstruction and real armor/weapon stack separately reviewed','Uncertain shoulder/cuff ink/AA edges recorded; no hidden anatomy invented'],
  'partition_produced':False,'semantic_mask_accepted':False,'candidate_layer_order':['body_rest','far_shoulder_visible_geometry','chest','near_arm_without_hand','near_shoulder','weapon','near_hand'],
  'layer_order_is_accepted':False,'risks':['Far cap needs truly visible pixels; wholebody must not hide it then call it rendered','Near cap must not be erased by replaying an opaque full sleeve after it','Across-chest forearm must cover plate naturally without copying chest/helmet pixels into arm mask','NearHand remains an approximate/uncertain anatomy candidate until actual source ownership and thumb review']},
 'future_armor_boundaries':{'ARM-LGT-001':'Partial rigid chest, exposed cloth and short caps; this draft only Ready4.','ARM-MED-001':'Own coverage/overlap silhouette and every state; not light recolor.','ARM-HVY-001':'Own bulk, articulation/weight and every state; never enlarge whole hero to fake armor mass.','ARM-ROB-001':'Own fabric drape/hem movement and every state, keeping actual foot clearance; not plate recolor.'},
 'generated':False,'ue_or_import_called':False,'new_guides_viewed':False,'formal_complete_units':0}
hp=write('macro-ready-preparation-v001.json',plan)
write('plan-v001.md','''# ARM-LGT-001持剑待机大轮廓准备

仅新源目录；未生成、未提取新甲、未创建mask、未导入/修改Source。四帧155Ready是唯一现姿势，131是唯一身份。旧147/149/150仅供设计/颜色经验，不能直贴其空手挂点或复制成Ready四帧。

最小顺序：先测155四帧可见领口、腰上沿、近/远肩接缝；先建立真实近臂/近手二元像素ownership并证明原RGBA逐字节重构；再分别做胸4/近肩4/远肩4。标准prepare已完成三个空run，均4×167ms、one sharedscale；没有raw。窗口胸104×80、近肩64×48、远肩40×44只是设计上限，尚非测量fit。所有source mount A和不确定接缝留null，不能给隐藏关节编精确坐标。

现跨胸前臂会遮胸甲。先用实际源像素分区再决定层序，不能旧mask、整身复制回放或bbox假语义区；近肩需在近臂后叠而手在剑后回放，远肩须真实有可见贡献且不盖盔/颈/手。拟层序尚未验收，必须用真实新组件逐帧验证。

这套只做轻甲局部胸/短caps的大体块，72px角色不放大、不靠细铆钉装饰。中甲、重甲、法袍分别保留不同覆盖、体积和动作需求，均未制作。新窗口guide只画原始技术框，不是盔甲美术或身体socket图；尚未E保全/查看。草稿prompts明确generation_ready=false。root先审挂接/分区需求，再决定下一次native输入；本稿不预留或调用生成。
''')
files=sorted(p for p in R.rglob('*') if p.is_file())
fp=write('preparation-freeze-v001.json',{'schema':'fairytale-lgt-sword-ready-plan-freeze-v1','file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],'status':'Draft standard requests only; mounts and source ownership unresolved; not generation-ready.','new_guides_viewed':False,'generated':False})
print(json.dumps({'plan':desc(hp),'freeze':desc(fp),'standard_prepare_runs':3,'generation_ready':False},ensure_ascii=False))
