"""Truthful durable checkpoint for the actual source-bound armor trial."""
from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';E=D/'evidence/sword-armor-ready-v001'
S=R/'source-assets/production/backups/2026-10-16_SwordReadyArmor24-preloadFix-actual126GREEN-v101'
A=R/'过程图稿与视频/2026-10-16_钟盔军剑低位胸肩真实按键试装_v002'
BAD=R/'过程图稿与视频/2026-10-16_钟盔军剑低位胸肩真实按键试装_v001'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=load(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-111515/index.json')
assert report['succeeded']==len(report['tests'])==126 and all(report[k]==0 for k in ['failed','notRun','inProcess','succeededWithWarnings'])
assert all(t['state']=='Success' and t['warnings']==t['errors']==0 for t in report['tests'])
old=load(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-074841/index.json')
assert {t['fullTestPath'] for t in old['tests']}<={t['fullTestPath'] for t in report['tests']}
manifest=load(S/'compiled-source-manifest.json')
for row in manifest['files']:
 for endpoint in [R,S]:
  p=endpoint/row['path'];v=desc(p);assert v['bytes']==row['bytes'] and v['sha256']==row['sha256'],p
assert len(manifest['files'])==1399
runtime=load(A/'原件/runtime-report.json');gate=load(A/'原件/sword-armor-runtime-verification.json')
pixels=load(A/'原件/visible-ready-head-gate-v001.json');failed=load(BAD/'原件/visible-ready-head-gate-v001.json')
assert runtime['passed'] and gate['passed'] and gate['actual_armor_masks']=={'-1':15,'1':15}
assert pixels['passed'] and pixels['checked_Ready_observations']==137 and pixels['failed_observations']==0 and pixels['minimum']==376
assert not failed['passed'] and failed['failed_observations']==3 and failed['minimum']==4
assert len(runtime['observations'])==174 and len(list((A/'原件').glob('*.png')))==175
assert desc(A/'展示副本/fairytale-sword-lowguard-armor-ready-silent.mp4')['sha256']=='b09be9ee852ffd4e46e98a80cf3953cd6d742dd6c91af6f80afb50aa0ead95a1'
assert load(A/'原件/video-presentation-receipt-v001.json')['full_decode_exit']==0
sourceindex=load(A/'index.json')
for path,sha in sourceindex['source_sha256_at_capture'].items():assert desc(R/path)['sha256'].upper()==sha
assert desc(R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll')['sha256'].upper()==sourceindex['module_sha256']
reviews=[E/'independent-layer-wiring-review-v001.md',E/'independent-native-frames-review-v001.md',
 E/'preload-fix-review-v002.md',E/'independent-native-frames-review-v002.md']
assert all(p.is_file() for p in reviews),'Wait for actual independent reports; no guessed review completion'
audit={'schema':'ready-armor24-postfix-checkpoint-v1','time':datetime.datetime.now().astimezone().isoformat(),
 'actual_automation_report':desc(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-111515/index.json'),
 'actual_full_success':126,'old122_names_preserved':True,'snapshot':desc(S/'compiled-source-manifest.json'),
 'snapshot_files':1399,'snapshot_bytes':manifest['bytes'],'endpoint_size_SHA_checks':2798,'mismatches':0,
 'captured_Source_DLL_unchanged':True,'actual_observations':174,'native_PNGs_including_prewarm':175,
 'actual_capture_duration_s':runtime['capture_timing']['requested_video_wall_duration_s'],
 'visible_head_gate_Ready_observations':137,'visible_head_gate_failures':0,'failed_v001_preserved':desc(BAD/'原件/visible-ready-head-gate-v001.json'),
 'root_whole_frame_indices':[0,5,6,7,8,9,10,15,16,17,18,19],
 'root_unscaled_crop_indices':[6,7,8,9,16,17,18,19],
 'browser_actual_sample_seconds':[.27303,5.833333],'browser_duration_s':5.833333,
 'browser_sampled_playback_only':True,'full_framewise_motion_accepted':False,'audio_recorded':False,
 'reviews':[desc(p) for p in reviews],'armor_fits_attacks':False,'real_equipment_ID_binding_complete':False,
 'formal_complete_units':0,'goal_status':'active'}
new(E/'actual-postfix-v101-audit-v001.json',audit)
review='''# 钟盔军剑低位胸肩试装：实际运行检查点

2026-10-16，继续落实用户EV-048“保持怪诞方向，增强盔甲和轮廓辨识”。当前结果为持剑待机试装，身体最高72px、UI隐藏。完整首批内容目标仍active，正式完成0/15。

## 事实

native158四帧低位持剑身体、159六帧首斩已独立导入；161修正胸片、162近肩和163远肩经测量后仅做整数位置注册，另导入12甲片＋12原身体分区Texture2D。旧917包不变，当前Production941。实际栈为BodyRest→远肩→胸片→不含手的近臂→近肩→独立军剑→近手，仅StableIdle四相使用；首斩及其他状态没有伪套待机甲。远肩没有生成原指定中央boss，当前采用明确另列的真实顶带铆钉试装设计，原要求保持未通过。

首次v100试录虽通过输入、资源对象与绘制栈校验，实际右Ready1/2/3首用帧只剩剑。root与独立评审均确认，137个Ready观测的可见头部门实际3失败。失败原件、视频、v100源码和说明更正保持留档。修复在启动预载全部24张纹理，等待这24张的编辑器编译及已有渲染flush，并拒绝初始化尚未完成的资源；没有延长预热、修改5.8秒试录要求或按键时序。

111349编译成功，111515完整126/126Success，零失败/警告/未运行/进行中，旧122名称保留。v101冻结1399文件、86,161,824字节；主目录与冻结目录2798次大小/SHA核对零差。新进程真实Enter/A/J录制5.8077535秒、174观测/175原生PNG含预热，左右Ready4和首斩6相全部出现，实际战斗相位取帧、甲栈、全部CRC与异步flush通过。137个Ready观测可见头部门全过，最小暖色盔像素376。无声视频完整解码通过。

root实际看12张完整新帧和8张未放大局部，覆盖左右全部Ready及首斩起/收；独立修复后审图另见[报告](evidence/sword-armor-ready-v001/independent-native-frames-review-v002.md)。浏览器实际读取1280×720/5.833333秒，在0.27303秒播放中和结尾采样，未声称逐帧连续动作验收。

## 推理

原先消失的三个首用帧已恢复，当前限定试样的首次绘制故障关闭。胸肩亮面使躯干更像盔甲冒险者，低位剑保持盔和眼窗可见；近肩外沿扩张仍克制，远肩在72px下主要呈小亮块，不能据此认定整体轮廓目标最终达标。

## 风险与下一步

当前出手会卸下待机甲、收回后再穿上，亮面与肩宽会突变。领口/肩带邻近盔沿、腹前剑和腕线的小像素叠合仍待改；未接受零穿插、手指咬合、脚锁或完整连续动作。接下来优先补首斩匹配的胸肩动作与分层，再做第二/三段连招、走跑/受击/死亡等状态，最后核实际装备ID、获取/保存和20搭配。内存暂停恢复已验证，磁盘codec、新进程Continue与音效试听仍待；不以本试装替代这些验收。

标准sprite工具源预览忽略请求时长的缺陷仍保留：首斩源预览6×100ms，游戏真实相位85/85/60/60/155/155ms；未靠本地重定时伪装源动作完成。所有新媒体展示前F/E保全；E164失败、E165修复后实录和E166播放页均独立留档，不覆盖旧版。

手动双击[F:/Ourgame/钟盔军剑胸肩试装.cmd](F:/Ourgame/钟盔军剑胸肩试装.cmd)可看当前候选，Enter开始，A/D换向、J攻击；新甲目前仅待机，其他状态有占位。本入口静态解析通过，未另外手动启动；自动录制已实际验证相同呈现flag。
'''
new(D/'runtime-review-fairytale-sword-armor-ready-v002.md',review)
# Working status documents are mutable; preserve their complete prior bytes first.
before=E/'status-before-checkpoint-v101';assert not before.exists();before.mkdir()
for name in ['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']:
 p=R/name;t=before/Path(name).name;shutil.copy2(p,t);assert desc(p)['sha256']==desc(t)['sha256']
summary='''2026-10-16当前：怪诞钟盔低位持剑待机已实际穿回胸甲与双肩，身体最高72px、UI隐藏。24新分层纹理实际导入/保存，旧917包不变、Production941；仅待机四相有甲，攻击甲与全状态尚未完成。首用帧消失的v100失败已留档，启动预载修复后v101真实双向Enter/A/J录制及137待机头部存在检查通过，原生175PNG/相位/甲栈/解码过。111349编译0、111515完整126回归全过；v1011399文件两端2798大小/SHA零差。正式完整0/15，目标active。

[当前实景、已知边界与下一步](docs/production/first-batch-v2/runtime-review-fairytale-sword-armor-ready-v002.md)。手动入口：[钟盔军剑胸肩试装.cmd](钟盔军剑胸肩试装.cmd)。

| 当前资源 | 实际接入 | 剩余适配 |
| --- | --- | --- |
| 低位持剑身体4帧／首斩身体6帧 | native158/159、左右真实按键取帧 | 连招二/三段及走跑/空中/受击/死亡等 |
| 胸片／近肩／远肩各4帧 | native161/162/163，12甲纹理；另12身体互斥层 | 只覆盖待机，出手卸甲；未绑定实际装备ID |
| 新媒体 | E165实录、E166播放页，F/E两遍SHA零差 | 无声、静帧＋播放采样；未接受完整动效/声音 |

此前检查点（历史）：'''
for name in ['README.md','AGENTS.md']:
 p=R/name;oldtext=p.read_text(encoding='utf-8-sig');first,sep,rest=oldtext.partition('\n\n此前检查点（历史）：')
 assert sep, name
 p.write_text(summary+rest,encoding='utf-8')
p=D/'progress.json';d=load(p)
d.update(current_task='EV048 lowguard and Ready-only chest/shoulders actual941packages; first-use invisible frames fixed by preload, actual126GREEN/v101 and real-J137Ready visible gate pass. Full armor/allstates/combos/audio/equipment/diskContinue remain; formal0/15, goalactive.',
 current_build='UnrealGame/Saved/Bootstrap/build-editor-20261016-111349.log',current_build_exit_code=0,
 current_compiled_snapshot=S.relative_to(R).as_posix(),ue_current_working_source_verified=True,ue_current_working_source_compiled=True,
 current_source_uncompiled_changes=None,actual_registered_test_count_current=126,
 next_native_request=164,next_snapshot='v102',next_retention_batch='E168',next_human_event='EV-049',
 current_turn_progress_classification='EV048 continuation; no new human event. Actual visible first-use RED→preload→same input GREEN plus limited Ready-only armor lookdev, fullgoalactive0/15.')
d['latest_strict_UE_automation']={'report':'UnrealGame/Saved/Automation/FirstRoom-20261016-111515/index.json','registered':126,'succeeded':126,'failed':0,'notRun':0,'inProcess':0,'warnings':0,'old122_registration_names_preserved':True,'scope':'Compiled startup preload and existing full registered regression; no art acceptance','formal_complete_units':0}
d['generation_accounting_current']={'requested_count':163,'window_number':7,'window_requested_count':19,'window_limit':24,'remaining_in_window':5,'lifetime_requested_count':187,'external_api_calls':0,'fee_unknown':True}
d['latest_visual_runtime_proof']={'version':'SwordArmorReady-v002','archive':A.relative_to(R).as_posix(),'snapshot':'v101','runtime_checks_passed':True,'Ready_visible_observations':137,'Ready_visible_failures':0,'capture_duration_s':runtime['capture_timing']['requested_video_wall_duration_s'],'observations':174,'original_PNGs':175,'retention':'E165','player_retention':'E166','review':'docs/production/first-batch-v2/runtime-review-fairytale-sword-armor-ready-v002.md','root_whole_views':12,'root_unscaled_crop_views':8,'full_framewise_motion_accepted':False,'complete_equipment_accepted':False,'audio_recorded':False}
d['current_retention_batches']=[f'E{i}' for i in range(138,168)]
d['current_turn_media_retention']={'latest_runtime':'E165','player':'E166','review_capsule':'E167_pending_copy','two_pass_size_SHA_mismatches':0,'root_README_unchanged':True,'not_acceptance':True}
d['fairytale_sword_low_guard_v002'].update(status='158Ready4/159Primary1six actual10imported and real-J bothfacings verified; measured actualgrips/designaxes used, fullmotion/thumb/allstates unaccepted',actual_grip_measured=True,actual_game_rendered_v002=True,retention=['E139','E140','E141','E142','E144','E145','E149','E150','E159','E161'])
d['fairytale_sword_armor_ready_v001']={'source_requests':[161,162,163],'new_Texture2Ds':24,'old917_unchanged':True,'Production_packages':941,'onlyStableIdle4':True,'actual_equipment_ID_binding':False,'attack_armor_fit':False,'failed_trial':'E164/v100 actual3Readyframes invisible','postfix_trial':'E165/v101 actual0of137invisible','source_snapshot_audit':audit,'formal_complete_units':0}
d['next_work']=d['next_turn_priorities']=['Match chest/shoulders and body partition to actual159Primary1 six phases; remove visible armor on/off discontinuity without reusing Ready parts on attacks','Continue new style fullstates/three-stage melee and actual armor IDs/20equipmentmix; maintain72px/UIhidden and clear helmet/hand silhouettes','Complete remaining enemies/Boss/actions/VFX/SFX/acquisition/rewards and disk codec/new-process Continue; preserve fullgoal0/15 until actual acceptance']
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n| 2026-10-16；EV-048续行，无新增人类事件 | 盔甲与轮廓辨识 | 158低位4/159首斩6真实双向，161胸片/162近肩/163远肩＋身体分区24纹理实际导入，保持72px无UI；v100首用角色消失3帧失败保留，v101预加载修复后137待机观测0失败，126回归过。 | 仅待机甲试装；攻击甲、全状态、20搭配/音效/磁盘Continue仍待。见[实际复核](docs/production/first-batch-v2/runtime-review-fairytale-sword-armor-ready-v002.md)。正式0/15，目标active。 |\n')
with (R/'.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 EV048 continuation: 158Ready4+159Primary1six imported10/old907 and actualv099 normalJ proven. 161/162/163 Ready-only armor12+exclusive body12 imported24/old917; Production941. Actualv100 metaGREEN but nativevisible3ReadyfirstuseRED retainedE164. Startup24preload+targetedtextureCompileWait+existingrenderflush, Initializedgate:111349build0→111515full126GREEN. v1011399files86161824B/2798twoendSHA0, same5.8s Enter/A/J freshprocess174obs175PNG,137Readyheadpresence0fail/min376, bothsides4/6/nativeCRC/flush/decode. E165runtime/E166player. Root12whole8unscaledcrop and browser.27303/end5.833333 sparse playback, nofullmotion/audio/armorattack/equipmentclaim. Formal0/15goalactive; diskContinue still open. Next match159six-phase armor, then remaining allstates/combos/enemies. nextnative164/E168/v102/humanEV049.\n')
print(json.dumps({'report':desc(D/'runtime-review-fairytale-sword-armor-ready-v002.md'),'audit':desc(E/'actual-postfix-v101-audit-v001.json'),'snapshot_endpoints_checked':2798,'mismatches':0,'formal_complete_units':0,'goal_status':'active'},ensure_ascii=False))
