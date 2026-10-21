"""Freeze two native prop candidates with actual visible roots and honest inferred footprints."""
from pathlib import Path
import ast,importlib.util,json,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
ledger=r.read(r.LEDGER);assert ledger['requested_count']==103 and ledger['current_window']['number']==5 and ledger['current_window']['requested_count']==7 and ledger['remaining_batch_requests']==17
assert not any(x['status']=='requested' for x in ledger['requests'])
props={};files=[];original_checks=[]
for key,slug,number,root,scale,footprint in[
 ('moss_low_wall','moss-low-wall',102,[256,408],260/478,[[31,365],[483,365],[495,410],[17,410]]),
 ('old_city_stele','old-city-stele',103,[256,431],.18,[[194,411],[343,420],[316,436],[171,425]])]:
 report=P/f'reviews/{slug}-processing-v001.json';source=r.read(report);path=Path(source['path']);im=Image.open(path)
 assert r.sha(path)==source['sha256'] and im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
 assert all(im.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
 assert math.isfinite(scale) and scale>0 and im.getpixel(tuple(root))[3]>=128,(key,root,im.getpixel(tuple(root)))
 copies=r.archive(path,path.relative_to(P),'frozen_scene_prop_candidate_actual_pixels_roots_not_runtime_acceptance');assert len(copies)==4 and all(r.sha(Path(x))==source['sha256'] for x in copies)
 entry=next(x for x in ledger['requests'] if x['request_number']==number)
 for p in[entry['tool_original_path'],entry['raw_path']]+entry['archive_paths']:assert r.sha(Path(p))==entry['sha256']
 original_checks.append({'request':number,'verified_source_tool_and_F_E_paths':6,'raw_sha256':entry['sha256']})
 bbox=list(im.getchannel('A').getbbox());row={'path':str(path),'sha256':source['sha256'],'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':[0]*4,
  'actual_source_bbox_px':bbox,'root_px':root,'root_sample_rgba':list(im.getpixel(tuple(root))),'root_measurement':'manual_actual_visible_front_contact_point; boundary_uncertainty2sourcepx',
  'uniform_scale':scale,'ground_footprint_px':footprint,'footprint_measurement':'inferred','hidden_footprint_verified':False,
  'frozen':True,'status':'importable_visual_candidate_pending_real_foundation_or_runtime_alignment','runtime_verified':False,
  'source_geometry_processing':'whole_native1254square_to512square_uniform_only; no_crop_bboxfit_translation_or_anisotropic_stretch',
  'display_canvas_logical_px':[512*scale,512*scale],'display_actual_bbox_logical_px':[(bbox[2]-bbox[0])*scale,(bbox[3]-bbox[1])*scale],
  'processing_report_path':str(report),'processing_report_sha256':r.sha(report),
  'source_provenance':{'request_number':number,'raw_path':entry['raw_path'],'raw_sha256':entry['sha256'],'tool_original_path':entry['tool_original_path'],'tool_original_sha256':entry['sha256'],
    'prompt_path':entry['prompt_path'],'prompt_sha256':r.sha(Path(entry['prompt_path'])),'references':entry['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0}}
 if key=='moss_low_wall':
  opaque_column_counts=[sum(im.getpixel((x,y))[3]>=200 for y in range(360,411)) for x in range(24,489)];assert min(opaque_column_counts)>0
  row.update(actual_visible_front_contact_root_px=root,actual_visible_front_contact_segment_px=[[17,410],[495,410]],visible_front_contact_core_segment_px=[[20,409],[492,409]],
   measured_front_span_source_px=478,front_span_logical_px=478*scale,source_top_depth_px=45,source_front_height_px=70,manual_plane_measurement_uncertainty_source_px=5,
   source_plane_measurement_kind='visible_top_and_front_plane_approximate_manual_measurements_not_hidden_ground_surface',
   predicted_top_depth_logical_px=45*scale,predicted_front_height_logical_px=70*scale,
   source_foundation_opaque_columns_checked=465,source_foundation_min_opaque_pixels_per_column=min(opaque_column_counts),source_foundation_no_full_depth_transparent_gap=True,
   existing_world_aabb_cm={'xmin':-1100,'xmax':-700,'ymin':60,'ymax':160},world_ground_anchor_cm=[-900,60],world_ground_anchor_kind='existing_AABB_near_edge_front_center_derived_arithmetic_not_new_collision',
   runtime_composition_route='root_draws_existing_stone_floor_texture_foundation_over_actual_shared_XY_AABB; prop102_is_only_facade_plus_top_overlay',
   foundation_texture_path=str(P.parent/'room-art-v001/processed/dungeon-floor-tile-512-v001.png'),foundation_texture_sha256=r.sha(P.parent/'room-art-v001/processed/dungeon-floor-tile-512-v001.png'),
   requested_footprint_depth_logical_px=38,requested_visual_height_logical_px=24,full_AABB_footprint_alignment_ready=False,
   limitations=['The native top is~45sourcepx and front~70sourcepx: at260/478 scale this is~24.48deep/~38.08high, not requested38deep/24high.',
    'Hidden back ground corners are inferred; this image cannot certify the existing400x100cmAABB footprint. Preserve actual ground foundation separately.',
    'The rendered alpha bbox is slightly wider than manually measured478px front span due to contour/AA; bbox width~263.26logical, about1.63px eachside beyond260.',
    'Actual front-contact root maps to existing(-900,60) near edge, not AABBcenter(-900,110); renderer must honor the declared anchor.',
    'Small chips/moss are visual only. Continuous opaque foundation confirmed in source; this does not implement collision or certify actor occlusion.'])
 else:
  row.update(actual_visible_front_contact_root_px=root,visible_front_contact_segment_px=[[171,425],[316,436]],world_ground_anchor_cm=[-920,300],world_interaction_anchor_cm=[-920,300],
   world_ground_anchor_kind='existing_investigation_anchor_no_new_collision',source_footprint_max_span_px=[172,25],source_footprint_trial_logical_px=[172*scale,25*scale],
   readable_carving='actual_recessed_sun_crest_and_three_short_illegible_chisel_mark_rows; no_modern_UI_text',
   limitations=['Back-left base contact is occluded/inferred; footprint is a visual estimate, not a new obstacle or interaction radius.',
    'Source~182x316visiblebbox at.18 is~32.76x56.88logical; legibility at runtime remains to be seen.',
    'Carved crest/marks are original visual candidates, not a user-approved city heraldry or translated inscription. Existing game interaction/UI status remains authoritative.'])
 props[key]=row;files.append({'path':str(path),'sha256':source['sha256']})
 # Diagnostic geometry on actual image pixels; never used as delivered texture.
 review=Image.new('RGB',(512,512),(35,41,45));review.paste(im,(0,0),im);d=ImageDraw.Draw(review)
 for x in range(0,512,32):d.line((x,0,x,511),fill=(48,60,60));d.text((x+1,1),str(x),fill='white')
 for y in range(0,512,32):d.line((0,y,511,y),fill=(48,60,60));d.text((1,y+1),str(y),fill='white')
 d.line(footprint+[footprint[0]],fill=(0,210,220),width=1);d.line((root[0]-7,root[1],root[0]+7,root[1]),fill=(255,230,90),width=2);d.line((root[0],root[1]-7,root[0],root[1]+7),fill=(255,230,90),width=2)
 d.text((8,80),f'{key} ACTUAL PIXELS / ROOT; CYAN FOOTPRINT INFERRED',fill='white')
 q=P/f'reviews/{slug}-manual-root-footprint-v001.png';assert not q.exists();review.save(q);r.archive(q,q.relative_to(P),'actual_prop_pixel_root_diagnostic_with_explicit_inferred_footprint_not_game_capture')
assert len(files)==len({x['sha256'] for x in files})==2
manifest={'schema':'frozen-scene-exploration-props-v1','version':1,'frozen':True,'status':'two_native_visual_candidates; foundation_composition_and_runtime_unfulfilled','props':props,
 'actual_unique_PNGs':2,'engine_destination_suggestion':'/Game/Production/SceneExploration/v001',
 'suggested_asset_names':{'moss_low_wall':'T_scene_moss_low_wall_v001','old_city_stele':'T_scene_old_city_stele_v001'},
 'coordinate_contract':'source xright/ydown; actual world+Yfar projectsup; apply one declared uniformscale only; root_px maps to each declared world_ground_anchor_cm',
 'collision_and_interaction_authority':'existingActor/worldonly; sourcealpha,bbox,inferredfootprint never creates or modifies collision/interaction',
 'mirror_or_repeat':'none_for_these_stationary_props; no_runtime_anisotropic_stretch','new_native_calls_this_task':2,'allowed_native_calls_this_task':2,
 'generation_accounting_snapshot':{'authoritative_ledger_path':str(r.LEDGER),'requested_count':103,'current_window':ledger['current_window'],'remaining':17,'pending':0},
 'original_source_C_F_E_verification':original_checks,'F_E_texture_copies_verified':8,'host_native_fee_usd':None,'external_api_calls':0,
 'runtime_verified':False,'full15_target_complete':False}
q=P/'manifests/import-scene-exploration-props-v001.json';q.parent.mkdir(exist_ok=True);assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_two_prop_native_source_contract_honest_wall_plane_mismatch_and_runtime_boundaries')
audit=P/'reviews/import-scene-exploration-props-v001-verification.json';r.write(audit,{'manifest_path':str(q),'manifest_sha256':r.sha(q),'files':files,'RGBA512_alpha_corners_hash_pass':True,
 'source_C_F_E_raw_paths_verified':12,'F_E_texture_copies_verified':8,'source_foundation_opaque_column_gate_pass':True,'wall_full_AABB_alignment_pass':False,'engine_executed':False,'errors':[]});r.archive(audit,audit.relative_to(P),'actual_source_texture_pixel_and_hash_verification_not_hidden_footprint_alignment')
for script in sorted(P.glob('*.py')):ast.parse(script.read_text('utf-8'));r.archive(script,Path('scripts')/script.name,'source_processing_bookkeeping_and_geometry_measurement_script')
for number in[102,103]:
 e=next(x for x in ledger['requests'] if x['request_number']==number);e.update(status='scene_prop_source_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),
  review_notes='Task2/2nativecallscomplete.512RGBAwholecanvasonly/manualfrontroots. Wallactual478span260logicalviaone260/478scale; top45/front70planesdeviatefromtarget, sharedrealAABBfloorfoundationrouteapprovedbyroot. Stele.18smallcarvedoldcitystone. Hiddenfootprintsnotverified, noEngine/collisionchange.')
ledger.setdefault('derived_deliveries',[]).append({'kind':'scene_exploration_wall_and_stele_candidate','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'actual_unique_PNGs':2,'new_generation_calls':2,'runtime_verified':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'props':{k:{a:v[a] for a in['path','sha256','actual_source_bbox_px','root_px','uniform_scale','ground_footprint_px','footprint_measurement']} for k,v in props.items()},
 'requested_count':103,'window5_used':7,'remaining':17,'task_calls':2,'pending':0,'source_pixel_gate':True,'hidden_wall_footprint_verified':False}))
