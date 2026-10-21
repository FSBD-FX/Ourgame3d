"""Prepare a new six-phase trial from canonical identity and both contact poses."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

root = Path('F:/Ourgame')
hero = root / 'source-assets/production/fairytale-hero-v001'
skill = Path('C:/Users/22499/.codex/skills/sprite-gen')
run = hero / 'sprite-run-walk-v004'
assert not run.exists(), 'Keep every previous run unchanged'
canonical = hero / 'sprite-run-idle-v002/curated/frame-0.png'
assert hashlib.sha256(canonical.read_bytes()).hexdigest() == 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
source = json.loads((hero / 'sprite-run-walk-v003/sprite-request.json').read_text(encoding='utf-8'))
source.pop('project_motion_guide', None)
source['character']['id'] = 'fairytale-hero-common-walk-dual-contact-v001'
source['character']['base_image'] = str(canonical)
source['states']['walk']['action'] = (
    'Exactly SIX distinct poses of ONE complete alternating humanoid walk cycle, all facing RIGHT in the '
    'same three-quarter camera. Empty hands; compact grounded walking, not running or high-knee marching. '
    'The canonical single idle image alone owns identity. The TWO-CONTACT image owns opposite limb-role '
    'examples: its LEFT character is phase0, its RIGHT character is phase3. The six-phase technical guide '
    'owns pose order only; RED means camera-near and BLUE means camera-far, never paint these colors. '
    'Near/far are fixed anatomical sides, not current screen-left/right. Keep a rigid unchanged bell '
    'helmet and stable body/glove/boot volumes. Natural opposing arm and leg swing. '
    '0 NEAR CONTACT: near leg forward/right with heel down; far leg rear/left with toe down. '
    'LARGE NEAR ARM BACK/LEFT, far arm forward/right, like the LEFT contact example. '
    '1 NEAR SUPPORT / FAR PASSING: near foot flat beneath pelvis, near knee supports weight; far knee '
    'swings forward passing the supporting leg, its boot clears ground slightly. Arms pass neutral. '
    '2 NEAR PUSH / FAR REACH: near rear toe pushes; far heel reaches front/right just before landing. '
    'Near arm swings forward across the torso; far arm goes back. '
    '3 FAR CONTACT: far leg front/right heel down; NEAR leg rear/left toe down. '
    'LARGE NEAR ARM FORWARD/RIGHT ACROSS TORSO, far arm back/left, like the RIGHT contact example. '
    'This is the OPPOSITE contact to0; never reset to the phase0 arm or leg layering. '
    '4 FAR SUPPORT / NEAR PASSING: far foot flat beneath pelvis supports weight; near knee swings '
    'forward passing the far support leg, near boot clears ground slightly. Arms pass neutral in '
    'the opposite direction to1. Do not make a backward kick or a high knee. '
    '5 FAR PUSH / NEAR REACH: far rear toe pushes; near heel reaches front/right before landing. '
    'LARGE NEAR ARM BACK/LEFT, far arm forward/right; continue smoothly back into0. '
    'Near-hand swing across0..5 is BACK, NEUTRAL, FRONT, FRONT, NEUTRAL, BACK. '
    '0/3,1/4,2/5 must swap the anatomical supporting/reaching leg and counter-swinging arm. '
    'Keep the pelvis centered within each cell and one real foot/toe grounded per pose. '
    'No full-character mirroring, repeated three-pose half-cycle, duplicate stills, drifting scale, '
    'extra limbs, detached pieces, shadows, motion trails, scenery, labels or technical guide marks.'
)
recipe = hero / 'walk-dual-contact-numeric-request-v001.json'
assert not recipe.exists()
recipe.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
subprocess.run([sys.executable, '-B', '-X', 'utf8', str(skill / 'scripts/prepare_sprite_run.py'),
                '--out-dir', str(run), '--character-id', source['character']['id'],
                '--base-image', str(canonical), '--description', source['character']['description'],
                '--chroma-key', '#00FF00', '--request', str(recipe)], check=True)
refs = run / 'references/motion'
refs.mkdir()
panel = refs / 'both-opposite-contacts-137-138-v001.png'
guide = refs / 'six-phase-near-far-technical-v001.png'
shutil.copy2(hero / 'sprite-run-contact-near-v001/references/dual-contact-motion-reference-v001.png', panel)
shutil.copy2(hero / 'sprite-run-walk-v003/references/layout-guides/walk-six-phase-technical-v001.png', guide)
request_path = run / 'sprite-request.json'
ready = json.loads(request_path.read_text(encoding='utf-8'))
ready['chroma'] = source['chroma']
references = [
    (run / 'base-source.png', 'sole identity: canonical131 single curated idle'),
    (panel, 'two opposite contacts: near138 left=phase0; far137 right=phase3; motion only'),
    (guide, 'six-phase original technical guide only; no character art authority'),
    (run / 'references/layout-guides/walk.png', 'six slots and padding only'),
]
rows = [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'role': role}
        for path, role in references]
ready['project_motion_references'] = rows
ready['project_runtime_design'] = {'frames': 6, 'durations_ms': [83]*6, 'loop_ms': 498,
    'native_facing': 1, 'future_clock': 'actual resolved ground displacement',
    'stride_design_world_units': 132, 'runtime_imported': False, 'motion_accepted': False}
request_path.write_text(json.dumps(ready, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
prompt_path = run / 'prompts/walk.txt'
prompt_path.write_text(prompt_path.read_text(encoding='utf-8') + '\n\nATTACHMENTS IN ORDER:\n'
    '1 canonical identity; 2 BOTH opposite contacts (LEFT=phase0, RIGHT=phase3); '
    '3 six-phase limb-role diagram; 4 blank six-slot spacing. Only image1 owns identity. '
    'Do not copy the diagrams, color codes or labels into the output.\n', encoding='utf-8')
(run / 'qa-notes.md').write_text(
    '# Multi-pose locomotion trial\n\n135/136 whole rows are rejected and are not image references. '
    '137/138 contribute two opposite static contacts only; canonical131 remains sole identity. '
    'This is not a single peak-pose locomotion anchor. No raw or motion acceptance yet. '
    'Extraction must use the project shared-row scale extension and installed sprite-gen venv.\n',
    encoding='utf-8')
(run / 'preparation-receipt-v001.json').write_text(json.dumps({
    'status': 'prepared_only_not_generated', 'run': str(run), 'references': rows,
    'numeric_request_sha256': hashlib.sha256(recipe.read_bytes()).hexdigest(),
    'sprite_request_sha256': hashlib.sha256(request_path.read_bytes()).hexdigest(),
    'prompt_sha256': hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
    'preparer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'full_motion_gate_required': True, 'automatic_import': False,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'prepared': str(run), 'references': rows}, ensure_ascii=False))
