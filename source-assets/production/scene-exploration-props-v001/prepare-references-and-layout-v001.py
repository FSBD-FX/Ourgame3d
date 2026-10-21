"""Preserve actual scene/style refs and draw geometry-only generation layout guides."""
from pathlib import Path
import importlib.util,shutil,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
refs=P/'references';refs.mkdir(parents=True,exist_ok=True);rows=[]
for src,name in[(Path('F:/Ourgame/过程图稿与视频/2026-10-15_侧路碎碑迷雾记忆真实出口探索运行_v001/原件/MovieFrame00628.png'),'actual-scene-failure-frame00628.png'),
 (P.parent/'room-art-v001/processed/dungeon-floor-tile-512-v001.png','actual-room-floor-style-v001.png')]:
 dst=refs/name;assert not dst.exists();shutil.copy2(src,dst);assert r.sha(src)==r.sha(dst);r.archive(dst,dst.relative_to(P),'actual_preserved_scene_or_room_style_reference_not_new_art');rows.append({'path':str(dst),'sha256':r.sha(dst),'source':str(src)})
# These are deliberately abstract wireframes/anchors, never creative art or deliverable props.
im=Image.new('RGB',(512,512),(255,0,255));d=ImageDraw.Draw(im)
d.rectangle((20,350,492,420),outline=(0,200,240),width=2);d.rectangle((20,306,492,376),outline=(255,255,255),width=2)
for a,b in[((20,306),(20,350)),((492,306),(492,350)),((20,376),(20,420)),((492,376),(492,420))]:d.line((a,b),fill=(255,255,255),width=2)
d.line((246,385,266,385),fill=(0,200,240),width=1);d.line((256,375,256,395),fill=(0,200,240),width=1)
d.text((24,285),'ABSTRACT LAYOUT ONLY / NO CREATIVE ART',fill='white');d.text((22,428),'GROUND 472x70  ROOT256385  HEIGHT44',fill='white')
q=refs/'low-wall-geometry-layout512-v001.png';assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'abstract_geometry_only_generation_guide_not_game_asset')
rows.append({'path':str(q),'sha256':r.sha(q),'kind':'geometry_only_layout'})
j=P/'reference-sources-v001.json';r.write(j,{'schema':'scene_prop_reference_sources_v1','references':rows,'native_generation_calls':0,'wall_target_source_footprint_px':[20,350,492,420],
 'wall_target_source_root_px':[256,385],'wall_target_visual_height_px':44,'uniform_trial_scale':.55,'wall_actual_world_AABB_cm':[-1100,-700,60,160],
 'collision_authority':'existing_game_geometry_read_only; image_never_edits_AABB','runtime_verified':False});r.archive(j,j.relative_to(P),'source_geometry_and_style_reference_provenance')
print(json.dumps({'references':rows,'generation_calls':0}))
