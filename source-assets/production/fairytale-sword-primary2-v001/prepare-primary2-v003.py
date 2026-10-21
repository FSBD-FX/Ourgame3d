"""Prepare a genuine low-to-high cut, with design guides only; no provider calls."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RUN = R / 'run-primary2-v003'
STATE = 'sword_primary_2'
DURATIONS = [75, 75, 60, 60, 135, 135]
POSES = [
    {'role': 'low guard handoff', 'shoulder': [205,248], 'elbow': [181,275], 'wrist': [194,297], 'grip': [212,313], 'axis': [.94,-.341]},
    {'role': 'low folded rear-hip load', 'shoulder': [210,250], 'elbow': [182,295], 'wrist': [201,317], 'grip': [220,326], 'axis': [.35,.937]},
    {'role': 'low forward entry with bent elbow', 'shoulder': [218,250], 'elbow': [230,300], 'wrist': [275,305], 'grip': [295,312], 'axis': [.8,.6]},
    {'role': 'upward wrist arc with tucked elbow', 'shoulder': [225,260], 'elbow': [235,315], 'wrist': [280,300], 'grip': [315,285], 'axis': [.8,-.6]},
    {'role': 'folding recovery', 'shoulder': [209,250], 'elbow': [189,284], 'wrist': [214,307], 'grip': [235,317], 'axis': [.99,.1]},
    {'role': 'return to low guard', 'shoulder': [205,248], 'elbow': [181,275], 'wrist': [194,297], 'grip': [212,313], 'axis': [.94,-.341]},
]

def desc(p):
    b=p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def write(p, value):
    assert not p.exists(), p
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return p

assert Path(sys.executable).resolve()==(SG/'.venv/Scripts/python.exe').resolve()
assert not RUN.exists()
refs=[]
for name in ['canonical131-idle0.png','158-ready0-motion.png','159-primary1-last-motion.png']:
    p=R/'sources-v002'/name
    q=R/'sources-v003'/name
    assert p.exists() and not q.exists()
    q.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,q)
    assert p.read_bytes()==q.read_bytes()
    refs.append(q)

seed={'states':{STATE:{'frames':6,'fps':10,'loop':False,'action':'A short bent-arm low-to-high sword cut. Wrist arcs upward while elbow stays tucked; no horizontal punch.'}},
      'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
      'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
seed_path=write(R/'requests/primary2-numeric-input-v003.json',seed)
argv=[sys.executable,'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),
      '--character-id','fairytale-common-hero-sword-primary2-v003','--base-image',str(refs[0]),
      '--description',seed['states'][STATE]['action'],'--style','Accepted131 hand-inked grotesque bell helmet and short cloth body; same direction, palette and silhouette.',
      '--cell-size','512','--safe-margin','48','--chroma-key','#00FF00','--request',str(seed_path)]
proc=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
write(R/'logs/standard-prepare-v003.log',proc.stdout+proc.stderr)
assert proc.returncode==0,proc.stderr
request=RUN/'sprite-request.json'
q=json.loads(request.read_text(encoding='utf-8'))
write(R/'standard-output/sprite-request-before-explicit-timing-v003.json',q)
q['states'][STATE]['durations_ms']=DURATIONS
q['fit'].update(seed['fit'])
q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# A motion diagram, not locally painted game art. All coordinates are design.
im=Image.new('RGB',(3072,512),'#eeeeee');d=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
for i,p in enumerate(POSES):
    ox=i*512
    def pts(v): return [(ox+x,y) for x,y in v]
    d.ellipse((ox+170,90,ox+355,234),fill='#bcbcbc',outline='#333333',width=3)
    d.rectangle((ox+240,55,ox+270,90),fill='#aaaaaa',outline='#333333',width=2)
    d.polygon(pts([(210,234),(290,239),(302,335),(211,335)]),fill='#888888',outline='#333333',width=2)
    d.line(pts([(240,335),(210,390),(190,450)]),fill='#888888',width=30)
    d.line(pts([(275,335),(295,390),(320,450)]),fill='#888888',width=30)
    d.line(pts([(155,464),(218,464)]),fill='#333333',width=12)
    d.line(pts([(280,464),(356,464)]),fill='#333333',width=12)
    d.line(pts([(296,256),(320,310),(341,342)]),fill='#aaaaaa',width=20)
    d.line(pts([p['shoulder'],p['elbow'],p['wrist']]),fill='#444444',width=20,joint='curve')
    d.line(pts([p['wrist'],p['grip']]),fill='#666666',width=16)
    gx,gy=p['grip'];d.ellipse((ox+gx-13,gy-20,ox+gx+13,gy+20),fill='#aaaaaa',outline='#222222',width=2)
    for x,y in [p['shoulder'],p['elbow'],p['wrist']]: d.ellipse((ox+x-4,y-4,ox+x+4,y+4),fill='#111111')
    ax,ay=p['axis'];d.line(pts([(gx,gy),(gx+ax*100,gy+ay*100)]),fill='#999999',width=3)
    d.text((ox+8,8),f"DESIGN phase{i}: {p['role']}",font=font,fill='#111111')
    d.text((ox+8,28),'Joint locations and gray blade ray are proposals, not measurements.',font=font,fill='#111111')
guide=R/'guides/primary2-short-elbow-rising-design-v003.png';assert not guide.exists();guide.parent.mkdir(exist_ok=True);im.save(guide)
refs.extend([guide,RUN/f'references/layout-guides/{STATE}.png'])
contract=write(R/'primary2-design-contract-v003.json',{'poses':POSES,'durations_ms':DURATIONS,'source_canvas':[512,512],
    'all_coordinates_are_design_not_measured':True,'actual_features':None,'body_height_max_screen_px':72,
    'runtime_authority':'existing actual melee Stage1 deadlines; no kernel change',
    'reason':'Native169 active2/3 still show nearly horizontal punch arms. ArcB changed blade angle but not elbow or wrist anatomy; do not accept as final motion.',
    'new_generation_accepted':False})
prompt='''Create exactly SIX complete body-only animation poses in ONE horizontal row for the SAME accepted bell-helmet adventurer in reference1. Keep the crooked warm bell helmet/top knob, two amber eyes inside a black window, charcoal cloth, brown gloves/boots, squat short arms, thick hand-ink outlines and matte broad planes. Fixed 3/4-facing-right view throughout. No face or human skin.

Reference1 is the sole accepted idle identity. References2 and3 supply only the previous low guard / first-cut ending for the two action boundaries. Reference4 is an original grayscale MOTION DESIGN diagram: follow its bent arm and wrist trajectory, not its body style. Reference5 supplies six-slot spacing only. Never print or copy guide marks, labels, gray diagram or rays into output.

This is a LOW-TO-HIGH SECOND SWORD CUT, not a punch. The gripping hand must travel on a curved arc below the helmet, driven by a clearly bent short elbow and wrist turning, rather than moving straight horizontally. The elbow stays low and closer to the torso while the wrist lifts. The active palm is viewed from the side, a narrow closed cylindrical grip with curled fingers and a separate opposing thumb. Keep the far arm relaxed and distinctly separate. No arm extension, boxing knuckles aimed forward, duplicated hand, stretched anatomy or wrist detached from cuff.

Six ordered poses: 0 compact low guard matching the previous ending; 1 draw the gripping hand DOWN beside the rear hip, bent elbow low, knees lightly compressed; 2 sweep into the low front with a still-bent elbow, hand below chest at waist height; 3 lift that wrist diagonally UP and forward while the elbow remains tucked low, visibly different from2, with forearm angled upward, never two horizontal jab poses; 4 fold the elbow inward as the body settles; 5 low guard ready for stop or the next cut. Two anticipation, two active, two recovery. Grounded boots and slight torso rotation, no lunge, jump or spin. Preserve short natural limb lengths over exact target coordinates.

The near hand is EMPTY but shaped to grip a separate future handle. Do not draw any sword, hilt, handle, cylinder or blade. No chest/shoulder armor, bracers, shield or effects baked into this shared body. The canonical helmet remains. Active gloves stay below the helmet lip and away from the eyes. Do not reuse the old straight-arm punching poses. All target coordinates in reference4 are design, not real sockets or bones.

Exactly six separated full bodies, equal invisible slots with generous gaps, on flat opaque GREEN #00FF00. No green material on the character. Entire knob and boots visible, same anatomical scale across the row, standing-equivalent416 sourcepx in512 cells with48px safe padding. Fixed shared row scale later; never normalize individual frames. No cast/contact shadow, floor, text, borders, grid, background scene, motion arc, trail, blur, loose debris or checkerboard. Native output is an intermediate row, not final art or timing proof. Requested timing75/75/60/60/135/135ms is the existing combat kernel intent and must not be printed.
'''
prompt_path=RUN/f'prompts/{STATE}.txt'
write(R/'standard-output/primary2-standard-prompt-v003.txt',prompt_path.read_text(encoding='utf-8'))
prompt_path.write_text(prompt,encoding='utf-8')
roles=['sole_identity_accepted_canonical131_idle','actual158_low_guard_motion_only','actual159_previous_exit_motion_only','original_short_elbow_rising_design_only','standard_six_slot_count_only']
handoff=write(R/'handoffs/primary2-native-input-v003.json',{'generation_ready':False,'root_review_required_before_generation':True,
    'rows':[{'component':'SwordPrimary2Body','state':STATE,'run_dir':RUN.as_posix(),'raw_output_path':(RUN/'raw'/f'{STATE}.png').as_posix(),
    'prompt':desc(prompt_path),'request':desc(request),'reference_images_in_order':[{'role':role,'file':desc(path)} for role,path in zip(roles,refs)],
    'target_mounts_are_measured':False,'standard_prepare_exit_code':0,'numeric_contract':desc(contract),
    'generation_scope':'Canonical131 body-only short-elbow low-to-high second cut, six phases, existing540ms combat kernel; no armor or finalmotion acceptance.'}],
    'formal_complete_units':0})
A=Path('F:/Ourgame/过程图稿与视频/2026-10-16_军剑第二段短肘上挑输入_v003')
assert not A.exists();(A/'原件').mkdir(parents=True);(A/'展示副本').mkdir()
files=[Path(__file__),seed_path,request,prompt_path,contract,handoff,*refs]
entries=[]
for i,p in enumerate(files):
    q=A/'原件'/f'{i:02d}-{p.name}';shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
    entries.append({'source':desc(p),'copy':desc(q)})
for p in refs[-2:]: shutil.copy2(p,A/'展示副本'/p.name)
write(A/'index.json',{'sources':entries,'source_version':'Primary2 design v003','status':'input only; new guides pending explicit review; no native call',
    'all_joint_points_are_design':True,'formal_complete_units':0})
write(A/'README.md','原始参考、标准prepare请求、技术设计图、提示词与索引。新图先E保留再审阅；不是游戏素材、动作验收或已生成角色。旧169与ArcB失败边界继续保留。\n')
print(json.dumps({'handoff':desc(handoff),'archive':A.as_posix(),'generation_ready':False,'native_called':False},ensure_ascii=False))
