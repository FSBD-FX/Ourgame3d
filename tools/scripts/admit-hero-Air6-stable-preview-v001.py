"""Root admits an actually run, retained and keyframe-reviewed fixed WIP preview."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');S=R/'Playables/钟盔轻甲-v142-CM52f906';N=R/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_right_v004';V=R/'过程图稿与视频/2026-10-19_钟盔稳定副本有限审阅记录_v001/原件/Root-staged-limited-review-v001.json';E=Path('E:/OurGame/Knight/过程图稿与视频')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p,local=False):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.relative_to(S).as_posix() if local else p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
review=read(V);assert review['RootApproved'] is True and review['Root_visible_keyframes_reviewed'] is True and review['FinalAccepted'] is False
supp=read(N/'staged-native-supplement-v001.json');assert supp['passed'] is True and supp['post_native_runtime_full_two_pass_verified'] is True
idx=read(N/'index.json');assert idx['exit_code']==0 and idx['process_id']==51516
retention=E/'2026-10-19-本项目E615-钟盔稳定副本有限审阅-v001/E-retention-index-v001.json';er=read(retention)
assert er['full_source_member_retention'] is True and er['verification_passes']==2 and er['source_and_member_hash_mismatches']==0
assert any(x['source']==V.as_posix() and (x['bytes'],x['sha256'])==(pin(V)['bytes'],pin(V)['sha256']) for x in er['files'])
O=S/'_proof/native-v004';O.mkdir(exist_ok=False)
sources=[N/n for n in ['native-independent-verification-v004.json','staged-native-supplement-v001.json','actual-loaded-staged-module-v001.json','launch-receipt-v001.json','index.json','brown-Ready-identity-verification-v001.json','原件/runtime-report.json']]+[V,retention,E/'2026-10-19-本项目E613-钟盔稳定副本原生三跳-v004/E-retention-index-v001.json',E/'2026-10-19-本项目E614-钟盔稳定副本完整视听对照-v004/E-retention-index-v001.json']
evidence=[]
for i,p in enumerate(sources):
 dst=O/(f'{i:02d}-'+p.name);assert not dst.exists();shutil.copy2(p,dst)
 for repeat in range(2):assert (pin(dst)['bytes'],pin(dst)['sha256'])==(pin(p)['bytes'],pin(p)['sha256'])
 evidence.append(pin(dst,True))
proof=dict(schema='HeroAir6-Root-staged-native-proof-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,actual_editor_game_native_execution=True,actual_staged_project_and_DLL_loaded=True,actual_process_id=51516,native_process_exit_code=0,Root_verified_before_and_after_runtime_equal=True,normal_manual_flags_verified=True,engine_build_id='37670630',source_CM_sha256='52f906018a042d006db3470ec2fa7b4603a6b54e2489ab33d2bdff0bf309cd62',runtime_manifest_pin=pin(S/'_proof/runtime-snapshot-manifest-v001.json',True),staged_project_path=(S/'CodexDungeon.uproject').as_posix(),evidence_pins=evidence,capture_control=supp['capture_control'],human_playtest=False,full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,FinalAccepted=False)
proofpath=S/'_proof/Root-staged-native-proof-v001.json';write(proofpath,proof)
approval=dict(schema='HeroAir6-Root-stable-manual-approval-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,approval_scope='LIMITED_WIP',stage_root=S.as_posix(),manual_trial_allowed=True,Root_staged_visible_keyframes_reviewed=True,runtime_manifest_pin=pin(S/'_proof/runtime-snapshot-manifest-v001.json',True),stage_copy_receipt_pin=pin(S/'_proof/stage-copy-receipt-v001.json',True),staged_native_proof_pin=pin(proofpath,True),Root_visible_review_receipt_pin=evidence[7],full_realtime_playback_reviewed=False,audio_listened=False,known_pose_join_refinement_open=True,FinalAccepted=False)
approvalpath=S/'_proof/Root-stable-approval-v001.json';write(approvalpath,approval)
wrapper=R/'tools/scripts/launch-hero-stable-preview-v001.ps1'
with wrapper.open('x',encoding='utf-8') as f:f.write("param([switch]$ValidateOnly)\n& 'F:/Ourgame/Playables/钟盔轻甲-v142-CM52f906/_proof/tools/launch-stable-preview-v001.ps1' -LightArtTrial -GuardFullArt -ValidateOnly:$ValidateOnly\n")
entry=R/'钟盔轻甲固定试玩.cmd'
with entry.open('xb') as f:f.write(b'@echo off\r\ncd /d "%~dp0"\r\npwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\\scripts\\launch-hero-stable-preview-v001.ps1"\r\npause\r\n')
result=dict(schema='Root-stable-preview-actual-admission-v001',actual_applied=True,approval=pin(approvalpath),native_proof=pin(proofpath),entry=pin(entry),wrapper=pin(wrapper),E_review_retention=pin(retention),manual_scope='LIMITED_WIP',full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False)
out=R/'source-assets/production/fairytale-hero-air-v001/root-stable-preview-v001/actual-stable-admission-v001.json';write(out,result);print(json.dumps(result,ensure_ascii=False))
