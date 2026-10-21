"""Author numeric input/NEW vector diagrams only. Never reads art into a canvas."""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run-front-idle-v001'
if (ROOT/'component-contract-v001.json').exists():raise RuntimeError('Preparation is already authored; never rerun over it')
sys.path.insert(0,'C:/Users/22499/.codex/skills/sprite-gen')
from sprite_gen.spec.layout import raw_rel
anchors=[([266,249],[263,303]),([267,245],[264,303]),([265,249],[263,304]),([266,249],[263,303])]
def write(name,value):
    path=ROOT/name
    if path.exists():raise RuntimeError('Never overwrite a prepared artifact: '+str(path))
    path.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

request_path=RUN/'sprite-request.json'
request=json.loads(request_path.read_text(encoding='utf-8'))
request['states']['armor_front_idle']['durations_ms']=[167]*4
request['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

contract={'schema':'fairytale-armor-independent-idle-preparation-v1','status':'prepared_not_generated',
 'scope':'147: four connected isolated front chest components only. Back/near/shoulders/bracers/shins and complete armor remain unproduced.',
 'trial_id':'trial_compact_plate_a','equipment_id':None,'frame_count':4,'durations_ms':[167]*4,'loop':True,
 'canonical_body_run':'F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002',
 'canonical_identity_frame':0,'common_body_pixel_changes_allowed':False,'native_facing':1,
 'body_canvas_px':[512,512],'body_display_canvas':72*512/416,'body_display_pivot_px':[256,464],
 'display_pivot_is_certified_foot_root':False,'component_fit_window_px':[78,60],
 'shared_scale_policy':'min(78/max_raw_component_width,60/max_raw_component_height,1), one scalar for all four after native chroma/components',
 'component_fit_is_full_body_fit':False,'per_frame_scale_allowed':False,'component_translation':'After extraction, author/reviewer measures collar and waist attachment pixels. Integer translation aligns actual waist attachment to its matching body target; collar is an independent residual/reject check. Never auto-warp/rotate/resize each frame.',
 'body_attachment_targets':[{'frame':i,'collar':c,'waist':w,'basis':'Author-selected garment attachment landmarks after actual PNG review and opaque-cloth sampling; design contract, not inferred bone/foot contacts. Root review before native147.','confidence':'medium; ink seam/collar has about2-3px visual ambiguity'} for i,(c,w) in enumerate(anchors)],
 'actual_generated_component_anchors':None,'actual_shared_scale':None,'actual_raw_hash':None,
 'back':{'status':'not_produced','path':None},'near':{'status':'not_produced','path':None},
 'future_stack':['actual_visible_armor_back','common_body_far','armor_front','weapon','common_near_arm','armor_near','common_near_hand'],
 'future_common_partition':'Same canonical131 RGBA pixels assigned once by reviewed binary ownership masks; body_far+near_arm+near_hand must reconstruct original RGBA exactly. No old-style masks and no full-body copy into multiple layers.',
 'native_compose_layers_claimed':False,'runtime_imported':False,'motion_accepted':False,'formal_complete_units':0}
write('component-contract-v001.json',contract)

prompt='''Create ONE horizontal component-row strip containing exactly FOUR independent connected chest-armor pieces, left to right. This is native147, a production-layer candidate for the four existing idle poses. It is NOT four dressed characters and NOT a full-body replacement.

REFERENCE OWNERSHIP: canonical131-idle-0 is the sole hero/style identity. The canonical131 four-pose contact gives the exact pose order0,1,2,3 and collar/waist relationship for each piece; never generate its body pixels. Reference146 is ONLY a material/construction reference for its compact curved breastplate and short connected straps. Ignore its helmet, anatomy, body proportions, pose, raw alpha border and framing. The two technical guides give counts/attachment shape; their blue fill, labels, markers, borders and arrows must not appear in the result.

OUTPUT ONLY THE ARMOR: each of the four items is one small curved front breastplate with two short straps visibly attached to it. Keep every item one connected component. Its upper notch fits beneath the existing dark collar; its short lower edge stops above the existing belt. Right-facing three-quarter view: respect the wider near side at image-left and compressed far side at image-right. Match each corresponding131 torso pose, with only subtle flexible-strap tension change through the four breathing poses; the same metal plate remains rigid and keeps its design/volume. The source idle timing stays4x167ms, but do not draw timing labels. Do not duplicate one image into four slots or introduce a different armor design in a later slot.

DESIGN: preserve146's compact, rounded, slightly crooked handmade breastplate construction; do not turn it into heavy square plate, a door-bar beam or another outfit. Use slightly cooler DESATURATED NEUTRAL GREY metal than146's warm tan helmet, with two or three broad matte painted values, a readable dark ink rim and restrained pale-grey upper highlight. Keep the playful grotesque dark-fairytale drawing of131. Short dark-leather straps may connect to the chest piece; no green/teal materials, tiny engraving, busy rivets or realistic surface noise. The final chest panel will be only about13.5x10.4px on a72px hero, so its broad shape and collar/waist separation must do the work.

NO helmet, eyes, neck, charcoal shirt, sleeves, shoulders/pauldrons, arms, skin, gloves, fingers, belt/buckle, hips, legs, boots, cape, skirt, weapon or shield. No whole hero, mannequin, ghost body or body-colored silhouette. No independent detached straps, floating rivets or extra components. No alternate views, turnarounds, scenery, floor, shadow, glow, white halo, checkerboard, typography or UI. These four components must be genuinely separate armor art, never146's full-body pixels copied into a layer.

BACKGROUND/LAYOUT: perfectly flat solid chroma GREEN #00FF00, fully opaque RGB-style background and opaque armor interiors. Exactly four well-separated objects in one horizontal row, generous green gaps and border on every side; no overlap and no extra items. Keep all four objects at the SAME drawing scale. They may be drawn large enough for clean ink and later deterministically reduced together; the numeric fit window78x60 is a final component limit, not an instruction to fill512px with a chest plate or to draw guide boxes. Extraction will use one shared component scale for the whole row, never per-frame body normalization.

SUCCESS BOUNDARY: produce only the four front chest pieces. Back/near armor, forearms, shins, weapon occlusion, complete four-armors, walk/action frames and runtime acceptance are separate work. Do not add their pixels to make this row look complete.
'''
write('prompts/147-four-idle-front-chest-v001.txt',prompt)

# Original technical diagram, expressed in body source coordinates then shown4x.
# It does not sample, composite, crop, recolor or edit any existing raster art.
points=[(222,250),(235,243),(245,244),(252,250),(269,253),(284,249),(290,245),(299,253),(300,296),(291,302),(240,303),(226,298)]
image=Image.new('RGB',(2048,512),'#f6f7f8');draw=ImageDraw.Draw(image)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512" viewBox="0 0 2048 512"><rect width="2048" height="512" fill="#f6f7f8"/>']
for i,(collar,waist) in enumerate(anchors):
    x=i*512
    def transform(a):return (x+256+(a[0]-263)*4,228+(a[1]-273)*4)
    poly=[transform(a) for a in points]
    draw.rectangle((x+12,12,x+500,500),outline='#718096',width=2)
    draw.polygon(poly,fill='#b6cfe0',outline='#244b66',width=5)
    c=transform(collar);w=transform(waist)
    draw.line((c,w),fill='#b45309',width=3)
    for pos,color in [(c,'#c43232'),(w,'#2455ba')]:
        draw.ellipse((pos[0]-6,pos[1]-6,pos[0]+6,pos[1]+6),fill=color)
    lines=[f'IDLE {i}  / 167ms',f'body collar {collar}',f'body waist  {waist}','4x TECHNICAL SHAPE ONLY','Connected chest + straps only']
    for j,line in enumerate(lines):draw.text((x+28,20+j*23 if j==0 else 375+(j-1)*24),line,fill='#172737',font=font)
    svg.append(f'<g><rect x="{x+12}" y="12" width="488" height="488" fill="none" stroke="#718096"/><polygon points="'+ ' '.join(f'{a},{b}' for a,b in poly)+'" fill="#b6cfe0" stroke="#244b66" stroke-width="5"/>')
    svg.append(f'<line x1="{c[0]}" y1="{c[1]}" x2="{w[0]}" y2="{w[1]}" stroke="#b45309" stroke-width="3"/><circle cx="{c[0]}" cy="{c[1]}" r="6" fill="#c43232"/><circle cx="{w[0]}" cy="{w[1]}" r="6" fill="#2455ba"/>')
    for j,line in enumerate(lines):svg.append(f'<text x="{x+28}" y="{40 if j==0 else 395+(j-1)*24}" font-family="Arial" font-size="18" fill="#172737">{line.replace("&","&amp;")}</text>')
    svg.append('</g>')
svg.append('</svg>')
image.save(ROOT/'guides/four-idle-chest-shape-and-mount-v001.png')
write('guides/four-idle-chest-shape-and-mount-v001.svg','\n'.join(svg)+'\n')

layout=list((RUN/'references/layout-guides').rglob('*.png'))
if len(layout)!=1:raise RuntimeError('Expected exactly one prepared layout guide')
roles=[('references/canonical131-idle-0.png','sole canonical identity/style; no129 or146 body identity'),
 ('references/canonical131-idle-four-pose-contact.png','exact four131 body poses0..3; pose/mount reference only, body pixels forbidden in armor output'),
 ('references/146-material-only.png','breastplate construction/material only; forbid its anatomy/helmet/body/alpha/framing'),
 (str(layout[0].relative_to(ROOT)),'sprite-gen numeric four-slot layout only; never render its labels/boxes'),
 ('guides/four-idle-chest-shape-and-mount-v001.png','original technical connected shape/mount design; blue/markers/text are not material')]
plan={'schema':'native147-four-idle-chest-input-plan-v1','status':'prepared_not_reserved_or_called','planned_native_request':147,
 'prompt':str(ROOT/'prompts/147-four-idle-front-chest-v001.txt'),'reference_images':[{'path':str(ROOT/name),'role':role,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest()} for name,role in roles],
 'transparent_background':False,'background':'#00FF00 flat chroma','external_api_calls_by_this_prep':0,
 'raw_destination_planned':str(RUN/raw_rel(request,'armor_front_idle')),'raw_exists':False,'root_only_native_generation':True,
 'generation_is_authorized_by_root_not_executed_here':True,'armor_component_count_planned':4,'full_armors_completed':0,'formal_complete_units':0}
write('native147-input-plan-v001.json',plan)
print(json.dumps({'references':len(roles),'layout':str(layout[0]),'frames':4,'timing':[167]*4,'generated':False}))
