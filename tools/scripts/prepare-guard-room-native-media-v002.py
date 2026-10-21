"""Preserve v001 media helper; independently verify its E copies before review."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys


def fact(path):
    path = Path(path).resolve()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return {'path': path.as_posix(), 'bytes': path.stat().st_size, 'sha256': h.hexdigest()}


parser = argparse.ArgumentParser()
parser.add_argument('--archive', required=True)
parser.add_argument('--retain-name', required=True)
args = parser.parse_args()
root = Path('F:/Ourgame').resolve()
retain_root = Path('E:/OurGame/Knight/过程图稿与视频').resolve()
readme = fact(retain_root / 'README.md')
target = retain_root / args.retain_name
assert target.parent == retain_root and not target.exists()
result = subprocess.run([
    sys.executable, '-B', '-X', 'utf8',
    str(root / 'tools/scripts/prepare-guard-room-native-media-v001.py'),
    '--archive', args.archive, '--retain-name', args.retain_name,
], cwd=root, check=False)
assert result.returncode == 0, 'Preserve failed helper output; no review authorized'
index = json.loads((target / 'E-retention-index-v001.json').read_text(encoding='utf-8-sig'))
for row in index['files']:
    assert fact(row['source']['path']) == row['source'], row['source']['path']
    assert fact(row['retained']['path']) == row['retained'], row['retained']['path']
    assert all(row['source'][key] == row['retained'][key] for key in ['bytes', 'sha256'])
assert fact(retain_root / 'README.md') == readme
receipt = target / 'independent-final-second-SHA256-pass-v002.json'
assert not receipt.exists()
receipt.write_text(json.dumps({
    'schema': 'guard-room-native-independent-final-retention-v002',
    'status': 'ALL_ORIGINALS_AND_PRESENTATION_RETAINED_BEFORE_ROOT_REVIEW',
    'first_pass_helper': fact(root / 'tools/scripts/prepare-guard-room-native-media-v001.py'),
    'second_pass_helper': fact(Path(__file__)),
    'retention_index': fact(target / 'E-retention-index-v001.json'),
    'file_count': len(index['files']), 'total_bytes': index['total_bytes'],
    'source_and_target_mismatches': 0, 'verification_passes': 2,
    'E_root_README_before_and_after': readme,
    'visual_reviewed': False, 'normal_J_full_clear': False,
    'formal_complete_units': 0,
}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'independent_second_pass': fact(receipt), 'E_root_README_unchanged': True}, ensure_ascii=False))
