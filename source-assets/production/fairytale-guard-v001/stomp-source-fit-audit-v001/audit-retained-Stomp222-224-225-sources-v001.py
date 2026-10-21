"""Read-only existing Stomp sources; writes new audit JSON only. No media or UE."""
from pathlib import Path
import hashlib,json
from PIL import Image
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
A=R/'source-assets/production/fairytale-guard-v001/art-preparation-v001'
O=Path(__file__).resolve().parent
DEFS=[
 (222,'StompWindup',A/'move221-stomp222-extraction-v001/stomp-windup6-six-curated-source-index-v001.json','2026-10-18-OurgameUE-guard221-222-native-v387','2026-10-18-OurgameUE-guard221-222-curated-v388'),
 (224,'StompActive',A/'stomp224-active2-extraction-v001/stomp224-active2-curated-source-index-v001.json','2026-10-18-OurgameUE-stomp224-raw-v398','2026-10-18-OurgameUE-stomp224-curated-v399'),
 (225,'StompRecovery',A/'stomp225-recovery4-extraction-v001/stomp225-recovery4-curated-source-index-v001.json','2026-10-18-OurgameUE-stomp-recovery225-raw-v405','2026-10-18-OurgameUE-stomp-recovery225-curated-v406'),
]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);v=pin(p);assert (v['bytes'],v['sha256'])==(row['bytes'],row['sha256']),p;return p
def retained(p,batch):
 m=E/batch/'source-size-SHA256.json';j=read(m)
 assert j['verification_passes']==2 and j['source_and_target_hash_mismatches']==0
 v=pin(p);matches=[x for x in j['files'] if x['bytes']==v['bytes'] and x['sha256']==v['sha256']]
 assert matches,(p,batch)
 candidates=[]
 for x in matches:
  ep=E/batch/Path(x['retained_relative']);assert ep.is_file();z=pin(ep)
  assert z['bytes']==v['bytes'] and z['sha256']==v['sha256'] and ep.read_bytes()==p.read_bytes()
  candidates.append(z)
 return dict(retention_manifest=pin(m),recorded_twoSHA_passes=2,recorded_hash_mismatches=0,current_exact_F_E_comparison=True,retained_files=candidates)
rows=[]
for sid,state,index,rawE,framesE in DEFS:
 j=read(index);raw=check(j['native_raw']);fs=[]
 for f in j['frames']:
  p=check(f['file'])
  with Image.open(p) as im:
   assert im.mode=='RGBA' and im.size==(512,512);rgba=hashlib.sha256(im.tobytes()).hexdigest();assert rgba==f['RGBA_sha256']
   fs.append(dict(frame=f['frame'],source=pin(p),RGBA_sha256=rgba,alpha_bbox=list(im.getchannel('A').getbbox()),retention=retained(p,framesE)))
 rows.append(dict(native_source_id=sid,state=state,index=pin(index),raw=pin(raw),raw_retention=retained(raw,rawE),shared_row_extraction=j['shared_row_fit'],frames=fs,actual_current_status='222 imported/scopedtrial;224/225 source accepted future candidates closed' if sid==222 else 'Source accepted future candidate; no trial admission',pixels_changed_by_this_audit=False))
out=dict(schema='Guard-Stomp222-224-225-retained-source-audit-v001',rows=rows,all12_curated_512RGBA_verified=True,all_raw_and_curated_F_E_exact=True,new_media_created=False,new_media_viewed=False,Source_Content_tools_ledger_modified=False,UE_or_generation_called=False,FinalAccepted=False)
p=O/'retained-source-inventory-v001.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(output=pin(p),rows=[dict(id=x['native_source_id'],raw=x['raw']['path'],curated0=x['frames'][0]['source']['path'],frames=len(x['frames'])) for x in rows]),ensure_ascii=False))
