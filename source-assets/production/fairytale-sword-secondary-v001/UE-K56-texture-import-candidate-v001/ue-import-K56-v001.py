"""Root-run K56 candidate. Preflight is host-only; native import never retries/overwrites."""
import argparse,os,sys
from pathlib import Path
from datetime import datetime,timezone
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import K56_import_common_v001 as K

def finish(unreal,tex,receipt,stage):
 event={'object_path':tex.get_path_name(),'stage':stage,'command':'Editor.AsyncTextureCompilationFinishAll','before':[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]};receipt.setdefault('compilation_barriers',[]).append(event)
 unreal.SystemLibrary.execute_console_command(None,event['command']);event['after']=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()];K.need(event['after']==[512,512],'Native dimensions after existing compilation barrier differ')

def native(args,m,c,rows):
 import unreal
 K.need(Path(unreal.Paths.project_dir()).resolve()==K.ROOT/'UnrealGame','Wrong native project')
 proof=K.read(K.checked({'path':str(Path(args.host_proof).resolve()),'bytes':Path(args.host_proof).stat().st_size,'sha256':args.host_proof_sha}))
 K.need(proof['passed'] is True and proof['UE_started'] is False and proof['no_UE_UBT_processes']==[],'Exact host/no-UE proof required')
 K.need(proof['manifest']==K.pin(args.manifest) and proof['compiled_manifest']==K.pin(K.CM) and proof['source_contract']==m['source_contract'] and proof['tool_pins']==K.tool_pins(),'Host inputs/tools differ')
 K.need(proof['source56_RGBA512_decoded'] is True and proof['eight_canonical_body_owner_unions_RGBA_exact'] is True,'Actual host decode proof missing')
 K.need(proof['candidate_freeze']==K.freeze_check(K.HERE/'candidate-freeze-v001.json',args.candidate_freeze_sha),'Exact scoped frozen tool required')
 out=Path(args.output).resolve();K.need(out.parent==Path(args.host_proof).resolve().parent and out.is_relative_to(K.ROOT/'docs/production/first-batch-v2/evidence') and not out.exists(),'Fresh Root evidence receipt outside candidate required')
 claim=K.write_new(out.with_name('native-import-claim-v001.json'),{'schema':'Root-K56-native-import-claim-v001','manifest':K.pin(args.manifest),'source_contract':m['source_contract'],'compiled_manifest':K.pin(K.CM),'replace_existing':False,'automatic_retry_allowed':False,'native_process_id':os.getpid()})
 receipt={'schema':'Root-K56-actual-native-texture-import-v001','utc':datetime.now(timezone.utc).isoformat(),'native_process_id':os.getpid(),'project_dir':str(Path(unreal.Paths.project_dir()).resolve()),'manifest':K.pin(args.manifest),'source_contract':m['source_contract'],'compiled_manifest':K.pin(K.CM),'host_proof':K.pin(args.host_proof),'tool_pins':K.tool_pins(),'candidate_freeze':proof['candidate_freeze'],'claim':claim,'settings_reference_actual_old14':K.pin(K.OLD_RECEIPT),'requested_settings':K.SETTINGS,'assets':[],'actual_count':0,'saved_count':0,'success':False,'automatic_retry_allowed':False,'runtime_GPU_pixel_format':'OPEN_importer_proves_sourceRGBA512_and_TC_EDITOR_ICON_not_GPU_readback','native_render_verified':False,'FinalAccepted':False}
 tasks=[]
 try:
  K.need(not K.DISK.exists(),'Target namespace already present; preserve outcome, no retry')
  K.need(not unreal.EditorAssetLibrary.list_assets(K.NAMESPACE,recursive=True,include_folder=False),'Registry namespace occupied')
  before_registry=set(unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False));receipt['registry_before']=sorted(before_registry)
  for _ in range(2):K.baseline();K.check_content(proof['all_Content_before'])
  sword=unreal.load_asset(m['reused_sword']['object_path']);K.need(isinstance(sword,unreal.Texture2D) and sword.get_path_name()==m['reused_sword']['object_path'],'Existing independent sword must actually exist; never import a replacement')
  for r in rows:
   K.need(not K.saved_path(r).exists() and not unreal.EditorAssetLibrary.does_asset_exist(r['package_name']),'Target already exists')
   task=unreal.AssetImportTask()
   for key,value in {'filename':r['source']['path'],'destination_path':K.NAMESPACE,'destination_name':r['asset_name'],'automated':True,'save':False,'replace_existing':False,'replace_existing_settings':False}.items():task.set_editor_property(key,value)
   tasks.append(task)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  settings={'compression_settings':unreal.TextureCompressionSettings.TC_EDITOR_ICON,'mip_gen_settings':unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,'lod_group':unreal.TextureGroup.TEXTUREGROUP_UI,'filter':unreal.TextureFilter.TF_BILINEAR,'never_stream':True,'srgb':True};old_actual=K.old_actual_settings()
  for r,task in zip(rows,tasks):
   K.need(list(task.get_editor_property('imported_object_paths'))==[r['object_path']],'Factory imported extra/wrong objects')
   tex=unreal.load_asset(r['package_name']);K.need(isinstance(tex,unreal.Texture2D) and tex.get_path_name()==r['object_path'],'Actual imported object is not exact Texture2D');receipt['actual_count']+=1
   finish(unreal,tex,receipt,'before_settings')
   filenames=list(tex.get_editor_property('asset_import_data').extract_filenames());K.need(len(filenames)==1 and Path(filenames[0]).resolve()==Path(r['source']['path']).resolve(),'Import source filename differs')
   for key,value in settings.items():tex.set_editor_property(key,value);K.need(tex.get_editor_property(key)==value,'Native setting readback differs: '+key)
   finish(unreal,tex,receipt,'after_settings_before_save');K.need(not K.saved_path(r).exists(),'Unexpected file appeared before exclusive save');K.need(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'New Texture2D save failed')
   actual_settings={k:bool(tex.get_editor_property(k)) if k in ('never_stream','srgb') else str(tex.get_editor_property(k)) for k in settings};dims=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]
   K.need(actual_settings==old_actual and tex.get_class().get_name()=='Texture2D' and dims==[512,512],'Post-save class/dimensions/settings differ from actual old14')
   K.checked(r['source']);receipt['assets'].append({'frame':r['frame'],'owner':r['owner'],'manifest_source_lineage':{'source_contract':m['source_contract'],'layer_key':str(r['frame'])+':'+r['owner'],'source':r['source'],'source_rgba_sha256':r['source_rgba_sha256'],'source_frame':r['source_frame'],'source_alias_frame':r['source_alias_frame']},'actual_object_path':tex.get_path_name(),'actual_class':tex.get_class().get_name(),'actual_dimensions':dims,'actual_settings':actual_settings,'actual_import_filenames':filenames,'saved':K.pin(K.saved_path(r))});receipt['saved_count']+=1
  expected_objects={r['object_path'] for r in rows};registered=set(unreal.EditorAssetLibrary.list_assets(K.NAMESPACE,recursive=True,include_folder=False));after_registry=set(unreal.EditorAssetLibrary.list_assets('/Game',recursive=True,include_folder=False))
  K.need(registered==expected_objects and after_registry==before_registry|expected_objects,'Native registry created extra/material/missing objects');receipt['registry_added']=sorted(after_registry-before_registry);receipt['registry_after_count']=len(after_registry)
  for _ in range(2):
   result=K.baseline(rows);K.need(result['production_files']==1495,'Production1495 exact membership required');K.check_content(proof['all_Content_before'],rows)
   for asset in receipt['assets']:K.checked(asset['saved'])
   for r in rows:K.checked(r['source'])
  receipt.update(success=True,old1439_unchanged=True,Source303_unchanged=True,actual_Production_files=1495,final_production_count=1495,new_saved_Texture2D_count=56,no_other_new_saved_or_registered_packages=True,verification_passes=2,twoSHA_mismatches=0)
 except Exception as error:
  receipt['failure']=repr(error);raise
 finally:
  receipt['task_imported_object_paths']=[list(t.get_editor_property('imported_object_paths')) for t in tasks]
  K.write_new(out,receipt);unreal.log('K56 actual import receipt: '+str(out))

