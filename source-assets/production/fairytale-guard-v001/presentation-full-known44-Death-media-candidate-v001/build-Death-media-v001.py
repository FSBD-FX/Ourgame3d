"""Prepare immutable media tool only. No native process, media decode/encode or View."""
from pathlib import Path
import ast,copy,hashlib,json,shutil
C=Path(__file__).resolve().parent;R=C.parents[3]
S=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-StunIR-media-candidate-v001'
D=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-combat-death-candidate-v006'
assert not (C/'Death-media-freeze-v001.json').exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(n,t):
 p=C/n;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
def js(n,v):write(n,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
for root,freeze in [(S,'StunIR-media-freeze-v001.json'),(D,'Death-candidate-freeze-v006.json')]:
 for x in read(root/freeze)['files']:
  p=root/x['path'];assert p.stat().st_size==x['bytes'] and pin(p)['sha256']==x['sha256']
dep=pin(D/'Death-candidate-freeze-v006.json');assert dep['sha256']=='0b8db789657b07945dd4abd8777218f0ec29a21b9a1da41186550b9d8056701b'
old=(S/'tooling/prepare-StunIR-native-media-v001.py').read_text(encoding='utf-8-sig')
head=old[:old.index('def qualified_choices')].replace('normal-J StunIR','normal-J Death')
qual='''def qualified_choices(r,v):
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

'''
start=old.index(" frames=sorted(original.glob('MovieFrame*.png'));offsets=");end=old.index(' samples=[]',start)
pipeline=old[start:end].replace('StunIR','Death')
tail=''' samples=[]
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
 (show/'automatic-coin-state-Death-v001.json').write_text(json.dumps(gold,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
 (show/'join-candidates-Death-v001.json').write_text(json.dumps(dict(schema='known44-Death-native-join-candidates-v001',pairs=joins,required_pairs=5,all_original_adjacent_callbacks=True,visual_reviewed=False,scope='Only the five consecutive original native Death phase transitions inside the original1s interval; same Died event. No montage/retime/interpolation.'),ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
 index=dict(schema='guard-known44-Death-native-media-v001',status='NATIVE_NORMAL_J_DEATH_AND_AUTOMATIC_COIN_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),session=pin(archive/'index.json'),media_candidate=pin(C/'Death-media-freeze-v001.json'),presentation_frame_retention=timing_receipt,samples=samples,required_sample_count=6,joins=joins,required_adjacent_join_count=5,automatic_coin=gold,procedural_gap_seen=r['procedural_gap_seen'],death_event_id=r['death_event_id'],death_at=r['death_at'],Death_art_duration_s=1.,Death_first_afterglow_s=.1,gameplay_death_delay_s=0,actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged_and_killed_by_normal_J=True,guard_final_HP=0,player_final_HP=r['player_final_HP'],player_damage_preserved=True,audio_recorded=False,visual_reviewed=False,E_before_view_required=True,formal_complete_units=0,render_callback_asset_pixel_attribution='Qualified actual original1s observation and native viewport CRC; Root must E preserve then actually View source-specific pixels/collapse-root/join quality. No all44-rendered/all57/final-art claim.')
 (archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
 (archive/'README.md').write_text('正常军剑J真实死亡与自动金币试样：Knight/Bat公开诊断清除；Guard仅正常J至原生Died/HP0，玩家实际损伤保留。同一Died原1秒Death6张1280×720原幅PNG，五个原相邻回调phase转场，原总时序完整静音录像及解码末帧。另复制真实coin9拾取前／首次自动收取／最终状态三张原幅图，金额及钱包只从真实ledger记录、不加伪HUD文字。相邻帧或合格相缺失拒绝；尚待E保全与实际View，不是全44/57、完整正常战斗、足锁、音效或最终美术验收。\\n',encoding='utf-8')
 print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),join_pairs=len(joins),coin_state_samples=len(states),coin_amount=9,coin_before=r['coin_before'],coin_after=r['coin_after'],final_wallet=r['wallet'],duration_s=duration-offsets[0],visual_reviewed=False)))

if __name__=='__main__':main()
'''
source=head+qual+pipeline+tail;ast.parse(source);write('tooling/prepare-Death-native-media-v001.py',source)
for name in ['prepare-guard-partial-native-media-v011-READONLY-REFERENCE.py','tooling/native-v011-timing-pipeline-REFERENCE-fragment.txt']:
 target=C/name;assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(S/name,target);assert pin(target)['sha256']==pin(S/name)['sha256']
js('media-input-contract-v001.json',dict(schema='known44-Death-media-input-contract-v001',native_report_schema='guard-art-known44-death-observer-v005',native_session_schema='guard-art-known44-death-session-v005',scenario='Death',independent_receipt='independent-Death-v005.json',exact_independent_source_tooling_freeze=dep,required_samples={'Death':6},required_original_adjacent_joins=5,same_original_Died_event_required=True,Death_original_duration_s=1.,Death_first_afterglow_s=.1,phase_starts_s=[0.,.1,.2,.35,.55,.75],held_last_after1s_cannot_repair_coverage=True,real_automatic_coin_amount=9,real_coin_state_samples=['before-pickup','first-auto-collected','final-state'],amount_or_wallet_overlay_allowed=False,UE_started=False,ffmpeg_started=False,View_used=False,formal_complete_units=0))
write('HANDOFF.md','''# Death media v001（仅候选；未编码/View）

严格接收Death observer/tooling v006 freeze `0b8db789657b07945dd4abd8777218f0ec29a21b9a1da41186550b9d8056701b`；native/session及independent receipt仍v005。session必须exit0/nativePASS/independentPASS；报告SHA、PID/run、Died事件、Mask63、原1秒/100ms余辉和真实coin9 receipt一致，不能拿在跑的index或失败报告生成PASS展示。

Death0..5六原幅1280×720 PNG都来自同一原Died且原 `[death_at,death_at+1)` 的独立coverage_witnesses，保留真实DrawId/SourceEventId/原clock/source/位置。原1秒后的保持末帧不能补相。五个phase边界0→1→2→3→4→5各必须有且仅有原连续callback i→i+1合格对，缺任何相邻对即validate-only失败，绝不借非相邻、后续保持帧或插值假造。copy十张join原幅PNG，不做裁剪/缩放/像素修改。

真实自动coin额外copy三张原幅：首次consumed之前紧邻一帧、首次consumed、最终complete；记录各实际sim/HP/ground/wallet与Rewards原文。coin9、operation/source/owner、before→after+9和真实拾取位置均核同一independent自动拾取见证；最终钱包照原件，不硬写29。金额只写metadata，不在无UI原图上补伪数字。只正常J Guard，Knight/Bat仍诊断，不能据此称三敌正常全战。

完整视频沿已实际用过的StunIR/v011 VFR原时基，微秒PTS、原总duration、frames:v原数cap、framemd5数量/PTS舍入上界、解码末帧1280×720全保留。仅输出文件命名从StunIR换Death。MP4是静音有损展示副本，原PNG不改。全部展示输出与archive README/source-version-status-index必须先不存在，拒绝覆盖。生成后Root先E保全，再实际View；此候选没有启动UE/UBT/ffmpeg/View。

Root命令：项目Python `-B -X utf8` 执行本目录 `tooling/prepare-Death-native-media-v001.py --archive '<absolute completed native archive>' --validate-only`。通过后去掉validate-only才编码/复制。Root当前native_left_v001尚在跑时仅能确认session协议与freeze pin，不能预报native或独立PASS。实际终局后再作只读host核对。
''')
# Parser/selector boundary fixtures only; never save a synthetic native report or media.
node=ast.parse(source);ns={};defs=[n for n in node.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.FunctionDef) and n.name in ['qualified_choices','adjacent_joins','coin_states']];exec(compile(ast.Module(body=defs,type_ignores=[]),'contract-only','exec'),ns)
r=dict(death_event_id='20',death_at=10.,guard_entity='3',actual_approach_side=-1,observations=[]);v={'coverage_witnesses':[]};starts=[0.,.1,.2,.35,.55,.75,1.]
for frame in range(6):
 stamp=10.+(starts[frame]+starts[frame+1])/2.;d=dict(DrawId=str(frame+1),EntityId='3',Drawn=True,SpatialCoverageEligible=True,DrawStack=['/test'],TexturePath='/test',Selection=dict(Clip='Death',Frame=frame,SampleTime=stamp,AttackId='7',SourceEventId='20',Phase=7,IntervalStart=10.,IntervalEnd=11.,DeathAge=stamp-10.,DeathAfterglow=stamp-10.<.1))
 o=dict(guard_draws=[d],guard_native=dict(dead=True,HP=0,phase=7,ground=[0,0]),player_HP=78,player_ground=[-125,0],phase='normal_guard_J_Death_and_coin',approach_spatial={'route_reached':True});r['observations'].append(o);v['coverage_witnesses'].append(dict(observation=frame,DrawId=str(frame+1),clip='Death',frame=frame,sample=stamp,AttackId='7',SourceEventId='20',player=[-125,0],guard=[0,0],object='/test'))
