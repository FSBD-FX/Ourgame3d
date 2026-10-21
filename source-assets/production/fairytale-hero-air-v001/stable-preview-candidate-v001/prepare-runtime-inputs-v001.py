"""Read-only origin inventory; writes NEW candidate manifests/templates, never stages or runs UE."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('stable_copy_candidate', HERE / 'stage-stable-preview-v001.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
ROOT = Path('F:/Ourgame')
PROJECT = ROOT / 'UnrealGame'
CM = ROOT / 'source-assets/production/backups/v142-HeroAir6-Observer296-CallbackReady-203GREEN-v002/compiled-source-manifest.json'
SOURCE_FREEZE = HERE.parent / 'production-observer-callback-ready-v002/HeroAir-production-observer-callback-ready-source-freeze-v002.json'
PRODUCTION_FREEZE = HERE.parent / 'production-candidate-v001/full-production-v001/HeroAir-full-production-candidate-freeze-v001.json'
CHECKER_FREEZE = HERE.parent / 'production-observer-callback-ready-v002/tooling-queued-input-v003/Air-production-proof-checker-freeze-v003.json'


def main():
    cm = M.read(CM)
    M.need(M.pin(CM)['sha256'] == M.CM_SHA, 'Different compiled history')
    fixed = ['CodexDungeon.uproject', 'Binaries/Win64/UnrealEditor-CodexDungeon.dll',
             'Binaries/Win64/UnrealEditor.modules', 'Binaries/Win64/CodexDungeonEditor.target',
             'Plugins/UnrealMCP/UnrealMCP.uplugin', 'Plugins/UnrealMCP/Binaries/Win64/UnrealEditor-UnrealMCP.dll',
             'Plugins/UnrealMCP/Binaries/Win64/UnrealEditor.modules']
    names = fixed + sorted(M.enumerate_files(PROJECT, 'Config') | M.enumerate_files(PROJECT, 'Content'))
    rows = [M.pin(PROJECT / name, PROJECT) for name in sorted(names)]
    M.need(len(rows) == M.RUNTIME_COUNT and sum(r['bytes'] for r in rows) == M.RUNTIME_BYTES, 'Actual runtime totals differ')
    M.exact_runtime(PROJECT, rows, origin=True)
    cm_by_name = {r['path']: r for r in cm['files']}
    for r in rows:
        original = cm_by_name.get('UnrealGame/' + r['path'])
        if original:
            M.need((original['bytes'], original['sha256']) == (r['bytes'], r['sha256']), 'Runtime differs from fixed CM: ' + r['path'])
    for path in [PROJECT / 'Binaries/Win64/UnrealEditor.modules',
                 PROJECT / 'Plugins/UnrealMCP/Binaries/Win64/UnrealEditor.modules',
                 Path('G:/UE_5.5/Engine/Binaries/Win64/UnrealEditor.modules')]:
        M.need(M.read(path)['BuildId'] == '37670630', 'Installed/project/plugin BuildId differs')
    evidence = [(CM, 'compiled-source-manifest.json'), (Path(cm['full_suite']['path']), 'strict203-index.json'),
                (Path(cm['build']['path']), 'compiled-build-result.json'), (Path(cm['build_log']['path']), 'compiled-build.log'),
                (SOURCE_FREEZE, 'source-probe-freeze.json'), (PRODUCTION_FREEZE, 'production-source-freeze.json'),
                (CHECKER_FREEZE, 'original-native-checker-freeze.json')]
    for key in ('full_suite', 'build', 'build_log'):
        M.check_pin(cm[key])
    M.need(M.pin(SOURCE_FREEZE)['sha256'] == M.SOURCE_FREEZE_SHA
           and M.pin(CHECKER_FREEZE)['sha256'] == M.CHECKER_SHA
           and M.pin(PRODUCTION_FREEZE)['sha256'] == '7197705254448e380d643edbef4b31fe3adf4f95a7b3c9d389ad574adea532e6', 'Retained source lineage differs')
    inputs = dict(schema='HeroAir6-stable-runtime-inputs-v001', RootApproved=False, actual_staged=False,
                  origin_project_root=PROJECT.as_posix(), proposed_stage_root=M.STAGE.as_posix(),
                  source_CM_pin=M.pin(CM), runtime_count=len(rows), runtime_bytes=sum(r['bytes'] for r in rows),
                  runtime_files=rows, evidence_files=[dict(source_pin=M.pin(p), staged_path='_proof/evidence/' + name) for p, name in evidence],
                  launcher_files=[dict(source_pin=M.pin(HERE / 'launch-stable-preview-v001.ps1'), staged_path='_proof/tools/launch-stable-preview-v001.ps1'),
                                  dict(source_pin=M.pin(HERE / 'stable-preview-entry-template.cmd'), staged_path='启动钟盔轻甲试玩.cmd')],
                  engine_files=[M.pin(Path('G:/UE_5.5') / name) for name in ['Engine/Binaries/Win64/UnrealEditor.exe',
                               'Engine/Binaries/Win64/UnrealEditor.modules', 'Engine/Build/Build.version']],
                  excluded=['Source', 'Intermediate', 'Saved', 'PDB', 'EXP', 'LIB', 'project-plugin docs'],
                  dependence='Installed G:/UE_5.5 and its engine plugins/VC runtime remain external; not a packaged distributable',
                  FinalAccepted=False)
    M.write_new(HERE / 'runtime-input-manifest-v001.json', inputs)
    M.write_new(HERE / 'Root-stage-request-TEMPLATE-v001.json',
                dict(schema='HeroAir6-Root-stable-stage-request-v001', RootApproved=False, is_template=True,
                     approval_scope='PHYSICAL_RUNTIME_COPY_ONLY', input_manifest_pin=M.pin(HERE / 'runtime-input-manifest-v001.json'),
                     candidate_freeze_pin=None, original_native_pair_pin=None, stage_root=M.STAGE.as_posix(), FinalAccepted=False))
    M.write_new(HERE / 'Root-staged-native-proof-TEMPLATE-v001.json',
                dict(schema='HeroAir6-Root-staged-native-proof-v001', RootApproved=False, is_template=True,
                     actual_editor_game_native_execution=False, actual_staged_project_and_DLL_loaded=False,
                     actual_process_id=None, native_process_exit_code=None, Root_verified_before_and_after_runtime_equal=False,
                     normal_manual_flags_verified=False, engine_build_id='37670630', source_CM_sha256=M.CM_SHA,
                     runtime_manifest_pin=None, staged_project_path=(M.STAGE / 'CodexDungeon.uproject').as_posix(),
                     evidence_pins=[], full_realtime_playback_reviewed=False, audio_listened=False,
                     known_pose_join_refinement_open=True, FinalAccepted=False))
    M.write_new(HERE / 'Root-stable-manual-approval-TEMPLATE-v001.json',
                dict(schema='HeroAir6-Root-stable-manual-approval-v001', RootApproved=False, is_template=True,
                     approval_scope='LIMITED_WIP', stage_root=M.STAGE.as_posix(), manual_trial_allowed=False,
                     Root_staged_visible_keyframes_reviewed=False, runtime_manifest_pin=None, stage_copy_receipt_pin=None,
                     staged_native_proof_pin=None, Root_visible_review_receipt_pin=None,
                     full_realtime_playback_reviewed=False, audio_listened=False, known_pose_join_refinement_open=True,
                     FinalAccepted=False))
    print({'runtime_count': len(rows), 'runtime_bytes': sum(r['bytes'] for r in rows),
           'runtime_MiB': sum(r['bytes'] for r in rows) / 1048576, 'actual_staged': False, 'UE_started': False})


if __name__ == '__main__':
    main()
