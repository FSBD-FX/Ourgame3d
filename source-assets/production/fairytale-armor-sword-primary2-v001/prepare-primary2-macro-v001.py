"""Prepare native171 light-armor input rows only. No generation, import or view."""
from pathlib import Path
import copy
import datetime
import hashlib
import json
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PRODUCTION = ROOT.parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
EXPECTED_INTERPRETER = SG / '.venv/Scripts/python.exe'
assert Path(sys.executable).resolve() == EXPECTED_INTERPRETER.resolve(), sys.executable
MEASUREMENT_ROOT = PRODUCTION / 'fairytale-sword-primary2-v001/primary2-measurement-v003'
MEASUREMENT = MEASUREMENT_ROOT / 'measurement-v003.json'
MEASUREMENT_FREEZE = MEASUREMENT_ROOT / 'measurement-freeze-v003.json'
CANON = PRODUCTION / 'fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
PRECEDENT = PRODUCTION / 'fairytale-armor-sword-primary1-v001/macro-registration-primary1-v001/delivery-freeze-v001.json'
DURATIONS = [75, 75, 60, 60, 135, 135]
SPECS = [
    ('Chest', 'armor_chest_sword_primary2', [70, 50], 161,
     'run-chest-ready-v003', 'actual central raised round chest boss'),
    ('NearShoulder', 'armor_shoulder_near_sword_primary2', [60, 44], 162,
     'run-nearshoulder-ready-v002', 'actual central near-cap washer dark-hole center'),
    ('FarShoulder', 'armor_shoulder_far_sword_primary2', [32, 30], 163,
     'run-farshoulder-ready-v002', 'actual small top-strap rivet center, NOT centralboss'),
]
HIDDEN_TRIALS = {
    'Chest': {3: ([263, 268], 8), 4: ([262, 269], 8)},
    'NearShoulder': {},
    'FarShoulder': {3: ([307, 274], 10)},
}


def fact(path):
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(relative, value):
    path = ROOT / relative
    assert not path.exists(), f'Refuse overwriting versioned input: {path}'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


assert fact(MEASUREMENT_FREEZE)['sha256'] == 'e03de5b66bb17e9e89d9f0487361b24635682c4124b957104e1bf43ff8c30f19'
assert fact(MEASUREMENT)['sha256'] == '9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4'
for pin in load(MEASUREMENT_FREEZE)['files']:
    assert fact(Path(pin['path'])) == pin
M = load(MEASUREMENT)
assert M['source_native'] == 171 and M['frame_count'] == 6
assert M['source_canvas'] == [512, 512] and M['source_mode'] == 'RGBA'
assert M['timing']['kernel'] == DURATIONS and sum(DURATIONS) == 540
assert M['timing']['standard_preview_total'] == 600 and M['timing']['retimed'] is False
assert fact(CANON)['sha256'] == 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
for pin in load(PRECEDENT)['files']:
    assert fact(Path(pin['path'])) == pin
source_checks = []
for frame in M['frames']:
    source = Path(frame['source']['path'])
    assert fact(source) == frame['source']
    with Image.open(source) as image:
        assert image.mode == 'RGBA' and image.size == (512, 512)
    retained = frame['all_E209_matching_copies']
    assert len(retained) == 3
    for pin in retained:
        assert fact(Path(pin['path'])) == pin
    source_checks.append({'frame': frame['frame'], 'original': fact(source), 'E209_matching_copies': retained})
for component, phases in HIDDEN_TRIALS.items():
    for phase in phases:
        assert M['frames'][phase]['body_design_A_candidates'][component]['point'] is None

