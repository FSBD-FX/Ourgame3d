"""Short-arm single-hand Primary1 from actual158 guard; preparation only, no generation/UE."""
from pathlib import Path
import datetime,hashlib,html,json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
C=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
READY=R/'run-ready-v002/curated/frame-0.png';run=R/'run-primary1-v003';assert not run.exists()
state='sword_primary_1';dur=[85,85,60,60,155,155]
poses=[
 {'phase':'anticipation1 actual low Ready','shoulder':[205,248],'elbow':[181,281],'wrist':[191,300],'grip':[212,313],'axis':[.94,-.341],'hip':[0,0]},
 {'phase':'anticipation2 short left load','shoulder':[205,248],'elbow':[166,258],'wrist':[144,232],'grip':[140,210],'axis':[-.2,-.98],'hip':[-2,0]},
 {'phase':'cut1 below face forward','shoulder':[208,249],'elbow':[235,278],'wrist':[267,291],'grip':[291,300],'axis':[.95,.31],'hip':[3,1]},
 {'phase':'cut2 compact low followthrough','shoulder':[208,250],'elbow':[218,290],'wrist':[254,317],'grip':[275,328],'axis':[.95,.31],'hip':[4,2]},
 {'phase':'recovery1 compact return','shoulder':[206,248],'elbow':[187,283],'wrist':[211,315],'grip':[232,327],'axis':[.99,.15],'hip':[1,0]},
 {'phase':'recovery2 actual low Ready','shoulder':[205,248],'elbow':[181,281],'wrist':[191,300],'grip':[212,313],'axis':[.94,-.341],'hip':[0,0]}]
for i,p in enumerate(poses):p.update(frame=i,duration_ms=dur[i],far_hand=[340,342])
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,x):
 p=R/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
assert desc(READY)['sha256']=='d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
contract={'schema':'fairytale-shortarm-primary1-design-v3','component':'SwordPrimary1','state':state,'frame_count':6,'durations_ms':dur,'loop':False,
 'poses':poses,'coordinates_measured':False,'axis_direction_role':'Explicit future blade alignment design only. An invisible cylinder/blade sign is not a body-only measurement.',
 'source_root_display_design_px':[256,464],'source_canvas_px':[512,512],'standing_equivalent_height_px':416,'fixed_display_canvas':72*512/416,
 'actual_guard_measurement_source':desc(R/'ready-measurement-v002/ready-marker-proposal-v002.json'),
 'bone_lengths_are_projected_design_not_true_skeleton':True,
 'segment_design_lengths':[{'frame':i,'upper':math.dist(p['shoulder'],p['elbow']),'forearm':math.dist(p['elbow'],p['wrist']),'palm_offset':math.dist(p['wrist'],p['grip'])} for i,p in enumerate(poses)],
 'actual_grip_axis_roots_after_native':None,'actual_helmet_hand_weapon_clearance_px':None,'generated':False,'formal_complete_units':0}
