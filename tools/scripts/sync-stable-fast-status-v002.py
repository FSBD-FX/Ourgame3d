from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');EV=R/'docs/production/first-batch-v2/evidence/HeroLandingPriority-v143-v001';O=EV/'current298-GREEN-stable-fast142-status-v002';O.mkdir(exist_ok=False);(O/'before').mkdir()
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
old=EV/'current298-GREEN-stable142-status-v001/current-status.json';s=read(old)
proof=R/'source-assets/production/fairytale-hero-air-v001/root-stable-fast-admission-v002/actual-timed-validation-v002.json';p=read(proof);assert p['passed'] is True
s.update(schema='Root-current-landing-v143-fast-stable-v142-status-v002',utc=datetime.now(timezone.utc).isoformat(),stable_entry=(R/'钟盔轻甲快捷试玩.cmd').as_posix(),stable_startup_verification_slow_optimization_in_progress=False,stable_fast_gate_actual_elapsed_seconds=p['elapsed_seconds'],stable_fast_validation=pin(proof),native_landing_J_Shift='OPEN_four_fresh_cases_pending_checker_review_fix1',last_E_batch=616,next_E_batch=617,prior_status_pin=pin(old))
write(O/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for x in files:
 dst=O/'before'/x.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(x,dst)
x=files[0];text=x.read_text(encoding='utf-8-sig');head,rest=text.split('\n\n',1);assert '固定入口初次完整校验较慢，正在优化' in head
head=head.replace('[固定试玩](钟盔轻甲固定试玩.cmd)','[快捷试玩](钟盔轻甲快捷试玩.cmd)').replace('固定入口初次完整校验较慢，正在优化','固定入口完整校验实测约5.8秒').replace('current298-GREEN-stable142-status-v001','current298-GREEN-stable-fast142-status-v002');x.write_text(head+'\n\n'+rest,encoding='utf-8')
x=files[1];q=read(x);q.update(current_status_authority=pin(O/'current-status.json'),current_stable_fast_gate_validation_v002=pin(proof),current_stable_manual_entry=(R/'钟盔轻甲快捷试玩.cmd').as_posix(),current_task='v143 source298 strict203GREEN; Task2 checker scoped review fixes, four native landing cases next; independent stablev142 fast preview5.78sec validated');x.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048执行进展：固定v142快捷入口完成实际1778文件／引擎／原生证明全量校验，实测5.7827204秒；开发Source298改动后仍独立可用。只优化每次真实父路径查询，旧资源／原生174帧与旧入口保留。落地四案检查器三处漏验正在收紧，尚未宣称新原生动作通过。\n')
x=files[3];g=read(x);g.setdefault('derived_deliveries',[]).append(dict(id='EV048-stable142-fast-launch-v002',utc=s['utc'],actual_timed_validation=pin(proof),elapsed_seconds=p['elapsed_seconds'],status=pin(O/'current-status.json'),image_generation_calls=0,formal_complete_units=0,FinalAccepted=False));x.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write(O/'status-sync-receipt.json',dict(status=pin(O/'current-status.json'),after=[pin(x) for x in files],before_backups_preserved=True,actualSource_Content_unchanged=True,FinalAccepted=False));print(json.dumps(pin(O/'current-status.json'),ensure_ascii=False))
