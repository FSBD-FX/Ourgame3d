"""Record actual bounded native Stomp trial, preserving previous manual entrypoints."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess

R=Path('F:/Ourgame');B=R/'source-assets/production/fairytale-guard-v001'
E=Path('E:/OurGame/Knight/过程图稿与视频')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
snapshot=R/'source-assets/production/backups/v139-Stomp193G';cm=read(snapshot/'compiled-source-manifest.json')
assert cm['source_files']==262 and cm['production_files']==1332 and cm['passed']==193 and cm['failed']==0
suite=read(R/cm['full_suite']['path']);assert len(suite['tests'])==193 and all(x['state']=='Success'and x['errors']==x['warnings']==0 for x in suite['tests'])
receipt_dir=R/'docs/production/first-batch-v2/evidence/guard-Stomp-v139-v001/root-native-checkpoint-v001'
assert not receipt_dir.exists();receipt_dir.mkdir(parents=True)
for name in ['README.md','项目需求台账.md','docs/production/first-batch-v2/progress.json','source-assets/production/first-unit-animation-v003/generation-ledger.json']:
 q=R/name;t=receipt_dir/'before'/name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,t)
native=[]
for side,number in [('left',541),('right',542)]:
 archive=R/f'过程图稿与视频/2026-10-18_怪诞守卫真实首个Stomp十二相闭环_{side}_v001'
 report=read(archive/'原件/runtime-report.json');ind_path=archive/'原件/independent-Stomp-native-verification-v001.json'
 if not ind_path.exists():
  matching=[p for p in(archive/'原件').glob('*.json')if read(p).get('schema')=='independent-Stomp50-native-verification-v001'];assert len(matching)==1;ind_path=matching[0]
 ind=read(ind_path);session=read(archive/'index.json')
 assert report['passed'] and ind['passed'] and session['exit_code']==0 and session['independent_passed']
 assert report['StompConfirmedHits']==1 and report['StompWindupMask']==63 and report['StompActiveMask']==3 and report['StompRecoveryMask']==15
 assert ind['actual_complete50_resident'] and ind['actual_quad_source_floor_and_mirror_verified'] and ind['optical_source_projection']['passed']
 retained=E/f'2026-10-18-OurgameUE-GuardStomp-native-{side}-v{number}/E-retention-index-v001.json';er=read(retained)
 assert er['verification_passes']==2 and er['source_and_member_hash_mismatches']==0
 native.append(dict(side=side,process_id=report['process_id'],frames=len(report['observations']),report=pin(archive/'原件/runtime-report.json'),independent=pin(ind_path),E_retention=pin(retained),confirmed_Stomp_hits=1,Guard_final_HP=report['guard_final_HP'],Hero_total_HP_loss=report['confirmed_HP_loss']))
media=R/'过程图稿与视频/2026-10-18_怪诞守卫跺击左右原生审阅_v001'
playback=R/'过程图稿与视频/2026-10-18_怪诞守卫跺击浏览器完整播放证明_v001'
for side in ['left','right']:
 d=read(playback/f'原件/{side}-ended-browser-v001.json')
 assert d['ended'] and d['paused'] and not d['loop'] and d['error'] is None and d['playbackRate']==1 and d['currentTime']==d['duration']
for batch in ['2026-10-18-OurgameUE-GuardStomp-review-media-v543','2026-10-18-OurgameUE-GuardStomp-browser-playback-v544']:
 d=read(E/batch/'E-retention-index-v001.json');assert d['verification_passes']==2 and d['source_and_member_hash_mismatches']==0
visual=receipt_dir/'Root-Stomp-native-and-visible-review-v139-v001.json'
write(visual,dict(schema='Root-GuardStomp-v139-native-and-visible-review-v001',utc=datetime.now(timezone.utc).isoformat(),
 compiled_manifest=pin(snapshot/'compiled-source-manifest.json'),full193=cm['full_suite'],native=native,
 source_pose_source_ids=[245,248],Root_12_phase_contacts_both_sides_viewed=True,Root_four_adjacent_join_pairs_both_sides_viewed=True,
 Root_full_1280x720_active_frame_both_sides_viewed=True,Root_browser_end_screens_both_sides_viewed=True,
 both_complete_silent_videos_actually_played_to_end=True,playback_index=pin(playback/'index.json'),
 scoped_gray_fallback_removed=True,scoped_native_logic_and_source_binding_passed=True,
 visual_decision='Keep bounded playable trial. Recovery1→2→3 has small authored translation, Recovery3→Ready1 has visible body/helmet/foot shift and source detail differences; polish remains.',
 risks=['Both actual returns chose Ready1; other three return phases only have predeclared source analysis, not new native captures.',
 'Late authored near shoe discrete shifts about2.990/2.517px; end eye to Ready1 about8.830x/5.122y, Euclidean10.208px. Not footlock.',
 'Original windup/source palettes and new low stance have different knee/torso proportions; native-size silhouettes readable but continuity not final.',
 'Knight/Bat are diagnostic predecessors. This is not manual whole-room completion, continuous audio acceptance or performance certification.',
 'Move6 remains deliberately unconfigured; Dodge32 remains unimported. Full15 units and20 combinations remain open.'],
 audio_recorded=False,footlock_certified=False,FinalAccepted=False,formal_complete_units=0,goal_status='active'))
launcher=R/'tools/scripts/launch-guard-room-native-trial-v010.ps1'
entries=['裂岩守卫挥斧试样.cmd','石廊三敌原生试玩.cmd','裂岩守卫三动作试样.cmd','钟盔轻甲倒地试玩.cmd','钟盔轻甲受击试玩.cmd']
changed=[]
for name in entries:
 q=R/name;before=pin(q);shutil.copy2(q,receipt_dir/'before'/name)
 text=q.read_text(encoding='utf-8-sig');assert text.count('launch-guard-room-native-trial-v009.ps1')==1
 q.write_text(text.replace('launch-guard-room-native-trial-v009.ps1','launch-guard-room-native-trial-v010.ps1'),encoding='utf-8',newline='\n');changed.append(dict(before=before,after=pin(q)))
new_entry=R/'裂岩守卫跺击试玩.cmd';assert not new_entry.exists()
new_entry.write_text('@echo off\ncd /d "F:\\Ourgame"\npwsh -NoProfile -ExecutionPolicy Bypass -File "F:\\Ourgame\\tools\\scripts\\launch-guard-room-native-trial-v010.ps1" -LightArtTrial -GuardFullArt\npause\n',encoding='utf-8',newline='\n')
preflight=subprocess.run(['pwsh','-NoProfile','-File',str(launcher),'-LightArtTrial','-GuardFullArt','-ValidateOnly'],capture_output=True,text=True,encoding='utf-8')
(receipt_dir/'manual-v010-ValidateOnly-v001.log').write_text(preflight.stdout+preflight.stderr,encoding='utf-8');assert preflight.returncode==0
facts=json.loads(preflight.stdout);assert facts['compiled_inputs_verified'] and facts['strict_registry']==193 and facts['source_files']==262 and facts['production_files']==1332 and facts['stomp_overlay'] and not facts['UE_started']
adoption=receipt_dir/'manual-v010-adoption-receipt-v001.json'
write(adoption,dict(schema='Root-guard-manual-v010-adoption-v139-v001',success=True,wrapper=pin(launcher),checkpoint=pin(B/'root-Stomp1332-checkpoint-v001/manual-input-v001.json'),
 validate_only_log=pin(receipt_dir/'manual-v010-ValidateOnly-v001.log'),facts=facts,preserved_old_v009=True,changed_entries=changed,new_entry=pin(new_entry),automatic_inputs=False,diagnostic_damage=False,FinalAccepted=False))
review=R/'docs/production/first-batch-v2/runtime-review-guard-Stomp-v139.md';assert not review.exists()
review.write_text('''# v139 石像守卫跺击：可玩试样

事实：落脚2相和收招4相已实际导入并接入，旧1326项保持，当前Production1332、Source262。完整193项严格通过，原190项保留。原预警900ms、落脚150ms、收招1500ms及命中规则不变。独立试样配置保留原44资源并补到50；Move6仍未准入。

| 实际记录 | 左侧 | 右侧 |
| --- | --- | --- |
| UE进程 | 62324 | 61308 |
| 原生电影帧／完整解码帧 | 472／472 | 499／499 |
| 首次自然跺击 | Aid2，预警6／落脚2／收招4 | 同左 |
| 严格相邻接续 | Ready→预警、预警→落脚、落脚→收招、收招→实际Ready1 | 同左 |
| 跺击正常命中 | 1次 | 1次 |
| 玩家结束HP／守卫HP | 63.1579／185 | 63.1579／185 |

推理与审阅：左右12相、四处原幅相邻接续和整体720p画面已Root实际审阅；两段完整静音原速录像均在浏览器播放至结束，无错误、无循环。画面中跺击不再切回灰色占位，小比例盔甲与持斧轮廓清楚，可继续用于试玩。

风险与剩余：收招后两相的作者回位会产生约2.99／2.52显示像素的离散近鞋位移，可能读作滑动；实际回Ready1头盔眼窗差约8.83横向／5.12纵向像素，身形与膝甲细节也有变化，仍需精修。保持源像素和整行比例，未宣称足锁、零跳变或最终美术。两侧本次都回Ready1，其余三相只有源分析。

录像前置Knight／Bat明确诊断清理；玩家和守卫按正常AI与战斗时钟运行。这不是整房手动通关、正常60FPS或声音验收。正式完整单元0/15、搭配0/20，目标继续。

| 资源 | 来源 | 当前状态 |
| --- | --- | --- |
| StompActive2 | 内置245，统一416px站姿基准 | 已导入、双侧实际绘制；精修待 |
| StompRecovery4 | 内置248，统一416px基准，后两相明确作者回位 | 已导入、双侧实际绘制；滑移待审修 |
| 原Guard44 | 原配置不变 | 独立旧入口契约保留 |
| Guard Move6 | 221／223／226不换腿；223另有边裁 | 拒绝准入，下一步两触地组件试验 |
| Hero Dodge32 | 现成源包与保全一致 | 尚未导入；后续原生接合 |

原生左右原件先保全E541／E542，审阅媒体E543，浏览器终态E544；均原字节两遍大小／SHA核对。242–248共7次内置请求，当前248、窗口11用8余16、累计272（另最初3张），外部API0，内置费用未知。失败源与旧稿均保留。

双击项目根目录“裂岩守卫跺击试玩.cmd”。Enter开局，E穿甲并等提交，WASD移动，J攻击，Shift闪避，Space跳跃，R重开。六个当前手动入口采用v010与实际193检查点，不带自动操作或诊断伤害。
''',encoding='utf-8')
archive=R/'过程图稿与视频/2026-10-18_守卫跺击运行记录与试玩入口_v001';assert not archive.exists()
for leaf in ['原件','展示副本']:(archive/leaf).mkdir(parents=True)
for src in [review,visual,adoption,launcher,new_entry]:
 for leaf in ['原件','展示副本']:shutil.copy2(src,archive/leaf/src.name)
write(archive/'index.json',dict(schema='Root-Stomp-v139-review-and-manual-entry-retention-v001',status='limited_trial_not_final',files=[pin(q)for q in sorted(archive.rglob('*'))if q.is_file()],native_media_E=[541,542,543,544],FinalAccepted=False))
(archive/'README.md').write_text('运行记录、Root审阅与v010试玩入口原件和展示副本分存；旧五入口已先在证据目录备份。当前是有限可玩试样，动作滑移和完整内容仍待，未发布。\n',encoding='utf-8')
print(json.dumps(dict(review=pin(review),visual=pin(visual),adoption=pin(adoption),text_archive=archive.as_posix(),new_manual_entry=pin(new_entry),Source262_Production1332_full193=True),ensure_ascii=False))
