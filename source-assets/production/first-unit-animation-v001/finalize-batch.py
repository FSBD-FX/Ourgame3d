"""Read actual generated PNGs, record QC/provenance and preserve review copies.

This script never draws, fixes or resizes artwork and never calls a model.
The subset manifest is intentionally NOT the formal content-atlas schema.
"""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[2] / '过程图稿与视频' / '2026-10-14_首单元动作生产_v001'
CONFIG = [
    ('hero', 'idle', 'hero-idle-matte-v002', 'visual_candidate', None),
    ('hero', 'walk', 'hero-walk-matte-v002', 'visual_candidate', None),
    ('hero', 'primary_1', 'hero-primary-1-body-matte-v002', 'body_only_assembly_candidate', [0.17, 0.12, 0.31]),
    ('hero', 'primary_2', 'hero-primary-2-body-matte-v002', 'body_only_assembly_candidate', [0.15, 0.12, 0.27]),
    ('hero', 'primary_3', 'hero-primary-3-body-matte-v002', 'body_only_assembly_candidate', [0.22, 0.12, 0.32]),
    ('stone', 'wake', 'stone-wake', 'visual_candidate_eye_flicker_review_required', None),
]

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy_no_overwrite(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert sha(target) == sha(source), f'Archive version conflict: {target}'
    else:
        shutil.copy2(source, target)

def pixel_record(path):
    raw = path.read_bytes()
    with Image.open(path) as opened:
        opened.load()
        assert opened.format == 'PNG' and opened.mode == 'RGBA', str(path)
        assert raw[24] == 8, f'Expected 8bit PNG: {path}'
        image = opened.copy()
    pixels = list(image.getdata())
    alpha = image.getchannel('A')
    visible = sum(a >= 128 for _r, _g, _b, a in pixels)
    fringe = sum(a >= 128 and r > g + 45 and b > g + 45 and r > 80 and b > 80 for r, g, b, a in pixels)
    bbox = image.getbbox()
    width, height = image.size
    result = {
        'path': str(path), 'sha256': sha(path), 'canvas_px': [width, height],
        'mode': 'RGBA', 'bit_depth': raw[24], 'alpha_extrema': list(alpha.getextrema()),
        'transparent_pixel_count': sum(a == 0 for _r, _g, _b, a in pixels),
        'visible_pixel_count_alpha_ge_128': visible, 'bbox_px': list(bbox) if bbox else None,
        'opaque_magenta_like_pixels': fringe, 'opaque_magenta_like_fraction': fringe / max(1, visible),
        'corners_transparent': all(image.getpixel(point)[3] == 0 for point in [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]),
    }
    assert bbox and width == 512 and height == 512
    assert result['alpha_extrema'] == [0, 255] and result['corners_transparent']
    assert 0 < bbox[0] < bbox[2] < width and 0 < bbox[1] < bbox[3] < height
    return result

def phase_plan(durations):
    if not durations:
        return None
    t = 0.0
    phases = []
    frames = []
    for index, (name, duration) in enumerate(zip(['windup', 'active', 'recovery'], durations)):
        end = round(t + duration, 6)
        phases.append({'name': name, 'start_s': t, 'end_s': end})
        middle = round(t + duration / 2, 6)
        frames.extend([{'frame_index': index*2, 'start_s': t, 'end_s': middle},
                       {'frame_index': index*2+1, 'start_s': middle, 'end_s': end}])
        t = end
    return {'status': 'authoring_plan_not_runtime_verified', 'duration_s': t,
            'source': 'docs/production/first-batch-v2/combo-spec.md',
            'phases_absolute': phases, 'frame_intervals_absolute': frames,
            'warning': 'GIF uses uniform preview delays; this plan must drive runtime phase binding. Images do not define damage windows.'}

def main():
    ledger = read(ROOT / 'generation-ledger.json')
    assert ledger['requested_count'] == 8 and len(ledger['requests']) == 8
    actions = []
    for actor, action, folder, status, timings in CONFIG:
        directory = ROOT / 'processed' / folder
        meta = read(directory / 'pipeline-meta.json')
        frames = [pixel_record(directory / f'{label}.png') for label in meta['frame_labels']]
        assert len(frames) == 6 and len({frame['sha256'] for frame in frames}) == 6
        summary = meta['qc_summary']
        assert summary['body_scale_cv'] <= 0.08 and summary['anchor_y_std'] <= 0.05
        assert summary.get('profile_body_scale_drift', 0) <= 0.08
        assert all(not meta[key] for key in ['empty_frames', 'source_edge_touch_frames', 'output_edge_touch_frames', 'paste_clamped_frames'])
        actions.append({'actor': actor, 'action': action, 'status': status,
            'folder': str(directory), 'sheet_path': str(directory / 'sheet-transparent.png'),
            'sheet_sha256': sha(directory / 'sheet-transparent.png'), 'frame_count': len(frames),
            'layout': {'rows': 2, 'columns': 3, 'cell_px': [512, 512]},
            'ground_root_px': meta['output_origin'], 'processor_qc': summary,
            'matting': {'threshold': meta['threshold'], 'edge_threshold': meta['edge_threshold']},
            'phase_binding_plan': phase_plan(timings), 'frames': frames,
            'layer_scope': 'whole body with baked clothing' if actor == 'hero' else 'whole stone body with baked shield and sword',
            'weapon_grip_emit_markers': 'missing_not_inferred', 'runtime_verified': False})
    raw_records = []
    for request in ledger['requests']:
        source = Path(request['source_path'])
        assert sha(source) == request['sha256']
        assert sha(Path(request['tool_original_path'])) == request['sha256']
        assert sha(Path(request['archive_original_path'])) == request['sha256']
        assert sha(Path(request['presentation_path'])) == request['sha256']
        with Image.open(source) as image:
            samples = [list(image.convert('RGB').getpixel(point)) for point in [(0,0),(image.width-1,0),(0,image.height-1),(image.width-1,image.height-1)]]
        raw_records.append({'request_number': request['request_number'], 'path': str(source),
            'sha256': request['sha256'], 'prompt_path': request['prompt_path'],
            'prompt_sha256': sha(Path(request['prompt_path'])), 'corner_rgb_samples': samples,
            'backend': 'image_gen.imagegen', 'model': 'host_default_model_not_exposed',
            'tool_original_path': request['tool_original_path'], 'license_class': 'host_generated_not_CC0_asserted'})
    payload = {'schema': 'generated-visual-subset-v1', 'status': 'visual_subset_not_runtime_accepted',
        'date': '2026-10-14', 'timezone': 'Asia/Shanghai', 'authorization': 'EV038',
        'generation_calls_used': 8, 'generation_calls_remaining_total': 16,
        'host_cost_usd': None, 'external_api_calls': 0,
        'anchors': [{'request_number': 1, 'status': 'internal_anchor_accepted_not_user_style_approval'},
                    {'request_number': 2, 'status': 'internal_anchor_accepted_not_user_style_approval'}],
        'actual_animation_frames': 36, 'actual_action_sheets': 6,
        'formal_content_atlas_validation_passed': False,
        'hero_scale_profile': str(ROOT / 'hero-scale-profile-matte-v002.json'),
        'hero_scale_profile_sha256': sha(ROOT / 'hero-scale-profile-matte-v002.json'),
        'raw_generation_provenance': raw_records, 'actions': actions,
        'limitations': ['No UE runtime import or playback in this task.',
            'Sword body poses can read as punches until sword/hand-occlusion assembly is verified.',
            'Baked clothing is not an interchangeable armor or near/far body layer set.',
            'Weapon component and per-frame grip/orientation/emitter markers remain missing.',
            'Stone wake eye goes dark again in frame4; review as flicker, not exact accepted wake behavior.',
            'Minor magenta-like edge pixels remain and are measured per frame; no claim of zero fringe.',
            'Existing formal atlas schema rejects fully hidden layers; no fake transparent or duplicate layers were supplied.',
            'These36frames cover only6actions, not the required22-action whole unit.',
            'GIF timing is preview-only; absolute phase plan is not implemented in runtime.',
            'Ground root is processor contact estimate [256,472], not prompt assumed [256,440].']}
    write(ROOT / 'generated-subset-manifest.json', payload)
    index = read(ARCHIVE / 'index.json')
    derived = {record['source']: record for record in index.get('derived_outputs', [])}
    folders = [ROOT/'processed'/item[2] for item in CONFIG]
    folders += [ROOT/'processed'/'hero-neutral-anchor', ROOT/'processed'/'stone-neutral-anchor']
    files = [path for folder in folders for path in folder.rglob('*') if path.is_file()]
    files += [ROOT/'hero-scale-profile-matte-v002.json', ROOT/'generated-subset-manifest.json']
    files += list((ROOT/'prompts').glob('*.txt'))
    for source in files:
        relative = source.relative_to(ROOT)
        original, presentation = ARCHIVE/'原件'/relative, ARCHIVE/'展示副本'/relative
        copy_no_overwrite(source, original); copy_no_overwrite(source, presentation)
        derived[str(source)] = {'source': str(source), 'original': str(original),
            'presentation': str(presentation), 'sha256': sha(source),
            'status': 'visual_candidate_not_runtime_accepted'}
    index['derived_outputs'] = list(derived.values())
    index['status'] = 'subbatch_8_calls_complete_visual_subset_only'
    index['actual_animation_frames'] = 36
    index['generation_calls_used'] = 8
    index['generation_calls_remaining_total'] = 16
    index['outputs'] = ledger['requests']
    write(ARCHIVE/'index.json', index)
    print(json.dumps({'actual_frames':36, 'actual_actions':6,
        'calls_used':8, 'calls_remaining_total':16,
        'max_magenta_like_opaque_pixels_per_frame':max(frame['opaque_magenta_like_pixels'] for item in actions for frame in item['frames']),
        'manifest':str(ROOT/'generated-subset-manifest.json')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
