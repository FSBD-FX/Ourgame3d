from pathlib import Path
import hashlib,json,os,shutil
R=Path('F:/Ourgame');C=R/'source-assets/production/fairytale-guard-v001/presentation-observer-fix-candidate-v005';out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-wake-native-regression-v005';assert not out.exists();out.mkdir()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
freeze=C/'wake-native-regression-freeze-v005.json';assert sha(freeze)=='6e3ce888ce8de158fbc259b2ceed5b291a2fccfaf483bae950b909fde5d5a247'
for q in read(freeze)['files']:
 f=C/q['path'];assert f.stat().st_size==q['bytes'] and sha(f)==q['sha256']
preserved=read(R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-wake-rounding-stage0-v003/actual-fixture-premise-RED-v001/manifest.json')
for q in preserved['files']:
 if q['path'].startswith('UnrealGame/Source/'):
  f=R/q['path'];assert f.stat().st_size==q['bytes'] and sha(f)==q['sha256']
dest=R/'UnrealGame/Source/CodexDungeon/Tests/DungeonGuardWakeEntryRoundingV003Tests.cpp';old=pin(dest);assert old['sha256']=='5a5b2002f991a437ffb8ff319868324def6393917cec1347bd055ac9e87fa8ac'
driver=R/'UnrealGame/Source/CodexDungeon/DungeonStoneGuardDriver.cpp';before=pin(driver);shutil.copy2(dest,out/'before-test-v003.cpp');shutil.copy2(C/'tests'/dest.name,dest);os.utime(dest,None);assert pin(driver)==before
(out/'admission.json').write_text(json.dumps(dict(status='TEST_ONLY_NATIVE_GEOMETRY_AND_PREVIEW_DERIVED_MATRIX_PENDING_SEMANTIC_RED',original_fixture_failure_preserved=True,original_test=old,admitted_test=pin(dest),driver_unchanged=before,production_changes=0,source_files=223,expected_registry=181,formal_complete_units=0),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(test=pin(dest),driver_unchanged=True,source_files=223)))
