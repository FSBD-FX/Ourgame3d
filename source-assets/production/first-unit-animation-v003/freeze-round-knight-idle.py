"""Freeze real PNG evidence and composite existing sword; never draws raw art."""
from pathlib import Path
import importlib.util
import math
from PIL import Image

P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
GRIPS=[(185,335),(184,334),(184,335),(184,336),(185,336),(186,336)]

def main():
    destination=P/'import-subset-v001.json'
    if destination.exists():raise ValueError('Frozen; never overwrite')
    d=P/'processed/round-knight-idle-body-v003'
    meta=r.read(d/'pipeline-meta.json')
    assert meta['output_origin']==[256.,472]
    assert not meta['edge_touch_frames'] and not meta['paste_clamped_frames'] and not meta['empty_frames']
    w=P/'components/military-sword-clean-v001.png'
    weapon=Image.open(w).convert('RGBA')
    frames=[];marks=[];assembled=[]
    sheet=Image.new('RGBA',(1536,1024),(238,230,214,255))
    for i,g in enumerate(GRIPS):
        f=d/f'idle-{i+1}.png';body=Image.open(f)
        assert body.mode=='RGBA' and body.size==(512,512)
        alpha=body.getchannel('A');assert alpha.getextrema()==(0,255)
        corners=[body.getpixel(q) for q in [(0,0),(511,0),(0,511),(511,511)]]
        assert all(q[3]==0 for q in corners)
        visible=[q for q in body.getdata() if q[3]>=128]
        magenta=sum(q[0]>180 and q[2]>150 and q[1]<120 for q in visible)
        assert magenta/max(1,len(visible))<.001
        grip=body.getpixel(g);assert grip[3]==255 and grip[0]>150 and grip[1]>70,(g,grip)
        roi=[g[0]-18,g[1]-18,g[0]+18,g[1]+18]
        patch=Image.new('RGBA',(512,512),(0,0,0,0));patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
        pf=P/'occlusion-patches'/f'idle-near-grip-{i+1}.png';assert not pf.exists();patch.save(pf)
        r.archive(pf,Path('occlusion-patches')/pf.name,'same_frame_near_fist_ROI_not_semantic_layer')
        angle=35.;scale=.4;a=math.radians(angle);c=math.cos(a)/scale;t=math.sin(a)/scale;x,y=g
        sword=weapon.transform((512,512),Image.Transform.AFFINE,
            (c,t,99-c*x-t*y,-t,c,256+t*x-c*y),Image.Resampling.BICUBIC)
        result=body.copy();result.alpha_composite(sword);result.alpha_composite(patch)
        preview=Image.new('RGBA',(512,512),(238,230,214,255));preview.alpha_composite(result)
        assembled.append(preview.convert('RGB'));sheet.alpha_composite(result,((i%3)*512,(i//3)*512))
        mark={'frame_index':i,'frame_path':str(f),'frame_sha256':r.sha(f),'grip_px':list(g),
            'grip_rgba':list(grip),'ground_root_px':[256,472],
            'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
            'measurement_status':'manual_visible_empty_fist_pixel_position_not_runtime_verified',
            'near_grip_occlusion_roi_px':roi,'near_grip_patch_path':str(pf),
            'near_grip_patch_sha256':r.sha(pf),
            'patch_semantics':'original_source_pixels_in_36x36_ROI_includes_small_wrist_or_coat_region_not_complete_hand_or_armor_layer'}
        marks.append(mark)
        frames.append({'index':i,'source_frame_index':i,'path':str(f),'sha256':r.sha(f),
            'canvas_px':[512,512],'mode':'RGBA','bit_depth':8,'alpha_extrema':list(alpha.getextrema()),
            'corner_rgba':[list(q) for q in corners],'corners_transparent':True,'bbox_px':list(alpha.getbbox()),
            'opaque_magenta_like_pixels':magenta,'opaque_magenta_like_fraction':magenta/max(1,len(visible)),
            'root_px':[256,472],'ground_root_px':[256,472],
            'grip_px':list(g),'weapon_angle_image_clockwise_deg':angle,'weapon_scale':scale,
            'near_grip_patch_path':str(pf),'near_grip_patch_sha256':r.sha(pf),
            'phase':'idle_loop','time_start_s':round(i*.15,9),'time_end_s':round((i+1)*.15,9),
            'actual_bottom_y_exclusive':alpha.getbbox()[3]})
    sp=P/'reviews/round-knight-idle-assembly-v001.png';sheet.save(sp)
    gp=P/'reviews/round-knight-idle-assembly-v001.gif'
    assembled[0].save(gp,save_all=True,append_images=assembled[1:],duration=150,loop=0)
    # Display scale simulation only; both completed sprite layers mirror together once.
    small=assembled[0].resize((160,160),Image.Resampling.LANCZOS)
    display=Image.new('RGB',(320,160),(238,230,214));display.paste(small,(0,0));display.paste(small.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(160,0))
    dp=P/'reviews/round-knight-160canvas-right-left-preview-v001.png';display.save(dp)
    for q in [sp,gp,dp]:r.archive(q,Path('reviews')/q.name,'deterministic_finished_sprite_assembly_preview_not_runtime')
    mp=P/'assembly-markers-import-v001.json'
    r.write(mp,{'schema':'manual-sword-assembly-markers-v1','version':1,'frozen':True,
        'actor_identity':'EV042_round_enclosed_helmet_little_knight_v003','runtime_verified':False,
        'angle_convention':'image_xy_y_down_positive_clockwise',
        'mirror_policy':'one_runtime_mirror_after_body_weapon_patch_assembly_no_preflipped_source',
        'weapon_grip_px':[99,256],'weapon_tip_px':[482,256],'weapon_scale':.4,
        'actions':[{'actor':'hero','action':'idle','armor_variant':'starter_composite_roundhelmet','frames':marks}],
        'limitations':['starter_clothing_baked_into_body','ROI_patch_not_complete_near_far_hand_layer','no_independent_armor_overlay']})
    action={'actor':'hero','actor_identity':'EV042_round_enclosed_helmet_little_knight_v003',
        'action':'idle','armor_variant':'starter_composite_roundhelmet','source_request_number':20,
        'status':'enclosed_identity_candidate_pixel_qc_pass_manual_assembly_pending_runtime',
        'frame_count':6,'frames':frames,'phase_mapping':{'idle_loop':[0,1,2,3,4,5]},
        'total_duration_s':.9,'loop':True,'frame_duration_s':.15,'processor_qc':meta['qc_summary'],
        'source_to_output_scale':[.8533333333333333],'bbox_fit_applied':False,
        'preview_sheet':str(sp),'preview_gif':str(gp)}
    r.write(destination,{'schema':'first-unit-import-subset-v1','version':1,'visual_version':'v003_EV042',
        'frozen':True,'status':'new_roundhelmet_idle_candidate_not_runtime_accepted',
        'authorization_events':['EV-039','EV-040','EV-041','EV-042'],
        'generation_accounting_window_requests_used_at_freeze':20,'generation_requests_new_visual_version':2,
        'carried_old_direction_requests':18,'host_fee_usd':None,'external_api_calls':0,
        'actual_unique_animation_png_count':6,'auxiliary_near_grip_patch_png_count':6,
        'logical_state_mapping_count':1,'actions':[action],
        'components':[{'file':str(w),'sha256':r.sha(w),'grip_px':[99,256],'tip_px':[482,256],
            'reused_from_frozen_v001':True,'new_generation_calls':0}],
        'assembly_markers_path':str(mp),'assembly_markers_sha256':r.sha(mp),
        'mirror_policy':'one_runtime_mirror_after_body_weapon_patch_assembly_no_preflipped_source',
        'runtime_verified':False,'formal_content_atlas_validation_passed':False,
        'limitations':['only_idle_no_new_walk_or_attacks','starter_clothing_body_composite_not_armor_overlay',
            'full_body_near_far_layer_contract_unfulfilled','six_36x36_ROI_patches_are_auxiliary_not_new_bodyframes',
            'manual_angles_and_occlusion_need_engine_review','groundroot472_is_processor_anchor_actual_bootbottom482_to484']})
    for q in [mp,destination]:r.archive(q,q.name,'frozen_EV042_roundhelmet_idle_candidate_import_contract')
    print({'import':str(destination),'sha256':r.sha(destination),'unique_body_frames':6,'auxiliary_patches':6,
        'new_visual_calls':2,'window_requests_used':20,'runtime_verified':False})

if __name__=='__main__':main()
