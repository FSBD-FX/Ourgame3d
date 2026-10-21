from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;OUT=HERE/'candidate-freeze-v001.json';assert not OUT.exists();rows=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p!=OUT:
  b=p.read_bytes();rows.append({'relative_path':p.relative_to(HERE).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
m={'schema':'request258-native-observation-candidate-freeze-v001','created_utc':datetime.now(timezone.utc).isoformat(),'status':'CANDIDATE_ONLY_NOT_ADMITTED_NOT_UE_COMPILED_NOT_RUN','actual_before_source_sha256':'e73bb9df5e3b95d1dcf16152e945f0efeb90ffc4c522a89b3c6a2d06cc71a422','binding_candidate_freeze_sha256':'eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9','host_checks':34,'host_failures':0,'red_expected_failures':6,'host_uses_UE_shim':True,'actual_writes':0,'UE_runs':0,'images_generated_or_viewed':0,'files':rows,'file_count':len(rows),'member_total_bytes':sum(r['bytes'] for r in rows),'excluded':'This freeze file only; all member bytes local to candidate'}
with OUT.open('x',encoding='utf-8',newline='\n') as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
b=OUT.read_bytes();print(json.dumps({'freeze':str(OUT),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'members':len(rows)}))
