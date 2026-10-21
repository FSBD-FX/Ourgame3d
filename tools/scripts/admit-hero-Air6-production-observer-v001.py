"""Root admission of a separate opt-in observer after actual294/full203 GREEN."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-hero-air-v001/production-observer-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/Root-production-observer-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,absolute=True):
 b=p.read_bytes();return dict(path=p.as_posix() if absolute else p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,s):
 if not v:raise ValueError(s)
ap=argparse.ArgumentParser();ap.add_argument('--compiled294',required=True);a=ap.parse_args()
cm=Path(a.compiled294).resolve();d=read(cm);need(d['source_files']==294 and d['production_files']==1419 and d['passed']==203 and d['failed']==0 and d['notRun']==0,'Actual294 strict203GREEN required')
q=read(Path(d['full_suite']['path']));need(tuple(q[k] for k in ['succeeded','succeededWithWarnings','failed','notRun','inProcess'])==(203,0,0,0,0),'Full203 suite not strictly GREEN')
need(sum(p.is_file() for p in (R/'UnrealGame/Source').rglob('*'))==294,'Actual source count drift')
for repeat in range(2):
 for row in d['files']:need(pin(R/row['path'],False)==row,'Compiled294 input changed')
fp=C/'HeroAir-production-observer-source-freeze-v001.json';need(pin(fp)['sha256']=='e7b9f44fe53fa2c827d962b359494badf2efbf1ffb8d2e2face8dd2449fa6140','Reviewed observer freeze changed');f=read(fp);need(len(f['members'])==14,'Observer freeze member count changed')
for repeat in range(2):
 for row in f['members']:need(pin(Path(row['path']))==row,'Frozen observer member changed')
names=['DungeonHeroAirProductionProbeV001.h','DungeonHeroAirProductionProbeV001.cpp','DungeonHUD.cpp'];targets=[R/'UnrealGame/Source/CodexDungeon'/n for n in names]
need(all(not p.exists() for p in targets[:2]),'New observer path occupied')
need(pin(targets[2])['sha256']=='6f86936c6a4c7b26afb812d585334a4a4bf471f0182295f94ae6374e9fb17bd5','HUD is not admitted full-production predecessor')
need(not O.exists(),'Fresh observer Root admission required');O.mkdir()
shutil.copy2(targets[2],O/'before-DungeonHUD.cpp')
for name,p in zip(names,targets):p.write_bytes((C/'new-source'/name).read_bytes())
need(sum(p.is_file() for p in (R/'UnrealGame/Source').rglob('*'))==296,'Expected actual296 Source')
after=[pin(p,False) for p in targets]
for repeat in range(2):
 for row in after:need(pin(R/row['path'],False)==row,'Actual observer bytes changed')
report=dict(schema='Root-HeroAir6-production-observer-source-admission-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,candidate_freeze=pin(fp),predecessor_compiled294=pin(cm),actual_source_files=296,actual_production_files=1419,after_files=after,ue_compiled=False,new_air_native_reviewed=False,verification_passes=2,source_byte_mismatches=0,FinalAccepted=False)
out=O/'actual-source-admission.json'
with out.open('x',encoding='utf-8') as h:json.dump(report,h,ensure_ascii=False,indent=2)
print(json.dumps(pin(out)))
