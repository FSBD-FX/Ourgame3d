"""Preserve whole native frames, unscaled crops and wall-timed silent presentation."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess
from PIL import Image

R=Path('F:/Ourgame')
A=R/'过程图稿与视频/2026-10-16_钟盔军剑第二段真实连击试装_v004'
O=A/'原件'; P=A/'展示副本'
p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);args=p.parse_args()
S=(R/args.snapshot).resolve();assert S.is_relative_to((R/'source-assets/production/backups').resolve())
F=R/'tools/runtime/asset-gen/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
    b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def new(p,v):
    assert not p.exists(),p
    p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report=load(O/'runtime-report.json');index=load(A/'index.json')
assert report['passed'] and report['native_async_capture_writes_flushed']
rows=report['observations'];frames=sorted(O.glob('MovieFrame*.png'))
assert len(rows)==len(frames) and len(frames)>120 and len(list(O.glob('*.png')))==len(frames)+1
assert load(O/'sword-primary2-fit-runtime-verification-v004.json')['kernel_phase_sampling_exact']
assert load(O/'visible-ready-primary2-head-gate-v001.json')['passed']
manifest=load(S/'compiled-source-manifest.json');mismatches=[]
for row in manifest['files']:
    # Audit the immutable source/DLL/asset capture endpoints. Presentation tools
    # are separately versioned and may legitimately be created after this freeze.
    for endpoint in (R,S):
        p=endpoint/row['path'];d=desc(p)
        if d['bytes']!=row['bytes'] or d['sha256']!=row['sha256']:mismatches.append(p.as_posix())
assert not mismatches,mismatches
for path,sha in index['source_sha256_at_capture'].items():assert desc(R/path)['sha256'].upper()==sha
assert desc(R/'UnrealGame/Binaries/Win64/UnrealEditor-CodexDungeon.dll')['sha256'].upper()==index['module_sha256']
new(O/'compiled-source-binding-audit-v001.json',{'snapshot':S.as_posix(),'snapshot_files':len(manifest['files']),'endpoint_checks':2*len(manifest['files']),'mismatches':0,'captured_Source_and_DLL_unchanged':True,'snapshot_manifest':desc(S/'compiled-source-manifest.json')})

chosen={}
for i,d in enumerate(rows):
    if d['supported']:
        chosen.setdefault((d['facing'],d['clip'],d['frame']),(i,d))
assert len(chosen)==32
selected=[]
for j,(key,(i,d)) in enumerate(sorted(chosen.items())):
    source=frames[i];target=P/f'selected-{j:02d}-{source.name}'
    assert not target.exists();shutil.copy2(source,target);assert desc(source)['sha256']==desc(target)['sha256']
    ratio=d['canvas_size']/512.
    footx=d['grip_screen'][0]+d['facing']*(256-d['grip'][0])*ratio
    footy=d['grip_screen'][1]+(464-d['grip'][1])*ratio
    x=max(0,min(1280-240,round(footx)-120));y=max(0,min(720-150,round(footy)-130))
    crop=P/f'crop-{j:02d}-{source.name}';assert not crop.exists()
    with Image.open(source) as image:
        assert image.size==(1280,720)
        image.crop((x,y,x+240,y+150)).save(crop)
    selected.append({'facing':key[0],'clip':key[1],'frame':key[2],'observation_index':i,'wall_offset_s':d['wall_offset_s'],'source':desc(source),'presentation_whole':desc(target),'unscaled_crop':desc(crop),'crop_rect_px':[x,y,240,150],'crop_resampled':False,'grip':d['grip'],'weapon_angle':d['weapon_angle'],'root_projected_screen':[footx,footy],'actually_viewed':False})
new(O/'selected-frame-source-map-v001.json',{'frames':selected,'selection_not_review':True,'formal_complete_units':0})
timing=report['capture_timing'];times=timing['frame_wall_offsets_s'];duration=timing['requested_video_wall_duration_s']
assert len(times)==len(frames) and 6.6<=duration<8
concat=[]
for i,p in enumerate(frames):
    start=0. if i==0 else times[i]
    end=times[i+1] if i+1<len(times) else duration
    assert end>start
    concat.extend(["file '"+p.as_posix()+"'",f'duration {end-start:.12f}'])
concat.append("file '"+frames[-1].as_posix()+"'")
lst=O/'wall-timed-native-frames-v001.txt';new(lst,'\n'.join(concat)+'\n')
video=P/'fairytale-sword-primary2-fit-silent.mp4';assert not video.exists()
argv=[str(F),'-hide_banner','-loglevel','info','-f','concat','-safe','0','-i',str(lst),'-vf','fps=30','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]
run=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',errors='replace')
new(O/'video-encode-v001.log',run.stdout+run.stderr);assert run.returncode==0
decode=[str(F),'-hide_banner','-v','error','-i',str(video),'-an','-f','null','NUL']
check=subprocess.run(decode,capture_output=True,text=True,encoding='utf-8',errors='replace')
new(O/'video-full-decode-v001.log',check.stdout+check.stderr);assert check.returncode==0 and not check.stderr.strip()
new(O/'video-presentation-receipt-v001.json',{'source_native_movies':len(frames),'native_original_including_prewarm':len(frames)+1,'capture_wall_duration_s':duration,'presentation_policy':'nativewalltimed concat, firstcapturedframe held from0 untilnext; lasttail repeated, CFR30 encode quantizes display only; no gameclock or sourceframes edited','encode_argv':argv,'encode_exit':run.returncode,'full_decode_argv':decode,'full_decode_exit':check.returncode,'video':desc(video),'audio_recorded':False,'audio_substituted':False,'motion_accepted':False,'formal_complete_units':0})
shutil.copy2(Path(__file__),O/'tool-postprocess-sword-primary2-fit-v004.py')
new(A/'README.md','Native171 Primary2six body under actual paired J/kernelStage1, Ready and Primary1 keep matching armor; Primary2 uses matching42 body/armor-layer textures, no motion/grip/footlock acceptance. Source/DLL bound to supplied compiled snapshot. 72px body/UIoff; silent. All recorded observations/PNGs, kernel phases, actual Ready7/Primary1and2-8 stacks/nativepixel/visiblehead gates passed. Selectedframes/video await explicit art review; equipment IDs/thumb/fullmotion/allstates/combos/audio remain unfinished.\n')
new(A/'source-version-status-index.json',{'status':'actualnative_pairedJ_Primary2_kernelphase_GREEN_visual_review_pending','snapshot':S.as_posix(),'selected_manifest':desc(O/'selected-frame-source-map-v001.json'),'video_receipt':desc(O/'video-presentation-receipt-v001.json'),'formal_complete_units':0})
print(json.dumps({'archive':A.as_posix(),'snapshot_checks':2*len(manifest['files']),'selected_whole':32,'unscaled_crops':32,'video':desc(video),'capture_duration':duration,'visual_review_pending':True},ensure_ascii=False))
