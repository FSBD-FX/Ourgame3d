from pathlib import Path
import hashlib, json, shutil, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('F:/Ourgame')
HERE = ROOT / 'source-assets/production/fairytale-guard-v001/art-preparation-v001'
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
PY = SG / '.venv/Scripts/python.exe'
assert Path(sys.executable).resolve() == PY.resolve()
OLD = HERE / 'armed-ready4-extraction-v001/run-ready209-shared-HD-v001'
READY = OLD / 'curated/frame-0.png'
ANCHOR = HERE / 'move6-stomp-W6-A2-R4-generation-ready-v001/accepted209-anchor-readcopy/references/anchors/right-anchor-x1.png'
OUT = HERE / 'move-leg-rig-seven-components-generation-ready-v001'
MEDIA = ROOT / '过程图稿与视频/2026-10-18_裂岩守卫Move真实分层七组件三组标准输入_v001'
assert not OUT.exists() and not MEDIA.exists()
OUT.mkdir()

def pin(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(rel, value):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return p

assert pin(READY)['sha256'] == '54df5fe718a98e1568513193dbde479aff6fd393d623755feb77813cacb4e804'
assert np.array_equal(np.array(Image.open(READY).convert('RGBA').crop(Image.open(READY).getbbox())), np.array(Image.open(ANCHOR)))
IDENTITY = OUT / 'references/accepted-ArmedReady209-curated-frame0.png'
IDENTITY.parent.mkdir()
shutil.copyfile(READY, IDENTITY)

COMMON = '''The attached accepted ArmedReady209 frame0 is the ONLY Guard identity and camera authority. Preserve its broad squat stone helmet, tiny amber eye window, broad low-detail warm stone plates, sparse olive moss on the physical NEAR/foreground shoulder, coarse irregular ink, matte shading and shallow elevated three-quarter side view facing SCREEN RIGHT. Do not change the viewpoint to a pure90-degree profile. No206/207/standalone208, bad211 or failed221/223/226 image is attached. The other attached images are production layout/part-role guides ONLY, not character/style or measured anatomy references.
This is a STATIC RIG-SOURCE COMPONENT kit for a future genuinely authored hierarchical2D animation. It is NOT a whole-body Move row, not animation phases, not an exploded assembled character, and not proof of a working rig or planted feet. One complete requested component per invisible cell, left to right in the exact role order below. Do not add assembled examples, extra legs, labels, joint markers, outlines of missing parts or colored diagram strokes. No scene, shadow, dust, flying stone, motion arcs, gradient background, checkerboard or photoreal grain. Flat pure #FF00FF background only; no magenta material.
Every part must be complete and uncut, with generous magenta outside every edge and between cells. Keep at least48/512 of each cell clear on all sides; for long horizontal axe silhouette leave still more outer blank margin. Components must not cross adjacent slots. Their differing natural lengths/widths must be preserved: do NOT enlarge a short shin or shoe to fill its slot or force three parts to equal visual height. Keep one consistent illustration density within each3-part kit, including the hidden overlap-cap art. The whole identity's legs provide visual construction and apparent proportions only; hidden bones are not claimed recovered. All eventual source pivots, exact lengths and cross-sheet fixed art-unit conversions will be authored/measured AFTER actual component extraction and Root source review. Do not print numeric rulers, pivots or dimension labels in the image.
Limb overlap caps are intentional complete stone surfaces for rotation: broad simple opaque rounded/slab cap beyond each joint seam so adjacent parts can cover each other without holes. No tiny disconnected chips or separate floating knee discs. Keep the outer joint-cap outlines simple and hideable under the neighboring piece; avoid a thick double black outline seam where parts will overlap. These newly generated cap surfaces are new candidate art, not reconstructed hidden Ready209 pixels. No stretching, warping, local paint repair or per-pose part rescaling is being requested.'''

REST = '''Output EXACTLY ONE connected LEGLESS BODYREST WITH ITS FIXED HEAVYAXE. Include the complete crown/helmet, head and eye slit, torso, both shoulders, both arms, BOTH closed fists around the SAME continuous straight woodshaft, complete unchanged single stoneaxe head, all shaft, and complete stone buttcap. Preserve the acceptedReady209 low-held armed upperbody pose and same body-to-axe ratio. Moss NEAR foreground arm stays on BUTTward/lower grip; FAR arm stays on HEADward/higher grip. No regrip, opening fists, axe shortening, missing buttcap or detached weapon. The hands/arms/axe are baked into this one component, not a new hand or weapon rig.
Keep the lower torso and broad foreground pelvis/hem plate as an opaque cover above the future thigh attachments. End the body component deliberately at that pelvis hem. OMIT BOTH ENTIRE LEGS AND BOTH SHOES: no thigh stubs hanging down, knees, shins, boots, planted toes, old painted leg silhouettes, dark painted leg-shaped gaps or detached spare legs. This is a complete designed legless component, not a cropped fullbody screenshot or half-character cut off at an image edge. Expose two visually sensible underside overlap/socket regions under the LEFT foreground/moss-side pelvis and RIGHT recessed pelvis so the later author can place distinct Near and Far thigh pivots. Do not draw actual pivot dots or pretend these are measured anatomical hip centers. Empty space below the hem is pure magenta. No gore or damaged/amputated appearance.
Keep the entire fixed axe and bodyrest inside ONE invisible cell with generous blank surround. Do not attach a fullbody comparison, a ghost-body floor line, a second pose or spare component. The absent legs do not authorize shrinking the helmet/torso or enlarging the axe to fill space.'''

def limb_action(side):
    is_near = side == 'near'
    side_text = 'NEAR physical LEFT/foreground hip beneath the moss-side torso; foreground stone-plane lighting and thickness' if is_near else 'FAR physical RIGHT/recessed hip; its own recessed stone-plane shading and apparent perspective'
    return f'''Output EXACTLY THREE DIFFERENT complete static components belonging ONLY to the {side.upper()} leg attached to the {side_text}. Preserve the acceptedGuard leg materials, stone slabs, ink and construction. Do not attach a hip/torso, arm, axe, head, entire leg, second leg, other-side variant or fullbody example. This is not three poses of one leg and not three equal-size objects. It is the ordered thigh/shin/shoe kit.
CELL0 = {side.upper()} THIGH / upperleg ONLY: complete upper hip overlap cap through a complete lower knee overlap cap, neutral axis approximately straight DOWN. Include the upper-leg plate surfaces and simple rounded joint coverage; do not include the shin or boot. The future explicit hip-to-knee author axis will be fixed after source review.
CELL1 = {side.upper()} SHIN / lowerleg ONLY: complete upper knee overlap cap through complete lower ankle overlap cap, neutral axis approximately straight DOWN. Keep its natural short stocky lowerleg length relative to the thigh from the same visual identity and same kit art-unit density. Do not include thigh or shoe. Integrate necessary front stone/knee coverage into this one connected part, not a floating extra disc. The future knee-to-ankle axis is authored after source review.
CELL2 = {side.upper()} FOOT / stone shoe ONLY: complete upper ankle overlap cap, heel, full sole and toe; toe points SCREEN RIGHT, sole approximately horizontal. Show the same shallow elevated three-quarter shoe plane as the identity, not a front-on rectangular block, sole underside or new side camera. Preserve naturally broad heavy shoe size relative to this kit's thigh and shin. No shin rising from the ankle cap, no floor/shadow and no toe clipping. The future ankle/heel/toe contact markers are author declarations after actual source review.
Separate the three components by wide magenta gutters. Joint-cap stone coverage belongs to each component and remains connected to it; do not bridge components with lines. Near and Far will be independently generated, not mirrored source replacements. Do not force apparent Near/Far dimensions identical or enlarge the far component to erase its accepted perspective; final one fixed cross-kit conversion and assembled standing-equivalent height remain unmeasured and gated. The later rig must rotate these rigid parts without changing their source geometry or lengths.'''

groups = [('rest1', 'right_move_bodyrest', 1, REST, ['bodyrest_fixedaxe']),
          ('near3kit', 'right_move_near_kit', 3, limb_action('near'), ['near_thigh', 'near_shin', 'near_foot']),
          ('far3kit', 'right_move_far_kit', 3, limb_action('far'), ['far_thigh', 'far_shin', 'far_foot'])]
font_path = next(p for p in [Path('C:/Windows/Fonts/arial.ttf'), Path('C:/Windows/Fonts/segoeui.ttf')] if p.exists())
font = lambda size: ImageFont.truetype(str(font_path), size)

def role_guide(group, roles, run):
    w, h, cw = 720 * len(roles), 720, 720
    im = Image.new('RGB', (w, h), 'white'); d = ImageDraw.Draw(im)
    for i, role in enumerate(roles):
        x = i * cw; cx = x + 360
        d.rectangle([x + 2, 2, x + 717, 717], outline=(55, 55, 55), width=4)
        d.text((x + 35, 24), f'{i}: {role.upper()}', font=font(31), fill=(30, 30, 30))
        d.text((x + 35, 68), 'ROLE / COMPLETE PART ONLY', font=font(24), fill=(90, 90, 90))
        d.rectangle([x + 72, 114, x + 648, 620], outline=(130, 163, 215), width=3)
        grey=(155, 165, 177); dark=(85, 97, 114)
        if group == 'rest1':
            d.rectangle([cx - 100, 180, cx + 100, 400], outline=grey, width=10)
            d.rectangle([cx - 130, 395, cx + 110, 430], outline=dark, width=10)
            d.line([(cx - 152, 350), (cx + 240, 260)], fill=grey, width=12)
            d.rectangle([cx + 205, 190, cx + 270, 310], outline=grey, width=9)
            d.text((x + 95, 470), 'EMPTY BELOW PELVIS HEM', font=font(27), fill=(90, 90, 90))
            d.text((x + 150, 510), 'NO LEGS / NO SHOES', font=font(27), fill=(90, 90, 90))
        elif role.endswith('thigh') or role.endswith('shin'):
            # Generic roles only. These are NOT Guard shapes, source art or measured joints.
            top, bottom = (210, 470) if role.endswith('thigh') else (250, 440)
            d.rounded_rectangle([cx - 54, top, cx + 54, bottom], radius=42, outline=grey, width=9)
            d.ellipse([cx - 50, top - 18, cx + 50, top + 60], outline=dark, width=4)
            d.ellipse([cx - 50, bottom - 60, cx + 50, bottom + 18], outline=dark, width=4)
            d.text((x + 123, 530), 'COMPLETE OVERLAP CAPS', font=font(25), fill=dark)
        else:
            d.rounded_rectangle([cx - 95, 355, cx + 140, 440], radius=28, outline=grey, width=9)
            d.ellipse([cx - 40, 315, cx + 40, 385], outline=dark, width=4)
            d.text((x + 177, 490), 'HEEL - SOLE - TOE >', font=font(27), fill=dark)
        d.text((x + 28, 644), 'GENERIC DIAGRAM: no anatomy / size authority', font=font(23), fill=(110, 110, 110))
        d.text((x + 28, 680), 'Keep natural size; do not fill every box equally', font=font(23), fill=(110, 110, 110))
    p = run / f'references/layout-guides/right/{group}-PART-ROLE-PRODUCTION-GUIDE.png'
    im.save(p)
    return p

def adapt_prompt(text, n):
    replacements = [
        ('pure side profile view facing camera-right', 'same shallow elevated three-quarter side view as accepted ArmedReady209, facing screen-right; not pure90-degree profile'),
        ('Create a single horizontal sprite strip for the game character', 'Create a single horizontal STATIC COMPONENT SOURCE strip for the game character'),
        ('Do not simply copy the still reference pose. Generate distinct animation poses that create a readable cycle or action.', 'Copy the accepted identity construction only. Generate the expressly requested distinct static component ROLES, not animation poses or an assembled wholebody.'),
        ('Animation action:', 'Static component production action:'),
        ('This row owns motion only. Spend the variation budget on limb contacts, arm counter-swing, body height, torso lean, head bob, hair bounce, and loop continuity.', 'This production row owns the explicitly requested component decomposition only. Preserve identity; do not animate, bob, counterswing, change grip or invent a walk cycle.'),
        (f'Exactly {n} full-body frames, left to right, in one horizontal row.', f'Exactly {n} complete STATIC SOURCE COMPONENTS in the declared role order, left to right in one horizontal row; NO fullbody poses.'),
        ('each requested slot must contain exactly one complete full-body pose.', 'each requested slot must contain exactly one complete specified static component, including its joint overlap caps where requested.'),
        (f'Spread the {n} poses evenly across the whole image width. Do not leave any requested slot blank or create large empty gaps between poses.', f'Use all {n} invisible slots with one specified component each; preserve generous clear magenta gutters and natural different part sizes. Do not enlarge short components to fill a cell.'),
        ('Center one complete pose in each slot. No pose may cross into the neighboring slot.', 'Center one complete specified component in each slot. No part or overlap cap may cross into the neighboring slot.'),
        ('No character body part should be clipped by the frame slot.', 'No requested source component, cap, shoe or axe edge may be clipped by its slot.'),
        ('Avoid motion blur. Use clear pose changes readable at', 'Avoid motion blur. Use complete readable static component surfaces at'),
        ('Preserve the same silhouette, face, proportions, palette, material, and props across every frame.', 'Preserve accepted identity materials and natural relative part proportions; the three kit slots deliberately contain different parts, not one repeated silhouette.'),
    ]
    changes=[]
    for before, after in replacements:
        assert text.count(before) == 1, (before, text.count(before))
        text=text.replace(before, after)
        changes.append({'before':before,'after':after,'count':1})
    assert 'full-body frames' not in text and 'complete full-body pose' not in text and 'pure side profile view facing camera-right' not in text
    return text, changes

handoffs=[]
for group,state,n,action,roles in groups:
    gp=OUT/group;gp.mkdir()
    req={'cell':{'shape':'square','width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
         'states':{'right_idle':{'frames':4,'fps':4,'loop':True,'action':'CARRIED acceptedReady209existing4 exactraw only; do NOT generate or charge.'},
                   state:{'frames':n,'fps':1,'loop':False,'action':COMMON+'\n\n'+action}},
         'directions':{'set':['right'],'mirror':{'left':'right'}},
         'style':'AcceptedArmedReady209 sole visual identity/camera. Native static component source art for an isolated future2D Move leg-rig pilot. Broad low-detail stone planes and coarse ink; no redesign.',
         'motion_phase_guides':False,
         'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':True,'segmentation':'components','shared_row_scale':True}}
    inp=write(f'{group}/standard-request-input-v001.json',req)
    run=gp/f'run-guard-move-leg-rig-{group}-v001'
    argv=[str(PY),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','ENM-STN-003-Move-LegRig-PILOT-components-v001','--base-image',str(ANCHOR),'--chroma-key','#FF00FF','--request',str(inp)]
    r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
    log=write(f'{group}/logs/standard-prepare.log',r.stdout+r.stderr)
    prep={'argv':argv,'actual_exit_code':r.returncode,'log':pin(log)}
    write(f'{group}/logs/standard-prepare-command.json',prep)
    assert r.returncode==0
    request=run/'sprite-request.json'
    d=json.loads(request.read_text(encoding='utf-8'))
    assert set(d['states'])=={'right_idle',state} and d['states'][state]['frames']==n
    carry=run/'raw/right/idle.png';carry.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(OLD/'raw/right/idle.png',carry)
    leaf=state.removeprefix('right_')
    prompt=run/f'prompts/right/{leaf}.txt'
    original=prompt.read_text(encoding='utf-8')
    write(f'{group}/standard-original-before-static-component-prompt-adapter.txt',original)
    adapted,changes=adapt_prompt(original,n)
    prompt.write_text(adapted,encoding='utf-8',newline='\n')
    audit=write(f'{group}/static-component-native-prompt-adapter-audit-v001.json',{'reason':'Installed prepare prompt assumes animated fullbody and pureprofile; static source component scope requires explicit textual adapter. SG code/request/extractor unchanged; original prompt preserved.','replacements':changes,'new_prompt':pin(prompt)})
    identity=run/'references/accepted-ArmedReady209-curated-frame0.png';shutil.copyfile(READY,identity)
    guide=run/f'references/layout-guides/right/{leaf}.png'
    production=role_guide(group,roles,run)
    refs=write(f'{group}/native-helper-references-ready-AFTER-ROOT-E-v001.json',{'references_in_order':[
        {'file':pin(identity),'role':'ONLY canonical acceptedArmedReady209 body/fixedaxe/camera identity. No prior failedMove pixel source and no component generated here yet.','already_retained':True},
        {'file':pin(guide),'role':f'Standard{n}slot component-row count/spacing/padding only.','already_retained':True},
        {'file':pin(production),'role':f'NEW generic component-role guide for {roles}; no Guard pixels, anatomy, exact proportions, rig measurements or final style authority.','already_retained':True}],
        'declaration_precondition':'CALL-TIME TEMPLATE ONLY: newguides are not retained at preparation creation. Root must retain this entire F canonical batch under E and verify2SHA before using this already_retained:true helper input. Do not call or View before that gate.'})
    hand=write(f'{group}/Root-native-generation-ready-v001.json',{'schema':'Guard-Move-isolated-leg-rig-static-source-standard-input-v001','group':group,'state':state,'component_roles_left_to_right':roles,'native_requested_components':n,'runtime_animation_frames':0,'run_dir':run.as_posix(),'prompt':pin(prompt),'refs_json':pin(refs),'request':pin(request),'output':(run/f'raw/right/{leaf}.png').as_posix(),'prepare':prep,'prompt_adapter_audit':pin(audit),'identity':pin(READY),'existingReady4raw_carried_exact':pin(carry),'source_pivots_or_lengths_measured':False,'new_guides_viewed':False,'new_guides_E_retained':False,'worker_native_calls':0,'TrialAllowed':False,'Root_decision_gate':'Root E retains inputs then decides each serialnative generation. Generation output is intermediate; standard shared extraction/inspect/compose/curated + E + actualRootView before parts/markers/rig pilot.','counts':'This is a new isolated Move pilot. Not a NativeSourceId, not an AI wholebodyMove6 row and not a replacement of frozenfull57 state/frame counts or v1/v2 wholebody tests.'})
    handoffs.append({'group':group,'handoff':pin(hand),'prompt':pin(prompt),'refs_json':pin(refs),'output':(run/f'raw/right/{leaf}.png').as_posix(),'roles':roles,'prepare_exit_code':r.returncode})

part_defs=[('bodyrest_fixedaxe','rest1',0,['root','crown','near_hip_socket','far_hip_socket'],None),
           ('near_thigh','near3kit',0,['hip','knee'],'near_hip_socket'),('near_shin','near3kit',1,['knee','ankle'],'near_thigh.knee'),('near_foot','near3kit',2,['ankle','heel','toe'],'near_shin.ankle'),
           ('far_thigh','far3kit',0,['hip','knee'],'far_hip_socket'),('far_shin','far3kit',1,['knee','ankle'],'far_thigh.knee'),('far_foot','far3kit',2,['ankle','heel','toe'],'far_shin.ankle')]
parts=[]
for name,group,index,markers,parent in part_defs:
    parts.append({'part':name,'group':group,'source_role_index':index,'actual_curated_source_pin':None,'source_RGBA_canvas_px':None,'source_alpha_bbox':None,'author_marker_status':'UNMEASURED/UNAUTHORED, must remainnull until actualcomponent source/E/View and explicit2Dartist declaration; not recovered hidden anatomy.','artist_markers':{m:None for m in markers},'parent_socket':parent,'source_length_px':None,'fixed_art_unit_conversion':None,'overlap_seam_masks':None})
assert len(parts)==7 and sum(len(p['artist_markers']) for p in parts)==18
plan=write('seven-source-components-eighteen-author-markers-and-contact-pilot-contract-v001.json',{
    'schema':'Guard-Move-LegRig-isolated-seven-part-source-plan-v001','Root_adoption':'Root adopted only source preparation and isolated genuine2D skeletal/IK contact pilot, not runtime integration or generation by this worker.','canonical_identity':pin(READY),'parts':parts,
    'hierarchy':'Root; BodyRest fixedaxe; NearThigh→NearShin→NearFoot and FarThigh→FarShin→FarFoot, eachhip authored separately.',
    'draw_order_far_to_near':['far_foot','far_shin','far_thigh','near_foot','near_shin','near_thigh','bodyrest_fixedaxe'],
    'occlusion':'Far chain always recessed, Near chain always foreground evenwhen itsfoot trails. BodyRest pelvishem/arms/fixedaxe covers upperlegseams. Withinchain initial childfirst/parentlast order is a pilot proposal, actualrotatedjoint silhouettes/seams must be reviewed; addnoextras until needed.',
    'standing_registration':{'target_crown_to_ground_display_px':100.8,'reference_Ready209_standing_extent_px':415,'reference_artistic_root':[235,464],'reference_not_component_registration':True,'assembled_crown_to_sole_source_units':None,'common_fixed_display_scale':None,'near_fixed_thigh_length':None,'near_fixed_shin_length':None,'far_fixed_thigh_length':None,'far_fixed_shin_length':None,'Root_or_hips_from_hidden_bones':False,'rule':'Measure actualcomponent sourcecap/pivot pairs. KeepONEfixedconversion per generatedkit (sameconversion for all3), plusoneassembleddisplay mapping; no perframe/perpartstretch or normalization. Crosskitconversionmustbeexplicitandfrozenafteridentity/capwidth/standing-equivalent review, never derivefromwholeaxealphaheight. Source3kitrelativepartproportionsmustsurvive extraction.'},
    'standard_pipeline':'3actual prepareCLIs succeeded. Nativecomponentrows only atRootcall. Standardchroma/component extraction/sharedfit/inspect/compose/curate for staticparts. SGframes count staticroles, not a new playableMove timing. Bottomfit alignment only places source cells; limb bottoms are NOT actualfootfloors. SGcompose-layers has no rotation/IK; futuregenuineRig is separate.',
    'first_milestone':{'scope':'Isolated two opposite physical-leg contacts only before full6phase or Source integration.','contacts':[{'accepted_distance_phase_world':0,'front_contact':'NEAR physicalLEFTforegroundhip chain','back_push':'FAR physicalRIGHTrecessedhip chain'},{'accepted_distance_phase_world':64,'front_contact':'FAR physicalRIGHTrecessedhip chain','back_push':'NEAR physicalLEFTforegroundhip chain'}],'cycle_distance_world':128,'clock':'AccumulateactualacceptedMovementreceiptpath lengths, no speed*time, plannedinputs, drawcounts or forged movement. Blockedmovement noadvance.','fixed_geometry':'Explicitartistpivotpairs definefixedlength; rigrotation/2boneIK canmovejoints, neverscale/warp/stretchbones or actorXYtohitfoot. Actualreachrequired at100.8display; markfailure ifunreachable.','foot_support':'InterpolateactualMovementFrom→To at64worldboundaries; stanceanchorworldfixedthenactualGroundprojection, includingY. No footlockclaimbeforeisolatedlive/rigderivedproof.','proof_required':['BothdifferentNear/Farhiplegchains actuallyreachoppositefrontcontactwithoutmirroringwholebody.','SamepartRGBA/sourcepins andsameauthoredfixedlengthsinbothposes.','Root/bodyregistration,crown/soleheight,seamcoverage,axe/pelvisocclusionat100.8display.','128actualacceptedDistance drivesphase; blocked receiptsproducezeroadvance, facing/turn policyexplicit.'],'pilot_status':'NOTBUILT/NOVISUAL/NORUNTIMEACCEPTANCE'},
    'preserved_contracts':{'old_v1_v2_wholebody_contracts_and_tests':'Unchanged and preserved; pilotnewmode mustbeexplicit, nofakemultilayerwholebodyadmission.','full57_freeze_counts':'Unchanged; sevennewcomponentsarenot57stateframeentries.','NativeSourceId':'Noneassigned, no fabricated native source orwholebodyMove6 evidence.','non_Move_actions':'All existing wholebody attacks/wake/idle/stun/death sources retained.','independent_WU_to_Active_upperbody_join_risk_px':29.6927,'independent_Active_to_Recovery_downcompression_px':10.4586,'TrialAllowed':False},
    'generation_and_cost':'Threeproposedsourcebatches1+3+3, Rootserialnativeledger/callowner. Existingautomaticbudgetauthorization reportedbyRoot; nofreshspend/nativenetworkbyworker and no externalAPI. Theseareinitialrequests, not cost/callcount guarantee; retriesifneededrequireactualsourcefailure evidence andRootdecision.',
    'worker_actions':{'actualSource_Content_tools_ledger_UE_modifications':0,'native_API_calls':0,'final_character_pixels_drawn':0,'generated_components':0,'rig_implemented':False,'new_guides_viewed':False}})
handoff=write('Root-three-batch-generation-ready-handoff-v001.json',{'schema':'Guard-Move-LegRig-three-standard-static-component-batches-handoff-v001','groups':handoffs,'component_and_pilot_contract':pin(plan),'canonical_F_media':MEDIA.as_posix(),'identity':pin(READY),'native_call_order_proposal':['rest1','near3kit','far3kit'],'call_order_not_automatic':'RootmayserialreserveallafterE, but reviewactualRestidentity/hem/axe before expandingifthatfirstsourcefails. Near/FarkitsmustnotattachunacceptedRestascompetingidentity; Ready209soleidentity.', 'new_guides_E_retained':False,'new_guides_viewed':False,'TrialAllowed':False,'native_calls':0})
write('HANDOFF.md','''# Move LegRig：三组静态组件标准输入\n\n仅准备候选：Rest-with-fixed-axe legless1、Near3kit、Far3kit，Ready209为唯一身份。三个标准prepare均实际退出0；完整原prompt保留，逐项文本适配消除纯侧视/整身动画的自动语句冲突。没有改SG、Source、Content、Root工具、ledger或UE，没有native/API调用。\n\n共7个拟生成组件和18个待作者定义的标记。实际部件pin、关节坐标、长度、接缝mask、统一装配尺度均为null；仅100.8px显示目标和Ready209已测415px冠底作为参考，不能拿斧alpha高度或逐件拉伸配准。三件kit必须共享提取尺度，跨kit固定转换只能在实际留档提取审图后显式记录。\n\n新generic role guides只说明部件和空白；没有绘制最终Guard或恢复隐藏骨骼。canonicalF原件/展示副本/索引已备，必须RootE两SHA保全后才View或用AFTER-ROOT-E refs调用。先两相反触地、固定长度、真实acceptedDistance128的隔离pilot；未通过不扩六相。七组件不计入既有full57冻结帧数，不冒NativeSourceId，不更改旧一层整身契约/测试。攻击衔接29.7px问题独立保留，TrialAllowed=false。\n''')
write('preparation-freeze-v001.json',{'schema':'Guard-Move-LegRig-three-batch-input-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'standard_prepare_actual_exit_codes':[x['prepare_exit_code'] for x in handoffs],'new_guides_viewed':False,'native_calls':0})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/标准输入包');(MEDIA/'展示副本').mkdir()
for g in handoffs:
    gp=OUT/g['group'];run=next(gp.glob('run-*'))
    for p in sorted((run/'references/layout-guides/right').glob('*.png')):
        shutil.copyfile(p,MEDIA/'展示副本'/f"{g['group']}-{p.name}")
index={'date':'2026-10-18','topic':'裂岩守卫Move真实分层七组件三组标准输入','version':'v001','status':'ONLY3standardinputs/newgenericguides-unviewed-awaitRootE/call-decision-gate;0actualcomponents/0rig/Trialfalse','source':OUT.as_posix(),'handoff':pin(handoff),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'handoff':pin(handoff),'groups':handoffs,'component_plan':pin(plan),'files_in_canonical':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes_in_canonical':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file())},ensure_ascii=False,indent=2))
