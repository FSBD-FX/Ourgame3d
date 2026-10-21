"""Immutable source/DLL/production-asset provenance for a real UE capture."""
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

def io_path(path):
    return Path("\\\\?\\" + str(path.resolve())) if os.name == "nt" else path


def plain_paths(paths):
    for path in paths:
        value = str(path)
        yield Path(value[4:]) if value.startswith("\\\\?\\") else path


parser = argparse.ArgumentParser()
parser.add_argument('--name', required=True)
parser.add_argument('--automation-report', default='')
parser.add_argument('--interrupted-run-log', default='')
parser.add_argument('--status', required=True)
parser.add_argument('--build-log', default='')
parser.add_argument('--candidate-freeze', required=True)
parser.add_argument('--candidate-freeze-sha256', required=True)
args = parser.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_-]+', args.name):
    raise RuntimeError('Snapshot name must be one directory component')
root = Path('F:/Ourgame')
destination = root / 'source-assets/production/backups' / args.name
if io_path(destination).exists():
    raise RuntimeError('Preserve prior versions; destination already exists')
if bool(args.automation_report) == bool(args.interrupted_run_log):
    raise RuntimeError('Supply one actual completed automation report OR an interrupted run log; never invent test counts')
automation_path = (root / (args.automation_report or args.interrupted_run_log)).resolve()
automation_path.relative_to(root)
automation = json.loads(io_path(automation_path).read_text(encoding='utf-8-sig')) if args.automation_report else None
if automation is None:
    raise RuntimeError('P3 capture requires the actual completed strict full141 report; interrupted evidence cannot claim readiness')
if automation['succeeded'] != 141 or any(automation[k] != 0 for k in ('succeededWithWarnings','failed','notRun','inProcess')):
    raise RuntimeError('Actual strict141 report is not GREEN')
if len(automation['tests']) != 141 or len({t['fullTestPath'] for t in automation['tests']}) != 141:
    raise RuntimeError('Actual141 registered names are not unique/complete')
if any(t['state'] != 'Success' or t['warnings'] != 0 or t['errors'] != 0 for t in automation['tests']):
    raise RuntimeError('Actual141 has a non-Success/error/warning result')
if not args.build_log:
    raise RuntimeError('Preserve the actual successful build log')
paths = [p for directory in ('UnrealGame/Source', 'UnrealGame/Config', 'UnrealGame/Content/Production')
         for p in plain_paths((io_path(root / directory)).rglob('*')) if io_path(p).is_file()]
paths.extend([automation_path, root / 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'])
if args.build_log:
    build_log = (root / args.build_log).resolve()
    build_log.relative_to(root)
    paths.append(build_log)
paths.append(root / 'tools/scripts/test-first-room.ps1')
paths.extend(p for p in plain_paths((io_path(root / 'tools/scripts')).glob('*.py')) if 'armor' in p.name or 'capture' in p.name)
paths.extend([root / 'tools/scripts/verify-content-combat.ps1', root / 'tools/scripts/freeze-first-unit-build.py'])
paths.append(root / 'tools/scripts/import-xbw-walk-v002.ps1')
paths.append(root / 'tools/scripts/verify-xbw-equipment-hold.py')
paths.append(root / 'tools/scripts/verify-clean-interface-scale.py')
paths.append(root / '试玩操作说明.md')
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-first-batch-audio-v002.py', 'import-first-batch-audio-v002.ps1'))
paths.append(root / 'source-assets/production/first-batch-audio-v002/manifest.json')
paths.extend(plain_paths((io_path(root / 'source-assets/production/first-batch-audio-v002/wav')).glob('*.wav')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('first-batch-audio-v002-import-*.json')))
paths.extend(plain_paths((io_path(root / 'source-assets/production/first-unit-armor-layers-v001/manifests')).glob('import-armor-*.json')))
paths.extend(plain_paths((io_path(root / 'source-assets/production/first-batch-XBW-armor-layers-v001/manifests')).glob('import-XBW-*-four-armors-v001.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('armor-*-import*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-armor-*-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-walk-v002-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-armor-walk-v002-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-weapon-components-v001.py', 'ue-import-xbw-ready-idle-v001.py',
    'ue-import-xbw-primary-v001.py', 'ue-import-xbw-reload-v001.py', 'ue-import-scene-exploration-props-v001.py',
    'ue-import-xbw-walk-v002.py', 'ue-import-xbw-armor-walk-v002.py', 'ue_xbw_walk_v002_checks.py'))
paths.extend(root / relative for relative in (
    'source-assets/production/first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json',
    'source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json',
    'source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-primary-v001.json',
    'source-assets/production/first-batch-weapon-actions-v001/manifests/import-XBW-reload-four-keyposes-v001.json',
    'source-assets/production/first-batch-weapon-actions-v001/manifests/weapon-state-lifecycle-v001.json',
    'source-assets/production/first-batch-XBW-walk-v001/manifests/import-XBW-common-walk-v002.json',
    'source-assets/production/first-batch-XBW-walk-v001/manifests/import-XBW-walk-four-armors-v002.json',
    'source-assets/production/first-batch-XBW-walk-v001/manifests/XBW-walk-neutral-state-minus1-extension-v003.json',
    'source-assets/production/scene-exploration-props-v001/manifests/import-scene-exploration-props-v001.json'))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('weapon-components-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-ready-idle-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-primary-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('xbw-reload-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('scene-exploration-props-v001-import-*.json')))
paths.extend(root / relative for relative in (
    'tools/scripts/play-first-room.ps1', 'tools/scripts/smoke-manual-weapon-preview.ps1',
    '开始试玩.cmd', '猎弩手动试玩.cmd', '场景探索试玩.cmd', '暗黑童话造型预览.cmd'))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-fairytale-lookdev-v001.py', 'ue_fairytale_lookdev_v001_checks.py',
    'import-fairytale-lookdev-v001.ps1', 'verify-fairytale-lookdev.py',
    'verify-fairytale-lookdev.ps1', 'extract-sprite-shared-row-scale.py',
    'prepare-fairytale-walk-phase-guide-v001.py', 'retain-save-generation-proof.py',
    'assemble-fairytale-walk-source-row-v001.py',
    'register-fairytale-walk-source-cell-v001.py', 'register-fairytale-walk-source-cell-v002.py'))
