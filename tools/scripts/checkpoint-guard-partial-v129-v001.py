from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-checkpoint-v129-v001';assert not out.exists();(out/'before').mkdir(parents=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
progress=R/'docs/production/first-batch-v2/progress.json';ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';requirements=R/'项目需求台账.md';readme=R/'README.md';cmd=R/'石廊三敌原生试玩.cmd'
for p in [progress,ledger,requirements,readme,cmd]:
 d=out/'before'/p.name;shutil.copy2(p,d);assert sha(p)==sha(d)
suite=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261018-111625/index.json');assert suite['succeeded']==180 and all(suite[k]==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
runtime=read(R/'过程图稿与视频/2026-10-18_石守卫三行整身原生试样_v001/原件/runtime-report.json');assert runtime['passed'] is False and (runtime['WakeMask'],runtime['ReadyMask'],runtime['WindupMask'])==(61,15,63)
l=read(ledger);assert l['requested_count']==224 and all(q['status']!='requested_pending' for q in l['requests'])
for q in l['requests']:
 n=q['request_number']
 if n==221:q['root_source_review']=dict(status='REJECTED_WHOLE_MOVE_ACTION',reason='Both contact halves repeat same physical leading leg; no alternating stride.',runtime_imported=False)
 if n==223:q['root_source_review']=dict(status='REJECTED_WHOLE_MOVE_ACTION_AND_SOURCE_CROP',reason='Source right-edge axe core cropped and same physical leading leg repeated. E393/E397 preserved; no local painting or hidden clipping repair.',runtime_imported=False)
 if n==222:q['root_source_review']=dict(status='SOURCE_POSE_CANDIDATE_AND_FAR_FOOT_VARIANT_ACCEPTED',registration='388px standing basis, near-support delta propagation; future trial only',trial_allowed=False,final_accepted=False)
 if n==224:q['root_source_review']=dict(status='TWO_CURATED_SOURCE_POSE_CANDIDATES_REVIEWED',reason='Both feet grounded, second pose compressed, same fixed axe grip; registration/native trial pending',trial_allowed=False,final_accepted=False)
 if n in [218,219,220]:q['root_source_review']=dict(status='BODY_ONLY_SOURCE_POSE_CANDIDATES_REVIEWED',all_curated_frames_viewed=True,reason='Same bell helmet/gray cloth/brown boots, articulated slip/recoil/collapse; floor/grip/equipment/native trial pending',runtime_imported=False,final_accepted=False)
