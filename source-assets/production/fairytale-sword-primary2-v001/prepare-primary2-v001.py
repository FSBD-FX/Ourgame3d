"""Prepare SWD001 Primary2 body-only inputs; no provider, extraction, or UE calls."""
from pathlib import Path
from datetime import datetime
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parent
PROJECT = Path('F:/Ourgame')
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
RETAINED = Path('E:/OurGame/Knight/过程图稿与视频')
STATE = 'sword_primary_2'
RUN = ROOT / 'run-primary2-v001'
DURATIONS = [75, 75, 60, 60, 135, 135]
BOUNDARIES = [0, 75, 150, 210, 270, 405, 540]
POSES = [
    dict(phase='handoff from actual159 final low guard', shoulder=[205,248], elbow=[181,275], wrist=[194,297], grip=[212,313], axis=[.94,-.341], hip=[0,0], far_hand=[340,342]),
    dict(phase='compact inward chest-below load', shoulder=[205,248], elbow=[181,268], wrist=[192,278], grip=[214,284], axis=[.98,.15], hip=[-2,0], far_hand=[341,341]),
    dict(phase='active1 inside-to-forward horizontal cut', shoulder=[207,248], elbow=[210,281], wrist=[235,288], grip=[256,291], axis=[1.,0.], hip=[2,1], far_hand=[342,339]),
    dict(phase='active2 short forward outside sweep', shoulder=[208,249], elbow=[230,277], wrist=[258,294], grip=[280,302], axis=[.99,-.10], hip=[3,1], far_hand=[342,338]),
    dict(phase='compact elbow return below chest', shoulder=[206,248], elbow=[190,285], wrist=[214,309], grip=[235,317], axis=[.99,.10], hip=[1,0], far_hand=[341,341]),
    dict(phase='low guard exit for stop or future third action', shoulder=[205,248], elbow=[181,275], wrist=[194,297], grip=[212,313], axis=[.94,-.341], hip=[0,0], far_hand=[340,342]),
]


def fact(path):
    data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def write(relative, value):
    path = ROOT / relative
    assert not path.exists(), f'Refuse overwrite: {path}'
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    path.write_text(text, encoding='utf-8', newline='\n')
    return path


def verify_retention(source, batch):
    manifest = RETAINED / batch / 'source-size-SHA256.json'
    payload = json.loads(manifest.read_text(encoding='utf-8-sig'))
    src = fact(source)
    matches = [x for x in payload['files'] if x['sha256'].lower() == src['sha256'] and x['bytes'] == src['bytes']]
    assert matches, f'Source has no retained byte match: {source}'
    target = RETAINED / batch / matches[0]['retained_relative'].replace('\\', '/')
    assert source.read_bytes() == target.read_bytes()
    return dict(source=src, retained=fact(target), retention_manifest=fact(manifest), direct_byte_equal=True)


