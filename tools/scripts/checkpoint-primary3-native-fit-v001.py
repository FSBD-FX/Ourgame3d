from pathlib import Path
import datetime,hashlib,json,shutil

R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2'
O=D/'evidence/primary3-native-fit-status-v001'
if O.exists():
    assert sorted(x.name for x in O.iterdir())==['before','failed-preflight-v001.json','failed-preflight-v001.py']
    assert not any((O/'before').iterdir()), 'Only resume the documented failure before status writes'
else:(O/'before').mkdir(parents=True)
A=R/'过程图稿与视频/2026-10-16_钟盔军剑三段真实连击试装_v001'
PLAYER=R/'过程图稿与视频/2026-10-16_军剑三段连续出招播放复核_v001'
SNAP='source-assets/production/backups/2026-10-16_Primary3Armor48-fit-full141GREEN-v116'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def desc(p):
    b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
audit=read(A/'原件/compiled-source-binding-audit-v001.json')
fit=read(A/'原件/sword-primary3-fit-runtime-verification-v001.json')
video=read(A/'原件/video-presentation-receipt-v001.json')
manifest=read(R/SNAP/'compiled-source-manifest.json')
assert audit['snapshot_files']==2197 and audit['endpoint_checks']==4394 and audit['mismatches']==0
assert audit['captured_Source_and_DLL_unchanged'] and audit['exact_Production_package_set']==1085
assert manifest['copied_files']==2197 and manifest['bytes']==134470213
assert fit['passed'] and fit['observations']==198 and fit['body_max_px']==72 and fit['UI_hidden']
assert len(fit['transitions'])==4 and all(x['exact_end_equals_start'] and x['actual_pending_seen'] and x['adjacent_observations'] for x in fit['transitions'])
assert video['full_decode_exit']==video['encode_exit']==0 and video['audio_streams']==0
assert video['video']['sha256']=='0164ca94b6f6bbf8bcaf4d39b6d3c346ae8bc18665641cce48032383716fa32d'
rr=read(R/'UnrealGame/Saved/Automation/FirstRoom-20261016-192628/index.json')
assert rr['succeeded']==141 and len(rr['tests'])==141 and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in rr['tests'])
assert all(rr.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess'])
EBASE=Path('E:/OurGame/Knight/过程图稿与视频')
retentions={}
for n,name,count,size in [(240,'2026-10-16-OurgameUE-primary3-three-stage-real-fit-v240',350,962594477),(241,'2026-10-16-OurgameUE-primary3-three-stage-review-player-v241',17,712347)]:
    p=EBASE/name/('retention-verification-v001.json' if n==240 else 'source-size-SHA256.json');v=read(p)
    assert v['file_count']==count and v['bytes']==size
    if n==240:
        assert v['executed'] and v['first_pass_mismatches']==v['second_pass_mismatches']==0 and v['E_root_README_unchanged']
    else:
        assert v['source_and_target_hash_mismatches']==0 and v['verification_passes']==2 and v['root_readme_unchanged']
    retentions[f'E{n}']=desc(p)
ind=D/'evidence/sword-primary3-native-review-v001/review-freeze-v001.json'
assert desc(ind)['sha256']=='6927ff0ff362717b5d46e0fa2bd0588c4b6abff9306863c35a821b16b1b091c4'
browser=dict(tab_id='15',url='http://127.0.0.1:56249/2026-10-16_军剑三段连续出招播放复核_v001/review-player.html',action='actual click 从头播放',start=dict(currentTime=0.236204,duration=6.633333,ended=False,paused=False,readyState=4,error=None,videoWidth=1280,videoHeight=720),end=dict(currentTime=6.633333,duration=6.633333,ended=True,paused=True,readyState=4,error=None,videoWidth=1280,videoHeight=720),markDeliverable_called=True,scope='Playback decode/progression only; does not certify continuous art, grip, foot lock or audio.')
write(O/'browser-playback-v001.json',browser)
progress=D/'progress.json';ledger=R/'source-assets/production/first-unit-animation-v003/generation-ledger.json'
for p in [R/'README.md',R/'AGENTS.md',R/'项目需求台账.md',progress,ledger]:shutil.copy2(p,O/'before'/p.name)
m=read(progress);lg=read(ledger)
assert lg['requested_count']==178 and lg['current_window']['requested_count']==10 and lg['remaining_batch_requests']==14
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for row in lg['requests']:
    if row['request_number'] in [175,176,177,178]:
        row['status']='native_three_stage_trial_reviewed_NEEDS_WORK_complete_equipment_pending'
        row.setdefault('review_history',[]).append(dict(time=now,native_capture_index=desc(A/'index.json'),independent_review_freeze=desc(ind),retention=['E240','E241'],scope='Both facings three stages/armor captured; actual art review NEEDS_WORK: crowded raised fist/hilt/helmet, low blade tip, gray armor/cloth silhouette. No complete-motion/audio/equipment acceptance.'))
write(ledger,lg)
m['current_task']='EV048 v116 actual bilateral three-stage armor trial recorded/reviewed NEEDS_WORK;72px/UIoff/.50 preserved,141 strictGREEN. Prioritize fist/helmet clearance, low blade tip and armor silhouette; formal0/15active.'
m['current_compiled_snapshot']=SNAP;m['current_snapshot_pending']=None;m['ue_current_working_source_verified']=True
m['current_source_verification_scope']='Compiled141 tests +2197 files4394 snapshot endpoints +actual native three-stage timing; art still NEEDS_WORK, not complete-equipment acceptance.'
m['current_compiled_snapshot_files']=2197;m['current_compiled_snapshot_bytes']=134470213
m['fairytale_sword_primary3_current_v001'].update(actual_native_fit_recording=desc(A/'index.json'),native_runtime_verification=desc(A/'原件/sword-primary3-fit-runtime-verification-v001.json'),source_binding_audit=desc(A/'原件/compiled-source-binding-audit-v001.json'),native_original_pngs=199,observations=198,capture_duration_s=6.601578898727894,actual_action_ids=[1,2,3,4,5,6],exact_buffered_end_start_transitions=4,root_reviewed_crops=26,root_reviewed_wholes=4,independent_reviewed_crops=20,independent_reviewed_wholes=2,independent_review_freeze=desc(ind),art_review_status='NEEDS_WORK',complete_unit=False,grip_accepted=False,footlock_accepted=False,full_motion_accepted=False,audio_accepted=False)
m['latest_native_review_player']=PLAYER.relative_to(R).as_posix();m['latest_native_review_browser_playback']=desc(O/'browser-playback-v001.json')
launcher=D/'evidence/sword-primary3-native-review-v001/launcher-preflight-v001.json'
assert desc(launcher)['sha256']=='e63f5e628a9d4f55ab0bf904fcd66859df7893c7d4505a5e37fd77cf5ca8cfe9'
m['latest_primary3_manual_launcher_preflight']=desc(launcher)
m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+['E240','E241']))
m['current_turn_media_retention'].update(actual_Primary3='E240350files962594477B/twoSHA0',Primary3_player='E24117files712347B/twoSHA0',latest_runtime='E240',player='E241')
m['next_retention_batch']='E242';m['next_snapshot']='v117';m['next_native_request']=179
m['next_work']=['Prioritize EV048 native art fixes: separate raised fist/hilt from helmet, increase low blade-tip margin and strengthen armor vs cloth large silhouette, retaining72px/UIoff/.50.','Then review/admit pending Bound renderer five-hunk candidate and prove native pickup/cancel/commit/replace/retake appearance; current resolver alone is not draw proof.','Finish all semantic states, five weapons/four armors/five enemies/Boss/20 pairings/VFX/SFX/persistence/15 auxiliaries with actual running proofs; formal0/15active.']
m['current_turn_progress_classification']='progress:actual native three-stage fit198 samples/199 originalPNGs;141 strictGREEN; Root30 and independent22 stills plus full browser playback reviewed. Art NEEDS_WORK; no full unit completion.'
m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=now
write(progress,m)
doc=D/'runtime-review-sword-primary3-fit-v001.md';assert not doc.exists()
doc.write_text('''# 军剑三段穿甲实景试样 v116

事实：本次UE5真实输入左右各三段攻击，198次观察、199张原始PNG，运行6.601579秒。四次接招均实际出现待接输入，上一段结束时间等于下一段起始时间，选定相邻帧未出现待机过桥。第三段六相时长为110/110/60/60/160/160毫秒，总660毫秒。保持人物身体最高72px、游戏UI隐藏、独立剑0.50。

当前Source已编译，完整141/141测试均Success且错误/警告/未运行均0。v116快照2197文件134470213字节，当前与快照4394端点核对零差，实际Production纹理1085。该证据证明本次源与运行相符，不代表美术接受。

推理：胸甲、近肩和远肩分层能随三段攻击维持盔甲身份，怪诞钟盔与琥珀眼窗在已看阶段可辨。Root实际审看26张原比例裁图和4张整景；独立复核审看20张裁图与2张整景。双方结论仍需修改：抬手时拳柄与盔缘拥挤，低位剑尖贴近靴底/地面基线，灰甲与灰衣的大轮廓区分不够。未直接断言已穿地或已完全无穿插。

风险与下一步：优先修握柄/盔缘间隙、剑尖余量和胸肩的大形区分，再接真实装备实例的渲染消费。动作行切换仍有轻微姿态差，足锁、连续动作质量、其他状态和完整视听尚未接受。绑定逻辑3项真实测试通过，但五文件渲染消费候选未应用，不能称已实现换装画面。本次无命中目标，录像无声，敌人没有在此范围更新。

来源：F过程目录“2026-10-16_钟盔军剑三段真实连击试装_v001”及“2026-10-16_军剑三段连续出招播放复核_v001”，展示前已保留E240/E241，两遍大小与SHA核验零差。浏览器实际从0.236204播放到6.633333秒结束，1280×720、readyState4、error空；该项仅证明播放解码，不等于连续美术验收。标准工具600毫秒预览未改为660毫秒以冒充内核。

可运行入口：F:/Ourgame/钟盔军剑三段穿甲试装.cmd。实际获取/换装/全状态/命中特效/音效及首批其他单元继续推进。人类要求仍EV048，没有新事件。正式完整内容单元0/15，目标active。内置请求178，当前窗口10/24余14，累计202，下一179；外部API0，内置费用未知。
''',encoding='utf-8')
header='''2026-10-16 当前检查点（EV048，v116）：左右三段穿甲实景已实际录制并审图，保留怪诞钟盔/琥珀眼窗、小比例72px和无UI。胸甲与前后肩随攻击分层遮挡；目前拳柄贴盔、低位剑尖及灰甲/灰衣的大轮廓仍需打磨，状态为试样待改。完整141/141测试严格通过，Source/DLL快照v116与当前4394端点零差。[实景复核记录](docs/production/first-batch-v2/runtime-review-sword-primary3-fit-v001.md)。

| 当前资源 | 已有运行证据 | 剩余 |
| --- | --- | --- |
| 钟盔军剑＋轻甲三段攻击 | 左右三段、198观察/199原图、真实接招；48张第三段新纹理 | 握柄/剑尖/轮廓、足锁及全状态 |
| 装备实例校验 | 取消/提交/替换/重拾等3测试通过 | 渲染消费候选尚未应用，实际换装画面待证 |
| 首批其他装备/敌人/Boss | 既有候选及历史记录 | 新风格完整动作、特效、音效及组合适配 |

[打开三段穿甲试装](钟盔军剑三段穿甲试装.cmd)。F原件及展示版已保留E240/E241；静音视频完整播放验证。正式完整单元0/15，目标active。内置请求178、当前窗口10/24余14、累计202、下一179；外部API0，内置费用未知。以下为历史检查点，先前“实录待录”等状态以本段为准。

'''
for p in [R/'README.md',R/'AGENTS.md']:p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 EV048续行，无新人类要求：v116左右三段穿甲198观察/199原PNG、四次真实接招无Ready桥；72px/UIoff/剑.50保持，full141严格通过，快照2197文件/4394端点零差。Root26裁图+4整景与独立20裁图+2整景结论NEEDS_WORK：拳柄贴盔、低位剑尖、灰甲灰衣轮廓待修。视频实际播到6.633333秒结束，无声；E240350files962594477B/E24117files712347B两遍SHA0。绑定渲染消费未应用、完整0/15active。详见runtime-review-sword-primary3-fit-v001.md。\n')
write(O/'checkpoint.json',dict(after=[desc(p) for p in [progress,ledger,doc,R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']],actual_fit=desc(A/'原件/sword-primary3-fit-runtime-verification-v001.json'),source_binding=desc(A/'原件/compiled-source-binding-audit-v001.json'),retentions=retentions,browser_playback=desc(O/'browser-playback-v001.json'),art_status='NEEDS_WORK',formal_complete_units=0,goal_status='active'))
print(json.dumps(dict(current_snapshot='v116',strict_full_tests=141,native_observations=198,original_pngs=199,art_status='NEEDS_WORK',formal_complete_units=0,goal_status='active'),ensure_ascii=False))
