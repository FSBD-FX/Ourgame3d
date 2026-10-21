"""Record actual v144 compile/full203, with native restore still explicitly pending."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
R=Path('F:/Ourgame')
O=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-GREEN-native-pending-status-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
prior=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001/current298-four-native-audio-candidates-status-v004/current-status.json'
cm=R/'source-assets/production/backups/v144-HeroAirDiskRestore300-203GREEN-v001/compiled-source-manifest.json'
assert pin(cm)['sha256']=='fb225bef1e9b2e3584a16d3eff192bd39587867b68c0fcdb525a4d876324e59a'
d=read(cm);assert d['registered_tests']==d['passed']==203 and d['failed']==d['notRun']==0
s=read(prior);s.update(schema='Root-current-air-disk-restore-build-v144-status-v001',utc=datetime.now(timezone.utc).isoformat(),prior_status_pin=pin(prior),actual_development_source_files=d['source_files'],actual_production_files=d['production_files'],actual_full_tests=203,compiled_manifest=pin(cm),source_admission=d['source_admission_pin'],supplemental_source_repairs=d['source_repair_admission_pins'],actual_v144_native_verified=False,v144_native='PENDING_fresh_checker_review_then_new_actual_source_and_pristine_target_processes',next_task='Actual two-process Air Apex disk save/restore; armor and action pose polish thereafter',last_E_batch=626,next_E_batch=627,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
s.pop('supplemental_source_repair',None)
O.mkdir(parents=True);(O/'before').mkdir();new(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
 dst=O/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
old=files[0].read_text(encoding='utf-8-sig');_,rest=old.split('\n\n',1)
head='2026-10-19 当前进行中（EV048，v144）：空中存档／新进程继续观察代码独立复核通过并接入，开发工程Source300／Production1419；实际Editor编译成功，原有D3D11完整203项严格通过，字节快照已封存。双进程实录仍待核验器独立复核及执行，尚不能宣称磁盘恢复通过。此前四案763帧落地接攻击／闪避已核验，六条本地动作音效候选已备齐并E626保全，尚未导入／绑定／试听。[快捷试玩](钟盔轻甲快捷试玩.cmd)保持独立v142；[当前状态](docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-GREEN-native-pending-status-v001/current-status.json)。落地起身、盔甲体积／轮廓、攻击力量感、完整原速播放与听感仍OPEN，正式0/15、搭配0/20；目标active。无新增图像生成或外部API调用。'
files[0].write_text(head+'\n\n'+rest,encoding='utf-8')
q=read(files[1]);q.update(current_status_authority=pin(O/'current-status.json'),current_task=s['next_task'],current_build=d['build_log']['path'],latest_build_attempt=d['build_log']['path'],current_build_exit_code=0,latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,current_compiled_snapshot=pin(cm),current_source_files=d['source_files'],current_registered_tests=203,production_texture_count_actual=d['production_files'],production_uasset_package_count_actual=d['production_files'],latest_strict_UE_automation=dict(report=d['full_suite'],succeeded=203,failed=0,notRun=0,mode='Actual unchanged complete203 Native D3D11 strictGREEN'),current_turn_progress_classification='v144 actual reviewed source admission/build/full203; new-process disk restore not yet executed; art/SFX open')
files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048执行进展：v144空中存档观察器独立代码审阅通过，实际Source300／Production1419编译与原有Native D3D11完整203测试严格通过；尚未执行双进程保存／恢复实录。护甲和动作衔接精修及音效实际绑定仍待继续，正式0/15、搭配0/20不变。\n')
g=read(files[3]);g.setdefault('derived_deliveries',[]).append(dict(id='EV048-v144-source300-build-full203-v001',utc=s['utc'],status=pin(O/'current-status.json'),compiled_manifest=pin(cm),image_generation_calls=0,external_API_calls=0,formal_complete_units=0,FinalAccepted=False));files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,FinalAccepted=False))
with (R/'.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/progress.md').open('a',encoding='utf-8') as f:f.write('\nRoot actual Task1 admission approved, Source inventory derived300 / Production1419 unchanged; Editor034859 exit0 and native full203034948 strictGREEN. CMfb225bef frozen with1723 current byte pins/twoSHA0. Task2 fresh independent review pending; no prereg/profile/native restore yet.\n')
print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
