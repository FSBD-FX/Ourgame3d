"""Create local immutable before/initial RED projection only; no game writes."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
path=ROOT/'UnrealGame/Source/CodexDungeon/DungeonHeroLandingPriorityProbeV001.cpp'
data=path.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(data)=='30b1db6503f8641bcac0165cfc134ae7e841b96f3f23b8d68b912a90696a2205'
for folder in ('before','projected','reports','fragments'):(HERE/folder).mkdir(exist_ok=False)
for folder in ('before','projected'):
 with (HERE/folder/path.name).open('xb') as f:f.write(data)
with (HERE/'before-source-pin.json').open('x',encoding='utf-8') as f:
 json.dump(dict(actual_before_path=path.as_posix(),local_before='before/'+path.name,bytes=len(data),sha256=sha(data),actual_source_written=False),f,indent=2)
print(json.dumps(dict(actual_before_sha256=sha(data),bytes=len(data),actual_source_written=False,UE_run=False)))
