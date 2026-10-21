"""Audit generated PNG pixels and assemble finished sprites; never draws raw art.

Coordinates/angles below are manually chosen from archived frame views. Hand
patches contain only pixels copied from the same source frame in a stated ROI;
they are not complete semantic body/hand/armor layers.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
from PIL import Image

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('record', ROOT/'production-record.py')
record = importlib.util.module_from_spec(spec)
spec.loader.exec_module(record)
CONFIG = [
    ('primary_1', 'hero-sword-primary1-body-v002', 1,
     [(121,183),(155,151),(297,250),(317,359),(265,372),(195,353)],
     [-125,-65,20,40,30,-35], [.17,.12,.31]),
    ('primary_2', 'hero-sword-primary2-hilt-clean-v002', 3,
     [(250,340),(118,342),(286,265),(197,160),(197,249),(210,264)],
     [30,50,-35,-70,-30,-55], [.15,.12,.27]),
    ('primary_3', 'hero-sword-primary3-body-v002', 4,
     [(150,233),(182,154),(261,356),(274,402),(177,334),(187,354)],
     [-70,-65,35,15,-20,-35], [.22,.12,.32]),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def audit(p):
    with Image.open(p) as original:
        assert original.mode == 'RGBA' and original.size == (512,512), p
        im = original.copy()
    alpha = im.getchannel('A')
    assert alpha.getextrema() == (0,255), p
    corners = [im.getpixel(q) for q in [(0,0),(511,0),(0,511),(511,511)]]
    assert all(q[3] == 0 for q in corners), p
    pixels = list(im.getdata())
    visible = sum(a >= 128 for r,g,b,a in pixels)
    magenta = sum(a>=128 and r>180 and b>150 and g<120 for r,g,b,a in pixels)
    assert visible > 0 and magenta/visible < .001, (p,magenta,visible)
    return {'path':str(p),'sha256':sha(p),'canvas_px':[512,512],'mode':'RGBA','bit_depth':8,
            'alpha_extrema':list(alpha.getextrema()),'corner_rgba':[list(x) for x in corners],
            'corners_transparent':True,'transparent_pixel_count':sum(a==0 for r,g,b,a in pixels),
            'visible_pixel_count_alpha_ge_128':visible,'bbox_px':list(alpha.getbbox()),
            'opaque_magenta_like_pixels':magenta,'opaque_magenta_like_fraction':magenta/visible,
            'ground_root_px':[256,472],'root_px':[256,472]}


def main():
    destination = ROOT/'import-subset-v001.json'
    if destination.exists():
        raise RuntimeError('Import subset is frozen: create a new version instead')
    ledger = record.read(ROOT/'generation-ledger.json')
    weapon_path = ROOT/'components/military-sword-clean-v001.png'
    weapon = Image.open(weapon_path).convert('RGBA')
    actions,markers = [],[]
    for action,folder,request,points,angles,phases in CONFIG:
        base = ROOT/'processed'/folder
        meta = record.read(base/'pipeline-meta.json')
        assert meta['output_origin'] == [256.,472] and not meta['paste_clamped_frames']
        assert not meta['edge_touch_frames'] and not meta['empty_frames']
        assert meta['qc_summary']['profile_body_scale_drift'] <= .08
        frames,markframes,assembled = [],[],[]
        sheet = Image.new('RGBA',(1536,1024),(238,230,214,255))
        time = 0
        durations = [phases[0]/2]*2+[phases[1]/2]*2+[phases[2]/2]*2
        for i,(point,angle,dt) in enumerate(zip(points,angles,durations)):
            path = base/f'attack-{i+1}.png';body = Image.open(path).convert('RGBA');data = audit(path)
            grip_pixel = body.getpixel(point)
            assert grip_pixel[3] == 255 and grip_pixel[0]>150 and grip_pixel[1]>70, (path,point,grip_pixel)
            roi = [point[0]-18,point[1]-18,point[0]+18,point[1]+18]
            patch = Image.new('RGBA',(512,512),(0,0,0,0))
            patch.paste(body.crop(tuple(roi)),(roi[0],roi[1]))
            patch_dir = ROOT/'occlusion-patches'/action;patch_dir.mkdir(parents=True,exist_ok=True)
            patch_path = patch_dir/f'near-grip-{i+1}.png'
            assert not patch_path.exists();patch.save(patch_path)
            record.archive(patch_path,Path('occlusion-patches')/action/patch_path.name,'extracted_existing_pixels_approximate_near_grip_ROI_not_complete_hand_layer')
            row = {'frame_index':i,'frame_path':str(path),'frame_sha256':sha(path),
                   'grip_px':list(point),'grip_rgba':list(grip_pixel),'ground_root_px':[256,472],
                   'weapon_angle_image_clockwise_deg':angle,'weapon_scale':.4,
                   'measurement_status':'manually_selected_inside_visible_closed_grip_runtime_pending',
                   'near_grip_occlusion_roi_px':roi,'near_grip_patch_path':str(patch_path),
                   'near_grip_patch_sha256':sha(patch_path),
                   'patch_semantics':'same_frame_existing_pixels_in_rectangular_ROI_includes_small_wrist_region_not_complete_semantic_hand_layer'}
            data.update(index=i,source_frame_index=i,grip_px=list(point),weapon_angle_image_clockwise_deg=angle,
                        weapon_scale=.4,near_grip_patch_path=str(patch_path),near_grip_patch_sha256=sha(patch_path),
                        phase=['windup','active','recovery'][i//2],time_start_s=round(time,9),time_end_s=round(time+dt,9))
            frames.append(data);markframes.append(row);time += dt
            # Composite existing finished layers with one explicit clockwise transform.
            a=math.radians(angle);c=math.cos(a)/.4;s=math.sin(a)/.4;x,y=point
            layer=weapon.transform((512,512),Image.Transform.AFFINE,
                (c,s,99-c*x-s*y,-s,c,256+s*x-c*y),Image.Resampling.BICUBIC)
            result=body.copy();result.alpha_composite(layer);result.alpha_composite(patch)
            preview=Image.new('RGBA',(512,512),(238,230,214,255));preview.alpha_composite(result)
            assembled.append(preview.convert('RGB'));sheet.alpha_composite(result,((i%3)*512,(i//3)*512))
        review_dir=ROOT/'reviews';review_dir.mkdir(exist_ok=True)
        sheet_path=review_dir/f'{action}-assembly-import-v001.png';assert not sheet_path.exists();sheet.save(sheet_path)
        gif_path=review_dir/f'{action}-phase-timing-preview-v001.gif';assert not gif_path.exists()
        assembled[0].save(gif_path,save_all=True,append_images=assembled[1:],duration=[round(t*1000) for t in durations],loop=0)
        for p in [sheet_path,gif_path]:record.archive(p,Path('reviews')/p.name,'finished_sprite_assembly_review_not_runtime_evidence')
        actions.append({'actor':'hero','action':action,'armor_variant':'baseline_composite',
            'status':'candidate_visual_and_pixel_qc_pass_pending_runtime', 'source_request_number':request,
            'frame_count':6,'frames':frames,'phase_mapping':{'windup':[0,1],'active':[2,3],'recovery':[4,5]},
            'phase_duration_s':dict(zip(['windup','active','recovery'],phases)),
            'total_duration_s':round(sum(phases),9),'processor_qc':meta['qc_summary'],
            'source_to_output_scale':list({f['source_to_output_scale'] for f in meta['frames']}),
            'bbox_fit_applied':False,'preview_sheet':str(sheet_path),'preview_gif':str(gif_path)})
        markers.append({'actor':'hero','action':action,'frames':markframes})
    markers_path=ROOT/'assembly-markers-import-v001.json'
    record.write(markers_path,{'schema':'manual-sword-assembly-markers-v1','frozen':True,
       'runtime_verified':False,'angle_convention':'image_xy_y_down_positive_clockwise',
       'mirror_policy':'one_runtime_mirror_after_assembly_no_preflipped_source','weapon_grip_px':[99,256],
       'weapon_tip_px':[482,256],'weapon_scale':.4,'actions':markers,
       'limitations':['clothing_baked_in_composite_body','near_grip_patch_is_ROI_pixel_replay_not_full_near_far_semantic_layer']})
    subset={'schema':'first-unit-import-subset-v1','version':1,'frozen':True,
       'status':'sword_correction_candidate_not_runtime_accepted','generation_calls_used_at_freeze':ledger['requested_count'],
       'host_fee_usd':None,'external_api_calls':0,'actual_unique_animation_png_count':18,
       'auxiliary_near_grip_patch_png_count':18,'logical_state_mapping_count':3,'actions':actions,
       'components':[{'file':str(weapon_path),'sha256':sha(weapon_path),'grip_px':[99,256],'tip_px':[482,256],
                      'reused_from_frozen_v001':True,'new_generation_calls':0}],
       'assembly_markers_path':str(markers_path),'assembly_markers_sha256':sha(markers_path),
       'mirror_policy':'one_runtime_mirror_after_assembly_no_preflipped_source','runtime_verified':False,
       'formal_content_atlas_validation_passed':False,
       'limitations':['body_with_clothing_composite_not_separate_armor_layer','full_body_near_far_layer_contract_unfulfilled',
                      'no_new_idle_walk_or_armor_atlases_in_this_frozen_subset','weapon_angles_and_patch_occlusion_pending_engine_review']}
    record.write(destination,subset)
    for p in [destination,markers_path]:record.archive(p,p.name,'frozen_sword_candidate_import_contract')
    print(json.dumps({'import':str(destination),'sha256':sha(destination),'unique_body_frames':18,
                      'auxiliary_patches':18,'calls_used':ledger['requested_count']},ensure_ascii=False))


if __name__=='__main__':
    main()
