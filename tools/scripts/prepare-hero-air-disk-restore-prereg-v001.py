"""Prepare one exclusive Root prereg after actual build and fresh checker review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import uuid

R = Path('F:/Ourgame')

def need(value, message):
    if not value:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pin(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=path.as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

def check(row):
    path = Path(row['path'])
    if not path.is_absolute():
        path = R / path
    actual = pin(path)
    need((actual['bytes'], actual['sha256']) == (row['bytes'], row['sha256']), 'Pinned bytes differ: ' + str(path))
    return path

parser = argparse.ArgumentParser()
parser.add_argument('--compiled-manifest', required=True)
parser.add_argument('--checker-freeze', required=True)
parser.add_argument('--checker-directory', required=True)
parser.add_argument('--checker-review', required=True)
parser.add_argument('--checker-review-sha', required=True)
parser.add_argument('--version', required=True)
parser.add_argument('--diagnostic-clear-knight', action='store_true')
args = parser.parse_args()
need(re.fullmatch(r'v[0-9]{3}', args.version), 'New version required')
checker = Path(args.checker_directory).resolve()
freeze_path = Path(args.checker_freeze).resolve()
review_path = Path(args.checker_review).resolve()
need(pin(review_path)['sha256'] == args.checker_review_sha, 'Fresh independently approved review pin required')
need('Approved' in review_path.read_text(encoding='utf-8'), 'Fresh checker review has no approval')
freeze = read(freeze_path)
need(any(Path(row['path']).resolve() == checker / 'verify-air-disk-restore-native-v001.py' for row in freeze['members']), 'Selected frozen checker differs')
for _ in range(2):
    for row in freeze['members']:
        check(row)
compiled_path = Path(args.compiled_manifest).resolve()
compiled = read(compiled_path)
need((compiled['registered_tests'], compiled['passed'], compiled['failed'], compiled['notRun']) == (203, 203, 0, 0), 'New strict203 CM required')
need(compiled['verification_passes'] == 2 and compiled['twoSHA_mismatches'] == 0, 'Actual compiled byte verification required')
for _ in range(2):
    for row in compiled['files']:
        check(row)
admission_path = check(compiled['source_admission_pin'])
admission = read(admission_path)
need(admission['RootApproved'] is True and admission['actual_applied'] is True, 'Actual source admission required')
template_path = checker / 'Root-prereg-TEMPLATE-v001.json'
prereg = read(template_path)
need(prereg['RootApproved'] is False and prereg['is_template'] is True, 'Original false template required')
for key in ('source_candidate_freeze_pin', 'protocol_pin', 'target_audio_policy_addendum_pin', 'target_audio_audit_evidence_pin'):
    check(prereg[key])
need(prereg['source_candidate_freeze_pin'] == admission['source_candidate_freeze'], 'Source freeze chain differs')
session = R / ('过程图稿与视频/2026-10-19_钟盔空中存档两进程_' + args.version)
source = R / ('过程图稿与视频/2026-10-19_钟盔空中存档_source_right_' + args.version)
target = R / ('过程图稿与视频/2026-10-19_钟盔空中存档_target_right_' + args.version)
for folder in (session, source, target):
    need(not folder.exists(), 'Preserve existing attempt: ' + str(folder))
profile_id = str(uuid.uuid4())
profiles = session / '原件/BoundRunOnly-v2'
need(not (profiles / profile_id).exists(), 'Profile must be fresh')
engine = Path('G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe')
dll = R / 'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'
game_modules = dll.parent / 'UnrealEditor.modules'
engine_modules = engine.parent / 'UnrealEditor.modules'
need(read(game_modules)['BuildId'] == read(engine_modules)['BuildId'], 'Actual engine/game BuildId mismatch')
visual = list(prereg['visual_flags'])
for flag in ('DungeonFairytaleSwordBodyPreview', 'DungeonFairytaleSwordBodyV002Preview',
             'DungeonFairytaleSwordArmorPrimary1Preview', 'DungeonFairytaleSwordPrimary2Preview',
             'DungeonFairytaleSwordPrimary2BodyPreview', 'DungeonFairytaleSwordPrimary2ArmorPreview',
             'DungeonFairytaleSwordPrimary3ArmorPreview'):
    if flag not in visual:
        visual.append(flag)
prereg.update(RootApproved=True, is_template=False, pre_registered_before_capture=True,
              created_utc=datetime.now(timezone.utc).isoformat(), FinalAccepted=False,
              session_directory=session.as_posix(), source_archive=source.as_posix(), target_archive=target.as_posix(),
              profiles_directory=profiles.as_posix(), profile_id=profile_id,
              predecessor_compiled_manifest_pin=admission['predecessor_compiled_manifest'],
              compiled_manifest_pin=pin(compiled_path), source_admission_pin=pin(admission_path),
              source_repair_admission_pins=compiled['source_repair_admission_pins'], checker_freeze_pin=pin(freeze_path),
              game_dll_pin=pin(dll), engine_executable_pin=pin(engine), uproject_pin=pin(R / 'UnrealGame/CodexDungeon.uproject'),
              game_module_descriptor_pin=pin(game_modules), engine_module_descriptor_pin=pin(engine_modules),
              visual_flags=visual, diagnostic_clear_knight=args.diagnostic_clear_knight,
              independent_checker_review_pin=pin(review_path), preparer_pin=pin(Path(__file__)),
              actual_source_files=compiled['source_files'], actual_production_files=compiled['production_files'])
for folder, role in ((session, 'session'), (source, 'source'), (target, 'target')):
    folder.mkdir()
    (folder / '原件').mkdir()
    (folder / '展示副本').mkdir()
    with (folder / 'README.md').open('x', encoding='utf-8') as stream:
        stream.write('钟盔空中磁盘存档与新进程继续的原生受控实录。角色：' + role + '。\n'
                     '保存全部成功／失败原件；展示前须完成F/E保全及核验。仅Bound Run，非完整账号存档；美术、原速播放及混音试听未验收。\n')
profiles.mkdir()
out = session / 'preregistration-v001.json'
with out.open('x', encoding='utf-8') as stream:
    json.dump(prereg, stream, ensure_ascii=False, indent=2)
print(json.dumps(dict(preregistration=pin(out), source_archive=source.as_posix(), target_archive=target.as_posix(), profile_id=profile_id), ensure_ascii=False))
