"""Read-only actual Hurt native inputs; NEW media output only. No UE, retime or manufactured join."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess,sys
import imageio_ffmpeg
from PIL import Image
C=Path(__file__).resolve().parent.parent


def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):
 p=Path(p).resolve();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def need(v,why):
 if not v:raise ValueError(why)
def checked_pin(row):
 p=Path(row['path']).resolve();need(pin(p)==row,'Pinned dependency differs: '+str(p));return p
def same_id(a,b):return str(a)==str(b)
def phase(age):return 3 if age>=.3 else 2 if age>=.2 else 1 if age>=.1 else 0

def renderer_kind(o,r):
 d=o['hurt_draw'];j=o['join_draw']
 if o['hurt_query_ok'] and o['hurt_active'] and o['animation']=='hurt' and o['hurt_remaining']>0:
  f=phase(o['hurt_elapsed'])
  need(o['phase']==9 and d['drawn'] and d['atomic_preflight_ready'] and d['supported'] and d['opt_in'],'Qualified actual Hurt draw missing')
  need(d['frame']==f and d['hurt_elapsed']==o['animation_time']==o['hurt_elapsed'] and d['hurt_remaining']==o['hurt_remaining'] and d['hurt_active'],'Actual Hurt age/remaining/frame differs')
  need(same_id(d['player_entity'],r['player_entity']) and same_id(d['weapon_instance'],r['sword_instance']) and same_id(d['armor_instance'],r['light_instance']) and d['run']==r['run'] and same_id(d['owner'],r['owner']),'Actual Hurt identity differs')
  need(d['sim']==o['sim'] and d['facing']==o['facing']==-r['actual_approach_side'] and d['actual_stack']==o['rendered_stack'] and len(d['slots'])==9 and d['nonempty_count']==len(d['actual_stack'])==(9 if f==0 else 8),'Actual Hurt shared-plan draw/stack differs')
  return 'Hurt'+str(f)
 if o['hurt_query_ok'] or o['hurt_active'] or o['animation']=='hurt' or d['drawn']:return 'Other'
 good=j['active'] and j['supported'] and j['texture_ready'] and j['armor_drawn'] and same_id(j['weapon_instance'],r['sword_instance']) and j['stack']==o['rendered_stack'] and bool(j['stack'])
 if good and not j['walk'] and j['clip']=='sword_ready_idle':return 'Ready'
 if good and j['walk'] and j['clip']=='sword_walk' and j['facing']==o['facing']==r['actual_approach_side']:return 'Walk'
 return 'Other'

def select_originals(r,v,frames):
 obs=r['observations'];kinds=[renderer_kind(o,r) for o in obs]
 h=[i for i,k in enumerate(kinds)if k.startswith('Hurt')]
 need(h and len(h)==v['native_Hurt_draws'] and {kinds[i]for i in h}=={'Hurt0','Hurt1','Hurt2','Hurt3'},'Actual complete four-phase Hurt observations required')
 witnesses=v['optical_source_projection']['source_registered_native_witnesses'];need(len(witnesses)==4,'Independent optical proof must contain actual4 phase witnesses')
 byname={f.name:i for i,f in enumerate(frames)};selected=[]
 for f in range(4):
  w=[x for x in witnesses if x['frame']==f];need(len(w)==1,'Independent phase witness missing/duplicate');w=w[0]
  need(w['original_PNG'] in byname,'Independent optical witness is not an original PNG');i=byname[w['original_PNG']]
  need(i in h and kinds[i]=='Hurt'+str(f) and same_id(obs[i]['hurt_draw']['draw_id'],w['native_draw_id']),'Optical witness does not bind actual query/draw phase')
  selected.append(dict(frame=f,observation=i,optical_witness=w))
 last=h[-1];need(kinds[last]=='Hurt3','Actual last Hurt draw must be phase3')
 ready=[i for i in range(last+1,len(obs))if kinds[i]=='Ready'];walk=[i for i in range(last+1,len(obs))if kinds[i]=='Walk']
 need(ready and walk,'Actual post-Hurt Ready/Walk source witnesses missing')
 first_ready=ready[0];first_walk=walk[0]
 pairs=[];missing=[]
 for name,before,after,left,right in [('Hurt3-to-first-Ready',last,first_ready,'Hurt3','Ready'),('Ready-to-first-Walk',first_walk-1,first_walk,'Ready','Walk')]:
  ok=after==before+1 and before>=last and kinds[before]==left and kinds[after]==right and first_ready<=first_walk
  if ok:
   lid=obs[before]['hurt_draw']['draw_id']if left.startswith('Hurt')else obs[before]['join_draw']['draw_id'];rid=obs[after]['join_draw']['draw_id']
   need(int(rid)>int(lid),'Adjacent renderer transition reused/reversed DrawId')
   pairs.append(dict(join=name,before=before,after=after,before_kind=left,after_kind=right,original_adjacent_callbacks=True,intervening_native_frames=0,callback_phases=[obs[before]['phase'],obs[after]['phase']],visual_accepted=False))
  else:missing.append(dict(join=name,reason='No exact original adjacent renderer-change pair; no synthetic/held/nonadjacent replacement',before=before,after=after,before_kind=kinds[before]if before>=0 else None,after_kind=kinds[after],intervening_native_frames=max(0,after-before-1)))
 transitions=[dict(before=i,after=i+1,before_kind=kinds[i],after_kind=kinds[i+1],callback_phases=[obs[i]['phase'],obs[i+1]['phase']])for i in range(last,len(obs)-1)if kinds[i]!=kinds[i+1]]
 return selected,dict(required=2,available=pairs,missing=missing,complete=not missing,actual_adjacent_renderer_changes=transitions,phase10_or11_not_used_as_renderer_transition_substitute=True)

def actual_inputs(archive):
 contract=read(C/'media-input-contract-v001.json')
 for row in read(C/'Hurt-native-media-freeze-v001.json')['files']:
  p=C/row['path'];f=pin(p);need(f['bytes']==row['bytes'] and f['sha256']==row['sha256'],'Frozen media candidate changed')
 dep=checked_pin(contract['exact_observer_checker_freeze']);checker=checked_pin(contract['official_checker']);checked_pin(contract['VFR_reference_freeze']);checked_pin(contract['VFR_reference_helper'])
 original=archive/'原件';report=original/'runtime-report.json';proof=original/contract['independent_receipt'];session_path=archive/'index.json'
 r=read(report);v=read(proof);session=read(session_path)
 need(session['schema']==contract['native_session_schema'] and session['candidate_freeze_sha256']==pin(dep)['sha256'] and same_id(session['process_id'],r['process_id']) and session['exit_code']==0 and session['native_reported_passed']is True and session['independent_passed']is True,'Actual final native/session/independent PASS required')
 need(r['schema']==contract['native_report_schema'] and r['scenario']==contract['scenario'] and r['passed']is True and r['flow_complete']is True and v['passed']is True,'Actual native or independent result is RED')
 need(r['requested_approach_side']==session['requested_approach_side'] and r['actual_approach_side']in [-1,1] and (session['requested_approach_side']==0 or session['requested_approach_side']==r['actual_approach_side']),'Requested/actual side differs')
 need(r['HurtMask']==15 and v['original_Hurt_frames']==[0,1,2,3] and v['native_quad_Root_Grip_axis_full_mirror_verified'] and v['native_PNG_CRC_FIFO_verified'] and v['optical_source_projection']['passed'],'Actual4 source phases/quad/optical/CRC independent gates required')
 need(v['optical_source_projection']['registration_search_used']is False and v['optical_source_projection']['actual_pixels_modified']is False,'Independent registration search or pixel edits forbidden')
 need(r['player_or_Guard_public_damage_used']is False and r['HP_poise_clock_actor_writes']is False and r['guard_final_HP']==185 and r['guard_incoming_count']==0 and r['actual_HP_loss']>0,'Normal Guard-to-player hit scope differs')
 need(r['silent_video']is True and r['audio_recorded']is False and v['audio_recorded']is False and r['visual_reviewed']is False and v['visual_reviewed']is False and r['formal_complete_units']==0 and v['FinalAccepted']is False,'Silent unaccepted presentation scope required')
 # The independent receipt has no invented PID/report-SHA field. Re-run its exact
 # frozen read-only checker against this session's original prereg/snapshot, and
 # require the same result. Root runs only after BOTH captures have terminated.
 prereg=Path(session['root_prereg']).resolve();snapshot=Path(session['snapshot']).resolve()
 need(pin(prereg)['sha256']==session['root_prereg_sha256'] and pin(snapshot/'compiled-source-manifest.json')['sha256']==session['snapshot_manifest_sha256'],'Session actual prereg/snapshot pins differ')
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8')
 need(result.returncode==0,'Frozen official independent checker rejected actual input: '+result.stderr)
 rerun=json.loads(result.stdout);need(rerun==v,'Retained independent PASS differs from readonly re-verification; preserve original receipt')
 rows=[json.loads(line)for line in (original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if line]
 movie=[x for x in rows if x['file'].startswith('MovieFrame')];frames=[original/x['file']for x in movie]
 need(frames and [f.name for f in frames]==sorted(f.name for f in frames) and {f.name for f in frames}=={f.name for f in original.glob('MovieFrame*.png')},'Original movie sequence missing/duplicate/reordered')
 obs=r['observations'];timing=r['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s']
 need(len(frames)==len(obs)==len(offsets) and all(type(t)in [int,float]and math.isfinite(t) for t in offsets) and all(y>x for x,y in zip(offsets,offsets[1:])) and timing['use_fixed_time_step']is False and duration>offsets[-1]>=offsets[0]>=0,'Actual native timing/count/end differs')
 need(all(o['wall_offset_s']==t for o,t in zip(obs,offsets)) and len({x['file']for x in movie})==len(frames),'Native observation/PNG timeline mapping differs')
 selected,joins=select_originals(r,v,frames)
 return r,v,frames,offsets,duration,selected,joins,dict(report=pin(report),independent=pin(proof),session=pin(session_path),official_checker=pin(checker),official_readonly_rerun_passed=True,independent_receipt_PID_and_reportSHA_not_invented=True,observer_freeze=pin(dep),root_prereg=pin(prereg),compiled_manifest=pin(snapshot/'compiled-source-manifest.json'))

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output');p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 archive=Path(a.archive).resolve();r,v,frames,offsets,duration,selected,joins,bindings=actual_inputs(archive)
 summary=dict(actual_native_and_independent_input_verified=True,native_frames=len(frames),actual_approach_side=r['actual_approach_side'],four_original_phase_samples=selected,actual_join_analysis=joins,media_written=False,UE_started=False,visual_reviewed=False)
 if a.validate_only or not joins['complete']:
  print(json.dumps(summary,ensure_ascii=False,indent=2))
  if not joins['complete']:raise SystemExit(3)
  return
 need(a.output,'NEW absolute output leaf required; never mutate the native archive')
 show=Path(a.output);need(show.is_absolute(),'Output must be absolute');show=show.resolve()
 need(show!=archive and archive not in show.parents and show not in archive.parents,'Output must be a separate NEW leaf outside the native archive')
 need(not show.exists() and show.parent.is_dir(),'Output leaf must not exist and parent must exist; preserve earlier versions')
 show.mkdir()
 concat=show/'hero-Hurt4-native-timing-v001.ffconcat';video=show/'hero-Hurt4-native-DIAGNOSTIC-silent-v001.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-Hurt-v001.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-Hurt-v001.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (show/'decoded-framemd5-Hurt-v001.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=show/'decoded-final-frame-Hurt-v001.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (show/'presentation-frame-retention-Hurt-v001.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 
 # Complete source index binds every native frame/offset and all displayed copies.
 source_rows=[]
 for i,(f,t,row)in enumerate(zip(frames,offsets,r['observations'])):
  source_rows.append(dict(observation=i,native_original=pin(f),wall_offset_s=t,decoded_video_PTS_s=int(decoded_rows[i][2])/1.e6,simulation_time=row['sim'],callback_phase=row['phase'],native_renderer_kind=renderer_kind(row,r)))
 def copy_native(i,name):
  dest=show/name;need(not dest.exists(),'Never overwrite a presentation copy');shutil.copy2(frames[i],dest)
  need(pin(frames[i])['sha256']==pin(dest)['sha256'],'Original presentation copy differs')
  with Image.open(dest)as im:need(im.format=='PNG' and im.size==(1280,720),'Only original1280x720 PNG allowed')
  return dict(observation=i,source=pin(frames[i]),presentation=pin(dest),wall_offset_s=offsets[i],simulation_time=r['observations'][i]['sim'],callback_phase=r['observations'][i]['phase'],resized=False,pixels_edited=False)
 samples=[]
 for s in selected:
  i=s['observation'];item=copy_native(i,f'Hurt-{s["frame"]:02d}-UNSCALED-Hurt-v001.png');o=r['observations'][i]
  item.update(frame=s['frame'],actual_query=dict(active=o['hurt_active'],elapsed=o['hurt_elapsed'],remaining=o['hurt_remaining'],animation_time=o['animation_time']),actual_hurt_draw=o['hurt_draw'],independent_optical_witness=s['optical_witness']);samples.append(item)
 copied_joins=[]
 for j in joins['available']:
  pair=[copy_native(j[side],f'JOIN-{j["join"]}-{side}-UNSCALED-Hurt-v001.png')for side in ['before','after']]
  for item in pair:
   o=r['observations'][item['observation']];item.update(actual_hurt_draw=o['hurt_draw'],actual_join_draw=o['join_draw'],actual_motion=o['motion'],native_renderer_kind=renderer_kind(o,r))
  copied_joins.append(dict(**j,pair=pair,original_wall_delta_s=offsets[j['after']]-offsets[j['before']],interpolation=False,retimed=False))
 last_source=copy_native(len(frames)-1,'native-final-frame-UNSCALED-Hurt-v001.png')
 with Image.open(last)as im:decoded_size=list(im.size)
 final=dict(native_original=pin(frames[-1]),native_copy=last_source,decoded_final=pin(last),decoded_dimensions=decoded_size,decoded_frame_index=len(frames)-1,decode_count_equals_native=True,source_and_decoded_are_separate=True,lossy_video_pixel_equality_not_claimed=True,visual_reviewed=False)
 index=dict(schema='Hero-Hurt4-native-media-source-version-status-v001',status='ACTUAL_NATIVE_AND_INDEPENDENT_PASS_MEDIA_VISUAL_REVIEW_PENDING',native_archive=archive.as_posix(),actual_side=r['actual_approach_side'],native_bindings=bindings,media_candidate=pin(C/'Hurt-native-media-freeze-v001.json'),video=pin(video),native_frame_count=len(frames),source_frames=source_rows,samples=samples,required_sample_count=4,joins=copied_joins,required_original_adjacent_joins=2,actual_join_analysis=joins,presentation_frame_retention=timing_receipt,final_frame=final,real_guard_hit=dict(event=r['hit_event'],attack=r['hit_attack'],at=r['hit_at'],actual_HP_loss=r['actual_HP_loss']),native_originals_modified=False,native_variable_pacing_preserved=True,video_silent=True,audio_recorded=False,visual_reviewed=False,FinalAccepted=False,formal_complete_units=0,E_before_view_required=True)
 (show/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'join-candidates-Hurt-v001.json').write_text(json.dumps(dict(analysis=joins,original_pairs=copied_joins,visual_reviewed=False,FinalAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'decoded-final-source-association-Hurt-v001.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'README.md').write_text('真实Guard重斧命中→玩家Hurt四相→Ready→Walk的同一原生过程。四张样本与两个严格相邻renderer回接对均为1280×720原幅PNG；只读原native archive，另列全帧source index、真实偏移VFR静音录像、frameMD5解码数量/PTS误差及独立原/解码末帧。Knight/Bat仅公开诊断清除；玩家和Guard无公开伤害/HP/韧性/时间/朝向写入。视频为有损展示，原末帧与解码末帧分别保留，不冒像素相等。Hurt光学门由既有独立checker决定，本helper不改阈值、不补帧改速拼动作。回接相邻性来自实际renderer字段，非phase10/11标签；未E保全和View，不称触柄/遮挡/no-pop或最终美术验收。\n',encoding='utf-8')
 print(json.dumps(dict(output=show.as_posix(),video=pin(video),native_frames=len(frames),samples=len(samples),original_adjacent_joins=len(copied_joins),actual_side=r['actual_approach_side'],decoded_final=pin(last),native_final=pin(frames[-1]),native_archive_modified=False,visual_reviewed=False),ensure_ascii=False))

if __name__=='__main__':main()
