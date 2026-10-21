"""Keep durable current WIP separate from the historical v140 playable checkpoint."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame')
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def pin(q):return dict(path=q.relative_to(R).as_posix(),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest())
cm=R/'source-assets/production/backups/v141-GuardMove7-Stage0-four-semantic-RED-v002/compiled-source-manifest.json';m=read(cm)
assert pin(cm)['sha256']=='62a0e1ab2bdf45d4a6caebc304b8c4bd14306f50327e65e459626d7cba6d8d6e'
assert m['semantic_stage0_RED_observed']and(m['source_files'],m['production_files'],m['passed'],m['failed'])==(279,1371,196,4)
out=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/Stage0-status-sync-v001';assert not out.exists();out.mkdir(parents=True)
files=[R/'README.md',R/'项目需求台账.md',R/'docs/production/first-batch-v2/progress.json'];before=[]
for q in files:before.append(pin(q));target=out/'before'/q.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
state=dict(version='v141-GuardMove7-Stage0-v002',Source=279,Production=1371,registered_tests=200,old196_passed=196,new_expected_semantic_RED=4,
 all_tests_green=False,source_compiled=True,source7_actual_imported=True,rig_runtime_implemented=False,native_verified=False,manual_current_checkpoint_ready=False,
 compiled_snapshot=pin(cm),fixture_failure_preserved_snapshot='source-assets/production/backups/v141-GuardMove7-Stage0-fixture-failure-v001/compiled-source-manifest.json',
 fixture_repair='Only one test birth-sign byte minus to plus; all assertions and game bounds unchanged',old196_test_sources_unchanged=True,
 runtime_trial_approval=pin(R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json'),
 native_import=pin(R/'UnrealGame/Saved/Bootstrap/GuardMove7-v001-import-20261018-140342-134561.json'),
 independent_import=pin(R/'source-assets/production/fairytale-guard-v001/Root-Move7-import-v001/independent-import-verification-20261018-140403-753926.json'),
 generation_calls_this_turn=0,external_API_calls=0,last_fully_green_checkpoint='v140-Dodge196G',
 formal_complete_units=0,completed_combinations=0,goal_status='active',FinalAccepted=False)
d=read(files[2]);d['current_task']='v141 GuardMove7真实导入1371，Source279编译成功、旧196通过＋4目标语义RED已冻结；正在实现实际距离驱动的七组件绘制，原生实录与新试玩入口待验证'
d['current_status_authority']='docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/Stage0-status-sync-v001/status-v001.json'
d['current_compiled_snapshot']=pin(cm);d['guard_Move_v141_work_in_progress']=state;d['goal_status']='active';d['completed_content_units']=0
foundation=d['completed_foundation_checks'];foundation['ue_latest_total']=200;foundation['ue_latest_failed']=4;foundation['ue_latest_changes_verified']=False
foundation['ue_latest_report']=m['full_suite']['path'];foundation['ue_current_working_source_verified']=False
files[2].write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
header='''2026-10-18 当前进行中（EV048，v141）：守卫七件式Move源已真实导入，Production1371；Source279编译成功，旧196项通过、四处目标功能缺失均由真实测试检出并冻结。七组件绘制正在实现，实景仍沿旧占位，尚无本版原生画面验收。\n\n| 内容 | 已核实 | 下一步 |\n| --- | --- | --- |\n| 七件源与导入 | Rest252＋Near250/Far251；7个Texture2D512与导入源读回，旧1364包两遍SHA不变 | 固定128实际距离周期、全7资源原子绘制与一次镜像 |\n| 验证 | 原196通过；4目标语义RED，含真实owner/路径、body-hip连接和float顶点边界 | 200全部通过后验证双侧AI移动→攻击→停步实录 |\n| 当前试玩 | 上个完整GREEN仍为v140，旧v011入口会拒绝当前工作中的源码/资源 | 运行审阅后更新版本化手动入口 |\n\n原出生点越界导致的首次测试失败已独立保存；仅修正一处测试出生方向，全部功能断言、游戏边界及旧196测试保持。正式完整0/15、搭配0/20，目标active。本轮无生成调用，E下一批仍574。以下v140及更早内容是历史已验证检查点。\n\n'''
files[0].write_text(header+files[0].read_text(encoding='utf-8-sig'),encoding='utf-8')
with files[1].open('a',encoding='utf-8')as f:f.write('\n\n2026-10-18 EV048持续实施／v141进行中：七件Move原源已实际导入1371，Source279编译；旧196通过，四新目标语义RED已真实确认并冻结，开始七件渲染实现。独立补测body-hip/root和Canvas浮点坍缩边界；首轮测试把Guard放到-1390（MinX=-1350外）导致两前提失败，失败Source/DLL/报告永久保存，随后仅一字节修测试spawn到合法-970、全部功能断言与游戏不动，重新得到四真RED。旧六帧Move门与50非Move源不变；当前无新版原生/美术通过，手动入口待GREEN及运行审阅更新。正式0/15、搭配0/20、目标active；无生成、外部API0，非新增用户需求。\n')
with(out/'status-v001.json').open('x',encoding='utf-8')as f:json.dump(state,f,ensure_ascii=False,indent=2);f.write('\n')
receipt=dict(schema='Root-GuardMove7-Stage0-current-status-sync-v141-v001',utc=datetime.now(timezone.utc).isoformat(),before=before,
 after=[pin(q)for q in files],status=pin(out/'status-v001.json'),Source=279,Production=1371,full_green=False,old196_passed=True,semantic_RED_count=4,FinalAccepted=False)
with(out/'sync-receipt-v001.json').open('x',encoding='utf-8')as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(receipt=pin(out/'sync-receipt-v001.json'),Source=279,Production=1371,full_green=False)))
