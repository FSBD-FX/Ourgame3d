"""Prepare three isolated leather Walk6 rows. No generation or runtime acceptance."""
from pathlib import Path
from PIL import Image
import datetime, hashlib, json, shutil, subprocess

R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-lgt-readability-v003'; O=B/'walk-leather-input-v001'
assert not O.exists(); O.mkdir()
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
def desc(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,x):
    assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

body=[R/f'source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated/frame-{i}.png' for i in range(6)]
body_pins=[desc(p) for p in body]
guide=Image.new('RGBA',(6*288,146),(0,0,0,0))
for i,p in enumerate(body):
    with Image.open(p) as im:
        assert im.mode=='RGBA' and im.size==(512,512)
        # Exact source pixels of torso/shoulder motion. No head/boots or resampling.
        guide.paste(im.crop((117,210,405,356)),(i*288,0))
guide_path=O/'walk-torso-six-source-pixel-motion-guide.png';guide.save(guide_path)
rows=[]
specs=[('Chest','Chest',184,'chest184-extraction-v001/run-shared-diagnostic-v001/frames/leather_chest_sword_ready/frame-0.png',(90,90)),
       ('NearShoulder','ShoulderNear',186,'near186-extraction-v001/run-shared-diagnostic-v001/frames/leather_nearshoulder_sword_ready/frame-0.png',(60,44)),
       ('FarShoulder','ShoulderFar',187,'far187-extraction-v001/run-shared-smallcomponent-v002/frames/leather_farshoulder_sword_ready/frame-0.png',(32,30))]
for component,runtime,number,anchor,widths in specs:
    anchor=B/anchor; state=f'leather_{component.lower()}_sword_walk'; run=O/f'run-{component.lower()}-walk-v001'
    request=dict(version=1,kind='sprite-gen-request',engine='component-row',character=dict(id=f'fairytale-leather-{component.lower()}-walk-v001',description=f'Only isolated {component} of the locked Ready{number} leather identity during the actual six Walk poses.'),cell=dict(shape='square',size=512,width=512,height=512,safe_margin_x=(512-widths[0])//2,safe_margin_y=(512-widths[1])//2),chroma_key=dict(name='green',hex='#00FF00',rgb=[0,255,0],selection='manual'),states={state:dict(frames=6,fps=1000/83,loop=True,action='Six cyclic walk component perspectives matching actual body motion, not repeated idle parts.',durations_ms=[83]*6)},style=f'Only Ready{number} component is appearance identity. Walk source torso strip is geometry/motion only.',fit=dict(pixel_unfake=False,resample='lanczos',align_x='bbox-center',align_y='bottom',ground_frames=False,segmentation='components',shared_row_scale=True),chroma=dict(mode='rgb',unmix_reach=4,spill_max_fraction=.005))
    req=O/'requests'/f'{component.lower()}-walk-request-v001.json';write(req,request)
    result=subprocess.run([str(SG/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id',request['character']['id'],'--base-image',str(anchor),'--request',str(req)],cwd=R,capture_output=True,text=True,encoding='utf-8')
    (O/f'prepare-{component.lower()}-v001.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
    prepared=json.loads((run/'sprite-request.json').read_text(encoding='utf-8-sig'));assert prepared['states'][state]['frames']==6 and prepared['fit']['shared_row_scale']
    identity=run/'base-source.png';assert identity.read_bytes()==anchor.read_bytes()
    motion=run/'references/walk-torso-motion-guide.png';shutil.copy2(guide_path,motion)
    shape={'Chest':'waist-length supple brown leather jerkin, round golden clasp, belt and small pouch. Preserve the physical pouch side and the two armholes; no arm or shoulder caps',
           'NearShoulder':'short rounded foreground brown leather shoulder cap only. No torso, chest, lining, low hanging ring or far shoulder',
           'FarShoulder':'tiny narrow curved FAR brown leather tab only, with compressed far perspective. No broad near cap, torso seam, lining or ring'}[component]
    prompt=(f'Image1 is the isolated Ready{number} {component}, the SOLE appearance/identity reference. Image2 contains six actual walk torso crops left-to-right, ONLY motion and camera geometry; do not copy its grey clothing or hands.\n\n'
            f'Draw ONLY the {shape} of image1, across exactly {prepared["states"][state]["frames"]} separated components in ONE horizontal row. Follow the six torso/shoulder perspectives and mild walking bob/twist from image2 in that order. All remain the same right-facing construction; foreshorten without flipping. Keep warm brown/tan leather, coarse ink outline and simple large shapes. Preserve component identity through the loop; no duplicate idle stickers.\n\n'
            'Flat OPAQUE GREEN #00FF00 background. No full person, head, helmet, eyes, skin, limbs, hands, sword, boots, shadows, ground, text, numbers, frame borders or other equipment. Draw no body under the component.\n\n'
            f'Numeric recipe: six source phases, [83,83,83,83,83,83]ms source preview loop; later one SHARED row scale into {widths[0]}x{widths[1]}px fit windows in512 cells. No per-frame scaling. Actual mounts/stride/foot lock and game animation remain unaccepted.\n')
    prompt_path=run/'prompts'/f'{state}.txt';prompt_path.write_text(prompt,encoding='utf-8')
    rows.append(dict(component=component,runtime_component=runtime,state=state,clip='sword_walk',run_dir=run.as_posix(),raw_output_path=(run/'raw'/f'{state}.png').as_posix(),prompt=desc(prompt_path),request=desc(run/'sprite-request.json'),reference_images_in_order=[dict(role='FIRST_isolated_Ready_sole_appearance_identity',file=desc(identity)),dict(role='SECOND_actual_Walk6_torso_crops_motion_only_not_appearance',file=desc(motion))],actual_runtime_body_pins=body_pins,standard_prepare_exit_code=0,frame_count=6,durations_ms=[83]*6,fit_window_design_px=list(widths),shared_row_scale=True,generation_ready=False,target_mounts_are_measured=False,future_component_A=[None]*6,future_body_target_B=[None]*6,future_integer_delta=[None]*6))
write(O/'walk-leather-native-input-draft-v001.json',dict(schema='walk-three-leather-component-native-input-v001',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_event='EV-048',rows=rows,generation_ready=False,root_review_required_before_generation=True,body_motion_guide_crop_xyxy=[117,210,405,356],near_hand_correction_separate=True,formal_complete_units=0))
print(json.dumps(dict(prepared=3,body_sources_verified=6,guide=desc(guide_path),draft=desc(O/'walk-leather-native-input-draft-v001.json'),generation=False),ensure_ascii=False))
