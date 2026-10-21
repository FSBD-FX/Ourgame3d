"""Root-only physical runtime copy. No UE launch, deletion, links, or automatic approval."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

CM_SHA = '52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62'
CHECKER_SHA = 'a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46'
SOURCE_FREEZE_SHA = 'be6e3a1cb2e6344b51bef45a872b3bfb05056f73b37cbf923ebb33474422a36f'
STAGE = Path('F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906')
ORIGIN = Path('F:/Ourgame/UnrealGame')
RUNTIME_COUNT = 1778
RUNTIME_BYTES = 143122086
REPARSE = 0x400


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')


def physical(path, root=None, file=False):
    """Reject reparse traversal before resolving it; reject multiply-linked target files."""
    path = Path(os.path.abspath(path))
    if root is not None:
        base = Path(os.path.abspath(root))
        need(path.is_relative_to(base), 'Path leaves its explicit root: ' + str(path))
    for part in (path, *path.parents):
        try:
            st = part.lstat()
        except FileNotFoundError:
            continue
        need(not part.is_symlink() and not (getattr(st, 'st_file_attributes', 0) & REPARSE),
             'Reparse/symlink path rejected: ' + str(part))
    if file:
        need(path.is_file() and path.stat().st_nlink == 1, 'Not a single physical file: ' + str(path))
    return path


def rel(root, name):
    p = Path(name)
    need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
         'Expected a clean relative forward-slash member')
    return physical(Path(root) / p, root)


def digest(path, buffered=False):
    with Path(path).open('rb') as inp:
        return (hashlib.sha256(inp.read()).hexdigest() if buffered
                else hashlib.file_digest(inp, 'sha256').hexdigest())


def pin(path, relative_to=None):
    path = physical(path, file=True)
    return dict(path=path.relative_to(relative_to).as_posix() if relative_to else path.as_posix(),
                bytes=path.stat().st_size, sha256=digest(path))


def check_file(path, row, buffered=False):
    path = physical(path, file=True)
    need(path.stat().st_size == row['bytes'] and digest(path, buffered) == row['sha256'],
         'File bytes/SHA differ: ' + str(path))


def check_pin(row):
    check_file(row['path'], row)
    return Path(row['path'])


def enumerate_files(root, directory):
    base = rel(root, directory)
    need(base.is_dir(), 'Required runtime directory missing: ' + directory)
    out = set()
    for parent, dirs, files in os.walk(base, followlinks=False):
        for name in dirs + files:
            physical(Path(parent) / name, root)
        for name in files:
            p = physical(Path(parent) / name, root, file=True)
            out.add(p.relative_to(root).as_posix())
    return out


def exact_runtime(root, rows, origin=False):
    names = [r['path'] for r in rows]
    need(len(set(names)) == len(names), 'Duplicate runtime members')
    for directory in ('Config', 'Content', 'Binaries', 'Plugins'):
        want = {n for n in names if n.startswith(directory + '/')}
        if origin and directory in ('Binaries', 'Plugins'):
            # Origin development folders also contain Source/Intermediate and compiler symbols.
            actual = set()
            for p in (Path(root) / directory).rglob('*'):
                if not p.is_file():
                    continue
                name = p.relative_to(root).as_posix()
                if any(part in ('Source', 'Intermediate', 'Saved') for part in p.relative_to(root).parts):
                    continue
                if p.suffix.lower() in ('.pdb', '.exp', '.lib', '.md'):
                    continue
                physical(p, root, file=True)
                actual.add(name)
        else:
            actual = enumerate_files(root, directory)
        need(actual == want, 'Runtime membership differs: ' + directory)
    need({p.name for p in Path(root).glob('*.uproject')} == {'CodexDungeon.uproject'},
         'Project descriptor membership differs')


def verify_rows(root, rows, buffered=False):
    for row in rows:
        check_file(rel(root, row['path']), row, buffered)


def copy_one(source, target, row):
    source = physical(source, file=True)
    physical(target)
    need(not Path(target).exists(), 'No overwrite: ' + str(target))
    check_file(source, row)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    physical(Path(target).parent)
    with source.open('rb') as inp, Path(target).open('xb') as out:
        shutil.copyfileobj(inp, out, length=1024 * 1024)
        out.flush()
        os.fsync(out.fileno())
    physical(target, file=True)


def copy_snapshot(origin, target, rows):
    """Small host tests exercise this same physical-copy kernel, never fake native approval."""
    origin = physical(origin)
    target = physical(target)
    need(not target.exists(), 'Destination already exists; leave it intact')
    target.mkdir(parents=True, exist_ok=False)
    for row in rows:
        copy_one(rel(origin, row['path']), rel(target, row['path']), row)
    for buffered in (False, True):
        verify_rows(origin, rows, buffered)
        verify_rows(target, rows, buffered)


def validate_pair(pair):
    need(pair['schema'] == 'hero-Air6-production-independent-pair-v001' and pair['passed'] is True
         and pair['actual_two_fresh_PIDs'] is True
         and pair['both6pose_None6_LGT9_rejump_Ready_verified'] is True, 'Actual retained original native pair required')
    for branch in (pair['left'], pair['right']):
        need(branch['schema'] == 'hero-Air6-production-independent-native-v001' and branch['passed'] is True
             and branch['compiled_manifest_pin']['sha256'] == CM_SHA
             and branch['checker_freeze_pin']['sha256'] == CHECKER_SHA
             and branch['source_probe_freeze_pin']['sha256'] == SOURCE_FREEZE_SHA,
             'Original native branch compilation/source/checker differs')


def stage(input_path, request_path):
    inputs = read(input_path)
    request = read(request_path)
    need(request.get('schema') == 'HeroAir6-Root-stable-stage-request-v001'
         and request.get('RootApproved') is True and request.get('is_template') is False
         and request.get('approval_scope') == 'PHYSICAL_RUNTIME_COPY_ONLY'
         and request.get('FinalAccepted') is False, 'Root actual stage request required; no files copied')
    need(inputs['schema'] == 'HeroAir6-stable-runtime-inputs-v001'
         and inputs['source_CM_pin']['sha256'] == CM_SHA
         and inputs['runtime_count'] == RUNTIME_COUNT and inputs['runtime_bytes'] == RUNTIME_BYTES
         and Path(inputs['origin_project_root']) == ORIGIN and Path(inputs['proposed_stage_root']) == STAGE,
         'Different frozen runtime input manifest')
    need(request['input_manifest_pin'] == pin(input_path), 'Root stage request does not bind frozen inputs')
    candidate_freeze = read(check_pin(request['candidate_freeze_pin']))
    for member in candidate_freeze['members']:
        check_pin(member)
    need(any(member == pin(__file__) for member in candidate_freeze['members']), 'Copier absent from candidate freeze')
    need(any(member == pin(input_path) for member in candidate_freeze['members']), 'Inputs absent from candidate freeze')
    need(Path(request['stage_root']) == STAGE and not STAGE.exists(), 'Exact NEW stage root required')
    physical(STAGE)
    count = subprocess.run(['pwsh', '-NoProfile', '-Command',
                            "@(Get-Process -Name 'UnrealEditor*','UnrealBuildTool' -ErrorAction SilentlyContinue).Count"],
                           check=True, capture_output=True, text=True)
    need(count.stdout.strip() == '0', 'Close actual UE/UBT before physical staging')
    cm = read(check_pin(inputs['source_CM_pin']))
    need((cm['source_files'], cm['production_files'], cm['registered_tests'], cm['passed'], cm['failed'], cm['notRun'])
         == (296, 1419, 203, 203, 0, 0), 'Retained CM296/1419/full203 differs')
    workspace = ORIGIN.parent
    for member in cm['files']:
        check_file(rel(workspace, member['path']), member)
    exact_runtime(ORIGIN, inputs['runtime_files'], origin=True)
    need(len(inputs['runtime_files']) == RUNTIME_COUNT
         and sum(r['bytes'] for r in inputs['runtime_files']) == RUNTIME_BYTES, 'Runtime list totals differ')
    pair_path = check_pin(request['original_native_pair_pin'])
    validate_pair(read(pair_path))
    for row in inputs['engine_files']:
        check_pin(row)
    copy_snapshot(ORIGIN, STAGE, inputs['runtime_files'])
    # All remaining files are explicit local metadata or launcher bytes, never origin Source files.
    staged_meta = []
    extras = inputs['evidence_files'] + inputs['launcher_files'] + [
        dict(source_pin=pin(input_path), staged_path='_proof/evidence/runtime-input-manifest.json'),
        dict(source_pin=pin(request_path), staged_path='_proof/evidence/Root-stage-request.json'),
        dict(source_pin=request['candidate_freeze_pin'], staged_path='_proof/evidence/candidate-freeze.json'),
        dict(source_pin=request['original_native_pair_pin'], staged_path='_proof/evidence/original-native-pair.json')]
    for row in extras:
        source = check_pin(row['source_pin'])
        target = rel(STAGE, row['staged_path'])
        copy_one(source, target, row['source_pin'])
        staged_meta.append(pin(target, STAGE))
    for buffered in (False, True):
        verify_rows(STAGE, inputs['runtime_files'] + staged_meta, buffered)
    exact_runtime(STAGE, inputs['runtime_files'])
    exact_runtime(ORIGIN, inputs['runtime_files'], origin=True)
    for row in extras:
        check_file(row['source_pin']['path'], row['source_pin'], True)
    # Origin Source is checked only during the Root staging operation, never by the later launcher.
    for member in cm['files']:
        check_file(rel(workspace, member['path']), member, True)
    snapshot = dict(schema='HeroAir6-physical-runtime-snapshot-v001', actual_stage_copy_succeeded=True,
                    stage_root=STAGE.as_posix(), source_CM_sha256=CM_SHA, engine_build_id='37670630',
                    runtime_files=inputs['runtime_files'], runtime_count=RUNTIME_COUNT, runtime_bytes=RUNTIME_BYTES,
                    metadata_files=staged_meta, engine_files=inputs['engine_files'],
                    source_runtime_two_pass_verified=True, target_runtime_two_pass_verified=True,
                    source_and_target_links_created=False, live_development_Source_needed_at_launch=False,
                    source_copied=False, Root_manual_trial_approved=False, FinalAccepted=False)
    snapshot_path = STAGE / '_proof/runtime-snapshot-manifest-v001.json'
    write_new(snapshot_path, snapshot)
    receipt = dict(schema='HeroAir6-actual-stage-copy-receipt-v001', success=True, utc=datetime.now(timezone.utc).isoformat(),
                   stage_root=STAGE.as_posix(), runtime_manifest_pin=pin(snapshot_path, STAGE),
                   runtime_count=RUNTIME_COUNT, runtime_bytes=RUNTIME_BYTES, verification_passes=2,
                   source_and_target_twoSHA_mismatches=0, physical_copy_no_links=True,
                   exact_runtime_membership_verified=True, UE_started=False, Root_manual_trial_approved=False,
                   FinalAccepted=False)
    write_new(STAGE / '_proof/stage-copy-receipt-v001.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-manifest', required=True)
    parser.add_argument('--Root-stage-request', required=True)
    parser.add_argument('--report', required=True, help='NEW Root report path; failure retained, never overwritten')
    args = parser.parse_args()
    report = Path(args.report)
    need(not report.exists(), 'Report exists; preserve it')
    preexisting_stage = STAGE.exists()
    try:
        result = stage(args.input_manifest, args.Root_stage_request)
        exit_code = 0
    except Exception as exc:
        result = dict(schema='HeroAir6-stage-copy-failure-v001', success=False,
                      utc=datetime.now(timezone.utc).isoformat(), error=str(exc),
                      partial_stage_retained=STAGE.exists() and not preexisting_stage,
                      preexisting_stage_preserved=preexisting_stage, stage_root=STAGE.as_posix(),
                      no_cleanup_performed=True, UE_started=False, Root_manual_trial_approved=False, FinalAccepted=False)
        exit_code = 3
    write_new(report, result)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
