"""Prepare exact numeric/crop evidence before any new diagnostic viewing."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path('F:/Ourgame')
source = root / 'source-assets/production/fairytale-sword-primary2-v001/primary2-measurement-v001'
freeze = source / 'measurement-freeze-v001.json'
assert hashlib.sha256(freeze.read_bytes()).hexdigest() == '289cef5e752abb873999df9ef2ba30b6a736d847319108ba2131b3cf50282b11'
doc = json.loads(freeze.read_text(encoding='utf-8-sig'))
archive = root / '过程图稿与视频/2026-10-16_军剑第二段真实掌心足底测量_v001'
assert not archive.exists()
(archive / '原件').mkdir(parents=True)
(archive / '展示副本').mkdir()
pins = []
for path in sorted(p for p in source.rglob('*') if p.is_file()):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if path != freeze:
        row = next(x for x in doc['files'] if Path(x['path']) == path)
        assert len(data) == row['bytes'] and digest == row['sha256']
    targets = [archive / '原件' / path.relative_to(source)]
    if path.suffix == '.png': targets.append(archive / '展示副本' / path.name)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        assert target.read_bytes() == data and path.read_bytes() == data
        pins.append({'source': path.as_posix(), 'copy': target.relative_to(archive).as_posix(),
                     'bytes': len(data), 'sha256': digest})
(archive / '.gdignore').write_bytes(b'')
index = {'source_version': 'native169/measurement-v001', 'files': pins,
 'status': 'actual RGBA numeric candidates; new crops not yet viewed at freeze',
 'grip_accepted': False, 'actual_hidden_bones_or_blade_axis_known': False,
 'footlock_accepted': False, 'runtime_imported': False,
 'previous_source_retention': 'E194', 'not_publication_or_acceptance': True}
(archive / 'source-version-status-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
(archive / 'README.md').write_text('原始512源已E194保留；本批仅真实掌心/近手轮廓/鞋接触带数据和无缩放裁图。近掌是可见手套候选，不是隐藏握柄/骨位；近鞋横移约2.27屏幕px，不能称足锁。先E留档，再root审图。无导入、无动作接受。\n', encoding='utf-8')
print(json.dumps({'archive': archive.as_posix(), 'exact_source_files': 23, 'presentation_crops': 18, 'copied_endpoints': len(pins)}, ensure_ascii=False))