choices=ns['qualified_choices'](r,v);assert len(choices)==6 and len(ns['adjacent_joins'](choices))==5;cases=['all6_same_Died_original_window_and5_adjacent_pairs']
def reject(name,mutator):
 rr,vv=copy.deepcopy((r,v));mutator(rr,vv)
 try:ns['qualified_choices'](rr,vv)
 except (AssertionError,KeyError,ValueError):cases.append(name);return
 raise AssertionError('Invalid contract accepted: '+name)
reject('other_Died_rejected',lambda rr,vv:rr.update(death_event_id='21'))
reject('missing_phase_rejected',lambda rr,vv:vv['coverage_witnesses'].pop())
reject('held_last_after_original1s_rejected',lambda rr,vv:rr['observations'][-1]['guard_draws'][0]['Selection'].update(SampleTime=11.,DeathAge=1.))
reject('wrong_afterglow_rejected',lambda rr,vv:rr['observations'][0]['guard_draws'][0]['Selection'].update(DeathAfterglow=False))
reject('fake_original_clock_rejected',lambda rr,vv:rr['observations'][0]['guard_draws'][0]['Selection'].update(IntervalStart=9.))
reject('live_owner_cannot_donate_Death',lambda rr,vv:rr['observations'][0]['guard_native'].update(dead=False,HP=1))
nonadj=copy.deepcopy(choices);x=nonadj[3][0];nonadj[3]=[(x[0]+1,*x[1:])]
try:ns['adjacent_joins'](nonadj)
except AssertionError:cases.append('nonadjacent_phase_join_rejected')
else:raise AssertionError('Nonadjacent transition accepted')
assert pipeline.replace('Death','StunIR')==old[start:end]
js('static-media-contract-check-v001.json',dict(schema='Death-media-contract-only-static-v001',passed=True,Python_AST_parsed=True,cases=cases,StunIR_v011_timing_pipeline_unchanged_except_output_names=True,synthetic_contract_only=True,native_proof_generated=False,UE_started=False,ffmpeg_started=False,View_used=False,formal_complete_units=0))
print(json.dumps(dict(prepared_candidate=C.as_posix(),tool_bytes=(C/'tooling/prepare-Death-native-media-v001.py').stat().st_size,static_checks=len(cases),native_validation_not_run=True)))
