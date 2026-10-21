"""Partition real body91 pixels; rigidly assemble independent weapon92 states."""
from pathlib import Path
import importlib.util, math, json
from PIL import Image, ImageDraw, ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
out=P/'components/XBW-reload-four-keyposes-v001'
if out.exists():assert not any(out.iterdir()),'Will not overwrite an existing nonempty delivery'
else:out.mkdir(parents=True)
near_polys=[
 [(266,264),(297,258),(322,254),(346,258),(353,267),(352,286),(339,295),(316,299),(299,298),(273,296),(264,286)],
 [(174,264),(205,260),(225,257),(243,262),(254,271),(253,287),(243,299),(227,302),(207,297),(176,293),(171,281)],
 [(215,266),(244,260),(263,254),(283,256),(300,262),(305,273),(301,278),(305,285),(299,294),(277,298),(254,294),(218,291),(212,280)],
 [(179,297),(207,291),(229,292),(245,299),(250,311),(245,327),(228,333),(211,332),(195,327),(180,322)]]
support_polys=[
 [(285,302),(301,298),(320,300),(334,303),(342,312),(343,329),(334,342),(318,345),(303,338),(292,331),(285,319)],
 [(290,302),(305,299),(322,301),(337,306),(344,315),(344,331),(335,344),(320,348),(305,341),(294,333),(289,320)],
 [(289,306),(305,302),(323,305),(337,310),(345,320),(344,335),(336,347),(322,349),(307,342),(296,336),(289,322)],
 [(289,306),(305,302),(323,305),(337,310),(345,320),(344,335),(336,347),(322,349),(307,342),(296,336),(289,322)]]
body_support=[[321,321],[321,323],[321,325],[321,325]]
body_contact=[[342,282],[236,278],[286,274],[224,316]]
component_support=[[344,320],[344,320],[344,286],[344,286]]
component_contact=[[402,244],[178,210],[312,166],[138,274]]
component_emit=[[506,263],[506,263],[506,229],[506,229]]
stages=['relaxed_string_grasp','draw_string_rear_capture','place_single_bolt','return_ready_pending_commit']
edges=[0.0,0.20,0.60,0.85,1.10];scale=.48
def mask(poly):
 q=Image.new('L',(512,512),0);ImageDraw.Draw(q).polygon(poly,fill=255);return q
def select(source,m):
 q=source.copy();q.putalpha(ImageChops.multiply(source.getchannel('A'),m));q.putdata([p if p[3] else(0,0,0,0) for p in q.get_flattened_data()]);return q
def save(image,path,status):
 image.save(path);copies=r.archive(path,path.relative_to(P),status);assert all(r.sha(Path(x))==r.sha(path) for x in copies)
 return {'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':list(image.getchannel('A').getextrema()),'corner_alpha':[image.getpixel(pt)[3] for pt in[(0,0),(511,0),(0,511),(511,511)]],'bbox_px':list(image.getchannel('A').getbbox()),'F_E_copies_verified':True}
