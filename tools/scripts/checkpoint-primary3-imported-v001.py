from pathlib import Path
import datetime,hashlib,json,shutil
R=Path('F:/Ourgame');D=R/'docs/production/first-batch-v2';P=R/'source-assets/production';O=D/'evidence/primary3-imported-status-v001';assert not O.exists();(O/'before').mkdir(parents=True)
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
report=R/'UnrealGame/Saved/Automation/FirstRoom-20261016-192628/index.json';rr=json.loads(report.read_text(encoding='utf-8-sig'))
assert rr['succeeded']==141 and all(rr.get(k,0)==0 for k in ['failed','succeededWithWarnings','notRun','inProcess']) and all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in rr['tests'])
ledger=P/'first-unit-animation-v003/generation-ledger.json';progress=D/'progress.json'
for p in [R/'README.md',R/'AGENTS.md',R/'项目需求台账.md',progress,ledger]:shutil.copy2(p,O/'before'/p.name)
lg=json.loads(ledger.read_text(encoding='utf-8'));assert lg['requested_count']==178 and lg['current_window']['requested_count']==10 and lg['remaining_batch_requests']==14
importreceipt=R/'UnrealGame/Saved/Bootstrap/sword-armor-primary3-v001-import-20261016-112045-451279.json'
for row in lg['requests']:
    if row['request_number'] in [175,176,177,178]:
        row['status']='runtime_imported_pending_native_three_stage_fit_and_complete_equipment';row['runtime_imported']=True;row.setdefault('review_history',[]).append({'time':datetime.datetime.now().astimezone().isoformat(),'import_actual':desc(importreceipt),'retention':['E228','E236','E237','E238','E239'],'scope':'48 actual saved,141 strictGREEN; P3 native grip/continuous motion/real bound render remain pending. Original receipts unchanged.'})
