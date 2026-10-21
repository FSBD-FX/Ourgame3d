"""Root applies reviewed callback observer candidate; current compiled296 retained."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p,relative=False):
 p=p.resolve();b=p.read_bytes();return dict(path=p.relative_to(R).as_posix() if relative else p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,s):
 if not v:raise ValueError(s)
ap=argparse.ArgumentParser();ap.add_argument('--candidate-freeze',required=True);ap.add_argument('--compiled-before',required=True);a=ap.parse_args()
fp=Path(a.candidate_freeze).resolve();cm=Path(a.compiled_before).resolve();f=read(fp);before=read(cm)
need(before['source_files']==296 and before['production_files']==1419 and before['passed']==203,'Actual296/full203 predecessor required')
for repeat in range(2):
 for row in before['files']:need(pin(R/row['path'],True)==row,'Actual compiled predecessor changed')
 for row in f['members']:
  p=Path(row['path']);p=p if p.is_absolute() else fp.parent/p;z=pin(p);need((z['bytes'],z['sha256'])==(row['bytes'],row['sha256']),'Candidate frozen bytes differ')
source=f['source_files'];names={'DungeonHeroAirProductionProbeV001.h','DungeonHeroAirProductionProbeV001.cpp','DungeonHUD.cpp'};need(len(source)==3 and {Path(r['path']).name for r in source}==names,'Exact reviewed observer source3 required')
O=EV/'Root-callback-ready-observer-admission-v002';need(not O.exists(),'Fresh admission required');(O/'before').mkdir(parents=True)
targets=[]
for row in source:
 src=Path(row['path']);src=src if src.is_absolute() else fp.parent/src;target=R/'UnrealGame/Source/CodexDungeon'/src.name
 shutil.copy2(target,O/'before'/target.name);targets.append((src,target,row))
for src,target,row in targets:target.write_bytes(src.read_bytes())
after=[pin(target,True) for src,target,row in targets]
for repeat in range(2):
 for (src,target,row),r in zip(targets,after):need((r['bytes'],r['sha256'])==(row['bytes'],row['sha256']) and pin(target,True)==r,'Actual admitted source mismatch')
need(sum(p.is_file() for p in (R/'UnrealGame/Source').rglob('*'))==296,'Source count changed')
report=dict(schema='Root-HeroAir6-callback-ready-source-admission-v002',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_applied=True,candidate_freeze=pin(fp),predecessor_compiled296=pin(cm),actual_source_files=296,actual_production_files=1419,after_files=after,verification_passes=2,byte_mismatches=0,scope='Observe real completed Ready callback before normal queued Space; no game physics/input API/test/asset changes',ue_compiled=False,native_core_flow_accepted=False,FinalAccepted=False)
p=O/'actual-source-admission.json'
with p.open('x',encoding='utf-8') as h:json.dump(report,h,ensure_ascii=False,indent=2)
print(json.dumps(pin(p)))