write(ledger,l)
p=read(progress);p.update(current_task='修复实际守卫苏醒边界的authoritative interval拒绝，再复测三行整身原生覆盖；继续主角全状态和守卫剩余源动作',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-111152.log',current_build_exit_code=0,current_source_uncompiled_changes=False,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_compiled_snapshot='source-assets/production/backups/v129-guard-partial-180G',current_compiled_snapshot_files=1869,current_production_packages=1226,actual_registered_test_count_current=180,current_review='docs/production/first-batch-v2/runtime-review-guard-partial-v129.md',current_status_authority='v129 actual strict180 GREEN; partial Guard native coverage RED preserved, no full unit accepted')
p['generation_accounting_current']=dict(requested_count=224,current_window_number=10,window_requested=8,window_remaining=16,lifetime_requested_count=l['lifetime_requested_count'],external_api_calls=0,host_fee_usd=None,all_native_outputs_retained=True)
p['fairytale_guard_partial_v129']=dict(source_files=222,production_files=1226,approved_partial_textures=16,actual_full_suite_180_GREEN=True,actual_native_passed=False,actual_WakeMask=61,actual_ReadyMask=15,actual_WindupMask=63,guard_HP=185,diagnostic_Knight_Bat=True,normal_J_full_clear=False,audio_recorded=False,root_visible_samples_viewed=6,root_all_frames_viewed=False,source_221_and_223_rejected=True,complete_units=0,issue='Actual authoritative interval rejection and ensure stall; numerical boundary investigation in progress')
write(progress,p)
review=R/'docs/production/first-batch-v2/runtime-review-guard-partial-v129.md';assert not review.exists()
review.write_text('''# v129 守卫三行动作：编译通过，实景覆盖失败已保留

事实：苏醒6、待机4、蓄斧6，共16张实际Texture2D已导入；222份Source、1226个Production包与实际DLL冻结，180项严格回归全部成功、无警告。原终结死亡闪色测试实际出现3成功1失败后，修复仅让死亡展示年龄到.22时清除旧闪色，四项专项及完整180通过。

原生PID55804按正式房间出生守卫，Knight/Bat用公开诊断伤害推进，守卫保持185HP。1537电影帧、53.52秒原时序静音录像：WakeMask61缺第1帧，Ready15、蓄斧63，Dormant48观察，故整轮RED。日志确有守卫authoritative interval拒绝与约2.3秒ensure停顿。完整失败原件E392保全，展示视频及17阶段原比例样本E396保全；Root已查看Dormant、Wake5、Ready0、蓄斧0/5及程序占位6张，不能据此宣称全部17样本或全部电影帧人工审完。

推理：当前优先检查苏醒椭圆交点重算时浮点舍入导致时间不能前进的边界；不屏蔽断言、不缩短苏醒、不放宽完整覆盖。现HUD已启动加载全16纹理，不能把缺帧直接归因于贴图首次加载。

风险与剩余：其余守卫动作仍明确程序占位，左右完整验收、声音混音及正常J全通关尚未完成。Move221/223两批整行拒绝，223另有斧头原图裁边；改为先验证相反触地关键姿态。Stomp222接受远脚跺击源变体并记录原近脚要求失败，224两张接地/压低源候选已审，尚未导入。主角218–220的4/4/5张身体动作源候选已审，装备和握点配准待做，未消除运行中的静态Ready缺口。正式完整0/15、完整搭配0/20，目标继续active。
''',encoding='utf-8')
prefix='''2026-10-18 当前检查点（EV048，v129）：守卫苏醒／待机／蓄斧16纹理已实际导入，180项严格回归通过；原生试样发现苏醒漏一帧与时间区间拒绝，失败录像已保留，正在修复。[本轮事实与边界](docs/production/first-batch-v2/runtime-review-guard-partial-v129.md)。

主角闪避4／受挫4／死亡5源帧已逐张审过，尚待配准与装备适配。守卫行走221／223已拒绝；不将错误步态接入。当前222份Source／1226资源包／1869快照文件；完整0/15、20搭配0/20。图像224，窗口10用8余16，外部API0，内置计费未知。以下检查点及更早入口为历史，以当前状态为准。

'''
readme.write_text(prefix+readme.read_text(encoding='utf-8-sig'),encoding='utf-8')
requirements.write_text(requirements.read_text(encoding='utf-8-sig')+'\n\n2026-10-18 EV048持续实施／v129：保持怪诞钟盔、清晰盔甲轮廓、小比例与隐藏HUD。16守卫纹理已导入，严格180全GREEN；实际守卫苏醒漏帧与interval拒绝仍RED，原件/录像E392/E396保留，正在复现修复。13主角源帧审过但未运行接入；221/223步态拒绝，222远脚跺击源变体明确记录原近脚规则失败；正式完整0/15，目标active。不是新的用户需求事件。\n',encoding='utf-8')
cmd.write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v002.ps1" -LightArtTrial\npause\n',encoding='utf-8')
partial=R/'裂岩守卫三动作试样.cmd';assert not partial.exists();partial.write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v002.ps1" -LightArtTrial -GuardPartialArt\npause\n',encoding='utf-8')
write(out/'checkpoint-manifest.json',dict(version='v129',actual_full180GREEN=True,actual_native_partial_RED=True,formal_complete_units=0,scope='Current checkpoint; active numerical-boundary repair pending',files=[dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=sha(q)) for q in [progress,ledger,requirements,readme,cmd,partial,review,Path(__file__)]]))
print(json.dumps(dict(checkpoint=out.as_posix(),full180GREEN=True,native_partial_passed=False,formal_complete_units=0)))
