from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-checkpoint-v130-spatial-correction-v002';assert not out.exists();(out/'before').mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
progress=R/'docs/production/first-batch-v2/progress.json';readme=R/'README.md';requirements=R/'项目需求台账.md';ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
for p in [progress,readme,requirements,ledger,R/'石廊三敌原生试玩.cmd',R/'裂岩守卫三动作试样.cmd']:shutil.copy2(p,out/'before'/p.name)
suite=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261018-115254/index.json');assert (suite['succeeded'],suite['failed'],suite['succeededWithWarnings'],suite['notRun'],suite['inProcess'])==(181,0,0,0,0)
left=read(R/'过程图稿与视频/2026-10-18_石守卫三行整身原生试样_v002/原件/runtime-report.json');right=read(R/'过程图稿与视频/2026-10-18_石守卫三行整身原生试样_v003/原件/runtime-report.json')
assert left['passed'] and right['passed']
g=[o for o in right['observations'] if o.get('guard_native')];max_dx=max(o['player_ground'][0]-o['guard_native']['ground'][0] for o in g);assert max_dx<2.
correction=dict(status='RIGHT_FACING_ART_VALID_SPATIAL_RIGHT_APPROACH_NOT_VALIDATED',source_event='EV-048',original_v003_passed=True,original_checker_checks='native clocks/source/frames/pixels/facing only',actual_max_right_dx=max_dx,actual_final_player=right['observations'][-1]['player_ground'],actual_final_guard=right['observations'][-1]['guard_native']['ground'],right_dx_over60_observations=0,player_final_HP=right['observations'][-1]['player_HP'],root_previous_both_side_spatial_claim_withdrawn=True,source_and_clock_checks_remain_valid=True,Wake_and_Dormant_only_facing_plus1=True,correction='NEW normal-input body-aware route and hard actual-position oracle pending; do not alter original media/reports',formal_complete_units=0)
(out/'spatial-scope-override-v001.json').write_text(json.dumps(correction,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=read(ledger);assert l['requested_count']==227
for q in l['requests']:
 if q['request_number']==225:q['root_source_review']=dict(status='FOUR_RECOVERY_SOURCE_POSES_REVIEWED',all_curated_frames_viewed=True,trial_allowed=False,reason='Feet grounded and no second stomp. WU-to-Active body jump remains unresolved; not imported.')
 if q['request_number']==226:q['root_source_review']=dict(status='REJECTED_CONTACT_PAIR_NO_PHYSICAL_LEG_EXCHANGE',reason='Both frames repeat far leg forward. Stop same generation strategy; true layer/bone Move pilot inputs only.',trial_allowed=False)
 if q['request_number']==227:q['root_source_review']=dict(status='FOUR_CLOSED_NEAR_HAND_HURT_SOURCE_POSES_REVIEWED',all_curated_frames_viewed=True,actual_weapon_contact=False,trial_allowed=False,reason='Near hand1 now closed; actual hilt axis/masks/armor/native remain unconfigured.')
ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(progress);p.update(current_task='守卫苏醒边界已修复并严格181通过；补真正右侧绕行的硬空间验证，继续13主角全状态的持物/盔甲配准',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-114631.log',current_build_exit_code=0,current_source_uncompiled_changes=False,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_compiled_snapshot='source-assets/production/backups/v130-guard-partial-181G',current_compiled_snapshot_files=1892,current_production_packages=1226,actual_registered_test_count_current=181,current_review='docs/production/first-batch-v2/runtime-review-guard-partial-v130.md',current_status_authority='v130 actual181 GREEN, left physical trial PASS; original right-facing art trial spatial coverage insufficient, explicit override pending v009 route')
p['current_snapshot_pending']=None;p['generation_accounting_current']=dict(requested_count=227,current_window_number=10,window_requested=11,window_remaining=13,lifetime_requested_count=l['lifetime_requested_count'],external_api_calls=0,host_fee_usd=None,all_native_outputs_retained=True)
p['guard_partial_v130']=dict(source_files=223,production_files=1226,snapshot_files=1892,strict181GREEN=True,left_native_movie_frames=657,right_facing_native_movie_frames=670,original_checker_masks=[63,15,63],left_physical_approach_valid=True,right_physical_approach_valid=False,spatial_scope_override=(out/'spatial-scope-override-v001.json').relative_to(R).as_posix(),Root_reviewed_new_samples=8,root_all_movie_frames_human_reviewed=False,complete_units=0,complete_gear_combinations=0,audio_recorded=False)
progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review=R/'docs/production/first-batch-v2/runtime-review-guard-partial-v130.md';assert not review.exists()
review.write_text('''# v130：苏醒边界修复与右侧空间验证纠正

事实：原生守卫椭圆入界重分段可拒绝合法时间区间，产生约2.3秒ensure停顿并漏苏醒第1帧。首个回归用例只失败在数值前提，已保留且不当作目标RED。用实际UE内核判定与真实宽预览构造的新版用例取得真正Accepted目标RED，再准入限定分片及实际端点的无epsilon修复；同测试GREEN，全181项严格成功且0警告。保留原1秒苏醒、AI攻击/HP/回执和断言。

左侧新原生PID55528共657电影帧，苏醒63/待机15/蓄斧63与逐帧像素通过，最后玩家距守卫X=-151.038，HP100；21.88秒静音录像播放到末尾无错误。右朝向PID53660共670电影帧的原检查器也通过时钟/纹理/像素/朝向，但Root审图发现角色重叠，复核坐标整个过程max右偏仅1.602px、没有任何dx>60观察，末HP26.316。它不能证明真正绕到右侧，之前双侧空间通过的说法撤回。原录像/检查报告/独立metadata冻结不倒改，最新空间覆盖纠正见evidence/guard-art-v001/root-checkpoint-v130-spatial-correction-v002/spatial-scope-override-v001.json。

推理：原观察路线仅检查房间障碍，无法绕开守卫身体；下一版只改观察正常WASD路线与空间计分/独立断言，先绕上下侧，确认实际±150位置后计Ready与蓄斧覆盖。不能只以Facing当人物所在侧。Dormant/Wake两进程均原生+1；仅Ready/蓄斧已绘制双朝向，不称Wake双向。

风险与剩余：试样只含16纹理三行动作，其他守卫动作仍程序占位。221/223/226行走连续不换腿，全部拒绝，先准备真实分层骨骼Move隔离pilot，尚未生成7组件。跺击WU→Active约29.7px上身位移未解决，不准入运行。主角Dodge4/Death5/Hurt2274源候选已审，Hurt近手纠错成立；剑柄轴、mask、甲与实际全状态仍待适配。Source223/Production1226/快照1892，正式完整0/15、完整搭配0/20，目标active。E411/E412原件及展示无损ZIP逐成员两遍大小/SHA0，旧失败E392/E396保留；声音未录入本批静音视频。
''',encoding='utf-8')
prefix='''2026-10-18 当前检查点（EV048，v130）：守卫苏醒边界拒绝已修复，181项严格回归通过。左侧657帧原生复测收齐三行动作并通过像素核对；右朝向670帧的空间接近验证不足，已明确纠正，正补绕行与位置断言。[本轮事实与边界](docs/production/first-batch-v2/runtime-review-guard-partial-v130.md)。

| 内容 | 已建立 | 仍需完成 |
| --- | --- | --- |
| 守卫16纹理 | 苏醒6／待机4／蓄斧6已导入；左侧21.88秒原生复测通过 | 真正右侧接近、其他动作、声音与完整敌人 |
| 主角全状态源 | 闪避4、死亡5、近手闭合的受挫4已审 | 独立武器接触、轻甲分层和实际运行 |
| 行走及跺击 | 错误步态已拒绝；分层骨骼pilot标准输入备好 | 真实换腿／足锁、跺击上身衔接 |

Source223／Production1226／快照1892；正式完整0/15、完整搭配0/20。生成227，窗口10用11余13，外部API0、内置计费未知。以下历史检查点和入口保留，以本段及progress当前字段为准。

'''
readme.write_text(prefix+readme.read_text(encoding='utf-8-sig'),encoding='utf-8')
requirements.write_text(requirements.read_text(encoding='utf-8-sig')+'\n\n2026-10-18 EV048持续实施/v130：守卫苏醒边界已真实RED→GREEN，181严格全过。左侧原生657帧复测通过；右朝向670帧原checker空间断言不足，Root复核坐标后明确撤回双侧空间通过并补正常绕行验证，原件不改。主角13全状态源候选已审，未实际装备配准；错误步态221/223/226拒绝，真骨骼Move仅准备pilot。正式完整0/15，目标active，非新增用户事件。\n',encoding='utf-8')
for name,flags in [('石廊三敌原生试玩.cmd','-LightArtTrial'),('裂岩守卫三动作试样.cmd','-LightArtTrial -GuardPartialArt')]:
 (R/name).write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v003.ps1" '+flags+'\npause\n',encoding='utf-8')
(out/'checkpoint-manifest.json').write_text(json.dumps(dict(version='v130',strict181GREEN=True,left_physical_native_passed=True,right_spatial_coverage_valid=False,formal_complete_units=0,files=[pin(q) for q in [progress,readme,requirements,ledger,review,out/'spatial-scope-override-v001.json',R/'石廊三敌原生试玩.cmd',R/'裂岩守卫三动作试样.cmd',Path(__file__)]]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=out.as_posix(),strict181GREEN=True,right_spatial_coverage=False,source223=True,formal_complete_units=0)))
