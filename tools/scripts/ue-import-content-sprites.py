"""UE Editor Python: import a frozen visual candidate subset, preserving source hashes.

Owns /Game/Production/FirstBatch/v001/CandidateSprites only. Importing a composite
does not certify interchangeable armor, hand occlusion, sockets or gameplay timing.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
VERSION = globals().get('SPRITE_VERSION', 'v001')
assert re.fullmatch(r'v[0-9]{3}', VERSION)
SOURCE = Path(globals().get('SPRITE_MANIFEST', ROOT / f'source-assets/production/first-unit-animation-v001/import-subset-{VERSION}.json')).resolve()
assert SOURCE.is_relative_to((ROOT/'source-assets/production').resolve())
manifest = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
RECEIPT = ROOT / f'UnrealGame/Saved/Bootstrap/content-sprites-{VERSION}-import.json'
previous = json.loads(RECEIPT.read_text(encoding='utf-8-sig')) if RECEIPT.exists() else {}
previous_hashes = {row['asset']: row['source_sha256'] for row in previous.get('assets', [])}
tasks, expected = [], []
for clip in manifest['actions']:
    actor, action = clip['actor'], clip['action']
    assert re.fullmatch(r'[a-z0-9_-]+', actor) and re.fullmatch(r'[a-z0-9_-]+', action)
    for index, frame in enumerate(clip['frames']):
        source = Path(frame['path']).resolve()
        assert source.is_relative_to((ROOT / 'source-assets/production').resolve()), source
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert digest == frame['sha256'], f'Changed frozen frame: {source}'
        assert frame['canvas_px'] == [512, 512] and frame['mode'] == 'RGBA'
        assert frame['alpha_extrema'] == [0, 255] and frame['corners_transparent']
        name = f'T_{actor}_{action}_{index:03d}_{VERSION}'.replace('-', '_')
        destination = f'/Game/Production/FirstBatch/{VERSION}/CandidateSprites/' + actor.title()
        asset_path = destination + '/' + name
        expected.append({'actor': actor, 'action': action, 'frame': index,
                         'source': str(source), 'source_sha256': digest, 'asset': asset_path,
                         'ground_root_px': frame.get('root_px', clip.get('ground_root_px'))})
        if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            assert previous_hashes.get(asset_path) == digest, f'Existing frame lacks matching receipt: {asset_path}'
            continue
        task = unreal.AssetImportTask()
        for prop, value in [('filename', str(source)), ('destination_path', destination),
                            ('destination_name', name), ('automated', True), ('save', True), ('replace_existing', False)]:
            task.set_editor_property(prop, value)
        tasks.append(task)
assert expected, 'Frozen subset has no frames'
for component in ([] if globals().get('SPRITE_REUSE_EXISTING_COMPONENTS',False) else manifest.get('components', [])):
    source = Path(component['file']).resolve()
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest == component['sha256'] and component['canvas_px'] == [512, 512]
    assert component['alpha_extrema'] == [0, 255]
    name = f'T_military_sword_{VERSION}'
    destination = f'/Game/Production/FirstBatch/{VERSION}/CandidateComponents'
    asset_path = destination + '/' + name
    expected.append({'actor': 'component', 'action': 'military_sword', 'frame': 0,
                     'source': str(source), 'source_sha256': digest, 'asset': asset_path,
                     'grip_px': component['landmarks_px']['grip']})
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        assert previous_hashes.get(asset_path) == digest, f'Component lacks matching receipt: {asset_path}'
        continue
    task = unreal.AssetImportTask()
    for prop, value in [('filename', str(source)), ('destination_path', destination),
                        ('destination_name', name), ('automated', True), ('save', True), ('replace_existing', False)]:
        task.set_editor_property(prop, value)
    tasks.append(task)
if tasks:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for row in expected:
    texture = unreal.load_asset(row['asset'])
    assert isinstance(texture, unreal.Texture2D), row['asset']
    texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('never_stream', True)
    texture.set_editor_property('srgb', True)
    row['imported_size'] = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
    assert row['imported_size'] == [512, 512], row
    unreal.EditorAssetLibrary.save_loaded_asset(texture, False)
report = {'utc': datetime.now(timezone.utc).isoformat(), 'manifest': str(SOURCE),
          'manifest_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'assets': expected, 'actual_count': len(expected), 'success': True,
          'formal_content_accepted': False,
          'reuse_existing_components': bool(globals().get('SPRITE_REUSE_EXISTING_COMPONENTS',False)),
          'scope': 'Frozen RGBA candidate import/class/dimensions only; runtime, sockets, layered equipment and motion acceptance separate'}
RECEIPT.parent.mkdir(parents=True, exist_ok=True)
if previous and len(previous.get('assets', [])) != len(expected):
    prior = RECEIPT.with_name('content-sprites-%s-import-initial-%d.json' % (VERSION, len(previous['assets'])))
    assert not prior.exists(), 'Preserve prior receipt; do not overwrite history'
    prior.write_bytes(RECEIPT.read_bytes())
RECEIPT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
unreal.log('Visual candidate import receipt: ' + str(RECEIPT))
