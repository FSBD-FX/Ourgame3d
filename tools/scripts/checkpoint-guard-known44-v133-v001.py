"""Publish the verified first-Axe milestone, retaining incomplete/failing work explicitly."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/fairytale-guard-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
out=D/'evidence/guard-full-v004/root-checkpoint-v133-v001';assert not out.exists();(out/'before').mkdir(parents=True)
snapshot=R/'source-assets/production/backups/v133-guard44-184G';m=read(snapshot/'compiled-source-manifest.json')
assert (m['source_files'],m['production_files'],m['strict_registered_tests'],len(m['files']))==(231,1254,184,1991)
for row in m['files']:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
s=read(R/m['full_suite']['path']);assert s['succeeded']==184 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in s['tests'])
trials=[]
for side,suffix,batch in [(1,'sideR_v002','2026-10-18-OurgameUE-known44-Axe-right-ZIP-v446'),(-1,'sideL_v001','2026-10-18-OurgameUE-known44-Axe-left-ZIP-v447')]:
 b=R/'过程图稿与视频'/('2026-10-18_石守卫完整分期单斧周期原生试样_'+suffix);r=read(b/'原件/runtime-report.json');v=read(b/'原件/independent-known44-AxeCycle-v002.json');mi=read(b/'source-version-status-index.json');ret=read(E/batch/'E-retention-index-v001.json')
 assert r['passed'] and v['passed'] and r['actual_approach_side']==side and r['spatial_approach']['player_HP']==100 and r['guard_final_HP']==185
 assert v['masks']=={'Wake':63,'Ready':15,'AxeWindup':63,'AxeActive':15,'AxeRecovery':15} and v['startup_known_unique_count']==44
 assert len(v['covered_required_texture_paths'])==24 and ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0 and not ret['source_deleted']
 assert mi['presentation_frame_retention']['decoded_frames']==len(r['observations']) and len(mi['samples'])==24 and len(mi['joins'])==3
 trials.append(dict(side=side,archive=b.relative_to(R).as_posix(),process_id=r['process_id'],movie_frames=len(r['observations']),native_duration_s=r['duration_s'],qualified_masks=v['masks'],known_resident=44,qualified_unique=24,actual_final=r['spatial_approach'],E_batch=batch,video=mi['video'],presentation_frame_retention=mi['presentation_frame_retention'],first_native_attack_id=r['cycle_attack_id'],native_damage_window=v['native_damage_window']))
assert len({t['process_id'] for t in trials})==2
rv=D/'evidence/guard-full-v004/root-v133-native-visible-review-v001.json';review=read(rv);assert len(review['actually_viewed_detail_plates'])==4 and review['both_decoded_final_frames_viewed'] and review['FinalAccepted'] is False
browser=R/'过程图稿与视频/2026-10-18_完整守卫单斧与受击试装播放核验_v001/原件/playback.json';bv=read(browser);assert all(x['ended'] and x['error'] is None and not x['loop'] for x in bv['videos'])
ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';l=read(ledger);assert l['requested_count']==233 and l['remaining_batch_requests']==7
progress=D/'progress.json';readme=R/'README.md';requirements=R/'项目需求台账.md'
for p in [progress,readme,requirements,R/'石廊三敌原生试玩.cmd',R/'裂岩守卫三动作试样.cmd']:
 shutil.copy2(p,out/'before'/p.name)
for name in ['石廊三敌原生试玩.cmd','裂岩守卫三动作试样.cmd','裂岩守卫挥斧试样.cmd']:
 (R/name).write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v006.ps1" -LightArtTrial -GuardFullArt\npause\n',encoding='utf-8')
doc=D/'runtime-review-guard-AxeCycle-v133.md';assert not doc.exists()
doc.write_text('''# v133：守卫挥斧完整周期的左右实景验证

事实：已接入独立全状态选择器与44张已登记源纹理，其中新增28张实际Texture2D，旧1226资源包两遍SHA不变。当前Source231、Production1254、编译快照1991文件。构建131137退出0，全184项严格Success、0错误警告。右PID40736记录689帧，左PID39336记录658帧，两个真实进程均由正常Enter/E/WASD路线到达守卫侧面，玩家100HP、守卫185HP、双方0命中回执。每侧只取首AttackId1，苏醒6、实际待机4、蓄斧6、挥斧4、收招4共24张合格纹理全部实际显示；挥斧仍原200ms、收招仍1400ms，没有慢钟或跨攻击补帧。

推理：首PID7812在Enter前因异步纹理编译/渲染就绪门被拒。最小生产修复让全部批准纹理先FinishCompilation，再经过原HUD Flush；同一硬512/resource门随后对44张全过，未改观察器首用加载或游戏时钟。工具v001误按前缀限制旧三测试，v002改为六个准确名称；右v002启动器未及时落盘PID导致独立核验误拒，原失败状态保留，对相同原件重核通过。左使用v003及时落盘修复，一次native与独立核验通过。快照首次长路径副本失败也保留，NEW扩展路径版本两遍核验完成；这些工具问题不冒称游戏失败或额外动作覆盖。

画面与留档：左右Active4/Recovery4及各三组原生相邻join已实际逐帧查看，单层斧头、左右轮廓、小比例和隐藏HUD可读。完整静音MP4保留689/658个原生帧各一次，微秒时基，最大累计时间戳舍入误差0.3421/0.3302ms。F原PNG不变，E446/E447无损ZIP逐成员两遍SHA0差；28原幅抽样与裁图对照在E455，浏览器实际播放至22.940991/21.904029秒ended且无error、截图已审，在E449。

风险与剩余：蓄力转挥斧、挥斧转收招仍有较硬的姿态/脚位变化，不验收零跳变或足锁。44加载不等于44动作完整证明，本次合格覆盖24；Stun、InterruptedRecovery、Death与实际正常J战斗/掉落仍须单独跑。Move6、StompActive2、StompRecovery4保持明确占位，Knight/Bat公开诊断清除不能算普通战斗全通，录像没有声音验收。主角Hurt四帧SWD源配准可继续，Chest228黑孔、Chest232双约束不合已拒绝；新Chest233统一四相已提取，仍待正确遮挡、整数配准与实际接入。只读mask旧floodfill诊断错误已有NEW真实反例和勘误，不倒改旧报告或擦源像素。

正式完整0/15、完整搭配0/20，目标active。图像233，窗口10用17余7，累计257（另初始3参考），外部API0，内置费用未知。首批5武器/4甲/5普通敌/Boss与15依赖范围不变。
''',encoding='utf-8')
p=read(progress);p.update(current_task='守卫首个挥斧完整周期已双侧原生验证；继续破韧/中断恢复/死亡与主角受击轻甲适配',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-131137.log',current_build_exit_code=0,current_source_uncompiled_changes=False,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_compiled_snapshot=snapshot.relative_to(R).as_posix(),current_compiled_snapshot_files=len(m['files']),current_compiled_snapshot_bytes=sum(x['bytes'] for x in m['files']),current_production_packages=1254,actual_registered_test_count_current=184,current_review=doc.relative_to(R).as_posix(),current_status_authority='v133 actual184 strict GREEN; independent known44 first-Axe right689/left658 and reviewed retained media; final0/15',current_snapshot_pending=None)
p['current_source_verification_scope']='ActualSource231/Production1254/1991 input pins; same first native Axe WU6/A4/R4 at original200ms/1400ms, qualifiedWake6/Ready4. 44resident is not full44/57 motion acceptance. No final joins/footlock/audio/fullcombat.'
p['guard_known44_AxeCycle_v133']=dict(trials=trials,strict184GREEN=True,Root_visible_review=pin(rv),browser_playback=pin(browser),original_right_launcher_failure_retained=True,right_same_original_independent_rerun=True,texture_compilation_before_existing_flush=True,formal_complete_units=0,complete_gear_combinations=0)
p['hero_Hurt_LGT_source_progress_v133']=dict(Chest228_rejected_opaque_armhole=True,Chest232_rejected_two_constraint_fit=True,Chest233_four_shared_extraction_ready=True,Chest233_input_window=[128,100],original_QA_motion_warning_retained=True,readonly_mask_diagnostic_amended=True,sourcefit_pending=True,runtime_imported=False,TrialAllowed=False)
p['current_generation_accounting']=dict(requested=l['requested_count'],window=l['current_window'],remaining=l['remaining_batch_requests'],lifetime=l['lifetime_requested_count'],external_api_calls=0,host_fee_usd=None)
p['current_guard_room_manual_trial']=dict(command=pin(R/'石廊三敌原生试玩.cmd'),guard_art_command=pin(R/'裂岩守卫挥斧试样.cmd'),launcher=pin(R/'tools/scripts/launch-guard-room-native-trial-v006.ps1'),snapshot=snapshot.relative_to(R).as_posix(),automatic_input=False,diagnostic_damage=False,HUD_hidden=True,known44_guard_art_trial=True,blocked_clips=['Move','StompActive','StompRecovery'])
p['current_turn_media_retention']=dict(first='E425',last='E455',two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True,large_native_originals='E446/E447 exact ZIP members; allF originalPNG retained',unused_number='E454 reserved for next sourcefit, no generated media claimed')
progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prefix='''2026-10-18 当前检查点（EV048，v133）：守卫蓄斧—挥斧—收招已完成真实左右侧原生验证，挥斧四帧均落在原200ms内；全184项严格回归通过。[事实与剩余](docs/production/first-batch-v2/runtime-review-guard-AxeCycle-v133.md) · [当前试玩](裂岩守卫挥斧试样.cmd)。

| 内容 | 已实际验证 | 仍需完成 |
| --- | --- | --- |
| 守卫动作 | 44纹理就绪；左右689/658原生帧，各24合格动作源与三组join已审 | 破韧/恢复/死亡实战，Move与跺击缺口，衔接/足锁和音效 |
| 主角受击装备 | 军剑四帧候选；胸甲黑孔/错位已定位，新233胸衣四相已提取 | 正确遮挡与配准、运行接入、回接待机 |
| 当前构建 | Source231／Production1254／快照1991，小比例与隐藏HUD保持 | 正式完整0/15、完整搭配0/20 |

生成233，窗口10用17余7，外部API0、内置计费未知。以下历史检查点保留，以本段和progress当前字段为准。

'''
readme.write_text(prefix+readme.read_text(encoding='utf-8-sig'),encoding='utf-8')
requirements.write_text(requirements.read_text(encoding='utf-8-sig')+'\n\n2026-10-18 EV048持续实施/v133：已接入守卫44纹理独立full试样，正常原窗口的首Axe蓄斧6/挥斧4/收招4与Wake6/Ready4双侧原生验证、实际录像抽样及播放复核完成；仍需破韧/中断恢复/死亡、Move/跺击、动作衔接与声音验收。受击军剑/轻甲源纠错继续；正式完整0/15，目标active，非新增用户事件。\n',encoding='utf-8')
(out/'checkpoint-manifest.json').write_text(json.dumps(dict(version='v133',strict184GREEN=True,trials=trials,formal_complete_units=0,files=[pin(q) for q in [progress,readme,requirements,doc,ledger,rv,Path(__file__),R/'石廊三敌原生试玩.cmd',R/'裂岩守卫挥斧试样.cmd']]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=out.as_posix(),strict184GREEN=True,both_actual_AxeCycle_sides=True,formal_complete_units=0)))
