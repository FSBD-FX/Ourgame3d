"""Root preserves 3GREEN/1RED, admits narrow fix and scoped trial registration."""
from pathlib import Path
import hashlib
import json
import os
import shutil

root = Path('F:/Ourgame').resolve()
module = root / 'UnrealGame/Source/CodexDungeon'
base = root / 'source-assets/production/fairytale-guard-v001'
review = root / 'source-assets/production/fairytale-hero-state-gap-v001/guard-presentation-review-v001'
out = root / 'docs/production/first-batch-v2/evidence/guard-art-v001/root-terminalRED-trial16-admission-v001'
registration_dir = base / 'root-trial-registration-v001'
assert not out.exists() and not registration_dir.exists()


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


report = root / 'UnrealGame/Saved/Automation/FirstRoom-20261018-110335/index.json'
r = read(report)
assert r['succeeded'] == 3 and r['failed'] == 1 and all(r[k] == 0 for k in ['succeededWithWarnings', 'notRun', 'inProcess'])
assert len(r['tests']) == 4 and all(t['warnings'] == 0 for t in r['tests'])
failure = [t for t in r['tests'] if t['state'] == 'Fail']
assert len(failure) == 1 and failure[0]['errors'] == 1 and failure[0]['fullTestPath'].endswith('TerminalDeathMaterialClockReview')
assert any('Terminal .22 endpoint expires lethal material tint' in e['event']['message'] for e in failure[0]['entries'])
sources = sorted(p for p in (root / 'UnrealGame/Source').rglob('*') if p.is_file())
assert len(sources) == 222
out.mkdir(parents=True)
paths = sources + [report, root / 'UnrealGame/Saved/Bootstrap/build-editor-20261018-110103.log', root / 'UnrealGame/Saved/Bootstrap/first-room-tests-20261018-110335.log', root / 'UnrealGame/Saved/Bootstrap/last-build.json']
retained = []
for path in paths:
    target = out / 'RED-originals' / path.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    retained.append({'source': fact(path), 'copy': fact(target)})
for repeat in range(2):
    for row in retained:
        assert fact(row['source']['path']) == row['source'] and fact(row['copy']['path']) == row['copy']
        assert all(row['source'][key] == row['copy'][key] for key in ['bytes', 'sha256'])
