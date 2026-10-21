"""Retained four-keypose contact comparison; no finished animation assertion."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
ledger=r.read(r.LEDGER);assert ledger['requested_count']==89 and ledger['current_window']['requested_count']==17
observations={
86:{'stage':'grasp_relaxed_front_string','visible_contact':'near hand contacts front near-vertical relaxed string; far hand supports foregrip','state_change':'not yet deep V, no bolt',
 'cartoon_contact_candidate_pass':True,'defect':None,'internal_mechanical_junction_visible':False,'layer_status':'integrated_source_not_decomposed'},
87:{'stage':'draw_string_back','visible_contact':'near hand draws deep-V apex backward using a generated small gray pull/latch detail; far support retained',
 'state_change':'near-vertical string has become deep V; still no bolt','cartoon_contact_candidate_pass':True,
 'defect':'raised gray pull/latch detail differs from neutral prop; exact internal capture at original rear slot not pixel-proven','internal_mechanical_junction_visible':False,'layer_status':'integrated_source_not_decomposed'},
88:{'stage':'place_one_bolt_in_rail','visible_contact':'near finger touches cream rear fletching/shaft; one bolt lies lengthwise on actual top rail; support stays on foregrip',
 'state_change':'bolt newly present; string remains drawn','cartoon_contact_candidate_pass':False,
 'defect':'extra third lower diagonal cable: both fletch-to-bow and sideplate-to-bow lines appear; one should be removed consistently with final ready state',
 'internal_mechanical_junction_visible':False,'layer_status':'integrated_source_not_decomposed'},
89:{'stage':'return_trigger_loaded_ready','visible_contact':'near hand returns to rear stock-neck grasp; far hand remains support; one seated bolt and two visible V legs',
 'state_change':'loading hand has left rail and resumed holding; extra third cable from88 removed','cartoon_contact_candidate_pass':True,
 'defect':'nock/string internal meeting remains occluded by side lock/stock; cannot claim pixel proof of a hidden point, not itself a regeneration requirement',
 'internal_mechanical_junction_visible':False,'layer_status':'integrated_source_not_decomposed'}}
rows=[]
for number,obs in observations.items():
    e=next(x for x in ledger['requests'] if x['request_number']==number);raw=Path(e['raw_path']);assert r.sha(raw)==e['sha256']
    assert all(r.sha(Path(x))==e['sha256'] for x in [e['tool_original_path'],*e['archive_paths']])
    canonical=P/f'processed/call{number}-single-keypose-v001/keypose-canonical512.png';im=Image.open(canonical);assert im.size==(512,512) and im.mode=='RGBA'
    crop=P/f'reviews/XBW-mechanical-contact-{number}-native-crop-v001.png';assert crop.exists()
    r.archive(Path(e['prompt_path']),Path(e['prompt_path']).relative_to(P),'four_single_keypose_native_prompt_history')
    rows.append({'request_number':number,'raw_path':str(raw),'raw_sha256':e['sha256'],'raw_canvas_px':e['image_size'],
     'canonical_path':str(canonical),'canonical_sha256':r.sha(canonical),'canonical_canvas_px':[512,512],
     'normalization':'whole_canvas_uniform512/1254_no_bboxfit_no_crop_no_translation','native_crop':str(crop),'native_crop_sha256':r.sha(crop),
     'F_E_C_raw_original_hashes_verified':True,'source_contains_visible_weapon':True,'runtime_animation_frames_certified':0,**obs})
current=[]
for e in ledger['requests']:
    if e.get('window_number',1)!=4:continue
    raw=Path(e['raw_path']);assert r.sha(raw)==e['sha256'];assert len(e['archive_paths'])==4
    assert all(r.sha(Path(x))==e['sha256'] for x in [e['tool_original_path'],*e['archive_paths']])
    current.append({'request':e['request_number'],'raw':str(raw),'sha256':e['sha256'],'status':e['status']})
assert len(current)==17
contract={'schema':'XBW_four_native_mechanical_keypose_contact_review_v1','status':'three_readable_contact_candidates_one_extra_cable_correction_pending_not_reload_animation',
 'art_review_standard':'cartoon mechanical readability of relaxed_string->draw_back->place_bolt->return_hold; invisible internal lock does not need to be simultaneously exposed',
 'source_keypose_count':4,'source_requests':[86,87,88,89],'rows':rows,'all_four_clean_contact_gates_pass':False,'readable_candidate_count':3,
 'no_six_frame_reload_sheet_expanded':True,'no_runtime_body_or_weapon_tracks_frozen_from_these_keyposes':True,'runtime_animation_frame_count_new':0,
 'known_minimum_visual_correction':[{'request_source':88,'scope':'one single-keypose native edit; remove duplicate lower cable to match89 while keeping loading hand/bolt/stock/boots',
    'reason':'visible duplicate cable, not a requirement to expose occluded internal nock','expected_generation_requests':1,'not_executed_in_this_report':True}],
 'decomposition_proposal':{
   'source_route':'weapon-specific integrated native source, then exact visible-pixel semantic masks; explicitly not a generic complete weapon-free body',
   'body_tracks':['body_far','body_support','body_near'],
   'weapon_tracks':['weapon_core_and_far_string','optional_weapon_front_string_only_if_actual_source_occlusion_requires_it'],
   'draw_order_candidate':['body_far','weapon_core_and_far_string','body_support','body_near','optional_weapon_front_string'],
   'mask_requirement':'actual native pixels only; disjoint masks; RGBA reconstruction must match source exactly; no skin/cloth hidden under weapon is painted or inferred',
   'missing_regions':'body pixels occluded by bow/string are unavailable; clip-specific coupled tracks must cover those regions and cannot be advertised as freely swappable universal body',
   'geometry':'all output tracks512samecanvas; whole source1254->512 uniform only; no perpart fit/scaling, limb repaint or hand redrawing',
   'markers':'measure actual per-pose primary/support visible grasp contacts and outlet after selection; weapon source landmarks/affine shared with Emit; these new integrated geometries do not inherit neutral-prop affine automatically',
   'mirror':'assemble canonical right and apply exactly one shared mirror; never separately regenerate left',
   'timing':'four static keyposes have no certified complete1.10s reload timeline; actual actor reload clock/grounding/cancellation authority unchanged',
   'armor':'four armor same-pose surfaces are unfulfilled for this weapon-specific action; old SWD armor clips cannot silently be reused',
   'world_emit':'image outlet is presentation geometry; no automatic addition to combat Z or proof of D02 target-height semantics'},
 'accounting':{'authoritative_ledger':str(r.LEDGER),'requested_count':89,'actual_completed_native_calls':sum('raw_path' in x for x in ledger['requests']),
   'window_number':4,'window_requested':17,'window_limit':24,'remaining':7,'pending_requests':0,'host_fee_usd':None,'external_api_calls':0},
 'current_window_raw_audit':{'sources_verified':17,'F_E_original_and_presentation_copies_verified':68,'tool_originals_verified':17,'files':current},
 'engine_executed_by_this_writer':False,'full_reload_accepted':False,'formal_art_acceptance':False}
q=P/'reviews/XBW-four-keypose-contact-review-v001.json';assert not q.exists();r.write(q,contract);r.archive(q,q.relative_to(P),'four_single_keypose_actual_contact_comparison_and_unfulfilled_decomposition_gate')
e=next(x for x in ledger['requests'] if x['request_number']==89);e.update(status='loaded_ready_two_string_legs_contact_candidate_hidden_nock_unproven',
 review_notes='Near hand returns to rear stock grasp, one bolt and2visible V legs; third cable removed. Internal meeting behind side lock/stock not pixel-proven and not itself a requirement to redraw. Four-keypose comparison has one remaining visible extra-cable defect88; no expanded sheet or runtime acceptance.',reviewed_utc=r.now())
ledger.setdefault('derived_deliveries',[]).append({'kind':'four_single_mechanical_keypose_contact_review','report':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),
 'native_keyposes':4,'runtime_animation_frames_new':0,'full_reload_accepted':False})
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'review':str(q),'sha256':r.sha(q),'readable_candidates':3,'needs_single_extra_cable_correction':88,'raw_sources_verified':17,'requested_count':89,'remaining':7}))
