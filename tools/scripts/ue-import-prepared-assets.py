"""Import a small, traceable source set inside the Unreal Engine 5.5 editor.

Execute in UE (Python Editor Script Plugin must be enabled):
    py "F:/Ourgame/tools/scripts/ue-import-prepared-assets.py"
or pass -ExecutePythonScript="F:/Ourgame/tools/scripts/ue-import-prepared-assets.py"
to the editor. Ordinary Python --preflight only checks source files; it does not
import unreal, edit a project, or create an engine import report.

Default reruns inspect existing per-item folders instead of overwriting assets.
Set CODEX_ASSET_IMPORT_REPLACE=1 in the editor's process environment to reimport.
Set CODEX_ASSET_IMPORT_ONLY=human,orc to limit a repair run to those source tasks.
Mini Dungeon animation imports use the measured +90 degree roll correction;
skeletal mesh imports keep zero rotation. Actual selected poses are checked by
the companion ue-diagnose-character-axis.py, which must stay beside this file.
No network requests, retargeting, level edits, or original-source writes occur.

API references (Epic, application_version=5.5):
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AssetImportTask?application_version=5.5
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxImportUI?application_version=5.5
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxStaticMeshImportData?application_version=5.5
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxSkeletalMeshImportData?application_version=5.5
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxAnimSequenceImportData?application_version=5.5
https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-audio-files?application_version=5.5
"""
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
import hashlib
import json
import os
import runpy
import sys
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPARED = PROJECT_ROOT / 'source-assets/third-party/preparation-2026-10-10-v1'
EXISTING = PROJECT_ROOT / 'source-assets/third-party/kenney/2026-10-10'
PROBE_FOLDER = PROJECT_ROOT / 'source-assets/blender-mcp-smoke/2026-10-10_092600'
DESTINATION_ROOT = '/Game/ThirdParty'
REPLACE_EXISTING = os.environ.get('CODEX_ASSET_IMPORT_REPLACE', '0') == '1'
ONLY_TASK_IDS = tuple(value.strip() for value in os.environ.get('CODEX_ASSET_IMPORT_ONLY', '').split(',') if value.strip())


def acquisition_source_path(recorded_path):
    """Map the preserved acquisition root at read time, without rewriting it."""
    try:
        relative = PureWindowsPath(recorded_path).relative_to(PureWindowsPath('E:/codex_game'))
    except ValueError:
        return Path(recorded_path).resolve()
    return PROJECT_ROOT.joinpath(*relative.parts).resolve()