write('input-source-audit-v001.json', {
    'measurement_freeze': fact(MEASUREMENT_FREEZE), 'measurement': fact(MEASUREMENT),
    'measurement_frozen_files_checked': 5, 'identity': fact(CANON), 'base_lock': 'prior accepted canonical131 idle; not newly visually certified here',
    'actual_primary1_delivery_freeze_precedent': fact(PRECEDENT), 'precedent_files_checked': len(load(PRECEDENT)['files']),
    'precedent_role': 'process/registration/stack precedent only; NOT pose truth and NO copied native159 coordinates',
    'frames': source_checks, 'new_outputs_viewed': False, 'native_or_image_generation_called': False,
})
decision = write('design-decision-far-family-v001.json', {
    'authority': 'Root explicit correction in current task, before any draft freeze',
    'decision': 'Keep approved Ready/P1 Far163 topstrap-rivet family/feature for the same light armor across Ready/P1/P2',
    'far163_original_centralboss_requirement_passed': False,
    'far163_failed_centralboss_history_preserved': True,
    'this_primary2_far_feature': 'small actual top-strap rivet; future A measured only after new output exists',
    'this_primary2_far_claims_centralboss_satisfaction': False,
    'chest_feature': 'central raised round boss', 'near_feature': 'central washer dark-hole',
    'future_generated_features_A': [None] * 6,
})
trial_path = write('hidden-attachment-trial-design-v001.json', {
    'authority': 'Root explicit hidden TRIAL design for native171; independent of immutable measurement-v003',
    'coordinate_convention': 'original512 x right, y down',
    'trials': [{'component': component, 'frame': phase, 'point': point, 'uncertainty_source_px': error,
                'kind': 'HIDDEN TRIAL DESIGN ONLY; not visible cloth, measured bone, joint or generated feature',
                'source_visible_cloth_A': None, 'future_generated_feature_A': None}
               for component, phases in HIDDEN_TRIALS.items() for phase, (point, error) in phases.items()],
    'measurement_modified': False, 'accepted_registration': False, 'new_outputs_viewed': False,
})

font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11)
contact = Image.new('RGB', (3072, 512), '#eeeeee')
for i, frame in enumerate(M['frames']):
    with Image.open(Path(frame['source']['path'])) as body:
        contact.paste(body, (i * 512, 0), body)
contact_path = ROOT / 'guides/native171-six-original512-contact-v001.png'
contact_path.parent.mkdir(parents=True, exist_ok=True)
assert not contact_path.exists()
contact.save(contact_path)

