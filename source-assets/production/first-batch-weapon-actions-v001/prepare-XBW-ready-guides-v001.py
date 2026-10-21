"""Existing-asset placement references only; new body artwork must use native gen."""
from pathlib import Path
import importlib.util,shutil,math,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
old=P.parent/'first-batch-weapon-components-v001'
helper=(old/'production-record.py').read_text('utf-8').replace('2026-10-15_首批独立武器组件_v001','2026-10-15_首批武器专属动作_v001')
hp=P/'production-record.py';assert not hp.exists();hp.write_text(helper,encoding='utf-8')
s=importlib.util.spec_from_file_location('record',hp);r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
source=P.parent/'first-unit-armor-layers-v001/processed/call45-fixed-canvas-v002/frame-0.png'
body=Image.open(source).convert('RGBA');assert body.size==(512,512)
weapon_path=old/'components/XBW001-neutral-component-v002.png';weapon=Image.open(weapon_path).convert('RGBA')
anchor=Image.new('RGBA',(1536,1024),(255,0,255,255));placement=anchor.copy()
scale=.55;grip=(200,308);wg=(128,253);support=(315,324)
render=weapon.transform((512,512),Image.Transform.AFFINE,(1/scale,0,wg[0]-grip[0]/scale,0,1/scale,wg[1]-grip[1]/scale),resample=Image.Resampling.BICUBIC)
for i in range(6):
    x=(i%3)*512;y=(i//3)*512;anchor.alpha_composite(body,(x,y));placement.alpha_composite(render,(x,y))
    d=ImageDraw.Draw(placement)
    for point,color in [(grip,(40,170,255,255)),(support,(80,240,130,255)),((256,472),(255,255,255,255))]:
        gx=x+point[0];gy=y+point[1];d.line([(gx-6,gy),(gx+6,gy)],fill=color,width=2);d.line([(gx,gy-6),(gx,gy+6)],fill=color,width=2)
for name,image in [('XBW-ready-body-anchor-v001.png',anchor),('XBW-ready-weapon-placement-geometry-v001.png',placement)]:
    q=P/'references'/name;assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True);image.convert('RGB').save(q);r.archive(q,q.relative_to(P),'existing_asset_and_geometry_reference_not_new_body_art')
q=P/'references/XBW-ready-guide-provenance-v001.json';assert not q.exists()
r.write(q,{'body_source':str(source),'body_source_sha256':r.sha(source),'weapon_source':str(weapon_path),'weapon_source_sha256':r.sha(weapon_path),
    'reference_only':True,'body_pixel_transform':'none; repeat accepted same512 reference six times over flatmagenta',
    'weapon_reference_transform':{'uniform_scale':scale,'primary_source':list(wg),'target_primary':list(grip),'actual_target_support':[200+(337-128)*scale,308+(282-253)*scale]},
    'target_root_px':[256,472],'target_primary_grip_px':list(grip),'target_support_grip_px':list(support),
    'no_generated_body_art_by_script':True,'generation_calls_added':0})
r.archive(q,q.relative_to(P),'crossbow_geometry_pose_planning_reference_provenance');print({'guides_archived':2})
