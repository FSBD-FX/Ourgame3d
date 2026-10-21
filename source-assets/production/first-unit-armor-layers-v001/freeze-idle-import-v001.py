"""Freeze candidate layers/markers with real pixels and archive SHA verification."""
from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
candidate=r.read(P/'manifests/idle-four-armors-candidate-v003.json')
old_idle=next(a for a in r.read(O/'import-subset-v005.json')['actions'] if a['action']=='idle')
out=P/'components/idle-runtime-front-v001';assert not out.exists();out.mkdir()
def pngrecord(path):
    im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512);a=im.getchannel('A')
    assert all(a.getpixel(pt)==0 for pt in [(0,0),(511,0),(0,511),(511,511)])
    return {'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':im.mode,'alpha_extrema':list(a.getextrema()),'corners_transparent':True,'bbox_px':list(a.getbbox()) if a.getbbox() else None,'nonempty':bool(a.getbbox())}
textures=[];bodies=[]
for row,old in zip(candidate['common_body'],old_idle['frames']):
    parts={name:pngrecord(Path(row['parts'][name]['path'])) for name in ['far','near']}
    for v in parts.values():textures.append(v)
    bodies.append({'index':row['frame_index'],'body_far':parts['far'],'body_near':parts['near'],'root_px':row['root_px'],'grip_px':row['grip_px'],'weapon_angle_image_clockwise_deg':row['weapon_angle_image_clockwise_deg'],'weapon_scale':row['weapon_scale'],'phase':'idle_loop','time_start_s':old['time_start_s'],'time_end_s':old['time_end_s'],'source_common_editable_path':row['parts']['common']['path'],'original_head_hands_preserved':True})
armors={}
for key,rows in candidate['armors'].items():
    armors[key]=[]
    for row in rows:
        front=Image.new('RGBA',(512,512),(0,0,0,0))
        sources=[]
        for name in ['armor_far_shoulder','armor_torso','armor_front']:
            v=row['parts'][name];p=Path(v['path']);assert r.sha(p)==v['sha256'];front.alpha_composite(Image.open(p).convert('RGBA'));sources.append(v)
        p=out/f'{key}-front-{row["frame_index"]}.png';front.save(p);r.archive(p,p.relative_to(P),'merged_actual_selected_front_armor_pixels_not_whole_body')
        record=pngrecord(p);record['component_sources']=sources
        back=pngrecord(Path(row['parts']['armor_back']['path']))
        textures.extend([record,back]);armors[key].append({'index':row['frame_index'],'armor_back':back,'armor_front':record,'root_px':row['root_px'],'grip_px':row['grip_px'],'selection_source_path':row['source_path'],'selection_source_sha256':row['source_sha256']})
# Re-read all canonical paths, pixel contracts, source hashes and four retained copies.
check=[]
for v in textures:
    p=Path(v['path']);assert r.sha(p)==v['sha256'];copies=r.archive(p,p.relative_to(P),'frozen_idle_layer_import_candidate')
    assert len(copies)==4 and all(r.sha(Path(q))==v['sha256'] for q in copies)
    check.append({'path':str(p),'sha256':v['sha256'],'four_archive_hashes_match':True})
assert len(textures)==60 and len({v['path'] for v in textures})==60
ledger=r.read(r.LEDGER);provenance=[]
for n in [45,48,49,50,51]:
    e=next(e for e in ledger['requests'] if e['request_number']==n)
    prompt=Path(e['prompt_path']);source=Path(e['raw_path']);assert r.sha(source)==e['sha256']
    r.archive(prompt,Path('prompts')/prompt.name,'native_generation_prompt_frozen')
    provenance.append({'request_number':n,'backend':'image_gen.imagegen','raw_path':str(source),'raw_sha256':r.sha(source),'prompt_path':str(prompt),'prompt_sha256':r.sha(prompt),'references':e['references'],'host_fee_usd':None,'external_api_calls':0})
manifest={'schema':'frozen-visible-armor-idle-import-v1','version':1,'frozen':True,'status':'candidate_for_runtime_armor_toggle_not_formal_acceptance','actor_identity':candidate['identity'],'clip':'idle','frame_count':6,'idle_duration_s':old_idle['frames'][-1]['time_end_s'],'common_body':bodies,'armors':armors,'weapon':candidate['weapon'],'draw_order':['armor_back','body_far','armor_front','independent_weapon','body_near'],'empty_armor_variant':'no_armor_omit_both_armor_layers_use_same_common_body','mirror_policy':'assemble_all_right_facing_layers_then_mirror_once_about_same_root','runtime_texture_count_new':60,'existing_independent_weapon_texture_count':1,'unique_common_body_pose_count':6,'armor_pose_samples':24,'editable_component_manifest':str(P/'manifests/idle-four-armors-candidate-v003.json'),'editable_component_manifest_sha256':r.sha(P/'manifests/idle-four-armors-candidate-v003.json'),'source_provenance':provenance,'pixel_checks':{'canvas_rgba_corners_hashes':True,'same_original_head_hands':True,'exact_body_near_far_reconstruction':True,'no_per_frame_scale_or_translation':True},'manual_visual_review':{'six_frames_each_armor_viewed':True,'isolated_surfaces_each_armor_viewed':True,'result':'readable_four_distinct_armor_surfaces_and_shared_knight_candidate','limitations':['Some one-pixel native seam/under-sleeve borders remain inside wearable selection; no claim of semantic perfect segmentation.','Back layers represent visible far-side cloth fragments only, not complete hidden garments.','body_near contains real visible forearm/wrist/hand, not a complete independently posed arm.','Only idle is frozen here. P1/P2/P3 and all other states remain unfulfilled.','No runtime weapon/armor20-combination/transition/footlock acceptance.']},'old_v2_four_layer_validator_pass_claimed':False,'runtime_verified':False,'full_armor_complete':False,'provenance_status':'host_generated_native_art_terms_apply_no_CC0_claim','host_fee_usd':None,'external_api_calls':0}
f=P/'manifests/import-armor-idle-v001.json';assert not f.exists();r.write(f,manifest);r.archive(f,f.relative_to(P),'frozen_idle_four_armor_actual_layer_candidate')
verification={'schema':'frozen-import-pixel-source-verification-v1','manifest':str(f),'manifest_sha256':r.sha(f),'new_runtime_PNGs':60,'archive_copies_verified':240,'files':check,'errors':[],'runtime_executed':False}
q=P/'reviews/import-armor-idle-v001-verification.json';r.write(q,verification);r.archive(q,q.relative_to(P),'frozen_import_actual_png_and_F_E_SHA_evidence')
print({'manifest':str(f),'sha256':r.sha(f),'new_runtime_PNGs':60,'existing_weapon':1,'errors':0})