ledger.write_text(json.dumps(lg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads(progress.read_text(encoding='utf-8'));m['current_task']='EV048 P3actual175 body+176177178armor48 saved/1037old unchanged/1085total,Source5 compiled/full141 strictGREEN. Native three-stage fit and bound render consumption pending; formal0/15active.'
m['current_build']='UnrealGame/Saved/Bootstrap/build-editor-20261016-192403.log';m['current_build_exit_code']=0;m['latest_build_attempt']=m['current_build'];m['latest_build_attempt_exit_code']=0
m['previous_compiled_snapshot_before_primary3']=m['current_compiled_snapshot'];m['current_compiled_snapshot']=None;m['current_snapshot_pending']='v116 actual3stage fit tools preparation, Source/DLL snapshot not yet frozen'
m['ue_current_working_source_compiled']=True;m['ue_current_working_source_verified']=False;m['current_source_uncompiled_changes']=None;m['latest_strict_UE_automation']={'report':report.relative_to(R).as_posix(),'succeeded':141,'failed':0,'warnings':0,'notRun':0,'inProcess':0,'all_states_Success':True};m['default_test_runner_expected_tests']=141;m['actual_registered_test_count_current']=141
for k in ['production_texture_count_actual','production_uasset_package_count_actual','production_package_count_actual']:m[k]=1085
m['fairytale_sword_primary3_current_v001']={'native_body':175,'native_armor':[176,177,178],'source_body_frames':6,'actual_saved_textures':48,'old_packages_unchanged':1037,'current_production_packages':1085,'candidate':desc(P/'fairytale-sword-primary3-runtime-v001/candidate-import-v001.json'),'import_receipt':desc(importreceipt),'durations_ms':[110,110,60,60,160,160],'standard_preview_ms':[100]*6,'standard_preview_matches_kernel':False,'all_six_body_and18_components_and24_layers_and6assemblies_Root_viewed':True,'grip_and_axes_candidates_only':True,'actual_native_fit_recording':None,'complete_unit':False}
m['fairytale_sword_equipment_binding_v001']={'cleanRED_report':'UnrealGame/Saved/Automation/FirstRoom-20261016-191319/index.json','actual_cleanRED_tests':3,'actual_stub_positive_errors':11,'targetGREEN_report':'UnrealGame/Saved/Automation/FirstRoom-20261016-192455/index.json','actual_targetGREEN':3,'fullGREEN':141,'resolver_compiled':True,'actual_renderer_consumption_applied':False,'native_binding_draw_proof':None,'scope':'True committed instance/version/owner validation only; draw integration and allstates remain. NoArmor/LGT/cancel/replace/retake/legitimateaffixes/pausedContinue covered by3 realworld tests.'}
m['generation_accounting_current']={'requested_count':178,'current_window':8,'window_requested':10,'window_remaining':14,'lifetime_requested_count':202,'external_api_calls':0,'host_fee_usd':None,'authorization_events':['EV-040','EV-041']};m['next_native_request']=179;m['next_retention_batch']='E240';m['next_snapshot']='v116'
m['current_retention_batches']=list(dict.fromkeys(m['current_retention_batches']+[f'E{i}' for i in range(225,240)]));m['current_turn_media_retention']['Primary3_preparation']='E225–E239 actual twoSHA0, all source/version/status retained'
m['next_work']=['Actual bilateral3stage native timing/appearance/Source-DLL freeze v116; preserve72/UIoff/.50 and oldbranches','AfterP3 checkpoint, actual Bound-mode draw consumption and native pickup/cancel/commit/replace/retake render proof','Complete chosenstyle allsemanticstates/all5weapons4armors5enemiesBoss/20pairings/VFX/SFX/persistence/15aux; formal0/15active']
m['current_turn_progress_classification']='progress:4actualnative calls,48 real savedtextures,Rootnewartviews,3cleanRED→3GREEN and full141; nativeP3fit pending';m['goal_status']='active';m['completed_content_units']=0;m['updated_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
progress.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=D/'primary3-asset-preparation-v001.md';assert not doc.exists();doc.write_text('''# 第三刀终结斩：已导入，实景试装待录

事实：原生175六身体、176胸甲/177近肩/178远肩各六透视已生成并标准提取。四工具正常完成，原请求未改、统一行缩比，十八甲片实际特征候选经过完整原512裁图和未缩放原生组件核对。二十四身体层可完整还原原RGBA，语义边界仍是候选。Root已审全部这些图及六无剑组合。

实际48 Texture保存成功，原1037包保持，当前1085。五份新/改Source编译0，三绑定测试由真实11个stub正控RED转为3GREEN，完整141/141均Success，errors/warnings/notRun/inProcess全0。绑定resolver尚未接到渲染，不能把逻辑测试当作换甲画面证明。

推理：第三刀从肩侧蓄力转为向下终结，独立胸肩在不同姿态保持同族金属轮廓。现可进行保持72px/UI隐藏/剑0.50的真实左右三段试装。新手掌候选来自175，剑轴为独立试装设计；遮挡处的甲挂点明确为Root隐藏TRIAL，不冒称骨点。

风险与待办：相0蓄力弱，相1拳盔贴近，相2双手交叠/横袖有拳击风险，低位剑尖与靴/地面待实景。远肩贡献、连续三段、握柄、足锁、全状态、真实换甲、命中/VFX/SFX及完整内容均未验收。标准600ms形状预览不等于Stage2真实660ms，不重时充当证明。

材料已按要求保存在F过程目录及E225–E239；本地保留不代表接受或发布。当前人类事件仍EV048；完整目标active，正式0/15。
''',encoding='utf-8')
header='''2026-10-16 进行中检查点（EV048，准备v116）：第三刀175身体及176/177/178胸肩已实际保存48新纹理，旧1037保持、当前1085。Root已审六身体/十八甲片/24身体层/六无剑组合，维持72px、无UI、独立剑0.50。五Source编译0、绑定3GREEN及完整141/141严格通过。第三刀双向实录尚未录，绑定resolver尚未消费到渲染，握柄/连续动作/全状态及完整0/15仍active。[准备事实与边界](docs/production/first-batch-v2/primary3-asset-preparation-v001.md)。

| 当前资源 | 状态 | 待验 |
| --- | --- | --- |
| 待机及前两刀 | v115穿胸肩实录仍为最近已审的运行证据 | 握柄/全运动 |
| 第三刀 | 六相660ms、48纹理已导入并编译 | 新三段左右实录/甲剑适配 |
| 实例绑定 | 真实取消/提交/替换/重拾等3测试通过 | 渲染消费及运行图 |
| 其他装备/敌人/Boss | 既有候选 | 新风格全状态与视听 |

内置请求178，窗口008为10/24、余14、累计202，下一179；外部API0，内置费用未知。新素材E225–E239已展示前保留。本段为当前进行中状态；v115 Source/DLL快照为历史，新的v116快照与实录待完成。

'''
for p in [R/'README.md',R/'AGENTS.md']:p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n2026-10-16 EV048续行，无新人类要求：175第三刀身体及176177178三甲已实际保存48Texture/旧1037保持/1085总；五Source编译0，3绑定RED→GREEN及full141strictGREEN。Root已审源图/分层/无剑组合，E225–E239保留。新三段实录与绑定渲染仍待，72/UIoff/.50保持，0/15active；ledger178/window00810of24/rem14/lifetime202/next179。\n')
(O/'checkpoint.json').write_text(json.dumps({'after':[desc(p) for p in [progress,ledger,doc,R/'README.md',R/'AGENTS.md',R/'项目需求台账.md']],'full_report':desc(report),'formal_complete_units':0,'goal_status':'active'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual_fullGREEN':141,'actual_imported':48,'current_production':1085,'native_fit_pending':True,'formal_complete_units':0},ensure_ascii=False))
