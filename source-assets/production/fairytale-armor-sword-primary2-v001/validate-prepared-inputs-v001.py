"""Read numeric/provenance/PNG metadata only; never display new images."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parent
assert Path(sys.executable).resolve() == Path('C:/Users/22499/.codex/skills/sprite-gen/.venv/Scripts/python.exe').resolve()
M_PATH = ROOT.parent / 'fairytale-sword-primary2-v001/primary2-measurement-v003/measurement-v003.json'
M = json.loads(M_PATH.read_text(encoding='utf-8-sig'))
H = json.loads((ROOT / 'primary2-macro-native-handoff-draft-v001.json').read_text(encoding='utf-8'))
expected = {'Chest': [70, 50], 'NearShoulder': [60, 44], 'FarShoulder': [32, 30]}
checks = []
for row in H['rows']:
    request = json.loads(Path(row['standard_request']['path']).read_text(encoding='utf-8'))
    state = request['states'][row['state']]
    assert state['frames'] == 6 and state['durations_ms'] == [75, 75, 60, 60, 135, 135] and state['loop'] is False
    assert request['chroma_key']['hex'] == '#00FF00' and request['fit']['shared_row_scale'] is True and request['fit']['pixel_unfake'] is False
    cell = request['cell']
    assert [cell['width'] - 2 * cell['safe_margin_x'], cell['height'] - 2 * cell['safe_margin_y']] == expected[row['component']]
    assert len(row['reference_images_in_order']) == 5 and row['standard_prepare_exit_code'] == 0
    for mount, source in zip(row['mount_candidates'], M['frames']):
        assert mount['visible_cloth_design_A'] == source['body_design_A_candidates'][row['component']]
        assert mount['future_generated_component_A'] is None
    assert row['future_generated_component_A'] == [None] * 6 and row['generation_ready'] is False and row['new_outputs_viewed'] is False
    for ref in row['reference_images_in_order']:
        pin = ref['file']; data = Path(pin['path']).read_bytes()
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256']
    text = Path(row['prompt']['path']).read_text(encoding='utf-8')
    assert 'full-body frames' not in text and 'complete full-body pose' not in text
    assert 'native171' in text and 'hidden trial' in text.lower()
    checks.append({'component': row['component'], 'frames': 6, 'fit_window': expected[row['component']], 'passed': True})
trials = json.loads((ROOT / 'hidden-attachment-trial-design-v001.json').read_text(encoding='utf-8'))['trials']
assert [(t['component'], t['frame'], t['point'], t['uncertainty_source_px']) for t in trials] == [
    ('Chest', 3, [263, 268], 8), ('Chest', 4, [262, 269], 8), ('FarShoulder', 3, [307, 274], 10)]
assert all(t['source_visible_cloth_A'] is None and t['future_generated_feature_A'] is None for t in trials)
assert hashlib.sha256(M_PATH.read_bytes()).hexdigest() == '9a776415005eb1a71228360d7b14f468bc6d34db76afa554555d87bdafd2e8e4'
assert not list(ROOT.glob('run-*/raw/*.png')) and not list(ROOT.glob('run-*/frames/**/*.png'))
metadata = []
for path in sorted((ROOT / 'guides').glob('*.png')):
    with Image.open(path) as image:
        assert image.size == (3072, 512)
        metadata.append({'path': path.as_posix(), 'size': list(image.size), 'mode': image.mode, 'explicitly_viewed': False})
report = {'schema': 'native171-armor-input-numeric-validation-v1', 'checks': checks, 'all_passed': True,
          'hidden_trial_count': 3, 'source_visible_nulls_preserved': True, 'source_measurement_unchanged': True,
          'guide_metadata_only': metadata, 'new_outputs_viewed': False, 'generation_ready': False,
          'raw_png_count': 0, 'frame_png_count': 0, 'UE_generation_import_called': False,
          'first_text_case_assertion_diagnostic': 'validation-diagnostic-v001.json', 'formal_complete_units': 0}
path = ROOT / 'input-validation-v001.json'
assert not path.exists()
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'report': path.as_posix(), 'all_passed': True, 'new_outputs_viewed': False, 'generation_ready': False}))
