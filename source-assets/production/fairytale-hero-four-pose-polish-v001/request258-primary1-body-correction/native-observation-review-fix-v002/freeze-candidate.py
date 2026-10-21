from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;OUT=HERE/'candidate-freeze-v002.json';assert not OUT.exists();sha=lambda b:hashlib.sha256(b).hexdigest();files=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p!=OUT:
  b=p.read_bytes();files.append({'relative_path':p.relative_to(HERE).as_posix(),'bytes':len(b),'sha256':sha(b)})
def pin(rel):
 b=(HERE/rel).read_bytes();return {'relative_path':rel,'bytes':len(b),'sha256':sha(b)}
m={'schema':'request258-native-observation-review-fix-freeze-v002','created_utc':datetime.now(timezone.utc).isoformat(),'status':'CANDIDATE_ONLY_NOT_ADMITTED_NOT_UE_COMPILED_NOT_RUN','projected_source':pin('projected/DungeonHeroLandingPriorityProbeV001.cpp'),'before_source':pin('before/DungeonHeroLandingPriorityProbeV001.cpp'),'dependencies':[{'role':'immutable_v001_observer_freeze',**pin('before/observer-candidate-freeze-v001.json')},{'role':'frozen_renderer_after_source',**pin('before/renderer-candidate-after.cpp')},{'role':'immutable_binding_candidate_freeze',**pin('before/binding-candidate-freeze-v001.json')},{'role':'fresh_review_important1',**pin('before/art258-native-observer-review-v001.md')}],'full_exact_seams':'exact-seams.json','scoped_delta_exact_seams':'v001-to-v002-exact-delta.json','preload_host_checks':11,'preload_host_failures':0,'preload_red_expected_failures':4,'retained_body_host_checks':34,'retained_body_host_failures':0,'host_uses_UE_shim':True,'actual_writes':0,'UE_runs':0,'images_generated_or_viewed':0,'files':files,'file_count':len(files),'member_total_bytes':sum(r['bytes'] for r in files),'excluded':'This freeze file only; all members local relative snapshots'}
with OUT.open('x',encoding='utf-8',newline='\n') as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
b=OUT.read_bytes();print(json.dumps({'freeze':str(OUT),'bytes':len(b),'sha256':sha(b),'members':len(files),'projected_source':m['projected_source']}))
