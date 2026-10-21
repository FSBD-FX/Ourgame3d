"""Admit only frozen actual-draw instrumentation and independent Stomp observer."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001/stomp-native-proof-candidate-v001'
F=B/'Stomp-native-source-freeze-v001.json';V=B/'source-boundary-fix-v002/Stomp-source-boundary-fix-freeze-v002.json'
O=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/observer-admission-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x,base=B):
    p=Path(x['path']);p=p if p.is_absolute() else base/p
    assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
assert sha(F)=='621729befcb020e38185f84df8e6ee29b776220c80e768780f715595b359b710'
assert sha(V)=='fc0bea2e02ad5d0ce9dea027520a85130a7704c870f42ad453b50cfeaf79a8c8'
for x in read(F)['files']+read(V)['files']:check(x)
for x in read(B/'exact-before-pins-v001.json')['files']:check(x)
snapshot=R/'source-assets/production/backups/v139-Stomp-Stage0-three-semantic-RED-v001/compiled-source-manifest.json'
old=[x for x in read(snapshot)['files'] if x['path'].startswith('UnrealGame/Source/')]
assert len(old)==260
for x in old:check(x,R)
patches=sorted((B/'patches').glob('*.patch'));assert len(patches)==3
cmd=['git','apply','--unidiff-zero']
result=subprocess.run(cmd+['--check']+[str(p) for p in patches],cwd=R,capture_output=True,text=True)
assert result.returncode==0,result.stderr
news=[B/'new-source/DungeonGuardStompProbeV001.h',B/'source-boundary-fix-v002/DungeonGuardStompProbeV001.cpp']
assert all(not (R/'UnrealGame/Source/CodexDungeon'/p.name).exists() for p in news)
assert not O.exists();O.mkdir(parents=True)
rec=dict(schema='Root-GuardStomp-observer-admission-v001',utc=datetime.now(timezone.utc).isoformat(),
         source_freeze=pin(F),same_Aid2_Ready_fix=pin(V),stage0_snapshot=pin(snapshot),success=False,
         native_render_verified=False,FinalAccepted=False)
try:
    result=subprocess.run(cmd+[str(p) for p in patches],cwd=R,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    for p in news:
        target=R/'UnrealGame/Source/CodexDungeon'/p.name;shutil.copy2(p,target);assert sha(p)==sha(target)
    changed={'UnrealGame/Source/CodexDungeon/'+s for s in [
        'DungeonFairytaleGuardFullDrawStateV003.h','DungeonFairytaleGuardFullPresentationV003.cpp','DungeonHUD.cpp']}
    for x in old:
        if x['path'] not in changed:check(x,R)
    assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==262
    rec.update(success=True,Source_count=262,Production_count=1326,
               unaffected_old_Source257_unchanged=True,
               admitted=[pin(R/p) for p in sorted(changed)]+[pin(R/'UnrealGame/Source/CodexDungeon'/p.name) for p in news])
except Exception as e:rec['failure']=str(e);raise
finally:
    with (O/'admission-receipt-v001.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(success=True,Source262=True,receipt=pin(O/'admission-receipt-v001.json'))))
