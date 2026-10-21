from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;OUT=HERE/'HeroLocomotionNativeObservation-freeze-v001.json';assert not OUT.exists()
files=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p!=OUT:
  b=p.read_bytes();files.append({'relative_path':p.relative_to(HERE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
m={'schema':'HeroLocomotionNativeObservationCandidateFreeze-v001','created_utc':datetime.now(timezone.utc).isoformat(),'status':'CANDIDATE_ONLY_NOT_ADMITTED_NOT_UE_COMPILED_NOT_RUN','base_compiled_manifest_sha256':'97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5','actual_writes':0,'UE_runs':0,'host_checks':18,'host_failures':0,'red_expected_failures':10,'all_members_are_local_candidate_snapshots':True,'files':files,'file_count':len(files),'member_total_bytes':sum(r['bytes'] for r in files),'excluded':'This freeze file only'}
with OUT.open('x',encoding='utf-8',newline='\n') as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
b=OUT.read_bytes();print(json.dumps({'freeze':str(OUT),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'members':len(files)}))
