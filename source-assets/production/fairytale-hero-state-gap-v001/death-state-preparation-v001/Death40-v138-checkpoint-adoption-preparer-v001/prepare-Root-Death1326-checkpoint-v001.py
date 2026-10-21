"""Root-run v138 scoped manual checkpoint preparation. Never adopts files or starts UE.

The worker prepares this program but does not execute it. Root must explicitly
approve the limited manual scope on invocation. Existing checkpoints and tools
are read only; all output goes to one new Root checkpoint directory.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import runpy
from datetime import datetime, timezone

R = Path('F:/Ourgame').resolve()
D = R / 'source-assets/production/fairytale-hero-state-gap-v001/death-state-preparation-v001'
C = D / 'Death40-manual-checkpoint-tooling-candidate-v001'
HERE = Path(__file__).resolve().parent
OWN_FREEZE = HERE / 'adoption-preparer-freeze-v001.json'
SNAPSHOT = R / 'source-assets/production/backups/v138-HeroDeath190G'
DEFAULT_OUTPUT = D / 'root-Death1326-checkpoint-v001'
INPUTS = {
    'snapshot': {'path': (SNAPSHOT / 'compiled-source-manifest.json').as_posix(), 'bytes': 496461, 'sha256': 'ede55a41524cf0e0180492be5eaebf4e05444b511b6c7a12845be568a37ad62b'},
    'Root_source_admission': {'path': (R / 'docs/production/first-batch-v2/evidence/hero-Death40-v001/root-observer-admission-v002/source-admission-v001.json').as_posix(), 'bytes': 4711, 'sha256': '043bfc8974c481e46bdb5a2194b630a23c4f3db67b7e5cf0af5f0009e482513a'},
    'production': {'path': (D / 'Death40-runtime-production-v001/Death40-production-freeze-v001.json').as_posix(), 'bytes': 11154, 'sha256': '132a326e6b29cf39622de30de040cc3a1a6fadb84a2bb4be12accab0e2121a90'},
    'observer': {'path': (D / 'Death40-native-observer-candidate-v001/Death-native-observer-freeze-v001.json').as_posix(), 'bytes': 3455, 'sha256': '8c9715b9792d5751a8c21dc9f94f1a32cfa2bd1ed356a6a5e47449de3c355ac8'},
    'observer_source': {'path': (D / 'Death40-native-observer-candidate-v001/Death-observer-source-freeze-v001.json').as_posix(), 'bytes': 2238, 'sha256': '2d444f97205bb29f848723905fcbbf75b2c31ae0b7dc955c4069ad18bf9c558a'},
    'manual_tooling': {'path': (C / 'Death1326-manual-tooling-freeze-v001.json').as_posix(), 'bytes': 3466, 'sha256': '85e7ffeec9eb1a71266b590da4b2a83bfe49f869c40e2d29bf90ef108d15a15b'},
    'old_known44': {'path': (R / 'source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v002/guard-known44-source-profile-prereg-Hurt1286-v001.json').as_posix(), 'bytes': 105512, 'sha256': '819e20ad249b471b8ab64604aa2c0a35fe0f9dcbb9b41680c5bd2df407ab1db5'},
}
ENTRIES = ('钟盔轻甲受击试玩.cmd', '裂岩守卫挥斧试样.cmd', '裂岩守卫三动作试样.cmd', '石廊三敌原生试玩.cmd')
ENTRY_SHA = '3965562b954038d16105bd0410882dd310f21700244fa7da7451f189b8c550c2'
EXISTING = {'DungeonFighter.h', 'DungeonFighter.cpp', 'DungeonHUD.h', 'DungeonHUD.cpp', 'DungeonFairytaleSwordPresentation.cpp'}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def resolve(value):
    p = Path(value)
    p = (p if p.is_absolute() else R / p).resolve()
    need(p.is_relative_to(R), 'Path escapes project: ' + str(p))
    return p


def read(path):
    return json.loads(resolve(path).read_text(encoding='utf-8-sig'))


def pin(path):
    p = resolve(path)
    b = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def check(row):
    need(type(row) is dict and set(row) == {'path', 'bytes', 'sha256'}, 'Exact pin required')
    actual = pin(row['path'])
    need(type(row['bytes']) is int and actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256'], 'Pinned input changed: ' + row['path'])
    return resolve(row['path'])


def relative(path):
    return resolve(path).relative_to(R).as_posix()


def freeze_members(freeze):
    rows = read(freeze)['files']
    need(type(rows) is list and rows, 'Empty freeze')
    for row in rows:
        p = Path(row['path'])
        p = p if p.is_absolute() else resolve(freeze).parent / p
        if not p.is_file() and not Path(row['path']).is_absolute():
            p = R / row['path']
        check(dict(row, path=p.as_posix()))
    return rows


def write_json(path, value):
    # Every output must be new and inside the selected Root checkpoint.
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def prepare(output, snapshot, root_approved):
    need(root_approved is True, 'Root must explicitly approve this limited manual-input checkpoint')
    need(resolve(snapshot) == SNAPSHOT, 'This preparer is bound to the unique actual v138 snapshot')
    output = resolve(output)
    need(output.parent == D and output.name.startswith('root-Death1326-checkpoint-v'), 'Use a new root-Death1326-checkpoint-vNNN directory under Death preparation')
    need(not output.exists(), 'No overwrite: select a new checkpoint directory')
    freeze_members(OWN_FREEZE)
    for row in INPUTS.values():
        check(row)
    prod_rows = freeze_members(check(INPUTS['production']))
    obs_rows = freeze_members(check(INPUTS['observer']))
    freeze_members(check(INPUTS['observer_source']))
    freeze_members(check(INPUTS['manual_tooling']))
    module = runpy.run_path(str(C / 'verify-Death1326-manual-input-v001.py'))
    cm = read(INPUTS['snapshot']['path'])
    files = {row['path'].replace('\\', '/'): row for row in cm['files']}
    need(len(files) == len(cm['files']), 'Duplicate compiled file')
    source_paths = {n for n in files if n.startswith('UnrealGame/Source/')}
    production_paths = {n for n in files if n.startswith('UnrealGame/Content/Production/')}
    need(cm['source_files'] == len(source_paths) and cm['production_files'] == len(production_paths) == 1326 and cm['strict_registered_tests'] == 190, 'Actual dynamic Source/full190/1326 differ')
    need(cm['source_verification_passes'] == 2 and cm['source_hash_mismatches'] == 0, 'Snapshot not actual twoSHA0')
    module['strict_suite'](read(check(cm['full_suite'])))
    build = read(check(cm['current_build']))
    need(build['ExitCode'] == 0 and build['Target'] == 'CodexDungeonEditor', 'Actual build is not successful Editor build')
    for repeat in range(2):
        for folder, expected in [('UnrealGame/Source', source_paths), ('UnrealGame/Content/Production', production_paths)]:
            actual = {p.relative_to(R).as_posix() for p in (R / folder).rglob('*') if p.is_file()}
            need(actual == expected, 'Current exact set differs: ' + folder)
        for row in files.values():
            check(row)
        for row in INPUTS.values():
            check(row)
    admission = read(INPUTS['Root_source_admission']['path'])
    need(admission['production_freeze'] == INPUTS['production'] and admission['observer_source_freeze'] == INPUTS['observer_source'], 'Root admission binds different candidate')
    need(admission['source_files'] == cm['source_files'] and admission['production_files'] == 1326, 'Root current admission counts differ')
    declared_new = admission['new_source_files']
    declared_existing = admission['existing_modified_files']
    admitted = declared_new + declared_existing
    required = set(module['DEATH_FILES'])
    need(len(declared_new) == 11 and len(declared_existing) == 5 and {relative(x['path']) for x in admitted} == required, 'Exact current11new+5existing Death admission required')
    need({Path(x['path']).name for x in declared_existing} == EXISTING, 'Existing five narrow patch identities differ')
    for row in admitted:
        n = relative(check(row))
        need(n in files and (row['bytes'], row['sha256']) == (files[n]['bytes'], files[n]['sha256']), 'Current Root source admission differs from compiled bytes: ' + n)
    mappings = []
    for role, rows, expected_count in [('Death_runtime_candidate_freeze_pin', prod_rows, 9), ('Death_observer_candidate_freeze_pin', obs_rows, 2)]:
        selected = [x for x in rows if x['path'].replace('\\', '/').startswith('new-source/')]
        need(len(selected) == expected_count, 'Exact new-source candidate member count differs')
        for row in selected:
            suffix = row['path'].replace('\\', '/').removeprefix('new-source/')
            target = 'UnrealGame/Source/CodexDungeon/' + suffix
            need(target in required and Path(target).name not in EXISTING, 'Attempt to map pre-observer existing HUD/patch bytes')
            need((row['bytes'], row['sha256']) == (files[target]['bytes'], files[target]['sha256']), 'New candidate bytes are not compiled: ' + target)
            mappings.append({'candidate_freeze_role': role, 'candidate_member_path': row['path'], 'actual_source_path': target})
    need(len(mappings) == len({x['actual_source_path'] for x in mappings}) == 11 and {x['actual_source_path'] for x in mappings} == {relative(x['path']) for x in declared_new}, 'Exact11 new admission mapping differs')
    obs = read(INPUTS['observer']['path'])['source_probe_freeze']
    need(obs['bytes'] == INPUTS['observer_source']['bytes'] and obs['sha256'] == INPUTS['observer_source']['sha256'], 'Observer source2d44 freeze not bound')
    # Existing four entrypoints are inspected; only proposed copies will be written.
    entry_text = {}
    for name in ENTRIES:
        check({'path': (R / name).as_posix(), 'bytes': 181, 'sha256': ENTRY_SHA})
        text = (R / name).read_text(encoding='utf-8-sig')
        need(text.count('launch-guard-room-native-trial-v008.ps1') == 1, 'Manual entrypoint is not the expected v008')
        entry_text[name] = text.replace('launch-guard-room-native-trial-v008.ps1', 'launch-guard-room-native-trial-v009.ps1')
    now = datetime.now(timezone.utc).isoformat()
    extension = read(C / 'Root-Death1326-production-extension-TEMPLATE-NOT-APPROVED-v001.json')
    for key, row in extension.items():
        if key.endswith('_pin') and row:
            check(row)
    extension.update(is_template=False, RootApproved=True, compiled_manifest_sha256=INPUTS['snapshot']['sha256'], registered_at_utc=now,
                     Root_scope='Exact1254+Hurt32+Death40 extension for current v138 manual trial; no GPU/native/media/final acceptance inferred.')
    old = read(INPUTS['old_known44']['path'])
    need(old['known_unique_sources'] == 44 and len(old['all_profile_rows']) == 13 and len(old['profile_facts']) in (10, 13), 'Complete old44 profile tables required')
    known44 = copy.deepcopy(old)
    old_admitted = [x['path'].replace('\\', '/') for x in old['admitted_source_files']]
    need(len(old_admitted) == len(set(old_admitted)) and all(x in files for x in old_admitted), 'Old Guard admission path set differs')
    known44.update(compiled_manifest_sha256=INPUTS['snapshot']['sha256'], strict_registered_tests=190,
                   source_files=cm['source_files'], production_files=1326,
                   admitted_source_files=[copy.deepcopy(files[x]) for x in old_admitted])
    changed = {'compiled_manifest_sha256', 'strict_registered_tests', 'source_files', 'production_files', 'admitted_source_files', 'production_extension_pin'}
    need(all(known44[k] == old[k] for k in old if k not in changed), 'A copied44 table/fact/gap was changed')
    # Directory creation and approvals occur only in Root's explicit invocation.
    output.mkdir()
    extension_path = output / 'production-extension-Root-approval-Death1326-v001.json'
    write_json(extension_path, extension)
    known44['production_extension_pin'] = pin(extension_path)
    known44['manual_checkpoint_rebinding'] = {
        'utc': now, 'old_prereg_pin': INPUTS['old_known44'], 'Root_source_admission_pin': INPUTS['Root_source_admission'],
        'scope': 'Current source/profile manual rebinding only. The copied legacy capture flag/status/date are provenance, not a new Guard capture prereg or new rendered44 coverage.',
        'all_original_noncurrent_fields_preserved': True, 'new_native_capture_claimed': False,
    }
    prereg_path = output / 'guard-known44-source-profile-prereg-Death1326-v001.json'
    write_json(prereg_path, known44)
    manual = read(C / 'Root-Death1326-manual-input-TEMPLATE-NOT-APPROVED-v001.json')
    manual.update(is_template=False, RootApproved=True, snapshot_directory=SNAPSHOT.as_posix(), snapshot_manifest_pin=INPUTS['snapshot'],
                  checkpoint_tooling_freeze_pin=INPUTS['manual_tooling'], full_suite_pin=cm['full_suite'], last_build_pin=cm['current_build'],
                  DLL_pin=files['UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll'], source_profile_prereg_pin=pin(prereg_path),
                  production_extension_approval_pin=pin(extension_path), Death_runtime_candidate_freeze_pin=INPUTS['production'],
                  Death_observer_candidate_freeze_pin=INPUTS['observer'], admitted_Death_source_files=[copy.deepcopy(files[x]) for x in module['DEATH_FILES']],
                  candidate_source_admissions=mappings, source_files=cm['source_files'], registered_at_utc=now,
                  Root_source_admission_pin=INPUTS['Root_source_admission'], Death_observer_source_freeze_pin=INPUTS['observer_source'],
                  adoption_preparer_freeze_pin=pin(OWN_FREEZE), Root_scope='Normal manual3-enemy source trial only; zero injected inputs or damage, debug-off, hidden traditional HUD; no final acceptance.')
    manual_path = output / 'manual-input-v001.json'
    write_json(manual_path, manual)
    result = module['verify'](manual_path, SNAPSHOT)
    need(result['current_live_verification_passes'] == 2 and result['UE_started'] is False, 'Frozen full current twoSHA validator did not complete')
    # Root may later adopt these exact staged copies. This program never does so.
    staged = output / 'staged-adoption'
    staged.mkdir()
    wrapper = staged / 'launch-guard-room-native-trial-v009.ps1'
    checkpoint = manual_path.as_posix().replace("'", "''")
    launcher = (C / 'launch-guard-room-native-trial-v009.ps1').as_posix()
    wrapper.write_text("param([string]$EngineRoot='G:\\UE_5.5',[string]$Snapshot='',[string]$RootCheckpoint='" + checkpoint + "',[switch]$LightArtTrial,[switch]$GuardFullArt,[switch]$ValidateOnly)\n$ErrorActionPreference='Stop'\n$PSBoundParameters['RootCheckpoint']=$RootCheckpoint\n$launcher='" + launcher + "'\n& $launcher @PSBoundParameters\nif($LASTEXITCODE -ne 0){exit $LASTEXITCODE}\n", encoding='utf-8', newline='\n')
    for name, text in entry_text.items():
        (staged / name).write_text(text, encoding='utf-8', newline='\n')
    receipt = {
        'schema': 'Root-Death1326-manual-checkpoint-preparation-receipt-v001', 'Root_explicit_scoped_approval': True, 'utc': now,
        'snapshot_manifest_pin': INPUTS['snapshot'], 'Root_source_admission_pin': INPUTS['Root_source_admission'],
        'adoption_preparer_freeze_pin': pin(OWN_FREEZE), 'source_files': cm['source_files'], 'production_files': 1326, 'strict_registered_tests': 190,
        'new_source_candidate_mappings': len(mappings), 'existing_source_current_pins': len(declared_existing), 'old_Guard_admission_paths_preserved': len(old_admitted),
        'profile_facts_unchanged': known44['profile_facts'] == old['profile_facts'], 'all13_rows_unchanged': known44['all_profile_rows'] == old['all_profile_rows'],
        'manual_input_pin': pin(manual_path), 'source_profile_pin': pin(prereg_path), 'production_extension_pin': pin(extension_path),
        'frozen_full_manual_validator': result, 'staged_adoption_files': [pin(p) for p in sorted(staged.iterdir())],
        'actual_tools_or_cmd_adopted': False, 'UE_started': False, 'actual_preload_finish_receipt': None, 'actual_runtime_receipt': None,
        'Source_ActualRuntimeGUIArt_acceptance_by': 'Root independently; no native/media acceptance synthesized here',
        'FinalAccepted': False, 'formal_complete_units': 0, 'formal_total_units': 15,
    }
    write_json(output / 'preparation-receipt-v001.json', receipt)
    print(json.dumps({'manual_input': manual_path.as_posix(), 'verified': result, 'staged_adoption_only': staged.as_posix(), 'actual_adoption': False}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--snapshot', default=SNAPSHOT.as_posix())
    ap.add_argument('--output', default=DEFAULT_OUTPUT.as_posix())
    ap.add_argument('--approve-root-scoped-manual-input', action='store_true', help='Root explicit approval of current source-only manual scope; never final art acceptance')
    args = ap.parse_args()
    prepare(args.output, args.snapshot, args.approve_root_scoped_manual_input)


if __name__ == '__main__':
    main()
