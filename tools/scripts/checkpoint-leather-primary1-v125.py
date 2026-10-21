from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';F=R/'source-assets/production/fairytale-lgt-readability-v003';O=D/'evidence/leather-primary1-v001/status-checkpoint-v125';assert not O.exists();O.mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
P=D/'progress.json';L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';RM=R/'README.md';REQ=R/'项目需求台账.md';CMD=R/'军剑真实装备绑定试玩.cmd'
for p in [P,L,RM,REQ,CMD]:
 q=O/'before'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
S=R/'source-assets/production/backups/v125-p1-157G';m=read(S/'compiled-source-manifest.json');assert m['current_automation_succeeded']==157 and m['production_packages']==1115 and m['copied_files']==1512
for row in m['files']:
 for base in [R,S]:
  d=pin(base/row['path']);assert (d['bytes'],d['sha256'])==(row['bytes'],row['sha256'])
contracts=R/'source-assets/production/checkpoint-v125-root-input-v001/manual-proof-contract-v125-v001.json'
v=subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'),'-B','-X','utf8',str(R/'tools/scripts/verify-equipment-bound-current-build-v006.py'),'--project',str(R),'--snapshot',S.relative_to(R).as_posix(),'--proof-contract',contracts.relative_to(R).as_posix()],cwd=R,check=True,capture_output=True,text=True,encoding='utf-8');gate=json.loads(v.stdout);assert gate['preflight_passed'] and gate['mismatches']==0;write(O/'manual-preflight-v006.json',gate)
A=R/'过程图稿与视频/2026-10-17_软皮轻甲左右第一刀试装_v001';V=R/'过程图稿与视频/2026-10-17_软皮轻甲首刀实景播放复核_v001';B=R/'过程图稿与视频/2026-10-17_软皮轻甲首刀播放浏览器证据_v001';a=read(A/'原件/runtime-report.json');browser=read(B/'原件/browser-playback.json');assert a['passed'] and a['leather_primary1_masks_left_right']==[63,63] and len(a['observations'])==96 and not a['mismatches'];assert browser['ended'] and browser['error'] is None and browser['duration']==3.2
ret=[];E=Path('E:/OurGame/Knight/过程图稿与视频')
for n in range(282,303):
 matches=[p for p in E.iterdir() if p.name.startswith('2026-10-17-OurgameUE-') and p.name.endswith(f'-v{n}')];assert len(matches)==1,(n,matches)
 p=matches[0]/'retention-verification-v001.json';p=p if p.exists() else matches[0]/'source-size-SHA256.json';d=read(p);assert d['verification_passes']==2 and d.get('source_and_target_hash_mismatches',d.get('source_and_retained_size_SHA_mismatches'))==0;ret.append(pin(p))
review=F/'root-native188-192-review-v125.json';assert not review.exists();write(review,dict(human_event='EV-048',new_human_event=None,reviews={'188':'not selected: Chest phase4 reversed perspective','189':'Near6 imported and native trial reviewed','190':'Far6 imported and native trial reviewed','191':'rejected: correction still reversed; not extracted/imported','192':'all6 same-facing Chest; selected and native trial reviewed'},wrong_body_mounts_v001_preserved_and_never_imported=True,actual_body_mounts_v002='Body159 run-primary1-v003, exact existing24body layers',native_trial=pin(A/'原件/runtime-report.json'),static_and_native_art_review=pin(V/'原件/root-native-art-review-v001.json'),Root_actually_viewed12native_crops_and2whole_and_browser_screenshot=True,browser_fullplay=pin(B/'原件/browser-playback.json'),full_motion_accepted=False,formal_complete_units=0))
ledger=read(L);assert ledger['requested_count']==192 and ledger['current_window']['requested_count']==24 and ledger['remaining_batch_requests']==0 and ledger['lifetime_requested_count']==216 and ledger['external_api_calls']==0
for row in ledger['requests']:
 if row['request_number'] in [188,189,190,191,192]:
  row['status']='rejected_wrong_perspective_not_imported' if row['request_number'] in [188,191] else 'native_Primary1_trial_reviewed_full_motion_unaccepted';row['root_semantic_review']=pin(review)
