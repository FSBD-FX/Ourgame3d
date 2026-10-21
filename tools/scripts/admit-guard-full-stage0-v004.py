"""Preserve actual v131 pins, then admit only full selector stage0 and same3 tests."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def verify(p,row):assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],p
for folder,name,expected in [('presentation-full-candidate-v003','presentation-full-freeze-v003.json','fa9446005a99b69cab9b6ce196e09b34d4f44d510eff777e83bee82567fd8380'),('presentation-full-candidate-v004','known44-admission-milestone-freeze-v004.json','ead3fbb7bd55478fe7ecdd16d940834d13195bed756949e6008528e9ea291d11')]:
 root=B/folder;f=root/name;assert sha(f)==expected
 for row in read(f)['files']:verify(root/row['path'],row)
old=R/'source-assets/production/backups/v131-guard-partial-181G';m=read(old/'compiled-source-manifest.json')
for row in m['files']:
 verify(R/row['path'],row)
 if not row['path'].startswith('UnrealGame/Content/'):verify(old/'files'/row['path'],row)
assert m['source_files']==223 and m['strict_registered_tests']==181 and m['production_files']==1226
out=R/'docs/production/first-batch-v2/evidence/guard-full-v004/root-stage0-admission-v001';assert not out.exists();out.mkdir(parents=True)
files=[('production-source/DungeonFairytaleGuardFullProfileV003.h','DungeonFairytaleGuardFullProfileV003.h'),('production-source/DungeonFairytaleGuardFullDataV003.inl','DungeonFairytaleGuardFullDataV003.inl'),('stage0/DungeonFairytaleGuardFullPoseV003.h','DungeonFairytaleGuardFullPoseV003.h'),('stage0/DungeonFairytaleGuardFullV003Tests.cpp','Tests/DungeonFairytaleGuardFullV003Tests.cpp')]
admitted=[]
for source,target in files:
 src=B/'presentation-full-candidate-v003'/source;dst=R/'UnrealGame/Source/CodexDungeon'/target;assert not dst.exists();shutil.copy2(src,dst);os.utime(dst,None);assert sha(src)==sha(dst);admitted.append(pin(dst))
patch=B/'presentation-full-candidate-v004/patches/full-data-retain-StompRecovery225-explicit-gap-v004.patch'
for mode in ['--check',None]:
 p=subprocess.run(['git','apply']+([mode] if mode else [])+[str(patch)],cwd=R,capture_output=True,text=True,encoding='utf-8');(out/('check.log' if mode else 'apply.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0
data=R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleGuardFullDataV003.inl';os.utime(data,None)
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==227
assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1226
admitted=[pin(R/row['path']) for row in admitted]
record=dict(status='ACTUAL_FULL_STAGE0_ADMITTED_NATIVE_RED_PENDING',previous_strict181_snapshot=pin(old/'compiled-source-manifest.json'),previous_all_actual_and_copied_pins_verified=len(m['files']),admitted=admitted,old_partial_Source_unchanged=True,new_source_count=227,production_packages=1226,expected_new_tests=3,expected_full_registry_only_plan=184,HUD_full_patch_applied=False,imports=False,formal_complete_units=0)
(out/'admission.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record))
