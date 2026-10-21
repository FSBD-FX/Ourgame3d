"""Preserve exact old checker/config, then run added tests before implementation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent;OLD=HERE.parent
def new_bytes(path,data):
    with path.open('xb') as f:f.write(data)
def pin(path):return dict(path=path.as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
for name in ('verify-hero-locomotion-audio-native-v001.py','dependencies-v001.json'):
    new_bytes(HERE/name,(OLD/name).read_bytes())
fixture=Path('F:/Ourgame/过程图稿与视频/2026-10-19_钟盔落地Shift_right_v001/原件/runtime-report.json')
with (HERE/'actual-historical-input-fixture-pin-v002.json').open('x',encoding='utf-8') as f:
    json.dump(dict(**pin(fixture),scope='Historical real normal input edge schema only; not current SFX native evidence'),f,ensure_ascii=False,indent=2);f.write('\n')
reports=HERE/'reports';reports.mkdir(exist_ok=False)
new_bytes(reports/'checker-before-fix-exact-old-v001.py',(OLD/'verify-hero-locomotion-audio-native-v001.py').read_bytes())
r=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'tests/test-fixed-input-edges-v002.py')],capture_output=True,text=True,encoding='utf-8')
new_bytes(reports/'added-host-tests-RED-v002.log',(r.stdout+r.stderr).encode('utf-8'))
assert r.returncode==1 and 'failures=8' in r.stderr and 'errors=' not in r.stderr,r.stdout+r.stderr
with (reports/'added-host-tests-RED-v002.json').open('x',encoding='utf-8') as f:
    json.dump(dict(actual_process_exit_code=r.returncode,tests=9,expected_failures=8,errors=0,
                   reason='Old checker accepts extra/missing/reordered/non-bool edges and has no exact native-session gate',
                   native_run=False,audio_constructed=False,FinalAccepted=False),f,indent=2);f.write('\n')
print(json.dumps(dict(RED_observed=True,tests=9,expected_failures=8,errors=0)))
