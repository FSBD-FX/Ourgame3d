"""Root checkpoint after actual 176 GREEN and retained native media review."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

ROOT = Path('F:/Ourgame').resolve()
EVIDENCE = ROOT / 'docs/production/first-batch-v2/evidence/guard-room-v001/root-checkpoint-v128-v001'
assert not EVIDENCE.exists()
EVIDENCE.mkdir(parents=True)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def fact(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return {'path': path.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


progress_path = ROOT / 'docs/production/first-batch-v2/progress.json'
ledger_path = ROOT / 'source-assets/production/first-unit-animation-v003/generation-ledger.json'
readme_path = ROOT / 'README.md'
requirements_path = ROOT / '项目需求台账.md'
before = []
for path in [progress_path, ledger_path, readme_path, requirements_path]:
    before.append(fact(path))
    shutil.copy2(path, EVIDENCE / ('before-' + path.name))

report_rel = 'UnrealGame/Saved/Automation/FirstRoom-20261018-102713/index.json'
report = read(ROOT / report_rel)
assert report['succeeded'] == 176
assert all(report[key] == 0 for key in ['failed', 'succeededWithWarnings', 'notRun', 'inProcess'])
tests = report['tests']
assert len(tests) == len({test['fullTestPath'] for test in tests}) == 176
assert all(test['state'] == 'Success' and test['errors'] == 0 and test['warnings'] == 0 for test in tests)
snapshot_rel = 'source-assets/production/backups/v128-guard-room-176G'
snapshot = read(ROOT / snapshot_rel / 'compiled-source-manifest.json')
assert len(snapshot['files']) == 1788 and snapshot['source_files'] == 213 and snapshot['production_files'] == 1210
assert fact(ROOT / report_rel)['sha256'] == snapshot['full_suite']['sha256']
assert len(list((ROOT / 'UnrealGame/Source/CodexDungeon').rglob('*.cpp'))) > 0
archive = ROOT / '过程图稿与视频/2026-10-18_石廊三敌原生流程诊断_v001'
proof = read(archive / '原件/independent-room-native-proof-v001.json')
assert proof['passed'] and proof['native_frames'] == 592 and proof['final_wallet'] == 40
assert proof['normal_J_full_clear'] is False and proof['two_process_disk_proof'] is False
retention = read(Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-guard-room-native-v370/independent-final-second-SHA256-pass-v002.json'))
assert retention['verification_passes'] == 2 and retention['source_and_target_mismatches'] == 0
browser = read(ROOT / '过程图稿与视频/2026-10-18_石廊诊断录像播放复核_v001/原件/playback-facts.json')
assert len(browser['browserPlayback']) == 1
assert browser['browserPlayback'][0]['ended'] and browser['browserPlayback'][0]['error'] is None
ledger = read(ledger_path)
assert ledger['requested_count'] == 214 and ledger['remaining_batch_requests'] == 2
review_path = ROOT / 'docs/production/first-batch-v2/runtime-review-guard-room-v128.md'
generation_review = {
    'schema': 'guard-native-source-review-v128-v001', 'formal_complete_units': 0,
    'source_event': 'EV-048', 'external_api_calls': 0, 'host_fee_usd': None,
    'rows': [
        {'number': 206, 'decision': 'identity_candidate_source_reviewed_runtime_pending'},
        {'number': 207, 'decision': 'empty_fist_idle_source_candidate_not_final_armed_action'},
        {'number': 208, 'decision': 'independent_axe_source_candidate_not_per_frame_rig'},
        {'number': 209, 'decision': 'armed_ready_anchor_candidate_lock_runtime_registration_pending'},
        {'number': 210, 'decision': 'wake_candidate_Dormant_alias_frame0_registration_transition_pending'},
        {'number': 211, 'decision': 'REJECTED_WHOLE_ROW_NEAR_HAND_SWAPS_TO_HEAD_GRIP_FRAMES2_TO5'},
        {'number': 212, 'decision': 'six_curated_frames_Root_reviewed_grip_topology_source_candidate_runtime_pending'},
        {'number': 213, 'decision': 'raw_four_stunned_poses_reviewed_shared_extraction_pending'},
        {'number': 214, 'decision': 'raw_six_death_poses_reviewed_frame0_eyes_still_lit_original_spec_pending'},
    ],
    'review_method': 'E retained before Root view; source candidate review is not runtime acceptance',
}
generation_review_path = EVIDENCE / 'guard-source-review-v001.json'
write(generation_review_path, generation_review)
for row in generation_review['rows']:
    request = next(r for r in ledger['requests'] if r['request_number'] == row['number'])
    assert request['status'] == 'generated_retained_pending_review'
    request['root_source_review'] = dict(row, review=fact(generation_review_path), runtime_imported=False, full_enemy_accepted=False)
write(ledger_path, ledger)

progress = read(progress_path)
progress['date'] = '2026-10-18'
progress['updated_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
progress['goal_status'] = 'active'
progress['goal_tool_status_observed_at_user_continuation'] = 'active'
progress['completed_content_units'] = 0
progress['current_task'] = 'v128 actual176 strictGREEN; native three-enemy Bridge diagnostic flow/rewards/grouped restore verified and eight unscaled keyframes reviewed. Complete Guard new art/all-state runtime and hero true unsupported actions next; 0/15.'
progress['current_review'] = review_path.relative_to(ROOT).as_posix()
progress['current_build'] = 'UnrealGame/Saved/Bootstrap/build-editor-20261018-102501.log'
progress['current_build_exit_code'] = 0
progress['current_compiled_snapshot'] = snapshot_rel
progress['current_compiled_snapshot_files'] = len(snapshot['files'])
progress['current_compiled_snapshot_bytes'] = sum(row['bytes'] for row in snapshot['files'])
progress['current_source_uncompiled_changes'] = False
progress['ue_current_working_source_verified'] = True
progress['ue_current_working_source_compiled'] = True
progress['ue_actual_total_production_files'] = 1210
progress['current_production_packages'] = 1210
progress['production_uasset_package_count_actual'] = 1210
progress['production_package_count_actual'] = 1210
progress['production_package_counts_by_group'] = {'ArtTrials': 344, 'FirstBatch': 861, 'RoomArt': 3, 'SceneExploration': 2}
progress['actual_registered_test_count_current'] = 176
progress['latest_strict_UE_automation'] = {'report': report_rel, 'succeeded': 176, 'failed': 0, 'warnings': 0, 'errors': 0, 'notRun': 0, 'inProcess': 0, 'all_states_Success': True}
progress['completed_foundation_checks'].update({
    'ue_tests_last_passed': 176, 'ue_latest_total': 176, 'ue_latest_failed': 0,
    'ue_latest_report': report_rel, 'ue_last_full_successful_report': report_rel,
    'ue_last_full_successful_count': 176, 'ue_verified_source_snapshot': snapshot_rel,
    'ue_current_working_source_verified': True,
})
progress['current_source_verification_scope'] = 'Actual176 strictGREEN; v128 Source213/Production1210/1788 input pins twoSHA0. Native PID27640 592 viewport-matching PNGs; public diagnostic kills after real J/Shift, warnings36+36, native coin7/4/9 pickup20to40, sameprocess RootV2 grouped restore only. NewGuard art not imported; unsupported hero poses bareReady0; fullunits0/15.'
progress['guard_room_v001'].update({
    'actual_GREEN': fact(ROOT / report_rel), 'actual_native': fact(archive / '原件/independent-room-native-proof-v001.json'),
    'formal_room_id': 'NATIVE-FIRSTBATCH-GUARD-BRIDGE-V001', 'complete': False,
    'native_normal_J_full_clear': False, 'native_public_diagnostic_damage_used': True,
    'same_process_grouped_restore_only': True,
})
progress['guard_feedback_v001'].update({
    'actual_GREEN': fact(ROOT / report_rel), 'complete': False, 'imported_guard_SoundWave': 11,
    'browser11_playback_ended': True, 'model_audio_input_supported': False,
    'subjective_timbre_accepted': False, 'game_loopback_this_capture': False,
})
progress['room_coin_allocation_v001'].update({'formal_room_binding': 'NATIVE-FIRSTBATCH-GUARD-BRIDGE-V001', 'actual_payout': True, 'actual_native': fact(archive / '原件/independent-room-native-proof-v001.json')})
progress['stone_guard_native_v001'].update({'save_supported': True, 'reward_supported': True, 'native_runtime_proof': fact(archive / '原件/independent-room-native-proof-v001.json'), 'formal_unit_complete': False})
progress['stone_guard_owner_v002']['guard_disk_V2_supported'] = True
progress['fairytale_guard_source_v128'] = generation_review
progress['hero_full_state_gap_v128'] = {'bound_presenter': 'Unsupported Dodge/Hurt/Death and invalid other weapon/armor bindings are bare static Ready0; no complete actions or equipment retention', 'current_new_style_partial_pairings': ['WPN-SWD-001+ARM-LGT-001'], 'complete_pairings': 0, 'required_pairings': 20, 'source_candidate_audit': 'source-assets/production/fairytale-hero-state-gap-v001', 'actual_native_dodge_keyframe_reviewed': True}
progress['previous_visual_runtime_proof_before_guard_room_v128'] = progress.get('latest_visual_runtime_proof')
video = archive / '展示副本/guard-room-native-flow-DIAGNOSTIC-silent-v001.mp4'
progress['latest_visual_runtime_proof'] = {'review': fact(review_path), 'archive': archive.as_posix(), 'capture_snapshot': snapshot_rel, 'video': fact(video), 'native_PNGs': 592, 'Root_unscaled_keyframes_reviewed': 8, 'browser_ended_error_null': True, 'normal_J_full_clear': False, 'public_diagnostic_damage_used': True, 'audio_recorded': False, 'full_motion_accepted': False, 'formal_complete_units': 0}
progress['latest_native_review_browser_playback'] = {'tab_id': '3', 'duration': 19.72, 'ended': True, 'error': None, 'retention': 'E373'}
progress['interactive_guard_room_trial_v128'] = {'cmd': fact(ROOT / '石廊三敌原生试玩.cmd'), 'launcher': fact(ROOT / 'tools/scripts/launch-guard-room-native-trial-v001.ps1'), 'snapshot': snapshot_rel, 'validation_only_passed': True, 'automatic_inputs': False, 'diagnostic_damage': False, 'display_only_light_source': True}
progress['generation_accounting_current'] = {'requested_count': 214, 'current_window': 9, 'window_requested': 22, 'window_remaining': 2, 'lifetime_requested_count': 238, 'external_api_calls': 0, 'host_fee_usd': None, 'authorization_events': ['EV-040', 'EV-041']}
progress['generation'].update({'current_ledger': ledger_path.relative_to(ROOT).as_posix(), 'current_window': ledger['current_window'], 'current_window_remaining': 2, 'EV039_and_later_requested': 214, 'production_generation_requested_excluding_initial_references': 238, 'total_host_image_requests_including_initial3_references': 241, 'external_API_calls': 0, 'host_billing': 'unverified'})
next_work = ['Complete Guard fixed-axe full action rows, independent per-row body/floor registration, actual import/normal-room transitions and hit/poise/death/VFX/audio review.', 'Complete hero real Dodge/Hurt/Death/equip/air states while retaining actual equipped components; no bareReady0 mask.', 'Complete all5 weapons/4armors/5normal enemies/Boss,20pairings,15aux and actual acquisition/combat/drop/save/restore proof.']
progress['next_work'] = next_work
progress['next_turn_priorities'] = next_work
progress['next_presentation_priorities'] = next_work
progress['next_native_request'] = 215
progress['next_media_retention_batch'] = 375
progress['next_retention_batch'] = 375
write(progress_path, progress)

header = '''2026-10-18 当前检查点（EV048，v128）：石廊三敌的分批出场、实际金币拾取和同进程恢复已跑通；176项严格回归全部通过。保持小比例钟盔与传统HUD隐藏。[正常试玩](石廊三敌原生试玩.cmd) · [19.72秒原生诊断录像](过程图稿与视频/2026-10-18_石廊三敌原生流程诊断_v001/展示副本/guard-room-native-flow-DIAGNOSTIC-silent-v001.mp4)。

| 内容 | 实际验证 | 剩余 |
| --- | --- | --- |
| 三敌房间 | 有限完整槽位、两次1.2秒预警、7/4/9掉金币并实际拾取20→40、恢复后不重放 | 正常J实战全通关、完整敌人美术与可听混音 |
| 守卫反馈 | 苏醒/脚步/蓄斧/重击/命中/破韧/死亡事件消费，11 SoundWave已导入 | 新动作逐行配准和真实视听验收；211换手错稿已拒绝 |
| 人物全状态 | Ready/Walk/军剑三段为当前小比例试装 | 闪避/受伤/死亡仍静态Ready0且丢装备，其他19搭配与全状态待做 |

[事实、推理和风险](docs/production/first-batch-v2/runtime-review-guard-room-v128.md)。录像含公开诊断伤害、静音，仅同进程分组恢复；蝙蝠/重斧守卫及世界拾取标记仍占位。新守卫美术仅源候选，尚未导入。当前Production1210，编译快照1788文件；正式完整0/15、目标active，首批范围不变。生成214／窗口22of24余2／累计238（另初始3参考），外部API0、内置计费未知。旧v127及更早入口保留为历史，以本段和progress当前字段为准。

'''
readme_path.write_text(header + readme_path.read_text(encoding='utf-8-sig'), encoding='utf-8')
with requirements_path.open('a', encoding='utf-8') as stream:
    stream.write('\n\n## 2026-10-18 EV048继续制作 · v128\n\n沿用怪诞卡通、小比例及增强盔甲轮廓，不新增人类事件或代替用户美术接受。实际176项严格通过，三敌Bridge原生592帧/两次1.2秒预警/地面7、4、9金币正常拾取20→40/同进程RootV2恢复均有记录；录像含公开诊断伤害、静音，非正常J全通关。Root看八张原比例关键帧，浏览器19.72秒结束无错误；F/E370与373保全。11守卫SoundWave实际导入但未主观试听。新守卫209/210/212源候选、211错误换手整行拒绝，未替换实际占位；Bound人物闪避/受伤/死亡静态Ready0丢装备已查清，下一步补真实动作。正式0/15、目标active；见 [v128记录](docs/production/first-batch-v2/runtime-review-guard-room-v128.md)。\n')
write(EVIDENCE / 'checkpoint-manifest.json', {'schema': 'root-v128-checkpoint-v001', 'before': before, 'after': [fact(path) for path in [progress_path, ledger_path, readme_path, requirements_path]], 'review': fact(review_path), 'actual_build_exit': 0, 'actual_tests': 176, 'actual_native_diagnostic_passed': True, 'formal_complete_units': 0})
print(json.dumps({'checkpoint': fact(EVIDENCE / 'checkpoint-manifest.json'), 'tests': 176, 'production': 1210, 'generation': 214, 'formal_complete_units': 0}, ensure_ascii=False))
