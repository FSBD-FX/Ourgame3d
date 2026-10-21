from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';B=R/'source-assets/production/fairytale-lgt-readability-v003'
O=D/'evidence/stone-guard-kernel-v001/root-final-checkpoint-v122'
S=R/'source-assets/production/backups/2026-10-16_StoneGuardKernel-full148GREEN-beforeNative-v122'
A=R/'过程图稿与视频/2026-10-16_军剑真实换装绑定_v005-guardKernelGREEN'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 assert not p.exists(),p;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not O.exists();O.mkdir(parents=True)
for p in [D/'progress.json',R/'README.md']:shutil.copy2(p,O/('before-'+p.name))
m=read(S/'compiled-source-manifest.json');assert m['current_automation_succeeded']==148
for row in m['files']:
 for base in [R,S]:
  d=desc(base/row['path']);assert d['bytes']==row['bytes'] and d['sha256']==row['sha256']
tests=read(R/m['current_automation_report']);assert len(tests['tests'])==len({t['fullTestPath'] for t in tests['tests']})==148
assert tests['succeeded']==148 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in tests['tests'])
assert all(tests.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
native=read(A/'原件/runtime-report.json');proof=read(A/'原件/independent-bound-flow-verification-v001.json')
assert native['passed'] and proof['observations']==141 and proof['original_PNGs']==142 and not proof['independent_metadata_mismatches']
playback=R/'过程图稿与视频/2026-10-16_当前148构建录像播放复核_v001/原件/playback-end.json';p=read(playback)
assert p['ended'] and p['time']==p['duration']==4.766667 and p['error'] is None
ledger_path=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json';l=read(ledger_path)
assert l['requested_count']==183 and l['current_window']['requested_count']==15 and l['remaining_batch_requests']==9
shutil.copy2(ledger_path,O/'before-semantic-review-ledger.json')
review=B/'root-semantic-review179-183-v001.json'
write(review,dict(source_event='EV-048',actual_native_calls_this_checkpoint=[179,180,181,182,183],runtime_imported=False,commonbody_replaced=False,reference179=dict(status='reference_only',core_alpha_128_height=1020,actual72CSS_preview_reviewed=True,inference='Brown short jerkin and shoulder steps separate more clearly from dark cloth in reference; anatomy not pixel locked to existing158'),failed180_181_182=dict(status='FAIL_do_not_import',reason='All three generated complete vests, chest baked both caps and shoulders retained entire torso/pouch',raws_preserved=True),near183=dict(status='isolated_geometry_improved_not_final',actual_root_viewed='raw and extracted shared-scale frame0 only',diagnostic_four512RGBA=True,grey_dark_lining_semantic_pending=True,actual_A=None,mount_mask_animation_runtime_accepted=False),formal_complete_units=0))
for r in l['requests']:
 if r['request_number'] in [179,180,181,182,183]:
  r['root_semantic_review']=desc(review)
  r['status']='generated_retained_reference_only' if r['request_number']==179 else 'generated_retained_component_rejected' if r['request_number']<183 else 'generated_retained_diagnostic_only_not_final'
ledger_path.write_text(json.dumps(l,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');shutil.copy2(ledger_path,O/'after-semantic-review-ledger.json')
manual=subprocess.run([sys.executable,'-B','-X','utf8',str(R/'tools/scripts/verify-equipment-bound-current-build-v003.py'),'--snapshot',S.relative_to(R).as_posix()],cwd=R,capture_output=True,text=True,encoding='utf-8')
assert manual.returncode==0,(manual.stdout,manual.stderr)
write(O/'manual-entry-preflight-v003.json',dict(exit_code=manual.returncode,result=json.loads(manual.stdout),manual_window_launched=False))
report=D/'runtime-review-guard-leather-v122.md'
assert not report.exists()
report.write_text('''# EV048：软皮轻甲参考与守卫纯核检查点 v122

事实：保持怪诞钟盔、小比例72px目标、军剑.50、传统HUD隐藏。本轮实际5次内置生成179–183：179是棕色短皮衣参考；180胸/181近肩/182远肩均误画整背心，Root看原图后拒绝导入。183单原图编辑已形成四个孤立近肩；开口暗内衬仍待语义检查，标准连通体提取/既有共同scale扩展产出四512RGBA诊断帧，自动QA零错警不代表最终A、mask、挂点或动作通过。全部原图和失败版本保留，外部API0、内置计费未知，没有以179整个人替换公共身体，1085 Production包保持。

事实：179/当前158的alpha≥128核心高分别1020/415，HTML只用CSS等高72，原PNG不改；浅/深背景与400%开关实际检查。Root看72深底对照及放大截图：胸/肩的褐色大面与暗衣区别更清楚；放大截图下缘受视口裁切，不作为全身构图验收。参考页 [本地对照](F:/Ourgame/过程图稿与视频/2026-10-16_软皮轻甲72像素参考对照_v001/展示副本/reference-preview.html)，尚未替换进游戏。

事实：STN003裂岩守卫新增纯核四组UE测试。stub实际编译0后3语义RED；生产v001原3GREEN，但新移动回归1RED/24错误，证明分步/零效果收据会改变停点。v002解析首次进入斧矩形或顿足椭圆的点，保持Y后X、40×28 sweep和无伤害副作用；独立定向147检查通过，作者213检查另存，二者不冒充实际UE。当前build232055真实Compile单CPP后exit0，FirstRoom-232216唯一148/148全Success，错误/警告/failed/notRun/inProcess全0。v122快照1268文件86495341B、2536源/快照端点0差。

事实：当前Source/DLL的既有普通输入换装回归v005正常结束，141观察/142原PNG、33个合法pending、三次提交、同轻甲实例2重拾version4、三段六相mask63×3，独立0不符。源视口CRC与异步flush均通过。原4.700887秒采集生成静音展示视频4.766667秒，IAB实际从头播完ended=true/error=null；Root看末帧整景和取消/换中甲途中/重拾三裁图，当前剑甲保持改善仍在，灰甲轮廓差别弱和白框占位仍在。此录像没有新棕甲或正式Guard敌人，不能借它证明新增纯核已真实生成/战斗。

推理：先把轻甲的材质和胸肩分层做正确，再测量实际特征A与遮挡，在不改原身体和放大人物的条件下试装。183只有部件几何改善；不把整个背心切出肩片作为最终成果。优先小规模真实走路/穿甲姿态和可更换甲层试验，保留已验证三段攻击；不因替换Ready参考就宣布全20搭配或全状态完成。

风险与剩余：Guard仍无NativeDriver、实际房间生成/LOS/sweep/HP镜像/伤害奖励消费及存续协议，奖励数额没有已定依据；不能给它凭空固定金币。轻甲Chest/Far纠错、183内衬、实际挂点/遮挡/四姿态试装和走跑跳伤亡/获取穿甲动作、全部20组合、所有敌人/Boss、特效/音效试听继续。正式单元0/15、目标active。内置183/window00815of24余9/累计207/下一184，自动授权沿用EV040/041，无新人类事件。

留档：E249–E265展示前保留；E262原PNG以无损ZIP保存完整文件字节，192源项/142原PNG两遍大小SHA零差、F原件和E根README保持。手动入口 [军剑真实装备绑定试玩](F:/Ourgame/军剑真实装备绑定试玩.cmd)已切v003/v122/nativev005，CLI实际预检0，未另开人工试玩窗口。通用test-first-room.ps1默认数仍为历史141，本轮命令明确传ExpectedTests148；历史字段以progress当前权威键为准。
''',encoding='utf-8')
v=read(D/'progress.json');v['current_task']='EV048: keep grotesque small bell hero; soft-leather179 reference reviewed at72CSS;180-182 complete-vest FAIL preserved;183 isolated near-cap diagnostic only, A/lining/mount pending. STN003 pure kernel actual3RED→3GREEN+movement1RED→full148GREEN, current native existing gear flow141obs142PNG0mismatch; GuardNativeDriver absent, full units0/15.'
v.update(ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=None,current_build=m['build_log'],current_build_exit_code=0,latest_build_attempt=m['build_log'],latest_build_attempt_exit_code=0,current_compiled_snapshot=S.relative_to(R).as_posix(),current_compiled_snapshot_files=m['copied_files'],current_compiled_snapshot_bytes=m['bytes'],actual_registered_test_count_current=148,goal_status='active',completed_content_units=0,next_native_request=184,next_snapshot='v123',next_retention_batch='E266')
v['latest_strict_UE_automation']=dict(report=m['current_automation_report'],succeeded=148,failed=0,warnings=0,notRun=0,inProcess=0,all_states_Success=True)
v['stone_guard_kernel_v001'].update(actual_UE_GREEN=desc(R/m['current_automation_report']),actual_native_driver=None,formal_unit_complete=False,independent_fix_review=desc(D/'evidence/stone-guard-kernel-v001/review-fix-v002/review.md'))
v['previous_visual_runtime_proof_before_v122']=v['latest_visual_runtime_proof']
v['latest_visual_runtime_proof']=dict(report=desc(report),archive=A.as_posix(),capture_snapshot=S.relative_to(R).as_posix(),video=desc(A/'展示副本/equipment-bound-flow-green-silent.mp4'),observations=141,original_PNG_including_prewarm=142,duration_s=proof['duration_s'],uniform_weapon_scale=.5,body_max_px=72,root_whole_views=1,root_unscaled_crop_views=3,actual_transaction_mismatches=0,actual_committed_operations=3,pending_committed_gear_observations=33,actual_weapon_pickup_proven=False,art_review_status='NEEDS_WORK',audio_recorded=False,full_motion_accepted=False,new_leather_runtime_imported=False,guard_native_driver=False,formal_complete_units=0)
v['latest_native_review_player']='过程图稿与视频/2026-10-16_守卫纯核后换装运行复核_v001';v['latest_native_review_browser_playback']=desc(playback)
v['latest_equipment_bound_manual_launcher_preflight']=desc(O/'manual-entry-preflight-v003.json')
v['generation_accounting_current']=dict(requested_count=183,current_window=8,window_requested=15,window_remaining=9,lifetime_requested_count=207,external_api_calls=0,host_fee_usd=None,authorization_events=['EV-040','EV-041'])
v['soft_leather_readability_v003']=dict(reference179=desc(B/'concept179-v001/raw/179-soft-leather-reference.png'),semantic_review=desc(review),reference_preview='过程图稿与视频/2026-10-16_软皮轻甲72像素参考对照_v001/展示副本/reference-preview.html',near183_diagnostic=desc(B/'near183-extraction-v001/numeric-diagnostic-v001.json'),imported=False,final_A=None)
v['current_source_verification_scope']='Current148 strictGREEN/2536 frozen endpoints plus current141obs142PNG/33pending0mismatch existing bound flow. PureGuard only, no NativeDriver; newleather reference/diagnostic not imported; no full motion/audio/unit acceptance.'
v['current_turn_progress_classification']='progress: actual STN0033semanticRED, newmovement1RED24errors then full148GREEN and refreshed current native regression/entry; five actual native179-183 refs/raw with three semantic rejects and one isolated-cap extraction diagnostic. Complete units0/15 active.'
v['current_retention_batches']=[p.name for p in sorted(Path('E:/OurGame/Knight/过程图稿与视频').iterdir()) if p.is_dir() and re.search(r'-v(24[9]|25[0-9]|26[0-5])$',p.name)]
v['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(D/'progress.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''2026-10-16 当前检查点（EV048，v122）：保持怪诞钟盔和小比例。新棕色软皮轻甲参考已按72像素等高检查，胸肩层次更清楚；尚未替换进游戏。180–182误画整背心已拒绝导入，183近肩已提取四512RGBA诊断帧，内衬/挂点/遮挡仍待。 [查看72像素对照](过程图稿与视频/2026-10-16_软皮轻甲72像素参考对照_v001/展示副本/reference-preview.html)。

| 当前内容 | 已验证 | 仍需制作 |
| --- | --- | --- |
| 软皮轻甲 | 179参考、183独立近肩数值诊断；原身体和全部1085资源保持 | 正确胸衣/远肩、内衬、实际挂点/四帧试装和全动作 |
| 裂岩守卫 | 纯核苏醒/攻击/中断/死亡及首次范围入口；实际新增四组测试通过 | NativeDriver、房间生成、实际伤害/奖励消费、存续、美术声音 |
| 当前游戏 | 148/148严格通过，换装141观察/142原PNG、33pending/3提交/三连击0差；录像已播完 | 灰甲差别弱、拾取Ready0占位、中甲/全动作与声音试听 |

[本轮事实、推理与剩余](docs/production/first-batch-v2/runtime-review-guard-leather-v122.md) · [当前试玩](军剑真实装备绑定试玩.cmd)。v122快照1268文件/2536端点0差；E249–E265保留，原PNG文件字节无损ZIP两遍核验。正式完整0/15，目标active。内置183/窗口15of24余9/累计207/下一184，外部API0、计费未知。以下旧检查点保留，以本段及progress当前权威字段为准。

'''
p=R/'README.md';p.write_text(text+p.read_text(encoding='utf-8-sig'),encoding='utf-8')
write(O/'checkpoint.json',dict(report=desc(report),progress=desc(D/'progress.json'),readme=desc(R/'README.md'),semantic_review=desc(review),source_files=m['copied_files'],source_snapshot_endpoint_checks=2*m['copied_files'],mismatches=0,actual_tests=148,actual_native_obs=141,original_PNGs=142,goal_status='active',formal_complete_units=0))
print(json.dumps(dict(current_build='v122',actual_tests=148,source_endpoint_checks=2536,native_observations=141,raw_native_requests=183,next_native184=True,formal_complete_units=0,goal_status='active'),ensure_ascii=False))