paths.append(root / 'tools/tests/test_sprite_shared_row_scale.py')
paths.append(root / 'source-assets/production/fairytale-lookdev-v001/manifests/import-lookdev-v001.json')
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-lookdev-v001-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-fairytale-walk-lookdev-v001.py', 'ue_fairytale_walk_lookdev_checks.py',
    'import-fairytale-walk-lookdev-v001.ps1', 'verify-fairytale-walk-lookdev.py',
    'verify-fairytale-walk-lookdev.ps1'))
paths.append(root / 'source-assets/production/fairytale-walk-lookdev-v001/manifests/import-walk-lookdev-v001.json')
paths.append(root / 'source-assets/production/fairytale-walk-lookdev-v001/manifests/old-production863-before-import.json')
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-walk-lookdev-v001-import-*.json')))
paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-walk-lookdev-v001/import-tool-version-used')).glob('*.py')))
paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-walk-lookdev-v001/import-tool-version-used')).glob('*.ps1')))
paths.append(root / '暗黑童话步态预览.cmd')
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-fairytale-chest-lookdev-v001.py', 'ue_fairytale_chest_lookdev_checks.py',
    'import-fairytale-chest-lookdev-v001.ps1', 'verify-fairytale-chest-lookdev.py',
    'verify-fairytale-chest-lookdev.ps1'))
paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-chest-lookdev-v001/manifests')).glob('*.json')))
paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-chest-lookdev-v001/import-tool-version-used')).glob('*')))
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-chest-lookdev-v001-import-*.json')))
shoulder = root / 'source-assets/production/fairytale-shoulder-lookdev-v001'
if io_path(shoulder).is_dir():
    paths.extend(plain_paths((io_path(shoulder / 'manifests')).glob('*.json')))
    paths.extend(plain_paths((io_path(shoulder / 'import-tool-version-used')).glob('*')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'ue-import-fairytale-shoulder-lookdev-v001.py', 'ue_fairytale_shoulder_lookdev_checks.py',
        'import-fairytale-shoulder-lookdev-v001.ps1', 'verify-fairytale-shoulder-lookdev.py',
        'verify-fairytale-shoulder-lookdev.ps1'))
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-shoulder-lookdev-v001-import-*.json')))
    if (io_path(root / '暗黑童话肩甲预览.cmd')).is_file():
        paths.append(root / '暗黑童话肩甲预览.cmd')
