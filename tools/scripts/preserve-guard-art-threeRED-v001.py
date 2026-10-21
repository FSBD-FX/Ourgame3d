"""Preserve the actual compiled three-test semantic RED before production."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path('F:/Ourgame').resolve()
out = root / 'docs/production/first-batch-v2/evidence/guard-art-v001/root-actual-threeRED-v001'
assert not out.exists()
report = root / 'UnrealGame/Saved/Automation/FirstRoom-20261018-105235/index.json'
r = json.loads(report.read_text(encoding='utf-8-sig'))
assert r['failed'] == 3 and all(r[k] == 0 for k in ['succeeded', 'succeededWithWarnings', 'notRun', 'inProcess'])
assert len(r['tests']) == len({t['fullTestPath'] for t in r['tests']}) == 3
assert all(t['state'] == 'Fail' and t['errors'] == 1 and t['warnings'] == 0 for t in r['tests'])
assert all(any(e['event']['type'] == 'Error' and 'Stage0:' in e['event']['message'] for e in t['entries']) for t in r['tests'])
sources = sorted(p for p in (root / 'UnrealGame/Source').rglob('*') if p.is_file())
assert len(sources) == 217
paths = sources + [report, root / 'UnrealGame/Saved/Bootstrap/build-editor-20261018-105147.log', root / 'UnrealGame/Saved/Bootstrap/first-room-tests-20261018-105235.log', root / 'UnrealGame/Saved/Bootstrap/last-build.json']
out.mkdir(parents=True)
rows = []
for path in paths:
    data = path.read_bytes()
    relative = path.relative_to(root)
    target = out / 'originals' / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    rows.append({'path': relative.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'retained': target.relative_to(out).as_posix()})
for repeat in range(2):
    for row in rows:
        for path in [root / row['path'], out / row['retained']]:
            data = path.read_bytes()
            assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
manifest = {'schema': 'guard-art-actual-UE-threeRED-v001', 'actual_build_exit': 0, 'actual_source_files': 217, 'semantic_RED': 3, 'warnings': 0, 'assertions_relaxed': False, 'source_and_copy_SHA_passes': 2, 'files': rows, 'formal_complete_units': 0}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'actual_threeRED_preserved': True, 'manifest': (out / 'manifest.json').as_posix(), 'files': len(rows)}))
