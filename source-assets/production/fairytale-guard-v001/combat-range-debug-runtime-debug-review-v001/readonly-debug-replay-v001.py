"""Readonly replay of exact frozen v002 checker. Writes only this NEW review directory."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path('F:/Ourgame');C=Path(__file__).resolve().parent
T=R/'source-assets/production/fairytale-guard-v001/combat-range-debug-tooling-candidate-v002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
p=argparse.ArgumentParser();p.add_argument('side',choices=['left']);a=p.parse_args()
archive=R/f'过程图稿与视频/2026-10-18_守卫范围默认关闭与显式调试Hurt试样_debug_{a.side}_v001'
index=read(archive/'index.json');snapshot=Path(index['snapshot']);prereg=Path(index['root_prereg']);orig=archive/'原件'
paths=[archive/'index.json',archive/'runtime.log',orig/'runtime-report.json',orig/'Hurt-independent-native-verification-v001.json',orig/'combat-range-debug-verification-v001.json',orig/'native-frame-pixels.jsonl',snapshot/'compiled-source-manifest.json',prereg,T/'combat-range-tooling-freeze-v002.json']
before=[pin(x)for x in paths]
out=C/f'debug-{a.side}-readonly-v002-replay.json';err=C/f'debug-{a.side}-readonly-v002-replay.stderr.txt';review=C/f'debug-{a.side}-host-review-v001.json'
assert not any(x.exists()for x in [out,err,review])
cmd=[sys.executable,'-B','-X','utf8',str(T/'tooling/verify-combat-range-log-v001.py'),'--archive',str(archive),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--expected-mode','debug1']
v=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');out.write_text(v.stdout,encoding='utf-8');err.write_text(v.stderr,encoding='utf-8')
after=[pin(x)for x in paths];assert before==after,'Readonly original inputs changed'
assert v.returncode==0,v.stderr
result=json.loads(v.stdout);assert result==read(orig/'combat-range-debug-verification-v001.json'),'Readonly range result differs from retained original receipt'
report=read(orig/'runtime-report.json');manifest=read(snapshot/'compiled-source-manifest.json')
summary=dict(schema='combat-range-debug-independent-host-review-v001',passed=True,mode='debug1',side=a.side,process_id=report['process_id'],native_observations=len(report['observations']),HUD_log_rows=result['HUD_log_rows'],all_HUD_enabled_one=True,maximum_submitted_range_lines=result['maximum_submitted_lines'],all_original_observations_exact_sim_matched=result['all_observations_exact_sim_matched'],actual_hit_AttackId=result['original_hit_attack'],same_original_Axe_Windup_observations=len(result['focus_witnesses']['AxeWindup']),same_original_Axe_Active_observations=len(result['focus_witnesses']['AxeActive']),HP_loss=result['original_HP_loss'],hit_at=result['original_hit_at'],HurtMask=result['HurtMask'],official_frozen_Hurt_oracle_rerun_equal=result['official_Hurt_checker_unchanged_rerun_equal'],range_replay_equal_to_retained_original_receipt=True,all_bound_original_inputs_before_after_two_SHA_unchanged=True,strict_registered_tests=manifest['strict_registered_tests'],input_pins=before,checker_stdout=pin(out),checker_stderr=pin(err),Source_or_archive_written=False,UE_started=False,UBT_started=False,algorithmic_PNG_CRC_and_optical_check_rerun=True,View_used=False,audio_reviewed=False,FinalAccepted=False,formal_complete_units=0)
assert summary['maximum_submitted_range_lines']==4 and summary['HurtMask']==15
review.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items()if k not in ['input_pins','checker_stdout','checker_stderr']},ensure_ascii=False))
