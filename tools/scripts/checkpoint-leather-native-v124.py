from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';F=R/'source-assets/production/fairytale-lgt-readability-v003'
O=D/'evidence/leather-ready-v001/status-checkpoint-v124';assert not O.exists();O.mkdir(parents=True)
P=D/'progress.json';L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';RM=R/'README.md';REQ=R/'项目需求台账.md'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in [P,L,RM,REQ]:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
S=R/'source-assets/production/backups/2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124';m=read(S/'compiled-source-manifest.json');assert m['current_automation_succeeded']==154 and m['production_packages']==1097
for row in m['files']:
 for base in [R,S]:
  p=base/row['path'];d=desc(p);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261017-004814/index.json';v=read(report);assert v['succeeded']==len(v['tests'])==154 and all(v.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']) and all(t['state']=='Success' and t['warnings']==t['errors']==0 for t in v['tests'])
A=R/'过程图稿与视频/2026-10-17_软皮轻甲左右待机试装_v001';B=R/'过程图稿与视频/2026-10-17_军剑真实换装绑定_v006-guardCoinGREEN';V=R/'过程图稿与视频/2026-10-17_软皮轻甲实景播放复核_v001'
a=read(A/'原件/runtime-report.json');b=read(B/'原件/runtime-report.json');assert a['passed'] and a['leather_ready_phase_masks_left_right']==[15,15] and not a['mismatches'] and len(a['observations'])==71;assert b['passed'] and not b['mismatches'] and b['light_primary_phase_masks']==[63,63,63] and len(b['observations'])==141
art=read(V/'原件/root-native-art-review-v001.json');assert art['root_actually_viewed_native_eight_crops'] and art['browser_both_recordings_ended_error_null']
E=Path('E:/OurGame/Knight/过程图稿与视频');ret=[]
for n in range(266,282):
 matches=[p for p in E.iterdir() if p.name.startswith('2026-10-') and '-OurgameUE-' in p.name and p.name.endswith(f'-v{n}')];assert len(matches)==1,(n,matches)
 folder=matches[0];p=folder/'retention-verification-v001.json'
 if not p.exists():p=folder/'source-size-SHA256.json'
 x=read(p);assert x['verification_passes']==2 and x.get('source_and_target_hash_mismatches',x.get('source_and_retained_size_SHA_mismatches'))==0;ret.append(desc(p))
ledger=read(L);assert ledger['requested_count']==187 and ledger['lifetime_requested_count']==211 and ledger['remaining_batch_requests']==5 and ledger['external_api_calls']==0
sem=F/'root-semantic-review184-187-v001.json';assert not sem.exists()
write(sem,dict(source_events=['EV-048'],human_new_event=None,actual_native_requests=[184,185,186,187],native_image_generated_count=4,review={'184':'Chest sleeveless leather eligible; actual clasp A measured and native Ready4 trial reviewed','185':'REJECT: broad Near-style cap/long ring instead of perspective Far; never extracted/imported','186':'Near gray lining removed; lower-right actual stitch A measured; native Ready4 trial reviewed','187':'tiny curved Far tab; explicit256small-component floor, default512failures and low-motion warning retained; actual tip A measured; native Ready4 trial reviewed'},trial_art_review=desc(V/'原件/root-native-art-review-v001.json'),new_actual_Texture2D=12,full_animation_accepted=False,full_unit_complete=False,human_style_accepted_claimed=False))
for n in [184,185,186,187]:
 rows=[r for r in ledger['requests'] if r['request_number']==n];assert len(rows)==1
 rows[0]['status']='rejected_far_perspective_not_imported' if n==185 else 'native_Ready4_trial_reviewed_full_motion_unaccepted'
 rows[0]['root_semantic_review']=desc(sem)
 rows[0]['review_notes']=read(sem)['review'][str(n)]
