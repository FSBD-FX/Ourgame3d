"""New review capsule; original media indices remain frozen at their historical state."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path('F:/Ourgame')
D = R / 'docs/production/first-batch-v2'
B = R / 'source-assets/production/fairytale-armor-sword-primary1-v001'
A = R / '过程图稿与视频/2026-10-16_首斩穿甲实录复核与工程检查点_v001'
assert not A.exists()


def desc(p):
    data = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


files = [D / 'runtime-review-fairytale-sword-armor-primary1-v001.md', D / 'runtime-review-fairytale-sword-armor-primary1-v001.json',
         D / 'progress.json', R / 'README.md', R / 'AGENTS.md', R / '项目需求台账.md', R / '试玩操作说明.md',
         R / '.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md',
         R / 'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md', Path(__file__),
         R / 'tools/scripts/checkpoint-primary1-armor42-runtime-v001.py', R / '钟盔军剑首斩穿甲试装.cmd',
         R / 'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for folder in [D / 'evidence/primary1-armor-v001', D / 'evidence/run-codec-v001']:
    files.extend(p for p in folder.rglob('*') if p.is_file())
for name in ['root-body-partition-review-v001.json', 'root-native164-167-review-v001.json', 'root-static42-candidate-review-v001.json',
             'root-hidden-registration-design-v002.json', 'far-fit32x30-design-v003.json', 'far-fit32x30-input-freeze-v003.json',
             'body-partition-peer-review-v001.md', 'body-partition-peer-review-v001.json']:
    files.append(B / name)
files.append(B / 'run-farshoulder-primary1-v003/sprite-request.json')
for folder in ['farshoulder-extraction-v001', 'farshoulder-extraction-v002']:
    freeze = B / folder / 'extracted-failure-freeze-v001.json'
    files.append(freeze)
    for entry in load(freeze)['files']:
        p = Path(entry['path'])
        assert desc(p) == entry
        files.append(p)
for folder, name in [('body-partition-v001','partition-freeze-v001.json'),
                     ('chest-extraction-v001','extracted-freeze-v001.json'),
                     ('nearshoulder-extraction-v001','extracted-freeze-v001.json'),
                     ('farshoulder-extraction-v003','extracted-freeze-v001.json'),
                     ('macro-registration-primary1-v001','delivery-freeze-v001.json')]:
    files.append(B / folder / name)
macro = B / 'macro-registration-primary1-v001'
files.extend(p for p in macro.glob('*') if p.is_file() and p.suffix in ('.json', '.py', '.md'))
for p in B.glob('*body*review*.json'):
    files.append(p)
files.extend(p for p in (B / 'body-partition-v001').glob('*review*') if p.is_file())
runtime = R / 'source-assets/production/fairytale-sword-armor-primary1-runtime-v001'
files.extend(p for p in runtime.rglob('*') if p.is_file())
files.extend((R / 'UnrealGame/Saved/Bootstrap').glob('sword-armor-primary1-v001-import-*.json'))
for name in ['prepare-sword-armor-primary1-import-v001.py', 'ue_sword_armor_primary1_v001_checks.py', 'ue-import-sword-armor-primary1-v001.py',
             'import-sword-armor-primary1-v001.ps1', 'bind-sword-armor-primary1-import-v001.py',
             'launch-fairytale-sword-armor-primary1-v001.ps1', 'verify-sword-armor-primary1-v001.py',
             'verify-sword-armor-primary1-v001.ps1', 'verify-ready-primary-body-pixel-presence-v001.py',
             'postprocess-sword-armor-primary1-v001.py', 'freeze-primary1-armor-build-v001.py', 'test-first-room.ps1']:
    files.append(R / 'tools/scripts' / name)
for name in ['DungeonHUD.h', 'DungeonHUD.cpp', 'DungeonFairytaleSwordPresentation.cpp', 'DungeonFairytaleSwordDrawState.h',
             'DungeonFairytaleSwordProbe.cpp', 'DungeonRunSnapshotCodec.h', 'DungeonRunSnapshotCodec.cpp',
             'Tests/DungeonRunSnapshotCodecTests.cpp', 'Tests/RunCodecFixture_v001.h']:
    files.append(R / 'UnrealGame/Source/CodexDungeon' / name)
for version in ['2026-10-16_RunCodecStage0-actual4RED-v102', '2026-10-16_RunCodec3GREEN1RED-PrimaryArmor42-unrendered-v103',
                '2026-10-16_RunCodecNULfix-actual130GREEN-PrimaryArmor42-v104']:
    files.append(R / 'source-assets/production/backups' / version / 'compiled-source-manifest.json')
for stamp in ['122948', '125747', '130720']:
    files.append(R / 'UnrealGame/Saved/Bootstrap' / ('build-editor-20261016-' + stamp + '.log'))
for stamp in ['123141', '125902', '130934', '131229']:
    files.append(R / 'UnrealGame/Saved/Automation' / ('FirstRoom-20261016-' + stamp) / 'index.json')
capture = R / '过程图稿与视频/2026-10-16_钟盔军剑首斩穿甲真实按键试装_v001'
files.extend(capture / name for name in ['index.json', 'source-version-status-index.json', 'README.md'])
files.extend(capture / '原件' / name for name in ['compiled-source-binding-audit-v001.json', 'native-async-write-summary.json',
             'native-pixel-verification.json', 'sword-armor-primary1-runtime-verification.json', 'visible-ready-primary-head-gate-v001.json',
             'selected-frame-source-map-v001.json', 'video-presentation-receipt-v001.json'])
player = R / '过程图稿与视频/2026-10-16_军剑首斩穿甲播放复核_v001'
files.extend(player / name for name in ['index.json', 'review-player.html', 'README.md'])
for suffix in ['primary1-armor42-realJ-runtime-v181', 'primary1-armor42-player-v182']:
    files.append(Path('E:/OurGame/Knight/过程图稿与视频') / ('2026-10-16-OurgameUE-' + suffix) / 'source-size-SHA256.json')
entries = []
assert all(p.is_file() for p in files), [str(p) for p in files if not p.is_file()]
(A / '原件').mkdir(parents=True)
(A / '展示副本').mkdir()
for i, p in enumerate(dict.fromkeys(files)):
    assert p.is_file(), p
    t = A / '原件' / f'{i:03d}-{p.name}'
    assert not t.exists()
    before = desc(p)
    shutil.copy2(p, t)
    assert desc(p) == before and t.read_bytes() == p.read_bytes()
    entries.append({'source':before, 'retained_relative':t.relative_to(A).as_posix()})
for name in ['ready-right.png', 'cut-right.png', 'follow-left.png']:
    p = player / '展示副本' / name
    t = A / '展示副本' / name
    shutil.copy2(p, t)
    assert p.read_bytes() == t.read_bytes()
    entries.append({'source':desc(p), 'retained_relative':t.relative_to(A).as_posix(), 'resampled':False})
(A / 'README.md').write_text('EV048首斩穿甲实景与工程复核总包。保留原生失败166/167旧规格、身体/部件/组合设计和真实v103实录检查、独立源码/原帧/最终构建审计，以及Codec实际4RED、3GREEN1RED和NUL窄修后4/130GREEN。原录像及175帧不重复复制，引用E181/E182已保全媒体；三个展示图为原生裁切的字节副本。录像仍v103，当前工程v104，连续动作/正式装备/全状态/敌人音效/磁盘Continue未完成。正式0/15、目标active；本总包复制前工作进度中的E183状态为pending，实际完成另记，不倒改源索引。\n', encoding='utf-8')
(A / 'source-version-status-index.json').write_text(json.dumps({'schema':'primary1-armor-final-review-capsule-v1',
    'status':'Bounded real-input first-cut armor trial reviewed; source/asset provenance and full130 code regression passed; art/full content unaccepted',
    'movie_snapshot':'v103', 'current_engine_snapshot':'v104', 'human_event':'EV048 continued',
    'formal_complete_units':0, 'goal_status':'active', 'native_source_failures_retained':True,
    'files':entries, 'size_SHA_mismatches':0, 'retention_E183':'pending_copy'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'archive':A.as_posix(), 'files':len(entries), 'source_bytes':sum(x['source']['bytes'] for x in entries), 'mismatches':0}, ensure_ascii=False))
