from pathlib import Path
import json,hashlib,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';E=D/'evidence/armor-primary2-status-v115'
assert not E.exists();E.mkdir()
names=['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json','source-assets/production/first-unit-animation-v003/generation-ledger.json']
for name in names:
 q=E/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,q);assert q.read_bytes()==(R/name).read_bytes()
report='docs/production/first-batch-v2/runtime-review-sword-primary2-fit-v004.md'
note=f'''2026-10-16 当前检查点 v115（EV048）：钟盔军剑的待机及前两段现均穿胸甲和双肩。第二段171短肘上挑加172/173/174新甲片已真实导入/双向连击实录，Root看32原比例裁图与两整景；所看样本不再在第二刀变灰衣。身体最高72px，游戏UI隐藏，独立剑0.50。[实景与边界]({report})。

| 当前资源 | 已实际完成的试装步骤 | 游戏内尺寸与待验边界 |
| --- | --- | --- |
| 钟盔军剑Ready/首斩 | 同族胸肩保留、双向实景 | 身体最高72px、剑0.50；完整动作待验 |
| 第二段身体/轻甲 | 171身体＋三甲18帧＋24身体层，真实八层绘制，双向无Ready桥 | 同72px；柄根/足锁/全过程间隙未接受 |
| 三甲素材 | 标准shared-row提取/实际特征测量/整数配准/42Texture实际保存 | 512源画布；600ms标准预览仍不同于540ms内核 |
| 第三段 | 实际Stage2数字已核，六相110/110/60/60/160/160ms | 尚未生成或接入新动作 |
| 其他装备/敌人/Boss | 既有候选保留 | 新风格全状态/实战视听及搭配未完成 |

180126编译0→180344完整138/138，所有errors/warnings/notRun/inProcess为0；v1151704文件/3408端点SHA0，旧995包保持、当前Production1037。E223实录/E224播放页已保留，新页播放至结尾无解码错误。可双击“钟盔军剑两段穿甲试装.cmd”审前两段；第三段和其他状态仍有占位。

内置请求174，窗口008已6/24、余18、累计198，下一175；外部API0、内置费用未知。正式完整0/15、目标active；当前人类事件仍EV048。其后为历史检查点，以本段及progress当前字段为准。

'''
for name in ['README.md','AGENTS.md']:
 p=R/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=D/'progress.json';s=json.loads(p.read_text(encoding='utf-8-sig'));g=json.loads((R/names[-1]).read_text(encoding='utf-8-sig'))
assert g['requested_count']==174 and g['current_window']['requested_count']==6
s.update(current_task='EV048 v115 actual two-stage matching armor bothfacings/72px/UIoff/full138GREEN, Root32crop+2whole reviewed; grip/fullmotion/thirdstage/all other units remain. Primary3 actual660ms numeric prep ready; formal0/15active',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261016-180126.log',current_build_exit_code=0,latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261016-180126.log',latest_build_attempt_exit_code=0,current_compiled_snapshot='source-assets/production/backups/2026-10-16_Primary2Armor42-fit-full138GREEN-v115',ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,next_snapshot='v116',next_native_request=175,next_retention_batch='E225')
s['latest_strict_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261016-180344/index.json',registered_in_filter=138,succeeded=138,failed=0,errors=0,warnings=0,notRun=0,inProcess=0,scope='v115code/4source trial, not full unit/art/deviceaudio acceptance')
s['generation_accounting_current']=dict(requested_count=174,window_number=8,window_requested_count=6,window_limit=24,remaining_in_window=18,lifetime_requested_count=198,external_api_calls=0,fee_unknown=True)
s['fairytale_sword_primary2_current_v001'].update(source_snapshot='v115',production_packages_total=1037,armor_primary2_present=True,runtime_retention='E223',player_retention='E224',player_decoded_to_end=True,grip_accepted=False,full_motion_accepted=False,review=report,next='Primary3 genuine sixbody/armor/sword states and real three-stage sequence, then remaining allstates/units')
s['fairytale_armor_primary2_current_v001'].update(state='actual42saved/source4compiled/full138GREEN/dual real8draw kernel fit and Root32crop static review; not complete equipment',imported=True,production_packages_total=1037,feature_A_measured=True,raw_retention=['E218','E219','E220'],standard_retention='E221',registration_retention='E222',runtime_retention='E223',player_retention='E224',measurement='source-assets/production/fairytale-armor-sword-primary2-v001/primary2-component-measurement-v001/measurement-freeze-v001.json',fullmotion_accepted=False,formal_complete_units=0)
s['current_source_frozen_audit_v115']=dict(files=1704,bytes=99050455,endpoint_checks=3408,differences=0,source_DLL_bound=True)
s['current_retention_batches']=list(dict.fromkeys(s.get('current_retention_batches',[])+['E221','E222','E223','E224']))
s['current_turn_media_retention'].update(standard_three_armor='E221124files5368707B/2SHA0',registered42='E22274files3086971B/2SHA0',actual_P2armor='E223282files856512283B/2SHA0',P2armor_player='E22410files916454B/2SHA0')
s['current_turn_progress_classification']='progress: P2matchingarmor actual native/strict full138 and reviewed native recording, no formal unit completion'
s['previous_goal_turn_classification']=dict(classification='progress',blocking_condition_repeated_consecutively=0,goal_status='active',reason='actual secondstage armor trial plus nextThirdstage numeric evidence')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
counterkeys=['requested_count','batch_requested_count','remaining_batch_requests','lifetime_requested_count','current_window'];before={k:g[k] for k in counterkeys}
for n in [171,172,173,174]:
 rows=[x for x in g['requests'] if x['request_number']==n];assert len(rows)==1;row=rows[0]
 row.setdefault('review_history',[]).append(dict(date='2026-10-16',scope='v115actualP2armor trial',report=report,runtime_retention='E223',fullmotion_accepted=False,formal_complete_units=0))
 row['status']='runtime_trial_candidate_pending_grip_allstates_and_complete_equipment';row['runtime_imported']=True
assert {k:g[k] for k in counterkeys}==before
(R/names[-1]).write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 v115续行（EV048，无新要求）：同族胸肩补到第二段，42真实保存/旧995保持/1037包；180126编译0/180344full138GREEN；双向八层6.60257秒实录/3408SHA0/E223，Root32crop+2whole和E224播放核验。握柄/第三段/全状态及正式15单元仍待，正式0/15active。ledger174/window0086of24/rem18/lifetime198/external0/费用未知；Sourcehold v115。\n')
print(json.dumps(dict(checkpoint='v115',production_packages=1037,full138=True,goal='active',formal_complete_units=0),ensure_ascii=False))
