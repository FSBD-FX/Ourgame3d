"""UE-only isolated whole-import comparison for the two prepared characters.

Execute with UE -ExecutePythonScript or py "F:/Ourgame/tools/scripts/ue-diagnose-character-axis.py".
Imports the original FBX with mesh + animation together at 60 FPS, new skeletons,
into /Game/Tests/Preparation/AxisDiagnostic/HumanFresh and OrcFresh.
For a new whole-import comparison without overwriting history, set
CODEX_CHARACTER_AXIS_FRESH_SUFFIX=FreshV2 (letters and digits only).
CODEX_CHARACTER_AXIS_REPAIR=1 selects the separate gated animation-only repair;
that mode can modify canonical animations only with APPLY_CANONICAL and backup.
Never deletes/replaces the canonical characters or edits a level. Existing
diagnostic folders are inspected, not overwritten. No standalone Python import
claim is made; the report is written only inside a real UE process.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import os
import re
import runpy
import traceback


def transform_record(value):
    location, rotation, scale = value.translation, value.rotation, value.scale3d
    return {
        'translation_cm': [float(location.x), float(location.y), float(location.z)],
        'rotation_quaternion_xyzw': [float(rotation.x), float(rotation.y), float(rotation.z), float(rotation.w)],
        'scale_xyz': [float(scale.x), float(scale.y), float(scale.z)],
    }


def import_data_record(obj):
    data = obj.get_editor_property('asset_import_data')
    out = {'class': data.get_class().get_name() if data else None, 'properties': {}, 'unavailable_properties': {}}
    for name in ('convert_scene', 'convert_scene_unit', 'force_front_x_axis', 'import_uniform_scale', 'import_rotation', 'import_translation', 'preserve_local_transform', 'use_default_sample_rate', 'custom_sample_rate', 'source_animation_name'):
        try:
            value = data.get_editor_property(name)
            if name == 'import_rotation':
                value = {'pitch': float(value.pitch), 'yaw': float(value.yaw), 'roll': float(value.roll)}
            elif name == 'import_translation':
                value = [float(value.x), float(value.y), float(value.z)]
            out['properties'][name] = value
        except Exception as exc:
            out['unavailable_properties'][name] = str(exc)
    return out


def diagnose_pose(unreal, label, folder, mesh_name, animation_folder=None):
    out = {'label': label, 'folder': folder, 'mesh_name': mesh_name, 'samples': [], 'errors': []}
    try:
        mesh = unreal.EditorAssetLibrary.load_asset(folder + '/' + mesh_name)
        if not isinstance(mesh, unreal.SkeletalMesh):
            raise ValueError('Expected SkeletalMesh was not found')
        skeleton = mesh.get_editor_property('skeleton')
        out['mesh_path'] = mesh.get_path_name()
        out['skeleton_path'] = skeleton.get_path_name()
        out['mesh_import_data'] = import_data_record(mesh)
        reference = unreal.AnimPoseExtensions.get_reference_pose(skeleton)
        names = [str(name) for name in unreal.AnimPoseExtensions.get_bone_names(reference)]
        selected = list(dict.fromkeys(names[:3] + [name for name in names if name.lower() in ('root', 'torso', 'head')]))
        out['bone_names'] = names
        out['selected_bones'] = selected

        def sample_pose(pose, sample):
            sample['valid_pose'] = bool(unreal.AnimPoseExtensions.is_valid(pose))
            if not sample['valid_pose']:
                raise ValueError('Invalid AnimPose')
            sample['bones'] = {}
            for name in selected:
                sample['bones'][name] = {
                    'local': transform_record(unreal.AnimPoseExtensions.get_bone_pose(pose, name, unreal.AnimPoseSpaces.LOCAL)),
                    'component': transform_record(unreal.AnimPoseExtensions.get_bone_pose(pose, name, unreal.AnimPoseSpaces.WORLD)),
                }
            return sample

        out['reference_pose'] = sample_pose(reference, {})
        options = unreal.AnimPoseEvaluationOptions()
        options.set_editor_property('should_retarget', False)
        options.set_editor_property('extract_root_motion', False)
        options.set_editor_property('incorporate_root_motion_into_pose', False)
        options.set_editor_property('optional_skeletal_mesh', mesh)
        for take in ('idle', 'attack-melee-right', 'attack-melee-left'):
            animation_path = (animation_folder or folder) + '/' + mesh_name + '_Anim_' + take
            try:
                animation = unreal.EditorAssetLibrary.load_asset(animation_path)
                if not isinstance(animation, unreal.AnimSequence):
                    raise ValueError('Expected AnimSequence was not found: ' + animation_path)
                duration = float(animation.get_editor_property('sequence_length'))
                data = import_data_record(animation)
                for time in (0.0, duration / 2):
                    pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(animation, time, options)
                    out['samples'].append(sample_pose(pose, {'take': take, 'animation_path': animation.get_path_name(), 'time_seconds': time, 'sequence_length_seconds': duration, 'animation_import_data': data}))
            except Exception as exc:
                out['errors'].append(str(exc))
        out['status'] = 'pose_samples_recorded' if not out['errors'] else 'pose_samples_partial'
    except Exception as exc:
        out['status'] = 'failed_pose_diagnostic'
        out['errors'].append(str(exc))
        out['traceback'] = traceback.format_exc()
    return out


def pose_alignment_gate(diagnostic):
    """Compare actual root rotations against the measured reference pose."""
    out = {'passed': False, 'root_angle_tolerance_degrees': 0.1, 'samples': [], 'errors': []}
    if diagnostic.get('status') != 'pose_samples_recorded' or len(diagnostic.get('samples', [])) != 6:
        out['errors'].append('Expected all six idle/melee pose samples to be recorded')
        return out
    reference = diagnostic['reference_pose']['bones']['root']['local']['rotation_quaternion_xyzw']
    for sample in diagnostic['samples']:
        actual = sample['bones']['root']['local']['rotation_quaternion_xyzw']
        dot = abs(sum(a * b for a, b in zip(reference, actual)))
        dot /= math.sqrt(sum(value * value for value in reference) * sum(value * value for value in actual))
        angle = math.degrees(2 * math.acos(min(1.0, dot)))
        head_height = sample['bones']['head']['component']['translation_cm'][2]
        passed = angle <= 0.1 and head_height > 10.0
        out['samples'].append({'take': sample['take'], 'time_seconds': sample['time_seconds'], 'root_reference_rotation_delta_degrees': angle, 'head_component_height_cm': head_height, 'passed': passed})
    out['passed'] = all(sample['passed'] for sample in out['samples'])
    return out


def run_axis_repair():
    """First prove an isolated animation import, then optionally repair canonical."""
    import unreal
    shared = runpy.run_path(str(Path(__file__).with_name('ue-import-prepared-assets.py')), run_name='asset_intake_library')
    shared['plan'].__globals__['ONLY_TASK_IDS'] = ()
    entries = [entry for entry in shared['plan']() if entry['id'] in ('human', 'orc')]
    saved = Path(unreal.Paths.project_saved_dir()).resolve() / 'Bootstrap'
    saved.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    path = saved / 'character-axis-repair-report.json'
    if path.is_file():
        (saved / ('character-axis-repair-report-before-' + run_id + '.json')).write_bytes(path.read_bytes())
    apply_canonical = os.environ.get('CODEX_CHARACTER_AXIS_APPLY_CANONICAL', '0') == '1'
    backup = os.environ.get('CODEX_CHARACTER_AXIS_BACKUP', '')
    report = {
        'schema_version': 1, 'run_id_utc': run_id, 'engine_executed': True,
        'engine_version': unreal.SystemLibrary.get_engine_version(),
        'script_path': str(Path(__file__).resolve()), 'status': 'running',
        'animation_import_rotation_degrees': {'pitch': 0.0, 'yaw': 0.0, 'roll': 90.0},
        'correction_basis': 'Measured original/fresh reference root is quaternion (-0.7071,0,0,0.7071); uncorrected animated root is identity. The first isolated roll=-90 import produced the opposite quaternion and was rejected by the 180-degree gate. Use roll=+90 in Unreal import options, then verify the actual quaternion rather than inferring its sign. Mesh and actor remain unchanged.',
        'mesh_modified': False, 'actor_or_level_modified': False,
        'apply_canonical_requested': apply_canonical, 'canonical_assets_modified': False,
        'canonical_backup_path': backup, 'aligned_entries': [], 'canonical_entries': [],
        'scope': 'Root/reference alignment at six selected pose samples, actual animation objects, and source-name correspondence. PIE rendering and animation behavior are verified separately.',
    }

    def write():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def import_animation_set(entry, destination, replace):
        result = dict(entry, destination_path=destination, errors=[], objects=[])
        result.update(shared['check_source'](entry))
        mesh = unreal.EditorAssetLibrary.load_asset(entry['destination_path'] + '/' + entry['destination_name'])
        if not isinstance(mesh, unreal.SkeletalMesh):
            raise ValueError('Canonical mesh missing for animation-only axis comparison')
        skeleton = mesh.get_editor_property('skeleton')
        result['skeleton_path'] = skeleton.get_path_name()
        existing = shared['inspect_folder'](unreal, destination)
        if existing and not replace:
            result['operation'] = 'inspect_existing_aligned_not_reimported'
        else:
            # Existing animation import metadata otherwise retains its previous
            # settings even when raw data is replaced by ImportAnimations.
            result['existing_animation_import_settings_updated'] = 0
            for obj in existing:
                if isinstance(obj, unreal.AnimSequence):
                    data = obj.get_editor_property('asset_import_data')
                    if isinstance(data, unreal.FbxAnimSequenceImportData):
                        data.set_editor_property('use_default_sample_rate', False)
                        data.set_editor_property('custom_sample_rate', 60)
                        data.set_editor_property('import_rotation', unreal.Rotator(pitch=0.0, yaw=0.0, roll=90.0))
                        result['existing_animation_import_settings_updated'] += 1
            options = shared['fbx_options'](unreal, 'animation', skeleton)
            options.get_editor_property('anim_sequence_import_data').set_editor_property('import_rotation', unreal.Rotator(pitch=0.0, yaw=0.0, roll=90.0))
            task = unreal.AssetImportTask()
            for name, value in {
                'filename': entry['source'], 'destination_path': destination,
                'destination_name': entry['destination_name'] + '_Anim',
                'automated': True, 'async_': False, 'replace_existing': replace,
                'replace_existing_settings': replace, 'save': True,
                'factory': unreal.FbxFactory(), 'options': options,
            }.items():
                task.set_editor_property(name, value)
            asset_tools.import_asset_tasks([task])
            result['operation'] = 'animation_only_root_axis_correction'
            result['task_imported_object_paths'] = list(task.get_editor_property('imported_object_paths'))
        clips = [obj for obj in shared['inspect_folder'](unreal, destination) if isinstance(obj, unreal.AnimSequence)]
        for obj in clips:
            record = shared['inspect_object'](unreal, obj)
            record['save_returned_true'] = bool(unreal.EditorAssetLibrary.save_loaded_asset(obj, only_if_is_dirty=False))
            record['import_data'] = import_data_record(obj)
            result['objects'].append(record)
        prefix = entry['destination_name'] + '_Anim_'
        actual_names = [obj.get_name().removeprefix(prefix) for obj in clips]
        source_names = shared['audited_animation_names'](entry)
        result['source_take_names'] = source_names
        result['actual_take_names'] = actual_names
        result['actual_anim_sequence_count'] = len(clips)
        result['source_take_names_without_observed_sequence'] = sorted(set(source_names) - set(actual_names))
        result['pose_diagnostic'] = diagnose_pose(unreal, entry['id'] + '_aligned', entry['destination_path'], entry['destination_name'], destination)
        result['alignment_gate'] = pose_alignment_gate(result['pose_diagnostic'])
        result['passed'] = (len(clips) == len(source_names) and not result['source_take_names_without_observed_sequence']
                            and result['alignment_gate']['passed']
                            and all(obj['save_returned_true'] and obj.get('skeleton_path') == result['skeleton_path'] for obj in result['objects']))
        return result

    variable = 'Interchange.FeatureFlags.Import.FBX'
    previous = None
    write()
    try:
        previous = bool(unreal.SystemLibrary.get_console_variable_bool_value(variable))
        report['interchange_fbx_enabled_before'] = previous
        unreal.SystemLibrary.execute_console_command(None, variable + ' False')
        if unreal.SystemLibrary.get_console_variable_bool_value(variable):
            raise RuntimeError('Could not select legacy FBX importer')
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        for entry in entries:
            destination = '/Game/Tests/Preparation/AxisDiagnostic/' + entry['id'].capitalize() + 'AlignedV2'
            report['aligned_entries'].append(import_animation_set(entry, destination, False))
            write()
        report['isolated_alignment_passed'] = all(entry['passed'] for entry in report['aligned_entries'])
        if not report['isolated_alignment_passed']:
            report['status'] = 'failed_isolated_alignment_gate_canonical_not_modified'
        elif not apply_canonical:
            report['status'] = 'isolated_alignment_passed_canonical_not_requested'
        else:
            backup_root = Path(backup)
            expected = [backup_root / 'Human/SK_Human.uasset', backup_root / 'Orc/SK_Orc.uasset']
            backup_ready = bool(backup) and all(file.is_file() and file.stat().st_size for file in expected) and len(list(backup_root.rglob('*attack-melee*.uasset'))) >= 4
            report['canonical_backup_verified'] = backup_ready
            if not backup_ready:
                raise ValueError('Canonical repair requires a verified backup containing Human/Orc meshes and four melee assets')
            report['canonical_assets_modified'] = True
            for entry in entries:
                report['canonical_entries'].append(import_animation_set(entry, entry['destination_path'], True))
                write()
            report['canonical_alignment_passed'] = all(entry['passed'] for entry in report['canonical_entries'])
            report['status'] = 'canonical_root_alignment_passed_pose_samples' if report['canonical_alignment_passed'] else 'failed_canonical_alignment_gate'
    except Exception as exc:
        report['status'] = 'fatal_script_exception'
        report['error'] = str(exc)
        report['traceback'] = traceback.format_exc()
        unreal.log_error(report['traceback'])
    finally:
        if previous is not None:
            unreal.SystemLibrary.execute_console_command(None, variable + (' True' if previous else ' False'))
            report['interchange_fbx_enabled_after_restore'] = bool(unreal.SystemLibrary.get_console_variable_bool_value(variable))
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        write()
        (saved / ('character-axis-repair-report-' + run_id + '.json')).write_bytes(path.read_bytes())
        unreal.log('Character root axis correction report: ' + str(path))
    return report


def run():
    import unreal
    shared = runpy.run_path(str(Path(__file__).with_name('ue-import-prepared-assets.py')), run_name='asset_intake_library')
    # Ensure inherited repair-run process variables cannot turn this into a
    # reimport. Function globals are explicit because runpy returns a namespace.
    shared['execute_item'].__globals__['REPLACE_EXISTING'] = False
    shared['plan'].__globals__['ONLY_TASK_IDS'] = ()
    fresh_suffix = os.environ.get('CODEX_CHARACTER_AXIS_FRESH_SUFFIX', 'Fresh')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{0,31}', fresh_suffix):
        raise ValueError('Fresh suffix must be 1-32 letters/digits, starting with a letter')
    selected = []
    for entry in shared['plan']():
        if entry['id'] in ('human', 'orc'):
            entry = dict(entry)
            role = entry['id'].capitalize()
            entry['destination_path'] = '/Game/Tests/Preparation/AxisDiagnostic/' + role + fresh_suffix
            entry['destination_name'] = 'SK_' + role + fresh_suffix
            selected.append(entry)
    saved = Path(unreal.Paths.project_saved_dir()).resolve() / 'Bootstrap'
    saved.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    path = saved / 'character-axis-diagnostic-report.json'
    if path.is_file():
        (saved / ('character-axis-diagnostic-report-before-' + run_id + '.json')).write_bytes(path.read_bytes())
    report = {
        'schema_version': 1, 'run_id_utc': run_id, 'engine_executed': True,
        'engine_version': unreal.SystemLibrary.get_engine_version(),
        'script_path': str(Path(__file__).resolve()),
        'status': 'running', 'entries': [],
        'scope': 'Fresh mesh+animation whole import only. Pose/bone/PIE comparison belongs to the separate editor verification report; object creation alone does not validate the animation axis.',
        'canonical_assets_modified': False, 'level_modified': False,
        'replace_existing': False, 'fresh_suffix': fresh_suffix,
    }

    def write():
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    variable = 'Interchange.FeatureFlags.Import.FBX'
    previous = None
    write()
    try:
        previous = bool(unreal.SystemLibrary.get_console_variable_bool_value(variable))
        report['interchange_fbx_enabled_before'] = previous
        unreal.SystemLibrary.execute_console_command(None, variable + ' False')
        report['interchange_fbx_enabled_during_import'] = bool(unreal.SystemLibrary.get_console_variable_bool_value(variable))
        if report['interchange_fbx_enabled_during_import']:
            raise RuntimeError('Could not select legacy FBX importer')
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        for entry in selected:
            report['currently_importing'] = entry['id']
            write()
            report['entries'].append(shared['execute_item'](unreal, asset_tools, entry))
            write()
        report['currently_importing'] = None
        report['bone_diagnostics'] = []
        for role in ('Human', 'Orc'):
            report['bone_diagnostics'].append(diagnose_pose(unreal, role + '_canonical', '/Game/ThirdParty/Kenney/MiniDungeon/' + role, 'SK_' + role))
            report['bone_diagnostics'].append(diagnose_pose(unreal, role + '_fresh_whole_import', '/Game/Tests/Preparation/AxisDiagnostic/' + role + fresh_suffix, 'SK_' + role + fresh_suffix))
            write()
        report['pose_alignment_gates'] = {item['label']: pose_alignment_gate(item) for item in report['bone_diagnostics']}
        report['fresh_pose_alignment_passed'] = all(gate['passed'] for label, gate in report['pose_alignment_gates'].items() if label.endswith('_fresh_whole_import'))
        failed = [entry['id'] for entry in report['entries'] if entry['status'].startswith('failed')]
        report['status'] = 'completed_with_failures' if failed or not report['fresh_pose_alignment_passed'] else 'whole_import_and_selected_pose_alignment_passed'
        report['summary'] = {
            'failed_task_ids': failed,
            'actual_observed_object_count': sum(len(entry['objects']) for entry in report['entries']),
            'actual_observed_anim_sequences': {entry['id']: entry.get('actual_anim_sequence_count_in_item_folder') for entry in report['entries']},
        }
    except Exception as exc:
        report['status'] = 'fatal_script_exception'
        report['error'] = str(exc)
        report['traceback'] = traceback.format_exc()
        unreal.log_error(report['traceback'])
    finally:
        if previous is not None:
            unreal.SystemLibrary.execute_console_command(None, variable + (' True' if previous else ' False'))
            report['interchange_fbx_enabled_after_restore'] = bool(unreal.SystemLibrary.get_console_variable_bool_value(variable))
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        write()
        (saved / ('character-axis-diagnostic-report-' + run_id + '.json')).write_bytes(path.read_bytes())
        unreal.log('Character axis whole-import diagnostic report: ' + str(path))
    return report


if __name__ == '__main__':
    run_axis_repair() if os.environ.get('CODEX_CHARACTER_AXIS_REPAIR', '0') == '1' else run()
