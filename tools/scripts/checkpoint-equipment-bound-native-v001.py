from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
O=D/'evidence/equipment-bound-execution-v001/final-checkpoint-v001';assert not O.exists();(O/'before').mkdir(parents=True)
RED=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v001-RED';GREEN=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v002-GREEN'
PLAYER=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定播放复核_v001'
SNAP='source-assets/production/backups/2026-10-16_EquipmentBound-V002-current141GREEN-beforeNative-v118'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
red=read(RED/'原件/runtime-report.json');green=read(GREEN/'原件/runtime-report.json');proof=read(GREEN/'原件/independent-bound-flow-verification-v001.json');audit=read(GREEN/'原件/source-and-snapshot-binding-verification-v001.json')
assert red['flow_complete'] and not red['passed'] and red['reason']=='' and len(red['mismatches'])==6
assert green['flow_complete'] and green['passed'] and not green['reason'] and not green['mismatches'] and green['light_primary_phase_masks']==[63]*3
assert proof['operations_committed']==3 and proof['observations']==141 and proof['original_PNGs']==142
assert audit['snapshot_files']==1267 and audit['endpoint_checks']==2534 and audit['mismatches']==0 and audit['current_full_automation_succeeded']==141
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-204529/index.json';rr=read(report)
assert rr['succeeded']==141 and len(rr['tests'])==141 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in rr['tests'])
assert all(rr.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
review=D/'evidence/equipment-bound-execution-v001/independent-native-art-review-v001/review-freeze-v001.json'
assert desc(review)['sha256']=='1bafbdd39046c4644d51dd4f33576db6824a75848ab8a1f996b0ee1253ca6435'
retentions={}
for n,name in [(242,'2026-10-16-OurgameUE-lossless-original-retention-format-v242'),(243,'2026-10-16-OurgameUE-equipment-bound-nativeRED-v243'),(244,'2026-10-16-OurgameUE-equipment-bound-nativeGREEN-v244')]:
 p=Path('E:/OurGame/Knight/过程图稿与视频')/name/'retention-verification-v001.json';v=read(p)
 assert v['verification_passes']==2 and v['source_and_retained_size_SHA_mismatches']==0 and v['E_root_README_unchanged']
 retentions[f'E{n}']=dict(receipt=desc(p),source_files=v['original_source_files'],original_bytes=v['unpacked_source_bytes'],stored_bytes=v['stored_media_bytes'],native_original_PNGs_in_lossless_ZIP=v['packed_native_pngs'])
p=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-16-OurgameUE-equipment-bound-review-player-v245/source-size-SHA256.json');v=read(p)
assert v['file_count']==17 and v['bytes']==1620454 and v['verification_passes']==2 and v['source_and_target_hash_mismatches']==0
retentions['E245']=dict(receipt=desc(p),source_files=17,bytes=1620454)
mapg=read(GREEN/'原件/selected-native-source-map-v001.json');mapr=read(RED/'原件/selected-native-source-map-v001.json')
phases=['baseline_no_armor','light_pending_cancel','light_canceled','light_ready','medium_commit','medium_unsupported_ready','original_light_retake_commit','original_light_retaken_ready']
viewed=[x for x in mapg['frames'] if (x['kind'].startswith('flow:') and x['flow_phase'] in phases) or x['kind'].startswith('combo:2:')];assert len(viewed)==14
wholes=[x for x in viewed if x['kind'] in ['flow:baseline_no_armor','combo:2:3']];assert len(wholes)==2
redviews=[x for x in mapr['frames'] if x['kind'] in ['flow:baseline_no_armor','flow:light_ready','flow:medium_unsupported_ready','flow:original_light_retaken_ready']];assert len(redviews)==4
write(O/'root-art-review-v001.json',dict(actually_viewed_current_crops=[x['unscaled_crop'] for x in viewed],actually_viewed_current_wholes=[x['source_whole'] for x in wholes],actually_viewed_old_crops=[x['unscaled_crop'] for x in redviews],status='NEEDS_WORK',findings=['Actual no-armor gray shirt vs current LGT and original LGT retake are visible; 72px whole-view distinction remains weak.','P3 raised blade is steeper/less entangled, low tip visibly slightly higher; grasp and full trajectory remain unaccepted.','Pending equip phases use Ready0 with no sword/armor, so committed old gear is not continuously visible.','MED is unsupported placeholder, not an adapted armor.','World pickup white-frame markers remain despite hidden traditional HUD.'],formal_complete_units=0))
write(O/'browser-playback-v001.json',dict(tab='16',player=PLAYER.as_posix(),current_start=0.230738,current_reset_start=0.173946,old_start=0.113599,current_end=4.766667,old_end=4.766667,current_ended=True,old_ended=True,readyState=4,error=None,videoWidth=1280,videoHeight=720,markDeliverable_called=True,scope='Actual playback progression/decode only; no full continuous art or audio acceptance.'))
write(O/'manual-launcher-preflight-v001.json',dict(actual_checker_exit=0,actual_PS_parse_errors=0,snapshot=SNAP,strict_current_tests=141,production_packages=1085,binding_flow_mismatches=0,manual_UE_window_launched=False,entry=desc(R/'军剑真实装备绑定试玩.cmd'),launcher=desc(R/'tools/scripts/launch-fairytale-equipment-bound-v001.ps1'),checker=desc(R/'tools/scripts/verify-equipment-bound-current-build-v001.py')))
doc=D/'runtime-review-equipment-bound-native-v001.md';assert not doc.exists()
doc.write_text('''# 真实装备控制军剑/轻甲画面：v117 RED → v118 GREEN

事实：当前已把一次只读装备解析接到军剑与全部当前甲层。实际旧版本跑完整Enter/E/A/E/J/Enter流程，141观察/142原PNG、4.701078秒，正常结束且流程完整，却在6处将实际无甲/中甲误画为轻甲或军剑。源/快照2526端点零差，这是真实行为RED。最初QA编译漏PlayerInput头导致exit6另留档，不当功能RED。

修正后的同一Probe及期望未改，实际再跑141观察/142原PNG、4.701257秒；三个提交操作、取消后同源重新拾取、中甲替换后原轻甲同实例重拾均走完。轻甲实例2首次提交版本2，重拾为4；三个攻击段各六相mask63，画面与当前资格核对0错误。真实普通输入驱动，QA源注册不等正式掉落/商店完成。

当前build-editor-20261016-204427.log exit0；FirstRoom-20261016-204529实际141/141，全部Success、errors/warnings/notRun/inProcess/failed为0。v118快照1267文件86336418字节，当前与快照2534端点零差；Production包1085与v116全部保持。快照包含全部当前Source/Config/Production、DLL、日志/报告及显式工具/候选引用，不重复复制全部历史准备资料。

推理：无甲不再被旧开关穿上轻甲，中甲不再被替画为轻甲；实际提交的LGT才获得当前胸肩。独立剑的第三刀两轴仅Bound模式从−135°/31.75°调整为−120°/24°，掌、RGBA、72px、剑.50、帧时长未改，旧V001/旧flags路径保留。CPU只能预测重叠减少和低剑尖余量；Root实际看当前14裁图+2整景与旧4裁图，独立看当前19裁图+2整景及旧4对照，实际观感有限改善，未签握姿/全运动。

风险和下一步：正在换装的7/28/107/130等帧仍Ready0无剑无甲，占位使已提交装备暂时消失；不能称整段始终保持旧装备画面。中甲外观未完成；当前三段是单向，另一完整朝向/全状态/20搭配/命中VFX/SFX/敌人/Boss仍待。本次只隐藏传统游戏HUD，世界拾取白框与地面标记仍可见。下一步先补pending装备身份的明确占位保持，再推进准备好的三近战音频测试/接入与全状态美术。

保留：E242为ZIP格式诊断；E243/E244各保留142原PNG的完整文件字节于原件/native-originals.zip，展示裁图和视频为普通副本，全部两遍解包大小/SHA零差，F原PNG不改；约528MB原材料各存为约145MB。E245保留对照播放器17项1620454字节。浏览器两片均播到4.766667秒结束、error空；展示CFR30含尾帧重复，源/游戏时钟未重时。录像静音，不作声音验收。

可运行入口：F:/Ourgame/军剑真实装备绑定试玩.cmd（仅预检实际通过，本轮未另开手动试玩窗口；运行证明来自受控普通输入）。所有人类要求仍记EV048，无新人类事件。内置请求178/当前窗口10of24余14/累计202/下一179，外部API0，本轮新图像调用0；内置历史费用未知。完整目标active、正式完整单元0/15。
''',encoding='utf-8')
P=D/'progress.json';L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
for p in [P,L,R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']:shutil.copy2(p,O/'before'/p.name)
m=read(P);lg=read(L);assert lg['requested_count']==178 and lg['current_window']['requested_count']==10 and lg['remaining_batch_requests']==14
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for row in lg['requests']:
 if row['request_number'] in [175,176,177,178]:
  row['status']='actual_bound_draw_trial_reviewed_NEEDS_WORK_full_unit_pending'
  row.setdefault('review_history',[]).append(dict(time=now,actual_bound_capture=desc(GREEN/'原件/runtime-report.json'),independent_review=desc(review),scope='Current LGT/NoArmor/MED-unsupported transaction binding corrected; same instance retake. Pending equip still strips visible gear/Ready0; full motion/audio/unit not accepted. No new generation.'))
write(L,lg)
m['previous_visual_runtime_proof_before_equipment_bound']=m['latest_visual_runtime_proof']
m['current_task']='EV048 currentv118141strictGREEN and actual same native transaction6false-draw→0. Bound renderer/axisV002 implemented, art NEEDS_WORK: pending gear disappears, MED/otherstates placeholders. Nextpendingretention then3meleeaudio; formal0/15active.'
m['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261016-204427.log';m['current_build_exit_code']=0;m['latest_build_attempt']=m['current_build'];m['latest_build_attempt_exit_code']=0
m['previous_compiled_snapshot_before_equipment_bound']='source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116'
m['current_compiled_snapshot']=SNAP;m['current_compiled_snapshot_files']=1267;m['current_compiled_snapshot_bytes']=86336418;m['current_snapshot_pending']=None
m['ue_current_working_source_compiled']=True;m['ue_current_working_source_verified']=True;m['current_source_uncompiled_changes']=None
m['current_source_verification_scope']='Current strict141 plus2534 source/snapshot endpoints and native transaction141observations. This verifies bounded binding, not pending pose/full motion/audio/all units.'
m['latest_strict_UE_automation']=dict(report=report.relative_to(R).as_posix(),succeeded=141,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
m['latest_visual_runtime_proof']=dict(report=desc(doc),archive=GREEN.as_posix(),capture_snapshot=SNAP,video=desc(GREEN/'展示副本/equipment-bound-flow-green-silent.mp4'),observations=141,original_PNG_including_prewarm=142,duration_s=green['duration_s'],uniform_weapon_scale=.5,body_max_px=72,root_whole_views=2,root_unscaled_crop_views=14,independent_whole_views=2,independent_unscaled_crop_views=19,independent_review_freeze=desc(review),actual_transaction_mismatches=0,actual_committed_operations=3,art_review_status='NEEDS_WORK',audio_recorded=False,full_motion_accepted=False,formal_complete_units=0)
m['fairytale_sword_equipment_binding_v001'].update(actual_renderer_consumption_applied=True,resolver_compiled=True,native_binding_draw_proof=desc(GREEN/'原件/runtime-report.json'),actual_feature_RED=desc(RED/'原件/runtime-report.json'),current_native_transaction_mismatches=0,current_fullGREEN=141,scope='Same-resolver draw permission for actual NoArmor/LGT; MED explicit unsupported. Three actual commits/original LGT retake. Pending animation currently Ready0 without gear, not complete identity continuity or equip motion.')
m['fairytale_sword_primary3_axis_V002_bound_trial']=dict(candidate_freeze=desc(R/'source-assets/production/fairytale-sword-primary3-clearance-v002/candidate-freeze-v002.json'),actual_source=desc(R/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPrimary3V002.inl'),actual_native_capture=desc(GREEN/'原件/runtime-report.json'),phase1_degrees=-120,phase3_degrees=24,old_V001_unchanged=True,palms_unchanged=True,native_complete_facing_count=1,grasp_accepted=False,full_trajectory_accepted=False)
m['latest_native_review_player']=PLAYER.relative_to(R).as_posix();m['latest_native_review_browser_playback']=desc(O/'browser-playback-v001.json');m['latest_primary3_manual_launcher_preflight']=desc(O/'manual-launcher-preflight-v001.json')
m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+['E242','E243','E244','E245']));m['current_turn_media_retention'].update(latest_runtime='E244',player='E245',equipment_bound_RED='E243192sourcefiles142PNGZIP/2SHA0',equipment_bound_GREEN='E244192sourcefiles142PNGZIP/2SHA0',equipment_bound_player='E24517files1620454B/2SHA0')
m['next_retention_batch']='E246';m['next_snapshot']='v119';m['next_native_request']=179
m['next_work']=['Fix pending committed-gear visibility using explicitly tagged Ready0 GearPlaceholder; new probe expectation must first RED onv118, then production sameResolver change and nativeGREEN. Do not call placeholders completed motion.','Run prepared3melee audio journal tests actualRED, admit minimal no-double-play patch, current full144 and actual audio/mix review.','Complete selectedstyle allsemanticstates/4armors/5weapons20pairings; actual otherfacing/VFX/SFX/get/drop/persistence and15aux.','Implement actual STN003/004/GOB001/Boss including reward whitelist/owner snapshot/codec and specificAI/art; currentgeneric enemies are not these units.']
m['current_audio_audit']=desc(D/'evidence/audio-completion-audit-v002/report.md');m['current_enemy_runtime_audit']=desc(D/'evidence/enemy-runtime-coverage-audit-v001/enemy-runtime-coverage-v001.md')
m['pending_melee_audio_candidates']=dict(tests=desc(R/'source-assets/production/melee-audio-journal-integration-v001/Tests/DungeonMeleeAudioJournalIntegrationTests.cpp'),patch=desc(R/'source-assets/production/melee-audio-journal-integration-v001/production-v001.patch'),actual_Source_applied=False,actual_RED=None,actual_GREEN=None)
m['pending_equipment_gear_retention_stage0']=dict(freeze=desc(R/'source-assets/production/fairytale-equipment-retain-gear-v001/test-v001/stage0-freeze-v001.json'),actual_Source_applied=False,actual_native_RED=None,production_patch_applied=False)
m['current_turn_progress_classification']='progress: actual Source binding/2axis, current141 strictGREEN, real native transaction6mismatchRED→0GREEN, original same-ID/version retake, actual art review changes nextaction to pendinggear visibility; no fullunitcompletion.'
m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=now;write(P,m)
header='''2026-10-16 当前检查点（EV048，v118）：军剑/轻甲画面已由实际提交装备实例控制，真实拾取取消、提交、换中甲及原轻甲重拾流程由旧6处误画→当前0处。当前141/141严格通过，快照1267文件/2534端点零差；保持钟盔、小比例72px、剑.50和传统HUD隐藏。[当前运行复核](docs/production/first-batch-v2/runtime-review-equipment-bound-native-v001.md)。

| 当前资源 | 已有实际证据 | 剩余 |
| --- | --- | --- |
| 军剑＋无甲/轻甲绑定 | 同一普通输入流程141观察/142原PNG、3提交、同轻甲实例2版本2→4 | 换装途中无剑无甲占位，完整过渡待补 |
| 第三刀两轴 | 新Bound选择−120°/24°，旧V001保留；单向六相实际审图 | 拳盔/握姿、完整另一朝向与全轨迹未验收 |
| 近战音频 | 现声音路径审计及3测试/最小patch候选准备 | 尚未准入/实际RED→GREEN/试听 |
| 敌人/Boss | STN001/002已有专用驱动；其他精确ID审计完成 | STN003/004/GOB001/Boss实际AI、奖励/存续、全美术待实装 |

[打开真实装备绑定试玩](军剑真实装备绑定试玩.cmd)。录像静音、世界拾取白框仍为占位，中甲尚未适配。E243/E244原PNG文件字节以无损ZIP两遍核验保留，E245播放器保留；全部旧稿保持。正式完整单元0/15，目标active；5武器/4甲/5敌/Boss、20搭配、全状态/特效/音效/存取及15依赖范围不变。内置请求178、当前窗口10/24余14、累计202、下一179，本轮无新图像调用；外部API0。以下为历史检查点，以本段及progress权威字段为准。

'''
for p in [R/'README.md',R/'AGENTS.md']:p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 EV048续行，无新人类事件：实际5文件绑定消费+V002两轴已编译/full141strictGREEN/v1181267files2534端点0。相同普通输入真实flow旧6误画→当前0，141obs142PNGs/3提交/原轻甲实例2版本2→4；Root当前14crop2whole/旧4crop、独立21当前+4旧图。pending换装仍无剑无甲Ready0、中甲占位、轮廓/握姿/全视听待，不能算完整动作。E242格式诊断、E243RED/E244GREEN无损ZIP原字节两遍SHA0、E245播放器保留，传统HUD隐藏但世界白框仍在。当前完整0/15active，生成178/window10of24/rem14/next179，本轮新生成0。详见runtime-review-equipment-bound-native-v001.md。\n')
plan=D/'equipment-bound-native-execution-v001.md';shutil.copy2(plan,O/'before'/plan.name);t=plan.read_text(encoding='utf-8');assert t.count('- [ ] **')==6;plan.write_text(t.replace('- [ ] **','- [x] **')+'\n验收边界更新：以上六项仅绑定候选实施与受控验证完成；独立审图发现pending临时脱甲/消剑，下一轮先补，完整内容仍0/15。\n',encoding='utf-8')
write(O/'checkpoint.json',dict(after=[desc(p) for p in [P,L,doc,R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']],plan=desc(plan),retentions=retentions,current_native=desc(GREEN/'原件/runtime-report.json'),root_art_review=desc(O/'root-art-review-v001.json'),independent_review=desc(review),formal_complete_units=0,goal_status='active'))
print(json.dumps(dict(current_snapshot='v118',strict_tests=141,actual_native_observations=141,actual_original_PNGs=142,transaction_mismatches=0,art='NEEDS_WORK',formal_complete_units=0,goal_status='active',next='pending gear continuity'),ensure_ascii=False))
