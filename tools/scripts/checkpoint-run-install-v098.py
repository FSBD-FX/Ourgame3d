"""Audit actual UE reports and both snapshot endpoints before documenting them."""
from pathlib import Path
import datetime, hashlib, json

R = Path('F:/Ourgame')
E = R / 'docs/production/first-batch-v2/evidence/run-install-v001'
SN = R / 'source-assets/production/backups/2026-10-16_RunInstall-extraStagePrimitive-actual126GREEN-v098'
REPORT = R / 'UnrealGame/Saved/Automation/FirstRoom-20261016-094815/index.json'
ATOMIC = R / 'UnrealGame/Saved/Automation/FirstRoom-20261016-094653/index.json'
OLD = R / 'UnrealGame/Saved/Automation/FirstRoom-20261016-074841/index.json'

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def desc(p):
    b = p.read_bytes()
    return {'path':p.as_posix(), 'bytes':len(b), 'sha256':hashlib.sha256(b).hexdigest()}

def new(p, v):
    assert not p.exists(), p
    p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report, atomic, old = map(load, (REPORT, ATOMIC, OLD))
for d,n in ((report,126),(atomic,1),(old,122)):
    assert d['succeeded']==n and len(d['tests'])==n
    assert all(d[k]==0 for k in ('failed','notRun','inProcess','succeededWithWarnings'))
    assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in d['tests'])
names = {t['fullTestPath'] for t in report['tests']}
assert len(names)==126 and {t['fullTestPath'] for t in old['tests']} <= names
actual = [x['event']['message'] for x in atomic['tests'][0]['entries']]
assert any('registered=1 storedPolicy=1 installed=0 ready=1 gate=1' in s for s in actual)
m = load(SN/'compiled-source-manifest.json')
checks=[]
for row in m['files']:
    for endpoint in (R,SN):
        p=endpoint/row['path']; a=desc(p)
        assert a['bytes']==row['bytes'] and a['sha256']==row['sha256'], p
        checks.append({'path':p.as_posix(),'matches':True})
assert len(checks)==2522
independent = E/'production-v002-independent-review-v001.md'
assert desc(independent)['sha256']=='d30ae02592eab79dea3100c702d6d40e30da809942b3c51e47709e9f9cc0b428'
feedback = E/'root-gate-independent-review-v002.md'
assert desc(feedback)['sha256']=='674d9342bc0f4dedea33b868cb0ed7af3c06632d140e80e54a03eddb2e7d5537'
audit={
    'schema':'run-install-actual-postfix-audit-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
    'full_report':desc(REPORT),'full_actual_success':126,'atomic_report':desc(ATOMIC),
    'actual_extra_primitive_rejected_message':actual,'old122_names_preserved':True,
    'snapshot_manifest':desc(SN/'compiled-source-manifest.json'),'snapshot_files':len(m['files']),
    'snapshot_bytes':m['bytes'],'endpoint_checks':len(checks),'mismatches':0,
    'independent_geometry_source_review':desc(independent),'independent_feedback_source_review':desc(feedback),
    'source_DLL_packages_compiled_and_bound':True,'real_sound_audition':False,
    'codec_disk_new_process_continue':False,'formal_complete_units':0,'checks':checks}
new(E/'actual-postfix126-audit-v001.json',audit)
note='''# 暂停恢复安装的实际回归检查点

2026-10-16。094241 构建成功；094653 单项测试实际拒绝已注册的额外碰撞组件，保留准备组和旧 Run；094815 默认完整 126 项全部成功，零警告、失败、未运行和进行中。原 122 项名称均保留。v098 冻结 1261 文件、80,089,392 字节，主目录与冻结目录共 2522 次大小／SHA256 检查零差。

原 093342 实际失败和 v097 保持原样。修复只要求暂存场景障碍的自有 primitive 集合恰为已核对的唯一 RootBox；源代码独立复核读取了本机 UE 的 OwnedComponents 实现。另两处 HUD 反馈消费者在暂停恢复门关闭时立即返回，已编译进本次 DLL；历史事件、游标和声音配置未改，但没有由此声称已试听声音或验收混音。

这是内存中事务准备、安装、输入恢复门的检查点。完整序列化、磁盘提交、新进程正常 Continue 仍未完成；实际游戏可见录像另有独立来源，不能用本次测试替换其历史 DLL。首批完整内容仍为 0/15。
'''
new(R/'docs/production/first-batch-v2/run-install-runtime-proof-v001.md',note)

