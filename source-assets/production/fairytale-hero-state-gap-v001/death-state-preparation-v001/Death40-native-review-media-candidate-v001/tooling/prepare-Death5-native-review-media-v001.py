"""Readonly actual Death5 native inputs; separate NEW review media, never native archive writes."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess,sys
import imageio_ffmpeg
from PIL import Image,ImageDraw
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
def phase(age):return 0 if age<.2 else 1 if age<.4 else 2 if age<.6 else 3 if age<.8 else 4
def ready_stack(frame):
 out=[]
 for component in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','NearHand']:
  if component=='NearHand':out.append('/Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002')
  leather=component in ['ShoulderFar','Chest','ShoulderNear'];name=f'T_Fairytale_{"LeatherReady"if leather else "SwordReady"}{component}_{frame:03d}_v001';out.append(f'/Game/Production/ArtTrials/EV048/{"v012/HeroLeatherReady"if leather else "v006/HeroSwordArmorReady"}/{name}.{name}')
 return out
def renderer_kind(o,r):
 d=o['death_draw']
 if o['dead']:
  f=phase(o['death_elapsed']);need(o['phase']==9 and o['HP']==0 and o['game_over']and o['animation']=='death'and o['death_query_ok']and o['death_active']and o['death_reported'],'Actual terminal Death sample missing')
  need(d['drawn']and d['supported']and d['atomic_preflight_ready']and d['frame']==f and d['death_elapsed']==o['death_elapsed']==o['animation_time']and d['sim']==o['sim']==r['frozen_sim'],'Actual Death query/sharedplan/frame differs')
  need(d['actual_stack']==o['rendered_stack']and len(d['slots'])==d['nonempty_count']==len(d['actual_stack'])==9 and d['facing']==o['facing']==-r['actual_approach_side']and d['tint']==d['plan_tint']==[1,1,1,1],'Actual terminal quad/stack/white/mirror facts differ')
  need(same_id(d['player_entity'],r['player_entity'])and same_id(d['weapon_instance'],r['sword_instance'])and same_id(d['armor_instance'],r['light_instance']),'Actual Death equipment identity differs')
  return 'Death'+str(f)
 need(not o['game_over']and o['HP']>0 and not o['death_query_ok']and not o['death_active']and not d['drawn'],'Live callback already activates Death')
 if o['animation']=='idle':
  for frame in range(4):
   if o['rendered_stack']==ready_stack(frame):return 'LiveIdleReady'+str(frame)+'ActualStack'
 # The Probe deliberately exposes no baseline Ready/Hurt DTO. Preserve that limit.
 if o['animation']=='hurt':return 'LiveHurtActualStackUnqualified'
 return 'Live'+o['animation']+'ActualStackUnqualified'
def select_originals(r,v,frames):
 obs=r['observations'];kinds=[renderer_kind(o,r)for o in obs];dead=[i for i,k in enumerate(kinds)if k.startswith('Death')]
 need(dead and len(dead)==v['native_Death_draws']and{kinds[i]for i in dead}=={'Death'+str(f)for f in range(5)},'Actual complete five-phase Death observations required')
 witnesses=v['optical_source_projection']['source_registered_native_witnesses'];need(len(witnesses)==5,'Independent source optical proof lacks five witnesses');byname={f.name:i for i,f in enumerate(frames)};selected=[]
 for f in range(5):
  ws=[w for w in witnesses if w['frame']==f];need(len(ws)==1,'Optical witness missing/duplicate');w=ws[0];need(w['original_PNG']in byname,'Optical witness is not an original movie PNG');i=byname[w['original_PNG']]
  need(i in dead and kinds[i]=='Death'+str(f)and same_id(obs[i]['death_draw']['draw_id'],w['native_draw_id']),'Independent source witness does not bind actual phase/DrawId');selected.append(dict(frame=f,observation=i,optical_witness=w))
 first=dead[0];need(first>0 and kinds[first]=='Death0','First actual dead callback must be Death0 and retain its live predecessor')
 before=first-1;qualified=kinds[before].startswith('LiveIdleReady');join=dict(join='ActualLiveIdleReadyStack-to-first-Death0',before=before,after=first,before_kind=kinds[before],after_kind=kinds[first],original_adjacent_callbacks=True,intervening_native_frames=0,callback_phases=[obs[before]['phase'],obs[first]['phase']],before_baseline_DrawId_or_Plan_recorded=False,before_authority='Actual animation idle plus exact current Ready layered stack; no baseline DTO/DrawId is invented',qualified=qualified,visual_accepted=False)
 hold=[i for i in dead if kinds[i]=='Death4'and obs[i]['death_draw']['last_frame_held']];need(len(hold)==v['actual_hold_callbacks']>=2 and obs[hold[-1]]['death_elapsed']>=1.2 and hold[-1]==len(obs)-1,'Actual final Death4 hold callback absent')
 return selected,join,hold[-1],kinds
def actual_inputs(archive):
 contract=read(C/'media-input-contract-v001.json')
 for row in read(C/'Death5-native-review-media-freeze-v001.json')['files']:
  f=pin(C/row['path']);need(f['bytes']==row['bytes']and f['sha256']==row['sha256'],'Frozen media candidate changed')
 dep=checked_pin(contract['exact_observer_checker_freeze']);checker=checked_pin(contract['official_checker']);checked_pin(contract['VFR_reference_freeze']);checked_pin(contract['VFR_reference_helper']);checked_pin(contract['Ready_renderer_source'])
 original=archive/'原件';report=original/'runtime-report.json';proof=original/contract['independent_receipt'];session_path=archive/'index.json';r=read(report);v=read(proof);session=read(session_path)
 need(session['schema']==contract['native_session_schema']and session['candidate_freeze_sha256']==pin(dep)['sha256']and same_id(session['process_id'],r['process_id'])and session['exit_code']==0 and session['native_reported_passed']is True and session['independent_passed']is True,'Actual terminal native/session/independent PASS required')
 need(r['schema']==contract['native_report_schema']and r['scenario']==contract['scenario']and r['passed']is True and r['flow_complete']is True and v['passed']is True,'Actual native or independent Death result is RED')
 need(r['requested_approach_side']==session['requested_approach_side']==r['actual_approach_side']and r['actual_approach_side']in[-1,1],'Requested side is not actual spatialside')
 need(r['DeathMask']==31 and v['native_Death_frames']==[0,1,2,3,4]and v['actual41resident_and9slots_verified']and v['actual_quad_source_projection_and_fullXmirror_verified']and v['actual_white_terminal_material_verified']and v['native_PNG_CRC_FIFO_verified']and v['inventory_and_world_pickup_identity_unchanged']and v['gameplay_and_kernel_clocks_frozen'],'Actual independent Death GPU/terminal/identity gates missing')
 need(v['optical_source_projection']['passed']and not v['optical_source_projection']['registration_search_used']and not v['optical_source_projection']['actual_pixels_modified'],'Fixed source optical PASS required, no alignment or altered pixels')
 need(not r['player_or_Guard_public_damage_used']and not r['HP_poise_clock_actor_writes']and r['guard_final_HP']==185 and r['guard_incoming_count']==0 and v['actual_guard_committed_hits']>1,'Natural Guard lethality scope differs')
 need(r['silent_video']and not r['audio_recorded']and not v['audio_recorded']and not r['visual_reviewed']and not v['visual_reviewed']and r['formal_complete_units']==0 and not v['FinalAccepted'],'Silent unaccepted presentation scope required')
 prereg=Path(session['root_prereg']).resolve();snapshot=Path(session['snapshot']).resolve();need(pin(prereg)['sha256']==session['root_prereg_sha256']and pin(snapshot/'compiled-source-manifest.json')['sha256']==session['snapshot_manifest_sha256'],'Exact actual prereg/snapshot pin differs')
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(result.returncode==0,'Frozen independent readonly re-verification rejected actual inputs: '+result.stderr);need(json.loads(result.stdout)==v,'Retained independent receipt differs from exact readonly rerun')
 rows=[json.loads(x)for x in(original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if x];movie=[x for x in rows if x['file'].startswith('MovieFrame')];frames=[original/x['file']for x in movie]
 need(frames and[f.name for f in frames]==sorted(f.name for f in frames)and{f.name for f in frames}=={f.name for f in original.glob('MovieFrame*.png')},'Original movie sequence missing/duplicate/reordered')
 timing=r['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s'];obs=r['observations']
 need(len(frames)==len(obs)==len(offsets)and all(math.isfinite(t)for t in offsets)and all(b>a for a,b in zip(offsets,offsets[1:]))and not timing['use_fixed_time_step']and duration>offsets[-1]>=offsets[0]>=0,'Actual callback count/monotonic native timeline missing')
 need(all(o['wall_offset_s']==t for o,t in zip(obs,offsets)),'One original observation per PNG callback required')
 selected,join,hold,kinds=select_originals(r,v,frames)
 return r,v,frames,offsets,duration,selected,join,hold,kinds,dict(report=pin(report),independent=pin(proof),session=pin(session_path),official_checker=pin(checker),official_readonly_rerun_passed=True,independent_receipt_PID_and_reportSHA_not_invented=True,observer_freeze=pin(dep),root_prereg=pin(prereg),compiled_manifest=pin(snapshot/'compiled-source-manifest.json'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output');p.add_argument('--validate-only',action='store_true');a=p.parse_args();archive=Path(a.archive).resolve();r,v,frames,offsets,duration,selected,join,hold,kinds,bindings=actual_inputs(archive)
 summary=dict(actual_native_and_independent_input_verified=True,native_frames=len(frames),actual_approach_side=r['actual_approach_side'],five_original_phase_samples=selected,actual_join=join,hold_observation=hold,media_written=False,UE_started=False,visual_reviewed=False)
 if a.validate_only or not join['qualified']:
  print(json.dumps(summary,ensure_ascii=False,indent=2))
  if not join['qualified']:raise SystemExit(3)
  return
 need(a.output,'NEW absolute output leaf required');show=Path(a.output);need(show.is_absolute(),'Output must be absolute');show=show.resolve();need(show!=archive and archive not in show.parents and show not in archive.parents,'Output must be outside readonly native archive');need(not show.exists()and show.parent.is_dir(),'Choose an unused separate leaf whose parent exists');show.mkdir();raw=show/'原件';display=show/'展示副本';raw.mkdir();display.mkdir()
 # MICROSECOND_VFR_BEGIN: unchanged retained Hurt pipeline except output names and directory.
 concat=display/'hero-Death5-native-timing-v001.ffconcat';video=display/'hero-Death5-native-DIAGNOSTIC-silent-v001.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-Death5-v001.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-Death5-v001.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(display/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (display/'decoded-framemd5-Death5-v001.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=display/'decoded-final-frame-Death5-v001.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (display/'presentation-frame-retention-Death5-v001.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # MICROSECOND_VFR_END
 source_rows=[dict(observation=i,native_original=pin(f),wall_offset_s=t,decoded_video_PTS_s=int(decoded_rows[i][2])/1.e6,simulation_time=o['sim'],actual_animation_time=o['animation_time'],callback_phase=o['phase'],native_renderer_kind=kinds[i])for i,(f,t,o)in enumerate(zip(frames,offsets,r['observations']))]
 def copy_native(i,name):
  dest=raw/name;need(not dest.exists(),'Never overwrite a source copy');shutil.copy2(frames[i],dest);need(pin(frames[i])['sha256']==pin(dest)['sha256'],'Original PNG copy changed');
  with Image.open(dest)as im:need(im.format=='PNG'and im.size==(1280,720),'Only actual original1280x720PNG allowed')
  o=r['observations'][i];return dict(observation=i,source=pin(frames[i]),copy=pin(dest),wall_offset_s=offsets[i],simulation_time=o['sim'],callback_phase=o['phase'],actual_animation=o['animation'],actual_animation_time=o['animation_time'],native_renderer_kind=kinds[i],actual_death_draw=o['death_draw'],actual_rendered_stack=o['rendered_stack'],resized=False,pixels_edited=False)
 samples=[]
 for s in selected:
  item=copy_native(s['observation'],f'Death-{s["frame"]:02d}-UNSCALED-native-v001.png');item.update(frame=s['frame'],independent_optical_witness=s['optical_witness']);samples.append(item)
 pair=[copy_native(join[key],f'JOIN-LiveReadyStack-to-Death0-{key}-UNSCALED-native-v001.png')for key in ['before','after']];joined=dict(**join,pair=pair,original_wall_delta_s=offsets[join['after']]-offsets[join['before']],interpolation=False,retimed=False)
 held=copy_native(hold,'Death4-HOLD-native-final-UNSCALED-v001.png')
 # Layout is outside unchanged native rectangles. No resize or painted game pixels.
 full=Image.new('RGB',(1280,5*744),(26,29,34));draw=ImageDraw.Draw(full)
 for n,s in enumerate(samples):
  draw.text((8,n*744+6),f'Death{s["frame"]} | original obs{s["observation"]} | actual age {s["actual_animation_time"]:.9f}',fill='white')
  with Image.open(s['copy']['path'])as im:full.paste(im.convert('RGB'),(0,n*744+24))
 full.save(display/'Death5-FULL-native-unscaled-rows-v001.png')
 contact=Image.new('RGB',(2560,744),(26,29,34));draw=ImageDraw.Draw(contact)
 for n,s in enumerate(pair):
  draw.text((n*1280+8,6),f'{s["native_renderer_kind"]} | original obs{s["observation"]} | wall {s["wall_offset_s"]:.9f}',fill='white')
  with Image.open(s['copy']['path'])as im:contact.paste(im.convert('RGB'),(n*1280,24))
 contact.save(display/'JOIN-LiveReadyStack-to-Death0-native-unscaled-pair-v001.png')
 # Ground-relative constant crop bounds enclose ALL actual submitted quads of five phases.
 bounds=[]
 for s in samples:
  d=s['actual_death_draw'];g=d['context_ground']
  for q in d['slots']:
   x,y=q['top'];w,h=q['size'];px,py=q['rotation_pivot'];cx,cy=x+px*w,y+py*h;a=math.radians(q['rotation']);co,si=math.cos(a),math.sin(a)
   for u,z in [(0,0),(1,0),(0,1),(1,1)]:
    dx,dy=x+u*w-cx,y+z*h-cy;bounds.append((cx+co*dx-si*dy-g[0],cy+si*dx+co*dy-g[1]))
 box=[math.floor(min(x for x,y in bounds))-4,math.floor(min(y for x,y in bounds))-4,math.ceil(max(x for x,y in bounds))+4,math.ceil(max(y for x,y in bounds))+4];cw,ch=box[2]-box[0]+2,box[3]-box[1]+2;sheet=Image.new('RGB',(5*cw,ch+24),(26,29,34));draw=ImageDraw.Draw(sheet);crops=[]
 for n,s in enumerate(samples):
  g=s['actual_death_draw']['context_ground'];b=[math.floor(g[0]+box[0]),math.floor(g[1]+box[1]),math.ceil(g[0]+box[2]),math.ceil(g[1]+box[3])];need(0<=b[0]<b[2]<=1280 and 0<=b[1]<b[3]<=720,'Native source crop would be clipped')
  with Image.open(s['copy']['path'])as im:crop=im.convert('RGB').crop(b)
  path=display/f'Death-{s["frame"]:02d}-NATIVE-PIXEL-CROP-v001.png';crop.save(path);sheet.paste(crop,(n*cw,24));draw.text((n*cw+3,6),f'Death{s["frame"]}',fill='white');crops.append(dict(frame=s['frame'],source=s['source'],source_pixel_crop_box=b,source_ground_relative_box=box,presentation=pin(path),resized=False,painted=False))
 sheet.save(display/'Death5-NATIVE-PIXEL-CROP-contact-v001.png')
 for name in ['runtime-report.json','Death-independent-native-verification-v001.json']:
  shutil.copy2(archive/'原件'/name,raw/name)
 shutil.copy2(archive/'index.json',raw/'native-session-index-readonly-copy.json')
 final=dict(native_original=pin(frames[-1]),native_copy=held,decoded_final=pin(last),decoded_frame_index=len(frames)-1,decode_count_equals_native=True,source_and_decoded_are_separate=True,lossy_video_pixel_equality_not_claimed=True,visual_reviewed=False)
 index=dict(schema='Hero-Death5-native-review-media-source-version-status-v001',status='ACTUAL_NATIVE_AND_INDEPENDENT_PASS_MEDIA_E_AND_VISUAL_REVIEW_PENDING',native_archive=archive.as_posix(),actual_side=r['actual_approach_side'],native_bindings=bindings,media_candidate=pin(C/'Death5-native-review-media-freeze-v001.json'),video=pin(video),native_frame_count=len(frames),source_frames=source_rows,samples=samples,required_sample_count=5,actual_adjacent_join=joined,hold_sample=held,crops=crops,presentation_frame_retention=timing_receipt,final_frame=final,natural_guard_lethal=dict(event=r['lethal_event'],attack=r['lethal_attack'],at=r['lethal_at'],confirmed_HP_loss=r['confirmed_HP_loss'],actual_committed_hits=v['actual_guard_committed_hits']),native_originals_modified=False,native_callback_variable_pacing_preserved=True,simulation_time_used_for_video=False,video_silent=True,audio_recorded=False,visual_reviewed=False,author_floor_or_weapon_contact_or_hidden_socket_measured=False,FinalAccepted=False,formal_complete_units=0,E_before_view_required=True)
 (show/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(raw/'decoded-final-source-association-v001.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'README.md').write_text('同一真实原生记录：Enter/E提交SWD+LGT，前置Knight/Bat明确诊断清除，正常WASD到守卫指定侧，守卫真实连续攻击致主角HP0与一次GameOver；不是正常完整房间通关。五相与最终hold均是原幅1280×720PNG；Live idle与精确Ready资源stack→Death0为真实相邻回调。Probe未记录前一Ready完整DTO/DrawId，因此不冒称该字段，死亡侧有真实Plan/DrawId。全帧VFR静音录像仅使用单调callback墙钟偏移；死亡后simulation/kernel冻结不参与编码。原始PNG、原/解码末帧、全帧SHA索引、PTS/解码数与五相固定光学receipt分别保留。展示拼版只布局原幅或源像素crop，未缩放或重绘游戏像素；视频是有损展示，不能冒原PNG像素相等。作者落剑/Root/axis不是实测接触、物理floor或骨socket。库存和世界掉落未改变；无E保全/View、未审阅、未FinalAccepted。\n',encoding='utf-8')
 print(json.dumps(dict(output=show.as_posix(),video=pin(video),native_frames=len(frames),decoded_frames=len(decoded_rows),max_PTS_error_s=max(errors),samples=len(samples),original_adjacent_joins=1,actual_side=r['actual_approach_side'],decoded_final=pin(last),native_final=pin(frames[-1]),native_archive_modified=False,visual_reviewed=False),ensure_ascii=False))
if __name__=='__main__':main()
