"""Admit frozen bounded Stomp Stage0; real three semantic REDs are next."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, subprocess
R=Path('F:/Ourgame')
B=R/'source-assets/production/fairytale-guard-v001/stomp-runtime-gap-audit-v001'
F=B/'Stomp-runtime-gap-audit-and-stage0-freeze-v001.json'
O=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/stage0-admission-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x, base=R):
    p=base/x['path']; assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
assert sha(F)=='33d7dc3a83f0783794e1bc5253413b37bc7b60302fa58935b7a20eb2c86e03f6'
f=read(F)
for x in f['members']: check(x,B)
oldmanifest=R/'source-assets/production/backups/v138-HeroDeath190G/compiled-source-manifest.json'
old=[x for x in read(oldmanifest)['files'] if x['path'].startswith('UnrealGame/Source/')]
assert len(old)==257
for x in old: check(x)
assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1326
patchrows=read(B/'candidate/patch-inputs-and-expected-normalized-output.json')
for x in patchrows: check(x['actual_before_pin']); check(x['patch'])
patches=[str(R/x['patch']['path']) for x in patchrows]
cmd=['git','apply','-p0','--ignore-space-change']
checkresult=subprocess.run(cmd+['--check']+patches,cwd=R,capture_output=True,text=True)
assert checkresult.returncode==0,checkresult.stderr
newroot=B/'candidate/stage0/new-source'
news=sorted(p for p in newroot.rglob('*') if p.is_file()); assert len(news)==3
assert all(not (R/'UnrealGame/Source/CodexDungeon'/p.relative_to(newroot)).exists() for p in news)
assert not O.exists();O.mkdir(parents=True)
receipt=dict(schema='Root-GuardStomp-Stage0-admission-v001',utc=datetime.now(timezone.utc).isoformat(),
             candidate_freeze=pin(F),old_snapshot=pin(oldmanifest),success=False,
             real_semantic_RED_verified=False,FinalAccepted=False)
try:
    applied=subprocess.run(cmd+patches,cwd=R,capture_output=True,text=True)
    assert applied.returncode==0,applied.stderr
    for p in news:
        d=R/'UnrealGame/Source/CodexDungeon'/p.relative_to(newroot);d.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,d);assert sha(p)==sha(d)
    for x in patchrows:
        p=R/x['target']
        normalized=p.read_text(encoding='utf-8').replace('\r\n','\n')
        assert hashlib.sha256(normalized.encode()).hexdigest()==x['normalized_after_sha256'],p
    changed={x['target'] for x in patchrows}
    for x in old:
        if x['path'] not in changed:check(x)
    source=list((R/'UnrealGame/Source').rglob('*')); source=[p for p in source if p.is_file()]
    assert len(source)==260
    receipt.update(success=True,Source_count=260,Production_count=1326,
                   old_unaffected_Source253_byte_unchanged=True,
                   admitted=[pin(R/x['target']) for x in patchrows]+[pin(R/'UnrealGame/Source/CodexDungeon'/p.relative_to(newroot)) for p in news])
except Exception as e:
    receipt['failure']=str(e);raise
finally:
    with (O/'admission-receipt-v001.json').open('x',encoding='utf-8') as out:json.dump(receipt,out,ensure_ascii=False,indent=2)
print(json.dumps(dict(success=True,Source260=True,Production1326=True,receipt=pin(O/'admission-receipt-v001.json'))))
