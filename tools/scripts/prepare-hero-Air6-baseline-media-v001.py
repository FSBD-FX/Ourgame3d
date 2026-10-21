"""Verify exact native gap captures and prepare full VFR presentation with real mix."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
R=Path('F:/Ourgame');ap=argparse.ArgumentParser();ap.add_argument('--side',choices=['left','right'],required=True);a=ap.parse_args()
M=R/f'过程图稿与视频/2026-10-19_钟盔跳跃旧渲染缺口实录_{a.side}_v001';O=M/'原件';D=M/'展示副本'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
report=read(O/'runtime-report.json');assert report['passed'] and report['baseline_gap_observed'] and not report['new_air_passed']
assert report['normal_space_inputs']==report['air_transitions']==report['landing_transitions']==2 and report['initial_hp']==report['capture_final_hp']==100 and report['physical_air_mask']==15 and report['second_landing_mask']==48
frames=sorted(O.glob('MovieFrame*.png'));obs=report['observations'];offsets=report['capture_timing']['frame_wall_offsets_s'];assert len(frames)==len(obs)==len(offsets)
duration=report['capture_timing']['capture_stop_monotonic_s']-report['capture_timing']['capture_start_monotonic_s'];assert duration>offsets[-1]
summary=read(O/'native-async-write-summary.json');assert summary['success'] and summary['flushed'] and summary['closed'] and summary['movie_saved']==summary['movie_completed']==summary['receipts_saved']==len(frames) and not any(summary[k] for k in ['movie_failed','movie_reservation_failed','rejected','pending'])
receipts=[json.loads(line) for line in (O/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if line];assert len(receipts)==len(frames)+1
for row in receipts:
 p=O/row['file'];im=Image.open(p).convert('RGBA');arr=np.array(im);assert row['saved'] and im.size==(1280,720) and zlib.crc32(arr[:,:,[2,1,0,3]].tobytes())&0xffffffff==row['native_BGRA8_crc32'],p
for x in read(M/'preregistration-v001.json')['files']:
 assert pin(Path(x['path']) if Path(x['path']).is_absolute() else R/x['path'])==dict(x,path=(Path(x['path']) if Path(x['path']).is_absolute() else R/x['path']).as_posix())
audio=read(M/'audio-independent-verification-v001.json');assert audio['passed'] and audio['decoded_PCM']['non_silent']
for x in obs:
 assert x['hp']==100 and not x['dead'] and not x['interface_visible'] and x['text_calls']==x['range_lines']==0 and not x['range_debug']
 if x['baseline_bare_ready0_gap']:assert x['old_draw']['frame']==0 and not x['old_draw']['armor_drawn'] and not x['old_draw']['sword_drawn'] and x['new_air_draw']['slot_count']==0
verification=M/'native-independent-verification-v001.json';assert not verification.exists()
verification.write_text(json.dumps(dict(schema='Root-Air6-baseline-independent-v001',passed=True,native=pin(O/'runtime-report.json'),source_pins_unchanged=True,full_PNG_BGRA_CRCs=len(receipts),native_frames=len(frames),all_original_200_still_green=True,only_scope='Observed missing Air poses/gear in existing renderer, real native mix captured; new art still not imported.',visual_reviewed=False,listened=False,formal_complete_units=0),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Reuse the retained exact all-frame microsecond VFR encoder unchanged.
encoder=R/'source-assets/production/fairytale-guard-v001/stomp-native-media-candidate-v001/tooling/retained-microsecond-VFR-v001.py'
spec=importlib.util.spec_from_file_location('retained_native_vfr',encoder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
work=M/'原件/派生编码日志';assert not work.exists();work.mkdir()
silent,last,timing,decoded=module.encode_vfr(work,frames,offsets,duration)
ff=imageio_ffmpeg.get_ffmpeg_exe();video=D/'hero-Air-baseline-native-mix-DIAGNOSTIC-v001.mp4';assert not video.exists()
command=[ff,'-hide_banner','-loglevel','error','-n','-itsoffset',f'{offsets[0]:.9f}','-i',str(silent),'-i',str(O/'audio-v001/runtime-mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-video_track_timescale','1000000','-movflags','+faststart',str(video)]
r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8');(work/'mux-native-audio.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
decode=subprocess.run([ff,'-hide_banner','-loglevel','info','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,encoding='utf-8');(work/'decode-complete-av.log').write_text(decode.stdout+decode.stderr,encoding='utf-8');assert decode.returncode==0
md5=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-map','0:v:0','-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8');assert md5.returncode==0
rows=[s for s in md5.stdout.splitlines() if s and not s.startswith('#')];assert len(rows)==len(frames)
(work/'muxed-video-full-framemd5.txt').write_text(md5.stdout,encoding='utf-8')
selected=[]
for phase in range(6):
 choices=[i for i,x in enumerate(obs) if x['physical_visual_key']==phase and (x['baseline_bare_ready0_gap'] if phase<4 else not x['melee_active'] and not x['wa_active'])];assert choices
 i=choices[len(choices)//2];dest=D/f'phase-{phase}-native-UNSCALED.png';assert not dest.exists();shutil.copy2(frames[i],dest);selected.append(dict(phase=phase,index=i,source=pin(frames[i]),presentation=pin(dest),observation=obs[i]))
board=Image.new('RGB',(1536,530),(45,48,54));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for k,s in enumerate(selected):
 x=s['observation'];g=x['ground'];c=x['camera_ground'];sx=round(640+(g[0]-c[0])*.65);sy=490;crop=(max(0,sx-110),sy-240,min(1280,sx+110),sy+80)
 im=Image.open(s['source']['path']).crop(crop);col=k%3;row=k//3;board.paste(im,(col*512+140,row*265+30));draw.text((col*512+8,row*265+6),f"phase{ s['phase']} H{x['jump_height']:.2f} V{x['vertical_velocity']:.1f} age{x['landing_visual_age']:.3f}",font=font,fill='white')
# Board crops are explicitly diagnostic; six full original screenshots above remain exact.
boardpath=D/'six-native-physical-phases-CROPPED-diagnostic.png';board.save(boardpath)
shutil.copy2(Path(__file__),O/Path(__file__).name)
index=dict(schema='Root-Air6-baseline-media-v001',status='native gap and actual signal verified; E and Root playback/visual review pending',native=pin(O/'runtime-report.json'),independent=pin(verification),audio_independent=pin(M/'audio-independent-verification-v001.json'),video=pin(video),video_frames=len(rows),native_frames=len(frames),all_frames_kept=True,first_video_PTS_offset_s=offsets[0],native_audio_PCM_original_preserved=True,AAC_is_lossy_presentation=True,no_audio_trim_or_replacement=True,silent_encoder_source=pin(encoder),VFR_timing=timing,samples=selected,visual_reviewed=False,listened=False,formal_complete_units=0,files=[pin(p) for p in sorted(M.rglob('*')) if p.is_file()])
(M/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(side=a.side,native_frames=len(frames),video=pin(video),raw_crc_passed=len(receipts),E_before_View=True),ensure_ascii=False))
