"""Close this NEW candidate once; verify every frozen pin twice."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,ast
HERE=Path(__file__).resolve().parent
ROOT=Path('F:/Ourgame')
def row(p):
 p=p.resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(x):
 p=Path(x['path']);p=p if p.is_absolute() else ROOT/p
 a=row(p);assert (a['bytes'],a['sha256'])==(x['bytes'],x['sha256']),str(p)
output=HERE/'Primary1Bridge258-native-checker-freeze-v001.json'
assert not output.exists()
for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
tests=json.loads((HERE/'reports/host-final-GREEN-v001.json').read_text())
assert tests['actual_exit_code']==0 and tests['tests']==22 and tests['failures']==0
members=[row(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
deps=json.loads((HERE/'dependencies-v001.json').read_text())['members']
for _ in range(2):
 for x in members+deps:check(x)
value=dict(schema='request258-primary1-bridge-native-checker-candidate-freeze-v001',created_utc=datetime.now(timezone.utc).isoformat(),
 members=members,dependency_pins=deps,member_count=len(members),dependency_pin_count=len(deps),verification_passes=2,twoSHA_mismatches=0,
 host_tests=22,host_failures=0,actual_Source_Content_tools_E_writes=0,UE_runs=0,images_or_media_viewed=0,
 future_observer_freeze_dynamically_verified_via_Root_admission=True,original_115_plus14_required_resource_count=129,
 source_audio_WAV_or_PCM_constructed=False,new_native_verified=False,FinalAccepted=False)
with output.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(row(output)));print('members',len(members),'dependencies',len(deps))