def main():
 p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--preflight',action='store_true');mode.add_argument('--native-import',action='store_true');p.add_argument('--manifest',required=True);p.add_argument('--manifest-sha',required=True);p.add_argument('--compiled-manifest',required=True);p.add_argument('--compiled-manifest-sha',required=True);p.add_argument('--candidate-freeze-sha');p.add_argument('--host-proof');p.add_argument('--host-proof-sha');p.add_argument('--output',required=True);a=p.parse_args()
 if a.preflight:K.no_ue_processes()
 m,c,rows=K.load_inputs(a.manifest,a.manifest_sha,a.compiled_manifest,a.compiled_manifest_sha,decode=a.preflight)
 if a.preflight:
  for _ in range(2):baseline=K.baseline()
  K.need(not K.DISK.exists() and all(not K.saved_path(r).exists() for r in rows),'All56 targets and namespace must be absent')
  content=K.content_snapshot();K.check_content(content)
  proof={'schema':'Root-K56-host-preflight-v001','passed':True,'utc':datetime.now(timezone.utc).isoformat(),'manifest':K.pin(a.manifest),'source_contract':m['source_contract'],'compiled_manifest':K.pin(K.CM),'tool_pins':K.tool_pins(),'candidate_freeze':K.freeze_check(K.HERE/'candidate-freeze-v001.json',a.candidate_freeze_sha) if a.candidate_freeze_sha else None,'source56_RGBA512_decoded':True,'eight_canonical_body_owner_unions_RGBA_exact':True,'no_UE_UBT_processes':K.no_ue_processes(),'UE_started':False,'destination_absent':True,'baseline':baseline,'all_Content_before':content,'actual_old14_settings':K.old_actual_settings(),'settings_reference':K.pin(K.OLD_RECEIPT),'source_pins':[r['source'] for r in rows],'FinalAccepted':False}
  print(K.write_new(a.output,proof));return
 K.need(a.host_proof and a.host_proof_sha and a.candidate_freeze_sha,'Native mode requires exact host proof and frozen checker');native(a,m,c,rows)
if __name__=='__main__':main()
