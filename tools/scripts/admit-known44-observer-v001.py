"""Preserve current production inputs, then admit the independent first-Axe observer."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-observer-candidate-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
out=R/'docs/production/first-batch-v2/evidence/guard-full-v004/root-known44-observer-admission-v001'
assert not out.exists();out.mkdir(parents=True)
freeze=C/'known44-AxeCycle-freeze-v001.json'
assert sha(freeze)=='7960a7760a870070e30ada80a5d7f10728a6d8f7e2f846247a12fb8931993cae'
for row in read(freeze)['files']:
 p=C/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
sources=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());assert len(sources)==229
suite=R/'UnrealGame/Saved/Automation/FirstRoom-20261018-125540/index.json';s=read(suite)
assert s['succeeded']==3 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in s['tests'])
build=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(build);assert b['ExitCode']==0 and '125243' in b['Log']
files=sources+[suite,build,Path(b['Log']),R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll',Path(__file__)]
rows=[]
for p in files:
 row=pin(p);q=out/'before/files'/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);rows.append(row)
for repeat in range(2):
 for row in rows:
  p=R/row['path'];q=out/'before/files'/row['path'];assert pin(p)==row and q.stat().st_size==row['bytes'] and sha(q)==row['sha256']
(out/'before/manifest.json').write_text(json.dumps(dict(status='ACTUAL_FULL_SELECTOR_3_GREEN_BEFORE_OBSERVER',files=rows,verification_passes=2),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['DungeonGuardArtKnown44Probe.h','DungeonGuardArtKnown44Probe.cpp']:
 p=C/'new-source'/name;q=R/'UnrealGame/Source/CodexDungeon'/name;assert not q.exists();shutil.copy2(p,q);os.utime(q,None);assert sha(p)==sha(q)
patch=C/'patches/minimal-HUD-known44-observer-startup-v001.patch'
for mode in ['--check',None]:
 r=subprocess.run(['git','apply']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');(out/('HUD-check.log' if mode else 'HUD-apply.log')).write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0
os.utime(R/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp',None)
actual=sorted(p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file());assert len(actual)==231
(out/'admission.json').write_text(json.dumps(dict(status='OBSERVER_ONLY_ADMITTED_BUILD_AND_NATIVE_PENDING',candidate=pin(freeze),source_files=len(actual),production_files=len(list((R/'UnrealGame/Content/Production').rglob('*.uasset'))),changes=[pin(R/'UnrealGame/Source/CodexDungeon'/n) for n in ['DungeonHUD.cpp','DungeonGuardArtKnown44Probe.h','DungeonGuardArtKnown44Probe.cpp']],formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(admitted=True,source_files=len(actual),build_pending=True)))
