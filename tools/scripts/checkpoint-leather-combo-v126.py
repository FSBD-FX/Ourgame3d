from pathlib import Path
import argparse, datetime, hashlib, json, shutil

R=Path('F:/Ourgame'); D=R/'docs/production/first-batch-v2'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
    b=p.read_bytes(); return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

a=argparse.ArgumentParser(); a.add_argument('--archive',required=True); a.add_argument('--browser',required=True); a.add_argument('--retention-last',type=int,required=True); a=a.parse_args()
S=R/'source-assets/production/backups/v126-combo-161G'; A=R/a.archive; B=R/a.browser
m=read(S/'compiled-source-manifest.json'); assert m['current_automation_succeeded']==161 and m['production_packages']==1151 and m['mismatches']==0
t=read(R/m['current_automation_report']); assert (t['succeeded'],t['failed'],t['notRun'],t['inProcess'],t['succeededWithWarnings'])==(161,0,0,0,0)
assert len(t['tests'])==len({x['fullTestPath'] for x in t['tests']})==161 and all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in t['tests'])
runtime=read(A/'原件/runtime-report.json'); proof=read(A/'原件/independent-leather-combo-verification-v001.json'); playback=read(B/'原件/playback.json')
assert runtime['passed'] and not runtime['mismatches'] and runtime['leather_combo_masks_left_right_by_stage']==[[63,63,63],[63,63,63]]
assert playback['ended'] and playback['error'] is None
ret=[]; E=Path('E:/OurGame/Knight/过程图稿与视频')
for n in range(303,a.retention_last+1):
    matches=[p for p in E.iterdir() if p.name.startswith('2026-10-17-OurgameUE-') and p.name.endswith(f'-v{n}')]; assert len(matches)==1,(n,matches)
    q=matches[0]/'retention-verification-v001.json'; q=q if q.exists() else matches[0]/'source-size-SHA256.json'; v=read(q)
    assert v['verification_passes']==2 and v.get('source_and_target_hash_mismatches',v.get('source_and_retained_size_SHA_mismatches',v.get('source_and_retained_size_SHA256_mismatches')))==0
    ret.append(pin(q))
P=D/'progress.json'; L=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'; RM=R/'README.md'; Q=R/'项目需求台账.md'
O=D/'evidence/leather-combo-v001/status-checkpoint-v126'; assert not O.exists()
for p in [P,L,RM,Q]:
    q=O/'before'/p.relative_to(R); q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,q); assert p.read_bytes()==q.read_bytes()
ledger=read(L); assert ledger['requested_count']==198 and ledger['lifetime_requested_count']==222 and ledger['batch_requested_count']==6 and ledger['remaining_batch_requests']==18 and ledger['external_api_calls']==0
F=R/'source-assets/production/fairytale-lgt-readability-v003'
for row in ledger['requests']:
    n=row['request_number']
    if 193<=n<=198:
        stage=2 if n<=195 else 3
        row.update(status='native_combo_trial_verified_pending_user_acceptance',runtime_imported=True,complete_armor=False,full_motion_accepted=False,user_art_acceptance=False,formal_complete_units=0)
        row['actual_combo_trial']=pin(A/'原件/runtime-report.json'); row['assembly_freeze']=pin(F/f'primary{stage}-integer-assembly-v001/assembly-freeze-v001.json')
        row['source_index']=pin(F/('primary2-far195-small-tab-v002/primary2-eighteen-source-index-v002.json' if stage==2 else 'primary3-leather-extraction-v001/primary3-eighteen-source-index-v002.json'))
        if n==195: row['retained_boundary']='Explicit tiny far tab min160/core>=128 only; original512/256 failures retained.'
