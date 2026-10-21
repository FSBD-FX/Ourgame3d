"""Prepare NEW Air production presentation after an actual independent PASS.

Read-only rerun of the frozen checker binds every source PNG/PCM/frame/time.
No UE, View, E retention, offline cue synthesis, retiming or source image edit.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import wave
import imageio_ffmpeg
import PIL
from PIL import Image, ImageDraw, ImageChops

sys.dont_write_bytecode = True
ROOT=Path('F:/Ourgame')
HERE=Path(__file__).resolve().parent
ENCODER=ROOT/'source-assets/production/fairytale-guard-v001/stomp-native-media-candidate-v001/tooling/retained-microsecond-VFR-v001.py'
ENCODER_SHA='6554573c99d4a2905200433718d0b56074aac6893b97c9436048db78c6cadc78'
CHECKER_FREEZE_SHA='a6bb3f8bd3127aa49b788f72ec1e7d9c9a9bddf8d790eb3c80c1de45e8166a46'


def need(value,reason):
    if not value:raise ValueError(reason)


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def pin(path):
    p=Path(path).resolve();h=hashlib.sha256();size=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):size+=len(b);h.update(b)
    return dict(path=p.as_posix(),bytes=size,sha256=h.hexdigest())


def checked(row):
    actual=pin(row['path']);need(actual==row,'Actual pinned input differs: '+str(row['path']));return Path(actual['path'])


def write_new(path,value):
    data=(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
    with Path(path).open('xb') as f:
        need(f.write(data)==len(data),'Short output write; preserve partial')
        f.flush()
        import os
        os.fsync(f.fileno())
    return pin(path)


def copy_exact(source,destination):
    before=pin(source)
    with Path(source).open('rb') as r,Path(destination).open('xb') as w:
        for b in iter(lambda:r.read(1024*1024),b''):need(w.write(b)==len(b),'Short exact-copy write')
    after=pin(destination);need((after['bytes'],after['sha256'])==(before['bytes'],before['sha256']),'Original copy differs')
    return after


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def runtime_environment():
    binary=imageio_ffmpeg.get_ffmpeg_exe()
    version=subprocess.run([binary,'-version'],capture_output=True,text=True,encoding='utf-8')
    need(version.returncode==0,'Cannot record actual ffmpeg version')
    return dict(Python_version=sys.version,Python_executable=pin(sys.executable),ffmpeg_binary=pin(binary),
                ffmpeg_version_output=version.stdout,Pillow_version=PIL.__version__,Pillow_module=pin(PIL.__file__),
                Pillow_Image_module=pin(Image.__file__),imageio_ffmpeg_version=imageio_ffmpeg.__version__,
                imageio_ffmpeg_module=pin(imageio_ffmpeg.__file__))


def timing_rows(text,count,expected):
    need('#tb 0: 1/1000000' in text,'Decoded presentation timebase differs')
    rows=[line.split(',') for line in text.splitlines() if line and not line.startswith('#')]
    need(len(rows)==count==len(expected),'Presentation dropped/added frames')
    stamps=[int(row[2])/1e6 for row in rows]
    need(all(b>a for a,b in zip(stamps,stamps[1:])),'Encoded frame PTS are not strictly increasing')
    errors=[abs(a-b) for a,b in zip(stamps,expected)];bound=count*1e-6+2e-6
    need(max(errors,default=0)<=bound,'Presentation PTS differ from original microsecond timeline')
    return rows,dict(decoded_frames=count,maximum_PTS_rounding_error_s=max(errors,default=0),derived_rounding_bound_s=bound,
                     expected_PTS=list(expected),decoded_PTS=stamps,timebase='1/1000000',every_native_frame_kept=True)


def run(command,log):
    result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
    write_new(log,json.dumps(command,ensure_ascii=False)+'\n'+result.stdout+result.stderr)
    need(result.returncode==0,'ffmpeg failed; preserve output/log: '+str(log))
    return result


def encode_with_full_native_mix(work,display,frames,offsets,duration,canonical_wav,expected_audio):
    need(pin(ENCODER)['sha256']==ENCODER_SHA,'Retained microsecond VFR helper changed')
    helper=module(ENCODER,'retained_native_microsecond_VFR')
    silent,last,original_timing,decoded=helper.encode_vfr(work,frames,offsets,duration)
    ff=imageio_ffmpeg.get_ffmpeg_exe();video=display/'hero-Air6-production-full-native-mix-DIAGNOSTIC-v001.mp4'
    # Entire native canonical PCM is the only audio input. Video begins at its
    # actual first-callback offset; no shortest/t/trim, fps filter or replacement.
    command=[ff,'-hide_banner','-loglevel','error','-n','-itsoffset',format(offsets[0],'.9f'),'-i',str(silent),
             '-i',str(canonical_wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k',
             '-video_track_timescale','1000000','-movie_timescale','1000000','-movflags','+faststart',str(video)]
    run(command,work/'mux-full-native-audio.log')
    run([ff,'-hide_banner','-loglevel','info','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'],work/'decode-complete-AV.log')
    md5=run([ff,'-hide_banner','-loglevel','error','-copyts','-i',str(video),'-map','0:v:0','-enc_time_base','1:1000000',
             '-fps_mode','passthrough','-f','framemd5','-'],work/'muxed-video-all-framemd5.log')
    rows,actual_timing=timing_rows(md5.stdout,len(frames),offsets)
    audio=run([ff,'-hide_banner','-loglevel','error','-copyts','-i',str(video),'-map','0:a:0','-c:a','pcm_s16le','-f','framemd5','-'],work/'decoded-complete-AAC-framemd5.log')
    rate=expected_audio['sample_rate_hz'];channels=expected_audio['channels'];native_samples=expected_audio['frames']
    need(f'#tb 0: 1/{rate}' in audio.stdout and f'#sample_rate 0: {rate}' in audio.stdout,'AAC presentation sample rate changed')
    audio_rows=[x.split(',') for x in audio.stdout.splitlines() if x and not x.startswith('#')]
    need(audio_rows and all(int(x[4])==int(x[3])*channels*2 for x in audio_rows),'Complete decoded AAC channel/sample layout changed')
    samples=sum(int(x[3]) for x in audio_rows);first=int(audio_rows[0][2])/rate
    need(abs(samples-native_samples)<=2048 and abs(first)<=1024/rate,'AAC full-file length/origin differs beyond two1024-sample priming/padding packets')
    final=display/'decoded-final-frame-Air6-production-lossy-v001.png'
    run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})',
         '-fps_mode','passthrough','-frames:v','1',str(final)],work/'decode-final-muxed-frame.log')
    with Image.open(final) as im:need(im.size==(1280,720),'Decoded last frame dimensions differ')
    receipt=dict(video=pin(video),original_silent_VFR=original_timing,muxed_VFR=actual_timing,full_AV_decoded=True,
                 actual_audio_origin_s=0,first_video_PTS_s=actual_timing['decoded_PTS'][0],native_first_callback_offset_s=offsets[0],
                 native_audio_samples=native_samples,decoded_AAC_samples=samples,decoded_AAC_first_PTS_s=first,
                 AAC_priming_padding_sample_bound=2048,AAC_is_lossy=True,AAC_PCM_byte_equality_claimed=False,
                 native_audio_trimmed_or_replaced=False,frames_dropped_or_added=False,simulation_time_used_for_video=False,
                 decoded_final=pin(final),native_final=pin(frames[-1]),decoded_source_pixel_equality_claimed=False,
                 visual_reviewed=False,audio_listened=False,FinalAccepted=False)
    write_new(work/'full-presentation-timing-and-audio-verification.json',receipt)
    return receipt


def chosen_samples(report,independent,frames):
    byname={f.name:i for i,f in enumerate(frames)};obs=report['observations'];samples=[]
    witnesses=independent['source_pixels']['source_registered_witnesses']
    need(len(witnesses)==18,'Actual18 optical witness samples required')
    for ordinal in (1,2,3):
        for frame in range(6):
            choices=[w for w in witnesses if w['ordinal']==ordinal and w['frame']==frame]
            need(len(choices)==1,'Missing/duplicate real phase witness')
            w=choices[0];need(w['file'] in byname,'Optical witness PNG not in actual movie FIFO')
            i=byname[w['file']];o=obs[i]
            need(o['observed_air_transition_ordinal']==ordinal and o['physical_visual_key']==frame
                 and o['new_air_draw']['drawn'] is True,'Original witness no longer matches actual sample')
            samples.append(dict(ordinal=ordinal,frame=frame,observation=i,witness=w))
    jump=independent['flow']['actual_adjacent_rejump'];need(jump['after']==jump['before']+1,'Re-jump must be actual adjacent callbacks')
    joins=[dict(kind='Land5_to_Air0_rejump',before=jump['before'],after=jump['after'])]
    for ordinal in (1,3):
        edges=[i for i in range(len(obs)-1) if obs[i]['observed_air_transition_ordinal']==ordinal
               and obs[i]['physical_visual_key']==5 and obs[i+1]['physical_visual_key']==-1
               and obs[i+1]['old_draw']['clip']=='sword_ready_idle' and not obs[i+1]['new_air_draw']['drawn']]
        need(len(edges)==1,'Actual Land5→Ready renderer adjacency missing/ambiguous')
        joins.append(dict(kind=f'Jump{ordinal}_Land5_to_Ready',before=edges[0],after=edges[0]+1))
    return samples,joins


def rectangles_nonoverlap(rects):
    for i,a in enumerate(rects):
        need(a[2]>a[0] and a[3]>a[1],'Empty board rectangle')
        for b in rects[:i]:need(a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1],'Board image rectangles overlap')


def make_board(path,samples,frames,report,columns,cropped):
    crop_w,crop_h=256,320;label=32;gap=12
    width,height=(crop_w,crop_h) if cropped else (1280,720)
    cell_w,cell_h=width+gap,height+label+gap;rows=math.ceil(len(samples)/columns)
    board=Image.new('RGB',(columns*cell_w,rows*cell_h),(26,29,34));draw=ImageDraw.Draw(board);rects=[];details=[]
    for k,s in enumerate(samples):
        i=s['observation'];o=report['observations'][i];col,row=k%columns,k//columns;x=col*cell_w;y=row*cell_h+label
        with Image.open(frames[i]) as im:
            need(im.size==(1280,720),'Original unscaled viewport required')
            if cropped:
                ground=o['new_air_draw']['context_ground'] if o['new_air_draw']['drawn'] else [round(640+(o['ground'][0]-o['camera_ground'][0])*.65),490-o['ground'][1]*.38]
                cx=int(round(ground[0]));cy=int(round(ground[1]));left=max(0,min(1280-crop_w,cx-crop_w//2));top=max(0,min(720-crop_h,cy-240))
                crop=[left,top,left+crop_w,top+crop_h];piece=im.crop(crop).convert('RGB')
            else:crop=[0,0,1280,720];piece=im.convert('RGB')
            rect=[x,y,x+width,y+height];rects.append(rect);board.paste(piece,(x,y))
        draw.text((col*cell_w+6,row*cell_h+6),f'Jump{o["observed_air_transition_ordinal"]} pose{o["physical_visual_key"]} | obs{i} wall{o["wall_offset_s"]:.6f}',fill='white')
        details.append(dict(observation=i,source=pin(frames[i]),source_crop=crop,board_rect=rect,source_pixels_resized=False,
                            source_PNG_modified=False,label_inside_game_rect=False))
    rectangles_nonoverlap(rects)
    with Path(path).open('xb') as f:board.save(f,format='PNG')
    with Image.open(path) as rendered:
        for d in details:
            with Image.open(d['source']['path']) as source:
                expected=source.crop(d['source_crop']).convert('RGB')
                need(ImageChops.difference(rendered.crop(d['board_rect']),expected).getbbox() is None,
                     'Board pixels differ from exact original crop; labels/painting/resizing forbidden')
    return dict(file=pin(path),details=details,cell_size=[cell_w,cell_h],rectangles_nonoverlapping=True,
                exact_RGB_source_crops_redecoded_and_equal=True,visual_reviewed=False)


def actual_inputs(archive,prereg_path,independent_path):
    p=read(prereg_path);need(p['RootApproved'] is True and p['is_template'] is False,'Actual Root prereg required')
    checker=checked(p['checker_pin']);freeze=checked(p['checker_freeze_pin'])
    need(pin(freeze)['sha256']==CHECKER_FREEZE_SHA,'This presentation requires frozen v002 checker')
    for row in read(freeze)['members']:checked(row)
    need(pin(checker) in read(freeze)['members'],'Actual checker absent from freeze')
    existing=sys.modules.get('air_production_contract_v001')
    need(existing is None or Path(existing.__file__).resolve()==checker.parent/'air_production_contract_v001.py','Another checker contract already imported')
    verify=module(checker,'actual_Air6_v002_native_checker')
    expected=read(independent_path);actual=verify.verify_native(archive,prereg_path)
    need(actual==expected and actual['passed'] is True,'Fresh readonly official recheck differs from retained actual result')
    original=Path(archive)/'原件';r=read(original/'runtime-report.json');rows=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
    movie=[x for x in rows if x['file'].startswith('MovieFrame')];frames=[original/x['file'] for x in movie]
    offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['capture_timing']['capture_stop_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']
    need(len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]>=offsets[0]>=0,'Full actual original timeline required')
    audio=actual['audio'];engine=checked(audio['engine_original']);canonical=checked(audio['canonical'])
    need(engine==original/'audio-v001/runtime-mix-engine-export.wav' and canonical==original/'audio-v001/runtime-mix.wav','Actual native full mix paths differ')
    samples,joins=chosen_samples(r,actual,frames)
    bindings=dict(native_report=pin(original/'runtime-report.json'),native_session=pin(Path(archive)/'index.json'),
                  root_prereg=pin(prereg_path),independent=pin(independent_path),actual_checker=pin(checker),checker_freeze=pin(freeze),
                  official_readonly_recheck_passed=True,compiled_manifest=p['compiled_manifest_pin'],source_probe_freeze=p['source_probe_freeze_pin'],
                  engine_original_WAV=pin(engine),canonical_WAV=pin(canonical),all_native_frame_pins=[pin(f) for f in frames])
    return r,actual,frames,offsets,duration,engine,canonical,samples,joins,bindings


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--archive',required=True);parser.add_argument('--root-prereg',required=True)
    parser.add_argument('--independent',required=True);parser.add_argument('--output');parser.add_argument('--validate-only',action='store_true');a=parser.parse_args()
    archive=Path(a.archive).resolve();prereg=Path(a.root_prereg).resolve();independent=Path(a.independent).resolve()
    r,v,frames,offsets,duration,engine,canonical,samples,joins,bindings=actual_inputs(archive,prereg,independent)
    if a.validate_only:
        print(json.dumps(dict(actual_native_and_independent_verified=True,all_native_frames=len(frames),samples=len(samples),joins=joins,
                              media_written=False,UE_started=False,View=False,FinalAccepted=False)));return
    need(a.output,'NEW F media output leaf required');output=Path(a.output)
    need(output.is_absolute(),'Absolute NEW media leaf required');output=output.resolve()
    need(output.parent==ROOT/'过程图稿与视频' and not output.exists() and output!=archive,'NEW direct F media leaf required')
    output.mkdir();raw=output/'原件';display=output/'展示副本';raw.mkdir();display.mkdir();work=raw/'派生编码日志';work.mkdir()
    environment=runtime_environment();write_new(work/'actual-runtime-environment.json',environment)
    # Copy complete original PCM/header files unchanged, never synthesize sound.
    copied_engine=copy_exact(engine,raw/'runtime-mix-engine-export.wav');copied_canonical=copy_exact(canonical,raw/'runtime-mix.wav')
    encoding=encode_with_full_native_mix(work,display,frames,offsets,duration,Path(copied_canonical['path']),v['audio']['decoded_PCM'])
    source_frames=[dict(observation=i,native_original=pin(f),wall_offset_s=offsets[i],decoded_video_PTS_s=encoding['muxed_VFR']['decoded_PTS'][i]) for i,f in enumerate(frames)]
    selected=[]
    for s in samples:
        dest=raw/f'Jump{s["ordinal"]}-pose{s["frame"]}-UNSCALED-original.png';cp=copy_exact(frames[s['observation']],dest)
        selected.append(dict(**s,original_full_viewport_copy=cp))
    joined=[]
    for j in joins:
        pair=[]
        for key in ('before','after'):
            i=j[key];cp=copy_exact(frames[i],raw/f'JOIN-{j["kind"]}-{key}-UNSCALED-original.png');pair.append(dict(observation=i,original=pin(frames[i]),copy=cp))
        joined.append(dict(**j,pair=pair,actual_adjacent_callbacks=True,interpolation=False,retiming=False))
    boards=[]
    lgt=[s for s in samples if s['ordinal']==2]
    boards.append(make_board(display/'LGT-sixpose-UNSCALED-crops-v001.png',lgt,frames,r,3,True))
    boards.append(make_board(display/'LGT-sixpose-FULL-native-rows-v001.png',lgt,frames,r,1,False))
    boards.append(make_board(display/'None-LGT-Rejump-eighteen-source-crops-v001.png',samples,frames,r,6,True))
    for j in joins:
        boards.append(make_board(display/f'JOIN-{j["kind"]}-FULL-native-pair-v001.png',[dict(observation=j['before']),dict(observation=j['after'])],frames,r,2,False))
    for src,name in ((archive/'原件/runtime-report.json','runtime-report-readonly-copy.json'),(archive/'index.json','session-index-readonly-copy.json'),
                     (prereg,'Root-prereg-readonly-copy.json'),(independent,'independent-checker-result-readonly-copy.json'),
                     (archive/'原件/native-frame-pixels.jsonl','native-frame-pixels-readonly-copy.jsonl'),
                     (archive/'原件/native-async-write-summary.json','native-async-write-summary-readonly-copy.json'),
                     (archive/'原件/native-lossless-capture.json','native-lossless-capture-readonly-copy.json')):
        copy_exact(src,raw/name)
    copy_exact(frames[-1],raw/'native-final-UNSCALED-original.png')
    for row in bindings['all_native_frame_pins']:checked(row)
    for row in (bindings['native_report'],bindings['native_session'],bindings['root_prereg'],bindings['independent'],bindings['engine_original_WAV'],bindings['canonical_WAV']):checked(row)
    write_new(output/'README.md','所有实际MovieFrame保持在原nativearchive，并以逐帧SHA/time引用；本包原件为原幅样本、实际join和完整engine/canonical WAV副本。展示VFR完整包含所有PNG；video按首callback真实offset，audio从完整PCM原点0开始，AAC有损且保留原WAV。板图只裁剪或原幅拼接，标签在游戏矩形外，所有rect不重叠，无resize/配准搜索/重绘/变速/造帧。Root须保全原native archive与本新包E后才View/试听；当前View=false，美术、音色和正式20仍未验收。\n')
    index=dict(schema='Hero-Air6-production-presentation-source-version-status-v001',status='Prepared from actual independent PASS; E retention and Root View/listening pending',
               native_archive=archive.as_posix(),actual_facing=r['requested_facing'],actual_process_id=r['process_id'],native_bindings=bindings,
               preparer=pin(__file__),microsecond_VFR_helper=pin(ENCODER),all_frames=source_frames,all_native_frames_kept=True,
               runtime_environment=environment,
               complete_engine_WAV_copy=copied_engine,complete_canonical_WAV_copy=copied_canonical,presentation_encoding=encoding,
               original_full_viewport_samples=selected,adjacent_joins=joined,boards=boards,
               full_native_archive_originals_referenced_not_duplicated=True,source_archive_modified=False,new_original_PNG_resized_or_painted=False,
               View=False,visual_reviewed=False,audio_listened=False,FinalAccepted=False,formal20_complete=False,
               E_before_View_required=True,E_scope='Root must retain both existing complete native archive and this NEW presentation leaf before View; tool does not create E files.',
               additional_J_Shift_save='OPEN_not_run',files=[pin(f) for f in sorted(output.rglob('*')) if f.is_file()])
    write_new(output/'来源-版本-状态索引.json',index)
    print(json.dumps(dict(output=output.as_posix(),native_frames=len(frames),decoded_frames=encoding['muxed_VFR']['decoded_frames'],View=False,E_created=False,FinalAccepted=False),ensure_ascii=False))


if __name__=='__main__':main()
