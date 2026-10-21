"""Record current verified milestone without upgrading final art/unit acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
S=R/'source-assets/production/backups/v136-Hurt187G';m=read(S/'compiled-source-manifest.json')
assert (m['source_files'],m['production_files'],m['strict_registered_tests'])==(246,1286,187)
suite=R/m['full_suite']['path'];j=read(suite);assert (j['succeeded'],j['failed'],j['succeededWithWarnings'],j['notRun'],j['inProcess'])==(187,0,0,0,0)
e=D/'evidence/Hurt-production-v001/root-checkpoint-v136-v001';assert not e.exists();(e/'before').mkdir(parents=True)
for n in ['README.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']:shutil.copy2(R/n,e/'before'/Path(n).name)
native=[]
for side,label,PID in [('left','左','37008'),('right','右','58316')]:
 A=R/('过程图稿与视频/2026-10-18_钟盔真实守卫重斧Hurt四相试样_native_'+side+'_v001')
 M=R/('过程图稿与视频/2026-10-18_钟盔轻甲真实受击与回接'+label+'侧实录_v001')
 r=read(A/'原件/runtime-report.json');v=read(A/'原件/Hurt-independent-native-verification-v001.json');index=read(A/'index.json');media=read(M/'source-version-status-index.json')
 assert r['passed'] and v['passed'] and index['independent_passed'] and str(index['process_id'])==PID and r['HurtMask']==15
 native.append(dict(side=side,process_id=PID,native_frames=len(r['observations']),HP=r['observations'][-1]['HP'],guard_HP=r['guard_final_HP'],actual_HP_loss=r['actual_HP_loss'],report=pin(A/'原件/runtime-report.json'),independent=pin(A/'原件/Hurt-independent-native-verification-v001.json'),video=media['video'],presentation_frame_retention=media['presentation_frame_retention']))
review=D/'evidence/Hurt-production-v001/root-visible-review-v136-v001.json';assert read(review)['rendered_complete_equipment'] and not read(review)['FinalAccepted']
browser=R/'过程图稿与视频/2026-10-18_钟盔轻甲双侧受击录像浏览器审阅_v001/index.json';assert read(browser)['ended_error_null_nonloop']
p=R/'README.md';old=p.read_text(encoding='utf-8-sig')
lead='''2026-10-18 当前检查点（EV048，v136）：钟盔＋棕皮轻甲＋军剑受击四相已真实接入，两侧由守卫正常重斧触发后保持装备并回到待机/行走；完整187项严格通过。[实际记录](docs/production/first-batch-v2/runtime-review-Hurt-v136.md) · [当前试玩](钟盔轻甲受击试玩.cmd)。

| 内容 | 已实际验证 | 仍需完成 |
| --- | --- | --- |
| 主角受击装备 | 32新纹理＋复用军剑；双侧359/388帧、四相/回接与固定配准像素核验、录像已审 | 扣位/握柄/足锁细修，闪避/死亡和其余搭配 |
| 守卫 | 正常J破韧/原窗恢复/死亡六相/自动coin9有实录；动作衔接仍需精修 | Move/跺击、默认调试范围框清理、最终特效/声音 |
| 当前构建 | Source246／Production1286／快照2172；小比例、隐藏传统HUD保持 | 正式完整0/15、完整搭配0/20，目标active |

本轮未生成新图像，仍233／窗口10用17余7／累计257，外部API0，内置计费未知。黄色攻击框属旧世界范围预警，普通试玩也会画；后续默认关闭，不把text_calls0当作无任何线框的证明。以下旧检查点保留，以本段及progress当前字段为准。

'''
p.write_text(lead+old,encoding='utf-8')
(R/'项目需求台账.md').open('a',encoding='utf-8').write('\n2026-10-18 EV048持续实施/v136：Hurt32实际导入后，sharedPlan/HUD真实接入，原三组3RED→3GREEN，完整187严格GREEN。Source246/Production1286/2172输入冻结；真实守卫Axe左359/右388帧四相、装备/Root/Grip/镜像/固定源像素/Ready-Walk回接首跑通过，Root已审图与完整播放，E463–E468先双SHA保全。默认黄色世界攻击范围框已确证普通试玩存在，列下一步清理；非新用户事件。扣位/足锁/声音及其他状态装备仍OPEN，正式完整0/15、目标active。\n')
p=D/'progress.json';j=read(p);j.update(current_task='钟盔轻甲持剑Hurt4双侧真实敌击/回接已接入验证；继续清理默认范围框及闪避/死亡装备适配',current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-162147.log',current_build_exit_code=0,latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261018-162147.log',latest_build_attempt_exit_code=0,current_source_uncompiled_changes=False,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_compiled_snapshot=S.relative_to(R).as_posix(),current_compiled_snapshot_files=len(m['files']),current_compiled_snapshot_bytes=sum(x['bytes'] for x in m['files']),current_snapshot_pending=None,current_status_authority='v136 actual187 strictGREEN/Source246/Production1286; realAxe→HeroHurt4 bothsides native+sourceoptical and Root retained visible review; final0/15',current_source_verification_scope='Fresh2172 compiled input pins; actual3RED→3GREEN/full187 and realGuardHit stationary4Hurt/Ready/Walk bothfacings. No final art/hiltfit/footlock/no-pop/audio/all20/fullcombat claim.',actual_registered_test_count_current=187,current_production_packages=1286,ue_actual_total_production_files=1286,production_package_count_actual=1286,production_uasset_package_count_actual=1286,current_review='docs/production/first-batch-v2/runtime-review-Hurt-v136.md',updated_utc=datetime.now(timezone.utc).isoformat(),goal_status='active',current_turn_progress_classification='progress')
j['latest_strict_UE_automation']=dict(report=pin(suite),succeeded=187,failed=0,warnings=0,notRun=0,inProcess=0,actual_registry=187,scope='current v136 complete registered suite')
j['latest_targeted_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261018-162524/index.json',succeeded=3,failed=0,scope='same frozen Hurt three groups after actual semanticRED')
j['hero_Hurt_runtime_current']=dict(stage='ACTUAL_BOTH_SIDES_NATIVE_SOURCEOPTICAL_AND_ROOT_VISIBLE_REVIEW_PASSED',Source=246,Production=1286,fullGREEN=187,compiled_snapshot=pin(S/'compiled-source-manifest.json'),three_semantic_RED_backup='source-assets/production/backups/Hurt-stage0-actual-three-semantic-RED-v001',actual_import_receipt='UnrealGame/Saved/Bootstrap/hurt32-v002-import-20261018-080500-460471.json',GPU_preload_finish_verified=True,actual_startup_resident_objects=33,native_Hurt_verified=True,native=native,root_visual_review=pin(review),browser_playback=pin(browser),all20=False,FinalAccepted=False,formal_complete_units=0)
j['current_guard_room_manual_trial']=dict(command='钟盔轻甲受击试玩.cmd',launcher='tools/scripts/launch-guard-room-native-trial-v007.ps1',checkpoint='source-assets/production/fairytale-guard-v001/root-Hurt1286-checkpoint-v001/manual-input-v001.json',actual_validate_only_passed=True,strict_registry=187,automatic_inputs=False,diagnostic_damage=False,Source=246,Production=1286)
j['current_turn_media_retention']=dict(first='E457',last='E468',two_size_SHA_passes=True,mismatches=0,E_root_README_unchanged=True,large_native_originals='E457/E460/E463/E464 exact ZIP members; F originals unchanged')
j['next_work']=['关闭full/partial/procedural三路径默认攻击范围调试矩形，保持原命中和时序并实景验证','角色SWD/LGT闪避与死亡分层/独立武器及回接','守卫Move与跺击正式动作','其他19装备搭配和首批剩余内容/声音完整验收']
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for repeat in range(2):
 for x in m['files']:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],str(p)
assert len([p for p in (R/'UnrealGame/Source').rglob('*') if p.is_file()])==246
assert len([p for p in (R/'UnrealGame/Content/Production').rglob('*') if p.is_file()])==1286
(e/'final-input-audit-v001.json').write_text(json.dumps(dict(current_compiled_snapshot=pin(S/'compiled-source-manifest.json'),checked_inputs=len(m['files']),verification_passes=2,endpoint_checks=2*len(m['files']),hash_mismatches=0,Source=246,Production=1286,fullGREEN=187,current_code_DLL_assets_match=True,goal_status='active',classification='progress',formal_complete_units=0,FinalAccepted=False,ui_world_range_rectangle_open=True,media_retained_before_view=True,native=native),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(Source=246,Production=1286,fullGREEN=187,compiled_inputs=len(m['files']),endpoint_checks=2*len(m['files']),hash_mismatches=0,formal_complete_units=0,goal_status='active',classification='progress')))