def plan():
    mini = PREPARED / 'kenney-mini-dungeon/extracted/Models/FBX format'
    dungeon = PREPARED / 'kenney-modular-dungeon-kit/extracted/Models/FBX format'
    rpg = PREPARED / 'kenney-rpg-audio/extracted/Audio'
    entries = [
        ('dungeon_room', dungeon / 'room-small.fbx', 'Kenney/ModularDungeon/RoomSmall', 'SM_RoomSmall', 'static', 'StaticMesh'),
        ('dungeon_floor', dungeon / 'template-floor.fbx', 'Kenney/ModularDungeon/Floor', 'SM_Floor', 'static', 'StaticMesh'),
        ('sword', mini / 'weapon-sword.fbx', 'Kenney/MiniDungeon/Sword', 'SM_Sword', 'static', 'StaticMesh'),
        ('coin', mini / 'coin.fbx', 'Kenney/MiniDungeon/Coin', 'SM_Coin', 'static', 'StaticMesh'),
        ('chest', mini / 'chest.fbx', 'Kenney/MiniDungeon/Chest', 'SM_Chest', 'static', 'StaticMesh'),
        ('human', mini / 'character-human.fbx', 'Kenney/MiniDungeon/Human', 'SK_Human', 'skeletal', 'SkeletalMesh'),
        ('orc', mini / 'character-orc.fbx', 'Kenney/MiniDungeon/Orc', 'SK_Orc', 'skeletal', 'SkeletalMesh'),
        ('mini_colormap', mini / 'Textures/colormap.png', 'Kenney/MiniDungeon/Textures', 'T_MiniColormap', 'texture', 'Texture2D'),
        ('dungeon_colormap', dungeon / 'Textures/colormap.png', 'Kenney/ModularDungeon/Textures', 'T_DungeonColormap', 'texture', 'Texture2D'),
        ('ui_button', EXISTING / 'kenney-ui-adventure/PNG/Default/button_brown_close.png', 'Kenney/UIAdventure/Button', 'T_ButtonBrownClose', 'texture', 'Texture2D'),
        ('impact', EXISTING / 'kenney-impact-sounds/Audio/impactGeneric_light_000.ogg', 'Kenney/ImpactSounds/ImpactLight', 'SW_ImpactLight', 'audio', 'SoundWave'),
        ('rpg_draw_knife', rpg / 'drawKnife1.ogg', 'Kenney/RPGAudio/DrawKnife', 'SW_DrawKnife', 'audio', 'SoundWave'),
        ('music_loop', PREPARED / 'abstraction-music-loop-bundle-2026-q3/extracted/Week 27 - Dusty Memories.ogg', 'Abstraction/MusicLoopQ3/DustyMemories', 'SW_DustyMemories', 'audio', 'SoundWave'),
        ('blender_probe', PROBE_FOLDER / 'connectivity-probe.fbx', 'Diagnostics/BlenderProbe', 'SM_BlenderProbe', 'static', 'StaticMesh'),
    ]
    checksums = {}
    reps = PREPARED / 'representative-files.json'
    if reps.is_file():
        for item in json.loads(reps.read_text(encoding='utf-8')):
            checksums[str(acquisition_source_path(item['actual_absolute_path'])).casefold()] = item['sha256']
    verification = PROBE_FOLDER / 'verification.json'
    if verification.is_file():
        data = json.loads(verification.read_text(encoding='utf-8-sig'))
        checksums[str((PROBE_FOLDER / 'connectivity-probe.fbx').resolve()).casefold()] = data['fbx']['sha256']
    result = []
    for key, source, folder, name, kind, expected_class in entries:
        result.append({
            'id': key, 'source': str(source.resolve()),
            'expected_source_sha256': checksums.get(str(source.resolve()).casefold()),
            'destination_path': DESTINATION_ROOT + '/' + folder,
            'destination_name': name, 'kind': kind,
            'expected_object_class': expected_class,
        })
    if ONLY_TASK_IDS:
        unknown = set(ONLY_TASK_IDS) - {entry['id'] for entry in result}
        if unknown:
            raise ValueError('Unknown CODEX_ASSET_IMPORT_ONLY task IDs: ' + ', '.join(sorted(unknown)))
        result = [entry for entry in result if entry['id'] in ONLY_TASK_IDS]
    return result


def audited_animation_names(entry):
    """Read the separate, preserved source audit rather than assuming clip counts."""
    if entry['kind'] != 'skeletal':
        return []
    package = PREPARED / 'kenney-mini-dungeon'
    source_relative = str(Path(entry['source']).relative_to(package / 'extracted')).replace('\\', '/')
    for record in json.loads((package / 'structure-audit.json').read_text(encoding='utf-8')):
        if record['path'].replace('\\', '/') == source_relative:
            return [clip['name'] for clip in record['animation_stacks']]
    raise ValueError('No separate source animation audit for ' + entry['source'])


def check_source(entry):
    source = Path(entry['source'])
    out = {'source_exists': source.is_file()}
    if not source.is_file():
        raise FileNotFoundError(str(source))
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    out.update(source_bytes=len(data), source_sha256=digest)
    expected = entry.get('expected_source_sha256')
    if not expected:
        raise ValueError('No preserved acquisition SHA256 was found for this source')
    out['source_hash_matches_acquisition'] = digest.lower() == expected.lower()
    if not out['source_hash_matches_acquisition']:
        raise ValueError('Source SHA256 differs from the preserved acquisition record')
    return out


