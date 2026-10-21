"""Keep exact real UE storage-test inputs, report, logs and owned IO fixtures."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument('--report', required=True)
parser.add_argument('--build-log', required=True)
parser.add_argument('--test-log', required=True)
parser.add_argument('--passed', type=int, required=True)
parser.add_argument('--failed', type=int, required=True)
args = parser.parse_args()
root = Path('F:/Ourgame')
def io_path(path):
    # Deep retained GUID/attempt fixture trees can exceed classic MAX_PATH.
    return Path('\\\\?\\' + str(path.resolve())) if os.name == 'nt' else path
if not re.fullmatch(r'[A-Za-z0-9_-]+', args.name):
    raise ValueError('Evidence name must be one directory component')
destination = root / 'docs/production/first-batch-v2/evidence/save-generation-store-v001' / args.name
if destination.exists():
    raise FileExistsError(destination)
report_path = (root / args.report).resolve()
report_path.relative_to(root / 'UnrealGame/Saved/Automation')
report_bytes = report_path.read_bytes()
report = json.loads(report_bytes.decode('utf-8-sig'))
if (report['succeeded'], report['failed'], report['notRun']) != (args.passed, args.failed, 0):
    raise ValueError('Actual result differs from expected evidence classification')
sources = [(report_path, Path('actual-automation-index-exact.json'))]
for relative in (
    args.build_log, args.test_log,
    'UnrealGame/Source/CodexDungeon/DungeonSaveGenerationStore.h',
    'UnrealGame/Source/CodexDungeon/DungeonSaveGenerationStore.cpp',
    'UnrealGame/Source/CodexDungeon/Tests/DungeonSaveGenerationStoreTests.cpp',
    'tools/scripts/retain-save-generation-proof.py',
):
    path = (root / relative).resolve()
    path.relative_to(root)
    sources.append((path, Path('source-and-logs') / path.relative_to(root)))
fixture_base = (root / 'UnrealGame/Saved/Automation/SaveGenerationStore').resolve()
fixtures = set()
for test in report['tests']:
    for entry in test.get('entries', []):
        message = entry['event']['message']
        match = re.search(r'Retained real isolated IO evidence: (.+)$', message)
        if match:
            fixture = Path(match.group(1)).resolve()
            fixture.relative_to(fixture_base)
            if not re.fullmatch(r'[A-Fa-f0-9]{32}', fixture.name):
                raise ValueError('Unexpected fixture path')
            fixtures.add(fixture)
for fixture in sorted(fixtures):
    for source in sorted(fixture.rglob('*')):
        if source.is_file():
            sources.append((source, Path('actual-io-fixtures') / source.relative_to(fixture_base)))
rows = []
for source, relative in sources:
    before = source.read_bytes()
    target = destination / relative
    target_io = io_path(target)
    target_io.parent.mkdir(parents=True, exist_ok=True)
    with target_io.open('xb') as stream:
        stream.write(before)
    if source.read_bytes() != before or target_io.read_bytes() != before:
        raise RuntimeError(f'Changed proof bytes: {source}')
    rows.append({'source': source.as_posix(), 'copy': relative.as_posix(),
                 'bytes': len(before), 'sha256': hashlib.sha256(before).hexdigest()})
manifest = {
    'kind': 'actual_UE_storage_automation_evidence',
    'source_report': report_path.as_posix(),
    'actual_passed': report['succeeded'], 'actual_failed': report['failed'],
    'actual_not_run': report['notRun'], 'fixture_directories': len(fixtures),
    'files': rows,
    'boundary': 'Real isolated Windows file IO; not Actor/Run restoration, process kill or power-loss proof.',
}
with (destination / 'manifest.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'evidence': destination.as_posix(), 'copied_files': len(rows),
                  'bytes': sum(row['bytes'] for row in rows),
                  'fixtures': len(fixtures), 'passed': report['succeeded'],
                  'failed': report['failed']}, ensure_ascii=False))
