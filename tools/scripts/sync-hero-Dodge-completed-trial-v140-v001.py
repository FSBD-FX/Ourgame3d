"""Sync durable current facts after actual196, bilateral native and reviewed video."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
O=R/'docs/production/first-batch-v2/evidence/hero-Dodge32-v140-v001/root-native-checkpoint-v001'
review=O/'Root-Dodge-native-and-visible-review-v140-v001.json';v=read(review);adoption=O/'manual-v011-adoption-receipt-v001.json'
assert v['both_complete_silent_videos_played_to_end']and not v['FinalAccepted']and read(adoption)['success']
cmfile=R/'source-assets/production/backups/v140-Dodge196G/compiled-source-manifest.json';cm=read(cmfile);assert(cm['source_files'],cm['production_files'],cm['passed'],cm['failed'])==(273,1364,196,0)
retentions=[]
for n in range(546,574):
 found=[p/'E-retention-index-v001.json'for p in E.iterdir()if p.is_dir()and re.search(r'(?:_E|-v)'+str(n)+r'(?:-|$)',p.name)]
 assert len(found)==1,(n,found);p=found[0];d=read(p);assert d['verification_passes']==2 and d['source_and_member_hash_mismatches']==0;retentions.append(pin(p))
lp=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';ledger=read(lp)
assert(ledger['requested_count'],ledger['batch_requested_count'],ledger['remaining_batch_requests'],ledger['lifetime_requested_count'],ledger['external_api_calls'])==(252,12,12,276,0)
delivery=dict(id='hero-Dodge4-native-v140',type='bounded_native_action_trial',review=pin(review),compiled_snapshot=pin(cmfile),imported_Dodge_textures=32,resident_textures=33,draw_slots=9,native_sides=[-1,1],strict_tests=196,retention=retentions,guard_source_native_calls_this_turn=[249,250,251,252],native_backwards_covered=False,blocked_native_covered=False,formal_complete_units=0,FinalAccepted=False)
assert not any(x.get('id')==delivery['id']for x in ledger['derived_deliveries']);ledger['derived_deliveries'].append(delivery);dump(lp,ledger)
p=R/'docs/production/first-batch-v2/progress.json';d=read(p)
d.update(updated_utc=datetime.now(timezone.utc).isoformat(),current_task='v140 SWD/LGT四相侧闪左右原生与196回归通过，七入口v011；GuardMove仍灰色占位，新Rest252七件作者试拼仅允许代码准备，继续真实Move接入',
 goal_status='active',completed_content_units=0,current_build='UnrealGame/Saved/Bootstrap/build-editor-20261018-205540.log',latest_build_attempt='UnrealGame/Saved/Bootstrap/build-editor-20261018-205540.log',current_build_exit_code=0,latest_build_attempt_exit_code=0,
 ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,current_compiled_snapshot='source-assets/production/backups/v140-Dodge196G',current_compiled_snapshot_files=len(cm['files']),current_compiled_snapshot_bytes=sum(x['bytes']for x in cm['files']),last_fully_green_checkpoint='v140-Dodge196G',
 current_production_packages=1364,production_package_count_actual=1364,production_uasset_package_count_actual=1364,ue_actual_total_production_files=1364,production_texture_count_actual=None,production_texture_counts_by_group=None,
 production_texture_count_scope='1364 is the actual Production package set. New32 Dodge Texture2Ds individually verified, old1332 unchanged; whole-tree native class total not recomputed.',actual_registered_test_count_current=196,
 current_status_authority='v140 actual Source273/Production1364/full196 strictGREEN; bilateral outward unblocked SWD/LGT Dodge4/33resident/9quad/actual source pixels and original Ready/Walk joins passed, full silent videos reviewed. Guard Move remains gray fallback, new7-part source author trial only. Full0/15 combos0/20 active.',
 current_source_verification_scope='Actual compiled273/1364 exact sets and file hashes, full196, three bounded Source admissions, v011 normal manual preflight and two native source/GPU/pixel/CRC proofs. Historical suffixed fields retain original scope.',
 current_review='Keep scoped SWD/LGT side-dodge playable trial; no complete unit, physical footlock or audio acceptance.',current_turn_progress_classification='progress: equipped Hero Dodge4 actually integrated and bilateral native-reviewed; complete first-batch goal remains open',
 current_snapshot_pending=None,next_snapshot='Fresh Source/Production snapshot and required tests after next Move rig implementation; current v140-Dodge196G.',next_native_request=253,next_retention_batch='E574',next_media_retention_batch='E574',next_E_retention_number=574,current_turn_media_retained=True,
 latest_native_review_player='Both silent side-dodge MP4s played to ended true at1x in IAB2/tab4, loopfalse/errornull; E570 end screenshots viewed. Guard gray Move fallback still visible.',current_guard_room_manual_trial=pin(adoption),current_manual_launcher_v011=pin(adoption),latest_visual_runtime_proof=pin(review))
d['previous_current_retention_batches_before_v140']=d.get('current_retention_batches');d['current_retention_batches']=d['current_turn_media_retention']=retentions
d['latest_strict_UE_automation']=dict(report=cm['full_suite'],succeeded=196,failed=0,warnings=0,notRun=0,inProcess=0,actual_registry=196,scope='Original193 retained plus three Dodge targets; exact frozen Stage0 tests unchanged')
d['latest_targeted_UE_automation']=dict(report='UnrealGame/Saved/Automation/FirstRoom-20261018-205431/index.json',succeeded=3,failed=0,scope='Actual Dodge three groups after exact Stage0 semantic RED')
d['generation_accounting_current']=dict(requested_count=252,current_window_number=11,window_requested=12,window_remaining=12,lifetime_requested_count=276,external_api_calls=0,host_fee_usd=None,all_native_outputs_retained=True)
d['current_generation_accounting']=dict(requested=252,window=ledger['current_window'],remaining=12,lifetime=276,external_api_calls=0,host_fee_usd=None,automatic_follow_on_batches_authorized=True)
d['current_Dodge32_native_preparation'].update(actual_imported=True,actual_native_verified=True,scoped_runtime_review=pin(review),FinalAccepted=False)
d['current_hero_Dodge_runtime_v140']=delivery
d['hero_Dodge_v140_work_in_progress'].update(native_Dodge_verified=True,native_scope='One outward unblocked Shift per side',manual_current_checkpoint_ready=True,art_final_accepted=False,complete_unit=False)
move=R/'docs/production/first-batch-v2/evidence/GuardMove-v140-v001/Root-Rest252-seven-part-preparation-review-v001.json'
d['guard_Move_v140_source_preparation']=dict(native_ids=[252,250,251],sources=7,Root_preparation_review=pin(move),standing_basis100p8=True,continuous_author_bob_peak104p8=True,actual_imported=False,actual_runtime_implemented=False,Move6_accepted=False,original6_raster_gate_unchanged=True)
d['next_work']=d['next_turn_priorities']=['Implement separate Guard7-component Move trial from actual accepted AI distance, both facings/joins and atomic7GPU/source proof; keep original rejected6-raster gate unchanged.',
 'Complete SWD/LGT nonattack rise/apex/fall/landing from actual height/vertical velocity/landing age; currently air falls to bareReady0.',
 'Refine torso/waist and Stomp-to-Ready, then complete actual VFX/SFX audible evidence and remaining19equipment combinations/other first-batch units.']
packages=[q for q in(R/'UnrealGame/Content/Production').rglob('*')if q.is_file()];assert len(packages)==1364
d['production_package_counts_by_group']=dict(sorted(Counter(q.relative_to(R/'UnrealGame/Content/Production').parts[1]if len(q.relative_to(R/'UnrealGame/Content/Production').parts)>2 else q.relative_to(R/'UnrealGame/Content/Production').parts[0]for q in packages).items()))
dump(p,d)
rm=R/'README.md';old=rm.read_text(encoding='utf-8-sig');first,rest=old.split('\n\n',1);assert first.startswith('2026-10-18 v140制作中：')
prefix='''2026-10-18 当前检查点（EV048，v140）：钟盔军剑＋棕皮轻甲的四相侧闪已接入，左右真实Shift、装备保留、回待机／回行走均通过；完整196项严格通过。小比例、怪诞盔甲轮廓和隐藏HUD保持。[侧闪试玩](钟盔轻甲闪避试玩.cmd) · [实景记录](docs/production/first-batch-v2/runtime-review-hero-Dodge-v140.md)。

| 内容 | 当前实际状态 | 剩余 |
| --- | --- | --- |
| 主角侧闪 |32新纹理＋军剑；左右310／339原生帧，四相、33驻留、九层绘制、真实回接 | 胸腰／甲片细修、其余装备与空中状态、VFX／SFX |
| 守卫行走 | Rest252＋Near250／Far251七件作者试拼已审，允许有限代码准备 | 实景Move仍是灰色几何占位，尚未导入／接入新步态 |
| 构建与试玩 | Source273／Production1364／196项全过；七个v011手动入口 | 正式完整0/15、完整搭配0/20，目标继续 |

操作：Enter开局，E穿甲，WASD移动，J攻击，Shift侧闪，Space跳跃，R重开。两段完整静音录像已审；仅覆盖向外无阻侧闪，前置Knight／Bat为明确诊断清理，不能当整房手动通关或声音验收。E546–573展示前两SHA保全。图像请求252／窗口11用12余12／累计276（另最初3张），外部API0、内置费用未知。

以下为历史检查点；当前状态以上述v140及progress当前字段为准。

'''
rm.write_text(prefix+rest,encoding='utf-8')
requirements=R/'项目需求台账.md'
with requirements.open('a',encoding='utf-8')as f:f.write('\n\n2026-10-18 EV048持续实施／v140：SWD001＋LGT001四相侧闪32纹理实际导入，Source273／Production1364／完整196严格GREEN。左右原生310／339帧、原400ms／185位移、60–200ms无敌查询、33驻留九层及四相／五相邻接续通过，Root完整静音播放与原像素审阅后保留限定可玩试样，七个入口升级v011。初次left_v001核验工具的方向归一和回接统计窗口错误保留，工具仅两处修复后重新双侧通过；Source／测试未改。守卫249–252原生源共4次，新七件作者步态准备候选已审，Move仍灰色占位，未算完整动作；主角空中状态、完整特效／声音和其余首批单位继续。正式0/15、搭配0/20，目标active。E546–573两SHA保全，当前252／窗口11用12余12／累计276（另最初3张），外部API0、费用未知。此为执行记录，不是新用户需求或最终美术接受。见[v140实景记录](docs/production/first-batch-v2/runtime-review-hero-Dodge-v140.md)。\n')
receipt=O/'current-status-sync-v140-v001.json';assert not receipt.exists()
with receipt.open('x',encoding='utf-8')as f:json.dump(dict(schema='Root-Dodge-v140-current-status-sync-v001',actual_full196_green=True,scoped_native_review=pin(review),outputs=[pin(q)for q in[p,rm,requirements,lp]],E_last=573,E_next=574,next_native_request=253,formal_complete_units=0,goal_status='active',FinalAccepted=False),f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(status=pin(receipt),Source=273,Production=1364,full_GREEN=196,formal_complete_units=0,E_last=573,next_request=253),ensure_ascii=False))
