"""Independent Air6 host contracts. No IO/native actions at module import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import struct
import sys
import zlib
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
ROOT = Path('F:/Ourgame')
HERE = Path(__file__).resolve().parent
LEAF = HERE.parent
AIR = LEAF.parent
COMPONENTS = ('BodyRest', 'ShoulderFar', 'Chest', 'NearArmWithoutHand', 'ShoulderNear',
              'HelmetForeground', 'FarHandForeground', 'NearHand', 'IndependentSword')
SCHEMA = 'hero-nonattack-air-production-native-observer-v001'
SCENARIO = 'NormalEnter_StarterNone6_E_LGT9_LandingRejump'
CLOSURE = '5df0479bd1689b8adeb525255e748db13288839bbc1b8523f7ec012f404bdaec'
SOURCE_FREEZE_SHA = 'e3786b74ac2292479780368531a99ebc097ec8df3c70629d8168a39ff75dfea7'
IMPORT_FREEZE = AIR / 'import-tooling-candidate-v001/Air48-import-tooling-freeze-v001.json'
IMPORT_FREEZE_SHA = '9121ac470908204ce67803d94556782f4ee3fd6db27ba3f356f46cd45ce777bc'
DODGE_PIXELS = ROOT / 'source-assets/production/fairytale-hero-state-gap-v001/dodge-native-observer-candidate-v001/tooling/verify-Dodge-source-pixels-v001.py'
DODGE_PIXELS_SHA = 'cee49fb96e9d6750a12c69babaeb9d1d2a87f4aae bd2048f7ff238b1db256727'.replace(' ', '')
AUDIO_CHECKER = AIR / 'audio-capture-helper-candidate-v001/tooling/check-native-main-submix-v001.py'
AUDIO_CHECKER_SHA = '39c32bd0d988107aa45f11dae91ca15db46fb1ca3c594e1903440065dceb8f46'


def need(value, why):
    if not value:
        raise ValueError(why)


def module(path, name, expected_sha=None):
    if expected_sha:
        need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected_sha, 'Frozen dependency changed: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def import_contract(freeze_path=IMPORT_FREEZE, expected_sha=IMPORT_FREEZE_SHA):
    freeze_path = Path(freeze_path)
    need(hashlib.sha256(freeze_path.read_bytes()).hexdigest() == expected_sha, 'Import tooling freeze changed')
    value = module(freeze_path.parent / 'air48_import_contract_v001.py', 'air48_frozen_contract')
    rows = value.read(freeze_path)['members']
    need(value.pin(value.__file__) in rows, 'Import contract not in actual tooling freeze')
    for row in rows:
        value.check(row)
    return value


def read(path):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'Duplicate JSON key')
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))


def finite(x):
    return type(x) in (int, float) and math.isfinite(x)


def uint(x, zero=False, bits=64):
    need(isinstance(x, str) and x.isascii() and x.isdecimal() and (x == '0' or not x.startswith('0')), 'Exact uint decimal string required')
    v = int(x)
    need((0 if zero else 1) <= v < 2 ** bits, 'Uint range')
    return v


def near(a, b, tol=1e-4):
    return finite(a) and finite(b) and abs(a - b) <= tol


def point(a, b, tol=1e-4):
    return isinstance(a, list) and len(a) == len(b) == 2 and all(near(x, y, tol) for x, y in zip(a, b))


def f32(x):
    need(finite(x), 'Finite float argument required')
    return struct.unpack('<f', struct.pack('<f', x))[0]


def file_under(directory, relative):
    need(isinstance(relative, str) and relative and '\\' not in relative and ':' not in relative
         and not relative.startswith('/') and all(x not in ('', '.', '..') for x in relative.split('/')), 'Evidence file path traversal')
    p = directory / Path(relative)
    need(p.resolve().is_relative_to(directory.resolve()) and not p.is_symlink(), 'Evidence path alias')
    for a in p.parents:
        if a == directory.parent:
            break
        need(not a.is_symlink(), 'Evidence parent alias')
    return p


def selection(h, v, age):
    need(all(finite(x) for x in (h, v, age)) and h >= 0, 'Finite physical sample')
    if h > 0 or v > 0:
        return 0 if v > 315 else 1 if v > 90 else 2 if v >= -90 else 3
    return (4 if age < f32(.06) else 5) if h == v == 0 and 0 <= age < f32(.12) else -1


def project(slot, source):
    x, y = slot['top']; w, h = slot['size']; u, v = slot['uv']; du, dv = slot['uv_size']
    px, py = slot['rotation_pivot']; qx = (source[0] / 512 - u) / du * w - px * w
    qy = (source[1] / 512 - v) / dv * h - py * h
    a = math.radians(slot['rotation']); co, si = math.cos(a), math.sin(a)
    return [x + px * w + co * qx - si * qy, y + py * h + si * qx + co * qy]


def frozen(value, c):
    p = c.check(value)
    f = read(p)
    rows = f.get('members', f.get('files'))
    need(isinstance(rows, list) and rows and len({r['path'] for r in rows}) == len(rows), 'Frozen members absent/duplicated')
    for repeat in range(2):
        for row in rows:
            c.check(row)
    return f


def strict203(suite):
    need(tuple(suite[k] for k in ('succeeded', 'succeededWithWarnings', 'failed', 'notRun', 'inProcess')) == (203, 0, 0, 0, 0), 'Actual full203 must all succeed without warnings')
    tests = suite['tests']
    need(len(tests) == 203 and len({t['fullTestPath'] for t in tests}) == 203, 'Exact203 unique registered tests')
    need(all(t['state'] == 'Success' and t['warnings'] == t['errors'] == 0
             and not any(e.get('event', {}).get('type') in ('Error', 'Warning') for e in t['entries']) for t in tests), 'Full suite per-test state/warning/error differs')


def prereg_header(p):
    need(p['schema'] == 'hero-Air6-Root-prereg-v001' and p['RootApproved'] is True and p['is_template'] is False
         and p['pre_registered_before_capture'] is True and p['FinalAccepted'] is False, 'Actual Root prereg required; template cannot pass')
    need(type(p['requested_facing']) is int and p['requested_facing'] in (-1, 1)
         and type(p['diagnostic_clear_knight']) is bool, 'Explicit side/diagnostic authorization required')


def source_only():
    c = import_contract(); directory = AIR / 'native-ready-candidate-v001'
    mp, fp = c.pin(directory / 'import-Air48-v001.json'), c.pin(directory / 'Air48-native-ready-freeze-v001.json')
    need(fp['sha256'] == SOURCE_FREEZE_SHA, 'Exact approved source49 freeze required')
    manifest, assets = c.load_prepared(mp, fp)
    profile_path = directory / 'Air-runtime-profile-data-v001.json'; profile = read(profile_path)
    need(profile['source_closure_digest'] == CLOSURE == manifest['source_closure_digest']
         and profile['import_manifest'] == mp and profile['Frames'] == read(c.check(manifest['source_closure']))['Frames'], 'Source49 typed profile closure differs')
    need([f['Root'] for f in profile['Frames']] == [[259, 457], [245, 500], [244, 530], [247, 449], [256, 464], [256, 464]], 'Approved virtual Root changed/clamped')
    return c, manifest, profile, mp, fp, c.pin(profile_path)


def preflight(prereg_path, checker_path):
    c = import_contract()
    prereg_path = c.resolve(prereg_path, within=ROOT)
    p = read(prereg_path)
    prereg_header(p)
    c, manifest, profile, mp, fp, pp = source_only()
    c = import_contract(c.check(p['import_tooling_freeze_pin']), p['import_tooling_freeze_pin']['sha256'])
    need(p['checker_pin'] == c.pin(checker_path) and p['source_manifest_pin'] == mp
         and p['source_freeze_pin'] == fp and p['prepared_profile_pin'] == pp, 'Root binds different checker/source/profile')
    checker_freeze = frozen(p['checker_freeze_pin'], c)
    need(p['checker_pin'] in checker_freeze.get('members', checker_freeze.get('files', []))
         and c.pin(__file__) in checker_freeze.get('members', checker_freeze.get('files', [])), 'Actual checker modules missing from freeze')
    for key in ('source_probe_freeze_pin', 'production_candidate_freeze_pin'):
        frozen(p[key], c)
    snapshot_path = c.check(p['compiled_manifest_pin']); snapshot = read(snapshot_path)
    need(snapshot['source_files'] == p['expected_source_files'] and type(p['expected_source_files']) is int
         and snapshot['production_files'] == p['expected_production_files'] == 1419, 'Actual compiled Source count/Production1419 required')
    suite = read(c.check(p['strict_full203_pin'])); strict203(suite)
    need(snapshot['full_suite'] == p['strict_full203_pin'], 'Compiled manifest binds different full203')
    rows = snapshot['files']; names = {r['path'] for r in rows}
    need(len(names) == len(rows), 'Duplicate compiled file membership')
    need('UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll' in names, 'Actual compiled game DLL pin required')
    for row in rows:
        c.check(row)
    for prefix, directory in (('UnrealGame/Source/', ROOT / 'UnrealGame/Source'),
                              ('UnrealGame/Content/Production/', ROOT / 'UnrealGame/Content/Production')):
        actual = {c.resolve(f, within=directory).relative_to(ROOT).as_posix() for f in directory.rglob('*') if f.is_file()}
        need(actual == {n for n in names if n.startswith(prefix)}, 'Actual compiled disk membership differs: ' + prefix)
        if prefix == 'UnrealGame/Source/':
            need(len(actual) == snapshot['source_files'], 'Actual Source membership count differs from compiled count')
    for key, fk in (('production_Source_admission_pin', 'production_candidate_freeze_pin'),
                    ('observer_Source_admission_pin', 'source_probe_freeze_pin')):
        admission = read(c.check(p[key]))
        need(admission['RootApproved'] is True and admission['is_template'] is False and admission['actual_applied'] is True
             and admission['candidate_freeze'] == p[fk] and admission['FinalAccepted'] is False, 'Actual scoped Source admission required')
        need(admission['after_files'] and all(r['path'] in names for r in admission['after_files']), 'Admitted Source paths not in compiled snapshot')
        source_freeze = read(c.check(p[fk]))
        candidate_rows = source_freeze.get('source_files')
        if not isinstance(candidate_rows, list):
            candidate_rows = source_freeze.get('members', source_freeze.get('files', []))
        for r in admission['after_files']:
            c.check(r)
            need(any(x == r for x in rows), 'Admitted actual Source pin differs from compiled file')
            need(any(Path(x['path']).name == Path(r['path']).name and (x['bytes'], x['sha256']) == (r['bytes'], r['sha256'])
                     for x in candidate_rows if isinstance(x, dict) and 'path' in x), 'Actual admitted Source bytes differ from frozen candidate')
    imported = c.load_import(c.check(p['import_manifest_pin']))
    receipt = read(c.check(p['import_native_receipt_pin'])); c.validate_receipt_assets(imported, receipt)
    need(receipt['success'] is True and receipt['actual_total'] == 1419 and receipt['manifest'] == p['import_manifest_pin'], 'Actual import48 receipt required')
    independent = read(c.check(p['import_independent_receipt_pin']))
    need(independent['schema'] == 'Air48-independent-saved-byte-twoSHA-v001' and independent['success'] is True
         and independent['manifest'] == p['import_manifest_pin'] and independent['native_receipt'] == p['import_native_receipt_pin']
         and independent['verification_passes'] == 2 and independent['actual_total'] == 1419
         and independent['old1371_exact_membership_unchanged_twice'] is True, 'Independent saved-byte receipt required')
    for repeat in range(2):
        c.verify_old(imported['old_production_files']); c.exact_membership(imported, True)
        for a in receipt['assets']:
            c.check(a['saved'])
    run_directory = c.resolve(p['root_run_directory'], within=ROOT)
    need(run_directory != ROOT and run_directory != LEAF, 'Exact future evidence leaf required')
    return c, p, manifest, profile, prereg_path, run_directory


def verify_draw(o, frame, profile, manifest, r):
    d = o['new_air_draw']; spec = profile['Frames'][frame]; side = r['requested_facing']
    root, grip, axis = spec['Root'], spec['Grip'], spec['AxisArtist']; scale = 72 / 416
    need(d['opt_in'] is True and d['drawn'] is True and d['atomic_preflight_ready'] is True and d['supported'] is True
         and d['missing_reason'] == '' and d['sample_valid'] is True, 'Air draw/query/preflight incomplete')
    need(d['frame'] == frame and d['pose'] == frame + 1 and d['facing'] == o['facing'] == side
         and d['sim'] == o['sim'] == d['sample_native_time'] and d['profile'] == profile['profile_id'], 'Physical selection/actual clock/profile mismatch')
    for k, want in (('sample_run', r['run']), ('binding_run', r['run']), ('sample_owner', r['owner']),
                    ('binding_owner', r['owner']), ('player_entity', r['owner']), ('sample_room', r['current_room']), ('sample_epoch', r['epoch'])):
        need(d[k] == want, 'Actual plan owner/run/currentroom/epoch differs: ' + k)
    need(d['sample_ground'] == o['ground'] and d['sample_H'] == o['jump_height'] == d['jump_height']
         and d['sample_V'] == o['vertical_velocity'] and d['sample_landing_age'] == o['landing_visual_age'], 'Plan is not raw actual sample')
    light = o['observed_air_transition_ordinal'] >= 2
    for field, want in (('weapon_instance', r['weapon_instance']), ('weapon_version', r['weapon_version']),
                        ('armor_instance', r['armor_instance'] if light else '0'), ('armor_version', r['armor_version'] if light else '0')):
        need(d[field] == o[field] == want, 'Committed gear instance/version differs')
    need(d['weapon_content'] == 'WPN-SWD-001' and d['armor_kind'] == (1 if light else 0)
         and d['armor_content'] == ('ARM-LGT-001' if light else ''), 'Actual NoArmor/Light binding differs')
    need(point(d['root_source'], root, 0) and point(d['grip_source'], grip, 0) and point(d['axis_artist'], axis, 0), 'Authored source points changed')
    need(d['ui_scale'] == 1 and near(d['canvas_size'], 512 * scale, 1e-10)
         and near(d['source_to_screen_scale'], scale, 1e-12) and d['weapon_scale'] == .5
         and near(d['weapon_width'], 512 * scale * .5, 1e-10), 'Original72/416/.50 geometry differs')
    ground = [f32(640. + (o['ground'][0] - o['camera_ground'][0]) * f32(.65)), f32(490. - o['ground'][1] * f32(.38))]
    need(point(d['context_ground'], ground, 0), 'Original .65f/.38f + Screen(float) registration differs')
    lifted = [ground[0], ground[1] - d['jump_height'] * .70]
    top = [lifted[0] - (root[0] if side > 0 else 512 - root[0]) * scale, lifted[1] - root[1] * scale]
    at = [lifted[0] + side * (grip[0] - root[0]) * scale, lifted[1] + (grip[1] - root[1]) * scale]
    theta = math.atan2(axis[1], axis[0]); angle = math.degrees(theta) * side
    pivot = [99 / 512 if side > 0 else 1 - 99 / 512, .5]
    need(point(d['body_top'], top) and point(d['grip_screen'], at)
         and point(d['sword_pivot_uv'], pivot, 1e-12) and near(d['weapon_angle'], angle, 1e-9)
         and d['texture_u'] == (0 if side > 0 else 1) and d['texture_du'] == side, 'One mirror/height/root/grip/axis/pivot differs')
    need(point(d['sword_top'], [at[k] - pivot[k] * d['weapon_width'] for k in range(2)]), 'Independent sword top differs')
    paths = {a['component']: a['object_path'] for a in manifest['assets'] if a['frame'] == frame}
    paths['IndependentSword'] = profile['independent_sword']['object_path']
    order = [(i, n) for i, n in enumerate(spec['SlotOrder']) if light or n not in ('Chest', 'ShoulderFar', 'ShoulderNear')]
    slots = d['slots']; expected = []
    need(d['slot_count'] == d['nonempty_count'] == len(slots) == len(order) == (9 if light else 6), 'None6/LGT9 enabled slot gaps/count differ')
    sword_slot = None
    for (i, name), s in zip(order, slots):
        sword = name == 'IndependentSword'; expected.append(paths[name])
        need(s['slot'] == i and s['component'] == COMPONENTS.index(name) and s['texture'] == paths[name]
             and s['drawn'] is True and s['texture_ready'] is True and s['known_empty'] is False, 'Actual source slot/path/order differs')
        need(s['trace_tint'] == d['tint'] == [1, 1, 1, 1] and s['draw_scale'] == 1 and s['scale_position'] is False
             and point(s['uv'], [d['texture_u'], 0], 0) and point(s['uv_size'], [d['texture_du'], 1], 0), 'Submitted tint/UV/scale differs')
        width = d['weapon_width'] if sword else d['canvas_size']; wanttop = d['sword_top'] if sword else d['body_top']
        need(point(s['top'], [f32(x) for x in wanttop], 0) and point(s['size'], [f32(width)] * 2, 0)
             and s['rotation'] == (f32(angle) if sword else 0)
             and point(s['rotation_pivot'], pivot if sword else [0, 0], 1e-12), 'Actual float DrawTexture arguments differ')
        if sword:
            sword_slot = s
        else:
            need(point(project(s, root), lifted, 2e-4) and point(project(s, grip), at, 2e-4), 'Actual float source-root/grip quad projection differs')
    for src in ([99, 256], [199, 256], [99, 356]):
        x, y = src[0] - 99, src[1] - 256
        want = [at[0] + side * .5 * scale * (math.cos(theta) * x - math.sin(theta) * y),
                at[1] + .5 * scale * (math.sin(theta) * x + math.cos(theta) * y)]
        need(point(project(sword_slot, src), want, 2e-4), 'Actual sword double mirror/registration differs')
    need(d['actual_stack'] == o['rendered_player_stack'] == o['old_draw']['actual_stack'] == expected, 'Actual renderer stacks differ')
    residents = d['resident_textures']; allpaths = {a['object_path'] for a in manifest['assets']} | {paths['IndependentSword']}
    need(d['resident_count'] == len(residents) == 49 and {x['texture'] for x in residents} == allpaths
         and all(x['class'] == 'Texture2D' and x['width'] == x['height'] == 512 and x['resource_ready'] is True
                 and x['pending_initialization'] is False for x in residents), 'Full49 residents must preflight even for NoArmor6')
    old = o['old_draw']
    need(old['active'] is True and old['supported'] is True and old['action_pose_supported'] is True
         and old['texture_ready'] is True and old['sword_drawn'] is True and old['armor_drawn'] is light
         and old['clip'] == 'sword_nonattack_air' and old['gear_placeholder'] is False, 'Old shared renderer does not report actual Air submission')
    need(old['draw_id'] == d['draw_id'] and old['sim'] == o['sim'] and old['frame'] == frame and old['facing'] == side
         and point(old['root_source'], root, 0) and point(old['grip_source'], grip, 0) and point(old['grip_screen'], at)
         and near(old['canvas_size'], d['canvas_size'], 1e-10) and old['body_texture'] == paths['BodyRest']
         and old['sword_texture'] == paths['IndependentSword'], 'Old shared record is stale or differs from submitted Air')


def verify_gpu(original, r, manifest, profile):
    rows = r['startup_actual_GPU_source_textures49']
    sources = {a['object_path']: (a['source'], a['frame'], COMPONENTS.index(a['component']), a['source_sha256'], a['source_RGBA_sha256']) for a in manifest['assets']}
    sword = profile['independent_sword']; sources[sword['object_path']] = (sword['source']['path'], -1, 8, sword['source']['sha256'], '')
    need(r['startup_readback_complete'] is True and len(rows) == 49 and {x['texture'] for x in rows} == set(sources), 'Actual unique49 startup textures required')
    timing = r['capture_timing']; first_input = min(x['wall_offset_s'] for x in r['normal_inputs']) + timing['capture_start_monotonic_s']
    stop = r['startup_readback_stop_monotonic_s']; need(finite(stop) and 0 < stop < timing['capture_start_monotonic_s'] <= first_input, 'Readback must finish before real audio origin/movie/input')
    files = set()
    for row in rows:
        path, frame, component, sha, rgba_sha = sources[row['texture']]
        need(row['class'] == 'Texture2D' and row['width'] == row['height'] == 512 and row['resource_ready'] is True
             and row['pending_initialization'] is False and row['sRGB'] is True and row['RHI_format'] in (2, 37)
             and row['frame'] == frame and row['component'] == component and row['source_SHA_metadata'] == sha
             and row['source_RGBA_SHA_metadata'] == rgba_sha and row['editor_source_format'] == 'TSF_BGRA8'
             and row['read_flags'] == 'RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy', 'Actual49 GPU/source mip format/metadata differs')
        need(finite(row['read_start_monotonic_s']) and finite(row['read_stop_monotonic_s'])
             and 0 < row['read_start_monotonic_s'] <= row['read_stop_monotonic_s'] <= stop, 'Actual RHI read time differs')
        with Image.open(path) as im:
            need(im.mode == 'RGBA' and im.size == (512, 512), 'Exact RGBA source required')
            expected = np.asarray(im).copy()
        for field, crcfield in (('GPU_file', 'GPU_BGRA8_CRC32'), ('editor_source_file', 'editor_source_BGRA8_CRC32')):
            need(row[field] not in files, 'Repeated raw readback file'); files.add(row[field])
            data = file_under(original, row[field]).read_bytes()
            need(len(data) == 512 * 512 * 4 and (zlib.crc32(data) & 0xffffffff) == row[crcfield], 'Original raw BGRA CRC/length differs')
            actual = np.frombuffer(data, dtype=np.uint8).reshape(512, 512, 4)[..., [2, 1, 0, 3]]
            need(np.array_equal(actual, expected), 'Actual GPU/editor mip bytes differ from exact PNG RGBA; metadata is not a substitute')
    actual_files = {p.relative_to(original).as_posix() for p in (original / 'texture-readback').glob('*.bin')}
    need(actual_files == files and len(files) == 98, 'Exact98 original readback bins required')
    return dict(actual49_GPU_and_editor_source_RGBA_byte_equal=True, actual_raw_bin_count=98)
