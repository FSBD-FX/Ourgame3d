"""Sync durable current status from an actual complete GREEN report."""
from pathlib import Path
import datetime,hashlib,json,shutil
root=Path('F:/Ourgame');docs=root/'docs/production/first-batch-v2';e=docs/'evidence/run-capture-v001'
audit=json.loads((e/'actual-full122-audit-v001.json').read_text(encoding='utf-8'));assert audit['succeeded']==122 and not audit['differences']
p=docs/'run-capture-typed-aggregate-runtime-proof-v001.md';assert not p.exists()
p.write_text('''# Bound Run完整类型采集与纯验证：实际122GREEN

2026-10-16，UE5.5.4。当前仅完成现有BoundDevelopmentV1范围的只读Capture与sealed纯Validate；pausedPrepare/Install、完整canonical codec、Store语义接线和新进程Continue尚未完成。当前正式内容0/15。

实际链：先由探索银行060539真实2RED→061546合法路线1GREEN/Restore1RED→061658两组GREEN建立非空真实源。聚合061737四组在正常输入的真实源后因Capture stub失败，v083保留。首次生产063039因新校验把ECC_MAX的deprecated伪通道32越界读取而误拒；本机原生response数组仅32个槽，改完整container逐槽exact比较，真实Visibility Ignore拒绝/恢复控制保留。063645/064122/064847分别保留unknownPrimitive及详细nativeBuilder诊断，均是几何前门RED，不假称纯Validate已测过。

原生默认Brush实际有6个编辑面，notForClientServer=true、四BSP数组为空、BodySetup为空且无有效游戏body；最终仅按exactWorld默认对象、native类/root/component/model同一、Brush_Default、明确非游戏标志和无碰撞体识别无效果bootstrap。其他unknownPrimitive继续拒绝；新增真实默认Brush临时挂BodySetup拒绝、保持Out/live不变、恢复nullptr又成功的控制，不删除夹具或改游戏墙配置。

最终build065417 exit0；实际065538四组全Success，实际065641全122项Success、零warnings/fail/notRun/inProcess。原116注册名全保留，原52个测试源逐SHA/size未改；新增正好bank2+aggregate4。默认runner仅在实际GREEN后116→122，无另一次默认参数重复运行的声明。v089冻结1164files、76,025,511B，canonical F与frozen F两端2328次大小/SHA检查零差；这不是E源代码镜像。当前DLL SHA62c80de938d93ad854b5b6872d91be34c33185b7e16919edb3e8bf6e53ba6362。

Capture在完整Tick之外读取真实equipment/Scene/world/currentactors含dead及顺序/rewards及物理pickups/每房精确fog/root时钟标志/audiofuturephase续行值；拒绝activeTick、未清damage/motion边界、未知geometry或丢失owner。构造局部完整候选并纯验证后才替换Out。Validate复用已验证owner原Restore与Fighter纯转发，不spawn/Step/Reveal/RNG/IO/replay；sealed结果只在全部验证后成组发布。真实lockedmelee/protecteddodge/pendingequip/reload/custommuzzle、正常击杀和跨房历史、精确探索、副本只读及非法候选原子拒绝均通过。

SceneCommitRequested与SceneEquipmentTargetLost是被公开交互入口接受、影响下一输入世代的续行事实，原值保留。TargetLost可由合法公开Select/Update在Tick之间产生，不根据当前Scene.pending强清为false；不是承诺重建整个过去输入journal。audio保存producer cursor/tail与未来义务，不保存SoundWave/UObject/旧播放请求或冒充完整历史音频账本。

已通过的无Canvas探索路线不是可见迷雾录像。当前新美术肩甲录像是明确unbound冻结观察、绑定历史v085 DLL，不能倒填本次v089或说它完成boundHUD迁移的可见验收。后续需要真实bound运行录像、事务安装/codec/Store/newprocessContinue及完整装备敌人动作与音效。
''',encoding='utf-8')
p=docs/'progress.json';s=json.loads(p.read_text(encoding='utf-8-sig'))
s['previous_full_GREEN_UE_automation']=s['latest_strict_UE_automation']
s['latest_strict_UE_automation']={'report':audit['actual_report'],'registered':122,'succeeded':122,'failed':0,'notRun':0,'inProcess':0,'warnings':0,'old116_names_preserved':True,'default_runner_separate_rerun':False}
s['latest_targeted_UE_automation']={'report':'UnrealGame/Saved/Automation/FirstRoom-20261016-065538/index.json','registered':4,'succeeded':4,'failed':0,'warnings':0,'notRun':0,'scope':'Actualtyped Capture/Validate, notInstall/Continue'}
s['current_compiled_snapshot']=audit['snapshot'];s['ue_current_working_source_compiled']=True;s['ue_current_working_source_verified']=True
s['current_source_uncompiled_changes']='None. CurrentgameSource/DLL/Production and122runnercount bound to actualfull065641/v089; subsequentdocs-only updates.'
s['current_working_source_after_v075']='Historicalv079116GREEN; currentv089full122GREEN, typedCaptureValidate only. No pausedInstall/codec/diskContinue.'
s['default_test_runner_expected_tests']=122;s['actual_registered_test_count_current']=122
s['run_capture_typed_aggregate_v001']={'status':'actualfull122GREEN_CaptureValidate_only','snapshot':audit['snapshot'],'proof':'docs/production/first-batch-v2/run-capture-typed-aggregate-runtime-proof-v001.md',
 'snapshot_files':1164,'snapshot_bytes':76025511,'canonical_F_vs_frozen_F_checks':2328,'differences':0,
 'old_test_source_files_unchanged':52,'whole_transaction_install_complete':False,'codec_complete':False,'disk_continue':False,'visible_bound_migration_recorded':False}
