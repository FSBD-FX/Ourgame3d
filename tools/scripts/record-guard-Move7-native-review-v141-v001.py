"""Bind Root's bounded visual judgement to two actual native and retained recordings."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path('F:/Ourgame');E=Path('E:/OurGame/Knight/过程图稿与视频')
O=R/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-checkpoint-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
cm=R/'source-assets/production/backups/v141-GuardMove7-Observer200G-v003/compiled-source-manifest.json';m=read(cm)
assert (m['source_files'],m['production_files'],m['passed'],m['failed'])==(283,1371,200,0)
assert pin(cm)['sha256']=='71efa450e6aea3d5107554ac524166c824ee253211452001662dad3facb62553'
native=[];media=[];retentions=[]
for side,sign,batch in [('left',-1,575),('right',1,576)]:
 a=R/f'过程图稿与视频/2026-10-18_裂岩守卫Move7真实追随128与自然入战试样_{side}_v002'
 rp=a/'原件/runtime-report.json';ip=a/'原件/Move7-independent-native-verification-v001.json';sp=a/'index.json'
 p=R/f'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-native-prereg-geometry-v003/Root-Move7-{side}-prereg-v001.json'
 r,v,s=read(rp),read(ip),read(sp)
 assert r['passed'] and v['passed'] and s['independent_passed'] and s['exit_code']==0
 assert v['actual_facing']==sign and v['six_distance_window_mask']==63 and v['accepted_cycle_distance']>=128 and v['unique_Move_draws']==25
 assert v['complete7GPU_and_submitted_floatquads'] and v['native_PNG_CRC_FIFO_verified'] and v['optical_source_projection']['passed'] and len(v['actual_adjacent_joins'])==2
 assert r['ready_seen']==3 and r['guard_final_HP']==185 and r['guard_incoming_count']==0
 native.append(dict(side=sign,archive=a.as_posix(),report_pin=pin(rp),independent_pin=pin(ip),prereg_pin=pin(p),session_pin=pin(sp),process_id=int(r['process_id'])))
 f=R/f'过程图稿与视频/2026-10-18_裂岩守卫七件步态与入战实录审阅_{side}_v001/source-version-status-index.json';d=read(f)
 assert d['native_frame_count']==d['presentation_frame_retention']['decoded_frames']==len(r['observations'])
 played=R/f'过程图稿与视频/2026-10-18_裂岩守卫七件步态完整播放证明_v001/原件/{side}-ended-browser-v001.json';b=read(played)
 assert b['ended'] and b['paused'] and not b['loop'] and b['error'] is None and b['playbackRate']==1 and b['currentTime']==b['duration']
 media.append(dict(side=sign,index=pin(f),video=d['video'],native_and_decoded_frames=len(r['observations']),playback=pin(played),complete_playback_duration=b['duration'],review_scope='Full silent 1x playback confirmed plus original-scale source windows and adjacent-frame visual review; not every-frame visual/audio acceptance'))
 for leaf in [f'2026-10-18-本项目E{batch}-裂岩守卫Move7{side}向实录原件-v002',f'2026-10-18-本项目E{batch+2}-裂岩守卫Move7{side}侧完整实录与接续审阅-v001']:
  q=E/leaf/'E-retention-index-v001.json';x=read(q);assert x['verification_passes']==2 and x['source_and_member_hash_mismatches']==0;retentions.append(pin(q))
for leaf in ['2026-10-18-本项目E579-裂岩守卫七件步态双侧播放器-v001','2026-10-18-本项目E580-裂岩守卫七件步态完整播放证明-v001']:
 q=E/leaf/'E-retention-index-v001.json';x=read(q);assert x['verification_passes']==2 and x['source_and_member_hash_mismatches']==0;retentions.append(pin(q))
assert not O.exists();O.mkdir(parents=True)
d=dict(schema='Root-GuardMove7-native-and-visible-review-v141-v001',utc=datetime.now(timezone.utc).isoformat(),is_template=False,RootApproved=True,FinalAccepted=False,limited_manual_trial_allowed=True,
 compiled_manifest_pin=pin(cm),native=native,media=media,E_before_view_retention=retentions,
 actual_both_facings_viewed=True,actual_six_distance_windows_viewed=True,actual_adjacent_joins_viewed=True,both_complete_silent_videos_viewed=True,
 actual_browser_end_screens_viewed=True,complete_playback_confirmed=True,
 visual_decision='Keep bounded manual trial: small armored silhouette, fixed single axe and alternating legs visible both ways; real Move no longer renders grey fallback. Actual natural attack/Ready transitions remain readable.',
 visible_polish_needed=['Passing knees and boots overlap heavily in some phases; gait needs polish.', 'Rest walking body and old whole-body attack/Ready change torso/hip/foot shape abruptly.'],
 remaining_scope=['Canonical straight-X approach only; diagonal/reversal/contact resets and footlock not certified.', 'Only unrotated BodyRest contributes legacy occlusion outline; rotated leg outlines remain open.', 'Ordinary Hurt/Stun transitions were not captured in this trial.', 'Recordings are silent; no complete SFX or listening acceptance.', 'Knight/Bat predecessors use explicit public diagnostic clearance; this is not a full-room manual completion proof.', 'Other equipment, enemies, combos and required acquire/drop/save coverage remain in the active full goal.'],
 first_failed_native_archive_preserved='过程图稿与视频/2026-10-18_裂岩守卫Move7真实追随128与自然入战试样_left_v001',
 proof_repairs='Typed fourth-test closure compatibility plus numpy real-scalar recognition; all original geometry/pixel/timing thresholds retained. Fresh left_v002/right_v002 required and used.',
 Source=283,Production=1371,strict_registered_tests=200,formal_complete_units=0,complete_combinations=0,generation_calls_this_turn=0,external_API_calls=0,goal_status='active')
q=O/'Root-GuardMove7-native-and-visible-review-v141-v001.json'
with q.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(review=pin(q),native_sides=2,formal_complete_units=0,limited_manual_trial_allowed=True),ensure_ascii=False))
