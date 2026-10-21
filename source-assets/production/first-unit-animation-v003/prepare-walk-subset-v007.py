"""Freeze only six alternating walk candidates; no pixel edits or engine access."""
from pathlib import Path
import argparse
import importlib.util
import math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('previous',P/'prepare-state-subset-v004.py')
previous=importlib.util.module_from_spec(s);s.loader.exec_module(previous)
GRIPS=[(192,353),(287,353),(211,352),(172,351),(98,367),(181,349)]
BELTS=[(273,338),(340,350),(297,338),(266,342),(234,357),(270,338)]
CROWNS=[112,130,111,117,135,113]
HELMET_X=[246,318,272,237,210,246]

def prepare():
 out=P/'import-subset-v007-candidate.json'
 if out.exists():raise ValueError('Do not overwrite candidate')
 basis=r.read(P/'import-subset-v005.json');markers=r.read(P/'assembly-markers-import-v005.json')
 folder=P/'processed/round-knight-walk-frame2-replacement-v003';meta=r.read(folder/'pipeline-meta.json')
 assert not any(meta[k] for k in ['edge_touch_frames','empty_frames','paste_clamped_frames'])
 assert meta['qc_summary']['profile_body_scale_drift']<=.08
 weapon=Image.open(P/'components/military-sword-clean-v001.png').convert('RGBA')
 wp=[(x,y) for y in range(512) for x in range(512) if weapon.getpixel((x,y))[3]>=128]
 frames=[];ms=[];previews=[];roots=[]
 sheet=Image.new('RGB',(1536,1024),(238,230,214))
 for i,(grip,belt) in enumerate(zip(GRIPS,BELTS)):
  f=folder/f'walk-{i+1}.png';body,pixels=previous.frame_pixels(f);x,y=grip
  assert body.getpixel(grip)[3]==255;root=[belt[0]-5,belt[1]+132];roots.append(root)
  roi=[x-26,y-26,x+26,y+26];patch=Image.new('RGBA',(512,512),(0,0,0,0));patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
  pd=P/'occlusion-patches-v007/walk';pd.mkdir(parents=True,exist_ok=True);pf=pd/f'near-grip-{i+1}.png';assert not pf.exists();patch.save(pf)
  r.archive(pf,Path('occlusion-patches-v007/walk')/pf.name,'real_source_ROI_not_complete_hand_layer')
  angle=30.;scale=.4;co=math.cos(math.radians(angle));si=math.sin(math.radians(angle))
  pts=[(x+scale*((u-99)*co-(v-256)*si),y+scale*((u-99)*si+(v-256)*co)) for u,v in wp]
  bounds=[min(q[0] for q in pts),min(q[1] for q in pts),max(q[0] for q in pts),max(q[1] for q in pts)]
  assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<512 and bounds[3]<512 and bounds[3]<root[1]
  c=co/scale;t=si/scale;sword=weapon.transform((512,512),Image.Transform.AFFINE,(c,t,99-c*x-t*y,-t,c,256+t*x-c*y),Image.Resampling.BICUBIC)
  assembled=body.copy();assembled.alpha_composite(sword);assembled.alpha_composite(patch)
  # Preview uses the exact future root translation. Runtime PNG is unchanged.
  bg=Image.new('RGBA',(512,512),(238,230,214,255));bg.alpha_composite(assembled,(256-root[0],472-root[1]))
  previews.append(bg.convert('RGB'));sheet.paste(previews[-1],((i%3)*512,(i//3)*512))
  common={'root_px':root,'ground_root_px':root,'root_kind':'manual_belt_proxy_no_single_foot_contact_claim',
   'belt_proxy_px':list(belt),'grip_px':list(grip),'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
   'weapon_visible':True,'near_grip_patch_path':str(pf),'near_grip_patch_sha256':r.sha(pf)}
  frames.append(dict(common,**pixels,index=i,source_frame_index=i,path=str(f),sha256=r.sha(f),
   phase=['contact','opposite_left_swing','passing','contact','opposite_right_swing','passing'][i],
   time_start_s=round(i*.1,9),time_end_s=round((i+1)*.1,9),
   original_processor_origin_px=meta['output_origin'],original_processor_selected_foot_anchor_px=meta['frames'][i]['anchor_source']))
  ms.append(dict(common,frame_index=i,frame_path=str(f),frame_sha256=r.sha(f),grip_rgba=list(body.getpixel(grip)),
   near_grip_occlusion_roi_px=roi,weapon_visible_bounds_px=bounds,
   measurement_status='manual_actual_fist_belt_proxy_pending_runtime_ground_contact',
   patch_semantics='source_52px_ROI_including_wrist_clothing_not_semantic_near_hand'))
 sp=P/'reviews/walk-root-aligned-assembly-v007.png';sheet.save(sp)
 gp=P/'reviews/walk-root-aligned-loop-v007.gif';previews[0].save(gp,save_all=True,append_images=previews[1:],duration=100,loop=0)
 for q in [sp,gp]:r.archive(q,Path('reviews')/q.name,'root_translated_component_preview_not_runtime_proof')
 relative_x=[x-root[0] for x,root in zip(HELMET_X,roots)];relative_y=[y-root[1] for y,root in zip(CROWNS,roots)]
 review={'source_request':44,'opposite_pose_reference_requests':[41,42],'rigid_helmet_width_range_px':[144,147],
  'rigid_helmet_height_range_px':[143,146],'manual_precision_px':3,
  'original_helmet_center_x_px':HELMET_X,'root_px':roots,'relative_helmet_x_px':relative_x,
  'relative_helmet_crown_y_px':relative_y,'relative_head_x_range_px':max(relative_x)-min(relative_x),
  'relative_crown_y_range_px':max(relative_y)-min(relative_y),
  'root_measurement':'same_idle_belt_to_ground_offset_[-5,132]_applied_to_actual_per_frame_buckle',
  'root_correction_changes_PNG':False,'per_frame_scale':False,
  'contact_limit':'swing_boot_sole_visible_in_frames1_4; lowest_pixel_is_not_certified_support_contact; actual_runtime_sliding_or_float_pending',
  'runtime_verified':False}
 assert review['relative_head_x_range_px']<=10 and review['relative_crown_y_range_px']<=10
 q=P/'reviews/walk-root-measurement-v007.json';r.write(q,review);r.archive(q,Path('reviews')/q.name,'manual_numeric_root_and_helmet_review_not_footlock_proof')
 raw=P/'raw/44-round-knight-walk-frame2-replacement-v003.png';ledger=r.read(P/'generation-ledger.json');entry=next(e for e in ledger['requests'] if e['request_number']==44)
 action={'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003','action':'walk',
  'armor_variant':'starter_composite_roundhelmet','source_request_number':44,'frame_count':6,'frames':frames,
  'loop':True,'total_duration_s':.6,'status':'alternating_walk_candidate_root_measured_pending_runtime',
  'game_phase_authority':'assistant_visual_loop_.6s_proposal_runtime_locomotion_speed_unchanged',
  'processor_qc':meta['qc_summary'],'source_to_output_scale':[.8533333333333333],'bbox_fit_applied':False,
  'preview_sheet':str(sp),'preview_gif':str(gp),'root_review':str(q),
  'source_provenance':{'raw_path':str(raw),'raw_sha256':r.sha(raw),'prompt_path':entry['prompt_path'],
   'prompt_sha256':r.sha(Path(entry['prompt_path'])),'backend':'image_gen.imagegen','host_fee_usd':None,
   'references':entry['references'],'CC0_structure_provenance':str(P/'references/kenney-six-pose-grid-provenance-v001.json')},
  'footlock_or_support_contact_accepted':False}
 basis.update(version=7,frozen=False,status='walk_only6_candidate_root_review_pending',actions=[action],
  actual_unique_animation_png_count=6,auxiliary_near_grip_patch_png_count=6,logical_state_mapping_count=1,
  manual_assembly_review='only_walk6_source_and_root_aligned_component_assembly_reviewed_after_FE_retention',
  generation_requests_new_visual_version=sum(1 for e in ledger['requests'] if e['request_number']>=19 and (
   e.get('source_directory')==str(P) or Path(e.get('raw_path','.')).parent.parent==P)),
  logical_frame_reference_count=6,previous_frozen_subset=str(P/'import-subset-v005.json'),
  delivery_scope='only_new_walk_merge_with_existing68_v005_do_not_reimport_or_replace_them',
  expected_merged_unique_body_count=74,
  generation_accounting={'cumulative_EV039_onward':ledger['requested_count'],'current_window':ledger['current_window'],
   'prior_EV038_calls':24,'lifetime_calls':ledger['lifetime_requested_count']},
  limitations=['candidate_only_runtime_ground_contact_foot_sliding_and_cycle_readability_pending',
   'manual_per_frame_belt_proxy_roots_required_do_not_force_[256,472]',
   'starter_composite_clothing_not_separate_armor','real_ROI_not_semantic_hand_layer',
   'full_content_acceptance_0_of_15_unchanged'])
 markers.update(version=7,actions=[{'actor':'hero','action':'walk','armor_variant':'starter_composite_roundhelmet','frames':ms}],
  previous_frozen_manifest=str(P/'assembly-markers-import-v005.json'),runtime_verified=False)
 r.write(P/'assembly-markers-import-v007-candidate.json',markers);r.write(out,basis)
 print({'candidate':str(out),'root_head_x_range':review['relative_head_x_range_px'],'root_crown_y_range':review['relative_crown_y_range_px']})

def freeze():
 out=P/'import-subset-v007.json';mp=P/'assembly-markers-import-v007.json';assert not out.exists() and not mp.exists()
 d=r.read(P/'import-subset-v007-candidate.json');m=r.read(P/'assembly-markers-import-v007-candidate.json')
 for f in d['actions'][0]['frames']:
  assert r.sha(Path(f['path']))==f['sha256'];assert r.sha(Path(f['near_grip_patch_path']))==f['near_grip_patch_sha256']
 d.update(frozen=True,status='walk_only6_root_reviewed_candidate_runtime_pending',assembly_markers_path=str(mp),
  manual_review='author_viewed_FE_retained_root_aligned6_assembly_and_actual_processed_frames')
 r.write(mp,m);d['assembly_markers_sha256']=r.sha(mp);r.write(out,d)
 for q in [out,mp]:r.archive(q,q.name,'frozen_only_walk6_candidate_runtime_pending')
 print({'path':str(out),'sha256':r.sha(out),'markers_sha256':r.sha(mp),'unique_body':6})

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');a=ap.parse_args()
 freeze() if a.freeze else prepare()
