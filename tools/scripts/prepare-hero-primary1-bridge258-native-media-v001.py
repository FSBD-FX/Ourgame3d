"""Full native video and original MainMix, using the frozen complete-AV encoder."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,importlib.util,math,struct,shutil
from PIL import Image,ImageDraw,ImageChops
R=Path('F:/Ourgame')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(row):
 p=Path(row['path']);a=pin(p);assert (a['bytes'],a['sha256'])==(row['bytes'],row['sha256']);return p
ap=argparse.ArgumentParser();ap.add_argument('--verification',required=True);ap.add_argument('--version',default='v002');ap.add_argument('--side',choices=['left','right'],required=True);a=ap.parse_args()
assert a.version.startswith('v') and a.version[1:].isdigit() and len(a.version)==4
P=Path(a.verification).resolve();proof=read(P);assert proof['passed'] and proof['native_PNG_FIFO_CRC_verified']
report_path=checked(proof['native_report_pin']);report=read(report_path);assert report['passed'] and report['flow_complete']
assert report['requested_action']=='J' and report['requested_facing']==(-1 if a.side=='left' else 1) and report['request258_primary1_bridge_optin'] is True
raw=report_path.parent;obs=report['observations'];t=report['capture_timing'];offsets=t['frame_wall_offsets_s'];duration=t['capture_stop_monotonic_s']-t['capture_start_monotonic_s']
assert len(obs)==len(offsets) and all(o['completed_callback'] is True and o['wall_offset_s']==offsets[i] for i,o in enumerate(obs))
assert not t['use_fixed_time_step'] and all(b>a for a,b in zip(offsets,offsets[1:])) and 0<=offsets[0]<offsets[-1]<duration
frames=[raw/('MovieFrame%05d.png'%i) for i in range(len(obs))];all_frames=[pin(p) for p in frames]
helper=R/'source-assets/production/fairytale-hero-air-v001/landing-presentation-candidate-v001/prepare-landing-presentation-v001.py'
assert pin(helper)['sha256']=='9c4d2644ce1b09eae8e6c540cc542a142d4c5fc0d4250bb3b96a6a7b738b9454'
spec=importlib.util.spec_from_file_location('frozen_full_native_encoder',helper);H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
O=R/('过程图稿与视频/2026-10-19_钟盔起手258完整实录_'+a.side+'_'+a.version);assert not O.exists();O.mkdir()
original=O/'原件';display=O/'展示副本';work=O/'编码记录';original.mkdir();display.mkdir();work.mkdir()
for p in (P,report_path):shutil.copy2(p,original/p.name)
audio=proof['audio'];canonical=checked(audio['canonical']);engine=checked(audio['engine_original'])
H.copy_exact(canonical,original/'runtime-mix.wav');H.copy_exact(engine,original/'runtime-mix-engine-export.wav')
encoding=H.encode_with_full_native_mix(work,display,frames,offsets,duration,original/'runtime-mix.wav',audio['decoded_PCM'])
video=display/('clock-helmet-primary1-bridge258-'+a.side+'-full-native-'+a.version+'.mp4');H.copy_exact(Path(encoding['video']['path']),video)
witnesses=proof['source_pixels']['source_pixel_witnesses'];selected=[x for x in witnesses if not x['kind'].startswith('Walk')]
assert selected
columns=4;width=256;height=320;label=52;gap=12;cellw=width+gap;cellh=height+label+gap
board=Image.new('RGB',(columns*cellw,math.ceil(len(selected)/columns)*cellh),(26,29,34));draw=ImageDraw.Draw(board);details=[]
for k,row in enumerate(selected):
 i=row['observation'];o=obs[i];assert row['file']==frames[i].name
 air=o['new_air_draw'];f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
 ground=air['context_ground'] if air['drawn'] else [f32(640+(o['ground'][0]-o['camera_ground'][0])*f32(.65)),f32(490-o['ground'][1]*f32(.38))]
 cx,cy=[int(round(v)) for v in ground];left=max(0,min(1280-width,cx-width//2));top=max(0,min(720-height,cy-240));crop=[left,top,left+width,top+height]
 x=(k%columns)*cellw;y=(k//columns)*cellh+label;rect=[x,y,x+width,y+height]
 with Image.open(frames[i]) as im:assert im.size==(1280,720);board.paste(im.crop(crop).convert('RGB'),(x,y))
 draw.multiline_text((x+4,y-label+3),'%s pose%s obs%s\nwall%.6f sim%.6f\nactual unscaled witness'%(row['kind'],row['frame'],i,o['wall_offset_s'],o['sim']),fill='white',spacing=2)
 details.append(dict(kind=row['kind'],frame=row['frame'],observation=i,source=all_frames[i],source_crop=crop,board_rect=rect))
 H.copy_exact(frames[i],original/('%s-obs%05d.png'%(row['kind'],i)))
boardpath=display/('primary1-bridge258-'+a.side+'-UNSCALED-witnesses-'+a.version+'.png')
with boardpath.open('xb') as f:board.save(f,format='PNG')
with Image.open(boardpath) as rendered:
 for row in details:
  with Image.open(row['source']['path']) as im:assert ImageChops.difference(rendered.crop(row['board_rect']),im.crop(row['source_crop']).convert('RGB')).getbbox() is None
with (O/'来源-版本-状态索引.json').open('x',encoding='utf-8') as f:json.dump(dict(schema='Root-primary1-bridge258-full-native-media-v001',side=a.side,utc=datetime.now(timezone.utc).isoformat(),independent_verification=pin(P),runtime=pin(report_path),all_native_frames=all_frames,full_original_WAV_preserved=True,presentation_encoding=encoding,playable_video=pin(video),witness_board=dict(file=pin(boardpath),samples=details,source_pixels_resized=False,exact_original_crop_pixels_redecoded_equal=True),frozen_AV_encoder=pin(helper),runtime_environment=H.runtime_environment(),visual_reviewed=False,full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False),f,ensure_ascii=False,indent=2)
(O/'README.md').write_text('真实正常输入落地接新起手J0/J1，再接旧J2–5和待机；保留全部原生PNG与完整MainMix。实际129纹理与8层绘制独立验证，旧整Body metadata不冒充新像素。受控Knight诊断和轻甲显示来源；E保全前不View，有限画面／原速播放／听感分别审阅。\n',encoding='utf-8')
print(json.dumps(dict(archive=O.as_posix(),video=pin(video),frames=len(frames),board=pin(boardpath),FinalAccepted=False),ensure_ascii=False))
