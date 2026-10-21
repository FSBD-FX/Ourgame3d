from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=D/'evidence/run-pristine-bootstrap-v001/status-before-v113-checkpoint-v001'
assert not B.exists();B.mkdir()
names=['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json',
       '.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md','docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md']
for name in names:
    q=B/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,q);assert q.read_bytes()==(R/name).read_bytes()
proof='docs/production/first-batch-v2/run-pristine-two-process-runtime-proof-v001.md'
art='docs/production/first-batch-v2/runtime-review-sword-primary2-fit-v002.md'
note=f'''2026-10-16 当前检查点 v113：EV048 怪诞钟盔与小比例继续，人物最高72px，UI隐藏。军剑待机/首斩保留胸肩；第二段ArcB真实双向连续输入已消除待机桥帧，但横臂身体和缺甲仍未接受。已另生成170短肘上挑，发现蓄力手张开后，以171定点闭握纠正；六帧标准提取和实际掌面/袖口/布面附件测量已完成，171尚未导入。[美术事实与限制]({art})。

局内存档已通过真正两个UE进程：v113实际162916编译0→162940完整138/138，所有errors/warnings/notRun/inProcess为0。原生共享几何判断实测渲染组件无body，真实阻挡Box仍拒绝。全新v002进程44460退出后启动52000；原生无初始新局入口、完整Codec安装/暂停字节一致、原装填期限唯一0→1补弹及未来声音请求通过，Source/DLL与v113冻结绑定，3178端点SHA零差。[实证]({proof})。完整D13/保存菜单/设备试听仍待；第一次核验器GUID格式失败及两次编译失败均保留。

| 资源/部分 | 当前状态 | 游戏内尺寸 | 来源 |
| --- | --- | --- | --- |
| 钟盔军剑待机/首斩与轻甲 | 真实双向候选，非完整装备 | 身体最高72px，独立剑0.50 | v105实录/E185、E189 |
| 第二段ArcB | 真实连续两段，无待机桥；身体挥砍与甲层未完成 | 同72px/UI隐藏 | v110/E200，播放页E201 |
| 171短肘上挑六帧 | 新身体候选，闭握修正/测量完成，未导入 | 512源帧，共同行尺度，未来最多72px | E208/E209；成本未知，外部API0 |
| 局内存档/继续合同 | 真正两个进程Run-only证明通过，菜单与完整Profile待做 | 不适用 | v113/E210 |

当前Production仍989包，新增171没有覆盖旧169。内置请求171，窗口008已3/24、余21，累计195，下一172；未调用外部API，内置费用未知。接下来以171制作独立剑试装与胸/双肩真实动作层，再推进第三段及其他装备/敌人状态。正式完整0/15，目标active；人类要求事件仍EV048，没有新增EV049。以下为历史记录，以本段与progress权威字段为准。

'''
for name in ['README.md','AGENTS.md']:
    p=R/name;p.write_text(note+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
p=R/'docs/production/first-batch-v2/progress.json';s=json.loads(p.read_text(encoding='utf-8-sig'))
generation=json.loads((R/'source-assets/production/first-unit-animation-v003/generation-ledger.json').read_text(encoding='utf-8-sig'))
assert generation['requested_count']==171 and generation['current_window']['requested_count']==3
session='UnrealGame/Saved/RunPristineProofs/20261016-163507-native-two-process-v002'
s.update({'current_task':'EV048: actual full138 and genuine two-process Run-only Continue v113 passed; ArcB noReady bridge but native169 motion/armor rejected; native171 closed-grip rising-cut six source frames measured, new independent sword + three armor rows in preparation. formal0/15 active.',
 'current_build':'UnrealGame/Saved/Bootstrap/build-editor-20261016-162916.log','current_build_exit_code':0,
 'latest_build_attempt':'UnrealGame/Saved/Bootstrap/build-editor-20261016-162916.log','latest_build_attempt_exit_code':0,
 'current_compiled_snapshot':'source-assets/production/backups/2026-10-16_RunTwoProcessProbe-admitted-full138GREEN-v113',
 'ue_current_working_source_compiled':True,'ue_current_working_source_verified':True,'current_source_uncompiled_changes':None,
 'actual_registered_test_count_current':138,'next_native_request':172,'next_snapshot':'v114','next_retention_batch':'E211',
 'current_turn_progress_classification':'progress: genuine two-process restore original reload and full138 actual; native170/171 source correction and measured mounts; no unit completion',
 'next_work':['Native171 independent sword import/capture, actual grip/head/feet fit; preserve rejected169/170 history',
              'Genuine Primary2 Chest/Near/Far armor rows and exact original body ownership/occlusion trial, then Primary3/allstates',
              'Finish original equipment/enemies/Boss and20pairings/VFX/SFX/acquire/equip/drop/full persistence; formal0/15 active']})
s['latest_strict_UE_automation']={'report':'UnrealGame/Saved/Automation/FirstRoom-20261016-162940/index.json','filter':'CodexDungeon','registered_in_filter':138,
 'succeeded':138,'failed':0,'notRun':0,'inProcess':0,'warnings':0,'errors':0,'old134_name_set_preserved':True,'scope':'v113 code contracts and optional native proof coordinator; not visual/device-audio/unit acceptance'}
s['latest_targeted_UE_automation']={'report':'UnrealGame/Saved/Automation/FirstRoom-20261016-161755/index.json','filter':'CodexDungeon.Content.RunPristine',
 'registered':3,'succeeded':3,'failed':0,'warnings':0,'errors':0,'native_geometry_1GREEN_report':'FirstRoom-20261016-161619/index.json'}
s['generation_accounting_current']={'requested_count':171,'window_number':8,'window_requested_count':3,'window_limit':24,'remaining_in_window':21,
 'lifetime_requested_count':generation['lifetime_requested_count'],'external_api_calls':0,'fee_unknown':True}
s['run_pristine_current_v001']={'state':'actual1RED4errors→geometry1GREEN/pristine3GREEN/full138GREEN; real two-process v002 source44460→restore52000 passed',
 'session':session,'source_and_DLL_snapshot':'v113','whole_codec_install_pause_bytes_identical':True,'initial_no_run_R_closed':True,
 'original_reload_deadline_unique_refill_future_audio_only':True,'full_D13':False,'save_continue_menu':False,'device_audio_auditioned':False,
 'proof':proof,'root_audit':'docs/production/first-batch-v2/evidence/run-pristine-bootstrap-v001/actual-two-process-v113-audit-v001.json',
 'old_failed_session_preserved':'20261016-163146-native-two-process-v001; verifier FGuid format bug, native roles exited0; original failed status unchanged',
 'formal_complete_units':0}
s['run_save_adapter_current_v001']['actual_new_process_Continue']=True
s['run_save_adapter_current_v001']['pristine_bootstrap_dependency']='closed native InitGame/explicit PreparePristine and genuine two-process proof passed; menu/fullD13 pending'
s['fairytale_sword_primary2_current_v001']={'native_request':171,'source_pose_accepted':False,'imported':False,'actual_mounts_measured':True,
 'shape_QA_passed':True,'standard_timing_contract_passed':False,'actual_kernel_timing_ms':[75,75,60,60,135,135],'standard_preview_ms':[100]*6,
 'derived_freeze':'source-assets/production/fairytale-sword-primary2-v001/primary2-extraction-v004/extracted-freeze-v004.json',
 'measurement_freeze':'source-assets/production/fairytale-sword-primary2-v001/primary2-measurement-v003/measurement-freeze-v003.json',
 'raw_SHA256':'527f93f7838c9a95f69c1ac16ecb7095c3aeda3e5a9190088aed6bdc89b1af85',
 'previous_native169_runtime_trial':{'imported':6,'production_packages_total':989,'ArcB_no_ready_bridge':True,'final_motion_accepted':False,'armor_primary2_present':False,'source_snapshot':'v110','retention':'E200/E201'},
 'native170_rejected_open_phase1_hand':True,'next':'native171 separate sword trial and three actual armor rows; axis1 shallower to avoid predicted ground tip; real fit pending',
 'complete_armor':False,'formal_complete_units':0}
s['current_source_frozen_audit_v113']={'files':1589,'bytes':94638273,'endpoint_checks':3178,'differences':0,'two_process_CodexDungeon_source_pins':155,'source_DLL_bound':True}
s['current_retention_batches']=list(dict.fromkeys(s.get('current_retention_batches',[])+[f'E{i}' for i in range(199,211)]))
s['current_turn_media_retention'].update({'ArcA':'E199','ArcB':'E200','ArcB_player':'E201','native170':'E202–E205','native171':'E206–E209',
    'two_process_actual_proof':'E210152files4922955B/2SHA0','E196':'failed partial preserved; not successful retention'})
s['previous_goal_turn_classification']={'classification':'progress','blocking_condition_repeated_consecutively':0,'reason':'new genuine process restore/full138, source171 and active sword/armor preparation','goal_status':'active'}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record='\n2026-10-16 v113续行（EV048，无新人类要求）：实际full138及真正两个UE进程Run-only原装填继续通过，3178端点SHA0/E210152files2SHA0；完整D13/菜单/设备试听待。ArcB真实连续输入无Ready桥但旧身体/缺甲不接受；170短肘p1开手失败后171闭握六帧提取/测量完成/E208209，未导入，正在独立剑与三甲row准备。ledger171/window0083of24/rem21/lifetime195/external0/费用未知。正式0/15active。\n'
for name in ['项目需求台账.md',*names[-2:]]:
    with (R/name).open('a',encoding='utf-8') as stream:stream.write(record)
print(json.dumps({'durable_checkpoint':'v113','backed_up_files':len(names),'actual_two_processes':True,'full':138,'native':171,'formal_complete_units':0},ensure_ascii=False))
