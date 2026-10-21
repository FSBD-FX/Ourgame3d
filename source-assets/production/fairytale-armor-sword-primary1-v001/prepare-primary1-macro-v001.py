"""Prepare three draft six-phase armor rows from retained native159; no generation/UE."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
PROD = Path('F:/Ourgame/source-assets/production')
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON = PROD / 'fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
CONTACT = PROD / 'fairytale-sword-v001/run-primary1-v003/qa/sword_primary_1-contact.png'
READY = PROD / 'fairytale-armor-sword-ready-v002'
MEASURE = R / 'primary1-measurement-candidate-v001.json'
M = json.loads(MEASURE.read_text(encoding='utf-8-sig'))
DURATIONS = [85, 85, 60, 60, 155, 155]
SPECS = [
    ('Chest', 'armor_chest_sword_primary1', [70, 50], READY / 'run-chest-ready-v003/curated/frame-0.png'),
    ('NearShoulder', 'armor_shoulder_near_sword_primary1', [60, 44], READY / 'run-nearshoulder-ready-v002/curated/frame-0.png'),
    ('FarShoulder', 'armor_shoulder_far_sword_primary1', [30, 28], READY / 'run-farshoulder-ready-v002/curated/frame-0.png'),
]


def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def write(rel, value):
    p = R / rel
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p


assert CANON.exists() and CONTACT.exists()
assert len(M['frames']) == 6 and M['durations_ms'] == DURATIONS
for f in M['frames']:
    p = Path(f['source']['path'])
    assert desc(p) == f['source']
    with Image.open(p) as im:
        assert im.mode == 'RGBA' and im.size == (512, 512)

font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
rows = []
for component, state, fit, family in SPECS:
    assert family.exists()
    run = R / f'run-{component.lower()}-primary1-v001'
    assert not run.exists(), run
    margins = [(512 - fit[0]) // 2, (512 - fit[1]) // 2]
    action = f'Six distinct isolated {component} views matching actual159 Primary1 phases0..5; no body, weapon or other armor.'
    seed = {
        'states': {state: {'frames': 6, 'fps': 10, 'loop': False, 'action': action}},
        'cell': {'width': 512, 'height': 512, 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]},
        'fit': {'pixel_unfake': False, 'resample': 'lanczos', 'align_x': 'bbox-center', 'align_y': 'bottom',
                'ground_frames': False, 'segmentation': 'components', 'shared_row_scale': True},
    }
    seed_path = write(f'requests/{component.lower()}-numeric-input-v001.json', seed)
    argv = [sys.executable, '-X', 'utf8', '-B', str(SG / 'scripts/prepare_sprite_run.py'),
            '--out-dir', str(run), '--character-id', f'fairytale-native159-armor-{component.lower()}-v001',
            '--base-image', str(CANON), '--description', action,
            '--style', 'Canonical131 grotesque hand-inked fairytale; actual159 poses; existing161/162/163 armor family and warm-gray metal. Isolated component only.',
            '--cell-size', '512', '--chroma-key', '#00FF00', '--request', str(seed_path)]
    result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
    write(f'logs/prepare-{component.lower()}-v001.log', result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    request_path = run / 'sprite-request.json'
    q = json.loads(request_path.read_text(encoding='utf-8'))
    write(f'requests/{component.lower()}-standard-before-explicit-fields-v001.json', q)
    q['cell'] = {'shape': 'square', 'width': 512, 'height': 512,
                 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]}
    q['fit'].update(seed['fit'])
    q['states'][state]['durations_ms'] = DURATIONS
    q['chroma'] = {'mode': 'rgb', 'unmix_reach': 4, 'spill_max_fraction': .005}
    request_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert (run / 'base-source.png').read_bytes() == CANON.read_bytes()

    # These are annotated technical contacts, never newly painted armor or production body pixels.
    guide = Image.new('RGB', (3072, 512), '#eeeeee')
    draw = ImageDraw.Draw(guide)
    for i, f in enumerate(M['frames']):
        ox = i * 512
        with Image.open(Path(f['source']['path'])) as body:
            guide.paste(body, (ox, 0), body)
        a = f['body_design_A_candidates'][component]['point']
        draw.line([(ox + x, y) for x, y in f['visible_near_sleeve_contour_candidate']] +
                  [(ox + f['visible_near_sleeve_contour_candidate'][0][0], f['visible_near_sleeve_contour_candidate'][0][1])],
                  fill='#6a3dad', width=1)
        draw.line([(ox + x, y) for x, y in f['visible_sleeve_to_brown_cuff_boundary_candidate']], fill='#f08213', width=2)
        if a is not None:
            x, y = a
            draw.rectangle((ox + x - fit[0] / 2, y - fit[1] / 2, ox + x + fit[0] / 2, y + fit[1] / 2),
                           outline='#166fd1', width=1)
            draw.ellipse((ox + x - 3, y - 3, ox + x + 3, y + 3), fill='#c51c24')
        draw.text((ox + 6, 6), f'159 phase{i} / {DURATIONS[i]}ms: {component}', fill='#111111', font=font)
        draw.text((ox + 6, 23), f'Visible-cloth DESIGN A: {a if a is not None else "NULL - occluded/unresolved"}', fill='#111111', font=font)
        draw.text((ox + 6, 478), 'Purple sleeve / orange cuff: +/-3px candidate; NOT binary ownership', fill='#111111', font=font)
        draw.text((ox + 6, 495), 'Blue window = extraction DESIGN ONLY; red point is not a bone', fill='#111111', font=font)
    guide_path = R / f'guides/{component.lower()}-actual159-design-v001.png'
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide.save(guide_path)

    feature = {
        'Chest': 'One clearly visible raised round CENTRAL chest boss, consistent with161, for later actual feature-edge measurement. The left strap bolt is NOT the central boss.',
        'NearShoulder': 'One clearly visible CENTRAL near-cap washer with dark hole, consistent with162; later A follows the actual washer-hole center.',
        'FarShoulder': 'Continue the explicit NEW topstrap-rivet trial from163: one clearly visible small top-strap rivet. This is NOT a central-front-boss contract;163 failed that original central-feature request and that failure remains.'
    }[component]
    construction = {
        'Chest': 'Broad compact chest plate with roughly1.5:1 width/height family, restrained edge and short straps. Preserve exposed dark collar and belt/buckle. Near forearm crosses IN FRONT atphase2 andphase3. Do not turn that gray forearm into chest material or move the boss onto the arm.',
        'NearShoulder': 'Broad functional near cap on the actual image-LEFT/front upper sleeve. Atphase1 the sleeve extends leftward under the helmet: author a genuine arm-following cap perspective/opening. Atphase2 the raised upper arm leads into a forearm across the torso. Atphase3 the forearm descends. Keep cap on the upper sleeve; never cover the brown cuff/fist or helmet/eyes.',
        'FarShoulder': 'Short compressed far cap on the image-RIGHT/deeper upper sleeve. It remains a distinct smaller far-perspective construction, never a mirrored near cap. Phase2 far attachment is unresolved behind the front action; preserve this uncertainty rather than inventing a measured socket.'
    }[component]
    mounts = [f['body_design_A_candidates'][component] for f in M['frames']]
    prompt = f'''DRAFT INPUT ONLY. GENERATION_READY=FALSE. No generator call is authorized by this file.

Create exactly SIX genuinely distinct isolated connected {component} armor views in ONE horizontal row, ordered actual native159 Primary1 phase0/1/2/3/4/5. This is the same compact light-armor family as the retained Ready component reference, adapted to real first-cut body poses. Not a completed item, combo, animation or equipment set.

REFERENCE ROLES: reference1 canonical131 is the sole hero identity/style. Reference2 actual159 six-body contact is the ONLY pose/depth authority; contact labels/standard100ms preview are not combat timing. Reference3 retained Ready component0 gives this item's construction, material and relative scale ONLY; never translate/rotate/warp or copy that image into all attack phases. Reference4 shows actual159 source pixels with candidate visible-cloth design points and sleeve/cuff traces; annotations are technical and must not appear in output. Reference5 is six-slot count/layout only. No anatomy, labels, marks or background copied from guides.

{construction}

PHASES:0 low-guard entry;1 real left-raised loading arm;2 forward crossing cut arm;3 downward follow-through arm;4 low-guard recovery;5 low-guard exit.0/4/5 share the158 Ready construction family but have their own159 cloth/fist/foot pixels and are NOT locked duplicates.1/2/3 require actual perspective/occlusion changes, not six offsets of idle armor. Keep the same rigid piece construction; no rubber stretch, melting plate, camera flip or arbitrary enlarged armor to hide joints.

{feature}

The future generated component A coordinates are all UNKNOWN/null until retained extraction and real feature measurement. Body visible-cloth DESIGN targets, not bones or existing physical rivets, are {json.dumps(mounts, ensure_ascii=False)}. Null means source attachment is occluded/unresolved; do not substitute a bbox center, a visible forearm point or a fabricated hidden joint. Generating a physically consistent isolated plate does not resolve registration of these null phases; those need a separately reviewed design decision after source exists.

Match the established warm-gray matte metal, restrained warm edge, coarse dark ink and few broad planes. Current extraction design maximum is{fit[0]}x{fit[1]}body-sourcepx; one common scale across the entire new six-piece row, no per-frame fit/rotation/warp, no changed body72px volume. A maximum rectangle is NOT a semantic silhouette or a license to fill it. Short foreshortening may reduce projected size; do not inflate an obscured piece to equal the longest view. Keep outline/large planes readable; avoid tiny decorative rivets, huge heavy squared pauldrons or extra harness.

Output ONLY the isolated connected {component}, six separate components on flat opaque GREEN #00FF00 with clear gaps. NO body/cloth/helmet/face/eyes/neck/hands/fingers/arms/legs/boots, blade/handle/scabbard, extra armor, effects, shadows, floor, UI, text, grid or checkerboard. No mirrored phase, recolored full body, Ready-pixel cutout, invisible armor replaced with a blank slot, or glove/cloth pixels baked into armor to disguise fit.

Requested six-phase durations are85/85/60/60/155/155ms, total600ms, non-looping. Standardfps10 previews only inspect shapes and may be100ms each; the actual game kernel phase must drive future body+armor+weapon together. Do not certify phase timing from a GIF.

Future layer trial: BodyRest > FarShoulder > Chest > NearArmWithoutHand > NearShoulder > separate Sword > NearHand. NearHand must own actual brown cuff/glove/ink/AA, not only a small fist replay polygon; current traces are uncertain candidates, not exact pixel masks. No hidden-pixel painting or body pose correction is authorized. Future exactRGBA reconstruction and semantic/collar/hand occlusion checks are separate requirements. No continuous transition, foot-lock, thumb anatomy, mirror-fit, attack damage, full equipment or all15-unit completion claim follows from this input preparation.
'''
    prompt_path = write(f'prompts/{component.lower()}-primary1-draft-v001.txt', prompt)
    refs = [('sole_identity131', CANON), ('actual159_only_six_phase_body_order', CONTACT),
            ('retained_ready_same_component_family_only', family), ('actual159_technical_design_no_bones', guide_path),
            ('standard_six_slot_count_only', run / f'references/layout-guides/{state}.png')]
    rows.append({
        'component': component, 'state': state, 'run_dir': run.as_posix(),
        'raw_output_path': (run / 'raw' / f'{state}.png').as_posix(), 'prompt': desc(prompt_path),
        'reference_images_in_order': [{'role': role, 'file': desc(path)} for role, path in refs],
        'frame_count': 6, 'durations_ms': DURATIONS, 'loop': False, 'native_facing': 1,
        'fit_window_design_px': fit, 'body_target_design_A': mounts,
        'future_generated_component_A': [None] * 6, 'generation_ready': False, 'native_request_number': None,
        'standard_prepare_command': argv, 'standard_prepare_exit_code': result.returncode,
        'standard_request': desc(request_path), 'new_guide_explicitly_viewed': False,
        'blockers': ['Root E retention and actual review of new technical guide/input',
                     'Separate versioned approval before any native generation',
                     'Occluded/null body A require an explicit later design registration decision',
                     'Actual159 complete cuff/sleeve ownership is not yet a binary pixel partition'],
    })

handoff = write('primary1-macro-native-handoff-draft-v001.json', {
    'schema': 'native159-primary1-three-armor-rows-input-draft-v1',
    'created_local': datetime.datetime.now().astimezone().isoformat(), 'identity': desc(CANON),
    'measurement': desc(MEASURE), 'rows': rows, 'generation_ready': False, 'native_called': False,
    'native_request_reserved': False, 'ue_or_import_called': False, 'new_guides_explicitly_viewed': False,
    'binary_body_partition_produced': False, 'formal_complete_units': 0,
})
print(json.dumps({'handoff': desc(handoff), 'standard_prepare_runs': 3,
                  'generation_ready': False, 'new_guides_explicitly_viewed': False}, ensure_ascii=False))
