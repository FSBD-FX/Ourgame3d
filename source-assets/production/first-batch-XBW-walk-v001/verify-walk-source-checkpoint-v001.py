"""Read actual PNGs, anatomy selections, matrices and four retention copies. No engine."""
from pathlib import Path
import importlib.util,ast,math,json
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
def png(x):
 p=Path(x['path']);assert r.sha(p)==x['sha256'];Image.open(p).verify();im=Image.open(p).convert('RGBA');assert im.size==(512,512)and im.getchannel('A').getextrema()==(0,255)and all(im.getpixel(q)[3]==0 for q in[(0,0),(511,0),(0,511),(511,511)]);return im
def pt(m,p):return[m[0]*p[0]+m[1]*p[1]+m[2],m[3]*p[0]+m[4]*p[1]+m[5]]
bodypath=P/'manifests/import-XBW-common-walk-v001.json';armorpath=P/'manifests/import-XBW-walk-four-armors-v001.json';neutralpath=P/'manifests/XBW-walk-neutral-state-minus1-extension-v002.json'
assert r.sha(bodypath)=='7185df2ad077ec92d020788f84f2f9b890dc7d042ceb7656d0a9576177d471a5';assert r.sha(armorpath)=='35b3a0cffc9fb731a40ff4a08cde7d5e89b5f7fceff67824feb08f31849e7ff4';assert r.sha(neutralpath)=='50905d2632020cbc475ff6e262c9074b40afc6b6bdf818d05aac0bd4df9f54c0'
b=r.read(bodypath);a=r.read(armorpath);n=r.read(neutralpath);assert a['common_body']==b['frames'];bodyhashes=set();armorhashes=set();bodychecks=0;armorchecks=0
for f in b['frames']:
 parts=[png(f[k])for k in['body_far','body_support','body_near']];rebuilt=parts[0].copy();rebuilt.alpha_composite(parts[1]);rebuilt.alpha_composite(parts[2]);assert r.sha(Path(f['source_body_path']))==f['source_body_sha256'];assert rebuilt.tobytes()==Image.open(f['source_body_path']).convert('RGBA').tobytes()
 for k in['body_far','body_support','body_near']:bodyhashes.add(f[k]['sha256']);bodychecks+=1
 m=f['source_body_transform_2x3'];assert m[0]==.94 and m[4]==.94 and m[1]==m[3]==0;assert math.dist(pt(m,f['native_primary_grip_px']),f['primary_grip_px'])<1e-9
 assert math.dist(pt(m,f['native_support_grip_px']),f['support_grip_px'])<1e-9 and f['root_px']==[256,472]
 for state in f['weapon_state_mappings']:
  assert r.sha(Path(state['path']))==state['sha256'];mm=state['component_to_body_affine_2x3'];assert math.dist(pt(mm,state['stock_grip_px']),f['primary_grip_px'])<1e-9
  error=math.dist(pt(mm,state['support_grip_px']),f['support_grip_px']);assert abs(error-state['support_alignment_error_px'])<1e-9 and error<=3.129
 for key,rows in a['armors'].items():
  af=rows[f['index']];native=Image.open(af['source_path']).convert('RGBA');assert r.sha(Path(af['source_path']))==af['source_sha256'];hands=ImageChops.lighter(parts[1].getchannel('A'),parts[2].getchannel('A'))
  for k in['armor_far','armor_near']:
   im=png(af[k]);assert not ImageChops.multiply(im.getchannel('A'),hands).getbbox();assert all(x==y for x,y in zip(im.get_flattened_data(),native.get_flattened_data())if x[3]);armorhashes.add(af[k]['sha256']);armorchecks+=1
  for mask in af['selection_masks'].values():assert r.sha(Path(mask['path']))==mask['sha256']
for f in n['frames']:
 assert f['primary_grip_px']==b['frames'][f['index']]['primary_grip_px']and f['support_grip_px']==b['frames'][f['index']]['support_grip_px'];assert r.sha(Path(f['component_path']))==f['component_sha256'];error=math.dist(pt(f['component_to_body_affine_2x3'],f['component_support_grip_px']),f['support_grip_px']);assert abs(error-f['support_alignment_error_px'])<1e-9;assert f['support_fit_gate_passed']==(error<=3.129)
assert n['support_fit_failed_frame_indices']==[2,4,5]and not n['support_fit_gate_passed_all_frames']and not n['neutral_grip_accepted']and not n['runtime_verified']
assert len(bodyhashes)==18 and len(armorhashes)==48 and bodychecks==18 and armorchecks==48
ledger=r.read(r.LEDGER);assert ledger['requested_count']==121 and ledger['current_window']['number']==6 and ledger['current_window']['requested_count']==1;assert not any(e['status']=='requested'for e in ledger['requests']);rawpaths=0
for e in ledger['requests']:
 if 116<=e['request_number']<=121:
  for q in[e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(q))==e['sha256'];Image.open(q).verify();rawpaths+=1
  for x in e['references']:assert r.sha(Path(x['path']))==x['sha256']
