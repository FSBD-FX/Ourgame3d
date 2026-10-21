"""Root-only actual exact48 import. --validate-only uses no Unreal module."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,sys
sys.dont_write_bytecode=True
checks_path=Path(__file__).with_name('ue_walk48_checks_v001.py')
spec=importlib.util.spec_from_file_location('walk48_checks',checks_path);checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)
d=checks.preflight()
if '--validate-only' in sys.argv:
 print(json.dumps({'source_preflight':True,'sources':48,'old_files_unchanged':1151,'old_verification_passes':2,'manifest_sha256':checks.MANIFEST_SHA,'UE_started':False}));raise SystemExit(0)

import unreal
checks.require(Path(unreal.Paths.project_dir()).resolve().parent==checks.ROOT,'Wrong actual UE project')
out=checks.ROOT/'UnrealGame/Saved/Bootstrap'/('fairytale-walk48-v001-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
receipt={'schema':'fairytale-walk48-native-import-receipt-v001','utc':datetime.now(timezone.utc).isoformat(),'manifest':str(checks.MANIFEST),
 'manifest_sha256':checks.MANIFEST_SHA,'namespace':checks.NAMESPACE,'importer_sha256':checks.sha(__file__),'checks_sha256':checks.sha(checks_path),
 'expected_count':48,'actual_count':0,'saved_count':0,'assets':[],'success':False,'runtime_verified':False,'motion_accepted':False,'formal_complete_units':0,
 'scope':d['scope'],'assembly_freeze':d['references']['assembly_freeze'],'source_pixel_proof':d['references']['source_pixel_proof'],'markers':d['references']['markers']}
try:
 if unreal.EditorAssetLibrary.does_directory_exist(checks.NAMESPACE):
  checks.require(not unreal.EditorAssetLibrary.list_assets(checks.NAMESPACE,recursive=True,include_folder=False),'Namespace registry already occupied')
 tasks=[]
 for x in d['assets']:
  checks.require(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),'Existing object; replacement forbidden')
  task=unreal.AssetImportTask()
  for k,v in [('filename',x['source']),('destination_path',checks.NAMESPACE),('destination_name',x['name']),('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(k,v)
  tasks.append(task)
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
 settings={'compression_settings':unreal.TextureCompressionSettings.TC_EDITOR_ICON,'mip_gen_settings':unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,
  'lod_group':unreal.TextureGroup.TEXTUREGROUP_UI,'never_stream':True,'srgb':True}
 for x,t in zip(d['assets'],tasks):
  checks.require(list(t.get_editor_property('imported_object_paths'))==[x['object_path']],'Unexpected imported object path')
  tex=unreal.load_asset(x['package_path']);checks.require(isinstance(tex,unreal.Texture2D),'Not actual Texture2D')
  checks.require([tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]==[512,512],'Actual native canvas changed')
  for k,v in settings.items():tex.set_editor_property(k,v);checks.require(tex.get_editor_property(k)==v,'Actual texture setting changed: '+k)
  receipt['actual_count']+=1
 checks.verify_old(d);checks.verify_old(d)
 for x in d['assets']:
  tex=unreal.load_asset(x['package_path']);checks.require(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'New Texture2D save failed')
  for k,v in settings.items():checks.require(tex.get_editor_property(k)==v,'Saved texture setting changed: '+k)
  disk=checks.DISK/(x['name']+'.uasset');checks.require(disk.is_file() and disk.stat().st_size>0,'New saved .uasset missing')
  receipt['assets'].append({**x,'actual_object_type':tex.get_class().get_name(),'actual_canvas':[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()],
   'actual_texture_settings':d['texture_settings'],'saved_uasset':str(disk),'saved_bytes':disk.stat().st_size,'saved_sha256':checks.sha(disk)})
  receipt['saved_count']+=1
 registered=list(unreal.EditorAssetLibrary.list_assets(checks.NAMESPACE,recursive=True,include_folder=False))
 checks.require(len(registered)==48 and set(registered)=={x['object_path'] for x in d['assets']},'Actual registry exact48 set differs')
 checks.exact_disk_set(d,True);checks.verify_old(d);checks.verify_old(d)
 receipt.update(success=True,old_files_unchanged=1151,old_verification_passes_after=2,registry_exact_set_passed=True,disk_exact_set_passed=True,total_production_files=1199)
except Exception as e:
 receipt['error']=str(e);raise
finally:
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
 unreal.log('Fairytale Walk48 native receipt: '+str(out))
