"""Copy explicit UE process batches to the user's required E: retention root.

F: stays canonical. Never walks unrelated projects, overwrites batches or changes
the E: root README. Both successful and failed supplied batches are preserved.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil

SOURCE_ROOT = Path('F:/Ourgame/过程图稿与视频').resolve()
DEST_ROOT = Path('E:/OurGame/Knight/过程图稿与视频').resolve()
parser = argparse.ArgumentParser()
parser.add_argument('--batch', required=True)
parser.add_argument('--source', action='append', required=True)
args = parser.parse_args()
assert args.batch.startswith('2026-') and '/' not in args.batch and '\\' not in args.batch
destination = DEST_ROOT / args.batch
assert destination.parent == DEST_ROOT
assert not destination.exists(), f'Existing batch must not be overwritten: {destination}'

def io_path(path):
    return Path("\\\\?\\" + str(path.resolve())) if os.name == "nt" else path


def digest(path):
    h = hashlib.sha256()
    with io_path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

sources = []
for name in args.source:
    source = (SOURCE_ROOT / name).resolve()
    assert source.parent == SOURCE_ROOT and source.is_dir(), source
    assert not source.is_symlink()
    sources.append(source)
assert len(set(sources)) == len(sources)
root_readme = DEST_ROOT / 'README.md'
root_readme_hash = digest(root_readme)
destination.mkdir()
(destination / '.gdignore').write_bytes(b'')
entries = []
for source in sources:
    for path in sorted(source.rglob('*')):
        assert not path.is_symlink(), path
        if not path.is_file():
            continue
        relative = path.relative_to(SOURCE_ROOT)
        target = destination / 'F盘原批次副本' / relative
        assert target.resolve().is_relative_to(destination.resolve())
        io_path(target).parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists()
        size, sha = io_path(path).stat().st_size, digest(path)
        shutil.copy2(io_path(path), io_path(target))
        assert io_path(path).stat().st_size == size and digest(path) == sha, f'Source changed: {path}'
        assert io_path(target).stat().st_size == size and digest(target) == sha, target
        entries.append({'source': str(path), 'retained_relative': str(target.relative_to(destination)),
                        'bytes': size, 'sha256': sha, 'source_version': source.name,
                        'status': 'exact_copy; source status and acceptance limits retained'})

for entry in entries:
    target = destination / entry['retained_relative']
    assert io_path(target).stat().st_size == entry['bytes'] and digest(target) == entry['sha256']
assert digest(root_readme) == root_readme_hash
index = {'date': datetime.datetime.now().astimezone().isoformat(), 'canonical_project': 'F:/Ourgame',
         'batch': args.batch, 'file_count': len(entries), 'bytes': sum(e['bytes'] for e in entries),
         'root_readme_unchanged': True, 'source_and_target_hash_mismatches': 0,
         'verification_passes': 2, 'not_publication_or_acceptance': True, 'files': entries}
(destination / 'source-size-SHA256.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
(destination / 'README.md').write_text(
    '# Ourgame UE 过程材料留档\n\n'
    '项目主目录为 F:/Ourgame。本批为用户要求的 E: 展示前保留副本，独立于旧 Knight/Godot 项目。\n\n'
    '完整保留所列 F: 批次的原件、展示副本、来源索引和失败记录；不覆盖旧版本。'
    '候选资源、自动 QA 实录及待审阅状态沿用源索引，不代表正式完成、听感验收或发布。\n\n'
    f"复制 {len(entries)} 项、{index['bytes']} 字节，源/目标大小与 SHA256 两遍核验零差；"
    '未改 E: 根目录 README。详见 source-size-SHA256.json。\n', encoding='utf-8')
print(json.dumps({k: v for k, v in index.items() if k != 'files'}, ensure_ascii=False))
