"""Admit two reviewed exact art seams after a clean exclusive fourteen-texture import."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction';EV=R/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);p=p if p.is_absolute() else R/p;a=pin(p);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),str(p)
def textbytes(s):return s.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
ap=argparse.ArgumentParser();ap.add_argument('--observer-review',required=True);ap.add_argument('--observer-review-sha',required=True);a=ap.parse_args()
review1=R/'.superpowers/sdd/2026-10-19-hero-locomotion-audio-v145/art258-import-binding-review-v001.md';review2=Path(a.observer_review).resolve()
assert pin(review1)['sha256']=='3315578d568df3d031e60484deaf96dcc1ac5c82bbe1f8d881ab63cd057fd7d4'
assert pin(review2)['sha256']==a.observer_review_sha and 'Approved' in review2.read_text(encoding='utf-8-sig')
f1=C/'UE-import-binding-candidate-v001/candidate-freeze-v001.json';f2=C/'native-observation-candidate-v001/candidate-freeze-v001.json'
assert pin(f1)['sha256']=='eaa11e20169bb6b53687671800100aa1eea1e703a29ec48ecb36ab55cbb0c6b9'
assert pin(f2)['sha256']=='0fcc6eb38e6675c48a6fa66811b371c3443e2570ce19ef6d7ddefaaf5b81c35e'
one=read(f1);two=read(f2);assert len(one['members'])==14 and len(one['dependency_pins'])==64 and two['file_count']==len(two['files'])==41
rows=one['members']+one['dependency_pins']+[dict(path=(f2.parent/x['relative_path']).resolve().as_posix(),bytes=x['bytes'],sha256=x['sha256']) for x in two['files']]
for _ in range(2):
 for row in rows:check(row)
cm=R/'source-assets/production/backups/v145-HeroLocomotionObserver303-1425-203GREEN-v001/compiled-source-manifest.json';assert pin(cm)['sha256']=='71e91acd625b9813be555f5b38012e9c7ae39727bb2bd35dc495e584865532ac';old=read(cm)
imp_path=EV/'Root-native-import-v001/import-receipt.json';ip=read(imp_path);exitp=EV/'Root-native-import-v001/exit-receipt-v001.json'
assert read(exitp)['exit_code']==0 and ip['success'] and ip['actual_count']==ip['saved_count']==len(ip['assets'])==14 and ip['old1425_unchanged'] and ip['final_production_count']==1439
added=[]
for x in ip['assets']:
 assert x['actual_class']=='Texture2D' and x['saved']['path'].startswith('F:/Ourgame/UnrealGame/Content/Production/ArtTrials/Request258/v001/HeroPrimary1Bridge/')
 check(x['saved']);added.append(pin(x['saved']['path']))
old_paths={row['path'] for row in old['files'] if row['path'].startswith('UnrealGame/Content/Production/')}
actual={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
assert len(actual)==1439 and actual==old_paths|{x['path'] for x in added}
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):check(row)
seam1=read(C/'UE-import-binding-candidate-v001/source/exact-seams-v001.json');seam2=read(C/'native-observation-candidate-v001/exact-seams.json')
targets=[Path(seam1['target']['path']),Path(seam2['historical_actual_source'])];before=[pin(p) for p in targets];projected=[]
for i,(target,ops) in enumerate(zip(targets,[seam1['seams'],seam2['operations']])):
 b=target.read_bytes()
 for op in ops:
  left=textbytes(op['before_text'] if 'before_text' in op else op['before']);right=textbytes(op['after_text'] if 'after_text' in op else op['after']);assert b.count(left)==1;b=b.replace(left,right,1)
 expected=Path(seam1['candidate_after']['path']) if i==0 else f2.parent/seam2['projected_source'];assert b==expected.read_bytes();projected.append(b)
O=EV/'Root-source-admission-v001';assert not O.exists();O.mkdir(parents=True)
for target,b in zip(targets,projected):shutil.copy2(target,O/('before-'+target.name));target.write_bytes(b)
after=[pin(p) for p in targets];changed={x['path']:x for x in after}
for _ in range(2):
 for row in old['files']:
  if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'])==changed.get(row['path'],row)
 for row in added:check(row)
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==303
content=O/'actual-content-admission.json'
with content.open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary1-bridge258-content-admission-v001',utc=datetime.now(timezone.utc).isoformat(),actual_import=pin(imp_path,True),actual_process=pin(exitp,True),old1425_unchanged=True,added=added,actual_production_files=1439,new_Texture2D_count=14,verification_passes=2,twoSHA_mismatches=0,FinalAccepted=False),f,ensure_ascii=False,indent=2)
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary1-bridge258-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,predecessor_compiled_manifest=pin(cm,True),source_candidate_freezes=[pin(f1,True),pin(f2,True)],fresh_source_reviews=[pin(review1,True),pin(review2,True)],content_admission_pin=pin(content,True),before_files=before,after_files=after,actual_source_files=303,actual_production_files=1439,new_source_files=0,verification_passes=2,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,native_art_verified=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True),ensure_ascii=False))
