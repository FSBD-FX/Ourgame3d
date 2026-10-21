"""Prepare one edit input set; draw only a new technical mannequin, never art pixels."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
import shutil
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PROJECT = Path('F:/Ourgame')
HERO = PROJECT / 'source-assets/production/fairytale-hero-v001'
TARGET = HERO / 'walk-passing-pose-inputs-v001/near_support_far_pass/raw/passing-pose.png'
IDENTITY = HERO / 'sprite-run-idle-v002/curated/frame-0.png'
EXPECTED = {
    TARGET: '33b3792646b9d53e08a3ebc7ad9f9ae2f9cac307ae7c082fc8f48989888750da',
    IDENTITY: 'f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718',
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)


def write_json(path: Path, data: object) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def main() -> None:
    outputs = list(ROOT.glob('prep-receipt.json')) + list(ROOT.glob('edit-request.json'))
    if outputs:
        raise SystemExit('Prepared version already exists; create a new version, never overwrite.')
    for path, expected in EXPECTED.items():
        if sha(path) != expected:
            raise SystemExit(f'Frozen input mismatch: {path}')
    created = datetime.now().astimezone().isoformat(timespec='seconds')
    target_copy = ROOT / 'references/edit-target/request140-passing-pose.png'
    identity_copy = ROOT / 'references/identity/canonical131-idle-frame-0.png'
    for source, destination in ((TARGET, target_copy), (IDENTITY, identity_copy)):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise SystemExit(f'Refuse to overwrite reference: {destination}')
        shutil.copyfile(source, destination)
        if sha(destination) != EXPECTED[source]:
            raise SystemExit('Reference copy mismatch')

    # Geometry is authored on an empty canvas. No source image is loaded by this
    # drawing path. Far volumes are placed first, then hidden by near volumes.
    near = '#CF3F41'
    far = '#356EC5'
    outline = '#202027'
    gray = '#D6D6DB'
    shapes = [
        ('ellipse', (187, 70, 325, 222), gray, 'schematic head; not helmet reference'),
        ('polygon', [(222, 224), (280, 224), (295, 305), (273, 339), (216, 337), (204, 305)], gray, 'schematic torso and pelvis'),
        ('polygon', [(278, 245), (296, 248), (315, 299), (309, 321), (290, 318), (277, 282)], gray, 'far neutral arm'),
        ('ellipse', (289, 309, 317, 342), gray, 'far empty glove placeholder'),
        ('polygon', [(209, 244), (225, 253), (207, 293), (208, 323), (190, 326), (184, 291)], gray, 'near neutral arm'),
        ('ellipse', (184, 314, 214, 345), gray, 'near empty glove placeholder'),
        ('polygon', [(247, 323), (267, 325), (305, 365), (314, 382), (292, 395), (272, 370), (252, 350)], far, 'far thigh rooted behind near hip'),
        ('ellipse', (283, 368, 313, 396), far, 'far forward knee'),
        ('polygon', [(287, 386), (309, 391), (301, 426), (279, 429), (278, 415)], far, 'far low forward shin'),
        ('polygon', [(276, 415), (300, 414), (305, 426), (326, 428), (340, 435), (338, 442), (276, 442), (270, 436)], far, 'far floating boot; design sole442'),
        ('polygon', [(214, 323), (242, 317), (264, 327), (261, 359), (254, 394), (219, 398), (211, 361)], near, 'near vertical front thigh hides far root'),
        ('ellipse', (216, 379, 255, 409), near, 'near stance knee in front'),
        ('polygon', [(218, 398), (253, 398), (246, 442), (216, 444), (211, 430)], near, 'near stance shin'),
        ('polygon', [(215, 433), (245, 432), (251, 446), (268, 450), (278, 456), (277, 464), (214, 464), (208, 457)], near, 'near grounded sole; design sole464'),
    ]
    png = ROOT / 'references/technical/thick-occlusion-guide-v001.png'
    svg = ROOT / 'references/technical/thick-occlusion-guide-v001.svg'
    png.parent.mkdir(parents=True, exist_ok=True)
    if png.exists() or svg.exists():
        raise SystemExit('Refuse to overwrite technical guide')
    im = Image.new('RGB', (512, 512), 'white')
    draw = ImageDraw.Draw(im)
    svg_parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">', '<rect width="512" height="512" fill="white"/>']
    for kind, coordinates, color, note in shapes:
        if kind == 'ellipse':
            draw.ellipse(coordinates, fill=color, outline=outline, width=3)
            x0, y0, x1, y1 = coordinates
            svg_parts.append(f'<ellipse cx="{(x0+x1)/2}" cy="{(y0+y1)/2}" rx="{(x1-x0)/2}" ry="{(y1-y0)/2}" fill="{color}" stroke="{outline}" stroke-width="3"><title>{escape(note)}</title></ellipse>')
        else:
            draw.polygon(coordinates, fill=color)
            draw.line(coordinates + [coordinates[0]], fill=outline, width=3, joint='curve')
            points = ' '.join(f'{x},{y}' for x, y in coordinates)
            svg_parts.append(f'<polygon points="{points}" fill="{color}" stroke="{outline}" stroke-width="3" stroke-linejoin="round"><title>{escape(note)}</title></polygon>')
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 13)
    labels = [(18, 19, 'TECHNICAL DEPTH ONLY - NOT CHARACTER ART', outline),
              (18, 42, 'RED = near / front stance; BLUE = far / rear swing', outline),
              (16, 360, 'NEAR FRONT', near), (16, 378, 'root occludes', near),
              (351, 354, 'FAR emerges', far), (351, 372, 'right / forward', far),
              (351, 428, 'low lift', far), (18, 486, 'Gray upper body is schematic. Preserve target upper art.', outline)]
    for x, y, label, color in labels:
        draw.text((x, y), label, font=font, fill=color)
        svg_parts.append(f'<text x="{x}" y="{y+12}" font-family="Arial,sans-serif" font-size="13" fill="{color}">{escape(label)}</text>')
    # Ground line is technical only, unrelated to any measured source root.
    draw.line([(166, 467), (345, 467)], fill='#808088', width=1)
    svg_parts.append('<path d="M166 467 H345" stroke="#808088" stroke-width="1"/>')
    svg_parts.append('</svg>')
    im.save(png, format='PNG')
    write_text(svg, '\n'.join(svg_parts) + '\n')

    prompt = '''EDIT IMAGE1 in place. Output exactly ONE full-body single-pose character image, preserving Image1 composition, resolution and pure green background. This is a local anatomy/depth correction of request140, not a new pose sheet or a new character.

REFERENCE AUTHORITY
Image1 is the EDIT TARGET: request140 near-support/far-passing attempt. Keep its existing head, helmet, torso, arms, hands, belt, both boots, camera and framing unchanged. It already has a low forward raised boot; do not turn that into a rear kick or move the whole character.
Image2 is the ONLY IDENTITY/STYLE authority: canonical request131 curated idle frame0. Preserve its same closed tan bell helmet, rigid dome/rim/top knob/side rivet, black visor with exactly two amber eyes, compact proportions, plain charcoal common body, brown gloves/boots and bold hand-drawn outlines/color blocks. Do not attach the old base or a failed whole walk row. Image2 does not request a return to idle stance.
Image3 is an ORIGINAL THICK-FILLED TECHNICAL OCCLUSION GUIDE ONLY. Red is the camera-NEAR front-depth leg; blue is the camera-FAR rear-depth leg. The blue far-root volume is drawn FIRST, then physically hidden under the filled red near thigh. Follow this actual overlap, not merely the labels. Translate both legs into the same original charcoal trousers with coherent dark shading. Do not copy guide colors, gray head/body, text, floor line, outlines as an overlay or any technical marks into the final artwork.

PRECISE LOCAL CORRECTION: NEAR STANCE IN FRONT / FAR LOW PASSING BEHIND
Only edit the trouser hip attachment, upper-thigh contours, knee shape and their overlap/shading, with the smallest adjacent trouser seam correction needed. Keep the belt and all upper-body artwork exactly as in Image1. Preserve the existing two boot shapes, approximate locations, low lift, ankle continuity and full-body placement; do not redraw the complete image.
The NEAR leg is the standing front-depth leg. It descends almost vertically from the visible near hip beneath the pelvis toward the EXISTING grounded boot on screen-left/beneath the body. Its upper thigh must form a solid foreground mass which OVERLAPS AND HIDES the FAR thigh's root at the crotch. Its knee stays low and aligned over its supporting boot. This supporting boot is the only flat ground contact.
The FAR leg is the passing rear-depth leg. Its thigh begins at the deeper, screen-right part of the pelvis, with its proximal root HIDDEN BEHIND the near stance thigh. From that hidden far hip, the thigh travels forward toward screen-RIGHT; it emerges only beyond the near thigh's right edge, then connects through the low forward knee to the EXISTING slightly raised forward boot. Show a clean, believable rear-depth emergence and one coherent hip-knee-boot chain. Do not let a broad diagonal foreground thigh start at the visible near hip and claim it is the far leg. No crossing foreground ribbon, swapped leg names, disconnected hip or third leg.
The raised far boot remains only slightly above the floor, under/just forward of the pelvis. No backwards kick, heel-to-butt fold, high knee, contact lunge, airborne run or both feet planted. The knee remains well below the belt. Do not mirror or turn the complete character. Near/far mean fixed camera-depth anatomical sides, not a label assigned according to whichever boot is rightmost.

LOCKS AND OUTPUT
Exactly two arms, two separate relaxed empty gloves, two legs and two complete boots. No weapon, armor, cape, new costume, exposed skin, lighting redesign, changed helmet volume, shortened helmet, eye change, upper-body repaint or identity drift. Keep Image1's background pure flat green #00FF00 and preserve its single complete figure and safe padding. No scenery, floor patch, shadows, dust, blur, glow, detached effects, labels, guide lines, colored limbs, mask visualization, text, UI, contact sheet or multiple poses. Output only the edited single full-body pose. Do not claim or illustrate a complete walk cycle.
'''
    prompt_file = ROOT / 'prompts/edit-passing-far-leg.txt'
    write_text(prompt_file, prompt)
    refs = [
        {'order': 1, 'path': str(target_copy), 'sha256': sha(target_copy), 'source': str(TARGET), 'source_request': 140, 'role': 'EDIT TARGET only; not identity truth'},
        {'order': 2, 'path': str(identity_copy), 'sha256': sha(identity_copy), 'source': str(IDENTITY), 'source_request': 131, 'role': 'sole identity/style; does not prescribe idle stance'},
        {'order': 3, 'path': str(png), 'sha256': sha(png), 'role': 'original filled-volume depth geometry only; not art or mask'},
    ]
    contract = {
        'schema': 'fairytale-hero-local-far-passing-edit-contract-v1',
        'prepared_at_system_local': created,
        'status': 'prepared_only_root_retention_and_review_required',
        'output_pose_count': 1, 'loop': False, 'native_facing': 1,
        'target_raw_dimensions_px': [1254, 1254],
        'reference_roles': refs,
        'editable': ['trouser hip attachment', 'thigh contour and depth overlap', 'knee contour/shading', 'minimal adjoining trouser seam'],
        'preserve': ['upper body artwork', 'helmet silhouette and identity', 'two amber eyes', 'arms and gloves', 'belt', 'both existing boots and low-lift geometry', 'camera', 'whole-body placement', 'flat green background'],
        'review_roi_hint_target_px': [490, 755, 775, 1020],
        'roi_semantics': 'rough human review area only; not a measured segmentation mask and not permission to repaint boots or belt',
        'fixed_depth_roles': {'near': 'foreground vertical stance; root at visible near pelvis; occludes far thigh root', 'far': 'rear-depth low forward passing; root behind near thigh; emerges at right edge toward forward knee/raised boot'},
        'guide': {'canvas_px': [512, 512], 'near_rgb_hex': near, 'far_rgb_hex': far, 'gray_upper_body': 'schematic only; never output identity', 'layer_order': ['gray schematic upper body', 'far blue thigh/shin/boot', 'near red thigh/shin/boot in front'], 'near_chain_design_px': [[238, 328], [236, 392], [229, 439]], 'far_chain_design_px': [[257, 329], [298, 382], [290, 424]], 'ground_sole_y_design_only': 464, 'swing_sole_y_design_only': 442, 'actual_art_pixels_used_to_draw_guide': False, 'svg': str(svg), 'svg_sha256': sha(svg)},
        'prohibitions': ['whole image mirror', 'relabel140 as correct without changing anatomy', 'local drawing on existing art', 'copy failed139 whole row', 'attach135/136 as identity', 'normalize motion by reordering or retiming'],
        'actual_output_measurements': {'raw_sha256': None, 'alpha_bbox': None, 'support_boot_roi': None, 'swing_boot_roi': None, 'ground_root_px': None, 'clearance_px': None},
        'gates_pending': ['root F/E input retention', 'actual new guide view by root', 'root sole native edit generation', 'raw F/E retention before viewing', 'actual upper-body preservation and hip-knee-boot static review', 'independent opposite-role comparison'],
        'does_not_establish': ['complete walk cycle', 'motion or seam pass', 'foot root or speed', 'runtime playback', 'UE import', 'final user art acceptance'],
        'future_walk_policy': 'One corrected static passing pose is only a motion-role candidate. A future cycle needs both opposite contacts and passing roles plus six-phase guidance; canonical131 remains sole identity. No single-pose-only final locomotion input.',
        'formal_complete_units': 0,
    }
    write_json(ROOT / 'role-contract.json', contract)
    request = {
        'schema': 'fairytale-hero-native-local-edit-input-v1',
        'prepared_at_system_local': created, 'status': 'prepared_only_not_generated',
        'intended_root_request_label': 142, 'label_not_proof_of_provider_call': True,
        'prompt_file': str(prompt_file), 'prompt_sha256': sha(prompt_file),
        'attachments_in_order': refs,
        'imagegen_parameters_for_root_only': {'referenced_image_paths': [row['path'] for row in refs], 'transparent_background': False, 'num_last_images_to_include': 'omit', 'prompt': 'read exact prompt_file'},
        'expected_future_raw_path': str(ROOT / 'raw/passing-far-leg-edit.png'),
        'generated_output_sha256': None, 'generation_completed': False,
        'generation_authority': 'root only; preparer has no native generation or UE permission',
        'automatic_extract_or_import': False,
    }
    write_json(ROOT / 'edit-request.json', request)
    write_text(ROOT / 'generation-handoff.md', f'''# 142 局部腿部遮挡纠错输入（只准备）

系统时间：{created}。目标是先纠正 140 的 near/far 髋—膝连接。现 140 的低前抬靴已比失败整行改善，但前景斜大腿仍像从 near 髋伸出，不能通过重命名把它当 far passing。

附件顺序固定：140 原件的逐字节副本为编辑目标；131 curated 单帧的逐字节副本是唯一身份；新的厚填充 technical guide 只负责深度/遮挡。Guide 是在空白画布创建的灰 mannequin 与彩色腿体块，不加载、不重绘或叠画任何已有美术；SVG/PNG 共用同份原创形状坐标。红 near 支撑腿后画，遮住先画的蓝 far 大腿根，蓝腿只从前腿右侧向前膝显露。

本次只允许髋/大腿/膝及最小裤缝改动，要求上身/头盔/双手/腰带保持，已有低抬靴不变成后踢。粗 ROI 只是审阅区域，不是已测 mask，也不意味着该框内所有像素都可改。

Root 先 F/E 保全本输入并实际查看 guide，再读 prompts/edit-passing-far-leg.txt 原文进行一次 native edit。生成后 raw 另行保全再看；不要覆盖 140/141、旧输入或原稿。准备者没有调用生成或 UE，也不替 root 接受新姿势。

本次不是 sprite-gen 完成，不生成 atlas，不设假 raw hash、不猜足根/速度，不接 UE。新姿势即便静态清楚，也仅为后续多姿势运动参考候选；完整六相/循环/真实播放仍需独立验证，完整单元仍 0。
''')
    write_text(ROOT / 'qa-review-checklist.md', '''# 待实际输出审查

- 对照140确认上身、钟盔刚体、眼睛、双臂、腰带和两靴未重绘变形；不只对照131说相似。
- 从固定近侧髋向下追到支撑膝/地面靴，近侧大腿是可见前景并实际遮挡远侧根。
- 远侧股根来自更深右侧髋，在近大腿后消失，再从近腿右边缘向前膝/低抬靴显露；不能是换了名字的前景斜腿。
- 检查恰好两腿，关节连续、长度/体积与140相容，低前抬没有变成后踢/高抬/双脚落地。
- 不接受红蓝技术色、图解头/文字/地线进入美术。不为通过而整图镜像、改相位标签、重定时或本地画改。
- 静态结果与141比较是否真正交换支撑/摆腿；歧义仍应写明。尚未量测的足根/间隙不填假值。
- 新素材保全之后才实际看；没有看GIF/UE不能报告动态或运行通过。单姿势不代表六相完成。
''')
    files = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file():
            files.append({'path': str(path), 'relative_path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size})
    receipt = {'schema': 'fairytale-hero-local-edit-preparation-receipt-v1', 'prepared_at_system_local': created, 'interpreter': sys.executable, 'scope': 'new input metadata, exact immutable reference copies, original blank-canvas technical guide only', 'files': files, 'generation_calls': 0, 'ue_or_ubt_calls': 0, 'guide_view_status': 'pending_root_retention_and_view', 'raw_exists': False, 'formal_complete_units': 0}
    write_json(ROOT / 'prep-receipt.json', receipt)
    print(json.dumps({'folder': str(ROOT), 'files_including_receipt': len(files) + 1, 'bytes': sum(row['bytes'] for row in files) + (ROOT / 'prep-receipt.json').stat().st_size, 'receipt_sha256': sha(ROOT / 'prep-receipt.json'), 'prompt_sha256': sha(prompt_file), 'request_sha256': sha(ROOT / 'edit-request.json'), 'guide_png_sha256': sha(png), 'guide_svg_sha256': sha(svg), 'guide_viewed': False, 'generation_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
