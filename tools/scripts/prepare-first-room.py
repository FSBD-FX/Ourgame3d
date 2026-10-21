"""Run inside UE Editor Python commandlet; import free raster frames and create FirstRoom.

Only owns /Game/Prototype/FirstRoom and /Game/Maps/FirstRoom. Historical maps are preserved.
"""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
SOURCE = ROOT / 'source-assets/prototype/first-room-v1'
manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8-sig'))
tools = unreal.AssetToolsHelpers.get_asset_tools()
tasks = []
expected = []
for role, description in manifest['characters'].items():
    for clip, data in description['clips'].items():
        for filename in data['frames']:
            source = SOURCE / filename
            assert source.is_file(), source
            name = 'T_' + source.stem
            destination = '/Game/Prototype/FirstRoom/Sprites/' + role.title()
            asset_path = destination + '/' + name
            expected.append((source, asset_path))
            if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
                continue
            task = unreal.AssetImportTask()
            task.set_editor_property('filename', str(source))
            task.set_editor_property('destination_path', destination)
            task.set_editor_property('destination_name', name)
            task.set_editor_property('automated', True)
            task.set_editor_property('save', True)
            task.set_editor_property('replace_existing', False)
            tasks.append(task)
if tasks:
    tools.import_asset_tasks(tasks)
assets = []
for source, asset_path in expected:
    texture = unreal.load_asset(asset_path)
    assert isinstance(texture, unreal.Texture2D), asset_path
    texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('never_stream', True)
    texture.set_editor_property('srgb', True)
    unreal.EditorAssetLibrary.save_loaded_asset(texture, False)
    assets.append({'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'asset': asset_path})

map_path = '/Game/Maps/FirstRoom'
if unreal.EditorAssetLibrary.does_asset_exist(map_path):
    unreal.EditorLoadingAndSavingUtils.load_map(map_path)
else:
    unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
game_mode = unreal.load_class(None, '/Script/CodexDungeon.DungeonGameMode')
assert game_mode, 'GameMode missing; compile C++ module first'
world.get_world_settings().set_editor_property('default_game_mode', game_mode)
assert unreal.EditorLoadingAndSavingUtils.save_map(world, map_path)
report = {'utc': datetime.now(timezone.utc).isoformat(), 'engine': unreal.SystemLibrary.get_engine_version(), 'map': map_path,
          'textures': assets, 'texture_count': len(assets), 'success': len(assets) == 64,
          'scope': 'Asset import and map creation only; runtime verified separately.'}
output = ROOT / 'UnrealGame/Saved/Bootstrap/first-room-import.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
unreal.log('FirstRoom preparation complete: ' + str(output))
