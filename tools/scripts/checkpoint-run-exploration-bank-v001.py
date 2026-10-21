"""Record actual bounded bank results without promoting the whole game/Continue."""
from pathlib import Path
import hashlib,json,shutil
root=Path('F:/Ourgame');doc=root/'docs/production/first-batch-v2'
e=doc/'evidence/run-exploration-v001/production-v001';assert not e.exists();e.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for name,expected in [('060539',(0,2)),('061546',(1,1)),('061658',(2,0))]:
 p=root/f'UnrealGame/Saved/Automation/FirstRoom-20261016-{name}/index.json';r=json.loads(p.read_text(encoding='utf-8-sig'))
 assert (r['succeeded'],r['failed'])==expected and r['notRun']==0 and r['inProcess']==0
 assert sum(t.get('warnings',0) for t in r['tests'])==0
 target=e/f'actual-{name}-index.json';shutil.copy2(p,target)
 records.append({'report':p.relative_to(root).as_posix(),'succeeded':r['succeeded'],'failed':r['failed'],'warnings':0,'sha256':sha(p)})
files=[]
for name in ['DungeonRunExploration.h','DungeonRunExploration.cpp','DungeonGameMode.h','DungeonGameMode.cpp','DungeonHUD.h','DungeonHUD.cpp','Tests/DungeonRunExplorationTests.cpp']:
 p=root/'UnrealGame/Source/CodexDungeon'/name;t=e/name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
 assert p.read_bytes()==t.read_bytes();files.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(e/'manifest.json').write_text(json.dumps({'scope':'root Run exploration bank only; source review pending; aggregate/Continue not completed','actual_reports':records,'files':files,'formal_complete_units':0},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
proof='''# Bound Run探索记忆银行：真实路线与恢复

2026-10-16，UE5.5.4。原HUD内存转为Run持有的逐房间银行；绑定Run的HUD只读取它，未绑定美术观察仍沿原路径。每个完整GameMode Tick结束，用原Reveal算法采样真实玩家位置，不用Canvas才能产生存档内容。

实际060539两组均RED，均因没有真实银行来源；生产采样和房间迁移后061546为1GREEN/1RED，恢复测试已获得真实源并明确在Restore入口失败。补上候选完整校验与一次替换后061658两组均GREEN，零警告/失败/未运行。v080/v081/v082分别保留三阶段。

正常按键探索、正常击杀、出口E和Enter后，两个房间的每一个迷雾double与独立观察路线使用既有算法的结果完全相等；历史房间未被新房入口覆盖。另一个银行恢复真实单房源，完整字段、插值和派生计数相等；未知schema、无效Run/currentRoom、NaN、负数、缺格、重复房、错误显示编号及未知边界被原子拒绝。Capture返回副本，调用方改值不改变原银行。

银行安装发生在换房奖励退场成功之后；预备失败不改变旧银行。完整Tick技术守卫覆盖各分支；没有从丢失的HUD缓存回填空记忆。公共Restore只安装验证完的候选，未生成新Run或重放探索。

这些是实际UE自动化中的Actor/按键流程，尚未拍摄这次HUD迁移后的可见运行录像。聚合Capture四组061737在真实源前提下仍RED，随后生产正在制作；磁盘继续、完整装备/敌人/20搭配仍未完成，正式0/15。不能将这两组通过称为全部122通过或新进程Continue通过。
'''
(doc/'run-exploration-bank-runtime-proof-v001.md').write_text(proof,encoding='utf-8')
p=doc/'progress.json';shutil.copy2(p,e/'progress-before.json');s=json.loads(p.read_text(encoding='utf-8-sig'))
s['run_exploration_bank_v001']={'status':'actual2GREEN_bounded_owner_HUD_authority_migrated','reports':records,
 'snapshot':'source-assets/production/backups/2026-10-16_RunExploration-bank2GREEN-v082',
 'proof':'docs/production/first-batch-v2/run-exploration-bank-runtime-proof-v001.md','visible_runtime_recorded':False,'aggregate_installed':False,'disk_continue':False}
s['ue_current_working_source_verified']=False;s['ue_current_working_source_compiled']=False
s['current_source_uncompiled_changes']='v083 actualRunCapture4semanticRED frozen after bank2GREEN; newFighter pureforwarder and worker typedAggregate production currently being edited. No whole122GREEN claim.'
s['current_working_source_after_v075']=s['current_source_uncompiled_changes']
s['latest_targeted_UE_automation']={'report':'UnrealGame/Saved/Automation/FirstRoom-20261016-061737/index.json','registered':4,'succeeded':0,'failed':4,'notRun':0,'warnings':0,'scope':'Actual typed aggregate semantic RED with admitted genuine sources; production implementation in progress.'}
s['default_test_runner_expected_tests']=116;s['actual_registered_test_count_current']=122
s['generation_accounting_current']={'requested_count':150,'window_number':7,'window_requested_count':6,'window_limit':24,'remaining_in_window':18,'lifetime_requested_count':174,'external_api_calls':0,'fee_unknown':True}
s['fairytale_shoulders_v001'].update(status='near149 fourRGBA/staticwear candidate; far150 rawactualretained, extraction pending; no new runtime import',
 actual_far_request=150,far_raw_sha256='b841ae819703d167fbec35efc4cf2f9333ec78ab9f345de90ed2573015cede97',
 near_original_two_point_gate='unaccepted; B correspondences not established, preserved numerical failure',near_static_review='docs/production/first-batch-v2/fairytale-shoulder149-static-review-v001.md',
 retention_batches=['E097','E098','E099','E101','E102','E103'],failed_retention_batch='E100 partial MAX_PATH CopyFile2 error; not successful retention')
s['next_native_request']=151;s['next_retention_batch']='E104';s['next_snapshot']='v084';s['next_human_event']='EV-049'
s['current_turn_progress_classification']='progress: actualRunExploration2RED -> source1GREEN/Restore1RED -> bank2GREEN; aggregate4 genuine-source RED; native149near/150far actual components advancing; full goal0/15'
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
head='''2026-10-16当前续行：Run探索银行060539真实2RED→061546路线1GREEN/Restore1RED→061658两组GREEN，零warn/fail/notRun，v082冻结。正常探索/击杀/出口换房完整记忆保留；HUD读Run银行。061737聚合四组真实源语义RED/v083已冻；当前新增Fighter纯校验转发及Aggregate生产在编辑，未编译/未全122GREEN，default116。银行迁移后的可见录像待补；磁盘Continue/正式15仍未完。
EV048美术：149近肩4RGBA/静态穿戴候选，旧B对应歧义导致3px门失败保留；v003单A挂点合同正在冻结。150真实far四组件raw已E103保全，提取待做，无新UE导入。F/E097–099/101–103各双SHA0；E100深路径复制失败partial保留，不当成功。ledger150/window0076of24剩18/lifetime174/external0/费用未知；next151/E104/v084/人类EV049。root sole UE/UBT/native/import/ledger/media，不唤醒stale agent。
'''
for name in ['README.md','AGENTS.md']:
 q=root/name;old=q.read_text(encoding='utf-8-sig');q.write_text(head+'\n此前检查点记录（以顶部当前状态为准）：\n\n'+old,encoding='utf-8')
plan=root/'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md'
text=plan.read_text(encoding='utf-8')
old='- [ ] Root: move bound-Run exploration authority to a complete room bank using the existing Reveal algorithm at each completed GameMode Tick. HUD consumes the bank; unbound lookdev retains its existing path. Stage0 two genuine route/room-history/atomic-restore tests before production; current schema/type/getter stubs are uncompiled.'
new='- [x] Root bounded bank implementation/actualUE owner tests:0605392RED→0615461GREEN/Restore1RED→0616582GREEN/v082. CompletedTick originalReveal, exact per-room values and atomicRestore; HUD consumes Run authority, unbound lookdev unchanged. Visible running migration evidence and independent final review still required before whole integration acceptance.'
assert old in text;plan.write_text(text.replace(old,new),encoding='utf-8')
ledgerpath=root/'.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md'
with ledgerpath.open('a',encoding='utf-8') as f:
 f.write('\n2026-10-16 actualcontinuation: bank0605392RED/v080 → producer0615461GREEN+Restore1semanticRED/v081 → candidateRestore0616582GREEN/v082, actualnormalroute+kill+E/Enter memory exact percompletedTick. Aggregate061737actual4semanticRED/v083; legitimate source admitted. Root pureFightervalidator forwarder only added; workerAggregateproduction authorized, Source nowuncompiled. No whole122GREEN/Continue/formalunit claim. Art149 extracted4/staticcandidate; old3pxfailure retained becauseB correspondence insufficient. Native150actualfarraw/E103, fivecorrectedrefs+neworiginaltechnicalguide/E102, noexistingart edited. E100partialCopyFile2deep-pathfailure preserved; E101flat recovery beforeview. Currentledger150/window7 6of24remain18/lifetime174. No newhuman event.\n')
print(json.dumps({'bank_actual':records,'evidence_files':len(files),'progress_updated':True,'new_human_event':False,'formal_complete_units':0},ensure_ascii=False))
