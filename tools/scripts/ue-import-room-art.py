"""Import frozen, scenery-only room layers; collision stays in gameplay data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import unreal

root=Path(unreal.Paths.project_dir()).resolve().parent
source=Path(globals().get('ROOM_ART_MANIFEST',root/'source-assets/production/room-art-v001/manifests/import-subset-v001.json')).resolve()
assert source.is_relative_to(root/'source-assets/production')
manifest=json.loads(source.read_text(encoding='utf-8-sig'))
assert manifest['frozen'] and manifest['stage_canvas_px']==[1280,720]
receipt=root/'UnrealGame/Saved/Bootstrap/room-art-v001-import.json'
previous=json.loads(receipt.read_text(encoding='utf-8-sig')) if receipt.exists() else {}
hashes={row['asset']:row['source_sha256'] for row in previous.get('assets',[])}
expected=[];tasks=[]
for layer in manifest['layers']:
    path=Path(layer['file']).resolve()
    assert path.is_relative_to(root/'source-assets/production')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==layer['sha256']
    name=layer['ue_asset_name'];destination=layer['ue_destination'].rstrip('/')
    assert re.fullmatch(r'T_Room(?:Far|Mid|Floor)_v[0-9]{3}',name)
    assert destination=='/Game/Production/RoomArt/v001'
    asset=destination+'/'+name
    row={'id':layer['id'],'source':str(path),'source_sha256':digest,'asset':asset,
         'expected_size':layer['normalized_dimensions_px'],'collision_role':'none'}
    expected.append(row)
    if unreal.EditorAssetLibrary.does_asset_exist(asset):
        assert hashes.get(asset)==digest,'Never overwrite a changed or unreceipted layer: '+asset
        continue
    task=unreal.AssetImportTask()
    for key,value in [('filename',str(path)),('destination_path',destination),('destination_name',name),
                      ('automated',True),('save',True),('replace_existing',False)]:
        task.set_editor_property(key,value)
    tasks.append(task)
assert expected
if tasks:unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for row in expected:
    texture=unreal.load_asset(row['asset']);assert isinstance(texture,unreal.Texture2D)
    texture.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('never_stream',True);texture.set_editor_property('srgb',True)
    row['imported_size']=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]
    assert row['imported_size']==row['expected_size']
    if row['id'] in ('far','mid'):assert row['imported_size']==[1280,720]
    unreal.EditorAssetLibrary.save_loaded_asset(texture,False)
if previous and previous.get('manifest_sha256')!=hashlib.sha256(source.read_bytes()).hexdigest():
    prior=receipt.with_name('room-art-v001-import-prior-%d.json'%len(previous['assets']))
    assert not prior.exists();prior.write_bytes(receipt.read_bytes())
report={'utc':datetime.now(timezone.utc).isoformat(),'manifest':str(source),
        'manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'assets':expected,
        'success':True,'actual_count':len(expected),'runtime_verified':False,'full_map_complete':False,
        'scope':'Texture/source/dimension verification only. Walk bounds, objects, exits and exploration remain separate.'}
receipt.parent.mkdir(parents=True,exist_ok=True)
receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
unreal.log('Room scenery import receipt: '+str(receipt))
