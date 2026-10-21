"""Versioned Known44 normal-J Death presentation only; original native offsets/pixels remain untouched."""
from pathlib import Path
import argparse,hashlib,json,math,shutil,subprocess
import imageio_ffmpeg
from PIL import Image
C=Path(__file__).resolve().parent.parent

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def qualified_choices(r,v):
 did=str(r['death_event_id']);obs=r['observations'];choices={};seen=set()
 for w in v['coverage_witnesses']:
  i=w['observation'];assert type(i) is int and 0<=i<len(obs)
  o=obs[i];ds=[d for d in o['guard_draws'] if d['DrawId']==w['DrawId'] and str(d['EntityId'])==str(r['guard_entity'])];assert len(ds)==1
  d=ds[0];s=d['Selection'];frame=s['Frame'];n=o['guard_native'];stamp=s['SampleTime'];age=stamp-r['death_at']
  assert s['Clip']=='Death' and type(frame) is int and 0<=frame<6 and str(d['DrawId']) not in seen;seen.add(str(d['DrawId']))
  assert d['Drawn'] is True and d['SpatialCoverageEligible'] is True and d['DrawStack']==[d['TexturePath']]
  assert w['clip']=='Death' and w['frame']==frame and w['sample']==stamp and str(w['AttackId'])==str(s['AttackId']) and str(w['SourceEventId'])==str(s['SourceEventId'])==did
  assert w['player']==o['player_ground'] and w['guard']==n['ground'] and w['object']==d['TexturePath']
  assert n['dead'] is True and n['HP']==0 and n['phase']==s['Phase']==7 and o['player_HP']>0 and o['phase']=='normal_guard_J_Death_and_coin' and o['approach_spatial']['route_reached'] is True
  side=r['actual_approach_side'];assert side in [-1,1] and 90<=side*(o['player_ground'][0]-n['ground'][0])<=155 and abs(o['player_ground'][1]-n['ground'][1])<=20
  assert s['IntervalStart']==r['death_at'] and s['IntervalEnd']==r['death_at']+1. and 0<=age<1. and abs(s['DeathAge']-age)<=1.e-8 and s['DeathAfterglow']==(age<.1)
  assert frame==sum(stamp>=r['death_at']+x for x in [.1,.2,.35,.55,.75])
  choices.setdefault(frame,[]).append((i,d,w))
 for frame in range(6):assert choices.get(frame),('Missing independently qualified original1s Death sample',frame)
 return choices

def adjacent_joins(choices):
 joins=[]
 for frame in range(5):
  pairs=[(l,r) for l in choices[frame] for r in choices[frame+1] if r[0]==l[0]+1]
  assert len(pairs)==1,('Missing/ambiguous original adjacent Death phase pair; no nonadjacent or held-last substitution',frame,frame+1)
  joins.append((frame,*pairs[0]))
 return joins

