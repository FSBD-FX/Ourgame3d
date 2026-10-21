from pathlib import Path
import hashlib,json,shutil,subprocess
import imageio_ffmpeg
R=Path('F:/Ourgame');S=R/'UnrealGame/Saved/GuardRunPristineProofs/20261018-091328-guard-native-two-process-v001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fact(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha(p))
session=read(S/'two-process-session.json');assert 'passed' in session['status'] and session['sources_unchanged']
assert len(session['processes'])==2 and session['processes'][0]['pid']!=session['processes'][1]['pid']
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();outputs=[]
for role,label in [('source','保存'),('restore','复开恢复')]:
 O=R/f'过程图稿与视频/2026-10-18_裂岩守卫V2双进程{label}实证_v001';assert not O.exists()
 original=O/'原件';show=O/'展示副本';original.mkdir(parents=True);show.mkdir()
 copied=[]
 for p in sorted((S/role).rglob('*')):
  if p.is_file():
   q=original/p.relative_to(S/role);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes();copied.append(dict(source=fact(p),retained=q.relative_to(O).as_posix()))
 for p in [x for x in S.iterdir() if x.is_file()]:
  q=original/'coordinator'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert p.read_bytes()==q.read_bytes()
 if role=='source':
  shutil.copytree(S/'BoundRunOnly-v2',original/'published-store/BoundRunOnly-v2')
  for p in (S/'BoundRunOnly-v2').rglob('*'):
   if p.is_file():assert p.read_bytes()==(original/'published-store/BoundRunOnly-v2'/p.relative_to(S/'BoundRunOnly-v2')).read_bytes()
 report=read(original/'runtime-report.json');assert report['passed'] and report['native_async_capture_writes_flushed']
 frames=sorted(original.glob('MovieFrame*.png'));timing=report['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=report['duration_s']
 assert len(frames)==len(offsets)==len(report['observations']) and duration>offsets[-1]
 lines=['ffconcat version 1.0']
 for i,p in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+p.as_posix().replace("'","'\\''")+"'",f'duration {dt:.12f}']
 lines.append("file '"+frames[-1].as_posix()+"'")
 concat=show/'native-frame-timing-v001.ffconcat';concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 video=show/f'guard-v2-{role}-silent-v001.mp4'
 cmd=[ffmpeg,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-vsync','vfr','-t',f'{duration-offsets[0]:.9f}','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]
 result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/'encode-v001.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0
 result=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],capture_output=True,text=True,encoding='utf-8');(show/'decode-v001.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0
 shutil.copy2(frames[-1],show/'last-native-viewport-UNSCALED.png')
 data=dict(schema='Root-guard-v2-native-process-media-v001',role=role,session=fact(S/'two-process-session.json'),role_report=fact(original/'runtime-report.json'),movie=fact(video),native_frames=len(frames),silent=True,full_decode_exit=0,Source_DLL_unchanged=True,Scope='two real UE processes/public003 setup/native disk+pristine resume; procedural enemy visual, formal room/reward/audio incomplete',source_copy=copied,visual_reviewed=False,complete_units=0)
 (O/'source-version-status-index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 (O/'README.md').write_text('裂岩守卫V2真实两进程运行证据。原件与原时间戳静音录像同时保留，独立技术核验通过；怪物外观仍占位，正式房间生成、奖励与音效未完成。展示前须E保全；尚未审看，不等于完整单元验收。\n',encoding='utf-8')
 outputs.append(dict(archive=str(O),role=role,frames=len(frames),video=fact(video)))
print(json.dumps(outputs,ensure_ascii=False))
