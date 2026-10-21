"""Freeze observed source-body/recoil candidate; never certify static bow release."""
from pathlib import Path
import importlib.util,copy,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
cp=P/'reviews/XBW-primary-layer-candidate-v001.json';c=r.read(cp);frames=[];files=[]
for row in c['frames']:
    source=Image.open(row['source_body_path']).convert('RGBA');assert r.sha(Path(row['source_body_path']))==row['source_body_sha256']
    rebuilt=Image.new('RGBA',(512,512));parts={}
    for key in ['body_far','body_support','body_near']:
        part=copy.deepcopy(row['parts'][key]);p=Path(part['path']);im=Image.open(p);assert r.sha(p)==part['sha256'] and im.mode=='RGBA' and im.size==(512,512)
        assert im.getchannel('A').getextrema()==(0,255)
        corners=[list(im.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]];assert all(px[3]==0 for px in corners)
        copies=r.archive(p,p.relative_to(P),'frozen_primary_shot_body_candidate_real_hand_tracks');assert all(r.sha(Path(x))==part['sha256'] for x in copies)
        part['corner_rgba']=corners;parts[key]=part;files.append(part);rebuilt.alpha_composite(im)
    assert rebuilt.tobytes()==source.tobytes() and row['support_alignment_error_px']<1
    frame=copy.deepcopy(row);frame.pop('parts');frame.update(parts);frames.append(frame)
assert len(files)==len({x['path'] for x in files})==18
reviews=[]
for name in ['assembled_right','assembled_left','body_near','body_support','hand_coordinates']:
    p=P/f'reviews/XBW-primary-{name}-v001.png';assert p.exists();r.archive(p,p.relative_to(P),'actual_static_primary_contact_reviewed_not_runtime');reviews.append({'path':str(p),'sha256':r.sha(p)})
