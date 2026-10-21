from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
R=Path('F:/Ourgame');M=R/'过程图稿与视频/2026-10-19_钟盔稳定副本完整视听与对照_right_v004';N=R/'过程图稿与视频/2026-10-19_钟盔装备跳跃三连实录_right_v004'
E=Path('E:/OurGame/Knight/过程图稿与视频')
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
ep=[E/'2026-10-19-本项目E613-钟盔稳定副本原生三跳-v004/E-retention-index-v001.json',E/'2026-10-19-本项目E614-钟盔稳定副本完整视听对照-v004/E-retention-index-v001.json']
for p in ep:
 d=read(p);assert d['verification_passes']==2 and d['source_and_member_hash_mismatches']==0 and d['full_source_member_retention'] is True and d['E_root_README_unchanged'] is True
names=['None-LGT-Rejump-eighteen-source-crops-v001.png','JOIN-Jump1_Land5_to_Ready-FULL-native-pair-v001.png','JOIN-Land5_to_Air0_rejump-FULL-native-pair-v001.png','JOIN-Jump3_Land5_to_Ready-FULL-native-pair-v001.png']
report=dict(schema='Root-staged-Air6-limited-visible-review-v001',utc=datetime.now(timezone.utc).isoformat(),RootApproved=True,is_template=False,approval_scope='LIMITED_WIP',manual_trial_allowed=True,actual_staged_process_id=51516,actual_native_callbacks=174,actual_native_verified=pin(N/'native-independent-verification-v004.json'),actual_staged_runtime_verified=pin(N/'staged-native-supplement-v001.json'),E_before_View=[pin(p) for p in ep],Root_visible_keyframes_reviewed=True,Root_reviewed_images=[pin(M/'展示副本'/n) for n in names],scope='Actual 18 unscaled pose crops and three adjacent native joins reviewed after exact full E613/E614 retention. Small72px helmet, blade and brown armor remain readable; actual final brown Ready identity preserved. This review is limited to visible keyframes.',known_issues=['First Rise/Ready silhouette change remains abrupt','Apex knee/hem tuck volume needs polish','Land4/Land5 body pose step needs polish'],known_pose_join_refinement_open=True,full_realtime_playback_reviewed=False,audio_listened=False,human_playtest=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
O=R/'过程图稿与视频/2026-10-19_钟盔稳定副本有限审阅记录_v001';O.mkdir(exist_ok=False);(O/'原件').mkdir();(O/'展示副本').mkdir()
write(O/'原件/Root-staged-limited-review-v001.json',report);shutil.copy2(O/'原件/Root-staged-limited-review-v001.json',O/'展示副本/Root-staged-limited-review-v001.json')
with (O/'README.md').open('x',encoding='utf-8') as f:f.write('固定试玩副本实际174帧原生三跳通过并有进程加载副本DLL记录；Root看18姿态及3相邻接缝，仅LIMITED_WIP。完整原速观看与试听未完成，关节/衣摆/落地接缝精修未完成，正式0/15与搭配0/20。原片已先E613/E614逐原字节保全；本批为之后形成的独立审阅记录。\n')
write(O/'来源-版本-状态索引.json',dict(status='LIMITED_WIP',source_archive=N.as_posix(),presentation_archive=M.as_posix(),files=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()],FinalAccepted=False))
print(json.dumps(pin(O/'原件/Root-staged-limited-review-v001.json'),ensure_ascii=False))
