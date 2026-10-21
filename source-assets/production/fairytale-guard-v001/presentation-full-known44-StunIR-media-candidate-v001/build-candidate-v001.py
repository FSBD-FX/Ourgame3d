"""Candidate-only deterministic source assembly; never launches UE/ffmpeg or reads media pixels."""
from pathlib import Path
import ast,copy,hashlib,json,runpy,shutil
C=Path(__file__).resolve().parent
R=C.parents[3]
M=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-media-candidate-v002'
D=R/'source-assets/production/fairytale-guard-v001/presentation-full-known44-combat-observer-candidate-v004'
assert C.name=='presentation-full-known44-StunIR-media-candidate-v001'
assert not (C/'StunIR-media-freeze-v001.json').exists(),'Never alter a frozen candidate'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(n,s):
 p=C/n;assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def js(n,v):write(n,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
dep=pin(D/'StunIR-candidate-freeze-v004.json')
assert dep['sha256']=='e3507a82b417883fe1dff70423c8035b72fa44cbd3c399f0d879f04923a4bf15'
for x in read(D/'StunIR-candidate-freeze-v004.json')['files']:
 p=D/x['path'];assert pin(p)['sha256']==x['sha256'] and p.stat().st_size==x['bytes']
for x in read(M/'known44-media-freeze-v002.json')['files']:
 p=M/x['path'];assert pin(p)['sha256']==x['sha256'] and p.stat().st_size==x['bytes']
old=(M/'tooling/prepare-known44-native-media-v002.py').read_text(encoding='utf-8-sig')
head=old[:old.index('def qualified_choices')]
head=head.replace('Known44 AxeCycle','Known44 normal-J StunIR').replace('argparse,hashlib,json,shutil,subprocess','argparse,hashlib,json,math,shutil,subprocess')
qualification='''def qualified_choices(r,v):
 aid=str(r['interrupted_attack_id']);bid=str(r['break_event_id']);obs=r['observations'];choices={};seen=set()
 for w in v['coverage_witnesses']:
  i=w['observation'];assert type(i) is int and 0<=i<len(obs)
  o=obs[i];ds=[d for d in o['guard_draws'] if d['DrawId']==w['DrawId'] and str(d['EntityId'])==str(r['guard_entity'])];assert len(ds)==1
  d=ds[0];s=d['Selection'];clip=s['Clip'];frame=s['Frame'];n=o['guard_native'];stamp=s['SampleTime']
  assert clip in ['Stunned','InterruptedRecovery'] and type(frame) is int and 0<=frame<4
  assert str(d['DrawId']) not in seen,'Repeated independent coverage DrawId';seen.add(str(d['DrawId']))
  assert d['Drawn'] is True and d['SpatialCoverageEligible'] is True and d['DrawStack']==[d['TexturePath']]
  assert w['clip']==clip and w['frame']==frame and w['sample']==stamp and str(w['AttackId'])==str(s['AttackId'])==aid==str(n['attack_id']) and str(w['SourceEventId'])==str(s['SourceEventId'])
  assert w['player']==o['player_ground'] and w['guard']==n['ground'] and w['object']==d['TexturePath']
  assert n['interrupted'] is True and n['HP']>0 and o['player_HP']>0 and o['phase']=='normal_guard_J_and_StunIR' and o['approach_spatial']['route_reached'] is True
  side=r['actual_approach_side'];assert side in [-1,1]
  assert 110<=side*(o['player_ground'][0]-n['ground'][0])<=155 and abs(o['player_ground'][1]-n['ground'][1])<=20
  if clip=='Stunned':
   assert str(s['SourceEventId'])==bid and s['Phase']==n['phase']==6 and s['IntervalStart']==r['break_at'] and s['IntervalEnd']==r['stun_end'] and r['break_at']<=stamp<r['stun_end']
   assert frame==sum(stamp>=r['break_at']+x for x in [.1,.2,.3])
  else:
   assert str(s['SourceEventId'])=='0' and s['Phase']==n['phase']==5 and s['IntervalStart']==r['stun_end'] and s['IntervalEnd']==r['original_occupied_until'] and r['stun_end']<=stamp<r['original_occupied_until']
   assert frame==min(3,math.floor((stamp-r['stun_end'])/(r['original_occupied_until']-r['stun_end'])*4))
  choices.setdefault((clip,frame),[]).append((i,d,w))
 for clip in ['Stunned','InterruptedRecovery']:
  for frame in range(4):assert choices.get((clip,frame)),('Missing independently qualified required sample',clip,frame)
 return choices

def adjacent_join(choices):
 left=choices[('Stunned',3)];right=choices[('InterruptedRecovery',0)]
 pairs=[(l,r) for l in left for r in right if r[0]==l[0]+1]
 if not pairs:return None
 assert len(pairs)==1,'One original break can have only one adjacent Stun-to-IR boundary'
 return pairs[0]

def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 archive=Path(a.archive).resolve();original=archive/'原件';show=archive/'展示副本';contract=read(C/'media-input-contract-v001.json')
 for row in read(C/'StunIR-media-freeze-v001.json')['files']:assert pin(C/row['path'])['sha256']==row['sha256'] and (C/row['path']).stat().st_size==row['bytes']
 dep=contract['exact_independent_source_tooling_freeze'];assert pin(Path(dep['path']))==dep
 report=original/'runtime-report.json';proof=original/contract['independent_receipt'];r=read(report);v=read(proof);session=read(archive/'index.json')
 assert session['schema']==contract['native_session_schema'] and session['candidate_freeze_sha256']==dep['sha256'] and str(session['process_id'])==r['process_id'] and session['exit_code']==0 and session['native_reported_passed'] is True and session['independent_passed'] is True
 assert r['schema']==contract['native_report_schema'] and r['scenario']==contract['scenario']=='StunIR' and r['passed'] is True and r['flow_complete'] is True and v['passed'] is True
 assert v['native_report_sha256']==pin(report)['sha256'] and str(v['process_id'])==r['process_id'] and v['run']==r['run']
 assert r['break_pinned'] is True and str(v['break_event_id'])==str(r['break_event_id']) and str(v['interrupted_attack_id'])==str(r['interrupted_attack_id']) and v['masks']=={'Stunned':15,'InterruptedRecovery':15} and r['StunMask']==r['InterruptedRecoveryMask']==15
 assert abs(r['stun_end']-(r['break_at']+.4))<=1.e-8 and r['original_occupied_until']-r['stun_end']>=.4
 assert r['normal_J_full_clear'] is False and r['guard_public_damage_used'] is False and r['guard_normal_J_only'] is True and r['guard_spawned_by_probe'] is False and r['game_tick_called_manually'] is False and r['player_damage_preserved'] is True and r['guard_final_HP']>0 and r['player_final_HP']>0 and r['spatial_approach']['route_reached'] is True
 assert r['silent_video'] is True and r['audio_recorded'] is False and r['visual_reviewed'] is False and v['visual_reviewed'] is False and r['formal_complete_units']==v['formal_complete_units']==0
 assert v['pixel_proof']['passed'] and v['pixel_proof']['native_async_writer_verified'] and v['pixel_proof']['every_source_viewport_pixel_crc_matches']
 frames=sorted(original.glob('MovieFrame*.png'));assert len(frames)==v['native_frames']==len(r['observations']) and v['pixel_proof']['verified_original_PNG_count']==len(frames)+1
 choices=qualified_choices(r,v);boundary=adjacent_join(choices)
 if a.validate_only:
  print(json.dumps(dict(actual_input_contract_verified=True,qualified_sample_keys=len(choices),required_samples=8,adjacent_Stun3_IR0_available=boundary is not None,media_written=False,UE_started=False,visual_reviewed=False)));return
 show.mkdir(exist_ok=True)
 assert not (archive/'source-version-status-index.json').exists() and not (archive/'README.md').exists(),'Never overwrite prior presentation index'
 assert not any(show.glob('*StunIR*v001*')),'Never overwrite earlier media; use a fresh capture/version'

'''
start=old.index(" frames=sorted(original.glob('MovieFrame*.png'));offsets=")
end=old.index(' samples=[]',start)
pipeline=old[start:end]
pipeline=pipeline.replace('known44-AxeCycle','known44-StunIR').replace('known44-v002','StunIR-v001').replace('timing-v002','timing-v001').replace('silent-v002','silent-v001')
tail=''' samples=[]
 def copy_native(i,dest):
  src=frames[i];assert not dest.exists();shutil.copy2(src,dest);assert pin(src)['sha256']==pin(dest)['sha256']
  with Image.open(dest) as im:assert im.format=='PNG' and im.size==(1280,720)
  return dict(frame_index=i,source=pin(src),presentation=pin(dest),wall_offset_s=offsets[i],resized=False)
 def selected_item(x,dest):
  i,d,w=x;item=copy_native(i,dest);s=d['Selection']
  item.update(clip=s['Clip'],frame=s['Frame'],AttackId=s['AttackId'],SourceEventId=s['SourceEventId'],sample_time=s['SampleTime'],interval_start=s['IntervalStart'],interval_end=s['IntervalEnd'],break_event_id=r['break_event_id'],coverage_witness=w,source_object=d['TexturePath']);return item
 for clip,count in contract['required_samples'].items():
  for frame in range(count):
   pool=choices[(clip,frame)];samples.append(selected_item(pool[len(pool)//2],show/f'{clip}-{frame:02d}-UNSCALED-StunIR-v001.png'))
 assert len(samples)==8
 joins=[];missing_joins=[]
 if boundary:
  left,right=boundary;li,ri=left[0],right[0]
  items=[selected_item(x,show/f'JOIN-Stunned3-to-InterruptedRecovery0-{label}-UNSCALED-StunIR-v001.png') for label,x in [('before',left),('after',right)]]
  joins.append(dict(join='Stunned3-to-InterruptedRecovery0',pair=items,original_adjacent_callbacks=True,intervening_native_frames=0,original_wall_delta_s=offsets[ri]-offsets[li],break_event_id=r['break_event_id'],interrupted_attack_id=r['interrupted_attack_id'],interpolation=False,join_visual_accepted=False))
 else:missing_joins.append(dict(join='Stunned3-to-InterruptedRecovery0',reason='No pair of independently qualified original adjacent callbacks; no later callback substitutes for adjacency',join_visual_accepted=False))
 (show/'join-candidates-StunIR-v001.json').write_text(json.dumps(dict(schema='known44-StunIR-native-join-candidates-v001',pairs=joins,missing=missing_joins,visual_reviewed=False,scope='Original consecutive full-viewport Stun3/IR0 only, same real85 break and original interrupted AttackId. No montage/retime/interpolation; missing adjacency remains explicit.'),ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
 index=dict(schema='guard-known44-StunIR-native-media-v001',status='NATIVE_NORMAL_J_STUNIR_TRIAL_PASSED_VISUAL_REVIEW_PENDING',video=pin(video),report=pin(report),independent=pin(proof),session=pin(archive/'index.json'),media_candidate=pin(C/'StunIR-media-freeze-v001.json'),presentation_frame_retention=timing_receipt,samples=samples,required_sample_count=8,joins=joins,missing_joins=missing_joins,procedural_gap_seen=r['procedural_gap_seen'],break_event_id=r['break_event_id'],interrupted_attack_id=r['interrupted_attack_id'],break_at=r['break_at'],stun_end=r['stun_end'],original_occupied_until=r['original_occupied_until'],IR_actual_duration_s=r['original_occupied_until']-r['stun_end'],actual_approach_side=r['actual_approach_side'],normal_J_full_clear=False,diagnostic_Knight_Bat=True,guard_damaged_by_normal_J=True,guard_final_HP=r['guard_final_HP'],player_final_HP=r['player_final_HP'],player_damage_preserved=True,audio_recorded=False,visual_reviewed=False,E_before_view_required=True,formal_complete_units=0,render_callback_asset_pixel_attribution='Qualified actual observation plus native viewport CRC. Asset-specific pixels and join quality still require E preservation and actual View; no all44-rendered/all57/Death/final-art claim.')
 (archive/'source-version-status-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\\n',encoding='utf-8')
 (archive/'README.md').write_text('正常J破韧与原窗恢复试样：Knight/Bat公开诊断清除；Guard仅正常军剑J真实受击，保留玩家实际损伤。同一次85破韧和原AttackId的Stun4/InterruptedRecovery4共8张原比例整幅PNG，IR使用实际剩余原占用窗而非固定400ms。原时序完整静音录像、只接受原连续回调的Stun3→IR0转场候选。缺相邻转场明确记录；尚待E保全与实际View，不是全44/57、Death、足锁、音效或最终美术验收。\\n',encoding='utf-8')
 print(json.dumps(dict(video=pin(video),native_frames=len(frames),samples=len(samples),join_pairs=len(joins),missing_join_pairs=len(missing_joins),duration_s=duration-offsets[0],visual_reviewed=False)))

if __name__=='__main__':main()
'''
source=head+qualification+pipeline+tail
ast.parse(source)
write('tooling/prepare-StunIR-native-media-v001.py',source)
for n in ['prepare-guard-partial-native-media-v011-READONLY-REFERENCE.py','tooling/native-v011-timing-pipeline-REFERENCE-fragment.txt']:
 assert not (C/n).exists();shutil.copy2(M/n,C/n);assert pin(C/n)['sha256']==pin(M/n)['sha256']
js('media-input-contract-v001.json',dict(schema='known44-StunIR-media-input-contract-v001',native_report_schema='guard-art-known44-combat-observer-v003',native_session_schema='guard-art-known44-combat-session-v003',scenario='StunIR',independent_receipt='independent-StunIR-v003.json',exact_independent_source_tooling_freeze=dep,required_samples=dict(Stunned=4,InterruptedRecovery=4),same_break_event_required=True,same_original_interrupted_attack_required=True,Stun_duration_s=.4,IR_clock='Actual positive original [StunUntil,OccupiedUntil), four normalized phases; SourceEventId0 legal',accepted_join='Only consecutive native callbacks Stunned3 to InterruptedRecovery0; otherwise explicit missing join',UE_started=False,ffmpeg_started=False,View_used=False,formal_complete_units=0))
write('HANDOFF.md','''# StunIR media v001（候选，尚未执行）

只接收已冻 StunIR observer/source/tooling v004（freeze SHA e3507a82b417883fe1dff70423c8035b72fa44cbd3c399f0d879f04923a4bf15）实际成功 session，以及同原件成功 independent-StunIR-v003.json。native/session 协议仍为 v003，不因目录版本改名。额外核实际报告 SHA、PID、run、同一 break_event_id/interrupted_attack_id、Stun15/IR15、原占用窗、正常 J/玩家实际损伤和 CRC/FIFO；错误 schema/hash/失败状态拒绝。

输出完整静音 VFR 与 Stun4/IR4 共8张1280×720原幅PNG。每相仅来自独立 coverage_witnesses 与同 DrawId/原时钟/实际位置/单整身斧 source；不重新计数、更不补帧。IR duration 读取原 [stun_end,original_occupied_until)，不固定400ms。相邻 join 仅同 break 的原连续 Stun3→IR0 两回调；无合格连续对则明确 missing，不借后续帧或后续break。此版不额外声称 Stun0前普通受击/IR3后Idle的完整视觉覆盖。

VFR 编码沿用 v011 全部微秒 PTS、-frames:v cap、解码 framemd5 数量和舍入上界、decoded-last1280×720验证；仅输出命名不同。完整源录像时长不裁剪或慢放。MP4是有损展示副本且静音；原PNG原件不改。全部展示副本/index须先不存在，避免覆盖已生成媒体；Root编码后按项目规范保全E，再实际View。

Root命令（绝对 archive 路径，先 validate-only）：

```powershell
.\\tools\\runtime\\asset-gen\\Scripts\\python.exe -B -X utf8 source-assets/production/fairytale-guard-v001/presentation-full-known44-StunIR-media-candidate-v001/tooling/prepare-StunIR-native-media-v001.py --archive '<actual fresh StunIR archive>' --validate-only
```

去掉 --validate-only 才编码/复制。此候选仅 Python AST、代码时基等价和选择边界检查；没有运行UE/ffmpeg/View，没有生成新媒体或声称原生通过。Death草案、Hurt4和Root准入不在本工具范围。
''')
# Synthetic structures below only exercise media selector rejection; never output native evidence.
ns={};exec(compile(ast.Module(body=[n for n in ast.parse(source).body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) and not isinstance(n,ast.FunctionDef) or isinstance(n,ast.FunctionDef) and n.name in ['qualified_choices','adjacent_join']],type_ignores=[]),'contract-only','exec'),ns)
r=dict(interrupted_attack_id='7',break_event_id='13',guard_entity='3',actual_approach_side=-1,break_at=10.,stun_end=10.4,original_occupied_until=11.6,observations=[])
v=dict(coverage_witnesses=[])
for clip in ['Stunned','InterruptedRecovery']:
 for frame in range(4):
  i=len(r['observations']);lo,hi=(10.,10.4) if clip=='Stunned' else (10.4,11.6);stamp=lo+(hi-lo)*(frame+.5)/4;phase=6 if clip=='Stunned' else 5;eid='13' if clip=='Stunned' else '0'
  s=dict(Clip=clip,Frame=frame,SampleTime=stamp,AttackId='7',SourceEventId=eid,Phase=phase,IntervalStart=lo,IntervalEnd=hi)
  d=dict(DrawId=str(i+1),EntityId='3',Selection=s,Drawn=True,SpatialCoverageEligible=True,DrawStack=['/test'],TexturePath='/test')
  o=dict(guard_draws=[d],guard_native=dict(ground=[0,0],attack_id='7',interrupted=True,HP=80,phase=phase),player_ground=[-125,0],player_HP=80,phase='normal_guard_J_and_StunIR',approach_spatial=dict(route_reached=True))
  r['observations'].append(o);v['coverage_witnesses'].append(dict(observation=i,DrawId=str(i+1),clip=clip,frame=frame,sample=stamp,AttackId='7',SourceEventId=eid,object='/test',player=[-125,0],guard=[0,0]))
