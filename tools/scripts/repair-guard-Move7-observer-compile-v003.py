"""Preserve the failed observer attempt; replace only one invalid JSON ref conversion."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame');S=R/'UnrealGame/Source/CodexDungeon';C=R/'source-assets/production/fairytale-guard-v001/Move7-native-observer-candidate-v001/source-compile-fix-v003'
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
def check(x,base=R):
 q=Path(x['path']);q=q if q.is_absolute()else base/q
 assert(q.stat().st_size,hashlib.sha256(q.read_bytes()).hexdigest())==(x['bytes'],x['sha256']),q
 return q
freeze=C/'Move7-observer-source-freeze-v003.json';assert pin(freeze)['sha256']=='610a78c82ccd41fbaa2abaa3713ef7346fb98c5ba0e8c1ca15f2817f34e8ce42'
for x in read(freeze)['files']:check(x,C)
parent=R/'source-assets/production/backups/v141-GuardMove7-Production200G-v001/compiled-source-manifest.json'
assert pin(parent)['sha256']=='0f011ba7e2963f4a686e7fcf84324ed3c5815f6c020fc2e818e6be79234ead38'
old=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/observer-admission-v001/admission-receipt-v001.json'
assert pin(old)['sha256']=='3d5af607a69fa391d81fdbfbf98d08f09a429663bc3935554b1390972b02af72'
m=read(parent);d=read(old);expected={x['path']:x for x in m['files']if x['path'].startswith('UnrealGame/Source/')};expected.update({x['path']:x for x in d['admitted']})
assert len(expected)==len([q for q in(R/'UnrealGame/Source').rglob('*')if q.is_file()])==283
for repeat in range(2):
 for x in expected.values():check(x)
cpp=S/'DungeonGuardMoveProbeV001.cpp';new=C/'new-source'/cpp.name;before=cpp.read_bytes();after=new.read_bytes()
needle=b'FJsonSerializer::Serialize(R.ToSharedRef(),Writer)';replacement=b'FJsonSerializer::Serialize(R,Writer)'
assert before.count(needle)==1 and after==before.replace(needle,replacement)
assert pin(S/'DungeonGuardMoveProbeV001.h')['sha256']==pin(C/'new-source/DungeonGuardMoveProbeV001.h')['sha256']
last=R/'UnrealGame/Saved/Bootstrap/last-build.json';b=read(last);assert b['ExitCode']==6 and Path(b['Log']).name=='build-editor-20261018-224551.log'
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/observer-compile-repair-v003';assert not out.exists();out.mkdir(parents=True)
shutil.copy2(cpp,out/'DungeonGuardMoveProbeV001.cpp.failed-v002')
shutil.copy2(last,out/'failed-last-build.json');shutil.copy2(Path(b['Log']),out/'failed-build.log')
shutil.copy2(old.parent/'DungeonHUD.cpp.before',out/'DungeonHUD.cpp.before')
assert pin(out/'DungeonHUD.cpp.before')['sha256']==d['previous'][0]['sha256']
receipt=dict(schema='Root-GuardMove7-observer-admission-v001',revision=3,utc=datetime.now(timezone.utc).isoformat(),is_template=False,RootApproved=True,success=False,
 previous_Source_count=281,Source_count=283,Production_count=1371,physical_before_Source_count=283,physical_after_Source_count=283,
 previous=d['previous'],physical_previous=[pin(cpp)],candidate_freeze=pin(freeze),previous_production200_GREEN=pin(parent),
 preserved_failed_observer_admission=pin(old),preserved_failed_source=pin(out/'DungeonGuardMoveProbeV001.cpp.failed-v002'),
 preserved_failed_build=pin(out/'failed-build.log'),preserved_failed_build_result=pin(out/'failed-last-build.json'),
 compile_fix='TSharedRef from MakeShared is passed directly to Serialize; remove invalid R.ToSharedRef() conversion only.',
 logical_chain='Final bounded observer extension from compiled281 to283; physical failed283 attempt is preserved and only its CPP conversion is repaired.',
 all_other_observer_bytes_unchanged=True,expected_registered_tests=200,all_four_tests_unchanged=True,old196_tests_unchanged=True,
 source_compiled_after_admission=False,native_passed=False,formal_complete_units=0,FinalAccepted=False)
try:
 shutil.copy2(new,cpp);assert cpp.read_bytes()==after
 for n,x in expected.items():
  if n!=cpp.relative_to(R).as_posix():check(x)
 receipt.update(success=True,admitted=[pin(S/n)for n in ['DungeonGuardMoveProbeV001.h','DungeonGuardMoveProbeV001.cpp','DungeonHUD.cpp']],unaffected_Source_unchanged=True)
except Exception as e:receipt['failure']=str(e);raise
finally:
 with(out/'admission-receipt-v003.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(success=True,Source=283,Production=1371,receipt=pin(out/'admission-receipt-v003.json'))))
