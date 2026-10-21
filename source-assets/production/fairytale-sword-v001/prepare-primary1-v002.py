"""New grayscale anatomy-only six-phase request; no generation, no asset editing."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

R=Path(__file__).resolve().parent; SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
C=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated/frame-0.png')
READY=R/'run-ready-v001/curated/frame-0.png'
run=R/'run-primary1-v002'; assert not run.exists()
state='sword_primary_1'; durations=[85,85,60,60,155,155]
poses=[
 {'phase':'anticipation1 / from Ready','shoulder':[205,248],'elbow':[213,289],'grip':[258,282],'far_hand':[345,345],'hip':[0,0],'axis':[0,-1]},
 {'phase':'anticipation2 / single-hand loaded','shoulder':[201,247],'elbow':[170,246],'grip':[165,190],'far_hand':[342,345],'hip':[-3,0],'axis':[-.35,-.93675]},
 {'phase':'cut1 / diagonal forward','shoulder':[218,249],'elbow':[270,268],'grip':[344,282],'far_hand':[307,342],'hip':[6,2],'axis':[.78,.62578]},
 {'phase':'cut2 / down and forward','shoulder':[217,252],'elbow':[283,312],'grip':[370,350],'far_hand':[315,336],'hip':[8,5],'axis':[.93,.36756]},
 {'phase':'recovery1 / release tension','shoulder':[211,249],'elbow':[249,294],'grip':[300,306],'far_hand':[345,345],'hip':[3,1],'axis':[.4,-.91652]},
 {'phase':'recovery2 / match Ready','shoulder':[205,248],'elbow':[213,289],'grip':[258,282],'far_hand':[345,345],'hip':[0,0],'axis':[0,-1]}]

def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,x):
 p=R/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
seed={'states':{state:{'frames':6,'fps':10,'loop':False,'action':'Canonical131 single near-hand sword BODY ONLY: Ready, load, diagonal cut, low forward followthrough, decelerate, Ready. Far hand remains visibly separate beside far waist in ALL six poses.'}},
 'cell':{'width':512,'height':512,'safe_margin_x':48,'safe_margin_y':48},
 'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
seedp=write('requests/primary1-numeric-input-v002.json',seed)
argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),'--character-id','fairytale-common-hero-sword-primary1-v002','--base-image',str(C),
 '--description',seed['states'][state]['action'],'--style','Canonical131 only: grotesque hand-inked bell helmet, dark cloth, original brown hands and boots. Fixed three-quarter right camera, one-handed sword body only.','--cell-size','512','--chroma-key','#00FF00','--request',str(seedp)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/prepare-primary1-v002.log',result.stdout+result.stderr);assert result.returncode==0
reqp=run/'sprite-request.json';req=json.loads(reqp.read_text(encoding='utf-8'));write('requests/primary1-v002-standard-prepare-before-explicit-fields.json',req)
req['fit'].update(seed['fit']);req['states'][state]['durations_ms']=durations;req['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
reqp.write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert (run/'base-source.png').read_bytes()==C.read_bytes()

# All new diagram pixels are original grayscale geometry, with no raster art copied in.
im=Image.new('RGB',(3072,512),'#eeeeee');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="3072" height="512" viewBox="0 0 3072 512"><rect width="100%" height="100%" fill="#eeeeee"/>']
for i,p in enumerate(poses):
 ox=i*512
 def poly(values,fill,outline='#222222',width=2):
  pp=[(ox+x,y) for x,y in values];d.polygon(pp,fill=fill,outline=outline,width=width)
  svg.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="{fill}" stroke="{outline}" stroke-width="{width}"/>')
 def line(values,fill,width):
  pp=[(ox+x,y) for x,y in values];d.line(pp,fill=fill,width=width,joint='curve')
  svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in pp)+f'" fill="none" stroke="{fill}" stroke-width="{width}" stroke-linejoin="round"/>')
 hx,hy=p['hip'];fx,fy=p['far_hand'];far_elbow=[307+hx*.3,298+hy*.3]
 # Far limb is behind the torso and terminates at a clearly separated relaxed hand.
 line([[291+hx*.3,250+hy*.3],far_elbow,[fx,fy-13]],'#888888',22)
 poly([(fx-10,fy-18),(fx+8,fy-17),(fx+13,fy-5),(fx+10,fy+13),(fx+3,fy+17),(fx,fy+5),(fx-4,fy+14),(fx-9,fy+11),(fx-6,fy-2),(fx-12,fy-7)],'#bbbbbb')
 poly([(207+hx,239+hy),(284+hx,241+hy),(302+hx,308+hy),(281+hx,339+hy),(234+hx,337+hy),(205+hx,302+hy)],'#777777')
 line([[237+hx,335+hy],[213+hx*.3,377+hy*.3],[194,425]],'#777777',34)
 line([[279+hx,335+hy],[290+hx*.3,377+hy*.3],[303,423]],'#777777',30)
 poly([(174,420),(211,420),(218,447),(223,464),(151,464),(156,445)],'#aaaaaa')
 poly([(283,420),(319,420),(325,443),(351,453),(355,461),(267,461),(272,444)],'#aaaaaa')
 poly([(173,210),(184,160),(202,126),(238,106),(282,108),(311,127),(324,156),(337,160),(337,177),(324,177),(335,226),(306,236),(250,229),(205,220)],'#bbbbbb')
 poly([(242,86),(269,86),(276,107),(243,107)],'#bbbbbb');poly([(230,66),(251,48),(273,76),(246,86)],'#bbbbbb')
 gx,gy=p['grip'];ax,ay=p['axis'];n=math.hypot(ax,ay);ax/=n;ay/=n;ux,uy=-ay,ax
 # Fist basis follows only the invisible planned handle axis. Neutral gray creases/thumb.
 def fist(values):return [(gx+u*ux+v*ax,gy+u*uy+v*ay) for u,v in values]
 line([p['shoulder'],p['elbow'],[gx-13*ux,gy-13*uy]],'#666666',29)
 poly(fist([(-18,-14),(-18,11),(-9,19),(11,18),(19,10),(20,-10),(10,-18),(-9,-19)]),'#aaaaaa')
 for v in [-9,-1,7]:line(fist([[-8,v],[16,v]]),'#333333',2)
 poly(fist([[-5,15],[2,20],[16,11],[12,4],[5,5]]),'#bbbbbb',width=2)
 # Only external text labels identify layers; there is no colored limb/axis/light cue.
 title=f'f{i}: {p["phase"]} / {durations[i]}ms'
 d.text((ox+12,12),title,fill='#111111',font=font)
 d.text((ox+12,30),'NEAR = sole active arm; FAR = relaxed separate waist hand',fill='#111111',font=font)
 d.text((ox+12,478),'DIAGRAM ONLY: no labels, gray recoloring, sword or FX in final',fill='#111111',font=font)
 svg.append(f'<text x="{ox+12}" y="24" font-size="12">{title}</text>')
 svg.append(f'<text x="{ox+12}" y="44" font-size="12">NEAR sole active arm / FAR separate relaxed waist hand</text>')
svg.append('</svg>');write('guides/primary1-anatomical-motion-v002.svg','\n'.join(svg)+'\n')
gp=R/'guides/primary1-anatomical-motion-v002.png';im.save(gp)
prompt='''Create exactly SIX complete FULL-BODY poses in one horizontal component row for the existing canonical131 hero's ONE-HANDED military-sword Primary1 body. BODY ONLY, with no sword or handle rendered.

REFERENCE ROLES, STRICT: image1 canonical131 idle0 is the ONLY identity, materials, helmet shape and original squat body-proportion authority. Image2 is actual native155 SwordReady frame0, used ONLY for the single-near-hand guard and separate far hand at the start/end of this action; preserve canonical131 identity. Image3 is an original GRAYSCALE anatomy/motion diagram, used only for arm continuity, six phase order and separate near/far roles; do NOT copy its gray colors, labels or simplified head. Image4 is the standard six-slot count/layout guide. No rejected native156 pose is supplied or to be reused.

THE ACTIVE NEAR ARM starts on the larger image-LEFT/front shoulder, bends through one anatomically connected elbow/forearm, and ends in ONE brown closed sword-grip fist. The FAR ARM belongs to the smaller image-RIGHT/back shoulder and hangs independently beside the FAR WAIST in EVERY pose. Its brown relaxed hand is always visibly separate from the active fist, never assists/grabs/clasps the active hand, never reaches above the head or across to the weapon. Maintain a clear air or dark-cloth separation between the hands. Do not invent a two-handed overhead chop, clasped prayer hands, boxing double fist or forward shove.

SIX PHASES IN EXACT ORDER: 0 starts in the actual native155 Ready guard, the active single near fist across the lower chest and the far hand relaxed down beside the right waist. 1 loads only the near fist high to image-LEFT of the helmet, near elbow bent; the far hand stays visibly down at the far waist. 2 drives that single near fist diagonally across the chest toward image-RIGHT; far hand stays back beside waist. 3 continues the SAME single-arm cut down and forward to the right below the chest, with a readable low followthrough rather than a straight thrust; far hand stays separately beside the far waist. 4 decelerates the near arm back toward guard; far hand remains separate. 5 MATCHES native155 Ready guard, near fist across the lower chest and relaxed far hand down, ready for seamless return. Exactly two anticipation, two cut, two recovery poses, with real connected shoulder/elbow/wrist changes. Source phases are 85,85,60,60,155,155ms; never print timings in the art.

HAND ANATOMY: one closed near brown leather glove with four visibly curled finger lobes and ONE distinct opposable thumb laid diagonally across the index/middle finger on the camera-facing fist surface. The thumb must have its own visible contour/crease rather than being omitted or confused with a fifth curled finger. Grip an INVISIBLE future cylindrical handle with believable overlapping fingers; no huge open C shape or flat mitten. Do NOT paint a rod/cylinder/wood handle/pommel/guard/blade into this BODY row. The relaxed far hand has a separate natural thumb and must not merge with the near glove. The guide is only a planned pose; actual palm, thumb, handle-axis and foot roots will be measured after generation, not assumed.

EXACT IDENTITY: original canonical131 crooked squat bell helmet, rigid shell/top knob, two amber eyes only inside black face opening, dark original cloth shirt/trousers and belt, brown gloves/boots. Fixed native RIGHT-facing three-quarter camera for ALL six; no new human anatomy or side/back camera. Same standing-equivalent scale across the complete row, 416px body on512 source and floor design464. Weight shift/crouch may be actual pose, but do not stretch the helmet or rescale bodies to normalize each bbox. No armor plates, shoulder caps, bracers, greaves or shield baked into this common body.

OUTPUT: six distinct complete connected full bodies on flat opaque GREEN #00FF00, generous green gaps, uncropped head-knob through boots. Clear original hand-inked outlines and opaque interiors. Render ONLY actual body pixels in the original131 palette. NO blue, purple, orange technical limb colors, colored edge lighting, body rim glow, blue thigh/knee patches, sparks, slash trail, smoke, shadow, floor, UI, labels, arrows, sockets, colored axes or numbers. Only the two contained eye shapes emit amber. Do not copy/mirror one pose six times. Later extraction uses one shared scale for the row, never per-frame fit. Final sword/hand occlusion and runtime binding are separate; this image does not certify complete actions or equipment.
'''
pp=write('prompts/primary1-body-only-v002.txt',prompt)
refs=[('sole_identity_canonical131',C),('actual155Ready_guard_motion_only',READY),('original_grayscale_anatomical_action_only',gp),('standard_component_count_layout',run/f'references/layout-guides/{state}.png')]
row={'component':'SwordPrimary1','state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),
 'prompt':desc(pp),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],
 'fit_window_px':[416,416],'target_mounts':[{'frame':i,'A':p['grip'],'grip_design_px':p['grip'],'grip_axis_design_xy':p['axis'],'far_hand_design_px':p['far_hand'],'source_root_design_px':[256,464],'meaning':'Pose design only; never import as measured markers.'} for i,p in enumerate(poses)],
 'frame_count':6,'durations_ms':durations,'loop':False,'source_native_facing':1,'shared_row_scale':True,'standing_equivalent_body_height_px':416,'body_canvas_px':[512,512],
 'source_root_design_px':[256,464],'target_mounts_are_measured':False,'generated':False,'new_guides_viewed':False,'formal_complete_units':0,
 'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode,
 'combat_phase_contract':{'weapon':'WPN-SWD-001','stage_zero_based':0,'windup_ms':170,'lock_ms':68,'active_ms':120,'recovery_ms':310,'base_boundaries_ms':[0,85,170,230,290,445,600],'runtime_sampler':'Existing GetPrimaryPoseFrame on actual Action phase times; never hard override accepted speed/deadlines.'},
 'correction_basis':'Rejected156 double-handed anatomy, blue thigh/knee FX, and last-frame Ready mismatch. Do not reference failed156 image.'}
hp=write('handoffs/primary1-native-input-v002.json',{'schema':'fairytale-sword-body-native-input-v1','created_local':datetime.datetime.now().astimezone().isoformat(),'rows':[row]})
files=sorted(p for p in R.rglob('*') if p.is_file() and ('primary1' in p.relative_to(R).as_posix() and 'v002' in p.relative_to(R).as_posix()))
fp=write('preparation-freeze-primary1-v002.json',{'schema':'fairytale-sword-body-input-freeze-v1','file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],'reference_count':4,'new_media_viewed':False,'generated':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(hp),'prompt':desc(pp),'freeze':desc(fp),'files':len(files)},ensure_ascii=False))
