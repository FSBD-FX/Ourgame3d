"""Archive exact-size frozen body frames as reference only; no new art."""
from pathlib import Path
import importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
d=r.read(O/'assembly-markers-import-v005.json')
for action in ['primary_1','primary_2','primary_3']:
    rows=next(a for a in d['actions'] if a['action']==action)['frames'];assert len(rows)==6
    sheet=Image.new('RGBA',(1536,1024),(255,0,255,255));sources=[]
    for i,row in enumerate(rows):
        p=Path(row['frame_path']);assert r.sha(p)==row['frame_sha256'];im=Image.open(p).convert('RGBA');assert im.size==(512,512)
        sheet.alpha_composite(im,((i%3)*512,(i//3)*512));sources.append({'index':i,'path':str(p),'sha256':r.sha(p),'grip_px':row['grip_px'],'root_px':row['ground_root_px']})
    q=P/f'references/frozen-{action}-pose-plate-v001.png';assert not q.exists();sheet.convert('RGB').save(q);r.archive(q,Path('references')/q.name,'frozen_actual_body_pose_reference_no_geometry_change')
    q=P/f'references/frozen-{action}-pose-provenance-v001.json';r.write(q,{'action':action,'sources':sources,'transforms':'none','cell':[512,512],'source_pose_frozen':True});r.archive(q,Path('references')/q.name,'frozen_pose_reference_provenance')
print({'pose_plates':3,'unique_source_frames':18,'scale':1})