write(L,ledger)
doc=D/'runtime-review-leather-combo-v126.md'; assert not doc.exists()
doc.write_text(f'''# EV048 软皮轻甲三连斩实景 · v126

2026-10-17。事实：保持怪诞方向、增强盔甲与轮廓。新版棕皮胸衣与双肩已覆盖待机及军剑三段攻击，新增36张Texture2D实际导入；原1115包不变，当前1151包。角色最高72px、独立军剑.50、传统HUD隐藏；世界拾取白框/圆环仍为占位。

当前Source/DLL实际编译通过，守卫原生恢复、完整V2编解码与原子安装延续三组，以及旧V1磁盘接口拒绝V2边界共四组通过；随后完整161项均Success、逐项零错误警告/未运行/进行中。旧V1字节保持；守卫V2磁盘Continue、正式死亡奖励及完整敌人美术声音仍未完成。首次fixture距离错误、锁文件读取失败、真正版本边界8项RED及首次皮甲缺图均原样保留。

当前构建重录：正常拾取/取消/一次LGT提交，左右正常J三段连击、真实窗口过期与转向。{len(runtime['observations'])}条实际观测、左右各三段六相36项覆盖，六个不同攻击ID、收招Ready计数均至少3，CRC/FIFO/异步停刷及源绑定0差。静音录像已解码并浏览器播至结束，error=null。Root在E留存后复核原比例动作与整场。棕皮大色块、短肩、钟盔眼窗更易辨识，上斩/低扫有区别；握柄/拇指、接缝与净空仍须连续实战复核。

推理：继续用胸肩大形和色块增强小比例识别，扣件不承担主要识别。下一个具体缺口是同款Walk：现有六张身体仅用于独立lookdev，尚无四归属身体层；先完成实际手肩脚测量与分层，再制作三部位软皮甲和普通移动选帧，不能把站姿平移当成步行动画。

风险与边界：同款行走/换装/受击/死亡/空中/闪避、其他武器与四甲共20组合、特效音效试听、合法掉落及完整存续仍未完成。新入口只展示本次皮甲待机和三连斩；旧默认v006仍绑定v125历史构建，不是当前已通过的默认入口。历史NONRELEASE diag_v002保持其旧DLL与pending索引，不能倒改成当前完整回归。

[当前静音录像]({(A/'展示副本/leather-combo-trial-silent.mp4').as_posix()}) · [软皮三连斩试玩](F:/Ourgame/软皮轻甲三连斩试玩.cmd) · [严格161报告](F:/Ourgame/{m['current_automation_report']})。v126冻结{m['copied_files']}文件/{m['source_and_copy_checks']}端点零差；E303–E{a.retention_last}两遍大小/SHA保全，F原件/旧失败/E根README不变。内置请求198，窗口009已6/24余18，累计222；自动授权EV040/041有效、外部API0、内置费用未知。没有新EV049；正式完整0/15，目标active。
''',encoding='utf-8')
x=read(P); x.update(date='2026-10-17',goal_status='active',current_task='EV048 matching soft leather Ready and three-stage melee native trial reviewed; continue full common actions and complete first-batch units.',current_build=m['build_log'],current_build_exit_code=0,latest_build_attempt=m['build_log'],latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,current_compiled_snapshot=S.relative_to(R).as_posix(),current_compiled_snapshot_files=m['copied_files'],current_compiled_snapshot_bytes=m['bytes'],actual_registered_test_count_current=161,current_production_packages=1151,production_package_count_actual=1151,production_uasset_package_count_actual=1151,production_texture_count_actual=None,next_native_request=199,next_snapshot='v127',next_retention_batch=f'E{a.retention_last+1}',next_media_retention_batch=a.retention_last+1,current_turn_progress_classification='progress',previous_goal_turn_classification='progress',updated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
x['previous_full_GREEN_UE_automation']=x.get('latest_strict_UE_automation'); x['latest_strict_UE_automation']=dict(report=m['current_automation_report'],succeeded=161,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
x['generation_accounting_current']=dict(requested_count=198,current_window=9,window_requested=6,window_remaining=18,lifetime_requested_count=222,external_api_calls=0,host_fee_usd=None,authorization_events=['EV-040','EV-041'])
x['stone_guard_owner_v002'].update(production_applied=True,actual_version_RED='docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-clean-version-RED-v002/manifest.json',actual_GREEN='docs/production/first-batch-v2/evidence/stone-guard-owner-v002/root-owner-fourGREEN-full161-v001/manifest.json',guard_disk_V2_supported=False,formal_complete_units=0)
x['leather_combo_v001'].update(runtime_verified=True,matching_clips=['Ready','Primary1','Primary2','Primary3'],new_Texture2D=36,actual_native=pin(A/'原件/runtime-report.json'),prewarm_fix='DungeonHUD BeginPlay loads selected P2/P3 leather resources before first draw',full_motion_accepted=False,user_art_acceptance=False,formal_complete_units=0)
x['latest_visual_runtime_proof']=dict(review=pin(doc),archive=A.as_posix(),capture_snapshot=S.relative_to(R).as_posix(),video=pin(A/'展示副本/leather-combo-trial-silent.mp4'),observations=len(runtime['observations']),selected_phases=36,browser_ended_error_null=True,audio_recorded=False,full_motion_accepted=False,formal_complete_units=0)
x['current_manual_launcher_v006']['current_source_verified']=False; x['current_manual_launcher_v006']['status']='historical_v125_only; use separate current leather trial'
x['current_leather_combo_manual_trial']=dict(command=pin(R/'软皮轻甲三连斩试玩.cmd'),launcher=pin(R/'tools/scripts/launch-leather-combo-trial-v001.ps1'),archive=A.as_posix(),snapshot=S.as_posix(),only_matching_Ready_primary123=True)
x['completed_foundation_checks'].update(ue_tests_last_passed=161,ue_latest_total=161,ue_latest_failed=0,ue_latest_report=m['current_automation_report'],ue_last_full_successful_report=m['current_automation_report'],ue_last_full_successful_count=161,ue_verified_source_snapshot=S.relative_to(R).as_posix(),ue_current_working_source_verified=True)
x['current_retention_batches']=ret; x['current_turn_media_retention']=dict(first='E303',last=f'E{a.retention_last}',two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True)
x['next_work']=['Complete matching SWD/LGT Walk6 actual body decomposition and measured hand/shoulder/ground contacts before new leather rows and normal movement selection.','Complete equip/hurt/death/dodge/air actions, transitions/VFX/SFX and all5weapons/4armors/20pairings plus15aux.','Complete Guard diskV2, formal room/reward flow and full enemy/Boss actual art/audio states.']; x['next_turn_priorities']=x['next_work']; write(P,x)
head=f'''2026-10-17 当前检查点（EV048，v126）：新版软皮轻甲已接入待机与军剑三段连斩，棕皮胸衣、短肩和钟盔眼窗增强小比例辨识，保持72px、军剑.50与传统HUD隐藏。[查看实际三连斩录像]({(A/'展示副本/leather-combo-trial-silent.mp4').relative_to(R).as_posix()})。

| 当前内容 | 已实际验证 | 剩余 |
| --- | --- | --- |
| 新皮甲三连斩 | 左右36相、真实单次装备提交、预加载缺图修复；录像已审 | 握柄/接缝、同款行走/换装/受击/死亡与全适配 |
| 石像守卫存续 | 原生恢复/Codec/安装延续及V1拒绝V2四组通过；全161项严格通过 | V2磁盘Continue、正式奖励与完整敌人视听 |
| 当前试装入口 | [软皮轻甲三连斩试玩](软皮轻甲三连斩试玩.cmd)，绑定当前v126 | 仅待机/三连斩美术试装；旧默认v006仍属v125历史 |

[事实、推理和边界](docs/production/first-batch-v2/runtime-review-leather-combo-v126.md)。1151资源包＝旧1115不变＋36新纹理；v126冻结{m['copied_files']}文件/{m['source_and_copy_checks']}端点0差。世界拾取标记仍占位。图像台账198/窗口6of24余18/累计222，外部API0。正式完整0/15、目标active。以下旧检查点保留，以本段及progress当前字段为准。

'''
RM.write_text(head+RM.read_text(encoding='utf-8-sig'),encoding='utf-8')
Q.write_text(Q.read_text(encoding='utf-8-sig')+'\n\n## 2026-10-17 EV048执行检查点 · v126\n\n沿用“保持怪诞方向，增强盔甲和轮廓辨识”；新版软皮待机与三连斩已实际导入、左右36相和当前构建重录通过，完整161项严格回归通过。仍是美术试装；同款行走/受击/死亡、20搭配及完整敌人等继续制作。没有新增人类EV049，也未代替用户最终接受。详见 [v126实景记录](docs/production/first-batch-v2/runtime-review-leather-combo-v126.md)。\n',encoding='utf-8')
write(O/'checkpoint.json',dict(progress=pin(P),README=pin(RM),requirements=pin(Q),ledger=pin(L),review=pin(doc),snapshot=pin(S/'compiled-source-manifest.json'),full161=True,formal_complete_units=0,goal_active=True,human_EV049_unused=True))
print(json.dumps(dict(checkpoint='v126',full161=True,observations=len(runtime['observations']),new_Texture2D=36,formal_complete_units=0,goal_active=True),ensure_ascii=False))
