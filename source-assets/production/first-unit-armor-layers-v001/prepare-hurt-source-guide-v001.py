"""Arrange six immutable hurt reference frames without transforming pixels."""
from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
mp=O/'assembly-markers-import-v005.json';a=next(x for x in r.read(mp)['actions'] if x['action']=='hurt')
sheet=Image.new('RGBA',(1536,1024),(255,0,255,255));sources=[]
for i,row in enumerate(a['frames']):
    p=Path(row['frame_path']);assert r.sha(p)==row['frame_sha256']
    image=Image.open(p).convert('RGBA');assert image.size==(512,512)
    sheet.alpha_composite(image,((i%3)*512,(i//3)*512))
    sources.append({'index':i,'path':str(p),'sha256':r.sha(p),'root_px':row['ground_root_px'],'grip_px':row['grip_px']})
out=P/'references/hurt-original-six-pose-guide-v001.png';assert not out.exists();sheet.convert('RGB').save(out)
r.archive(out,out.relative_to(P),'immutable_hurt_poses_same_canvas_no_art_generated_or_transformed')
jp=P/'references/hurt-original-six-pose-guide-v001.json';assert not jp.exists()
r.write(jp,{'canvas_px':[1536,1024],'grid_rows':2,'grid_cols':3,'cell_px':[512,512],'source_marker_manifest':str(mp),'source_marker_manifest_sha256':r.sha(mp),
    'sources':sources,'source_pixel_transform':'none; original alpha composition over flat magenta only'})
r.archive(jp,jp.relative_to(P),'original_hurt_pose_reference_provenance');print(out)
