"""Shared .94 scale and measured rigid origin alignment; original anatomy never redrawn."""
from pathlib import Path
import importlib.util,math
from PIL import Image,ImageDraw,ImageChops,ImageOps
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
SCALE=.94
# Manual actual native fist centers, not skeleton joints (3px source uncertainty).
GRIPS=[(228,294),(230,294),(228,294),(236,262),(239,262),(224,262)]
SUPPORTS=[(333,299),(336,299),(331,300),(342,267),(342,267),(328,267)]
# Source contact evidence is intentionally distinct from an inferred ground root.
SOLES=[(183,471),(153,475),(308,477),(310,438),(345,444),(189,438)]
KINDS=['visible_flat_near_support_sole','extended_near_boot_toe_proxy_no_flat_support_demonstrated','visible_flat_far_support_sole','visible_flat_far_support_sole','extended_far_boot_toe_proxy_no_flat_support_demonstrated','visible_flat_near_support_sole']
def mask(poly):
 m=Image.new('L',(512,512),0);ImageDraw.Draw(m).polygon(poly,fill=255);return m
def select(src,m):
 im=src.copy();im.putalpha(ImageChops.multiply(src.getchannel('A'),m));im.putdata([px if px[3] else(0,0,0,0) for px in im.get_flattened_data()]);return im
def save(im,q,status):
 q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),status)
 return {'path':str(q),'sha256':r.sha(q),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None,'bbox_px':list(im.getchannel('A').getbbox()) if im.mode=='RGBA' else None}
