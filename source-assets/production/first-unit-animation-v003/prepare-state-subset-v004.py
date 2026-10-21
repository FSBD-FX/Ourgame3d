"""Build reviewed real-sprite assemblies, then freeze a new import contract.

Never changes source PNGs, earlier subsets, gameplay clocks, or engine files.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import math
from PIL import Image

P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
COMBAT=P.parents[2]/'docs/design/player-combat-v1/player-combat-rules.json'
WEAPONS=P.parents[2]/'docs/design/equipment-v1/weapons.json'
CONFIG=[
 ('hurt','hurt','hurt',31,.4,None),
 ('dodge','dodge','dodge',32,.4,None),
 ('secondary','secondary','attack',35,.68,[.20,.10,.38]),
 ('air_primary_1','air-primary1','attack',36,.60,[.17,.12,.31]),
 ('equip_weapon','equip','idle',37,.35,None),
 ('equip_armor','equip','idle',37,.50,None),
]

def frame_pixels(path):
 im=Image.open(path);assert im.mode=='RGBA' and im.size==(512,512)
 alpha=im.getchannel('A');assert alpha.getextrema()==(0,255)
 corners=[list(im.getpixel(q)) for q in [(0,0),(511,0),(0,511),(511,511)]]
 assert all(q[3]==0 for q in corners)
 pixels=[q for q in im.get_flattened_data() if q[3]>=128]
 bad=sum(q[0]>180 and q[2]>150 and q[1]<120 for q in pixels)
 assert bad/max(1,len(pixels))<.001
 return im,{'canvas_px':[512,512],'mode':'RGBA','bit_depth':8,
  'alpha_extrema':[0,255],'corner_rgba':corners,'corners_transparent':True,
  'bbox_px':list(alpha.getbbox()),'opaque_magenta_like_pixels':bad,
  'opaque_magenta_like_fraction':bad/max(1,len(pixels))}

def prepare():
 draft=P/'import-subset-v004-candidate.json'
 if draft.exists():raise ValueError('Do not overwrite a prepared candidate')
 subset=r.read(P/'import-subset-v003.json');markers=r.read(P/'assembly-markers-import-v003.json')
 measurements=r.read(P/'reviews/manual-state-grip-measurements-v005.json')
 ledger=r.read(P/'generation-ledger.json')
 weapon_path=P/'components/military-sword-clean-v001.png';weapon=Image.open(weapon_path).convert('RGBA')
 wp=[(x,y) for y in range(512) for x in range(512) if weapon.getpixel((x,y))[3]>=128]
 cache={}
 for action,slug,prefix,request,total,phases in CONFIG:
  measure=next(a for a in measurements['actions'] if a['action']==slug)
  entry=next(a for a in ledger['requests'] if a['request_number']==request)
  assert r.sha(Path(entry['raw_path']))==entry['sha256']
  folder=P/f'processed/round-knight-{slug}-body-v003';meta=r.read(folder/'pipeline-meta.json')
  assert not any(meta[k] for k in ['edge_touch_frames','empty_frames','paste_clamped_frames'])
  assert meta['qc_summary']['profile_body_scale_drift']<=.08
  assert all(abs(f['source_to_output_scale']-.8533333333333333)<1e-9 for f in meta['frames'])
  durations=([phases[0]/2]*2+[phases[1]/2]*2+[phases[2]/2]*2) if phases else [total/6]*6
  fs=[];ms=[];assembled=[];time=0.
  for i,(point,dt) in enumerate(zip(measure['frames'],durations)):
   f=Path(point['frame_path']);assert r.sha(f)==point['frame_sha256']
   body,pixel=frame_pixels(f);x,y=point['grip_px'];angle=point['weapon_angle_image_clockwise_deg']
   assert body.getpixel((x,y))[3]==255
   roi=[x-26,y-26,x+26,y+26]
   patchfile=P/f'occlusion-patches-v004/{slug}/near-grip-{i+1}.png'
   if (slug,i) not in cache:
    patchfile.parent.mkdir(parents=True,exist_ok=True)
    patch=Image.new('RGBA',(512,512),(0,0,0,0));patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
    if patchfile.exists():assert Image.open(patchfile).tobytes()==patch.tobytes()
    else:patch.save(patchfile)
    r.archive(patchfile,Path('occlusion-patches-v004')/slug/patchfile.name,'same_frame_ROI_not_semantic_hand_or_armor_layer')
    cache[(slug,i)]=patch
   patch=cache[(slug,i)]
   a=math.radians(angle);co=math.cos(a);si=math.sin(a);scale=.4
   pts=[(x+scale*((u-99)*co-(v-256)*si),y+scale*((u-99)*si+(v-256)*co)) for u,v in wp]
   bounds=[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]
   assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<512 and bounds[3]<512
   assert bounds[3]<=point['root_px'][1]
   c=co/scale;t=si/scale
   sword=weapon.transform((512,512),Image.Transform.AFFINE,(c,t,99-c*x-t*y,-t,c,256+t*x-c*y),Image.Resampling.BICUBIC)
   result=body.copy();result.alpha_composite(sword);result.alpha_composite(patch)
   bg=Image.new('RGBA',(512,512),(238,230,214,255));bg.alpha_composite(result);assembled.append(bg.convert('RGB'))
   common={'grip_px':[x,y],'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
    'near_grip_patch_path':str(patchfile),'near_grip_patch_sha256':r.sha(patchfile),
    'ground_root_px':point['root_px'],'root_kind':point['root_kind']}
   if 'belt_proxy_px' in point:common['belt_proxy_px']=point['belt_proxy_px']
   phase=['windup','active','recovery'][i//2] if phases else action
   fs.append(dict(common,**pixel,index=i,source_frame_index=i,path=str(f),sha256=r.sha(f),
    root_px=point['root_px'],phase=phase,time_start_s=round(time,9),time_end_s=round(time+dt,9)))
   ms.append(dict(common,frame_index=i,frame_path=str(f),frame_sha256=r.sha(f),grip_rgba=list(body.getpixel((x,y))),
    near_grip_occlusion_roi_px=roi,weapon_visible_bounds_px=bounds,
    measurement_status='manual_processed_pixel_grip_and_proxy_root_review_pending_runtime',
    patch_semantics='52px_ROI_source_pixel_replay_including_wrist_clothing_not_semantic_hand_layer'))
   time+=dt
  sheet=Image.new('RGB',(1536,1024),(238,230,214))
  for i,im in enumerate(assembled):sheet.paste(im,((i%3)*512,(i//3)*512))
  sp=P/f'reviews/{action}-assembly-v004.png'
  if sp.exists():assert Image.open(sp).convert('RGB').tobytes()==sheet.tobytes()
  else:sheet.save(sp)
  r.archive(sp,Path('reviews')/sp.name,'real_sprite_component_assembly_candidate_pending_review')
  item={'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003',
   'action':action,'armor_variant':'starter_composite_roundhelmet','source_request_number':request,
   'frame_count':6,'frames':fs,'loop':False,'total_duration_s':total,
   'status':'manual_assembly_candidate_pending_runtime','processor_qc':meta['qc_summary'],
   'source_to_output_scale':[.8533333333333333],'bbox_fit_applied':False,'preview_sheet':str(sp),
   'source_provenance':{'raw_path':entry['raw_path'],'raw_sha256':entry['sha256'],
    'prompt_path':entry['prompt_path'],'prompt_sha256':r.sha(Path(entry['prompt_path'])),
    'backend':'image_gen.imagegen','host_fee_usd':None,'references':entry['references']},
   'game_phase_authority':'source_design_and_runtime_action_clock_not_art_or_preview',
   'timing_source':{'path':str(COMBAT),'sha256':r.sha(COMBAT)}}
  if phases:
   item.update(phase_mapping={'windup':[0,1],'active':[2,3],'recovery':[4,5]},
    phase_duration_s=dict(zip(['windup','active','recovery'],phases)))
  if action=='secondary':
   item['timing_source']={'path':str(WEAPONS),'sha256':r.sha(WEAPONS),'weapon_id':'WPN-SWD-001','field':'secondary'}
   item['movement_authority']='runtime_only_collision_limited_advance_30cm_not_baked_in_sprite'
  elif action=='air_primary_1':
   item.update(virtual_root_measurements=str(P/'reviews/manual-state-grip-measurements-v005.json'),
    actual_height_authority='actorZ_only_no_sprite_global_jump_trajectory',
    attack_authority='existing_primary1_timeline_once_per_takeoff_no_extra_land_hit',
    root_estimation_uncertainty_px=3)
  elif action=='hurt':
   item['selection_guard']='only_actual_poise_break_stun_.4s_not_every_HP_loss_or_.65s_damage_iframes'
  elif action=='dodge':
   item['gameplay_iframe_interval_s']=[.06,.20];item['gameplay_iframe_end_exclusive']=True
  else:
   item['transaction_guard']='visual_sampling_only_actual_equipment_commit_and_cancel_remain_runtime_authority'
  subset['actions'].append(item)
  markers['actions'].append({'actor':'hero','action':action,'armor_variant':'starter_composite_roundhelmet','frames':ms})
 body_paths={f['path'] for a in subset['actions'] for f in a['frames']}
 patch_paths={f['near_grip_patch_path'] for a in subset['actions'] for f in a['frames']}
 assert len(body_paths)==54 and len(patch_paths)==54
 for f in body_paths:frame_pixels(Path(f))
 subset.update(version=4,frozen=False,status='expanded_state_candidate_manual_assembly_review_pending',
  actual_unique_animation_png_count=54,auxiliary_near_grip_patch_png_count=54,
  logical_state_mapping_count=len(subset['actions']),previous_frozen_subset=str(P/'import-subset-v003.json'),
  generation_accounting={'cumulative_EV039_onward':ledger['requested_count'],'current_window':ledger['current_window'],
   'prior_EV038_calls':24,'lifetime_calls':ledger['lifetime_requested_count']},
  unique_frame_count_rule='equip_weapon_and_equip_armor_reuse_same6_pngs_count_once',
  excluded_sources=[{'request':n,'action':'walk','reason':'gait_failed_not_frozen'} for n in [21,29,30]]+[
   {'request':33,'action':'death','reason':'strict_grounded_qc_failed_pose_aware_review_pending'},
   {'request':34,'action':'jump_family','reason':'rigid_helmet_cross_clip_scale_mismatch_and_virtual_roots_pending'}],
  limitations=['starter_clothing_body_composite_not_isolated_armor_overlay','ROI_replay_not_complete_hand_layer',
   'walk_jump_fall_land_death_not_included','new_states_runtime_not_verified',
   'source_design_timing_is_not_runtime_implementation_evidence'])
 subset['generation_requests_new_visual_version']=sum(1 for e in ledger['requests'] if e['request_number']>=19 and (
  e.get('source_directory')==str(P) or Path(e.get('raw_path','.')).parent.parent==P))
 markers.update(version=4,previous_frozen_manifest=str(P/'assembly-markers-import-v003.json'),
  root_convention='grounded_profile_estimate_or_explicit_per_frame_airborne_virtual_proxy',runtime_verified=False)
 r.write(P/'assembly-markers-import-v004-candidate.json',markers);r.write(draft,subset)
 print({'candidate':str(draft),'body_unique':54,'roi_unique':54,'logical_states':len(subset['actions'])})

def freeze():
 out=P/'import-subset-v004.json';mp=P/'assembly-markers-import-v004.json'
 if out.exists() or mp.exists():raise ValueError('Frozen output exists')
 subset=r.read(P/'import-subset-v004-candidate.json');markers=r.read(P/'assembly-markers-import-v004-candidate.json')
 assert subset['actual_unique_animation_png_count']==54
 for a in subset['actions']:
  for f in a['frames']:
   assert r.sha(Path(f['path']))==f['sha256'];assert r.sha(Path(f['near_grip_patch_path']))==f['near_grip_patch_sha256']
 subset.update(frozen=True,status='EV042_expanded54_candidate_manual_assembly_reviewed_pending_runtime',
  manual_assembly_review='author_viewed_all_six_new_logical_assembly_sheets_after_FE_preservation',
  assembly_markers_path=str(mp));r.write(mp,markers);subset['assembly_markers_sha256']=r.sha(mp)
 r.write(out,subset)
 for q in [mp,out]:r.archive(q,q.name,'frozen_expanded_real_png_candidate_not_runtime_acceptance')
 print({'path':str(out),'sha256':r.sha(out),'markers':str(mp),'markers_sha256':r.sha(mp),
        'body_unique':54,'new_unique_body_frames':30,'logical_states':len(subset['actions'])})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');a=ap.parse_args()
 freeze() if a.freeze else prepare()