write(L,ledger)
doc=D/'runtime-review-leather-native-v124.md';assert not doc.exists()
doc.write_text('''# EV048 软皮轻甲实景试穿与运行接入 · v124

2026-10-17，Asia/Shanghai。继续“保持怪诞方向，增强盔甲和轮廓辨识”；本次没有新增用户事件或把助手数值当用户逐项批准。

事实：新版行路短衣为棕色软皮胸衣、不对称短近肩和窄远肩。184胸衣、186近肩、187远肩按实际可见扣件／缝线／端点A配artist设计B，仅整数平移；原Body158和三身体层不变。185远肩视角错误被拒绝，原稿及失败提取全部保留。新12个Texture2D实际导入v012，旧1085包大小/SHA保持；当前Production总1097包，不能把包数误称全部Texture2D数量。

实际游戏通过普通Enter/E/A取消/E提交轻甲，再普通方向输入转面；同一轻甲实例2左右各Ready4，71观察／72原PNG，一次提交、0差异。Root在E280后看整景和全部八张1:1裁图；胸衣与短肩比旧灰甲清楚，钟盔、琥珀眼窗和双手保持可见。新录像2.366667秒、默认旧甲三连击录像4.766667秒均完整播放ended=true/error=null；静音。实际尺寸仍为身体目标72px、独立军剑.50、传统HUD隐藏，地面白框／标记仍占位。

推理：这套胸肩分离与暖皮色可作为待机试穿基准，仍需把新风格延续到走路、攻击、受击、换装等动作，才适合替换默认完整试玩。小扣件在72px下不能承担装备识别，优先保留头盔、肩和胸部的大轮廓。Ready试样不计整套装备或全动画完成，也不冒用默认旧灰甲三段动作证据。

风险与边界：新版目前仅Ready4；未完成全状态、20搭配、抓握／过渡、特效声音及正式获取／掉落／存档验收。默认试玩仍用旧动作外观，和新的可选待机试穿分开。录像为实际墙钟的CFR30展示副本，原PNG像素和文件字节保持；没有录音或试听验收。

运行基础：STN003守卫真实驱动已由实际3组语义RED到3GREEN，覆盖实体身份／一次减伤／实际时钟招式／宽体碰撞／无奖励死亡观察；程序绘制仍是占位，正式奖励／Save Unsupported，不能计完整敌人。房间金币最大余数整数分配由实际3RED到3GREEN，仅返回预分配计划，未接正式房间完整槽位清单、一次结算、掉落或钱包。两项均通过独立审查。当前源完整154/154逐项Success，错误／警告／未运行／进行中均0；实际编译004636，报告004814，v1241292文件／2584端点0差。另用同一构建录制默认绑定流程141观察／142PNG、三提交、原甲同实例重拾、三段63³、0差。

资料：

- [新版试穿播放器](../../../过程图稿与视频/2026-10-17_软皮轻甲左右待机试装_v001/review-player.html)
- [八帧原比例实景](../../../过程图稿与视频/2026-10-17_软皮轻甲实景播放复核_v001/展示副本/native-ready-eight-frames-unscaled.png)
- [当前默认试玩](../../../军剑真实装备绑定试玩.cmd)
- [实际源冻结](../../../source-assets/production/backups/2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124/compiled-source-manifest.json)

展示前留存E266–E281，源和目标大小/SHA各两遍0差；大原PNG按原文件字节无损ZIP，F原件不动，E根README未改。内置台账187、窗口008已用19/24余5、累计211、下一188；外部API0、内置费用未核实。正式完整0/15，目标active。下一步优先新版皮甲动作连续性，再完成其余装备／敌人内容单元。
''',encoding='utf-8')
v=read(P);v.update(date='2026-10-17',goal_status='active',current_task='EV048 new leather Ready4 both facings actual trial reviewed; next complete matching walk/equip/attack/hurt/death armor states. STN003 native and pure coin allocation integrated but formal content/reward/Save incomplete.',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261017-004636.log',current_build_exit_code=0,latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261017-004636.log',latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,current_compiled_snapshot=S.relative_to(R).as_posix(),current_compiled_snapshot_files=1292,current_compiled_snapshot_bytes=m['bytes'],actual_registered_test_count_current=154,production_uasset_package_count_actual=1097,production_package_count_actual=1097,production_texture_count_actual=None,production_texture_count_scope='Texture2D class count not recomputed; current1097 counts all Production packages. New12Texture2D individually native-verified; old1085packages unchanged.',next_native_request=188,next_snapshot='v125',next_human_event='EV-049',next_retention_batch='E282',current_turn_progress_classification='progress',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
v['previous_full_GREEN_UE_automation']=v.get('latest_strict_UE_automation');v['latest_strict_UE_automation']=dict(report=report.relative_to(R).as_posix(),succeeded=154,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
v['generation_accounting_current']=dict(requested_count=187,current_window=8,window_requested=19,window_remaining=5,lifetime_requested_count=211,external_api_calls=0,host_fee_usd=None,authorization_events=['EV-040','EV-041'])
v['previous_visual_runtime_proof_before_v124']=v.get('latest_visual_runtime_proof');v['latest_visual_runtime_proof']=dict(report=desc(doc),archive=A.as_posix(),capture_snapshot=S.relative_to(R).as_posix(),video=desc(A/'展示副本/leather-ready-trial-silent.mp4'),observations=71,original_PNG_including_prewarm=72,actual_committed_operations=1,actual_ready_masks_left_right=[15,15],actual_transaction_mismatches=0,body_max_px=72,uniform_weapon_scale=.5,root_whole_views=1,root_unscaled_crop_views=8,browser_ended_error_null=True,audio_recorded=False,full_motion_accepted=False,art_review_status='Ready trial usable; full content NEEDS_WORK',new_leather_runtime_imported=True,guard_native_driver=True,formal_complete_units=0)
v['latest_native_review_player']=V.relative_to(R).as_posix();v['latest_native_review_browser_playback']=dict(tab_id='18',ready_duration=2.366667,existing_flow_duration=4.766667,ended=True,error=None,retention='E281')
v['current_retention_batches']=ret;v['current_turn_media_retention']=dict(first='E266',last='E281',batches=16,two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True)
v['soft_leather_readability_v003'].update(semantic_review184_187=desc(sem),actual_new_Texture2D=12,actual_import_receipt=desc(R/'UnrealGame/Saved/Bootstrap/leather-ready-v001-import-20261016-164451-394112.json'),actual_native_ready_trial=desc(A/'原件/runtime-report.json'),actual_native_eight_root_review=desc(V/'原件/root-native-art-review-v001.json'),only_Ready4_each_facing=True,default_whole_game_replaced=False,full_motion_accepted=False)
v['stone_guard_native_v001'].update(production_applied=True,production_admission=desc(D/'evidence/stone-guard-native-v001/root-production-admission-v001/admission.json'),actual_UE_GREEN=desc(R/'UnrealGame/Saved/Automation/FirstRoom-20261017-003649/index.json'),actual_full_GREEN=desc(report),review=desc(D/'evidence/stone-guard-native-v001/production-review-v001/review.md'),save_supported=False,reward_supported=False,formal_unit_complete=False)
v['room_coin_allocation_v001'].update(actual_UE_GREEN=desc(R/'UnrealGame/Saved/Automation/FirstRoom-20261017-003132/index.json'),actual_full_GREEN=desc(report),formal_room_binding=None,actual_payout=False)
v['completed_foundation_checks'].update(ue_tests_last_passed=154,ue_latest_total=154,ue_latest_failed=0,ue_latest_report=report.relative_to(R).as_posix(),ue_last_full_successful_report=report.relative_to(R).as_posix(),ue_last_full_successful_count=154,ue_verified_source_snapshot=S.relative_to(R).as_posix(),ue_current_working_source_verified=True,guard_native_driver=True,room_coin_integer_plan_native3_passed=True)
v['next_work']=['Complete matching new soft-leather walk/equip/Primary1-3/hurt/death and source mounts before whole-game replacement; keep72px/helmet/hiddenHUD.', 'Complete SWD grasp/transition and remaining weapons4armors/all20pairings/statuses/VFX/SFX/actual pickup/drop/Save and15aux.', 'Complete STN003Guard art/statuses/audio/formal room allocation and once death settlement/owner codec, then STN004/GOB001/Boss and remaining units.'];v['next_turn_priorities']=v['next_work'];write(P,v)
head='''2026-10-17 当前检查点（EV048，v124）：新版棕色软皮胸衣＋短近肩／窄远肩已进入实际场景；保持怪诞钟盔、72px小比例、军剑.50和传统HUD隐藏。真实拾取提交同一件轻甲后，左右各四帧待机试穿通过，八张原比例实景已审，录像已完整播放。[打开新版试穿](过程图稿与视频/2026-10-17_软皮轻甲左右待机试装_v001/review-player.html)。

| 当前内容 | 已验证 | 仍需制作 |
| --- | --- | --- |
| 新软皮轻甲 | 12新Texture2D、实际一次拾取提交、左右Ready4；盔甲与灰衣更易区分 | 新风格走路／攻击／换装／受击／死亡及全适配，暂不替换默认完整动作 |
| 裂岩守卫 | 实际驱动3RED→3GREEN、真实时钟／一次减伤／宽体碰撞；独立复核 | 程序外形仍占位；完整美术声音、正式奖励／房间生成和存档 |
| 房间金币分配 | 整数预分配3RED→3GREEN，零数／溢出／拒绝原子性 | 正式房间完整槽位、一次结算、真实掉落／拾取钱包 |
| 当前游戏 | 当前154/154零错误警告；另默认换装141观察、三提交／三连击0差 | 世界拾取白框、完整动作与音效继续制作 |

[本轮事实、推理和边界](docs/production/first-batch-v2/runtime-review-leather-native-v124.md) · [默认试玩](军剑真实装备绑定试玩.cmd)（旧攻击外观保留）。当前1097资源包＝旧1085不变＋新12纹理；v1241292文件／2584端点0差。E266–E281展示前两遍留存，原图保持，录像静音。正式完整0/15、目标active；图像台账187／窗口19of24余5／累计211／下一188，外部API0，内置费用未知。以下旧检查点保留，以本段和progress当前权威字段为准。

''';RM.write_text(head+RM.read_text(encoding='utf-8-sig'),encoding='utf-8')
REQ.write_text(REQ.read_text(encoding='utf-8-sig')+'\n\n## 2026-10-17 EV048执行检查点 · v124\n\n继续既有“保持怪诞方向，增强盔甲和轮廓辨识”，没有新增用户事件或将试样视为用户最终接受。新棕色软皮胸衣／近肩／窄远肩进入实际Ready-only试穿：正常取消与一次提交、同件轻甲左右四帧，原比例八帧及静音录像已审；全动作与全部装备／敌人仍未完成。当前154项严格测试通过，新12纹理／旧1085包不变；STN003真实驱动与纯金币预分配接入通过，正式奖励及Save仍未闭合。详见 [v124运行记录](docs/production/first-batch-v2/runtime-review-leather-native-v124.md)。\n',encoding='utf-8')
out=subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'),'-B','-X','utf8',str(R/'tools/scripts/verify-equipment-bound-current-build-v004.py'),'--snapshot',S.relative_to(R).as_posix()],cwd=R,check=True,capture_output=True,text=True,encoding='utf-8');(O/'manual-launcher-preflight-v004.txt').write_text(out.stdout,encoding='utf-8')
write(O/'checkpoint.json',dict(progress=desc(P),README=desc(RM),requirements=desc(REQ),ledger=desc(L),runtime_review=desc(doc),source_and_frozen_endpoint_checks=2584,source_mismatches=0,current_tests=154,production_packages=1097,native_new_trial_observations=71,native_default_observations=141,formal_complete_units=0,goal_status='active',next_native=188,next_snapshot='v125',next_retention='E282',human_event_049_unused=True))
print(json.dumps(dict(checkpoint='v124',actual_native_trial_reviewed=True,default_manual_preflight_passed=True,actual_tests=154,formal_complete_units=0,goal_active=True,next_retention='E282'),ensure_ascii=False))
