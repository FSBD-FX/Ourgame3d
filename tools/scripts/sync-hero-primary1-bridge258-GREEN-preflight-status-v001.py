from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
EV=R/'docs/production/first-batch-v2/evidence/HeroPrimary1Bridge258-v146-v001'
O=EV/'current303-1439-GREEN-art-native-preflight-fix-v001';assert not O.exists()
prior=EV/'current303-1439-art-bound-tests-pending-v001/current-status.json'
cm=R/'source-assets/production/backups/v146-Primary1Bridge258-303-1439-203GREEN-v001/compiled-source-manifest.json'
assert pin(cm)['sha256']=='0943bc48284765015990b1621d5cd95046c450060030a59ad6f2025f17594fcd'
m=read(cm);suite=read(m['full_suite']['path'])
assert (suite['succeeded'],suite['succeededWithWarnings'],suite['failed'],suite['notRun'],suite['inProcess'])==(203,0,0,0,0)
s=read(prior);s.update(schema='Root-current303-1439-GREEN-art-native-preflight-fix-v001',utc=datetime.now(timezone.utc).isoformat(),prior_status_pin=pin(prior),current_compiled_manifest=pin(cm),current_whole_source_content_verified=True,current_full203_running=False,full_native203=dict(passed=203,failed=0,warnings=0,notRun=0,inProcess=0,report=m['full_suite']),new_art14_native_verified=False,first_art_native_attempt=dict(version='right_v001',preflight_failed=True,UE_started=False,reason='relative_path dependency parser',source_content_mutated=False),last_E_batch=643,next_E_batch=644,goal_status='active',FinalAccepted=False)
O.mkdir();(O/'before').mkdir();new(O/'current-status.json',s)
fs=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in fs:
 d=O/'before'/p.relative_to(R);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
t=fs[0].read_text(encoding='utf-8-sig');old,rest=t.split('\n\n',1)
head='2026-10-19 v146进行中：14张新起手贴图及前两帧轻甲／独立军剑已实际接入并编译。Source303／Production1439，原Native D3D11完整203严格通过，CM094已封存。左右实录的首次预检发现相对路径解析缺口并在UE启动前停止，最小修正已对实际工程预检通过，待独立复核后录制。历史音效198帧／10请求及原件已E640–643保全；完整视听和美术仍待验收。正式0/15、搭配0/20，目标active。'
t=head+'\n\n'+rest
t=t.replace('两格已提取、分层／配甲／边缘清理并E639；有限静图审阅，尚未实装','两格已提取、分层／配甲／边缘清理并E639；已实际导入与编译绑定，左右实录待核验')
fs[0].write_text(t,encoding='utf-8')
q=read(fs[1]);q.update(current_status_authority=pin(O/'current-status.json'),current_task='Capture new258 J right and left after scoped checker fix review; then Ready direct-entry proof',current_compiled_snapshot=pin(cm),current_source_files=303,current_production_packages=1439,current_source_uncompiled_changes=False,current_whole_source_content_verified=True,current_registered_tests=203,current_build_exit_code=0)
fs[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with fs[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 v146：新起手258的14张贴图与两个Source seam实际接入、编译及原203全部通过；Source303／Production1439、CM094。首次right_v001在UE启动前严格预检失败，原因是checker对relative_path依赖字段遗漏；保留失败E643，最小修正待复核。尚无新258左右实录，不当作动作或美术完成。\n')
g=read(fs[3]);assert g['requested_count']==258 and g['current_window']['requested_count']==18
g.setdefault('derived_deliveries',[]).append(dict(id='v146-primary1-bridge258-GREEN-preflight-fix-v001',utc=s['utc'],status=pin(O/'current-status.json'),image_generation_calls=0,external_API_calls=0,formal_complete_units=0,FinalAccepted=False))
fs[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(p) for p in fs],backups_preserved=True,Source_Content_unchanged=True,FinalAccepted=False));print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
