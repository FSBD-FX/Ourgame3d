from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');O=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/current298-GREEN-stable142-status-v001';O.mkdir(parents=True,exist_ok=False);(O/'before').mkdir()
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
cm=R/'source-assets/production/backups/v143-HeroLandingPriority298-203GREEN-v001/compiled-source-manifest.json';d=read(cm);assert d['source_files']==298 and d['passed']==203
stable=R/'source-assets/production/fairytale-hero-air-v001/root-stable-preview-v001/actual-stable-admission-v001.json'
status=dict(schema='Root-current-landing-priority-v143-stable-v142-status-v001',utc=datetime.now(timezone.utc).isoformat(),goal_status='active',actual_development_source_files=298,actual_production_files=1419,actual_full_tests=203,compiled_manifest=pin(cm),source_admission=d['source_admission_pin'],supplemental_source_repair=d['supplemental_source_repair_pin'],native_landing_J_Shift='OPEN_four_fresh_cases_pending_independent_checker',stable_playable=pin(stable),stable_entry=(R/'钟盔轻甲固定试玩.cmd').as_posix(),stable_version='v142-CM52f906',stable_native_process_id=51516,stable_native_frames=174,stable_approval_scope='LIMITED_WIP',actual_stable_validate_only_exit=0,stable_startup_verification_slow_optimization_in_progress=True,full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,last_E_batch=615,next_E_batch=616,image_generation_calls_this_turn=0,external_API_calls=0,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
write(O/'current-status.json',status)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
 dst=O/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
README=files[0];old=README.read_text(encoding='utf-8-sig');head='2026-10-19 当前进行中（EV048，v143）：落地攻击／闪避观察代码已接入，开发工程Source298／Production1419，真实D3D11完整203项严格通过；四场左右朝向落地动作实录待独立核验器冻结。固定v142试玩已另存物理副本，实际174帧三跳、加载副本DLL、完整原片／混音及两遍核验通过，Root审18姿态和三处真实回接后允许有限试玩。[固定试玩](钟盔轻甲固定试玩.cmd) · [当前状态](docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/current298-GREEN-stable142-status-v001/current-status.json)。固定入口初次完整校验较慢，正在优化；旧v013入口因开发源码变动会拒绝。动作接续精修、完整原速观看／试听、落地四案和磁盘恢复仍OPEN，正式0/15、搭配0/20；目标active。本轮无生成，256／窗口11用16余8、外部API0。\n\n以下为历史检查点；开发版本与固定试玩版本分别以上述记录为准。\n\n'
README.write_text(head+old,encoding='utf-8')
p=files[1];q=read(p);q.update(current_task='v143 landing J/Shift observer integrated and strict203GREEN; four native cases next; stable v142 physical preview retained',current_build=d['build_log']['path'],current_build_exit_code=0,current_source_uncompiled_changes=False,current_compiled_snapshot=pin(cm),current_source_files=298,current_registered_tests=203,current_status_authority=pin(O/'current-status.json'),current_turn_progress_classification='Actual Source298/Production1419/203GREEN; stable v142 native174 and limited keyframe review; v143 action cases/checker pending; no complete units',current_stable_playable_v142=pin(stable))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n\n2026-10-19 EV048执行进展（非新增用户需求）：固定v142钟盔轻甲试玩已物理隔离并实际原生174帧三跳核验、E613–615保全及有限姿态审阅通过；开发v143落地J/Shift观察器准入Source298，修复UE5.5三处Printf literal调用后完整203严格通过，四场动作实录与磁盘恢复待推进。完整原速播放／试听及动作精修仍未完成，正式0/15与搭配0/20不变。\n')
p=files[3];g=read(p);g.setdefault('derived_deliveries',[]).append(dict(id='EV048-v143-landing-source298-GREEN-stable142-preview',type='native_observer_and_stable_preview_not_new_generation',utc=status['utc'],status=pin(O/'current-status.json'),image_generation_calls=0,formal_complete_units=0,FinalAccepted=False));p.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,Source_Content_untouched=True,FinalAccepted=False))
print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
