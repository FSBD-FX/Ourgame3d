"""Prepare one original technical pose guide; never generate or edit character art."""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CANONICAL = Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
CANONICAL_SHA = 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CANONICAL) == CANONICAL_SHA
TARGETS = [
    'README.md', 'anchor-request.json', 'pose-contract.json',
    'prompts/far-contact-anchor.txt',
    'references/identity/canonical-idle-frame-0.png',
    'references/technical/far-contact-role-guide-v001.svg',
    'references/technical/far-contact-role-guide-v001.png',
    'prep-receipt-v001.json',
]
assert not any((HERE / p).exists() for p in TARGETS), 'Fresh version only; never overwrite prepared inputs.'

def write(rel, content):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(content)
    return p

def write_json(rel, content):
    return write(rel, json.dumps(content, ensure_ascii=False, indent=2) + '\n')

identity = HERE / 'references/identity/canonical-idle-frame-0.png'
identity.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(CANONICAL, identity)
assert sha(identity) == CANONICAL_SHA

# All coordinates are an ORIGINAL technical diagram, not a measurement or
# repaint of the canonical sprite. Gray body/head is schematic, not style.
near_arm = [(233, 255), (285, 283), (346, 302)]
far_arm = [(267, 255), (218, 284), (169, 312)]
near_leg = [(245, 328), (211, 384), (180, 434)]
far_leg = [(266, 328), (301, 387), (338, 443)]
near_boot = [(180, 434), (157, 438), (172, 452), (210, 464)]
far_boot = [(338, 443), (323, 464), (374, 455)]
near_contact, far_contact = [210, 464], [323, 464]
red, blue, gray = '#cf3f41', '#356ec5', '#626a74'

def poly(points, color, width=9):
    pts = ' '.join(f'{x},{y}' for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'

svg = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">',
    '<rect width="512" height="512" fill="#ffffff"/>',
    '<g font-family="Arial, sans-serif" font-size="13" fill="#202020">',
    '<text x="12" y="20">TECHNICAL FAR-CONTACT GUIDE / NOT CHARACTER ART</text>',
    '<text x="12" y="41" fill="#cf3f41">RED = camera-NEAR</text>',
    '<text x="278" y="41" fill="#356ec5">BLUE = camera-FAR</text></g>',
    '<rect x="48" y="48" width="416" height="416" fill="none" stroke="#dddddd" stroke-dasharray="5 5"/>',
    '<line x1="74" y1="464" x2="440" y2="464" stroke="#888888" stroke-width="2"/>',
    poly(far_arm, blue), poly(far_leg, blue), poly(far_boot, blue),
    '<ellipse cx="256" cy="151" rx="67" ry="72" fill="none" stroke="#626a74" stroke-width="5"/>',
    '<path d="M 329,151 L 362,151 M 350,141 L 362,151 L 350,161" fill="none" stroke="#626a74" stroke-width="4"/>',
    '<path d="M 256,223 L 256,252 L 256,328 M 233,255 L 267,255 M 245,328 L 266,328" fill="none" stroke="#626a74" stroke-width="7" stroke-linecap="round"/>',
    poly(near_leg, red), poly(near_boot, red), poly(near_arm, red),
]
for points, color in [(far_arm, blue), (far_leg, blue), (near_leg, red), (near_arm, red)]:
    for x, y in points:
        svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#ffffff" stroke="{color}" stroke-width="3"/>')
for point, color in [(near_contact, red), (far_contact, blue)]:
    x, y = point
    svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/>')
svg += [
    '<g font-family="Arial, sans-serif" font-size="12" fill="#202020">',
    '<text x="82" y="486">near REAR TOE</text>',
    '<text x="285" y="486">far FRONT HEEL</text>',
    '<text x="14" y="504">One pose only. Facing RIGHT. No motion or foot-root acceptance.</text>',
    '</g></svg>',
]
svg_path = write('references/technical/far-contact-role-guide-v001.svg', '\n'.join(svg) + '\n')

