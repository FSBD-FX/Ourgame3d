"""Record only actual strict build, retained spatial trials and explicit review receipts."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
out=R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-checkpoint-v131-v001'
assert not out.exists()
snapshot=R/'source-assets/production/backups/v131-guard-partial-181G';m=read(snapshot/'compiled-source-manifest.json')
assert (m['source_files'],m['production_files'],m['strict_registered_tests'],len(m['files']))==(223,1226,181,1919)
for row in m['files']:
 q=R/row['path'];assert q.stat().st_size==row['bytes'] and sha(q)==row['sha256'],q
suite=read(R/m['full_suite']['path']);assert len(suite['tests'])==181 and all(x['state']=='Success' and x['errors']==x['warnings']==0 for x in suite['tests'])
trials=[]
for side,suffix,batch in [(1,'sideR_route_v004','2026-10-18-OurgameUE-guard-true-right-native-ZIP-v420'),(-1,'sideL_route_v005','2026-10-18-OurgameUE-guard-true-left-native-ZIP-v421')]:
 b=R/'过程图稿与视频'/('2026-10-18_石守卫三行整身原生试样_'+suffix)
 r=read(b/'原件/runtime-report.json');v=read(b/'原件/independent-guard-art-partial-v010.json');midx=read(b/'source-version-status-index.json');ret=read(E/batch/'E-retention-index-v001.json')
 assert r['passed'] and v['passed'] and r['actual_approach_side']==side and r['spatial_approach']['strict_point'] and r['spatial_approach']['player_HP']==100
 assert v['masks']=={'Wake':63,'Ready':15,'AxeWindup':63} and r['guard_final_HP']==185 and r['guard_incoming_receipt_count']==0
 assert ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0 and ret['source_deleted'] is False
 assert midx['presentation_frame_retention']['decoded_frames']==len(r['observations']) and midx['presentation_frame_retention']['every_native_frame_has_one_encoded_frame']
 trials.append(dict(side=side,archive=b.relative_to(R).as_posix(),process_id=r['process_id'],movie_frames=len(r['observations']),masks=v['masks'],actual_final=r['spatial_approach'],E_batch=batch,video=midx['video'],presentation_frame_retention=midx['presentation_frame_retention'],Wake_facings=sorted({d['Selection']['Facing'] for o in r['observations'] for d in o['guard_draws'] if d['Selection']['Clip']=='Wake'})))
assert len({x['process_id'] for x in trials})==2
review=read(R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-v131-native-visible-review-v001.json')
assert review['reviewed_samples'] and review['both_decoded_last_frames_viewed'] and review['formal_complete_units']==0
playback=read(R/'过程图稿与视频/2026-10-18_守卫真实双侧录像播放核验_v001/原件/playback.json')
assert len(playback['videos'])==2 and all(x['ended'] and x['error'] is None for x in playback['videos'])
(out/'before').mkdir(parents=True)
progress=R/'docs/production/first-batch-v2/progress.json';readme=R/'README.md';requirements=R/'项目需求台账.md';ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
for q in [progress,readme,requirements,ledger,R/'石廊三敌原生试玩.cmd',R/'裂岩守卫三动作试样.cmd']:shutil.copy2(q,out/'before'/q.name)
l=read(ledger);assert l['requested_count']==227
for request in l['requests']:
 if request['request_number']==227:
  request['root_source_review'].update(source_composite_contact_reviewed_all_four=True,authored_transform_candidate='source-assets/production/fairytale-hero-state-gap-v001/hurt227-SWD-four-fit-v002/candidate-v002',offline400ms_nonloop_reviewed=True,LGT_native_pending=True,native_weapon_contact=False,trial_allowed=False)
ledger.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(progress);p.update(current_task='守卫三行动作真实左右侧试样已验证；继续受挫四帧军剑与轻甲配准、完整守卫动作接入',current_build=m['current_build']['path'],current_build_exit_code=0,current_source_uncompiled_changes=False,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_compiled_snapshot=snapshot.relative_to(R).as_posix(),current_compiled_snapshot_files=1919,current_production_packages=1226,actual_registered_test_count_current=181,current_review='docs/production/first-batch-v2/runtime-review-guard-spatial-v131.md',current_status_authority='v131 actual181 strict GREEN; two actual spatial-side partial trials and retained samples reviewed; formal0/15')
p['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261018-122316.log';p['current_snapshot_pending']=None
p['current_compiled_snapshot_bytes']=sum(row['bytes'] for row in m['files'])
p['current_source_verification_scope']='Actual v131 strict181 GREEN; exact Source223/Production1226/1919 compiled input pins. Native right689 and left658 real reached-side partial trials with playerHP100/Guard185/0incoming, qualified Ready15/Windup63, unique Wake63 at facing+1, no final art/audio/full-combat acceptance.'
p['current_turn_media_retention']=dict(first='E419',last='E424',two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True,large_native_originals='E420/E421 exact ZIP members; F original PNGs unchanged')
p['current_turn_media_retained']=dict(F_E_batches=['E419','E420','E421','E422','E423','E424'],hash_mismatches=0,verification_passes=2,root_readme_unchanged=True,large_originals_lossless_ZIP=True)
p['guard_partial_v131']=dict(source_files=223,production_files=1226,snapshot_files=1919,strict181GREEN=True,trials=trials,source_scope='v009 observer-only route/position changes; gameplay unchanged',Wake_dual_facing_validated=False,Root_visible_review=pin(R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-v131-native-visible-review-v001.json'),complete_units=0,complete_gear_combinations=0,audio_recorded=False)
p['hero_Hurt227_SWD_sourcefit_v002']=dict(four_source_composites_contact_reviewed=True,offline400ms_nonloop_playback_ended=True,Root_review=pin(R/'docs/production/first-batch-v2/evidence/guard-art-v001/root-Hurt227-SWD-four-sourcefit-visible-review-v001.json'),E_batch='2026-10-18-OurgameUE-Hurt227-SWD-four-fit-v422',authored_grip_axis=True,zero_pop=False,LGT_native_pending=True,TrialAllowed=False)
for name,flags in [('石廊三敌原生试玩.cmd','-LightArtTrial'),('裂岩守卫三动作试样.cmd','-LightArtTrial -GuardPartialArt')]:
 (R/name).write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v004.ps1" '+flags+'\npause\n',encoding='utf-8')
p['current_guard_room_manual_trial']=dict(command=pin(R/'石廊三敌原生试玩.cmd'),guard_art_command=pin(R/'裂岩守卫三动作试样.cmd'),launcher=pin(R/'tools/scripts/launch-guard-room-native-trial-v004.ps1'),snapshot=snapshot.relative_to(R).as_posix(),automatic_input=False,diagnostic_damage=False,HUD_hidden=True,partial_guard_art_only=True)
progress.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=R/'docs/production/first-batch-v2/runtime-review-guard-spatial-v131.md';assert not doc.exists()
doc.write_text('''# v131：真实左右侧观察与三行动作试样

事实：仅现有观察程序新增普通WASD三段路线，绕开实际身体后才计入空间覆盖；未改守卫AI、伤害、生命或时钟。UE构建122316退出0，严格181项全Success、0错误警告。相同构建的新右侧PID46396记录689帧，左侧PID6728记录658帧，两侧独立位置与像素/FIFO核验通过。右侧真实终点dx144.766/dy−2.198，左侧dx−151.038/dy−2.201，玩家均100HP、守卫185HP且无incoming receipt。坐标均为world ground单位；旧v130文档的1.602px应读作1.602 world ground单位。两侧Wake63/Ready15/Windup63收齐；两次Wake仍只有实际+1朝向，不能称苏醒双朝向。

推理：原右朝向试样把Facing当作所在侧，曾卡在守卫身体。新门逐帧检查真实侧向距离、半径、纵向偏差；蓄斧后半程只允许在真实锁定后纵向避让。原失败与范围纠正保留，不倒改旧报告。本次正常试玩入口不使用观察输入或诊断伤害，已绑定当前构建。

展示核验：新录像保留689/658个原生帧各一次，微秒时基，原始时间戳舍入误差最大约0.349/0.330ms；F全部原件与展示以无损ZIP在E420/E421逐成员两遍SHA保全。Root实际抽样与末帧对照、浏览器播放结束记录另存。旧浏览器灰色尾图与原生末帧不同；不据此推断native callback错帧。新v010展示多一个末尾重复帧的失败副本也保留，新v011已通过帧数核验。

风险与剩余：本批只含苏醒6、待机4、蓄斧6共16纹理。其余守卫动作仍明确程序占位，Knight/Bat仍由公开诊断伤害清除，录像静音，未证明普通J全战或完整敌人。主角受挫闭握源四帧已审，军剑作者配准与轻甲适配继续；错误换腿步态不接入。Source223/Production1226/快照1919；正式完整0/15、完整搭配0/20，目标active。图像227，本轮无新增生成、外部API0，内置费用未知。
''',encoding='utf-8')
prefix='''2026-10-18 当前检查点（EV048，v131）：守卫苏醒／待机／蓄斧三行动作已在同一构建完成真实左右侧复测，玩家均满生命；181项严格回归通过。[本轮事实与边界](docs/production/first-batch-v2/runtime-review-guard-spatial-v131.md) · [当前试玩](裂岩守卫三动作试样.cmd)。

| 内容 | 已实际验证 | 仍需完成 |
| --- | --- | --- |
| 守卫三行动作 | 16纹理；右689／左658原生帧，真实位置与像素核验、录像抽样已审 | 其余动作、完整战斗、声音与最终美术验收 |
| 主角受挫持物 | 四帧闭握军剑配准候选与400ms非循环离线预览已审 | 棕皮轻甲分层、回接变化与实际运行 |
| 当前构建 | Source223／Production1226／快照1919；HUD隐藏、小比例保持 | 正式完整0/15、完整搭配0/20 |

生成227，窗口10用11余13，外部API0、内置计费未知。以下历史检查点保留，以本段及progress当前字段为准。

'''
readme.write_text(prefix+readme.read_text(encoding='utf-8-sig'),encoding='utf-8')
requirements.write_text(requirements.read_text(encoding='utf-8-sig')+'\n\n2026-10-18 EV048持续实施/v131：同构建严格181通过，正常WASD绕行后的真实左右侧三行动作试样与像素核验通过，两侧玩家100HP。原错误Facing-only空间结论和旧录像均保留，Wake仍只+1。受挫四帧持剑/轻甲继续制作，完整守卫其他动作待接入。正式完整0/15，目标active，非新增用户事件。\n',encoding='utf-8')
receipt=dict(version='v131',strict181GREEN=True,both_actual_spatial_sides_passed=True,formal_complete_units=0,complete_gear_combinations=0,trials=trials,files=[pin(q) for q in [progress,readme,requirements,ledger,doc,Path(__file__),R/'石廊三敌原生试玩.cmd',R/'裂岩守卫三动作试样.cmd']])
(out/'checkpoint-manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(checkpoint=out.as_posix(),strict181GREEN=True,both_actual_sides=True,formal_complete_units=0)))
