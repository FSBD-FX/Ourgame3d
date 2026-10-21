"""Separate NEW review media from actual Dodge4 native PASS. No archive writes or View."""
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
def checked(row):
 p=Path(row['path']);need(pin(p)==row,'Pinned input differs');return p
def actual_inputs(archive):
 for x in read(C/'Dodge-native-media-freeze-v002.json')['files']:
  p=pin(C/x['path']);need((p['bytes'],p['sha256'])==(x['bytes'],x['sha256']),'Frozen media helper changed')
 contract=read(C/'media-input-contract-v002.json');observer=checked(contract['observer_freeze']);checker=checked(contract['official_checker']);repair=checked(contract['proof_repair_freeze']);checked(contract['VFR_reference_helper']);checked(contract['VFR_reference_freeze'])
 original=archive/'原件';r=read(original/'runtime-report.json');v=read(original/'Dodge-independent-native-verification-v002.json');index=read(archive/'index.json')
 need(index['schema']=='hero-Dodge4-native-session-v001'and index['process_id']==int(r['process_id'])and index['exit_code']==0 and index['native_reported_passed']is True and index['independent_passed']is True and index['candidate_freeze_sha256']==pin(observer)['sha256'],'Actual session/native/independent PASS required')
 need(index['proof_repair_freeze_sha256']==pin(repair)['sha256']and index['proof_repair_checker_sha256']==pin(checker)['sha256']and v['proof_repair_freeze_pin']==pin(repair)and v['proof_repair_checker_pin']==pin(checker),'Exact new proof repair session/receipt binding differs')
 need(r['schema']=='hero-SWD-LGT-Dodge4-native-observer-v001'and r['scenario']=='NormalShiftOutwardUnblockedDodge4'and r['passed']is True and r['flow_complete']is True and v['schema']=='hero-Dodge4-independent-native-v002'and v['passed']is True,'Actual native/schema independent proof failed')
 need(v['process_id']==int(r['process_id'])and v['native_report_pin']==pin(original/'runtime-report.json')and v['native_Dodge_frames']==[0,1,2,3]and r['DodgeMask']==15 and v['original400ms_unblocked185_verified']and v['original60to200ms_iframe_verified']and v['actual33resident_and9slots_verified']and v['actual_quad_source_projection_and_fullXmirror_verified']and v['native_PNG_CRC_FIFO_verified'],'Original clock/33GPU/9quad/PNG proof absent')
 need(r['silent_video']and not r['audio_recorded']and not r['visual_reviewed']and not v['visual_reviewed']and not v['FinalAccepted']and r['formal_complete_units']==0,'Limited silent trial only')
 snapshot=Path(index['snapshot']).resolve();prereg=Path(index['root_prereg']).resolve();need(pin(prereg)['sha256']==index['root_prereg_sha256']and pin(snapshot/'compiled-source-manifest.json')['sha256']==index['snapshot_manifest_sha256'],'Actual prereg/snapshot changed')
 result=subprocess.run([sys.executable,'-B','-X','utf8',str(checker),'--snapshot',str(snapshot),'--root-prereg',str(prereg),'--archive',str(archive)],capture_output=True,text=True,encoding='utf-8');need(result.returncode==0,'Exact readonly official recheck failed: '+result.stderr);need(json.loads(result.stdout)==v,'Exact readonly recheck differs from retained receipt')
 rows=[json.loads(s)for s in(original/'native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines()if s];movie=[x for x in rows if x['file'].startswith('MovieFrame')];frames=[original/x['file']for x in movie]
 need(frames and[f.name for f in frames]==sorted(f.name for f in frames)and{f.name for f in frames}=={f.name for f in original.glob('MovieFrame*.png')},'Original movie frame membership/order differs')
 timing=r['capture_timing'];offsets=timing['frame_wall_offsets_s'];duration=timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s'];obs=r['observations']
 need(len(frames)==len(offsets)==len(obs)and all(math.isfinite(t)for t in offsets)and all(b>a for a,b in zip(offsets,offsets[1:]))and duration>offsets[-1]>=offsets[0]>=0 and not timing['use_fixed_time_step']and all(o['wall_offset_s']==t for o,t in zip(obs,offsets)),'Actual one observation/PNG variable callback timeline differs')
 byname={f.name:i for i,f in enumerate(frames)};witnesses=v['optical_source_projection']['source_registered_native_witnesses'];need(len(witnesses)==4,'Four source optical witnesses required');samples=[]
 for frame in range(4):
  ws=[w for w in witnesses if w['frame']==frame];need(len(ws)==1,'Missing/duplicate optical phase witness');w=ws[0];i=byname[w['original_PNG']];o=obs[i];d=o['dodge_draw']
  need(o['phase']==9 and o['dodge_query_ok']and d['drawn']and d['frame']==frame and d['draw_id']==w['native_draw_id']and d['dodge_action']==r['dodge_action'],'Original exact optical witness not SAME action/phase/DrawId');samples.append(dict(frame=frame,observation=i,optical_witness=w))
 joins=[]
 for frame in range(3):
  edges=[i for i in range(len(obs)-1)if obs[i]['dodge_query_ok']and obs[i+1]['dodge_query_ok']and obs[i]['dodge_draw']['frame']==frame and obs[i+1]['dodge_draw']['frame']==frame+1]
  need(len(edges)==1,'Original Dodge phase transition not one adjacent callback pair');i=edges[0];joins.append(dict(kind=f'Dodge{frame}_to_Dodge{frame+1}',from_observation=i,to_observation=i+1))
 need([e['kind']for e in v['actual_adjacent_joins']]==['Dodge3_to_Ready','Ready_to_Walk'],'Original actual Ready/Walk edges absent')
 joins+=v['actual_adjacent_joins']
 for edge in joins:need(edge['to_observation']==edge['from_observation']+1,'Missing callback cannot be turned into a join')
 bindings=dict(native_report=pin(original/'runtime-report.json'),independent=pin(original/'Dodge-independent-native-verification-v002.json'),session=pin(archive/'index.json'),official_checker=pin(checker),observer_freeze=pin(observer),root_prereg=pin(prereg),compiled_manifest=pin(snapshot/'compiled-source-manifest.json'),official_readonly_rerun_passed=True)
 return r,v,frames,offsets,duration,samples,joins,bindings

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--output');p.add_argument('--validate-only',action='store_true');a=p.parse_args();archive=Path(a.archive).resolve();r,v,frames,offsets,duration,selected,joins,bindings=actual_inputs(archive)
 if a.validate_only:print(json.dumps(dict(actual_native_and_independent_verified=True,native_frames=len(frames),original_phase_samples=selected,original_adjacent_joins=joins,media_written=False,UE_started=False,visual_reviewed=False),ensure_ascii=False));return
 need(a.output,'NEW absolute output leaf required');show=Path(a.output);need(show.is_absolute(),'Absolute output required');show=show.resolve();need(show!=archive and archive not in show.parents and show not in archive.parents,'Output must remain separate from readonly native archive');need(not show.exists()and show.parent.is_dir(),'Unused output leaf whose parent exists required');show.mkdir();raw=show/'原件';display=show/'展示副本';raw.mkdir();display.mkdir()
 # MICROSECOND_VFR_BEGIN
 concat=display/'hero-Dodge4-native-timing-v002.ffconcat';video=display/'hero-Dodge4-native-DIAGNOSTIC-silent-v002.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-Dodge4-v002.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-Dodge4-v002.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(display/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (display/'decoded-framemd5-Dodge4-v002.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=display/'decoded-final-frame-Dodge4-v002.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (display/'presentation-frame-retention-Dodge4-v002.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 # MICROSECOND_VFR_END
 def copy_native(i,name):
  dest=raw/name;shutil.copy2(frames[i],dest);need(pin(dest)['sha256']==pin(frames[i])['sha256'],'Original PNG copy differs')
  with Image.open(dest)as im:need(im.format=='PNG'and im.size==(1280,720),'Native original viewport dimensions differ')
  o=r['observations'][i];return dict(observation=i,source=pin(frames[i]),copy=pin(dest),wall_offset_s=offsets[i],simulation_time=o['sim'],actual_animation=o['animation'],actual_animation_time=o['animation_time'],Dodge_record=o['dodge_record'],Dodge_draw=o['dodge_draw'],ordinary_join_draw=o['join_draw'],actual_rendered_stack=o['rendered_stack'],resized=False,pixels_edited=False)
 samples=[]
 for s in selected:
  row=copy_native(s['observation'],f'Dodge-{s["frame"]:02d}-UNSCALED-native-v002.png');row.update(frame=s['frame'],independent_optical_witness=s['optical_witness']);samples.append(row)
 joined=[]
 for edge in joins:
  pair=[copy_native(edge[key],f'JOIN-{edge["kind"]}-{key}-UNSCALED-native-v002.png')for key in ['from_observation','to_observation']];joined.append(dict(**edge,pair=pair,original_adjacent_callbacks=True,intervening_native_frames=0,original_wall_delta_s=offsets[edge['to_observation']]-offsets[edge['from_observation']],interpolation=False,retimed=False))
 full=Image.new('RGB',(1280,4*744),(26,29,34));draw=ImageDraw.Draw(full)
 for n,s in enumerate(samples):
  draw.text((8,n*744+6),f'Dodge{s["frame"]} | original obs{s["observation"]} | actual age{s["Dodge_draw"]["dodge_elapsed"]:.9f}',fill='white')
  with Image.open(s['copy']['path'])as im:full.paste(im.convert('RGB'),(0,n*744+24))
 full.save(display/'Dodge4-FULL-native-unscaled-rows-v002.png')
 for edge in joined:
  board=Image.new('RGB',(2560,744),(26,29,34));draw=ImageDraw.Draw(board)
  for n,s in enumerate(edge['pair']):
   draw.text((n*1280+8,6),f'{edge["kind"]} | original obs{s["observation"]} | wall{s["wall_offset_s"]:.9f}',fill='white')
   with Image.open(s['copy']['path'])as im:board.paste(im.convert('RGB'),(n*1280,24))
  board.save(display/f'JOIN-{edge["kind"]}-native-unscaled-pair-v002.png')
 lastcopy=copy_native(len(frames)-1,'native-final-UNSCALED-v002.png')
 for name in ['runtime-report.json','Dodge-independent-native-verification-v002.json']:shutil.copy2(archive/'原件'/name,raw/name)
 shutil.copy2(archive/'index.json',raw/'native-session-index-readonly-copy.json')
 source_rows=[dict(observation=i,native_original=pin(f),wall_offset_s=t,decoded_video_PTS_s=int(decoded_rows[i][2])/1.e6,simulation_time=o['sim'],callback_phase=o['phase'],actual_animation=o['animation'],actual_animation_time=o['animation_time'])for i,(f,t,o)in enumerate(zip(frames,offsets,r['observations']))]
 final=dict(native_original=pin(frames[-1]),native_copy=lastcopy,decoded_final=pin(last),decoded_frame_index=len(frames)-1,decode_count_equals_native=True,source_and_decoded_are_separate=True,lossy_video_pixel_equality_not_claimed=True,visual_reviewed=False)
 index=dict(schema='Hero-Dodge4-native-review-media-source-version-status-v002',status='ACTUAL_NATIVE_AND_INDEPENDENT_PASS_E_AND_VISUAL_REVIEW_PENDING',native_archive=archive.as_posix(),actual_side=r['actual_approach_side'],native_bindings=bindings,media_candidate=pin(C/'Dodge-native-media-freeze-v002.json'),video=pin(video),native_frame_count=len(frames),source_frames=source_rows,samples=samples,required_sample_count=4,actual_adjacent_joins=joined,required_join_count=5,presentation_frame_retention=timing_receipt,final_frame=final,native_originals_modified=False,native_callback_variable_pacing_preserved=True,simulation_time_used_for_video=False,video_silent=True,audio_recorded=False,visual_reviewed=False,native_backwards_covered=False,blocked_native_covered=False,author_floor_or_weapon_contact_or_hidden_socket_measured=False,FinalAccepted=False,formal_complete_units=0,E_before_view_required=True)
 (show/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(raw/'decoded-final-source-association-v002.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'README.md').write_text('真实正常Enter/E提交SWD+LGT，Knight/Bat明确诊断清除；计划出生Guard185无受击。正常WASD绕侧±140后一次向外Shift，真实400ms/185world，4相及5组真实相邻回调。只覆盖向外无阻；后退/受阻/中断不是本录像覆盖。样本/joins均是原幅1280×720PNG与单调callback墙钟VFR静音展示；不丢/重帧，末帧源/有损解码分别留档，仿真时钟不参与编码。拼板只在原游戏矩形外加标签，无缩放/重绘。作者Root/Grip/axis并非骨socket/足锁；人物/剑/甲片衔接待Root E后实际View，无音色/正式接受声明。\n',encoding='utf-8')
 print(json.dumps(dict(output=show.as_posix(),native_frames=len(frames),decoded_frames=len(decoded_rows),original_samples=len(samples),original_adjacent_joins=len(joined),native_archive_modified=False,visual_reviewed=False),ensure_ascii=False))
if __name__=='__main__':main()
