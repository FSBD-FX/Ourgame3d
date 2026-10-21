from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,importlib.util,math
from PIL import Image,ImageDraw,ImageChops
R=Path('F:/Ourgame')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(row):
 p=Path(row['path']);v=pin(p);assert (v['bytes'],v['sha256'])==(row['bytes'],row['sha256']);return p
ap=argparse.ArgumentParser();ap.add_argument('--verification',required=True);ap.add_argument('--version',default='v001');a=ap.parse_args()
assert len(a.version)==4 and a.version.startswith('v') and a.version[1:].isdigit()
proofpath=Path(a.verification).resolve();proof=read(proofpath);assert proof['passed'] and proof['audio_recorded'] is False
reportpath=checked(proof['native_report_pin']);report=read(reportpath);assert report['passed'] and report['flow_complete'] and report['silent_video'] and not report['audio_recorded']
raw=reportpath.parent;obs=report['observations'];t=report['capture_timing'];offsets=t['frame_wall_offsets_s'];duration=t['capture_stop_monotonic_s']-t['capture_start_monotonic_s']
assert not t['use_fixed_time_step'] and offsets==[o['wall_offset_s'] for o in obs] and all(b>a for a,b in zip(offsets,offsets[1:]))
frames=[raw/('MovieFrame%05d.png'%i) for i in range(len(obs))];framepins=[pin(p) for p in frames]
helper=R/'source-assets/production/fairytale-hero-air-v001/landing-presentation-candidate-v001/prepare-landing-presentation-v001.py'
assert pin(helper)['sha256']=='9c4d2644ce1b09eae8e6c540cc542a142d4c5fc0d4250bb3b96a6a7b738b9454'
spec=importlib.util.spec_from_file_location('retained_complete_encoder_ready',helper);H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
assert H.pin(H.ENCODER)['sha256']==H.ENCODER_SHA
encoder=H.module(H.ENCODER,'retained_silent_native_VFR_ready')
O=R/('过程图稿与视频/2026-10-19_钟盔待机三连258完整实录_'+a.version);assert not O.exists();O.mkdir();original=O/'原件';display=O/'展示副本';work=O/'编码记录'
for p in (original,display,work):p.mkdir()
for p in (proofpath,reportpath):H.copy_exact(p,original/p.name)
silent,last,timing,decoded=encoder.encode_vfr(work,frames,offsets,duration)
video=display/('clock-helmet-ready-combo258-full-native-silent-'+a.version+'.mp4');H.copy_exact(silent,video)
witnesses=proof['source_screen_pixels']['source_screen_coordinate_witnesses'];assert len(witnesses)==12
columns=4;cw=256;ch=180;gap=12;label=52;board=Image.new('RGB',(columns*(cw+gap),math.ceil(len(witnesses)/columns)*(ch+label+gap)),(26,29,34));draw=ImageDraw.Draw(board);samples=[]
for k,w in enumerate(witnesses):
 i=w['observation'];o=obs[i];assert w['file']==frames[i].name
 scale=o['canvas_size']/512;ground=[o['grip_screen'][0]+(o['root'][0]-o['grip'][0])*o['facing']*scale,o['grip_screen'][1]+(o['root'][1]-o['grip'][1])*scale]
 left=max(0,min(1280-cw,round(ground[0]-cw/2)));top=max(0,min(720-ch,round(ground[1]-144)));crop=[left,top,left+cw,top+ch]
 x=(k%columns)*(cw+gap);y=(k//columns)*(ch+label+gap)+label;rect=[x,y,x+cw,y+ch]
 with Image.open(frames[i]) as im:assert im.size==(1280,720);board.paste(im.crop(crop).convert('RGB'),(x,y))
 draw.multiline_text((x+3,y-label+2),'%s frame%s obs%s\nwall%.6f sim%.6f\nactual unscaled crop'%(o['clip'],o['frame'],i,o['wall_offset_s'],o['sim']),fill='white',spacing=2)
 H.copy_exact(frames[i],original/('witness-obs%05d.png'%i));samples.append(dict(observation=i,clip=o['clip'],frame=o['frame'],source=framepins[i],crop=crop,board_rect=rect,screen_root_inferred_from_same_draw_markers=True,independent_world_projection=False))
boardpath=display/('primary1-bridge258-ready-combo-UNSCALED-witnesses-'+a.version+'.png')
with boardpath.open('xb') as f:board.save(f,format='PNG')
with Image.open(boardpath) as im:
 for row in samples:
  with Image.open(row['source']['path']) as native:assert ImageChops.difference(im.crop(row['board_rect']),native.crop(row['crop']).convert('RGB')).getbbox() is None
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary1-bridge258-Ready-full-native-silent-media-v001',utc=datetime.now(timezone.utc).isoformat(),verification=pin(proofpath),runtime=pin(reportpath),all_native_frames=framepins,video=pin(video),native_VFR_timing=timing,full_native_video_decoded=True,native_first_callback_offset_s=offsets[0],audio_recorded=False,audio_added=False,witness_board=dict(file=pin(boardpath),samples=samples,unscaled_original_crop_pixels_equal=True),OPEN=proof['OPEN'],visual_reviewed=False,full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
(O/'README.md').write_text('真实默认地图QA来源：Enter/E/A取消/E提交轻甲，待机→新起手首段→三段连招→待机，随后完整中甲替换与原轻甲重拾。全部原生callback保持VFR；原观察器无录音，本片明确静音。12张原像素裁片不缩放；无GPU/世界坐标/内部PID/合法来源或孤立首段回待机闭环声明。先E完整保全再View。\n',encoding='utf-8')
print(json.dumps(dict(archive=O.as_posix(),video=pin(video),board=pin(boardpath),frames=len(frames),audio_recorded=False,FinalAccepted=False),ensure_ascii=False))
