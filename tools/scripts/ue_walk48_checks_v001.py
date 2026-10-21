"""Stdlib-only exact48 frozen-source/native-receipt checks; no asset mutation."""
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame').resolve()
CANDIDATE=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-import-candidate-v001'
MANIFEST=CANDIDATE/'import-walk48-v001.json'
MANIFEST_SHA='0098a1f16d99c59a55c2e7b43d9709a4d3c71d9fc14a5d148b84326b57f1f680'
NAMESPACE='/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk'
DISK=ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v016/HeroLeatherWalk'
PRODUCTION=ROOT/'UnrealGame/Content/Production'
COMPONENTS={'Body':'RevisedWhole','BodyRest':'BodyLayers/BodyRest','NearArmWithoutHand':'BodyLayers/NearArmWithoutHand',
 'HelmetForeground':'BodyLayers/HelmetForeground','NearHand':'BodyLayers/NearHand','ShoulderFar':'Armor/FarShoulder','Chest':'Armor/Chest','ShoulderNear':'Armor/NearShoulder'}
def require(value,why):
 if not value:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(x):
 p=Path(x['path']).resolve();require(p.is_relative_to(ROOT) and p.is_file(),'Pinned path missing/outside project: '+str(p))
 require(p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Pinned file changed: '+str(p));return p
def document():
 require(sha(MANIFEST)==MANIFEST_SHA,'Unique48 manifest changed');return load(MANIFEST)
def old_rows(d):
 rows=load(pin(d['old_inventory']))['files'];require(len(rows)==d['old_file_count']==1151,'Current frozen old inventory/count changed');return rows
def verify_old(d):
 rows=old_rows(d)
 for x in rows:
  p=ROOT/x['path'];require(p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Old Production file changed: '+str(p))
 return len(rows)
def exact_disk_set(d,imported):
 current={p.relative_to(ROOT).as_posix() for p in PRODUCTION.rglob('*') if p.is_file()}
 expected={x['path'] for x in old_rows(d)}
 if imported:expected.update((DISK/(x['name']+'.uasset')).relative_to(ROOT).as_posix() for x in d['assets'])
 require(current==expected,'Actual all-Production file set differs from frozen old + exact48')
 require(len(current)==(1199 if imported else 1151),'Wrong all-Production file count')
 if imported:
  require({p.name for p in DISK.rglob('*') if p.is_file()}=={x['name']+'.uasset' for x in d['assets']},'Target disk exact48 set differs')

def preflight(require_unused=True):
 d=document();require(d['frozen'] and d['asset_count']==48 and len(d['assets'])==48 and d['namespace']==NAMESPACE,'Wrong48 namespace/count')
 require(d['canvas_px']==[512,512] and d['durations_ms']==[83]*6 and d['cycle_seconds']==.498
  and d['cycle_distance_world_units_art_tuned']==80. and not d['movement_speed_changed'],'Canvas/tuning scope changed')
 require(d['body_canvas_size']==72*512/416 and d['independent_sword_scale']==.5 and d['native_facing']==1,'Presentation scale changed')
 require(d['import_permitted_for_root_native_trial'] and not d['replace_existing'] and not d['runtime_verified']
  and not d['full_motion_accepted'] and d['formal_complete_units']==0,'Import scope/authority changed')
 require(d['source_to_runtime_component']==COMPONENTS,'Component map changed')
 for ref in d['references'].values():pin(ref)
 assembly=load(d['references']['assembly_freeze']['path'])
 for x in assembly['files']:pin(x)
 proof=load(d['references']['source_pixel_proof']['path']);markers=load(d['references']['markers']['path'])
 require(proof['import_candidate_png_count']==48 and proof['import_breakdown']=={'armor18':18,'exclusive_body_layers':24,'revised_whole6':6},'Assembly source set changed')
 for b in proof['body6']:
  require(all(b[k]==0 for k in ['outside_oldhandmask_union_newhandalpha_RGBA_mismatch_pixels','four_layers_revisedwhole_RGBA_mismatch_pixels',
   'exclusive_owner_mask_pair_intersection_pixels','exclusive_layer_alpha_pair_intersection_pixels']),'Frozen body closure proof changed')
 require({(x['component'],x['frame']) for x in d['assets']}=={(c,i) for c in COMPONENTS for i in range(6)},'Missing/duplicate component phase')
 require(len({x['source'] for x in d['assets']})==len({x['object_path'] for x in d['assets']})==48,'Nonunique48 source/destination')
 decoder=Path(__file__).with_name('walk_png_decoder_v001.py')
 require(sha(decoder)=='6e3ce8d6884a32499ffa9cbf14c848b4e43ec58f9183e14df679f803e109caa3','Pinned stdlib decoder changed')
 spec=importlib.util.spec_from_file_location('walk48_png_decoder',decoder);dec=importlib.util.module_from_spec(spec);spec.loader.exec_module(dec)
 source_root=Path(d['references']['assembly_freeze']['path']).parent/'import-candidate-48'
 require({p.resolve() for p in source_root.rglob('*.png')}=={Path(x['source']).resolve() for x in d['assets']},'Actual PNG set differs from unique48 manifest')
 for x in d['assets']:
  p=Path(x['source']).resolve();expected=(source_root/COMPONENTS[x['component']]/f'frame-{x["frame"]}.png').resolve()
  require(p==expected and p.stat().st_size==x['source_bytes'] and sha(p)==x['source_sha256'],'Frozen PNG changed: '+str(p))
  name=f'T_Fairytale_Walk_{x["component"]}_{x["frame"]:03d}_v001'
  require((x['name'],x['package_path'],x['object_path'])==(name,NAMESPACE+'/'+name,NAMESPACE+'/'+name+'.'+name),'Destination identity changed')
  info=dec.inspect_rgba_png(p.read_bytes());require(info['nonempty'] and info['corners_transparent'] and info['alpha_extrema']==[0,255],'Invalid native RGBA source')
  require(info['rgba_sha256']==x['source_rgba_sha256'] and info['bbox_px']==x['source_bbox'],'Decoded RGBA/bbox changed')
 for i,m in enumerate(markers['frames']):
  phase=d['phases'][i];require(phase['frame']==i and phase['duration_seconds']==.083 and phase['root_display_canvas_px']==m['ground_pivot_px']
   and phase['grip_artist_design_canvas_px']==m['Grip_canvas_px'] and phase['axis_artist_design_screen_xy']==m['Axis_artist_bladehold_screen_xy'],'Profile marker changed')
  require(phase['object_paths']=={x['component']:x['object_path'] for x in d['assets'] if x['frame']==i},'Profile object-path map differs from unique48 assets')
 if require_unused:
  require(not DISK.parent.exists() or not any(p.is_file() for p in DISK.parent.rglob('*')),'New v016 namespace already has disk files; no replacement')
  exact_disk_set(d,False)
 verify_old(d);verify_old(d)
 return d

def verify_receipt(path):
 d=preflight(False);r=load(path)
 require(r['success'] and r['manifest_sha256']==MANIFEST_SHA and r['actual_count']==r['saved_count']==48
  and r['old_files_unchanged']==1151 and r['old_verification_passes_after']==2,'Native48 receipt not successful')
 require(len(r['assets'])==48 and {x['object_path'] for x in r['assets']}=={x['object_path'] for x in d['assets']},'Receipt exact48 set differs')
 for x in r['assets']:
  p=Path(x['saved_uasset']).resolve();require(p==DISK/(x['name']+'.uasset') and p.stat().st_size==x['saved_bytes'] and sha(p)==x['saved_sha256'],'Saved new package changed')
 exact_disk_set(d,True);verify_old(d);verify_old(d)
 return {'native_receipt_verified':True,'saved48':48,'old1151_two_passes_unchanged':True,'total_files':1199,'manifest_sha256':MANIFEST_SHA}

if __name__=='__main__':
 if '--verify-receipt' in sys.argv:result=verify_receipt(sys.argv[sys.argv.index('--verify-receipt')+1])
 else:
  preflight();result={'source_preflight':True,'sources':48,'decoded_RGBA_hashes':48,'old_files_unchanged':1151,'old_verification_passes':2,'namespace_unused':True,'manifest_sha256':MANIFEST_SHA,'UE_started':False}
 print(json.dumps(result,ensure_ascii=False))
