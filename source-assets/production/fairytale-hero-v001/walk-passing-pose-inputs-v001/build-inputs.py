"""Prepare two original technical passing-pose inputs; never generate/edit art."""
from pathlib import Path
import hashlib
import json
import shutil
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
PREPARED_AT=datetime.now().astimezone().isoformat(timespec='seconds')
PREPARED_DATE=PREPARED_AT[:10]
CANONICAL=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
CANONICAL_SHA='f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CANONICAL)==CANONICAL_SHA
assert not (HERE/'README.md').exists() and not (HERE/'prep-receipt-v001.json').exists()
PHASES={
 'near_support_far_pass':{
  'support':'near','swing':'far','future_phase':1,
  'near_leg':[(245,328),(250,385),(255,438)],
  'far_leg':[(267,328),(300,376),(286,423)],
  'near_boot':[(255,438),(242,447),(242,464),(299,464)],
  'far_boot':[(286,423),(276,433),(276,442),(322,442)],
  'depth':'Near stance upper thigh is the visible front layer descending from the near hip; far passing thigh starts behind the near hip and moves forward on the far side, its knee emerging ahead/right of the supporting thigh. Do not turn that far boot into a rear kick.',
 },
 'far_support_near_pass':{
  'support':'far','swing':'near','future_phase':4,
  'near_leg':[(245,328),(296,376),(284,423)],
  'far_leg':[(267,328),(261,385),(255,438)],
  'near_boot':[(284,423),(274,433),(274,442),(320,442)],
  'far_boot':[(255,438),(242,447),(242,464),(299,464)],
  'depth':'Near passing upper thigh starts at the visible near hip and sweeps IN FRONT OF the far supporting thigh where they cross; far stance remains connected to its own deeper hip and descends underneath. Do not redraw the near leg as the same vertical stance leg used in the other trial.',
 },
}
RED,BLUE,GRAY='#cf3f41','#356ec5','#626a74'
NEAR_ARM=[(233,255),(229,288),(235,322)]
FAR_ARM=[(267,255),(279,286),(283,320)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)

def write(p,text):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
 return p
