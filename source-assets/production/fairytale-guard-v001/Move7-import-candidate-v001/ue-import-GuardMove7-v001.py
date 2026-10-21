"""Exact seven Texture2D native import; default host mode, no import without explicit execution."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from move7_import_contract_v001 import *

def independent(manifest_path,m,receipt_path):
 r=read(receipt_path);need(r['schema']=='GuardMove7-native-import-v001'and r['success']is True,'Actual seven-resource import did not pass')
 need(r['manifest']==pin(manifest_path)and r['actual_total']==r['total_production_files']==1371 and r['verification_passes']==2 and r['old1364_unchanged_twice']is True,'Actual manifest/1371/twoSHA differs')
 approval(check(r['Root_limited_import_approval_pin']),dict(m,manifest_path=manifest_path));validate_receipt_assets(m,r)
 for repeat in range(2):
  verify_old(m['old_production_files']);exact_membership(m,True)
  for x in r['assets']:check(x['saved'])
 out=manifest_path.parent/('independent-import-verification-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
 proof=dict(schema='GuardMove7-independent-import-twoSHA-v001',success=True,manifest=pin(manifest_path),receipt=pin(receipt_path),verifier=pin(__file__),Root_limited_import_approval_pin=r['Root_limited_import_approval_pin'],old1364_unchanged_twice=True,new7_saved_twice=True,actual_total=1371,total_production_files=1371,exact_total=1371,verification_passes=2,hash_mismatches=0,native_metadata_receipt_checked=True,sourceScope='Original native Texture2D/import provenance/settings readback plus two host saved-package byte passes; not fresh UE metadata/GPU/draw/rig proof',presentation_type=TYPE,runtime_verified=False,native_draw_verified=False,TrialAllowed=False,RuntimeTrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
 with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(dict(success=True,independent_receipt=pin(out),actual_total=1371)))

def native(manifest_path,m,approval_path):
 import unreal
 approval(approval_path,dict(m,manifest_path=manifest_path));need(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong actual Unreal project')
 out=ROOT/'UnrealGame/Saved/Bootstrap'/('GuardMove7-v001-import-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')+'.json')
 receipt=dict(schema='GuardMove7-native-import-v001',presentation_type=TYPE,manifest=pin(manifest_path),importer=pin(__file__),contract=pin(HERE/'move7_import_contract_v001.py'),Root_limited_import_approval_pin=pin(approval_path),assets=[],success=False,runtime_verified=False,native_draw_verified=False,TrialAllowed=False,RuntimeTrialAllowed=False,FinalAccepted=False,formal_complete_units=0)
 try:
  need(not unreal.EditorAssetLibrary.list_assets(NAMESPACE,recursive=True,include_folder=False),'Native destination namespace occupied')
  tasks=[]
  for x in m['assets']:
   need(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),'Native object already exists')
   task=unreal.AssetImportTask()
   for k,v in [('filename',x['source']['path']),('destination_path',NAMESPACE),('destination_name',x['name']),('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(k,v)
   tasks.append(task)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  settings=dict(compression_settings=unreal.TextureCompressionSettings.TC_EDITOR_ICON,mip_gen_settings=unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,lod_group=unreal.TextureGroup.TEXTUREGROUP_UI,never_stream=True,srgb=True,filter=unreal.TextureFilter.TF_BILINEAR)
  for x,task in zip(m['assets'],tasks):
   need(list(task.get_editor_property('imported_object_paths'))==[x['object_path']],'Unexpected imported object')
   tex=unreal.load_asset(x['package_path']);need(isinstance(tex,unreal.Texture2D)and tex.get_path_name()==x['object_path'],'Actual Texture2D/object mismatch')
   dimensions=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()];need(dimensions==[512,512],'Actual dimensions changed')
   names=list(tex.get_editor_property('asset_import_data').extract_filenames());need(len(names)==1 and resolve(names[0])==resolve(x['source']['path']),'Actual import filename changed')
   for k,v in settings.items():tex.set_editor_property(k,v);need(tex.get_editor_property(k)==v,'Actual texture setting readback differs: '+k)
   need(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'Texture save failed')
   receipt['assets'].append(dict(component=x['component'],source_native_batch_id=x['source_native_batch_id'],source=x['source'],source_RGBA_sha256=x['source_RGBA_sha256'],actual_object_path=tex.get_path_name(),actual_class=tex.get_class().get_name(),actual_dimensions=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()],actual_import_filenames=list(tex.get_editor_property('asset_import_data').extract_filenames()),actual_settings={k:str(tex.get_editor_property(k))for k in settings},saved=pin(x['saved_path'])))
  need(set(unreal.EditorAssetLibrary.list_assets(NAMESPACE,recursive=True,include_folder=False))=={x['object_path']for x in m['assets']},'Native exact seven-object registry differs')
  validate_receipt_assets(m,receipt)
  for repeat in range(2):
   verify_old(m['old_production_files']);exact_membership(m,True)
   for x in receipt['assets']:check(x['saved'])
  receipt.update(success=True,old1364_unchanged_twice=True,new7_saved_twice=True,verification_passes=2,actual_total=1371,total_production_files=1371)
 except Exception as error:receipt['failure']=str(error);raise
 finally:
  with out.open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
  unreal.log('Move7 actual import receipt: '+str(out))

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',default=os.environ.get('DUNGEON_MOVE7_IMPORT_MANIFEST'));p.add_argument('--root-approval',default=os.environ.get('DUNGEON_MOVE7_IMPORT_APPROVAL'));p.add_argument('--validate-only',action='store_true');p.add_argument('--verify-receipt');p.add_argument('--execute-native',action='store_true',default=os.environ.get('DUNGEON_MOVE7_EXECUTE_IMPORT')=='1');a=p.parse_args();need(a.manifest,'Explicit prepared manifest required');need(not(a.verify_receipt and(a.validate_only or a.execute_native)),'Choose one host/import mode');manifest_path=resolve(a.manifest);m=load_manifest(manifest_path,decode_rgba=bool(a.validate_only or a.verify_receipt or not a.execute_native))
 if a.verify_receipt:independent(manifest_path,m,resolve(a.verify_receipt));return
 verify_old(m['old_production_files']);verify_old(m['old_production_files']);exact_membership(m,False);need(all(not Path(x['saved_path']).exists()for x in m['assets']),'Never replace an existing saved package')
 approved=False
 if a.root_approval:approval(resolve(a.root_approval),dict(m,manifest_path=manifest_path));approved=True
 if a.validate_only or not a.execute_native:
  print(json.dumps(dict(schema='GuardMove7-import-source-preflight-v001',success=True,old1364_unchanged_twice=True,source7_RGBA512_verified=True,Root_approval_accepted=approved,expected_total=1371,UE_started=False,runtime_verified=False,TrialAllowed=False,FinalAccepted=False)));return
 need(approved,'Explicit approved Root import receipt required before UE mutation');native(manifest_path,m,resolve(a.root_approval))
if __name__=='__main__':main()
