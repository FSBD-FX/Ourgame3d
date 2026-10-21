"""Preserve the reproducible selector failure; derive NEW v002 with one fix."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
original = HERE / 'verify-local-locomotion-audio-v001.py'
raw = original.read_bytes()
failed = HERE / 'provenance/standalone-verifier-failed-attempt-v001'
failed.mkdir()
with (failed / 'verify-local-locomotion-audio-v001.py').open('xb') as stream:
    stream.write(raw)
result = subprocess.run([sys.executable, '-B', '-X', 'utf8', str(original)], capture_output=True)
with (failed / 'actual-stderr.log').open('xb') as stream:
    stream.write(result.stderr)
with (failed / 'actual-stdout.log').open('xb') as stream:
    stream.write(result.stdout)
assert result.returncode == 1 and b'footstep00.ogg' in result.stderr
manifest = json.loads((HERE / 'manifest.json').read_text('utf-8'))
relative_catalog_rows = [row['local_catalog_row'] for row in manifest['sources']
                         if not Path(row['local_catalog_row']['path']).is_absolute()]
assert len(relative_catalog_rows) == 8
analysis = {
    'actual_exit_code': result.returncode,
    'cause': 'Recursive pin selector mistook relative package catalog rows for absolute file pins; not an audio/source/recipe/decode failure',
    'relative_catalog_rows_count': len(relative_catalog_rows),
    'failure_preserved': True, 'assets_changed': False,
    'manifest_sha256': hashlib.sha256((HERE / 'manifest.json').read_bytes()).hexdigest(),
    'fix_scope': 'NEW verifier v002 selects only absolute path pins; relative catalog rows remain separately checked against ZIP members and original OGG hashes',
}
with (failed / 'failure-analysis.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(analysis, ensure_ascii=False, indent=2) + '\n')
old = b"if all(k in node for k in ('path', 'bytes', 'sha256')):"
new = b"if all(k in node for k in ('path', 'bytes', 'sha256')) and Path(node['path']).is_absolute():"
assert raw.count(old) == 1
with (HERE / 'verify-local-locomotion-audio-v002.py').open('xb') as stream:
    stream.write(raw.replace(old, new))
print(json.dumps(analysis, ensure_ascii=False))
