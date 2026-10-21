"""Freeze48 actual native clothing overlays over the immutable18-body candidate."""
from pathlib import Path
import importlib.util,ast
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
src=P/'manifests/XBW-walk-four-armors-selection-candidate-v004.json';d=r.read(src);cp=Path(d['source_body_contract_path']);assert r.sha(cp)==d['source_body_contract_sha256'];body=r.read(cp)
hashes=set();copies=0
for key,rows in d['armors'].items():
 assert [f['index']for f in rows]==list(range(6))
 for f in rows:
  native=Image.open(f['source_path']).convert('RGBA');assert r.sha(Path(f['source_path']))==f['source_sha256'];protected=Image.open(f['selection_masks']['protected']['path']).convert('L')
  base=body['frames'][f['index']];hands=ImageChops.lighter(Image.open(base['body_near']['path']).getchannel('A'),Image.open(base['body_support']['path']).getchannel('A'))
  for k in ['armor_far','armor_near']:
   x=f[k];p=Path(x['path']);Image.open(p).verify();im=Image.open(p).convert('RGBA');assert r.sha(p)==x['sha256']and im.size==(512,512)and im.getchannel('A').getextrema()==(0,255)
   assert not ImageChops.multiply(im.getchannel('A'),protected).getbbox()and not ImageChops.multiply(im.getchannel('A'),hands).getbbox()
   assert all(a==b for a,b in zip(im.get_flattened_data(),native.get_flattened_data())if a[3]);assert not any(a[3]and a[0]>a[1]+30 and a[2]>a[1]+30 for a in im.get_flattened_data())
   assert all(im.getpixel(p)[3]==0 for p in[(0,0),(511,0),(0,511),(511,511)]);hashes.add(x['sha256']);copies+=len(r.archive(p,p.relative_to(P),'frozen_actual_same_pose_XBW_walk_armor_surface_candidate'))
  for x in f['selection_masks'].values():assert r.sha(Path(x['path']))==x['sha256']
  assert f['root_px']==[256,472]and f['primary_grip_px']==base['primary_grip_px']and f['support_grip_px']==base['support_grip_px']
  f.update(frozen=True,static_source_layer_candidate_reviewed=True,complete_armor=False,semantic_review_passed=False,runtime_verified=False)
assert len(hashes)==48 and copies==192
for x in d['previews']:assert r.sha(Path(x['path']))==x['sha256']
ledger=r.read(r.LEDGER);provenance=[]
for n in [118,119,120,121]:
 e=next(x for x in ledger['requests']if x['request_number']==n)
 for q in[e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(q))==e['sha256']
 report=P/f'processed/call{n}-fixed-canvas-v001/processing-report.json';assert r.read(report)['material_retention_pass']
 provenance.append({'request_number':n,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],'tool_original_sha256':e['sha256'],'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references'],'processing_report_path':str(report),'processing_report_sha256':r.sha(report)})
 e.update(status='XBW_walk_four_armor_source_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),review_notes='All24native armor/pose selections and48directional assemblies viewed afterF/E retention. Original body18/grips untouched; true ROB long sleeve source selected. Partial underclothes/cuff/shin edges remain; runtime/footlock/fullarmor false.')
d.update(schema='frozen-XBW-pose-armor-layer-subset-v1',version=1,frozen=True,status='four_armor_static_walk_layer_candidates_pending_runtime_and_coverage_acceptance',weapon_id='WPN-XBW-001',clip='walk',root_px=[256,472],duration_s=.6,loop=True,phase_intervals_s=[{'phase':'walk','start_s':0,'end_s':.6}],required_armor_tracks=['armor_far','armor_near'],missing_layer_policy='disable_variant_explicitly_never_stretch_Sword_fallback',body_track_authority='verbatim_immutable_common_walk_7185df2a',body_geometry_transform='none_relative_to_frozen_common_walk; original_common_shared0.94_alignment_recorded_in_source_contract',armor_per_frame_geometry_transform='none_native512_source_pixel_selection',mirror_policy='single_parent_horizontal_flip_for_body_armor_weapon_sockets',source_pose_time_authority='actor_actual_walk_elapsed_nominal6x0.1_no_movement_speed_change',armor_pose_combinations=24,source_generation_calls=4,source_provenance=provenance,selection_candidate_path=str(src),selection_candidate_sha256=r.sha(src),generation_accounting_snapshot={'ledger_path':str(r.LEDGER),'requested_count':ledger['requested_count'],'window':ledger['current_window'],'remaining_window_requests':ledger['remaining_batch_requests'],'new_walk_task_limit':8,'new_walk_task_used':6,'new_walk_task_remaining':2,'external_API_calls':0,'host_fee_usd':None},pixel_checks={'actual_RGBA512_PNG_CRC_hash':True,'transparent_corners':True,'native_source_pixels_only':True,'original_hand_alpha_overlap_pixels':0,'protected_head_hands_belt_excluded':True,'F_E_texture_copies_verified':copies},manual_review={'reviewer':'/root/assets_prepare','all24armor_pose_combinations_both_directions_reviewed':True,'static_assembly_candidate':True,'full_coverage_accepted':False},limitations=['Common body remains brown composite underclothes. Old collar/waist/slit/shoulder and cuff wedges can remain visible; these48overlays do not claim a naked-base full armor production.','ROB has actual long-cloth forearm sleeve pixels in ArmorNear; original distal hand/blue wrist safety margins remain. Completely sealed cuff transitions are not accepted.','HVY bent shin plates use manually revised per-pose native selections; exact complete steel coverage and source-border seams remain candidates. No old Sword armor frame was deformed.','Two common stride contact proxies and unverified body-bob/footlock carry through unchanged. No source selection pass accepts runtime ground contact.','Only visible back surface is inArmorFar; hidden back remainsnull. Six body poses are reused for24armor/pose combinations;48PNG is the two-layer count, not48new body poses.','No clip runtime/20equipment combinations/weapon emission/contact or fullunit acceptance follows from source CRC/hash/alpha checks.'],runtime_verified=False,footlock_certified=False,semantic_full_armor_acceptance=False,full_equipment_combinations_complete=False)
out=P/'manifests/import-XBW-walk-four-armors-v001.json';assert not out.exists();r.write(out,d);r.archive(out,out.relative_to(P),'frozen48_actual_XBW_walk_armor_overlays_candidate_no_runtime_claim')
ledger.setdefault('derived_deliveries',[]).append({'kind':'XBW_walk_four_armors_candidate','manifest':str(out),'sha256':r.sha(out),'actual_armor_PNGs':48,'body_PNGs_reused':18,'new_native_calls':4,'recorded_utc':r.now(),'runtime_verified':False});r.write(r.LEDGER,ledger)
for a in r.ARCHIVES:r.write(a/'generation-ledger-snapshot.json',ledger)
for f in P.glob('*.py'):ast.parse(f.read_text('utf-8'));r.archive(f,Path('scripts')/f.name,'actual_native_source_selection_provenance_script')
for f in(P/'prompts').glob('*.txt'):r.archive(f,f.relative_to(P),'handwritten_host_native_prompt')
print({'manifest':str(out),'sha256':r.sha(out),'armor_PNGs':48,'body_PNGs_reused':18,'F_E_copies':copies,'ledger':ledger['requested_count'],'task_used':6})