def preflight():
    results = []
    for entry in plan():
        item = dict(entry)
        try:
            item.update(check_source(entry), status='source_verified_not_imported')
        except Exception as exc:
            item.update(status='source_check_failed', error=str(exc))
        results.append(item)
    payload = {'mode': 'ordinary_python_source_preflight', 'engine_executed': False, 'entries': results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if any(e['status'] == 'source_check_failed' for e in results) else 0


def configure_mini_dungeon_animation_data(unreal, anim_data):
    """Source-specific settings, measured in UE5.5.4; not a general FBX preset."""
    anim_data.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    anim_data.set_editor_property('import_bone_tracks', True)
    # Source melee range is 0.416667 s. Default 30 FPS rejects its half frame.
    # UE's actual resulting AnimSequence is 0.400000006 s at 60 FPS; gameplay
    # must use that observed length, not assume exact source time preservation.
    anim_data.set_editor_property('use_default_sample_rate', False)
    anim_data.set_editor_property('custom_sample_rate', 60)
    anim_data.set_editor_property('snap_to_closest_frame_boundary', False)
    anim_data.set_editor_property('convert_scene', True)
    anim_data.set_editor_property('convert_scene_unit', True)
    anim_data.set_editor_property('force_front_x_axis', False)
    anim_data.set_editor_property('import_uniform_scale', 1.0)
    # These FBXs have a +90 X parent wrapper. UE's uncorrected animated root
    # was identity while its reference root was (-.7071,0,0,.7071). Unreal's
    # +90 roll option (not -90) matched the reference in twelve measured poses.
    # Correct animation import data only: never compensate actor or mesh pose.
    anim_data.set_editor_property('import_rotation', unreal.Rotator(pitch=0.0, yaw=0.0, roll=90.0))


def fbx_options(unreal, kind, skeleton=None):
    options = unreal.FbxImportUI()
    options.set_editor_property('automated_import_should_detect_type', False)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    animation_only = kind == 'animation'
    options.set_editor_property('import_mesh', not animation_only)
    options.set_editor_property('create_physics_asset', False)
    skeletal = kind in ('skeletal', 'animation')
    options.set_editor_property('import_as_skeletal', skeletal)
    options.set_editor_property('import_animations', skeletal)
    options.set_editor_property('mesh_type_to_import',
        unreal.FBXImportType.FBXIT_ANIMATION if animation_only else
        unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH)
    # New skeleton for each source. No merge, mannequin mapping, or retarget assumption.
    if skeletal:
        options.set_editor_property('skeleton', skeleton)
        mesh_data = options.get_editor_property('skeletal_mesh_import_data')
        mesh_data.set_editor_property('import_morph_targets', False)
        mesh_data.set_editor_property('import_meshes_in_bone_hierarchy', True)
        mesh_data.set_editor_property('update_skeleton_reference_pose', False)
        anim_data = options.get_editor_property('anim_sequence_import_data')
        configure_mini_dungeon_animation_data(unreal, anim_data)
    else:
        mesh_data = options.get_editor_property('static_mesh_import_data')
        mesh_data.set_editor_property('combine_meshes', True)
        mesh_data.set_editor_property('auto_generate_collision', False)
        mesh_data.set_editor_property('generate_lightmap_u_vs', True)
        mesh_data.set_editor_property('build_nanite', False)
    mesh_data.set_editor_property('convert_scene', True)
    mesh_data.set_editor_property('convert_scene_unit', True)
    mesh_data.set_editor_property('force_front_x_axis', False)
    mesh_data.set_editor_property('import_uniform_scale', 1.0)
    mesh_data.set_editor_property('import_rotation', unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))
    return options


