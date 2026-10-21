"""Root-owned, exact36 new Texture2D imports, two separate18 receipts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];B=R/'source-assets/production/fairytale-lgt-readability-v003/combo-import-v001';C=B/'root-import-contract-v001.json'
def require(v,why):
 if not v:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(x):
 p=Path(x['path']);require(p.is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Pinned input changed: '+str(p));return p
require(sha(C)=='3506ebdc2a46cb784366ad621bebbea0f761633c35b557b73262f82a0381de6a','Root import contract changed');c=load(C);require(c['new_count']==36 and c['total_packages_after']==1151,'Wrong import contract')
old=load(pin(c['old_inventory']))['files'];require(len(old)==1115,'Old inventory wrong')
def verify_old():
 for x in old:require((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'],'Old package changed')
decoder=Path(__file__).with_name('ue-import-armor-primary2-four-v001.py');require(sha(decoder)=='5c667edbeb81eac54648d14ff92b8883d1b15a39a05cc3b56c17933dd29eb49a','PNG decoder changed');spec=importlib.util.spec_from_file_location('existing_rgba_decoder',decoder);dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
docs=[]
for clip,m in zip((2,3),c['manifests']):
 path=pin(m);d=load(path);ns=f'/Game/Production/ArtTrials/EV048/v0{clip+12}/HeroLeatherPrimary{clip}';disk=R/'UnrealGame/Content'/ns.removeprefix('/Game/')
 require(d['import_permitted'] and not d['Root_static_review_required'] and not d['full_motion_accepted'] and d['formal_complete_units']==0,'Root trial-only approval missing')
 require(d['namespace']==ns and len(d['assets'])==d['asset_count']==18 and d['body_assets_reused_unchanged']==24,'Wrong namespace/count')
 require(d['canvas_px']==[512,512] and d['display_root']==[256,464] and d['preview_canvas_size']==72*512/416 and d['native_facing']==1,'Geometry changed')
 require(d['durations_ms']==([75,75,60,60,135,135] if clip==2 else [110,110,60,60,160,160]),'Timing changed')
 for ref in d['references'].values():pin(ref)
 require({(x['component'],x['frame']) for x in d['assets']}=={(x,i) for x in ['Chest','ShoulderNear','ShoulderFar'] for i in range(6)},'Wrong six-phase component set')
 for x in d['assets']:
  p=Path(x['source']);require(p.is_relative_to(R) and p.stat().st_size==x['source_bytes'] and sha(p)==x['source_sha256'],'PNG changed');name=f'T_Fairytale_LeatherPrimary{clip}{x["component"]}_{x["frame"]:03d}_v001'
  require((x['name'],x['package_path'],x['object_path'])==(name,ns+'/'+name,ns+'/'+name+'.'+name),'Object identity changed');info=dec.inspect_rgba_png(p.read_bytes());require(info['nonempty'] and info['corners_transparent'] and info['alpha_extrema']==[0,255],'Bad PNG')
 require(not disk.exists() or not any(p.is_file() for p in disk.rglob('*')),'No overwrite of namespaces');docs.append((clip,path,d,ns,disk))
verify_old();require(len(list((R/'UnrealGame/Content/Production').rglob('*.uasset')))==1115,'Unexpected starting package set')
if '--validate-only' in sys.argv:print(json.dumps(dict(preflight=True,new_sources=36,old_packages_unchanged=1115)));raise SystemExit(0)
import unreal
require(Path(unreal.Paths.project_dir()).resolve().parent==R,'Wrong project')
all_saved=[]
for clip,path,d,ns,disk in docs:
 receipt=dict(schema=f'leather-primary{clip}-18-native-import-v1',manifest=str(path),manifest_sha256=sha(path),namespace=ns,actual_count=0,saved_count=0,expected_count=18,assets=[],success=False,formal_complete_units=0,assembly_freeze=d['assembly_freeze'],runtime_verified=False,motion_accepted=False,scope='New armor3 components only; integer fit eligible for native trial, original24body layers unchanged; full unit unaccepted')
 out=R/'UnrealGame/Saved/Bootstrap'/f'leather-primary{clip}-combo-v001-import-{datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")}.json'
 try:
  tasks=[]
  for x in d['assets']:
   require(not unreal.EditorAssetLibrary.does_asset_exist(x['package_path']),'Object collision');task=unreal.AssetImportTask()
   for k,v in [('filename',x['source']),('destination_path',ns),('destination_name',x['name']),('automated',True),('save',False),('replace_existing',False)]:task.set_editor_property(k,v)
   tasks.append(task)
  unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
  for x,t in zip(d['assets'],tasks):
   require(list(t.get_editor_property('imported_object_paths'))==[x['object_path']],'Wrong imported object');tex=unreal.load_asset(x['package_path']);require(isinstance(tex,unreal.Texture2D) and [tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]==[512,512],'Wrong Texture2D/canvas')
   for k,v in [('compression_settings',unreal.TextureCompressionSettings.TC_EDITOR_ICON),('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS),('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI),('never_stream',True),('srgb',True)]:tex.set_editor_property(k,v);require(tex.get_editor_property(k)==v,'Texture setting changed')
   receipt['actual_count']+=1
  verify_old()
  for x in d['assets']:
   tex=unreal.load_asset(x['package_path']);require(unreal.EditorAssetLibrary.save_loaded_asset(tex,False),'Save failed');p=disk/(x['name']+'.uasset');require(p.is_file() and p.stat().st_size>0,'Package missing');actual={**x,'actual_object_type':tex.get_class().get_name(),'saved_uasset':str(p),'saved_bytes':p.stat().st_size,'saved_sha256':sha(p)};receipt['assets'].append(actual);all_saved.append(actual);receipt['saved_count']+=1
  require(set(unreal.EditorAssetLibrary.list_assets(ns,recursive=True,include_folder=False))=={x['object_path'] for x in d['assets']},'Registry mismatch');require({p.name for p in disk.iterdir() if p.is_file()}=={x['name']+'.uasset' for x in d['assets']},'Disk set mismatch');verify_old();receipt.update(success=True,old_packages_unchanged=1115,registry_exact_set_passed=True,disk_exact_set_passed=True)
 except Exception as e:receipt['error']=str(e);raise
 finally:
  with out.open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
  unreal.log('Leather combo receipt: '+str(out))
verify_old();require(len(list((R/'UnrealGame/Content/Production').rglob('*.uasset')))==1151,'Final package count mismatch')
for x in all_saved:require(sha(x['saved_uasset'])==x['saved_sha256'],'New package changed across stages')
