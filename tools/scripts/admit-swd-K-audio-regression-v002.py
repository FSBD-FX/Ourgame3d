from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-sword-secondary-v001/forward-step-regression-candidate-v001';O=R/'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-forward-step-regression-source-admission-v001'
ap=argparse.ArgumentParser();ap.add_argument('--review',required=True);ap.add_argument('--review-sha',required=True);a=ap.parse_args()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,rel=False):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if rel else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);p=p if p.is_absolute() else R/p;assert (pin(p)['bytes'],pin(p)['sha256'])==(row['bytes'],row['sha256']),p
review=Path(a.review).resolve();assert pin(review)['sha256']==a.review_sha and 'Approved' in review.read_text(encoding='utf-8')
freeze=C/'candidate-freeze-v001.json';assert pin(freeze)['sha256']=='397dff7ea8420c1771018cc8ce644fbfbf17cf5c0149c75f78c14777a02a8ee2';f=read(freeze)
cm=R/'source-assets/production/backups/v147-SWDStepAudio303-1439-202G1RED-v001/compiled-source-manifest.json';assert pin(cm)['sha256']=='fb8e5ad2ea8e0f5996ee2e55e447c3ce9a4dfb9b550d9f33bd30bda4f3ff7152';old=read(cm)
for _ in range(2):
 for row in f['members']+f['dependency_pins']+old['files']:check(row)
seam=read(C/'exact-seams-v001.json');target=R/seam['path'];before=target.read_bytes();assert (len(before),hashlib.sha256(before).hexdigest())==(seam['before']['bytes'],seam['before']['sha256']);text=before.decode('utf-8');nl='\r\n' if b'\r\n' in before else '\n'
for op in seam['operations']:
 l=op['anchor'].replace('\n',nl);addition=op['addition'].replace('\n',nl);assert text.count(l)==1
 kind=op['kind'];assert kind in ('insert_before','insert_after','replace')
 r=addition+l if kind=='insert_before' else l+addition if kind=='insert_after' else addition
 text=text.replace(l,r,1)
after=text.encode('utf-8');assert after==(C/'projected'/seam['path']).read_bytes();assert (len(after),hashlib.sha256(after).hexdigest())==(25019,'7f74bfeaea90044925495c801b935be4beccc90d8ed3b944a157101aa109d75b')
assert not O.exists();O.mkdir(parents=True);shutil.copy2(target,O/('before-'+target.name));bp=pin(target,True);target.write_bytes(after);applied=pin(target,True)
for row in old['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'],True)==(applied if row['path']==applied['path'] else row)
out=O/'actual-source-admission.json';out.write_text(json.dumps(dict(schema='Root-K-audio-strict-provenance-regression-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,actual_applied=True,is_template=False,predecessor_compiled_manifest=pin(cm),source_candidate_freeze=pin(freeze),fresh_source_review=pin(review),before_files=[bp],after_files=[applied],actual_source_files=303,actual_production_files=1439,new_source_files=0,new_test_IDs=0,old203_IDs_preserved=True,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,regression_GREEN=False,native_audio_verified=False,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(out),ensure_ascii=False))