rows = []
for component, state, window, native, family_dir, feature in SPECS:
    family = PRODUCTION / f'fairytale-armor-sword-ready-v002/{family_dir}/curated/frame-0.png'
    assert family.exists()
    run = ROOT / f'run-{component.lower()}-primary2-v001'
    assert not run.exists(), run
    margins = [(512 - window[0]) // 2, (512 - window[1]) // 2]
    action = f'Six distinct isolated {component} rigid light-armor component views in original native171 Primary2 phase0..5 order; no body or weapon.'
    fit = {'pixel_unfake': False, 'resample': 'lanczos', 'align_x': 'bbox-center', 'align_y': 'bottom',
           'ground_frames': False, 'segmentation': 'components', 'shared_row_scale': True}
    seed = {'states': {state: {'frames': 6, 'fps': 10, 'loop': False, 'action': action}},
            'cell': {'width': 512, 'height': 512, 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]}, 'fit': fit}
    seed_path = write(f'requests/{component.lower()}-numeric-input-v001.json', seed)
    argv = [sys.executable, '-X', 'utf8', '-B', str(SG / 'scripts/prepare_sprite_run.py'), '--out-dir', str(run),
            '--character-id', f'fairytale-native171-armor-{component.lower()}-v001', '--base-image', str(CANON),
            '--description', action, '--style', 'Canonical131 grotesque hand-inked fairytale; native171 poses only; retained161/162/163 light-armor material family. Isolated component.',
            '--cell-size', '512', '--chroma-key', '#00FF00', '--request', str(seed_path)]
    completed = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
    write(f'logs/prepare-{component.lower()}-v001.log', completed.stdout + completed.stderr)
    assert completed.returncode == 0, completed.stderr
    request_path = run / 'sprite-request.json'
    request = load(request_path)
    write(f'requests/{component.lower()}-standard-before-explicit-fields-v001.json', request)
    assert request['cell']['width'] == 512 and request['cell']['height'] == 512
    assert request['cell']['safe_margin_x'] == margins[0] and request['cell']['safe_margin_y'] == margins[1]
    request['fit'].update(fit)
    request['states'][state]['durations_ms'] = DURATIONS
    request['chroma'] = {'mode': 'rgb', 'unmix_reach': 4, 'spill_max_fraction': .005}
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert (run / 'base-source.png').read_bytes() == CANON.read_bytes()
    prompt_path = run / 'prompts' / f'{state}.txt'
    standard_prompt = prompt_path.read_text(encoding='utf-8')
    write(f'prompts/{component.lower()}-standard-before-component-scope-v001.txt', standard_prompt)
    scoped = standard_prompt.replace('full-body frames', f'complete isolated {component} views')
    scoped = scoped.replace('complete full-body pose', f'complete isolated {component} view')
    scoped = scoped.replace('No character body part should be clipped by the frame slot.', 'No component edge should be clipped by the frame slot.')
    scoped = scoped.replace('Spend the variation budget on limb contacts, arm counter-swing, body height, torso lean, head bob, hair bounce, and loop continuity.',
                            'Vary only rigid plate foreshortening, flange opening and strap depth following native171; never render or redesign any body part.')

    guide = contact.copy()
    drawing = ImageDraw.Draw(guide)
    mounts = []
    for i, frame in enumerate(M['frames']):
        ox = i * 512
        visible = copy.deepcopy(frame['body_design_A_candidates'][component])
        trial = HIDDEN_TRIALS[component].get(i)
        entry = {'frame': i, 'visible_cloth_design_A': visible, 'hidden_trial_design_A': None, 'future_generated_component_A': None}
        if trial:
            point, error = trial
            entry['hidden_trial_design_A'] = {'point': point, 'uncertainty_source_px': error,
                'kind': 'Root HIDDEN TRIAL DESIGN ONLY; not visible/measured cloth/bone/joint or generated feature'}
        mounts.append(entry)
        sleeve = frame['visible_near_sleeve_contour_candidate']['points']
        cuff = frame['visible_sleeve_to_brown_cuff_boundary_candidate']['points']
        drawing.line([(ox + x, y) for x, y in sleeve + [sleeve[0]]], fill='#7135aa', width=1)
        drawing.line([(ox + x, y) for x, y in cuff], fill='#df780b', width=2)
        point = visible['point'] if visible['point'] is not None else trial[0] if trial else None
        if point is not None:
            x, y = point
            drawing.rectangle((ox + x - window[0] / 2, y - window[1] / 2, ox + x + window[0] / 2, y + window[1] / 2), outline='#166fd1', width=1)
            if visible['point'] is not None:
                drawing.ellipse((ox + x - 3, y - 3, ox + x + 3, y + 3), fill='#bd1525')
            else:
                drawing.polygon([(ox + x, y - 5), (ox + x + 5, y), (ox + x, y + 5), (ox + x - 5, y)], fill='#f09a12')
        label = f'Visible-cloth DESIGN {visible["point"]}' if visible['point'] is not None else f'Visible A NULL; HIDDEN TRIAL {trial[0]} +/-{trial[1]}'
        drawing.text((ox + 5, 5), f'171 phase{i} / kernel{DURATIONS[i]}ms: {component}', fill='#111111', font=font)
        drawing.text((ox + 5, 20), label, fill='#111111', font=font)
        drawing.text((ox + 5, 479), 'Purple sleeve / orange cuff: candidates, NOT binary ownership', fill='#111111', font=font)
        drawing.text((ox + 5, 495), 'Blue fit window DESIGN only. Red/diamond are NOT bones.', fill='#111111', font=font)
    guide_path = ROOT / f'guides/{component.lower()}-native171-design-v001.png'
    assert not guide_path.exists()
    guide.save(guide_path)
    construction = {
        'Chest': 'Compact broad torso plate, same161 central-boss construction and warm-gray metal, restrained straps/flanges. Keep collar and belt readable. In phases3/4 the near sleeve/forearm/cuff crosses IN FRONT; keep armor behind that arm and hand. Those chest mounts are hidden TRIAL design, not sampled exposed shirt.',
        'NearShoulder': 'Larger image-LEFT/front cap on the actual upper grey sleeve. Preserve162 central washer dark-hole and a functional open cap. Phase1 near arm loads to the left; phases2/3 fold and rise to chest level, phase4 recoils, phase5 returns. Author real rigid cap perspective/opening changes. Stay above the brown cuff and avoid helmet/eyewindow; never turn the forearm/fist into shoulder armor.',
        'FarShoulder': 'Smaller, deeper, compressed image-RIGHT/back cap, same approved163 topstrap-rivet construction across Ready/P1/P2. Never mirror the near cap or inflate its small projected size. Phase3 is partly/fully obscured by the near fist: its isolated plate still needs a physically consistent view under the separate hidden TRIAL design. Far163 failed the original centralboss request; this row deliberately continues the approved topstrap family and MUST NOT claim centralboss compliance.',
    }[component]
    extra = f'''

STRICT COMPONENT-ROW INPUT, GENERATION_READY=FALSE. No generator is called by preparation.
The subject is ONLY one standalone {component} armor piece per slot, never the hero. Generic identity/face language above locks style only and does not request body pixels. Request truth is exactly six512 slots, margins{margins[0]}/{margins[1]}, green#00FF00, shared row scale and non-looping kernel durations{DURATIONS}. Do not independently normalize individual frames or use local rotation/warp to fake new views.

REFERENCE OWNERSHIP: reference1 canonical131 accepted idle is the sole identity/style; reference2 is the six original512 native171 bodies in phase order and is the ONLY motion/depth authority; reference3 retained Ready{native} component0 supplies this same item's construction/material only, not attack geometry or reusable pixels; reference4 is technical source171 cloth/sleeve/cuff/design annotation; reference5 is standard count/padding only. Do not reproduce labels, fit boxes, colored points or diagrams. No old native159/169/170 pose or attachment coordinates are authority.

{construction}
Future physical feature A: {feature}. It must be a real drawn metal feature with an unambiguous center. Every generated feature-A coordinate is still UNKNOWN/null until new raw output is retained, standard-extracted and actually measured. Neither body design targets, the rectangle center nor a convenient side bolt may be substituted for this physical component feature.

PHASES from actual171 only:0 compact low guard;1 low/left loading with closed hand;2 bent sleeve and near fist across abdomen;3 raised bent near forearm/cuff/fist under helmet at chest;4 chest-level recoiling closed hand;5 low-guard return. Preserve genuine foreshortening and occlusion changes, not six translated idle pieces. Do not stretch plate material, flip camera, fill the maximum fit rectangle, duplicate0 into5, or enlarge the72px hero to conceal a seam. The requested{window[0]}x{window[1]}sourcepx fit ceiling is a DESIGN envelope, not an accepted silhouette or fit.

Visible-cloth candidates and separate Root hidden TRIALs follow; null visible data must stay null and are never claimed sampled bones/cloth. Hidden TRIAL points are explicit provisional design only, with lower certainty, not a replacement measurement:
{json.dumps(mounts, ensure_ascii=False)}

Output six genuinely different isolated CONNECTED {component} views, whole in their invisible slots, generously separated on flat opaque GREEN #00FF00. Warm-gray matte metal, coarse dark ink, restrained warm edge, few broad readable planes, same light-armor volume. NO body, cloth, helmet, face, eyes, neck, hands/fingers/cuff/glove/arms/legs/boots, blade/handle, other armor, FX, ground/shadows, text, labels, grid or checkerboard. Do not cut out, redraw, translate or warp Ready pixels into fake attack layers. No blank slot for an obscured phase; later real body partition determines visibility.

Future stack trial, bottom to top: BodyRest / FarShoulder / Chest / NearArmWithoutHand / NearShoulder-cap / ExactHelmet / separateSword / NearHand. Actual brown cuff, glove, shared ink and AA ownership, exact helmet partition and plate contribution need separate originalRGBA partition plus real feature registration and fit. No such partition or fit is produced by this preparation.

TIMING LIMIT: requested combat durations75/75/60/60/135/135 total540ms. The standard fps10 preview/atlas path is known to yield100ms x6=600ms. This input does not fix, retime or certify that discrepancy; shape review and future kernel-driven runtime timing remain separate. No motion/transition/foot-lock/grip/thumb/mirrored-fit/hit/SFX/equipment-set/unit acceptance follows from these files.
'''
    prompt_path.write_text(scoped + extra, encoding='utf-8')
    write(f'run-{component.lower()}-primary2-v001/qa-notes.md',
          'Prepared input only; raw and frames empty. Standard prepare prompt preserved outside run; canonical prompt scopes generic full-body wording to isolated component.\n'
          'Identity=accepted131; motion=original171 only; Ready component=construction/material only. No new output viewed. Generation_ready=false.\n'
          'Kernel540ms != standard100ms*6=600ms; no timing QA/retiming. Actual partition/registration/fit and all runtime acceptance pending.\n')
    refs = [('sole_identity_accepted_idle131', CANON), ('only_motion_original171_six512', contact_path),
            (f'ready{native}_same_lightarmor_family_material_only', family),
            ('source171_visible_design_and_separate_hidden_trial_technical_only', guide_path),
            ('standard_six_count_spacing_only', run / f'references/layout-guides/{state}.png')]
    rows.append({'component': component, 'state': state, 'run_dir': run.as_posix(), 'raw_output_planned': (run / f'raw/{state}.png').as_posix(),
                 'prompt': fact(prompt_path), 'reference_images_in_order': [{'role': role, 'file': fact(path)} for role, path in refs],
                 'frame_count': 6, 'durations_ms': DURATIONS, 'kernel_total_ms': 540, 'standard_preview_total_ms': 600,
                 'shared_row_scale': True, 'per_frame_normalization': False, 'fit_window_design_px': window,
                 'mount_candidates': mounts, 'future_generated_component_A': [None] * 6, 'feature_contract': feature,
                 'standard_prepare_command': argv, 'standard_prepare_exit_code': completed.returncode,
                 'standard_request': fact(request_path), 'generation_ready': False, 'new_outputs_viewed': False,
                 'native_request_number': None, 'native_generation_called': False})
