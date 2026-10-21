"""Verify and admit only the independent normal-J StunIR observer."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-combat-death-candidate-v005'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
f=C/'Death-candidate-freeze-v005.json';assert sha(f)=='06feabca90c4e0f1a8bafe87584797072b5e3ed5760e58cfdef2f6faf71664f5'
for x in read(f)['files']:
 p=C/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
snapshot=R/'source-assets/production/backups/v134-StunIR-184G/compiled-source-manifest.json';m=read(snapshot)
for x in m['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==233
out=R/'docs/production/first-batch-v2/evidence/guard-Death-v005/root-admission-v001';assert not out.exists();(out/'before').mkdir(parents=True)
for p in [R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp',R/'docs/production/first-batch-v2/progress.json']:
 shutil.copy2(p,out/'before'/p.name)
for n in ['DungeonGuardArtDeathProbeV005.h','DungeonGuardArtDeathProbeV005.cpp']:
 p=C/'new-source'/n;q=R/'UnrealGame/Source/CodexDungeon'/n;assert not q.exists();shutil.copy2(p,q);os.utime(q,None);assert sha(p)==sha(q)
patch=C/'patches/minimal-HUD-Death-after-StunIR-v004-startup-v005.patch'
for mode in ['--check',None]:
 v=subprocess.run(['git','apply']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');(out/('HUD-check.log' if mode else 'HUD-apply.log')).write_text(v.stdout+v.stderr,encoding='utf-8');assert v.returncode==0
os.utime(R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp',None)
source=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()];assert len(source)==235
p=R/'docs/production/first-batch-v2/progress.json';v=read(p);v.update(current_source_uncompiled_changes=True,ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_snapshot_pending='v135 normal-J Death observer compile/full184/native pending');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'admission.json').write_text(json.dumps(dict(status='SOURCE_ADMITTED_COMPILE_NATIVE_PENDING',prior_compiled_snapshot=pin(snapshot),candidate=pin(f),source_files=235,production_files=1254,gameplay_changed=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_files=235,production_files=1254,observer_admitted=True,build_pending=True)))
