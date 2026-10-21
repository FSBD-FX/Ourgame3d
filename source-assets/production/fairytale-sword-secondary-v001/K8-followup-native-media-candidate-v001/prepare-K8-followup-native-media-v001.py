"""Finite read-only-input presentation preparation for a passed actual K pilot.
Root executes this candidate after review. No UE launch, gameplay or source writes.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, shutil, subprocess, sys
from datetime import datetime, timezone
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
C=ROOT/'source-assets/production/fairytale-sword-secondary-v001'
PIXEL=dict(path=(C/'K8-native-pixel-checker-candidate-v002/verify-K8-native-pixels-v002.py').as_posix(),bytes=23039,sha256='aa677a9c15fb5dcf2414c22b7b5940870db4711d8d566e22122d942d6ee08188')
PIXEL_FREEZE=dict(path=(C/'K8-native-pixel-checker-candidate-v002/candidate-freeze-v002.json').as_posix(),bytes=6601,sha256='fb14b809e95a53cb4b318f1e9cd97d5e8a68c1c53c1ba4ffa14d7eda7d57e28a')
ENCODER=dict(path=(ROOT/'source-assets/production/fairytale-guard-v001/stomp-native-media-candidate-v001/tooling/retained-microsecond-VFR-v001.py').as_posix(),bytes=3585,sha256='6554573c99d4a2905200433718d0b56074aac6893b97c9436048db78c6cadc78')

def need(ok,why):
 if not ok:raise ValueError(why)
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def pin(path):
 path=Path(path);h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return dict(path=path.as_posix(),bytes=path.stat().st_size,sha256=h.hexdigest())
def checked(row):
 p=Path(row['path']);need(pin(p)==row,'Immutable input pin differs: '+str(p));return p
def save(path,value):
 with Path(path).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def module(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def copy_exact(source,target):
 source=Path(source);target=Path(target);before=pin(source)
 with source.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)
 need(pin(source)==before and pin(target)['sha256']==before['sha256'] and pin(target)['bytes']==before['bytes'],'Exact retained copy mismatch')
 return dict(source=before,retained=pin(target))
def choose_log(archive,prereg_path,case,explicit=None):
 original=archive/'原件'
 if explicit is not None:log=Path(explicit).resolve()
 elif (original/'actual-native-engine-log-preserved-v001.log').is_file():log=original/'actual-native-engine-log-preserved-v001.log'
 elif (original/'Root-provenance-v001/actual-native-engine.log').is_file():log=original/'Root-provenance-v001/actual-native-engine.log'
 else:raise ValueError('No archive-local preserved engine log; pass --engine-log for the actual launched prereg. Mutable global logs are never selected.')
 text=log.read_text(encoding='utf-8-sig',errors='replace').replace('\\','/')
 need(prereg_path.as_posix() in text and '-DungeonSwdForwardStepCase='+case in text,'Preserved engine log does not match actual launched prereg/case')
 return log

def preflight(archive,prereg_path,engine_log=None):
 archive=Path(archive).resolve();prereg_path=Path(prereg_path).resolve();original=archive/'原件';prereg=read(prereg_path);report=read(original/'runtime-report.json');native=read(archive/'native-check-result.json')
 need(native['status']=='ExploratoryPilotRecorded' and native['pilot_checks_passed'] is True and native['errors']=={} and native['formal_accepted'] is False and native['checker_accepted'] is False,'Actual passed pilot checks required; failed/raw-missing archives stay unchanged')
 need(report['route_mode']==prereg['route_mode']=='exploratory_pilot' and report['passed'] is True and report['flow_complete'] is True and report['failure']=='' and report['secondary_frame_mask']==255,'Actual completed K8 pilot required')
 need(report['formal_accepted'] is False and report['checker_accepted'] is False,'Presentation does not grant formal acceptance')
 launch=read(archive/'launch-argv.json');started=read(archive/'process-started.json');exited=read(archive/'process-exit.json');sha=pin(prereg_path)['sha256'];case=report['case']
 need(sha==launch['prereg_sha256']==started['prereg_sha256'] and started['process_id']==report['process_id'] and started['native_run_attempted'] is True and exited['native_run_attempted'] is True and exited['exit_code']==0,'Original prereg/process/OS exit does not match')
 need(case in prereg['cases'] and '-DungeonSwdForwardStepCase='+case in launch['argv'] and '-DungeonSwdForwardStepPrereg='+prereg_path.as_posix() in [x.replace('\\','/') for x in launch['argv']],'Actual case/prereg argv binding differs')
 placement=native['checks']['placement'];need(placement['passed'] is True and placement['witness']==report['placement_witnesses'][0] and placement['classification']==report['native_route_classification']==native['observed_classification'],'Actual native placement provenance differs')
 need(prereg['checker_dependencies']['K_pixel_composition']==PIXEL and prereg['checker_dependencies']['K_pixel_composition_freeze']==PIXEL_FREEZE,'Pinned approved pixel-v002 script/freeze required')
 art=module(checked(PIXEL),'K8_followup_actual_pixels');checked(PIXEL_FREEZE);pixel=art.audit(archive,prereg)
 need(pixel['passed'] is True and pixel['actual_native_pixel_composition_verified'] is True,'Actual unchanged K pixel audit failed')
 log=choose_log(archive,prereg_path,case,engine_log);inputs=[dict(name='launched-prereg.json',path=prereg_path)]
 for key,name in [('compiled_manifest','compiled-source-manifest.json'),('source_admission','actual-source-admission.json'),('review_report','source-independent-review.md')]:inputs.append(dict(name=name,path=checked(prereg[key])))
 inputs += [dict(name='actual-native-engine.log',path=log),dict(name='prepare-K8-followup-native-media-v001.py',path=Path(__file__).resolve()),dict(name='retained-microsecond-VFR-v001.py',path=checked(ENCODER)),dict(name='verify-K8-native-pixels-v002.py',path=checked(PIXEL)),dict(name='pixel-candidate-freeze-v002.json',path=checked(PIXEL_FREEZE))]
 frames=sorted(original.glob('MovieFrame*.png'));obs=report['observations'];t=report['capture_timing'];offsets=t['frame_wall_offsets_s'];duration=t['capture_stop_monotonic_s']-t['capture_start_monotonic_s']
 need(not t['use_fixed_time_step'] and len(frames)==len(obs)==len(offsets)>1 and offsets==[o['wall_offset_s'] for o in obs] and all(b>a for a,b in zip(offsets,offsets[1:])) and duration>offsets[-1],'Actual all-frame native timing missing/inconsistent')
 mix=report['main_submix_capture'];wav=Path(mix['canonical_wav']);need(mix['phase']=='Complete' and mix['failure']=='' and wav.resolve()==(original/'audio-v001/runtime-mix.wav').resolve() and wav.is_file(),'Actual original completed main-mix WAV missing')
 before=[i for i,o in enumerate(obs) if o['common_draw'].get('clip')=='sword_ready_idle' and o['sim']<report['accepted_action']['start']]
 after=[i for i,o in enumerate(obs) if o['common_draw'].get('clip')=='sword_ready_idle' and o['sim']>=report['accepted_action']['end']]
 witnesses=pixel['K8_native_pixel_witnesses'];need(before and len(after)>=2 and [w['frame'] for w in witnesses]==list(range(8)),'Real Ready/K8/End selection is incomplete')
 choices=[('Ready-before',before[-1])]+[(f"K{w['frame']}",w['callback_index']) for w in witnesses]+[('Ready-after',after[0])]
 need(len({i for label,i in choices})==10 and all(frames[w['callback_index']].name==w['original_PNG'] for w in witnesses),'Actual ten-frame source selection differs from native pixel FIFO')
 return dict(archive=archive,prereg_path=prereg_path,original=original,prereg=prereg,report=report,native=native,pixel=pixel,frames=frames,offsets=offsets,duration=duration,wav=wav,inputs=inputs,choices=choices,placement=placement)

def crop_box(witnesses):
 # A common actual K quad union keeps the same 1:1 diagnostic crop in all ten
 # panels. Ready has no typed quad trace: its full exact PNG is retained and its
 # crop is explicitly anchored to this K union, not claimed Ready pixel proof.
 boxes=[w['submitted_quad_ROI'] for w in witnesses];x0=min(b[0] for b in boxes);y0=min(b[1] for b in boxes);x1=max(b[2] for b in boxes);y1=max(b[3] for b in boxes)
 width=min(1280,max(200,math.ceil(x1-x0)));height=min(720,max(190,math.ceil(y1-y0)));left=max(0,min(1280-width,math.floor((x0+x1-width)/2)));top=max(0,min(720-height,math.floor((y0+y1-height)/2)))
 return (left,top,left+width,top+height)
def run(archive,prereg_path,out,engine_log=None):
 out=Path(out).resolve();archive=Path(archive).resolve();need(not out.exists() and out.is_relative_to(archive) and not out.is_relative_to(archive/'原件') and not out.is_relative_to(HERE),'One NEW presentation directory inside the archive, outside 原件, is required')
 data=preflight(archive,prereg_path,engine_log);out.mkdir(exist_ok=False)
 try:
  original=data['original'];report=data['report'];frames=data['frames'];offsets=data['offsets'];duration=data['duration'];case=report['case'];native_input_pins=[pin(p) for p in [original/'runtime-report.json',archive/'native-check-result.json',archive/'launch-argv.json',archive/'process-started.json',archive/'process-exit.json',data['wav']]]
  save(out/'independent-K8-native-pixel-audit-v002.json',data['pixel']);display=out/'展示副本';display.mkdir();work=out/'派生编码日志-v001';work.mkdir();provenance=out/'来源凭证';provenance.mkdir()
  retained=[copy_exact(x['path'],provenance/x['name']) for x in data['inputs']]
  # Unchanged proven encoder API: every original frame, actual offsets, duration.
  encoder=module(checked(ENCODER),'K8_followup_proven_VFR');silent,last,timing,decoded=encoder.encode_vfr(work,frames,offsets,duration)
  video=display/f'SWD001-K-{case}-native-timing-original-mix-v001.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
  command=[ff,'-hide_banner','-loglevel','error','-n','-itsoffset',f'{offsets[0]:.9f}','-i',str(silent),'-i',str(data['wav']),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-video_track_timescale','1000000','-movflags','+faststart',str(video)]
  result=subprocess.run(command,capture_output=True,text=True,encoding='utf8');(work/'mux-native-audio.log').write_text(result.stdout+result.stderr,encoding='utf8');need(result.returncode==0,'Mux failed; partial presentation retained: '+result.stderr)
  full=subprocess.run([ff,'-hide_banner','-loglevel','info','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True,encoding='utf8');(work/'full-audio-video-decode.log').write_text(full.stdout+full.stderr,encoding='utf8');need(full.returncode==0,'Full AV decode failed: '+full.stderr)
  md5=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-map','0:v:0','-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf8');need(md5.returncode==0,'Full muxed frame decode failed');decoded_rows=[l for l in md5.stdout.splitlines() if l and not l.startswith('#')];need(len(decoded_rows)==len(frames),'Mux dropped/added actual native frames');(work/'muxed-video-full-framemd5.txt').write_text(md5.stdout,encoding='utf8')
  box=crop_box(data['pixel']['K8_native_pixel_witnesses']);width=box[2]-box[0];height=box[3]-box[1];board=Image.new('RGB',(5*(width+20),2*(height+36)),(35,39,45));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13);samples=[]
  for k,(label,i) in enumerate(data['choices']):
   source=frames[i];target=display/f'{k:02d}-{label}-native-1280x720.png';pair=copy_exact(source,target)
   with Image.open(source) as im:crop=im.convert('RGB').crop(box)
   x,y=(k%5)*(width+20)+10,(k//5)*(height+36);board.paste(crop,(x,y+32));draw.text((x,y+2),f'{label} callback {i}',fill='white',font=font);draw.text((x,y+17),f'wall {offsets[i]:.6f}s / 1:1 crop',fill='white',font=font);samples.append(dict(label=label,callback_index=i,wall_offset_s=offsets[i],full_frame=pair,diagnostic_crop_box=box,crop_scale=1,Ready_crop_anchor='actual K quad union; Ready typed geometry unavailable' if label.startswith('Ready') else None))
  board_path=display/'K8-and-Ready-native-UNSCALED-crop-board-v001.png';board.save(board_path)
  # Recheck input pins after processing: encoding/presentation never alters raw.
  for row in native_input_pins:checked(row)
  save(out/'README-status.json',dict(case=case,actual_classification=report['native_route_classification'],actual_committed_delta=data['placement']['witness']['committed_delta'],status='Actual passed pilot-derived presentation; retention and human review pending',all_native_frames=len(frames),visual_reviewed=False,full_realtime_playback_reviewed=False,audio_listened=False,device_onset_measured=False,Ready_optical_composition_verified=False,individual_owner_unique_pixel_attribution=False,formal_accepted=False,FinalAccepted=False))
  index=dict(schema='K8-followup-native-media-v001',utc=datetime.now(timezone.utc).isoformat(),archive=archive.as_posix(),case=case,requested_facing=report['requested_facing'],actual_classification=report['native_route_classification'],actual_placement=data['placement']['witness'],native_process_id=report['process_id'],original_OS_exit=0,native_inputs=native_input_pins,independent_pixels=pin(out/'independent-K8-native-pixel-audit-v002.json'),all_native_frames_kept=True,native_frames=len(frames),original_full_frames=[pin(f) for f in frames],video=pin(video),VFR_timing=timing,video_full_AV_decode_passed=True,decoded_video_frames=len(decoded_rows),original_WAV_unchanged=True,AAC_is_lossy_presentation=True,no_audio_trim_or_replacement=True,first_callback_offset_s=offsets[0],encoder=ENCODER,tool=pin(Path(__file__)),provenance=retained,samples=samples,diagnostic_board=pin(board_path),Ready_optical_composition_verified=False,unique_individual_owner_attribution=False,visual_reviewed=False,full_realtime_playback_reviewed=False,audio_listened=False,device_onset_measured=False,formal_accepted=False,FinalAccepted=False,files=[pin(f) for f in sorted(out.rglob('*')) if f.is_file()]);save(out/'source-version-status-index-v001.json',index)
  return dict(status='PresentationPrepared',out=out.as_posix(),case=case,actual_classification=report['native_route_classification'],actual_committed_delta=data['placement']['witness']['committed_delta'],native_frames=len(frames),video=pin(video),actual_K8_pixel_audit_passed=True,retention_before_View_required=True,visual_reviewed=False,audio_listened=False,FinalAccepted=False)
 except Exception as e:
  save(out/'presentation-failure-preserved-v001.json',dict(status='NeedsFixes',reason=str(e),raw_archive_modified=False,partial_output_retained=True,FinalAccepted=False));raise

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--prereg',type=Path,required=True);ap.add_argument('--out',type=Path);ap.add_argument('--engine-log',type=Path);ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
 try:
  if args.preflight:
   d=preflight(args.archive,args.prereg,args.engine_log);result=dict(status='ReadOnlyInputsVerified',case=d['report']['case'],native_frames=len(d['frames']),actual_committed_delta=d['placement']['witness']['committed_delta'],actual_K8_pixel_audit_passed=True,media_written=False,FinalAccepted=False)
  else:need(args.out is not None,'--out NEW is required for media preparation');result=run(args.archive,args.prereg,args.out,args.engine_log)
  print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0)
 except (ValueError,KeyError,TypeError,OSError,AssertionError,IndexError) as e:print(json.dumps(dict(status='NeedsFixes',reason=str(e),raw_archive_modified=False,failed_or_partial_evidence_preserved=True,FinalAccepted=False),ensure_ascii=False,indent=2));sys.exit(3)
