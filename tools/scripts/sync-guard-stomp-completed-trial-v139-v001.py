"""Sync durable current aliases to actual193/native trial; formal goal remains active."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snapshot=R/'source-assets/production/backups/v139-Stomp193G';cm=read(snapshot/'compiled-source-manifest.json')
assert(cm['source_files'],cm['production_files'],cm['passed'],cm['failed'])==(262,1332,193,0)
for prefix,count in [('UnrealGame/Source/',262),('UnrealGame/Content/Production/',1332)]:
 expected=[x for x in cm['files']if x['path'].startswith(prefix)];assert len(expected)==count
 actual=[q for q in (R/prefix).rglob('*')if q.is_file()];assert{q.relative_to(R).as_posix()for q in actual}=={x['path']for x in expected}
 for x in expected:
  a=pin(R/x['path']);assert(a['bytes'],a['sha256'])==(x['bytes'],x['sha256'])
root=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/root-native-checkpoint-v001'
review=root/'Root-Stomp-native-and-visible-review-v139-v001.json';v=read(review);assert v['scoped_gray_fallback_removed'] and v['both_complete_silent_videos_actually_played_to_end'] and not v['FinalAccepted']
adoption=root/'manual-v010-adoption-receipt-v001.json';assert read(adoption)['success']
retentions=[]
for n,topic in [(541,'native-left'),(542,'native-right'),(543,'review-media'),(544,'browser-playback'),(545,'record-and-launcher')]:
 p=E/f'2026-10-18-OurgameUE-GuardStomp-{topic}-v{n}/E-retention-index-v001.json';d=read(p)
 assert d['verification_passes']==2 and d['source_and_member_hash_mismatches']==0;retentions.append(pin(p))
ledgerpath=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';ledger=read(ledgerpath)
assert ledger['requested_count']==248 and ledger['batch_requested_count']==8 and ledger['remaining_batch_requests']==16 and ledger['lifetime_requested_count']==272 and ledger['external_api_calls']==0
delivery=dict(id='guard-Stomp-native-v139',type='bounded_native_action_trial',native_source_ids=[245,248],source_images_this_turn=list(range(242,249)),strict_tests=193,
 compiled_snapshot=pin(snapshot/'compiled-source-manifest.json'),review=pin(review),retention=retentions,native_sides=[-1,1],source_frames=6,
 gray_fallback_removed=True,visual_polish_remaining=True,formal_complete_units=0,FinalAccepted=False)
assert not any(x.get('id')==delivery['id']for x in ledger['derived_deliveries']);ledger['derived_deliveries'].append(delivery);dump(ledgerpath,ledger)
p=R/'docs/production/first-batch-v2/progress.json';d=read(p)
d.update(updated_utc=datetime.now(timezone.utc).isoformat(),current_task='v139跺击A2/R4双侧原生接入及193回归通过；可玩试样保留，收招滑移/身形回接待精修，下一步Move两触地组件pilot和现成Dodge32接合',
 goal_status='active',completed_content_units=0,current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-200017.log',current_build_exit_code=0,
 latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261018-200017.log',latest_build_attempt_exit_code=0,
 ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,
 current_compiled_snapshot='source-assets/production/backups/v139-Stomp193G',current_compiled_snapshot_files=len(cm['files']),current_compiled_snapshot_bytes=sum(x['bytes']for x in cm['files']),
 last_fully_green_checkpoint='v139-Stomp193G',current_production_packages=1332,production_package_count_actual=1332,production_uasset_package_count_actual=1332,ue_actual_total_production_files=1332,
 production_texture_count_actual=None,production_texture_counts_by_group=None,production_texture_count_scope='1332 is the actual Production file/package set. New6 individually native Texture2D verified; old1326 unchanged. Whole-tree native Texture2D class count has not been recomputed.',
 actual_registered_test_count_current=193,current_status_authority='v139 actual Source262/Production1332/strict193 GREEN; both native Aid2 cycles, 12phases/fouradjacent joins/source50/actual quad/source optics passed; E541–545/Root still review and full silent playback. Gray fallback removed for Stomp; late translation and Ready1 shape jump remain. Full0/15, combos0/20, active.',
 current_source_verification_scope='Fresh compiled v139 Source262/Production1332 exact set and file hashes, DLL/full193 snapshot, v010 manual193 preflight and bilateral native source50 optical proof. Historical suffixed fields retain their original scope.',
 current_review='Bounded Stomp gray fallback closure and native binding passed; source shape transitions/sliding require polish. No complete unit or combination acceptance.',
 current_turn_progress_classification='progress: Guard Stomp active/recovery actual bilateral native trial; full units and combinations remain open',
 current_snapshot_pending=None,next_snapshot='Create fresh snapshot after next actual Source change and required verification; current v139-Stomp193G.',
 next_native_request=249,next_retention_batch='E546',next_media_retention_batch='E546',next_E_retention_number=546,
 latest_native_review_player='Both complete silent Stomp MP4s played in IAB2/tab4 to ended true, loop false, error null; E544 browser screenshots reviewed. Not continuous audio acceptance.',
 current_turn_media_retained=True)
d['previous_current_retention_batches_before_v139']=d.get('current_retention_batches');d['current_retention_batches']=retentions
d['latest_strict_UE_automation']=dict(report=cm['full_suite'],succeeded=193,failed=0,warnings=0,notRun=0,inProcess=0,actual_registry=193,scope='Original190 targets retained; three Stomp semantic REDs now GREEN in full193')
d['generation_accounting_current']=dict(requested_count=248,current_window_number=11,window_requested=8,window_remaining=16,lifetime_requested_count=272,external_api_calls=0,host_fee_usd=None,all_native_outputs_retained=True)
d['current_generation_accounting']=dict(requested=248,window=ledger['current_window'],remaining=16,lifetime=272,external_api_calls=0,host_fee_usd=None,automatic_follow_on_batches_authorized=True)
d['current_manual_launcher_v010']=pin(adoption);d['current_guard_room_manual_trial']=pin(adoption)
d['current_guard_Stomp_trial_v139']=delivery
d['stomp_v139_work_in_progress']=dict(source_files=262,production_files=1332,source_compiled=True,last_test_source_files=262,last_test_report=cm['full_suite']['path'],registered_tests=193,
 old_tests_passed=190,new_expected_semantic_RED=0,all_tests_green=True,stage0_semantic_RED_preserved=3,overlay_rows_imported=True,native_stomp_cycle_verified=True,
 native_stomp_complete=False,manual_current_checkpoint_ready=True,old44_profile_retained=True,Root_rejected_sources=[224,242,243,244,246,247],
 Active245_limited_source_fit_approved=True,Recovery248_authored_late_return_limited_approved=True,last_E_retention=545,native_calls_this_turn=7,requested_count=248,formal_complete_units=0,
 native_stomp_complete_false_reason='Binding/clock coverage passed, visible sliding and ending shape transition still require polish; audio and full enemy states remain open.')
packages=[q for q in (R/'UnrealGame/Content/Production').rglob('*')if q.is_file()];assert len(packages)==1332 and all(q.suffix=='.uasset'for q in packages)
d['production_package_counts_by_group']=dict(sorted(Counter(q.relative_to(R/'UnrealGame/Content/Production').parts[1]if len(q.relative_to(R/'UnrealGame/Content/Production').parts)>2 else q.relative_to(R/'UnrealGame/Content/Production').parts[0]for q in packages).items()))
d['next_turn_priorities']=['Guard Move: actual seven-component source then only two opposite ground-contact pilot poses; never reuse rejected221/223/226 as valid sixframe walk.',
 'Hero SWD/LGT Dodge32: existing source pack, exact limited import and real400ms state/equipment/join verification; no need to regenerate whole body/armor rows.',
 'Refine Stomp recovery-to-Ready and audible VFX/SFX/state transitions before claiming a complete enemy.',
 'Continue remaining weapons/armors/enemies/Boss and20 combinations under full original scope.']
dump(p,d)
readme=R/'README.md';text=readme.read_text(encoding='utf-8-sig');first,rest=text.split('\n\n',1)
assert first.startswith('2026-10-18 v139制作中：')
prefix='''2026-10-18 当前检查点（EV048，v139）：石像守卫跺击的落脚2相／收招4相已接入，左右真实AI跺击不再切回灰色占位，完整193项严格通过。保留小比例、怪诞盔甲轮廓和隐藏HUD；当前仍是可玩试样，收招轻微滑移及回待机身形跳变继续精修。[试玩](裂岩守卫跺击试玩.cmd) · [运行记录](docs/production/first-batch-v2/runtime-review-guard-Stomp-v139.md)。

| 内容 | 当前实际状态 | 剩余 |
| --- | --- | --- |
| 守卫跺击 | 原预警6＋新落脚2／收招4；左右472／499原生电影帧、实际回Ready1；50资源驻留 | 收招作者横移／膝甲与身形衔接、足锁细修 |
| 构建与试玩 | Source262／Production1332／193项全过；v010六个手动入口 | 正式完整0/15、完整搭配0/20，目标active |
| 下一工作 | Guard Move七组件源先做两触地pilot；已有Dodge32源包 | Move未接入；Dodge32未导入；完整VFX/SFX与其余装备敌人继续 |

操作：Enter开局，E穿甲／交互，WASD移动，J攻击，Shift闪避，Space跳跃，R重开。两段完整静音录像与原幅接续已审；前置Knight／Bat为明确诊断清理，不能当作整房手动通关或声音验收。E541–545两遍SHA保全。图像请求248／窗口11用8余16／累计272（另最初3张），外部API0、内置费用未知。

以下是历史检查点；当前状态以上述v139及progress当前字段为准。

'''
readme.write_text(prefix+rest,encoding='utf-8')
requirements=R/'项目需求台账.md'
with requirements.open('a',encoding='utf-8')as f:f.write('\n\n2026-10-18 EV048持续实施／v139：沿用怪诞卡通、小比例与清楚盔甲轮廓，石像守卫跺击Active2／Recovery4实际导入，原1326保持、当前1332；完整193严格GREEN。真实左右首个Aid2自然跺击472／499电影帧、各12相／四原回调相邻接续／50资源与固定源像素／正常命中通过；Root原幅、相位、接续和完整静音播放审阅后保留有限可玩试样，新增跺击试玩并升级六入口v010。收招作者位移可能滑脚，回Ready1仍有身形／头盔跳变；Move未准入、Dodge32未导入，正式0/15、搭配0/20，目标active。E541–545展示前两SHA保全，旧稿与失败源保留。本轮242–248共7次内置，当前248／窗口11用8余16／累计272（另最初3张），外部API0、费用未知；不是新用户需求或最终美术接受。见 [v139实景记录](docs/production/first-batch-v2/runtime-review-guard-Stomp-v139.md)。\n')
receipt=root/'current-status-sync-v139-v001.json'
assert not receipt.exists();dump(receipt,dict(schema='Root-Stomp-v139-current-status-sync-v001',Source262_Production1332_current_hashes_unchanged=True,
 actual_full193_green=True,final_units=0,goal_status='active',outputs=[pin(q)for q in [p,readme,requirements,ledgerpath]],E_last=545,E_next=546,
 generation_counters_unchanged=True,old_status_and_ledger_before=root.joinpath('before').as_posix(),FinalAccepted=False))
print(json.dumps(dict(status=pin(receipt),current_source=262,current_production=1332,full_GREEN=193,formal_units=0,E_last=545,next_request=249),ensure_ascii=False))