limbs = root / 'source-assets/production/fairytale-limb-lookdev-v001'
if io_path(limbs).is_dir():
    paths.extend(plain_paths((io_path(limbs / 'manifests')).glob('*.json')))
    paths.extend(plain_paths((io_path(limbs / 'import-tool-version-used')).glob('*')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'ue-import-fairytale-limb-lookdev-v001.py', 'ue_fairytale_limb_lookdev_checks.py',
        'import-fairytale-limb-lookdev-v001.ps1', 'verify-fairytale-limb-lookdev.py',
        'verify-fairytale-limb-lookdev.ps1', 'freeze-limb-lookdev-source-v001.py',
        'native-near-limb-trial-v001.py'))
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-limb-lookdev-v001-import-*.json')))
    if (io_path(root / '暗黑童话护腕护胫预览.cmd')).is_file():
        paths.append(root / '暗黑童话护腕护胫预览.cmd')
if (io_path(root / '暗黑童话胸甲预览.cmd')).is_file():
    paths.append(root / '暗黑童话胸甲预览.cmd')
limbs2 = root / 'source-assets/production/fairytale-limb-lookdev-v002'
if io_path(limbs2).is_dir():
    paths.extend(plain_paths((io_path(limbs2 / 'manifests')).glob('*.json')))
    paths.extend(plain_paths((io_path(limbs2 / 'import-tool-version-used')).glob('*')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'ue-import-fairytale-limb-lookdev-v002.py', 'ue_fairytale_limb_lookdev_v002_checks.py',
        'import-fairytale-limb-lookdev-v002.ps1', 'verify-fairytale-limb-lookdev-v002.py',
        'verify-fairytale-limb-lookdev-v002.ps1', 'freeze-limb-lookdev-source-v002.py',
        'native-near-limb-trial-v002.py'))
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-limb-lookdev-v002-import-*.json')))
sword = root / 'source-assets/production/fairytale-sword-runtime-v001'
if io_path(sword).is_dir():
    paths.extend(plain_paths((io_path(sword / 'manifests')).glob('*.json')))
    paths.extend(plain_paths((io_path(sword / 'import-tool-version-used')).glob('*')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'ue-import-fairytale-sword-body-v001.py', 'ue_fairytale_sword_body_v001_checks.py',
        'import-fairytale-sword-body-v001.ps1', 'native-fairytale-sword-v001.py',
        'verify-fairytale-sword-body.py', 'verify-fairytale-sword-body.ps1',
        'verify-native-sword-capture-pixels.py'))
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-sword-body-v001-import-*.json')))
    for clip in ('run-ready-v001', 'run-primary1-v002'):
        paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-sword-v001' / clip / 'curated')).glob('*.png')))
    for version in ('ready-extraction-v001','primary1-extraction-v002'):
        paths.append(root / 'source-assets/production/fairytale-sword-v001' / version / 'extracted-freeze-v001.json')
    if (io_path(root / '钟盔军剑动作试装.cmd')).is_file():
        paths.append(root / '钟盔军剑动作试装.cmd')
sword_v002 = root / 'source-assets/production/fairytale-sword-runtime-v002'
if io_path(sword_v002).is_dir():
    paths.extend(plain_paths((io_path(sword_v002 / 'manifests')).glob('*.json')))
    paths.extend(plain_paths((io_path(sword_v002 / 'import-tool-version-used')).glob('*')))
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('fairytale-sword-body-v002-import-*.json')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'prepare-fairytale-sword-body-v002-import.py', 'ue-import-fairytale-sword-body-v002.py',
        'ue_fairytale_sword_body_v002_checks.py', 'import-fairytale-sword-body-v002.ps1',
        'verify-fairytale-sword-body-v002.py', 'verify-fairytale-sword-body-v002.ps1',
        'native-fairytale-sword-v002.py', 'native-fairytale-armor-ready-v002.py'))
    for clip in ('run-ready-v002', 'run-primary1-v003'):
        paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-sword-v001' / clip / 'curated')).glob('*.png')))
    for version in ('ready-extraction-v002', 'primary1-extraction-v003'):
        paths.append(root / 'source-assets/production/fairytale-sword-v001' / version / 'extracted-freeze-v001.json')
    for version in ('ready-measurement-v002', 'primary1-measurement-v003'):
        paths.extend(plain_paths((io_path(root / 'source-assets/production/fairytale-sword-v001' / version)).glob('*')))
    paths.extend(p for p in plain_paths((io_path(sword / 'data-export-v003')).rglob('*')) if io_path(p).is_file())
