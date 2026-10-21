"""Freeze a source-only review checkpoint, with real call/part/source accounting."""
from pathlib import Path
import importlib.util,json,copy
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
ledger=r.read(r.LEDGER);assert ledger['requested_count']==90 and ledger['current_window']['requested_count']==18
e90=next(e for e in ledger['requests']if e['request_number']==90)
e90.update(status='native_duplicate_cable_repair_failed_retained; derived_real_shared_panel_trial_separate',
 review_notes='90native source still retained duplicate lower cord; correction call failed and is counted. No further native request. Separate component-bake trial reuses actual opaque stock surface pixels89 in source90; raw90 and hands/feet untouched. Not source90pixel-exact reconstruction, not complete reload/runtime.',reviewed_utc=r.now())
inputs=[(86,'0 relaxed-string grasp',P/'processed/call86-single-keypose-v001/keypose-canonical512.png'),
 (87,'1 rear draw contact',P/'processed/call87-single-keypose-v001/keypose-canonical512.png'),
 (None,'2 bolt placement / shared89 panel',P/'decomposition-trials/loading-shared-panel-v002/loading-composite-reference.png'),
 (89,'3 loaded trigger hold',P/'processed/call89-single-keypose-v001/keypose-canonical512.png')]
preview=Image.new('RGB',(1024,1104),(28,34,40));small=Image.new('RGB',(640,200),(28,34,40));d=ImageDraw.Draw(preview);ds=ImageDraw.Draw(small);sources=[]
for i,(number,label,p)in enumerate(inputs):
    im=Image.open(p).convert('RGBA');assert im.size==(512,512);ox=i%2*512;oy=i//2*552;preview.paste(im,(ox,oy+25),im);d.text((ox+15,oy+5),label,fill='white')
    thumb=im.resize((160,160),Image.Resampling.LANCZOS);small.paste(thumb,(i*160,20),thumb);ds.text((i*160+5,3),f'stage{i} ref only',fill='white')
    sources.append({'stage':i,'request_number':number,'path':str(p),'sha256':r.sha(p),'canvas_px':[512,512],'runtime_frame_accepted':False})
pq=P/'reviews/XBW-four-keypose-comparison-v002.png';assert not pq.exists();preview.save(pq);r.archive(pq,pq.relative_to(P),'4static_keypose_source_comparison_not_new_animation_sheet_or_engine_proof')
sq=P/'reviews/XBW-four-keypose-160canvas-reference-v002.png';small.save(sq);r.archive(sq,sq.relative_to(P),'static_110px_approx_body_readability_reference_NOT_runtime_screenshot')
audited=[]
for e in ledger['requests']:
    if e.get('window_number',1)!=4:continue
    raw=Path(e['raw_path']);assert r.sha(raw)==e['sha256']
    assert all(r.sha(Path(x))==e['sha256'] for x in[e['tool_original_path'],*e['archive_paths']])
    audited.append({'request':e['request_number'],'raw':str(raw),'sha256':e['sha256'],'status':e['status']})
assert len(audited)==18
frozen=[]
for filename in ['import-XBW-ready-idle-v001.json','import-XBW-primary-v001.json']:
    p=P/'manifests'/filename;m=r.read(p)
    for row in m['frames']:
        for key in ['body_far','body_support','body_near']:assert r.sha(Path(row[key]['path']))==row[key]['sha256']
    frozen.append({'path':str(p),'sha256':r.sha(p),'source_body_frames':6,'body_tracks':18,'immutable_referenced_source_hashes_rechecked':True})
