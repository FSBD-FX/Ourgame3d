"""Freeze a four-keypose runtime-test candidate, never certify full reload acceptance."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
cp=P/'reviews/XBW-reload-four-keypose-layer-candidate-v002.json';c=r.read(cp);ledger=r.read(r.LEDGER);files=[];frames=[]
for row in c['frames']:
 source=Image.open(row['body_source']).convert('RGBA');assert r.sha(Path(row['body_source']))==row['body_source_sha256'];rebuilt=Image.new('RGBA',(512,512));frame=copy.deepcopy(row)
 for key in ['body_far','body_support','body_near','weapon']:
  part=copy.deepcopy(row['parts'][key] if key!='weapon' else row['weapon']);p=Path(part['path']);im=Image.open(p);assert r.sha(p)==part['sha256'] and im.mode=='RGBA' and im.size==(512,512)
  assert im.getchannel('A').getextrema()==(0,255);corners=[list(im.getpixel(pt)) for pt in[(0,0),(511,0),(0,511),(511,511)]];assert all(x[3]==0 for x in corners)
  copies=r.archive(p,p.relative_to(P),'frozen_four_keypose_reload_test_candidate_not_full_action_acceptance');assert all(r.sha(Path(x))==part['sha256'] for x in copies)
  part['corner_rgba']=corners;frame[key]=part;files.append(part)
  if key!='weapon':rebuilt.alpha_composite(im)
 assert rebuilt.tobytes()==source.tobytes() and row['support_error_source_px']<1e-9 and row['manipulation_error_source_px']<2.5
 frame.pop('parts');frame['ground_root_px']=row['root_px'];frame['time_start_normalized']=row['time_start_s']/1.1;frame['time_end_normalized']=row['time_end_s']/1.1
 frame['primary_stock_grip_px']=row['body_manipulation_contact_px'] if row['index']==3 else None
 frame['primary_grip_visibility']='real_stock_hand_only_in_ready_stage3; earlier_near_hand_is_manipulator'
 frame['near_hand_roi_px']=list(Image.open(row['parts']['body_near']['path']).getchannel('A').getbbox())
 frame['support_hand_roi_px']=list(Image.open(row['parts']['body_support']['path']).getchannel('A').getbbox())
 frame['manual_grip_measurement_status']='actual_source_pixel_estimate_with_2to4px_boundary_uncertainty_not_skeletal_joint'
 frames.append(frame)
assert len(files)==len({x['path'] for x in files})==16
provenance=[]
for number in [91,92]:
 entry=next(x for x in ledger['requests'] if x['request_number']==number)
 for p in [entry['tool_original_path'],entry['raw_path']]+entry['archive_paths']:assert r.sha(Path(p))==entry['sha256']
 provenance.append({'request_number':number,'raw_path':entry['raw_path'],'raw_sha256':entry['sha256'],'tool_original_path':entry['tool_original_path'],'prompt_path':entry['prompt_path'],
  'prompt_sha256':r.sha(Path(entry['prompt_path'])),'references':entry['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0})
 r.archive(Path(entry['prompt_path']),Path(entry['prompt_path']).relative_to(P),'frozen_source_prompt')
design=Path('F:/Ourgame/docs/design/equipment-v1/weapons.json');weapon=next(x for x in r.read(design) if x['id']=='WPN-XBW-001');assert weapon['reload_s']==1.1
reviews=[]
for name in ['assembled_right','assembled_left','body_near','body_support','body_far']:
 p=P/f'reviews/XBW-reload-four-keyposes-{name}-v002.png';assert p.exists();r.archive(p,p.relative_to(P),'actual_static_four_keypose_assembly_reviewed_for_runtime_test');reviews.append({'path':str(p),'sha256':r.sha(p)})
for script in ['process-body-keyposes91-v001.py','process-weapon-states92-v001.py','assemble-XBW-reload-four-keyposes-v001.py','assemble-XBW-reload-four-keyposes-v002.py',Path(__file__).name]:
 r.archive(P/script,Path('scripts')/script,'source_preserving_processing_and_manual_semantic_selection_script')
# Frozen primary/idle source hashes are checked, never revised by this candidate.
prior=[]
for name in ['import-XBW-ready-idle-v001.json','import-XBW-primary-v001.json']:
 p=P/'manifests'/name;j=r.read(p)
 for row in j['frames']:
  for key in ['body_far','body_support','body_near']:assert r.sha(Path(row[key]['path']))==row[key]['sha256']
 prior.append({'path':str(p),'sha256':r.sha(p),'referenced_original_tracks_unchanged':18})
manifest={'schema':'frozen-weapon-specific-reload-keyposes-v1','version':1,'frozen':True,
 'status':'coarse_four_keypose_reload_test_candidate; full_reload_runtime_smoothness_and_state_lifecycle_unfulfilled',
 'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_knight','weapon_id':'WPN-XBW-001','weapon_family':'XBW','action':'reload','clip_id':'xbw_reload_four_keyposes',
 'canvas_px':[512,512],'frame_count':4,'unique_body_source_frames':4,'unique_weapon_source_states':4,'body_texture_count_new':12,'weapon_texture_count_new':4,'runtime_texture_count_referenced':16,
 'loop':False,'duration_s':1.10,'frames':frames,'draw_order':c['draw_order'],'required_runtime_tracks':['body_far','weapon','body_support','body_near'],
 'missing_track_policy':'disable_candidate_when_any_required_track_missing','weapon_scale_all_frames':.48,'source_body_geometry_transform':'none_no_bboxfit_no_perframe_zoom',
 'mirror_policy':{'texture':'canonical_right_compose_then_flip_once','continuous_source_coordinates':'left_x=512-right_x about root_x256','pixel_indices':'left_index=511-right_index','no_second_flip':True},
 'phase_intervals_s':[{'phase':row['stage'],'start':row['time_start_s'],'end':row['time_end_s'],'frame_indices':[row['index']]} for row in frames],
 'sampling':'use_authoritative_actual_reload_elapsed_over_actual_duration_to_select_normalized_intervals; frame_index_never_commits_ammo',
 'logical_events_from_images':[],'ammo_commit_authority':'only_actual_kernel_ReloadComplete; nominal1.10s; no_refill_on_cancel_or_visual_stage3',
 'weapon_state_lifecycle_pending':['After successful actual commit, retain loaded-state3 decor on ready until actual shot or instance reset.',
  'After actual emission show relaxed state0 for the emptied instance; this candidate does not change frozen primary79fd body contract.',
  'Cancel/switch/death must follow actual instance ammo/reload state, not the most recent visually inserted bolt. No presentation state grants ammunition.'],
 'source_provenance':provenance,'timing_source':{'path':str(design),'sha256':r.sha(design),'record_id':'WPN-XBW-001','reload_s':1.1,'frame_hold_splits':'assistant_presentation_candidate_not_source_rule_change'},
 'selection_candidate':str(cp),'selection_candidate_sha256':r.sha(cp),'prior_frozen_manifests_unchanged':prior,
 'generation_accounting_snapshot':{'authoritative_ledger':str(r.LEDGER),'requested_count':ledger['requested_count'],'current_window':ledger['current_window'],'remaining':ledger['remaining_batch_requests']},
 'pixel_checks':{'RGBA512_alpha_corners_actual_read':True,'body_three_track_exact_reconstruction':True,'F_E_copies_verified':64,'new_PNGs_unique_hashes':len({x['sha256'] for x in files}),
  'support_errors_source_px':[x['support_error_source_px'] for x in frames],'manipulation_errors_source_px':[x['manipulation_error_source_px'] for x in frames]},
 'manual_review':{'four_right_left_composites_viewed':True,'near_hand_v002_excludes_obvious_vest_triangles':True,'result':'cartoon_relaxed_draw_load_return_readable_static_candidate',
  'visible_contacts':['Front hooked fingers surround relaxed string.','Rear fist occludes small pull tab; two Vlegs exit toward front nocks.','Bolt shaft passes loading pinch opening; underlying torso remains on far track.','Ready fist covers original stock grasp and support fist covers forward handle.'],
  'occluded_or_uncertain':['Rear capture internal junction under side lock/stock not pixel-proven.','Tiny hand-outline boundary and2to4px socket uncertainty remain for running review.',
   'Four discontinuous keyposes do not prove continuous pulling/lowering trajectory or smooth1.10s playback.'],'reviews':reviews},
 'armor_variants_unfulfilled':['ARM-LGT-001','ARM-MED-001','ARM-HVY-001','ARM-ROB-001'],'limitations':c['limitations'],
 'runtime_verified':False,'full_reload_accepted':False,'full_weapon_actions_complete':False}
q=P/'manifests/import-XBW-reload-four-keyposes-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_honest_four_keypose_reload_runtime_test_contract')
audit=P/'reviews/import-XBW-reload-four-keyposes-v001-verification.json';assert not audit.exists();r.write(audit,{'manifest':str(q),'manifest_sha256':r.sha(q),'files':files,'new_file_count':16,'F_E_copies_verified':64,
 'source_raw_C_F_E_hash_pass':True,'prior36_body_tracks_unchanged':True,'errors':[],'engine_executed':False});r.archive(audit,audit.relative_to(P),'real_pixel_hash_source_reconstruction_verification_not_runtime_acceptance')
for number in [91,92]:
 entry=next(x for x in ledger['requests'] if x['request_number']==number);entry.update(status='four_keypose_reload_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),
  review_notes='Actual body91 and weapon92 four keyposes paired with fixedprop.48 and actual distal hand tracks. v002 removes obvious near-hand vest triangles. 4poses/12body+4weaponPNG only; no six-frame inflation, no engine/complete reload claim.')
ledger.setdefault('derived_deliveries',[]).append({'kind':'four_keypose_XBW_reload_test_candidate','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'new_body_track_PNGs':12,'new_weapon_state_PNGs':4,
 'unique_body_keyposes':4,'unique_weapon_states':4,'runtime_verified':False,'full_reload_accepted':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'PNG_count':16,'F_E_copies':64,'frame_count':4,'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests'],'errors':[]}))