def pt(m,p):return [m[0]*p[0]+m[1]*p[1]+m[2],m[3]*p[0]+m[4]*p[1]+m[5]]
life=P.parent/'first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json';d=r.read(life)
states=[d['states'][i] for i in [0,3]];rows=[]
sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['body','body_far','body_support','body_near','assembled_right','assembled_left']}
for i in range(6):
 source=P/f'processed/call117-fixed-canvas-v001/frame-{i}.png';native=Image.open(source).convert('RGBA')
 tx=256-SCALE*256;ty=472-SCALE*SOLES[i][1];forward=[SCALE,0,tx,0,SCALE,ty]
 body=native.transform((512,512),Image.Transform.AFFINE,(1/SCALE,0,-tx/SCALE,0,1/SCALE,-ty/SCALE),resample=Image.Resampling.BICUBIC)
 body.putdata([px if px[3] else(0,0,0,0) for px in body.get_flattened_data()])
 g=pt(forward,GRIPS[i]);h=pt(forward,SUPPORTS[i])
 near_poly=[pt(forward,(GRIPS[i][0]+dx,GRIPS[i][1]+dy)) for dx,dy in [(-28,-15),(-12,-21),(3,-20),(16,-14),(20,-4),(18,13),(8,21),(-8,20),(-22,13),(-28,4)]]
 support_poly=[pt(forward,(SUPPORTS[i][0]+dx,SUPPORTS[i][1]+dy)) for dx,dy in [(-28,-14),(-10,-21),(4,-20),(16,-14),(19,-4),(16,16),(4,24),(-12,22),(-23,14),(-28,3)]]
 near=mask(near_poly);support=mask(support_poly);assert not ImageChops.multiply(near,support).getbbox()
 parts={'body_far':select(body,ImageChops.invert(ImageChops.lighter(near,support))),'body_support':select(body,support),'body_near':select(body,near)}
 check=parts['body_far'].copy();check.alpha_composite(parts['body_support']);check.alpha_composite(parts['body_near']);assert check.tobytes()==body.tobytes()
 assert body.getpixel(tuple(round(x) for x in g))[3]==255 and body.getpixel(tuple(round(x) for x in h))[3]==255
 files={k:save(im,P/f'components/XBW-common-walk-v001/{k}-{i}.png','actual_native_derived_three_body_tracks_not_runtime_walk_acceptance') for k,im in parts.items()}
 bodyfile=save(body,P/f'processed/call117-common-profile-v001/body-{i}.png','one_shared_scale_point_aligned_body_candidate_original_raw_preserved')
 nm=P/f'masks/XBW-common-walk-near-{i}-v001.png';sm=P/f'masks/XBW-common-walk-support-{i}-v001.png';save(near,nm,'manual_distal_hand_mask');save(support,sm,'manual_distal_hand_mask')
 angle=math.atan2(h[1]-g[1],h[0]-g[0])-math.atan2(12,206);co=.48*math.cos(angle);si=.48*math.sin(angle)
 state_rows=[]
 for state in states:
  anchor=state['stock_grip_px'];m=[co,-si,g[0]-co*anchor[0]+si*anchor[1],si,co,g[1]-si*anchor[0]-co*anchor[1]]
  actual=pt(m,state['support_grip_px']);error=math.dist(actual,h);assert error<=3.129 # existing lifecycle maximum, not relaxed for this walk
  det=co*co+si*si;inv=(co/det,si/det,-(co*m[2]+si*m[5])/det,-si/det,co/det,-(-si*m[2]+co*m[5])/det)
  rendered=Image.open(state['path']).convert('RGBA').transform((512,512),Image.Transform.AFFINE,inv,resample=Image.Resampling.BICUBIC)
  state_rows.append({'state_index':state['state_index'],'path':state['path'],'sha256':state['sha256'],'stock_grip_px':anchor,'support_grip_px':state['support_grip_px'],'virtual_emit_px':state['emit_px'],'component_to_body_affine_2x3':m,'transformed_stock_px':pt(m,anchor),'transformed_support_px':actual,'support_alignment_error_px':error,'transformed_virtual_emit_body_px':pt(m,state['emit_px']),'emit_is_virtual_not_opaque_or_combat_Z':True})
  if state['state_index']==3:
   assembled=parts['body_far'].copy();assembled.alpha_composite(rendered);assembled.alpha_composite(parts['body_support']);assembled.alpha_composite(parts['body_near'])
 for name,im in [('body',body),*parts.items(),('assembled_right',assembled),('assembled_left',ImageOps.mirror(assembled))]:sheets[name].alpha_composite(im,((i%3)*512,(i//3)*512))
 rows.append({'index':i,'source_native_body_path':str(source),'source_native_body_sha256':r.sha(source),'source_body_path':bodyfile['path'],'source_body_sha256':bodyfile['sha256'],'source_body_transform_2x3':forward,'source_geometry_transform':'single_shared_uniform_scale_0.94_then_rigid_translation_no_frame_fit','source_sole_px':SOLES[i],'source_sole_measurement':KINDS[i],'sole_measurement_uncertainty_px':3,'transformed_sole_px':pt(forward,SOLES[i]),'ground_root_px':[256,472],'root_px':[256,472],'root_kind':'nominal_shared_ground_origin; source_two_stride_frames_contact_proxy_not_footlock','primary_grip_px':g,'grip_px':g,'support_grip_px':h,'native_primary_grip_px':GRIPS[i],'native_support_grip_px':SUPPORTS[i],'grip_measurement_uncertainty_native_px':3,'near_hand_polygon_px':near_poly,'support_hand_polygon_px':support_poly,'selection_masks':{'near':{'path':str(nm),'sha256':r.sha(nm)},'support':{'path':str(sm),'sha256':r.sha(sm)}},**files,'weapon_state_mappings':state_rows,'weapon_scale':.48,'weapon_angle_image_clockwise_deg':math.degrees(angle),'phase':'walk','time_start_s':i*.1,'time_end_s':(i+1)*.1,'body_three_track_exact_source_reconstruction':True,'weapon_visible':True,'runtime_verified':False})
previews=[]
for name,im in sheets.items():
 q=P/f'reviews/XBW-common-walk-{name}-v001.png';save(im,q,'static_native_derived_walk_assembly_candidate_not_footlock_or_runtime_certificate');previews.append({'kind':name,'path':str(q),'sha256':r.sha(q)})
q=P/'manifests/XBW-common-walk-candidate-v001.json';r.write(q,{'schema':'XBW-common-walk-three-body-track-candidate-v1','frame_count':6,'canvas_px':[512,512],'root_px':[256,472],'frames':rows,'previews':previews,'weapon_lifecycle_contract_path':str(life),'weapon_lifecycle_contract_sha256':r.sha(life),'draw_order':['body_far','independent_weapon','body_support','body_near'],'duration_s':.6,'loop':True,'actual_new_body_PNGs':18,'source_body_count':6,'fixed_body_scale':SCALE,'fixed_weapon_scale':.48,'max_support_alignment_error_px':max(s['support_alignment_error_px'] for f in rows for s in f['weapon_state_mappings']),'existing_support_error_ceiling_not_relaxed_px':3.129,'runtime_verified':False,'footlock_certified':False,'manual_assembly_review_passed':False});r.archive(q,q.relative_to(P),'walk_source_candidate_actual_measurements_pending_manual_review')
print({'body_tracks':18,'max_support_error':max(s['support_alignment_error_px'] for f in rows for s in f['weapon_state_mappings'])})