ready_armor = root / 'source-assets/production/fairytale-sword-armor-ready-runtime-v001'
if io_path(ready_armor).is_dir():
    paths.extend(p for p in plain_paths(io_path(ready_armor).rglob('*')) if io_path(p).is_file())
    paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-armor-ready-v001-import-*.json')))
    paths.extend(root / 'tools/scripts' / name for name in (
        'prepare-sword-armor-ready-import-v001.py', 'ue-import-sword-armor-ready-v001.py',
        'ue_sword_armor_ready_v001_checks.py', 'import-sword-armor-ready-v001.ps1',
        'verify-sword-armor-ready-v001.py', 'verify-sword-armor-ready-v001.ps1',
        'verify-sword-armor-ready-v002.ps1', 'verify-ready-body-pixel-presence-v001.py',
        'prepare-sword-armor-ready-verifiers-v001.py', 'launch-fairytale-sword-body-v002.ps1',
        'launch-fairytale-sword-armor-ready-v001.ps1'))
    macro = root / 'source-assets/production/fairytale-armor-sword-ready-v002/macro-registration-proposed-v001'
    freeze = macro / 'delivery-freeze-v001.json'
    paths.append(freeze)
    paths.extend(Path(row['path']) for row in json.loads(io_path(freeze).read_text(encoding='utf-8-sig'))['files'])
    for name in ('钟盔军剑低位动作试装.cmd','钟盔军剑胸肩试装.cmd'):
        if (io_path(root / name)).is_file(): paths.append(root / name)
# Exact candidate source files used by the new namespace are part of this snapshot.
candidate_freeze = (root / args.candidate_freeze).resolve()
candidate_freeze.relative_to(root)
if hashlib.sha256(io_path(candidate_freeze).read_bytes()).hexdigest() != args.candidate_freeze_sha256:
    raise RuntimeError('Candidate freeze pin changed')
for row in json.loads(io_path(candidate_freeze).read_text(encoding='utf-8-sig'))['files']:
    source = Path(row['path']).resolve()
    source.relative_to(root)
    value = io_path(source).read_bytes()
    if len(value) != row['bytes'] or hashlib.sha256(value).hexdigest() != row['sha256']:
        raise RuntimeError('Candidate source changed: ' + str(source))
    paths.append(source)
paths.append(candidate_freeze)
primary_runtime = root / 'source-assets/production/fairytale-sword-armor-primary1-runtime-v001'
paths.extend(p for p in plain_paths(io_path(primary_runtime).rglob('*')) if io_path(p).is_file())
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-armor-primary1-v001-import-*.json')))
paths.extend([Path(__file__), root / '钟盔军剑首斩穿甲试装.cmd'])
paths.extend(root / 'tools/scripts' / name for name in ('verify-sword-readability-v001.py','verify-sword-readability-v001.ps1','postprocess-sword-armor-primary1-v002.py'))
# Source169 six-body import and exact root opt-in fit tooling.
p2_runtime = root / 'source-assets/production/fairytale-sword-primary2-runtime-v001'
paths.extend(p for p in plain_paths(io_path(p2_runtime).rglob('*')) if io_path(p).is_file())
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-primary2-v001-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-sword-primary2-v001.py', 'ue_sword_primary2_v001_checks.py', 'import-sword-primary2-v001.ps1',
    'verify-sword-primary2-fit-v001.py', 'verify-sword-primary2-fit-v001.ps1',
    'verify-ready-primary2-body-pixel-presence-v001.py', 'postprocess-sword-primary2-fit-v001.py'))
paths.extend(p for p in plain_paths((io_path(root / 'source-assets/production/fairytale-sword-primary2-arc-v002')).rglob('*')) if io_path(p).is_file())
paths.extend(root / 'tools/scripts' / name for name in ('verify-sword-primary2-fit-v002.py','verify-sword-primary2-fit-v002.ps1','postprocess-sword-primary2-fit-v002.py'))
# Native171 new six-body namespace, source measurements, corrected axis history and actual import.
p2_new = root / 'source-assets/production/fairytale-sword-primary2-runtime-v002'
paths.extend(p for p in plain_paths(io_path(p2_new).rglob('*')) if io_path(p).is_file())
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-primary2-v002-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'ue-import-sword-primary2-v002.py','ue_sword_primary2_v002_checks.py','import-sword-primary2-v002.ps1',
    'verify-sword-primary2-fit-v003.py','verify-sword-primary2-fit-v003.ps1','postprocess-sword-primary2-fit-v003.py'))
