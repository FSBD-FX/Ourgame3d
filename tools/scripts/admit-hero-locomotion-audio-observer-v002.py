from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=False):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
ap=argparse.ArgumentParser();ap.add_argument('--candidate-freeze',required=True);ap.add_argument('--candidate-file',required=True);ap.add_argument('--review',required=True);ap.add_argument('--review-sha',required=True);a=ap.parse_args()
candidate=Path(a.candidate_file).resolve();freeze=Path(a.candidate_freeze).resolve();review=Path(a.review).resolve()
assert pin(review,True)['sha256']==a.review_sha and ('Approved' in review.read_text(encoding='utf-8-sig'))
f=read(freeze)
assert f['schema']=='HeroLocomotionNativeObservationCandidateFreeze-v001' and f['file_count']==len(f['files'])==31
rows=[dict(path=(freeze.parent/x['relative_path']).resolve().as_posix(),bytes=x['bytes'],sha256=x['sha256']) for x in f['files']]
assert all(Path(x['path']).is_relative_to(freeze.parent) for x in rows)
assert any(Path(row['path']).resolve()==candidate and row['sha256']==pin(candidate,True)['sha256'] for row in rows)
for _ in range(2):
 for row in rows:
  actual=pin(row['path'],True);assert (actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256'])
cm=R/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/compiled-source-manifest.json'
assert pin(cm)['sha256']=='97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5'
d=read(cm);target=R/'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp'
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==303
assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1425
for row in d['files']:
 if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'])==row
O=EV/'Root-observer-source-admission-v001';assert not O.exists();O.mkdir()
before=pin(target);shutil.copy2(target,O/'before.cpp');shutil.copy2(candidate,O/'after-preview.cpp')
target.write_bytes(candidate.read_bytes());after=pin(target)
for _ in range(2):
 for row in d['files']:
  if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'])==(after if row['path']==after['path'] else row)
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as outstream:json.dump(dict(schema='Root-hero-locomotion-audio-observer-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,predecessor_compiled_manifest=pin(cm,True),source_candidate_freeze=pin(freeze,True),fresh_source_review=pin(review,True),after_files=[after],before_files=[before],actual_source_files=303,actual_production_files=1425,new_source_files=0,verification_passes=2,unrelated_source_tests_content_byte_mismatches=0,UE_compiled=False,native_audio_verified=False,FinalAccepted=False),outstream,ensure_ascii=False,indent=2)
print(json.dumps(pin(out,True),ensure_ascii=False))
