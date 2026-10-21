"""Offline preparation only. Writes this NEW candidate directory, never assets."""
from pathlib import Path
from PIL import Image
import ast,hashlib,json

ROOT=Path('F:/Ourgame').resolve()
OUT=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-import-candidate-v001'
ASSEMBLY=ROOT/'source-assets/production/fairytale-lgt-readability-v003/walk-body-armor-assembly-v001/2026-10-18-closed72-final48-candidate-v002'
SOURCE=ASSEMBLY/'import-candidate-48'
NS='/Game/Production/ArtTrials/EV048/v016/HeroLeatherWalk'
COMPONENTS={'Body':'RevisedWhole','BodyRest':'BodyLayers/BodyRest','NearArmWithoutHand':'BodyLayers/NearArmWithoutHand',
 'HelmetForeground':'BodyLayers/HelmetForeground','NearHand':'BodyLayers/NearHand','ShoulderFar':'Armor/FarShoulder','Chest':'Armor/Chest','ShoulderNear':'Armor/NearShoulder'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

frozen=load(ASSEMBLY/'final48-freeze-v001.json')
for x in frozen['files']:
 p=Path(x['path']);assert p.is_file() and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert len(list(SOURCE.rglob('*.png')))==48
assert not (ROOT/'UnrealGame/Content/Production/ArtTrials/EV048/v016').exists()

def inventory():
 return [{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
  for p in sorted((ROOT/'UnrealGame/Content/Production').rglob('*')) if p.is_file()]
before=inventory();assert len(before)==1151 and all(x['path'].endswith('.uasset') for x in before)
assert inventory()==before
inv=OUT/'old-production1151-before-import-v001.json'
write(inv,{'schema':'walk-import-old-production-all-files-v001','files':before,'count':len(before),'preparation_independent_passes':2,'passes_equal':True})

markers=load(ASSEMBLY/'walk-six-Grip-Axis-ground-display-markers-v001.json')
assets=[]
for component,folder in COMPONENTS.items():
 for i in range(6):
  p=SOURCE/folder/f'frame-{i}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512)
  a=im.getchannel('A');assert a.getextrema()==(0,255) and all(im.getpixel(xy)[3]==0 for xy in [(0,0),(511,0),(0,511),(511,511)])
  name=f'T_Fairytale_Walk_{component}_{i:03d}_v001'
  assets.append({'component':component,'frame':i,'source':p.as_posix(),'source_bytes':p.stat().st_size,'source_sha256':sha(p),
   'source_rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'source_bbox':list(a.getbbox()),
   'name':name,'package_path':NS+'/'+name,'object_path':NS+'/'+name+'.'+name})
assert len({a['source'] for a in assets})==len({a['object_path'] for a in assets})==48
phases=[]
for i,m in enumerate(markers['frames']):
 assert m['frame']==i and m['duration_ms']==83 and m['ground_pivot_px']==[256,464]
 phases.append({'frame':i,'duration_seconds':.083,'root_display_canvas_px':m['ground_pivot_px'],
  'root_role':m['ground_pivot_role'],'grip_artist_design_canvas_px':m['Grip_canvas_px'],
  'axis_artist_design_screen_xy':m['Axis_artist_bladehold_screen_xy'],
  'object_paths':{a['component']:a['object_path'] for a in assets if a['frame']==i}})
manifest={'schema':'fairytale-walk48-native-import-candidate-v001','frozen':True,'asset_count':48,'namespace':NS,
 'canvas_px':[512,512],'durations_ms':[83]*6,'cycle_seconds':.498,'cycle_distance_world_units_art_tuned':80.,
 'movement_speed_changed':False,'body_canvas_size':72*512/416,'independent_sword_scale':.5,'native_facing':1,
 'display_root_role':'Canvas anchor only; no physical support-root or foot-lock claim',
 'scope':'48 exact closed72 body/LGT trial textures. Actual running motion/grasp/footlock/formal unit not accepted.',
 'root_static_review_retention':'E342; Root independently viewed final noSword6/layers/wrist5 and authorized 48 import preparation',
 'import_permitted_for_root_native_trial':True,'runtime_verified':False,'full_motion_accepted':False,'formal_complete_units':0,
 'replace_existing':False,'old_inventory':pin(inv),'old_file_count':1151,'expected_final_file_count':1199,
 'texture_settings':{'compression_settings':'TC_EDITOR_ICON','mip_gen_settings':'TMGS_NO_MIPMAPS','lod_group':'TEXTUREGROUP_UI','never_stream':True,'srgb':True},
 'references':{'assembly_freeze':pin(ASSEMBLY/'final48-freeze-v001.json'),
  'source_pixel_proof':pin(ASSEMBLY/'closed72-final48-source-and-pixel-proof-v001.json'),
  'markers':pin(ASSEMBLY/'walk-six-Grip-Axis-ground-display-markers-v001.json')},
 'source_to_runtime_component':COMPONENTS,'phases':phases,'assets':assets}
write(OUT/'import-walk48-v001.json',manifest)

# Copy the proven stdlib decoder function into a NEW local module; append actual
# decoded RGBA hashing so UE bundled Python needs neither Pillow nor numpy.
decoder_source=(ROOT/'tools/scripts/ue-import-armor-primary2-four-v001.py').read_text(encoding='utf-8-sig')
tree=ast.parse(decoder_source);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='inspect_rgba_png')
fn=ast.get_source_segment(decoder_source,node)
fn=fn.replace('corners = []','corners = []\n    rgba_hash = hashlib.sha256()',1)
fn=fn.replace('        previous = row','        rgba_hash.update(row)\n        previous = row',1)
fn=fn.replace('return {"canvas_px": [512, 512]','return {"rgba_sha256": rgba_hash.hexdigest(), "canvas_px": [512, 512]',1)
module='"""Copied proven five-filter native RGBA decoder plus decoded-byte SHA. No image mutation."""\nimport struct,zlib,hashlib\ndef require(condition,message):\n    if not condition: raise ValueError(message)\n\n'+fn+'\n'
(OUT/'walk_png_decoder_v001.py').write_text(module,encoding='utf-8',newline='')
print(json.dumps({'manifest':pin(OUT/'import-walk48-v001.json'),'inventory':pin(inv),'decoder':pin(OUT/'walk_png_decoder_v001.py'),'old_passes':2,'sources':48},indent=2))
