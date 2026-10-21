from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-sword-secondary-v001/forward-step-audio-candidate-v001';O=R/'docs/production/first-batch-v2/evidence/HeroSwordSecondary-v147-v001/Root-forward-step-audio-source-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,rel=False):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if rel else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);p=p if p.is_absolute() else R/p;assert (pin(p)['bytes'],pin(p)['sha256'])==(row['bytes'],row['sha256']),p
freeze=C/'candidate-freeze-v001.json';assert pin(freeze)['sha256']=='682d92a7c22fcfe28a7c94970cd36ee63a47c81edf312a4a0fedc265e30a5bae'
review=R/'.superpowers/sdd/2026-10-19-swd-secondary-v147/K-forward-step-audio-review-v001.md';assert pin(review)['sha256']=='b37cda77486ff67eaa7c3b8b3dbbaf5dcecc8c65caf4e0c7195c07b973fce66a'
cm=R/'source-assets/production/backups/v146-Primary1Bridge258-Residency-303-1439-203GREEN-v002/compiled-source-manifest.json';assert pin(cm)['sha256']=='e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564';old=read(cm)
f=read(freeze)
for _ in range(2):
 for row in f['members']+f['dependencies']:check(row)
 for row in old['files']:check(row)
subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'),'-B','-X','utf8',str(C/'check-candidate.py'),'--against-current'],check=True,cwd=R)
index=read(C/'exact-seams.json');pending=[]
for row in index['files']:
 target=R/'UnrealGame/Source/CodexDungeon'/row['name'];before=target.read_bytes();assert before==(C/row['before']).read_bytes()
 text=before.decode('utf-8');nl='\r\n' if row['line_ending']=='CRLF' else '\n'
 for op in row['operations']:
  a=op['before'].replace('\n',nl);b=op['after'].replace('\n',nl);assert text.count(a)==1;text=text.replace(a,b,1)
 after=text.encode('utf-8');assert after==(C/row['projected']).read_bytes();pending.append((target,before,after))
assert len(pending)==3 and not O.exists();O.mkdir(parents=True);(O/'before').mkdir()
for p,before,after in pending:shutil.copy2(p,O/'before'/p.name)
beforepins=[pin(p,True) for p,_,_ in pending]
for p,_,after in pending:p.write_bytes(after)
afterpins=[pin(p,True) for p,_,_ in pending];changed={x['path']:x for x in afterpins}
for _ in range(2):
 for row in old['files']:
  if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'],True)==changed.get(row['path'],row)
 assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==303
 assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1439
out=O/'actual-source-admission.json';out.write_text(json.dumps(dict(schema='Root-SWD001-K-postcommit-forward-step-audio-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,actual_applied=True,is_template=False,predecessor_compiled_manifest=pin(cm),source_candidate_freeze=pin(freeze),fresh_source_review=pin(review),before_files=beforepins,after_files=afterpins,actual_source_files=303,actual_production_files=1439,new_source_files=0,verification_passes=2,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,native_audio_verified=False,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(pin(out),ensure_ascii=False))
