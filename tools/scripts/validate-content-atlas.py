"""Read-only PNG/manifest gate for SWD001 + LGT001 + STN001, profile v2.

This checks declared art data, never image quality, legal conclusions, gameplay
or engine readiness. It does not repair pixels, rewrite files or call services.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys

from PIL import Image


PROFILE = {
    'player': {
        'layers': {'body_far', 'armor', 'weapon', 'body_near'},
        'actions': {'idle', 'walk', 'jump', 'fall', 'land', 'dodge', 'hurt', 'death',
                    'primary_1', 'primary_2', 'primary_3', 'secondary', 'air_primary_1'},
        'timings': {'primary_1': (0.17, 0.12, 0.31), 'primary_2': (0.15, 0.12, 0.27),
                    'primary_3': (0.22, 0.12, 0.32), 'secondary': (0.20, 0.10, 0.38),
                    'air_primary_1': (0.17, 0.12, 0.31)},
    },
    'stone_knight': {
        'layers': {'body', 'shield'},
        'actions': {'dormant', 'wake', 'idle', 'walk', 'charge', 'shield_bash', 'recovery', 'hurt', 'death'},
        'timings': {'charge': (0.90, 0.80, 1.60), 'shield_bash': (0.70, 0.12, 0.90)},
    },
}
UNITS = {'WPN-SWD-001', 'ARM-LGT-001', 'ENM-STN-001'}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def point(value, canvas):
    return (isinstance(value, list) and len(value) == 2 and all(number(v) for v in value)
            and 0 <= value[0] <= canvas[0] and 0 <= value[1] <= canvas[1])


def validate_manifest(manifest_path, root=None):
    manifest_path = Path(manifest_path).resolve()
    root = Path(root).resolve() if root else manifest_path.parent
    result = {'manifest': str(manifest_path), 'root': str(root), 'passed': False,
              'engine_executed': False, 'runtime_status': 'not_evaluated',
              'scope': 'Declared first-unit-v2 PNG/data contract only; no visual review, gameplay or legal acceptance',
              'image_files_decoded': 0, 'frame_layer_records_checked': 0, 'errors': []}
    errors = result['errors']

    def error(code, location, message):
        errors.append({'code': code, 'location': location, 'message': message})

    try:
        data = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('Manifest root must be an object')
    except (OSError, ValueError) as exc:
        error('MANIFEST_READ', '$', str(exc))
        return result

    raw_cache, png_cache = {}, {}

    def file_bytes(relative, digest, location):
        if not isinstance(relative, str) or not relative:
            error('FILE_MISSING', location, 'A nonempty relative file path is required')
            return None, None
        path = (root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(root):
            error('PATH_OUTSIDE_ROOT', location, 'Only files within the explicit root are allowed')
            return None, None
        if not path.is_file():
            error('FILE_MISSING', location, relative)
            return None, None
        if path not in raw_cache:
            raw_cache[path] = path.read_bytes()
        raw = raw_cache[path]
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', digest):
            error('HASH_MISMATCH', location, 'A SHA256 hex digest is required')
        elif hashlib.sha256(raw).hexdigest() != digest.lower():
            error('HASH_MISMATCH', location, 'Actual file bytes differ from the declared SHA256')
        return path, raw

    def check_png(record, canvas, location):
        result['frame_layer_records_checked'] += 1
        if record.get('placeholder') is not False:
            error('PLACEHOLDER', location, 'A layer must explicitly declare placeholder=false')
        if record.get('baked_mirror_count') != 0 or record.get('runtime_mirror_count') != 0:
            error('MIRROR_CONTRACT', location, 'Layers stay canonical; only the parent facing transform mirrors')
        if record.get('provenance_id') not in provenance:
            error('PROVENANCE', location, 'Layer provenance_id does not resolve')
        path, raw = file_bytes(record.get('path'), record.get('sha256'), location)
        if raw is None:
            return
        if any(part.casefold() in ('prototype', 'placeholder', 'placeholders') for part in path.relative_to(root).parts):
            error('PLACEHOLDER', location, 'Known prototype/placeholder source folders cannot be relabelled as final layers')
        if path not in png_cache:
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    image.load()  # Decode real pixels; a filename/header is insufficient.
                    if image.format != 'PNG':
                        raise ValueError('Expected PNG bytes')
                    alpha = image.getchannel('A').getextrema() if image.mode == 'RGBA' else None
                    png_cache[path] = {'size': list(image.size), 'mode': image.mode,
                                       'rgba8': len(raw) > 25 and raw[24] == 8 and raw[25] == 6,
                                       'alpha': alpha}
                    result['image_files_decoded'] += 1
            except (OSError, ValueError) as exc:
                png_cache[path] = {'decode_error': str(exc)}
        info = png_cache[path]
        if 'decode_error' in info:
            error('PNG_DECODE', location, info['decode_error'])
            return
        if info['mode'] != 'RGBA' or not info['rgba8']:
            error('PNG_RGBA8', location, 'Actual PNG must be 8-bit RGBA')
        elif info['alpha'][0] != 0 or info['alpha'][1] == 0:
            error('PNG_ALPHA', location, 'Require real transparent pixels and nonempty visible content')
        if info['size'] != canvas:
            error('CANVAS_MISMATCH', location, 'Actual PNG dimensions differ from the actor logical canvas')

    if data.get('schema_version') != 1 or data.get('profile') != 'first-unit-v2':
        error('SCHEMA', '$', 'Expected schema_version=1, profile=first-unit-v2')
    if data.get('status') != 'production_candidate':
        error('STATUS', '$/status', 'Templates and prototypes cannot pass the formal art-data gate')
    if data.get('placeholder') is not False:
        error('PLACEHOLDER', '$/placeholder', 'An explicit non-placeholder declaration is required')
    units = data.get('units')
    if (not isinstance(units, list) or not all(isinstance(unit, str) for unit in units)
            or set(units) != UNITS or len(units) != 3):
        error('UNITS', '$/units', 'This small profile covers precisely SWD001, LGT001 and STN001')

    provenance = data.get('provenance', {})
    if not isinstance(provenance, dict):
        error('PROVENANCE', '$/provenance', 'Expected an object keyed by source ID')
        provenance = {}
    for source_id, source in provenance.items():
        location = '$/provenance/' + source_id
        if not isinstance(source, dict):
            error('PROVENANCE', location, 'Expected a source record')
            continue
        license_name = source.get('license', '')
        if not isinstance(license_name, str) or license_name.lower() in ('', 'unknown', 'unverified', 'todo', 'placeholder'):
            error('LICENSE', location, 'A named license/authorization basis is required')
        if source.get('origin') not in ('original', 'third_party', 'derived', 'generated'):
            error('PROVENANCE', location, 'Expected a named source origin, not a prototype placeholder')
        if source.get('origin') == 'generated':
            if not all(isinstance(source.get(key), str) and source[key].strip() for key in ('provider', 'model', 'prompt_path', 'prompt_sha256')):
                error('PROVENANCE_GENERATION', location, 'Generated art requires actual backend/model and retained prompt provenance')
            file_bytes(source.get('prompt_path'), source.get('prompt_sha256'), location + '/prompt')
        file_bytes(source.get('source_path'), source.get('source_sha256'), location + '/source')
        file_bytes(source.get('license_evidence_path'), source.get('license_evidence_sha256'), location + '/license_evidence')

    actors = data.get('actors', [])
    if not isinstance(actors, list):
        error('SCHEMA', '$/actors', 'Expected a list')
        actors = []
    roles = [actor.get('role') for actor in actors if isinstance(actor, dict)]
    if set(roles) != set(PROFILE) or len(roles) != 2:
        error('MISSING_ACTOR', '$/actors', 'Require one player and one stone_knight')
    for actor in actors:
        if not isinstance(actor, dict) or actor.get('role') not in PROFILE:
            error('SCHEMA', '$/actors', 'Unknown or malformed actor')
            continue
        role = actor['role']
        spec = PROFILE[role]
        location = '$/actors/' + role
        canvas = actor.get('canvas_px')
        if not (isinstance(canvas, list) and len(canvas) == 2 and
                all(isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 4096 for v in canvas)):
            error('CANVAS_MISMATCH', location, 'Canvas requires two positive integer dimensions <=4096')
            canvas = [0, 0]
        pivot = actor.get('ground_pivot_px')
        if not point(pivot, canvas):
            error('PIVOT_MISMATCH', location, 'A finite ground pivot within the canvas is required')
        layers = actor.get('required_layers', [])
        if not isinstance(layers, list) or not all(isinstance(v, str) for v in layers):
            error('LAYER_SET', location, 'required_layers must be named layers')
            layers = []
        if not spec['layers'].issubset(set(layers)) or len(set(layers)) != len(layers):
            error('LAYER_SET', location, 'Required body/equipment layers are missing or duplicated')
        facings = actor.get('facings', {})
        for facing, mirror in (('right', 0), ('left', 1)):
            if not isinstance(facings, dict) or facing not in facings:
                error('FACING_MISSING', location, 'Both right and left must resolve')
            elif facings[facing] != {'source_facing': 'right', 'baked_mirror_count': 0, 'runtime_mirror_count': mirror}:
                error('MIRROR_CONTRACT', location + '/facings/' + facing, 'Canonical right assets mirror once for left')
        if role == 'player':
            compatible = (actor.get('weapon_id') == 'WPN-SWD-001' and actor.get('armor_id') == 'ARM-LGT-001'
                          and isinstance(actor.get('weapon_compatible_armors'), list)
                          and 'ARM-LGT-001' in actor['weapon_compatible_armors']
                          and isinstance(actor.get('armor_compatible_weapons'), list)
                          and 'WPN-SWD-001' in actor['armor_compatible_weapons'])
            if not compatible:
                error('EQUIPMENT_COMPATIBILITY', location, 'Weapon and armor must mutually permit this pair')
        elif actor.get('enemy_id') != 'ENM-STN-001':
            error('UNITS', location, 'Expected ENM-STN-001')

        actions = actor.get('actions', [])
        if not isinstance(actions, list):
            actions = []
        action_ids = [action.get('id') for action in actions if isinstance(action, dict)]
        if not spec['actions'].issubset(set(action_ids)):
            error('MISSING_ACTION', location, 'Missing required actions: ' + ', '.join(sorted(spec['actions'] - set(action_ids))))
        if len(set(action_ids)) != len(action_ids):
            error('MISSING_ACTION', location, 'Action IDs must be unique')
        for action in actions:
            if not isinstance(action, dict):
                error('SCHEMA', location, 'Malformed action')
                continue
            name = action.get('id', '')
            action_location = location + '/actions/' + str(name)
            if action.get('geometry_kind') not in ('none', 'melee', 'body', 'emission'):
                error('SCHEMA', action_location, 'geometry_kind must be none, melee, body or emission')
            duration = action.get('duration_s')
            if not number(duration) or duration <= 0:
                error('PHASE_TIMELINE', action_location, 'A positive absolute duration is required')
                duration = 0.0
            phases = action.get('phases', [])
            if not isinstance(phases, list):
                phases = []
            cursor, measured = 0.0, []
            if not phases:
                error('PHASE_TIMELINE', action_location, 'Phases must cover the complete action')
            for phase in phases:
                if not isinstance(phase, dict):
                    error('PHASE_TIMELINE', action_location, 'Malformed phase')
                    continue
                start, end = phase.get('start_s'), phase.get('end_s')
                if not number(start) or not number(end) or abs(start - cursor) > 1e-6 or end <= start:
                    error('PHASE_TIMELINE', action_location, 'Phase times must be contiguous absolute seconds, without resetting')
                    continue
                measured.append(end - start)
                cursor = end
            if abs(cursor - duration) > 1e-6:
                error('PHASE_TIMELINE', action_location, 'Final phase must end at duration_s')
            if name in spec['timings']:
                expected = spec['timings'][name]
                if ([phase.get('id') for phase in phases if isinstance(phase, dict)] != ['windup', 'active', 'recovery']
                        or len(measured) != 3 or any(abs(a-b) > 1e-6 for a, b in zip(measured, expected))):
                    error('SOURCE_TIMING', action_location, 'Combat phases differ from the frozen first-unit-v2 source times')

            frames = action.get('frames', [])
            if not isinstance(frames, list):
                frames = []
            count = action.get('frame_count')
            if not isinstance(count, int) or isinstance(count, bool) or count < 1 or len(frames) != count:
                error('FRAME_COUNT', action_location, 'All declared frames must be present')
            if name in spec['timings']:
                for phase in phases:
                    if (isinstance(phase, dict) and number(phase.get('start_s')) and number(phase.get('end_s'))
                            and not any(isinstance(frame, dict) and number(frame.get('time_s'))
                                        and phase['start_s'] - 1e-6 <= frame['time_s'] < phase['end_s'] - 1e-6
                                        for frame in frames)):
                        error('FRAME_PHASE_COVERAGE', action_location, 'Every combat phase requires an actual frame sample')
            previous_time = -1.0
            for index, frame in enumerate(frames):
                frame_location = action_location + '/frames/' + str(index)
                if not isinstance(frame, dict):
                    error('FRAME_COUNT', frame_location, 'Malformed frame')
                    continue
                if frame.get('index') != index:
                    error('FRAME_COUNT', frame_location, 'Frame indices must be continuous from zero')
                time = frame.get('time_s')
                if not number(time) or not 0 <= time <= duration or time <= previous_time or (index == 0 and time != 0):
                    error('FRAME_TIME', frame_location, 'Frame times are absolute, strictly increasing, starting at zero')
                if number(time):
                    previous_time = time
                if frame.get('canvas_px') != canvas:
                    error('CANVAS_MISMATCH', frame_location, 'Frame logical canvas differs')
                if frame.get('ground_pivot_px') != pivot:
                    error('PIVOT_MISMATCH', frame_location, 'Ground pivot drift is forbidden')
                markers = frame.get('markers_px', {})
                if not isinstance(markers, dict):
                    markers = {}
                required = {'ground_root', 'shield_contact'} if role == 'stone_knight' else {'ground_root', 'hand_near', 'grip_primary', 'weapon_tip'}
                if action.get('geometry_kind') == 'emission':
                    required.add('emitter_primary')
                for marker in required:
                    if marker not in markers:
                        error('MARKER_MISSING', frame_location, marker)
                    elif not point(markers[marker], canvas):
                        error('MARKER_POSITION', frame_location, 'Marker must be finite and inside the logical canvas: ' + marker)
                if markers.get('ground_root') != pivot:
                    error('PIVOT_MISMATCH', frame_location, 'ground_root must match the stable actor pivot')
                if role == 'player' and point(markers.get('hand_near'), canvas) and point(markers.get('grip_primary'), canvas):
                    if math.dist(markers['hand_near'], markers['grip_primary']) > 1.0:
                        error('GRIP_ALIGNMENT', frame_location, 'Primary grip must meet the near hand within one source pixel')
                frame_layers = frame.get('layers', {})
                if not isinstance(frame_layers, dict):
                    frame_layers = {}
                if set(frame_layers) != set(layers):
                    error('LAYER_SET', frame_location, 'Every frame must contain the complete declared layer set')
                for layer_name, record in frame_layers.items():
                    if not isinstance(record, dict):
                        error('LAYER_SET', frame_location, 'Malformed layer record')
                    else:
                        check_png(record, canvas, frame_location + '/layers/' + layer_name)
    result['passed'] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path, help='All source/evidence paths are relative to this root; default manifest directory')
    args = parser.parse_args()
    report = validate_manifest(args.manifest, args.root)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