def draw_motion_guide():
    # An original grayscale design diagram, never a body-pixel repaint or final sprite.
    image = Image.new('RGB', (512 * len(POSES), 512), '#eeeeee')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="3072" height="512"><rect width="100%" height="100%" fill="#eeeeee"/>']
    for frame, pose in enumerate(POSES):
        ox = frame * 512
        hx, hy = pose['hip']

        def polygon(points, fill, width=2):
            points = [(ox + x, y) for x, y in points]
            draw.polygon(points, fill=fill, outline='#222222', width=width)
            svg.append('<polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x,y in points) + f'" fill="{fill}" stroke="#222222" stroke-width="{width}"/>')

        def line(points, fill, width):
            points = [(ox + x, y) for x, y in points]
            draw.line(points, fill=fill, width=width, joint='curve')
            svg.append('<polyline points="' + ' '.join(f'{x:.2f},{y:.2f}' for x,y in points) + f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round"/>')

        fx, fy = pose['far_hand']
        line([(291+hx*.3,250+hy*.3),(314,302),(fx,fy-13)], '#999999', 22)
        polygon([(fx-10,fy-18),(fx+8,fy-17),(fx+13,fy-5),(fx+10,fy+13),(fx+3,fy+17),(fx,fy+5),(fx-4,fy+14),(fx-9,fy+11),(fx-6,fy-2),(fx-12,fy-7)], '#bbbbbb')
        polygon([(207+hx,239+hy),(284+hx,241+hy),(302+hx,308+hy),(281+hx,339),(234+hx,337),(205+hx,302+hy)], '#777777')
        line([(237+hx,335),(213+hx*.3,377),(194,425)], '#777777', 34)
        line([(279+hx,335),(290+hx*.3,377),(303,423)], '#777777', 30)
        polygon([(174,420),(211,420),(218,447),(223,464),(151,464),(156,445)], '#aaaaaa')
        polygon([(283,420),(319,420),(325,443),(351,453),(355,460),(267,460),(272,444)], '#aaaaaa')
        polygon([(173,210),(184,160),(202,126),(238,106),(282,108),(311,127),(324,156),(337,160),(337,177),(324,177),(335,226),(306,236),(250,229),(205,220)], '#bbbbbb')
        polygon([(242,86),(269,86),(276,107),(243,107)], '#bbbbbb')
        polygon([(230,66),(251,48),(273,76),(246,86)], '#bbbbbb')
        line([pose['shoulder'],pose['elbow'],pose['wrist']], '#666666', 29)
        line([pose['wrist'],pose['grip']], '#999999', 22)
        gx, gy = pose['grip']
        ax, ay = pose['axis']
        length = math.hypot(ax, ay)
        ax, ay = ax / length, ay / length
        ux, uy = -ay, ax

        def hand(points):
            return [(gx+u*ux+v*ax,gy+u*uy+v*ay) for u,v in points]

        polygon(hand([(-18,-14),(-18,11),(-9,19),(11,18),(19,10),(20,-10),(10,-18),(-9,-19)]), '#aaaaaa')
        for v in [-9,-1,7]:
            line(hand([(-8,v),(16,v)]), '#333333', 2)
        polygon(hand([(-5,15),(2,20),(16,11),(12,4),(5,5)]), '#bbbbbb')
        # No rendered weapon/axis; the numbers are in JSON/text, not final art.
        for yy, text in zip([12,30,480], [f'f{frame} / {pose["phase"]} / {DURATIONS[frame]}ms', 'SHORT ARM / forward +X active sweep / far hand separate', 'GRAY DESIGN ONLY: no guide shapes, labels or recolor in final.']):
            draw.text((ox+12,yy), text, fill='#111111', font=font)
            svg.append(f'<text x="{ox+12}" y="{yy+12}" font-size="12">{html.escape(text)}</text>')
    svg.append('</svg>')
    write('guides/primary2-shortarm-motion-v001.svg', '\n'.join(svg) + '\n')
    target = ROOT / 'guides/primary2-shortarm-motion-v001.png'
    assert not target.exists()
    image.save(target)
    return target


def main():
    assert Path(sys.executable).resolve() == (SG / '.venv/Scripts/python.exe').resolve(), sys.executable
    assert np.__version__
    assert not RUN.exists(), 'Fresh preparation only, no force/reuse.'
    kernel = PROJECT / 'UnrealGame/Source/CodexDungeon/DungeonContentCombat.h'
    sampler = PROJECT / 'UnrealGame/Source/CodexDungeon/DungeonFighter.cpp'
    kernel_text = kernel.read_text(encoding='utf-8')
    stages = re.findall(r'MakeStage\((\d+),(\d+),(\d+),([^)]*)\)', re.search(r'D\[0\]\.Primary=\{([^;]+)\};',kernel_text).group(1))
    assert tuple(map(int,stages[1][:3])) == (150,120,270)
    assert DURATIONS == [int(x)//2 for x in stages[1][:3] for _ in range(2)]
    assert sum(DURATIONS) == BOUNDARIES[-1] == 540
    assert all(POSES[i]['axis'][0] > .95 for i in [2,3])
    canonical = PROJECT / 'source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png'
    ready = PROJECT / 'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
    prior = PROJECT / 'source-assets/production/fairytale-sword-v001/run-primary1-v003/curated/frame-5.png'
    sources = [
        ('canonical131-idle0.png',canonical,'2026-10-15-OurgameUE-公共身体刚盔待机提取预览-v048','sole accepted canonical idle identity'),
        ('158-ready0-motion.png',ready,'2026-10-16-OurgameUE-lowguard-extracted-v141','low guard posture only, no identity ownership'),
        ('159-primary1-last-motion.png',prior,'2026-10-16-OurgameUE-lowguard-primary-extract-gap-v149','previous action exit only, not a whole-row motion replacement'),
    ]
    provenance = []
    for name,path,batch,role in sources:
        record = verify_retention(path,batch)
        record['role'] = role
        destination = ROOT / 'sources' / name
        assert not destination.exists()
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,destination)
        assert destination.read_bytes() == path.read_bytes()
        record['input_copy'] = fact(destination)
        provenance.append(record)
    write('source-retention-proof-v001.json',dict(schema='primary2-existing-sources-retained-before-view-v1',sources=provenance,existing_sources_viewed=True,new_derived_images_viewed=False))
    action = 'Compact single-handed body-only reverse horizontal second slash: low guard, short inward below-chest load, two forward +X outward cuts below the eye window, compact elbow return, low guard exit. This is not the first high-load diagonal slash.'
    seed = dict(states={STATE:dict(frames=6,fps=10,loop=False,action=action,durations_ms=DURATIONS)},cell=dict(width=512,height=512,safe_margin_x=48,safe_margin_y=48),fit=dict(pixel_unfake=False,resample='lanczos',align_x='bbox-center',align_y='bottom',ground_frames=False,segmentation='components',shared_row_scale=True))
    seed_path = write('requests/primary2-numeric-input-v001.json',seed)
    argv = [sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(RUN),'--character-id','fairytale-common-hero-sword-primary2-v001','--base-image',str(ROOT/'sources/canonical131-idle0.png'),'--description',action,'--style','EXACT accepted canonical131 grotesque squat bell helmet, charcoal cloth, brown gloves/boots. One native3/4right direction, body-only, no added armor or weapon.','--cell-size','512','--safe-margin','48','--chroma-key','#00FF00','--request',str(seed_path)]
    result = subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
    write('logs/standard-prepare-v001.log',result.stdout+result.stderr)
    assert result.returncode == 0, result.stdout+result.stderr
    request_path = RUN / 'sprite-request.json'
    request = json.loads(request_path.read_text(encoding='utf-8'))
    write('standard-output/sprite-request-before-explicit-timing-v001.json',request)
    request['states'][STATE]['durations_ms'] = DURATIONS
    request['fit'].update(seed['fit'])
    request['chroma'] = dict(mode='rgb',unmix_reach=4,spill_max_fraction=.005)
    request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    assert (RUN/'base-source.png').read_bytes() == canonical.read_bytes()
    guide = draw_motion_guide()
    timing = dict(weapon='WPN-SWD-001',stage_zero_based=1,windup_ms=150,lock_ms=60,active_ms=120,recovery_ms=270,total_ms=540,frame_boundaries_ms=BOUNDARIES,durations_ms=DURATIONS,damage=24,stagger=14,range_cm=135,depth_halfwidth_cm=46,source_kernel=fact(kernel),source_sampler=fact(sampler),runtime_sampler='Actual accepted Action Start/ActiveStart/ActiveEnd/End via GetPrimaryPoseFrame. No independent clock, input, damage, root movement or speed override.',action_speed_pct_clamp=[-20,20],speed_examples=[dict(action_speed_pct=p,frame_durations_ms=[d/(1+p/100) for d in DURATIONS],total_ms=540/(1+p/100)) for p in [-20,0,20]],old_v1_equipment_text_is_superseded='Old no-combo/no-random-crit wording is not the authority for the subsequently requested three-stage kernel.',nominal_fps_only=10,standard_fps_preview_is_not_timing_proof=True)
    pose_records = []
    for i, p in enumerate(POSES):
        pose_records.append(dict(frame=i,phase=p['phase'],duration_ms=DURATIONS[i],source_root_design_px=[256,464],near_shoulder_design_px=p['shoulder'],near_elbow_design_px=p['elbow'],near_wrist_design_px=p['wrist'],near_grip_design_px=p['grip'],invisible_blade_axis_design_xy=p['axis'],far_hand_design_px=p['far_hand'],torso_weight_offset_design_px=p['hip'],upper_arm_projected_design_length=math.dist(p['shoulder'],p['elbow']),forearm_projected_design_length=math.dist(p['elbow'],p['wrist']),palm_offset_design_length=math.dist(p['wrist'],p['grip']),all_coordinates_are_design_not_measurement=True,actual_grip_px=None,actual_axis_xy=None,actual_foot_roots_px=None,actual_thumb_contour=None,actual_helmet_hand_blade_clearance=None))
    contract = write('primary2-design-contract-v001.json',dict(schema='fairytale-shortarm-primary2-design-v1',state=STATE,frame_count=6,timing=timing,source_canvas_px=[512,512],source_native_facing=1,source_root_display_design_px=[256,464],standing_equivalent_design_height_px=416,fixed_display_canvas=72*512/416,visible_body_height_upper_bound_px=72,poses=pose_records,continuity=dict(previous_actual_source=provenance[2]['source'],entry_design='Source159 final guard is posture reference; new pose0 must be measured and reviewed after generation.',exit_design='Return to actual158 low guard posture; no claim future Primary3 is designed/accepted.',source_or_runtime_motion_accepted=False),generation_ready=False,generated=False,formal_complete_units=0))
    prompt_path = RUN / 'prompts' / f'{STATE}.txt'
    standard_prompt = prompt_path.read_text(encoding='utf-8')
    write('standard-output/primary2-standard-prompt-v001.txt',standard_prompt)
    phase_text = '\n'.join(f'{i}: {p["phase"]}; near shoulder{p["shoulder"]} > elbow{p["elbow"]} > wrist{p["wrist"]} > grip{p["grip"]}; invisible future blade axis{p["axis"]}; far hand{p["far_hand"]}; {DURATIONS[i]}ms.' for i,p in enumerate(POSES))
    suffix = f'''

PROJECT PRIMARY2 SPECIFICATION (derived from the request's {request['states'][STATE]['frames']} frames; all target coordinates below are DESIGN, never measured sockets):
Reference1 is accepted canonical131 idle0, the ONLY identity, colors, asymmetry, squat proportions and short-arm scale. Reference2 actual158 Ready0 and reference3 actual159 Primary1 final frame provide ONLY the low guard entry/exit posture. They are not alternate identities and must not turn this into a copied Primary1 row. Reference4 is an ORIGINAL GRAYSCALE anatomy/motion diagram only; reference5 is the STANDARD slot count/layout only. Neither guide is a final palette, helmet shape or technical mark to paint. No old human,155/157 guard, old marker, old armor or old fist mask is attached.

{phase_text}

This is the SECOND accepted grounded normal attack, a COMPACT REVERSE/HORIZONTAL BACKHAND CUT. Phase0 starts from the existing low image-left waist guard. Phase1 draws the near fist INWARD below the chest, not high beside/over the helmet. Phase2/3 unfold the short near elbow/wrist/fist from the inside toward the forward image-RIGHT +X side; their future blade axes point FORWARD, not behind the player. The two active poses are below the glowing eye window, sweep at lower chest/waist level and remain visibly different from Primary1's high side load and downward diagonal cut. Do not fake a reverse swing by rotating an invisible future sword while keeping one static vertical mitten. Phase4 folds the short elbow back; phase5 returns to the low158 guard for stopping or later chaining. No extra automatic strike, spin, jump, lunge, stretched reach, or camera/body-facing reversal.

ANATOMY: exactly one short upper arm, true elbow, forearm, continuous cuff/wrist and ONE closed brown gripping near fist; wrist-to-grip belongs to the palm, not an extra forearm. Keep canonical131 natural short anatomy ahead of design coordinates; shorten/reposition a target rather than stretch a limb/torso or lower the shoulder. Four curled fingers and ONE separately outlined opposable thumb visible on the camera-facing glove surface must grip an INVISIBLE future cylinder; thumb is outside over index/middle, not a flat mitten or duplicated digit. Change hand orientation with the intended grip axis. The image-RIGHT far arm/hand remains its OWN relaxed balance limb, visibly separate from the active hand, no two-hand clasp/support, no extra limb. At phase3 its deeper contour may be partly occluded but cannot become a second near fist.

BODY ONLY: retain131's actual large crooked bell helmet/top knob, black eye window with two contained amber eyes, charcoal CLOTH shirt/trousers/belt, brown gloves and boots. The canonical helmet is identity, not permission to add armor. NO chestplate, shoulder cap, bracer, greave, shield, sword, blade, grip cylinder, wooden handle, hilt, pommel, sword trail or detached effect baked into the body. No old131 standing pose repeated six times; no exact local copy, mirrored clone or static bob as attack motion. Original head proportions/colors and native3/4RIGHT camera remain fixed, with only slight grounded torso weight transfer. Keep the body standing-equivalent416px in512 with knob/sole inside the48px safe border and design baseline464; extraction will use one shared row scale, never per-frame size normalization. Later body remains at most72px; no enlarged hero.

OUTPUT: a single horizontal row of exactly{request['states'][STATE]['frames']} separate complete full bodies, in this order, opaque flat GREEN #00FF00 with generous green gaps. No slot borders/labels/numbers/axis/arrows, gray diagram recolor, floor/shadow/scenery/UI/checkerboard, rim light, smoke, slash arc or glow except the two contained eyes. Target durations75/75/60/60/135/135ms are numeric playback intent only and must not be printed. New actual grip/thumb/root/helmet clearance, 159→new entry and new→158 exit, temporal motion and future armor fit will be checked AFTER native generation and deterministic extraction; none is accepted by this prompt.
'''
    prompt_path.write_text(standard_prompt+suffix,encoding='utf-8',newline='\n')
    refs = [('sole_identity_accepted_canonical131_idle',RUN/'base-source.png'),('actual158_low_guard_motion_only',ROOT/'sources/158-ready0-motion.png'),('actual159_prior_exit_motion_only',ROOT/'sources/159-primary1-last-motion.png'),('original_grayscale_shortarm_motion_design_only',guide),('standard_slot_layout_only',RUN/f'references/layout-guides/{STATE}.png')]
    handoff = write('handoffs/primary2-native-input-v001.json',dict(schema='fairytale-sword-primary2-body-native-input-v1',created_local=datetime.now().astimezone().isoformat(),generation_ready=False,root_review_required_before_generation=True,rows=[dict(component='SwordPrimary2Body',state=STATE,run_dir=RUN.as_posix(),raw_output_path=(RUN/'raw'/f'{STATE}.png').as_posix(),request=fact(request_path),prompt=fact(prompt_path),reference_images_in_order=[dict(role=role,file=fact(path)) for role,path in refs],reference_count=len(refs),frame_count=6,durations_ms=DURATIONS,loop=False,source_canvas_px=[512,512],source_native_facing=1,source_root_design_px=[256,464],fixed_display_canvas=72*512/416,shared_row_scale=True,target_mounts_are_measured=False,target_mounts=pose_records,numeric_contract=fact(contract),source_retention_proof=fact(ROOT/'source-retention-proof-v001.json'),standard_prepare_command=argv,standard_prepare_exit_code=result.returncode,actual_raw_sha256=None,actual_new_mounts=None,new_derived_images_viewed=False,generated=False,extracted=False,imported=False)],formal_complete_units=0))
    write('qa-notes.md','Preparation only. Existing source images were checked against E048/E141/E149 before view. New layout/motion diagrams have NOT been viewed and await root retention/review. Canonical131 alone owns identity. Root confirmed Stage1 75/75/60/60/135/135ms and inside-to-forward +X compact reverse horizontal sweep. All new anchors/axes/segment lengths are projected DESIGN, not measured joints or accepted sword clearance. Standard prepare uses integer nominal fps10 and drops explicit durations; original standard output is retained, then the new request explicitly stores nonuniform durations. A later standard fps-only preview may be600ms/100ms frames; it cannot certify540ms or these unequal phases and must be reported honestly without local retime. Actual kernel phase deadlines remain runtime authority. No native generation/extraction/import/runtime/media or complete unit acceptance.\n')
    paths = sorted(p for p in ROOT.rglob('*') if p.is_file())
    freeze = write('preparation-freeze-v001.json',dict(schema='fairytale-sword-primary2-preparation-freeze-v1',created_local=datetime.now().astimezone().isoformat(),file_count=len(paths),total_bytes=sum(p.stat().st_size for p in paths),files=[fact(p) for p in paths],external_source_refs=provenance,reference_count=5,generation_ready=False,new_derived_images_viewed=False,generated=False,extracted=False,imported=False,formal_complete_units=0))
    print(json.dumps(dict(freeze=fact(freeze),handoff=fact(handoff),contract=fact(contract),prompt=fact(prompt_path),guide=fact(guide),files_frozen=len(paths),bytes_frozen=sum(p.stat().st_size for p in paths),new_derived_images_viewed=False),ensure_ascii=False))


if __name__ == '__main__':
    main()
