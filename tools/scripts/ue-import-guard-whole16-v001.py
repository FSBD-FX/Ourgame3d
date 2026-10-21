"""Root exact16 Texture2D import with unchanged old1210; native API, no art edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path('F:/Ourgame').resolve()
MANIFEST = ROOT / 'source-assets/production/fairytale-guard-v001/root-trial-registration-v001/import-manifest.json'
EXPECTED_SHA = '1a345a4b5f494002effea9f565b1fecbd6618211bf08bd05d6a52c6b4cd01c43'
NAMESPACE = '/Game/Production/FirstBatch/GuardWhole_v001'


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def need(value, why):
    if not value:
        raise ValueError(why)


def old_unchanged(data):
    for row in data['old_production_files']:
        now = fact(ROOT / row['path'])
        need(all(now[key] == row[key] for key in ['bytes', 'sha256']), 'Old package changed: ' + row['path'])


def load():
    need(fact(MANIFEST)['sha256'] == EXPECTED_SHA, 'Root import manifest changed')
    data = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    need(data['expected_old_count'] == 1210 and data['expected_new_count'] == len(data['assets']) == 16, 'Exact import scope changed')
    need(fact(data['root_trial_registration']['path']) == data['root_trial_registration'], 'Root scoped trial record changed')
    for row in data['assets']:
        need(fact(row['source']['path']) == row['source'], 'Source PNG changed')
    return data


data = load()
if '--verify-receipt' in sys.argv:
    receipt_path = Path(sys.argv[sys.argv.index('--verify-receipt') + 1])
    receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    need(receipt['success'] and len(receipt['assets']) == 16, 'Native import receipt failed')
    for repeat in range(2):
        old_unchanged(data)
        for row in receipt['assets']:
            need(fact(row['saved']['path']) == row['saved'], 'Native saved package changed')
    actual = {path.resolve() for path in (ROOT / 'UnrealGame/Content/Production').rglob('*') if path.is_file()}
    expected = {ROOT / row['path'] for row in data['old_production_files']} | {Path(row['saved_path']) for row in data['assets']}
    need(actual == expected and len(actual) == 1226, 'Actual Production file set is not old1210 plus exact16')
    output = MANIFEST.parent / 'independent-import-verification-v001.json'
    need(not output.exists(), 'Never overwrite independent import result')
    output.write_text(json.dumps({'success': True, 'old1210_unchanged': True, 'new16_saved': True, 'actual_total': 1226, 'verification_passes': 2, 'receipt': fact(receipt_path), 'runtime_verified': False, 'formal_complete_units': 0}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'old1210_unchanged': True, 'new_Texture2D': 16, 'total': 1226, 'two_SHA_passes': True}))
    raise SystemExit(0)

old_unchanged(data)
old_unchanged(data)
need(len([p for p in (ROOT / 'UnrealGame/Content/Production').rglob('*') if p.is_file()]) == 1210, 'Fresh exact old1210 namespace required')
need(all(not Path(row['saved_path']).exists() for row in data['assets']), 'Never replace an existing package')
if '--validate-only' in sys.argv:
    from PIL import Image
    for row in data['assets']:
        with Image.open(row['source']['path']) as im:
            need(im.mode == 'RGBA' and im.size == (512, 512), 'Source must be actual512 RGBA')
            need(im.getchannel('A').getextrema() == (0, 255), 'Missing native source alpha range')
    print(json.dumps({'source_RGBA512_exact16': True, 'old1210_two_SHA_passes': True, 'UE_started': False}))
    raise SystemExit(0)

import unreal
need(Path(unreal.Paths.project_dir()).resolve().parent == ROOT, 'Wrong actual UE project')
receipt_path = ROOT / 'UnrealGame/Saved/Bootstrap' / ('guard-whole16-v001-import-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f') + '.json')
receipt = {'schema': 'guard-whole16-actual-native-import-v001', 'manifest': fact(MANIFEST), 'importer': fact(Path(__file__)), 'assets': [], 'success': False, 'runtime_verified': False, 'formal_complete_units': 0}
try:
    if unreal.EditorAssetLibrary.does_directory_exist(NAMESPACE):
        need(not unreal.EditorAssetLibrary.list_assets(NAMESPACE, recursive=True, include_folder=False), 'Namespace registry occupied')
    tasks = []
    for row in data['assets']:
        need(not unreal.EditorAssetLibrary.does_asset_exist(row['package_path']), 'Existing actual asset; replacement forbidden')
        task = unreal.AssetImportTask()
        for key, value in [('filename', row['source']['path']), ('destination_path', row['destination_path']), ('destination_name', row['name']), ('automated', True), ('save', False), ('replace_existing', False)]:
            task.set_editor_property(key, value)
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    settings = {'compression_settings': unreal.TextureCompressionSettings.TC_EDITOR_ICON, 'mip_gen_settings': unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS, 'lod_group': unreal.TextureGroup.TEXTUREGROUP_UI, 'never_stream': True, 'srgb': True, 'filter': unreal.TextureFilter.TF_BILINEAR}
    for row, task in zip(data['assets'], tasks):
        need(list(task.get_editor_property('imported_object_paths')) == [row['object_path']], 'Unexpected actual imported object path')
        tex = unreal.load_asset(row['package_path'])
        need(isinstance(tex, unreal.Texture2D) and tex.get_path_name() == row['object_path'], 'Actual object is not expected Texture2D')
        need([tex.blueprint_get_size_x(), tex.blueprint_get_size_y()] == [512, 512], 'Actual texture dimensions changed')
        filenames = list(tex.get_editor_property('asset_import_data').extract_filenames())
        need(len(filenames) == 1 and Path(filenames[0]).resolve() == Path(row['source']['path']).resolve(), 'Actual source filename provenance differs')
        for key, value in settings.items():
            tex.set_editor_property(key, value)
            need(tex.get_editor_property(key) == value, 'Actual texture setting differs: ' + key)
        need(unreal.EditorAssetLibrary.save_loaded_asset(tex, False), 'Saving native new Texture2D failed')
        receipt['assets'].append({'source': row['source'], 'actual_object_path': tex.get_path_name(), 'actual_class': tex.get_class().get_name(), 'actual_dimensions': [512, 512], 'actual_import_filenames': filenames, 'actual_settings': {key: str(tex.get_editor_property(key)) for key in settings}, 'saved': fact(row['saved_path'])})
    need(set(unreal.EditorAssetLibrary.list_assets(NAMESPACE, recursive=True, include_folder=False)) == {row['object_path'] for row in data['assets']}, 'Native registry exact16 set differs')
    old_unchanged(data)
    old_unchanged(data)
    need(len([p for p in (ROOT / 'UnrealGame/Content/Production').rglob('*') if p.is_file()]) == 1226, 'Final native package count differs')
    receipt.update(success=True, old1210_unchanged=True, verification_passes=2, total_production_files=1226)
except Exception as error:
    receipt['failure'] = str(error)
    raise
finally:
    with receipt_path.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
    unreal.log('Guard whole16 native import receipt: ' + str(receipt_path))