def inspect_object(unreal, obj):
    item = {'path': obj.get_path_name(), 'name': obj.get_name(), 'class': obj.get_class().get_name()}
    try:
        if isinstance(obj, (unreal.StaticMesh, unreal.SkeletalMesh)):
            bounds = obj.get_bounds()
            extent = bounds.box_extent
            item['local_bounds_origin_cm'] = [float(bounds.origin.x), float(bounds.origin.y), float(bounds.origin.z)]
            item['local_dimensions_cm_xyz'] = [float(extent.x) * 2, float(extent.y) * 2, float(extent.z) * 2]
        if isinstance(obj, unreal.SkeletalMesh):
            skeleton = obj.get_editor_property('skeleton')
            item['skeleton_path'] = skeleton.get_path_name() if skeleton else None
        if isinstance(obj, unreal.AnimSequence):
            item['sequence_length_seconds'] = float(obj.get_editor_property('sequence_length'))
            skeleton = obj.get_editor_property('skeleton')
            item['skeleton_path'] = skeleton.get_path_name() if skeleton else None
            data = obj.get_editor_property('asset_import_data')
            item['import_data_class'] = data.get_class().get_name() if data else None
            if isinstance(data, unreal.FbxAnimSequenceImportData):
                rotation = data.get_editor_property('import_rotation')
                item['actual_animation_import_settings'] = {
                    'use_default_sample_rate': bool(data.get_editor_property('use_default_sample_rate')),
                    'custom_sample_rate': int(data.get_editor_property('custom_sample_rate')),
                    'import_rotation_degrees': {'pitch': float(rotation.pitch), 'yaw': float(rotation.yaw), 'roll': float(rotation.roll)},
                }
    except Exception as exc:
        # A missing optional metadata field must not erase a successfully imported object.
        item['metadata_read_error'] = str(exc)
    return item


def inspect_folder(unreal, destination):
    objects = []
    for path in unreal.EditorAssetLibrary.list_assets(destination, recursive=True, include_folder=False):
        obj = unreal.EditorAssetLibrary.load_asset(path)
        if obj:
            objects.append(obj)
    return objects


