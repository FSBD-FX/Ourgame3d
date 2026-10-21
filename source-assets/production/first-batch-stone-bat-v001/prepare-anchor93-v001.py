"""Real native stone bat matte and one shared reference-scale placement."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==93);src=Path(e['raw_path']);assert r.sha(src)==e['sha256'];raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
out=P/'processed/call93-anchor-v001';assert not out.exists();out.mkdir(parents=True)
im=m.clean_edges(m.remove_bg_magenta(raw,threshold=90,edge_threshold=140),depth=3)
im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
erased=sum(a[3] and not b[3] and not(a[0]>a[1]+30 and a[2]>a[1]+30) for a,b in zip(raw.get_flattened_data(),im.get_flattened_data()));assert erased==0
def save(image,path,status):image.save(path);r.archive(path,path.relative_to(P),status);return {'path':str(path),'sha256':r.sha(path),'canvas_px':list(image.size),'bbox_px':list(image.getchannel('A').getbbox())}
native=save(im,out/'anchor-native1254.png','actual_native_bat_matte_no_art_repainting')
canonical=im.resize((512,512),Image.Resampling.LANCZOS);normalized=save(canonical,out/'anchor-whole-canvas512.png','whole_canvas_normalization_before_one_reference_scale_placement')
# One accepted identity-scale placement, reused via native generation anchor guides.
scale=.8;old=[288,302];pivot=[256,280];tx=pivot[0]-scale*old[0];ty=pivot[1]-scale*old[1]
anchor=canonical.transform((512,512),Image.Transform.AFFINE,(1/scale,0,-tx/scale,0,1/scale,-ty/scale),resample=Image.Resampling.BICUBIC)
anchor.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in anchor.get_flattened_data()])
assert anchor.getchannel('A').getextrema()==(0,255) and all(anchor.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
item=save(anchor,out/'stone-bat-identity-anchor512.png','actual_stone_bat_candidate_identity_profile_one_fixed_reference_scale_not_runtime_accepted')
reference=P/'references/stone-bat-anchor-magenta512-v001.png';reference.parent.mkdir(exist_ok=True);bg=Image.new('RGB',(512,512),(255,0,255));bg.paste(anchor,(0,0),anchor);bg.save(reference);r.archive(reference,reference.relative_to(P),'actual_identity_anchor_reference_for_native_action_generation')
guide=P/'references/stone-bat-six-cell-anchor-guide-v001.png';sheet=Image.new('RGB',(1536,1024),(255,0,255))
for i in range(6):sheet.paste(bg,(i%3*512,i//3*512))
sheet.save(guide);r.archive(guide,guide.relative_to(P),'six_repeated_actual_anchor_frames_LAYOUT_GUIDE_not_six_unique_motion_frames')
profile={'schema':'stone_bat_visual_identity_profile_v1','actor_id':'ENM-STN-002','status':'internal_style_anchor_not_user_or_runtime_approved','canvas_px':[512,512],
 'pivot_px':pivot,'pivot_kind':'manually_estimated_chest_center_attached_to_actual_actorXYZ_not_ground_feet','source':str(src),'source_sha256':r.sha(src),'native_canvas':[1254,1254],
 'matte_native':native,'normalized_whole_canvas':normalized,'anchor':item,'one_reference_transform':{'scale':scale,'from_chest_estimate_px':old,'to_pivot_px':pivot,'translation_px':[tx,ty],'bboxfit':False},
 'action_processing':'new_action_native_cells_must_match_this_guide; exact_grid_wholecell512_only; do_not_apply_anchor0.8_again_or_fit_each_pose',
 'safe_silhouette_envelope_px':[48,80,424,416],'guide':str(guide),'guide_sha256':r.sha(guide),'recommended_trial_display_canvas_px':128,
 'actual_reference_alpha_extrema':[0,255],'erased_non_chroma_native_pixels':erased,'no_baked_shadow_or_world_height':True,
 'design_sources':[{'path':str(p),'sha256':r.sha(p)} for p in [Path('F:/Ourgame/docs/design/enemies-v1/stone-forest.json'),Path('F:/Ourgame/docs/design/presentation-v1/02-敌人场景与特效规范.md')]],
 'limits':['Actual actorZ90/high or20/low must be projected outside sprite; no pose sheet may fake a worldZ transition.',
 'Ground shadow belongs to groundXY; wing silhouette never resizes body16x12cm or hurtbox.','This1anchor is not hover/wake/attacks/recovery/hurt/death completion.'],'runtime_verified':False}
j=P/'manifests/stone-bat-identity-profile-v001.json';j.parent.mkdir(exist_ok=True);r.write(j,profile);r.archive(j,j.relative_to(P),'real_identity_scale_pivot_profile_not_full_bat_acceptance')
e.update(status='stone_bat_native_identity_anchor_processed_pending_action_grids',reviewed_utc=r.now(),review_notes='Cold grey segmented stone bat, amber eyes/cracks, fixed3/4right silhouette accepted internally for action anchor only. Raw87percentwidth normalized once .8 to~70percent; actual chest estimated288302 placed256280, no frame bboxfit. Not runtime/body-size change.')
e['identity_profile']={'path':str(j),'sha256':r.sha(j)};r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'profile':str(j),'sha256':r.sha(j),'anchor_bbox_px':item['bbox_px'],'pivot':pivot,'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
