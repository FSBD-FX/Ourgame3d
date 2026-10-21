"""Root admission of independently reviewed opt-in landing observer; no UE or gameplay changes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/landing-priority-observer-candidate-v001';O=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/Root-source-admission-v001'
def need(v,s):
 if not v:raise ValueError(s)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,relative=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if relative else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
freeze=C/'HeroLandingPriority-Task1-source-freeze-v001.json';need(pin(freeze)['sha256']=='cb6e2ac79240ce6a5477b237b6796414182bb0388b2285d1df5135b4e5c4c9d8','Task1 source freeze changed')
for repeat in range(2):
 for row in read(freeze)['members']:
  p=Path(row['path']);z=pin(p);need((z['bytes'],z['sha256'])==(row['bytes'],row['sha256']),'Frozen source member changed')
ixpath=C/'Task1-Root-source-admit-index-v001.json';need(pin(ixpath)['sha256']=='7a1902c4b897d5b6ca817cccb5c8f0e516f2d551a82469df88e57a6e4ebc081c','Admit index changed');ix=read(ixpath)
cm=Path(ix['predecessor_compiled_manifest_pin']['path']);need(pin(cm)['sha256']=='52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62','Wrong predecessor CM');d=read(cm)
before={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};expected={x['path'] for x in d['files'] if x['path'].startswith('UnrealGame/Source/')};need(before==expected and len(before)==296,'Actual Source membership drift')
prod={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()};need(prod=={x['path'] for x in d['files'] if x['path'].startswith('UnrealGame/Content/Production/')} and len(prod)==1419,'Actual Production membership drift')
for repeat in range(2):
 for row in d['files']:need(pin(R/row['path'],True)==row,'Current compiled input drift '+row['path'])
stable=R/'Playables/钟盔轻甲-v142-CM52f906/_proof/Root-stable-approval-v001.json';sa=read(stable);need(sa['RootApproved'] is True and sa['manual_trial_allowed'] is True and sa['Root_staged_visible_keyframes_reviewed'] is True,'Preserve approved actual native stable preview first')
review=R/'.superpowers/sdd/2026-10-19-hero-landing-priority-v143/task-1-scoped-review-fix1-v001.md';need(review.is_file(),'Fresh scoped source review required')
pending=[]
for row in ix['new_source']:
 p=R/row['target'];need(not p.exists(),'New source path occupied');src=Path(row['candidate_pin']['path']);need(pin(src)['sha256']==row['candidate_pin']['sha256'],'New source bytes drift');pending.append((p,src.read_bytes(),False))
for row in ix['existing_source_edits']:
 p=R/row['target'];need(pin(p,True)==row['before_pin'],'Shared source predecessor drift');b=p.read_bytes()
 for e in row['edits']:
  needle=e['needle'].encode('utf-8');need(b.count(needle)==e['expected_occurrences']==1,'Shared seam not unique');b=b.replace(needle,e['replacement'].encode('utf-8'),1)
 need((len(b),hashlib.sha256(b).hexdigest())==(row['after_bytes'],row['after_sha256']),'Planned source delta differs');pending.append((p,b,True))
need(not O.exists(),'Preserve previous admission');O.mkdir(parents=True);(O/'before').mkdir();(O/'after-preview').mkdir()
for p,b,exists in pending:
 if exists:shutil.copy2(p,O/'before'/p.name)
 with (O/'after-preview'/p.name).open('xb') as f:f.write(b)
for p,b,exists in pending:
 if exists:p.write_bytes(b)
 else:
  with p.open('xb') as f:f.write(b)
after={p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()};need(after==before|{x['target'] for x in ix['new_source']},'Unexpected Source inventory change')
changed={p.relative_to(R).as_posix() for p,_,_ in pending}
for repeat in range(2):
 for row in d['files']:
  if row['path'] not in changed:need(pin(R/row['path'],True)==row,'Unrelated compiled input drift')
 for p,b,_ in pending:need(p.read_bytes()==b,'Admitted Source bytes drift')
result=dict(schema='Root-hero-landing-priority-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,source_candidate_freeze=pin(freeze),source_admit_index=pin(ixpath),predecessor_compiled_manifest=pin(cm),fresh_scoped_source_review=pin(review),actual_stable_preview_approval=pin(stable),actual_source_files=len(after),actual_production_files=len(prod),new_source_files=ix['expected_new_source_delta'],after_files=[pin(p,True) for p,_,_ in pending],verification_passes=2,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,native_landing_actions_reviewed=False,FinalAccepted=False)
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out),ensure_ascii=False))
