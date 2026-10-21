"""Prepare three soft-leather Ready component rows; no generation/import/UE.

Run only with sprite-gen's venv. All writes stay beside this script. New technical
guides are NOT opened here: Root must retain them before visual review.
"""
from pathlib import Path
import datetime
import hashlib
import json
import platform
import re
import subprocess
import sys
import PIL
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = Path('F:/Ourgame')
ASSETS = ROOT / 'source-assets/production'
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
PYTHON = SG / '.venv/Scripts/python.exe'
CANON = ASSETS / 'fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
LEATHER = ASSETS / 'fairytale-lgt-readability-v003/concept179-v001/raw/179-soft-leather-reference.png'
MEASUREMENT = ASSETS / 'fairytale-armor-sword-ready-v002/measurement-candidate-v002.json'
DESIGN = ROOT / 'docs/design/equipment-v1/03-防具.md'
TIMES = {'Ready': [167] * 4, 'Primary1': [85, 85, 60, 60, 155, 155],
         'Primary2': [75, 75, 60, 60, 135, 135], 'Primary3': [110, 110, 60, 60, 160, 160]}
BODY = {'Ready': ASSETS / 'fairytale-sword-v001/run-ready-v002',
        'Primary1': ASSETS / 'fairytale-sword-v001/run-primary1-v003',
        'Primary2': ASSETS / 'fairytale-sword-primary2-v001/run-primary2-v004',
        'Primary3': ASSETS / 'fairytale-sword-primary3-v001/run-primary3-v001'}
FAMILIES = {'Ready': ASSETS / 'fairytale-armor-sword-ready-v002',
            'Primary1': ASSETS / 'fairytale-armor-sword-primary1-v001',
            'Primary2': ASSETS / 'fairytale-armor-sword-primary2-v001',
            'Primary3': ASSETS / 'fairytale-sword-primary3-v001/armor-input-v001'}
IMPORTS = {'Ready': FAMILIES['Ready'] / 'macro-registration-proposed-v001/macro-ready-import-handoff-v001.json',
           'Primary1': FAMILIES['Primary1'] / 'macro-registration-primary1-v001/candidate-import-v001.json',
           'Primary2': ASSETS / 'fairytale-armor-sword-primary2-runtime-v001/candidate-import-v001.json',
           'Primary3': ASSETS / 'fairytale-sword-primary3-runtime-v001/candidate-import-v001.json'}
REGISTRATIONS = {'Ready': FAMILIES['Ready'] / 'macro-registration-proposed-v001/macro-measurement-registration-v001.json',
                 'Primary1': FAMILIES['Primary1'] / 'macro-registration-primary1-v001/feature-measurement-registration-v001.json',
                 'Primary2': IMPORTS['Primary2'], 'Primary3': IMPORTS['Primary3']}
COMPONENTS = [('Chest', 'chest', 'Chest', [90, 90]),
              ('NearShoulder', 'nearshoulder', 'ShoulderNear', [60, 44]),
              ('FarShoulder', 'farshoulder', 'ShoulderFar', [30, 28])]
NATIVES = {'Ready': [161, 162, 163], 'Primary1': [164, 165, 167],
           'Primary2': [172, 173, 174], 'Primary3': [176, 177, 178]}
WATCHED = {}


