"""Actual66PNG/source replay/state matrices/mirror/retention verification, no engine/API."""
from pathlib import Path
import importlib.util,math,ast,json
from PIL import Image,ImageChops,ImageOps
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);skill=importlib.util.module_from_spec(s);s.loader.exec_module(skill)
cp=P/'manifests/import-XBW-common-walk-v002.json';ap=P/'manifests/import-XBW-walk-four-armors-v002.json';np=P/'manifests/XBW-walk-neutral-state-minus1-extension-v003.json'
assert r.sha(cp)=='901e9e307a0654ae8c6f8385af2a9b4be94b063e06bfde2ca77cf43db1d1deab'and r.sha(ap)=='c14a031fbd674dadb11f4a4d363f9e65e6bac2b724e39533625f2df24f59cac2'and r.sha(np)=='f7c0a4d77528b361208fd72185063ff64f0354a0ac222e27ebbac04bdf4678e1'
b=r.read(cp);a=r.read(ap);n=r.read(np);old=r.read(P/'manifests/import-XBW-common-walk-v001.json');assert a['common_body']==b['frames'];hashes=set();checks=0;matrixchecks=0;mirrors=0;replays=0;cropped=0
def png(x):
 q=Path(x['path']);assert r.sha(q)==x['sha256'];Image.open(q).verify();im=Image.open(q);assert im.mode=='RGBA'and im.size==(512,512);assert im.getchannel('A').getextrema()==(0,255)and all(im.getpixel(p)[3]==0 for p in[(0,0),(511,0),(0,511),(511,511)]);hashes.add(x['sha256']);return im
def inverse(m):
 aa,bb,c,d,e,f=m;det=aa*e-bb*d;return(e/det,-bb/det,(bb*f-e*c)/det,-d/det,aa/det,(d*c-aa*f)/det)
def point(m,p):return[m[0]*p[0]+m[1]*p[1]+m[2],m[3]*p[0]+m[4]*p[1]+m[5]]
def replay(rawpath,rawsha,box,mat):
 q=Path(rawpath);assert r.sha(q)==rawsha;src=skill.clean_edges(skill.remove_bg_magenta(Image.open(q).convert('RGBA').crop(tuple(box)),threshold=90,edge_threshold=140),depth=3);res=src.transform((512,512),Image.Transform.AFFINE,inverse(mat),resample=Image.Resampling.BICUBIC);res.putdata([p if p[3]and not(p[0]>p[1]+30 and p[2]>p[1]+30)else(0,0,0,0)for p in res.get_flattened_data()]);return res
for f in b['frames']:
 body=[png(f[k])for k in['body_far','body_support','body_near']];checks+=3;reb=body[0].copy();reb.alpha_composite(body[1]);reb.alpha_composite(body[2]);source=Image.open(f['source_body_path']).convert('RGBA');assert r.sha(Path(f['source_body_path']))==f['source_body_sha256']and reb.tobytes()==source.tobytes()
 m=f['source_body_transform_2x3'];assert m[0]==m[4]==.96 and m[1]==m[3]==0;assert math.dist(point(m,f['source_sole_px']),f['transformed_sole_px'])<1e-9 and abs(f['transformed_sole_px'][1]-472)<1e-9
 assert f['native_primary_grip_px']==old['frames'][f['index']]['native_primary_grip_px']and f['native_support_grip_px']==old['frames'][f['index']]['native_support_grip_px'];assert math.dist(point(m,f['native_primary_grip_px']),f['primary_grip_px'])<1e-9 and math.dist(point(m,f['native_support_grip_px']),f['support_grip_px'])<1e-9
 assert replay(f['raw_source_path'],f['raw_source_sha256'],f['raw_cell_box_px'],m).tobytes()==source.tobytes();replays+=1
 for st in f['weapon_state_mappings']:
  assert r.sha(Path(st['path']))==st['sha256'];mm=st['component_to_body_affine_2x3'];assert abs(math.hypot(mm[0],mm[3])-.48)<1e-9 and abs(math.hypot(mm[1],mm[4])-.48)<1e-9;assert math.dist(point(mm,st['stock_grip_px']),f['primary_grip_px'])<1e-9
  err=math.dist(point(mm,st['support_grip_px']),f['support_grip_px']);assert abs(err-st['support_alignment_error_px'])<1e-9 and err<=3.129;matrixchecks+=1
 for key,rows in a['armors'].items():
  af=rows[f['index']];transformed=Image.open(af['source_path']).convert('RGBA');assert r.sha(Path(af['source_path']))==af['source_sha256'];T=af['source_geometry_transform_2x3'];assert abs(T[0]-.96/.94)<1e-10 and T[0]==T[4]and T[1]==T[3]==0 and math.dist(point(T,[256,472]),[256,472])<1e-9
  assert replay(af['raw_source_path'],af['raw_source_sha256'],af['raw_cell_box_px'],T).tobytes()==transformed.tobytes();replays+=1
  hands=ImageChops.lighter(body[1].getchannel('A'),body[2].getchannel('A'))
  for k in['armor_far','armor_near']:
   im=png(af[k]);checks+=1;assert not ImageChops.multiply(im.getchannel('A'),hands).getbbox();assert all(x==y for x,y in zip(im.get_flattened_data(),transformed.get_flattened_data())if x[3])
  for mask in af['selection_masks'].values():assert r.sha(Path(mask['path']))==mask['sha256']and r.sha(Path(mask['source_mask_path']))==mask['source_mask_sha256']
