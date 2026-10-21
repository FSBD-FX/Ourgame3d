"""Freeze reviewed actual walk component candidates; never imports engine assets."""
from pathlib import Path
import importlib.util
import hashlib
import json
from PIL import Image, ImageChops
P=Path(__file__).resolve().parent; O=P.parent/'first-unit-animation-v003'
spec=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
spec=importlib.util.spec_from_file_location('trace',P/'extract-walk-four-armors-v002.py')
tr=importlib.util.module_from_spec(spec);spec.loader.exec_module(tr)
candidate=P/'manifests/walk-four-armors-candidate-v002.json';c=r.read(candidate)
prior=O/'import-subset-v007.json'; old=next(a for a in r.read(prior)['actions'] if a['action']=='walk')
files=[]
def record(value):
    p=Path(value['path']);assert r.sha(p)==value['sha256']
    im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512)
    alpha=im.getchannel('A');assert alpha.getextrema()==(0,255)
    corners=[list(im.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]]
    assert all(pixel[3]==0 for pixel in corners)
    copies=r.archive(p,p.relative_to(P),'frozen_walk_true_visible_component_candidate')
    assert len(copies)==4 and all(r.sha(Path(q))==r.sha(p) for q in copies)
    result={'path':str(p),'sha256':r.sha(p),'canvas_px':[512,512],'mode':'RGBA',
            'alpha_extrema':list(alpha.getextrema()),'corner_rgba':corners,
            'bbox_px':list(alpha.getbbox()),'four_archive_hashes_match':True}
    files.append(result);return result

bodies=[];armors={key:[] for key in c['armors']}
for row,t in zip(c['common_body'],old['frames']):
    far=record(row['parts']['body_far']);near=record(row['parts']['body_near'])
    base=Image.open(row['parts']['base_common']['path']).convert('RGBA')
    reconstructed=Image.open(far['path']).convert('RGBA');reconstructed.alpha_composite(Image.open(near['path']).convert('RGBA'))
    assert reconstructed.tobytes()==base.tobytes()
    assert row['root_px']==t['root_px'] and row['grip_px']==t['grip_px']
    masks=tr.masks_for(row['index']);original=Image.open(row['source_original_path']).convert('RGBA')
    assert r.sha(Path(row['source_original_path']))==row['source_original_sha256']
    for name in ['head','weapon_hand','other_hand']:
        assert tr.sel.extract(base,masks[name]).tobytes()==tr.sel.extract(original,masks[name]).tobytes()
    bodies.append({'index':row['index'],'body_far':far,'body_near':near,
        'root_px':row['root_px'],'root_kind':row['root_kind'],'belt_proxy_px':t['belt_proxy_px'],
        'grip_px':row['grip_px'],'weapon_angle_image_clockwise_deg':row['weapon_angle_image_clockwise_deg'],
        'weapon_scale':.4,'phase':t['phase'],'time_start_s':t['time_start_s'],'time_end_s':t['time_end_s'],
        'head_hands_original_within_explicit_trace':True,'body_far_near_exact_reconstruction':True,
        'original_lower_region_restored_from_y':row['original_lower_region_restored_from_y']})
for key,rows in c['armors'].items():
    for row,b in zip(rows,bodies):
        front=record(row['armor_front']);image=Image.open(front['path']).convert('RGBA')
        source=Image.open(row['source_path']).convert('RGBA');assert r.sha(Path(row['source_path']))==row['source_sha256']
        assert all(a==z for a,z in zip(image.get_flattened_data(),source.get_flattened_data()) if a[3])
        for name,mask in tr.masks_for(row['index']).items():
            if name!='cloth':assert ImageChops.multiply(image.getchannel('A'),mask).getbbox() is None
        armors[key].append({'index':row['index'],'armor_front':front,'armor_back':None,
            'armor_back_visibility':row['armor_back_visibility'],'root_px':b['root_px'],'grip_px':b['grip_px'],
            'native_source_path':row['source_path'],'native_source_sha256':row['source_sha256'],
            'mask_path':row['mask_path'],'mask_sha256':row['mask_sha256'],
            'every_visible_pixel_equals_native_source':True,'pruned_detached_fragment_sizes':row['pruned_detached_fragment_sizes']})
