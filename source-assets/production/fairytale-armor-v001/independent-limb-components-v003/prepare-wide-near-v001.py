"""Prepare two wider near-side idle rows; original technical diagrams only."""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SG=Path('C:/Users/22499/.codex/skills/sprite-gen')
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002')
PALETTE=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-limb-components-v002/near-limbs-registration-proposed-v001/composite-preview/frame-0.png')
parser=argparse.ArgumentParser();parser.add_argument('--component',choices=['near-bracer','near-shin'],required=True)
key=parser.parse_args().component
rows={
 'near-bracer':dict(component='NearBracer',state='armor_bracer_near_idle',fit=[44,28],A=[187,283],
   shape=[(-17,-14),(7,-13),(14,-6),(10,7),(-10,14),(-24,10),(-30,0),(-28,-9)],
   seam=[(-28,16),(-10,16),(7,24)],
   rule='Make a WIDE, LOW-PROFILE near forearm plate,44 wide by28 high after fit. The connected round rivet is on the INNER/image-RIGHT part, about68% of plate width from the left and about50% of height from the top. The same body mount[187,283] then lets the plate spread LEFT, rather than sit entirely inside the sleeve. Top about269, distal bottom at297-298 maximum. Its leftmost wing is aroundx157-159 at middle/upper height; lower edge tapers back toward the forearm. Keep the original brown wrist cuff and whole hand untouched. Do not place the rivet on the old image-left position.',
   extents='Design offsets x[-30,+14],y[-14,+14]; display target about1-2px extra outer silhouette, must be judged in actual72px game.'),
 'near-shin':dict(component='NearShin',state='armor_shin_near_idle',fit=[44,34],A=[219,367],
   shape=[(-14,-8),(8,-7),(14,0),(13,12),(5,25),(-12,23),(-29,8),(-20,4),(-20,-1)],
   seam=[(-30,26),(-4,33),(14,36)],
   rule='Make a SHORT WIDE near cloth-shin plate,about43 wide by33-34 high within44x34. The connected round rivet is INNER/image-RIGHT, about68-70% of width from the left, about25% of height from the top. Same body mount[219,367]. Right edge around232-233; left wing around190-194 and bottom no lower than393. IMPORTANT: bevel/retract the UPPER-LEFT corner toward205 at359. The near hand occupies aboutx190-194 at359-371; do not extend a square top-left panel into it. Put the widest outward wing at abouty375, below the hand, then taper the lower edge ABOVE the diagonal brown boot rim. No boot leather or foot coverage. Do not reuse the old narrow inside-the-pants geometry.',
   extents='Design offsets x[-29,+14],y[-8,+25]; upper-left chamfer leaves the hand clear; actual fit/72px silhouette gain still pending.')
}
row=rows[key];run=ROOT/f'run-{key}-idle-v001';state=row['state'];now=datetime.datetime.now().astimezone().isoformat()
assert not run.exists(),'Do not overwrite a prepared run'
def desc(p):
 p=Path(p);b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=ROOT/rel;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return p