for prefix,previews in[('body',b['previews']),('armor',a['previews'])]:
 for p in previews:assert r.sha(Path(p['path']))==p['sha256']
 keys=[None]if prefix=='body'else list(a['armors'])
 for key in keys:
  for label in['neutral','empty0','loaded3']:
   filt=lambda p:(prefix=='body'or p['armor_id']==key)
   rr=next(p for p in previews if filt(p)and p['kind']==f'{label}_right');ll=next(p for p in previews if filt(p)and p['kind']==f'{label}_left');right=Image.open(rr['path']).convert('RGBA');left=Image.open(ll['path']).convert('RGBA')
   for i in range(6):
    box=(i%3*512,i//3*512,(i%3+1)*512,(i//3+1)*512);assert ImageOps.mirror(right.crop(box)).tobytes()==left.crop(box).tobytes();mirrors+=1
assert checks==66 and len(hashes)==66 and matrixchecks==18 and mirrors==90 and replays==30
assert n['support_fit_gate_passed_all_frames']and n['support_fit_failed_frame_indices']==[]and not n['runtime_verified']and not b['footlock_certified']and not a['semantic_full_armor_acceptance']
ledger=r.read(r.LEDGER);assert ledger['requested_count']==121 and ledger['current_window']['number']==6 and ledger['current_window']['requested_count']==1
for folder in r.ARCHIVES:assert r.sha(r.LEDGER)==r.sha(folder/'generation-ledger-snapshot.json')
old_checks={P/'manifests/import-XBW-common-walk-v001.json':'7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5',P/'manifests/import-XBW-walk-four-armors-v001.json':'35b3a0cffc9fb731a40ff4a08cde7d5e89b5f7fceff67824feb08f31849e7ff4',P/'manifests/XBW-walk-neutral-state-minus1-extension-v002.json':'50905d2632020cbc475ff6e262c9074b40afc6b6bdf818d05aac0bd4df9f54c0',P.parent/'first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json':'94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe',P.parent/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json':'275794953add2f130f0b7912fa9e01a16c21e4e017957af4c4d9c7793c240d68'}
for q,digest in old_checks.items():assert r.sha(q)==digest
asts=0
for q in P.glob('*profile096*.py'):ast.parse(q.read_text('utf-8'));r.archive(q,Path('scripts')/q.name,'new096_single_native_pass_processing_or_verification_provenance');asts+=1
count=0;size=0
for folder in r.ARCHIVES:
 for f in r.read(folder/'index.json')['files']:
  assert r.sha(Path(f['source']))==f['sha256']
  for category in['原件','展示副本']:
   q=folder/category/f['relative'];assert r.sha(q)==f['sha256']and q.stat().st_size==f['bytes'];count+=1;size+=q.stat().st_size
result={'schema':'new096_XBW_walk_source_checkpoint_v1','actual_new_texture_PNGs':66,'body_PNGs':18,'armor_PNGs':48,'body_source_poses':6,'armor_pose_combinations':24,'all66_CRC_hash_RGBA512_alpha_corners_passed':True,'body_three_track_exact_reconstruction':True,'independent_native_raw_single_resampling_replays':replays,'all_original_native_body_grip_markers_preserved':True,'all_armor_layer_pixels_equal_once_transformed_native_source':True,'actual_hand_alpha_overlap_pixels':0,'extra_garment_mask_pixels_removed_for_hand_safety':28,'body_shared_scale':.96,'armor_common_raw_coordinate_change_scale':.96/.94,'all_armor_frames_same_root_centered_transform':True,'root_px':[256,472],'component_fixed_scale':.48,'all18_pose_state_error_gates_passed':True,'support_error_gate_px':3.129,'max_error_all_components_px':b['max_support_alignment_error_px'],'max_error_neutral_px':n['max_support_alignment_error_px'],'per_cell_single_mirror_comparisons':mirrors,'new_generation_calls':0,'external_API_calls':0,'ledger121_bytes_equal_prior_F_E_snapshots':True,'ledger_sha256':r.sha(r.LEDGER),'old_frozen_contract_hash_checks_unchanged':len(old_checks),'own_profile096_python_AST_passed':asts,'F_E_archive_paths_verified':count,'F_E_archive_bytes_verified':size,'F_E_hash_size_differences':0,'body_manifest_path':str(cp),'body_manifest_sha256':r.sha(cp),'armor_manifest_path':str(ap),'armor_manifest_sha256':r.sha(ap),'neutral_extension_path':str(np),'neutral_extension_sha256':r.sha(np),'UE_import_performed':False,'UE_UBT_Source_write_performed':False,'BodySize160_changed':False,'movespeed_changed':False,'runtime_grip_accepted':False,'footlock_certified':False,'full_armor_coverage_accepted':False,'complete20equipment_combinations':False,'manual_review_scope':'Bodyall3statesbothdirections; armorall24poseisolated+neutralbothdirections+state0/3rightdirection viewed. All other leftdirections pixelchecked as one mirror, not independently runtime-tested.'}
q=P/'reviews/XBW-walk-profile096-source-verification-v001.json';assert not q.exists();r.write(q,result);r.archive(q,q.relative_to(P),'actual_new096_66PNG_raw_replay_matrix_mirror_retention_pass_not_runtime');log=q.with_suffix('.log');log.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8');r.archive(log,log.relative_to(P),'actual_successful096_source_checkpoint_assertion_output');print(json.dumps(result,ensure_ascii=False,indent=2))
