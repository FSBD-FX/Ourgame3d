from pathlib import Path
import hashlib,json,os,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/presentation-observer-fix-candidate-v003';out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-wake-rounding-stage0-v003';assert not out.exists();out.mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
freeze=C/'wake-entry-fix-freeze-v003.json';assert sha(freeze)=='a10496c192f2f6ec3599e7d2e3edf1c69bb53209c190b4becf99b98166d85284'
for q in read(freeze)['files']:
 f=C/q['path'];assert f.stat().st_size==q['bytes'] and sha(f)==q['sha256']
snapshot=R/'source-assets/production/backups/v129-guard-partial-180G/compiled-source-manifest.json';m=read(snapshot);sources=[q for q in m['files'] if q['path'].startswith('UnrealGame/Source/')]
assert len(sources)==222
for repeat in range(2):
 for q in sources:
  f=R/q['path'];assert f.stat().st_size==q['bytes'] and sha(f)==q['sha256']
assert {p.relative_to(R).as_posix() for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()}=={q['path'] for q in sources}
driver=R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuardDriver.cpp';before=pin(driver);shutil.copy2(driver,out/'baseline-DungeonStoneGuardDriver.cpp')
test=C/'tests/DungeonGuardWakeEntryRoundingV003Tests.cpp';dest=R/'UnrealGame/Source/CodexDungeon/Tests'/test.name;assert not dest.exists();shutil.copy2(test,dest);os.utime(dest,None);assert sha(dest)==sha(test) and pin(driver)==before
(out/'admission.json').write_text(json.dumps(dict(stage='UNCHANGED_REAL_DRIVER_PLUS_NEW_REGRESSION_PENDING_ACTUAL_RED',freeze=pin(freeze),test=pin(dest),baseline_driver=before,source_files=223,expected_registered_tests=181,UE_run=False,existing_source_verified_twice=True,formal_complete_units=0),indent=2)+'\n',encoding='utf-8')
progress=R/'docs/production/first-batch-v2/progress.json';shutil.copy2(progress,out/'progress-before.json');p=read(progress);p['current_source_uncompiled_changes']=True;p['ue_current_working_source_compiled']=False;p['current_snapshot_pending']='v130 wake-entry numerical regression stage0 actual RED pending';progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source_files=223,test=pin(dest),driver_unchanged=True,expected_registered_tests=181)))
