"""Record actual v144 pair and bounded Root image review; full art/audio remain open."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
R=Path('F:/Ourgame');M=R/'过程图稿与视频';E=Path('E:/OurGame/Knight/过程图稿与视频')
EV=R/'docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
P=M/'2026-10-19_钟盔空中存档两进程_v001/independent-two-process-verification-v001.json';proof=read(P)
assert proof['passed'] and proof['process_order']['nonoverlapping_native_processes'] and proof['disk']['published_originals_unchanged']
retentions=[]
for n in range(629,635):
 paths=list(E.glob(f'2026-10-19-本项目E{n}-*/E-retention-index-v001.json'));assert len(paths)==1
 d=read(paths[0]);assert d['verification_passes']==2 and d['kind']=='full' and d['full_source_member_retention']
 retentions.append(dict(batch=n,index=pin(paths[0]),file_count=d['file_count'],source_bytes=d['source_bytes']))
images=[M/'2026-10-19_钟盔空中存档实录_source_right_v001/展示副本/air-disk-source-UNSCALED-witnesses-v001.png',M/'2026-10-19_钟盔空中存档实录_target_right_v001/展示副本/air-disk-target-UNSCALED-witnesses-v001.png',M/'2026-10-19_钟盔空中存档_source_right_v001/原件/MovieFrame00110.png',M/'2026-10-19_钟盔空中存档_target_right_v001/原件/MovieFrame00001.png']
media=[]
for role in ('source','target'):
 p=M/f'2026-10-19_钟盔空中存档实录_{role}_right_v001/来源-版本-状态索引.json';d=read(p);assert d['presentation_encoding']['full_AV_decoded'] and d['presentation_encoding']['frames_dropped_or_added'] is False
 media.append(dict(role=role,index=pin(p),video=d['playable_video'],callbacks=len(d['all_native_frames'])))
assert sum(v['callbacks'] for v in media)==175
O=M/'2026-10-19_钟盔空中存档有限审阅_v001';O.mkdir();(O/'原件').mkdir();(O/'展示副本').mkdir()
review=dict(schema='Root-air-disk-native-limited-review-v001',utc=datetime.now(timezone.utc).isoformat(),actual_independent_pair=pin(P),actual_source_files=300,actual_production_files=1419,actual_full203=True,actual_source_and_target_callbacks=175,actual_source_PID=41424,actual_target_PID=23216,native_disk_restore_passed=True,restore_scope='BoundRunOnly-v2; not full Account/Profile/Settings/talents',actual_complete_codec_bytes=proof['source_flow']['whole_codec']['complete_codec_bytes'],source_one_Space=True,target_no_Space=True,diagnostic_knight_clearance=False,actual_await_completed_callbacks=proof['target_flow']['paused_callback_count'],actual_await_wall_s=proof['target_flow']['pause_wall_s'],original_saved_trajectory_continued=True,whole_published_disk_bytes_unchanged=True,media=media,Root_viewed_images=[pin(p) for p in images],retention_before_Root_View=retentions,performed_scope='Viewed two unscaled witness boards (4source+8target samples) and two full native viewports. Independently checked all175 native PNG/resources/pixels/FIFO/audio; full AV decoded for both processes.',visible_facts=['Source Apex and target installed/paused Apex retain the same helmet/light armor/independent sword silhouette in reviewed witnesses.', 'Target falls and lands then returns equipped Ready; no missing armor layer seen in reviewed samples.', 'Full viewport retains small72px standing-equivalent hero, hiddenHUD/range and exploration dimming.'],visual_refinement_open=['AirRise/Ready, Apex hem/knee and Land4/Land5 body shape continuity remains for refinement.', 'J0/J1/Dodge0/Dodge3 armor/helmet silhouettes still require art polish; newrequest257 body is wider and not imported.'],target_actual_native_recording_silent=True,source_native_mix_nonzero_not_each_cue_attributed=True,full_realtime_playback_reviewed=False,audio_listened=False,final_art_accepted=False,formal_complete_units=0,completed_combinations=0,FinalAccepted=False)
rp=O/'原件/Root-limited-review-v001.json';new(rp,review);shutil.copy2(rp,O/'展示副本'/rp.name);shutil.copy2(P,O/'原件'/P.name)
(O/'README.md').write_text('两真实进程磁盘保存／恢复已独立通过。Root有限查看两张12样本原尺寸动作板及2张全景；全175帧/原混音/AV解码保留。目标录音实际静音；原速连续观看与听感、美术精修尚未完成，非完整账号存档或正式内容单元完成。\n',encoding='utf-8')
new(O/'来源-版本-状态索引.json',dict(schema='Root-air-disk-review-source-version-status-v001',review=pin(rp),files=[pin(p) for p in sorted(O.rglob('*')) if p.is_file()],FinalAccepted=False))
retainer=R/'source-assets/production/fairytale-hero-air-v001/native-retention-solid-candidate-v001/retain-native-media-lossless-solid-tar-xz-v001.py'
batch='2026-10-19-本项目E635-钟盔空中存档有限审阅-v001'
subprocess.run([str(R/'tools/runtime/asset-gen/Scripts/python.exe'),'-B','-X','utf8',str(retainer),'--source',str(O),'--batch',batch,'--preset','3'],check=True)
review_E=E/batch/'E-retention-index-v001.json'
prior=EV/'current300-GREEN-art257-native-pending-status-v002/current-status.json';s=read(prior)
s.update(schema='Root-current-air-disk-native-bounded-review-v144-status-v003',utc=review['utc'],prior_status_pin=pin(prior),actual_v144_native_verified=True,v144_native='PASS_actual_sequential_PID41424_23216_wholeCodec_disk_pause_original_trajectory; limitedvisualreview_only',v144_independent_pair=pin(P),v144_limited_Root_review=pin(rp),v144_limited_review_E=pin(review_E),v144_native_media_E=retentions,last_E_batch=635,next_E_batch=636,next_task='Six local locomotion SFX binding candidate; narrow J0/J1 body correction and armor silhouette polish; all final art/audio/other units open',FinalAccepted=False)
status_dir=EV/'current300-GREEN-native-reviewed-art257-status-v003';status_dir.mkdir();(status_dir/'before').mkdir();new(status_dir/'current-status.json',s)
files=[R/'README.md',R/'docs/production/first-batch-v2/progress.json',R/'项目需求台账.md',R/'source-assets/production/first-unit-animation-v003/generation-ledger.json']
for p in files:
 dst=status_dir/'before'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
old=files[0].read_text(encoding='utf-8-sig');_,rest=old.split('\n\n',1)
head='2026-10-19 当前进行中（EV048，v144）：空中顶点磁盘保存→源进程完全退出→新pristine进程恢复已实际通过；两进程175原生回调，同装备／整Codec／暂停保持／新Enter继续原下落落地轨迹，published磁盘字节不变。Source300／Production1419编译及原有D3D11完整203严格通过；E629–635完整保全。Root有限审12姿态样本与2全景，原速完整观看／试听尚未完成。新攻击起手修片257仍偏宽，未导入；六条本地动作音效接入候选制作中。[快捷试玩](钟盔轻甲快捷试玩.cmd)保持独立v142；[当前状态](docs/production/first-batch-v2/evidence/HeroAirDiskRestore-v144-v001/current300-GREEN-native-reviewed-art257-status-v003/current-status.json)。这里只验证Bound Run，非完整账号存档；美术／SFX／正式0/15与搭配0/20继续，目标active。内置请求257，窗口11用17余7，生命周期281另初始3；外部API0，内置费用未知。'
files[0].write_text(head+'\n\n'+rest,encoding='utf-8')
q=read(files[1]);q.update(current_status_authority=pin(status_dir/'current-status.json'),current_task=s['next_task'],current_v144_native_pair=pin(P),current_v144_limited_visual_review=pin(rp),current_turn_progress_classification='Actual Source300/1419/full203 and sequential native disk restore175frames passed; limitedvisualreview; art257wider/unimported, locomotionSFXcandidateonly, formal0');files[1].write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with files[2].open('a',encoding='utf-8') as f:f.write('\n2026-10-19 EV048：v144真实PID41424保存／退出后PID23216pristine恢复通过，175原生回调／整Codec32026B／暂停12回调0.216s／新Enter继续原轨迹／磁盘不变，E629–635。有限看12样本与2全景，原速观看和听感未验收。Bound Run非完整账号存档；动作／音效和其余首批内容继续，正式0/15与搭配0/20不变。\n')
g=read(files[3]);g.setdefault('derived_deliveries',[]).append(dict(id='EV048-v144-two-native-disk175-limited-review-v001',utc=s['utc'],status=pin(status_dir/'current-status.json'),native_pair=pin(P),image_generation_calls=0,external_API_calls=0,formal_complete_units=0,FinalAccepted=False));files[3].write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new(status_dir/'status-sync-receipt.json',dict(status=pin(status_dir/'current-status.json'),after=[pin(p) for p in files],backups_preserved=True,Source_Content_unchanged=True,FinalAccepted=False))
with (R/'.superpowers/sdd/2026-10-19-hero-air-disk-restore-v144/progress.md').open('a',encoding='utf-8') as f:f.write('\nTask1/2/3 bounded v144 complete: fresh source Approved + tooling scoped fix Approved; actualSource300/CMfb225/full203; true sequential diskpair Source41424/131callbacks +Target23216/44callbacks, fullCodec/disk/pristine/pause/neutralEnter/originaltrajectory/resources/typedpixels/PNG/audio PASS, fullAVdecode, E629–635, Root4images boundedreview. No sourceKnightdiagnostic. Fullgoal/formalart/audio/fullrealtime remainOPEN; new257bodywider/unimported and sixaudio bindingcandidate underway.\n')
print(json.dumps(dict(status=pin(status_dir/'current-status.json'),limited_review=pin(rp),last_E=635,next_E=636),ensure_ascii=False))
