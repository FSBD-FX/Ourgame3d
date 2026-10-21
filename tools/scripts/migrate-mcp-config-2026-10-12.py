"""One-time, audited relocation of this project's two Codex MCP launch entries."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import tomllib

project = Path(__file__).resolve().parents[2]
if project != Path('F:/Ourgame'):
    raise RuntimeError('This migration is specific to F:/Ourgame.')
config = Path.home() / '.codex/config.toml'
original = config.read_text(encoding='utf-8-sig')
before = tomllib.loads(original)
expected = copy.deepcopy(before)

def relocate(value):
    if isinstance(value, str):
        return value.replace('E:/codex_game', 'F:/Ourgame').replace('E:\\codex_game', 'F:\\Ourgame')
    if isinstance(value, list):
        return [relocate(item) for item in value]
    if isinstance(value, dict):
        return {key: relocate(item) for key, item in value.items()}
    return value

for name in ('blender-mcp', 'unreal-mcp'):
    expected['mcp_servers'][name] = relocate(expected['mcp_servers'][name])
expected['mcp_servers']['blender-mcp']['command'] = 'F:/Ourgame/tools/runtime/blender-mcp/.venv/Scripts/python.exe'
expected['mcp_servers']['blender-mcp']['args'] = ['F:/Ourgame/tools/scripts/run-blender-mcp.py', '--host', '127.0.0.1', '--port', '9876']

chunks = re.split(r'(?m)(?=^\[)', original)
for index, chunk in enumerate(chunks):
    header = chunk.splitlines()[0] if chunk else ''
    if re.fullmatch(r'\[mcp_servers\.(blender-mcp|unreal-mcp)(?:\.env)?\]', header):
        chunk = chunk.replace('E:/codex_game', 'F:/Ourgame').replace('E:\\\\codex_game', 'F:\\\\Ourgame').replace('E:\\codex_game', 'F:\\Ourgame')
        if header == '[mcp_servers.blender-mcp]':
            for field in ('command', 'args'):
                pattern = r'(?m)^' + field + r'\s*=\s*' + (r'\[[\s\S]*?\]' if field == 'args' else r'[^\n]*')
                replacement = field + ' = ' + json.dumps(expected['mcp_servers']['blender-mcp'][field], ensure_ascii=False)
                chunk, count = re.subn(pattern, lambda _: replacement, chunk, count=1)
                if count != 1:
                    raise RuntimeError(f'Expected one Blender {field} line.')
        chunks[index] = chunk
updated = ''.join(chunks)
if tomllib.loads(updated) != expected:
    raise RuntimeError('Configuration diff extends beyond the intended two MCP entries; no write performed.')
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup = config.parent / 'backups' / f'config.pre-ourgame-migration-{stamp}.toml'
backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(original, encoding='utf-8')
config.write_text(updated, encoding='utf-8')
record = {'date': '2026-10-12', 'config': str(config), 'backup': str(backup), 'updated_servers': ['blender-mcp', 'unreal-mcp'], 'all_other_settings_preserved': True, 'blender_entry': 'project Python + import wrapper; copied EXE launcher avoided', 'new_root': str(project)}
(project / 'docs/mcp-path-migration-2026-10-12.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False, indent=2))
