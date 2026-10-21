"""Versioned Known44 AxeCycle presentation only; original native offsets/pixels remain untouched."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
import imageio_ffmpeg
from PIL import Image
C=Path(__file__).resolve().parent.parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def qualified_choices(r,v):
 cid=str(r['cycle_attack_id']);obs=r['observations'];choices={}
 for w in v['coverage_witnesses']:
  i=w['observation'];assert type(i) is int and 0<=i<len(obs)
  o=obs[i];ds=[d for d in o['guard_draws'] if d['DrawId']==w['DrawId'] and str(d['EntityId'])==str(r['guard_entity'])];assert len(ds)==1
  d=ds[0];s=d['Selection'];clip=s['Clip'];frame=s['Frame']
  assert d['Drawn'] is True and d['SpatialCoverageEligible'] is True and d['DrawStack']==[d['TexturePath']]
  assert w['clip']==clip and w['frame']==frame and w['sample']==s['SampleTime'] and str(w['AttackId'])==str(s['AttackId']) and str(w['SourceEventId'])==str(s['SourceEventId'])
  assert w['player']==o['player_ground'] and w['guard']==o['guard_native']['ground'] and w['object']==d['TexturePath']
  if clip in ['AxeWindup','AxeActive','AxeRecovery']:assert str(s['AttackId'])==cid==str(o['guard_native']['attack_id']) and not o['guard_native']['interrupted']
  choices.setdefault((clip,frame),[]).append((i,d,w))
 for clip,count in [('Wake',6),('Ready',4),('AxeWindup',6),('AxeActive',4),('AxeRecovery',4)]:
  for frame in range(count):assert choices.get((clip,frame)),('Missing independently qualified required sample',clip,frame)
 return choices

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';contract=read(C/'media-input-contract-v002.json')
 for row in read(C/'known44-media-freeze-v002.json')['files']:assert pin(C/row['path'])['sha256']==row['sha256'] and (C/row['path']).stat().st_size==row['bytes']
 allowed=contract['allowed_independent_tooling_freezes'];assert len(allowed)==2 and len({x['sha256'] for x in allowed})==2
 for row in allowed:assert pin(Path(row['path']))==row
 session=read(archive/'index.json');matches=[x for x in allowed if x['sha256']==session['candidate_freeze_sha256']];assert len(matches)==1,'Only exact frozen tooling v002/v003 is accepted'
 dep=matches[0]
 report=original/'runtime-report.json';proof=original/contract['independent_receipt'];r=read(report);v=read(proof);session=read(archive/'index.json')
 assert session['schema']==contract['native_session_schema'] and session['candidate_freeze_sha256']==dep['sha256'] and str(session['process_id'])==r['process_id']
 assert r['schema']==contract['native_report_schema'] and r['scenario']==contract['scenario']=='AxeCycle' and r['passed'] is True and r['flow_complete'] is True and v['passed'] is True
 assert r['cycle_pinned'] is True and str(v['cycle_attack_id'])==str(r['cycle_attack_id']) and v['masks']=={'Wake':63,'Ready':15,'AxeWindup':63,'AxeActive':15,'AxeRecovery':15}
 assert r['normal_J_full_clear'] is False and r['guard_public_damage_used'] is False and r['guard_final_HP']==185 and r['spatial_approach']['route_reached'] is True
 assert v['pixel_proof']['passed'] and v['pixel_proof']['native_async_writer_verified'] and v['pixel_proof']['every_source_viewport_pixel_crc_matches']
 frames=sorted(original.glob('MovieFrame*.png'));assert len(frames)==v['native_frames']==len(r['observations']) and v['pixel_proof']['verified_original_PNG_count']==len(frames)+1
 choices=qualified_choices(r,v)
 if a.validate_only:
  print(json.dumps(dict(actual_input_contract_verified=True,qualified_sample_keys=len(choices),required_samples=24,media_written=False,UE_started=False,visual_reviewed=False)));return
 show.mkdir(exist_ok=True)
 assert not (archive/'source-version-status-index.json').exists() and not (archive/'README.md').exists(),'Never overwrite prior presentation index'
 assert not any(show.glob('*known44*v002*')),'Never overwrite earlier media; use a fresh capture/version'

 frames=sorted(original.glob('MovieFrame*.png'));offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['duration_s']
 assert len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]
 concat=show/'guard-known44-AxeCycle-native-timing-v002.ffconcat';video=show/'guard-known44-AxeCycle-native-DIAGNOSTIC-silent-v002.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-known44-v002.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-known44-v002.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (show/'decoded-framemd5-known44-v002.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=show/'decoded-final-frame-known44-v002.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (show/'presentation-frame-retention-known44-v002.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 
 samples=[]
 def copy_native(i,dest):
  src=frames[i];assert not dest.exists();shutil.copy2(src,dest);assert pin(src)['sha256']==pin(dest)['sha256']
  with Image.open(dest) as im:assert im.format=='PNG' and im.size==(1280,720)
  return dict(frame_index=i,source=pin(src),presentation=pin(dest),wall_offset_s=offsets[i],resized=False)
 for clip,count in contract['required_samples'].items():
  for frame in range(count):
   pool=choices[(clip,frame)];i,d,w=pool[len(pool)//2];item=copy_native(i,show/f'{clip}-{frame:02d}-UNSCALED-known44-v002.png')
   item.update(clip=clip,frame=frame,AttackId=d['Selection']['AttackId'],SourceEventId=d['Selection']['SourceEventId'],sample_time=d['Selection']['SampleTime'],coverage_witness=w,source_object=d['TexturePath']);samples.append(item)
 assert len(samples)==24
 joins=[];missing_joins=[];cid=str(r['cycle_attack_id'])
 for name,before,after in [('AxeWindup5-to-Active0',('AxeWindup',5),('AxeActive',0)),('AxeActive3-to-Recovery0',('AxeActive',3),('AxeRecovery',0)),('AxeRecovery3-to-native-Ready',('AxeRecovery',3),None)]:
  left=max(choices[before],key=lambda x:x[0]);li=left[0]
  rightpool=choices[after] if after else [x for (clip,f),pool in choices.items() if clip=='Ready' for x in pool if str(x[1]['Selection']['AttackId'])==cid]
  rightpool=[x for x in rightpool if x[0]>li]
  if not rightpool:missing_joins.append(dict(join=name,reason='No later independently qualified Ready of the same original retained AttackId; never substitute a later cycle'));continue
  right=min(rightpool,key=lambda x:x[0]);ri=right[0]
  items=[]
  for label,x in [('before',left),('after',right)]:
   i,d,w=x;item=copy_native(i,show/f'JOIN-{name}-{label}-UNSCALED-known44-v002.png');item.update(clip=d['Selection']['Clip'],frame=d['Selection']['Frame'],AttackId=d['Selection']['AttackId'],SourceEventId=d['Selection']['SourceEventId'],sample_time=d['Selection']['SampleTime'],coverage_witness=w);items.append(item)
  joins.append(dict(join=name,pair=items,original_adjacent_callbacks=ri==li+1,intervening_native_frames=ri-li-1,original_wall_delta_s=offsets[ri]-offsets[li],interpolation=False,join_visual_accepted=False))
 (show/'join-candidates-known44-v002.json').write_text(json.dumps(dict(schema='known44-AxeCycle-native-join-candidates-v002',pairs=joins,missing=missing_joins,visual_reviewed=False,scope='Exact original full-viewport before/after copies; any nonadjacent gap is explicit, no montage/retime/interpolation.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 index=dict(schema='guard-known44-AxeCycle-native-media-v002',status='NATIVE_AXECYCLE_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),session=pin(archive/'index.json'),media_candidate=pin(C/'known44-media-freeze-v002.json'),presentation_frame_retention=timing_receipt,samples=samples,required_sample_count=24,joins=joins,missing_joins=missing_joins,DormantSeen=r['DormantSeen'],DormantUnobserved=r['DormantUnobserved'],procedural_gap_seen=r['procedural_gap_seen'],optional_Dormant_or_gap_samples_required=False,cycle_attack_id=cid,actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged=False,audio_recorded=False,visual_reviewed=False,E_before_view_required=True,formal_complete_units=0,render_callback_asset_pixel_attribution='Qualified actual observation plus native viewport CRC. Asset-specific pixels and join quality still require E preservation and actual View; no44-rendered/all57/final-art claim.')
 (archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (archive/'README.md').write_text('完整分期单斧周期试样：正常WASD真实侧面；Knight/Bat公开诊断清除，Guard185/Player100。首个原AttackId的WU6/Active4/Recovery4，加真实Wake6/Ready4共24原比例整幅PNG；44 resident不等于44渲染。原时序完整静音录像与明确相邻/非相邻join候选，尚待E保全与实际View，不是完整57/敌人/足锁/音效/最终美术验收。\n',encoding='utf-8')
 print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),join_pairs=len(joins),duration_s=duration-offsets[0],visual_reviewed=False)))

if __name__=='__main__':main()
