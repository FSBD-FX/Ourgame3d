"""Root reviewed admission of five Air semantic sources and two QA audio sources."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame'); S=R/'UnrealGame/Source/CodexDungeon'
C=R/'source-assets/production/fairytale-hero-air-v001/runtime-candidate-v001/stage0'
A=R/'source-assets/production/fairytale-hero-air-v001/audio-capture-helper-candidate-v001'
O=R/'docs/production/first-batch-v2/evidence/HeroAir6-v142-v001/stage0-and-audio-admission-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p): return dict(path=p.relative_to(R).as_posix(), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(base,x):
    p=base/x['path']; assert (p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),p
    return p
cf=C/'HeroAir-Stage0-candidate-freeze-v001.json'; af=A/'native-main-submix-capture-helper-freeze-v001.json'
assert pin(cf)['sha256']=='37513295d00ee57f1726260c0da10a296e378962cb1d4cbe21bb6e3010d42c2a'
assert pin(af)['sha256']=='91e1a74f78dcf1b712d121930da8e08e3543254d4227d43c2b774df730089c3e'
for base,f,key in [(C,cf,'members'),(A,af,'files')]:
    for _ in range(2):
        for x in read(f)[key]: check(base,x)
cm=R/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json'
assert pin(cm)['sha256']=='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
old=read(cm); before=[pin(p) for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()]
assert len(before)==283
assert {x['path']:x for x in before}=={x['path']:x for x in old['files'] if x['path'].startswith('UnrealGame/Source/')}
production=[x for x in old['files'] if x['path'].startswith('UnrealGame/Content/Production/')]
assert len(production)==1371 and len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1371
for x in production: check(R,x)
index=read(C/'stage0-admission-index-v001.json'); maps=index['files']
assert len(maps)==8 and sum(x['kind']=='new' for x in maps)==5
maps=[dict(x,base=C) for x in maps]+[dict(kind='new',candidate='new-source/'+n,actual='UnrealGame/Source/CodexDungeon/'+n,base=A) for n in ['DungeonNativeMainSubmixCaptureV001.h','DungeonNativeMainSubmixCaptureV001.cpp']]
assert not O.exists();(O/'before').mkdir(parents=True)
for x in maps:
    src=x['base']/x['candidate'];dst=R/x['actual'];assert src.is_file()
    if x['kind']=='new': assert not dst.exists(),dst
    else: shutil.copy2(dst,O/'before'/dst.name)
(O/'before-Source283-pins-v001.json').write_text(json.dumps(before,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=dict(schema='Root-HeroAir6-Stage0-audio-admission-v001',utc=datetime.now(timezone.utc).isoformat(),success=False,source_before=283,source_after=290,production=1371,registered_tests_expected=203,old200_test_bytes_unchanged=True,semantic_red_verified=False,compiled=False,root_independent_static_review='All five Air sources, all three complete real-input semantic test groups, three narrow seams and audio helper read. Air explicitly remains stubbed; no physics, state priority, source art, save or existing production behavior altered.',candidate_freezes=[pin(cf),pin(af)],formal_complete_units=0,completed_combinations=0)
try:
    for x in maps:
        dst=R/x['actual'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(x['base']/x['candidate'],dst)
    touched={x['actual'] for x in maps if x['kind']=='existing'}
    for x in before:
        if x['path'] not in touched:check(R,x)
    after=[pin(p) for p in sorted((R/'UnrealGame/Source').rglob('*')) if p.is_file()];assert len(after)==290
    for x in maps: assert pin(R/x['actual'])['sha256']==pin(x['base']/x['candidate'])['sha256']
    receipt.update(success=True,admitted=[pin(R/x['actual']) for x in maps],unaffected_source_unchanged=True,production_unchanged=True)
finally:
    (O/'admission-receipt-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(success=receipt['success'],Source=290,Production=1371,receipt=pin(O/'admission-receipt-v001.json')),ensure_ascii=False))
