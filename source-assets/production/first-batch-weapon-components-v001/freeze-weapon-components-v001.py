"""Freeze four distinct actual neutral components and measured physical sockets."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
processed_path=P/'processed/neutral-props-v002/processing-report.json';processed=r.read(processed_path)
measure_path=P/'reviews/component-socket-measurement-candidate-v002.json';measured=r.read(measure_path)
weapons={};files=[]
for row in processed['weapons']:
    family=row['family'];m=measured['weapons'][family];p=Path(row['path']);assert r.sha(p)==row['sha256']==m['sha256']
    image=Image.open(p);assert image.mode=='RGBA' and image.size==(512,512) and image.getchannel('A').getextrema()==(0,255)
    assert all(image.getpixel(pt)[3]==0 for pt in [(0,0),(511,0),(0,511),(511,511)])
    assert row['opaque_magenta_fraction']==0 and row['erased_non_chroma_pixels_native']==0
    for key in ['primary_grip_px','support_grip_px']:assert image.getpixel(tuple(m[key]))[3]>=245
    if m['emit_px'] is not None:
        assert image.getpixel(tuple(m['emit_px']))[3]==0
        assert image.getpixel(tuple(m['emit_surface_px']))[3]>=245
    if m['tip_px'] is not None:assert image.getpixel(tuple(m['tip_px']))[3]>0
    copies=r.archive(p,p.relative_to(P),'frozen_neutral_component_physical_sockets_candidate_not_body_action_acceptance')
    assert len(copies)==4 and all(r.sha(Path(q))==row['sha256'] for q in copies)
    entry=next(x for x in r.read(r.LEDGER)['requests'] if x['request_number']==row['request_number'])
    raw=Path(entry['raw_path']);prompt=Path(entry['prompt_path']);assert r.sha(raw)==entry['sha256']
    assert len(entry['archive_paths'])==4 and all(r.sha(Path(q))==entry['sha256'] for q in entry['archive_paths'])
    assert Path(entry['tool_original_path']).exists() and r.sha(Path(entry['tool_original_path']))==entry['sha256']
    r.archive(prompt,prompt.relative_to(P),'frozen_original_neutral_weapon_generation_prompt')
    diagnostic=Path(m['diagnostic']);r.archive(diagnostic,diagnostic.relative_to(P),'reviewed_actual_physical_socket_diagnostic_only')
    item={**copy.deepcopy(row),**copy.deepcopy(m),'frame_count':1,'state':'neutral_empty_static_component',
       'manual_measurement_status':'actual_normalized_pixels_and_diagnostic_reviewed',
       'semantic_socket_review_passed':True,'static_prop_candidate_review_passed':True,
       'source_provenance':{'request_number':entry['request_number'],'backend':'image_gen.imagegen','raw_path':str(raw),'raw_sha256':r.sha(raw),
          'tool_original_path':entry['tool_original_path'],'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':entry['references'],
          'authorization_events':['EV039','EV040','EV041'],'external_api_calls':0,'host_fee_usd':None,
          'source_kind':'original_host_native_generated_candidate; no_CC0_or_external_supplier_license_inferred'},
       'source_or_socket_positions_guessed_from_prompt':False,'actor_hand_occlusion_required':True,
       'requires_paired_hand_body_pose':family in ['XBW','SPR','GSW'],
       'existing_SWD_body_actions_certified_for_this_weapon':False,'full_weapon_actions_complete':False,'runtime_verified':False}
    weapons[item['weapon_id']]=item;files.append({'path':str(p),'sha256':r.sha(p),'four_archive_copies':copies})

old_contract=P.parent/'first-unit-animation-v003/import-subset-v005.json'
old_sword=P.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png'
assert r.sha(old_sword)=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
weapons['WPN-SWD-001']={'weapon_id':'WPN-SWD-001','family':'SWD','state':'reused_existing_military_sword_component',
 'path':str(old_sword),'sha256':r.sha(old_sword),'canvas_px':[512,512],'primary_grip_px':[99,256],'support_grip_px':None,'tip_px':[482,256],'emit_px':None,
 'canonical_forward_axis':[1,0],'new_generation':False,'source_provenance_contract':str(old_contract),'source_provenance_contract_sha256':r.sha(old_contract),
 'runtime_acceptance_scope':'Existing root-owned prior SWD evidence only; this writer makes no new runtime claim.'}
assert len(weapons)==5 and len({x['sha256'] for x in weapons.values()})==5
ledger=r.read(r.LEDGER);assert ledger['requested_count']==80 and ledger['current_window']['number']==4 and ledger['current_window']['requested_count']==8
manifest={'schema':'frozen-neutral-weapon-components-import-v1','version':1,'frozen':True,
 'status':'four_distinct_neutral_prop_candidates_physical_sockets_measured; corresponding_body_motion_unfulfilled',
 'weapons':weapons,'new_runtime_texture_count':4,'reused_runtime_texture_count':1,'total_distinct_weapon_components':5,
 'new_visual_requests':[77,78,79,80],'generation_accounting':{'authoritative_ledger':str(r.LEDGER),'EV039_requested_count':80,'current_window':4,'window_requested_count':8,'window_limit':24,'remaining':16},
 'coordinate_system':'512source_image_Xright_Ydown; all new props canonical forward +X',
 'renderer_handoff':[
  'Map each family/id to its distinct component, never silently substitute the military sword for XBW/STF/SPR/GSW.',
  'Transform component primary_grip to the actual actor grip; transform support/tip/emit with that same rotation, uniform scale and translation.',
  'Mirror the assembled actor/weapon/socket geometry once about the actor ground root. Do not separately mirror the weapon again.',
  'Emit is a deliberate free-air landmark at actual visible outlet/lens. Ranged origin must follow it into world height, not default actor ground origin.',
  'Body near-hand occlusion must use actual actor hand pixels. A prop neutral component alone does not certify paired-hand placement or an attack/reload animation.',
  'Choose initial display scale/angle by actual assembled poses. No universal Sword scale is certified here; long pole/staff may require larger draw bounds than a512 actor crop.',
  'Do not change combat range, hit windows, muzzle collision, damage or resource timing from sprite dimensions.'
 ],
 'processing_report':str(processed_path),'processing_report_sha256':r.sha(processed_path),
 'socket_measurement':str(measure_path),'socket_measurement_sha256':r.sha(measure_path),
 'processing_script':str(P/'process-neutral-props-v002.py'),'processing_script_sha256':r.sha(P/'process-neutral-props-v002.py'),
 'prior_versions_retained':['neutral-props-v001_and_component_v001_retained_with_magenta_fringe','socket_candidate_v001_crossbow_lip_sample_was_in_air_corrected_in_v002'],
 'pixel_QC':{'four_real_RGBA512_PNGs':True,'transparent_corners':True,'opaque_magenta_fraction_zero':True,'native_non_chroma_erasure_zero':True,'whole1254_to512_uniform_canvas_normalization':True,
    'no_bboxfit_crop_or_individual_part_repaint':True,'all_new_grips_on_opaque_actual_material':True,'new_F_E_archive_copies_verified':16},
 'manual_review':{'four_neutral_sources_and_normalized_components_reviewed':True,'physical_socket_diagnostics_reviewed':True,
    'scope':'Static distinct silhouette and measured physical sockets only. No shoot/reload/cast/thrust/twohand swing/20combination or runtime acceptance.'},
 'full_weapon_actions_complete':False,'runtime_verified':False,'external_api_calls':0,'host_fee_usd':None}
out=P/'manifests/import-weapon-components-v001.json';assert not out.exists();r.write(out,manifest);r.archive(out,out.relative_to(P),'frozen4_neutral_weapon_components_not_complete_weapon_motion')
audit=P/'reviews/import-weapon-components-v001-verification.json';assert not audit.exists();r.write(audit,{'manifest':str(out),'manifest_sha256':r.sha(out),'new_real_files':files,
 'new_file_count':4,'reused_sword_count':1,'four_archive_copies_per_new_file':True,'five_component_hashes_distinct':True,'errors':[],'engine_executed':False})
r.archive(audit,audit.relative_to(P),'actual_neutral_component_hash_alpha_physical_socket_evidence')
for script in ['process-neutral-props-v002.py','prepare-component-socket-review-v002.py','freeze-weapon-components-v001.py']:
 r.archive(P/script,Path('scripts')/script,'frozen_neutral_component_processing_measurement_implementation')
ledger.setdefault('derived_deliveries',[]).append({'kind':'distinct_neutral_weapon_components','manifest':str(out),'sha256':r.sha(out),'recorded_utc':r.now(),'new_runtime_PNGs':4,'reused_PNGs':1,'full_actions_complete':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(out),'sha256':r.sha(out),'new_distinct_PNGs':4,'reused_sword':1,'requested_count':80,'window4_requested':8,'remaining':16,'errors':0},ensure_ascii=False))