(out / 'actual-3GREEN-1RED-manifest.json').write_text(json.dumps({'actual_build_exit': 0, 'succeeded': 3, 'failed': 1, 'warnings': 0, 'assertions_relaxed': False, 'two_pass_SHA_mismatches': 0, 'files': retained}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
pose = module / 'DungeonFairytaleGuardPose.h'
assert fact(pose)['sha256'] == 'ba331c8d33ca62e1604b8df55eb8089f9395330c480aae41ea7354d1daafa6d1'
original = (base / 'presentation-candidate-v001/production-source/DungeonFairytaleGuardPose.h').read_bytes()
repair_path = review / 'production-repair-v002/DungeonFairytaleGuardPose.h'
assert fact(repair_path)['sha256'] == '6f93a4e79d6e91f047436147e56247df93771a1b68aa00c588d97b0ba6e2fa2f'
fixed = repair_path.read_bytes()
def qualified_CRLF(data):
    assert data.count(b'const FEvent*') == 4
    return data.replace(b'const FEvent*', b'const DungeonStoneGuard::FEvent*').replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
assert pose.read_bytes() == qualified_CRLF(original)
pose.write_bytes(qualified_CRLF(fixed))
os.utime(pose, None)

registration_dir.mkdir()
proposal = base / 'presentation-candidate-v001/registration-proposals-and-import-map-v001.json'
assert fact(proposal)['sha256'] == '33a81584cf1b01c3c92d4649643279aea759a32004ac6b6deb31a4525e0db22c'
mapping = read(proposal)
assert len(mapping['rows']) == 3 and sum(len(row['frames']) for row in mapping['rows']) == 16
source_frames = []
for row in mapping['rows']:
    assert row['native_source_id'] in [209, 210, 212] and not row['final_accepted']
    assert row['ONE_row_display_px_per_source_px'] == 100.8 / row['standing_body_extent_px']
    evidence = row['registration_evidence']
    actual = fact(root / evidence['path'])
    assert all(actual[key] == evidence[key] for key in ['bytes', 'sha256'])
    for frame in row['frames']:
        assert fact(frame['source']['path']) == frame['source']
        source_frames.append(frame)
    row['trial_allowed'] = True
    row['trial_approval_record'] = (registration_dir / 'approval.json').relative_to(root).as_posix()
approval = {'schema': 'root-guard16-scoped-trial-registration-v001', 'source_event': 'EV-048', 'purpose': 'Opt-in actual UE world trial of Dormant alias/Wake/Ready/AxeWindup and measured floor registration; not full enemy acceptance', 'TrialAllowed': True, 'FinalAccepted': False, 'upstream_proposal': fact(proposal), 'source_and_registration_SHA_verified': True, 'source_pixels_modified': False, 'hero_body_reference_px': 72, 'Guard_standing_body_px': 100.8, 'rows': mapping['rows'], 'alias': mapping['alias'], 'rejected_native_rows': [211], 'other_states': 'Explicit procedural gaps until independently authored/admitted; never Ready substitution', 'formal_complete_units': 0}
approval_path = registration_dir / 'approval.json'
approval_path.write_text(json.dumps(approval, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
data = module / 'DungeonFairytaleGuardDataV001.inl'
assert fact(data)['sha256'] == '8c4994696102e30e9e5b531699508d94ccb9e408aa20f7a1d69edf4b05b33020'
before = b'R.TrialAllowed=false;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("");'
after = ('R.TrialAllowed=true;R.FinalAccepted=false;R.TrialApprovalRecord=TEXT("' + approval_path.relative_to(root).as_posix() + '");').encode('utf-8')
raw = data.read_bytes()
assert raw.count(before) == 3
data.write_bytes(raw.replace(before, after))
os.utime(data, None)
snapshot = read(root / 'source-assets/production/backups/v128-guard-room-176G/compiled-source-manifest.json')
old = [row for row in snapshot['files'] if row['path'].startswith('UnrealGame/Content/Production/')]
assert len(old) == 1210
for repeat in range(2):
    for row in old:
        now = fact(root / row['path'])
        assert all(now[key] == row[key] for key in ['bytes', 'sha256'])
assets = []
for frame in source_frames:
    object_path = frame['proposed_object_path']
    package, name = object_path.rsplit('.', 1)
    assert package.startswith('/Game/Production/FirstBatch/GuardWhole_v001/')
    disk = root / 'UnrealGame/Content' / (package.removeprefix('/Game/') + '.uasset')
    assert not disk.exists()
    assets.append({'source': frame['source'], 'object_path': object_path, 'package_path': package, 'destination_path': package.rsplit('/', 1)[0], 'name': name, 'saved_path': disk.as_posix()})
manifest = {'schema': 'root-guard16-source-native-import-v001', 'root_trial_registration': fact(approval_path), 'old_production_files': old, 'expected_old_count': 1210, 'expected_new_count': 16, 'expected_total': 1226, 'assets': assets, 'runtime_accepted': False, 'formal_complete_units': 0}
manifest_path = registration_dir / 'import-manifest.json'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(out / 'admission.json').write_text(json.dumps({'terminal_fix': fact(pose), 'qualified_header_line_endings': 'CRLF preserved from prior compile repair; C++ behavior delta is narrow death material expiry only', 'trial_data': fact(data), 'trial_approval': fact(approval_path), 'import_manifest': fact(manifest_path), 'tests_unchanged': True, 'actual_source_files': 222, 'production_files': 1210, 'native_rebuild_and_import_pending': True, 'formal_complete_units': 0}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'actual_RED_preserved': True, 'terminal_fix_applied': True, 'trial_rows': 3, 'source_textures': 16, 'import_manifest': fact(manifest_path), 'rebuild_and_import_pending': True}, ensure_ascii=False))
