"""Versioned Known44 normal-J StunIR presentation only; original native offsets/pixels remain untouched."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess
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
 aid=str(r['interrupted_attack_id']);bid=str(r['break_event_id']);obs=r['observations'];choices={};seen=set()
 for w in v['coverage_witnesses']:
  i=w['observation'];assert type(i) is int and 0<=i<len(obs)
  o=obs[i];ds=[d for d in o['guard_draws'] if d['DrawId']==w['DrawId'] and str(d['EntityId'])==str(r['guard_entity'])];assert len(ds)==1
  d=ds[0];s=d['Selection'];clip=s['Clip'];frame=s['Frame'];n=o['guard_native'];stamp=s['SampleTime']
  assert clip in ['Stunned','InterruptedRecovery'] and type(frame) is int and 0<=frame<4
  assert str(d['DrawId']) not in seen,'Repeated independent coverage DrawId';seen.add(str(d['DrawId']))
  assert d['Drawn'] is True and d['SpatialCoverageEligible'] is True and d['DrawStack']==[d['TexturePath']]
  assert w['clip']==clip and w['frame']==frame and w['sample']==stamp and str(w['AttackId'])==str(s['AttackId'])==aid==str(n['attack_id']) and str(w['SourceEventId'])==str(s['SourceEventId'])
  assert w['player']==o['player_ground'] and w['guard']==n['ground'] and w['object']==d['TexturePath']
  assert n['interrupted'] is True and n['HP']>0 and o['player_HP']>0 and o['phase']=='normal_guard_J_and_StunIR' and o['approach_spatial']['route_reached'] is True
  side=r['actual_approach_side'];assert side in [-1,1]
  assert 110<=side*(o['player_ground'][0]-n['ground'][0])<=155 and abs(o['player_ground'][1]-n['ground'][1])<=20
  if clip=='Stunned':
   assert str(s['SourceEventId'])==bid and s['Phase']==n['phase']==6 and s['IntervalStart']==r['break_at'] and s['IntervalEnd']==r['stun_end'] and r['break_at']<=stamp<r['stun_end']
   assert frame==sum(stamp>=r['break_at']+x for x in [.1,.2,.3])
  else:
   assert str(s['SourceEventId'])=='0' and s['Phase']==n['phase']==5 and s['IntervalStart']==r['stun_end'] and s['IntervalEnd']==r['original_occupied_until'] and r['stun_end']<=stamp<r['original_occupied_until']
   assert frame==min(3,math.floor((stamp-r['stun_end'])/(r['original_occupied_until']-r['stun_end'])*4))
  choices.setdefault((clip,frame),[]).append((i,d,w))
 for clip in ['Stunned','InterruptedRecovery']:
  for frame in range(4):assert choices.get((clip,frame)),('Missing independently qualified required sample',clip,frame)
 return choices

def adjacent_join(choices):
 left=choices[('Stunned',3)];right=choices[('InterruptedRecovery',0)]
 pairs=[(l,r) for l in left for r in right if r[0]==l[0]+1]
 if not pairs:return None
 assert len(pairs)==1,'One original break can have only one adjacent Stun-to-IR boundary'
 return pairs[0]

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';contract=read(C/'media-input-contract-v001.json')
 for row in read(C/'StunIR-media-freeze-v001.json')['files']:assert pin(C/row['path'])['sha256']==row['sha256'] and (C/row['path']).stat().st_size==row['bytes']
 dep=contract['exact_independent_source_tooling_freeze'];assert pin(Path(dep['path']))==dep
 report=original/'runtime-report.json';proof=original/contract['independent_receipt'];r=read(report);v=read(proof);session=read(archive/'index.json')
 assert session['schema']==contract['native_session_schema'] and session['candidate_freeze_sha256']==dep['sha256'] and str(session['process_id'])==r['process_id'] and session['exit_code']==0 and session['native_reported_passed'] is True and session['independent_passed'] is True
 assert r['schema']==contract['native_report_schema'] and r['scenario']==contract['scenario']=='StunIR' and r['passed'] is True and r['flow_complete'] is True and v['passed'] is True
 assert v['native_report_sha256']==pin(report)['sha256'] and str(v['process_id'])==r['process_id'] and v['run']==r['run']
 assert r['break_pinned'] is True and str(v['break_event_id'])==str(r['break_event_id']) and str(v['interrupted_attack_id'])==str(r['interrupted_attack_id']) and v['masks']=={'Stunned':15,'InterruptedRecovery':15} and r['StunMask']==r['InterruptedRecoveryMask']==15
 assert abs(r['stun_end']-(r['break_at']+.4))<=1.e-8 and r['original_occupied_until']-r['stun_end']>=.4
 assert r['normal_J_full_clear'] is False and r['guard_public_damage_used'] is False and r['guard_normal_J_only'] is True and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False and r['player_damage_preserved'] is True and r['guard_final_HP']>0 and r['player_final_HP']>0 and r['spatial_approach']['route_reached'] is True
 assert r['silent_video'] is True and r['audio_recorded'] is False and r['visual_reviewed'] is False and v['visual_reviewed'] is False and r['formal_complete_units']==v['formal_complete_units']==0
 assert v['pixel_proof']['passed'] and v['pixel_proof']['native_async_writer_verified'] and v['pixel_proof']['every_source_viewport_pixel_crc_matches']
 frames=sorted(original.glob('MovieFrame*.png'));assert len(frames)==v['native_frames']==len(r['observations']) and v['pixel_proof']['verified_original_PNG_count']==len(frames)+1
 choices=qualified_choices(r,v);boundary=adjacent_join(choices)
 if a.validate_only:
  print(json.dumps(dict(actual_input_contract_verified=True,qualified_sample_keys=len(choices),required_samples=8,adjacent_Stun3_IR0_available=boundary is not None,media_written=False,UE_started=False,visual_reviewed=False)));return
 show.mkdir(exist_ok=True)
 assert not (archive/'source-version-status-index.json').exists() and not (archive/'README.md').exists(),'Never overwrite prior presentation index'
 assert not any(show.glob('*StunIR*v001*')),'Never overwrite earlier media; use a fresh capture/version'

 frames=sorted(original.glob('MovieFrame*.png'));offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['duration_s']
 assert len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]
 concat=show/'guard-known44-StunIR-native-timing-v001.ffconcat';video=show/'guard-known44-StunIR-native-DIAGNOSTIC-silent-v001.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-StunIR-v001.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-StunIR-v001.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (show/'decoded-framemd5-StunIR-v001.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=show/'decoded-final-frame-StunIR-v001.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (show/'presentation-frame-retention-StunIR-v001.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 
 samples=[]
 def copy_native(i,dest):
  src=frames[i];assert not dest.exists();shutil.copy2(src,dest);assert pin(src)['sha256']==pin(dest)['sha256']
  with Image.open(dest) as im:assert im.format=='PNG' and im.size==(1280,720)
  return dict(frame_index=i,source=pin(src),presentation=pin(dest),wall_offset_s=offsets[i],resized=False)
 def selected_item(x,dest):
  i,d,w=x;item=copy_native(i,dest);s=d['Selection']
  item.update(clip=s['Clip'],frame=s['Frame'],AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],sample_time=s['SampleTime'],interval_start=s['IntervalStart'],interval_end=s['IntervalEnd'],break_event_id=r['break_event_id'],coverage_witness=w,source_object=d['TexturePath']);return item
 for clip,count in contract['required_samples'].items():
  for frame in range(count):
   pool=choices[(clip,frame)];samples.append(selected_item(pool[len(pool)//2],show/f'{clip}-{frame:02d}-UNSCALED-StunIR-v001.png'))
 assert len(samples)==8
 joins=[];missing_joins=[]
 if boundary:
  left,right=boundary;li,ri=left[0],right[0]
  items=[selected_item(x,show/f'JOIN-Stunned3-to-InterruptedRecovery0-{label}-UNSCALED-StunIR-v001.png') for label,x in [('before',left),('after',right)]]
  joins.append(dict(join='Stunned3-to-InterruptedRecovery0',pair=items,original_adjacent_callbacks=True,intervening_native_frames=0,original_wall_delta_s=offsets[ri]-offsets[li],break_event_id=r['break_event_id'],interrupted_attack_id=r['interrupted_attack_id'],interpolation=False,join_visual_accepted=False))
 else:missing_joins.append(dict(join='Stunned3-to-InterruptedRecovery0',reason='No pair of independently qualified original adjacent callbacks; no later callback substitutes for adjacency',join_visual_accepted=False))
 (show/'join-candidates-StunIR-v001.json').write_text(json.dumps(dict(schema='known44-StunIR-native-join-candidates-v001',pairs=joins,missing=missing_joins,visual_reviewed=False,scope='Original consecutive full-viewport Stun3/IR0 only, same real85 break and original interrupted AttackId. No montage/retime/interpolation; missing adjacency remains explicit.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 index=dict(schema='guard-known44-StunIR-native-media-v001',status='NATIVE_NORMAL_J_STUNIR_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),session=pin(archive/'index.json'),media_candidate=pin(C/'StunIR-media-freeze-v001.json'),presentation_frame_retention=timing_receipt,samples=samples,required_sample_count=8,joins=joins,missing_joins=missing_joins,procedural_gap_seen=r['procedural_gap_seen'],break_event_id=r['break_event_id'],interrupted_attack_id=r['interrupted_attack_id'],break_at=r['break_at'],stun_end=r['stun_end'],original_occupied_until=r['original_occupied_until'],IR_actual_duration_s=r['original_occupied_until']-r['stun_end'],actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged_by_normal_J=True,guard_final_HP=r['guard_final_HP'],player_final_HP=r['player_final_HP'],player_damage_preserved=True,audio_recorded=False,visual_reviewed=False,E_before_view_required=True,formal_complete_units=0,render_callback_asset_pixel_attribution='Qualified actual observation plus native viewport CRC. Asset-specific pixels and join quality still require E preservation and actual View; no all44-rendered/all57/Death/final-art claim.')
 (archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (archive/'README.md').write_text('正常J破韧与原窗恢复试样：Knight/Bat公开诊断清除；Guard仅正常军剑J真实受击，保留玩家实际损伤。同一次85破韧和原AttackId的Stun4/InterruptedRecovery4共8张原比例整幅PNG，IR使用实际剩余原占用窗而非固定400ms。原时序完整静音录像、只接受原连续回调的Stun3→IR0转场候选。缺相邻转场明确记录；尚待E保全与实际View，不是全44/57、Death、足锁、音效或最终美术验收。\n',encoding='utf-8')
 print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),join_pairs=len(joins),missing_join_pairs=len(missing_joins),duration_s=duration-offsets[0],visual_reviewed=False)))

if __name__=='__main__':main()
