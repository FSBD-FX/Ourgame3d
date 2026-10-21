"""Preserve real v144 role clips and unscaled witness boards; no native rerun or art claim."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,importlib.util,math,shutil,struct
from PIL import Image,ImageDraw,ImageChops
R=Path('F:/Ourgame');M=R/'过程图稿与视频'
P=M/'2026-10-19_钟盔空中存档两进程_v001/independent-two-process-verification-v001.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def need(v,s):
 if not v:raise ValueError(s)
def checked(row):
 p=Path(row['path']);a=pin(p);need((a['bytes'],a['sha256'])==(row['bytes'],row['sha256']),'Pinned media input drift');return p
def new(p,v):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
helper_path=R/'source-assets/production/fairytale-hero-air-v001/landing-presentation-candidate-v001/prepare-landing-presentation-v001.py'
need(pin(helper_path)['sha256']=='9c4d2644ce1b09eae8e6c540cc542a142d4c5fc0d4250bb3b96a6a7b738b9454','Frozen full-AV helper changed')
spec=importlib.util.spec_from_file_location('retained_full_native_AV_only',helper_path);H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
proof=read(P);need(proof['passed'] and proof['schema']=='hero-air-disk-restore-independent-two-native-v001','Actual independent pair PASS required')
checked(proof['root_prereg_pin']);checked(proof['two_process_session_pin']);checked(proof['compiled_manifest_pin']);checked(proof['game_dll_pin'])
for role in ('source','target'):
 v=proof['roles'][role];report_path=checked(v['native_report_pin']);report=read(report_path);raw=report_path.parent
 need(report['passed'] and report['flow_complete'] and v['native_PNG_FIFO_CRC_verified'],'Complete role native PASS required')
 obs=report['observations'];timing=report['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s']
 frames=[raw/('MovieFrame%05d.png'%i) for i in range(len(obs))]
 need(len(frames)==len(offsets)==v['callbacks'] and all(o['completed_callback'] is True and o['wall_offset_s']==offsets[i] for i,o in enumerate(obs)),'Actual callback timeline binding differs')
 need(all(b>a for a,b in zip(offsets,offsets[1:])) and 0<=offsets[0]<offsets[-1]<duration,'Strict real-wall full timeline required')
 all_frames=[pin(p) for p in frames]
 O=M/('2026-10-19_钟盔空中存档实录_'+role+'_right_v001');need(not O.exists(),'Preserve previous role presentation')
 O.mkdir();original=O/'原件';display=O/'展示副本';work=O/'编码记录';original.mkdir();display.mkdir();work.mkdir()
 for path in (P,report_path):shutil.copy2(path,original/path.name)
 audio=v['audio'];canonical=checked(audio['canonical']);engine=checked(audio['engine_original'])
 H.copy_exact(canonical,original/'runtime-mix.wav');H.copy_exact(engine,original/'runtime-mix-engine-export.wav')
 encoding=H.encode_with_full_native_mix(work,display,frames,offsets,duration,original/'runtime-mix.wav',audio['decoded_PCM'])
 video=display/('clock-helmet-air-disk-'+role+'-full-native-v001.mp4');H.copy_exact(Path(encoding['video']['path']),video)
 witnesses=v['source_pixels']['source_pixel_witnesses']
 selected=[row for row in witnesses if not row['kind'].startswith('Walk')]
 columns=4;width=256;height=320;label=52;gap=12;cellw=width+gap;cellh=height+label+gap
 board=Image.new('RGB',(columns*cellw,math.ceil(len(selected)/columns)*cellh),(26,29,34));draw=ImageDraw.Draw(board);details=[]
 for k,row in enumerate(selected):
  i=row['observation'];o=obs[i];need(row['file']==frames[i].name,'Witness PNG differs from actual callback')
  air=o['new_air_draw']
  if air['drawn']:
   ground=air['context_ground'];origin='actual_new_air_draw_context_ground'
  else:
   f32=lambda value:struct.unpack('<f',struct.pack('<f',value))[0]
   ground=[f32(640+(o['ground'][0]-o['camera_ground'][0])*f32(.65)),f32(490-o['ground'][1]*f32(.38))];origin='observed_ground_projection_for_crop_only'
  cx,cy=map(lambda a:int(round(a)),ground);left=max(0,min(1280-width,cx-width//2));top=max(0,min(720-height,cy-240));crop=[left,top,left+width,top+height]
  x=(k%columns)*cellw;y=(k//columns)*cellh+label;rect=[x,y,x+width,y+height]
  with Image.open(frames[i]) as im:need(im.size==(1280,720),'Actual full viewport required');board.paste(im.crop(crop).convert('RGB'),(x,y))
  text='%s %s pose%s obs%s\nwall%.6f sim%.6f\nactual unscaled pose witness'%(role,row['kind'],row['frame'],i,o['wall_offset_s'],o['sim'])
  draw.multiline_text((x+4,y-label+3),text,fill='white',spacing=2)
  details.append(dict(kind=row['kind'],frame=row['frame'],observation=i,source=all_frames[i],source_crop=crop,board_rect=rect,crop_anchor=origin))
  H.copy_exact(frames[i],original/('%s-obs%05d.png'%(row['kind'],i)))
 board_path=display/('air-disk-'+role+'-UNSCALED-witnesses-v001.png')
 with board_path.open('xb') as f:board.save(f,format='PNG')
 with Image.open(board_path) as rendered:
  for row in details:
   with Image.open(row['source']['path']) as im:need(ImageChops.difference(rendered.crop(row['board_rect']),im.crop(row['source_crop']).convert('RGB')).getbbox() is None,'Reopened board crop differs')
 index=dict(schema='Root-air-disk-two-process-role-media-v001',utc=datetime.now(timezone.utc).isoformat(),role=role,process_id=v['process_id'],independent_pair=pin(P),runtime=pin(report_path),all_native_frames=all_frames,full_original_WAV_preserved=True,native_audio_silent=not audio['decoded_PCM']['non_silent'],presentation_encoding=encoding,playable_video=pin(video),witness_board=dict(file=pin(board_path),samples=details,source_pixels_resized=False,exact_original_crop_pixels_redecoded_equal=True,label_inside_game_rect=False),frozen_AV_encoder=pin(helper_path),runtime_environment=H.runtime_environment(),visual_reviewed=False,full_realtime_playback_reviewed=False,audio_listened=False,FinalAccepted=False)
 new(O/'来源-版本-状态索引.json',index)
 (O/'README.md').write_text('真实空中磁盘存档两进程实录：'+role+'。保留全部真实回调及完整原混音；源与目标为分开的真实进程，不拼成连续同进程片。目标实际录音为静音，不代表脚步／跳跃／落地音效完成。原始PNG完整保留在对应native目录，本包含见证原幅与无缩放裁切。辅助编码器历史Air6/DIAGNOSTIC文件名保留，实际角色以本索引为准；清晰命名视频是其逐字节副本。有限画面／原速播放／试听／最终美术尚未验收。\n',encoding='utf-8')
 print(json.dumps(dict(role=role,archive=O.as_posix(),video=pin(video),native_frames=len(frames),board=pin(board_path),FinalAccepted=False),ensure_ascii=False))