paths.extend(root / 'tools/scripts' / name for name in (
    'verify-run-pristine-two-process-v002.py','verify-run-pristine-two-process-v002.ps1'))
p2_armor = root / 'source-assets/production/fairytale-armor-sword-primary2-runtime-v001'
paths.extend(p for p in plain_paths(io_path(p2_armor).rglob('*')) if io_path(p).is_file())
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-armor-primary2-v001-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'verify-sword-primary2-fit-v004.py','verify-sword-primary2-fit-v004.ps1','postprocess-sword-primary2-fit-v004.py',
    'ue_sword_armor_primary2_v001_checks.py','ue-import-sword-armor-primary2-v001.py','import-sword-armor-primary2-v001.ps1'))
# Native175 third-stage48 (6 whole bodies +42 exclusivebody/armor layers), exact marker DESIGN and actual import.
p3_runtime = root / 'source-assets/production/fairytale-sword-primary3-runtime-v001'
paths.extend(p for p in plain_paths(io_path(p3_runtime).rglob('*')) if io_path(p).is_file())
paths.extend(p for p in plain_paths((io_path(root / 'source-assets/production/fairytale-sword-primary3-v001')).rglob('*')) if io_path(p).is_file())
paths.extend(p for p in plain_paths((io_path(root / 'source-assets/production/fairytale-sword-primary3-body-partition-v001')).rglob('*')) if io_path(p).is_file())
paths.extend(plain_paths((io_path(root / 'UnrealGame/Saved/Bootstrap')).glob('sword-armor-primary3-v001-import-*.json')))
paths.extend(root / 'tools/scripts' / name for name in (
    'verify-sword-primary3-fit-v001.py','verify-sword-primary3-fit-v001.ps1',
    'postprocess-sword-primary3-fit-v001.py','freeze-sword-primary3-fit-build-v001.py',
    'verify-ready-primary3-body-pixel-presence-v001.py','retain-sword-primary3-fit-v001.py',
    'ue_sword_armor_primary3_v001_checks.py','ue-import-sword-armor-primary3-v001.py','import-sword-armor-primary3-v001.ps1'))
source_inline = root / 'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary3V001.inl'
expected_inline = '6749343b607b21ae5d7d1b8d1bf959b67324d13b85c7f6b37f70097088116054'
if hashlib.sha256(io_path(source_inline).read_bytes()).hexdigest() != expected_inline:
    raise RuntimeError('Root-admitted P3 inline differs from frozen candidate')
production = {p.relative_to(root).as_posix() for p in plain_paths((io_path(root / 'UnrealGame/Content/Production')).rglob('*')) if io_path(p).is_file()}
if len(production) != 1085:
    raise RuntimeError('Actual P3 capture expects exact1085 Production files')
paths.extend(root / relative for relative in ('tools/scripts/launch-fairytale-sword-armor-primary3-v001.ps1','钟盔军剑三段穿甲试装.cmd'))
rows = []
for source in sorted(set(paths)):
    relative = source.relative_to(root)
    data = io_path(source).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    target = destination / relative
    io_path(target.parent).mkdir(parents=True, exist_ok=True)
    shutil.copy2(io_path(source), io_path(target))
    if io_path(target).read_bytes() != data or io_path(source).read_bytes() != data:
        raise RuntimeError(f'Changed source or snapshot: {source}')
    rows.append({'path': relative.as_posix(), 'bytes': len(data), 'sha256': digest})
manifest = {
    'snapshot': destination.as_posix(), 'status': args.status,
    'automation_report': args.automation_report,
    'interrupted_run_log': args.interrupted_run_log,
    'complete_automation_report_available': automation is not None,
    'actual_automation_succeeded': automation['succeeded'] if automation is not None else None,
    'actual_automation_failed': automation['failed'] if automation is not None else None,
    'actual_automation_not_run': automation['notRun'] if automation is not None else None,
    'files': rows, 'copied_files': len(rows), 'bytes': sum(row['bytes'] for row in rows),
    'formal_complete_units': 0,
    'capture_observations': None, 'capture_duration_s': None,
    'capture_executed_by_this_tool': False, 'strict_automation_expected': 141,
}
io_path(destination / 'compiled-source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in manifest.items() if k != 'files'}, ensure_ascii=False))
