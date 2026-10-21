"""Actual exact40 native Texture2D import; old1286 must remain byte-identical."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys
R=Path('F:/Ourgame').resolve()
M=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001/Root-Death40-import-v001/import-manifest.json'
def fact(p):
 p=Path(p).resolve();return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def need(v,why):
 if not v: raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(x):need(fact(x['path'])==x,'Pin changed: '+x['path'])
m=read(M)
need(m['schema']=='Root-Death40-native-import-v001' and (m['expected_old_count'],m['expected_new_count'],m['expected_final_count'])==(1286,40,1326),'Scope changed')
need(len(m['assets'])==40 and len({x['object_path'] for x in m['assets']})==40,'Exact40 manifest required')
for key in ['root_trial_registration','candidate_freeze','source_manifest','old_compiled_snapshot']:check(m[key])
need(m['candidate_freeze']['sha256']=='5f6506b609440d8cfda40b493b7ce9b23131b0f83aa09add333f8d8e74ef788c','Wrong candidate')
for x in m['assets']:check(x['source']);check(x['retained_E'])
def verify_old():
 for x in m['old_production_files']:
  p=R/x['path'];need(p.stat().st_size==x['bytes'] and fact(p)['sha256']==x['sha256'],'Old package changed: '+x['path'])
def exact_final():
 actual={p.resolve() for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
 expected={(R/x['path']).resolve() for x in m['old_production_files']}|{Path(x['saved_path']).resolve() for x in m['assets']}
 need(actual==expected and len(actual)==1326,'Actual Production set must be exact old1286+40')
if '--verify-receipt' in sys.argv:
 receipt_path=Path(sys.argv[sys.argv.index('--verify-receipt')+1]);receipt=read(receipt_path)
 need(receipt['success'] and len(receipt['assets'])==40 and receipt['manifest']==fact(M),'Actual import receipt failed')
 for repeat in range(2):
  verify_old();exact_final()
  for x in receipt['assets']:check(x['saved'])
 output=M.parent/('independent-import-verification-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
 with output.open('x',encoding='utf-8') as f:json.dump(dict(success=True,old1286_unchanged_twice=True,new40_saved_twice=True,exact_total=1326,receipt=fact(receipt_path),manifest=fact(M),verification_passes=2,hash_mismatches=0,runtime_verified=False,formal_complete_units=0),f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(success=True,independent_receipt=fact(output),actual_total=1326)));raise SystemExit(0)
verify_old();verify_old()
need(len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1286,'Fresh exact old1286 required')
need(all(not Path(x['saved_path']).exists() for x in m['assets']),'Never replace existing package')
if '--validate-only' in sys.argv:
 from PIL import Image
 for x in m['assets']:
  with Image.open(x['source']['path']) as im:
   need(im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getbbox(),'Nonempty RGBA512 required')
   need(hashlib.sha256(im.tobytes()).hexdigest()==x['source_RGBA_sha256'],'Actual RGBA changed')
 print(json.dumps(dict(exact40_RGBA512=True,old1286_unchanged_twice=True,UE_started=False)));raise SystemExit(0)
import unreal
need(Path(unreal.Paths.project_dir()).resolve().parent==R,'Wrong actual project')
receipt_path=R/'UnrealGame/Saved/Bootstrap'/('hero-Death40-v001-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
receipt=dict(schema='hero-Death40-native-import-v001',manifest=fact(M),importer=fact(Path(__file__)),assets=[],success=False,runtime_verified=False,formal_complete_units=0)
try:
 need(not unreal.EditorAssetLibrary.list_assets(m['namespace'],recursive=True,include_folder=False),'Native namespace occupied')
 tasks=[]
 for x in m['assets']:
  need(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),'Actual object already exists')
  task=unreal.AssetImportTask()
  for key,value in [('filename',x['source']['path']),('destination_path',m['namespace']),('destination_name',x['name']),('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(key,value)
  tasks.append(task)
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
 settings=dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,lod_group=unreal.TextureGroup.TEXTUREGROUP_UI,never_stream=True,srgb=True,filter=unreal.TextureFilter.TF_BILINEAR)
 for x,task in zip(m['assets'],tasks):
  need(list(task.get_editor_property('imported_object_paths'))==[x['object_path']],'Unexpected actual imported path')
  tex=unreal.load_asset(x['package_path']);need(isinstance(tex,unreal.Texture2D) and tex.get_path_name()==x['object_path'],'Wrong Texture2D object')
  need([tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]==[512,512],'Wrong actual texture size')
  filenames=list(tex.get_editor_property('asset_import_data').extract_filenames())
  need(len(filenames)==1 and Path(filenames[0]).resolve()==Path(x['source']['path']).resolve(),'Wrong source provenance')
  for key,value in settings.items():tex.set_editor_property(key,value);need(tex.get_editor_property(key)==value,'Setting differs: '+key)
  need(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'Native asset save failed')
  receipt['assets'].append(dict(component=x['component'],frame=x['frame'],source=x['source'],actual_object_path=tex.get_path_name(),actual_class=tex.get_class().get_name(),actual_dimensions=[512,512],actual_import_filenames=filenames,actual_settings={key:str(tex.get_editor_property(key)) for key in settings},saved=fact(x['saved_path'])))
 need(set(unreal.EditorAssetLibrary.list_assets(m['namespace'],recursive=True,include_folder=False))=={x['object_path'] for x in m['assets']},'Native registry40 differs')
 verify_old();verify_old();exact_final()
 receipt.update(success=True,old1286_unchanged=True,verification_passes=2,total_production_files=1326)
except Exception as error:
 receipt['failure']=str(error);raise
finally:
 with receipt_path.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
 unreal.log('Death40 actual import receipt: '+str(receipt_path))