panel=P/'decomposition-trials/loading-shared-panel-v002/trial-report.json';pr=r.read(panel)
assert pr['outside_selection_changed_pixels']==0 and pr['entire_source90_alpha_unchanged'] and pr['every_replacement_pixel_from_actual_opaque_source89']
report={'schema':'XBW_source_keypose_and_layer_checkpoint_v2','status':'4_cartoon_state_contact_candidates_static_only; full_reload_tracks_and_runtime_unfulfilled',
 'prior_review':str(P/'reviews/XBW-four-keypose-contact-review-v001.json'),'prior_review_sha256':r.sha(P/'reviews/XBW-four-keypose-contact-review-v001.json'),
 'review_definition':'parent clarified cartoon state/contact readability, not exposing all internal junctions; original visible-cable defect remains in raw88/90',
 'cartoon_state_readability_internal_candidate_count':4,'source_mechanical_pixel_certification_claimed':False,'all_source_art_clean':False,
 'review_sources':sources,'comparison':{'path':str(pq),'sha256':r.sha(pq)},'reference_160canvas':{'path':str(sq),'sha256':r.sha(sq),'actual_engine_capture':False},
 'contact_review':['86 near hand visibly reaches front relaxed string; far hand supports.',
   '87 near hand draws deep V backward via generated small pull/latch detail; exact internal capture is unproven.',
   '88/90 loading hand and one bolt/rail contact are readable. Native duplicate-cable correction90 failed; source kept.',
   'Derived loading candidate selects real common-opaque stock panel89 in90. Source90alpha and every pixel outside that selection are unchanged; no hand/skin/body painted.',
   '89 near hand returns to stock-neck hold with one seated bolt and2visible V legs. Side lock/stock occlude internal nock; this is recorded, not pixel-certified.'],
 'shared_panel_trial':str(panel),'shared_panel_trial_sha256':r.sha(panel),'shared_panel_scope':'actual common-opaque stock surface component; no whole89prop fit, no raw90repair success claimed',
 'shared_panel_remaining_limits':['Wood-grain seam and a tiny proximal cord stroke near fletch remain presentation candidates pending running-size review.',
  'This is a two-native-source component assembly reference; it is not raw90 and not evidence that imagegen90 succeeded.'],
 'first_split_trial':str(P/'decomposition-trials/keypose86-v003/trial-report.json'),'first_split_trial_sha256':r.sha(P/'decomposition-trials/keypose86-v003/trial-report.json'),
 'first_split_scope':'4real PNG tracks body_far/weapon_core/support/near reconstruct source86exactly; semantic boundary trial not frozen/importable',
 'decomposition_boundary':'Integrated source lacks body pixels hidden by weapon. Exact visible-pixel partitions may be clip-specific coupled tracks; not a universal complete weapon-free body.',
 'tracks_for_all4_keyposes_completed':False,'expanded6frame_raw_generated':False,'complete1_10s_reload_timeline_frozen':False,'runtime_import_allowed':False,'full_reload_accepted':False,
 'frozen_existing_body_contracts':frozen,
 'additional_unfulfilled':['firing string-release/bolt weapon state','reload all-keypose semantic tracks and hand/emit markers','four armor same-pose XBW surfaces','actual runtime transitions/20equipment combinations',
   'actor D02 combat-height vs image outlet projection semantics; no direct artworkY->combatZ assumption'],
 'accounting':{'authoritative_ledger':str(r.LEDGER),'requested_count':90,'completed_native_calls':sum('raw_path'in e for e in ledger['requests']),
   'lifetime_including_separate_EV038':ledger['lifetime_requested_count'],'window_number':4,'window_requested':18,'window_limit':24,'remaining':6,'pending':0,'host_fee_usd':None,'external_API_calls':0},
 'current_window_raw_verification':{'actual_sources':18,'F_E_original_and_presentation_copies':72,'tool_originals':18,'errors':[],'sources':audited},
 'new_runtime_reload_animation_frames':0,'engine_started_by_this_writer':False,'global_code_or_UE_project_modified':False}
q=P/'reviews/XBW-four-keypose-contact-review-v002.json';assert not q.exists();r.write(q,report);r.archive(q,q.relative_to(P),'actual_cartoon_keypose_contact_scope_and_shared_native_component_trial_checkpoint')
ledger.setdefault('derived_deliveries',[]).append({'kind':'XBW_cartoon_keypose_and_actual_shared_panel_checkpoint','report':str(q),'sha256':r.sha(q),
 'recorded_utc':r.now(),'native_generation_requests_added_for_derived_work':0,'new_runtime_reload_animation_frames':0})
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(q),'sha256':r.sha(q),'source_keyposes':4,'shared_panel_no_generation':True,'requested_count':90,'remaining':6,'raws_verified':18,'native_repair90_failed':True}))
