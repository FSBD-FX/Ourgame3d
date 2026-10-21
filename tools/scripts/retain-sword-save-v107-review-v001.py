"""Preserve bounded review/actual IO evidence without duplicating native movies."""
from pathlib import Path
import hashlib
import json
import re
import shutil

R = Path('F:/Ourgame')
A = R / '过程图稿与视频/2026-10-16_军剑辨识与局内磁盘存档复核_v001'
assert not A.exists()
(A / '原件').mkdir(parents=True)
(A / '展示副本').mkdir()
S = R / 'source-assets/production/backups/2026-10-16_RunSaveAdapter-actual134GREEN-v107'
inputs = []
for relative in ('README.md', 'AGENTS.md', '项目需求台账.md', 'docs/production/first-batch-v2/progress.json',
 'docs/production/first-batch-v2/run-save-adapter-runtime-proof-v001.md',
 'docs/production/first-batch-v2/runtime-review-sword-readability-v001.md',
 'docs/production/first-batch-v2/runtime-review-sword-readability-v001.json',
 'tools/scripts/audit-run-save-adapter-v107.py', 'tools/scripts/checkpoint-save-adapter-v107.py',
 'source-assets/production/first-unit-animation-v003/generation-ledger.json',
 'source-assets/production/fairytale-sword-primary2-v001/root-native168-source-review-v001.json',
 'source-assets/production/fairytale-sword-primary2-v001/primary2-extraction-v002/extracted-freeze-v002.json',
 'source-assets/production/fairytale-sword-primary2-v001/primary2-measurement-v001/measurement-freeze-v001.json'):
    inputs.append((R / relative, Path('原件') / relative))
inputs.append((S / 'compiled-source-manifest.json', Path('原件/v107-compiled-source-manifest.json')))
for directory in ('docs/production/first-batch-v2/evidence/run-save-adapter-v001',
                  'docs/production/first-batch-v2/evidence/sword-readability-v001'):
    inputs.extend((p, Path('原件') / p.relative_to(R)) for p in (R / directory).rglob('*') if p.is_file())
for name in ('DungeonRunSaveAdapter.h', 'DungeonRunSaveAdapter.cpp', 'Tests/DungeonRunSaveAdapterTests.cpp',
             'DungeonFairytaleSwordBodyV002.inl', 'DungeonFairytaleSwordPresentation.cpp',
             'DungeonFairytaleSwordDrawState.h', 'DungeonFairytaleSwordProbe.cpp', 'DungeonHUD.cpp'):
    relative = Path('UnrealGame/Source/CodexDungeon') / name
    inputs.append((S / relative, Path('原件/v107-exact-source') / name))
reports = ['UnrealGame/Saved/Automation/FirstRoom-20261016-' + stamp + '/index.json'
           for stamp in ('140335', '142054', '142409')]
fixtures = set()
for relative in reports:
    path = R / relative
    inputs.append((path, Path('原件/actual-reports') / (path.parent.name + '.json')))
    report = json.loads(path.read_text(encoding='utf-8-sig'))
    for test in report['tests']:
        if not test['fullTestPath'].startswith('CodexDungeon.Content.RunSaveAdapter.'):
            continue
        for entry in test['entries']:
            match = re.search(r'Retained real isolated run-only save IO: (.+)$', entry['event']['message'])
            if match:
                folder = Path(match.group(1)).resolve()
                folder.relative_to(R / 'UnrealGame/Saved/Automation/RunSaveAdapter')
                assert re.fullmatch('[0-9A-F]{32}', folder.name)
                fixtures.add(folder)
for folder in sorted(fixtures):
    for path in sorted(p for p in folder.rglob('*') if p.is_file()):
        suffix = path.relative_to(folder).as_posix()
        label = hashlib.sha256(suffix.encode()).hexdigest()[:16] + '-' + path.name
        inputs.append((path, Path('原件/actual-IO') / folder.name / label))
for stamp in ('140235', '141911'):
    p = R / f'UnrealGame/Saved/Bootstrap/build-editor-20261016-{stamp}.log'
    inputs.append((p, Path('原件/actual-logs') / p.name))
for stamp in ('140335', '142054', '142409'):
    p = R / f'UnrealGame/Saved/Bootstrap/first-room-tests-20261016-{stamp}.log'
    inputs.append((p, Path('原件/actual-logs') / p.name))
for relative in ('docs/production/first-batch-v2/run-save-adapter-runtime-proof-v001.md',
                 'docs/production/first-batch-v2/runtime-review-sword-readability-v001.md'):
    inputs.append((R / relative, Path('展示副本') / Path(relative).name))
unique = {}
for source, relative in inputs:
    assert relative not in unique or unique[relative] == source
    unique[relative] = source
rows = []
for relative, source in sorted(unique.items(), key=lambda x: x[0].as_posix()):
    data = source.read_bytes()
    target = A / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists()
    shutil.copy2(source, target)
    assert target.read_bytes() == data and source.read_bytes() == data
    rows.append({'source': source.as_posix(), 'copy': relative.as_posix(), 'bytes': len(data),
                 'sha256': hashlib.sha256(data).hexdigest()})
index = {'version': 'v107-review-v001', 'source_version': 'v105 sword movie; v107 SaveAdapter Source/full134',
 'status': 'actual Root review and bounded tests passed; pristine process Continue/full content not complete',
 'files': rows, 'actual_IO_roots': len(fixtures), 'movies_already_retained': ['E185', 'E189'],
 'source_and_diagnostics_already_retained': ['E188', 'E190', 'E193', 'E194', 'E195'],
 'not_publication_or_acceptance': True, 'formal_complete_units': 0, 'goal_status': 'active'}
(A / 'source-version-status-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
(A / '.gdignore').write_bytes(b'')
(A / 'README.md').write_text('本批保存实际存档源码、RED/GREEN/全134报告、原磁盘IO和军剑实景复核；录像已E185/E189保全，不重复复制。v105录像来源不改为v107。169第二段是尚未导入的测量/剑适配候选。新进程Continue、完整D13及完整单位仍待。正式0/15，目标active。\n', encoding='utf-8')
print(json.dumps({'archive': A.as_posix(), 'copied_files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'IO_roots': len(fixtures)}, ensure_ascii=False))
