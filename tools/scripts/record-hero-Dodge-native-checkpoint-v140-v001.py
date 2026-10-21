"""Record actual scoped Dodge proof and adopt the verified normal v011 entry."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
O=R/'docs/production/first-batch-v2/evidence/hero-Dodge32-v140-v001/root-native-checkpoint-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
cmfile=R/'source-assets/production/backups/v140-Dodge196G/compiled-source-manifest.json';cm=read(cmfile)
assert(cm['source_files'],cm['production_files'],cm['passed'],cm['failed'])==(273,1364,196,0)
for prefix,count in [('UnrealGame/Source/',273),('UnrealGame/Content/Production/',1364)]:
 rows=[x for x in cm['files']if x['path'].startswith(prefix)];assert len(rows)==count
 assert {q.relative_to(R).as_posix()for q in(R/prefix).rglob('*')if q.is_file()}=={x['path']for x in rows}
 for x in rows:
  actual=pin(R/x['path']);assert(actual['bytes'],actual['sha256'])==(x['bytes'],x['sha256'])
native=[];media=[]
for side in ['left','right']:
 archive=R/f'过程图稿与视频/2026-10-18_钟盔真实Shift向外闪避四相试样_{side}_v002'
 report=read(archive/'原件/runtime-report.json');verified=read(archive/'原件/Dodge-independent-native-verification-v002.json');session=read(archive/'index.json')
 assert report['passed']and verified['passed']and session['independent_passed']and session['exit_code']==0
 assert report['DodgeMask']==15 and verified['native_Dodge_frames']==[0,1,2,3]and verified['original400ms_unblocked185_verified']
 assert verified['actual33resident_and9slots_verified']and verified['optical_source_projection']['passed']and len(verified['actual_adjacent_joins'])==2
 playback=R/f'过程图稿与视频/2026-10-18_钟盔侧闪浏览器完整播放证明_v001/原件/{side}-ended-browser-v001.json';played=read(playback)
 assert played['ended']and played['paused']and not played['loop']and played['error']is None and played['playbackRate']==1 and played['currentTime']==played['duration']
 folder=R/f'过程图稿与视频/2026-10-18_钟盔侧闪左右实录审阅_{side}_v002';m=read(folder/'source-version-status-index.json')
 timing=m['presentation_frame_retention'];assert timing['decoded_frames']==timing['native_frames']==len(report['observations'])and m['required_sample_count']==4 and m['required_join_count']==5
 native.append(dict(side=side,process_id=report['process_id'],observations=len(report['observations']),Dodge_draws=verified['native_Dodge_draws'],Ready_callbacks=report['ReadySeen'],Walk_callbacks=report['WalkSeen'],accepted_walk=report['accepted_walk'],player_final_HP=report['observations'][-1]['HP'],Guard_final_HP=report['guard_final_HP'],report=pin(archive/'原件/runtime-report.json'),independent=pin(archive/'原件/Dodge-independent-native-verification-v002.json'),session=pin(archive/'index.json'),playback=pin(playback)))
 media.append(dict(side=side,index=pin(folder/'source-version-status-index.json'),video=m['video']))
assert not O.exists();O.mkdir()
for name in ['README.md','项目需求台账.md','docs/production/first-batch-v2/progress.json','source-assets/production/first-unit-animation-v003/generation-ledger.json']:
 p=R/name;t=O/'before'/name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
visual=O/'Root-Dodge-native-and-visible-review-v140-v001.json'
write(visual,dict(schema='Root-Dodge-v140-native-and-visible-review-v001',utc=datetime.now(timezone.utc).isoformat(),compiled_manifest=pin(cmfile),full196=cm['full_suite'],native=native,media=media,
 actual_four_phases_both_sides_viewed=True,actual_five_adjacent_pairs_both_sides_viewed=True,fixed_native100pct_cropboards_viewed=True,both_complete_silent_videos_played_to_end=True,both_browser_end_screens_viewed=True,
 visual_decision='Keep scoped playable SWD001/LGT001 outward side-dodge trial: small armored silhouette and sword/armor stay visible; original end returns to equipped Ready then Walk.',
 risks=['Only one outward unblocked action per side is native scope; backwards/blocked/interruption coverage is automation, not these videos.',
 'Prepared source EDIT protection/buckle registration failures remain recorded; torso/waist shape and pose changes still need polish. Source preparation review is not changed to final acceptance.',
 'Native author Root/Grip/axis and actual quad/source pixels are verified; physical floor contact, hidden socket and footlock are not certified.',
 'Guard Move still uses the visible gray geometric fallback in the final recording. New seven-part walking author trial is not yet imported or wired.',
 'Knight/Bat predecessors use explicit diagnostic clearance. Videos are silent, not whole-room manual play or complete audio/VFX acceptance.'],
 proof_tool_repairs=['Normalized retained artist direction is compared strictly to the compiled unit direction; Root/Grip and all geometric/pixel tolerances unchanged.',
 'Ready-to-Walk recovery credit is confined to the same completed action; genuine pre-action staging transitions remain recorded and excluded from recovery credit.'],
 original_failed_left_v001_preserved=True,source_tests_unchanged_by_proof_repair=True,FinalAccepted=False,formal_complete_units=0,complete_combinations=0,goal_status='active'))
launcher=R/'tools/scripts/launch-guard-room-native-trial-v011.ps1'
check=subprocess.run(['pwsh','-NoProfile','-File',str(launcher),'-LightArtTrial','-GuardFullArt','-ValidateOnly'],capture_output=True,text=True,encoding='utf-8')
(O/'manual-v011-ValidateOnly-v001.log').write_text(check.stdout+check.stderr,encoding='utf-8');assert check.returncode==0
facts=json.loads(check.stdout);assert facts['strict_registry']==196 and facts['source_files']==273 and facts['production_files']==1364 and not facts['UE_started']and not facts['automatic_inputs']and not facts['diagnostic_damage']
names=['裂岩守卫挥斧试样.cmd','石廊三敌原生试玩.cmd','裂岩守卫三动作试样.cmd','钟盔轻甲倒地试玩.cmd','钟盔轻甲受击试玩.cmd','裂岩守卫跺击试玩.cmd'];changed=[]
for name in names:
 p=R/name;old=pin(p);shutil.copy2(p,O/'before'/name);text=p.read_text(encoding='utf-8-sig');assert text.count('launch-guard-room-native-trial-v010.ps1')==1
 p.write_text(text.replace('launch-guard-room-native-trial-v010.ps1','launch-guard-room-native-trial-v011.ps1'),encoding='utf-8',newline='\n');changed.append(dict(before=old,after=pin(p)))
entry=R/'钟盔轻甲闪避试玩.cmd';assert not entry.exists();entry.write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v011.ps1" -LightArtTrial -GuardFullArt\npause\n',encoding='utf-8',newline='\n')
adoption=O/'manual-v011-adoption-receipt-v001.json';write(adoption,dict(schema='Root-Dodge-v011-manual-adoption-v140-v001',success=True,wrapper=pin(launcher),checkpoint=pin(R/'source-assets/production/fairytale-hero-state-gap-v001/root-Dodge1364-checkpoint-v001/manual-input-v001.json'),validation=pin(O/'manual-v011-ValidateOnly-v001.log'),facts=facts,changed_entries=changed,new_entry=pin(entry),old_v010_preserved=True,FinalAccepted=False))
doc=R/'docs/production/first-batch-v2/runtime-review-hero-Dodge-v140.md';assert not doc.exists()
doc.write_text('''# v140 钟盔军剑＋轻甲侧闪：可玩试样

事实：SWD001／LGT001 的32张分层已实际导入，复用独立军剑，共33驻留资源、每相9个实际绘制层。Source273／Production1364，完整196项严格通过，原193项保留。沿用原400ms动作、185位移、1.2s冷却及60–200ms无敌窗口，未改战斗／输入／存档规则。

| 实录 | 左侧 | 右侧 |
| --- | --- | --- |
| 真实UE进程 | 61732 | 48420 |
| 原生帧＝完整解码帧 | 310 | 339 |
| 侧闪绘制／四相 | 11／全四相 | 11／全四相 |
| 回待机／普通行走回调 | 2／4 | 2／4 |
| 正常输入 | Enter、E、WASD、一次向外Shift | 同左 |
| 传统HUD／范围调试 | 隐藏／关闭 | 隐藏／关闭 |

推理：左右军剑、轻甲与小比例轮廓在真实侧闪及回待机／回行走中保留，原时钟、实际GPU quad和源像素核验通过；保留为限定可玩试样。Root已审四相、五组真实相邻接续、100%原像素裁切和两段完整静音播放。

风险与剩余：胸腰／甲片配准与姿态跳变继续精修，旧源EDIT保护失败记录不改；没有足锁、隐藏骨socket或声音验收。此次只覆盖向外无阻侧闪，后退、受阻和中断是自动化检查覆盖。Knight／Bat为明确的前置诊断清理。末帧守卫追击仍是灰色几何占位；新的七组件Move仅作者试拼，尚未接入。

首次left_v001的核验失败与原件完整保留：一处错将单位方向与原始向量比较，一处误把动作前起步计入动作后回接。新核验工具只修这两处规则表达，保留全部门槛，重新左右实录通过。正式完整0/15、完整搭配0/20，目标继续。

[侧闪试玩](../../../钟盔轻甲闪避试玩.cmd) · [左侧静音实录](../../../过程图稿与视频/2026-10-18_钟盔侧闪左右实录审阅_left_v002/展示副本/hero-Dodge4-native-DIAGNOSTIC-silent-v002.mp4) · [右侧静音实录](../../../过程图稿与视频/2026-10-18_钟盔侧闪左右实录审阅_right_v002/展示副本/hero-Dodge4-native-DIAGNOSTIC-silent-v002.mp4)

操作：Enter开局，E穿甲，WASD移动，J攻击，Shift侧闪，Space跳跃，R重开。手动入口没有自动输入或诊断伤害。
''',encoding='utf-8')
print(json.dumps(dict(review=pin(visual),manual_adoption=pin(adoption),document=pin(doc),formal_complete_units=0),ensure_ascii=False))
