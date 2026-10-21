"""Admit only the frozen observer patch, preserving the previous actual build."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
R=Path('F:/Ourgame')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def pin(p): return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def verify(p,row): assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],p
C=R/'source-assets/production/fairytale-guard-v001/presentation-observer-route-candidate-v009'
freeze=C/'observer-route-freeze-v009.json'
assert sha(freeze)=='ddbc99dcae3853a00d6ccf386606d4b8eeb3b8473dec5f103ef6a706997f69ec'
for row in read(freeze)['files']: verify(C/row['path'],row)
old=R/'source-assets/production/backups/v130-guard-partial-181G'
manifest=read(old/'compiled-source-manifest.json')
assert manifest['strict_registered_tests']==181 and manifest['source_files']==223 and manifest['production_files']==1226
for row in manifest['files']:
 verify(R/row['path'],row)
 if not row['path'].startswith('UnrealGame/Content/'): verify(old/'files'/row['path'],row)
for folder in ['UnrealGame/Source','UnrealGame/Content/Production']:
 assert {q.relative_to(R).as_posix() for q in (R/folder).rglob('*') if q.is_file()}=={r['path'] for r in manifest['files'] if r['path'].startswith(folder+'/')}
out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-spatial-route-admission-v009'
assert not out.exists();out.mkdir()
source=R/'UnrealGame/Source/CodexDungeon/DungeonGuardArtPartialProbe.cpp'
before=pin(source);copy=out/'before-DungeonGuardArtPartialProbe.cpp';shutil.copy2(source,copy)
assert sha(source)=='ee9706ff2b0dd6f4608862507d62e2c5950ac706dfaf2044f76b82a3a5ed87e8'
patch=C/'patches/observer-body-aware-route-spatial-credit-v009.patch'
for mode in ['--check',None]:
 result=subprocess.run(['git','apply']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8')
 (out/('check.log' if mode else 'apply.log')).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0
os.utime(source,None)
candidate=C/'new-source/DungeonGuardArtPartialProbe.cpp'
assert source.read_text(encoding='utf-8-sig')==candidate.read_text(encoding='utf-8-sig')
changed=[]
for row in manifest['files']:
 p=R/row['path']
 if p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:changed.append(row['path'])
assert changed==[source.relative_to(R).as_posix()],changed
receipt=dict(status='ONLY_OBSERVER_ROUTE_AND_SPATIAL_CREDIT_ADMITTED_NATIVE_PENDING',before=before,after=pin(source),candidate_freeze=pin(freeze),previous_actual_compiled_manifest=pin(old/'compiled-source-manifest.json'),previous_build_source_config_dll_report_copied=True,previous_manifest_verified_files=len(manifest['files']),only_changed=changed,registry=181,source_files=223,production_files=1226,formal_complete_units=0)
(out/'admission.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