action=f'Four genuinely rendered isolated {row["component"]} metal plates matching canonical131 idle0,1,2,3. Wider OUTER silhouette, inner-right rivet, no body/hand/boot pixels.'
seed={'states':{state:{'frames':4,'fps':6,'loop':True,'action':action}},
 'cell':{'width':512,'height':512,'safe_margin_x':(512-row['fit'][0])//2,'safe_margin_y':(512-row['fit'][1])//2},
 'fit':{'pixel_unfake':False,'resample':'lanczos','align_x':'bbox-center','align_y':'bottom','ground_frames':False,'segmentation':'components','shared_row_scale':True}}
seed_path=write(f'requests/{key}-numeric-input-v001.json',seed)
argv=[sys.executable,'-X','utf8','-B',str(SG/'scripts/prepare_sprite_run.py'),'--out-dir',str(run),
 '--character-id',f'fairytale-wide-{key}-idle-v001','--base-image',str(CANON/'curated/frame-0.png'),
 '--description',action,'--style','Canonical131 grotesque cartoon ink; existing147/149/150 grey iron broad values and charcoal contour, no green metal.',
 '--cell-size','512','--chroma-key','#00FF00','--request',str(seed_path)]
result=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8')
write(f'logs/prepare-{key}-v001.log',result.stdout+result.stderr);assert result.returncode==0
request_path=run/'sprite-request.json';request=json.loads(request_path.read_text(encoding='utf-8'))
write(f'requests/{key}-standard-prepare-before-explicit-fields.json',request)
request['fit'].update(seed['fit']);request['states'][state]['durations_ms']=[167]*4
request['chroma']={'mode':'rgb','unmix_reach':4,'spill_max_fraction':.005}
request_path.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert (run/'base-source.png').read_bytes()==(CANON/'curated/frame-0.png').read_bytes()
im=Image.new('RGB',(2048,512),'#f4f6f8');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="512" viewBox="0 0 2048 512"><rect width="2048" height="512" fill="#f4f6f8"/>']
targets=[]
for i in range(4):
 ox=512*i
 def tx(p):return (ox+280+p[0]*5,205+p[1]*5)
 points=[tx(p) for p in row['shape']];seam=[tx(p) for p in row['seam']];a=tx((0,0))
 d.rectangle((ox+10,10,ox+502,502),outline='#94a3b8',width=2)
 d.text((ox+20,24),f'{row["component"]} WIDE /idle{i}/167ms',fill='#172554',font=font)
 d.text((ox+20,50),f'A={row["A"]} INNER RIGHT /fit{row["fit"]}',fill='#172554',font=font)
 d.polygon(points,fill='#9eb6c8',outline='#334155',width=4)
 d.ellipse((a[0]-6,a[1]-6,a[0]+6,a[1]+6),fill='#dc2626')
 d.line(seam,fill='#b45309',width=6)
 d.text((ox+20,414),'RED=real rivet center / sole primary A',fill='#172554',font=font)
 d.text((ox+20,440),'ORANGE=cuff/boot direction HINT only',fill='#172554',font=font)
 d.text((ox+20,466),'Original SCHEMATIC, not body mask/art',fill='#172554',font=font)
 svg += [f'<rect x="{ox+10}" y="10" width="492" height="492" fill="none" stroke="#94a3b8"/>',
 f'<text x="{ox+20}" y="40" font-size="16">{row["component"]} WIDE /idle{i}/167ms</text>',
 f'<text x="{ox+20}" y="66" font-size="16">A={row["A"]} INNER RIGHT /fit{row["fit"]}</text>',
 '<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+'" fill="#9eb6c8" stroke="#334155" stroke-width="4"/>',
 f'<circle cx="{a[0]}" cy="{a[1]}" r="6" fill="#dc2626"/>',
 '<polyline points="'+' '.join(f'{x},{y}' for x,y in seam)+'" fill="none" stroke="#b45309" stroke-width="6"/>',
 f'<text x="{ox+20}" y="430" font-size="16">RED=real rivet center / sole primary A</text>',
 f'<text x="{ox+20}" y="456" font-size="16">ORANGE=cuff/boot direction HINT only</text>',
 f'<text x="{ox+20}" y="482" font-size="16">Original SCHEMATIC, not body mask/art</text>']
 rgba=Image.open(CANON/f'curated/frame-{i}.png').convert('RGBA').getpixel(tuple(row['A']));assert rgba[3]==255
 targets.append({'frame':i,'A':row['A'],'original_cloth_rgba':list(rgba),'confidence':'Garment design mount, not bone; semantic ambiguity about2-3px.'})
svg.append('</svg>');write(f'guides/{key}-wide-inner-rivet-v001.svg','\n'.join(svg)+'\n')
guide=ROOT/f'guides/{key}-wide-inner-rivet-v001.png';guide.parent.mkdir(parents=True,exist_ok=True);im.save(guide)
prompt=f'''Produce exactly FOUR isolated connected NEAR-SIDE {row['component'].upper()} armor plates, one horizontal row for canonical131 idle0,1,2,3. This is a targeted WIDER-SILHOUETTE geometry correction, not a new character or a full outfit.

FIVE REFERENCES, STRICT ROLES: 1)131idle0 is the sole identity/style. 2)131fouridle contact gives pose order and original unaltered limb/cuff geometry. 3)The existing assembled armor composite gives ONLY147/149/150 grey iron palette, broad ink and handmade construction; IGNORE the geometry of its OLD narrow bracer/shin. 4)Standard4slot guide gives exact component count4. 5)NEW original wide-shape guide gives the outward expansion and INNER-RIGHT connected rivet placement; its red/orange/blue schematic colors, marks/text/border never appear in art.

GEOMETRY, MANDATORY: {row['rule']} {row['extents']} Keep the commonbody, original mount and fixed72px display unchanged. The objective is outer contour gain at small size, not added engraving or a larger hero. Follow the new guide's broad plate/chamfer, not the old inside-clothing silhouette. Rivet placement is a real plate feature, not a technical counting dot or a hidden pivot.

Same slightly crooked grotesque cartoon handmade iron as the existing chest/shoulders. A broad matte desaturated grey face, strong charcoal outer rim and one restrained pale edge; no tiny decoration, spikes or detached straps. Preserve rigid construction across four corresponding idle poses, whose limbs barely move. Do not paste a clone four times or mirror/crop another side. Each slot is ONE physically connected armor plate, exactly FOUR components total; no fake bridge or detached marker.

Output ONLY these four metal pieces, no original sleeve/pants, skin, glove cuff, hand/fingers, boot rim/foot/toe/sole, head/helmet, chest/shoulder plate, opposite limb, weapon or mannequin. Clean fully opaque GREEN #00FF00 background; opaque plate interiors with clean ink edges. Generous green separation and outer padding. One common source drawing scale; later native component extraction uses ONE shared ratio/Lanczos for the row, not per-frame normalization. No floor/shadow/glow/halo/checkerboard/UI/text/numbers. Timing stays4x167ms; do not render timing labels.

After generation the actual connected rivet ring center will be measured and integer-translated to the unchanged body A. No repainted body, arbitrary pivot swap, hand mask shortcut or full-motion acceptance is implied. This is only an idle trial component, not full armor or attack/walk coverage.
'''
prompt_path=write(f'prompts/{key}-wide-four-idle-v001.txt',prompt)
refs=[('sole_identity',CANON/'curated/frame-0.png'),('four_idle_pose_order_only',CANON/'qa/idle-contact.png'),
 ('existing_armor_palette_construction_only_IGNORE_old_limb_geometry',PALETTE),
 ('standard_four_component_count_layout',run/f'references/layout-guides/{state}.png'),('original_wide_shape_inner_rivet_schematic_not_mask',guide)]
entry={'component':row['component'],'state':state,'run_dir':run.as_posix(),'raw_output_path':(run/'raw'/f'{state}.png').as_posix(),
 'prompt':desc(prompt_path),'reference_images_in_order':[{'role':role,'file':desc(p)} for role,p in refs],
 'fit_window_px':row['fit'],'target_mounts':targets,'frame_count':4,'durations_ms':[167]*4,
 'source_native_facing':1,'shared_row_scale':True,'body_canvas_px':[512,512],'body_display_canvas_size':72*512/416,
 'body_display_pivot_px':[256,464],'pivot_is_certified_feet_root':False,'design_extent_notes':row['extents'],
 'new_guides_viewed':False,'generated':False,'actual_raw_sha256':None,'formal_complete_units':0,
 'standard_prepare_command':argv,'standard_prepare_exit_code':result.returncode}
handoff=write(f'handoffs/{key}-native-input-v001.json',{'schema':'fairytale-limb-component-native-input-v1','created_local':now,'rows':[entry]})
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and (key in p.relative_to(ROOT).as_posix() or p.name==Path(__file__).name))
freeze=write(f'preparation-freeze-{key}-v001.json',{'schema':'fairytale-limb-input-freeze-v1','created_local':now,
 'file_count':len(files),'total_bytes':sum(p.stat().st_size for p in files),'files':[desc(p) for p in files],
 'reference_limit_per_call':5,'new_media_viewed':False,'generated':False,'formal_complete_units':0})
print(json.dumps({'handoff':desc(handoff),'prompt':desc(prompt_path),'freeze':desc(freeze)},ensure_ascii=False))
