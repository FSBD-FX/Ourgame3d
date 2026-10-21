"""Actual candidate/static/import checkpoint, before any new compiled gameplay."""
from pathlib import Path
import hashlib,json,shutil
R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-armor-sword-primary1-v001';D=R/'docs/production/first-batch-v2';M=B/'macro-registration-primary1-v001'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=M/'delivery-freeze-v001.json';assert desc(f)['sha256']=='5ff4826bc868a846650ac53fc58f66adc46621f5c98e9052bcfaab2a009433af'
for x in load(f)['files']:assert desc(Path(x['path']))==x
receipt=R/'UnrealGame/Saved/Bootstrap/sword-armor-primary1-v001-import-20261016-044956-227837.json';r=load(receipt)
assert r['success'] and r['actual_count']==r['saved_count']==42 and r['old_packages_unchanged']==941
assert sum(p.is_file() for p in (R/'UnrealGame/Content/Production').rglob('*'))==983
new(B/'root-static42-candidate-review-v001.json',{'freeze':desc(f),'retention_before_view':'E180;71files2618523B;two size/SHA passes0diff',
 'actually_viewed':[desc(M/f'assemblies/frame-{i}-macro-no-sword.png') for i in range(6)],'view_px':[512,512],
 'facts':['All six head/eye-window shapes remain visible above armor in original512 composites','Chest is behind near sleeve/arm during crossed phase2 and down phase3; far shoulder can be occluded by that arm','Near cap outline reads separately from gray sleeve; phases0/4/5 retain the same overall metal family','Composites contain no independent weapon; no grip/blade clearance was reviewed here'],
 'reasoning':'Suitable as an explicitly bounded candidate for the first real Ready-to-Primary1 transition trial. Full-size static readability does not establish72px game readability.',
 'risks':['Chest orientation/width varies in phases1/2/3; actual motion and returning to Ready must be inspected','All actual component features have manual +-2sourcepx uncertainty; body targets are visible-cloth designs or explicit hidden trial choices, not measured bones','Shared ink/AA ownership bands and weapon/hand/helmet clearance remain unaccepted','Actual equipment ID, walks, later combos and all other states are not covered'],
 'proceed_to_bounded_game_trial':True,'static_art_finally_accepted':False,'full_motion_accepted':False,'formal_complete_units':0})
backup=D/'evidence/primary1-armor-v001/status-before-import42-v001';assert not backup.exists();backup.mkdir(parents=True)
for name in ['README.md','AGENTS.md','项目需求台账.md','docs/production/first-batch-v2/progress.json']:
 p=R/name;shutil.copy2(p,backup/p.name);assert desc(p)['sha256']==desc(backup/p.name)['sha256']
for name in ['README.md','AGENTS.md']:
 p=R/name;old=p.read_text(encoding='utf-8-sig')
 summary='2026-10-16当前：EV048首斩胸肩42分层Texture已实际导入/保存，old941不变、Production983。root已看六张512无武器组合，眼窗完整、横臂/下劈遮挡可进入实景试装；尚未运行新穿甲接线，不能据静态图认定72px辨识或动作完成。来源159身体24层、164胸/165近肩/167远肩18层；166错误中央圆盘与原30×28提取失败均保留，167新统一32×30全行规格通过基础QA，未放门。原图/派生/候选展示前E168–180保全。\n\nCodec Stage0已实际122948编译0→123141四组语义RED，v102冻结1410文件并复核不可变SHA零差。生产Codec与首斩8层HUD正在实现/复核，当前工作源码仍未编译，历史v101只有待机穿甲。人物72px、UI隐藏约束继续，正式完整0/15/目标active。\n\n此前检查点（历史）：\n\n'
 p.write_text(summary+old,encoding='utf-8')
p=D/'progress.json';d=load(p)
d.update(current_task='EV048 Primary1 armor42 actualimport/saved and six static candidates rootviewed; old941unchanged/Production983. New opt-in HUD and Codec production still uncompiled; actualv102 four semanticRED proved. Fullgoalactive0/15.',
 production_texture_count_actual=959,production_texture_count_scope='Actual983Productionpackages=959T_+22SW_+2M_;42new Primary1 Texture2Ds saved, old941unchanged',
 next_snapshot='v103',next_retention_batch='E181',ue_current_working_source_compiled=False,ue_current_working_source_verified=False)
d['fairytale_sword_primary1_armor_current_v001'].update(new_Texture2Ds_imported=42,actual_import_receipt=desc(receipt),old941_packages_unchanged=True,Production_packages=983,root_static_no_weapon_composites_viewed=6,static_review=desc(B/'root-static42-candidate-review-v001.json'),candidate_retention='E180',actual_game_rendered=False,full_motion_accepted=False,equipment_or_motion_accepted=False)
d['current_retention_batches']=[f'E{i}' for i in range(138,181)]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (R/'项目需求台账.md').open('a',encoding='utf-8') as f:f.write('\n| 2026-10-16；EV048继续执行，无新要求事件 | 首斩胸肩匹配 | 42分层Texture实际import/saved，old941不变/Production983；六张原512无武器组合已root审看并E180保全，眼窗/基本遮挡可试装。 | 新HUD/Codec当前未编译或录制；静态图不等于72px动态通过，完整0/15仍active。 |\n')
print(json.dumps({'actual_import_receipt':desc(receipt),'static_views':6,'Production_packages':983,'new_gameplay_rendered':False,'current_source_compiled':False,'formal_complete_units':0}))