# Render the same ORIGINAL geometry to a new RGB PNG. No existing art is
# loaded, cropped, traced, recolored, composited or otherwise edited here.
img = Image.new('RGB', (512, 512), '#ffffff')
d = ImageDraw.Draw(img)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
d.text((12, 6), 'TECHNICAL FAR-CONTACT GUIDE / NOT CHARACTER ART', fill='#202020', font=font)
d.text((12, 27), 'RED = camera-NEAR', fill=red, font=font)
d.text((278, 27), 'BLUE = camera-FAR', fill=blue, font=font)
for x in range(48, 465, 10):
    d.line([(x, 48), (min(x + 5, 464), 48)], fill='#dddddd')
    d.line([(x, 464), (min(x + 5, 464), 464)], fill='#dddddd')
for y in range(48, 465, 10):
    d.line([(48, y), (48, min(y + 5, 464))], fill='#dddddd')
    d.line([(464, y), (464, min(y + 5, 464))], fill='#dddddd')
d.line([(74, 464), (440, 464)], fill='#888888', width=2)
for points in (far_arm, far_leg, far_boot):
    d.line(points, fill=blue, width=9, joint='curve')
d.ellipse([189, 79, 323, 223], outline=gray, width=5)
d.line([(329, 151), (362, 151)], fill=gray, width=4)
d.line([(350, 141), (362, 151), (350, 161)], fill=gray, width=4)
for points in [[(256, 223), (256, 252), (256, 328)], [(233, 255), (267, 255)], [(245, 328), (266, 328)]]:
    d.line(points, fill=gray, width=7, joint='curve')
for points in (near_leg, near_boot, near_arm):
    d.line(points, fill=red, width=9, joint='curve')
for points, color in [(far_arm, blue), (far_leg, blue), (near_leg, red), (near_arm, red)]:
    for x, y in points:
        d.ellipse([x-6, y-6, x+6, y+6], fill='white', outline=color, width=3)
for (x,y), color in [(near_contact, red), (far_contact, blue)]:
    d.ellipse([x-6,y-6,x+6,y+6], fill=color)
d.text((82, 474), 'near REAR TOE', fill='#202020', font=small)
d.text((285, 474), 'far FRONT HEEL', fill='#202020', font=small)
d.text((14, 492), 'One pose only. Facing RIGHT. No motion or foot-root acceptance.', fill='#202020', font=small)
png_path = HERE / 'references/technical/far-contact-role-guide-v001.png'
img.save(png_path, format='PNG')

pose = {
    'schema': 'fairytale-hero-opposite-contact-technical-contract-v1',
    'status': 'prepared_only_not_generated_not_accepted',
    'purpose': 'Isolate one far-contact role correction before attempting another complete walk row.',
    'native_facing': 1,
    'phase': 'far_contact',
    'frame_count': 1,
    'loop': False,
    'target_canvas_px': [512, 512],
    'safe_margin_px': [48, 48],
    'identity': {'path': str(CANONICAL), 'sha256': CANONICAL_SHA, 'source_request': 131,
                 'copied_path': str(identity), 'is_single_curated_idle': True,
                 'final_user_art_or_motion_approval': False},
    'limb_roles': {
        'near_arm': 'camera-near visible larger arm swings FORWARD to screen-right, crossing in front of torso',
        'far_arm': 'camera-far arm swings BACK to screen-left behind torso, hand still separately visible',
        'near_leg': 'camera-near leg trails BACK toward screen-left; rear TOE contacts baseline, heel lifted',
        'far_leg': 'camera-far leg extends FORWARD toward screen-right; front HEEL contacts baseline, toe slightly lifted',
        'counter_swing': 'forward near arm opposes forward far leg; backward far arm opposes backward near leg',
        'near_far_meaning': 'camera depth, never relabel by current screen-left/right position',
    },
    'guide': {'svg': str(svg_path), 'png': str(png_path), 'png_sha256': sha(png_path),
              'role': 'original technical limb-role illustration only, not style or body-root measurement',
              'colors_for_guide_only': {'camera_near': red, 'camera_far': blue},
              'schematic_joints_px': {'near_arm': near_arm, 'far_arm': far_arm,
                                      'near_leg': near_leg, 'far_leg': far_leg},
              'schematic_sole_contacts_px': {'near_rear_toe': near_contact, 'far_front_heel': far_contact},
              'ground_baseline_y_design_only': 464,
              'pixels_from_existing_art_used': False},
    'observed_output_measurements': {'alpha_bbox': None, 'body_height_px': None,
                                     'helmet_bbox': None, 'feet_rois': None, 'root_px': None,
                                     'source_sha256': None},
    'acceptance_needed': ['actual generated full-body view', 'canonical identity/rigid helmet comparison',
                          'track both arm chains and both leg chains with camera-near/far roles',
                          'front heel and rear toe contact inspection', 'independent static review'],
    'does_not_establish': ['six-frame gait', 'loop seam', 'foot sliding', 'left mirror', 'runtime integration',
                           'armor adaptation', 'weapon sockets', 'complete content unit'],
    'future_complete_row_rule': 'An accepted single far-contact trial may join a MULTI-POSE reference containing BOTH opposite contacts and six-phase motion guidance. It must not become the sole peak-pose walk anchor or replace canonical idle identity.',
    'formal_complete_units': 0,
}
write_json('pose-contract.json', pose)