s['current_turn_progress_classification']='progress: bank2RED to2GREEN; aggregate4semanticRED and nativegeometry false-rejection diagnosis to full122GREEN;149near/150far actual8import and25.2s12combinationUE recording reviewed; completegoal0/15'
s['next_snapshot']='v090';s['next_retention_batch']='E109';s['next_native_request']=151;s['next_human_event']='EV-049';s['goal_status']='active'
s['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
head='''2026-10-16当前已核状态：065641实际完整UE122/122Success、零警告/失败/未运行/inProcess；旧116名和52旧test源保留。Run探索银行与typedAggregate只读Capture/pureValidate闭合，v0891164files76025511B canonicalF/frozenF两端2328SHA大小零差，DLL62c80de9…。默认runner122。pausedInstall/codec/Store语义接线/新进程Continue及bound迷雾可见录像仍待，正式完整内容0/15，fullgoalactive。
EV048美术实际完成本轮试样：149near4/150far4独立肩甲导入并与147胸片/原131body在72px、UIoff下录制25.201684s、756观测/757PNG。12组合全部四pose/3–4wrap、全CRC/FIFO/flush/MP4decode过；E106771files2801563708B两SHA0。root8＋peer36＝36unique原帧审看，真实浏览器短段采样播放，未全视频逐帧/完整motion或zero collision接受。近肩可辨；far细节弱、near pose1盔下紧。录像绑定历史v085，不用v089倒填。E107播放页、E108复核留档；E100partial失败仍保留。Production881=857T+22SW+2M，old873unchanged。ledger150/window0076of24剩18/lifetime174/external0/费用未知；next151/E109/v090/真实humanEV049。

'''
for name in ['README.md','AGENTS.md']:
 p=root/name;old=p.read_text(encoding='utf-8-sig');p.write_text(head+'此前检查点记录（以顶部当前状态为准）：\n\n'+old,encoding='utf-8')
readme=root/'README.md'
with readme.open('a',encoding='utf-8') as f:
 f.write('''\n## EV048当前资产试样状态（2026-10-16）

| 资产 | 实际接入 | 当前边界 |
| --- | --- | --- |
| 原131钟盔角色 | 4idle/6walk独立造型观察；最高72px | 战斗各状态与新甲层仍待完整适配 |
| 147独立胸片 | 4idle、实际Texture2D与真实显隐录像 | 正式换甲/全动作待 |
| 149近肩＋150远肩 | 真正不同透视各4idle；8Texture2D实际导入、12组合实录 | 护腕/护胫、保护mask、武器遮挡与全动作待 |
| 蘑菇石像造型 | 4idle真实观察、93.6px目标 | 完整新风格敌人各状态待 |

[25秒双肩甲实录](F:/Ourgame/过程图稿与视频/2026-10-16_暗黑童话双肩甲明暗双向真实观察_v001/展示副本/fairytale-shoulder-lookdev-silent.mp4) · [手动试样入口](F:/Ourgame/暗黑童话肩甲预览.cmd) · [本轮复核](F:/Ourgame/docs/production/first-batch-v2/runtime-review-fairytale-shoulder-lookdev-v001.md)。入口与实录同flag，cmd尚未单独启动；不是正式装备获取或战斗完成。
''')
plan=root/'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md';text=plan.read_text(encoding='utf-8')
text=text.replace('- [ ] Capture remaining GameMode/Run fields and compose existing verified owners into the aggregate, including pickup/reward/audio/room/input cursors; do not reimplement the completed owner primitives.',
 '- [x] Bounded typed current-owner Capture/Validate inclpickup/rewards/audio/room/input: actual0655384GREEN→065641full122GREEN/v089. Existing owner primitives reused; pausedInstall/codec/newprocessContinue remain separate below.')
text=text.replace('- [ ] scale_tests: complete typed aggregate Capture and sealed pure Validate. Include all current owner states/scalars/dead actors and order/pickup projections/stable rewards/exploration/audio continuation seeds/known geometry scope. Upstream bank source must first be genuinely admitted; a missing-bank failure cannot certify aggregate semanticRED.',
 '- [x] scale_tests typed Capture/Validate: admittedbank2GREEN→061737aggregate4semanticRED; nativegeometry diagnostics preserved, exactresponse/defaultbuilder correction andnegativecontrols→0655384GREEN/065641full122GREEN. Scope isCapture/Validate only; finalindependentreview addedseparately.')
plan.write_text(text,encoding='utf-8')
with (root/'.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md').open('a',encoding='utf-8') as f:
 f.write('\nActual currentcontinuation progress: native149near/150far actual8Texture2D imported/saved old873unchanged/Production881;25.201684s756HUD757PNG12displaycombinations allfourposes3–4wrap, fullnativeCRC/FIFO/flush andsilentMP4decode. E106771files2801563708B twoSHA0 before8root+36peer=36unique originalviews; actualIAB shortcycle sampling, fullmotion/masks/allactions notaccepted. E107player/E108reviews retained. Ledger150/window7 6of24remaining18/lifetime174; no newhumanEV. Typedaggregate actual063039/063645/064122/064847 geometryRED retained; local32-slot deprecatedindex bug exactcontainer fix; precise nativebootstrapBrush6editorPolys/0BSP/0Body recognized onlyexactknown object, visibility/bodySetup/foreignBox negative controls intact. Actual065538target4GREEN→065641full122Success0warnings/fail/notRun/inProcess, v0891164files76025511B canonicalF/frozenF2328sizeSHA0; old116names/52oldtestsource exact. Defaultcount122 onlyafterGREEN, no separatedefaultrepeatclaimed. Captured/Validated only, pausedInstall/codec/StoreContinue/visibleboundmigration/full15 remain. Goalactive0of15, next151/E109/v090/humanEV049.\n')
print(json.dumps({'actual_full_GREEN':122,'snapshot':'v089','durable_status_synced':True,'formal_complete_units':0,'goal_status':'active','independent_final_review':'pending_addendum'}))
