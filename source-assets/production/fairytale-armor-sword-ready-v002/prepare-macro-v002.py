"""Three draft standard armor rows for actual native158; no native generation/UE."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
READY = Path('F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002')
PALETTE = Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front/frame-0.png')
MEASURE = R / 'measurement-candidate-v002.json'
M = json.loads(MEASURE.read_text(encoding='utf-8'))
SPECS = [('Chest', 'armor_chest_sword_ready', [70, 50]),
         ('NearShoulder', 'armor_shoulder_near_sword_ready', [60, 44]),
         ('FarShoulder', 'armor_shoulder_far_sword_ready', [30, 28])]

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(rel, value):
    p = R / rel
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p

assert CANON.exists() and PALETTE.exists() and (READY / 'qa/sword_ready_idle-contact.png').exists()
rows = []
for label, state, fit in SPECS:
    run = R / f'run-{label.lower()}-ready-v002'
    assert not run.exists(), run
    margins = [(512 - fit[0]) // 2, (512 - fit[1]) // 2]
    action = f'Four distinct isolated connected {label} pieces, matching actual native158 low Ready0..3. No body, weapon or other armor.'
    seed = {'states': {state: {'frames': 4, 'fps': 6, 'loop': True, 'action': action}},
            'cell': {'width': 512, 'height': 512, 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]},
            'fit': {'pixel_unfake': False, 'resample': 'lanczos', 'align_x': 'bbox-center', 'align_y': 'bottom',
                    'ground_frames': False, 'segmentation': 'components', 'shared_row_scale': True}}
    sp = write(f'requests/{label.lower()}-numeric-input-v002.json', seed)
    argv = [sys.executable, '-X', 'utf8', '-B', str(SG / 'scripts/prepare_sprite_run.py'), '--out-dir', str(run),
            '--character-id', f'fairytale-native158-macro-{label.lower()}-v002', '--base-image', str(CANON),
            '--description', action, '--style', 'Canonical131 hand-inked grotesque fairytale. Warm-gray147 metal palette only. Isolated broad armor component, not body or complete equipment.',
            '--cell-size', '512', '--chroma-key', '#00FF00', '--request', str(sp)]
    result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
    write(f'logs/prepare-{label.lower()}-v002.log', result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    qp = run / 'sprite-request.json'
    q = json.loads(qp.read_text(encoding='utf-8'))
    write(f'requests/{label.lower()}-standard-before-explicit-fields-v002.json', q)
    q['cell'] = {'shape': 'square', 'width': 512, 'height': 512, 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]}
    q['fit'].update(seed['fit']); q['states'][state]['durations_ms'] = [167] * 4
    q['chroma'] = {'mode': 'rgb', 'unmix_reach': 4, 'spill_max_fraction': .005}
    qp.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert (run / 'base-source.png').read_bytes() == CANON.read_bytes()

    # Exact source pixels on a neutral technical contact; no new body/armor art.
    guide = Image.new('RGB', (2048, 512), '#eeeeee')
    draw = ImageDraw.Draw(guide)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
    for i, f in enumerate(M['frames']):
        im = Image.open(Path(f['source']['path']))
        guide.paste(im, (i * 512, 0), im)
        x, y = f['body_attachment_design_A'][label]['point']; ox = i * 512
        draw.rectangle((ox + x - fit[0] / 2, y - fit[1] / 2, ox + x + fit[0] / 2, y + fit[1] / 2), outline='#166fd1', width=1)
        draw.ellipse((ox + x - 3, y - 3, ox + x + 3, y + 3), fill='#c51c24')
        draw.text((ox + 8, 8), f'158 actual Ready{i}: {label}; design A={x},{y}', fill='#111111', font=font)
        draw.text((ox + 8, 25), f'Window {fit[0]}x{fit[1]} is extraction DESIGN ONLY', fill='#111111', font=font)
        draw.text((ox + 8, 480), 'No bone/socket truth; no allowed semantic bbox or final armor drawn', fill='#111111', font=font)
    gp = R / f'guides/{label.lower()}-native158-design-A-v002.png'
    gp.parent.mkdir(parents=True, exist_ok=True); guide.save(gp)
    mounts = [f['body_attachment_design_A'][label] for f in M['frames']]
    direction = {'Chest': 'One connected broad upper-chest plate, inside the actual visible collar-lower-edge and belt-upper-edge. Expose dark neck/collar and belt; taper edges around actual near sleeve and far sleeve. No chest-wide harness over the low fist.',
                 'NearShoulder': 'One large functional near cap on the actual larger image-LEFT/front upper sleeve. Expand the OUTER shoulder silhouette, not upward into helmet/collar or down across forearm/cuff/hand. Inner edge must taper around the collar. No gigantic heavy beam or squared heavy pauldron.',
                 'FarShoulder': 'One genuinely different short/compressed far cap on the actual smaller image-RIGHT/deeper exposed sleeve. It must contribute visible metal without covering helmet/neck/hand. Author the true far perspective, never mirror/copy the near cap.'}[label]
    prompt = f'''DRAFT, GENERATION_READY=FALSE. Do not invoke a generator until root reviews the retained body partition and this technical guide.

Create exactly FOUR distinct isolated connected {label} armor components in one horizontal component row, matching actual native158 low sword-Ready0/1/2/3. These are a limited macro armor observation candidate, not a completed named item/set or attack row.

REFERENCE ROLES: canonical131 idle0 is the sole character/style identity; actual native158 four-body contact is the ONLY pose/depth authority (the near fist is actually image-LEFT at the waist, not design275315 or old155 across-chest);147 isolated plate gives ONLY warm-gray matte metal, warm restrained edge and coarse hand-ink line/palette, NEVER old shape/placement/body anatomy. The new actual158 guide shows a chosen visible cloth design A and adjustable extraction window, not a skeleton, a semantic collision mask or final armor art. Standard four-slot guide gives count/layout only. Do not copy labels/red dots/blue rectangles into output.

{direction}

Use broad readable warm-gray planes with a dark coarse contour; few large construction forms, minimal small rivet ornament. Preserve the squat character's72px body scale. The component extraction design window is {fit[0]}x{fit[1]}sourcepx; all four pieces use one common row scale, never individual fit or warp. A window is NOT permission to fill a box or overlap protected body parts. The body target design A values are {json.dumps(mounts, ensure_ascii=False)}. They have3–5px visible-surface selection uncertainty, are not hidden bones or old tracking locks. Generate one clearly visible functional attachment/rivet feature for later actual A measurement; its future pixel coordinate is UNKNOWN/null now. No second forced B attachment, no bbox-center substituted for A.

Output only this isolated armor component four times as genuinely distinct breath poses in the real158 pose order,4x167ms. NO helmet, face, eyes, neck, cloth body, arms/hands/fingers/legs/boots, blade/handle, other armor piece, whole-body painting, floor/shadow/FX/UI/text/checkerboard. Flat opaque GREEN #00FF00 background and generous clear gaps. Clean opaque metal interiors, original hand-inked edges. Never clone one piece four times, mirror near to far, crop147/149/150 into new source, or bake glove/cloth pixels to hide joints.

Future layer trial is BodyRest > FarShoulder > Chest > NearArmWithoutHand > NearShoulder > separate Sword > NearHand, copied from the actual158 RGBA partitions. Do not hide an entire cap behind a full-body replay or cover the fist/collar to manufacture fit. Actual generated A, silhouette, original thumb/cuff boundary uncertainty, chest/shoulder attachment and visible contribution will be checked only after retained extraction. No seamless157 attack transition, all-state/four-armor compatibility or equipment-complete claim follows from this idle trial.
'''
    pp = write(f'prompts/{label.lower()}-draft-v002.txt', prompt)
    refs = [('sole_identity131', CANON), ('actual158_only_four_ready_poses', READY / 'qa/sword_ready_idle-contact.png'),
            ('147_palette_only_no_geometry', PALETTE), ('actual158_design_mount_technical_only', gp),
            ('standard_four_count_only', run / f'references/layout-guides/{state}.png')]
    rows.append({'component': label, 'state': state, 'run_dir': run.as_posix(), 'raw_output_path': (run / 'raw' / f'{state}.png').as_posix(),
                 'prompt': desc(pp), 'reference_images_in_order': [{'role': role, 'file': desc(p)} for role, p in refs],
                 'frame_count': 4, 'durations_ms': [167] * 4, 'fit_window_design_px': fit,
                 'target_body_design_A': mounts, 'future_generated_component_A': [None] * 4,
                 'generation_ready': False, 'native_request_number': None, 'standard_prepare_command': argv,
                 'standard_prepare_exit_code': result.returncode, 'new_guide_explicitly_viewed': False,
                 'blockers': ['Root review of retained actual partition v002 and technical guides', 'Root separately approves versioned generation-ready input']})

hp = write('macro-native-handoff-draft-v002.json', {'schema': 'native158-macro-three-row-draft-v2',
    'created_local': datetime.datetime.now().astimezone().isoformat(), 'identity': desc(CANON), 'measurement': desc(MEASURE),
    'body_partition': desc(R / 'body-partition-v002/proof-v001.json'), 'rows': rows, 'generation_ready': False,
    'native_called': False, 'ue_or_import_called': False, 'new_guides_explicitly_viewed': False, 'formal_complete_units': 0})
print(json.dumps({'handoff': desc(hp), 'standard_prepare_runs': 3, 'generation_ready': False}, ensure_ascii=False))