sheets={name:Image.new('RGBA',(1024,1024)) for name in['body_far','body_support','body_near','weapon','assembled_right','assembled_left']};rows=[]
for i in range(4):
 src=P/f'processed/call91-four-body-keyposes-v001/body-{i}.png';source=Image.open(src).convert('RGBA')
 weapon_src=P/f'processed/call92-four-weapon-states-v001/weapon-{i}.png';weapon=Image.open(weapon_src).convert('RGBA')
 nm=mask(near_polys[i]);sm=ImageChops.multiply(mask(support_polys[i]),ImageChops.invert(nm));assert ImageChops.multiply(nm,sm).getbbox() is None
 near=select(source,nm);support=select(source,sm);far=select(source,ImageChops.invert(ImageChops.lighter(nm,sm)))
 reconstructed=far.copy();reconstructed.alpha_composite(support);reconstructed.alpha_composite(near);assert reconstructed.tobytes()==source.tobytes()
 for name,im in [('near',nm),('support',sm)]:
  q=out/f'{name}-selection-mask-{i}.png';im.save(q);r.archive(q,q.relative_to(P),'manual_actual_distal_hand_and_wrist_selection_not_creative_art')
 parts={name:save(im,out/f'{name}-{i}.png','actual_body91_pixels_semantic_hand_track_candidate_pending_manual_assembly_review') for name,im in[('body_far',far),('body_support',support),('body_near',near)]}
 wp=save(weapon,out/f'weapon-{i}.png','actual_native92_complete_component_state_preserved_whole_canvas')
 c0=component_support[i];c1=component_contact[i];b0=body_support[i];b1=body_contact[i]
 theta=math.atan2(b1[1]-b0[1],b1[0]-b0[0])-math.atan2(c1[1]-c0[1],c1[0]-c0[0]);co=math.cos(theta);si=math.sin(theta)
 tx=b0[0]-scale*(co*c0[0]-si*c0[1]);ty=b0[1]-scale*(si*c0[0]+co*c0[1]);matrix=[[scale*co,-scale*si,tx],[scale*si,scale*co,ty]]
 def point(p):return [matrix[0][0]*p[0]+matrix[0][1]*p[1]+tx,matrix[1][0]*p[0]+matrix[1][1]*p[1]+ty]
 render=weapon.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,-(co*tx+si*ty)/scale,-si/scale,co/scale,-(-si*tx+co*ty)/scale),resample=Image.Resampling.BICUBIC)
 assembled=far.copy();assembled.alpha_composite(render);assembled.alpha_composite(support);assembled.alpha_composite(near)
 mirrored=assembled.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 for name,im in [('body_far',far),('body_support',support),('body_near',near),('weapon',weapon),('assembled_right',assembled),('assembled_left',mirrored)]:sheets[name].alpha_composite(im,(i%2*512,i//2*512))
 emit=point(component_emit[i]);near_actual=point(c1)
 rows.append({'index':i,'stage':stages[i],'time_start_s':edges[i],'time_end_s':edges[i+1],'body_source':str(src),'body_source_sha256':r.sha(src),'parts':parts,'weapon':wp,
  'root_px':[256,472],'root_kind':'inherited_profile_origin_not_new_footlock_certificate','canvas_px':[512,512],
  'body_support_contact_px':b0,'body_manipulation_contact_px':b1,'manipulation_kind':['front_string_hook','rear_pull_tab_grasp','loading_bolt_pincher_negative_space','stock_primary_grip'][i],
  'sample_body_contact_rgba':list(source.getpixel(tuple(b1))),'sample_support_rgba':list(source.getpixel(tuple(b0))),
  'component_support_grip_px':c0,'component_manipulation_contact_px':c1,'sample_component_contact_rgba':list(weapon.getpixel(tuple(c1))),
  'weapon_scale':scale,'weapon_angle_image_clockwise_deg':math.degrees(theta),'component_to_body_affine_2x3':matrix,
  'transformed_manipulation_contact_px':near_actual,'manipulation_error_source_px':math.dist(near_actual,b1),'transformed_support_px':point(c0),'support_error_source_px':math.dist(point(c0),b0),
  'component_emit_px':component_emit[i],'transformed_emit_body_px':emit,'emit_delta_from_root_source_px':[emit[0]-256,emit[1]-472],
  'sampled_emit_alpha':weapon.getpixel(tuple(component_emit[i]))[3],'projectile_or_damage_events':[],'ammo_commit_event_from_image':False,
  'exact_body_source_reconstruction':True,'selection_masks_manual_not_semantic_certificate':True})
for name,im in sheets.items():
 q=P/f'reviews/XBW-reload-four-keyposes-{name}-v001.png';im.save(q);r.archive(q,q.relative_to(P),'four_actual_keypose_assembly_candidate_NOT_six_unique_frames_or_runtime_capture')
j=P/'reviews/XBW-reload-four-keypose-layer-candidate-v001.json';assert not j.exists();r.write(j,{'schema':'XBW_reload_four_native_keypose_candidate_v1','body_request':91,'weapon_request':92,'frames':rows,'canvas_px':[512,512],
 'source_body_keyposes':4,'source_weapon_states':4,'new_body_track_PNGs':12,'new_weapon_component_PNGs':4,'native_generation_requests_added_by_script':0,
 'draw_order':['body_far','independent_weapon_state','body_support','body_near'],'nominal_reload_duration_s':1.10,'keypose_edges_s':edges,
 'temporal_sampling':'four_real_keyposes_held_in_authoritative_reload_clock_not_six_interpolated_new_frames','fixed_weapon_scale_all_frames':scale,
 'body_geometry_transform':'none','component_geometry_transform':'one_uniform_scale_plus_rigid_rotation_translation_per_state_actual_source_coordinates',
 'mirror':'compose_right_then_mirror_once_x_left=511-x_pixelcenters_no_secondary_flip',
 'manual_assembly_review_passed':False,'runtime_verified':False,'full_reload_accepted':False,
 'limitations':['Four source keyposes, not six unique inbetweens; 1.10s coarse-hold smoothness must be tested in game.',
 'Component92 lower-row native placement is34px higher; actual component markers/matrix compensate without editing or boxfitting source pixels.',
 'Near-hand manipulation contacts differ from rear primary stock grip for stages0..2; pinch center may correctly be alpha0 between opaque fingers.',
 'Small rear capture is naturally hidden by side lock. No pixel claim for internal joint/cable routing under opaque stock.',
 'Cosmetic loaded bolt before1.10s is pending insertion; only actual ReloadComplete may add ammo. Cancellation must select logical instance weapon state.',
 'No ammo/damage/height/grounding/cancel/sound authority here. Source Emit is image-local geometry, never blindly add to D02 ground/jump combat Height.',
 'Four armor surfaces for these new reload poses remain unmade; this is common underclothes only.']});r.archive(j,j.relative_to(P),'honest_four_keypose_contact_and_1.10_timing_candidate_pending_visual_review')
print(json.dumps({'candidate':str(j),'sha256':r.sha(j),'body_PNGs':12,'weapon_PNGs':4,'errors':[x['manipulation_error_source_px'] for x in rows],'angles':[x['weapon_angle_image_clockwise_deg'] for x in rows]}))