old={
 'first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json':'21c8ff90c59c411bfdbcabcfee0292881d77e4e652cc2fde46cab35e99373813',
 'first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json':'79fd2508eabfdab26f4dcb1cc21682d08b2518d37bbc0111fc38655869eeb11f',
 'first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json':'9a0f99a5b32a5b898b9fa98d4b40812daf5e532a73954f13df91a7c166297ee8',
 'first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json':'94f2d3b6163f620babe8d5d550cacbeb7204ca69f8b3942ebdc27f512e72fffe',
 'first-batch-XBW-armor-layers-v001/manifests/import-XBW-primary-four-armors-v001.json':'0acc811b8633f8d3b165ea588ad38c8f95372f4bd13ab37ec7ece7174ecc0a82',
 'first-batch-XBW-armor-layers-v001/manifests/import-XBW-reload-four-armors-v001.json':'963d74e304894088492b205fb9b113b0e5b6d9acf52785724c6d400271722002',
 'first-batch-XBW-armor-layers-v001/manifests/import-XBW-ready_idle-four-armors-v001.json':'093d6b15a44dadc485b28584784c888b2df7f1a88261891632ef836e128925a1',
 'first-batch-stone-bat-v001/manifests/import-stone-bat-subset-v002.json':'de293cd758a6112e7f3d26e15821ebbb308d203c980b07a7107780254e09cf45',
 'scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json':'a6eb21c81c1c2a29ac703454ee03318604e4cf5c96bde8070540e3f8c2a5c969'}
for name,digest in old.items():assert r.sha(P.parent/name)==digest,name
asts=0
for q in P.glob('*.py'):ast.parse(q.read_text('utf-8'));r.archive(q,Path('scripts')/q.name,'frozen_source_processing_or_verification_provenance');asts+=1
retained=0;retainedbytes=0
for folder in r.ARCHIVES:
 index=r.read(folder/'index.json')
 for f in index['files']:
  source=Path(f['source']);assert r.sha(source)==f['sha256']and source.stat().st_size==f['bytes'],source
  for category in['原件','展示副本']:
   q=folder/category/f['relative'];assert r.sha(q)==f['sha256']and q.stat().st_size==f['bytes'];retained+=1;retainedbytes+=q.stat().st_size
out=P/'reviews/XBW-walk-source-verification-v001.json';assert not out.exists();result={'schema':'source-only-XBW-walk-checkpoint-verification-v1','actual_body_PNGs':18,'actual_armor_PNGs':48,'actual_total_new_texture_PNGs':66,'actual_body_source_poses':6,'actual_armor_pose_combinations':24,'body_three_track_exact_reconstruction':True,'armor_original_hand_alpha_overlap_pixels':0,'armor_native_source_pixels_preserved':True,'body_shared_scale':.94,'state0_3_fixed_component_scale':.48,'state0_3_max_support_error_px':b['max_support_alignment_error_px'],'neutral_max_error_px':n['max_support_alignment_error_px'],'neutral_failed_frame_indices':[2,4,5],'neutral_fit_accepted':False,'PNG_CRC_hash_alpha_canvas_corners_passed':True,'new_native_calls':6,'request_range':[116,121],'raw_C_source_F_E_paths_verified':rawpaths,'failed116_preserved':True,'pending':0,'ledger_requested_count':121,'window6_requested_count':1,'task_limit':8,'task_remaining_unused':2,'external_API_calls':0,'host_fee_usd':None,'old_frozen_contract_hashes_unchanged_count':len(old),'own_python_AST_passed_count':asts,'F_E_archive_paths_verified':retained,'F_E_archive_bytes_verified':retainedbytes,'F_E_SHA_size_differences':0,'body_manifest_path':str(bodypath),'body_manifest_sha256':r.sha(bodypath),'armor_manifest_path':str(armorpath),'armor_manifest_sha256':r.sha(armorpath),'neutral_extension_path':str(neutralpath),'neutral_extension_sha256':r.sha(neutralpath),'runtime_verified':False,'footlock_certified':False,'full_equipment_combinations_complete':False,'no_UE_UBT_or_external_API_run':True,'accounting_snapshot_boundary':'window005-request-source-audit-v001 and generation-ledger-after-window005-before-request121-v001 are actual transition records. generation-ledger-window005-closed-source-snapshot-v001 is a later closed-window projection with final review statuses, not an original pre121timestamped ledger.'}
r.write(out,result);r.archive(out,out.relative_to(P),'actual_source_only_checkpoint_all66PNG_and_retention_verified_neutral_three_failed_gates')
text=json.dumps(result,ensure_ascii=False,indent=2);log=P/'reviews/XBW-walk-source-verification-v001.log';log.write_text(text+'\n','utf-8');r.archive(log,log.relative_to(P),'actual_successful_source_verification_assertion_output_no_engine')
print(text)
