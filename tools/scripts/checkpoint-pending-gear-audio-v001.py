"""Record the actual pending-gear RED/GREEN and current 144-test audio milestone."""
from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
O=D/'evidence/pending-gear-native-v001/final-checkpoint-v001'
RED=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v003-pendingRED'
GREEN=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v004-pendingGREEN'
PLAYER=R/'过程图稿与视频/2026-10-16_换装装备保持播放复核_v001'
SNAP='source-assets/production/backups/2026-10-16_PendingGear-MeleeAudio-full144GREEN-beforeNative-v121'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def freeze(p):
 v=read(p)
 for row in v['files']:
  x=desc(R/row['path']);assert x['bytes']==row['bytes'] and x['sha256']==row['sha256']
 return desc(p)
assert not O.exists()
red=read(RED/'原件/runtime-report.json');green=read(GREEN/'原件/runtime-report.json')
proof=read(GREEN/'原件/independent-bound-flow-verification-v001.json')
source=read(GREEN/'原件/source-and-snapshot-binding-verification-v001.json')
assert red['flow_complete'] and not red['reason'] and not red['passed'] and len(red['mismatches'])==6
assert green['flow_complete'] and not green['reason'] and green['passed'] and not green['mismatches']
assert green['light_primary_phase_masks']==[63]*3 and proof['operations_committed']==3
assert proof['observations']==140 and proof['original_PNGs']==141 and proof['pending_identity_placeholder_observations']==33
assert source['snapshot_files']==1268 and source['endpoint_checks']==2536 and source['mismatches']==0 and source['current_full_automation_succeeded']==144
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-215505/index.json';v=read(report)
assert v['succeeded']==144 and len(v['tests'])==144 and len({x['fullTestPath'] for x in v['tests']})==144
assert all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in v['tests'])
assert all(v.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
audio_tests=[x['fullTestPath'] for x in v['tests'] if '.MeleeAudioJournal.' in x['fullTestPath']];assert len(audio_tests)==3
audio_red=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-214936/index.json';av=read(audio_red)
assert av['failed']==3 and av['succeeded']==0 and all(x['errors']==2 and x['warnings']==0 for x in av['tests'])
manifest=read(R/SNAP/'compiled-source-manifest.json');assert manifest['copied_files']==1268 and manifest['bytes']==86390215 and manifest['current_automation_succeeded']==144
old=read(R/'source-assets/production/backups/2026-10-16_PendingGear-nativeRED-beforeConsumer-v119/compiled-source-manifest.json')
probe='UnrealGame/Source/CodexDungeon/DungeonFairytaleEquipmentBoundProbe.cpp'
assert next(x for x in old['files'] if x['path']==probe)==next(x for x in manifest['files'] if x['path']==probe)
art=freeze(D/'evidence/pending-gear-native-v001/independent-native-art-review-v001/review-freeze-v001.json')
consumer=freeze(D/'evidence/pending-gear-native-v001/independent-consumer-review-v001/review-freeze-v001.json')
audio=freeze(D/'evidence/melee-audio-journal-execution-v001/independent-production-review-v001/review-freeze-v001.json')
assert art['sha256']=='b6ec3c998811d75fe2acbc934c8688f5de7552de9bc3ac633ac715d5658f2777'
retentions={}
for n,name in [(246,'2026-10-16-OurgameUE-pendingGear-nativeRED-v246'),(247,'2026-10-16-OurgameUE-pendingGear-nativeGREEN-v247')]:
 p=Path('E:/OurGame/Knight/过程图稿与视频')/name/'retention-verification-v001.json';x=read(p)
 assert x['verification_passes']==2 and x['source_and_retained_size_SHA_mismatches']==0 and x['E_root_README_unchanged']
 retentions[f'E{n}']=dict(receipt=desc(p),source_files=x['original_source_files'],native_PNGs=x['packed_native_pngs'],original_bytes=x['unpacked_source_bytes'],stored_bytes=x['stored_media_bytes'])
p=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-pendingGear-review-player-v248/source-size-SHA256.json');x=read(p)
assert x['verification_passes']==2 and x['source_and_target_hash_mismatches']==0 and x['file_count']==19 and x['bytes']==1793805
retentions['E248']=dict(receipt=desc(p),source_files=19,bytes=1793805)
ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';lg=read(ledger)
assert lg['requested_count']==178 and lg['current_window']['requested_count']==10 and lg['remaining_batch_requests']==14
ledger_before=desc(ledger)
(O/'before').mkdir(parents=True)
for p in [D/'progress.json',R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']:shutil.copy2(p,O/'before'/p.name)
mg=read(GREEN/'原件/selected-native-source-map-v001.json');mr=read(RED/'原件/selected-native-source-map-v001.json')
keys=['light_pending_cancel','light_pickup_commit','medium_commit','medium_unsupported_ready','original_light_retake_commit','original_light_retaken_ready']
root_current=[next(x for x in mg['frames'] if x['kind']=='flow:'+key) for key in keys]
root_old=[next(x for x in mr['frames'] if x['kind']=='flow:'+key) for key in keys[:3]]
write(O/'root-art-review-v001.json',dict(actually_viewed_current_crops=[x['unscaled_crop'] for x in root_current],actually_viewed_current_wholes=[root_current[i]['source_whole'] for i in [0,2]],actually_viewed_old_crops=[x['unscaled_crop'] for x in root_old],status='NEEDS_WORK',findings=['Pending current NoArmor retains sword without target light armor.','Pending old LGT to MED retains actual LGT and sword until commit.','Committed MED and pending MED to LGT remain unsupported; after retake actual LGT restored.','Pickup still uses Ready0 standing grip, not a completed pickup/armor-change action.','72px whole-view armor/cloth distinction remains weak; chest/shoulder silhouette and value separation are next art priorities.','World source white outline and ground marker placeholders remain.'],formal_complete_units=0))
write(O/'browser-playback-v001.json',dict(tab='16',player=PLAYER.as_posix(),current_start=.236271,current_reset_start=.203355,old_start=.214502,current_end=4.733333,old_end=4.766667,current_ended=True,old_ended=True,readyState=4,hasError=False,videoWidth=1280,videoHeight=720,markDeliverable_called=True,scope='Actual playback progression/decode only; source frames reviewed separately, no continuous-motion/audio acceptance.'))
write(O/'manual-launcher-preflight-v002.json',dict(actual_checker_exit=0,actual_PS_parse_errors=0,snapshot=SNAP,strict_current_tests=144,native_observations=140,binding_flow_mismatches=0,manual_UE_window_launched=False,entry=desc(R/'军剑真实装备绑定试玩.cmd'),launcher=desc(R/'tools/scripts/launch-fairytale-equipment-bound-v002.ps1'),checker=desc(R/'tools/scripts/verify-equipment-bound-current-build-v002.py')))
doc=D/'runtime-review-pending-gear-audio-v001.md';assert not doc.exists()
doc.write_text('''# 换装装备保持与近战声音事件：v121 当前检查点

事实：新增原生期望先原样准入，实际v119完整普通输入流程141观察/142原PNG正常结束，但出现6项pending缺剑/缺甲RED。两文件局部生产修正后，完全相同Probe/输入/期望实际再跑，140观察/141原PNG、4.668312秒、33个合法pending观察，三个提交和原轻甲同实例重拾均走完、三段六相mask63×3，0错。帧数自然随墙钟而变，未重时或用固定步长凑数。MED外观仍明确unsupported，当前实景只有PickupArmor，PickupWeapon并未获得原生证据。

推理：pending期间以本次唯一Resolve所得的已提交装备决定剑甲；目标装备未提交不选皮。Supported及ActionPoseSupported仍表示动作真值false，GearPlaceholder只开放地面安全条件下的真实合法Pickup，借用Ready0/frame0维持身份。MED、其它未支持动作保持封闭，非Bound旧路径保持。此修正不等于制作了拿取/穿甲动作。

近战声音：三组测试在215505当前全144报告中全Success。先在214936实际3Fail，各仅SWD首个正例的fact/request为0两项错误；不能说后两族已取得RED。修正后各测试才走完军剑/重剑/长枪的三段普通攻击、技能1/1/3独立窗口、被打断旧出手静音和恢复后的新出手。真实公共Enter/E/J/K与GameMode/HUD消费者、内核合法窗口、声音路径/身份/时刻/gain.25和重复更新不重放均受检查。Bound旧直接播放移除，转既有journal；unbound原型路径和旧五cue保持。测试音频设备关闭，此项是事件/播放请求证据，不是扬声器音色或混音验收。

当前build-editor-20261016-215341.log exit0；FirstRoom-20261016-215505严格144/144，唯一144项全Success、errors/warnings/failed/notRun/inProcess为0。v121快照1268文件86390215字节，实际Source与快照2536端点0差，1085 Production包与v116全保持；本轮未生成或重画资源。

审图：Root实际看当前6裁图+2整景与旧3裁图，独立同样6+2与旧3；选定文件/ZIP成员/原ROI核验无差。拾取原剑与旧轻甲持续显示的改善可见；整景72px的胸肩灰甲与灰衣差异仍弱，下一步优先强化胸肩外轮廓和明暗分区。保持钟盔怪诞方向、身高72px上限、剑.50、传统HUD隐藏；世界白框和地面标记尚为占位。当前完整拿取/换甲/走跑跳伤亡、另一完整攻击朝向、握姿轨迹、全部20组合/敌人/Boss/VFX/SFX及15辅助依赖都继续推进，正式完整仍0/15 active。

留档：E246保留RED192源项/142原PNG，E247保留GREEN191源项/141原PNG；原PNG完整文件字节以无损ZIP保存，两遍解包大小/SHA0差、F原件不变。E248播放器19项1793805B两遍核验0差。浏览器两片实际播完，当前4.733333秒、旧4.766667秒，无视频错误；CFR30展示量化/尾帧重复不改变游戏时钟和源图。静音录像不能证明本轮声音听感。

失败也保留：Windows PowerShell5误读UTF8无BOM中文路径导致第一次捕获工具失败，切换pwsh后成功，前者不算功能RED。音频候选测试直接读private HurtTime导致214814编译exit6，保存before/log后只换为公开hurt动画观察，214912编译0，之后才有真实3RED。Root两个生产hunk重生原生换行transport，普通git apply--check/apply0，没有放宽测试或改Probe期望。

可用入口 F:/Ourgame/军剑真实装备绑定试玩.cmd 已切v002/v121并实际预检0/PS解析0，本轮未另开人工试玩窗口。内置请求178、窗口10/24余14、累计202、下一179；本轮新图像0、外部API0，历史内置费用未知。EV048续行，无新人类要求事件。所有历史稿和检查点保留。
''',encoding='utf-8')
m=read(D/'progress.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
m['previous_visual_runtime_proof_before_pending_gear']=m['latest_visual_runtime_proof']
m['current_task']='EV048: v121 full144strictGREEN and same native pending6RED→0GREEN; Ready0 retains committed gear in33 actual armor-pickup observations. Melee audio3cleanRED→3GREEN within full144. Art NEEDS_WORK; next chest/shoulder silhouette and action poses. formal0/15active.'
m['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261016-215341.log';m['current_build_exit_code']=0;m['latest_build_attempt']=m['current_build'];m['latest_build_attempt_exit_code']=0
m['previous_compiled_snapshot_before_pending_gear']='source-assets/production/backups/2026-10-16_MeleeAudio-3cleanRED-beforeProduction-v120'
m['current_compiled_snapshot']=SNAP;m['current_compiled_snapshot_files']=1268;m['current_compiled_snapshot_bytes']=86390215;m['current_snapshot_pending']=None
m['ue_current_working_source_compiled']=True;m['ue_current_working_source_verified']=True;m['current_source_uncompiled_changes']=None
m['current_source_verification_scope']='Current144 strictGREEN/2536 frozen endpoints plus actual140obs141PNG pending identity0mismatch. Does not accept full pickup motion, device audio or complete units.'
m['latest_strict_UE_automation']=dict(report=report.relative_to(R).as_posix(),succeeded=144,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
m['latest_visual_runtime_proof']=dict(report=desc(doc),archive=GREEN.as_posix(),capture_snapshot=SNAP,video=desc(GREEN/'展示副本/equipment-bound-flow-green-silent.mp4'),observations=140,original_PNG_including_prewarm=141,duration_s=green['duration_s'],uniform_weapon_scale=.5,body_max_px=72,root_whole_views=2,root_unscaled_crop_views=6,independent_whole_views=2,independent_unscaled_crop_views=6,independent_review_freeze=art,actual_transaction_mismatches=0,actual_committed_operations=3,pending_committed_gear_observations=33,actual_weapon_pickup_proven=False,art_review_status='NEEDS_WORK',audio_recorded=False,full_motion_accepted=False,formal_complete_units=0)
m['fairytale_sword_equipment_binding_v001'].update(native_binding_draw_proof=desc(GREEN/'原件/runtime-report.json'),current_native_transaction_mismatches=0,current_fullGREEN=144,scope='Valid current SWD+None/LGT retains gear during actual armor Pickup using explicitly unsupported Ready0 placeholder. MED unavailable; full pickup/equip motion/otherstates and native WeaponPickup not accepted.')
m['pending_equipment_gear_retention_stage0'].update(production_patch_applied=True,actual_native_GREEN=desc(GREEN/'原件/runtime-report.json'),actual_native_RED=desc(RED/'原件/runtime-report.json'),same_native_probe_and_expectations=True,production_admission=desc(D/'evidence/pending-gear-native-v001/production-admission-v001/admission.json'),independent_source_review=consumer,actual_placeholder_observations=33,action_pose_accepted=False)
m['pending_melee_audio_candidates'].update(actual_Source_applied=True,actual_RED=desc(audio_red),actual_GREEN=desc(report),actual_tests=desc(R/'UnrealGame/Source/CodexDungeon/Tests/DungeonMeleeAudioJournalIntegrationTests.cpp'),admitted_patch=desc(R/'source-assets/production/melee-audio-journal-integration-v001/rebase-v002/production-rebased-final-v002.patch'),independent_source_review=audio,device_audio_audition=False)
m['latest_native_review_player']=PLAYER.relative_to(R).as_posix();m['latest_native_review_browser_playback']=desc(O/'browser-playback-v001.json');m['latest_primary3_manual_launcher_preflight']=desc(O/'manual-launcher-preflight-v002.json');m['latest_equipment_bound_manual_launcher_preflight']=m['latest_primary3_manual_launcher_preflight']
m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+['E246','E247','E248']))
m['current_turn_media_retention'].update(latest_runtime='E247',player='E248',pending_gear_RED='E246192sourcefiles142PNGZIP/2SHA0',pending_gear_GREEN='E247191sourcefiles141PNGZIP/2SHA0',pending_gear_player='E24819files1793805B/2SHA0')
m['next_retention_batch']='E249';m['next_snapshot']='v122';m['next_native_request']=179
m['next_work']=['EV048 art priority: strengthen readable chest/shoulder armor silhouette and light-dark separation at72px while preserving grotesque bell helmet and scene/body scale; current gray cloth/armor distinction weak.','Replace Ready0 identity placeholders with true equip/pickup and locomotion/air/hurt/death/skill poses; complete other facing/20 weapon-armor pairings, grasp/trajectory and real weapon-pickup proof.','Actual native audio device/mix/impact/material feedback and remaining enemies including stone bat wing. Current144 proves event/request correctness, not listening.','Implement actual STN003/004/GOB001/Boss AI/reward/owner codec and all assets/VFX/SFX, get/equip/drop/save and15 auxiliary dependencies; full5weapons4armors5enemiesBoss scope retained.']
m['current_turn_progress_classification']='progress: actual two-file pendingGear native6RED→0GREEN plus three-file meleeAudio3cleanRED→full144GREEN, real140obs141PNG33placeholder observations, actual art review. Not full-unit completion.'
m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=now;write(D/'progress.json',m)
header='''2026-10-16 当前检查点（EV048，v121）：保持怪诞钟盔和小比例；拾取中军剑、原轻甲不再临时消失。当前144/144严格通过，真实同流程pending6项RED→0GREEN，140观察/141原PNG、33个合法装备保持观察。军剑/重剑/长枪声音事件与一次播放请求接入通过，音色和混音尚待试听。[本轮实景复核](docs/production/first-batch-v2/runtime-review-pending-gear-audio-v001.md)。

| 当前资源 | 已验证 | 仍需制作 |
| --- | --- | --- |
| 换装时的剑与轻甲 | 当前已提交装备在拾取进行中保持；取消/三个提交/原轻甲同实例重拾 | 目前借用Ready0持剑站姿；完整拿取/穿甲动作及中甲外观 |
| 三近战声音 | 普通三段、技能独立出手、被打断出手及重复消费检查 | 实际音色/混音、材料命中和全敌人声音 |
| 当前美术 | 保持钟盔、72px、剑.50；传统HUD隐藏 | 胸肩灰甲与衣服整景差异弱，优先加强轮廓/明暗；世界拾取白框仍占位 |

[打开当前试玩](军剑真实装备绑定试玩.cmd)。v121快照1268文件/2536端点0差，E246/E247原PNG以无损ZIP留档并两遍核验，E248播放器已保留并播完。录像静音；正式完整单元仍0/15、目标active，5武器/4甲/5敌/Boss、20组合、全状态/特效/音效/获取掉落存续及15依赖范围不变。无新图像生成：请求178/窗口10of24余14/累计202/下一179、外部API0。以下旧检查点按历史保留，以本段及progress当前字段为准。

'''
for p in [R/'README.md',R/'AGENTS.md']:p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 EV048续行，无新人类事件：v119pending6真实RED→v121原Probe/期望/输入0GREEN（140obs141PNG/33合法pending）。当前Source build215341exit0/full215505严格144GREEN，三近战audio3cleanRED→3GREEN包含full144，仅事件/请求非音色验收。保持72px/剑.50/怪诞钟盔，Ready0仅装备身份占位而非完整换装，中甲/胸肩辨识/世界白框/全状态仍待。E246/E247两遍无损原件SHA0、E24819项1793805B播放器播完；Source1268files2536端点0。正式0/15active、完整scope不缩；生成178/window10/rem14/next179不变。本轮新图像0。\n')
assert desc(ledger)==ledger_before,'No generation ledger/quota changes were authorized by this no-generation checkpoint'
write(O/'checkpoint.json',dict(after=[desc(p) for p in [D/'progress.json',doc,R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']],generation_ledger_unchanged=ledger_before,retentions=retentions,current_native=desc(GREEN/'原件/runtime-report.json'),current_automation=desc(report),same_probe_RED_GREEN=True,root_art_review=desc(O/'root-art-review-v001.json'),independent_art_review=art,independent_consumer_review=consumer,independent_audio_review=audio,formal_complete_units=0,goal_status='active'))
print(json.dumps(dict(current_snapshot='v121',strict_tests=144,actual_native_observations=140,actual_original_PNGs=141,pending_kept_observations=33,transaction_mismatches=0,art='NEEDS_WORK',formal_complete_units=0,goal_status='active',next='Armor chest/shoulder silhouette and full action poses'),ensure_ascii=False))
