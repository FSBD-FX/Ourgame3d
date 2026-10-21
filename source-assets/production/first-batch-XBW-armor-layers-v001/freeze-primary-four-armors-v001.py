"""Freeze reviewed source-layer candidates, keeping runtime/full-armor limits explicit."""
from pathlib import Path
import ast,importlib.util,json
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
def main():
 src=P/'manifests/XBW-primary-four-armors-selection-candidate-v003.json';candidate=r.read(src);bodypath=Path(candidate['source_body_contract_path']);assert r.sha(bodypath)==candidate['source_body_contract_sha256'];body=r.read(bodypath)
 source_rows=[];count=0;copies_checked=0
 for key,frames in candidate['armors'].items():
  assert [f['index'] for f in frames]==list(range(6))
  for f in frames:
   original=Image.open(f['source_path']).convert('RGBA');assert r.sha(Path(f['source_path']))==f['source_sha256']
   for layer in ['armor_far','armor_near']:
    q=Path(f[layer]['path']);im=Image.open(q).convert('RGBA');assert r.sha(q)==f[layer]['sha256'] and im.size==(512,512)
    assert im.getchannel('A').getbbox() and im.getchannel('A').getextrema()==(0,255)
    assert all(im.getpixel(p)[3]==0 for p in [(0,0),(511,0),(0,511),(511,511)])
    assert all(a==b for a,b in zip(im.get_flattened_data(),original.get_flattened_data()) if a[3])
    assert not any(a[3] and a[0]>a[1]+30 and a[2]>a[1]+30 for a in im.get_flattened_data())
    for mask in f['selection_masks'].values():assert r.sha(Path(mask['path']))==mask['sha256']
    protected=Image.open(f['selection_masks']['protected']['path']).convert('L');assert not ImageChops.multiply(im.getchannel('A'),protected).getbbox()
    copies=r.archive(q,q.relative_to(P),'frozen_actual_XBW_primary_armor_layer_candidate_runtime_unverified');assert len(copies)==4;copies_checked+=4;count+=1
   assert f['root_px']==[256,472] and f['primary_grip_px']==body['frames'][f['index']]['primary_grip_px'] and f['support_grip_px']==body['frames'][f['index']]['support_grip_px']
   f.update(frozen=True,static_source_layer_candidate_reviewed=True,semantic_review_passed=False,complete_armor=False,runtime_verified=False,
    review_notes='All6poses/right+leftreviewed after F/E retention. Original head/distal fists/wraps/belt/pouch excluded with4px safety margin; clothing and original native under-sleeve surfaces remain. This is a usable static assembly candidate, not full costume coverage or runtime acceptance.')
  for kind in ['native_selected','assembled_right','assembled_left']:
   q=P/f'reviews/XBW-primary-{key}-{kind}-selection-v003.png';assert q.exists()
 ledger=r.read(r.LEDGER)
 for n in [104,105,106,107]:
  e=next(x for x in ledger['requests'] if x['request_number']==n)
  for q in [e['tool_original_path'],e['raw_path']]+e['archive_paths']:assert r.sha(Path(q))==e['sha256']
  source_rows.append({'request_number':n,'raw_path':e['raw_path'],'raw_sha256':e['sha256'],'tool_original_path':e['tool_original_path'],'tool_original_sha256':e['sha256'],'prompt_path':e['prompt_path'],'prompt_sha256':r.sha(Path(e['prompt_path'])),'references':e['references'],'processing_report_path':str(P/f'processed/call{n}-fixed-canvas-v001/processing-report.json'),'processing_report_sha256':r.sha(P/f'processed/call{n}-fixed-canvas-v001/processing-report.json')})
  e.update(status='XBW_primary_four_armor_layer_candidate_frozen_runtime_unfulfilled',reviewed_utc=r.now(),review_notes='Source surfaces selected and static two-direction review complete; 4px protected anatomy margin; original clothing underlayer/cuff transition remains candidate. No fullarmor/runtime/20combination claim.')
 assert count==48 and copies_checked==192
 previews=[]
 for key in candidate['armors']:
  for kind in ['native_selected','assembled_right','assembled_left']:
   q=P/f'reviews/XBW-primary-{key}-{kind}-selection-v003.png';previews.append({'armor_id':key,'kind':kind,'path':str(q),'sha256':r.sha(q)})
 manifest={'schema':'frozen-XBW-pose-armor-layer-subset-v1','version':1,'frozen':True,'status':'four_armor_primary_static_layer_candidates_pending_runtime_and_coverage_acceptance','weapon_id':'WPN-XBW-001','clip':'primary','frame_count':6,'canvas_px':[512,512],
  'source_body_contract_path':str(bodypath),'source_body_contract_sha256':r.sha(bodypath),'common_body':body['frames'],'armors':candidate['armors'],
  'draw_order':['body_far','armor_far','independent_weapon','body_support','armor_near','body_near'],'required_armor_tracks':['armor_far','armor_near'],'missing_layer_policy':'disable_variant_with_explicit_diagnostic_never_stretch_or_use_Sword_fallback',
  'body_track_authority':'exact_frozen_XBW_primary18_body_files_no_replacement','armor_far_scope':'actual_visible_chest_far_shoulder_sleeve_back_or_split_hem_and_plate_shins; hidden_back_null',
  'armor_near_scope':'actual_visible_near_shoulder_and_cloth_sleeve_before_original_distal_trigger_fist; no_hand_head_or_weapon_art',
  'root_px':[256,472],'body_geometry_transform':'none','armor_per_frame_geometry_transform':'none','mirror_policy':'one_parent_horizontal_flip_for_body_armor_weapon_and_sockets; never_flip_sources_or_each_layer_twice',
  'phase_intervals_s':body['phase_intervals_s'],'source_pose_time_authority':'inherit79fd_primary; actor_effective_elapsed_remaps_existing_phase_fractions; no_image_event_commits_damage',
  'weapon_component_policy':'independent; original79fdneutral_transform_or_explicit94f2weapon_state_contract_selected_by_runtime_owner; never_mix_state_and_oldneutral_pivot',
  'armor_texture_count_new':48,'common_body_texture_count_reused':18,'armor_pose_combinations':24,'source_generation_calls':4,'source_requests':[104,105,106,107],
  'selection_candidate_path':str(src),'selection_candidate_sha256':r.sha(src),'source_provenance':source_rows,'previews':previews,
  'pixel_checks':{'actual_RGBA512':True,'transparent_corners':True,'source_pixels_only':True,'no_magenta_selected':True,'original_protected_head_hand_wrap_belt_excluded':True,'F_E_armor_texture_copies_verified':192},
  'manual_review':{'reviewed_all_24_pose_combinations_both_directions':True,'reviewer':'/root/assets_prepare','static_assembly_candidate':True,'full_coverage_accepted':False,'runtime_verified':False},
  'generation_accounting_snapshot':{'ledger_path':str(r.LEDGER),'requested_count':ledger['requested_count'],'window':ledger['current_window'],'remaining':ledger['remaining_batch_requests'],'task_max_requests':12,'task_used_requests':4},
  'limitations':['Common body is the frozen composite brown underclothes; this does not create a naked universal body. Old under-tunic can remain visible at belt/slit edges and collar.',
   '4px safety exclusions preserve original hand/wrist/belt pixels. ROB genuine long cloth sleeves are selected, but small original skin/under-sleeve wedges remain at some cuff boundaries, especially frames0/4/5; full sealed sleeve coverage remains unfulfilled.',
   'Original short armor styles intentionally retain some native yellow under-sleeve surfaces in cloth layer; these are not hand pixels or metal.',
   'Only actual visible back surfaces are selected. Unseen garment back null is lawful hidden content, not a fabricated transparent image proving full four-layer compliance.',
   'No body/grip/root refit or Sword armor deformation. Static source/alpha review is not runtime contact,cloth continuity,full actions or20equipment acceptance.',
   'Primary source component string/bolt-state handoff remains the separate lifecycle candidate; source images never choose actual damage/ammo or CombatHeight.'],
  'semantic_full_armor_acceptance':False,'runtime_verified':False,'full_equipment_combinations_complete':False}
 q=P/'manifests/import-XBW-primary-four-armors-v001.json';assert not q.exists();r.write(q,manifest);r.archive(q,q.relative_to(P),'frozen_XBW_primary48_actual_surface_candidates_honest_underlayer_and_cuff_limits')
 ledger.setdefault('derived_deliveries',[]).append({'kind':'XBW_primary_four_armors_candidate','manifest':str(q),'sha256':r.sha(q),'actual_armor_pngs':48,'body_pngs_reused':18,'new_native_calls':4,'recorded_utc':r.now(),'runtime_verified':False});r.write(r.LEDGER,ledger)
 for archive in r.ARCHIVES:r.write(archive/'generation-ledger-snapshot.json',ledger)
 for f in P.glob('*.py'):ast.parse(f.read_text('utf-8'));r.archive(f,Path('scripts')/f.name,'actual_source_selection_and_provenance_script')
 for f in (P/'prompts').glob('*.txt'):r.archive(f,f.relative_to(P),'handwritten_native_prompt')
 print(json.dumps({'manifest':str(q),'sha256':r.sha(q),'armor_pngs':48,'reused_body_pngs':18,'F_E_layer_copies':192,'calls':4,'ledger':ledger['requested_count'],'runtime_verified':False}))
if __name__=='__main__':main()
