"""NEW landing-priority native AV presentation. No UE, View, E, or asset generation.

The retained VFR/full PCM/AAC/decode functions below are exact source copies.
Only the final explicit landing checker CLI is permitted to validate native input.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, struct, subprocess, sys
import imageio_ffmpeg
import PIL
from PIL import Image, ImageDraw, ImageChops
sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame')
HERE=Path(__file__).resolve().parent
ENCODER=ROOT/'source-assets/production/fairytale-guard-v001/stomp-native-media-candidate-v001/tooling/retained-microsecond-VFR-v001.py'
ENCODER_SHA='6554573c99d4a2905200433718d0b56074aac6893b97c9436048db78c6cadc78'
RUNTIME_SCHEMA='hero-landing-priority-native-observer-v001'
NATIVE_SCHEMA='hero-landing-priority-independent-native-v001'
FOUR_SCHEMA='hero-landing-priority-independent-four-v001'

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


def rectangles_nonoverlap(rects):
    for i,a in enumerate(rects):
        need(a[2]>a[0] and a[3]>a[1],'Empty board rectangle')
        for b in rects[:i]:need(a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1],'Board image rectangles overlap')


def resolve_pinned(row,base=ROOT):
    need(isinstance(row,dict) and type(row.get('bytes')) is int,'Complete actual file pin required')
    p=Path(row['path']);p=(p if p.is_absolute() else Path(base)/p).resolve();actual=pin(p)
    need((actual['bytes'],actual['sha256'])==(row['bytes'],row['sha256']),'Actual pinned bytes/SHA changed: '+str(p))
    return p


def same_pin(a,b):
    absolute=lambda row:(Path(row['path']) if Path(row['path']).is_absolute() else ROOT/row['path']).resolve()
    return (absolute(a)==absolute(b)
            and (a['bytes'],a['sha256'])==(b['bytes'],b['sha256']))


def exact_json_equal(a,b):
    return (json.dumps(a,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
            ==json.dumps(b,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False))


def retained_case(value,actual):
    if value.get('schema')==NATIVE_SCHEMA:
        return value,dict(kind='single_native',selected_index=None)
    need(value.get('schema')==FOUR_SCHEMA and value.get('passed') is True
         and value.get('four_fresh_processes') is True and len(value.get('cases',[]))==4,
         'Retained independent input must be one native result or actual four-case result')
    cases=value['cases'];need({(x['requested_action'],x['requested_facing']) for x in cases}
        =={('J',-1),('J',1),('Shift',-1),('Shift',1)} and len({x['process_id'] for x in cases})==4
        and len({x['run'] for x in cases})==4,'Retained four-case identities are not distinct')
    rows=[(i,x) for i,x in enumerate(cases) if same_pin(x['root_prereg_pin'],actual['root_prereg_pin'])]
    need(len(rows)==1,'Selected actual prereg absent/duplicate in retained four-case result')
    i,selected=rows[0]
    return selected,dict(kind='actual_four_case_unchanged_branch',selected_index=i,
                         other_three_cases_reexecuted_by_this_tool=False)


def verify_current_checker(checker,freeze,prereg):
    binding=read(HERE/'checker-binding-v001.json')
    need(binding['status']=='BOUND_FINAL_FROZEN_LANDING_CHECKER'
         and binding.get('checker_pin') and binding.get('checker_freeze_pin'),
         'Final new landing checker has not been frozen/bound; no native claim is possible')
    need(same_pin(pin(checker),binding['checker_pin']) and same_pin(pin(freeze),binding['checker_freeze_pin']),
         'Explicit checker/freeze differs from final frozen landing binding')
    for row in (binding['checker_pin'],binding['checker_freeze_pin']):resolve_pinned(row)
    cf=read(freeze);need(cf.get('FinalAccepted') is False,'Checker freeze is not content acceptance')
    members=cf.get('members');need(isinstance(members,list) and members,'Frozen current checker members required')
    paths=[resolve_pinned(row) for row in members]
    need(Path(checker).resolve() in paths,'Explicit current checker absent from its freeze')
    need(same_pin(prereg['checker_freeze_pin'],pin(freeze)),'Root prereg binds a different checker freeze')
    return binding


def official_recheck(archive,prereg,independent,checker,freeze,capture):
    p=read(prereg)
    need(p.get('schema')=='hero-landing-priority-root-prereg-v001' and p.get('RootApproved') is True
         and p.get('is_template') is False,'Actual current landing Root prereg required')
    verify_current_checker(checker,freeze,p)
    command=[sys.executable,'-B','-X','utf8',str(checker),'--archive',str(archive),'--prereg',str(prereg)]
    proc=subprocess.run(command,cwd=Path(checker).parent,capture_output=True,text=True,encoding='utf-8')
    capture.update(command=command,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
    need(proc.returncode==0,'Current official landing checker rejected native case; original evidence retained')
    actual=json.loads(proc.stdout)
    need(actual.get('schema')==NATIVE_SCHEMA and actual.get('passed') is True,'Official result is not a current native PASS')
    selected,selection=retained_case(read(independent),actual)
    need(exact_json_equal(actual,selected),'Fresh official independent dict differs from the retained selected dict')
    need(same_pin(actual['checker_freeze_pin'],pin(freeze)) and same_pin(actual['root_prereg_pin'],pin(prereg)),
         'Official output binds another actual prereg/checker')
    return p,actual,selection


def verify_timeline(report,movie):
    need(report.get('schema')==RUNTIME_SCHEMA,'Wrong actual landing runtime schema')
    observations=report['observations'];timing=report['capture_timing'];offsets=timing['frame_wall_offsets_s']
    duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s']
    need(len(observations)==len(movie)==len(offsets)>0,'Actual callback/PNG/timestamp count differs')
    need(all(type(x) in (int,float) and math.isfinite(x) for x in offsets+[duration]),'Nonfinite native capture clock')
    need(duration>offsets[-1]>=offsets[0]>=0 and all(b>a for a,b in zip(offsets,offsets[1:])),
         'Actual audio-origin timeline is not strictly increasing')
    need(all(o['completed_callback'] is True and o['wall_offset_s']==offsets[i]
             for i,o in enumerate(observations)),'PNG timeline does not belong to completed actual callbacks')
    names=[m['file'] for m in movie]
    need(len(set(names))==len(names) and all(Path(n).name==n and '/' not in n and '\\' not in n for n in names),
         'Actual native PNG filename membership differs')
    return offsets,duration


def actual_stack(observation,kind):
    stack=observation['rendered_player_stack'];old=observation['old_draw']
    need(isinstance(stack,list) and stack and stack==old['actual_stack'],'Actual submitted player stack differs')
    if kind=='Air':
        draw=observation['new_air_draw']
        need(draw['drawn'] is True and draw['slot_count']==9 and draw['actual_stack']==stack,'Actual Air9 stack required')
    elif kind=='Shift':
        draw=observation['dodge_draw']
        need(draw['drawn'] is True and draw['slot_count']==9 and draw['resident_count']==33
             and draw['actual_stack']==stack and old['clip']=='sword_dodge','Actual Dodge9/33 stack required')
    elif kind=='J':
        need(old['clip']=='sword_primary_1' and len(stack)==8,'Actual J legacy8 stack required')
    elif kind=='Ready':
        need(old['clip']=='sword_ready_idle' and len(stack)==7,'Actual Ready7 stack required')
    else:need(kind=='Observed_other','Unknown presentation classification')
    return list(stack)


def observed_kind(observation,action):
    if observation['new_air_draw']['drawn'] is True:return 'Air'
    if observation['dodge_draw']['drawn'] is True:return 'Shift'
    if observation['action']['active'] is True:return action
    if observation['old_draw']['clip']=='sword_ready_idle':return 'Ready'
    return 'Observed_other'


def pose_frame(observation,kind):
    if kind=='Air':return observation['physical_visual_key']
    if kind=='Shift':return observation['dodge_draw']['frame']
    return observation['old_draw']['frame']


def choose_samples(report,independent,movie):
    obs=report['observations'];action=report['requested_action'];side=report['requested_facing']
    need(action in ('J','Shift') and type(side) is int and side in (-1,1),'Wrong actual action/facing case')
    witnesses=independent['source_pixels']['source_pixel_witnesses'];samples=[]
    for kind,count in (('Air',5),(action,6 if action=='J' else 4)):
        for frame in range(count):
            rows=[w for w in witnesses if w['kind']==kind and w['frame']==frame]
            need(len(rows)==1,'Actual optical witness for pose missing/duplicate')
            w=rows[0];i=w['observation'];need(type(i) is int and 0<=i<len(obs),'Witness observation index invalid')
            need(w['file']==movie[i]['file'] and pose_frame(obs[i],kind)==frame,'Witness does not map to its actual PNG/pose')
            if kind==action:need(obs[i]['action']['active'] is True,'Action witness does not show actual active action')
            samples.append(dict(kind=kind,frame=frame,observation=i,witness=w,actual_submitted_stack=actual_stack(obs[i],kind)))
    for i,label in ((report['ready_callback_index'],'initial_Ready'),(len(obs)-1,'final_Ready')):
        rows=[w for w in witnesses if w['kind']=='Ready' and w['observation']==i]
        need(len(rows)==1 and rows[0]['file']==movie[i]['file'],'Actual initial/final Ready witness missing')
        samples.append(dict(kind='Ready',label=label,frame=pose_frame(obs[i],'Ready'),observation=i,
                            witness=rows[0],actual_submitted_stack=actual_stack(obs[i],'Ready')))
    first=report['first_action_callback_index'];need(type(first) is int and 0<first<len(obs),'First actual action index invalid')
    active=[i for i,o in enumerate(obs) if o['action']['active'] is True]
    need(active and active[0]==first,'First active callback cannot be borrowed/skipped')
    token=report['landing_callback_index'];need(type(token) is int and 0<=token<first,'Actual causal token index invalid')
    need(obs[token]['physical_visual_key']==4,'Actual causal token does not map to its Land4 pose')
    last=active[-1];need(last+1<len(obs),'Actual action completion has no later callback')
    ready=next((i for i in range(last+1,len(obs)) if observed_kind(obs[i],action)=='Ready'),None)
    need(ready is not None,'Actual action completion has no later observed Ready callback')
    def boundary(label,before,after,role):
        left,right=observed_kind(obs[before],action),observed_kind(obs[after],action)
        actual_stack(obs[before],left);actual_stack(obs[after],right)
        return dict(kind=label,before=before,after=after,before_kind=left,after_kind=right,
                    before_pose=pose_frame(obs[before],left),after_pose=pose_frame(obs[after],right),role=role,
                    actual_adjacent_callbacks=after==before+1,intervening_callback_indices=list(range(before+1,after)),
                    intervening_callback_count=after-before-1,wall_interval_s=obs[after]['wall_offset_s']-obs[before]['wall_offset_s'],
                    simulation_interval_s=obs[after]['sim']-obs[before]['sim'],endpoint_pair_only=True,interpolation=False)
    joins=[boundary(f'previous_callback_to_first_{action}',first-1,first,'actual_adjacent_start_boundary'),
           boundary(f'causal_Land4_token_to_first_{action}',token,first,'causal_token_endpoints_gap_explicit'),
           boundary(f'last_{action}_to_first_Ready',last,ready,'action_ready_endpoints_gap_explicit')]
    if ready>last+1:
        joins.extend([boundary(f'last_{action}_to_next_callback',last,last+1,'actual_adjacent_end_boundary'),
                      boundary('previous_callback_to_first_Ready',ready-1,ready,'actual_adjacent_ready_boundary')])
    return samples,joins


def crop_ground(observation):
    for key in ('new_air_draw','dodge_draw'):
        draw=observation[key]
        if draw['drawn'] is True:return list(draw['context_ground']),key+'.context_ground'
    # Presentation window only: this is derived from native observed ground/camera,
    # never claimed as a native legacy floatquad or fitted from pixels/body metadata.
    f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
    ground=observation['ground'];camera=observation['camera_ground']
    return [f32(640+(ground[0]-camera[0])*f32(.65)),f32(490-ground[1]*f32(.38))], 'observed_ground_camera_fixed_projection_for_crop_only'


def make_landing_board(path,samples,frames,report,columns,cropped,boundary=None):
    width,height=(256,320) if cropped else (1280,720);gap=12;label=44
    cell_w,cell_h=width+gap,height+label+gap;rows=math.ceil(len(samples)/columns)
    need(samples and columns>0,'Board requires actual samples')
    board=Image.new('RGB',(columns*cell_w,rows*cell_h),(26,29,34));draw=ImageDraw.Draw(board);rects=[];details=[]
    for k,s in enumerate(samples):
        i=s['observation'];o=report['observations'][i];x=(k%columns)*cell_w;y=(k//columns)*cell_h+label
        with Image.open(frames[i]) as im:
            need(im.size==(1280,720),'Original unscaled native viewport required')
            if cropped:
                ground,origin=crop_ground(o);cx,cy=(int(round(v)) for v in ground)
                left=max(0,min(1280-width,cx-width//2));top=max(0,min(720-height,cy-240));crop=[left,top,left+width,top+height]
            else:crop=[0,0,1280,720];origin='full_viewport'
            rect=[x,y,x+width,y+height];rects.append(rect);board.paste(im.crop(crop).convert('RGB'),(x,y))
        relation=('adjacent callbacks' if boundary['actual_adjacent_callbacks'] else f'ENDPOINTS: {boundary["intervening_callback_count"]} intervening') if boundary else 'pose witness'
        text=f'{s["kind"]} pose{s["frame"]} | obs{i} | stack{len(o["rendered_player_stack"])}\nwall{o["wall_offset_s"]:.6f} sim{o["sim"]:.6f}\n{relation}'
        draw.multiline_text(((k%columns)*cell_w+6,(k//columns)*cell_h+4),text,fill='white',spacing=2)
        details.append(dict(observation=i,kind=s['kind'],frame=s['frame'],source=pin(frames[i]),source_crop=crop,
                            board_rect=rect,crop_anchor=origin,actual_submitted_stack=list(o['rendered_player_stack']),
                            source_pixels_resized=False,label_inside_game_rect=False))
    rectangles_nonoverlap(rects)
    with Path(path).open('xb') as f:board.save(f,format='PNG')
    with Image.open(path) as rendered:
        for row in details:
            with Image.open(row['source']['path']) as source:
                need(ImageChops.difference(rendered.crop(row['board_rect']),source.crop(row['source_crop']).convert('RGB')).getbbox() is None,
                     'Board differs from exact source crop; resizing/labels/painting forbidden')
    return dict(file=pin(path),details=details,boundary=boundary,rectangles_nonoverlapping=True,exact_original_crop_pixels_redecoded_equal=True,visual_reviewed=False)


def actual_inputs(archive,prereg,independent,checker,freeze,capture):
    p,v,selection=official_recheck(archive,prereg,independent,checker,freeze,capture)
    original=archive/'原件';report=read(original/'runtime-report.json')
    rows=[json.loads(x) for x in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if x]
    movie=[x for x in rows if x['file'].startswith('MovieFrame')];offsets,duration=verify_timeline(report,movie)
    need(report['requested_action']==v['requested_action']==p['requested_action']
         and report['requested_facing']==v['requested_facing']==p['requested_facing'],'Actual requested case differs')
    frames=[original/x['file'] for x in movie]
    engine=resolve_pinned(v['audio']['engine_original']);canonical=resolve_pinned(v['audio']['canonical'])
    need(engine==(original/'audio-v001/runtime-mix-engine-export.wav').resolve()
         and canonical==(original/'audio-v001/runtime-mix.wav').resolve(),'Full original native mix paths differ')
    samples,joins=choose_samples(report,v,movie)
    bindings=dict(native_report=pin(original/'runtime-report.json'),native_session=pin(archive/'index.json'),root_prereg=pin(prereg),
                  retained_independent=pin(independent),retained_selection=selection,actual_checker=pin(checker),checker_freeze=pin(freeze),
                  official_landing_CLI_rerun_passed=True,exact_selected_independent_dict_equal=True,
                  compiled_manifest=p['compiled_manifest_pin'],source_candidate_freeze=p['source_candidate_freeze_pin'],
                  source_admission=p['source_admission_pin'],source_repair_admission=p['source_repair_admission_pin'],
                  engine_original_WAV=pin(engine),canonical_WAV=pin(canonical),all_native_frame_pins=[pin(f) for f in frames])
    return report,v,frames,offsets,duration,engine,canonical,samples,joins,bindings


def prepare(a,output,raw,display,work,capture):
    paths=[Path(x).resolve() for x in (a.archive,a.prereg,a.independent,a.checker,a.checkerfreeze)]
    archive,prereg,independent,checker,freeze=paths
    r,v,frames,offsets,duration,engine,canonical,samples,joins,bindings=actual_inputs(*paths,capture)
    write_new(work/'official-current-landing-checker-rerun.json',capture)
    write_new(work/'fresh-official-independent-native-dict.json',v)
    environment=runtime_environment();write_new(work/'actual-runtime-environment.json',environment)
    copied_engine=copy_exact(engine,raw/'runtime-mix-engine-export.wav');copied_canonical=copy_exact(canonical,raw/'runtime-mix.wav')
    encoding=encode_with_full_native_mix(work,display,frames,offsets,duration,Path(copied_canonical['path']),v['audio']['decoded_PCM'])
    selected=[]
    for sample in samples:
        dest=raw/f'{sample["kind"]}-pose{sample["frame"]}-obs{sample["observation"]}-UNSCALED-original.png'
        selected.append(dict(**sample,original_full_viewport_copy=copy_exact(frames[sample['observation']],dest)))
    joined=[];boards=[]
    for join in joins:
        pair=[];pair_samples=[]
        for key in ('before','after'):
            i=join[key];o=r['observations'][i]
            kind=observed_kind(o,r['requested_action'])
            pair_samples.append(dict(observation=i,kind=kind,frame=pose_frame(o,kind)))
            copied=copy_exact(frames[i],raw/f'JOIN-{join["kind"]}-{key}-obs{i}-UNSCALED-original.png')
            pair.append(dict(observation=i,native_original=pin(frames[i]),copy=copied,actual_submitted_stack=actual_stack(o,kind)))
        joined.append(dict(**join,pair=pair))
        boards.append(make_landing_board(display/f'JOIN-{join["kind"]}-FULL-native-endpoints-v001.png',pair_samples,frames,r,2,False,join))
        boards.append(make_landing_board(display/f'JOIN-{join["kind"]}-UNSCALED-crops-v001.png',pair_samples,frames,r,2,True,join))
    action_samples=[s for s in samples if s['kind']==r['requested_action']]
    air_samples=[s for s in samples if s['kind']=='Air']
    boards.append(make_landing_board(display/'action-allposes-FULL-native-rows-v001.png',action_samples,frames,r,1,False))
    boards.append(make_landing_board(display/'action-allposes-UNSCALED-crops-v001.png',action_samples,frames,r,3 if r['requested_action']=='J' else 2,True))
    boards.append(make_landing_board(display/'Air0-to-Land4-UNSCALED-crops-v001.png',air_samples,frames,r,3,True))
    boards.append(make_landing_board(display/'Air-Land-action-Ready-all-UNSCALED-crops-v001.png',samples,frames,r,5,True))
    for src,name in ((archive/'原件/runtime-report.json','runtime-report-readonly-copy.json'),(archive/'index.json','session-index-readonly-copy.json'),
                     (archive/'launch-receipt-v001.json','launch-receipt-readonly-copy.json'),(prereg,'Root-prereg-readonly-copy.json'),
                     (independent,'retained-independent-readonly-copy.json'),(freeze,'current-checker-freeze-readonly-copy.json'),
                     (checker,'current-checker-script-readonly-copy.py'),(HERE/'checker-binding-v001.json','final-checker-binding-readonly-copy.json'),
                     (archive/'原件/native-frame-pixels.jsonl','native-frame-pixels-readonly-copy.jsonl'),
                     (archive/'原件/native-async-write-summary.json','native-async-write-summary-readonly-copy.json'),
                     (archive/'原件/native-lossless-capture.json','native-lossless-capture-readonly-copy.json')):copy_exact(src,raw/name)
    copy_exact(frames[-1],raw/'native-final-UNSCALED-original.png')
    for row in bindings['all_native_frame_pins']:resolve_pinned(row)
    for key in ('native_report','native_session','root_prereg','retained_independent','actual_checker','checker_freeze','engine_original_WAV','canonical_WAV'):resolve_pinned(bindings[key])
    source_frames=[dict(observation=i,native_original=pin(frame),wall_offset_s=offsets[i],decoded_video_PTS_s=encoding['muxed_VFR']['decoded_PTS'][i]) for i,frame in enumerate(frames)]
    write_new(output/'README.md','本包由最终冻结的landing checker官方CLI重新完整验证并与retained independent选定dict精确比较后准备。每个真实PNG按callback wall offset微秒VFR保留；完整原engine/canonical PCM另存，AAC完整呈现且有损，无trim/变速/造帧。保留原幅关键帧及无缩放裁剪板，标签在游戏矩形外；真实相邻边界按callback呈现，Land4因果token及action→Ready端点如有间隔，板与索引明确标注intervening callbacks，绝不假称相邻。legacy body_texture不作为实际层栈来源，层栈来自actual_stack/observations。编码函数与历史Air管线逐字相同，部分内部文件名保留历史标签，实际case以索引为准。全帧原PNG引用原native archive，本媒体目录不自称全原件自包含，也不宣称E已保全。Root须保全原archive与本包E后才View/试听；当前View=false/听感未审/最终未验收。\n')
    index=dict(schema='hero-landing-priority-presentation-source-version-status-v001',status='Actual selected native case verified; E retention and Root visual/audio review pending',
               actual_action=r['requested_action'],actual_facing=r['requested_facing'],actual_process_id=r['process_id'],native_archive=archive.as_posix(),
               native_bindings=bindings,preparer=pin(__file__),retained_codec_functions=pin(HERE/'retained-codec-functions-v001.json'),microsecond_VFR_helper=pin(ENCODER),
               all_frames=source_frames,all_native_frames_kept=True,complete_engine_WAV_copy=copied_engine,complete_canonical_WAV_copy=copied_canonical,
               presentation_encoding=encoding,runtime_environment=environment,original_full_viewport_samples=selected,callback_boundaries=joined,boards=boards,
               full_native_archive_originals_referenced_not_duplicated=True,legacy_body_texture_used_as_stack=False,source_archive_modified=False,
               View=False,visual_reviewed=False,audio_listened=False,FinalAccepted=False,E_before_View_required=True,
               real_save_restore='OPEN_not_run',files=[pin(f) for f in sorted(output.rglob('*')) if f.is_file()])
    write_new(output/'来源-版本-状态索引.json',index)
    return dict(output=output.as_posix(),action=r['requested_action'],facing=r['requested_facing'],native_frames=len(frames),
                decoded_frames=encoding['muxed_VFR']['decoded_frames'],actual_adjacent_pairs=sum(j['actual_adjacent_callbacks'] for j in joined),
                nonadjacent_endpoint_pairs=sum(not j['actual_adjacent_callbacks'] for j in joined),View=False,E_created=False,FinalAccepted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','prereg','independent','checker','checkerfreeze'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--output',required=True);a=parser.parse_args()
    output=Path(a.output);need(output.is_absolute(),'Absolute NEW F media leaf required');output=output.resolve()
    archive=Path(a.archive).resolve();need(output.parent==ROOT/'过程图稿与视频' and not output.exists() and output!=archive,'NEW direct F media leaf required')
    output.mkdir();raw=output/'原件';display=output/'展示副本';raw.mkdir();display.mkdir();work=raw/'派生编码日志';work.mkdir();capture={}
    try:
        result=prepare(a,output,raw,display,work,capture)
    except Exception as exc:
        failure=dict(schema='hero-landing-presentation-failure-v001',passed=False,error=str(exc),official_checker_process=capture,
                     partial_output_retained=True,source_archive_modified=False,View=False,E_created=False,FinalAccepted=False)
        write_new(output/'FAILED-preserved-v001.json',failure);print(json.dumps(failure,ensure_ascii=False));return 3
    print(json.dumps(result,ensure_ascii=False));return 0


if __name__=='__main__':raise SystemExit(main())