P=R/'docs/production/first-batch-v2/progress.json'; d=load(P)
d['current_compiled_snapshot']=SN.relative_to(R).as_posix()
d['ue_current_working_source_compiled']=True
d['current_source_uncompiled_changes']='None in Source after actual094241 build / full094815126GREEN; bounded in-memory install only, not disk Continue or complete content.'
d['latest_strict_UE_automation']={'report':REPORT.relative_to(R).as_posix(),'registered':126,'succeeded':126,'failed':0,'notRun':0,'inProcess':0,'warnings':0,'old122_registration_names_preserved':True,'scope':'actual production-v002 extra owned primitive rejection plus compiled feedback gates; complete registered regression only','formal_complete_units':0}
d['latest_targeted_UE_automation']={'report':ATOMIC.relative_to(R).as_posix(),'registered':1,'succeeded':1,'failed':0,'notRun':0,'warnings':0,'scope':'actual extra staged primitive rejection and original Run retention'}
d['next_snapshot']='v099'
ri=d['run_install_v001']; ri.update({'snapshot':SN.relative_to(R).as_posix(),'production_uncompiled':False,'actual_extra_primitive_RED':'UnrealGame/Saved/Automation/FirstRoom-20261016-093342/index.json','actual_extra_primitive_GREEN':ATOMIC.relative_to(R).as_posix(),'actual_full_GREEN':REPORT.relative_to(R).as_posix(),'source_feedback_gate_fix_compiled':True,'known_pending':'codec/disk/new-process Continue; real audio audition and complete content','postfix_audit':'docs/production/first-batch-v2/evidence/run-install-v001/actual-postfix126-audit-v001.json','independent_extra_primitive_review':independent.relative_to(R).as_posix(),'bounded_in_memory_install':True})
sw=d['fairytale_sword_v001']; sw['primary1_source']='source-assets/production/fairytale-sword-v001/run-primary1-v002'; sw['status']='actual real-input double-facing trial reviewed; Ready/return blade/helmet crowded, low guard redesign pending; incomplete all states/armor/combos/audio'; sw['independent_visual_review']='docs/production/first-batch-v2/evidence/sword-body-v001/independent-runtime-selected-frames-review-v001.md'
sw['retention_batches']=list(dict.fromkeys(sw['retention_batches']+['E136','E137']))
P.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary='2026-10-16当前：钟盔军剑155待机4帧＋157首斩6帧已实际导入并通过真实Enter/A/J双向试录；人物最高72px、无UI。待机／收招竖剑与头盔相挤，正调整低位单手持握；胸肩大轮廓、全动作与四甲适配未完成。暂停恢复安装094241编译、094653额外碰撞组件拒绝及094815完整126回归通过，v098两端2522大小／SHA零差；内存安装不等于磁盘Continue，正式完整0/15。'
for name in ('README.md','AGENTS.md'):
    p=R/name; text=p.read_text(encoding='utf-8-sig'); first,rest=text.split('\n\n',1)
    assert first.startswith('2026-10-16进行中：新131钟盔持剑Ready155')
    p.write_text(summary+'\n\n'+rest,encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:
    f.write('\n| 2026-10-16；EV048持剑适配续行（非新人类事件） | REQ-010/019/020/022/023 | 原155待机4＋157首斩6实际导入10纹理、真实双向按键试录；完整126回归与额外碰撞组件回滚修复通过。 | 待机与收招持剑挤盔，需改低位护持；宏观甲层、全动作／三段／音效未完。内存安装仅分项证据，0/15，下一人类事件EV049。 |\n')
with (R/'.superpowers/sdd/2026-10-15-bound-run-capture-restore/progress.md').open('a',encoding='utf-8') as f:
    f.write('\n2026-10-16 checkpoint: production-v002 actual094653Atomic1GREEN→094815default126GREEN after094241build0. v0981261files80089392B,2522endpointSHA/size0diff; old122names preserved. Geometry source independent d30ae025 and feedback674d9342 read/hash verified. Only bounded memory install accepted; codecs/disk/fresh-process Continue remain open. Sword real-J historical movie remains v096 and visual silhouette needs work.\n')
plan=R/'docs/superpowers/plans/2026-10-15-bound-run-capture-restore.md'; text=plan.read_text(encoding='utf-8-sig')
oldline='- [ ] Add aggregate cross-reference validation and transactional paused installation; separate geometry reconstruction from SpawnRoom/new-Run semantics.'
assert oldline in text
text=text.replace(oldline,'- [x] Bounded aggregate cross-reference validation and transactional paused installation; actual4semanticRED/v095 → full126/v096 → extra primitive actualRED/v097 → narrowfix/full126/v098. Geometry reconstruction is separate from SpawnRoom/new-Run semantics; this does not complete disk Continue.',1)
plan.write_text(text,encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k!='checks'},ensure_ascii=False))
