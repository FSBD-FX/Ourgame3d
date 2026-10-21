"""Root archives approved hero identity, standard guides and exact row prompts."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path('F:/Ourgame').resolve()
base = root / 'source-assets/production/fairytale-hero-state-gap-v001'
candidate = base / 'standard-input-candidate-v001'
batch = candidate / 'process-batches/2026-10-18-right-body-states-v001'
out = root / '过程图稿与视频/2026-10-18_钟盔闪避受挫死亡标准输入_v001'
assert not out.exists()


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


freeze_path = candidate / 'standard-input-freeze-v001.json'
assert fact(freeze_path)['sha256'] == '3a4e5fbaa085e2606deb7d87e27a5d1abe2d18705e40f2a446ee4a663b2a2066'
freeze = json.loads(freeze_path.read_text(encoding='utf-8-sig'))
assert len(freeze['files']) == 18
for row in freeze['files']:
    assert fact(row['path']) == row
index = json.loads((batch / 'batch-index-v001.json').read_text(encoding='utf-8-sig'))
for row in index['files']:
    assert fact(row['path']) == row
anchor = index['identity_anchor']
assert fact(anchor['path']) == anchor and anchor['sha256'] == 'd3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
for state in ['dodge', 'hurt', 'death']:
    refs = batch / ('native-' + state + '-references-v001.json')
    assert not refs.exists()
    refs.write_text(json.dumps({'references_in_order': [
        {'file': anchor, 'role': 'ONLY accepted nativeRight SwordReady v002 frame0 BODY identity; no armor or weapon baked. Retain this archive in E before generation.', 'already_retained': True},
        {'file': fact(batch / 'references/layout-guides' / (state + '.png')), 'role': 'Standard slot count and safe padding guide only, no hidden marker or identity. E retain before View/native.', 'already_retained': True},
    ]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
files = [Path(row['path']) for row in freeze['files']] + [freeze_path] + sorted(p for p in batch.rglob('*') if p.is_file()) + [Path(anchor['path']), Path(__file__)]
(out / '原件').mkdir(parents=True)
(out / '展示副本').mkdir()
rows = []
for i, path in enumerate(dict.fromkeys(files)):
    target = out / '原件' / (f'{i:03d}-' + path.name)
    shutil.copy2(path, target)
    assert all(fact(path)[key] == fact(target)[key] for key in ['bytes', 'sha256'])
    rows.append({'source': fact(path), 'retained': target.relative_to(out).as_posix()})
for name, path in [('identity-anchor', Path(anchor['path']))] + [(state + '-guide', batch / 'references/layout-guides' / (state + '.png')) for state in ['dodge', 'hurt', 'death']]:
    shutil.copy2(path, out / '展示副本' / (name + '.png'))
(out / 'source-version-status-index.json').write_text(json.dumps({'schema': 'hero-native-standard-input-archive-v001', 'status': 'STANDARD_INPUT_NOT_GENERATED_E_RETENTION_PENDING', 'files': rows, 'formal_complete_units': 0}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(out / 'README.md').write_text('钟盔身体四帧闪避、四帧破韧受挫、五帧死亡标准输入。唯一现行Ready身份，不含武器甲、无实际骨点或20组合验收；无AI生成或UE调用。原件和展示副本必须E保全后View或生成。\n', encoding='utf-8')
old = root / 'tools/scripts/native-fairytale-guard-v001.py'
new = root / 'tools/scripts/native-hero-state-v001.py'
assert not new.exists()
text = old.read_text(encoding='utf-8-sig')
replacements = {
    "BASE = ROOT / 'source-assets/production/fairytale-guard-v001'": "BASE = ROOT / 'source-assets/production/fairytale-hero-state-gap-v001'",
    "asset='fairytale-guard003-'+output.parent.name": "asset='fairytale-hero-nativeRight-'+output.stem",
    "scope='Guard003 new identity/component candidate; Base Lock and standard row preparation remain separate gates'": "scope='Current bell-helmet body-only new action candidate; equipment modules and measured source registration remain separate gates'",
}
for before, after in replacements.items():
    assert text.count(before) == 1, before
    text = text.replace(before, after)
new.write_text(text, encoding='utf-8')
print(json.dumps({'archive': out.as_posix(), 'files': len(rows), 'new_native_accounting_helper': fact(new), 'E_before_View_required': True}, ensure_ascii=False))
