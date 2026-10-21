"""Retained tested Death microsecond VFR code; only output filenames changed."""
from pathlib import Path
import hashlib,json,subprocess
import imageio_ffmpeg
from PIL import Image

def pin(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())

def encode_vfr(display,frames,offsets,duration):
 # MICROSECOND_VFR_BEGIN: unchanged retained Hurt pipeline except output names and directory.
 concat=display/'guard-Stomp-native-timing-v001.ffconcat';video=display/'guard-Stomp-native-DIAGNOSTIC-silent-v001.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-Stomp-v001.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-Stomp-v001.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(display/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (display/'decoded-framemd5-Stomp-v001.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=display/'decoded-final-frame-Stomp-v001.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (display/'presentation-frame-retention-Stomp-v001.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # MICROSECOND_VFR_END
 return video,last,timing_receipt,decoded_rows