cp=write('primary1-design-contract-v003.json',contract)
action='Six connected short-arm ONE-HANDED sword BODY-ONLY poses from actual158 low-left-waist guard: lowReady, left-of-helmet load, below-face forward diagonal cut, compact low followthrough, compact return, exact lowReady. Far hand stays separate at far waist.'
seed={'states':{state:{'frames':6,'fps':10,'loop':False,'action':action}},'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
 'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
sp=write('requests/primary1-numeric-input-v003.json',seed)
argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','fairytale-common-hero-sword-primary1-v003','--base-image',str(C),
 '--description',action,'--style','EXACT canonical131 squat grotesque bell-helmet identity, short limbs, dark cloth/brown gloves and boots, fixed3/4right. Body-only no armor or blade.','--cell-size','512','--chroma-key','#00FF00','--request',str(sp)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/prepare-primary1-v003.log',result.stdout+result.stderr);assert result.returncode==0
qp=run/'sprite-request.json';q=json.loads(qp.read_text(encoding='utf-8'));write('requests/primary1-standard-before-explicit-fields-v003.json',q)
q['fit'].update(seed['fit']);q['states'][state]['durations_ms']=dur;q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert (run/'base-source.png').read_bytes()==C.read_bytes()

# Original grayscale diagram only. It contains no copied131/158 raster pixels.
im=Image.new('RGB',(3072,512),'#eeeeee');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="3072" height="512"><rect width="100%" height="100%" fill="#eeeeee"/>']
for i,p in enumerate(poses):
 ox=i*512;hx,hy=p['hip'];fx,fy=p['far_hand']
 def poly(points,fill,outline='#222222',width=2):
  pp=[(ox+x,y) for x,y in points];d.polygon(pp,fill=fill,outline=outline,width=width)
  svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
 def line(points,fill,width):
  pp=[(ox+x,y) for x,y in points];d.line(pp,fill=fill,width=width,joint='curve')
  svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round"/>')
 line([[291+hx*.3,250+hy*.3],[314,302],[fx,fy-13]],'#888888',22)
 poly([(fx-10,fy-18),(fx+8,fy-17),(fx+13,fy-5),(fx+10,fy+13),(fx+3,fy+17),(fx,fy+5),(fx-4,fy+14),(fx-9,fy+11),(fx-6,fy-2),(fx-12,fy-7)],'#bbbbbb')
 poly([(207+hx,239+hy),(284+hx,241+hy),(302+hx,308+hy),(281+hx,339),(234+hx,337),(205+hx,302+hy)],'#777777')
 line([[237+hx,335],[213+hx*.3,377],[194,425]],'#777777',34);line([[279+hx,335],[290+hx*.3,377],[303,423]],'#777777',30)
 poly([(174,420),(211,420),(218,447),(223,464),(151,464),(156,445)],'#aaaaaa')
 poly([(283,420),(319,420),(325,443),(351,453),(355,460),(267,460),(272,444)],'#aaaaaa')
 poly([(173,210),(184,160),(202,126),(238,106),(282,108),(311,127),(324,156),(337,160),(337,177),(324,177),(335,226),(306,236),(250,229),(205,220)],'#bbbbbb')
 poly([(242,86),(269,86),(276,107),(243,107)],'#bbbbbb');poly([(230,66),(251,48),(273,76),(246,86)],'#bbbbbb')
 line([p['shoulder'],p['elbow'],p['wrist']],'#666666',29)
 gx,gy=p['grip'];ax,ay=p['axis'];n=math.hypot(ax,ay);ax/=n;ay/=n;ux,uy=-ay,ax
 def hand(points):return [(gx+u*ux+v*ax,gy+u*uy+v*ay) for u,v in points]
 line([p['wrist'],p['grip']],'#999999',22)
 poly(hand([[-18,-14],[-18,11],[-9,19],[11,18],[19,10],[20,-10],[10,-18],[-9,-19]]),'#aaaaaa')
 for v in [-9,-1,7]:line(hand([[-8,v],[16,v]]),'#333333',2)
 poly(hand([[-5,15],[2,20],[16,11],[12,4],[5,5]]),'#bbbbbb',width=2)
 texts=[f'f{i} / {p["phase"]} / {dur[i]}ms','SHORT linked shoulder > elbow > wrist > palm; FAR stays down','GRAY DIAGRAM ONLY. Final has no labels/gray recolor/sword/FX.']
 for yy,t in zip([12,30,480],texts):d.text((ox+12,yy),t,fill='#111111',font=font);svg.append(f'<text x="{ox+12}" y="{yy+12}" font-size="12">{html.escape(t)}</text>')
svg.append('</svg>');write('guides/primary1-anatomical-motion-v003.svg','\n'.join(svg)+'\n');gp=R/'guides/primary1-anatomical-motion-v003.png';im.save(gp)
phase='\n'.join(f'{i}: {p["phase"]}. near shoulder{p["shoulder"]} -> elbow{p["elbow"]} -> wrist{p["wrist"]} -> single fist/grip{p["grip"]}, planned invisible-axis{p["axis"]}; relaxed far hand{p["far_hand"]}; {dur[i]}ms.' for i,p in enumerate(poses))
prompt=f'''Create ONE horizontal production component row of exactly SIX distinct complete FULL-BODY poses for canonical131's ONE-HANDED military-sword Primary1. BODY ONLY; no sword or visible handle.

REFERENCE OWNERSHIP: image1 canonical131idle0 is the ONLY identity, squat proportions, short-arm scale, bell-helmet construction and original palette. Image2 is actual native158 lowReady frame0 used ONLY for the guard/near-hand/far-hand posture at0/5, never a new identity. Image3 is original GRAYSCALE anatomy/motion guidance ONLY, not a final palette or head design. Image4 is standard6slot count/layout ONLY. No old155/157 near-face guard or failed156 is attached.

EXACT SIX-PHASE DESIGN (planned source-space points, never measured future sockets):
{phase}

0 and5 must visibly match image2's ACTUAL compact low near fist at the image-LEFT waist, around[212,313], with the separate far hand relaxed down. Do not return to an upright across-chest fist or the former planned275315 guard that158 did not draw. 1 loads only the short near arm to the LEFT of the helmet, keeping the fist and invisible future blade off the eye/face area; no arm stretched over the forehead, no two-handed overhead clasp. 2 cuts forward across BELOW the face/chin at chest/waist height with a single near hand, never across the glowing eye window. 3 continues down in a COMPACT followthrough, not a long forward reach or enormous lunge. 4 returns through a short folded arm to5's actual guard. The poseguide is subordinate to canonical131 natural anatomy; if a target would stretch a bone, shorten/reposition the pose without changing body/helmet proportions.

ANATOMY CRITICAL: the larger front/near arm starts at image-LEFT shoulder and has exactly one short upper arm, one true elbow, one forearm, a continuous cuff/wrist and ONE closed brown gripping fist. The wrist-to-grip segment belongs to the palm, not extra forearm. Retain canonical131's short limbs and body volume: do not lengthen an upper arm/forearm, lower the shoulder or stretch the torso/head to reach a point. Wrist and hand orientation must change with the implied grip axis; do not keep one upright fist while only a future blade rotates. The original four curled fingers and ONE distinctly outlined opposable thumb cross the index/middle area on the camera-facing glove surface. No flat mitten, open claw, omitted thumb, extra finger, separate cuff or disconnected hand. The invisible cylinder/blade-end direction is a design aid only: NO rod/wood handle/cylinder/pommel/guard/blade is painted into this BODY.

FAR HAND: its smaller image-RIGHT/back shoulder leads to its own relaxed hanging hand beside the far waist, visibly separated in ALL six frames; never clasp/support the active near hand. Keep its open hanging fingers independent and above boots. Aim for clear contour separation rather than trusting center distance; no technical gap marks in final. Arm overlap must make the front near path and deeper far path readable, not invent a third limb.

IDENTITY/CAMERA: exact canonical131 squat crooked bell-helmet/top knob, rigid shell, two amber eyes contained in black slit, original dark cloth shirt/trousers/belt and brown gloves/boots. Fixed native RIGHT-facing3/4camera, no human body/style switch, head/neck twist or altered helmet silhouette. Slight grounded weight transfer can support a cut without shrinking/enlarging frames; keep boots planted except actual controlled weight shift. Standing-equivalent416px on512source, design ground464, one shared native/extraction scale. Body stays max72px on1280x720 later; no per-frame fit or enlarged hero. No armor plates/caps/bracers/greaves/shield baked in.

OUTPUT: exactly six connected complete full bodies on flat opaque GREEN #00FF00, generous green gaps, no cropping from knob to soles. Original hand-inked outline/opaque materials. No blade/weapon/handle, slash trail, sparks, smoke, body rim lighting or blue/purple glow, technical gray limb recolor/labels/arrows/axis/numbers, floor/shadow/UI/checkerboard or alternative camera. Only the two contained amber eyes glow. Six genuinely drawn poses, no copy/mirror/static bob substitutes. Source timing85/85/60/60/155/155ms; never print it. Final actual grip/axis/thumb/root/helmet clearance and motion will be measured after extraction, not asserted from this plan. Other stages/air/armor/effects are separate; this image cannot certify a complete unit.
'''
pp=write('prompts/primary1-body-only-v003.txt',prompt)
refs=[('sole_identity131',C),('actual158_low_ready_guard_motion_only',READY),('original_grayscale_short_arm_motion_only',gp),('standard_component_count_layout',run/f'references/layout-guides/{state}.png')]
row={'component':'SwordPrimary1','state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),'prompt':desc(pp),
 'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],'frame_count':6,'durations_ms':dur,'loop':False,'fit_window_px':[416,416],
 'target_mounts':[{'frame':i,'A':p['grip'],'grip_design_px':p['grip'],'near_wrist_design_px':p['wrist'],'grip_axis_design_xy':p['axis'],'far_hand_design_px':p['far_hand'],'source_root_design_px':[256,464],'meaning':'Authoring pose design, not measured hidden bone/handle/blade/clearance.'} for i,p in enumerate(poses)],
 'source_native_facing':1,'source_canvas_px':[512,512],'source_root_design_px':[256,464],'shared_row_scale':True,'target_mounts_are_measured':False,
 'numeric_design_contract':desc(cp),'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode,
 'combat_phase_contract':{'weapon':'WPN-SWD-001','stage_zero_based':0,'windup_ms':170,'lock_ms':68,'active_ms':120,'recovery_ms':310,'base_boundaries_ms':[0,85,170,230,290,445,600],'runtime_sampler':'Existing GetPrimaryPoseFrame on accepted actual phase deadlines; no hard time or ActionSpeed override.'},
 'new_guides_viewed':False,'generated':False,'actual_raw_sha256':None,'formal_complete_units':0}
hp=write('handoffs/primary1-native-input-v003.json',{'schema':'fairytale-sword-body-native-input-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'rows':[row]})
files=sorted(p for p in R.rglob('*') if p.is_file() and 'primary1' in p.relative_to(R).as_posix() and 'v003' in p.relative_to(R).as_posix())
fp=write('preparation-freeze-primary1-v003.json',{'schema':'fairytale-sword-body-input-freeze-v1','file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],'reference_count':4,'new_media_viewed':False,'generated':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(hp),'prompt':desc(pp),'freeze':desc(fp),'guide':desc(gp),'source_contract':desc(cp)},ensure_ascii=False))
