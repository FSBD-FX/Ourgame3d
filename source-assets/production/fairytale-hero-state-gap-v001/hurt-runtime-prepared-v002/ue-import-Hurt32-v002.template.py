"""Prepared exact32 Hurt import/validator; Root executes explicitly via PS. No art edits."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,sys
ROOT=Path('F:/Ourgame').resolve()
CONFIG=Path(r'__CONFIG_PATH__')
EXPECTED_CONFIG_SHA='__CONFIG_SHA__'

def fact(p):
 p=Path(p).resolve();b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def need(v,why):
 if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def checkpin(v):
 need(fact(v['path'])==v,'Pinned input changed: '+v['path']);return read(v['path'])
def prodset():return {p.resolve()for p in (ROOT/'UnrealGame/Content/Production').rglob('*')if p.is_file()}
def output(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def load():
 need(fact(CONFIG)['sha256']==EXPECTED_CONFIG_SHA,'Prepared config changed');cfg=read(CONFIG)
 m=checkpin(cfg['import_manifest']);profile=checkpin(cfg['profile']);checkpin(cfg['source_review_lock'])
 guard=checkpin(cfg['old_guard_manifest']);verification=checkpin(cfg['old_guard_independent_verification']);receipt=checkpin(cfg['old_guard_actual_receipt'])
 need(verification['success']and verification['actual_total']==1254 and verification['receipt']==cfg['old_guard_actual_receipt'],'Old1254 lineage invalid')
 need(receipt['success']and receipt['manifest']==cfg['old_guard_manifest']and len(receipt['assets'])==28 and guard['expected_old_count']==1226 and len(guard['old_production_files'])==1226,'Old1226+28 lineage invalid')
 need({r['actual_object_path']for r in receipt['assets']}=={r['object_path']for r in guard['assets']},'Old28 receipt object set differs')
 old={str((ROOT/r['path']).resolve()):{'bytes':r['bytes'],'sha256':r['sha256']}for r in guard['old_production_files']}
 for r in receipt['assets']:
  saved=r['saved'];need(saved['path']not in old,'Duplicate old package');old[str(Path(saved['path']).resolve())]={'bytes':saved['bytes'],'sha256':saved['sha256']}
 need(len(old)==1254,'Expected exact old1254')
 ns=cfg['namespace'];need(ns=='/Game/Production/ArtTrials/EV048/v017/HeroLeatherHurt'and m['namespace']==ns and m['asset_count']==len(m['assets'])==32,'Exact Hurt32 namespace/scope changed')
 need(profile['source_closure_digest']==m['source_closure_digest']and profile['duration_ms']==400 and profile['body_canvas_display_px']==72*512/416,'Profile identity or constants differ')
 need(not m['replace_existing']and cfg['expected_final_count']==1286 and m['canvas_px']==[512,512],'No-overwrite/final count/canvas changed')
 need(m['texture_settings']==cfg['manifest_texture_settings'],'Frozen manifest UI settings differ')
 expected={(i,n)for i in range(4)for n in ['BodyRest','NearArmWithoutHand','HelmetForeground','FarHandForeground','NearHand','ShoulderFar','Chest','ShoulderNear']}
 need({(r['frame'],r['component'])for r in m['assets']}==expected,'Actual5body+3armor row set differs')
 targets=set();objects=set()
 for r in m['assets']:
  need(r['package_path']==ns+'/'+r['name']and r['object_path']==r['package_path']+'.'+r['name'],'Asset path/name differs')
  need(r['known_optional_empty']==(r['component']=='FarHandForeground'and r['frame']in [1,2,3]),'Optionalempty contract differs')
  need(r['expected_object_class']=='Texture2D'and r['source_mode']=='RGBA'and r['source_canvas']==[512,512],'Declared source/class differs')
  need(fact(r['source'])['bytes']==r['source_bytes']and fact(r['source'])['sha256']==r['source_sha256'],'Source PNG changed')
  saved=(ROOT/'UnrealGame/Content'/((r['package_path'][6:])+'.uasset')).resolve();need(saved.is_relative_to(ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v017/HeroLeatherHurt'),'Target escaped namespace')
  r['saved_path']=saved.as_posix();targets.add(saved);objects.add(r['object_path'])
 need(len(targets)==len(objects)==32,'Duplicate target or object')
 need(len(profile['frames'])==4 and {(f['frame'],k,v)for f in profile['frames']for k,v in f['textures'].items()}=={(r['frame'],r['component'],r['object_path'])for r in m['assets']},'Profile32 texture references differ')
 return cfg,m,old,targets,objects
def old_twice(old,allowed):
 for repeat in range(2):
  need(prodset()==allowed,'Production exact file set differs')
  for p,v in old.items():
   now=fact(p);need(all(now[k]==v[k]for k in ['bytes','sha256']),'Old1254 changed: '+p)
def source_RGBA(m):
 from PIL import Image
 empty=[]
 for r in m['assets']:
  with Image.open(r['source'])as im:
   need(im.mode=='RGBA'and im.size==(512,512),'Actual source must be512RGBA')
   need(hashlib.sha256(im.tobytes()).hexdigest()==r['source_RGBA_sha256'],'Decoded source RGBA changed')
   hist=im.getchannel('A').histogram();used=sum(hist[1:]);core=sum(hist[128:])
   need(used==r['source_alpha_nonzero_pixels']and core==r['source_alpha128_pixels'],'Source alpha metadata differs')
   need((list(im.getchannel('A').getbbox())if used else None)==r['source_alpha_bbox'],'Source bbox differs')
   if r['known_optional_empty']:
    need(used==core==0,'Knownempty FarHand source isnotempty');empty.append([r['component'],r['frame']])
   else:need(used>0 and core>0,'Mandatorysource empty')
 need(empty==[['FarHandForeground',1],['FarHandForeground',2],['FarHandForeground',3]],'Exact3empty rows differ')
def verify_receipt(path,cfg,m,old,targets,objects):
 source_RGBA(m)
 rc=read(path);need(rc['success']and len(rc['assets'])==32 and rc['manifest']==fact(cfg['import_manifest']['path']),'Native receipt scope failed')
 need(rc['config']==fact(CONFIG)and rc['importer']['sha256']==fact(__file__)['sha256'],'Receipt importer/config mismatch')
 need({r['actual_object_path']for r in rc['assets']}==objects,'Native object set differs')
 old_twice(old,set(map(Path,old))|targets)
 for repeat in range(2):
  for r in rc['assets']:
   need(r['actual_class']=='Texture2D'and r['actual_dimensions']==[512,512]and r['native_UI_settings_verified'],'ActualTexture2D/dimensions/UIsettings failed')
   expected=next(x for x in m['assets']if x['object_path']==r['actual_object_path'])
   need(r['actual_import_filenames']==[str(Path(expected['source']).resolve())],'Native source filename differs')
   need(r['source_png_sha256']==expected['source_sha256']and r['source_RGBA_sha256']==expected['source_RGBA_sha256']and r['known_optional_empty']==expected['known_optional_empty'],'Native source/empty metadata differs')
   need(r['actual_settings_raw']==cfg['expected_native_settings_raw'],'Native receipt UI settings differ')
   need(fact(r['saved']['path'])==r['saved']and Path(r['saved']['path']).resolve()==Path(expected['saved_path']),'Saved native package changed')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f');p=Path(cfg['validation_directory'])/('independent-import-verification-'+stamp+'.json')
 output(p,{'schema':'Hurt32-independent-native-receipt-verification-v002','success':True,'old1254_twoSHA_unchanged':True,'new32_saved_twoSHA_unchanged':True,'exact_total':1286,'receipt':fact(path),'runtime_verified':False,'FinalAccepted':False})
 print(json.dumps({'success':True,'verification':fact(p),'old1254_twoSHA_unchanged':True,'new32':32,'total':1286}))
def main():
 parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group();g.add_argument('--validate-only',action='store_true');g.add_argument('--verify-receipt');parser.add_argument('--preflight-receipt');args=parser.parse_args()
 cfg,m,old,targets,objects=load()
 if args.verify_receipt:verify_receipt(args.verify_receipt,cfg,m,old,targets,objects);return
 old_twice(old,set(map(Path,old)));need(all(not p.exists()for p in targets),'Nooverwrite; expected new target exists')
 nsdir=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v017/HeroLeatherHurt';need(not nsdir.exists()or not any(nsdir.rglob('*')),'Physical Hurt namespace occupied')
 if args.validate_only:
  source_RGBA(m);stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f');p=Path(args.preflight_receipt)if args.preflight_receipt else Path(cfg['validation_directory'])/('host-source-preflight-'+stamp+'.json')
  need(p.resolve().is_relative_to(Path(cfg['validation_directory']).resolve()),'Preflight output escaped candidate validation directory')
  output(p,{'schema':'Hurt32-host-source-preflight-v002','success':True,'config':fact(CONFIG),'manifest':fact(cfg['import_manifest']['path']),'importer':fact(__file__),'source_closure_digest':m['source_closure_digest'],'source_PNG_and_decoded_RGBA32_exact':True,'known_optional_empty':[['FarHandForeground',1],['FarHandForeground',2],['FarHandForeground',3]],'old1254_twoSHA_unchanged':True,'namespace_physical_empty':True,'UE_started':False,'native_receipt':None,'actual_import_performed':False,'FinalAccepted':False})
  print(json.dumps({'success':True,'preflight':fact(p),'UE_started':False,'actual_import_performed':False}));return
 need(os.environ.get('OURGAME_HURT32_EXECUTE')=='1','Native branch is RootPS -ExecuteNative only')
 preflight_path=Path(os.environ.get('OURGAME_HURT32_PREFLIGHT',''));need(preflight_path.is_file(),'Missing explicit host RGBApreflight')
 pre=read(preflight_path);need(pre['success']and pre['config']==fact(CONFIG)and pre['manifest']==fact(cfg['import_manifest']['path'])and pre['importer']['sha256']==fact(__file__)['sha256']and pre['source_PNG_and_decoded_RGBA32_exact'],'Host preflight changed')
 import unreal
 need(Path(unreal.Paths.project_dir()).resolve().parent==ROOT,'Wrong UE project')
 ns=cfg['namespace'];stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f');rp=ROOT/'UnrealGame/Saved/Bootstrap'/('hurt32-v002-import-'+stamp+'.json')
 rc={'schema':'Hurt32-actual-native-import-v002','config':fact(CONFIG),'manifest':fact(cfg['import_manifest']['path']),'importer':fact(__file__),'host_RGBA_preflight':fact(preflight_path),'assets':[],'success':False,'runtime_verified':False,'FinalAccepted':False}
 try:
  if unreal.EditorAssetLibrary.does_directory_exist(ns):need(not unreal.EditorAssetLibrary.list_assets(ns,recursive=True,include_folder=False),'Registry namespace occupied')
  tasks=[]
  for r in m['assets']:
   need(not unreal.EditorAssetLibrary.does_asset_exist(r['package_path']),'Neverreplace actualexistingasset')
   task=unreal.AssetImportTask()
   for key,value in [('filename',r['source']),('destination_path',ns),('destination_name',r['name']),('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(key,value)
   tasks.append(task)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  settings={'compression_settings':unreal.TextureCompressionSettings.TC_EDITOR_ICON,'mip_gen_settings':unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS,'lod_group':unreal.TextureGroup.TEXTUREGROUP_UI,'never_stream':True,'srgb':True,'filter':unreal.TextureFilter.TF_BILINEAR}
  for r,task in zip(m['assets'],tasks):
   need(list(task.get_editor_property('imported_object_paths'))==[r['object_path']],'Unexpected imported object path')
   tex=unreal.load_asset(r['package_path']);need(isinstance(tex,unreal.Texture2D)and tex.get_path_name()==r['object_path'],'NotexpectedTexture2D')
   dims=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()];need(dims==[512,512],'Actualtexture dimensions differ')
   filenames=list(tex.get_editor_property('asset_import_data').extract_filenames());need(len(filenames)==1 and Path(filenames[0]).resolve()==Path(r['source']).resolve(),'Actualsource filename provenance differs')
   for key,value in settings.items():tex.set_editor_property(key,value);need(tex.get_editor_property(key)==value,'ActualUIsetting differs: '+key)
   need(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'NativeTexture2D save failed')
   rc['assets'].append({'component':r['component'],'frame':r['frame'],'source_png_sha256':r['source_sha256'],'source_RGBA_sha256':r['source_RGBA_sha256'],'source_RGBA_role':'ExactsourcePNGdecodedbyhost; nativeGPU/source-mipRGBA notqueried','known_optional_empty':r['known_optional_empty'],'actual_object_path':tex.get_path_name(),'actual_class':tex.get_class().get_name(),'actual_dimensions':dims,'actual_import_filenames':[str(Path(filenames[0]).resolve())],'native_UI_settings_verified':True,'actual_settings_raw':{k:str(tex.get_editor_property(k))for k in settings},'saved':fact(r['saved_path'])})
  need(set(unreal.EditorAssetLibrary.list_assets(ns,recursive=True,include_folder=False))==objects,'Registry exact32 set differs')
  old_twice(old,set(map(Path,old))|targets);rc.update(success=True,old1254_twoSHA_unchanged=True,total_production_files=1286,loaded_and_saved_Texture2D_objects=32,GPU_compile_finish_claimed=False)
 except Exception as error:rc['failure']=str(error);raise
 finally:output(rp,rc);unreal.log('Hurt32 native import receipt: '+str(rp))
if __name__=='__main__':main()
