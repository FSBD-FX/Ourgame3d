"""Preserve native wholes, exact unscaled crops and true wall-timed silent video."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess
from PIL import Image

ROOT=Path('F:/Ourgame')
DEFAULT_ARCHIVE='过程图稿与视频/2026-10-16_钟盔军剑三段真实连击试装_v001'
FFMPEG=ROOT/'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

def io_path(path):
    path=Path(path)
    return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' else path
def load(path):return json.loads(io_path(path).read_text(encoding='utf-8-sig'))
def desc(path):
    data=io_path(path).read_bytes();return {'path':path.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def new(path,value):
    with io_path(path).open('x',encoding='utf-8') as handle:
        handle.write(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--snapshot',required=True)
    parser.add_argument('--archive',default=DEFAULT_ARCHIVE);args=parser.parse_args()
    archive=(ROOT/args.archive).resolve();original=archive/'原件';presentation=archive/'展示副本'
    assert archive.is_relative_to((ROOT/'过程图稿与视频').resolve())
    snapshot=(ROOT/args.snapshot).resolve()
    assert snapshot.is_relative_to((ROOT/'source-assets/production/backups').resolve())
    report=load(original/'runtime-report.json');index=load(archive/'index.json')
    assert report['passed'] and report['native_async_capture_writes_flushed'] and report['primary3_armor_trial']
    rows=report['observations'];frames=sorted(original.glob('MovieFrame*.png'))
    assert len(rows)==len(frames) and len(frames)>160 and len(list(original.glob('*.png')))==len(frames)+1
    verified=load(original/'sword-primary3-fit-runtime-verification-v001.json')
    assert verified['passed'] and verified['kernel_phase_sampling_exact'] and verified['full141_snapshot_verified']
    assert len(verified['transitions'])==4 and verified['actual_buffer_pending_and_exact_end_start_no_ready_bridge']
    assert load(original/'visible-ready-primary3-head-gate-v001.json')['passed']
    manifest=load(snapshot/'compiled-source-manifest.json');mismatches=[]
    actual=load(ROOT/manifest['automation_report'])
    assert actual['succeeded']==141 and all(actual[k]==0 for k in ('succeededWithWarnings','failed','notRun','inProcess'))
    assert len(actual['tests'])==len({t['fullTestPath'] for t in actual['tests']})==141
    assert all(t['state']=='Success' and t['errors']==t['warnings']==0 for t in actual['tests'])
    for row in manifest['files']:
        for endpoint in (ROOT,snapshot):
            path=endpoint/row['path'];value=desc(path)
            if value['bytes']!=row['bytes'] or value['sha256']!=row['sha256']:mismatches.append(path.as_posix())
    assert not mismatches,mismatches
    current_sources={p.relative_to(ROOT).as_posix().replace('/','\\') for p in (ROOT/'UnrealGame/Source/CodexDungeon').rglob('*') if p.is_file()}
    captured_sources={path.replace('/','\\') for path in index['source_sha256_at_capture']}
    assert current_sources==captured_sources
    for path,expected in index['source_sha256_at_capture'].items():assert desc(ROOT/path)['sha256'].upper()==expected
    assert desc(ROOT/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll')['sha256'].upper()==index['module_sha256']
    production={p.relative_to(ROOT).as_posix() for p in (ROOT/'UnrealGame/Content/Production').rglob('*') if p.is_file()}
    assert production=={r['path'] for r in manifest['files'] if r['path'].startswith('UnrealGame/Content/Production/')} and len(production)==1085
    new(original/'compiled-source-binding-audit-v001.json',{'snapshot':snapshot.as_posix(),'snapshot_files':len(manifest['files']),
        'endpoint_checks':2*len(manifest['files']),'mismatches':0,'captured_Source_and_DLL_unchanged':True,
        'exact_Production_package_set':1085,'strict_actual_automation_success':141,'snapshot_manifest':desc(snapshot/'compiled-source-manifest.json')})

    chosen={}
    for i,d in enumerate(rows):
        if d['supported']:chosen.setdefault((d['facing'],d['clip'],d['frame']),(i,d))
    assert len(chosen)==44
    selected=[]
    def preserve(i,d,stem,extra):
        source=frames[i];target=presentation/f'{stem}-{source.name}'
        assert not target.exists();shutil.copy2(source,target);assert desc(source)['sha256']==desc(target)['sha256']
        ratio=d['canvas_size']/512.
        footx=d['grip_screen'][0]+d['facing']*(256-d['grip'][0])*ratio
        footy=d['grip_screen'][1]+(464-d['grip'][1])*ratio
        x=max(0,min(1280-240,round(footx)-120));y=max(0,min(720-150,round(footy)-130))
        crop=presentation/f'crop-{stem}-{source.name}';assert not crop.exists()
        with Image.open(source) as image:
            assert image.size==(1280,720)
            original_pixels=image.crop((x,y,x+240,y+150));original_pixels.save(crop)
            with Image.open(crop) as saved:assert saved.size==(240,150) and saved.tobytes()==original_pixels.tobytes()
        value={'facing':d['facing'],'clip':d['clip'],'frame':d['frame'],'observation_index':i,'wall_offset_s':d['wall_offset_s'],
            'source':desc(source),'presentation_whole':desc(target),'unscaled_crop':desc(crop),'crop_rect_px':[x,y,240,150],
            'crop_resampled':False,'grip':d['grip'],'weapon_angle':d['weapon_angle'],'root_projected_screen':[footx,footy],
            'actually_viewed':False}
        value.update(extra);return value
    for j,(key,(i,d)) in enumerate(sorted(chosen.items())):
        selected.append(preserve(i,d,f'selected-{j:02d}',{'selection_kind':'one_per_actual_phase_and_facing'}))
    boundary=[]
    for j,transition in enumerate(verified['transitions']):
        left,right=transition['from_observation'],transition['to_observation']
        assert right==left+1
        for k,(i,role) in enumerate(((left-1,'pre_neighbor'),(left,'from_last'),(right,'to_first'),(right+1,'post_neighbor'))):
            assert 0<=i<len(rows) and rows[i]['supported']
            assert rows[i]['facing']==transition['facing']
            boundary.append(preserve(i,rows[i],f'boundary-{j:02d}-{k:02d}',{'selection_kind':'actual_contiguous_transition',
                'transition':transition,'boundary_role':role}))
    assert len(boundary)==16
    new(original/'selected-frame-source-map-v001.json',{'frames':selected,'transition_frames':boundary,
        'selected_phase_wholes':44,'selected_primary3_both_facing_six':12,'contiguous_boundary_wholes':16,
        'selection_not_review':True,'formal_complete_units':0})

    timing=report['capture_timing'];times=timing['frame_wall_offsets_s'];duration=timing['requested_video_wall_duration_s']
    assert len(times)==len(frames) and 6.6<=duration<8
    concat=[]
    for i,path in enumerate(frames):
        start=0. if i==0 else times[i];end=times[i+1] if i+1<len(times) else duration
        assert end>start;concat.extend(["file '"+path.as_posix()+"'",f'duration {end-start:.12f}'])
    concat.append("file '"+frames[-1].as_posix()+"'")
    listing=original/'wall-timed-native-frames-v001.txt';new(listing,'\n'.join(concat)+'\n')
    video=presentation/'fairytale-sword-primary3-fit-silent.mp4';assert not video.exists()
    argv=[str(FFMPEG),'-hide_banner','-loglevel','info','-f','concat','-safe','0','-i',str(listing),'-vf','fps=30','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]
    encoded=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',errors='replace')
    new(original/'video-encode-v001.log',encoded.stdout+encoded.stderr);assert encoded.returncode==0
    decode=[str(FFMPEG),'-hide_banner','-v','error','-i',str(video),'-an','-f','null','NUL']
    decoded=subprocess.run(decode,capture_output=True,text=True,encoding='utf-8',errors='replace')
    new(original/'video-full-decode-v001.log',decoded.stdout+decoded.stderr);assert decoded.returncode==0 and not decoded.stderr.strip()
    streams=[str(FFMPEG),'-hide_banner','-i',str(video),'-map','0:v:0','-f','null','NUL']
    inspected=subprocess.run(streams,capture_output=True,text=True,encoding='utf-8',errors='replace')
    stream_text=inspected.stdout+inspected.stderr;new(original/'video-stream-inspection-v001.log',stream_text)
    assert inspected.returncode==0 and re.search(r'(?im)^\s*Stream\s+#\d+:\d+[^\r\n]*:\s*Video\s*:',stream_text)
    assert not re.search(r'(?im)^\s*Stream\s+#\d+:\d+[^\r\n]*:\s*Audio\s*:',stream_text)
    new(original/'video-presentation-receipt-v001.json',{'source_native_movies':len(frames),'native_original_including_prewarm':len(frames)+1,
        'capture_wall_duration_s':duration,'presentation_policy':'nativewalltimed concat, first frame held from0 untilnext; lasttail repeated, CFR30 encode quantizes display only; no gameclock/source retime',
        'encode_argv':argv,'encode_exit':encoded.returncode,'full_decode_argv':decode,'full_decode_exit':decoded.returncode,
        'stream_inspection_argv':streams,'stream_inspection_exit':inspected.returncode,'audio_streams':0,
        'video':desc(video),'audio_recorded':False,'audio_substituted':False,'motion_accepted':False,'formal_complete_units':0})
    toolcopy=original/'tool-postprocess-sword-primary3-fit-v001.py';assert not toolcopy.exists();shutil.copy2(Path(__file__),toolcopy)
    new(archive/'README.md','Native175第三段身体与176/177/178甲，真实六次J串接Stage0→1→2，两向各六相。1085包/Source/DLL绑定实际full141冻结，72px/UIoff/.50独立剑，原native像素/排他FIFO/flush和固定暖色信号门保留。44组选相及四处连续边界的16帧、原墙钟无声视频只供审阅；未接受握柄、足锁、穿插、命中、完整动作/装备或音频。标准源预览600ms不等真实Stage2 660ms，本片未修改游戏时钟。\n')
    new(archive/'source-version-status-index.json',{'status':'actualnative_sixJ_three_stage_kernel_GREEN_visual_review_pending',
        'snapshot':snapshot.as_posix(),'selected_manifest':desc(original/'selected-frame-source-map-v001.json'),
        'video_receipt':desc(original/'video-presentation-receipt-v001.json'),'formal_complete_units':0})
    print(json.dumps({'archive':archive.as_posix(),'snapshot_checks':2*len(manifest['files']),
        'selected_whole':44,'unscaled_phase_crops':44,'boundary_whole':16,'unscaled_boundary_crops':16,
        'video':desc(video),'capture_duration':duration,'visual_review_pending':True},ensure_ascii=False))

if __name__=='__main__':main()
