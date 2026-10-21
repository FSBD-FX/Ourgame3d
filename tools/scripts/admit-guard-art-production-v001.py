"""Root production admission after actual three RED; keep terminal defect for RED4."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess

root = Path('F:/Ourgame').resolve()
base = root / 'source-assets/production/fairytale-guard-v001'
v1, v2 = base / 'presentation-candidate-v001', base / 'presentation-candidate-v002'
review = root / 'source-assets/production/fairytale-hero-state-gap-v001/guard-presentation-review-v001'
out = root / 'docs/production/first-batch-v2/evidence/guard-art-v001/root-production-terminalRED-admission-v001'
assert not out.exists()


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


assert fact(v1 / 'presentation-freeze-v001.json')['sha256'] == '5e13d1ba16e45bd74b6a1adda45403b783b11072ca77de18b45870a1017bd78a'
assert fact(v2 / 'source-freeze-v002.json')['sha256'] == '50f638f57ab38c0883e0b94164d5806acb22dd4676402cce5ea4e385fe689b86'
assert fact(review / 'terminal-regression-and-repair-freeze-v001.json')['sha256'] == '7a236df6a8b1b600f951382b1124034724e189871b8cf9c70141f577fd29f0ab'
for where, freeze in [(v1, v1 / 'presentation-freeze-v001.json'), (v2, v2 / 'source-freeze-v002.json')]:
    for row in read(freeze)['files']:
        now = fact(where / row['path'])
        assert all(now[key] == row[key] for key in ['bytes', 'sha256'])
for row in read(review / 'terminal-regression-and-repair-freeze-v001.json')['files']:
    assert fact(row['path']) == row
red = read(root / 'docs/production/first-batch-v2/evidence/guard-art-v001/root-actual-threeRED-v001/manifest.json')
assert red['semantic_RED'] == 3 and red['actual_source_files'] == 217
for row in red['files']:
    if row['path'].startswith('UnrealGame/Source/'):
        now = fact(root / row['path'])
        assert all(now[key] == row[key] for key in ['bytes', 'sha256']), row['path']
module = root / 'UnrealGame/Source/CodexDungeon'
original_test = module / 'Tests/DungeonFairytaleGuardPresentationTests.cpp'
assert fact(original_test)['sha256'] == 'd28c85e175e3cf0141d20a23637d8c0f56ca95619edfab422742b9a6f9b362a4'
pairs = [(v1 / 'production-source' / name, module / name) for name in ['DungeonFairytaleGuardPose.h', 'DungeonFairytaleGuardDrawState.h', 'DungeonFairytaleGuardPresentation.cpp']]
pairs += [(v2 / 'new-source' / name, module / name) for name in ['DungeonGuardArtPartialProbe.h', 'DungeonGuardArtPartialProbe.cpp']]
pairs += [(review / 'tests/DungeonFairytaleGuardTerminalMaterialReviewTests.cpp', module / 'Tests/DungeonFairytaleGuardTerminalMaterialReviewTests.cpp')]
assert all(not target.exists() for _, target in pairs[1:])
out.mkdir(parents=True)
for name in ['DungeonHUD.h', 'DungeonHUD.cpp', 'DungeonFairytaleGuardPose.h']:
    shutil.copy2(module / name, out / ('before-' + name))
progress_path = root / 'docs/production/first-batch-v2/progress.json'
shutil.copy2(progress_path, out / 'before-progress.json')
(out / 'started.json').write_text(json.dumps({'expected_source_after': 222, 'original_three_tests_unchanged': fact(original_test), 'terminal_fix_not_applied': True}, indent=2) + '\n', encoding='utf-8')
rows = []
for source, target in pairs:
    shutil.copy2(source, target)
    os.utime(target, None)
    assert all(fact(source)[key] == fact(target)[key] for key in ['bytes', 'sha256'])
    rows.append({'candidate': fact(source), 'actual': fact(target)})
for patch in [v1 / 'patches/minimal-HUD-partial-trial-v001.patch', v2 / 'patches/minimal-HUD-observer-startup-v002.patch']:
    for mode in ['check', 'apply']:
        args = ['git', 'apply', '-p0', '--ignore-space-change']
        if mode == 'check':
            args.append('--check')
        args.append(str(patch))
        result = subprocess.run(args, cwd=root, capture_output=True, text=True, encoding='utf-8')
        (out / (patch.stem + '-' + mode + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
        assert result.returncode == 0, 'Preserve partial admission and inspect: ' + patch.name + ' ' + mode
for name in ['DungeonHUD.h', 'DungeonHUD.cpp']:
    os.utime(module / name, None)
assert fact(original_test)['sha256'] == 'd28c85e175e3cf0141d20a23637d8c0f56ca95619edfab422742b9a6f9b362a4'
assert len([p for p in (root / 'UnrealGame/Source').rglob('*') if p.is_file()]) == 222
progress = read(progress_path)
progress['current_source_uncompiled_changes'] = True
progress['current_task'] = 'Guard partial production+native observer+independent fourth terminal test admitted. Actual build and expected3GREEN/1RED pending; no imported Guard textures or final registration.'
progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(out / 'admission.json').write_text(json.dumps({'schema': 'root-guard-art-production-for-terminalRED-v001', 'files': rows, 'HUD_after': [fact(module / n) for n in ['DungeonHUD.h', 'DungeonHUD.cpp']], 'original_three_tests_unchanged': True, 'terminal_bug_fix_applied': False, 'actual_source_files': 222, 'expected_registered_tests': 180, 'production_files': 1210, 'native_build_claimed': False, 'formal_complete_units': 0}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'source_files': 222, 'expected_tests': 180, 'actual_build_and_four_tests_pending': True}))
