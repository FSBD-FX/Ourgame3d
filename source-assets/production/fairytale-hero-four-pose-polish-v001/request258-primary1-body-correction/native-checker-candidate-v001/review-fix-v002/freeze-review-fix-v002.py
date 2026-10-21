"""Freeze NEW child only; retain all old dependencies and scoped real preflight."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
def pin(path):
 path=path.resolve();b=path.read_bytes();return dict(path=path.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
 value=pin(path);assert (value['bytes'],value['sha256'])==(row['bytes'],row['sha256']),str(path)
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
output=HERE/'Primary1Bridge258-native-checker-review-fix-freeze-v002.json'
assert not output.exists()
for path in HERE.glob('*.py'):ast.parse(path.read_text(encoding='utf-8-sig'))
green=read(HERE/'review-fix-reports/host-GREEN-v002.json');preflight=read(HERE/'review-fix-reports/actual-current1439-preflight-v002.json');process=read(HERE/'review-fix-reports/actual-current1439-preflight-process-v002.json')
assert green['tests']==34 and green['failures']==0 and green['actual_exit_code']==0
assert preflight['passed'] and process['actual_exit_code']==0 and preflight['compiled_manifest_pin']['sha256']=='0943bc48284765015990b1621d5cd95046c450060030a59ad6f2025f17594fcd'
assert preflight['source_admission_pin']['sha256']=='9437c764bd919d43afd64eef33b11477b01c9cf06857a907f9e7351af755165c'
deps=read(HERE/'dependencies-v001.json')['members'];seen={(Path(x['path']) if Path(x['path']).is_absolute() else ROOT/x['path']).resolve() for x in deps}
def add(path):
 path=path.resolve()
 if path not in seen:deps.append(pin(path));seen.add(path)
add(HERE.parent/'Primary1Bridge258-native-checker-freeze-v001.json')
for path in HERE.parent.glob('*.py'):add(path)
source=ROOT/'source-assets/production/fairytale-hero-four-pose-polish-v001/request258-primary1-body-correction/native-observation-review-fix-v002/candidate-freeze-v002.json';add(source)
f=read(source)
for row in f['files']+f['dependencies']:add(source.parent/row['relative_path'])
for row in (preflight['compiled_manifest_pin'],preflight['source_admission_pin']):add(Path(row['path']))
for row in read(HERE/'freeze-entry-fixtures/external-absolute.json')['dependencies']:add(Path(row['path']))
members=[pin(path) for path in sorted(HERE.rglob('*')) if path.is_file() and '__pycache__' not in path.parts]
for _ in range(2):
 for row in members+deps:check(row)
value=dict(schema='request258-primary1-bridge-native-checker-review-fix-freeze-v002',created_utc=datetime.now(timezone.utc).isoformat(),members=members,dependency_pins=deps,
 member_count=len(members),dependency_pin_count=len(deps),verification_passes=2,twoSHA_mismatches=0,
 host_tests=34,host_failures=0,retained_original_tests=22,new_relative_boundary_tests=12,
 current_actual1439_preflight=pin(HERE/'review-fix-reports/actual-current1439-preflight-v002.json'),current_actual1439_preflight_exit_code=0,
 production_checker_changed_functions=['freeze_members'],all_other_checker_bytes_unchanged=True,
 actual_Source_Content_tools_E_writes=0,UE_runs=0,images_or_media_viewed=0,new_native_verified=False,FinalAccepted=False)
with output.open('x',encoding='utf-8') as file:json.dump(value,file,ensure_ascii=False,indent=2);file.write('\n')
print(json.dumps(pin(output)));print('members',len(members),'dependencies',len(deps))
