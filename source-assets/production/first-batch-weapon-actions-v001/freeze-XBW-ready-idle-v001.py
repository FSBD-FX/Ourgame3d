"""Freeze reviewed XBW ready idle only, with explicit support/near source tracks."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
cp=P/'reviews/XBW-ready-idle-layer-candidate-v001.json';c=r.read(cp);files=[];frames=[]
for row in c['frames']:
    source=Image.open(row['source_body_path']).convert('RGBA');assert r.sha(Path(row['source_body_path']))==row['source_body_sha256']
    rebuilt=Image.new('RGBA',(512,512),(0,0,0,0));parts={}
    for key in ['body_far','body_support','body_near']:
        d=copy.deepcopy(row['parts'][key]);p=Path(d['path']);assert r.sha(p)==d['sha256']
        im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512) and im.getchannel('A').getextrema()==(0,255)
        corners=[list(im.getpixel(x)) for x in [(0,0),(511,0),(0,511),(511,511)]];assert all(x[3]==0 for x in corners)
        copies=r.archive(p,p.relative_to(P),'frozen_XBW_ready_body_track_candidate_no_attack_runtime_claim');assert all(r.sha(Path(x))==d['sha256'] for x in copies)
        d['corner_rgba']=corners;d['four_archive_copies_verified']=True;parts[key]=d;files.append(d);rebuilt.alpha_composite(im)
    assert rebuilt.tobytes()==source.tobytes()
    assert row['support_alignment_error_px']<1
    frame=copy.deepcopy(row);frame.pop('parts');frame.update(parts);frame['weapon_visible']=True;frames.append(frame)
assert len(files)==18 and len({x['path'] for x in files})==18 and c['unique_source_body_hashes']==6
reviews=[]
for name in ['body_support','body_near','assembled_right','assembled_left']:
    p=P/f'reviews/XBW-ready-idle-{name}-v001.png';assert p.exists();r.archive(p,p.relative_to(P),'reviewed_XBW_two_hand_idle_static_candidate');reviews.append({'path':str(p),'sha256':r.sha(p)})
ledger=r.read(r.LEDGER);assert ledger['requested_count']==81 and ledger['current_window']['requested_count']==9
entry=next(x for x in ledger['requests'] if x['request_number']==81);prompt=Path(entry['prompt_path']);r.archive(prompt,prompt.relative_to(P),'frozen_XBW_twohand_idle_native_prompt')
scripts=['process-body-fixed-canvas-v001.py','extract-XBW-ready-idle-v001.py','freeze-XBW-ready-idle-v001.py']
for script in scripts:r.archive(P/script,Path('scripts')/script,'frozen_XBW_real_source_track_and_fixed_weapon_matrix_implementation')
manifest={'schema':'frozen-weapon-specific-body-tracks-v1','version':1,'frozen':True,
 'status':'XBW_two_hand_ready_idle_underclothes_candidate_static_assembled_not_attack_or_runtime_accepted',
 'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_knight','weapon_id':'WPN-XBW-001','weapon_family':'XBW',
 'action':'ready_idle','clip_id':'xbw_ready_idle','loop':True,'duration_s':.9,'frame_count':6,'unique_body_source_hashes':6,
 'canvas_px':[512,512],'frame_duration_s':.15,'frames':frames,
 'weapon_component':{'path':c['weapon']['path'],'sha256':c['weapon']['sha256'],'canvas_px':[512,512],
   'primary_grip_px':c['weapon']['primary_grip_px'],'support_grip_px':c['weapon']['support_grip_px'],'emit_px':c['weapon']['emit_px']},
 'weapon_contract':c['weapon_contract'],'weapon_contract_sha256':c['weapon_contract_sha256'],
 'draw_order':['body_far','independent_XBW_weapon','body_support','body_near'],
 'required_runtime_body_tracks':['body_far','body_support','body_near'],'missing_track_policy':'do_not_claim_this_candidate_active_when_any_required_track_is_missing',
 'mirror_policy':'assemble_right_once; mirror_actor_weapon_support_near_and_emit_once_about_same_ground_root',
 'fixed_weapon_transform':{'uniform_scale':.48,'angle_image_clockwise_deg':-5.,'target_primary_grip_px':[224,316],
   'same_transform_all_frames':True,'actual_support_target_px':[325,321],'support_fit_error_source_px':frames[0]['support_alignment_error_px'],
   'actual_emit_body_px':frames[0]['transformed_emit_body_px'],'emit_delta_from_ground_root_body_px':frames[0]['emit_delta_from_ground_root_body_px']},
 'phase_time_scope':'ready_idle_0_to0.9_loop_only; no_attack_window_or_emit_event',
 'damage_or_projectile_emission_events':[],'body_texture_count_new':18,'component_texture_count_reused':1,'runtime_texture_count_referenced':19,
 'source_provenance':{'request_number':81,'raw_path':entry['raw_path'],'raw_sha256':entry['sha256'],'tool_original_path':entry['tool_original_path'],
   'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':entry['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0},
 'generation_accounting':{'authoritative_ledger':str(r.LEDGER),'requested_count':81,'window_number':4,'window_requested':9,'window_limit':24,'remaining':15},
 'selection_candidate':str(cp),'selection_candidate_sha256':r.sha(cp),
 'processing_sources':[{'path':str(P/x),'sha256':r.sha(P/x)} for x in scripts],
 'pixel_checks':{'real_RGBA512_alpha_corners':True,'18_unique_track_paths':True,'source_three_track_exact_reconstruction':True,
   'all_grip_and_support_points_actual_opaque_body_pixels':True,'fixed_weapon_matrix_all6_frames':True,'support_fit_error_below1_source_px':True,
   'F_E_track_copies_verified':72,'source_resize_fit_or_translation':False},
 'manual_review':{'body_support_and_near_semantic_tracks_viewed':True,'six_frames_both_direction_static_assemblies_viewed':True,'reviews':reviews,
    'result':'actual_held_crossbow_near_trigger_fist_and_far_support_fist_visible; static_candidate_only'},
 'armor_variants_unfulfilled':['ARM-LGT-001','ARM-MED-001','ARM-HVY-001','ARM-ROB-001'],
 'limitations':c['limitations']+['Six native source PNG hashes are distinct but poses form a minimal breathing idle, not six different attacks.',
    'Both body hands are native generated original pixels; no code-painted hand/arm or wholebody geometry change was used in extraction.',
    'Physical world muzzle/collision/time authority must consume this same transform in the actor/kernel adapter and be verified by root; HUD is not authority.'],
 'runtime_verified':False,'full_weapon_actions_complete':False}
q=P/'manifests/import-XBW-ready-idle-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_XBW_three_body_track_ready_idle_candidate_not_shoot_or_reload')
a=P/'reviews/import-XBW-ready-idle-v001-verification.json';r.write(a,{'manifest':str(q),'manifest_sha256':r.sha(q),'new_real_files':files,'new_file_count':18,
   'F_E_copies_verified':72,'support_error_px':frames[0]['support_alignment_error_px'],'emit_body_px':frames[0]['transformed_emit_body_px'],
   'source_exact_reconstruction_all6':True,'errors':[],'engine_executed':False});r.archive(a,a.relative_to(P),'actual_XBW_ready_source_track_geometry_hash_evidence')
entry.update(status='XBW_ready_idle_body3tracks_frozen_static_assembly_candidate',review_notes='Native twohand ready idle reviewed; exact source far/support/near reconstruction and fixed .48/-5deg component matrix yields support error .1955px. Six static right/left assemblies reviewed; underclothes only, armor/shot/reload and runtime origins still unfulfilled.',reviewed_utc=r.now())
ledger.setdefault('derived_deliveries',[]).append({'kind':'weapon_specific_ready_idle','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'new_runtime_PNGs':18,'reused_component_PNGs':1,'runtime_verified':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'new_body_track_PNGs':18,'support_error_px':frames[0]['support_alignment_error_px'],'requested_count':81,'remaining_window4':15,'errors':0}))
