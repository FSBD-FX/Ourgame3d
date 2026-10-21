"""New-version near-contact inputs; draw original technical guide, never edit art."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CANONICAL = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
CANONICAL_SHA = 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
FAR137 = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/walk-opposite-anchor-v001/raw/far-contact-anchor.png')
FAR137_SHA = '85d48ab699751302364ece823f3a56b57ab863009ab815a5d147609c9baeb88b'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CANONICAL) == CANONICAL_SHA and sha(FAR137) == FAR137_SHA
TARGETS = ['README.md','anchor-request.json','pose-contract.json','prompts/near-contact-anchor.txt',
           'references/identity/canonical-idle-frame-0.png',
           'references/technical/near-contact-role-guide-v001.svg',
           'references/technical/near-contact-role-guide-v001.png','prep-receipt-v001.json']
assert not any((HERE/p).exists() for p in TARGETS), 'New version only; do not overwrite.'

def write(rel, content):
    p=HERE/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:f.write(content)
    return p
def write_json(rel, content):return write(rel,json.dumps(content,ensure_ascii=False,indent=2)+'\n')

identity=HERE/'references/identity/canonical-idle-frame-0.png'
identity.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(CANONICAL,identity)
assert sha(identity)==CANONICAL_SHA

# Coordinates are design schematics, not measurements of131,137 or old walks.
near_arm=[(233,255),(205,284),(168,312)]
far_arm=[(267,255),(302,283),(347,302)]
near_leg=[(245,328),(293,387),(329,443)]
far_leg=[(266,328),(227,384),(195,434)]
near_boot=[(329,443),(314,464),(365,455)]
far_boot=[(195,434),(172,438),(187,452),(225,464)]
near_contact,far_contact=[314,464],[225,464]
red,blue,gray='#cf3f41','#356ec5','#626a74'

def poly(points,color,width=9):
    pts=' '.join(f'{x},{y}'for x,y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">',
     '<rect width="512" height="512" fill="#ffffff"/>',
     '<g font-family="Arial,sans-serif" font-size="13" fill="#202020">',
     '<text x="12" y="20">TECHNICAL NEAR-CONTACT GUIDE / NOT CHARACTER ART</text>',
     '<text x="12" y="41" fill="#cf3f41">RED = camera-NEAR</text>',
     '<text x="278" y="41" fill="#356ec5">BLUE = camera-FAR</text></g>',
     '<rect x="48" y="48" width="416" height="416" fill="none" stroke="#dddddd" stroke-dasharray="5 5"/>',
     '<line x1="74" y1="464" x2="440" y2="464" stroke="#888888" stroke-width="2"/>',
     poly(far_arm,blue),poly(far_leg,blue),poly(far_boot,blue),
     '<ellipse cx="256" cy="151" rx="67" ry="72" fill="none" stroke="#626a74" stroke-width="5"/>',
     '<path d="M329,151 L362,151 M350,141 L362,151 L350,161" fill="none" stroke="#626a74" stroke-width="4"/>',
     '<path d="M256,223 L256,252 L256,328 M233,255 L267,255 M245,328 L266,328" fill="none" stroke="#626a74" stroke-width="7" stroke-linecap="round"/>',
     poly(near_leg,red),poly(near_boot,red),poly(near_arm,red)]
for points,color in [(far_arm,blue),(far_leg,blue),(near_leg,red),(near_arm,red)]:
    for x,y in points:svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#ffffff" stroke="{color}" stroke-width="3"/>')
for (x,y),color in [(near_contact,red),(far_contact,blue)]:svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/>')
svg+=['<g font-family="Arial,sans-serif" font-size="12" fill="#202020">',
      '<text x="88" y="486">far REAR TOE</text>',
      '<text x="282" y="486">near FRONT HEEL</text>',
      '<text x="14" y="504">One pose only. Facing RIGHT. No motion or foot-root acceptance.</text>',
      '</g></svg>']
svg_path=write('references/technical/near-contact-role-guide-v001.svg','\n'.join(svg)+'\n')

# Only blank-canvas technical rendering; no character art is opened or edited.
img=Image.new('RGB',(512,512),'#ffffff');d=ImageDraw.Draw(img)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
d.text((12,6),'TECHNICAL NEAR-CONTACT GUIDE / NOT CHARACTER ART',fill='#202020',font=font)
d.text((12,27),'RED = camera-NEAR',fill=red,font=font)
d.text((278,27),'BLUE = camera-FAR',fill=blue,font=font)
for x in range(48,465,10):
    d.line([(x,48),(min(x+5,464),48)],fill='#dddddd')
    d.line([(x,464),(min(x+5,464),464)],fill='#dddddd')
for y in range(48,465,10):
    d.line([(48,y),(48,min(y+5,464))],fill='#dddddd')
    d.line([(464,y),(464,min(y+5,464))],fill='#dddddd')
d.line([(74,464),(440,464)],fill='#888888',width=2)
for points in (far_arm,far_leg,far_boot):d.line(points,fill=blue,width=9,joint='curve')
d.ellipse([189,79,323,223],outline=gray,width=5)
d.line([(329,151),(362,151)],fill=gray,width=4)
d.line([(350,141),(362,151),(350,161)],fill=gray,width=4)
for points in [[(256,223),(256,252),(256,328)],[(233,255),(267,255)],[(245,328),(266,328)]]:d.line(points,fill=gray,width=7,joint='curve')
for points in (near_leg,near_boot,near_arm):d.line(points,fill=red,width=9,joint='curve')
for points,color in [(far_arm,blue),(far_leg,blue),(near_leg,red),(near_arm,red)]:
    for x,y in points:d.ellipse([x-6,y-6,x+6,y+6],fill='white',outline=color,width=3)
for (x,y),color in [(near_contact,red),(far_contact,blue)]:d.ellipse([x-6,y-6,x+6,y+6],fill=color)
d.text((88,474),'far REAR TOE',fill='#202020',font=small)
d.text((282,474),'near FRONT HEEL',fill='#202020',font=small)
d.text((14,492),'One pose only. Facing RIGHT. No motion or foot-root acceptance.',fill='#202020',font=small)
png_path=HERE/'references/technical/near-contact-role-guide-v001.png';img.save(png_path,format='PNG')

future_rule='After independent static acceptance, combine BOTH opposite contact poses into a multi-pose motion reference plus complete six-phase guide. Neither single pose is a sole final walk anchor. Canonical131 alone continues to own identity.'
pose={'schema':'fairytale-hero-near-contact-technical-contract-v1','status':'prepared_only_not_generated_not_accepted',
      'native_facing':1,'phase':'near_contact','frame_count':1,'loop':False,
      'target_canvas_px':[512,512],'safe_margin_px':[48,48],
      'identity':{'path':str(CANONICAL),'sha256':CANONICAL_SHA,'source_request':131,'copied_path':str(identity),
                  'single_curated_idle':True,'final_user_art_or_motion_approval':False},
      'limb_roles':{'near_arm':'camera-near larger visible arm swings BACK toward screen-left, hand rear/left',
                    'far_arm':'camera-far arm swings FORWARD toward screen-right, separate hand front/right',
                    'near_leg':'camera-near leg reaches FORWARD to screen-right; front HEEL down, toe slightly raised',
                    'far_leg':'camera-far leg trails BACK to screen-left; rear TOE down, heel raised',
                    'counter_swing':'forward far arm opposes forward near leg; backward near arm opposes backward far leg',
                    'near_far_meaning':'camera depth, never relabel by current screen side'},
      'guide':{'svg':str(svg_path),'png':str(png_path),'png_sha256':sha(png_path),
               'role':'original technical motion-role diagram only, not style or actual root measurement',
               'colors_for_guide_only':{'camera_near':red,'camera_far':blue},
               'schematic_joints_px':{'near_arm':near_arm,'far_arm':far_arm,'near_leg':near_leg,'far_leg':far_leg},
               'sole_contacts_design_px':{'near_front_heel':near_contact,'far_rear_toe':far_contact},
               'ground_baseline_y_design_only':464,'pixels_from_existing_art_used':False},
      '137_comparison_only':{'path':str(FAR137),'sha256':FAR137_SHA,'role':'opposite static pose / proportion comparison only, never identity',
                            'attached_to_primary_generation':False,'static_roles_independently_reviewed':True,'motion_accepted':False},
      'observed_output_measurements':{'alpha_bbox':None,'body_height_px':None,'helmet_bbox':None,'foot_rois':None,'root_px':None,'sha256':None},
      'acceptance_needed':['actual generated full-body view','canonical helmet/identity comparison','continuous near/far shoulder/hip chains',
                           'near-front-heel/far-rear-toe grounding','independent static review'],
      'does_not_establish':['six-phase gait','loop seam','foot sliding','left mirror','runtime','armor or weapon adaptation'],
      'future_complete_row_rule':future_rule,'formal_complete_units':0}
write_json('pose-contract.json',pose)

prompt='''Generate exactly ONE full-body character pose, not an animation strip, not multiple views.

ATTACHMENT AUTHORITY
Image1 is the ONLY character identity/style authority: request131 single curated idle. Preserve its closed tan bell helmet, two amber visor eyes, exact dome/rim/visor/side rivet/top knob, charcoal plain underclothes, belt, brown gloves/boots, compact body thickness and proportions. Keep the same original RIGHT-facing three-quarter camera and rigid helmet volume. Do not squash, shorten, rotate, redesign or change eye count. Empty hands, NO armor, weapon, shield, cape or new costume.
Image2 is an ORIGINAL TECHNICAL LIMB-ROLE GUIDE ONLY. RED marks camera-NEAR limbs; BLUE marks camera-FAR limbs. Use these roles, never the guide's style, colors or gray schematic head. Render the limbs in Image1's charcoal clothing and brown gloves/boots. Near/far mean camera depth, not screen-left/right: keep each limb's identity continuous through shoulder/elbow/wrist and hip/knee/ankle.

EXACT REQUIRED POSE: NEAR-LEG FORWARD CONTACT
Keep the ENTIRE character facing RIGHT. This is the opposite half-stride to a far-leg-forward contact:
- The camera-NEAR larger visible ARM swings BACK toward screen-LEFT. Its brown hand is clearly rear/left. Show a natural elbow and relaxed empty glove, not a weapon grip or punch.
- The camera-FAR ARM swings FORWARD toward screen-RIGHT; its separate brown hand is clearly front/right. Preserve the far shoulder/upper-arm depth behind the torso where occluded, with a natural visible forearm/hand forward. Do not label the near arm as far just because it moves right.
- The camera-NEAR LEG extends FORWARD toward screen-RIGHT from the near hip/knee, visibly in front of the far leg where they cross. Its front boot HEEL touches the ground; its TOE is SLIGHTLY LIFTED.
- The camera-FAR LEG trails BACK toward screen-LEFT from its own far hip/knee behind the near thigh. Its rear boot TOE touches the SAME baseline; its HEEL is RAISED.
The forward hand and forward leg MUST be OPPOSITE sides: FAR arm forward + NEAR leg forward. The backward pair is NEAR arm back + FAR leg back. Do not show near hand and near leg both forward. Do not mirror or turn the whole character, helmet, visor or lighting to obtain this opposite phase.

GROUNDING AND ANATOMY
One walking CONTACT pose: near front HEEL + far rear TOE touch one baseline. Not running, jumping, high-knee marching, fighting guard, or two flat planted soles. Softly bent knees, compact natural stride. Exactly two hands and two complete boots, continuous plausible shoulders/hips/knees/ankles, no fused knees, detached hands, extra fingers or changing limb length. Match Image1's glove/boot volume and head-to-body proportions. Do not invent new accessories.

OUTPUT AND STYLE
Exactly one square image, nominal512x512 canvas, one full head-to-toe figure centered with at least48px safe padding on all sides. SAME hand-drawn dark-fairytale cartoon, bold uneven ink contours and broad painted material blocks from Image1. No realistic texture, PBR, 3D render, new palette or tone redesign. Use a perfectly FLAT PURE GREEN #00FF00 background for deterministic alpha extraction, and no green in the character.
No cast/contact shadow, ground patch, scenery, dust, detached effects, blur, trails, UI, text, numbers, arrows, bones, phase labels, colored limbs, joint dots, floor line, guide borders or checkerboard. Do not paste the technical diagram into the output. Do not output a strip, contact sheet, idle stance or complete-character mirrored image. Output only the single near-contact character image.
'''
write('prompts/near-contact-anchor.txt',prompt)
request={'schema':'fairytale-hero-single-near-contact-input-v1','status':'prepared_only_root_generation_pending',
         'purpose':'single static opposite-contact correction, not complete walk','output_pose_count':1,'phase':'near_contact','native_facing':1,
         'target_canvas_px':[512,512],'safe_margin_px':[48,48],'chroma_key':{'rgb':[0,255,0],'hex':'#00FF00'},
         'prompt_file':str(HERE/'prompts/near-contact-anchor.txt'),
         'attachments_in_order':[{'order':1,'path':str(identity),'sha256':sha(identity),'role':'sole identity: canonical131 single curated idle'},
                                 {'order':2,'path':str(png_path),'sha256':sha(png_path),'role':'original near-contact limb-role guide only'}],
         '137_comparison':pose['137_comparison_only'],
         'excluded_image_references':['129 original base','135 failed whole walk','136 failed whole walk','multi-frame idle strip'],
         'imagegen_parameters_for_root_only':{'referenced_image_paths':[str(identity),str(png_path)],'transparent_background':False,
                                             'num_last_images_to_include':'omit','prompt':'read exact prompt_file'},
         'generation_authority':'root only; preparer must not call generator','generation_completed':False,
         'expected_future_raw_path':str(HERE/'raw/near-contact-anchor.png'),'generated_output_sha256':None,
         'automatic_import_or_extraction':False,'retention_before_view':'root F/E preserve new guide and future output before new image view/presentation',
         'future_complete_row_rule':future_rule}
write_json('anchor-request.json',request)
write('README.md','''# Near-contact 单姿势纠错输入 v001

仅准备输入，无生成/提取/UE/UBT；非完整 sprite-gen run，不改旧图、Source、ledger 或保全索引。新技术guide尚未view，待root F/E保全后实际查看；它是原创骨架，不是最终美术。

事实：已实际查看137 far-contact原件、131 canonical及已保全far-guide。137近侧大手跨胸前摆、近后腿/远前腿角色比136清楚，静姿势可继续；未判运动/脚根/最终批准。详细报告位于docs/production/first-batch-v2/fairytale-hero-far-contact-137-independent-v001.md。

本次相反接触：近手左后、远手右前；近腿右前且前跟接地/脚尖略抬，远腿左后且后趾接地/脚跟抬。前摆手与前腿属对侧，身体及钟盔仍保持原生朝右三分之四视角，不镜像整个人来换相。

唯一身份是131 idle-v002/curated/frame-0.png，字节副本SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。primary只附canonical＋新guide两张。137只作已留档的相反姿势/体积对照，不默认附给生成器，不替代身份；135/136失败行、129 base和整idle行均不附。技术guide由空白画布画出，全部坐标为设计点，不能当作新角色足根或体积实测。没有用PIL修改任何现有角色像素。

root后续读取anchor-request.json与prompts/near-contact-anchor.txt完整提示词，先保全输入/guide并实看，再独占生成一张raw/near-contact-anchor.png；实际输出request/尺寸/SHA生成后再记录，没有预编原件哈希。保全新原稿后，逐链复核近/远肩肘腕与髋膝踝、前跟后趾、刚性头盔与身份、空手公共身体和解剖，再做独立静态判定。不符则另版生成，不画改或重定时。

两张contact也不是完整walk。若新静姿势接受，按sprite-gen locomotion边界把它与137组成包含两个相反contact的多姿势motion参考，并配完整六相guide；canonical131继续独占身份。不得把单contact作为唯一整行peak-pose anchor，也不重复两张充当六帧。后续仍须实际六相逐帧/循环播放、5→0、真实脚根/步幅/镜像与UE小比例检查。完整单元仍0/15。

prep-receipt-v001.json绑定准备文件。build-inputs.py只使用sprite-gen自带Python，从空白创建技术SVG/PNG并严格字节复制canonical；不调用native生成或installed skill，拒绝覆盖本版既有输出。PNG/SVG需要root保全后视觉核对，文件/几何检查不代替看图。
''')

assert near_arm[-1][0]<near_arm[0][0] and far_arm[-1][0]>far_arm[0][0]
assert near_contact[0]>near_leg[0][0] and far_contact[0]<far_leg[0][0]
assert near_contact[1]==far_contact[1]==464
assert len(request['attachments_in_order'])==2 and not pose['137_comparison_only']['attached_to_primary_generation']
assert not (HERE/'raw').exists()
files=[HERE/'build-inputs.py']+[HERE/p for p in TARGETS if p!='prep-receipt-v001.json']
receipt={'schema':'near-contact-input-preparation-receipt-v1','status':'frozen_inputs_only_guide_view_pending_retention',
         'files':[{'relative_path':str(p.relative_to(HERE)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files],
         'checks':{'canonical_exact_copy':True,'two_ordered_primary_attachments':True,'one_pose_only':True,'contralateral_arm_leg_forward':True,
                   'two_design_contacts_same_baseline':True,'137_comparison_not_identity_not_primary_attached':True,
                   'no_failed_walk_reference_attached':True,'no_generated_raw':True,'no_existing_art_edited':True},
         'generation_called':False,'UE_or_UBT_called':False,'technical_guide_original_only':True,
         'new_guide_visual_review_performed':False,'root_retention_pending':True}
write_json('prep-receipt-v001.json',receipt)
print(json.dumps({'prepared_files':len(files)+1,'indexed_inputs':len(files),'input_bytes':sum(p.stat().st_size for p in files),
                  'request_sha256':sha(HERE/'anchor-request.json'),'prompt_sha256':sha(HERE/'prompts/near-contact-anchor.txt'),
                  'guide_png_sha256':sha(png_path),'receipt_sha256':sha(HERE/'prep-receipt-v001.json')},ensure_ascii=False))