assert len(files)==36 and len({f['path'] for f in files})==36
provenance=[]
for number in range(57,62):
    e=next(e for e in r.read(r.LEDGER)['requests'] if e['request_number']==number)
    raw=Path(e['raw_path']);prompt=Path(e['prompt_path']);assert r.sha(raw)==e['sha256']
    r.archive(prompt,prompt.relative_to(P),'frozen_native_walk_component_prompt')
    provenance.append({'request_number':number,'raw_path':str(raw),'raw_sha256':r.sha(raw),
        'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':e['references'],
        'backend':'image_gen.imagegen','host_fee_usd':None})
scripts=['extract-walk-four-armors-v002.py','process-fixed-canvas-v001.py']
for name in scripts:r.archive(P/name,Path('scripts')/name,'frozen_walk_actual_pixel_selection_implementation')
manifest={'schema':'frozen-visible-armor-action-import-v1','version':1,'frozen':True,
    'status':'four_armor_walk_visible_surface_candidates_for_runtime_preview',
    'actor_identity':'EV042_round_enclosed_helmet_knight','clip':'walk','frame_count':6,
    'duration_seconds':.6,'frame_duration_seconds':.1,'loop':True,
    'phase_time_source':'unchanged_frozen_walk_v007_actual_metadata_not_damage_timeline',
    'common_body':bodies,'armors':armors,'unfulfilled_armors':[],
    'draw_order':['body_far','armor_front','independent_weapon','body_near'],
    'no_armor_variant':'omit armor_front use same common body',
    'weapon':r.read(P/'manifests/import-armor-idle-v001.json')['weapon'],
    'mirror_policy':'assemble_right_facing_once_then_one_runtime_mirror_about_common_root',
    'runtime_texture_count_new':36,'runtime_texture_count_total':36,
    'unique_common_pose_count':6,'armor_pose_samples':24,'source_provenance':provenance,
    'common_body_canonical_json_sha256':hashlib.sha256(json.dumps(bodies,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
    'original_walk_import':str(prior),'original_walk_import_sha256':r.sha(prior),
    'selection_manifest':str(candidate),'selection_manifest_sha256':r.sha(candidate),
    'processing_sources':[{'path':str(P/name),'sha256':r.sha(P/name)} for name in scripts],
    'pixel_checks':{'rgba512_real_alpha_corners_and_F_E_hashes':True,'body_exact_reconstruction':True,
        'traced_original_head_hands_preserved':True,'armor_visible_RGBA_equals_native_source':True,
        'armor_traced_head_forearm_hands_waist_intersection_zero':True,'no_body_scale_or_translation':True},
    'manual_visual_review':{'six_frames_each_of_four_isolated_armors_and_sword_assemblies_viewed':True,
        'result':'candidate_real_visible_garment_surfaces_after_elbow_hem_and_boot_wedge_cleanup',
        'limitations':c['limitations']+[
            'Folded far shin in walk frame2 has no actually visible plate; no substitute pants patch was retained.',
            'Material borders and five-pixel cuff clearance are candidate seams, not semantic-perfect garment segmentation.',
            'No motion, transition,20-equipment-combination or actual layered runtime appearance acceptance is claimed.']},
    'prior_failed_selection_versions':['v001_elbow_skin_trouser_triangles_and_robe_boot_wedges'],
    'old_v2_four_layer_validator_pass_claimed':False,'runtime_verified':False,
    'footlock_or_support_contact_accepted':False,'complete_armor':False,
    'external_api_calls':0,'host_fee_usd':None}
path=P/'manifests/import-armor-walk-four-v001.json';assert not path.exists();r.write(path,manifest)
r.archive(path,path.relative_to(P),'frozen_four_armor_walk_visible_surface_candidate')
audit=P/'reviews/import-armor-walk-four-v001-verification.json'
r.write(audit,{'manifest':str(path),'manifest_sha256':r.sha(path),'real_files':files,
    'new_runtime_PNGs':36,'F_E_archive_copies_verified':144,'errors':[],
    'runtime_executed':False,'footlock_or_support_contact_accepted':False})
r.archive(audit,audit.relative_to(P),'actual_walk_pixel_and_archive_verification')
print({'manifest':str(path),'sha256':r.sha(path),'new_runtime_PNGs':36,'errors':0})
