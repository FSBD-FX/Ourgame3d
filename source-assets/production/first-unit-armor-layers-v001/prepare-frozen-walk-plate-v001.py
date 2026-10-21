from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent;O=P.parent/'first-unit-animation-v003'
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
d=r.read(O/'assembly-markers-import-v007.json');a=next(a for a in d['actions'] if a['action']=='walk');frames=a['frames'];assert len(frames)==6
sheet=Image.new('RGBA',(1536,1024),(255,0,255,255));sources=[]
for i,f in enumerate(frames):
 p=Path(f['frame_path']);assert r.sha(p)==f['frame_sha256'];im=Image.open(p).convert('RGBA');assert im.size==(512,512);sheet.alpha_composite(im,((i%3)*512,(i//3)*512))
 sources.append({'index':i,'path':str(p),'sha256':r.sha(p),'grip_px':f['grip_px'],'root_px':f['ground_root_px']})
q=P/'references/frozen-walk-pose-plate-v001.png';assert not q.exists();sheet.convert('RGB').save(q);r.archive(q,q.relative_to(P),'actual_frozen_alternating_walk_pose_reference_no_geometry_transform')
q=P/'references/frozen-walk-pose-provenance-v001.json';r.write(q,{'sources':sources,'transforms':'none','parent_runtime_status':'alternating_legs_and_identity_verified_candidate_footlock_bob_unresolved','support_root_scope':'existing_manually_measured_contact_proxies_not_new_footlock_certification'});r.archive(q,q.relative_to(P),'actual_walk_reference_source_and_scope')
print({'actual_walk_frames':6,'pose_changes':0})
