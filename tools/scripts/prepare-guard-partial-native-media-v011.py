"""Keep full native timing and choose only independently spatially qualified samples."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
import imageio_ffmpeg
from PIL import Image
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);a=p.parse_args()
archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';show.mkdir(exist_ok=True)
report=original/'runtime-report.json';proof=original/'independent-guard-art-partial-v010.json'
r=read(report);v=read(proof)
assert r['schema']=='guard-art-partial-native-observer-v009' and r['passed'] and v['passed']
assert r['normal_J_full_clear'] is False and r['guard_final_HP']==185 and r['spatial_approach']['route_reached']
frames=sorted(original.glob('MovieFrame*.png'));offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['duration_s']
assert len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]
concat=show/'guard-partial-native-timing-v011.ffconcat';video=show/'guard-partial-native-DIAGNOSTIC-silent-v011.mp4'
assert not concat.exists() and not video.exists()
lines=['ffconcat version 1.0']
for i,f in enumerate(frames):
 dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
 lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
ff=imageio_ffmpeg.get_ffmpeg_exe()
for name,cmd in [('encode-v011.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-v011.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
assert decoded.returncode==0,decoded.stderr
(show/'decoded-framemd5-v011.txt').write_text(decoded.stdout,encoding='utf-8')
decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
assert '#tb 0: 1/1000000' in decoded.stdout
errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
last=show/'decoded-final-frame-v011.png'
end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
assert end.returncode==0 and last.is_file(),end.stderr
with Image.open(last) as im:assert im.size==(1280,720)
timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
(show/'presentation-frame-retention-v011.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
samples=[];missing=[]
for clip,count in [('Dormant',1),('Wake',6),('Ready',4),('AxeWindup',6),('ProceduralGap',1)]:
 for frame in range(count):
  choices=[]
  for i,o in enumerate(r['observations']):
   for d in o['guard_draws']:
    if int(d['EntityId'])!=int(r['guard_entity']):continue
    if clip=='ProceduralGap':matched=d['ProceduralFallback'] and not d['Drawn']
    else:matched=d['Drawn'] and d['Selection']['Clip']==clip and d['Selection']['Frame']==frame
    if matched and clip in ['Ready','AxeWindup']:
     matched=d['SpatialCoverageEligible'] and any(w['observation']==i and w['clip']==clip and w['frame']==frame and w['DrawId']==d['DrawId'] for w in v['coverage_witnesses'])
    if matched:choices.append(i);break
  if not choices and clip=='Dormant':missing.append(dict(clip=clip,frame=frame));continue
  assert choices,(clip,frame)
  i=choices[len(choices)//2];src=frames[i];dest=show/f'{clip}-{frame:02d}-UNSCALED-native-v011.png';assert not dest.exists();shutil.copy2(src,dest)
  samples.append(dict(clip=clip,frame=frame,frame_index=i,source=pin(src),presentation=pin(dest),resized=False,spatial_rule='independent qualified observation' if clip in ['Ready','AxeWindup'] else 'native observation'))
index=dict(schema='guard-partial-native-media-v011',status='SPATIAL_PARTIAL_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),presentation_frame_retention=timing_receipt,missing_samples=missing,samples=samples,actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged=False,audio_recorded=False,visual_reviewed=False,formal_complete_units=0,render_callback_asset_pixel_attribution='Observation metadata and captured viewport; inspect visually, do not infer asset-specific pixel proof from CRC alone')
(archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(archive/'README.md').write_text('守卫三行动作空间试样：普通WASD绕行到真实侧面、位置逐帧核验；Knight/Bat公开诊断清除，守卫185HP，玩家100HP。原时序完整静音录像，样本按独立空间资格选择。只包含Wake/Ready/AxeWindup三行，其他动作仍程序占位；尚待E双SHA保全与实际审图，非完整敌人验收。CRC证明捕获像素一致，不单独证明每张PNG的特定资源相位。\n',encoding='utf-8')
print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),duration_s=duration-offsets[0],visual_reviewed=False)))