def coin_states(r,v):
 a=v['automatic_reward'];oid=str(a['coin_object_id']);op=str(a['collection_operation_id']);obs=r['observations']
 assert oid==str(r['coin_object_id']) and op==str(r['coin_operation_id']) and a['collected_at']==r['coin_collected_at'] and a['before']==r['coin_before'] and a['after']==r['coin_after']==a['before']+9
 rewards=r['rewards_final'];coins=[x for x in rewards['Objects'] if str(x['ObjectId'])==oid];cols=[x for x in rewards['Collections'] if str(x['ObjectId'])==oid]
 assert len(coins)==len(cols)==1;coin=coins[0];col=cols[0]
 assert coin['Kind']==0 and coin['Amount']==9 and coin['Consumed'] is True and coin['Retired'] is False and str(coin['CollectionOperationId'])==op
 assert str(col['OperationId'])==op and str(col['SourceId'])==str(coin['SourceId']) and str(col['OwnerId'])==str(r['owner']) and col['AtTime']==a['collected_at'] and col['BeforeCoins']==a['before'] and col['AfterCoins']==a['after'] and col['AtTime']>=r['death_at']+1.
 consumed=[]
 for i,o in enumerate(obs):
  xs=[x for x in o['rewards']['Objects'] if str(x['ObjectId'])==oid]
  assert len(xs)<=1
  if xs and xs[0]['Consumed']:consumed.append(i)
 i=a['first_consumed_observation'];assert type(i) is int and i>0 and consumed and consumed[0]==i and consumed==list(range(i,len(obs)))
 after=obs[i];before=obs[i-1];prior=[x for x in before['rewards']['Objects'] if str(x['ObjectId'])==oid]
 assert len(prior)==1 and prior[0]['Consumed'] is False and prior[0]['Amount']==9 and prior[0]['SourceId']==coin['SourceId']
 assert before['guard_native']['dead'] and before['guard_native']['HP']==0 and after['wallet']==a['after']
 prior_collections=before['rewards']['Collections'];after_collections=after['rewards']['Collections']
 assert after_collections[:len(prior_collections)]==prior_collections
 new_collections=after_collections[len(prior_collections):];assert new_collections and len([x for x in new_collections if str(x['OperationId'])==op])==1
 objects={str(x['ObjectId']):x for x in after['rewards']['Objects']};wallet=before['wallet'];callback_chain=[]
 for x in new_collections:
  obj=objects[str(x['ObjectId'])];assert obj['Kind']==0 and obj['Consumed'] and obj['Amount']>0 and str(obj['CollectionOperationId'])==str(x['OperationId']) and str(obj['SourceId'])==str(x['SourceId']) and str(x['OwnerId'])==str(r['owner'])
  assert x['BeforeCoins']==wallet and x['AfterCoins']==wallet+obj['Amount'];wallet=x['AfterCoins'];callback_chain.append(dict(collection=x,amount=obj['Amount'],is_Guard_coin=str(x['ObjectId'])==oid))
 assert wallet==after['wallet']
 assert after['player_ground']==a['automatic_collection_position'] and after['player_HP']>0 and abs(after['player_ground'][0]-coin['Position'][0])<=60 and abs(after['player_ground'][1]-coin['Position'][1])<=30
 final=obs[-1];assert final['phase']=='complete' and final['room_cleared'] and final['wallet']==r['wallet'] and final['guard_native']['dead'] and final['guard_native']['HP']==0 and final['guard_native']['death_settled'] and final['guard_native']['reward_claimed']
 return [('before-pickup',i-1),('first-auto-collected',i),('final-state',len(obs)-1)],dict(coin=coin,collection=col,independent_automatic_reward=a,actual_adjacent_callback_before_wallet=before['wallet'],actual_adjacent_callback_after_wallet=after['wallet'],collections_between_callbacks=callback_chain,Guard_before_is_intermediate_ledger_state=before['wallet']!=a['before'],no_intermediate_wallet_callback_fabricated=True,final_wallet=r['wallet'])

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';contract=read(C/'media-input-contract-v001.json')
 for row in read(C/'Death-media-freeze-v001.json')['files']:assert pin(C/row['path'])['sha256']==row['sha256'] and (C/row['path']).stat().st_size==row['bytes']
 dep=contract['exact_independent_source_tooling_freeze'];assert pin(Path(dep['path']))==dep
 report=original/'runtime-report.json';proof=original/contract['independent_receipt'];r=read(report);v=read(proof);session=read(archive/'index.json')
 assert session['schema']==contract['native_session_schema'] and session['candidate_freeze_sha256']==dep['sha256'] and str(session['process_id'])==r['process_id'] and session['exit_code']==0 and session['native_reported_passed'] is True and session['independent_passed'] is True
 assert r['schema']==contract['native_report_schema'] and r['scenario']==contract['scenario']=='Death' and r['passed'] is True and r['flow_complete'] is True and v['passed'] is True
 assert v['native_report_sha256']==pin(report)['sha256'] and str(v['process_id'])==r['process_id'] and v['run']==r['run']
 assert r['death_pinned'] is True and str(v['death_event_id'])==str(r['death_event_id']) and v['death_at']==r['death_at'] and v['masks']=={'Death':63} and r['DeathMask']==63 and r['coin_collected'] is True
 assert r['normal_J_full_clear'] is False and r['guard_public_damage_used'] is False and r['guard_normal_J_only'] is True and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False and r['player_damage_preserved'] is True and r['guard_final_HP']==0 and r['player_final_HP']>0 and r['spatial_approach']['route_reached'] is True
 assert r['silent_video'] is True and r['audio_recorded'] is False and r['visual_reviewed'] is False and v['visual_reviewed'] is False and r['formal_complete_units']==v['formal_complete_units']==0
 assert v['pixel_proof']['passed'] and v['pixel_proof']['native_async_writer_verified'] and v['pixel_proof']['every_source_viewport_pixel_crc_matches']
 frames=sorted(original.glob('MovieFrame*.png'));assert len(frames)==v['native_frames']==len(r['observations']) and v['pixel_proof']['verified_original_PNG_count']==len(frames)+1
 offsets=r['capture_timing']['frame_wall_offsets_s'];assert len(offsets)==len(frames) and all(math.isfinite(x) for x in offsets) and all(y>x for x,y in zip(offsets,offsets[1:])) and r['capture_timing']['use_fixed_time_step'] is False and r['duration_s']>offsets[-1]
 assert all(abs(o['wall_offset_s']-t)<=1.e-8 for o,t in zip(r['observations'],offsets))
 choices=qualified_choices(r,v);boundaries=adjacent_joins(choices);gold_states,gold=coin_states(r,v)
 if a.validate_only:
  print(json.dumps(dict(actual_input_contract_verified=True,qualified_sample_keys=len(choices),required_samples=6,original_adjacent_join_pairs=len(boundaries),real_coin_amount=gold['coin']['Amount'],coin_before=gold['collection']['BeforeCoins'],coin_after=gold['collection']['AfterCoins'],final_wallet=r['wallet'],native_frames=len(frames),media_written=False,UE_started=False,visual_reviewed=False)));return
 show.mkdir(exist_ok=True)
 assert not (archive/'source-version-status-index.json').exists() and not (archive/'README.md').exists(),'Never overwrite prior presentation index'
 assert not any(show.glob('*Death*v001*')),'Never overwrite earlier media; use a fresh capture/version'

 frames=sorted(original.glob('MovieFrame*.png'));offsets=r['capture_timing']['frame_wall_offsets_s'];duration=r['duration_s']
 assert len(frames)==len(offsets)==len(r['observations']) and duration>offsets[-1]
 concat=show/'guard-known44-Death-native-timing-v001.ffconcat';video=show/'guard-known44-Death-native-DIAGNOSTIC-silent-v001.mp4'
 assert not concat.exists() and not video.exists()
 lines=['ffconcat version 1.0']
 for i,f in enumerate(frames):
  dt=(offsets[i+1] if i+1<len(frames) else duration)-offsets[i];assert dt>0
  lines += ["file '"+f.as_posix().replace("'","'\\''")+"'",'option framerate 1000000',f'duration {dt:.12f}']
 lines += ["file '"+frames[-1].as_posix().replace("'","'\\''")+"'",'option framerate 1000000']
 concat.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 ff=imageio_ffmpeg.get_ffmpeg_exe()
 for name,cmd in [('encode-Death-v001.log',[ff,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','0','-i',str(concat),'-fps_mode','passthrough','-enc_time_base','1:1000000','-video_track_timescale','1000000','-t',f'{duration-offsets[0]:.9f}','-frames:v',str(len(frames)),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-an',str(video)]),('decode-Death-v001.log',[ff,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'])]:
  result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');(show/name).write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,(name,result.stderr)
 decoded=subprocess.run([ff,'-hide_banner','-loglevel','error','-i',str(video),'-enc_time_base','1:1000000','-fps_mode','passthrough','-f','framemd5','-'],capture_output=True,text=True,encoding='utf-8')
 assert decoded.returncode==0,decoded.stderr
 (show/'decoded-framemd5-Death-v001.txt').write_text(decoded.stdout,encoding='utf-8')
 decoded_rows=[line.split(',') for line in decoded.stdout.splitlines() if line and not line.startswith('#')]
 assert len(decoded_rows)==len(frames),('Presentation dropped/added frames',len(decoded_rows),len(frames))
 assert '#tb 0: 1/1000000' in decoded.stdout
 errors=[abs(int(row[2])/1.e6-(stamp-offsets[0])) for row,stamp in zip(decoded_rows,offsets)]
 assert max(errors)<=len(frames)*1.e-6+2.e-6,('Presentation timestamps exceed derived concat rounding bound',max(errors))
 last=show/'decoded-final-frame-Death-v001.png'
 end=subprocess.run([ff,'-hide_banner','-loglevel','error','-n','-i',str(video),'-vf',f'select=eq(n\\,{len(frames)-1})','-fps_mode','passthrough','-frames:v','1',str(last)],capture_output=True,text=True,encoding='utf-8')
 assert end.returncode==0 and last.is_file(),end.stderr
 with Image.open(last) as im:assert im.size==(1280,720)
 timing_receipt=dict(decoded_frames=len(decoded_rows),native_frames=len(frames),every_native_frame_has_one_encoded_frame=True,microsecond_encoder_and_track_timebase=True,maximum_timestamp_rounding_error_s=max(errors),derived_rounding_bound_s=len(frames)*1.e-6+2.e-6,decoded_last_frame=pin(last),native_last_frame=pin(frames[-1]),lossy_presentation=True,visual_reviewed=False)
 (show/'presentation-frame-retention-Death-v001.json').write_text(json.dumps(timing_receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 
 samples=[]
 def copy_native(i,dest):
  src=frames[i];assert not dest.exists();shutil.copy2(src,dest);assert pin(src)['sha256']==pin(dest)['sha256']
  with Image.open(dest) as im:assert im.format=='PNG' and im.size==(1280,720)
  return dict(frame_index=i,source=pin(src),presentation=pin(dest),wall_offset_s=offsets[i],resized=False)
 def selected_item(x,dest):
  i,d,w=x;item=copy_native(i,dest);s=d['Selection']
  item.update(clip='Death',frame=s['Frame'],AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],sample_time=s['SampleTime'],DeathAge=s['DeathAge'],DeathAfterglow=s['DeathAfterglow'],interval_start=s['IntervalStart'],interval_end=s['IntervalEnd'],death_event_id=r['death_event_id'],coverage_witness=w,source_object=d['TexturePath']);return item
 for frame in range(6):
  pool=choices[frame];samples.append(selected_item(pool[len(pool)//2],show/f'Death-{frame:02d}-UNSCALED-Death-v001.png'))
 joins=[]
 for phase,left,right in boundaries:
  li,ri=left[0],right[0];name=f'Death{phase}-to-Death{phase+1}'
  pair=[selected_item(x,show/f'JOIN-{name}-{label}-UNSCALED-Death-v001.png') for label,x in [('before',left),('after',right)]]
  joins.append(dict(join=name,pair=pair,original_adjacent_callbacks=True,intervening_native_frames=0,original_wall_delta_s=offsets[ri]-offsets[li],death_event_id=r['death_event_id'],interpolation=False,join_visual_accepted=False))
 assert len(samples)==6 and len(joins)==5
 states=[]
 for label,i in gold_states:
  o=r['observations'][i];item=copy_native(i,show/f'COIN-{label}-UNSCALED-Death-v001.png')
  item.update(state=label,sim=o['sim'],player=o['player_ground'],player_HP=o['player_HP'],wallet=o['wallet'],guard_native=o['guard_native'],original_rewards=o['rewards'],amount_overlay_added=False);states.append(item)
 gold.update(original_callback_states=states,source_amount9_is_metadata_not_fake_HUD_text=True,visual_reviewed=False)
 (show/'automatic-coin-state-Death-v001.json').write_text(json.dumps(gold,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (show/'join-candidates-Death-v001.json').write_text(json.dumps(dict(schema='known44-Death-native-join-candidates-v001',pairs=joins,required_pairs=5,all_original_adjacent_callbacks=True,visual_reviewed=False,scope='Only the five consecutive original native Death phase transitions inside the original1s interval; same Died event. No montage/retime/interpolation.'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 index=dict(schema='guard-known44-Death-native-media-v001',status='NATIVE_NORMAL_J_DEATH_AND_AUTOMATIC_COIN_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),session=pin(archive/'index.json'),media_candidate=pin(C/'Death-media-freeze-v001.json'),presentation_frame_retention=timing_receipt,samples=samples,required_sample_count=6,joins=joins,required_adjacent_join_count=5,automatic_coin=gold,procedural_gap_seen=r['procedural_gap_seen'],death_event_id=r['death_event_id'],death_at=r['death_at'],Death_art_duration_s=1.,Death_first_afterglow_s=.1,gameplay_death_delay_s=0,actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged_and_killed_by_normal_J=True,guard_final_HP=0,player_final_HP=r['player_final_HP'],player_damage_preserved=True,audio_recorded=False,visual_reviewed=False,E_before_view_required=True,formal_complete_units=0,render_callback_asset_pixel_attribution='Qualified actual original1s observation and native viewport CRC; Root must E preserve then actually View source-specific pixels/collapse-root/join quality. No all44-rendered/all57/final-art claim.')
 (archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (archive/'README.md').write_text('正常军剑J真实死亡与自动金币试样：Knight/Bat公开诊断清除；Guard仅正常J至原生Died/HP0，玩家实际损伤保留。同一Died原1秒Death6张1280×720原幅PNG，五个原相邻回调phase转场，原总时序完整静音录像及解码末帧。另复制真实coin9拾取前／首次自动收取／最终状态三张原幅图，金额及钱包只从真实ledger记录、不加伪HUD文字。相邻帧或合格相缺失拒绝；尚待E保全与实际View，不是全44/57、完整正常战斗、足锁、音效或最终美术验收。\n',encoding='utf-8')
 print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),join_pairs=len(joins),coin_state_samples=len(states),coin_amount=9,coin_before=r['coin_before'],coin_after=r['coin_after'],final_wallet=r['wallet'],duration_s=duration-offsets[0],visual_reviewed=False)))

if __name__=='__main__':main()
