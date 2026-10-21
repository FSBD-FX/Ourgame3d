"""Bind the actual v103 visual trial to the later, separate v104 codec regression."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path('F:/Ourgame')
D = R / 'docs/production/first-batch-v2'
B = R / 'source-assets/production/fairytale-armor-sword-primary1-v001'
A = R / '过程图稿与视频/2026-10-16_钟盔军剑首斩穿甲真实按键试装_v001'
S103 = R / 'source-assets/production/backups/2026-10-16_RunCodec3GREEN1RED-PrimaryArmor42-unrendered-v103'
S104 = R / 'source-assets/production/backups/2026-10-16_RunCodecNULfix-actual130GREEN-PrimaryArmor42-v104'
EVIDENCE = D / 'evidence/primary1-armor-v001'


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def desc(p):
    data = p.read_bytes()
    return {'path': p.as_posix(), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def new(p, value):
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def check_report(relative, count):
    p = R / relative
    d = load(p)
    assert d['succeeded'] == count and len(d['tests']) == count
    assert all(d.get(k, 0) == 0 for k in ('failed', 'notRun', 'inProcess', 'succeededWithWarnings'))
    assert all(t['state'] == 'Success' and t.get('warnings', 0) == 0 and t.get('errors', 0) == 0 for t in d['tests'])
    names = {t['fullTestPath'] for t in d['tests']}
    assert len(names) == count
    return p, names


full, names130 = check_report('UnrealGame/Saved/Automation/FirstRoom-20261016-131229/index.json', 130)
targeted, names4 = check_report('UnrealGame/Saved/Automation/FirstRoom-20261016-130934/index.json', 4)
old, names126 = check_report('UnrealGame/Saved/Automation/FirstRoom-20261016-111515/index.json', 126)
assert names126 < names130 and names130 - names126 == names4
assert '[int]$ExpectedTests = 130' in (R / 'tools/scripts/test-first-room.ps1').read_text(encoding='utf-8-sig')

# Immutable historical movie inputs, then both endpoints of every current snapshot entry.
m103, m104 = load(S103 / 'compiled-source-manifest.json'), load(S104 / 'compiled-source-manifest.json')
for x in m103['files']:
    p = S103 / x['path']
    q = desc(p)
    assert q['bytes'] == x['bytes'] and q['sha256'] == x['sha256'], p
for x in m104['files']:
    for p in (R / x['path'], S104 / x['path']):
        q = desc(p)
        assert q['bytes'] == x['bytes'] and q['sha256'] == x['sha256'], p
assert m104['actual_automation_succeeded'] == 130 and m104['actual_automation_failed'] == 0
art_names = ['DungeonHUD.h', 'DungeonHUD.cpp', 'DungeonFairytaleSwordPresentation.cpp', 'DungeonFairytaleSwordDrawState.h', 'DungeonFairytaleSwordProbe.cpp']
art = [R / 'UnrealGame/Source/CodexDungeon' / n for n in art_names]
for p in art:
    assert p.read_bytes() == (S103 / p.relative_to(R)).read_bytes()
packages = [p for p in (R / 'UnrealGame/Content/Production').rglob('*') if p.is_file()]
assert len(packages) == 983
assert len([p for p in (S103 / 'UnrealGame/Content/Production').rglob('*') if p.is_file()]) == 983
for p in packages:
    assert p.read_bytes() == (S103 / p.relative_to(R)).read_bytes()
codec = R / 'UnrealGame/Source/CodexDungeon/DungeonRunSnapshotCodec.cpp'
assert desc(codec)['sha256'] == '0dc1a8e720c018700a62828859bb8f1d49c793d725adbae82d8b5252f4bf6728'
assert desc(R / 'UnrealGame/Source/CodexDungeon/Tests/DungeonRunSnapshotCodecTests.cpp')['sha256'] == '9fdb83df5c6134aa9b232b21674985a756d9d3dcda22dc1792569ac9f5284d31'

runtime = load(A / '原件/sword-armor-primary1-runtime-verification.json')
head = load(A / '原件/visible-ready-primary-head-gate-v001.json')
pixels = load(A / '原件/native-pixel-verification.json')
video = load(A / '原件/video-presentation-receipt-v001.json')
binding = load(A / '原件/compiled-source-binding-audit-v001.json')
selected = load(A / '原件/selected-frame-source-map-v001.json')['frames']
assert runtime['passed'] and runtime['observations'] == 174 and runtime['kernel_phase_sampling_exact']
assert runtime['Ready_stack_exact'] and runtime['Primary_stack_exact']
assert head['passed'] and head['checked_supported_observations'] == 171 and head['failed_observations'] == 0 and head['minimum'] == 376
assert pixels['passed'] and pixels['verified_original_PNG_count'] == 175
assert video['full_decode_exit'] == 0 and video['audio_recorded'] is False
assert desc(Path(video['video']['path'])) == video['video']
assert binding['endpoint_checks'] == 3070 and binding['mismatches'] == 0
retained = []
for suffix, count in [('primary1-armor42-realJ-runtime-v181', 234), ('primary1-armor42-player-v182', 7)]:
    p = Path('E:/OurGame/Knight/过程图稿与视频') / ('2026-10-16-OurgameUE-' + suffix) / 'source-size-SHA256.json'
    d = load(p)
    assert d['file_count'] == count and d['verification_passes'] == 2 and d['source_and_target_hash_mismatches'] == 0 and d['root_readme_unchanged']
    retained.append(desc(p))

review = {
    'human_event': 'EV-048 continued; no new human requirements event',
    'facts': {
        'new_imported_Texture2D': 42, 'old941_unchanged': True, 'Production_packages': 983,
        'capture_snapshot': desc(S103 / 'compiled-source-manifest.json'),
        'capture_source_codec_state': '3GREEN1RED, before the later narrow embedded-NUL production fix',
        'capture_duration_s': runtime['duration_s'], 'observations': 174, 'original_PNG_including_prewarm': 175,
        'Ready_masks_both_facings': 15, 'Primary1_masks_both_facings': 63,
        'Ready_stack': 7, 'Primary_stack': 8, 'body_max_px_at_1280x720': 72, 'game_UI_hidden': True,
        'native_pixel_checks': desc(A / '原件/native-pixel-verification.json'),
        'head_gate_checked': 171, 'head_gate_failures': 0, 'head_gate_minimum': 376, 'head_gate_threshold': 20,
        'kernel_primary_phase_ms': [85, 85, 60, 60, 155, 155],
        'capture_before_codec_fix_source_binding_endpoints': 3070,
        'root_actually_viewed_whole_selected_indices': [0, 2, 3, 10, 12, 13, 16, 6],
        'root_actually_viewed_unscaled_crops': [desc(Path(x['unscaled_crop']['path'])) for x in selected],
        'independent_native_review': desc(EVIDENCE / 'independent-native-review-v001.md'),
        'independent_native_review_json': desc(EVIDENCE / 'independent-native-review-v001.json'),
        'independent_source_review': desc(EVIDENCE / 'independent-source-review-v002.md'),
        'browser_playback_samples': {'tab': 10, 'playing_s': 0.289762, 'ended_s': 5.833333, 'width': 1280, 'height': 720, 'error': None, 'continuous_framewise_visual_review': False},
        'video': video['video'], 'audio_recorded': False,
        'current_snapshot': desc(S104 / 'compiled-source-manifest.json'),
        'current_build': desc(R / 'UnrealGame/Saved/Bootstrap/build-editor-20261016-130720.log'),
        'current_snapshot_files': len(m104['files']), 'current_snapshot_endpoint_checks': len(m104['files']) * 2,
        'current_snapshot_size_SHA_mismatches': 0, 'historical_v103_frozen_files_checked': len(m103['files']),
        'art_five_Source_and_all983_packages_unchanged_since_movie': True,
        'full130': desc(full), 'targeted4': desc(targeted), 'old126_names_preserved': True,
        'warnings_errors_notRun_inProcess': 0, 'default_test_runner_count': 130,
        'retention_receipts': retained,
    },
    'reasoning': 'The candidate armor remains attached from Ready through the first attack using actual kernel phases and matching six-pose components. This is sufficient to continue the chosen grotesque armor direction at small scale. Regression success establishes the covered code contracts only; neither a larger source composite nor a visible-head gate proves finished art or motion.',
    'risks_and_open_work': [
        'Far shoulder and crossed/downstroke chest are weak or occluded; thin windup blade has weak contrast against brick although present outside the helmet.',
        'Root reviewed eight whole frames and twenty native-size crops; independent reviewer reviewed twenty whole frames and twelve Primary crops. Browser playback samples are not full continuous framewise motion acceptance.',
        'Thumb/grip, footlock, shared ink ownership, Ready transitions and zero overlap remain unaccepted.',
        'Only Ready4 and ground Primary1six are implemented in this new armor style. Walk/run/air/hurt/death and Primary2/3 remain placeholders using new Ready0 without armor or sword.',
        'Actual equipment-ID switching, four armor types and twenty weapon/armor pairings remain unfinished.',
        'No enemy hit or sound was recorded in this silent first-cut trial; remaining enemies, Boss, VFX, SFX and full content acceptance remain open.',
        'The installed standard sprite preview GIF has six 100ms frames, differing from the requested attack timing. It is retained as a known defect; actual game phase timing above is separately verified and source previews were not manually retimed.',
        'Hidden registration targets are explicit trial designs with source-pixel uncertainty, not measured bones. Native166 and old native16730x28 failures are retained; new16732x30 uses one shared row scale and unchanged QA.',
        'Codec canonical transport now passes four groups and full130 after preserving actual4RED then3GREEN1RED and fixing only scalar NUL append. Disk semantic adapter, menu Continue and fresh-process resume are still unfinished.',
    ],
    'art_finally_accepted': False, 'full_motion_accepted': False, 'formal_complete_units': 0, 'goal_status': 'active',
}
new(D / 'runtime-review-fairytale-sword-armor-primary1-v001.json', review)
new(D / 'runtime-review-fairytale-sword-armor-primary1-v001.md', '''# EV048 首斩穿甲实景检查点

事实：胸甲、双肩与身体共42张分层纹理已实际导入，旧941包未变，Production共983包。v103真实Enter/A/J双向试装5.800889秒、174观察/175原PNG；待机四相、地面第一斩六相齐全，实际7/8层堆栈与内核85/85/60/60/155/155ms一致，人物最高72px、游戏UI隐藏。原生像素校验、171次可见钟盔检查及视频完整解码通过。录像无声，原始版本仍是v103。

推理：第一斩现在保留胸肩，钟盔与眼窗在小比例下可辨，可以按既定怪诞盔甲方向继续制作。root实际看8幅完整画面与20幅原尺寸裁图，独立审图看20幅完整画面与12幅首斩裁图；播放页已打开并抽样确认播放到结尾。此证据支持局部试装，不等于连续动作、握剑或完整装备验收。

风险与下一步：远肩、横臂/下劈胸甲与蓄力细剑刃仍弱，先改善轮廓和背景对比，再检查连续动作/握剑/脚锁，制作连招二三段及走跑、受击、死亡等状态。未覆盖状态明确使用新Ready0无甲无剑占位；四种甲/20搭配、正式装备ID、敌人/Boss、特效音效、获取掉落及存档继续推进。标准源GIF仍为六帧各100ms的已知工具缺陷，游戏相位另行核验，不以其证明游戏节奏。

工程核验：新Codec在真实四组RED和随后3GREEN1RED后，仅修正FString::AppendChar忽略NUL的两个标量分支；测试未放宽。130720编译退出0，130934定向4/4、131229完整130/130通过，零警告/错误/未运行，旧126项名称保留。当前v104与v103的五个美术Source及全部983资源逐字节相同；录像不倒填成v104。完整磁盘存档/新进程Continue尚未完成。

媒体先在F留原件/展示副本并于E181/E182两遍大小与SHA核验零差，旧版本与失败样本保留。首批完整目标仍active，正式完成0/15。
''')

backup = EVIDENCE / 'status-before-runtime-final-v001'
assert not backup.exists()
backup.mkdir()
status_files = ['README.md', 'AGENTS.md', '项目需求台账.md', 'docs/production/first-batch-v2/progress.json', '.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md', 'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md']
for i, name in enumerate(status_files):
    p = R / name
    target = backup / f'{i:02d}-{p.name}'
    shutil.copy2(p, target)
    assert p.read_bytes() == target.read_bytes()

summary = '''2026-10-16当前：EV048怪诞钟盔首斩穿甲试装已实录。人物最高72px、游戏UI隐藏，待机四相/第一斩六相均保留胸甲和双肩，42新Texture实际保存、旧941不变、Production983。真实双向Enter/A/J5.800889秒，174观察/175原PNG，内核相位/7与8层堆栈/171次可见钟盔/完整解码通过。root与独立审图已复核，播放页已打开；远肩和蓄力细刃仍弱，连续动作、握剑与全状态尚未接受。新入口：钟盔军剑首斩穿甲试装.cmd；录像与审阅见 docs/production/first-batch-v2/runtime-review-fairytale-sword-armor-primary1-v001.md。

当前v104：130720编译退出0→130934Codec4/4→131229完整130/130，零警告/错误/未运行，旧126注册保留。v103录像仍绑定当时3GREEN1RED的Codec；后续只修NUL标量追加，五个美术Source和983资源不变，不倒填录像版本。存档传输Codec通过覆盖测试，磁盘语义接入与新进程Continue仍未完成。

| 当前资源/功能 | 已接入 | 尚待完成 |
| --- | --- | --- |
| 钟盔持剑角色与胸肩甲 | 待机4相、首斩6相；双向、小比例、UI隐藏 | 连招2/3、走跑/空中/受击/死亡、连续动作与握剑验收 |
| 首斩匹配分层 | 159身体四归属24层 +164胸/165近肩/167远肩18层，共42Texture | 正式装备ID、四种防具/20武器防具搭配 |
| 首批敌人、Boss、音效特效 | 保留既有候选与代码 | 新画风完整动作、实战命中、视听和获取掉落验收 |
| 局内存档 | 有界内存捕获/安装、严格Codec与130项回归 | 磁盘完整语义接入和新进程Continue |

媒体F原件/展示副本已先行E181/E182两遍SHA留档；本轮复核总包E183待复制核验。内置生成请求167，窗口007已23/24、余1，下一168；外部API0、内置费用未核实。正式完整0/15，目标active。

此前检查点（历史，以顶部当前及progress权威字段为准）：

'''
for name in ['README.md', 'AGENTS.md']:
    p = R / name
    p.write_text(summary + p.read_text(encoding='utf-8-sig'), encoding='utf-8')

p = D / 'progress.json'
d = load(p)
priorities = [
    'Strengthen far shoulder/chest and windup sword contrast at72px; inspect continuous Ready/Primary1 motion, thumb/grip and footlock before art acceptance',
    'Build Primary2/3 plus walk/run/air/hurt/death in the chosen grotesque armor style; bind actual equipment IDs/four armors/20 pairings',
    'Finish remaining enemies/Boss/VFX/SFX/acquisition/rewards and disk semantic adapter/new-process Continue; keep full goal active0/15',
]
d.update(current_task='EV048 first-cut armor real-input trial complete as bounded candidate: Ready4/Primary1six both-facing72px/UIoff,42new textures/983packages. Current v104 actual130GREEN after narrow Codec NUL fix; recording remainsv103. Fullmotion/equipment/allstates/enemies/audio/diskContinue unfinished; formal0/15 active.',
         current_build='UnrealGame/Saved/Bootstrap/build-editor-20261016-130720.log', current_build_exit_code=0,
         current_compiled_snapshot=S104.relative_to(R).as_posix(), next_snapshot='v105', next_retention_batch='E183',
         actual_registered_test_count_current=130, ue_current_working_source_verified=True, ue_current_working_source_compiled=True,
         current_source_uncompiled_changes='', current_working_source_after_v075='Historical suffix; currentv104 actual130GREEN. Disk semantic adapter/new-processContinue still open.',
         next_work=priorities, next_turn_priorities=priorities, next_presentation_priorities=priorities,
         current_turn_progress_classification='Actual4native calls,42textures imported, realbothfacing first-cut armor trial, codeCodec130GREEN; no new human event; formal0/15',
         version_suffixed_status_fields_are_historical=True)
d['latest_strict_UE_automation'] = {'report':full.relative_to(R).as_posix(), 'filter':'CodexDungeon', 'registered_in_filter':130, 'succeeded':130, 'failed':0, 'notRun':0, 'inProcess':0, 'warnings':0, 'errors':0, 'old126_names_preserved':True, 'new_codec_groups':4, 'scope':'Covered current code contracts only; no full art/motion/content acceptance', 'formal_complete_units':0}
d['latest_visual_runtime_proof'] = {'report':desc(D / 'runtime-review-fairytale-sword-armor-primary1-v001.json'), 'capture_snapshot':S103.relative_to(R).as_posix(), 'video':video['video'], 'archive':A.as_posix(), 'observations':174, 'original_PNG_including_prewarm':175, 'duration_s':runtime['duration_s'], 'Ready_stack':7, 'Primary_stack':8, 'root_whole_views':8, 'root_unscaled_crop_views':20, 'independent_whole_views':20, 'independent_Primary_crop_views':12, 'audio_recorded':False, 'full_motion_accepted':False, 'formal_complete_units':0}
d['current_source_frozen_audit_v104'] = {'files':len(m104['files']), 'bytes':m104['bytes'], 'two_end_checks':2*len(m104['files']), 'differences':0, 'artSource5_Production983_unchanged_since_v103':True, 'timing':'Before final documentation updates; code/DLL/assets unchanged by documentation'}
d['fairytale_sword_primary1_armor_current_v001'].update(HUD_optin_wiring_written_uncompiled=False, actual_game_rendered=True, full_motion_accepted=False, equipment_or_motion_accepted=False, capture_snapshot='v103', current_compiled_snapshot='v104', runtime_review=desc(D / 'runtime-review-fairytale-sword-armor-primary1-v001.json'))
d['run_codec_current_v001'].update(production_implementation_in_progress=False, production_implementation_version='implementation-v002', production_cpp=desc(codec), final_targeted_report=desc(targeted), final_full_report=desc(full), final_succeeded=4, actual_full_succeeded=130, preserved_intermediate='v1033GREEN1RED embeddedNUL; narrow scalar AppendChars fix only', Store_semantic_live_adapter_bound=False, new_process_Continue_complete=False)
d['current_turn_media_retention'] = {'latest_runtime':'E181', 'player':'E182', 'review_capsule':'E183_pending_copy', 'two_pass_size_SHA_mismatches':0, 'root_README_unchanged':True, 'not_acceptance':True}
d['current_retention_batches'] = [f'E{i}' for i in range(138,183)]
assert d['goal_status'] == 'active' and all(x['status'] == 'not_complete' for x in d['units'])
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
with (R / '项目需求台账.md').open('a', encoding='utf-8') as f:
    f.write('\n| 2026-10-16；EV048继续执行，无新要求事件 | 怪诞盔甲与轮廓 | 首斩匹配42Texture接入；真实双向72px/UI隐藏，5.8秒174观察/175原PNG；root及独立原尺寸审图，E181实录/E182播放页。 | 待机到首斩穿甲已接入，远肩/细剑刃/连续动作仍需打磨；后两段、全状态和正式装备未完成。v104完整130回归通过，录像仍v103；完整0/15目标active。 |\n')
checkpoint = '\n2026-10-16 EV048 Primary1 armor checkpoint: actual42Texture import/983Production; v103realEnter/A/J5.800889s174obs175nativePNG, Ready7/Primary8 kernelstacks and bothfacing4/6 phases,171headchecks0fail/min376, CRC/flush/decode pass. Root8whole20crop and independent20whole12crop reviewed; browserplayback .289762/end5.833333 sparse samples. Far shoulder/thin windup blade/fullmotion/grip remain unaccepted. ProductionCodec preservedactual4RED then3GREEN1RED; narrowFString NUL AppendChars scalarfix only,130720build0→130934target4GREEN→131229full130GREEN,old126names retained. v104Source/DLL/assets snapshot audited; artSource5/all983packages match originalv103movie. E181/E182 retained; E183reviewcapsule pending. Newstyle Primary2/3/allstates/equipment20mix/enemies/SFX/VFX/disksemanticadapter/freshprocessContinue remain open; goalactive0/15. Nextnative168/window007remaining1,nextsnapshotv105,humanEV049.\n'
with (R / '.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md').open('a', encoding='utf-8') as f:
    f.write(checkpoint)
with (R / 'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md').open('a', encoding='utf-8') as f:
    f.write('\n## EV048 first-cut armor and Codec checkpoint — 2026-10-16\n\n- [x] Matching Primary1 six-pose body/armor42Texture and bounded actual72px dual-facing real-input trial; originalv103movie retainedE181/E182.\n- [x] Canonical typed Codec transport: actual4RED→3GREEN1RED→narrow scalarNULfix→target4GREEN/full130GREEN; tests unchanged, currentv104.\n- [ ] Art acceptance: far shoulder/chest, thin windup blade, continuous motion/grip/footlock, Primary2/3/allstates/actual equipment20mix, enemies/Boss/VFX/SFX.\n- [ ] Existing generation-store full semantic adapter plus disk commit and fresh-process normal-input Continue; transport alone does not close the save plan.\n')
print(json.dumps({'snapshot':S104.name, 'files':len(m104['files']), 'endpoint_checks':2*len(m104['files']), 'differences':0, 'full_regression':130, 'actual_visual_snapshot':'v103', 'formal_complete_units':0}, ensure_ascii=False))
