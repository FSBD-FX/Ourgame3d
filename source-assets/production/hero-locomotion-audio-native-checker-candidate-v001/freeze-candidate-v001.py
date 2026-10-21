"""Freeze only this NEW checker directory and its exact read-only dependencies."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE=Path(__file__).resolve().parent
def row(path):
    return dict(path=path.as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
target=HERE/'HeroLocomotionNativeChecker-freeze-v001.json'
assert not target.exists()
members=[row(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
deps=json.loads((HERE/'dependencies-v001.json').read_text(encoding='utf-8-sig'))['members']
for x in members+deps:
    p=Path(x['path']);assert p.is_file() and p.stat().st_size==x['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
value=dict(schema='HeroLocomotionNativeCheckerCandidateFreeze-v001',utc=datetime.now(timezone.utc).isoformat(),
           members=members,dependency_pins=deps,member_count=len(members),dependency_pin_count=len(deps),
           host_tests=13,host_failures=0,actual_Source_Content_tools_mutations=0,UE_started=False,
           source_audio_WAV_or_PCM_constructed=False,new_media_viewed=False,new_native_verified=False,FinalAccepted=False)
with target.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(row(target)))