prompt = '''Generate exactly ONE full-body character pose, not an animation strip, not multiple views.

ATTACHMENT AUTHORITY
Image 1 is the ONLY character identity and style authority: the single curated frame from request131 idle-v002. Keep its original right-facing three-quarter camera, closed tan bell helmet, two amber eyes inside the black visor, exact helmet dome/rim/visor/side rivet/top knob, charcoal plain underclothes, belt, brown gloves and boots. Retain the same compact proportions, material blocks, outline weight and helmet volume. Do not redesign, squash, shorten or rotate the helmet; do not change the eye count. The character is EMPTY-HANDED, with no armor, weapon, shield, cape or new costume.

Image 2 is an ORIGINAL TECHNICAL LIMB-ROLE GUIDE ONLY. It is not character art or a style reference. RED identifies the camera-NEAR arm and leg. BLUE identifies the camera-FAR arm and leg. Translate those limb roles into the original charcoal clothes and brown gloves/boots; do not draw red/blue limbs or technical marks. The gray schematic head is not a replacement helmet shape. Near/far mean depth relative to the camera, never current screen-left/right. Keep those identities through the shoulders, elbows, hips, knees and feet.

SINGLE REQUIRED POSE: FAR-LEG FORWARD CONTACT
The whole character continues to face RIGHT. Create the OPPOSITE contact of a near-leg-forward walk:
- The camera-NEAR, larger visible ARM swings FORWARD toward screen-RIGHT. Its upper arm and forearm come across IN FRONT of the torso. Its brown hand is clearly at the front/right, not hanging behind at lower-left. Show a natural bent elbow and a relaxed empty glove; it is a walking swing, not a punch or fighting guard.
- The camera-FAR ARM swings BACK toward screen-LEFT, behind the torso. Keep its separate brown hand visible at rear/left. Do not leave the large near hand behind and merely swap labels.
- The camera-NEAR LEG trails BACK toward screen-LEFT. Connect it visibly to the near hip and knee. Its rear boot TOE touches the ground, with its HEEL RAISED.
- The camera-FAR LEG extends FORWARD toward screen-RIGHT. Connect it through the far hip/knee, preserving depth and consistent occlusion. Its front boot HEEL touches the same ground baseline, with its TOE SLIGHTLY LIFTED.
The forward hand and forward leg MUST belong to OPPOSITE sides: near arm forward + far leg forward. The backward pair is far arm back + near leg back. Do not show the near hand and near leg both forward. Do not mirror the complete character, the head, the visor or the lighting to achieve the opposite contact.

GROUNDING AND ANATOMY
This is one walking contact pose, not running, jumping, high-knee marching, a wide combat stance or two planted flat soles. Both shoes have a real contact: FAR front HEEL and NEAR rear TOE on one baseline. Knees remain softly bent; stance is compact and natural. Draw exactly two arms, two hands, two legs and two complete boots. Preserve limb lengths, glove/boot volume, body thickness and the same rigid helmet scale from Image1. Make the two arms and two leg chains readable; maintain plausible hip and shoulder connections, no detached hands, fused knees, extra fingers or broken ankles.

OUTPUT AND STYLE
One square image with one complete head-to-toe figure, centered, nominal 512x512 canvas, at least 48px safe padding on every side. Use the SAME hand-drawn dark-fairytale cartoon identity from Image1, broad painted color blocks and bold uneven ink contours; no realistic texture, PBR, 3D, new palette or new tone. Use a perfectly FLAT pure GREEN #00FF00 background for later deterministic alpha extraction. Do not use green in the character.
No cast/contact shadow, ground patch, scenery, detached FX, dust, blur, trails, UI, words, numbers, phase labels, arrows, stick lines, skeleton colors, joints, floor line, guide borders or checkerboard. Do not paste the technical diagram into the output. Do not output a contact sheet or copy the idle stance. Output only the single far-contact character image.
'''
write('prompts/far-contact-anchor.txt', prompt)

