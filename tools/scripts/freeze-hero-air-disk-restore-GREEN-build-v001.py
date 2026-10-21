"""Freeze actual reviewed v144 source, DLL and subsequent unchanged full203 suite."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil

R = Path('F:/Ourgame')
EV = R / 'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001'

def need(value, message):
    if not value:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pin(path, absolute=False):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=path.as_posix() if absolute else path.relative_to(R).as_posix(),
                bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

def dt(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

parser = argparse.ArgumentParser()
parser.add_argument('--suite', required=True)
parser.add_argument('--output-name', required=True)
parser.add_argument('--repair', action='append', default=[])
args = parser.parse_args()
need(args.output_name.replace('-', '').replace('_', '').isalnum(), 'Safe new snapshot name required')
admission_path = EV / 'Root-source-admission-v001/actual-source-admission.json'
admission = read(admission_path)
need(admission['RootApproved'] is True and admission['actual_applied'] is True and admission['is_template'] is False, 'Actual reviewed admission required')
before = read(admission['predecessor_compiled_manifest']['path'])
changed = {row['path']: row for row in admission['after_files']}
repairs = []
latest_source_utc = dt(admission['utc'])
for item in args.repair:
    path = Path(item).resolve()
    data = read(path)
    need(data['actual_applied'] is True, 'Actual repair receipt required')
    after_path = Path(data['after']['path']).resolve()
    need(after_path.is_relative_to((R / 'UnrealGame/Source').resolve()), 'Repair outside Source')
    need(pin(after_path, True) == data['after'], 'Repair after pin differs')
    changed[after_path.relative_to(R).as_posix()] = pin(after_path)
    latest_source_utc = max(latest_source_utc, dt(data['utc']))
    repairs.append(path)
suite = Path(args.suite).resolve()
need(suite.is_relative_to((R / 'UnrealGame/Saved/Automation').resolve()), 'Actual automation report required')
result = read(suite)
need(tuple(result[k] for k in ['succeeded', 'succeededWithWarnings', 'failed', 'notRun', 'inProcess']) == (203, 0, 0, 0, 0), 'Full203 strictly GREEN required')
tests = result['tests']
need(len(tests) == len({row['fullTestPath'] for row in tests}) == 203, '203 unique actual tests required')
old_suite = read(before['full_suite']['path'])
need({row['fullTestPath'] for row in tests} == {row['fullTestPath'] for row in old_suite['tests']}, 'Original suite membership differs')
for test in tests:
    need(test['state'] == 'Success' and test['warnings'] == 0 and test['errors'] == 0 and
         not any(entry['event']['type'] in ('Error', 'Warning') for entry in test['entries']), 'Test not strictly GREEN')
source = sorted(path for path in (R / 'UnrealGame/Source').rglob('*') if path.is_file())
production = sorted(path for path in (R / 'UnrealGame/Content/Production').rglob('*') if path.is_file())
old_source = {row['path'] for row in before['files'] if row['path'].startswith('UnrealGame/Source/')}
old_production = {row['path'] for row in before['files'] if row['path'].startswith('UnrealGame/Content/Production/')}
new_names = set(changed) - old_source
need(len(new_names) == admission['new_source_files'], 'New Source delta differs')
need({p.relative_to(R).as_posix() for p in source} == old_source | new_names, 'Source membership differs')
need({p.relative_to(R).as_posix() for p in production} == old_production, 'Production membership differs')
need(len(source) == admission['actual_source_files'] and len(production) == admission['actual_production_files'], 'Actual derived counts differ')
for row in before['files']:
    if row['path'].startswith(('UnrealGame/Source/', 'UnrealGame/Content/Production/')) and row['path'] not in changed:
        need(pin(R / row['path']) == row, 'Unrelated source/test/production changed: ' + row['path'])
for row in changed.values():
    need(pin(R / row['path']) == row, 'Current admitted/repaired source differs')
build = R / 'UnrealGame/Saved/Bootstrap/last-build.json'
build_data = read(build)
need(build_data['ExitCode'] == 0 and dt(build_data['Utc']) > latest_source_utc, 'Fresh actual successful build required')
need(suite.stat().st_mtime >= dt(build_data['Utc']).timestamp(), 'Suite predates successful build')
log = Path(build_data['Log']).resolve()
dll = R / 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
output = R / 'source-assets/production/backups' / args.output_name
need(not output.exists(), 'Preserve previous snapshot')
output.mkdir()
files = source + production + [dll, build, log, suite]
pins = [pin(path) for path in files]
copies = []
for path in source + [dll, build, log, suite, admission_path] + repairs:
    destination = output / 'snapshot' / path.relative_to(R)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    need(pin(path)['sha256'] == pin(destination)['sha256'], 'Snapshot bytes differ')
    copies.append(dict(source=pin(path), copy=pin(destination)))
for _ in range(2):
    for row in pins:
        need(pin(R / row['path']) == row, 'Compiled input drift during freeze')
manifest = dict(schema='Root-hero-air-disk-restore-full203-GREEN-build-v001',
                utc=datetime.now(timezone.utc).isoformat(), source_files=len(source), production_files=len(production),
                registered_tests=len(tests), passed=203, failed=0, notRun=0, full_suite=pin(suite, True),
                build=pin(build, True), build_log=pin(log, True), files=pins, copies=copies,
                source_admission_pin=pin(admission_path, True), source_repair_admission_pins=[pin(p, True) for p in repairs],
                verification_passes=2, twoSHA_mismatches=0, old203_tests_unchanged=True,
                native_two_process_restore_reviewed=False, formal_complete_units=0, completed_combinations=0, FinalAccepted=False)
out = output / 'compiled-source-manifest.json'
with out.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
print(json.dumps(pin(out, True), ensure_ascii=False))
