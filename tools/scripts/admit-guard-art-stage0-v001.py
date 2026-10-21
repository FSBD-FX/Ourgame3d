"""Root-only additive stage0 for three real UE presentation contract tests."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path('F:/Ourgame').resolve()
candidate = root / 'source-assets/production/fairytale-guard-v001/presentation-candidate-v001'
out = root / 'docs/production/first-batch-v2/evidence/guard-art-v001/root-stage0-admission-v001'
assert not out.exists()


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


freeze = candidate / 'presentation-freeze-v001.json'
assert fact(freeze)['sha256'] == '5e13d1ba16e45bd74b6a1adda45403b783b11072ca77de18b45870a1017bd78a'
subprocess.run([sys.executable, '-B', '-X', 'utf8', str(candidate / 'verify-candidate-v001.py')], cwd=root, check=True)
snapshot = json.loads(read(root / 'source-assets/production/backups/v128-guard-room-176G/compiled-source-manifest.json'))
source_rows = [row for row in snapshot['files'] if row['path'].startswith('UnrealGame/Source/')]
assert len(source_rows) == 213
actual = sorted(p.relative_to(root).as_posix() for p in (root / 'UnrealGame/Source').rglob('*') if p.is_file())
assert actual == sorted(row['path'] for row in source_rows)
for repeat in range(2):
    for row in source_rows:
        now = fact(root / row['path'])
        assert all(now[key] == row[key] for key in ['bytes', 'sha256']), row['path']
module = root / 'UnrealGame/Source/CodexDungeon'
pairs = [
    (candidate / 'stage0/DungeonFairytaleGuardPose.h', module / 'DungeonFairytaleGuardPose.h'),
    (candidate / 'production-source/DungeonFairytaleGuardProfile.h', module / 'DungeonFairytaleGuardProfile.h'),
    (candidate / 'production-source/DungeonFairytaleGuardDataV001.inl', module / 'DungeonFairytaleGuardDataV001.inl'),
    (candidate / 'stage0/DungeonFairytaleGuardPresentationTests.cpp', module / 'Tests/DungeonFairytaleGuardPresentationTests.cpp'),
]
assert all(not target.exists() for _, target in pairs)
out.mkdir(parents=True)
progress_path = root / 'docs/production/first-batch-v2/progress.json'
shutil.copy2(progress_path, out / 'before-progress.json')
rows = []
for source, target in pairs:
    shutil.copy2(source, target)
    os.utime(target, None)
    assert all(fact(source)[key] == fact(target)[key] for key in ['bytes', 'sha256'])
    rows.append({'candidate': fact(source), 'actual': fact(target)})
assert len([p for p in (root / 'UnrealGame/Source').rglob('*') if p.is_file()]) == 217
progress = json.loads(read(progress_path))
progress['current_source_uncompiled_changes'] = True
progress['ue_current_working_source_verified'] = False
progress['ue_current_working_source_compiled'] = False
progress['current_task'] = 'Guard art partial selector Stage0 admitted four new Source files; actual UE3RED pending. v128 remains previous compiled/runtime proof; no new Guard textures imported.'
progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
receipt = out / 'admission.json'
receipt.write_text(json.dumps({'schema': 'root-guard-art-stage0-admission-v001', 'freeze': fact(freeze), 'baseline_Source213_two_passes_zero_diff': True, 'new_files': rows, 'actual_source_files': 217, 'HUD_unchanged': True, 'native_build_or_RED_claimed': False, 'production_files': 1210, 'formal_complete_units': 0}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'admission': fact(receipt), 'source_files': 217, 'actual_UE_RED_pending': True}, ensure_ascii=False))
