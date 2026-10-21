"""Native159 standard shared-row extraction and unscaled diagnostics; no display/import."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
from PIL import Image

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
H = json.loads((R / 'handoffs/primary1-native-input-v003.json').read_text(encoding='utf-8'))['rows'][0]
run, state = Path(H['run_dir']), H['state']
out = R / 'primary1-extraction-v003'
parser = argparse.ArgumentParser()
parser.add_argument('--finalize-existing', action='store_true', help='Retain already-executed standard output after explicit timing diagnosis; do not run tools again.')
finalize_existing = parser.parse_args().finalize_existing
if finalize_existing:
    assert out.exists() and (out / 'failed-attempt-v001/extract-primary1-v003-before-timing-diagnosis.py').exists()
else:
    assert not out.exists(), out
    out.mkdir()
durations = [85, 85, 60, 60, 155, 155]

def desc(p):
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(p, x):
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

raw = Path(H['raw_output_path'])
assert desc(raw)['sha256'] == '1a29c97a5d8bb33e4921402675a41dc0c09fd8b398a4cafa2198d2e4f440880a'
assert H['frame_count'] == 6 and H['durations_ms'] == durations and H['loop'] is False
wrapper = Path('F:/Ourgame/tools/scripts/extract-sprite-shared-row-scale.py')
assert desc(wrapper)['sha256'] == '2d7464dc2e8dd962a7d4dc170c0a7401d09cf1a626415309b4921b7d89d88aa3'
before = (run / 'sprite-request.json').read_bytes()
if finalize_existing:
    assert before == (out / 'sprite-request-before-extraction.json').read_bytes()
else:
    (out / 'sprite-request-before-extraction.json').write_bytes(before)
commands = []
for name, tool, args in [
    ('extract-shared-row', wrapper, []),
    ('compose-atlas', SG / 'scripts/compose_sprite_atlas.py', []),
    ('export-curated', SG / 'scripts/export_curated_pngs.py', ['--state', state]),
    ('preview', SG / 'scripts/preview_animation.py', []),
]:
    argv = [sys.executable, '-X', 'utf8', '-B', str(tool), '--run-dir', str(run)] + args
    log = out / f'{name}-v001.log'
    if finalize_existing:
        assert log.exists(), log
        # First execution reached the subsequent manifest timing assert; every command's
        # exit-code assertion therefore passed. Original logs and failed script are retained.
        exit_code = 0
    else:
        result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
        write(log, result.stdout + result.stderr)
        exit_code = result.returncode
    commands.append({'argv': argv, 'tool': desc(tool), 'exit_code': exit_code, 'log': desc(log),
                     'ran_in_finalization': not finalize_existing})
    assert exit_code == 0, (name, exit_code)
assert before == (run / 'sprite-request.json').read_bytes()
request = json.loads(before)
assert request['states'][state]['durations_ms'] == durations
assert request['states'][state]['loop'] is False
manifest = json.loads((run / 'frames/frames-manifest.json').read_text(encoding='utf-8'))
assert manifest['ok'] and manifest['errors'] == [] and manifest['warnings'] == []
atlas_report = json.loads((run / 'sprite-sheet-alpha.report.json').read_text(encoding='utf-8'))
assert atlas_report['ok'], atlas_report
runtime = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
actual_atlas_durations = runtime['animation']['rows'][state]['durations_ms']
assert runtime['animation']['rows'][state]['loop'] is False
with Image.open(run / f'qa/{state}.gif') as gif:
    actual_gif_durations = []
    for i in range(gif.n_frames):
        gif.seek(i)
        actual_gif_durations.append(gif.info.get('duration'))
timing_gate = actual_atlas_durations == durations and actual_gif_durations == durations
if not timing_gate:
    assert finalize_existing and actual_atlas_durations == [100] * 6 and actual_gif_durations == [100] * 6
    write(out / 'failed-attempt-v001/timing-diagnosis.json', {
        'schema': 'standard-sprite-tool-nonuniform-timing-diagnosis-v1',
        'first_run_exit_code': 1,
        'first_run_assertion': "runtime['animation']['rows'][state]['durations_ms'] == durations",
        'standard_command_exit_codes_before_assertion': [0, 0, 0, 0],
        'request_durations_ms': durations, 'actual_atlas_durations_ms': actual_atlas_durations,
        'actual_gif_durations_ms': actual_gif_durations,
        'compose_implementation': desc(SG / 'sprite_gen/compose/compose_atlas.py'),
        'compose_source_lines': [216, 227],
        'preview_implementation': desc(SG / 'sprite_gen/qa/preview.py'),
        'preview_source_lines': [127, 134],
        'finding': 'Installed standard compose/preview derive equal durations from fps and do not honor this request nonuniform array.',
        'installed_tools_modified': False, 'pixels_modified_to_repair': False,
        'preview_retimed': False, 'motion_rhythm_accepted': False,
    })
row = manifest['rows'][0]
shared = row['shared_row_fit']
assert not shared['per_frame_scale_normalization']
frames = []
for i in range(6):
    p = run / f'curated/frame-{i}.png'
    with Image.open(p) as im:
        assert im.mode == 'RGBA' and im.size == (512, 512)
        bbox = im.getchannel('A').getbbox()
        assert bbox
        diagnostics = []
        # Wide ROIs inspect actual output without assuming the design grip was obeyed.
        for role, roi in [('hands_inspection', [80, 100, 432, 390]),
                          ('feet', [128, 415, 388, 465]),
                          ('whole_alpha_bbox', list(bbox))]:
            q = out / f'diagnostics-v001/frame-{i}-{role}.png'
            q.parent.mkdir(parents=True, exist_ok=True)
            crop = im.crop(roi)
            crop.save(q)
            assert crop.tobytes() == im.crop(roi).tobytes()
            diagnostics.append({'role': role, 'source_roi_px': roi, 'file': desc(q),
                                'resampled': False, 'source_pixel_bytes_preserved': True,
                                'semantic_mask': False, 'art_asset': False})
    frames.append({'frame': i, 'file': desc(p), 'alpha_bbox_px': list(bbox),
                   'alpha_bbox_size_px': [bbox[2] - bbox[0], bbox[3] - bbox[1]],
                   'diagnostics': diagnostics, 'grip_actual_px': None,
                   'handle_axis_actual_xy': None, 'fist_replay_polygon_actual_px': None,
                   'feet_root_actual_px': None,
                   'measurement_status': 'Actual hand/feet not visually measured. No planned or previous markers transplanted; wait root E retention before review.'})
assert len({x['file']['sha256'] for x in frames}) == 6
receipt = {
    'schema': 'fairytale-native159-primary1-shared-extraction-v3',
    'created_local': datetime.datetime.now().astimezone().isoformat(),
    'component': 'SwordPrimary1', 'raw': desc(raw), 'handoff': desc(R / 'handoffs/primary1-native-input-v003.json'),
    'request': desc(run / 'sprite-request.json'), 'commands': commands, 'frames': frames,
    'frames_manifest': desc(run / 'frames/frames-manifest.json'),
    'atlas_report': desc(run / 'sprite-sheet-alpha.report.json'),
    'QA_errors': manifest['errors'], 'QA_warnings': manifest['warnings'],
    'unique_frame_png_count': len({x['file']['sha256'] for x in frames}),
    'shared_row_ratio': shared['scale'], 'shared_row_fit': shared,
    'durations_ms': durations, 'loop': False, 'request_and_timing_modified': False,
    'actual_atlas_durations_ms': actual_atlas_durations, 'actual_gif_durations_ms': actual_gif_durations,
    'timing_gate': timing_gate,
    'preview_scope': 'Shape-only equal-time standard preview; nonuniform combat timing must be sampled from the unchanged request through actual kernel phase, not this GIF.',
    'new_alpha_or_contact_or_diagnostics_viewed': False,
    'raw_explicitly_viewed_by_this_script_or_reviewer': False,
    'native_called': False, 'ue_import_called': False, 'formal_complete_units': 0,
}
write(out / 'extraction-receipt-v001.json', receipt)
files = sorted([p for p in run.rglob('*') if p.is_file()] +
               [p for p in out.rglob('*') if p.is_file()] + [Path(__file__).resolve()])
fp = out / 'extracted-freeze-v001.json'
write(fp, {'schema': 'fairytale-sword-body-extracted-freeze-v3',
           'created_local': datetime.datetime.now().astimezone().isoformat(),
           'component': 'SwordPrimary1', 'native_request': 159,
           'file_count': len(files), 'total_bytes': sum(p.stat().st_size for p in files),
           'files': [desc(p) for p in files], 'new_outputs_viewed': False,
           'registration_proposed': False, 'accepted': False})
print(json.dumps({'freeze': desc(fp), 'files': len(files),
                  'bytes': sum(p.stat().st_size for p in files),
                  'QA_errors': manifest['errors'], 'QA_warnings': manifest['warnings'],
                  'shared_row_ratio': shared['scale'], 'durations_ms': durations,
                  'actual_atlas_durations_ms': actual_atlas_durations,
                  'actual_gif_durations_ms': actual_gif_durations, 'timing_gate': timing_gate,
                  'frames': [{k: x[k] for k in ['frame', 'file', 'alpha_bbox_px', 'grip_actual_px']} for x in frames]}, ensure_ascii=False))
