"""Root adopt separate readonly native probe after production writer stops."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
C=B/'Death40-runtime-production-v001';N=B/'Death40-native-observer-candidate-v001';S=R/'UnrealGame/Source/CodexDungeon'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def check(x,base=R):
 p=Path(x['path']);p=p if p.is_absolute() else base/p
 assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
pf=C/'Death40-production-freeze-v001.json';nf=N/'Death-observer-source-freeze-v001.json'
assert sha(pf)=='132a326e6b29cf39622de30de040cc3a1a6fadb84a2bb4be12accab0e2121a90'
assert sha(nf)=='2d444f97205bb29f848723905fcbbf75b2c31ae0b7dc955c4069ad18bf9c558a'
p=read(pf);n=read(nf)
for x in p['files']:check(x,C)
for x in p['new_source_files']+p['existing_modified_files']:check(x)
for x in n['files']+n['actual_DTO_headers']:check(x)
red=Path(p['actual_semantic_RED_manifest']['path']);check(p['actual_semantic_RED_manifest'])
assert read(red)['focused_semantic_failed']==3
assert sha(S/'Tests/DungeonFairytaleSwordDeathV001Tests.cpp')==p['original_RED_tests_sha256']
assert len([q for q in (R/'UnrealGame/Source').rglob('*') if q.is_file()])==255
assert len([q for q in (R/'UnrealGame/Content/Production').rglob('*') if q.is_file()])==1326
proc=subprocess.run(['pwsh','-NoProfile','-Command',"@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True)
assert proc.returncode==0 and proc.stdout.strip()=='0'
out=R/'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-observer-admission-v001'
assert not out.exists();out.mkdir(parents=True)
shutil.copy2(S/'DungeonHUD.cpp',out/'DungeonHUD-before-observer.cpp')
shutil.copy2(R/'docs/production/first-batch-v2/progress.json',out/'progress-before.json')
patch=N/'patches/minimal-HUD-Death-observer-startup-v001.patch'
q=subprocess.run(['git','apply','--check',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8')
(out/'patch-check.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr
for q in (N/'new-source').glob('*'):
 d=S/q.name;assert not d.exists();shutil.copy2(q,d);os.utime(d,None);assert sha(q)==sha(d)
q=subprocess.run(['git','apply',str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8')
(out/'patch-apply.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr
os.utime(S/'DungeonHUD.cpp',None)
allsource={q.relative_to(R).as_posix():pin(q) for q in (R/'UnrealGame/Source').rglob('*') if q.is_file()}
prior=read(R/'source-assets/production/backups/v137-range187G/compiled-source-manifest.json')
old={x['path']:x for x in prior['files'] if x['path'].startswith('UnrealGame/Source/')}
new=[allsource[x] for x in sorted(set(allsource)-set(old))]
changed=[allsource[x] for x in sorted(set(old)&set(allsource)) if allsource[x]['sha256']!=old[x]['sha256']]
assert len(allsource)==257 and len(new)==11 and len(changed)==5 and not set(old)-set(allsource)
assert sha(S/'Tests/DungeonFairytaleSwordDeathV001Tests.cpp')==p['original_RED_tests_sha256']
receipt=dict(schema='Root-Death40-production-and-observer-source-admission-v001',production_freeze=pin(pf),observer_source_freeze=pin(nf),
 actual_semantic_RED_manifest=pin(red),source_files=257,production_files=1326,new_source_files=new,existing_modified_files=changed,
 old241_source_byte_unchanged=True,original_RED_tests_unchanged=True,actual_compiled=False,actual_native_verified=False,formal_complete_units=0)
(out/'source-admission-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
j=read(R/'docs/production/first-batch-v2/progress.json');j.update(current_source_uncompiled_changes=True,ue_current_working_source_compiled=False,ue_current_working_source_verified=False,
 current_snapshot_pending='Death40 production+real Guard lethal observer Source257/Production1326 admitted after actual three semantic RED; compile/GREEN190/native both sides pending',
 current_hero_Death40_source_admission=pin(out/'source-admission-v001.json'))
(R/'docs/production/first-batch-v2/progress.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(admitted=True,Source=257,Production=1326,new11_changed5=True,old241_unchanged=True,compile_native_pending=True)))
