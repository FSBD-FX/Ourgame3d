from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001';O=EV/'current303-1425-GREEN-matte-reviewed-v001'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
cm=R/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/compiled-source-manifest.json';d=read(cm)
assert pin(cm)['sha256']=='97d4d0290ce17ff2bb0c4a97b3c03d8921bb398c8d0eddef1505809eae77ebd5'
prior=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-native-reviewed-art258-status-v004/current-status.json'
s=read(prior);s.update(schema='Root-current303-locomotion-GREEN-matte-reviewed-v001',utc=datetime.now(timezone.utc).isoformat(),prior_status_pin=pin(prior),actual_development_source_files=303,actual_source_files=303,actual_production_files=1425,actual_production_textures=1419,actual_production_SoundWaves_added=6,actual_full_tests=203,compiled_manifest=pin(cm),source_admission=d['source_admission_pin'],supplemental_source_repairs=d['source_repair_admission_pins'],content_admission=d['content_admission_pin'],current_source_uncompiled_changes=False,SoundWaves_imported=True,initial_import_process_exit_code=1,fresh_readonly_process_exit_code=0,native_locomotion_audio_verified=False,native_audio_cue_requests_observed=False,native_runtime_ADPCM_decode_verified=False,next_task='Normal-input native locomotion cue observations and MainMix; request258 cleaned body/armor fit native preparation',last_E_batch=639,next_E_batch=640,formal_complete_units=0,completed_combinations=0,goal_status='active',FinalAccepted=False)
s['native_disk_restore_source300_historical_frames']=175
s['new_art258_matte_review']=dict(candidate='request258-primary1-body-correction/matte-edge-clean-candidate-v002',E_batch=639,Root_viewed_images=3,actual_runtime_imported=False,limited_findings='512px magenta edge substantially removed; fixed72px armor and sword silhouette retained. Slight dark edge remains; native transitions and full motion unverified.',FinalAccepted=False)
assert not O.exists();O.mkdir();(O/'before').mkdir();new(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
 dst=O/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
old=files[0].read_text(encoding='utf-8-sig');_,rest=old.split('\n\n',1)
head='2026-10-19 v145进行中：移动音效已实际接入Source303，Production现为1419纹理＋6新增SoundWave（合计1425）；干净Editor编译与原有Native D3D11完整203严格通过，CM97d4d029已封存。首次音效导入进程退出1但6资源保存成功，随后新进程只读核验退出0、完整原始PCM逐字节一致；运行时逐cue触发／ADPCM发声／混音与听感仍待验证。攻击起手258的两身体格、原轻甲／独立剑试装与边缘清理已完成候选并E639保全，已有限静图审阅，尚未实装。历史Source300双进程空中存档175帧验证保留。[快捷试玩](钟盔轻甲快捷试玩.cmd)保持独立v142；[当前状态](docs/production/first-batch-v2/evidence/HeroLocomotionAudio-v145-v001/current303-1425-GREEN-matte-reviewed-v001/current-status.json)。正式0/15、搭配0/20，目标active；内置请求258、窗口11用18余6、生命周期282另初始3；外部API0，内置费用未知。'
files[0].write_text(head+'\n\n'+rest,encoding='utf-8')
q=read(files[1]);q.update(current_status_authority=pin(O/'current-status.json'),current_task=s['next_task'],current_build=d['build_log']['path'],latest_build_attempt=d['build_log']['path'],current_build_exit_code=0,latest_build_attempt_exit_code=0,ue_current_working_source_compiled=True,ue_current_working_source_verified=True,current_source_uncompiled_changes=False,current_compiled_snapshot=pin(cm),current_source_files=303,current_registered_tests=203,production_texture_count_actual=1419,production_SoundWave_count_added=6,production_uasset_package_count_actual=1425,latest_strict_UE_automation=dict(report=d['full_suite'],succeeded=203,failed=0,notRun=0,mode='Actual unchanged complete203 Native D3D11 strictGREEN'),current_turn_progress_classification='Actual six SoundWaves and source binding compiled/full203; native cue/mix pending; cleaned art candidate reviewed, unimported')
files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 v145进展：Source303、1419纹理＋6新增SoundWave已编译并通过原有Native完整203。首次导入exit1与后续只读核验exit0均保留，不把原始PCM核对当作实际发声。修片258分层／配甲／去洋红边候选已E639并有限静图审阅，尚未游戏实装。下一步正常输入逐cue和实际混音；原速观看／听感与其余内容继续，正式0/15、搭配0/20。\n')
g=read(files[3]);g.setdefault('derived_deliveries',[]).append(dict(id='v145-source303-1425-full203-and-matte-review-v001',utc=s['utc'],status=pin(O/'current-status.json'),compiled_manifest=pin(cm),image_generation_calls=0,external_API_calls=0,formal_complete_units=0,FinalAccepted=False));files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,FinalAccepted=False))
print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
