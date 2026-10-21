"""Refresh only durable status; preserve all prior checkpoint text and bytes."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil

root = Path('F:/Ourgame')
base = root / 'docs/production/first-batch-v2/evidence/run-save-adapter-v001'
before = base / 'status-before-v107-checkpoint-v001'
assert not before.exists()
before.mkdir()
names = ('README.md', 'AGENTS.md', '项目需求台账.md', 'docs/production/first-batch-v2/progress.json',
         '.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md',
         'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md')
for name in names:
    dst = before / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / name, dst)
    assert dst.read_bytes() == (root / name).read_bytes()

note = '''2026-10-16 当前检查点 v107：保持 EV048 怪诞钟盔与小比例。军剑统一显示比例 0.50，人物仍最高72px、UI隐藏，待机四相和首斩六相保留胸肩甲。v105真实双向实录已审，剑刃辨识改善；低位握柄、连续动作与全状态仍待打磨。原实录E185、播放页E189保持原来源版本。

存档真实进展：141911编译0 → 142054针对4/4 → 142409完整134/134，逐项零警告/错误/未运行，原130注册保留。v107冻结1545文件/3090端点大小与SHA零差，五美术Source与983资源和v105相同。[证据及边界](docs/production/first-batch-v2/run-save-adapter-runtime-proof-v001.md)。当前支持独立run-only磁盘传输与已有合法World分组安装，真正无初始新局的进程Continue仍待制作；完整D13尚未支持。

第二段：168直拳状初稿拒绝导入；169折肘纠正已生成、标准提取六帧，正在按真实像素测掌心/足底，再试独立剑适配。形状QA通过不等于握柄/足锁或动作验收，标准派生预览600ms也不符合540ms内核，均如实保留。原件/派生E193/E194。内置请求169，自动授权窗口008已1/24、余23，外部API0、费用未知；下一170。

| 当前部分 | 已实际接入 | 剩余 |
| --- | --- | --- |
| 钟盔军剑与胸肩 | 双向、72px、无UI；四相待机/六相首斩 | 第二/三段、走跑/空中/受击/死亡、握剑及连续动作 |
| 局内存档 | 严格整局Codec、真实磁盘、已有合法World原装填继续 | pristine新进程入口、完整Profile owner |
| 首批其余装备/敌人/Boss | 既有候选与代码保留 | 新风格全状态、20搭配、实战特效音效及获取掉落验收 |

正式完整0/15，目标active；当前人类事件仍EV048，下一EV049。以下均为历史记录，以本段及progress权威字段为准。

'''
for name in ('README.md', 'AGENTS.md'):
    path = root / name
    path.write_text(note + path.read_text(encoding='utf-8-sig'), encoding='utf-8')
ledger_path = root / '项目需求台账.md'
with ledger_path.open('a', encoding='utf-8') as f:
    f.write('\n| 2026-10-16；EV048继续，无新要求事件 | 怪诞军剑与原局保存 | v105剑0.50保持72px/UI隐藏并真实双向审录；169第二段六帧提取后测真实掌心/足底，尚未导入。SaveAdapter实际4GREEN及全134GREEN，v1073090端点SHA零差。 | [存档实证与范围](docs/production/first-batch-v2/run-save-adapter-runtime-proof-v001.md)；真正pristine新进程Continue、完整D13、全状态/20搭配/设备声音仍待，正式0/15active。 |\n')

path = root / 'docs/production/first-batch-v2/progress.json'
p = json.loads(path.read_text(encoding='utf-8-sig'))
p.update({
 'current_task': 'EV048 sword50 v105 real-J/native reviewed,72px/UIoff/armor kept. SaveAdapter actual4+full134GREEN v107 audited. Native169 standard6frame source measuring real palm/feet before sword-fit; not imported. Pristine new-process Continue/fullD13/full units remain; formal0/15 active.',
 'current_build': 'UnrealGame/Saved/Bootstrap/build-editor-20261016-141911.log',
 'current_build_exit_code': 0, 'latest_build_attempt': 'UnrealGame/Saved/Bootstrap/build-editor-20261016-141911.log',
 'latest_build_attempt_exit_code': 0,
 'current_compiled_snapshot': 'source-assets/production/backups/2026-10-16_RunSaveAdapter-actual134GREEN-v107',
 'ue_current_working_source_verified': True, 'ue_current_working_source_compiled': True,
 'current_source_uncompiled_changes': None, 'actual_registered_test_count_current': 134,
 'next_native_request': 170, 'next_snapshot': 'v108', 'next_retention_batch': 'E195',
 'current_turn_progress_classification': 'progress: actual uniform sword readability trial, native168 rejected/169 standard source, real SaveAdapter4RED12errors→4GREEN→full134GREEN; no unit completion',
})
p['latest_strict_UE_automation'] = {
 'report': 'UnrealGame/Saved/Automation/FirstRoom-20261016-142409/index.json',
 'filter': 'CodexDungeon', 'registered_in_filter': 134, 'succeeded': 134,
 'failed': 0, 'notRun': 0, 'inProcess': 0, 'warnings': 0,
 'old130_name_set_preserved': True, 'scope': 'v107 covered code contracts; real Run-only disk and existing valid World install, not pristine process Continue or art acceptance', 'formal_complete_units': 0}
p['latest_targeted_UE_automation'] = {'report': 'UnrealGame/Saved/Automation/FirstRoom-20261016-142054/index.json',
 'filter': 'CodexDungeon.Content.RunSaveAdapter', 'registered': 4, 'succeeded': 4,
 'failed': 0, 'notRun': 0, 'inProcess': 0, 'warnings': 0,
 'scope': 'Run-only canonical header/Codec/real disk/head/fault and existing target original reload'}
generation = json.loads((root / 'source-assets/production/first-unit-animation-v003/generation-ledger.json').read_text(encoding='utf-8-sig'))
assert generation['requested_count'] == 169 and generation['current_window']['requested_count'] == 1
p['generation_accounting_current'] = {'requested_count': 169, 'window_number': 8,
 'window_requested_count': 1, 'window_limit': 24, 'remaining_in_window': 23,
 'lifetime_requested_count': 193, 'external_api_calls': 0, 'fee_unknown': True}
p['run_codec_current_v001']['Store_semantic_live_adapter_bound'] = True
p['run_save_adapter_current_v001'] = {
 'state': 'actual4RED12errors then implementation4GREEN/full134GREEN v107; tests and 8 dependencies immutable',
 'scope': 'isolated BoundDevelopmentRunV1 only; CompleteProfile refused',
 'stage0_build': '140235exit0', 'actual_RED': 'FirstRoom-20261016-140335/index.json',
 'actual_RED_error_count': 12, 'production_build': '141911exit0',
 'actual_targeted': 'FirstRoom-20261016-142054/index.json', 'actual_full': 'FirstRoom-20261016-142409/index.json',
 'snapshot': 'v107', 'root_proof': 'docs/production/first-batch-v2/run-save-adapter-runtime-proof-v001.md',
 'independent_review': 'docs/production/first-batch-v2/evidence/run-save-adapter-v001/independent-production-review-v001.md',
 'actual_new_process_Continue': False, 'complete_D13': False,
 'pristine_bootstrap_dependency': 'explicit InitGame suppression + closed pristine gate + separate Prepare, preserve ordinary valid-target contract',
 'coverage_limits': ['outer metadata special character full Store roundtrip not separately executed', 'bad B2 followed by Adapter next normalCommit statically traced only'],
 'formal_complete_units': 0}
p['fairytale_sword_primary2_current_v001'] = {
 'native_request': 169, 'source_pose_accepted': False, 'imported': False,
 'shape_QA_passed': True, 'standard_timing_contract_passed': False,
 'actual_kernel_timing_ms': [75,75,60,60,135,135], 'standard_preview_ms': [100]*6,
 'derived_freeze': 'source-assets/production/fairytale-sword-primary2-v001/primary2-extraction-v002/extracted-freeze-v002.json',
 'raw_SHA256': '44552ec706ace7a07a49a8b3169bfb6483aff22912837dea156667f269e26747',
 'actual_mounts_measured': False, 'next': 'real palm/near-hand mask/feet evidence then independent-sword bounded fit trial; no more blind regeneration',
 'rejected_previous': 'native168 longpunch source preserved/E188/E190', 'formal_complete_units': 0}
p['current_source_frozen_audit_v107'] = {'files': 1545, 'bytes': 91947864, 'two_end_checks': 3090,
 'differences': 0, 'old_v105_Source_unchanged': 146, 'art5_Production983_identical_to_v105': True,
 'path': 'docs/production/first-batch-v2/evidence/run-save-adapter-v001/actual134GREEN-v107-audit-v001.json',
 'timing': 'before current documentation; UE Source/DLL/packages untouched by this checkpoint'}
p['current_turn_media_retention'].update({'review_capsule': 'pending_new_version_after_measurement', 'latest_source_derived': 'E194'})
p['current_retention_batches'] = list(dict.fromkeys(p.get('current_retention_batches', []) + [f'E{i}' for i in range(191,195)]))
p['next_work'] = ['Implement and actually verify pristine no-newRun startup gate/prepare, then two genuine processes Continue',
 'Measure169 real palm/feet and test independent sword fit; retain failed168 and unaccepted motion/timing',
 'Finish full original equipment/enemies/Boss, all states,20pairings,VFX/SFX/acquire/equip/drops and full persistence; formal0/15active']
p['previous_goal_turn_classification'] = {'classification': 'progress', 'blocking_condition_repeated_consecutively': 0,
 'reason': 'actual new sword runtime/native-source work and semantic SaveAdapter4RED→full134GREEN; next bootstrap is actionable', 'goal_status': 'active'}
path.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding='utf-8')
plan_note = '\n\n2026-10-16 v107实际续行：SaveAdapter Stage0 140235编译0→140335真实4RED/12errors（v106状态14error旧文字另有erratum）；只生产CPP后141911编译0→142054四组GREEN→142409完整134GREEN，旧130名集保留/default134。v1071545files91947864B/3090current+frozen端点SHA0；旧146Source、美术5Source与983包和原v105剑50录像一致。独立审查实际4及10slot文件，不冒full134独立审查。run-only真实disk/head/fault/atomicPrepare/既有World原reload未来行为闭合；外层特殊metadata和badhead→下一commit未单测，pristine新进程Continue及完整D13未完。EV048 art：168源姿态拒绝；169标准6帧提取/真实掌心足底测量中，未导入/未接受motion，preview600≠kernel540保留。ledger169/window0081of24/remaining23/lifetime193/external0/费用未知。正式0/15active，下一pristine InitGame封门和独立Prepare，不削弱正常Capture目标前提。\n'
for name in names[-2:]:
    with (root / name).open('a', encoding='utf-8') as f: f.write(plan_note)
print(json.dumps({'status': 'v107 durable current checkpoint refreshed', 'before_files': len(names),
                  'registered': 134, 'native': 169, 'formal_complete_units': 0}, ensure_ascii=False))
