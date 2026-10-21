"""Freeze honest P2 partial garment candidates with actual PNG/source/retention checks."""
from pathlib import Path
import importlib.util,json,hashlib
from PIL import Image,ImageChops
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('trace',P/'extract-primary2-four-armors-v003.py');tr=importlib.util.module_from_spec(s);s.loader.exec_module(tr)
candidate=P/'manifests/primary2-four-armors-candidate-v003.json';c=r.read(candidate)
original_import=O/'import-subset-v005.json';old=next(a for a in r.read(original_import)['actions'] if a['action']=='primary_2')
files=[]
def record(value):
    p=Path(value['path']);assert r.sha(p)==value['sha256'];im=Image.open(p)
    assert im.mode=='RGBA' and im.size==(512,512);alpha=im.getchannel('A');assert alpha.getextrema()==(0,255)
    corners=[list(im.getpixel(pt)) for pt in [(0,0),(511,0),(0,511),(511,511)]];assert all(x[3]==0 for x in corners)
    copies=r.archive(p,p.relative_to(P),'frozen_P2_actual_partial_garment_candidate');assert len(copies)==4 and all(r.sha(Path(q))==r.sha(p) for q in copies)
    d={'path':str(p),'sha256':r.sha(p),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':list(alpha.getextrema()),'corner_rgba':corners,'bbox_px':list(alpha.getbbox()),'four_archive_hashes_match':True};files.append(d);return d
bodies=[];armors={key:[] for key in c['armors']}
for row,t in zip(c['common_body'],old['frames']):
    far=record(row['parts']['body_far']);near=record(row['parts']['body_near']);base=Image.open(row['parts']['base_common']['path']).convert('RGBA')
    image=Image.open(far['path']).convert('RGBA');image.alpha_composite(Image.open(near['path']).convert('RGBA'));assert image.tobytes()==base.tobytes()
    orig=Image.open(row['source_original_path']).convert('RGBA');assert r.sha(Path(row['source_original_path']))==row['source_original_sha256']
    masks=tr.masks_for(row['index'])
    for name in ['head','weapon_forearm','other_forearm','weapon_hand','other_hand']:assert tr.w.sel.extract(base,masks[name]).tobytes()==tr.w.sel.extract(orig,masks[name]).tobytes()
    assert row['root_px']==t['root_px'] and row['grip_px']==t['grip_px']
    bodies.append({'index':row['index'],'body_far':far,'body_near':near,'root_px':row['root_px'],'grip_px':row['grip_px'],
        'weapon_angle_image_clockwise_deg':row['weapon_angle_image_clockwise_deg'],'weapon_scale':.4,
        'phase':t['phase'],'time_start_s':t['time_start_s'],'time_end_s':t['time_end_s'],
        'head_hands_forearms_original_within_explicit_trace':True,'body_far_near_exact_reconstruction':True,
        'body_near_scope':row['near_scope'],'lowerlegs_original_y410_onwards':True})
for key,rows in c['armors'].items():
    for row,b in zip(rows,bodies):
        front=record(row['armor_front']);image=Image.open(front['path']).convert('RGBA');source=Image.open(row['source_path']).convert('RGBA')
        assert r.sha(Path(row['source_path']))==row['source_sha256'];assert all(x==y for x,y in zip(image.get_flattened_data(),source.get_flattened_data()) if x[3])
        for name,mask in tr.masks_for(row['index']).items():
            if name!='cloth':assert ImageChops.multiply(image.getchannel('A'),mask).getbbox() is None
        armors[key].append({'index':row['index'],'armor_front':front,'armor_back':None,'armor_back_visibility':row['armor_back_visibility'],
            'root_px':b['root_px'],'grip_px':b['grip_px'],'native_source_path':row['source_path'],'native_source_sha256':row['source_sha256'],
            'mask_path':row['mask_path'],'mask_sha256':row['mask_sha256'],'every_visible_pixel_equals_native_source':True,
            'pruned_detached_fragment_sizes':row['pruned_detached_fragment_sizes']})
assert len(files)==36 and len({f['path'] for f in files})==36
sources=[]
for n in range(62,67):
    entry=next(e for e in r.read(r.LEDGER)['requests'] if e['request_number']==n);raw=Path(entry['raw_path']);prompt=Path(entry['prompt_path'])
    assert r.sha(raw)==entry['sha256'];r.archive(prompt,prompt.relative_to(P),'frozen_native_P2_garment_prompt')
    sources.append({'request_number':n,'raw_path':str(raw),'raw_sha256':r.sha(raw),'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':entry['references'],'backend':'image_gen.imagegen','host_fee_usd':None})
scripts=['extract-primary2-four-armors-v003.py','process-fixed-canvas-v001.py']
for name in scripts:r.archive(P/name,Path('scripts')/name,'frozen_P2_actual_pixel_selection_implementation')
manifest={'schema':'frozen-visible-armor-action-import-v1','version':1,'frozen':True,
    'status':'four_armor_P2_partial_surface_candidates_for_runtime_preview_not_complete_clothing',
    'actor_identity':'EV042_round_enclosed_helmet_knight','clip':'primary_2','frame_count':6,
    'phase_seconds':[.15,.12,.27],'phase_frames':[2,2,2],'phase_time_source':'unchanged_frozen_primary2_actual_metadata',
    'common_body':bodies,'armors':armors,'unfulfilled_armors':[],
    'unfulfilled_surfaces':{'ARM-ROB-001':['full_long_sleeve_coverage_on_original_forearm; source_cuff_and_wrap_requires_new_actual_near_garment_revision']},
    'draw_order':['body_far','armor_front','independent_weapon','body_near'],'no_armor_variant':'omit armor_front use same common body',
    'weapon':r.read(P/'manifests/import-armor-idle-v001.json')['weapon'],'mirror_policy':'assemble_right_facing_once_then_one_runtime_mirror_about_common_root',
    'runtime_texture_count_new':36,'runtime_texture_count_total':36,'unique_common_pose_count':6,'armor_pose_samples':24,
    'common_body_canonical_json_sha256':hashlib.sha256(json.dumps(bodies,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
    'source_provenance':sources,'original_action_import':str(original_import),'original_action_import_sha256':r.sha(original_import),
    'selection_manifest':str(candidate),'selection_manifest_sha256':r.sha(candidate),
    'processing_sources':[{'path':str(P/name),'sha256':r.sha(P/name)} for name in scripts],
    'pixel_checks':{'rgba512_real_alpha_corners_F_E_hashes':True,'body_exact_reconstruction':True,'traced_original_head_hands_forearms_preserved':True,
        'armor_visible_RGBA_equals_native_source':True,'armor_head_hand_forearm_waist_trace_intersection_zero':True,'no_body_scale_or_translation':True},
    'manual_visual_review':{'six_frames_each_isolated_and_sword_assembled_reviewed':True,
        'result':'actual_partial_surface_candidate_no_body_or_forearm_wrap_imported_as_armor',
        'limitations':c['limitations']+['Original bare forearm preservation is a conservative partial contract only, not a permanent requirement; later actual sleeve layers may cover it while preserving original hands/grips.',
            'Three-pixel arm clearance may reveal undercoat seams. Greave strap borders are native wearable edges, not full boots.',
            'No motion/transition/20-combination/runtime complete appearance acceptance.']},
    'prior_failed_selection_versions':['v001_mail_trouser_gap_and_ROB_source_wrap','v002_ROB_wrap_color_classifier_insufficient'],
    'old_v2_four_layer_validator_pass_claimed':False,'runtime_verified':False,'complete_armor':False,'external_api_calls':0,'host_fee_usd':None}
path=P/'manifests/import-armor-primary2-four-v001.json';assert not path.exists();r.write(path,manifest);r.archive(path,path.relative_to(P),'frozen_four_armor_P2_honest_partial_candidate')
audit=P/'reviews/import-armor-primary2-four-v001-verification.json';r.write(audit,{'manifest':str(path),'manifest_sha256':r.sha(path),'real_files':files,'new_runtime_PNGs':36,'F_E_archive_copies_verified':144,'errors':[],'runtime_executed':False})
r.archive(audit,audit.relative_to(P),'actual_P2_pixel_source_retention_evidence');print({'manifest':str(path),'sha256':r.sha(path),'runtime_PNGs':36,'errors':0})
