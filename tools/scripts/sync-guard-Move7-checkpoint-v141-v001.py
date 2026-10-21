"""Sync durable status only after native review and actual normal v012 validation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
BASE=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-checkpoint-v001'
O=BASE/'current-status-sync-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=BASE/'Root-GuardMove7-native-and-visible-review-v141-v001.json';v=read(review)
adoption=BASE/'manual-adoption-v012-v001/adoption-receipt-v001.json';ad=read(adoption)
assert v['limited_manual_trial_allowed'] and v['both_complete_silent_videos_viewed'] and not v['FinalAccepted'] and ad['success']
cmfile=R/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json';cm=read(cmfile)
assert (cm['source_files'],cm['production_files'],cm['passed'],cm['failed'])==(283,1371,200,0)
rows=[x for x in cm['files']if x['path'].startswith(('UnrealGame/Source/','UnrealGame/Content/Production/'))or x['path']=='UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll']
assert len(rows)==1655
for repeat in range(2):
 for x in rows:
  a=pin(R/x['path']);assert (a['bytes'],a['sha256'])==(x['bytes'],x['sha256'])
retentions=[]
for n in range(574,581):
 matches=list(E.glob(f'2026-10-18-本项目E{n}-*/E-retention-index-v001.json'));assert len(matches)==1
 q=matches[0];d=read(q);assert d['verification_passes']==2 and d['source_and_member_hash_mismatches']==0;retentions.append(pin(q))
paths=[R/'README.md',R/'项目需求台账.md',R/'docs/production/first-batch-v2/progress.json',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json',R/'docs/superpowers/plans/2026-10-18-guard-move7.md']
assert not O.exists();O.mkdir(parents=True)
before=[]
for p in paths:
 before.append(pin(p));q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
lp=paths[3];ledger=read(lp);assert (ledger['requested_count'],ledger['batch_requested_count'],ledger['remaining_batch_requests'],ledger['lifetime_requested_count'],ledger['external_api_calls'])==(252,12,12,276,0)
delivery=dict(id='guard-Move7-native-v141',type='bounded_native_derived_component_trial',review=pin(review),compiled_snapshot=pin(cmfile),source_native_ids=[252,250,251],imported_textures=7,resident_textures=7,draw_slots=7,strict_tests=200,native_sides=[-1,1],formal_complete_units=0,complete_combinations=0,FinalAccepted=False,generation_calls_this_turn=0,retention=retentions)
assert not any(x.get('id')==delivery['id']for x in ledger['derived_deliveries']);ledger['derived_deliveries'].append(delivery);write(lp,ledger)
status=dict(version='v141-GuardMove7-native-reviewed',Source=283,Production=1371,registered_tests=200,failed_tests=0,all_tests_green=True,source_compiled=True,source7_actual_imported=True,rig_runtime_implemented=True,native_verified=True,manual_current_checkpoint_ready=True,compiled_snapshot=pin(cmfile),review=pin(review),manual_adoption=pin(adoption),source_and_DLL_and_Production_1655pins_verified_twice=True,
 native_left=dict(PID=47360,frames=448),native_right=dict(PID=42880,frames=478),draw_slots=7,distance_cycle=128,six_distance_windows=True,
 visible_polish_needed=v['visible_polish_needed'],remaining_scope=v['remaining_scope'],formal_complete_units=0,completed_combinations=0,goal_status='active',FinalAccepted=False,generation_calls_this_turn=0,external_API_calls=0,last_E=580,next_E=581,next_image_request=253)
write(O/'status-v001.json',status)
p=paths[2];d=read(p)
d.update(updated_utc=datetime.now(timezone.utc).isoformat(),current_task='v141 守卫七件Move已真实接入：Source283/Production1371/full200，两侧真实AI距离步态/入战/回待机、GPU源像素及静音录像审阅通过；八入口升级v012。继续膝靴/旧姿态衔接、主角空中状态、完整VFX/SFX与剩余首批单位',goal_status='active',completed_content_units=0,
 current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-225000.log',latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261018-225000.log',current_build_exit_code=0,latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,
 current_compiled_snapshot='source-assets/production/backups/v141-GuardMove7-Observer200G-v003',current_compiled_snapshot_files=len(cm['files']),current_compiled_snapshot_bytes=sum(x['bytes']for x in cm['files']),last_fully_green_checkpoint='v141-GuardMove7-Observer200G-v003',
 current_production_packages=1371,production_package_count_actual=1371,production_uasset_package_count_actual=1371,ue_actual_total_production_files=1371,production_texture_count_actual=None,production_texture_counts_by_group=None,production_texture_count_scope='1371实际Production包；7新增Texture2D源/设置原生读回，旧1364 unchanged。全树class总数本轮未重算。',actual_registered_test_count_current=200,
 current_status_authority=pin(O/'status-v001.json'),current_source_verification_scope='Current283Source+DLL+1371Production1655pins twoSHA0; full200; exact five Move source admissions; two real native/GPU/quad/pixel/CRC proofs; inherited v011 complete manual gates and current v012 validation.',current_review='保留七件Guard步态有限可玩试样；膝靴拥挤与走路/旧攻击身形跳变仍需精修，非完整单元或声音验收。',current_turn_progress_classification='GuardMove7实际接入且双侧原生审阅，完整首批目标继续',
 current_snapshot_pending=None,next_snapshot='Fresh actual source/content snapshot and required checks after next implementation.',next_native_request=253,next_retention_batch='E581',next_media_retention_batch='E581',next_E_retention_number=581,current_turn_media_retained=True,
 latest_native_review_player='Move7静音左右完整1x播放至ended，14.901204/15.904014秒；六窗口与两组相邻接续原尺寸审阅，E574-580先保全。',current_guard_room_manual_trial=pin(adoption),current_manual_launcher_v012=pin(adoption),latest_visual_runtime_proof=pin(review))
d['guard_Move_v141_work_in_progress']=status;d['current_Guard_Move7_runtime_v141']=delivery
d['previous_current_retention_batches_before_v141']=d.get('current_retention_batches');d['current_retention_batches']=d['current_turn_media_retention']=retentions
d['latest_strict_UE_automation']=dict(report=cm['full_suite'],succeeded=200,failed=0,warnings=0,notRun=0,inProcess=0,actual_registry=200,scope='原196字节不变＋四新Move测试；合法出生方向一字节修正后四真RED→GREEN，原失败保留。')
d['latest_targeted_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261018-223916/index.json',succeeded=4,failed=0,scope='Four frozen Move semantic groups')
foundation=d['completed_foundation_checks'];foundation.update(ue_latest_total=200,ue_latest_failed=0,ue_latest_changes_verified=True,ue_latest_report=cm['full_suite']['path'],ue_current_working_source_verified=True)
d['guard_Move_v140_source_preparation'].update(actual_imported=True,actual_runtime_implemented=True,current_scoped_review=pin(review),FinalAccepted=False)
d['next_work']=d['next_turn_priorities']=['Refine Guard passing knees/boots and Rest-to-old-combat torso/hip shape continuity; native Hurt/Stun/turn contact and rotated leg outlines remain open.', 'Implement SWD/LGT nonattack rise/apex/fall/real landing using original height/verticalVelocity/LandingVisualAge and original game timings; current air still bareReady0.', 'Complete actual VFX/SFX audible evidence and remaining first-batch gear/enemies,20 combinations and acquire/drop/save requirements.']
write(p,d)
header='''2026-10-18 当前检查点（EV048，v141）：石像守卫七件行走已真实接入，左右追近→停步挥斧→回待机的实际运行与源像素核验通过，完整200项检查通过。小比例、怪诞盔甲轮廓和隐藏HUD保持。[行走试玩](裂岩守卫行走试玩.cmd) · [实景记录](docs/production/first-batch-v2/runtime-review-guard-Move7-v141.md)。

| 内容 | 已核实 | 仍需完成 |
| --- | --- | --- |
| 守卫行走资产 | Rest252＋Near250/Far251，共7个真实导入组件；全7驻留/绘制、实际距离128周期和单次镜像 | 膝靴交错拥挤、旧攻击/待机身形衔接精修 |
| 实际运行 | 左448／右478原生帧与完整解码帧一致；6距离窗口、2组真实相邻回接；完整静音播放及原像素审阅 | 转向/Y接地、普通Hurt/Stun衔接、足锁和声音 |
| 构建与试玩 | Source283／Production1371／200项严格通过；八个v012手动入口，无自动输入或诊断伤害 | 正式完整0/15、完整搭配0/20，目标active |

操作：Enter开局，E穿甲／交互，WASD移动，J攻击，Shift闪避，Space跳跃，R重开。实录前置Knight/Bat有明确诊断清理，不能算整房手动通关或音效验收。旧失败原件与核验工具版本全部保留；E574–580展示前两SHA保全。本轮无图像生成，当前请求252／窗口11用12余12／累计276（另最初3张），外部API0。下方均为历史检查点。

'''
paths[0].write_text(header+paths[0].read_text(encoding='utf-8-sig'),encoding='utf-8')
with paths[1].open('a',encoding='utf-8')as f:f.write('\n\n2026-10-18 EV048持续实施／v141：Guard七件Move真实导入并接入，Source283／Production1371／完整200严格GREEN。左右实际AI追近128距离六窗口、25次合格Move绘制、7资源/同quad/sourcepixels/CRC、自然首攻击与同Aid收招回Ready核验通过；448/478原帧完整解码、1x静音播放、原尺寸窗口/接续审阅后保留限定可玩试样，八入口v012。膝靴交错、旧攻击/待机身形跳变仍需精修；转向/Y接地、Hurt/Stun、声音/足锁未完成。首测试fixture越界及首次原生工具numpy标量误拒均永久留档，未放宽几何/像素/时序标准；重新左右实录通过，旧六帧Move闭门与旧196保持。E574–580先双SHA保全。本轮无生成，252／window11用12余12／累计276，外部API0；正式0/15、搭配0/20、目标active，非新需求事件。见[v141实景记录](docs/production/first-batch-v2/runtime-review-guard-Move7-v141.md)。\n')
plan=paths[4];s=plan.read_text(encoding='utf-8');a,b=s.split('### Task4:',1);a=a.replace('- [ ]','- [x]');s=a+'### Task4:'+b
s=s.replace('initial three tests stay byte-identical.','initial three test assertions stay unchanged; the separate one-byte legal-spawn fixture repair is preserved before the genuine semantic RED snapshot.');plan.write_text(s,encoding='utf-8')
doc=R/'docs/production/first-batch-v2/runtime-review-guard-Move7-v141.md';assert not doc.exists()
doc.write_text('''# v141 石像守卫七件行走：有限可玩试样

事实：Rest252／Near250／Far251七个组件已实际导入和接入。Source283、Production1371、完整200项严格通过，旧196测试与旧1364资源保持。使用真实AI接受移动距离、固定128周期、全7驻留原子绘制与单次镜像；其他状态沿用50个既有源。

| 实录 | 左侧 | 右侧 |
| --- | --- | --- |
| 原生进程 | 47360 | 42880 |
| 原帧＝完整解码帧 | 448 | 478 |
| 合格Move绘制／距离窗口 | 25／6 | 25／6 |
| 观察周期距离 | 128.00067 | 128.00067 |
| 回待机回调 | 3 | 3 |
| 完整静音播放 | 14.901204秒 | 15.904014秒 |

推理：真实GPU源像素、绘制参数、左右朝向与自然入战/回接一致；小比例盔甲和斧头保持可辨，行走不再出现灰色占位，保留为可玩试样。Root核对了完整1x播放终态、六窗口及两组原尺寸相邻回调；这不等于逐帧视觉或听感验收。

风险与剩余：膝靴交错拥挤，新的行走身形与旧攻击/待机切换仍偏硬；转向/Y接地、足锁、旋转腿遮挡轮廓与普通Hurt/Stun衔接待补。视频静音，前置Knight/Bat明确诊断清理，不能代替整房手动或完整声音验收。首次源测试出生点越界、原生工具对numpy实数类型的误拒均保留；只修错误表达，原门槛未放宽，fresh左右v002重新验证。

[行走试玩](../../../裂岩守卫行走试玩.cmd) · [左侧完整静音实录](../../../过程图稿与视频/2026-10-18_裂岩守卫七件步态与入战实录审阅_left_v001/展示副本/guard-Move7-native-DIAGNOSTIC-silent-v001.mp4) · [右侧完整静音实录](../../../过程图稿与视频/2026-10-18_裂岩守卫七件步态与入战实录审阅_right_v001/展示副本/guard-Move7-native-DIAGNOSTIC-silent-v001.mp4)

Enter开局，E穿甲/交互，WASD移动，J攻击，Shift闪避，Space跳跃，R重开。v012正常手动入口没有自动输入或诊断伤害。正式完整0/15、搭配0/20，目标继续；本轮无新增图像生成。
''',encoding='utf-8')
receipt=O/'sync-receipt-v001.json';write(receipt,dict(schema='Root-GuardMove7-v141-current-status-sync-v001',utc=datetime.now(timezone.utc).isoformat(),before=before,after=[pin(p)for p in paths],document=pin(doc),status=pin(O/'status-v001.json'),Source=283,Production=1371,full_GREEN=200,Source_DLL_Production_twoSHA0=True,last_E=580,next_E=581,next_image_request=253,formal_complete_units=0,goal_status='active',FinalAccepted=False))
print(json.dumps(dict(receipt=pin(receipt),document=pin(doc),source_files=283,production_files=1371,full_GREEN=200,formal_complete_units=0,next_E=581),ensure_ascii=False))