def write_json(p,d):return write(p,json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def poly(points,color,width=9):
 pts=' '.join(f'{x},{y}'for x,y in points)
 return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>'

all_phase_files=[]
for name,cfg in PHASES.items():
 p=HERE/name
 assert not p.exists(),f'New phase directory required: {p}'
 identity=p/'references/identity/canonical-idle-frame-0.png'
 identity.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(CANONICAL,identity)
 assert sha(identity)==CANONICAL_SHA
 title=f"TECHNICAL: {cfg['support'].upper()} SUPPORT / {cfg['swing'].upper()} PASS (NOT ART)"
 support_label=f"{cfg['support'].upper()} full sole / grounded"
 swing_label=f"{cfg['swing'].upper()} knee FORWARD"
 paths=[(FAR_ARM,BLUE),(cfg['far_leg'],BLUE),(cfg['far_boot'],BLUE)]
 near_paths=[(cfg['near_leg'],RED),(cfg['near_boot'],RED),(NEAR_ARM,RED)]
 # Original schematic on a blank canvas. No source artwork is loaded/traced.
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">',
      '<rect width="512" height="512" fill="#ffffff"/>',
      '<g font-family="Arial,sans-serif" font-size="13" fill="#202020">',
      f'<text x="12" y="20">{title}</text>',
      '<text x="12" y="41" fill="#cf3f41">RED = camera-NEAR</text>',
      '<text x="278" y="41" fill="#356ec5">BLUE = camera-FAR</text></g>',
      '<rect x="48" y="48" width="416" height="416" fill="none" stroke="#dddddd" stroke-dasharray="5 5"/>',
      '<line x1="74" y1="464" x2="440" y2="464" stroke="#888888" stroke-width="2"/>']
 svg += [poly(points,color)for points,color in paths]
 svg += ['<ellipse cx="256" cy="151" rx="67" ry="72" fill="none" stroke="#626a74" stroke-width="5"/>',
         '<path d="M329,151 L362,151 M350,141 L362,151 L350,161" fill="none" stroke="#626a74" stroke-width="4"/>',
         '<path d="M256,223 L256,252 L256,328 M233,255 L267,255 M245,328 L267,328" fill="none" stroke="#626a74" stroke-width="7" stroke-linecap="round"/>']
 svg += [poly(points,color)for points,color in near_paths]
 for points,color in [(FAR_ARM,BLUE),(cfg['far_leg'],BLUE),(cfg['near_leg'],RED),(NEAR_ARM,RED)]:
  for x,y in points:svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#ffffff" stroke="{color}" stroke-width="3"/>')
 svg += ['<path d="M346,442 L346,464 M341,447 L346,442 L351,447 M341,459 L346,464 L351,459" fill="none" stroke="#888888" stroke-width="2"/>',
         '<g font-family="Arial,sans-serif" font-size="12" fill="#202020">',
         f'<text x="320" y="374">{swing_label}</text>',
         '<text x="354" y="455">low clearance</text>',
         f'<text x="168" y="486">{support_label}</text>',
         '<text x="12" y="504">One pose only / RIGHT facing / no cycle or measured root</text>',
         '</g></svg>']
 svg_path=write(p/'references/technical/passing-role-guide-v001.svg','\n'.join(svg)+'\n')
 img=Image.new('RGB',(512,512),'#ffffff');d=ImageDraw.Draw(img)
 d.text((12,6),title,fill='#202020',font=font)
 d.text((12,27),'RED = camera-NEAR',fill=RED,font=font)
 d.text((278,27),'BLUE = camera-FAR',fill=BLUE,font=font)
 for x in range(48,465,10):
  d.line([(x,48),(min(x+5,464),48)],fill='#dddddd');d.line([(x,464),(min(x+5,464),464)],fill='#dddddd')
 for y in range(48,465,10):
  d.line([(48,y),(48,min(y+5,464))],fill='#dddddd');d.line([(464,y),(464,min(y+5,464))],fill='#dddddd')
 d.line([(74,464),(440,464)],fill='#888888',width=2)
 for points,color in paths:d.line(points,fill=color,width=9,joint='curve')
 d.ellipse([189,79,323,223],outline=GRAY,width=5)
 d.line([(329,151),(362,151)],fill=GRAY,width=4);d.line([(350,141),(362,151),(350,161)],fill=GRAY,width=4)
 for points in [[(256,223),(256,252),(256,328)],[(233,255),(267,255)],[(245,328),(267,328)]]:d.line(points,fill=GRAY,width=7,joint='curve')
 for points,color in near_paths:d.line(points,fill=color,width=9,joint='curve')
 for points,color in [(FAR_ARM,BLUE),(cfg['far_leg'],BLUE),(cfg['near_leg'],RED),(NEAR_ARM,RED)]:
  for x,y in points:d.ellipse([x-6,y-6,x+6,y+6],fill='white',outline=color,width=3)
 d.line([(346,442),(346,464)],fill='#888888',width=2)
 d.line([(341,447),(346,442),(351,447)],fill='#888888',width=2)
 d.line([(341,459),(346,464),(351,459)],fill='#888888',width=2)
 d.text((320,362),swing_label,fill='#202020',font=small)
 d.text((354,443),'low clearance',fill='#202020',font=small)
 d.text((168,474),support_label,fill='#202020',font=small)
 d.text((12,492),'One pose only / RIGHT facing / no cycle or measured root',fill='#202020',font=small)
 png_path=p/'references/technical/passing-role-guide-v001.png';img.save(png_path,format='PNG')

 support,swing=cfg['support'].upper(),cfg['swing'].upper()
 prompt=f'''Generate exactly ONE full-body WALK PASSING pose, not a strip, not multiple views and not a complete cycle.

ATTACHMENT AUTHORITY
Image1 is the ONLY identity/style reference: request131 single curated idle. Preserve its compact body proportions, closed tan bell helmet, black visor with exactly two amber eyes, exact dome/rim/visor/side rivet/top knob, charcoal plain underclothes, belt, brown gloves/boots and bold hand-drawn ink/painted color blocks. Same original RIGHT-facing three-quarter camera. Helmet is rigid: no squash, shortening, changed volume, new angle or changed eye count. EMPTY HANDS, no armor, weapon, shield, cape, skin redesign or new costume.
Image2 is ORIGINAL TECHNICAL LIMB-ROLE guidance only, never identity/style. RED is camera-NEAR arm and leg; BLUE is camera-FAR arm and leg. Translate both to the original charcoal clothes and brown gloves/boots. No colored limbs or gray schematic head in final art. Near/far are FIXED camera-depth sides, not current screen-left/right. Follow each chain shoulder-elbow-wrist and hip-knee-ankle; do not swap names to fit a reused pose.

EXACT SINGLE POSE: {support} SUPPORT / {swing} PASSING FORWARD
The {support} leg is the ONLY supporting leg. Its thigh and knee descend beneath the pelvis with a natural small knee bend. Its boot FULL SOLE is FLAT on the ground directly beneath the pelvis. Not a forward heel strike, rear toe push, lunge or wide fighting stance.
The {swing} leg is the SWING leg. Its KNEE moves FORWARD toward screen-RIGHT, visibly ahead of the supporting knee, as it passes the stance leg. Its lower leg bends naturally downward; the {swing} boot is beneath or JUST IN FRONT of the pelvis and is clearly a SMALL DISTANCE ABOVE the ground. Keep this boot FORWARD of the stance leg, not folded back to screen-LEFT. Show low clearance, about a small fraction of one boot height, not a high-knee march. The knee stays well BELOW the belt/hip level. Do not draw a backwards kick, heel-to-butt recovery, airborne run, second planted foot or contact pose.
Depth/occlusion requirement: {cfg['depth']}
Make the pelvis-to-thigh connection and the forward swing knee readable, with coherent shading and overlap so the identity of the supporting leg and the opposite passing leg is unambiguous. A small natural shoulder/hip counterrotation is allowed to expose these chains; keep the camera, same right-facing helmet, body volume and near/far depth consistent. Do not turn or mirror the complete character.

ARMS AT PASSING
Both arms pass through a relaxed, softly bent NEUTRAL down position near the sides. The camera-near arm remains the larger visible front-depth arm; the far arm remains attached to its far shoulder. Hands are separate relaxed empty gloves. Neutral arm angles can be similar in the two opposite passing trials; do NOT force a punch, swap the arms or invent different hand roles just to make poses look different. The leg support/swing roles must actually exchange. This still image does not establish their direction of motion or speed.

ANATOMY AND FRAMING
Exactly two arms/hands and two legs/complete boots, stable limb lengths and glove/boot volumes. No detached hands, missing feet, extra fingers, fused knees or impossible ankles. One square image, nominal512x512, one complete centered head-to-toe figure, at least48px safe padding on every side. The pelvis stays over the supporting sole; no body translation used as a substitute for the pose. Keep Image1's proportions and identity.
Use perfectly FLAT PURE GREEN #00FF00 background for later deterministic extraction; no green in the character. No ground patch or cast/contact shadow, dust, blur, trails, glow, detached effects, scenery, UI, words, numbers, labels, arrows, bones, joint dots, floor line, colored guide marks, guide borders or checkerboard. Do not paste Image2's technical diagram. No realistic texture, PBR, 3D render, new style or palette. Output only this single {support.lower()}-support/{swing.lower()}-passing character image.
'''
 prompt_path=write(p/'prompts/passing-pose.txt',prompt)
 pose={
  'schema':'fairytale-hero-single-passing-pose-contract-v1','status':'prepared_only_not_generated_not_accepted',
  'prepared_local_date':PREPARED_DATE,'prepared_at_system_local':PREPARED_AT,'phase_name':name,'future_six_phase_index':cfg['future_phase'],
  'output_pose_count':1,'loop':False,'native_facing':1,'target_canvas_px':[512,512],'safe_margin_px':[48,48],
  'identity':{'path':str(CANONICAL),'copy':str(identity),'sha256':CANONICAL_SHA,'source_request':131,
              'sole_identity':True,'final_user_art_or_motion_approval':False},
  'roles':{'support_leg':cfg['support'],'support_foot':'full sole flat directly beneath pelvis; only ground contact',
           'swing_leg':cfg['swing'],'swing_knee':'forward/right of support knee, well below hip/belt',
           'swing_boot':'under or just in front of pelvis, slightly above ground, never left/rear kick',
           'occlusion':cfg['depth'],'arms':'neutral can share angle; camera-depth identities and shoulder chains stay fixed'},
  'guide':{'png':str(png_path),'png_sha256':sha(png_path),'svg':str(svg_path),
           'role':'original technical geometry only, not style or measurement from art',
           'colors_for_guide_only':{'near':RED,'far':BLUE},
           'joints_design_px':{'near_arm':NEAR_ARM,'far_arm':FAR_ARM,'near_leg':cfg['near_leg'],'far_leg':cfg['far_leg']},
           'ground_baseline_y_design_only':464,'swing_sole_y_design_only':442,'low_clearance_design_only':22,
           'existing_art_pixels_used':False},
  'actual_output_measurements':{'raw_sha256':None,'alpha_bbox':None,'helmet_bbox':None,'body_height_px':None,
                               'support_boot_roi':None,'swing_boot_roi':None,'clearance_px':None,'root_px':None},
  'acceptance_needed':['root retention and actual guide review before generation','actual output identity/rigid helmet comparison',
                       'unambiguous opposite support/swing hip-knee-boot chains','low forward passing boot with only support foot grounded',
                       'independent static review'],
  'does_not_establish':['six-phase gait','motion direction or speed','loop seam','foot slide','left mirror','runtime or equipment adaptation'],
  'future_complete_row_policy':'Only after both opposite passing roles pass static review, combine accepted multi-pose motion references with both contacts and six-phase guidance. Canonical131 alone remains identity. Do not splice/relabel/reorder/retime failed139 into acceptance or use a single peak pose as sole walk anchor.',
  'formal_complete_units':0,
 }
 pose_path=write_json(p/'pose-contract.json',pose)
 request={
  'schema':'fairytale-hero-passing-pose-generation-input-v1','status':'prepared_only_root_generation_pending',
  'phase_name':name,'output_pose_count':1,'native_facing':1,'target_canvas_px':[512,512],
  'chroma_key':{'rgb':[0,255,0],'hex':'#00FF00'},'prompt_file':str(prompt_path),
  'attachments_in_order':[{'order':1,'path':str(identity),'sha256':sha(identity),'role':'sole identity: canonical131 single curated idle'},
                          {'order':2,'path':str(png_path),'sha256':sha(png_path),'role':'original single passing-pose technical guide only'}],
  'excluded_default_attachments':['137 contact','138 contact','139 failed walk','135/136 failed walks','129 base','whole idle strip'],
  '137_138_role':'known static role comparisons only, not default generation inputs or identity',
  'imagegen_parameters_for_root_only':{'referenced_image_paths':[str(identity),str(png_path)],'transparent_background':False,
                                      'num_last_images_to_include':'omit','prompt':'read exact prompt_file'},
  'generation_authority':'root only; preparer has no generation/UE permission','generation_completed':False,
  'expected_future_raw_path':str(p/'raw/passing-pose.png'),'generated_output_sha256':None,
  'automatic_extract_or_import':False,'retention_before_view':'root F/E v074 input retention, then actual new guide review; future raw must also be retained before view',
  'no_speed_or_root_lock':True,'future_complete_row_policy':pose['future_complete_row_policy'],
 }
 request_path=write_json(p/'anchor-request.json',request)
 support_points=cfg[cfg['support']+'_leg'];swing_points=cfg[cfg['swing']+'_leg']
 assert swing_points[1][0]>support_points[1][0] and swing_points[1][1]>328
 assert min(x for x,y in cfg[cfg['swing']+'_boot'])>256
 assert cfg[cfg['support']+'_boot'][-1][1]==464 and cfg[cfg['swing']+'_boot'][-1][1]==442
 assert len(request['attachments_in_order'])==2 and not (p/'raw').exists()
 phase_files=[identity,svg_path,png_path,prompt_path,pose_path,request_path]
 receipt={'schema':'passing-pose-input-preparation-receipt-v1','phase_name':name,'prepared_local_date':PREPARED_DATE,'prepared_at_system_local':PREPARED_AT,
          'status':'frozen_inputs_only_new_guide_view_pending_root_retention',
          'files':[{'relative_path':str(f.relative_to(p)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':sha(f)}for f in phase_files],
          'checks':{'canonical_exact_copy':True,'only_two_ordered_attachments':True,'one_pose_only':True,
                    'opposite_support_and_swing_leg':True,'swing_knee_forward_and_below_hips_design':True,
                    'swing_boot_forward_and_low_clearance_design':True,'neutral_arm_similarity_allowed':True,
                    'no_failed_or_contact_row_attached':True,'no_generated_raw':True,'no_existing_art_pixels_edited':True},
          'generation_called':False,'UE_or_UBT_called':False,'new_guide_viewed':False,'retention_pending':True}
 receipt_path=write_json(p/'prep-receipt-v001.json',receipt)
 all_phase_files.extend(phase_files+[receipt_path])

readme=write(HERE/'README.md','''# 两张相反passing单姿势输入 v001

日期：2026-10-16。仅执行2026-10-15-bound-run-capture-restore计划的Separate art task；运行时快照由其他协作者负责。本目录仅准备两单姿势，未生成最终角色像素、未提取/导入/播放/运行UE，未改Source、旧素材、ledger、进度或保全索引。

唯一身份：131 idle-v002/curated/frame-0.png，两个输入均为严格字节副本，SHA f931dec698967ae497daf85d8bfd2a9c49d59ca34fd56a96a6167e677c3de718。canonical此前已实际查看/留档：闭钟盔、双琥珀眼、灰黑内衣、棕手套靴、空手、固定朝右三分之四深度。技术身份锚点不等于最终用户画风/运动批准。

## 两个独立入口

- near_support_far_pass/anchor-request.json 与 prompts/passing-pose.txt：近脚掌在骨盆下支撑，远膝向右前越过支撑腿；远靴在骨盆下/略前低抬，不后踢。
- far_support_near_pass/anchor-request.json 与 prompts/passing-pose.txt：远脚掌支撑，近膝前移；近大腿在交叉处覆盖远支撑腿，近靴低抬到骨盆前/下方。

每个入口仅附本相canonical副本＋原创单相骨架guide，137/138仅为已知接触角色对照，不默认附，139及135/136失败行均不附。近/远按相机深度，不随屏幕左右改名；引导中的红近蓝远不得进入角色配色。轻微躯干/肩髋反扭可帮助看到连接，但不得改相机、钟盔体积或整体镜像。

neutral臂可以经过相同角度、未来速度方向相反；本次不会以同角度手位判错或强画拳击来制造两帧差别。两个支撑/摆腿身份必须实际相反，不能仅换标签。靴子抬到骨盆后或抬膝至腰以上都不满足本低passing题。

## 技术设计与未知实测

两个guide都从白纸原创绘制，非现有角色图的描改/裁切/调色。SVG保留设计几何，PNG是同几何的技术参考。设计站立sole基线464、摆sole442，22px低抬仅用于讲解；所有髋膝点与颜色层次都是技术设计，不能当新原稿足根、真实脚底、步幅或速度。实际生成/alpha/头盔bbox/足根字段保持null。

新guide本准备者没有view；须root按v074 F/E保全后实际查看，再独占原生生成140/141。未来原稿保存到各相raw/passing-pose.png，实际request/尺寸/SHA生成后再记录，保全后再审；不预写不存在的PNG哈希。费用/供应商调用由root，准备者不调用图像工具。

静态审查须沿两髋→膝→靴检查深度和身份，确认唯一支撑靴全掌接地、另一靴向前低抬，保持canonical身体体积、钟盔与解剖。技术文件/结构通过不是视觉通过。两相都接受后才考虑多姿势运动参考和完整六相；不能拼接/重标/重排/重定时失败139成合格动作，不能将任何单峰姿势作为完整walk唯一锚点。之后仍须实际循环、接缝、落足/步幅、镜像和UE小尺度验证。formal complete units仍0/15。

## 可复核输入

每相prep-receipt绑定其6个输入；本目录prep-receipt绑定全部14个相文件、此README与原始build-inputs.py。脚本使用sprite-gen自带venv，只字节复制canonical并从空白画技术guide，拒绝覆盖本版输出。无installed skill修改。root收到freeze后负责保全/看guide/生成，准备者至此停止视觉写入。
''')
files=[HERE/'build-inputs.py',readme]+all_phase_files
overall={'schema':'two-passing-pose-inputs-preparation-receipt-v1','prepared_local_date':PREPARED_DATE,'prepared_at_system_local':PREPARED_AT,
         'status':'frozen_inputs_only_root_retention_and_guide_review_pending','phase_names':list(PHASES),
         'files':[{'relative_path':str(f.relative_to(HERE)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':sha(f)}for f in files],
         'checks':{'two_independent_opposite_roles':True,'each_only_canonical_and_own_guide':True,'canonical_sha_exact_both':True,
                   'design_low_forward_boot_clearance':True,'future_root_speed_motion_unknown':True,'no_generation_or_UE':True},
         'new_guide_visual_review_performed':False,'generation_calls':0,'formal_complete_units':0}
write_json(HERE/'prep-receipt-v001.json',overall)
print(json.dumps({'total_files':len(files)+1,'indexed_inputs':len(files),'indexed_bytes':sum(f.stat().st_size for f in files),
                  'overall_receipt_sha256':sha(HERE/'prep-receipt-v001.json'),
                  'phases':{n:{'request_sha256':sha(HERE/n/'anchor-request.json'),'prompt_sha256':sha(HERE/n/'prompts/passing-pose.txt'),
                               'guide_png_sha256':sha(HERE/n/'references/technical/passing-role-guide-v001.png'),
                               'receipt_sha256':sha(HERE/n/'prep-receipt-v001.json')}for n in PHASES}},ensure_ascii=False))