choices=ns['qualified_choices'](r,v);assert len(choices)==8 and ns['adjacent_join'](choices) is not None
passed=['valid_contract_only_8keys_and_adjacent_boundary']
def rejected(name,mutate):
 rr,vv=copy.deepcopy(r),copy.deepcopy(v);mutate(rr,vv)
 try:ns['qualified_choices'](rr,vv)
 except (AssertionError,ValueError,KeyError):passed.append(name);return
 raise AssertionError('Negative contract accepted: '+name)
rejected('other_attack_rejected',lambda rr,vv:rr['observations'][0]['guard_native'].update(attack_id='8'))
rejected('other_break_rejected',lambda rr,vv:rr.update(break_event_id='14'))
rejected('IR_nonzero_source_event_rejected',lambda rr,vv:rr['observations'][4]['guard_draws'][0]['Selection'].update(SourceEventId='13'))
rejected('wrong_native_phase_rejected',lambda rr,vv:rr['observations'][0]['guard_native'].update(phase=5))
rejected('wrong_original_clock_rejected',lambda rr,vv:rr['observations'][0]['guard_draws'][0]['Selection'].update(IntervalStart=9.))
rejected('unqualified_spatial_sample_rejected',lambda rr,vv:rr['observations'][0].update(player_ground=[-80,0]))
rejected('missing_phase_rejected',lambda rr,vv:vv['coverage_witnesses'].pop())
rejected('duplicate_DrawId_rejected',lambda rr,vv:vv['coverage_witnesses'].append(copy.deepcopy(vv['coverage_witnesses'][0])))
nonadjacent=copy.deepcopy(choices);x=nonadjacent[('InterruptedRecovery',0)][0];nonadjacent[('InterruptedRecovery',0)]=[(x[0]+1,*x[1:])];assert ns['adjacent_join'](nonadjacent) is None;passed.append('nonadjacent_join_is_explicitly_missing')
normalize=lambda x:x.replace('known44-StunIR','known44-AxeCycle').replace('StunIR-v001','known44-v002').replace('timing-v001','timing-v002').replace('silent-v001','silent-v002')
assert normalize(pipeline)==old[start:end]
js('static-media-contract-check-v001.json',dict(schema='StunIR-media-contract-static-v001',passed=True,Python_AST_parsed=True,checks=passed,v011_timing_pipeline_unchanged_except_output_names=True,synthetic_contract_only=True,native_proof_generated=False,UE_started=False,ffmpeg_started=False,View_used=False,formal_complete_units=0))
rows=[]
for p in sorted(C.rglob('*')):
 if p.is_file():
  q=pin(p);q['path']=p.relative_to(C).as_posix();rows.append(q)
js('StunIR-media-freeze-v001.json',dict(schema='known44-StunIR-media-candidate-freeze-v001',immutable=True,scope='Exact StunIR-v004 success only, same-break Stun4/IR4 and native adjacent join; original VFR unchanged',UE_started=False,ffmpeg_started=False,View_used=False,formal_complete_units=0,files=rows))
print(json.dumps(pin(C/'StunIR-media-freeze-v001.json')))
