from pathlib import Path
import json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
B=D/'evidence/sword-primary2-body-v001/status-before-v114-checkpoint-v001'
assert not B.exists();B.mkdir()
names=['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']
for n in names:
    q=B/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/n,q);assert q.read_bytes()==(R/n).read_bytes()
note='''2026-10-16 当前检查点 v114（EV048）：短肘上挑171已实际导入并运行，人物最高72px、UI隐藏。左右连续两段无Ready桥，Root及独立静帧审看确认姿态更可读；第二段仍缺胸肩甲，柄根/手套及完整动作尚未接受。[实景与限制](docs/production/first-batch-v2/runtime-review-sword-primary2-fit-v003.md)。新实录E213、播放页E216，实际播放至结尾无解码错误。

| 当前资源 | 状态 | 游戏内尺寸 |
| --- | --- | --- |
| 钟盔军剑Ready/首斩轻甲 | 双向实景候选，已穿胸肩 | 身体最高72px，独立剑0.50 |
| 第二段171短肘上挑 | 新身体六帧/独立剑已运行；握柄/完整运动未验收 | 同72px/UI隐藏 |
| 第二段四归属身体 | 24层候选，原RGBA重建一致；穿甲遮挡待实景 | 同512源画布，保持72px |
| 第二段胸/近肩/远肩 | 输入及三份精简提示词已审，准备真实六透视生成 | 源拟合窗70×50/60×44/32×30；同72px角色 |
| 局内存档继续 | v113真正两个进程Run-only通过；完整D13/菜单/设备试听待做 | 不适用 |

165653编译0→165921完整138/138。新六Texture另存，原989包未改，当前Production995。存档两进程证据仍绑定原v113。正式内容单元0/15、目标active；内置费用未知、外部API0。本段为当前，其后均为历史检查点。

'''
for n in ['README.md','AGENTS.md']:
    p=R/n;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=D/'progress.json';s=json.loads(p.read_text(encoding='utf-8-sig'))
g=json.loads((R/'source-assets/production/first-unit-animation-v003/generation-ledger.json').read_text(encoding='utf-8-sig'))
s.update(current_task='EV048 native171 sixbody real bilateral buffered P1→P2 fit v114 and static review done; three armor rows approved/preparing; grip/armor/complete units not accepted',
 current_build='UnrealGame/Saved/Bootstrap/build-editor-20261016-165653.log',current_build_exit_code=0,
 latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261016-165653.log',latest_build_attempt_exit_code=0,
 current_compiled_snapshot='source-assets/production/backups/2026-10-16_Primary2Native171-fit-full138GREEN-v114',
 ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,
 actual_registered_test_count_current=138,next_snapshot='v115',next_native_request=g['requested_count']+1,next_retention_batch='E217')
s['latest_strict_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261016-165921/index.json',filter='CodexDungeon',registered_in_filter=138,succeeded=138,failed=0,notRun=0,inProcess=0,warnings=0,errors=0,scope='v114 code contracts; not visual/device-audio/unit acceptance')
s['generation_accounting_current']=dict(requested_count=g['requested_count'],window_number=g['current_window']['number'],window_requested_count=g['current_window']['requested_count'],window_limit=24,remaining_in_window=g['remaining_batch_requests'],lifetime_requested_count=g['lifetime_requested_count'],external_api_calls=0,fee_unknown=True)
s['fairytale_sword_primary2_current_v001'].update(imported=True,source_pose_accepted=False,source_pose_scope='limited readable risingcut candidate, continue armor trial',production_packages_total=995,source_snapshot='v114',no_ready_bridge_both_facings=True,armor_primary2_present=False,full_motion_accepted=False,grip_accepted=False,runtime_retention='E213',player_retention='E216',player_decoded_to_end=True,review='docs/production/first-batch-v2/runtime-review-sword-primary2-fit-v003.md',next='Generate3actualarmor sixviews; standard extraction/realfeature measure/partition registration/nativefit; thenPrimary3/allstates')
s['fairytale_armor_primary2_current_v001']=dict(state='approved3nativeinputrows beforegeneration',original_input_retention='E214',body_partition_retention='E215',approved_handoff='source-assets/production/fairytale-armor-sword-primary2-v001/primary2-macro-native-handoff-approved-v002.json',feature_A_measured=False,imported=False,formal_complete_units=0)
s['current_retention_batches']=list(dict.fromkeys(s.get('current_retention_batches',[])+['E211','E213','E214','E215','E216']))
s['current_turn_media_retention'].update(native171_actual_fit='E213',three_armor_inputs='E214',four_owner_partition='E215',native171_player='E216',E212='empty diagnostic, not successful retention; failure preserved')
s['current_turn_progress_classification']='progress: real171 fit/import/full138 and reviewed three armor inputs; no formal content unit complete'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 v114续行（EV048，无新要求）：171短肘上挑导入/双向两段实录与静帧审查，72px/UIoff，138GREEN；P2缺胸肩和握柄细节待做。三甲输入E214、身体分层E215、新播放器E216保留，正式0/15active。\n')
print(json.dumps(dict(checkpoint='v114',native=g['requested_count'],formal_complete_units=0),ensure_ascii=False))