ledger=r.read(r.LEDGER);entry=next(x for x in ledger['requests'] if x['request_number']==82);assert entry['raw_path'] and r.sha(Path(entry['raw_path']))==entry['sha256']
assert r.sha(Path(entry['tool_original_path']))==entry['sha256'] and all(r.sha(Path(x))==entry['sha256'] for x in entry['archive_paths'])
for x in [Path(entry['prompt_path']),P/'extract-XBW-primary-v001.py',Path(__file__)]:r.archive(x,Path('scripts')/x.name if x.suffix=='.py' else x.relative_to(P),'frozen_primary_source_process_or_prompt')
design=Path('F:/Ourgame/docs/design/equipment-v1/weapons.json');weapon=next(x for x in r.read(design) if x['id']=='WPN-XBW-001')
assert [weapon[x] for x in ['windup_s','active_s','recovery_s','cycle_s']]==[.16,.04,.48,.68]
manifest={'schema':'frozen-weapon-specific-body-tracks-v1','version':1,'frozen':True,
 'status':'XBW_primary_shot_body_and_rigid_weapon_candidate; string_mechanism_and_runtime_unfulfilled',
 'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_knight','weapon_id':'WPN-XBW-001','weapon_family':'XBW','action':'primary','clip_id':'xbw_primary',
 'loop':False,'duration_s':.68,'frame_count':6,'unique_body_source_hashes':len({x['source_body_sha256'] for x in frames}),'canvas_px':[512,512],
 'frames':frames,'weapon_component':{key:c['weapon'][key] for key in ['path','sha256','primary_grip_px','support_grip_px','emit_px']},
 'weapon_contract':c['weapon_contract'],'weapon_contract_sha256':c['weapon_contract_sha256'],'draw_order':c['draw_order'],
 'required_runtime_body_tracks':['body_far','body_support','body_near'],'missing_track_policy':'disable_candidate_when_any_required_track_missing',
 'mirror_policy':'assemble_canonical_right; apply_one_shared_mirror_about_ground_root_to_body_weapon_hands_and_emit',
 'phase_intervals_s':[{'phase':'windup','start':0,'end':.16,'frames':[0,1]},{'phase':'active','start':.16,'end':.20,'frames':[2,3]},{'phase':'recovery','start':.20,'end':.68,'frames':[4,5]}],
 'nominal_emission_events':[{'time_s':.16,'frame_index':2,'kind':'single_primary_bolt','emit_body_px':frames[2]['transformed_emit_body_px'],'authority':'actual_actor_kernel_event_only'}],
 'timing_source':{'path':str(design),'sha256':r.sha(design),'record_id':'WPN-XBW-001','nominal_source_values_only':True,
   'effective_start_and_modifiers':'actor_kernel_authority; do_not_fire_projectile_from_frame_counter_or_HUD'},
 'socket_contract':'Grip,Support,Emit use each frame component_to_body_affine_2x3; map body delta through actual root projection/height and mirror once in Actor adapter',
 'weapon_scale_fixed_all_frames':.48,'body_texture_count_new':18,'component_texture_count_reused':1,'runtime_texture_count_referenced':19,
 'source_provenance':{'request_number':82,'raw_path':entry['raw_path'],'raw_sha256':entry['sha256'],'tool_original_path':entry['tool_original_path'],
   'prompt_path':entry['prompt_path'],'prompt_sha256':r.sha(Path(entry['prompt_path'])),'references':entry['references'],'backend':'image_gen.imagegen','host_fee_usd':None,'external_api_calls':0},
 'generation_accounting_snapshot':{'authoritative_ledger':str(r.LEDGER),'requested_count':ledger['requested_count'],'current_window':ledger['current_window'],'remaining':ledger['remaining_batch_requests']},
 'selection_candidate':str(cp),'selection_candidate_sha256':r.sha(cp),
 'pixel_checks':{'real_RGBA512_alpha_corners':True,'source_three_track_exact_reconstruction':True,'support_errors_px':[x['support_alignment_error_px'] for x in frames],
  'fixed_prop_scale_all6':True,'same_affine_for_grips_emit':True,'F_E_track_copies_verified':72,'source_resize_fit_or_translation':False},
 'manual_review':{'right_left_all6_assemblies_viewed':True,'actual_hand_tracks_viewed':True,'reviews':reviews,'result':'raised_aim_recoil_lower_return_present; actual_two_hand_component_contact_candidate'},
 'armor_variants_unfulfilled':['ARM-LGT-001','ARM-MED-001','ARM-HVY-001','ARM-ROB-001'],'limitations':c['limitations'],
 'string_release_component_animation_complete':False,'runtime_verified':False,'full_weapon_actions_complete':False}
q=P/'manifests/import-XBW-primary-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_XBW_primary_body_socket_candidate_not_complete_mechanism_runtime')
audit=P/'reviews/import-XBW-primary-v001-verification.json';r.write(audit,{'manifest':str(q),'manifest_sha256':r.sha(q),'new_file_count':18,'F_E_copies_verified':72,
 'new_real_files':files,'source_raw_F_E_C_hash_pass':True,'errors':[],'engine_executed':False});r.archive(audit,audit.relative_to(P),'actual_primary_source_hash_alpha_reconstruction_verification')
entry.update(status='XBW_primary_body3tracks_frozen_static_assembly_candidate',review_notes='Six real raise/recoil/recover body poses and original distal hands reviewed both directions. Fixed .48 component scale, per-pose rigid affine, all support errors<1px; release nominal .16 same matrix Grip/Emit. Static bow string/reload states, armor surfaces and runtime world muzzle remain unfulfilled.',reviewed_utc=r.now())
ledger.setdefault('derived_deliveries',[]).append({'kind':'weapon_specific_primary_body','manifest':str(q),'sha256':r.sha(q),'recorded_utc':r.now(),'new_runtime_PNGs':18,'reused_component_PNGs':1,'runtime_verified':False})
r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'new_body_tracks':18,'nominal_emit_s':.16,'release_emit_body_px':frames[2]['transformed_emit_body_px'],'requested_count':ledger['requested_count'],'remaining':ledger['remaining_batch_requests'],'errors':0}))
