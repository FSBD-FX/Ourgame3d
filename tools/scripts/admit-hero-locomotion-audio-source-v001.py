"""Root actual admission of the reviewed six-cue adapter; content import remains separate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/hero-locomotion-audio-binding-candidate-v001';O=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/Root-source-admission-v001'
def need(v,s):
 if not v:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,relative=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if relative else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def inventory(p):return {q.relative_to(R).as_posix() for q in p.rglob('*') if q.is_file()}
freeze=C/'HeroLocomotionAudioBindingCandidate-freeze-v001.json';need(pin(freeze)['sha256']=='08fe82025bf0da648730ca13e7a2164e88c773c606544ba18efdffa3e5eb4c39','Reviewed freeze differs')
review=R/'.superpowers/sdd/2026-10-19-hero-locomotion-audio-v145/task-1-source-import-review-v001.md';need(pin(review)['sha256']=='445298f33a3a83ad1fa275ab3005ce598c9bf812122ca9de4765d5e0dfeba414','Fresh review differs')
seams=C/'exact-seams.json';index=read(seams);cm=Path(index['base_compiled_source_manifest']);need(pin(cm)['sha256']==index['base_manifest_sha256']=='fb225bef1e9b2e3584a16d3eff192bd39587867b68c0fcdb525a4d876324e59a','Wrong current predecessor')
before=read(cm);source=inventory(R/'UnrealGame/Source');production=inventory(R/'UnrealGame/Content/Production')
need(source=={r['path'] for r in before['files'] if r['path'].startswith('UnrealGame/Source/')},'Source membership drift')
need(production=={r['path'] for r in before['files'] if r['path'].startswith('UnrealGame/Content/Production/')},'Production membership drift')
for _ in range(2):
 for row in read(freeze)['files']:
  actual=pin(C/row['relative_path']);need((actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256']),'Frozen candidate drift')
 for row in before['files']:need(pin(R/row['path'],True)==row,'Compiled predecessor drift: '+row['path'])
pending=[]
for name in index['new_source_files']:
 p=Path(name);dst=R/'UnrealGame/Source/CodexDungeon'/p.name;need(not dst.exists(),'New path occupied');pending.append((dst,p.read_bytes(),False))
for row in index['files']:
 p=Path(row['actual_source']).resolve();need(p.is_relative_to((R/'UnrealGame/Source').resolve()),'Overlay outside Source')
 b=p.read_bytes();need((len(b),hashlib.sha256(b).hexdigest())==(row['source_bytes'],row['source_sha256']),'Overlay before differs');text=b.decode('utf-8');nl='\r\n' if row['line_ending']=='CRLF' else '\n'
 for op in row['operations']:
  a=op['before'].replace('\n',nl);z=op['after'].replace('\n',nl);need(text.count(a)==1,'Overlay seam not unique');text=text.replace(a,z,1)
 b=text.encode('utf-8');need((len(b),hashlib.sha256(b).hexdigest())==(row['result_bytes'],row['result_sha256']),'Overlay after differs');pending.append((p,b,True))
need(len(pending)==len({p for p,_,_ in pending})==6,'Admission scope differs')
need(not O.exists(),'Preserve previous admission');O.mkdir(parents=True);(O/'before').mkdir();(O/'after-preview').mkdir()
for p,b,exists in pending:
 if exists:shutil.copy2(p,O/'before'/p.name)
 with (O/'after-preview'/p.name).open('xb') as f:f.write(b)
for p,b,exists in pending:
 if exists:p.write_bytes(b)
 else:
  with p.open('xb') as f:f.write(b)
added={p.relative_to(R).as_posix() for p,_,exists in pending if not exists};changed={p.relative_to(R).as_posix() for p,_,_ in pending};after=inventory(R/'UnrealGame/Source')
need(after==source|added,'Source membership after differs')
for _ in range(2):
 for row in before['files']:
  if row['path'] not in changed:need(pin(R/row['path'],True)==row,'Unrelated compiled input differs')
 for p,b,_ in pending:need(p.read_bytes()==b,'Applied bytes differ')
 need(inventory(R/'UnrealGame/Content/Production')==production,'Content import occurred during source admission')
result=dict(schema='Root-hero-locomotion-audio-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,source_candidate_freeze=pin(freeze),source_admit_index=pin(seams),predecessor_compiled_manifest=pin(cm),fresh_source_import_review=pin(review),actual_source_files=len(after),actual_production_files=len(production),new_source_files=len(added),after_files=[pin(p,True) for p,_,_ in pending],verification_passes=2,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,SoundWaves_imported=False,native_audio_verified=False,FinalAccepted=False)
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out),ensure_ascii=False))