write(L,ledger)
doc=D/'runtime-review-leather-primary1-v125.md';assert not doc.exists();doc.write_text('''# EV048 软皮轻甲首刀实景 · v125

2026-10-17。事实：继续“保持怪诞方向，增强盔甲和轮廓辨识”。新胸衣192、近肩189、远肩190按标准提取／明确curated选择导出与实际可见A、artist设计B，仅做整数平移，实际运行Body159v003的24身体层逐字节保持。18个新Texture2D实际另存v013；旧1097包大小/SHA不变，当前Production1115包（不是全部Texture2D类计数）。

实际游戏正常Enter/E/A取消/E提交同一件轻甲，随后两次正常J、原连击窗口自然过期与正常A/D转向：96观察／97原PNG、左右各首刀六相63/63、两个不同实际AttackId、第二刀结束后三帧真实Ready，0差。Root在E298后看全12张原比例裁图和两张整景；新棕皮色块比灰衣容易区分，钟盔、琥珀眼窗和近手保持可见。3.2秒静音录像在浏览器完整播放ended=true/error=null，页面截图E302后已审。身体目标72px、独立军剑.50、传统HUD隐藏；世界拾取标记仍占位。

推理：用胸肩的大形状与暖皮色增强小比例辨识是可继续的试装方向。小扣件在72px下不能承担主要识别，接下来沿相同身份制作第二、第三段及其他状态。完整默认试玩仍用原灰甲动作，新版Ready／首刀是独立试样，避免把未齐全外观直接当完整替换。

风险和边界：握柄、待机接缝与完整连招、走跑／换装／受击／死亡、特效声音及20搭配仍未完成。188和191第五相反向已保留拒绝；第一次对位误用了Bodyv001，未导入，已改实际v003。标准HD导出false-variant失败与首次导入脚本尺寸预检失败均保留；未擦改像素或量化。192第2帧一个alpha1绿点保留，不冒称源图所有非零alpha绿像素为0。首次长快照名触发Windows长路径，失败目录保留；新短名最大240字符，所有原检查保持。

运行事实：实际020436编译0，纯石像守卫Restore由已保全的三组语义RED到020948三组GREEN；随后首刀实录计数改为第二刀首次实际帧重置，再021555增量编译0，021707完整157项逐项Success、错误／警告／未运行／进行中0。v125-p1-157G冻结1512文件／3024端点0差。当前相同Source/DLL另录Ready71观察／72PNG双15，默认旧外观完整流程141观察／142PNG、三提交、原甲重拾与三段63³，均0差。手动入口按各自外观范围验三份当前证明，继续默认旧完整外观。

Restore是纯内核验证与原子深拷贝：同实体、同出生身份，接收Policy保留；NativeOwner、Codec、正式死亡奖励与磁盘Continue还未接通。v1缺少同刻调用批次和世界输入，兼容合法历史并保留数值，不能唯一重建缺失provenance。不能因三组测试通过就称完整敌人或存档完成。

[首刀播放器](../../../过程图稿与视频/2026-10-17_软皮轻甲首刀实景播放复核_v001/review-player.html) · [默认试玩](../../../军剑真实装备绑定试玩.cmd)。本轮E282–E302原件／展示副本两遍大小SHA0差，大原PNG按原文件字节无损ZIP，F原件和E根README不变。内置台账192、窗口008已24/24、累计216，下一193需按已有自动授权开新窗口；外部API0、内置费用未知。没有新用户EV049，正式完整0/15、目标active。第二、第三段新皮甲三组件输入已按真实运行身体／导入记录核对准备，尚未生成。
''',encoding='utf-8')
text='@echo off\r\npwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\\scripts\\launch-fairytale-equipment-bound-v006.ps1" -Snapshot "source-assets/production/backups/v125-p1-157G" -ProofContract "source-assets/production/checkpoint-v125-root-input-v001/manual-proof-contract-v125-v001.json"\r\n';CMD.write_bytes(text.encode('utf-8'))
x=read(P);x.update(date='2026-10-17',goal_status='active',current_task='EV048 soft-leather Ready and Primary1 actual both-facing fit trial reviewed; matching Primary2/3 inputs prepared. Continue full weapon/armor/enemy units.',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261017-021555.log',current_build_exit_code=0,latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261017-021555.log',latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,current_compiled_snapshot=S.relative_to(R).as_posix(),current_compiled_snapshot_files=1512,current_compiled_snapshot_bytes=m['bytes'],actual_registered_test_count_current=157,production_uasset_package_count_actual=1115,production_package_count_actual=1115,production_texture_count_actual=None,next_native_request=193,next_snapshot='v126',next_retention_batch='E303',current_turn_progress_classification='progress',previous_goal_turn_classification='progress',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
x['previous_full_GREEN_UE_automation']=x.get('latest_strict_UE_automation');x['latest_strict_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261017-021707/index.json',succeeded=157,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
x['generation_accounting_current']=dict(requested_count=192,current_window=8,window_requested=24,window_remaining=0,lifetime_requested_count=216,external_api_calls=0,host_fee_usd=None,authorization_events=['EV-040','EV-041'],automatic_next_window_authorized=True)
x['latest_visual_runtime_proof']=dict(report=pin(doc),archive=A.as_posix(),capture_snapshot=S.relative_to(R).as_posix(),video=pin(A/'展示副本/leather-primary1-trial-silent.mp4'),observations=96,original_PNG_including_prewarm=97,actual_committed_operations=1,actual_primary1_masks_left_right=[63,63],actual_transaction_mismatches=0,body_max_px=72,uniform_weapon_scale=.5,root_whole_views=2,root_unscaled_crop_views=12,browser_ended_error_null=True,final_actual_Ready_observations=3,audio_recorded=False,full_motion_accepted=False,formal_complete_units=0)
x['leather_primary1_v001'].update(actual_art_import=pin(R/'UnrealGame/Saved/Bootstrap/leather-primary1-v002-v001-import-20261016-180837-920536.json'),actual_new_Texture2D=18,actual_native_trial=pin(A/'原件/runtime-report.json'),review=pin(review),only_Ready_and_Primary1=True,default_complete_art_replaced=False,full_animation_accepted=False)
x['stone_guard_restore_v001'].update(actual_UE_GREEN=pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261017-020948/index.json'),actual_full_GREEN=pin(R/'UnrealGame/Saved/Automation/FirstRoom-20261017-021707/index.json'),native_owner_persistence=False,formal_complete_units=0)
x['latest_native_review_player']=V.relative_to(R).as_posix();x['latest_native_review_browser_playback']=dict(tab_id='19',duration=3.2,ended=True,error=None,retention='E302');x['current_retention_batches']=ret;x['current_turn_media_retention']=dict(first='E282',last='E302',batches=21,two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True);x['current_manual_launcher_v006']=dict(command=pin(CMD),proof_contract=pin(contracts),verified_modes=gate['native_proofs'],partial_new_art_flags_in_default=False)
x['completed_foundation_checks'].update(ue_tests_last_passed=157,ue_latest_total=157,ue_latest_failed=0,ue_latest_report='UnrealGame/Saved/Automation/FirstRoom-20261017-021707/index.json',ue_last_full_successful_report='UnrealGame/Saved/Automation/FirstRoom-20261017-021707/index.json',ue_last_full_successful_count=157,ue_verified_source_snapshot=S.relative_to(R).as_posix(),ue_current_working_source_verified=True)
x['next_work']=['Generate/fit/native-review matching soft-leather Primary2/3 using prepared verified runtime-body inputs; keep72px/hiddenHUD/independentSword.','Complete SWD/LGT common locomotion/equip/hurt/death/transitions/VFX/SFX and all5weapons/4armors/20pairings, actualacquire/drop/Save+15aux.','Admit meaningful NativeGuardOwner Stage0/production and explicitCodec/Installer/reward flow; complete Guard/enemy/Boss real art/audio/states.'];x['next_turn_priorities']=x['next_work'];write(P,x)
head='''2026-10-17 当前检查点（EV048，v125）：新版软皮轻甲已从待机推进到首刀实际试装。棕皮胸衣与短肩增强小比例辨识，保持怪诞钟盔、72px、军剑.50及传统HUD隐藏。[打开左右首刀录像](过程图稿与视频/2026-10-17_软皮轻甲首刀实景播放复核_v001/review-player.html)。

| 当前内容 | 已验证 | 仍需制作 |
| --- | --- | --- |
| 新软皮轻甲首刀 | 18新Texture2D；实际一次拾取提交、左右六相、收招后三帧Ready；12原比例裁图及3.2秒静音录像已审 | 同款第二／第三段、握柄／接缝、走跑／换装／受击／死亡与全适配 |
| 当前完整试玩 | 同构建旧灰甲141观察、三提交／重拾／三段63³；独立新版Ready双15、首刀双63均0差 | 默认完整外观继续保留，世界拾取标记仍占位 |
| 石像守卫Restore | 实际三组RED→三GREEN，完整157项严格通过；同出生状态验证与原子深拷贝 | NativeOwner／Codec／正式奖励与磁盘Continue、完整敌人美术声音 |

[事实、推理和边界](docs/production/first-batch-v2/runtime-review-leather-primary1-v125.md) · [默认试玩](军剑真实装备绑定试玩.cmd)。当前1115资源包＝旧1097不变＋新18纹理；v125-p1-157G1512文件／3024端点0差。E282–E302展示前两遍保全，F原PNG不变。正式完整0/15、目标active；图像台账192／窗口24of24／累计216，下一193按已有自动授权开新窗口，外部API0、内置费用未知。以下旧检查点保留，以本段及progress当前字段为准。

''';RM.write_text(head+RM.read_text(encoding='utf-8-sig'),encoding='utf-8');REQ.write_text(REQ.read_text(encoding='utf-8-sig')+'\n\n## 2026-10-17 EV048执行检查点 · v125\n\n沿用“保持怪诞方向，增强盔甲和轮廓辨识”。新皮甲首刀已真实导入／同件轻甲左右六相／实际收招回待机，实景原比例十二帧与3.2秒静音录像已复核；新版第二三段及其他全状态尚未完成，默认完整外观保持。未新增人类EV049或代替用户最终接受。当前157项严格测试通过，18新纹理／原1097包不变，纯守卫Restore接入通过但完整敌人与Save仍未完成。详见 [v125记录](docs/production/first-batch-v2/runtime-review-leather-primary1-v125.md)。\n',encoding='utf-8')
write(O/'checkpoint.json',dict(progress=pin(P),README=pin(RM),requirements=pin(REQ),ledger=pin(L),runtime_review=pin(doc),manual_command=pin(CMD),manual_preflight=pin(O/'manual-preflight-v006.json'),full157=True,compiled_snapshot=pin(S/'compiled-source-manifest.json'),endpoint_mismatches=0,formal_complete_units=0,goal_status='active',next_native=193,next_snapshot='v126',next_retention='E303',human_EV049_unused=True));print(json.dumps(dict(checkpoint='v125',actual_tests=157,actual_primary1_observations=96,three_current_native_modes_verified=True,default_manual_restored_to_current_build=True,formal_complete_units=0,goal_active=True),ensure_ascii=False))