def execute_item(unreal, asset_tools, entry):
    item = dict(entry)
    item.update(status='starting', objects=[], errors=[], warnings=[])
    try:
        item.update(check_source(entry))
        before = inspect_folder(unreal, entry['destination_path'])
        before_paths = {obj.get_path_name() for obj in before}
        if before and not REPLACE_EXISTING:
            objects = before
            item['status'] = 'inspected_existing_not_reimported'
            item['warnings'].append('Per-item destination already contains assets; original imports were not overwritten')
        else:
            unreal.EditorAssetLibrary.make_directory(entry['destination_path'])
            import_kind = entry['kind']
            import_name = entry['destination_name']
            animation_skeleton = None
            if before and REPLACE_EXISTING and entry['kind'] == 'skeletal':
                # UE5.5 FbxFactory returns through its mesh reimport handler before
                # processing the full multi-take import options. Import animations
                # explicitly with the same prefix and existing skeleton instead.
                meshes = [obj for obj in before if isinstance(obj, unreal.SkeletalMesh) and obj.get_name() == entry['destination_name']]
                if len(meshes) != 1:
                    raise ValueError('Animation repair requires exactly one existing named SkeletalMesh')
                animation_skeleton = meshes[0].get_editor_property('skeleton')
                if not animation_skeleton:
                    raise ValueError('Existing SkeletalMesh has no Skeleton for animation repair')
                import_kind = 'animation'
                import_name += '_Anim'
                item['animation_target_skeleton_path'] = animation_skeleton.get_path_name()
                # ImportAnimations updates raw animation but can retain the old
                # per-sequence metadata; keep later editor Reimport consistent.
                item['existing_animation_import_settings_updated'] = 0
                for obj in before:
                    if isinstance(obj, unreal.AnimSequence) and obj.get_name().startswith(import_name + '_'):
                        data = obj.get_editor_property('asset_import_data')
                        if isinstance(data, unreal.FbxAnimSequenceImportData):
                            configure_mini_dungeon_animation_data(unreal, data)
                            item['existing_animation_import_settings_updated'] += 1
            item['import_operation'] = 'animation_only_existing_skeleton' if import_kind == 'animation' else 'source_mesh_or_media_import'
            task = unreal.AssetImportTask()
            task.set_editor_property('filename', entry['source'])
            task.set_editor_property('destination_path', entry['destination_path'])
            task.set_editor_property('destination_name', import_name)
            task.set_editor_property('automated', True)
            task.set_editor_property('async_', False)
            task.set_editor_property('replace_existing', REPLACE_EXISTING)
            task.set_editor_property('replace_existing_settings', REPLACE_EXISTING)
            task.set_editor_property('save', True)
            if entry['kind'] in ('static', 'skeletal'):
                task.set_editor_property('factory', unreal.FbxFactory())
                task.set_editor_property('options', fbx_options(unreal, import_kind, animation_skeleton))
            # Texture/audio use the editor's matching importer; OGG is documented by UE5.5.
            asset_tools.import_asset_tasks([task])
            task_objects = list(task.get_objects())
            item['task_imported_object_paths'] = list(task.get_editor_property('imported_object_paths'))
            # Factories may return just a mesh. Include new Skeleton/AnimSequence assets
            # from this dedicated folder, without inferring them from source clip counts.
            by_path = {obj.get_path_name(): obj for obj in task_objects if obj}
            for obj in inspect_folder(unreal, entry['destination_path']):
                by_path[obj.get_path_name()] = obj
            objects = list(by_path.values())
            item['status'] = 'import_task_finished'
        for obj in objects:
            record = inspect_object(unreal, obj)
            record['existed_before_this_run'] = obj.get_path_name() in before_paths
            if item['status'] == 'import_task_finished':
                try:
                    record['save_returned_true'] = bool(unreal.EditorAssetLibrary.save_loaded_asset(obj, only_if_is_dirty=False))
                except Exception as exc:
                    record['save_returned_true'] = False
                    record['save_error'] = str(exc)
            else:
                record['save_returned_true'] = None
            item['objects'].append(record)
        expected_class = getattr(unreal, entry['expected_object_class'])
        expected_objects = [obj for obj in objects if isinstance(obj, expected_class)]
        item['expected_class_observed'] = bool(expected_objects)
        if not expected_objects:
            item['status'] = 'failed_expected_object_class_not_observed'
            item['errors'].append('No actual ' + entry['expected_object_class'] + ' was returned or found')
        if entry['kind'] == 'skeletal':
            clips = [o for o in item['objects'] if o['class'] == 'AnimSequence']
            source_names = audited_animation_names(entry)
            prefix = entry['destination_name'] + '_Anim_'
            actual_names = [o['name'][len(prefix):] if o['name'].startswith(prefix) else o['name'] for o in clips]
            missing_names = sorted(set(source_names) - set(actual_names))
            item['source_animation_stack_count_from_separate_source_audit'] = len(source_names)
            item['source_animation_stack_names_from_separate_source_audit'] = source_names
            item['actual_anim_sequence_count_in_item_folder'] = len(clips)
            item['actual_anim_sequence_names'] = [o['name'] for o in clips]
            item['actual_take_names_from_asset_names'] = actual_names
            item['source_take_names_without_observed_sequence'] = missing_names
            mesh_skeleton_paths = {obj.get_editor_property('skeleton').get_path_name()
                                   for obj in expected_objects if obj.get_editor_property('skeleton')}
            item['all_animations_use_character_skeleton'] = bool(clips) and len(mesh_skeleton_paths) == 1 and all(
                clip.get('skeleton_path') in mesh_skeleton_paths for clip in clips)
            item['source_take_comparison_scope'] = 'Name correspondence only; no animation playback or semantic equivalence verified'
            item['requested_animation_import_settings'] = {
                'applied_during_this_run': item['status'] == 'import_task_finished',
                'use_default_sample_rate': False, 'custom_sample_rate': 60,
                'snap_to_closest_frame_boundary': False,
                'animation_import_rotation_degrees': {'pitch': 0.0, 'yaw': 0.0, 'roll': 90.0},
                'mesh_import_rotation_degrees': {'pitch': 0.0, 'yaw': 0.0, 'roll': 0.0},
                'scope': 'Prepared Kenney Mini Dungeon human/orc only; not a general character preset',
            }
            item['retargeting_performed'] = False
            if missing_names:
                item['status'] = 'failed_source_animation_takes_not_observed'
                item['errors'].append('Source takes without observed AnimSequence: ' + ', '.join(missing_names))
            if len(clips) != len(source_names) or not item['all_animations_use_character_skeleton']:
                item['status'] = 'failed_character_animation_count_or_skeleton'
                item['errors'].append('Expected exactly the audited take count on the character Skeleton')
            pose_helpers = runpy.run_path(str(Path(__file__).with_name('ue-diagnose-character-axis.py')), run_name='character_pose_validation_library')
            diagnostic = pose_helpers['diagnose_pose'](unreal, entry['id'], entry['destination_path'], entry['destination_name'])
            gate = pose_helpers['pose_alignment_gate'](diagnostic)
            item['selected_pose_diagnostic'] = diagnostic
            item['selected_pose_alignment_gate'] = gate
            if not gate['passed']:
                item['status'] = 'failed_selected_character_pose_alignment'
                item['errors'].append('Idle/melee root or head alignment failed; object/clip counts alone do not validate the character')
        if entry['id'] == 'chest':
            item['warnings'].append('Chest intake is static; source open/close animations are not imported by this static task')
        if entry['id'] == 'blender_probe':
            dimensions = [o['local_dimensions_cm_xyz'] for o in item['objects'] if o.get('class') == 'StaticMesh' and 'local_dimensions_cm_xyz' in o]
            item['probe_expected_dimensions_cm_xyz'] = [100.0, 100.0, 200.0]
            item['probe_actual_dimensions_cm_xyz'] = dimensions
            item['probe_axis_permutation_size_match'] = any(all(abs(a-b) <= 1.0 for a,b in zip(sorted(d), [100.0,100.0,200.0])) for d in dimensions)
            item['probe_exact_xyz_size_match'] = any(all(abs(a-b) <= 1.0 for a,b in zip(d, [100.0,100.0,200.0])) for d in dimensions)
            item['probe_longest_axes'] = ['XYZ'[max(range(3), key=lambda k: d[k])] for d in dimensions]
            if not item['probe_axis_permutation_size_match']:
                item['warnings'].append('Probe dimensions do not match 100x100x200 cm even allowing an axis permutation; investigate conversion')
        if entry['kind'] in ('static', 'skeletal'):
            item['materials_automatically_imported'] = False
            item['textures_assigned_to_materials'] = False
            item['gameplay_collision_verified'] = False
        if any(o.get('save_returned_true') is False for o in item['objects']):
            item['warnings'].append('At least one imported object did not confirm a successful save')
    except Exception as exc:
        item['status'] = 'failed_exception'
        item['errors'].append(str(exc))
        item['traceback'] = traceback.format_exc()
    return item


