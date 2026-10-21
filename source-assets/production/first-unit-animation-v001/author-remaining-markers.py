"""Annotate the38 remaining existing hero frames. No generation or art edits."""
from pathlib import Path
import json
import hashlib
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
NEW=[
 ('jump_family','hero-jump-family-processor-review',[(160,320),(151,285),(157,312),(161,314),(155,283),(156,283),(151,290),(194,331)], [30,20,-45,-35,25,35,20,35], 'curled_or_relaxed_hand'),
 ('dodge','hero-dodge',[(209,308),(234,328),(250,351),(241,328),(221,314),(224,315)], [35,25,15,20,25,35], 'closed_near_fist'),
 ('hurt','hero-hurt',[(203,373),(256,313),(252,321),(246,318),(204,351),(203,372)], [35,-25,-35,-15,20,35], 'relaxed_then_closed_then_relaxed'),
 ('death','hero-death',[(235,351),(238,390),(246,440),(278,452),(320,459),(310,461)], [35,20,0,0,0,0], 'relaxed_visible_hand_not_grasp'),
 ('secondary','hero-secondary-body',[(238,291),(153,190),(228,294),(313,373),(240,291),(239,291)], [-45,-135,-20,45,25,-45], 'closed_near_fist'),
 ('air_primary_1','hero-air-primary-1-body-processor-review',[(229,237),(149,152),(376,295),(274,268),(228,235),(225,235)], [-45,-135,-40,25,55,-45], 'closed_near_fist'),
]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    frozen=json.loads((ROOT/'import-subset-v002.json').read_text(encoding='utf-8'))
    frame_info={f['sha256']:f for action in frozen['actions'] for f in action['frames']}
    data=json.loads((ROOT/'assembly-markers-v001.json').read_text(encoding='utf-8'))
    data['schema']='manual-assembly-markers-v2'
    data['version']='v002'
    data['previous_version_path']=str(ROOT/'assembly-markers-v001.json')
    data['previous_version_sha256']=sha(ROOT/'assembly-markers-v001.json')
    data['status']='draft_remaining_hand_crop_review_pending'
    data['original_v001_action_markers_retained']=True
    data['runtime_tuning_reference']={'source':'root message2026-10-15; arithmetic candidate not acceptance',
        'weapon_scale_candidate':.40,'idle_angle_candidate':35,'walk_angle_candidate':30,
        'primary_3_frame3_angle_candidate':25,'primary_3_frame4_angle_candidate':40,
        'source_angles_in_v001_actions_are_not_overwritten':True,'runtime_verified':False}
    debug=Image.new('RGB',(8*192,6*222),'#252525');draw=ImageDraw.Draw(debug)
    for row,(action,folder,points,angles,hand_pose) in enumerate(NEW):
        directory=ROOT/'processed'/folder
        meta=json.loads((directory/'pipeline-meta.json').read_text())
        frames=[]
        for index,(label,(x,y),angle) in enumerate(zip(meta['frame_labels'],points,angles)):
            path=directory/(label+'.png');im=Image.open(path).convert('RGBA');hash_=sha(path);record=frame_info[hash_]
            sample=list(im.getpixel((x,y)))
            assert sample[3]>=128, (action,index,x,y,sample)
            polygon=[[x-21,y-12],[x-9,y-23],[x+10,y-22],[x+22,y-9],[x+23,y+8],[x+9,y+23],[x-10,y+22],[x-22,y+8]]
            frames.append({'index':index,'source_frame_index':index,'path':str(path),'sha256':hash_,
                'ground_root_px':record['root_px'],'grip_px':[x,y],
                'grip_measurement_status':'manual_visible_hand_point_candidate_pending_crop_review',
                'source_pixel_rgba':sample,'marker_alpha_verified':True,'hand_pose':hand_pose,
                'weapon_angle_deg_clockwise_screen':angle,'angle_status':'authored_candidate_not_measured_blade_pose',
                'near_hand_occlusion':{'status':'manual_approximate_hand_roi_runtime_refinement_pending',
                    'polygon_px':polygon,'bbox_px':[x-23,y-23,x+24,y+24],
                    'rule':'Reuse original source pixels only; refine contour before claiming genuine near-hand layer.'}})
            crop=im.crop((x-48,y-48,x+48,y+48)).resize((192,192),Image.Resampling.NEAREST)
            bg=Image.new('RGBA',crop.size,'#252525');bg.alpha_composite(crop);debug.paste(bg.convert('RGB'),(index*192,row*222))
            cx,cy=index*192+96,row*222+96
            draw.line((cx-9,cy,cx+9,cy),fill='#00FFFF',width=2);draw.line((cx,cy-9,cx,cy+9),fill='#00FFFF',width=2)
            draw.text((index*192+5,row*222+195),f'{action}{index+1} ({x},{y})',fill='white')
        if action=='jump_family':
            for name,indices in [('jump',[0,1,2,3]),('fall',[4,5]),('land',[6,7])]:
                data['actions'].append({'id':name,'body_directory':str(directory),'source_family':'jump_family',
                    'source_frame_indices':indices,'frames':[frames[i] for i in indices]})
        else:
            data['actions'].append({'id':action,'body_directory':str(directory),'frames':frames})
    data['actual_unique_hero_frame_markers']=68
    data['logical_hero_actions']=13
    data['limitations'].extend(['Death hand remains visible but relaxed, proposed horizontal sword-rest pose is not a verified gameplay drop.',
        'Air roots are the separate manual proxy metadata in import-v002, no second actorZ or sprite parabola.'])
    (ROOT/'assembly-markers-v002-draft.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    debug.save(ROOT/'reviews'/'remaining-marker-closeups-v002.png')
    print('recorded38new/68total hero frame markers, no alpha-empty centres')

if __name__=='__main__':main()
