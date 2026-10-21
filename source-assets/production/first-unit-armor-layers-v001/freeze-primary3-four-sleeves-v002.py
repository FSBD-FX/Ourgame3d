"""Freeze real sleeve tracks, without claiming full-state or runtime acceptance."""
from pathlib import Path
import importlib.util, copy, json, hashlib
from PIL import Image, ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
prior_path=P/'manifests/import-armor-primary3-four-v001.json';prior=r.read(prior_path)
assert r.sha(prior_path)=='e97f2958f624e8d27c0942931e48a293c5bee6b33ebfd42148956dfd3f288497'
candidate_path=P/'manifests/primary3-ROB-real-sleeves-candidate-v001.json';c=r.read(candidate_path)
files=[];new_files=[]

def record(value,new=False):
    path=Path(value['path']);assert r.sha(path)==value['sha256']
    image=Image.open(path);assert image.mode=='RGBA' and image.size==(512,512)
    alpha=image.getchannel('A');assert alpha.getextrema()==(0,255)
    corners=[list(image.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]];assert all(x[3]==0 for x in corners)
    copies=r.archive(path,path.relative_to(P),'frozen_P3_real_sleeve_candidate_not_runtime_acceptance');assert len(copies)==4
    assert all(r.sha(Path(q))==r.sha(path) for q in copies)
    d={'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],
       'corner_rgba':corners,'bbox_px':list(alpha.getbbox()),'four_archive_hashes_match':True}
    files.append(d)
    if new:new_files.append(d)
    return d

bodies=[]
for i,(old,row) in enumerate(zip(prior['common_body'],c['frames'])):
    far=record(row['parts']['body_far'],True);near=record(row['parts']['body_near'],True)
    before=Image.open(old['body_far']['path']).convert('RGBA');before.alpha_composite(Image.open(old['body_near']['path']).convert('RGBA'))
    after=Image.open(far['path']).convert('RGBA');after.alpha_composite(Image.open(near['path']).convert('RGBA'));assert before.tobytes()==after.tobytes()
    assert before.getpixel(tuple(old['grip_px']))==Image.open(near['path']).getpixel(tuple(old['grip_px']))
    body=copy.deepcopy(old);body.update(body_far=far,body_near=near,body_near_scope='actual_original_distal_gripping_fist_plus_short_wrist; other_forearm_pixels_moved_to_far',
        common_whole_body_RGBA_equals_prior=True,body_far_near_exact_reconstruction=True,
        hand_selection_mask=row['mask_paths']['distal_hand'],hand_occlusion_bbox_px=near['bbox_px'])
    bodies.append(body)

armors={key:[] for key in prior['armors']}
for key,rows in prior['armors'].items():
    for i,(old,row) in enumerate(zip(rows,c['frames'])):
        item=copy.deepcopy(old)
        if key=='ARM-ROB-001':
            front=record(row['parts']['armor_front'],True);near=record(row['parts']['armor_near'],True)
            source=Image.open(row['source_path']).convert('RGBA');a=Image.open(front['path']).convert('RGBA');b=Image.open(near['path']).convert('RGBA')
            assert all(x==y for image in [a,b] for x,y in zip(image.get_flattened_data(),source.get_flattened_data()) if x[3])
            assert ImageChops.multiply(a.getchannel('A'),b.getchannel('A')).getbbox() is None
            item.update(armor_front=front,armor_near=near,mask_path=row['mask_paths']['combined_front']['path'],mask_sha256=row['mask_paths']['combined_front']['sha256'],
                armor_near_mask=row['mask_paths']['weapon_arm_cloth'],near_visibility='actual_gray_weapon_arm_sleeve_and_bluegray_cloth_wrap_in_front_of_sword_before_original_fist',
                all_selection_masks=row['mask_paths'],source_cloth_only_no_skin_or_hand_repaint=True,
                coverage_scope='actual_visible_torso_sleeves_cuffs_wrap_and_split_hem; native71_multiple_poses_have_actual_skin_gaps')
        else:
            item.update(armor_front=record(old['armor_front']),armor_near=None,
                near_visibility='no_new_near_garment_selected_for_this_armor; existing_partial_front_retained')
        armors[key].append(item)

assert len(files)==42 and len({f['path'] for f in files})==42
assert len(new_files)==24 and len({f['path'] for f in new_files})==24
reviews=[]
for key in armors:
    for direction in ['right','left']:
        path=P/f'reviews/primary3-four-armors-sleeves-v001-{key}-{direction}.png';assert path.exists()
        copies=r.archive(path,path.relative_to(P),'manually_reviewed_6_pose_sword_assembly_candidate_not_runtime_motion');assert all(r.sha(Path(q))==r.sha(path) for q in copies)
        reviews.append({'path':str(path),'sha256':r.sha(path),'armor_id':key,'direction':direction,'six_pose_candidates_reviewed':True})

