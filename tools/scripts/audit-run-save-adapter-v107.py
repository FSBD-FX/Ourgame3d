"""Read actual frozen endpoints and reports; never edits UE/source/fixtures."""
from pathlib import Path
import hashlib
import json

ROOT = Path('F:/Ourgame')
EVIDENCE = ROOT / 'docs/production/first-batch-v2/evidence/run-save-adapter-v001'
OUT = EVIDENCE / 'actual134GREEN-v107-audit-v001.json'
assert not OUT.exists(), 'Keep prior audit immutable'
SNAP = ROOT / 'source-assets/production/backups/2026-10-16_RunSaveAdapter-actual134GREEN-v107'
OLD = ROOT / 'source-assets/production/backups/2026-10-16_SwordDisplayScale50-actual130GREEN-v105'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def pin(path):
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

manifest_path = SNAP / 'compiled-source-manifest.json'
manifest = read(manifest_path)
old = read(OLD / 'compiled-source-manifest.json')
failures = []
for row in manifest['files']:
    for endpoint in (ROOT / row['path'], SNAP / row['path']):
        actual = pin(endpoint)
        if any(actual[k] != row[k] for k in ('bytes', 'sha256')):
            failures.append({'path': endpoint.as_posix(), 'reason': 'size/SHA differs from freeze'})
assert len(manifest['files']) == 1545
assert not failures, failures

old_rows = {r['path']: r for r in old['files']}
new_rows = {r['path']: r for r in manifest['files']}
old_source = [p for p in old_rows if p.startswith('UnrealGame/Source/')]
source_differences = [p for p in old_source if old_rows[p] != new_rows[p]]
assert not source_differences, source_differences
art = ['DungeonFairytaleSwordBodyV002.inl', 'DungeonFairytaleSwordPresentation.cpp',
       'DungeonFairytaleSwordDrawState.h', 'DungeonFairytaleSwordProbe.cpp', 'DungeonHUD.cpp']
art_pins = []
for name in art:
    path = 'UnrealGame/Source/CodexDungeon/' + name
    assert old_rows[path] == new_rows[path]
    art_pins.append(new_rows[path])
packages = [p for p in new_rows if p.startswith('UnrealGame/Content/Production/')]
assert len(packages) == 983
assert all(old_rows[p] == new_rows[p] for p in packages)
tests_path = ROOT / 'UnrealGame/Source/CodexDungeon/Tests/DungeonRunSaveAdapterTests.cpp'
stage = read(EVIDENCE / 'stage0-v001/freeze-manifest-v001.json')
test_pin = next(x for x in stage['source_pins'] if x['path'].endswith('DungeonRunSaveAdapterTests.cpp'))
assert all(pin(tests_path)[k] == test_pin[k] for k in ('bytes', 'sha256'))
deps = []
for row in stage['read_only_dependency_pins']:
    actual = pin(Path(row['path']))
    assert all(actual[k] == row[k] for k in ('bytes', 'sha256'))
    deps.append(actual)

def report(relative, expected):
    path = ROOT / relative
    doc = read(path)
    assert doc['succeeded'] == expected
    assert all(doc[k] == 0 for k in ('failed', 'notRun', 'inProcess', 'succeededWithWarnings'))
    assert len(doc['tests']) == expected
    assert all(t['state'] == 'Success' and t['errors'] == 0 and t['warnings'] == 0 for t in doc['tests'])
    return path, doc

full_path, full = report('UnrealGame/Saved/Automation/FirstRoom-20261016-142409/index.json', 134)
target_path, targeted = report('UnrealGame/Saved/Automation/FirstRoom-20261016-142054/index.json', 4)
old_report_path, old_report = report('UnrealGame/Saved/Automation/FirstRoom-20261016-133855/index.json', 130)
old_names = {x['fullTestPath'] for x in old_report['tests']}
new_names = {x['fullTestPath'] for x in full['tests']}
additions = sorted(new_names - old_names)
assert len(old_names) == 130 and not (old_names - new_names)
assert additions == sorted(x['fullTestPath'] for x in targeted['tests'])
assert all(n.startswith('CodexDungeon.Content.RunSaveAdapter.') for n in additions)
runner = ROOT / 'tools/scripts/test-first-room.ps1'
assert '[int]$ExpectedTests = 134' in runner.read_text(encoding='utf-8-sig')
build = ROOT / 'UnrealGame/Saved/Bootstrap/build-editor-20261016-141911.log'
build_text = build.read_text(encoding='utf-8-sig')
assert 'Compile [x64] DungeonRunSaveAdapter.cpp' in build_text
assert 'Link [x64] UnrealEditor-CodexDungeon.dll' in build_text
assert 'Total execution time:' in build_text
result = {
    'schema': 'root-run-save-adapter-actual134GREEN-v107-audit-v001',
    'snapshot': SNAP.as_posix(), 'snapshot_manifest': pin(manifest_path),
    'snapshot_files': len(manifest['files']), 'endpoint_checks': 2 * len(manifest['files']),
    'size_SHA_mismatches': 0, 'bytes': manifest['bytes'],
    'old_v105_Source_unchanged': len(old_source),
    'art5_Source_identical_to_original_v105_movie': art_pins,
    'production_packages_identical_to_v105': len(packages),
    'Stage0_test_unchanged': pin(tests_path), 'old_dependencies_unchanged': deps,
    'actual_build_log': pin(build), 'actual_build_exit_recorded_by_root': 0,
    'actual_target4': pin(target_path), 'actual_full134': pin(full_path),
    'all_per_test_state_success_no_warning_error': True,
    'old130_name_set_preserved': True, 'new_four_registrations': additions,
    'runner_default134_after_actual_success': pin(runner),
    'actual_scope': 'BoundDevelopmentRunV1 real disk/head/fault/atomicPrepare; existing valid target World and future original reload',
    'actual_pristine_new_process_Continue': False,
    'complete_profile_D13': False, 'full_motion_audio_art_accepted': False,
    'formal_complete_units': 0, 'goal_status': 'active',
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: result[k] for k in ('snapshot_files', 'endpoint_checks', 'size_SHA_mismatches', 'bytes', 'old_v105_Source_unchanged', 'production_packages_identical_to_v105', 'old130_name_set_preserved', 'actual_pristine_new_process_Continue')}, ensure_ascii=False))
