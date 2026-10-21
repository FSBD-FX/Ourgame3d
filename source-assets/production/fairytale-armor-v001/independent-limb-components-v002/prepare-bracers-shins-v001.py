"""Prepare numeric requests and ORIGINAL technical diagrams only; never generate/edit final art."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002')
STYLE_REFERENCE = Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v001/far150-registration-proposed-v001/composite-preview/frame-0.png')
IDENTITY = CANON / 'curated/frame-0.png'
POSE_CONTACT = CANON / 'qa/idle-contact.png'
BODY = [CANON / f'curated/frame-{i}.png' for i in range(4)]
NOW = datetime.datetime.now().astimezone().isoformat()
parser = argparse.ArgumentParser()
parser.add_argument('--component', choices=['near-bracer','near-shin','far-bracer','far-shin'], required=True)
selection = parser.parse_args().component
if (ROOT / f'preparation-freeze-{selection}-v001.json').exists():
    raise RuntimeError('Frozen preparation exists; never overwrite it.')

def desc(p):
    p = Path(p)
    data = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def write(relative, value):
    p = ROOT / relative
    if p.exists():
        raise RuntimeError('Never overwrite: ' + str(p))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p

rows = [
    dict(key='near-bracer', state='armor_bracer_near_idle', role='near forearm', fit=(34,28), A=(187,283),
         outline=[(-14,-10),(-3,-12),(13,-7),(16,1),(7,10),(-6,14),(-18,8),(-18,0)], axis=(-9,11),
         protected=[(-23,17),(-10,17),(7,25),(2,64),(-29,67),(-41,45),(-36,22)],
         seam=[(-23,17),(-10,17),(7,25)],
         depth='The NEAR arm is the larger image-LEFT arm. Its short exposed cloth forearm slopes down-left toward the brown glove cuff. The metal is a broad, low-profile asymmetric forearm plate; its distal edge follows that down-left axis, but stops ABOVE the brown cuff. Do not cover any leather cuff, palm, thumb or fingers.',
         expected_readability='5.88x4.85 display pixels maximum at72px body; broad metal value/outer silhouette is plausible, rivet detail is not promised.',
         risk='Only about twenty source pixels of sleeve separate elbow and glove; the wrist seam is diagonal and varies slightly. Greatest risk is a glove-like output or distal rim covering the existing brown cuff.'),
    dict(key='near-shin', state='armor_shin_near_idle', role='near lower leg', fit=(36,34), A=(219,367),
         outline=[(-12,-7),(10,-7),(16,1),(12,15),(1,26),(-14,20),(-18,7)], axis=(-7,22),
         protected=[(-30,26),(-4,33),(14,36),(12,94),(-49,94),(-50,71)],
         seam=[(-30,26),(-4,33),(14,36)],
         depth='The NEAR leg is the image-LEFT leg. Its visible cloth lower-leg panel slopes slightly down-left into a DIAGONAL brown boot rim. Make a short, broad tapered greave over the CLOTH section only, below the knee and ABOVE that brown rim. The tip ends before the boot leather; no knee disk, boot cuff, foot, toe, sole or detached strap.',
         expected_readability='6.23x5.88 display pixels maximum at72px body; likely stronger silhouette contribution than far-side trim, still requires actual game review.',
         risk='Character has short cloth shins and tall boots. Calling the output a shin guard must not justify covering the boot rim or extending toward the ground.'),
    dict(key='far-bracer', state='armor_bracer_far_idle', role='far forearm', fit=(22,24), A=(315,296),
         outline=[(-8,-9),(2,-11),(10,-4),(11,5),(5,11),(-5,10),(-11,2)], axis=(5,9),
         protected=[(3,14),(15,8),(24,25),(43,65),(16,72),(-1,40)],
         seam=[(3,14),(15,8),(24,25)],
         depth='The FAR arm is the narrower image-RIGHT arm, receding behind the torso. Its foreshortened exposed sleeve leads down-right to the smaller brown glove. Produce the genuinely narrower visible far forearm plate, with different wrap/visible edge geometry from the near bracer; do not flip, copy or crop the near design. Stop before the brown glove cuff.',
         expected_readability='3.81x4.15 display pixels maximum at72px body; actual legibility uncertain, prepare only and do not default to a generation call.',
         risk='Tiny far forearm may read as one highlight beside the glove. Whole-body overlay also has no true hand occluder; cannot claim zero collision without actual review.'),
    dict(key='far-shin', state='armor_shin_far_idle', role='far lower leg', fit=(28,30), A=(288,370),
         outline=[(-11,-6),(10,-5),(14,4),(9,19),(0,24),(-12,18),(-14,5)], axis=(2,21),
         protected=[(-14,26),(12,29),(29,29),(63,73),(61,91),(-25,89)],
         seam=[(-14,26),(12,29),(29,29)],
         depth='The FAR leg is the image-RIGHT leg. Its shorter foreshortened cloth shin is more upright and presents a compressed metal face, not a mirrored near greave. The naturally visible plate ends ABOVE the brown boot rim; preserve the existing leather cuff, foot, toe and sole completely.',
         expected_readability='4.85x5.19 display pixels maximum at72px body; a small metal patch may be visible but exact near/far construction detail is not promised.',
         risk='Boot rim is nearly horizontal but not identical across poses. Far shin cannot be inferred from a mirrored near guard; actual visible source geometry must be separate.')
]

style = ('Canonical131 inked cartoon grotesque dark-fairytale identity, compact handmade plate construction matching actual147 chest and149/150 shoulder pieces. '
         'Broad matte desaturated grey metal face, restrained pale highlight, strong charcoal outer contour, no green/teal material, no ornate micro-detail.')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
prepared = []
for row in rows:
    if row['key'] != selection:
        continue
    key, state, fit = row['key'], row['state'], row['fit']
    run = ROOT / f'run-{key}-idle-v001'
    action = (f'Exactly four independent, connected {row["role"]} armor PLATES ONLY, one for each canonical131 idle pose0,1,2,3. '
              'One component per frame, no body or detached hardware; actual distinct native pieces, not copies or mirror substitutes.')
    seed = {'states': {state: {'frames':4,'fps':6,'loop':True,'action':action}},
            'cell': {'width':512,'height':512,'safe_margin_x':(512-fit[0])//2,'safe_margin_y':(512-fit[1])//2},
            'fit': {'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom',
                    'ground_frames':False,'segmentation':'components','shared_row_scale':True}}
    seed_path = write(f'requests/{key}-numeric-input-v001.json', seed)
    cmd = [sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),
           '--out-dir',str(run),'--character-id',f'fairytale-armor-trial-a-{key}-idle-v001',
           '--base-image',str(IDENTITY),'--description',action,'--style',style,'--cell-size','512',
           '--chroma-key','#00FF00','--request',str(seed_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    write(f'logs/prepare-{key}-v001.log', result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{key} standard prepare failed: {result.returncode}')
    request_path = run / 'sprite-request.json'
    request = json.loads(request_path.read_text(encoding='utf-8'))
    write(f'requests/{key}-standard-prepare-before-explicit-fields.json', request)
    request['states'][state]['durations_ms'] = [167]*4
    request['fit'].update(seed['fit'])
    request['chroma'] = {'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
    request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert request['cell']['safe_margin_x']==(512-fit[0])//2
    assert request['cell']['safe_margin_y']==(512-fit[1])//2
    assert (run/'base-source.png').read_bytes()==IDENTITY.read_bytes()

    # ORIGINAL schematic, not a crop/mask/repaint of any character pixels.
    # A red connected rivet is the sole mount; blue axis and tan zone are hints.
    im = Image.new('RGB',(2048,512),'#f4f6f8')
    draw = ImageDraw.Draw(im)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512" viewBox="0 0 2048 512"><rect width="2048" height="512" fill="#f4f6f8"/>']
    samples = []
    for i in range(4):
        ox = i*512
        def tx(p): return (ox+256+p[0]*5,200+p[1]*5)
        draw.rectangle((ox+10,10,ox+502,502),outline='#94a3b8',width=2)
        draw.text((ox+22,23),f'{key.upper()} / idle{i} /167ms',fill='#172554',font=font)
        draw.text((ox+22,49),f'BODY design A={row["A"]}; window={fit}',fill='#172554',font=font)
        protected = [tx(p) for p in row['protected']]
        draw.polygon(protected,fill='#e9c39e',outline='#9a5a35',width=3)
        seam = [tx(p) for p in row['seam']]
        draw.line(seam,fill='#713f12',width=4)
        axis = tx(row['axis'])
        a = tx((0,0))
        draw.line([a,axis],fill='#0284c7',width=20)
        points = [tx(p) for p in row['outline']]
        fill = '#9eb6c8' if key.startswith('near') else '#b9a7c4'
        draw.polygon(points,fill=fill,outline='#334155',width=4)
        draw.ellipse((a[0]-5,a[1]-5,a[0]+5,a[1]+5),fill='#dc2626')
        draw.text((ox+22,429),'RED=A only; axis is NOT another mount',fill='#172554',font=font)
        draw.text((ox+22,451),'TAN=protected cuff/hand or boot HINT',fill='#172554',font=font)
        draw.text((ox+22,474),'SCHEMATIC NOT MASK / no marks in art',fill='#172554',font=font)
        svg += [f'<rect x="{ox+10}" y="10" width="492" height="492" fill="none" stroke="#94a3b8"/>',
                f'<text x="{ox+22}" y="39" font-size="16">{key.upper()} / idle{i} /167ms</text>',
                f'<text x="{ox+22}" y="65" font-size="16">BODY design A={row["A"]}; window={fit}</text>',
                '<polygon points="'+' '.join(f'{x},{y}' for x,y in protected)+'" fill="#e9c39e" stroke="#9a5a35" stroke-width="3"/>',
                '<polyline points="'+' '.join(f'{x},{y}' for x,y in seam)+'" fill="none" stroke="#713f12" stroke-width="4"/>',
                f'<line x1="{a[0]}" y1="{a[1]}" x2="{axis[0]}" y2="{axis[1]}" stroke="#0284c7" stroke-width="20"/>',
                '<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" stroke="#334155" stroke-width="4"/>',
                f'<circle cx="{a[0]}" cy="{a[1]}" r="5" fill="#dc2626"/>',
                f'<text x="{ox+22}" y="445" font-size="16">RED=A only; axis is NOT another mount</text>',
                f'<text x="{ox+22}" y="467" font-size="16">TAN=protected cuff/hand or boot HINT</text>',
                f'<text x="{ox+22}" y="490" font-size="16">SCHEMATIC NOT MASK / no marks in art</text>']
        with Image.open(BODY[i]) as body:
            rgba = body.convert('RGBA').getpixel(row['A'])
        assert rgba[3]==255, 'Design mount is not opaque original cloth'
        samples.append({'frame':i,'A_body_px':list(row['A']),'A_body_rgba':list(rgba),'source':desc(BODY[i]),
                        'meaning':'Selected garment design mount on visible cloth, not a recovered bone or an actual existing rivet.',
                        'confidence':'medium; +/-2-3 source pixels of semantic/ink boundary ambiguity',
                        'constant_across_four':'Intentional stable design location inside the visible cloth patch in each actual frame; not claimed automatic tracking.'})
    svg.append('</svg>')
    guide_svg = write(f'guides/{key}-primary-mount-and-clearance-v001.svg','\n'.join(svg)+'\n')
    guide_png = ROOT / f'guides/{key}-primary-mount-and-clearance-v001.png'
    im.save(guide_png)

    prompt = f'''Create ONE production component-row strip containing exactly FOUR separate connected {row['role'].upper()} ARMOR PLATES, left to right for canonical131 idle poses0,1,2,3. Only the metal plate for this ONE anatomical side and body segment. No dressed hero, full arm, leg, glove or boot.

STRICT FIVE-REFERENCE ROLES:
1. canonical131 idle0 is the ONLY character and style identity. Its warm bell helmet, common body proportions and right-facing three-quarter depth are fixed context; none of the body is output.
2. canonical131 four-idle contact owns matching pose order0,1,2,3. Follow the corresponding visible cloth limb and cuff angle. Its limbs move very little: retain rigid plate volume and do not invent large motion to fake four different poses.
3. actual147 chest +149 near shoulder +150 far shoulder composite is ONLY the existing desaturated grey iron, broad charcoal ink and compact handmade construction reference. Ignore its character/body and already-worn pieces as output; no chest or shoulder pixels in this row.
4. standard four-slot layout owns total count4 and clear separation.
5. NEW original technical diagram owns plate silhouette direction and the single red primary mount A. Tan is only a schematic protected leather/hand/boot zone, NOT a measured semantic mask. Blue is a direction hint, NOT a second attachment. All guide colors, red dot, labels, border, axis and tan objects vanish from final output.

ANATOMY/DEPTH: {row['depth']}

PLATE DESIGN: a compact slightly crooked dark-fairytale cartoon iron plate, matching the already-generated chest and shoulders. One broad mid-grey metal face, a strong charcoal outside rim and at most one restrained pale edge. Keep large shapes useful at a72px body; no tiny engraving, chains, spikes or detached straps. Include ONE simple physically connected round mounting rivet within the plate, at the red-A guide position relative to the plate. The actual rivet center can be measured after extraction. The final fitted plate stays within{fit[0]}x{fit[1]} source pixels on the unchanged512 body canvas; do not turn the plate into a full-body416px sprite. Do not draw a separate technical marker or counting dot.

FOUR GENUINE PIECES: make the same rigid armor for each matching actual idle pose with coherent perspective and local cloth attachment. These are four native rendered component frames, not a pasted clone row, not a left/right mirror set, and not anatomy relabelled to pass. Near and far are separate genuine depth-specific designs. No recolored old armor, body crop, baked clothing or filled mannequin. Each frame is exactly ONE connected plate, so the whole row has FOUR connected components; use no fake bridge joining separate parts.

OUTPUT: flat fully opaque GREEN #00FF00 background, opaque metal interiors and clean cartoon ink edges. Four isolated objects on a single horizontal row, ample green gutters and outer padding. Use ONE common source drawing scale across all four; later extraction applies ONE shared row scale with Lanczos, never individual per-frame normalization. No floor, drop shadow, glow, halo, checkerboard, alpha preview, UI, words, labels, numbers or alternate camera views. Do not draw timing text; original timing remains4x167ms.

ABSOLUTE EXCLUSIONS: no helmet, head, face, neck, torso, chest, shoulder cap, shirt/sleeve or skin, opposite limb plate, glove cuff, hand, thumb, fingers, belt, knee disk, leather boot rim, foot, toe, sole, weapon or shield. Crop-free isolated armor is the output; technical supports are invisible.

STATUS: this is only this four-idle component row. No full armor, walk, attacks, weapon socket, exact hand-occluder or final motion acceptance is implied. Future near-arm/near-hand separation must use actual131 pixels, never old masks.
'''
    prompt_path = write(f'prompts/{key}-four-idle-v001.txt', prompt)
    refs = [{'role':'sole_identity','file':desc(IDENTITY)},
            {'role':'four_idle_pose_order_only','file':desc(POSE_CONTACT)},
            {'role':'actual147_149_150_material_construction_only','file':desc(STYLE_REFERENCE)},
            {'role':'standard_four_component_count_layout','file':desc(run/f'references/layout-guides/{state}.png')},
            {'role':'original_primary_mount_clearance_schematic_not_mask','file':desc(guide_png)}]
    assert len(refs)==5
    component_name = {'near-bracer':'NearBracer','near-shin':'NearShin','far-bracer':'FarBracer','far-shin':'FarShin'}[key]
    entry = {**row,'component':component_name,'status':'prepared_not_generated','run_dir':run.as_posix(),'prompt':desc(prompt_path),
             'reference_images_in_order':refs,'source_pose_mounts':samples,'source_native_facing':1,
             'fit_window_px':list(fit),'target_mounts':[{'frame':i,'A':list(row['A'])} for i in range(4)],
             'body_canvas_px':[512,512],'body_display_canvas_size':72*512/416,'body_display_pivot_px':[256,464],
             'pivot_is_certified_feet_root':False,'frame_count':4,'durations_ms':[167]*4,
             'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),'actual_native_request_number':None,
             'actual_raw_sha256':None,'actual_component_mounts':None,'generated':False,
             'standard_prepare_command':cmd,'standard_prepare_exit_code':result.returncode,
             'registration_plan':'After E-retained extraction, measure the actual connected rivet center A then integer-translate it to the named body design mount. Preserve croppedRGBA; no resize/warp/rotation/repaint. Axis/protected schematic is not another point residual or mask.'}
    prepared.append(entry)
    write(f'handoffs/{key}-native-input-v001.json',{'schema':'fairytale-limb-component-native-input-v1','created_local':NOW,'rows':[entry]})

contract = {'schema':'fairytale-bracer-shin-four-independent-idle-rows-v1','created_local':NOW,
            'status':'prepared_not_generated_not_imported','sole_identity':desc(IDENTITY),
            'old_reference_retention':'Root confirmed canonical131 fouridle E048 and actual147/149/150 full composite E105 before this review. New guides not viewed; root must retain them before viewing.',
            'actual_originals_viewed':[desc(p) for p in BODY]+[desc(STYLE_REFERENCE)],
            'rows':prepared,'minimum_call_order':['near-bracer first','near-shin after first actual fit review','far-bracer/far-shin prepared only; no default generation'],
            'scale':'Each row ONE scalar=min(windowWidth/maxRawWidth,windowHeight/maxRawHeight,1), no per-frame fit. Four rows have different intentional anatomical windows, not one normalizing scale across armor/body.',
            'A_contract':'Sole primary is actual connected rivet center. Target is an independently selected garment design mount with recorded original RGBA; no bone, hidden-root, foot, bbox-center or two-feature residual claims.',
            'protected_regions':'Original brown glove cuffs/hands and boot leather/feet remain intact. Technical tan polygons are schematic only, not semantic masks. Current no-mask static or runtime review cannot claim zero collision.',
            'runtime_layer_boundary':'For present unarmed idle only, actual narrow overlay can be reviewed against whole131. Future weapons need true131 near_arm/near_hand binary ownership and exact RGBA reconstruction, with weapon/armor/hand order; never reuse old masks.',
            'runtime_mirror':'Same canvas/pivot and ONE assembled mirror for displayFacing-1; source near/far identity does not swap.',
            'accepted_art':False,'motion_accepted':False,'full_armor_complete':False,'runtime_imported':False,'formal_complete_units':0}
write(f'limb-component-contract-{selection}-v001.json',contract)
if not (ROOT/'README.md').exists():
    write('README.md', '''# EV048 independent bracer/shin idle preparation

Prepared four separate4-frame component runs with standard sprite-gen ownvenv; no raw generation, extraction, import or Unreal execution.
Near bracer first; near shin next after actual fit review. Far rows are prepared alternatives, not authorization to spend a call automatically.
Canonical131 is the only identity. Existing147/149/150 full composite is material/construction only. Exactly five image references per row.
Each row has one shared scale and4x167ms. A is a garment-design mount/rivet-center registration plan, not a bone or feet root.
Technical diagrams are original shapes, NOT art edits or semantic masks. They have not been viewed pending root E retention.
Hand/glove cuff and boot/foot preservation must be checked on actual extracted/composited pieces. No mask-zero-collision, full armor or motion claim.
''')
all_files = sorted(p for p in ROOT.rglob('*') if p.is_file() and
                   (selection in p.relative_to(ROOT).as_posix() or p.name in ['README.md',Path(__file__).name]))
write(f'preparation-freeze-{selection}-v001.json',{'schema':'fairytale-limb-input-freeze-v1','created_local':NOW,
      'status':'prepared_not_generated','file_count':len(all_files),'total_bytes':sum(p.stat().st_size for p in all_files),
      'files':[desc(p) for p in all_files],'reference_limit_per_call':5,'new_media_viewed':False,
      'generation_by_this_author':False,'unreal_by_this_author':False,'formal_complete_units':0})
print(json.dumps({'status':'ready_for_root_retention_then_input_review','rows':len(prepared),
                  'first_handoff':desc(ROOT/f'handoffs/{selection}-native-input-v001.json'),
                  'first_prompt':desc(ROOT/f'prompts/{selection}-four-idle-v001.txt'),
                  'freeze':desc(ROOT/f'preparation-freeze-{selection}-v001.json')},ensure_ascii=False))
