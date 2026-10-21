"""Preview actual selected layers and existing separate sword; no new art."""
from pathlib import Path
import importlib.util,json,math
from PIL import Image
P=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('record',P/'production-record.py')
r=importlib.util.module_from_spec(S);S.loader.exec_module(r)
O=P.parent/'first-unit-animation-v003'
D=P/'components/idle-selection-v001'
markers=json.loads((O/'assembly-markers-import-v005.json').read_text('utf-8-sig'))
frames=next(x for x in markers['actions'] if x['action']=='idle')['frames']
sword=Image.open(O.parent/'first-unit-animation-v002/components/military-sword-clean-v001.png').convert('RGBA')
def weapon(marker):
    scale=marker['weapon_scale'];a=math.radians(marker['weapon_angle_image_clockwise_deg'])
    c=math.cos(a);s=math.sin(a);gx,gy=marker['grip_px'];sx,sy=markers['weapon_grip_px']
    # Pillow affine is inverse destination->source; only independent prop transforms.
    coeff=(c/scale,s/scale,sx-(c*gx+s*gy)/scale,-s/scale,c/scale,sy-(-s*gx+c*gy)/scale)
    return sword.transform((512,512),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC)
sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['base-no-armor','LGT-on','LGT-on-sword']}
rows=[]
for i,m in enumerate(frames):
    parts={name:Image.open(D/f'{name}-{i}.png').convert('RGBA') for name in ['body_far','body_near','armor_back','armor_far_shoulder','armor_torso','armor_front']}
    base=parts['body_far'].copy();base.alpha_composite(parts['body_near'])
    worn=Image.new('RGBA',(512,512),(0,0,0,0))
    for name in ['armor_back','body_far','armor_far_shoulder','armor_torso','armor_front']:worn.alpha_composite(parts[name])
    armed=worn.copy();armed.alpha_composite(weapon(m));armed.alpha_composite(parts['body_near'])
    worn.alpha_composite(parts['body_near'])
    for name,im in [('base-no-armor',base),('LGT-on',worn),('LGT-on-sword',armed)]:
        sheets[name].alpha_composite(im,((i%3)*512,(i//3)*512))
    rows.append({'frame':i,'root_px':m['ground_root_px'],'grip_px':m['grip_px'],'weapon_angle':m['weapon_angle_image_clockwise_deg'],'base_to_LGT_changed_pixels':sum(a!=b for a,b in zip(base.getdata(),worn.getdata()))})
for name,im in sheets.items():
    f=P/f'reviews/idle-{name}-composite-v001.png'
    if f.exists():raise ValueError('Never overwrite preview')
    im.save(f);r.archive(f,Path('reviews')/f.name,'actual_component_toggle_preview_pending_visual_review_not_runtime')
f=P/'reviews/idle-component-composite-evidence-v001.json'
r.write(f,{'frames':rows,'stack':['armor_back','body_far','armor_far_shoulder','armor_torso','armor_front','separate_sword','body_near'],'base_geometry_transforms':'none','weapon_transform':'existing scale .4 angle35 grip99,256','runtime_verified':False})
r.archive(f,Path('reviews')/f.name,'component_toggle_measurements')
print({'frames':len(rows),'previews':len(sheets)})
