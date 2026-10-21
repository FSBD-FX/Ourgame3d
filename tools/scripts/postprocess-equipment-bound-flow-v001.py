"""Inspect real bound-flow output and make silent wall-timed review copies."""
from pathlib import Path
import argparse,hashlib,json,math,subprocess
from PIL import Image
import imageio_ffmpeg
R=Path('F:/Ourgame')
ap=argparse.ArgumentParser();ap.add_argument('--archive',required=True);ap.add_argument('--snapshot',required=True);ap.add_argument('--expect',choices=['RED','GREEN'],required=True);a=ap.parse_args()
A=(R/a.archive).resolve();S=(R/a.snapshot).resolve();O=A/'原件';P=A/'展示副本'
assert A.is_relative_to(R/'过程图稿与视频') and S.is_relative_to(R/'source-assets/production/backups')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def desc(p):
 b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def new(p,v):
 assert not p.exists();p.write_text(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(O/'runtime-report.json');index=read(A/'index.json');pix=read(O/'native-pixel-verification.json');manifest=read(S/'compiled-source-manifest.json')
assert v['schema']=='fairytale-equipment-bound-native-flow-v1' and v['flow_complete'] and v['reason']==''
assert v['light_primary_phase_masks']==[63,63,63] and v['native_async_capture_writes_flushed']
assert v['silent_video'] and not v['audio_recorded'] and not v['capture_timing']['use_fixed_time_step']
assert pix['every_source_viewport_pixel_crc_matches'] and pix['native_async_writer_verified']
assert index['source_manifest_SHA256']==desc(S/'compiled-source-manifest.json')['sha256']
for row in manifest['files']:
 for base in [R,S]:
  p=base/row['path'];d=desc(p);assert d['bytes']==row['bytes'] and d['sha256']==row['sha256'],p
audit=dict(snapshot=S.as_posix(),snapshot_files=len(manifest['files']),endpoint_checks=2*len(manifest['files']),mismatches=0,production_packages=1085,current_full_automation_succeeded=manifest['current_automation_succeeded'],source_and_DLL_unchanged=True)
new(O/'source-and-snapshot-binding-verification-v001.json',audit)
movies=sorted(O.glob('MovieFrame*.png'));obs=v['observations'];offsets=v['capture_timing']['frame_wall_offsets_s'];duration=v['capture_timing']['requested_video_wall_duration_s']
assert len(movies)==len(obs)==len(offsets)>0 and pix['verified_original_PNG_count']==len(movies)+1
light=v['light_instance_id'];medium=v['medium_instance_id'];found=[];unique=set()
for i,x in enumerate(obs):
 armor=x['committed_armor_id'];mode='no_armor' if armor=='0' else 'light_armor' if armor==light else 'unsupported_medium' if armor==medium else None
 assert mode==x['expected_armor_mode'] and mode is not None
 assert not x['interface_visible'] and x['text_calls']==0 and abs(x['canvas_size']-72*512/416)<1e-9
 has=any(('Shoulder' in q or 'Chest' in q) for q in x['draw_stack'])
 assert has==x['draw_stack_has_armor']
 reason=None
 if mode=='no_armor' and (x['armor_drawn'] or has):reason='actual_no_armor_is_dressed_by_art_flags'
 if mode=='unsupported_medium' and (x['supported'] or x['armor_drawn'] or has or x['weapon']):reason='unsupported_medium_is_falsely_drawn_as_sword_or_light'
 if mode=='light_armor' and x['supported']:
  assert x['armor_drawn'] and has and x['armor_ready'] and x['weapon'] and len(x['draw_stack'])==(7 if x['clip']=='sword_ready_idle' else 8)
 if reason:
  key=(x['flow_phase'],reason)
  if key not in unique:found.append(dict(phase=key[0],reason=key[1],first_observation=i));unique.add(key)
native={(x['phase'],x['reason']) for x in v['mismatches']}
assert native==unique, 'Unexpected native mismatch; do not re-label an unrelated fixture failure as feature RED'
if a.expect=='RED':assert not v['passed'] and found and index['runtime_passed'] is False
else:assert v['passed'] and not found and index['runtime_passed'] is True
stages={}
for x in obs:
 if x['flow_step']==6 and x['supported'] and x['stage'] in [0,1,2] and x['clip'].startswith('sword_primary_'):
  stages.setdefault(x['stage'],set()).add(x['action_id'])
assert set(stages)=={0,1,2} and all(len(s)==1 for s in stages.values()) and len(set.union(*stages.values()))==3
last=obs[-1];assert last['committed_armor_id']==light and last['armor_mirror']=='ARM-LGT-001'
first=obs[0];assert int(last['operation_count'])-int(first['operation_count'])==3 and int(last['next_operation_id'])-int(first['next_operation_id'])==3
proof=dict(expected=a.expect,actual_native_feature_RED=a.expect=='RED',independent_metadata_mismatches=found,flow_complete=True,observations=len(obs),original_PNGs=len(movies)+1,duration_s=duration,three_stage_action_ids={str(k):sorted(q) for k,q in stages.items()},three_stage_masks=[63,63,63],actual_light_id=light,actual_medium_id=medium,final_original_light_version=last['committed_armor_version'],operations_committed=3,whole_game_audio_accepted=False,full_motion_accepted=False,formal_complete_units=0)
new(O/'independent-bound-flow-verification-v001.json',proof)
# Phase samples and actual six phases, no invented inbetweens or resampling.
selected=[];phase_values={}
for i,x in enumerate(obs):phase_values.setdefault(x['flow_phase'],[]).append(i)
for phase,values in phase_values.items():selected.append((values[len(values)//2],'flow:'+phase))
for stage in [0,1,2]:
 for frame in range(6):
  hits=[i for i,x in enumerate(obs) if x['flow_step']==6 and x['supported'] and x['stage']==stage and x['frame']==frame]
  assert hits;selected.append((hits[0],f'combo:{stage}:{frame}'))
maps=[]
for j,(i,kind) in enumerate(selected):
 x=obs[i];scale=x['canvas_size']/512.;rootx=x['grip_screen'][0]-x['facing']*(x['grip'][0]-x['root'][0])*scale;rooty=x['grip_screen'][1]-(x['grip'][1]-x['root'][1])*scale
 left=max(0,min(1040,int(math.floor(rootx))-110));top=max(0,min(560,int(math.floor(rooty))-130));rect=[left,top,240,160]
 crop=P/f'crop-{j:02d}-{movies[i].name}';assert not crop.exists()
 with Image.open(movies[i]) as im:
  assert im.size==(1280,720);im.crop((left,top,left+240,top+160)).save(crop)
 with Image.open(movies[i]) as im,Image.open(crop) as ci:assert im.crop((left,top,left+240,top+160)).tobytes()==ci.tobytes()
 maps.append(dict(kind=kind,observation=i,flow_phase=x['flow_phase'],clip=x['clip'],stage=x['stage'],frame=x['frame'],facing=x['facing'],source_whole=desc(movies[i]),unscaled_crop=desc(crop),crop_rect_px=rect,crop_resampled=False,actually_viewed=False))
new(O/'selected-native-source-map-v001.json',dict(frames=maps,selection_is_not_art_review=True))
concat=O/'wall-timed-native-frames-v001.txt';lines=[]
for i,p in enumerate(movies):
 d=(offsets[i+1] if i+1<len(movies) else duration)-(offsets[i] if i>0 else 0.)
 assert d>0;lines += ["file '"+p.as_posix()+"'",f'duration {d:.12f}']
lines += ["file '"+movies[-1].as_posix()+"'"]
new(concat,'\n'.join(lines)+'\n');ff=imageio_ffmpeg.get_ffmpeg_exe();video=P/f'equipment-bound-flow-{a.expect.lower()}-silent.mp4';assert not video.exists()
encode=[ff,'-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-vf','fps=30','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]
er=subprocess.run(encode,capture_output=True,text=True);new(O/'video-encode.log',er.stdout+er.stderr);assert er.returncode==0
decode=[ff,'-hide_banner','-v','error','-i',str(video),'-an','-f','null','NUL'];dr=subprocess.run(decode,capture_output=True,text=True);new(O/'video-full-decode.log',dr.stdout+dr.stderr);assert dr.returncode==0
new(O/'video-presentation-receipt-v001.json',dict(video=desc(video),encode_argv=encode,encode_exit=er.returncode,full_decode_argv=decode,full_decode_exit=dr.returncode,audio_recorded=False,policy='Actual wall-time concat, CFR30 display quantization and tail duplicate; source frames/game clocks unchanged',motion_accepted=False))
provenance=O/'provenance';provenance.mkdir();(provenance/'compiled-source-manifest.json').write_bytes((S/'compiled-source-manifest.json').read_bytes());(provenance/'postprocess-equipment-bound-flow-v001.py').write_bytes(Path(__file__).read_bytes())
new(A/'source-version-status-index.json',dict(status='actual full transaction feature RED preserved' if a.expect=='RED' else 'actual transaction binding GREEN; art review pending',source_snapshot=a.snapshot,native_report=desc(O/'runtime-report.json'),source_binding=desc(O/'source-and-snapshot-binding-verification-v001.json'),native_pixel_proof=desc(O/'native-pixel-verification.json'),independent_flow=desc(O/'independent-bound-flow-verification-v001.json'),video=desc(video),selected_frames=len(maps),formal_complete_units=0))
new(A/'README.md',f'真实装备提交画面绑定 {a.expect}。无甲→移动取消轻甲→同源轻甲提交→单向三段攻击→中甲替换→原轻甲同实例重拾；三个真实提交操作。QA来源不等正式掉落，静音且完整状态/握姿/美术/音效未验收；原PNG保持，展示为实际墙钟时序CFR30副本。\n')
print(json.dumps(dict(expected=a.expect,observations=len(obs),source_snapshot_files=len(manifest['files']),source_endpoint_checks=2*len(manifest['files']),source_mismatches=0,selected_unscaled_crops=len(maps),actual_feature_mismatches=len(found),video=desc(video),formal_complete_units=0),ensure_ascii=False))