handoff = write('primary2-macro-native-handoff-draft-v001.json', {
    'schema': 'native171-primary2-three-lightarmor-standard-input-draft-v1', 'created_local': datetime.datetime.now().astimezone().isoformat(),
    'identity': fact(CANON), 'measurement_freeze': fact(MEASUREMENT_FREEZE), 'measurement': fact(MEASUREMENT),
    'hidden_trial_decision': fact(trial_path), 'far_family_design_decision': fact(decision), 'rows': rows,
    'generation_ready': False, 'native_called': False, 'external_api_calls': 0, 'native_request_reserved': False,
    'UE_import_or_UBT_called': False, 'new_outputs_viewed': False, 'body_partition_produced': False,
    'timing_contract_passed': False, 'formal_complete_units': 0,
    'blockers': ['Root retention and actual review of new input/guide before any generation',
                 'Actual independent newly generated armor perspective rows remain absent',
                 'Future physical feature A measurement and originalRGBA partition/registration/fit required',
                 'Standard600ms versus kernel540ms remains an explicit unresolved preview timing boundary'],
})
assert fact(MEASUREMENT)['sha256'] == '9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4'
assert fact(MEASUREMENT_FREEZE)['sha256'] == 'e03de5b66bb17e9e89d9f0487361b24635682c4124b957104e1bf43ff8c30f19'
assert not list(ROOT.glob('run-*/raw/*.png')) and not list(ROOT.glob('run-*/frames/**/*.png'))
print(json.dumps({'handoff': fact(handoff), 'standard_prepare_runs': 3, 'all_exit_zero': True,
                  'generation_ready': False, 'new_outputs_viewed': False}, ensure_ascii=False))