def descriptor(path, watch=True):
    path = Path(path)
    data = path.read_bytes()
    result = {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if watch and not path.is_relative_to(OUT):
        WATCHED[path] = dict(result)
    return result


def read_json(path):
    descriptor(path)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(relative, value):
    path = OUT / relative
    assert path.is_relative_to(OUT), path
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        assert path.read_bytes() == payload.encode('utf-8'), ('Refuse changed existing output', path)
        return path  # Exact prior read-only index may survive an earlier preflight failure.
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(payload)
    return path


def png_info(path):
    source = descriptor(path)
    with Image.open(path) as image:
        assert image.mode == 'RGBA' and image.size == (512, 512), path
        a = np.asarray(image)
        source.update({'mode': image.mode, 'canvas_px': list(image.size),
                       'alpha_bbox_diagnostic_only': list(image.getchannel('A').getbbox()),
                       'nonzero_alpha_pixels': int(np.count_nonzero(a[:, :, 3]))})
    return source


def old_run(clip, token):
    version = 'v001'
    if clip == 'Ready':
        version = 'v003' if token == 'chest' else 'v002'
    elif clip == 'Primary1' and token == 'farshoulder':
        version = 'v003'
    return FAMILIES[clip] / f'run-{token}-{clip.lower()}-{version}'


def provenance_index():
    rows = []
    for clip, durations in TIMES.items():
        imported = read_json(IMPORTS[clip])
        for index, (component, token, runtime_key, _) in enumerate(COMPONENTS):
            run = old_run(clip, token)
            request_path = run / 'sprite-request.json'
            q = read_json(request_path)
            assert len(q['states']) == 1
            state, cfg = next(iter(q['states'].items()))
            assert cfg['frames'] == len(durations) and cfg['durations_ms'] == durations
            raw = run / 'raw' / f'{state}.png'
            fitted = [png_info(run / f'curated/frame-{i}.png') for i in range(len(durations))]
            registered = []
            for i in range(len(durations)):
                t = next(t for t in imported['textures'] if t['component'] == runtime_key and t['frame'] == i)
                actual = descriptor(t['source']['path'])
                assert all(actual[key] == t['source'][key] for key in ('path', 'bytes', 'sha256')), actual
                registered.append(png_info(actual['path']))
            fm = read_json(run / 'frames/frames-manifest.json')
            shared = fm['rows'][0]['shared_row_fit']
            assert shared['policy'] == 'one_raw_component_max_extent_scale_for_entire_row'
            assert shared['per_frame_scale_normalization'] is False
            current_bodies = [png_info(BODY[clip] / f'curated/frame-{i}.png') for i in range(len(durations))]
            rows.append({'clip': clip, 'component': component, 'old_native_request': NATIVES[clip][index],
                         'old_run': run.as_posix(), 'request': descriptor(request_path), 'raw': descriptor(raw),
                         'fitted_curated': fitted, 'registration_authority': descriptor(REGISTRATIONS[clip]),
                         'registered_current_texture_sources': registered,
                         'current_import_candidate': descriptor(IMPORTS[clip]), 'current_body_sources': current_bodies,
                         'durations_ms': durations, 'shared_row_fit': shared,
                         'old_source_role': 'geometry / perspective / motion basis only; NOT new leather item identity',
                         'new_run_created': clip == 'Ready', 'new_generated_feature_A': [None] * len(durations),
                         'new_run_permission': 'Ready preparation only' if clip == 'Ready' else 'INDEX ONLY; not prepared'})
    assert len(rows) == 12
    return write('existing-twelve-row-provenance-v001.json', {
        'schema': 'lgt-soft-leather-twelve-existing-row-provenance-v1', 'rows': rows,
        'new_prepared_row_count': 3, 'remaining_nine_runs_prepared': False,
        'joint_reuse_or_locomotion_solved': False, 'formal_complete_units': 0})


def main():
    assert Path(sys.executable).resolve() == PYTHON.resolve(), sys.executable
    assert descriptor(CANON)['sha256'] == 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
    assert descriptor(LEATHER)['sha256'] == 'f29ccca00cfb1095dc263240b3f554c780e421cfebf531099e2e92f5281c3c38'
    with Image.open(LEATHER) as image:
        assert image.mode == 'RGBA' and image.size == (1254, 1254)
    design_text = DESIGN.read_text(encoding='utf-8-sig')
    assert '褐色腰长皮衣、软肩、小布包' in design_text
    descriptor(DESIGN)
    measurement = read_json(MEASUREMENT)
    index_path = provenance_index()
    tools = [SG / 'scripts/prepare_sprite_run.py', SG / 'sprite_gen/gen/prepare.py', SG / 'SKILL.md',
             SG / 'scripts/extract_sprite_row_frames.py', SG / 'scripts/compose_sprite_atlas.py',
             SG / 'scripts/export_curated_pngs.py', SG / 'scripts/preview_animation.py',
             ROOT / 'tools/scripts/extract-sprite-shared-row-scale.py']
    tool_report = write('toolchain-provenance-v001.json', {
        'python_executable': sys.executable, 'python_version': platform.python_version(),
        'pillow_version': PIL.__version__, 'numpy_version': np.__version__,
        'sprite_gen_declared_version': re.search(r'^version:\s*(.+)$', (SG / 'SKILL.md').read_text(encoding='utf-8'), re.M).group(1),
        'tool_files': [descriptor(p) for p in tools], 'tools_modified': False})
    rows = []
    directions = {
        'Chest': 'One connected supple waist-length warm-brown leather jerkin front INCLUDING its one small connected side pouch. Broad light/dark leather planes and a few soft folds. Collar opening stays below the bell helmet; bottom hem reaches the belt / upper hip but leaves trousers and knees clear. Leave the grey near sleeve and the complete brown cuff/glove separate. Show one small functional front clasp or rivet for future feature measurement, NOT a large metal boss. Do not shrink this into the old little 70x50 plate.',
        'NearShoulder': 'One compact supple leather near shoulder cap: larger image-LEFT / foreground upper sleeve. A short rounded soft edge adds an outward silhouette, not a square hard pauldron or metal beam. Taper the neck edge below the helmet and stop before the elbow, forearm, cuff and fist. Keep a clearly visible dark joint gap. One modest stitch seam or leather clasp is enough; no metal washer or central disc.',
        'FarShoulder': 'One genuinely different compressed far leather cap: smaller image-RIGHT / deeper sleeve. Short soft shoulder, clear dark edge, restrained warm highlight. Keep neck and far glove clear. Do not mirror the near shoulder; preserve the same right-facing garment construction. A small seam / strap clasp may provide a later visible attachment feature; no front metal boss or large rivet disc.'}
    for component, token, runtime_key, window in COMPONENTS:
        state = f'leather_{token}_sword_ready'
        run = OUT / f'run-{token}-ready-v001'
        margins = [(512 - n) // 2 for n in window]
        action = f'Four distinct isolated connected soft-leather {component} views matching native158 Ready0..3; no character pixels.'
        seed = {'version': 1, 'kind': 'sprite-gen-request', 'engine': 'component-row',
                'states': {state: {'frames': 4, 'fps': 6, 'loop': True, 'action': action, 'durations_ms': TIMES['Ready']}},
                'cell': {'width': 512, 'height': 512, 'safe_margin_x': margins[0], 'safe_margin_y': margins[1]},
                'motion_phase_guides': False, 'fit': {'pixel_unfake': False, 'resample': 'lanczos',
                    'align_x': 'bbox-center', 'align_y': 'bottom', 'ground_frames': False,
                    'segmentation': 'components', 'shared_row_scale': True},
                'chroma': {'mode': 'rgb', 'unmix_reach': 4, 'spill_max_fraction': 0.005}}
        seed_path = write(f'requests/{token}-ready-numeric-input-v001.json', seed)
        argv = [str(PYTHON), '-X', 'utf8', '-B', str(SG / 'scripts/prepare_sprite_run.py'),
                '--out-dir', str(run), '--character-id', f'fairytale-lgt-soft-leather-{token}-ready-v001',
                '--base-image', str(CANON), '--description', action,
                '--style', 'Canonical131 grotesque hand-ink style; native179 warm-brown supple leather garment identity. Component only, no body or metal plate.',
                '--cell-size', '512', '--chroma-key', '#00FF00', '--request', str(seed_path)]
        if run.exists():
            # Resume ONLY the locally documented Chest post-prepare validation stop;
            # do not rerun standard prepare or overwrite any existing run.
            saved_before = OUT / f'requests/{token}-standard-request-before-explicit-v001.json'
            assert token == 'chest' and saved_before.exists()
            assert saved_before.read_bytes() == (run / 'sprite-request.json').read_bytes()
            assert not list((run / 'raw').glob('*.png'))
            result = subprocess.CompletedProcess(argv, 0, '', '')
        else:
            result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8')
            write(f'logs/prepare-{token}-ready-v001.log', result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        request_path = run / 'sprite-request.json'
        original = request_path.read_bytes()
        before = OUT / f'requests/{token}-standard-request-before-explicit-v001.json'
        if before.exists():
            assert before.read_bytes() == original
        else:
            with before.open('xb') as stream:
                stream.write(original)
        q = json.loads(original)
        changes = {}
        for key in ('fit', 'chroma', 'motion_phase_guides'):
            if q.get(key) != seed[key]:
                changes[key] = {'before': q.get(key), 'after': seed[key]}
                q[key] = seed[key]
        if q['states'][state].get('durations_ms') != TIMES['Ready']:
            changes[f'states.{state}.durations_ms'] = {'before': q['states'][state].get('durations_ms'), 'after': TIMES['Ready']}
            q['states'][state]['durations_ms'] = TIMES['Ready']
        assert q['cell']['safe_margin_x'] == margins[0] and q['cell']['safe_margin_y'] == margins[1]
        if changes:
            request_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        write(f'requests/{token}-explicit-request-fields-v001.json', {'changes': changes,
              'standard_before': descriptor(before), 'final': descriptor(request_path),
              'reason': 'Project shared-row/chroma contract explicit; standard output preserved before any change.'})
        assert (run / 'base-source.png').read_bytes() == CANON.read_bytes()
        guide = Image.new('RGB', (2048, 512), '#eeeeee')
        draw = ImageDraw.Draw(guide)
        font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
        mounts = []
        for frame in measurement['frames']:
            i = frame['frame']
            source = BODY['Ready'] / f'curated/frame-{i}.png'
            with Image.open(source) as image:
                guide.paste(image, (i * 512, 0), image)
            site = frame['body_attachment_design_A'][component]
            point = site['point']
            center = [point[0], point[1] + (7 if component == 'Chest' else 0)]
            x, y = center
            ox = i * 512
            draw.rectangle((ox+x-window[0]//2, y-window[1]//2, ox+x+window[0]//2, y+window[1]//2), outline='#196ab5', width=1)
            draw.line((ox+point[0]-3, point[1], ox+point[0]+3, point[1]), fill='#c52b32', width=1)
            draw.line((ox+point[0], point[1]-3, ox+point[0], point[1]+3), fill='#c52b32', width=1)
            draw.text((ox+8, 8), f'158 Ready{i} actual body; {component} DESIGN ONLY', fill='#111111', font=font)
            draw.text((ox+8, 26), f'{window[0]}x{window[1]} source window; no bone / final art', fill='#111111', font=font)
            draw.text((ox+8, 481), 'Future generated feature A = null. Do not copy guide marks.', fill='#111111', font=font)
            mounts.append({'frame': i, 'source': descriptor(source),
                           'visible_cloth_site_design': {'point': point, 'uncertainty_source_px': site['uncertainty_source_px'], 'measured_bone': False},
                           'window_center_design': center, 'window_size_design': window,
                           'window_is_semantic_mask_or_certified_fit': False,
                           'future_generated_component_A': None, 'hidden_joint': None})
        guide_path = OUT / f'guides/{token}-ready-body-design-v001.png'
        guide_path.parent.mkdir(parents=True, exist_ok=True)
        assert not guide_path.exists()
        guide.save(guide_path)
        prompt = f'''Create exactly FOUR complete, mutually separated, connected {component} components in one horizontal row, for native158 sword Ready0, Ready1, Ready2, Ready3. This is an isolated garment-component trial, not a full-body redraw or final equipment.

Five ordered reference roles: (1) canonical131 is the SOLE hero ink/style/body-proportion identity, but output NO body; (2) native179 is the NEW garment construction/material authority: warm brown supple leather waist-length jerkin, short soft shoulder caps and one small pouch, NOT hard grey metal; (3) the technical contact contains actual native158 body poses and visible cloth DESIGN sites, not measured bones; (4) the old corresponding grey-metal row supplies perspective / breathing-motion basis ONLY: discard its material, boss/washer ornament and small-chest proportions; (5) the standard four-slot guide supplies count/layout only. Never copy dots, lines, labels or rectangles into the output.

{directions[component]}

Keep four different subtle breathing perspectives of ONE garment construction, always native 3/4 RIGHT. No mirrored fourth pose, no cloned repeated piece, no deformation of a pasted old component. Use coarse hand-ink contours, broad warm tan highlights, reddish-brown midtones and deep brown shadow planes. Preserve soft leather folds and dark joints. Avoid thin grey outlines and busy tiny rivets; the goal is silhouette and value readability on a maximum72px hero. Garment identity must stay distinct from medium/heavy metal armor.

Source cell512x512. Proposed shared extraction window {window[0]}x{window[1]} sourcepx; all four pieces use ONE common row scale. This window is a design maximum, not permission to fill a rectangle, enlarge the hero, overlap the helmet, glove or knees, or resize each pose separately. The jerkin may reach the existing belt/upper hip; waist and near-arm occlusion require later actual fit review. A front clasp / shoulder seam must be measured on the FUTURE output; its actual component A is UNKNOWN/null. Existing cloth sites are attachment design candidates with3-5px uncertainty, not anatomical joints or a measured new clasp. Do not center a whole bbox and call it A.

Output only this garment component four times with generous clear gaps on flat opaque GREEN #00FF00. No hero, helmet, eyes, neck, skin, grey undercloth sleeves, hands/gloves/fingers, legs/boots, sword/handle, other armor piece, detached pouch, floor/shadow/VFX/UI/text/checkerboard. Chest is a single connected jerkin+pouch; shoulder rows contain only their respective cap. Clear opaque leather interiors and hand-ink edges.

Requested4x167ms is metadata, not a claim that the standard fps preview preserves exact durations. Future order: BodyRest > FarShoulder > Chest > NearArmWithoutHand > NearShoulder > independent Sword > NearHand. This keeps actual sleeve/hand pixels in front, never bakes them into leather. Single whole-parent mirror only at runtime. No generation approval, motion/footlock acceptance, hidden-joint cutout solution, other-state compatibility or20-combination completion is implied.
'''
        assert len(prompt.split()) <= 800
        prompt_path = write(f'prompts/{token}-ready-canonical-draft-v001.txt', prompt)
        old_row = next(r for r in read_json(index_path)['rows'] if r['clip'] == 'Ready' and r['component'] == component)
        refs = [('canonical131_sole_hero_ink_identity_no_body_output', CANON),
                ('native179_new_soft_leather_garment_identity_not_body_replacement', LEATHER),
                ('actual_native158_ready_motion_and_visible_cloth_design_only', guide_path),
                ('old_matching_row_geometry_motion_only_IGNORE_grey_metal_identity', Path(old_row['raw']['path'])),
                ('standard_four_slot_count_layout_only', run / f'references/layout-guides/{state}.png')]
        rows.append({'component': component, 'runtime_component': runtime_key, 'state': state,
                     'run_dir': run.as_posix(), 'raw_output_path': (run / 'raw' / f'{state}.png').as_posix(),
                     'prompt': descriptor(prompt_path), 'request': descriptor(request_path),
                     'reference_images_in_order': [{'role': role, 'file': descriptor(path)} for role, path in refs],
                     'frame_count': 4, 'durations_ms': TIMES['Ready'], 'fit_window_design_px': window,
                     'mount_candidates': mounts, 'future_component_A': [None]*4,
                     'target_mounts_are_measured': False, 'generation_ready': False,
                     'native_request_number': None, 'standard_prepare_command': argv,
                     'standard_prepare_exit_code': result.returncode,
                     'generation_scope': 'Ready soft-leather isolated component input only; no actual generation or joint/motion acceptance'})
    handoff = write('lgt-ready-native-input-draft-v001.json', {
        'schema': 'lgt-soft-leather-ready-three-component-row-draft-v1',
        'created_local': datetime.datetime.now().astimezone().isoformat(),
        'sole_hero_identity': descriptor(CANON), 'new_garment_identity_reference': descriptor(LEATHER),
        'design_contract': descriptor(DESIGN), 'existing_twelve_row_index': descriptor(index_path),
        'toolchain': descriptor(tool_report), 'ready_body_measurement': descriptor(MEASUREMENT),
        'rows': rows, 'generation_ready': False, 'root_review_required_before_generation': True,
        'new_guides_explicitly_viewed': False, 'native_called': False, 'ue_or_import_called': False,
        'joint_cutout_or_locomotion_solved': False, 'other_nine_new_runs_prepared': False,
        'native_facing': 1, 'display_root': [256,464], 'maximum_body_height_screen_px': 72,
        'whole_parent_mirror_once': True, 'formal_complete_units': 0})
    mismatches = [str(p) for p, before in WATCHED.items() if descriptor(p, watch=False) != before]
    assert not mismatches, mismatches
    write('preparation-verification-v001.json', {'standard_prepare_runs': 3, 'prepare_exit_codes': [0]*3,
          'source_files_rechecked_unchanged': len(WATCHED), 'source_mismatches': mismatches,
          'new_raw_files': list(str(p) for p in OUT.glob('run-*/raw/*') if p.is_file()),
          'new_guides_explicitly_viewed': False, 'native_called': False,
          'handoff': descriptor(handoff), 'future_feature_A_all_null': True,
          'new_primary_runs_created': False})
    print(json.dumps({'handoff': descriptor(handoff), 'prepared_rows': 3, 'indexed_existing_rows': 12,
                      'generation_ready': False, 'new_guides_viewed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