scripts=['select-primary3-ROB-sleeves-v001.py','prepare-primary3-sleeve-review-v002.py','freeze-primary3-four-sleeves-v002.py']
for name in scripts:r.archive(P/name,Path('scripts')/name,'frozen_P3_real_sleeve_selection_and_review_implementation')
limitations=[
 'This is a six-pose P3 candidate only; no full-state four-armor or 20-equipment motion acceptance.',
 'Native71 contains actual exposed skin between cuff and wrist wrap in several poses. A full wrist-covering sleeve is not present in this source. No invented cloth or painted skin fills it.',
 'Common near track is repartitioned for all four armors; the reconstructed common body is byte-identical to the prior one, but sword/forearm occlusion changes and needs runtime review.',
 'LGT/MED/HVY reuse prior partial fronts. This sleeve revision does not invent their missing forearm clothing.',
 'ROB armor_near must be drawn after independent sword and before original distal hand. Missing this track must disable/reject this appearance rather than silently show partial clothing.',
 'Existing P3 head trace is reused to exclude all new sleeve pixels. Static manual traces do not certify an independent rig or anatomical segmentation.',
 'Native AA/magenta fringe, hem seams, clip transitions, true mirror motion and weapon/body intersections still need running-game review.'
]
manifest={
 'schema':'frozen-visible-armor-action-import-v2','version':2,'frozen':True,
 'status':'four_armor_P3_with_actual_ROB_sleeve_near_track_candidate_not_complete_armor',
 'actor_identity':prior['actor_identity'],'clip':'primary_3','frame_count':6,
 'phase_seconds':prior['phase_seconds'],'phase_frames':prior['phase_frames'],'phase_time_source':'unchanged_prior_frozen_P3_absolute_windows',
 'common_body':bodies,'armors':armors,'draw_order':['body_far','armor_front','independent_weapon','armor_near','body_near'],
 'required_runtime_tracks':['body_far','armor_front','independent_weapon','armor_near','body_near'],
 'null_track_policy':{'armor_near':{'ARM-ROB-001':'required_non_null_all_6_frames','ARM-LGT-001':'null_allowed_no_selected_near_garment','ARM-MED-001':'null_allowed_no_selected_near_garment','ARM-HVY-001':'null_allowed_no_selected_near_garment'},'armor_back':'null_all_frames_no_hidden_back_invented'},
 'no_armor_variant':'omit all armor tracks; use same reconstructed common body',
 'weapon':prior['weapon'],'mirror_policy':prior['mirror_policy'],
 'runtime_texture_count_new':24,'runtime_texture_count_reused':18,'runtime_texture_count_total':42,
 'runtime_new_files':new_files,'unique_common_pose_count':6,'armor_pose_samples':24,
 'supersedes_for_this_clip_only':{'path':str(prior_path),'sha256':r.sha(prior_path),'old_files_overwritten':False,'old_ROB_front_retained_as_history':True},
 'selection_manifest':str(candidate_path),'selection_manifest_sha256':r.sha(candidate_path),
 'source_provenance':prior['source_provenance'],'generation_requests_added_by_this_revision':0,
 'generation_accounting':{'authoritative_ledger':str(r.LEDGER),'requested_count':71,'current_window':3,'current_window_requested':23,'current_window_limit':24},
 'processing_sources':[{'path':str(P/name),'sha256':r.sha(P/name)} for name in scripts],
 'pixel_checks':{'real_RGBA_512_alpha_corners_F_E_hashes':True,'common_body_exact_prior_RGBA_reconstruction':True,
    'original_grip_pixels_preserved':True,'ROB_visible_RGBA_equals_same_coordinate_native71':True,'ROB_front_near_alpha_disjoint':True,
    'no_source_resize_translation_paint_or_joint_change':True},
 'manual_visual_review':{'result':'actual_existing_ROB_cuffs_and_cloth_wraps_selected; native71_exposed_forearm_gaps_remain; not_full_long_sleeves',
     'four_armors_6_frames_both_directions_previewed':True,'reviews':reviews,'limitations':limitations},
 'unfulfilled_surfaces':{'ARM-ROB-001':['non_P2_P3_states_real_sleeve_near_tracks','complete_wrist_covering_cloth_not_in_native71_multiple_poses'],
   'ARM-LGT-001':['all_state_completeness_and_transitions'], 'ARM-MED-001':['all_state_completeness_and_transitions'], 'ARM-HVY-001':['all_state_completeness_and_transitions']},
 'old_v2_four_layer_validator_pass_claimed':False,'runtime_verified':False,'complete_armor':False,'external_api_calls':0,'host_fee_usd':None
}
path=P/'manifests/import-armor-primary3-four-sleeves-v002.json';assert not path.exists();r.write(path,manifest);r.archive(path,path.relative_to(P),'frozen_P3_actual_ROB_sleeves_contract_explicit_near_track_not_runtime_accepted')
audit_path=P/'reviews/import-armor-primary3-four-sleeves-v002-verification.json';assert not audit_path.exists()
r.write(audit_path,{'manifest':str(path),'manifest_sha256':r.sha(path),'real_files':files,'real_file_count':42,'new_file_count':24,'reused_file_count':18,
    'F_E_copies_verified':168,'errors':[],'generation_calls_added':0,'runtime_executed':False})
r.archive(audit_path,audit_path.relative_to(P),'actual_ROB_sleeve_source_hash_alpha_retention_verification')
ledger=r.read(r.LEDGER);assert ledger['requested_count']==71 and ledger['current_window']['requested_count']==23
delivery={'kind':'derived_existing_source_sleeve_contract','manifest':str(path),'sha256':r.sha(path),'recorded_utc':r.now(),'generation_calls_added':0,'new_runtime_PNGs':24,'referenced_runtime_PNGs':42}
ledger.setdefault('derived_deliveries',[]).append(delivery);r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'manifest':str(path),'sha256':r.sha(path),'new_PNGs':24,'total_PNGs':42,'errors':0},ensure_ascii=False))
