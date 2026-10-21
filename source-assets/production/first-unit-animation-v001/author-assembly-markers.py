"""Manual first-unit socket annotations and debug crops; no generated artwork."""
from pathlib import Path
import json
import hashlib
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SETS = [
    ('idle', 'hero-idle-matte-v002', [(203,373)]*6, [45]*6, 'relaxed_open_hand_not_closed_grasp'),
    ('walk', 'hero-walk-matte-v002', [(166,379),(196,378),(160,380),(270,353),(228,378),(162,378)], [35,40,45,20,40,35], 'partly_curled_or_relaxed_hand'),
    ('primary_1', 'hero-primary-1-body-matte-v002', [(210,300),(156,229),(366,285),(277,287),(215,300),(203,300)], [-45,-135,-20,25,55,-45], 'closed_fist'),
    ('primary_2', 'hero-primary-2-body-matte-v002', [(252,352),(164,348),(306,243),(191,177),(247,271),(250,341)], [45,135,10,-65,-90,-45], 'closed_fist'),
    ('primary_3', 'hero-primary-3-body-matte-v002', [(195,344),(212,148),(297,373),(320,397),(188,339),(200,338)], [-45,-100,-20,50,70,-45], 'closed_fist'),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    actions = []
    debug = Image.new('RGB', (6*192, 5*222), '#252525')
    draw = ImageDraw.Draw(debug)
    for row, (action, folder, points, angles, hand_pose) in enumerate(SETS):
        directory = ROOT/'processed'/folder
        meta = json.loads((directory/'pipeline-meta.json').read_text())
        frames = []
        for index, (label, (x,y), angle) in enumerate(zip(meta['frame_labels'], points, angles)):
            source = directory/(label+'.png')
            image = Image.open(source).convert('RGBA')
            sample = list(image.getpixel((x,y)))
            # A deliberately conservative manual ROI, not an exact hand silhouette.
            box = [x-22,y-22,x+22,y+22]
            polygon = [[box[0],box[1]],[box[2],box[1]],[box[2],box[3]],[box[0],box[3]]]
            frames.append({'index':index,'path':str(source),'sha256':sha(source),
                'ground_root_px':meta['output_origin'],'grip_px':[x,y],
                'grip_measurement_status':'manual_visible_hand_point_candidate',
                'source_pixel_rgba':sample,'hand_pose':hand_pose,
                'weapon_angle_deg_clockwise_screen':angle,
                'angle_status':'authored_candidate_not_measured_blade_pose',
                'near_hand_occlusion':{'status':'manual_roi_only_exact_contour_pending',
                    'polygon_px':polygon,'bbox_px':box,
                    'rule':'Overlay only original body pixels inside a refined hand contour above the independent weapon; rectangular ROI alone may cover unrelated sleeve/body.'}})
            crop=image.crop((x-48,y-48,x+48,y+48)).resize((192,192),Image.Resampling.NEAREST)
            bg=Image.new('RGBA',crop.size,'#252525');bg.alpha_composite(crop)
            debug.paste(bg.convert('RGB'),(index*192,row*222))
            cx,cy=index*192+96,row*222+96
            draw.line((cx-9,cy,cx+9,cy),fill='#00FFFF',width=2)
            draw.line((cx,cy-9,cx,cy+9),fill='#00FFFF',width=2)
            draw.text((index*192+5,row*222+194),f'{action} {index+1} ({x},{y})',fill='white')
        actions.append({'id':action,'body_directory':str(directory),'frames':frames})
    output={'schema':'manual-assembly-markers-v1','status':'manual_measurement_candidates_pending_assembly_review',
        'canvas_px':[512,512],'coordinates':'top_left_origin_x_right_y_down_pixels',
        'canonical_direction':'right','mirror_once_rule':'left grip x=512-right_x; left angle=180-right_angle, wrap to[-180,180]; mirror source texture once only',
        'weapon_component':{'path':str(ROOT/'processed'/'military-sword-component'/'clean.png'),
            'sha256':sha(ROOT/'processed'/'military-sword-component'/'clean.png'),
            'grip_px':[99,256],'tip_px':[482,256],
            'uniform_scale_candidate':0.55,'scale_status':'authored_initial_assembly_scale_not_runtime_verified'},
        'actions':actions,'runtime_verified':False,
        'limitations':['No fabricated near/far body or armor layers.',
            'Idle hand is open; attach plus occlusion may still fail natural grasp review.',
            'Weapon angles are authored assembly choices because body sheets contain no blade.',
            'All occlusion rectangles are conservative location marks, not precise extracted hand layers.']}
    (ROOT/'assembly-markers-v001-draft.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'reviews').mkdir(exist_ok=True)
    debug.save(ROOT/'reviews'/'marker-closeups-v001.png')
    print(ROOT/'assembly-markers-v001-draft.json')

if __name__=='__main__':
    main()
