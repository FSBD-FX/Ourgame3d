"""Root admission of frozen unsupported Hurt API + three semantic-red tests."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
R=Path('F:/Ourgame')
C=R/'source-assets/production/fairytale-hero-state-gap-v001/hurt-runtime-integration-candidate-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p): return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
freeze=C/'Hurt-stage0-freeze-v001.json'
assert sha(freeze)=='2a2f6c20d223dfe111a251670c3d76097a576ae7d14faca253aa1954e89b3b80'
for x in read(freeze)['files']:
 p=C/x['path']; assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
snapshot=R/'source-assets/production/backups/v135-Death-184G/compiled-source-manifest.json'
for x in read(snapshot)['files']:
 p=R/x['path']; assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],str(p)
archive=R/'过程图稿与视频/2026-10-18_石守卫正常军剑死亡与自动金币试样_native_left_v001'
assert read(archive/'index.json')['independent_passed']
assert read(archive/'原件/independent-Death-v005.json')['passed']
check=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True)
assert check.stdout.strip()=='0',check.stdout
out=R/'docs/production/first-batch-v2/evidence/Hurt-stage0-v001/root-admission-v001'
assert not out.exists(); (out/'before').mkdir(parents=True)
for p in [R/'UnrealGame/Source/CodexDungeon/DungeonFighter.h',R/'UnrealGame/Source/CodexDungeon/DungeonFighter.cpp',R/'docs/production/first-batch-v2/progress.json']:
 shutil.copy2(p,out/'before'/p.name)
patch=C/'patches/Fighter-readonly-Hurt-query-stage0-v001.patch'
for mode in ['--check',None]:
 v=subprocess.run(['git','apply']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8')
 (out/('patch-check.log' if mode else 'patch-apply.log')).write_text(v.stdout+v.stderr,encoding='utf-8'); assert v.returncode==0
files=sorted(p for p in (C/'new-source').rglob('*') if p.is_file()); assert len(files)==6
for p in files:
 q=R/'UnrealGame/Source/CodexDungeon'/p.relative_to(C/'new-source'); assert not q.exists()
 q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);os.utime(q,None);assert sha(q)==sha(p)
for n in ['DungeonFighter.h','DungeonFighter.cpp']: os.utime(R/'UnrealGame/Source/CodexDungeon'/n,None)
count=len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()]);assert count==241
p=R/'docs/production/first-batch-v2/progress.json';v=read(p)
v.update(current_source_uncompiled_changes=True,ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_snapshot_pending='Hurt Stage0 actual compile/three semantic RED pending; v135 Guard native Death PASS retained')
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'admission.json').write_text(json.dumps(dict(status='STAGE0_SOURCE_ADMITTED_COMPILE_AND_SEMANTIC_RED_PENDING',candidate=pin(freeze),prior_compiled_snapshot=pin(snapshot),source_files=count,production_files=1254,new_tests=3,gameplay_changed=False,production_selector_implemented=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_files=count,production_files=1254,stage0_admitted=True,semantic_RED_observed=False)))
