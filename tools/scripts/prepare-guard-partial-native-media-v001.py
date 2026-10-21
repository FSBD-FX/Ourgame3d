"""Encode unchanged native observations and select unscaled source witnesses; no viewing."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
import imageio_ffmpeg
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--failed-diagnostic',action='store_true');a=p.parse_args()
archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';show.mkdir(exist_ok=True)
r=read(original/'runtime-report.json');proof_path=original/'independent-guard-art-partial-v002.json'
if a.failed_diagnostic:assert r['passed'] is False and r['failure']
else:assert r['passed'] and read(proof_path)['passed']
assert r['normal_J_full_clear'] is False and r['guard_final_HP']==185
frames=sorted(original.glob('MovieFrame*.png'));offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['duration_s']
assert len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]
concat=show/'guard-partial-native-timing-v001.ffconcat';video=show/'guard-partial-native-DIAGNOSTIC-silent-v001.mp4'
assert not concat.exists() and not video.exists()
lines=['ffconcat version 1.0']
for i,f in enumerate(frames):
 dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
 lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",f'duration {dt:.12f}']
lines.append("file '"+frames[-1].as_posix().replace("'","'\\''")+"'");concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
for name,cmd in [('encode-v001.log',[ffmpeg,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-t',f'{duration-offsets[0]:.9f}','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-v001.log',[ffmpeg,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
samples=[];missing=[]
for clip,count in [('Dormant',1),('Wake',6),('Ready',4),('AxeWindup',6),('ProceduralGap',1)]:
 for frame in range(count):
  choices=[]
  for i,o in enumerate(r['observations']):
   for d in o['guard_draws']:
    if int(d['EntityId'])!=int(r['guard_entity']):continue
    if clip=='ProceduralGap':matched=d['ProceduralFallback'] and not d['Drawn']
    else:matched=d['Drawn'] and d['Selection']['Clip']==clip and d['Selection']['Frame']==frame
    if matched:choices.append(i);break
  if not choices and (clip=='Dormant' or a.failed_diagnostic):missing.append(dict(clip=clip,frame=frame));continue
  assert choices,(clip,frame);i=choices[len(choices)//2];src=frames[i];dest=show/f'{clip}-{frame:02d}-UNSCALED-native.png';assert not dest.exists();shutil.copy2(src,dest)
  samples.append(dict(clip=clip,frame=frame,frame_index=i,source=pin(src),presentation=pin(dest),resized=False))
index=dict(schema='guard-partial-native-media-v001',status='ACTUAL_NATIVE_RED_PRESERVED_VISUAL_DIAGNOSTIC_ONLY' if a.failed_diagnostic else 'TECHNICAL_PARTIAL_TRIAL_PASSED_VISUAL_REVIEW_PENDING',failure=r.get('failure'),missing_samples=missing,video=pin(video),report=pin(original/'runtime-report.json'),independent=pin(proof_path) if proof_path.exists() else None,samples=samples,actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged=False,audio_recorded=False,visual_reviewed=False,formal_complete_units=0)
(archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(archive/'README.md').write_text('守卫三行整身原生试样：真实房间出生与战斗时钟、主角正常方向输入，Knight/Bat公开诊断清除，守卫保持185HP。仅Dormant别名/Wake/Ready/AxeWindup16纹理；其他动作明确程序占位。原件、原时间戳静音录像与未缩放实景副本已保留；尚待E双SHA保全与Root审图，不是完整敌人或正常J全通关验收。\n',encoding='utf-8')
print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),duration_s=duration-offsets[0],visual_reviewed=False)))
