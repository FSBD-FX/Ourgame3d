"""New low outward Ready body preparation only; grayscale original guide, no generation/UE."""
from pathlib import Path
import datetime,hashlib,json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
C=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
run=R/'run-ready-v002';assert not run.exists();state='sword_ready_idle'
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,x):
 p=R/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
poses=[]
for i,dy in enumerate([0,-1,1,0]):
 poses.append({'frame':i,'duration_ms':167,'near_shoulder_design_px':[205,248+dy],'near_elbow_design_px':[217,286+dy],
  'near_wrist_design_px':[255,304+dy],'near_grip_design_px':[275,315+dy],'near_handle_axis_design_xy':[.94,-.341],
  'far_hand_design_px':[345,365+dy],'source_root_display_design_px':[256,464]})
contract={'schema':'fairytale-low-outward-ready-design-v2','component':'SwordReady','state':state,'frame_count':4,'loop':True,'durations_ms':[167]*4,
 'source_native_facing':1,'source_canvas_px':[512,512],'standing_equivalent_height_px':416,'fixed_display_canvas_at1280x720':72*512/416,
 'poses':poses,'coordinates_measured':False,'shoulder_is_hidden_joint_truth':False,
 'design_reason':'Withdrawn314315 would need128px straight shoulder-to-grip reach. This lower/closer grip preserves approximately40px upper arm and42px forearm; wrist-to-grip is palm offset, not extra forearm.',
 'design_segment_lengths_px':{'upper_arm':math.dist([205,248],[217,286]),'forearm':math.dist([217,286],[255,304]),'wrist_to_grip_palm_offset':math.dist([255,304],[275,315])},
 'hand_outline_separation_design_min_px':12,'hand_outline_separation_measured_px':None,
 'future_weapon_tip_design_only_px':[275+.4*383*.94,315+.4*383*(-.341)],
 'helmet_clearance_measured_px':None,'actual_grip_axis_root':None,'thumb_accepted':False,
 'known_transition_risk':'Old157 Primary1 frames0/4/5 remain across-chest guard and have not been changed to match this new Ready. Do not claim seam acceptance by replacing Ready alone.',
 'formal_complete_units':0,'generated':False}