def run_in_editor():
    import unreal
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    saved = Path(unreal.Paths.project_saved_dir()).resolve() / 'Bootstrap'
    saved.mkdir(parents=True, exist_ok=True)
    report_path = saved / 'asset-import-report.json'
    if report_path.is_file():
        previous = saved / ('asset-import-report-before-' + run_id + '.json')
        previous.write_bytes(report_path.read_bytes())
    report = {
        'schema_version': 3, 'run_id_utc': run_id,
        'engine_version': unreal.SystemLibrary.get_engine_version(),
        'script_path': str(Path(__file__).resolve()),
        'project_saved_bootstrap': str(saved), 'destination_root': DESTINATION_ROOT,
        'native_importer_log_directory': str(saved.parent / 'Logs'),
        'native_importer_message_scope': 'Python exceptions and observed missing/wrong objects are recorded here; additional native FBX/audio warnings and errors remain in the editor log',
        'replace_existing': REPLACE_EXISTING, 'engine_executed': True,
        'requested_task_ids': list(ONLY_TASK_IDS) if ONLY_TASK_IDS else 'all',
        'status': 'running', 'entries': [],
        'verification_scope': 'Actual object classes, local mesh bounds and six selected idle/melee root/head pose samples per character; no PIE playback, rendered scene, audio audition, or gameplay validation',
    }

    def write_report():
        temporary = report_path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(report_path)

    write_report()
    interchange_variable = 'Interchange.FeatureFlags.Import.FBX'
    interchange_before = None
    try:
        # FbxImportUI belongs to the legacy FBX importer. Keep the choice local
        # to this invocation and restore it before returning to the editor.
        interchange_before = bool(unreal.SystemLibrary.get_console_variable_bool_value(interchange_variable))
        report['interchange_fbx_enabled_before'] = interchange_before
        if interchange_before:
            unreal.SystemLibrary.execute_console_command(None, interchange_variable + ' False')
        report['interchange_fbx_enabled_during_import'] = bool(unreal.SystemLibrary.get_console_variable_bool_value(interchange_variable))
        if report['interchange_fbx_enabled_during_import']:
            raise RuntimeError('Unable to select legacy FBX importer for FbxImportUI')
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        for entry in plan():
            report['currently_importing'] = entry['id']
            write_report()
            unreal.log('Prepared asset intake: ' + entry['id'])
            result = execute_item(unreal, tools, entry)
            report['entries'].append(result)
            report['currently_importing'] = None
            write_report()
            if result['status'].startswith('failed'):
                unreal.log_error('Asset intake failed: ' + entry['id'] + ': ' + '; '.join(result['errors']))
        failed = [e['id'] for e in report['entries'] if e['status'].startswith('failed')]
        report['summary'] = {
            'source_tasks': len(report['entries']), 'failed_task_ids': failed,
            'actual_observed_object_count': sum(len(e['objects']) for e in report['entries']),
            'actual_observed_anim_sequences': {e['id']:e['actual_anim_sequence_count_in_item_folder'] for e in report['entries'] if e['kind']=='skeletal' and 'actual_anim_sequence_count_in_item_folder' in e},
            'tasks_with_warnings': [e['id'] for e in report['entries'] if e['warnings']],
        }
        report['status'] = 'completed_with_failures' if failed else 'completed_intake_inspection'
    except Exception as exc:
        report['status'] = 'fatal_script_exception'
        report['fatal_error'] = str(exc)
        report['fatal_traceback'] = traceback.format_exc()
        unreal.log_error(report['fatal_traceback'])
    finally:
        if interchange_before is not None:
            unreal.SystemLibrary.execute_console_command(None, interchange_variable + (' True' if interchange_before else ' False'))
            report['interchange_fbx_enabled_after_restore'] = bool(unreal.SystemLibrary.get_console_variable_bool_value(interchange_variable))
        report['finished_utc'] = datetime.now(timezone.utc).isoformat()
        write_report()
        (saved / ('asset-import-report-' + run_id + '.json')).write_bytes(report_path.read_bytes())
        unreal.log('Prepared asset import report: ' + str(report_path))
    return report


if __name__ == '__main__':
    if '--preflight' in sys.argv:
        raise SystemExit(preflight())
    run_in_editor()