request = {
    'schema': 'fairytale-hero-single-opposite-contact-input-v1',
    'status': 'prepared_only_root_generation_pending',
    'purpose': 'static correction trial; not a complete sprite-gen animation run',
    'output_pose_count': 1, 'phase': 'far_contact', 'native_facing': 1,
    'target_canvas_px': [512, 512], 'safe_margin_px': [48, 48],
    'chroma_key': {'rgb': [0,255,0], 'hex': '#00FF00'},
    'prompt_file': str(HERE / 'prompts/far-contact-anchor.txt'),
    'attachments_in_order': [
        {'order':1, 'path':str(identity), 'sha256':sha(identity), 'role':'sole character identity; request131 single curated idle'},
        {'order':2, 'path':str(png_path), 'sha256':sha(png_path), 'role':'original technical near/far limb roles only'},
    ],
    'excluded_image_references': ['request129 original base', 'request135 failed walk', 'request136 failed walk', 'multi-frame idle strip'],
    'imagegen_parameters_for_root_only': {'referenced_image_paths':[str(identity),str(png_path)], 'transparent_background':False,
                                         'num_last_images_to_include':'omit', 'prompt':'read exact prompt_file'},
    'generation_authority':'root only; this preparer made no provider call',
    'generation_completed':False,
    'expected_future_raw_path':str(HERE / 'raw/far-contact-anchor.png'),
    'generated_output_sha256':None,
    'automatic_import_or_extraction':False,
    'retention_before_view':'root must preserve newly prepared guide and future generation in F/E before presenting/reviewing those new images',
    'future_row_reference_policy':pose['future_complete_row_rule'],
}
write_json('anchor-request.json', request)

