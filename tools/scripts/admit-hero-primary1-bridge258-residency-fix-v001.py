from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001'
TARGET=R/'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,absolute=True):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(row):
 p=Path(row.get('path',''));p=p if p.is_absolute() else R/p
 assert pin(p)['bytes']==row['bytes'] and pin(p)['sha256']==row['sha256'];return p
ap=argparse.ArgumentParser();ap.add_argument('--freeze',required=True);ap.add_argument('--freeze-sha',required=True);ap.add_argument('--projected',required=True);ap.add_argument('--review',required=True);ap.add_argument('--review-sha',required=True);a=ap.parse_args()
freeze,projected,review=map(lambda p:Path(p).resolve(),(a.freeze,a.projected,a.review))
assert pin(freeze)['sha256']==a.freeze_sha and pin(review)['sha256']==a.review_sha and 'Approved' in review.read_text(encoding='utf-8-sig')
fr=read(freeze);members=fr.get('members',fr.get('files'));assert members and fr.get('FinalAccepted',False) is False
allrows=members+fr.get('dependency_pins',fr.get('dependencies',[]))
for _ in range(2):
 for row in allrows:
  if 'relative_path' in row:
   p=(freeze.parent/row['relative_path']).resolve();assert p.is_relative_to(freeze.parent);checked(dict(row,path=p.as_posix()))
  else:checked(row)
assert any((row['bytes'],row['sha256'])==(pin(projected)['bytes'],pin(projected)['sha256']) for row in members)
cm=R/'source-assets/production/backups/v146-Primary1Bridge258-303-1439-203GREEN-v001/compiled-source-manifest.json';assert pin(cm)['sha256']=='0943bc48284765015990b1621d5cd95046c450060030a59ad6f2025f17594fcd'
m=read(cm);oldadp=Path(m['source_admission_pin']['path']);checked(m['source_admission_pin']);oldad=read(oldadp)
for row in m['files']:checked(row)
assert pin(TARGET)['sha256']=='30b1db6503f8641bcac0165cfc134ae7e841b96f3f23b8d68b912a90696a2205'
assert pin(projected)['sha256']!=pin(TARGET)['sha256']
O=EV/'Root-source-residency-admission-v002';assert not O.exists();O.mkdir()
before=pin(TARGET,False);shutil.copy2(TARGET,O/('before-'+TARGET.name));TARGET.write_bytes(projected.read_bytes());assert TARGET.read_bytes()==projected.read_bytes()
after=pin(TARGET,False)
for _ in range(2):
 for row in m['files']:
  if row['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/')):assert pin(R/row['path'],False)==(after if row['path']==after['path'] else row)
assert sum(p.is_file() for p in (R/'UnrealGame/Source').rglob('*'))==303 and sum(p.is_file() for p in (R/'UnrealGame/Content/Production').rglob('*'))==1439
ad=dict(oldad);ad.update(utc=datetime.now(timezone.utc).isoformat(),superseded_source_admission=pin(oldadp),incremental_predecessor_compiled_manifest=pin(cm),incremental_before_files=[before],incremental_after_files=[after],actual_incremental_source_files_changed=1,actual_incremental_renderer_changed=False,UE_compiled=False,native_art_verified=False)
ad['source_candidate_freezes']=[oldad['source_candidate_freezes'][0],pin(freeze)];ad['fresh_source_reviews']=[oldad['fresh_source_reviews'][0],pin(review)]
ad['after_files']=[after if x['path']==after['path'] else x for x in oldad['after_files']]
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as f:json.dump(ad,f,ensure_ascii=False,indent=2)
print(json.dumps(pin(out)))
