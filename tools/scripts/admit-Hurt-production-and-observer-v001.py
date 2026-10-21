"""Root narrow admission after actual three semantic RED and exact native32 import."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame'); B=R/'source-assets/production/fairytale-hero-state-gap-v001'
C=B/'hurt-runtime-production-candidate-v001';N=B/'hurt-native-observer-candidate-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x,base=R):
 p=Path(x['path']);p=p if p.is_absolute() else base/p
 assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
 return p
for f,want in [(C/'Hurt-production-freeze-v001.json','6837c8a2dbca431578781eb56e43afc9d0940b97bac744b7c632c4229f184f6a'),(N/'Hurt-observer-source-freeze-v001.json','c52e9bf398c128781eb00ca7b6b4400b8c36d228b5331abd1b17d22ae3bc9f03')]:
 assert sha(f)==want
 for x in read(f)['files']:check(x,f.parent)
check(read(N/'Hurt-observer-source-freeze-v001.json')['agreed_HUD_trace_header_at_source_freeze'])
stage0=read(R/'source-assets/production/backups/Hurt-stage0-actual-three-semantic-RED-v001/compiled-stage0-semantic-red-manifest.json')
assert stage0['focused_semantic_failed']==3 and not stage0['fixture_or_compile_failure']
for x in stage0['files']:check(x)
for x in read(C/'before-pins-v001.json')['files']:check(x)
rc=read(R/'UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json')
assert rc['success'] and rc['total_production_files']==1286 and len(rc['assets'])==32
v=read(B/'hurt-runtime-prepared-v002/validation-runs/independent-import-verification-20261018-080516-753883.json');assert v['success'] and v['exact_total']==1286 and v['new32_saved_twoSHA_unchanged'] and v['old1254_twoSHA_unchanged'];check(v['receipt'])
for a in rc['assets']:check(a['saved'])
q=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True);assert q.stdout.strip()=='0'
out=R/'docs/production/first-batch-v2/evidence/Hurt-production-v001/root-admission-v001';assert not out.exists();(out/'before').mkdir(parents=True)
for x in read(C/'before-pins-v001.json')['files']:
 p=R/x['path'];shutil.copy2(p,out/'before'/p.name)
shutil.copy2(R/'docs/production/first-batch-v2/progress.json',out/'before/progress.json')
def patch(p,label):
 for flag in ['--check',None]:
  v=subprocess.run(['git','apply']+([flag] if flag else [])+[str(p)],cwd=R,capture_output=True,text=True,encoding='utf-8')
  (out/(label+('-check.log' if flag else '-apply.log'))).write_text(v.stdout+v.stderr,encoding='utf-8');assert v.returncode==0,v.stderr
patch(C/'patches/Hurt-production-shared-plan-HUD-v001.patch','production')
for p in (C/'changed-source').glob('*'):assert sha(R/'UnrealGame/Source/CodexDungeon'/p.name)==sha(p)
for p in (C/'new-source').glob('*'):assert sha(R/'UnrealGame/Source/CodexDungeon'/p.name)==sha(p)
for p in (N/'new-source').glob('*'):
 d=R/'UnrealGame/Source/CodexDungeon'/p.name;assert not d.exists();shutil.copy2(p,d);assert sha(d)==sha(p)
patch(N/'patches/minimal-HUD-Hurt-observer-startup-v001.patch','observer')
changed=[R/'UnrealGame/Source/CodexDungeon'/p.name for folder in [C/'changed-source',C/'new-source',N/'new-source'] for p in folder.glob('*') if p.is_file()]
for p in changed:os.utime(p,None)
assert sha(R/'UnrealGame/Source/CodexDungeon/Tests/DungeonFairytaleSwordHurtV001Tests.cpp')=='046d7e632d48673ac9c68ba6f20b281f82478b49d7c839f616afb5b852c63ed1'
sources=[p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()];assert len(sources)==246
assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1286
p=R/'docs/production/first-batch-v2/progress.json';j=read(p);j.update(current_source_uncompiled_changes=True,ue_current_working_source_compiled=False,ue_current_working_source_verified=False,current_snapshot_pending='Hurt production sharedPlan/HUD and normalGuardHit observer admitted246; actual build/3GREEN/full187/native pending');p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'admission.json').write_text(json.dumps(dict(status='NARROW_SOURCE_ADMITTED_AFTER_ACTUAL_SEMANTIC_RED_IMPORT32',source_files=246,production_files=1286,actual_three_semantic_RED_retained=True,tests_unchanged=True,production_freeze=pin(C/'Hurt-production-freeze-v001.json'),observer_source_freeze=pin(N/'Hurt-observer-source-freeze-v001.json'),admitted_source_files=[pin(p) for p in changed],actual_UE_compiled=False,actual_Hurt_render_verified=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_files=246,production_files=1286,production_and_observer_admitted=True,build_pending=True)))
