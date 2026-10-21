"""Verify minimal delta, unchanged old tests against new module, preflight, freeze."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent;OLD=HERE.parent;ROOT=Path('F:/Ourgame')
def pin(path):return dict(path=path.as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def new(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
checker=HERE/'verify-hero-locomotion-audio-native-v001.py'
V=module(checker,'fixed_checker_under_test')
before=(OLD/checker.name).read_bytes();after=checker.read_bytes()
start=after.index(b'def verify_fixed_normal_inputs(r):\n');end=after.index(b'def verify_session(',start)
added=after[start:end]
call=b'    verify_fixed_normal_inputs(r)\n'
assert after.count(call)==1 and after[:start]+after[end:].replace(call,b'',1)==before
assert (HERE/'dependencies-v001.json').read_bytes()==(OLD/'dependencies-v001.json').read_bytes()
with (HERE/'reports/exact-implementation-delta-v002.txt').open('x',encoding='utf-8') as f:
    f.write(added.decode('utf-8')+'\n# Exactly one added call as verify_session first statement:\n'+call.decode('utf-8'))
old_tests=module(OLD/'tests/test-checker-v001.py','unchanged_original_13_tests');old_tests.V=V
buffer=io.StringIO();result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(old_tests.Contracts))
with (HERE/'reports/unchanged-13-tests-on-new-checker-GREEN-v002.log').open('x',encoding='utf-8') as f:f.write(buffer.getvalue())
assert result.wasSuccessful() and result.testsRun==13
added_tests=subprocess.run([sys.executable,'-B','-X','utf8',str(HERE/'tests/test-fixed-input-edges-v002.py')],capture_output=True,text=True,encoding='utf-8')
with (HERE/'reports/added-host-tests-GREEN-v002.log').open('x',encoding='utf-8') as f:f.write(added_tests.stdout+added_tests.stderr)
assert added_tests.returncode==0 and 'Ran 9 tests' in added_tests.stderr
cm=ROOT/'source-assets/production/backups/v145-HeroLocomotionObserver303-1425-203GREEN-v001/compiled-source-manifest.json'
ad=ROOT/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/Root-observer-source-admission-v001/actual-source-admission.json'
assert pin(cm)['sha256']=='71e91acd625b9813be555f5b38012e9c7ae39727bb2bd35dc495e584865532ac'
assert pin(ad)['sha256']=='488087ee431f2847c2549177d19ceb8eeab4ed080bf677149363997bf1648f2c'
pre=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--preflight','--compiled-manifest',str(cm),'--source-admission',str(ad),
                    '--out',str(HERE/'reports/actual-current-preflight-v002.json')],capture_output=True,text=True,encoding='utf-8')
with (HERE/'reports/actual-current-preflight-process-v002.log').open('x',encoding='utf-8') as f:f.write(pre.stdout+pre.stderr)
assert pre.returncode==0,pre.stdout+pre.stderr
new(HERE/'reports/review-fix-verification-v002.json',dict(schema='HeroLocomotionNativeCheckerScopedFixVerification-v002',
    old_13_test_bodies_changed=False,old_13_tests_run_against_new_checker=13,old_13_failures=0,added_tests=9,added_failures=0,
    exact_function_and_one_call_only=True,dependency_table_byte_identical=True,actual_current_preflight_exit_code=pre.returncode,
    current_compiled_manifest_pin=pin(cm),current_source_admission_pin=pin(ad),UE_started=False,new_native_verified=False,
    source_audio_WAV_or_PCM_constructed=False,new_media_viewed=False,FinalAccepted=False))
members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
deps=json.loads((HERE/'dependencies-v001.json').read_text(encoding='utf-8-sig'))['members']
extra=[pin(OLD/'HeroLocomotionNativeChecker-freeze-v001.json'),pin(OLD/checker.name),pin(OLD/'tests/test-checker-v001.py'),
       pin(ROOT/'.superpowers/sdd/2026-10-19-hero-locomotion-audio-v145/task-3-native-checker-review-v001.md')]
fixture=json.loads((HERE/'actual-historical-input-fixture-pin-v002.json').read_text(encoding='utf-8-sig'))
extra.append({k:fixture[k] for k in ('path','bytes','sha256')})
for row in members+deps+extra:
    p=Path(row['path']);assert p.is_file() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
target=HERE/'HeroLocomotionNativeChecker-review-fix-freeze-v002.json'
new(target,dict(schema='HeroLocomotionNativeCheckerReviewFixFreeze-v002',utc=datetime.now(timezone.utc).isoformat(),members=members,
    dependency_pins=deps+extra,member_count=len(members),dependency_pin_count=len(deps+extra),old_checker_pin=pin(OLD/checker.name),
    only_new_native_gate='exact_12_normal_input_edges_with_strict_bool_type',old_gates_unchanged=True,
    host_tests=22,host_failures=0,added_RED_expected_failures=8,actual_preflight_passed=True,UE_started=False,new_native_verified=False,
    new_media_viewed=False,FinalAccepted=False))
print(json.dumps(pin(target)))