cp=write('ready-design-contract-v002.json',contract)
action='Exactly four distinct canonical131 BODY-ONLY low-outward single-hand Ready breaths. Short near arm bends continuously through a visible elbow/wrist into a closed brown fist below/right of chest; far relaxed hand visibly separate beside far thigh.'
seed={'states':{state:{'frames':4,'fps':6,'loop':True,'action':action}},'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
 'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
sp=write('requests/ready-numeric-input-v002.json',seed)
argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','fairytale-common-hero-sword-ready-v002','--base-image',str(C),
 '--description',action,'--style','EXACT canonical131 grotesque hand-inked dark-fairytale bell helmet/dark cloth/brown gloves and boots. Same squat short-limbed identity; body-only no armor or sword.','--cell-size','512','--chroma-key','#00FF00','--request',str(sp)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/prepare-ready-v002.log',result.stdout+result.stderr);assert result.returncode==0
qp=run/'sprite-request.json';q=json.loads(qp.read_text(encoding='utf-8'));write('requests/ready-standard-before-explicit-fields-v002.json',q)
q['fit'].update(seed['fit']);q['states'][state]['durations_ms']=contract['durations_ms'];q['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert (run/'base-source.png').read_bytes()==C.read_bytes()

# Newly drawn technical geometry only; no old art is copied/repainted into this guide.
im=Image.new('RGB',(2048,512),'#eeeeee');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512"><rect width="100%" height="100%" fill="#eeeeee"/>']
for i,p in enumerate(poses):
 ox=i*512
 def poly(points,fill,outline='#222222',width=2):
  pp=[(ox+x,y) for x,y in points];d.polygon(pp,fill=fill,outline=outline,width=width)
  svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
 def line(points,fill,width):
  pp=[(ox+x,y) for x,y in points];d.line(pp,fill=fill,width=width,joint='curve')
  svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round"/>')
 dy=[0,-1,1,0][i];fx,fy=p['far_hand_design_px']
 line([[291,250+dy],[316,315+dy],[fx,fy-13]],'#888888',22)
 poly([(fx-10,fy-18),(fx+8,fy-17),(fx+13,fy-5),(fx+10,fy+13),(fx+3,fy+17),(fx,fy+5),(fx-4,fy+14),(fx-9,fy+11),(fx-6,fy-2),(fx-12,fy-7)],'#bbbbbb')
 poly([(207,239+dy),(284,241+dy),(302,308+dy),(281,339),(234,337),(205,302+dy)],'#777777')
 line([[237,335],[213,377],[194,425]],'#777777',34);line([[279,335],[290,377],[303,423]],'#777777',30)
 poly([(174,420),(211,420),(218,447),(223,464),(151,464),(156,445)],'#aaaaaa')
 poly([(283,420),(319,420),(325,443),(351,453),(355,461),(267,461),(272,444)],'#aaaaaa')
 poly([(173,210),(184,160),(202,126),(238,106),(282,108),(311,127),(324,156),(337,160),(337,177),(324,177),(335,226),(306,236),(250,229),(205,220)],'#bbbbbb')
 poly([(242,86),(269,86),(276,107),(243,107)],'#bbbbbb');poly([(230,66),(251,48),(273,76),(246,86)],'#bbbbbb')
 line([p['near_shoulder_design_px'],p['near_elbow_design_px'],p['near_wrist_design_px']],'#666666',29)
 gx,gy=p['near_grip_design_px'];ax,ay=p['near_handle_axis_design_xy'];n=math.hypot(ax,ay);ax/=n;ay/=n;ux,uy=-ay,ax
 def hand(points):return [(gx+u*ux+v*ax,gy+u*uy+v*ay) for u,v in points]
 # Real wrist continuation to palm, not a long forearm terminating at a detached fist.
 line([p['near_wrist_design_px'],[gx,gy]],'#999999',22)
 poly(hand([[-18,-14],[-18,11],[-9,19],[11,18],[19,10],[20,-10],[10,-18],[-9,-19]]),'#aaaaaa')
 for v in [-9,-1,7]:line(hand([[-8,v],[16,v]]),'#333333',2)
 poly(hand([[-5,15],[2,20],[16,11],[12,4],[5,5]]),'#bbbbbb',width=2)
 texts=[f'Ready f{i} /167ms: LOW OUTWARD single near hand','SHORT arm: shoulder > elbow > wrist > palm grip','GRAY DIAGRAM ONLY: no gray recoloring/text/axes in final']
 for yy,t in zip([12,30,480],texts):d.text((ox+12,yy),t,fill='#111111',font=font);svg.append(f'<text x="{ox+12}" y="{yy+12}" font-size="12">{t.replace(">","&gt;")}</text>')
svg.append('</svg>');write('guides/ready-anatomical-motion-v002.svg','\n'.join(svg)+'\n')
gp=R/'guides/ready-anatomical-motion-v002.png';im.save(gp)
details='\n'.join(f'{p["frame"]}: shoulder{p["near_shoulder_design_px"]} -> elbow{p["near_elbow_design_px"]} -> wrist{p["near_wrist_design_px"]} -> closed near palm/grip{p["near_grip_design_px"]}; far relaxed hand{p["far_hand_design_px"]}; invisible handle axis{p["near_handle_axis_design_xy"]}; {p["duration_ms"]}ms.' for p in poses)
prompt=f'''Create exactly FOUR distinct complete FULL-BODY poses on ONE horizontal component row for canonical131's low-outward ONE-HANDED sword-ready IDLE. BODY ONLY. This is the same existing squat hero, not a new identity, armor sheet or a whole sword.

REFERENCE ROLES: image1 canonical131idle0 is the ONLY identity/material/proportion authority. Image2 is an original neutral GRAYSCALE anatomy diagram ONLY for the new low-outward arm, separate relaxed far hand and pose order. Do NOT copy its simplified helmet or gray palette. Image3 is the standard four-slot count/layout ONLY. No old155 vertical-fist Ready, rejected156, other human identity, armor or sword reference is attached.

POSE CONTRACT (all planned locations, not measured future sockets):
{details}

The larger NEAR arm starts at the image-LEFT/front shoulder and bends through one short upper arm, an actual elbow, one forearm, a continuous wrist/cuff and ONE closed brown fist held LOW and slightly forward to image-RIGHT at waist level. It must remain recognizably canonical131's short arm. The wrist-to-palm segment is inside the glove, NOT extra forearm length. Never stretch an upper arm, drop the shoulder/lengthen the torso, enlarge the body or move the helmet to reach diagram coordinates. Anatomy and original proportions take priority over exact diagram points. The former very far[314,315] target is withdrawn and must NOT be used. Keep this compact near grip near[275,315], with natural bent elbow and no disconnected cuff/hand.

FIST/THUMB: rotate the actual near hand so its four curled fingers wrap an INVISIBLE cylinder aligned low-forward/right with approximate[.94,-.341] axis. This is not the old upright fist with only a sword rotated on top. The four finger creases and ONE distinct opposable thumb across the index/middle area must be visible on the camera-facing surface. No flat mitten, open C claw, fifth curled finger, omitted thumb or extra hand. No cylinder/wood rod/handle/pommel/guard/blade is painted into this BODY row; only believable original brown leather glove/cuff pixels. The future sword is separate. No technical axis marks.

FAR ARM: smaller/deeper image-RIGHT shoulder belongs to its own relaxed hanging brown hand beside the far waist/thigh, around[345,365]. It must remain visibly separate from the active near fist, with an intended clear contour gap of at least12sourcepx (about2px at72px body). This gap is a design aim, not proof of final pixels; keep anatomy natural and move the relaxed far arm behind its own hip if needed. Never clasp/support the near fist, point up to an invisible handle or duplicate the active glove. Fingers hang above the boot cuff, not through it.

Four genuinely drawn subtle breathing poses, same low-ready guard, rigid unchanged helmet, stable planted boots and4->0 loop. Do not paste one frame four times or mirror to invent poses. Same standing-equivalent416px on512source, design floor464, fixed native RIGHT-facing3/4camera. One shared drawing/extraction scale for the row; no per-frame fit. Do not enlarge the hero to make the equipment readable. Keep original squat crooked bell helmet/top knob, two amber eyes contained in the dark face slit, original dark cloth shirt/trousers/belt and brown gloves/boots. No armor plate, chestplate, pauldron, bracer, shin plate or shield.

OUTPUT: exactly four separate complete connected full bodies on flat opaque GREEN #00FF00, generous green gaps, uncropped knob to soles, original hand-inked outline and opaque interiors. Only body pixels. No sword/weapon/rod, body glow, blue/purple/colored lighting, colored diagram limbs, slash trails, smoke, sparks, floor/shadow, UI, text, labels, arrows, numbers, red dots, handles or checkerboard. The gray technical diagram is not a final color reference. Source timing is4x167ms but never print it.

BOUNDARY: actual near grip, finger/thumb overlap, invisible-axis estimate, feet and helmet/weapon clearance will be measured after native output. Diagram values are design targets only. This new Ready does NOT silently update old157 attack0/4/5; attack transitions and all armor/actions remain unaccepted until genuinely adapted and run-reviewed.
'''
pp=write('prompts/ready-body-only-v002.txt',prompt)
refs=[('sole_identity131',C),('original_grayscale_low_outward_anatomy_only',gp),('standard_component_count_layout',run/f'references/layout-guides/{state}.png')]
row={'component':'SwordReady','state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),'prompt':desc(pp),
 'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],'frame_count':4,'durations_ms':[167]*4,'loop':True,'fit_window_px':[416,416],
 'target_mounts':[{'frame':p['frame'],'A':p['near_grip_design_px'],'grip_design_px':p['near_grip_design_px'],'near_wrist_design_px':p['near_wrist_design_px'],'grip_axis_design_xy':p['near_handle_axis_design_xy'],'far_hand_design_px':p['far_hand_design_px'],'source_root_design_px':[256,464],'meaning':'Authoring pose only; not a measured joint/grip/root/clearance.'} for p in poses],
 'source_native_facing':1,'source_canvas_px':[512,512],'source_root_design_px':[256,464],'shared_row_scale':True,'target_mounts_are_measured':False,
 'numeric_design_contract':desc(cp),'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode,'new_guides_viewed':False,'generated':False,'actual_raw_sha256':None,'formal_complete_units':0}
hp=write('handoffs/ready-native-input-v002.json',{'schema':'fairytale-sword-body-native-input-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'rows':[row]})
files=sorted(p for p in R.rglob('*') if p.is_file() and 'ready' in p.relative_to(R).as_posix() and 'v002' in p.relative_to(R).as_posix())
fp=write('preparation-freeze-ready-v002.json',{'schema':'fairytale-sword-body-input-freeze-v1','file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],'reference_count':3,'new_media_viewed':False,'generated':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(hp),'prompt':desc(pp),'freeze':desc(fp),'short_arm_lengths':contract['design_segment_lengths_px']},ensure_ascii=False))
