"""Prepare requests and ORIGINAL technical guides only; no art generation/edit/extract."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
if (ROOT / 'shoulder-component-contract-v002.json').exists():
    raise RuntimeError('Prepared inputs already exist; never overwrite frozen inputs')
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002')
OLD = Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001')
MAT = Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/readability-reference-v001/raw/146-compact-armor-readability-reference-v001.png')
IDENTITY = CANON / 'curated/frame-0.png'
POSES = CANON / 'qa/idle-contact.png'
CHEST = OLD / 'registration-proposed-v001/composite-preview/frame-0.png'
BODY = [CANON / f'curated/frame-{i}.png' for i in range(4)]
NEAR = [((215,248),(202,271)),((215,246),(202,270)),((215,249),(202,272)),((215,248),(202,271))]
FAR = [((296,255),(302,275)),((296,253),(302,273)),((296,256),(302,276)),((296,255),(302,275))]

def desc(p):
    b = p.read_bytes()
    return {'path':p.as_posix(), 'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest()}

def write(p, data):
    p = ROOT / p
    if p.exists(): raise RuntimeError('Never overwrite: ' + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

before = [desc(p) for p in BODY + [POSES,MAT,CHEST,OLD/'component-contract-v001.json',OLD/'extraction-v001/extracted-and-proposed-freeze-v001.json']]
time_now = datetime.datetime.now().astimezone().isoformat()
style = 'Canonical131 cartoon grotesque dark-fairytale ink; compact handmade146 pauldrons, matte desaturated neutral-grey147 chest palette with broad values and dark rim, no green/teal material.'
rows = []
samples = []
for side, targets, fit in [('near',NEAR,(56,44)),('far',FAR,(32,40))]:
    state = f'armor_shoulder_{side}_idle'
    run = ROOT / f'run-shoulder-{side}-idle-v001'
    action = (f'Exactly four distinct isolated connected {side}-side shoulder armor caps in canonical131 idle pose order0,1,2,3. '
              'Armor-only rigid small pauldron; one physically attached mounting rivet per cap. No body, shirt, arm, hand, chest, detached strap or opposite shoulder. '
              'Near/image-left is the wider front deltoid; far/image-right is the compressed deeper shoulder. Do not flip a near cap to make a far cap.')
    seed = {'states':{state:{'frames':4,'fps':6,'loop':True,'action':action}},
            'cell':{'width':512,'height':512,'safe_margin_x':(512-fit[0])//2,'safe_margin_y':(512-fit[1])//2},
            'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom',
                   'ground_frames':False,'segmentation':'components','shared_row_scale':True}}
    seed_path = f'requests/{side}-numeric-input-v001.json'
    write(seed_path,seed)
    cmd = [sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),
           '--out-dir',str(run),'--character-id',f'fairytale-armor-trial-a-shoulder-{side}-idle-v001',
           '--base-image',str(IDENTITY),'--description',action,'--style',style,'--cell-size','512',
           '--chroma-key','#00FF00','--request',str(ROOT/seed_path)]
    result = subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    write(f'logs/prepare-{side}-v001.log',result.stdout+result.stderr)
    if result.returncode: raise RuntimeError(f'{side} prepare failed: {result.returncode}')
    request_path = run/'sprite-request.json'
    request = json.loads(request_path.read_text(encoding='utf-8'))
    write(f'requests/{side}-standard-prepare-output-before-explicit-fields.json',request)
    request['states'][state]['durations_ms'] = [167]*4
    request['fit'].update(seed['fit'])
    request['chroma'] = {'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
    request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if request['cell']['safe_margin_x']!=(512-fit[0])//2 or request['cell']['safe_margin_y']!=(512-fit[1])//2:
        raise RuntimeError('Standard prepare discarded the exact component fit window')
    if (run/'base-source.png').read_bytes()!=IDENTITY.read_bytes(): raise RuntimeError('Identity copy mismatch')

    # NEW vector blocks only. Existing art is never read into the diagram canvas.
    im = Image.new('RGB',(2048,512),'#f4f6f8'); d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512" viewBox="0 0 2048 512"><rect width="2048" height="512" fill="#f4f6f8"/>']
    outline = [(-25,11),(-22,-2),(-10,-12),(6,-11),(16,-3),(20,10),(8,21),(-13,23),(-30,16)] if side=='near' else [(-9,-9),(1,-12),(12,-5),(18,8),(16,18),(6,20),(-5,15),(-9,5)]
    local_lip=(-13,23) if side=='near' else (6,20)
    for i,(mount,lip) in enumerate(targets):
        ox=i*512
        def tx(p): return (ox+256+p[0]*5,235+p[1]*5)
        d.rectangle((ox+10,10,ox+502,502),outline='#94a3b8',width=2)
        d.text((ox+24,24),f'{side.upper()} shoulder / idle {i} / 167ms',fill='#172554',font=font)
        d.text((ox+24,52),f'BODY mount {mount}; lip support {lip}',fill='#172554',font=font)
        # A short original shoulder/upper-arm axis gives depth, not a mannequin render.
        arm_end=(-31,47) if side=='near' else (18,45)
        d.line([tx((0,0)),tx(arm_end)],fill='#c9ced5',width=35 if side=='near' else 22)
        ps=[tx(p) for p in outline]
        d.polygon(ps,fill='#93b8d1' if side=='near' else '#cab2d4',outline='#334155',width=4)
        a,b=tx((0,0)),tx(local_lip)
        for p,color in [(a,'#dc2626'),(b,'#16803c')]:d.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill=color)
        d.text((ox+24,445),'Red = rivet mount; green = lower rim center',fill='#172554',font=font)
        d.text((ox+24,472),'TECHNICAL COLORS/AXIS/LABELS MUST NOT APPEAR',fill='#172554',font=font)
        svg += [f'<rect x="{ox+10}" y="10" width="492" height="492" fill="none" stroke="#94a3b8"/>',
                f'<text x="{ox+24}" y="40" font-size="17">{side.upper()} shoulder / idle {i} / 167ms</text>',
                f'<text x="{ox+24}" y="68" font-size="16">BODY mount {mount}; lip support {lip}</text>',
                f'<line x1="{a[0]}" y1="{a[1]}" x2="{tx(arm_end)[0]}" y2="{tx(arm_end)[1]}" stroke="#c9ced5" stroke-width="{35 if side=="near" else 22}"/>',
                '<polygon points="'+' '.join(f'{x},{y}' for x,y in ps)+'" fill="'+('#93b8d1' if side=='near' else '#cab2d4')+'" stroke="#334155" stroke-width="4"/>',
                f'<circle cx="{a[0]}" cy="{a[1]}" r="5" fill="#dc2626"/><circle cx="{b[0]}" cy="{b[1]}" r="5" fill="#16803c"/>']
        body_image=Image.open(BODY[i]).convert('RGBA')
        samples.append({'side':side,'frame':i,'mount_px':mount,'mount_rgba':body_image.getpixel(mount),
                        'lip_support_px':lip,'lip_support_rgba':body_image.getpixel(lip),
                        'basis':'Reviewer selected garment design mounts after actual canonical PNG review; read-only opaque pixel sampling, not bone tracking.',
                        'confidence':'medium; approximately +/-3px garment/ink contour ambiguity; far shoulder partly obscured by helmet/torso.' if side=='far' else 'medium; approximately +/-2-3px garment/ink contour ambiguity.'})
        if body_image.getpixel(mount)[3]<128 or body_image.getpixel(lip)[3]<128:raise RuntimeError('Target is not on opaque body art')
    svg.append('</svg>')
    guide=f'guides/shoulder-{side}-mount-and-shape-v001'
    write(guide+'.svg','\n'.join(svg)+'\n')
    im.save(ROOT/(guide+'.png'))
    ownership=f'''REFERENCE OWNERSHIP (strict):
1. canonical131 idle0 is the ONLY character/style identity. Never use129,135/136/139,146body or147body as identity.
2. canonical131 four-pose contact is POSE ONLY: preserve idle order0,1,2,3 and right-facing three-quarter depth.
3.146 is only compact rounded pauldron CONSTRUCTION. Ignore its body, helmet, proportional scale and warm armor palette.
4.147 composite0 is ONLY actual chest grey palette/ink and occupied torso footprint. Do not output its body or chest.
5.standard row guide owns count4 and placement; the new original {side} shoulder guide owns mount/lip geometry, not final colors.
All reference bodies/axes/marks are invisible scaffolding, never output pixels.
'''
    side_text=('The NEAR shoulder is image-LEFT in this native right-facing view: a wider forward deltoid cap, curved dome and slightly flared lower rim. '
               'Its lower-rim center sits down-left of its mounting rivet, following the outward-downward near upper arm. '
               'Do not turn it into the far skinny cap or a horizontal chest beam.') if side=='near' else (
               'The FAR shoulder is image-RIGHT and BEHIND the torso/helmet: a narrow foreshortened cap, not a flipped duplicate of the near cap. '
               'Its visible top rim begins below the helmet edge; lower-rim center sits down-right of its inner mounting rivet. '
               'Show only the naturally visible pauldron silhouette for each pose, not an invented fully exposed opposite arm.')
    prompt=f'''Create ONE production component-row strip with exactly FOUR separated connected {side.upper()} SHOULDER-ARMOR CAPS, left to right for the existing canonical131 idle poses0,1,2,3. One cap per pose; this is NOT four heroes, NOT shoulder pairs in a slot, and NOT an assembled outfit.

{ownership}
GEOMETRY: {side_text} The plate is the same compact handmade armor in every pose, rigid metal with a broad matte mid-grey face, restrained pale grey highlight and strong charcoal rim. Use the actual147 chest palette; keep metal more desaturated/cooler than the warm tan helmet. Preserve146's round, slightly crooked cartoony construction, with a short flared lip rather than spikes or ornate noise. One small simple round mounting rivet belongs INSIDE/CONNECTED to each plate; it is an actual armor feature, not a detached counting dot. No disconnected straps or hardware. Follow each matching131 shoulder breathing pose with subtle real changes in perspective/attachment angle, never clone one cap four times or locally mirror copies.

MOUNTING: the red guide point means the center of that connected mounting rivet; green means the actual LOWER-RIM center along the upper-arm direction. These are distinct named physical features. Keep their direction and separation consistent with the matching body pose; no foot roots, collar/U-notch substitution or guessed universal root. The final component size limit is{fit[0]}x{fit[1]} on the existing512 body canvas, not a full-body416px fit. The guide is illustrative geometry; all diagram colors, dots, text, axis and border must vanish. Actual generated landmarks will be measured after extraction; do not draw extra anchor markers.

OUTPUT ONLY FOUR {side.upper()} CAPS: no opposite-side shoulder, head, helmet, neck, chestplate, body, shirt, upper-arm tissue/sleeve, forearm, elbow guard, glove, hand, belt, leg, boots, weapon, shield, cape or mannequin. Each cap is one connected armor object. Four separate objects mean FOUR total connected components, not eight pieces, not fake joining bridges and not a whole-body silhouette hidden under plate paint.

BACKGROUND/LAYOUT: flat fully opaque GREEN #00FF00 background, opaque plate interiors, clean cartoon ink edges. Exactly four objects on one horizontal row with generous green gaps and outer borders. Keep one common source drawing scale for all four caps, large enough for clean extraction; native component pipeline will deterministically reduce the row with ONE shared ratio, never individual normalization. No scenery/floor/shadow/glow/halo, checkerboard, UI, numbers, labels or alternate camera views. Original timing is4x167ms; do not draw it.

BOUNDARY: only this {side}4-idle row. Other shoulder side, bracers/shins, same131 near-arm/near-hand partition, walk, weapon occlusion and full actions are separate real work. No baked character pixels to make this row appear complete.
'''
    prompt_path=f'prompts/{side}-four-idle-shoulder-v001.txt'
    write(prompt_path,prompt)
    refs=[{'role':'sole_identity','file':desc(IDENTITY)}, {'role':'four_idle_pose_order_only','file':desc(POSES)},
          {'role':'pauldron_construction_only_not_body_or_palette','file':desc(MAT)},
          {'role':'147_actual_chest_palette_and_torso_footprint_only','file':desc(CHEST)},
          {'role':'standard_component_count_layout','file':desc(run/f'references/layout-guides/{state}.png')},
          {'role':'original_technical_mount_and_depth_only','file':desc(ROOT/(guide+'.png'))}]
    rows.append({'side':side,'state':state,'run_dir':run.as_posix(),'prompt':desc(ROOT/prompt_path),
                 'reference_images_in_order':refs,'expected_native_components':4,'frame_count':4,'durations_ms':[167]*4,
                 'native_facing':1,'component_fit_window_px':fit,'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),
                 'native_call_number':None,'actual_raw_sha256':None,'actual_generated_mounts':None,
                 'standard_prepare_command':cmd,'standard_prepare_exit_code':result.returncode,
                 'request_augmentation':'Only explicit durations_ms167, shared/component fitting and RGB chroma fields after standard prepare; before output preserved.'})

contract={'schema':'fairytale-armor-independent-limbs-preparation-v2','created_local':time_now,'status':'prepared_not_generated',
          'scope':'Near4 and far4 shoulder caps only; two native calls by root, no extracted output yet.',
          'trial_id':'trial_compact_plate_a','equipment_id':None,'body_canvas_px':[512,512],
          'body_display_canvas':72*512/416,'body_display_pivot_px':[256,464],'pivot_is_certified_feet_root':False,
          'sole_identity':desc(IDENTITY),'pose_authority':[desc(p) for p in BODY],'body_targets':samples,'rows':rows,
          'shared_scale':'Per near/far row min(fitW/maxRawW,fitH/maxRawH,1); one scalar for all4 in that row, no per-frame fit. Near/far size windows are intentional perspective-specific contracts, not a claim of one scalar across8.',
          'registration':'Measure actual connected rivet center A and lower-rim center B in extracted RGBA, then integer translation aligns A to the body mount; B is an independent residual. Preserve exact cropped RGBA. No per-frame resize/rotate/warp/repaint or whole-bbox/foot-root substitution.',
          'attachment_tolerance_design_px':3,'tolerance_is_not_measured_result':True,
          'generated_raw_and_landmarks_exist':False,'sourceart_pixels_changed':False,'near_far_mirror_copy_allowed':False,
          'runtime_flip':'Generate both genuine depth roles in nativeFacing+1. For displayFacing-1, mirror body and entire assembled components ONCE around the same display pivot; never swap anatomical side labels.',
          'occlusion':'Current unarmed shoulder fit preview may overlay whole131 under the helmet only where the candidate alpha actually avoids helmet/neck. Future weapons require actual canonical131 body_far/near_arm/near_hand binary partition with exact RGBA reconstruction; old masks/body_near contract not reused.',
          'back_bracers_shins':'not_produced','walk_actions':'not_produced','runtime_imported':False,'motion_accepted':False,'formal_complete_units':0}
write('shoulder-component-contract-v002.json',contract)
write('native-shoulders-input-plan-v001.json',{'schema':'native-shoulder-two-row-handoff-v1','created_local':time_now,
      'minimum_reliable_calls':2,'call_order':['near4 first (root may use148)','far4 second (root selects then-current unused request number)'],
      'reason':'Four isolated same-side caps per call matches component-row4. A disconnected near+far pair has8 total components and cannot be labelled4; a fake bridge is not real armor. One8-row call would mix role/pose indexing and makes matching less reliable.',
      'rows':rows,'generation_author':'root only','generation_executed':False,'retention_before_view':'root E preservation required before viewing NEW guides or generated media'})
write('README.md','''# Independent shoulder components v001 preparation

Two separate native requests: near4, then far4. See shoulder-component-contract-v002.json and native-shoulders-input-plan-v001.json for exact paths, source roles and commands. All raw/output hashes are null until actual root generation. The standard tool generic prompts are retained as provenance; root should use the authored prompts/{near,far}-four-idle-shoulder-v001.txt, which prohibit full bodies and own the strict reference roles.

Only NEW original technical diagrams were drawn on blank canvases. Existing raster references were read for metadata/pixel samples or byte-copied by standard prepare; none were painted, cut into armor, composed or rescaled. No guide/PNG was viewed before root E retention. No extraction, native generation, Unreal, import, ledger or Source mutation.

Real canonical131 garment attachment points are reviewer-selected design mounts with2-3px uncertainty, not measured bones or certified foot roots. Near56x44/far32x40 are component size limits; later root measures real rivet/lower-rim landmarks without changing their definitions to pass. Actual alpha/overlap/72px/cycle must then be reviewed. Shoulder rows are not complete armor or any formal completed unit.
''')
after=[desc(Path(x['path'])) for x in before]
if before!=after:raise RuntimeError('Existing canonical/chest inputs changed during preparation')
write('preparation-execution-receipt-v001.json',{'schema':'shoulder-preparation-execution-v1','created_local':time_now,
      'interpreter':sys.executable,'interpreter_is_skill_own_venv':Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve(),
      'commands':[{'side':r['side'],'argv':r['standard_prepare_command'],'exit_code':r['standard_prepare_exit_code']} for r in rows],
      'old_source_files_before':before,'old_source_files_after_identical':before==after,
      'tools':[desc(SG/'scripts/prepare_sprite_run.py'),desc(Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py'))],
      'new_diagrams_viewed':False,'native_called':False,'ue_or_import_called':False,'extraction_called':False,'formal_complete_units':0})
files=[desc(p) for p in sorted(ROOT.rglob('*')) if p.is_file()]
write('preparation-freeze-v001.json',{'schema':'shoulder-preparation-freeze-v1','created_local':time_now,
      'files_excluding_this_manifest':files,'count_excluding_this_manifest':len(files),'bytes_excluding_this_manifest':sum(x['bytes'] for x in files),
      'generated_assets':0,'status':'frozen_input_only_await_root_retention_review'})
print(json.dumps({'ok':True,'root':ROOT.as_posix(),'files_with_manifest':len(files)+1,'freeze':desc(ROOT/'preparation-freeze-v001.json'),'rows':[r['state'] for r in rows]},ensure_ascii=False))
