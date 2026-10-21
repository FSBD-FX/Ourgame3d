"""Candidate-only immutable snapshots; actual Source is read-only."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
CM=ROOT/'source-assets/production/backups/v146-Primary1Bridge258-Residency-303-1439-203GREEN-v002/compiled-source-manifest.json'
assert hashlib.sha256(CM.read_bytes()).hexdigest()=='e08bf832e82c6af093650b7ebde3fa4fc25b59aa47bfe465bb239f7308292564'
rows={r['path']:r for r in json.loads(CM.read_text())['files']}
names=('DungeonActionAudioFeedback.h','DungeonWorldProjectiles.cpp','DungeonHUD.cpp','DungeonWeaponActions.h','DungeonContentCombat.h')
pins=[]
for name in names:
 rel='UnrealGame/Source/CodexDungeon/'+name;p=ROOT/rel;b=p.read_bytes();r=rows[rel]
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],('Actual source drift',name)
 out=HERE/'before'/name;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f:f.write(b)
 pins.append(dict(name=name,actual_path=p.as_posix(),local_path=out.relative_to(HERE).as_posix(),bytes=len(b),sha256=r['sha256']))
with (HERE/'before-source-pins.json').open('x',encoding='utf-8') as f:json.dump(pins,f,indent=2);f.write('\n')
print(json.dumps(dict(copied=len(pins),actual_source_written=False,compiled_manifest_sha256=hashlib.sha256(CM.read_bytes()).hexdigest())))
