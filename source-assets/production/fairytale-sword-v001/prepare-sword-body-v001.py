"""Prepare original motion diagrams and standard body-only requests; no generation/Unreal."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002')
parser=argparse.ArgumentParser();parser.add_argument('--component',choices=['ready','primary1'],required=True)
key=parser.parse_args().component;now=datetime.datetime.now().astimezone().isoformat()
ready=[]
for i,dy in enumerate([0,-1,1,0]):
 ready.append(dict(phase=f'ready{i}',shoulder=[215,250+dy],elbow=[232,289+dy],grip=[282,306+dy],far_elbow=[314,293+dy],far_hand=[333,339+dy],hip_shift=[0,0],axis=[.70,-.70]))
primary=[
 dict(phase='anticipation1 gather',shoulder=[214,250],elbow=[193,282],grip=[234,288],far_elbow=[312,286],far_hand=[321,333],hip_shift=[-2,0],axis=[-.65,-.76]),
 dict(phase='anticipation2 loaded',shoulder=[210,247],elbow=[176,242],grip=[160,191],far_elbow=[321,284],far_hand=[326,322],hip_shift=[-4,0],axis=[-.45,-.89]),
 dict(phase='cut1 forward crossing',shoulder=[224,250],elbow=[265,264],grip=[318,280],far_elbow=[309,292],far_hand=[292,328],hip_shift=[8,3],axis=[.80,.60]),
 dict(phase='cut2 low followthrough',shoulder=[225,250],elbow=[269,305],grip=[314,351],far_elbow=[295,301],far_hand=[272,329],hip_shift=[10,5],axis=[.80,.60]),
 dict(phase='recovery1 decelerate',shoulder=[218,250],elbow=[252,300],grip=[290,334],far_elbow=[314,293],far_hand=[328,335],hip_shift=[4,1],axis=[.70,-.70]),
 dict(phase='recovery2 to ready',shoulder=[215,250],elbow=[232,289],grip=[282,306],far_elbow=[314,293],far_hand=[333,339],hip_shift=[0,0],axis=[.70,-.70])]
poses=ready if key=='ready' else primary;count=len(poses);component='SwordReady' if key=='ready' else 'SwordPrimary1'
state='sword_ready_idle' if key=='ready' else 'sword_primary_1';durations=[167]*4 if key=='ready' else [85,85,60,60,155,155]
run=ROOT/f'run-{key}-v001';assert not run.exists()
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=ROOT/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
action=(f'Exactly{count} separate complete canonical131 BODY-ONLY poses. Larger image-LEFT near arm owns a closed cylindrical sword-grip fist; actual sword is omitted. '
        +('Four subtle ready breaths, identical guard and rigid helmet, loop to first.' if key=='ready' else 'Six nonloop poses in order: gather, loaded anticipation, forward diagonal cut, low followthrough, deceleration, return to ready; two frames per real combat phase.'))
seed={'states':{state:{'frames':count,'fps':6 if key=='ready' else 10,'loop':key=='ready','action':action}},
 'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
 'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
seed_path=write(f'requests/{key}-numeric-input-v001.json',seed)
argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),
 '--character-id',f'fairytale-common-hero-sword-{key}-v001','--base-image',str(CANON/'curated/frame-0.png'),
 '--description',action,'--style','EXACT canonical131 grotesque hand-inked dark-fairytale bell helmet, dark cloth, brown leather hands/boots; no armor plates or realistic human identity.',
 '--cell-size','512','--chroma-key','#00FF00','--request',str(seed_path)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write(f'logs/prepare-{key}-v001.log',result.stdout+result.stderr);assert result.returncode==0
request_path=run/'sprite-request.json';request=json.loads(request_path.read_text(encoding='utf-8'));write(f'requests/{key}-standard-prepare-before-explicit-fields.json',request)
request['fit'].update(seed['fit']);request['states'][state]['durations_ms']=durations;request['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert (run/'base-source.png').read_bytes()==(CANON/'curated/frame-0.png').read_bytes()

# New anatomical schematic only; no original raster copied/painted into the guide.
im=Image.new('RGB',(count*512,512),'#f4f6f8');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="'+str(count*512)+'" height="512" viewBox="0 0 '+str(count*512)+' 512"><rect width="100%" height="100%" fill="#f4f6f8"/>']
for i,p in enumerate(poses):
 ox=i*512
 def pts(values):return [(ox+x,y) for x,y in values]
 def line(values,color,width):
  pp=pts(values);d.line(pp,fill=color,width=width,joint='curve');svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pp)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
 def poly(values,color,outline='#334155',width=2):
  pp=pts(values);d.polygon(pp,fill=color,outline=outline,width=width);svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pp)+f'" fill="{color}" stroke="{outline}" stroke-width="{width}"/>')
 d.rectangle((ox+8,8,ox+504,504),outline='#94a3b8',width=1)
 d.text((ox+14,14),f'{component} f{i} /{p["phase"]}',fill='#172554',font=font)
 d.text((ox+14,35),f'{durations[i]}ms  BODY ONLY / near=blue, far=orange',fill='#172554',font=font)
 # Explicit fixed original character depth; the schematic is NOT a new identity.
 hx,hy=p['hip_shift'];far_shoulder=[300+hx*.3,250+hy*.3]
 line([far_shoulder,p['far_elbow'],p['far_hand']],'#d49b58',22)
 poly([(219+hx,242+hy),(291+hx,244+hy),(301+hx,310+hy),(280+hx,339+hy),(238+hx,337+hy),(215+hx,307+hy)],'#6b7280')
 line([[239+hx,335+hy],[217+hx*.3,377+hy*.3],[201,423]],'#6b7280',33)
 line([[279+hx,335+hy],[291+hx*.3,377+hy*.3],[303,423]],'#626977',29)
 poly([(183,420),(221,420),(226,453),(233,464),(169,464),(174,451)],'#a77953')
 poly([(285,420),(321,420),(326,447),(352,457),(350,464),(270,464),(274,448)],'#a77953')
 poly([(185,210),(193,163),(210,127),(244,106),(285,108),(313,127),(326,157),(339,161),(338,178),(325,178),(337,226),(306,236),(251,229),(211,221)],'#c0b7a5')
 poly([(246,87),(272,87),(279,106),(246,106)],'#c0b7a5');poly([(238,67),(260,48),(278,76),(250,86)],'#c0b7a5')
 line([p['shoulder'],p['elbow'],p['grip']],'#729fbd',28)
 # Closed fist: four curled digits and one opposable thumb on camera-facing side.
 gx,gy=p['grip'];poly([(gx-18,gy-15),(gx+10,gy-18),(gx+20,gy-6),(gx+17,gy+12),(gx+4,gy+18),(gx-17,gy+12)],'#ae805a')
 for dy in [-7,0,7]:line([[gx-14,gy+dy],[gx+3,gy+dy+2]],'#61452f',2)
 poly([(gx+9,gy-13),(gx+20,gy-6),(gx+7,gy+7),(gx,gy+3)],'#bd9168',width=1)
 fx,fy=p['far_hand'];poly([(fx-10,fy-13),(fx+9,fy-11),(fx+12,fy+12),(fx-7,fy+16)],'#b58c66')
 # Dashed short grip-axis marks, NOT a painted cylinder, sword, blade or socket fact.
 ax,ay=p['axis']
 for j in [-3,-2,2,3]:line([[gx+ax*j*7,gy+ay*j*7],[gx+ax*(j+.45)*7,gy+ay*(j+.45)*7]],'#0284c7',2)
 d.ellipse((ox+gx-3,gy-3,ox+gx+3,gy+3),fill='#dc2626')
 d.text((ox+14,477),'A=planned palm grip only; no sword/marks in output',fill='#172554',font=font)
 svg.append(f'<text x="{ox+14}" y="29" font-size="14">{component} f{i} / {p["phase"]}</text>')
 svg.append(f'<text x="{ox+14}" y="49" font-size="14">{durations[i]}ms BODY ONLY; near blue/far orange</text>')
 svg.append(f'<circle cx="{ox+gx}" cy="{gy}" r="3" fill="#dc2626"/>')
 svg.append(f'<text x="{ox+14}" y="491" font-size="14">A=planned palm grip only; no sword/marks in output</text>')
svg.append('</svg>');write(f'guides/{key}-anatomical-motion-v001.svg','\n'.join(svg)+'\n')
guide=ROOT/f'guides/{key}-anatomical-motion-v001.png';guide.parent.mkdir(parents=True,exist_ok=True);im.save(guide)

phase_text=('Four READY-IDLE bodies, same sword-ready closed near-hand guard throughout; tiny actual torso breathing only, helmet rigid, feet planted and4->0 seamless. Near shoulder is image-LEFT and in front; near forearm bends across the chest toward image-RIGHT, ending in a correctly closed grip fist in front of the lower chest. Far hand remains separate and relaxed/counterbalancing, never also grabbing a blade.' if key=='ready' else
 'Six NONLOOP bodies.0 gather from ready,1 fully loaded anticipation at image-LEFT of helmet,2 strong forward diagonal cut across chest toward image-RIGHT,3 low forward followthrough,4 decelerating return,5 matches the ready guard. Exactly2anticipation/2cut/2recover, with visible shoulder/elbow/wrist changes and weight transfer through planted legs. Do not substitute static bobbing or a mirrored pose. Keep the near shoulder/arm anatomically in front even when its hand crosses to image-RIGHT; do not turn it into the smaller far arm. Keep hands clear of the glowing eye opening and preserve the same fixed3/4right camera; never switch to a back/side/front orthographic view.')
prompt=f'''Create ONE horizontal production component-row with exactly{count} separate FULL-BODY canonical131 characters, BODY ONLY, for{component}. This is the new existing hero's real sword-body state, not a new identity or an assembled weapon sheet.

REFERENCE OWNERSHIP:131idle0 is the ONLY appearance/proportion/identity authority.131fouridle contact gives original body volume, rigid bell-helmet construction and source colors only; it does NOT override the NEW arm/hand action. Original anatomical guide gives phase order, near/far depth and grip-hand placement, not final colors or a new character. Standard{count}slot guide gives count/layout. No old human body, realistic knight, armor reference or baked sword identity is attached.

ACTION: {phase_text}

HANDS, CRITICAL: the larger near arm starts at image-LEFT/front shoulder, with a real elbow and forearm joining the near hand continuously. That near brown leather hand forms a CLOSED CYLINDRICAL GRIP around an INVISIBLE future sword handle: four fingers curl around the cylinder with correct creases, and ONE opposable thumb lies across the index/middle side on the camera-facing surface. Not an open C claw, pointing finger, flat mitten or extra finger. Preserve131's brown leather glove/cuff identity. The guide redA is a planned palm/grip center and short blue dashes are only an invisible grip-axis cue. Do NOT render a rod, wooden handle, cylinder, pommel, blade, guard or red/blue mark; future separate sword artwork will occupy the grip. Do not leave an oversized empty hole; the closed fist must have credible finger/thumb overlap. Far hand has its own natural opposing thumb anatomy and never duplicates the near hand.

IDENTITY: EXACT same squat bell helmet, crooked top knob, black face opening with two amber eyes, dark cloth shirt/trousers, original belt and brown gloves/boots as131. Helmet shell and body volume stay rigid through motion; no stretching a neck/helmet, tall human anatomy, missing limbs or extra joints. No chestplate, shoulder caps, bracers, greaves or any armor plate baked into the body. Keep the same three-quarter native RIGHT-facing view. Maintain body standing-equivalent height416px on512source canvas, floor at source464 as a design guide; crouch/torso rotation is actual pose, not per-frame rescaling. Hands stay within the body strip; no blade/swoosh expands the bbox. One common native drawing scale across the row; later extraction uses ONE shared ratio, never individual normalized frame fitting. The final actual feet/grip/axis will be measured, not assumed from this diagram.

OUTPUT: exactly{count} full-body connected silhouettes on one row, generous green gaps, complete head-knob through boots, no cropping. Flat opaque GREEN #00FF00 background, opaque body interiors and clean hand-inked edges. Render only real body pixels. No sword/weapon/wood rod/shield, armor pieces, slash trail, smoke, glow outside the two eye shapes, sparks, floor/shadow, UI, technical colors/axis/labels/numbers/checkerboard or alternative views. Do not paste one body{count}times, mirror it to invent attacks or locally repaint an old body. Source timing is {durations}ms, but never print it in the artwork.

BOUNDARY: this only prepares the requested sword body row. Real sword is a separate existing component; new palm/axis and original hand-pixel occlusion must be measured after extraction. Old V007 grip/root472/hand polygon and XBW sockets do not apply. Other attacks, movement, armor combinations, effects and audio remain separate work; no complete-unit or motion acceptance is implied.
'''
prompt_path=write(f'prompts/{key}-body-only-v001.txt',prompt)
refs=[('sole_identity',CANON/'curated/frame-0.png'),('original131_body_proportions_only_not_new_action',CANON/'qa/idle-contact.png'),
 ('original_anatomical_action_guide_only',guide),('standard_component_count_layout',run/f'references/layout-guides/{state}.png')]
target_mounts=[{'frame':i,'A':p['grip'],'grip_design_px':p['grip'],'grip_axis_design_xy':p['axis'],
 'source_root_design_px':[256,464],'meaning':'Unmeasured planned source pose/grip/root only; real source feet/palm/thumb/axis must be measured after native output.'} for i,p in enumerate(poses)]
entry={'component':component,'state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),
 'prompt':desc(prompt_path),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],
 'fit_window_px':[416,416],'target_mounts':target_mounts,'frame_count':count,'durations_ms':durations,'loop':key=='ready',
 'source_native_facing':1,'shared_row_scale':True,'standing_equivalent_body_height_px':416,'body_canvas_px':[512,512],
 'source_root_design_px':[256,464],'target_mounts_are_measured':False,'new_guides_viewed':False,'generated':False,
 'actual_raw_sha256':None,'formal_complete_units':0,'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode,
 'combat_phase_contract':None if key=='ready' else {'weapon':'WPN-SWD-001','stage_zero_based':0,'windup_ms':170,'lock_ms':68,'active_ms':120,'recovery_ms':310,'base_boundaries_ms':[0,85,170,230,290,445,600],'runtime_sampler':'Existing ADungeonFighter::GetPrimaryPoseFrame; actual frozen Action phase times divide each phase in two, ActionSpeed applied by kernel. No hard-time override.'}}
handoff=write(f'handoffs/{key}-native-input-v001.json',{'schema':'fairytale-sword-body-native-input-v1','created_local':now,'rows':[entry]})
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and (key in p.relative_to(ROOT).as_posix() or p.name==Path(__file__).name))
freeze=write(f'preparation-freeze-{key}-v001.json',{'schema':'fairytale-sword-body-input-freeze-v1','created_local':now,
 'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],
 'reference_count':4,'new_media_viewed':False,'generated':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(handoff),'prompt':desc(prompt_path),'freeze':desc(freeze)},ensure_ascii=False))
