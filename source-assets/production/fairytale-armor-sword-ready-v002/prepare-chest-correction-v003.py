"""Draft standard Chest-v003 correction; actual160 remains rejected and unchanged."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = R / 'run-chest-ready-v003'
STATE = 'armor_chest_sword_ready'
assert not RUN.exists(), RUN

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(rel, value):
    p = R / rel
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return p

canonical = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
poses = Path('F:/Ourgame/source-assets/production/fairytale-sword-v001/run-ready-v002/qa/sword_ready_idle-contact.png')
positive0 = R / 'run-chest-ready-v002/curated/frame-0.png'
assert desc(positive0)['sha256'] == '6f9998c2cf44685b3d0d27831df365b5de9d134e20a094cfc39b9860e3a4fb6f'
seed = {'states': {STATE: {'frames': 4, 'fps': 6, 'loop': True,
        'action': 'Four distinct isolated connected BROAD Chest components, design width:height about1.5:1, same native3/4RIGHT on every pose; one clear central raised boss for future actual A measurement.'}},
        'cell': {'width': 512, 'height': 512, 'safe_margin_x': 221, 'safe_margin_y': 231},
        'fit': {'pixel_unfake': False, 'resample': 'lanczos', 'align_x': 'bbox-center', 'align_y': 'bottom',
                'ground_frames': False, 'segmentation': 'components', 'shared_row_scale': True}}
sp = write('requests/chest-correction-numeric-input-v003.json', seed)
argv = [sys.executable, '-X', 'utf8', '-B', str(SG / 'scripts/prepare_sprite_run.py'), '--out-dir', str(RUN),
        '--character-id', 'fairytale-native158-chest-facing-correction-v003', '--base-image', str(canonical),
        '--description', seed['states'][STATE]['action'], '--style',
        'Canonical131 hand-inked grotesque fairytale. Native160 positive frame0 warm-gray metal and same right-facing construction only. No body pixels.',
        '--cell-size', '512', '--chroma-key', '#00FF00', '--request', str(sp)]
result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
write('logs/prepare-chest-correction-v003.log', result.stdout + result.stderr)
assert result.returncode == 0, result.stderr
qp = RUN / 'sprite-request.json'; q = json.loads(qp.read_text(encoding='utf-8'))
write('requests/chest-correction-standard-before-explicit-fields-v003.json', q)
q['cell'] = {'shape': 'square', 'width': 512, 'height': 512, 'safe_margin_x': 221, 'safe_margin_y': 231}
q['fit'].update(seed['fit']); q['states'][STATE]['durations_ms'] = [167] * 4
q['chroma'] = {'mode': 'rgb', 'unmix_reach': 4, 'spill_max_fraction': .005}
qp.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
prompt = '''DRAFT ONLY, GENERATION_READY=FALSE. Root must first retain/review the actual160 extracted positive frame0, and approve a versioned corrected prompt. This file does not authorize or invoke generation.

Create exactly FOUR distinct isolated connected warm-gray chest-armor components for actual native158 low Ready0..3. Every piece faces the SAME native3/4RIGHT. Do not mirror, reverse perspective, alternate front/back or turn the fourth piece. Use attached actual160 positive frame0 only as the correct right-facing coarse construction/material reference: larger nearer strap/side armhole on image-LEFT, compressed farther strap/edge on image-RIGHT in ALL FOUR pieces. Its slender57x50 proportions are NOT locked: redesign a visibly broader horizontal plate, width:height about1.5:1 (approximately70x45 within the70x50 extraction design ceiling). Do not merely stretch or resize the old piece; author the broad form with the same material and perspective. Frame0 is not permission to clone it four times. Subtle real breathing differences only; preserve consistent construction, scale and camera.

Five reference roles: canonical131 is sole body/style identity (never render its body); actual158 four-body contact is the only current pose/depth authority; actual160 curated0 replaces147 palette-only with correct chest shape/warm-gray material reference; actual158 chest A guide contains visible-cloth DESIGN points and an adjustable70x50 extraction envelope, not a skeleton/semantic mask/final armor; standard four-slot guide gives count/layout only. Do not attach rejected160 frame3, old155 pose or old masks. No labels, red dots or rectangles in output.

Add ONE clearly visible CENTRAL raised round boss/rivet on the main chest plane, not on a side strap. This physical central boss will be the sole future component A. It must be a real drawn metal feature with an unambiguous visible center, not a bbox-center invented after extraction. Its actual pixel coordinate is UNKNOWN/null until the new output is retained and measured. The body target A259271 (other poses as guide) is central visible cloth, not a left strap bolt: never blindly align the large left strap bolt to that central body target. Side strap fasteners may remain construction details but are not competing primary A features. Keep the central boss subordinate to the broad plate, not an eye, face, glowing orb or ornate emblem.

Broad readable upper-chest mass, warm-gray matte metal, coarse dark ink outline, restrained warm edge; keep actual collar and belt visible and the near low fist clear. One connected component per pose; no neck/helmet/eyes/cloth/arms/hands/boots/body pixels, weapon, other armor piece, floor/shadow/FX/UI/text. Native158 source remains a72px squat hero, never enlarge it. Four times167ms, one shared row scale,512 cells, planned component envelope70x50 sourcepx. This is an extraction DESIGN ceiling, not a fill-box or proven fit. No per-frame fit/warp or local mirror correction.

Flat opaque GREEN #00FF00 around four generously separated whole components, opaque clean metal interiors. Actual generated feature A, protection against collar/hand overlap, all four fixed facings, chest fit, visible contribution, mirrored runtime and continuous Ready motion remain to be reviewed. Do not claim157 attack seams, full armor/equipment or game integration.
'''
pp = write('prompts/chest-correction-draft-v003.txt', prompt)
refs = [('sole_identity131', canonical), ('actual158_four_pose_only', poses), ('actual160_positive0_shape_palette_only_after_root_review', positive0),
        ('actual158_cloth_design_A_only', R / 'guides/chest-native158-design-A-v002.png'),
        ('standard_four_count_only', RUN / f'references/layout-guides/{STATE}.png')]
hp = write('chest-correction-handoff-draft-v003.json', {'schema': 'native158-chest-facing-correction-draft-v3',
        'created_local': datetime.datetime.now().astimezone().isoformat(), 'component': 'Chest', 'state': STATE,
        'run_dir': RUN.as_posix(), 'raw_output_path': (RUN / 'raw' / f'{STATE}.png').as_posix(), 'prompt': desc(pp),
        'reference_images_in_order': [{'role': role, 'file': desc(p)} for role, p in refs],
        'frame_count': 4, 'durations_ms': [167] * 4, 'fit_window_design_px': [70, 50],
        'shape_aspect_ratio_design': 1.5, 'approximate_shape_design_px': [70, 45],
        'actual_generated_component_A': [None] * 4, 'native_request_number': None, 'generation_ready': False,
        'blockers': ['Root E-retention/visual review of native160 curated0', 'Root versioned corrected prompt approval'],
        'standard_prepare_command': argv, 'standard_prepare_exit_code': result.returncode,
        'native160_whole_row_rejected': True, 'native160_changed': False, 'new_guides_explicitly_viewed': False,
        'native_called': False, 'ue_or_import_called': False, 'formal_complete_units': 0})
files = sorted([Path(__file__).resolve(), sp, pp, hp] + list(RUN.rglob('*')) +
               [R / 'requests/chest-correction-standard-before-explicit-fields-v003.json', R / 'logs/prepare-chest-correction-v003.log'])
files = [p for p in files if p.is_file()]
fp = write('chest-correction-preparation-freeze-v003.json', {'schema': 'chest-correction-draft-preparation-freeze-v3',
        'created_local': datetime.datetime.now().astimezone().isoformat(), 'file_count': len(files),
        'total_bytes': sum(p.stat().st_size for p in files), 'files': [desc(p) for p in files],
        'generation_ready': False, 'actual_generated_A': None, 'native_called': False, 'accepted': False})
print(json.dumps({'freeze': desc(fp), 'handoff': desc(hp), 'standard_prepare_exit_code': 0,
                  'raw_exists': (RUN / 'raw' / f'{STATE}.png').exists(), 'generation_ready': False}, ensure_ascii=False))
