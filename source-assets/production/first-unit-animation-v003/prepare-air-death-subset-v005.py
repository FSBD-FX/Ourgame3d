"""Append eight shared jump-family frames and six honest pose-aware death frames."""
from pathlib import Path
import argparse
import copy
import importlib.util
import math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('previous',P/'prepare-state-subset-v004.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous)
GRIPS=[(198,303),(204,301),(206,270),(146,274),(166,266),(192,279),(173,276),(193,299)]
BELTS=[(270,312),(272,315),(272,282),(257,294),(261,279),(265,280),(265,304),(278,291)]
ROOTS=[(256,394),(256,384),(267,414),(252,426),(256,411),(260,412),(256,391),(256,413)]

def prepare():
 draft=P/'import-subset-v005-candidate.json'
 if draft.exists():raise ValueError('Candidate already exists')
 subset=r.read(P/'import-subset-v004.json');markers=r.read(P/'assembly-markers-import-v004.json')
 ledger=r.read(P/'generation-ledger.json');weapon=Image.open(P/'components/military-sword-clean-v001.png').convert('RGBA')
 wp=[(x,y) for y in range(512) for x in range(512) if weapon.getpixel((x,y))[3]>=128]
 jump=P/'processed/round-knight-jump-family-padded-v001';jm=r.read(jump/'pipeline-meta.json')
 assert all(abs(f['source_to_output_scale']-.8533333333333333)<1e-9 for f in jm['frames'])
 assert jm['qc_summary']['profile_body_scale_drift']<=.08
 full_frames=[];full_markers=[];sheet=Image.new('RGB',(2048,1024),(238,230,214))
 for i,(grip,belt,root) in enumerate(zip(GRIPS,BELTS,ROOTS)):
  f=jump/f'jump-{i+1}.png';body,pixels=previous.frame_pixels(f);x,y=grip;assert body.getpixel(grip)[3]==255
  roi=[x-26,y-26,x+26,y+26];patch=Image.new('RGBA',(512,512),(0,0,0,0));patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
  pd=P/'occlusion-patches-v005/jump-family';pd.mkdir(parents=True,exist_ok=True)
  pf=pd/f'near-grip-{i+1}.png';assert not pf.exists();patch.save(pf)
  r.archive(pf,Path('occlusion-patches-v005/jump-family')/pf.name,'same_frame_ROI_not_semantic_hand_layer')
  angle=30.;co=math.cos(math.radians(angle));si=math.sin(math.radians(angle));scale=.4
  pts=[(x+scale*((u-99)*co-(v-256)*si),y+scale*((u-99)*si+(v-256)*co)) for u,v in wp]
  bounds=[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]
  assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<512 and bounds[3]<512
  assert bounds[3]<=root[1]
  c=co/scale;t=si/scale;sword=weapon.transform((512,512),Image.Transform.AFFINE,(c,t,99-c*x-t*y,-t,c,256+t*x-c*y),Image.Resampling.BICUBIC)
  result=body.copy();result.alpha_composite(sword);result.alpha_composite(patch)
  bg=Image.new('RGBA',(512,512),(238,230,214,255));bg.alpha_composite(result);sheet.paste(bg.convert('RGB'),((i%4)*512,(i//4)*512))
  kind='grounded_contact_estimate' if i in [0,1,6,7] else 'virtual_belt_proxy_ground_root'
  common={'grip_px':list(grip),'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
   'near_grip_patch_path':str(pf),'near_grip_patch_sha256':r.sha(pf),'ground_root_px':list(root),
   'root_px':list(root),'root_kind':kind,'belt_proxy_px':list(belt),'weapon_visible':True}
  full_frames.append(dict(common,**pixels,index=i,source_frame_index=i,path=str(f),sha256=r.sha(f)))
  full_markers.append(dict(common,frame_index=i,frame_path=str(f),frame_sha256=r.sha(f),
   near_grip_occlusion_roi_px=roi,weapon_visible_bounds_px=bounds,
   measurement_status='manual_closed_fist_and_root_proxy_review_pending_runtime',
   patch_semantics='52px_source_pixel_ROI_not_full_hand_layer'))
 sp=P/'reviews/jump-family-assembly-v005.png';sheet.save(sp);r.archive(sp,Path('reviews')/sp.name,'jump_family_candidate_assembly_pending_runtime')
 # These times sample nominal flat-ground flight only; height/landing remain actual actor facts.
 configs=[('jump',[0,1,2,3],[.05,.05,.15,.10],0.),('fall',[4,5],[.175,.175],.35),('land',[6,7],[.06,.06],None)]
 combat=previous.COMBAT
 for action,indices,dts,air_offset in configs:
  fs=[];ms=[];time=0.
  for n,(i,dt) in enumerate(zip(indices,dts)):
   frame=copy.deepcopy(full_frames[i]);frame.update(index=n,phase=action,time_start_s=round(time,9),time_end_s=round(time+dt,9))
   if air_offset is not None:frame.update(nominal_air_time_start_s=round(air_offset+time,9),nominal_air_time_end_s=round(air_offset+time+dt,9))
   fs.append(frame);mark=copy.deepcopy(full_markers[i]);mark['frame_index']=n;ms.append(mark);time+=dt
  subset['actions'].append({'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003',
   'action':action,'armor_variant':'starter_composite_roundhelmet','source_request_number':34,
   'frame_count':len(fs),'frames':fs,'loop':False,'total_duration_s':round(sum(dts),9),
   'status':'layout_calibrated_pose_aware_candidate_pending_runtime','processor_qc':jm['qc_summary'],
   'source_to_output_scale':[.8533333333333333],'bbox_fit_applied':False,'preview_sheet':str(sp),
   'timing_authority':'nominal_flat_flight_visual_mapping_only_actual_Z_velocity_contact_override',
   'timing_source':{'path':str(combat),'sha256':r.sha(combat),'flat_flight_s':.7,'launch_speed_cm_s':630,'gravity_cm_s2':1800},
   'land_visual_duration_is_assistant_presentation_proposal':action=='land',
   'land_grants_new_action_lock_or_iframes':False,'actorZ_is_only_global_height':True,
   'source_provenance':{'raw_path':str(P/'raw/34-round-knight-jump-family-body-v003.png'),
    'raw_sha256':r.sha(P/'raw/34-round-knight-jump-family-body-v003.png'),
    'derived_path':str(P/'derived/34-jump-512cell-padding-v001.png'),
    'derived_sha256':r.sha(P/'derived/34-jump-512cell-padding-v001.png'),
    'calibration_report':str(P/'reviews/jump-grid-padding-calibration-v001.json'),
    'operation':'native_cells_padded_no_subject_resize_same_existing_profile','generation_calls_added':0},
   'root_uncertainty_px':3})
  markers['actions'].append({'actor':'hero','action':action,'armor_variant':'starter_composite_roundhelmet','frames':ms})
 death=P/'processed/round-knight-death-body-v003';dm=r.read(death/'pipeline-meta.json');dfs=[];dms=[]
 death_sheet=Image.new('RGB',(1536,1024),(238,230,214));time=0.
 for i,dt in enumerate([.10,.10,.15,.15,.15,.15]):
  f=death/f'death-{i+1}.png';body,pixels=previous.frame_pixels(f)
  common={'weapon_visible':False,'grip_px':None,'weapon_angle_image_clockwise_deg':None,'weapon_scale':None,
   'near_grip_patch_path':None,'near_grip_patch_sha256':None,'ground_root_px':[256,472],
   'root_px':[256,472],'root_kind':'stable_death_ground_contact_estimate'}
  dfs.append(dict(common,**pixels,index=i,source_frame_index=i,path=str(f),sha256=r.sha(f),
   phase='collapse' if i<4 else 'corpse_hold',time_start_s=round(time,9),time_end_s=round(time+dt,9)))
  dms.append(dict(common,frame_index=i,frame_path=str(f),frame_sha256=r.sha(f),near_grip_occlusion_roi_px=None,
   measurement_status='hands_open_weapon_hidden_no_fabricated_socket',patch_semantics=None))
  bg=Image.new('RGBA',(512,512),(238,230,214,255));bg.alpha_composite(body);death_sheet.paste(bg.convert('RGB'),((i%3)*512,(i//3)*512));time+=dt
 dsp=P/'reviews/death-pose-aware-v005.png';death_sheet.save(dsp);r.archive(dsp,Path('reviews')/dsp.name,'death_pose_aware_candidate_original_strict_failure_retained')
 subset['actions'].append({'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003',
  'action':'death','armor_variant':'starter_composite_roundhelmet','source_request_number':33,'frame_count':6,'frames':dfs,
  'loop':False,'total_duration_s':.8,'hold_last_frame':True,
  'status':'pose_aware_candidate_original_grounded_strict_qc_FAILED_not_overridden',
  'processor_qc':dm['qc_summary'],'original_processor_exit_code':1,'ordinary_grounded_qc_pass':False,
  'pose_aware_review':{'rigid_helmet_major_minor_axes_px':{'frame1':[140,130],'frame4':[145,130],'frame6':[143,127]},
   'measurement_uncertainty_px':5,'all_processed_uniform_scale':.8533333333333333,
   'per_frame_bbox_scale':False,'body_clipping_seen':False,'last_two_remain_side_lying':True,
   'body_height_or_area_CV_not_applicable_to_collapse':True},
  'preview_sheet':str(dsp),'timing_authority':'assistant_visual_.8s_settle_proposal_actual_death_immediate',
  'weapon_policy':'hide_component_only_no_inventory_drop_or_ownership_change',
  'adapter_requirement':'must_support_weapon_visible_false_and_null_grip_ROI_without_fabricating_layers',
  'source_provenance':{'raw_path':str(P/'raw/33-round-knight-death-body-v003.png'),
   'raw_sha256':r.sha(P/'raw/33-round-knight-death-body-v003.png')}})
 markers['actions'].append({'actor':'hero','action':'death','armor_variant':'starter_composite_roundhelmet','frames':dms})
 unique={f['path'] for a in subset['actions'] for f in a['frames']};patches={f['near_grip_patch_path'] for a in subset['actions'] for f in a['frames'] if f.get('near_grip_patch_path')}
 assert len(unique)==68 and len(patches)==62
 subset.update(version=5,frozen=False,status='68unique_roundhelmet_candidate_manual_review_pending',
  actual_unique_animation_png_count=68,auxiliary_near_grip_patch_png_count=62,
  generation_requests_new_visual_version=sum(1 for e in ledger['requests'] if e['request_number']>=19 and (
   e.get('source_directory')==str(P) or Path(e.get('raw_path','.')).parent.parent==P)),
  logical_state_mapping_count=len(subset['actions']),logical_frame_reference_count=sum(len(a['frames']) for a in subset['actions']),
  previous_frozen_subset=str(P/'import-subset-v004.json'),
  generation_accounting={'cumulative_EV039_onward':ledger['requested_count'],'current_window':ledger['current_window'],
   'prior_EV038_calls':24,'lifetime_calls':ledger['lifetime_requested_count']},
  excluded_sources=[{'request':n,'action':'walk','reason':'failed_leg_alternation_or_order_not_accepted'} for n in [21,29,30,38,39]],
  limitations=['walk_still_missing','starter_clothing_body_not_isolated_armor_layer','real_hand_ROI_not_semantic_layer',
   'death_original_grounded_strict_failure_preserved_pose_aware_candidate_only','jump_roots_are_manual_proxies',
   'new_state_runtime_unverified','full_content_formal_acceptance_0_of_15_unchanged'])
 markers.update(version=5,previous_frozen_manifest=str(P/'assembly-markers-import-v004.json'),
  legal_hidden_weapon_frames='death_no_grip_no_ROI_only_visual_hide_never_inventory_drop')
 r.write(P/'assembly-markers-import-v005-candidate.json',markers);r.write(draft,subset)
 print({'candidate':str(draft),'unique':len(unique),'logical_frame_references':subset['logical_frame_reference_count'],'patches':len(patches)})

def freeze():
 out=P/'import-subset-v005.json';mp=P/'assembly-markers-import-v005.json'
 assert not out.exists() and not mp.exists()
 d=r.read(P/'import-subset-v005-candidate.json');m=r.read(P/'assembly-markers-import-v005-candidate.json')
 for a in d['actions']:
  for f in a['frames']:
   assert r.sha(Path(f['path']))==f['sha256']
   if f.get('near_grip_patch_path'):assert r.sha(Path(f['near_grip_patch_path']))==f['near_grip_patch_sha256']
 d.update(frozen=True,status='68unique_roundhelmet_pose_aware_candidate_manual_reviewed_pending_runtime',
  assembly_markers_path=str(mp),manual_assembly_review='author_viewed_jump_8_and_death_6_after_FE_preservation')
 r.write(mp,m);d['assembly_markers_sha256']=r.sha(mp);r.write(out,d)
 for q in [out,mp]:r.archive(q,q.name,'frozen68unique_candidate_not_formal_or_runtime_acceptance')
 print({'path':str(out),'sha256':r.sha(out),'markers_sha256':r.sha(mp),'unique':68,'logical_frame_references':74})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');a=ap.parse_args()
 freeze() if a.freeze else prepare()