readme = '''# Opposite-contact 单姿势纠错输入 v001

状态：仅输入准备。没有调用图像生成器、提取器、UE/UBT，没有生成任何最终角色像素或动作帧；不是完整 sprite-gen run。此目录不覆盖旧版 walk、原稿、Source、ledger 或保全索引。

## 事实、推理与边界

唯一身份输入是 request131 的 idle-v002/curated/frame-0.png，字节副本位于 references/identity；SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。该 512² RGBA 图已实际查看：完整钟盔、双琥珀眼、灰黑内衣、棕手套和靴、空手、原生朝右三分之四视角。既有技术 idle 身份不等于最终用户美术或动作验收。135/136 仅留在旧审阅报告，未附为新生成输入；129 早期 base 和整张 idle strip 也不附。

root 要求的 near 手前 / far 腿前是对侧摆臂，自洽；near 腿后 / far 手后是另一对。将“两只鞋接地”明确为远前脚跟与近后脚趾接触同一线，避免误生两只平底全掌贴地的战斗站姿。新技术 guide 的红=近侧、蓝=远侧，不把画面左右当肢体身份；颜色只用于讲解，不是最终角色配色。

guide 是从空白画布绘制的原创技术骨架，SVG 与 PNG 均随本版保留。build-inputs.py 没有读取或改画角色像素，仅字节复制身份图；所有骨架点都是设计说明，不能作为新角色实际足根、盔甲包围盒、动作长度或 runtime 物理测量。新 guide 尚待 root F/E 保全和实际视觉审核；本准备者没有展示或宣称看过新 guide。未来生成原件也必须先保全再看。

## root 后续输入

使用 anchor-request.json 的两附件顺序与 prompts/far-contact-anchor.txt 完整提示词：1=唯一身份，2=仅肢体角色 guide；生成 exactly one far-contact full-body pose。费用/生成由 root 处理，本准备者没有调用供应商。新原件须独立落 raw/far-contact-anchor.png、记录实际 request/尺寸/SHA、F/E 保全后审图；不预先编造原件、足根或 alpha 报告。

静帧审核顺序：先身份和刚性钟盔；再逐条连接肩→肘→近前手/远后手、髋→膝→近后腿/远前腿；再确认前跟/后趾接地、没有多手多腿/断腕/融膝；最后检查小尺度可辨性。若不符，保留失败版本并另版再生成，不能本地修画角色或改时长掩盖错误。

## 不把单图当完整 walk

sprite-gen/docs/directional-anchor-workflow.md 的 State anchor gate 明确禁止把单个 peak pose 作为最终 cyclic locomotion row 的唯一状态锚点。本图只隔离 far_contact 的纠错题；若随后静帧接受，它可加入同时包含两种相反 contact 的多姿势 motion reference，并配六相骨架。canonical idle 始终拥有身份；不得把此一姿势重复成六帧，也不能直接把它当后半循环已经完成。

完整六相仍须连贯支持/摆腿/推蹬、真实播放 5→0、落足/步幅量测、左右镜像与实际 UE 小尺度检查。本次没有新增 armor、weapon sockets 或 gameplay，formal complete units 仍 0/15。

## 文件与复现

anchor-request.json 是本次输入入口；pose-contract.json 区分技术设计值与尚未知的生成实测值。prep-receipt-v001.json 绑定所有准备输入 SHA。原始 guide 几何与渲染均在 build-inputs.py；只允许在新的空版本目录复现，脚本拒绝覆盖本版已存在的准备输出。运行所用 Python 为 sprite-gen 自带 .venv/Scripts/python.exe；未修改 installed skill。
'''
write('README.md', readme)

assert near_arm[-1][0] > near_arm[0][0] and far_arm[-1][0] < far_arm[0][0]
assert near_contact[0] < near_leg[0][0] and far_contact[0] > far_leg[0][0]
assert near_contact[1] == far_contact[1] == 464
assert len(request['attachments_in_order']) == 2 and request['output_pose_count'] == 1
assert not (HERE / 'raw/far-contact-anchor.png').exists()
files = [HERE/'build-inputs.py'] + [HERE/p for p in TARGETS if p != 'prep-receipt-v001.json']
receipt = {
    'schema':'opposite-contact-input-preparation-receipt-v1',
    'status':'frozen_inputs_only_guide_visual_review_pending_retention',
    'files':[{'relative_path':str(p.relative_to(HERE)).replace('\\','/'), 'bytes':p.stat().st_size, 'sha256':sha(p)} for p in files],
    'checks':{'canonical_exact_copy':True,'two_ordered_attachments':True,'one_pose_only':True,
              'contralateral_arm_leg_forward':True,'two_design_contacts_same_baseline':True,
              'no_failed_walk_reference_attached':True,'no_generated_raw':True,'no_existing_artwork_edited':True},
    'generation_called':False,'UE_or_UBT_called':False,'guide_pixels_original_technical_only':True,
    'new_guide_visual_review_performed':False,'root_retention_pending':True,
}
write_json('prep-receipt-v001.json', receipt)
print(json.dumps({'prepared_files':len(files)+1,'indexed_input_files':len(files),
                  'input_bytes':sum(p.stat().st_size for p in files),
                  'receipt_sha256':sha(HERE/'prep-receipt-v001.json'),
                  'request_sha256':sha(HERE/'anchor-request.json'),
                  'prompt_sha256':sha(HERE/'prompts/far-contact-anchor.txt'),
                  'guide_png_sha256':sha(png_path)},ensure_ascii=False))
