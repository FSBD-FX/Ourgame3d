"""Manual grips and real-pixel evidence; composites existing layers only."""
from pathlib import Path
import importlib.util
import math
from PIL import Image

P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
CONFIG=[
 ('primary_2','primary2-hilt-clean',28,[(227,368),(134,343),(315,239),(192,114),(163,168),(176,227)],[30,50,-35,-35,-75,-80],[.15,.12,.27],[70,80,60,60,130,140]),
]
def main():
 out=P/'import-subset-v003.json'
 if out.exists():raise ValueError('Already frozen; create new version')
 subset=r.read(P/'import-subset-v002.json');markers=r.read(P/'assembly-markers-import-v002.json')
 w=P/'components/military-sword-clean-v001.png';weapon=Image.open(w).convert('RGBA')
 wp=[(x,y) for y in range(512) for x in range(512) if weapon.getpixel((x,y))[3]>=128]
 for action,folder,request,points,angles,phases,gifms in CONFIG:
  d=P/f'processed/round-knight-{folder}-v003';meta=r.read(d/'pipeline-meta.json')
  assert meta['output_origin']==[256.,472] and not meta['edge_touch_frames'] and not meta['paste_clamped_frames'] and not meta['empty_frames']
  assert meta['qc_summary']['profile_body_scale_drift']<=.08
  fs=[];ms=[];assembled=[];sheet=Image.new('RGBA',(1536,1024),(238,230,214,255));time=0.
  durations=[phases[0]/2]*2+[phases[1]/2]*2+[phases[2]/2]*2
  for i,(grip,angle,dt) in enumerate(zip(points,angles,durations)):
   f=d/f'attack-{i+1}.png';body=Image.open(f)
   assert body.mode=='RGBA' and body.size==(512,512)
   alpha=body.getchannel('A');assert alpha.getextrema()==(0,255)
   corners=[body.getpixel(q) for q in [(0,0),(511,0),(0,511),(511,511)]];assert all(q[3]==0 for q in corners)
   visible=[q for q in body.getdata() if q[3]>=128]
   magenta=sum(q[0]>180 and q[2]>150 and q[1]<120 for q in visible);assert magenta/max(1,len(visible))<.001
   rgba=body.getpixel(grip);assert rgba[3]==255 # A manually viewed finger crease may be dark brown.
   roi=[grip[0]-26,grip[1]-26,grip[0]+26,grip[1]+26]
   patch=Image.new('RGBA',(512,512),(0,0,0,0));patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
   pd=P/'occlusion-patches'/action;pd.mkdir(exist_ok=True)
   pf=pd/f'near-grip-{i+1}.png';assert not pf.exists();patch.save(pf)
   r.archive(pf,Path('occlusion-patches')/action/pf.name,'same_frame_52x52_ROI_not_complete_hand_layer')
   a=math.radians(angle);co=math.cos(a);si=math.sin(a);x,y=grip;scale=.4
   transformed=[(x+scale*((qx-99)*co-(qy-256)*si),y+scale*((qx-99)*si+(qy-256)*co)) for qx,qy in wp]
   bounds=[min(q[0] for q in transformed),min(q[1] for q in transformed),max(q[0] for q in transformed),max(q[1] for q in transformed)]
   assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<512 and bounds[3]<512,(action,i,bounds)
   assert bounds[3]<=472,(action,i,'sword penetrates authored ground root',bounds)
   c=co/scale;t=si/scale
   sword=weapon.transform((512,512),Image.Transform.AFFINE,(c,t,99-c*x-t*y,-t,c,256+t*x-c*y),Image.Resampling.BICUBIC)
   result=body.copy();result.alpha_composite(sword);result.alpha_composite(patch)
   preview=Image.new('RGBA',(512,512),(238,230,214,255));preview.alpha_composite(result)
   assembled.append(preview.convert('RGB'));sheet.alpha_composite(result,((i%3)*512,(i//3)*512))
   common={'grip_px':list(grip),'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
    'near_grip_patch_path':str(pf),'near_grip_patch_sha256':r.sha(pf),'ground_root_px':[256,472]}
   ms.append(dict(common,frame_index=i,frame_path=str(f),frame_sha256=r.sha(f),grip_rgba=list(rgba),
    measurement_status='manual_pixel_review_and_raw_to_processor_transform_pending_runtime',
    near_grip_occlusion_roi_px=roi,weapon_visible_bounds_px=bounds,
    patch_semantics='source_pixels_in_52x52_ROI_including_some_wrist_or_clothing_not_semantic_hand_or_armor_layer'))
   fs.append(dict(common,index=i,source_frame_index=i,path=str(f),sha256=r.sha(f),canvas_px=[512,512],mode='RGBA',bit_depth=8,
    alpha_extrema=list(alpha.getextrema()),corner_rgba=[list(q) for q in corners],corners_transparent=True,
    bbox_px=list(alpha.getbbox()),opaque_magenta_like_pixels=magenta,opaque_magenta_like_fraction=magenta/max(1,len(visible)),
    root_px=[256,472],phase=['windup','active','recovery'][i//2],time_start_s=round(time,9),time_end_s=round(time+dt,9)))
   time+=dt
  sp=P/f'reviews/{action}-assembly-v003.png';sheet.save(sp)
  gp=P/f'reviews/{action}-phase-preview-v003.gif';assembled[0].save(gp,save_all=True,append_images=assembled[1:],duration=gifms,loop=0)
  for q in [sp,gp]:r.archive(q,Path('reviews')/q.name,'manual_finished_sprite_assembly_candidate_not_runtime')
  subset['actions'].append({'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003',
   'action':action,'armor_variant':'starter_composite_roundhelmet','source_request_number':request,
   'status':'manual_assembly_candidate_pending_runtime','frame_count':6,'frames':fs,
   'phase_mapping':{'windup':[0,1],'active':[2,3],'recovery':[4,5]},
   'phase_duration_s':dict(zip(['windup','active','recovery'],phases)), 'total_duration_s':round(sum(phases),9),
   'loop':False,'processor_qc':meta['qc_summary'],'source_to_output_scale':[.8533333333333333],
   'bbox_fit_applied':False,'preview_sheet':str(sp),'preview_gif':str(gp),
   'gif_quantization_ms':gifms,'game_phase_authority':'exact_JSON_phase_times_not_GIF'})
  markers['actions'].append({'actor':'hero','action':action,'armor_variant':'starter_composite_roundhelmet','frames':ms})
 mp=P/'assembly-markers-import-v003.json';markers.update(version=3,previous_frozen_manifest=str(P/'assembly-markers-import-v002.json'));r.write(mp,markers)
 subset.update(version=3,status='EV042_idle_and_three_attacks_candidate_not_runtime_accepted',
  actual_unique_animation_png_count=24,auxiliary_near_grip_patch_png_count=24,logical_state_mapping_count=4,
  generation_accounting={"cumulative_EV039_onward":29,"current_window":2,"current_window_requests":5,"current_window_limit":24,"new_visual_identity_calls":8,"environment_calls":3,"prior_EV038_calls":24,"lifetime_calls":53},generation_requests_new_visual_version=8,
  assembly_markers_path=str(mp),assembly_markers_sha256=r.sha(mp),previous_frozen_subset=str(P/'import-subset-v002.json'),
  excluded_sources=[{'request':21,'action':'walk','reason':'one_sided_or_repeated_gait_needs_correction'},
                    {'request':29,'action':'walk','reason':'second_text_only_walk_still_repeats_one_sided_leg_pattern'}],
  limitations=['starter_clothing_body_composite_not_armor_overlay','full_near_far_semantic_layer_contract_unfulfilled',
   'manual_ROI_pixel_replay_not_full_hand_layer','walk_excluded_not_complete_newidentity_actions',
   'gameplay_collision_damage_and_phase_rules_unchanged_by_art','runtime_verified_false'])
 subset.pop('generation_accounting_window_requests_used_at_freeze',None)
 subset['superseded_sources']=[{'request':23,'action':'primary_2','superseded_by':28,'reason':'baked_hilt_removed_in_native_image_edit'}]
 r.write(out,subset)
 for q in [mp,out]:r.archive(q,q.name,'frozen_EV042_candidate_idle_P1_P2_P3_import_contract')
 print({'path':str(out),'sha256':r.sha(out),'body_frames':24,'roi_patches':24})

if __name__=='__main__':main()
