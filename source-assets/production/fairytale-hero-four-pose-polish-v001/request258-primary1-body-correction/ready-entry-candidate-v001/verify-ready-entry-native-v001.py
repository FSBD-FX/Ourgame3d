"""Narrow default EquipmentBound Ready→258 J entry proof. No UE launch here.
GPU/source readback, world projection, physical H/V, audio and isolated J1→Ready remain OPEN.
"""
from pathlib import Path
from datetime import datetime
import argparse,hashlib,importlib.util,json,math,struct,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
PHASES=('start','baseline_no_armor','light_pending_cancel','light_canceled','light_pickup_commit','light_ready','light_three_stage','medium_selection','medium_commit','medium_unsupported_ready','original_light_retake_selection','original_light_retake_commit','original_light_retaken_ready','complete')
OPEN=('GPU_source_readback','independent_world_camera_projection','physical_jump_height_velocity_grounded_snapshot','internal_runtime_PID_claim','full_MainMix_and_all_audio','lawful_loot_shop_source','full_equipment_receipt_payload','isolated_J1_to_Ready','Primary2_Primary3_source_pixel_acceptance','unreported_hitflash_tint','model_visual_review')
def need(v,why):
 if not v:raise ValueError(why)
def read(p):
 def unique(rows):
  d={}
  for k,v in rows:need(k not in d,'Duplicate JSON key');d[k]=v
  return d
 return json.loads(Path(p).read_text(encoding='utf-8-sig'),object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in()).throw(ValueError('Nonfinite JSON')))
def resolved(p):
 p=Path(p);return (p if p.is_absolute() else ROOT/p).resolve()
def pin(p):
 p=resolved(p);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=h.hexdigest())
def check(r):
 p=resolved(r['path']);a=pin(p);need(type(r['bytes']) is int and r['bytes']>=0 and (a['bytes'],a['sha256'])==(r['bytes'],r['sha256']),'Pinned input changed: '+str(p));return p
def same(a,b):return resolved(a['path'])==resolved(b['path']) and (a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])
def finite(v):return type(v) in(int,float) and math.isfinite(v)
def near(a,b,tol=1e-8):return finite(a) and finite(b) and abs(a-b)<=tol
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def uint(v):
 need(type(v) is str and v.isascii() and v.isdigit() and str(int(v))==v and 0<=int(v)<2**64,'Exact uint64 decimal required');return int(v)
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def inputs_expected():
 return [(k,d) for k in ('Enter','E','A','E','J','J','J','E','Enter','E','Enter') for d in (True,False)]
def expected_arguments(archive):
 return ['F:/Ourgame/UnrealGame/CodexDungeon.uproject','/Game/Maps/FirstRoom','-game','-d3d11','-windowed','-ResX=1280','-ResY=720','-NoSplash','-NoLiveCoding','-nop4','-unattended','-DungeonSceneExplorationPreview','-DungeonCandidateSprites','-DungeonFairytaleSwordBodyPreview','-DungeonFairytaleSwordBodyV002Preview','-DungeonFairytaleSwordArmorPrimary1Preview','-DungeonFairytaleSwordPrimary2Preview','-DungeonFairytaleSwordPrimary2BodyPreview','-DungeonFairytaleSwordPrimary2ArmorPreview','-DungeonFairytaleSwordPrimary3ArmorPreview','-DungeonFairytaleLeatherReadyPreview','-DungeonFairytaleLeatherPrimary1Preview','-DungeonFairytalePrimary1Bridge258Preview','-DungeonFairytaleSwordEquipmentBoundPreview','-DungeonFairytaleEquipmentBoundProof','-DungeonContentProof','-DungeonFastLosslessCapture','-DungeonAsyncLosslessCapture','-DungeonContentProofDir='+str(archive/'原件'),'-ExecCmds=t.MaxFPS 30,r.ScreenshotDelegate 1','-abslog='+str(archive/'native-engine.log')]
def setup():
 rows=read(HERE/'required-pins-v001.json')['pins'];p={k:check(v) for k,v in rows.items()}
 contract=read(HERE/'ready-entry-source-contract-v001.json')
 need(len(contract['sources'])==67 and len({x['object_path'] for x in contract['sources']})==67,'Exact67 Ready/J1/sword source PNGs required')
 for x in contract['sources']:check(x['source'])
 return rows,p,contract
def preflight(compiled_manifest,source_admission):
 rows,p,contract=setup();cm_pin,ad_pin=pin(compiled_manifest),pin(source_admission);cm=read(compiled_manifest);ad=read(source_admission)
 need(same(cm['source_admission_pin'],ad_pin) and ad['schema']=='Root-primary1-bridge258-source-admission-v001'
      and ad['RootApproved'] is True and ad['is_template'] is False and ad['actual_applied'] is True
      and ad['actual_source_files']==303 and ad['actual_production_files']==1439
      and len(ad['source_candidate_freezes'])==len(ad['fresh_source_reviews'])==2,'Selected actual current CM/Root art admission required')
 for value in ad['source_candidate_freezes']+ad['fresh_source_reviews']:check(value)
 current={x['path']:x for x in cm['files']}
 for key in ('observer','presentation','HUD'):
  basis=rows[key];member=current['UnrealGame/Source/CodexDungeon/'+Path(basis['path']).name]
  need((member['bytes'],member['sha256'])==(basis['bytes'],basis['sha256']),'Related Ready observer/renderer/HUD source basis changed; explicit candidate update required')
 need(cm['source_files']==303 and cm['production_files']==1439 and cm['registered_tests']==cm['passed']==203 and cm['failed']==cm['notRun']==0,'Actual Source303/Production1439/full203 required')
 suite=read(check(cm['full_suite']));need(tuple(suite[k] for k in ('succeeded','succeededWithWarnings','failed','notRun','inProcess'))==(203,0,0,0,0),'Strict203 aggregate differs')
 need(len(suite['tests'])==len({x['fullTestPath'] for x in suite['tests']})==203 and all(x['state']=='Success' and x['warnings']==x['errors']==0 and not any(e.get('event',{}).get('type') in ('Warning','Error') for e in x['entries']) for x in suite['tests']),'Strict203 per-test results differ')
 build=read(check(cm['build']));need(build['ExitCode']==0 and build['Target']=='CodexDungeonEditor' and resolved(build['Log'])==check(cm['build_log']),'Actual clean current Editor build required')
 paths={x['path'] for x in cm['files']};need(len(paths)==len(cm['files']),'Duplicate compiled member')
 for x in cm['files']:check(x)
 for prefix,count in (('UnrealGame/Source/',303),('UnrealGame/Content/Production/',1439)):
  actual={x.relative_to(ROOT).as_posix() for x in (ROOT/prefix).rglob('*') if x.is_file()};need(len(actual)==count and actual=={x for x in paths if x.startswith(prefix)},'Actual current directory membership differs')
 return dict(schema='request258-ready-entry-preflight-v001',passed=True,compiled_manifest_pin=cm_pin,source_admission_pin=ad_pin,source_files303=303,production_files1439=1439,registered_tests=203,required_source_PNGs=67,UE_started=False,OPEN=list(OPEN),FinalAccepted=False)
def verify_inputs(r):
 a=r['normal_input_requests'];need(a==r['inputevents'] and type(a) is list and len(a)==22 and all(type(x.get('key')) is str and type(x.get('down')) is bool for x in a) and [(x['key'],x['down']) for x in a]==inputs_expected(),'Exact22 Enter/E/A cancel/E/Jx3/E/Enter/E/Enter edges required')
 duration=r['duration_s'];need(all(finite(x['wall_offset_s']) and 0<=x['wall_offset_s']<=duration and finite(x['sim']) for x in a) and all(x['wall_offset_s']<y['wall_offset_s'] and x['sim']<=y['sim'] for x,y in zip(a,a[1:])),'Actual monotonic input clocks required')
 return [x for x in a if x['down']]
def marker_draw(o,c):
 need(o['clip'] in c['frames'] and type(o['frame']) is int and 0<=o['frame']<len(c['frames'][o['clip']]),'Invalid Ready/J1 source clip/frame')
 frame=c['frames'][o['clip']][o['frame']];side=o['facing'];need(type(side) is int and side in(-1,1),'Exact facing required')
 need(o['draw_stack']==frame['draw_stack'] and o['root']==frame['root'] and o['grip']==frame['grip'] and o['texture']==frame['legacy_full_body_readiness_texture'] and o['weapon']==c['sword'],'Exact same-draw source stack/Root/Grip/sword differs')
 need(o['body_max_contract']==72 and near(o['canvas_size'],c['display_canvas']) and o['weapon_scale']==.5 and o['weapon_width']==f32(c['display_canvas']*.5) and near(o['weapon_angle'],math.degrees(math.atan2(frame['axis'][1],frame['axis'][0]))*side),'Fixed72px/independent sword axis/scale differs')
 need(len(o['grip_screen'])==2 and all(finite(x) for x in o['grip_screen']),'Finite recorded screen Grip required')
 return frame
def verify_flow(r,c):
 need(r['schema']=='fairytale-equipment-bound-native-flow-v1' and r['passed'] is True and r['flow_complete'] is True and r['failure']==r['reason']=='' and r['mismatches']==[],'Actual default complete native flow must pass; preserve all real enemy/flow failures')
 need(r['leather_ready_only_trial'] is r['leather_primary1_only_trial'] is r['leather_combo_only_trial'] is False and r['light_primary_phase_masks']==[63,63,63],'Default full flow/three original stage masks required')
 need(r['silent_video'] is True and r['audio_recorded'] is False and r['native_async_capture_writes_flushed'] is True and r['formal_complete_units']==0,'Native silent/async scope differs')
 down=verify_inputs(r);obs=r['observations'];need(type(obs) is list and len(obs)>0,'Actual observations required')
 timing=r['capture_timing'];need(timing['use_fixed_time_step'] is False and near(r['duration_s'],timing['capture_stop_monotonic_s']-timing['capture_start_monotonic_s']) and timing['frame_wall_offsets_s']==[x['wall_offset_s'] for x in obs],'Actual original callback wall offsets required')
 need(all(finite(o['wall_offset_s']) and 0<=o['wall_offset_s']<r['duration_s'] and finite(o['sim']) and o['sim']==o['actual_sim'] for o in obs) and all(a['wall_offset_s']<b['wall_offset_s'] and a['sim']<=b['sim'] and uint(a['draw_id'])<uint(b['draw_id']) for a,b in zip(obs,obs[1:])),'Fresh native same-draw clocks/IDs required')
 identity=('run','run_alias','owner_id','active_slot','committed_weapon_id','committed_weapon_version','instance_id','weapon_mirror')
 need(all(all(o[k]==obs[0][k] for k in identity) and o['instance_id']==o['committed_weapon_id'] and o['weapon_mirror']=='WPN-SWD-001' and o['active'] is True and o['texture_ready'] is True and o['interface_visible'] is False and o['text_calls']==0 and o['body_max_contract']==72 and near(o['canvas_size'],c['display_canvas']) for o in obs),'Actual owner/run/sword/72px/UI binding differs')
 need(len(obs[0]['run'])==32 and uint(obs[0]['owner_id'])>0 and uint(obs[0]['committed_weapon_id'])>0,'Actual owner/run/sword required')
 checks=r['phasechecks'];need(all(type(x['step']) is int for x in checks) and [x['step'] for x in checks]==list(range(13)) and all(x['phase']==PHASES[x['step']] for x in checks) and all(a['wall_offset_s']<b['wall_offset_s'] and a['sim']<=b['sim'] for a,b in zip(checks,checks[1:])),'Preserve all default phase/extra combo/medium/retake transitions')
 need(all(type(o['flow_step']) is int and o['flow_step'] in range(13) and o['flow_phase']==PHASES[o['flow_step']] for o in obs) and all(a['flow_step']<=b['flow_step'] for a,b in zip(obs,obs[1:])),'Actual flow observation order differs')
 phases={step:[(i,o) for i,o in enumerate(obs) if o['flow_step']==step] for step in range(13)};need(all(phases[s] for s in range(1,13)),'Actual default phase callbacks missing')
 light,medium=uint(r['light_instance_id']),uint(r['medium_instance_id']);need(light>0 and medium>0 and light!=medium and uint(r['light_source_id'])>0 and uint(r['medium_source_id'])>0 and uint(r['original_light_drop_source'])>0,'Actual QA light/medium/original-drop identities required')
 base=phases[1][-1][1];op=uint(base['next_operation_id']);count=uint(base['operation_count'])
 pending=[o for _,o in phases[2] if o['pending_equipment_action']];need(pending and all(o['pending_instance_id']==str(light) and o['committed_armor_id']=='0' and o['selected_source_id']==r['light_source_id'] and o['pending_equipment_kind']==2 and finite(o['equipment_deadline']) for o in pending),'Actual first E pending same light source required')
 deadline=pending[0]['equipment_deadline'];need(down[1]['sim']<=deadline-.5<=pending[0]['sim'] and deadline-.4<=down[2]['sim']<deadline-.08,'Normal A must cancel inside actual original .50 E window')
 canceled=phases[3][-1][1];need(canceled['pending_equipment_action'] is False and canceled['committed_armor_id']=='0' and uint(canceled['next_operation_id'])==op and uint(canceled['operation_count'])==count and canceled['sim']>deadline+.02 and down[3]['sim']>deadline+.02,'Canceled E cannot late-commit or spend operation')
 second=[o for _,o in phases[4] if o['pending_equipment_action']];need(second and all(o['pending_instance_id']==str(light) and o['selected_source_id']==r['light_source_id'] and o['committed_armor_id']=='0' for o in second) and down[3]['sim']<=second[0]['equipment_deadline']-.5<=second[0]['sim'],'Second normal E must actually queue original light again')
 before=[(i,o) for i,o in phases[5] if o['animation']=='idle' and o['clip']=='sword_ready_idle' and o['supported'] is True and o['pending_equipment_action'] is False and o['needs_slot_selection'] is False]
 need(len(before)>=3 and all(o['wall_offset_s']<down[4]['wall_offset_s'] for _,o in before),'At least3 actual committed Ready callbacks before first J required')
 armor_version=before[0][1]['committed_armor_version']
 for _,o in before:
  need(o['committed_armor_id']==str(light) and o['armor_mirror']=='ARM-LGT-001' and o['committed_armor_version']==armor_version and uint(o['next_operation_id'])==op+1 and uint(o['operation_count'])==count+1 and o['sim']>=second[0]['equipment_deadline'],'Actual .50 light commit and Ready inventory operation required');marker_draw(o,c)
 stages=[]
 for stage in range(3):
  rows=[(i,o) for i,o in phases[6] if o['clip']=='sword_primary_'+str(stage+1) and o['stage']==stage and o['supported'] is True]
  need(rows and all(type(o['frame']) is int and type(o['stage']) is int for _,o in rows) and {o['frame'] for _,o in rows}==set(range(6)) and rows[0][1]['frame']==0 and all(a['frame']<=b['frame'] for (_,a),(_,b) in zip(rows,rows[1:])),'Six ordered original phases per actual combo stage required')
  first=rows[0][1];need(uint(first['action_id'])>0 and first['start']<=first['sim']<first['end'] and down[4+stage]['sim']<=first['start'] and down[4+stage]['wall_offset_s']<first['wall_offset_s'],'Each real queued J must precede own fresh actual action')
  need(all(o['action_id']==first['action_id'] and all(o[k]==first[k] for k in ('start','active_at','active_end','end')) and o['start']<=o['sim']<o['end'] and o['facing']==-1 and o['committed_armor_id']==str(light) and o['committed_armor_version']==armor_version and o['armor_mirror']=='ARM-LGT-001' and o['armor_drawn'] is True and o['draw_stack_has_armor'] is True and o['weapon']==c['sword'] and len(o['draw_stack'])==8 for _,o in rows),'Same native actual left-facing light/sword action/clock/stack required')
  if stage==0:
   need(near(first['end']-first['start'],.6),'Original Primary1 .60 interval changed')
   for _,o in rows:marker_draw(o,c)
  else:need(uint(first['action_id'])>uint(stages[-1][0][1]['action_id']) and first['start']>=stages[-1][0][1]['end'],'Actual three-stage IDs and intervals must progress')
  stages.append(rows)
 need(before[-1][1]['wall_offset_s']<down[4]['wall_offset_s']<stages[0][0][1]['wall_offset_s'],'Ready→first J0 causal wall order differs')
 after=[(i,o) for i,o in phases[6] if o['clip']=='sword_ready_idle' and o['animation']=='idle' and o['supported'] is True and o['pending_equipment_action'] is False and o['sim']>=stages[2][0][1]['end']]
 need(len(after)>=3,'Require3 genuinely post-stage3 Ready callbacks, never pre-J Ready counts')
 for _,o in after:need(o['committed_armor_id']==str(light) and o['committed_armor_version']==armor_version,'Post-chain Ready changed original light');marker_draw(o,c)
 med=phases[9];retake=phases[12];need(len(med)>=3 and len(retake)>=3,'Keep actual medium and original-light retake Ready callbacks')
 need(all(o['committed_armor_id']==str(medium) and o['armor_mirror']=='ARM-MED-001' and o['supported'] is False and o['armor_drawn'] is False and o['draw_stack_has_armor'] is False and o['weapon']=='' and uint(o['next_operation_id'])==op+2 and uint(o['operation_count'])==count+2 for _,o in med),'Actual medium replacement must remain unsupported with no false light/sword')
 need(all(o['committed_armor_id']==str(light) and uint(o['committed_armor_version'])>uint(armor_version) and o['armor_mirror']=='ARM-LGT-001' and uint(o['next_operation_id'])==op+3 and uint(o['operation_count'])==count+3 for _,o in retake),'Actual original-light retake identity/version/operations differ')
 for _,o in retake:marker_draw(o,c)
 witnesses=before[-3:]+[rows[len(rows)//2] for frame in range(6) for rows in [[x for x in stages[0] if x[1]['frame']==frame]]]+after[:3]
 return dict(passed=True,first_Ready_indices=[i for i,_ in before],first_J0_index=stages[0][0][0],first_J_action_id=stages[0][0][1]['action_id'],three_action_ids=[rows[0][1]['action_id'] for rows in stages],three_stage_masks=[63,63,63],post_chain_Ready_indices=[i for i,_ in after],light_instance_id=str(light),light_version=armor_version,medium_and_original_light_retake_preserved=True,isolated_J1_to_Ready='OPEN_full_chain_intervenes',physical_grounded_snapshot='OPEN_not_recorded',witness_indices=[i for i,_ in witnesses])
def verify_session(a,cm_pin,ad_pin):
 p=read(a/'preregistration-v001.json');launch=read(a/'launch-receipt-v001.json');index=read(a/'index.json')
 need(p['schema']=='Root-primary1-bridge258-ready-entry-prereg-v001' and p['RootApproved'] is True and p['is_template'] is False and p['pre_registered_before_capture'] is True and p['FinalAccepted'] is False and resolved(p['run_directory'])==a and ROOT in a.parents and p['OPEN']==list(OPEN),'Actual fresh Root bounded prereg required')
 for key,value in (('compiled_manifest_pin',cm_pin),('source_admission_pin',ad_pin)):need(same(p[key],value),'Prereg selected actual current CM/AD differs')
 need(same(p['checker_pin'],pin(__file__)) and same(p['launcher_pin'],pin(HERE/'run-ready-entry-native-v001.ps1')),'Prereg checker/launcher differs')
 frozen=read(check(p['checker_freeze_pin']))
 for row in frozen['members']+frozen['dependency_pins']:check(row)
 for name in ('verify-ready-entry-native-v001.py','prepare-ready-entry-prereg-v001.py','run-ready-entry-native-v001.ps1','required-pins-v001.json','ready-entry-source-contract-v001.json'):
  need(any(same(x,pin(HERE/name)) for x in frozen['members']),'Actual tool/config absent from selected candidate freeze')
 need(index['exit_code']==0 and type(index['process_id']) is int and type(launch['process_id']) is int and index['process_id']==launch['process_id'] and index['process_id']>0 and same(index['root_prereg_pin'],pin(a/'preregistration-v001.json')),'Actual Root process/normal OS exit/prereg association differs')
 for key in ('compiled_manifest_pin','source_admission_pin','checker_freeze_pin'):need(same(index[key],p[key]),'Actual session lineage differs')
 need(type(p['arguments']) is list and all(type(x) is str for x in p['arguments']) and type(launch['arguments']) is list and all(type(x) is str for x in launch['arguments']) and launch['arguments']==p['arguments'],'Preregistered exact argv must equal actual launch')
 need(p['expected_default_side']==-1 and p['QA_registered_sources'] is True and p['lawful_source_acceptance'] is False and p['isolated_J1_to_Ready'] is False and p['Knight_cleanup'] is False and p['forced_pose_HP_AI_position_time'] is False and p['maximum_render_FPS']==30 and p['fixed_time_step'] is False and p['audio_recorded'] is False,'Bounded prereg scope differs')
 need(launch['schema']=='Root-primary1-bridge258-ready-entry-launch-v001' and launch['human_input'] is False and launch['Knight_cleanup'] is False and launch['forced_pose_HP_AI_position_time'] is False and [x.replace('\\','/') for x in launch['arguments']]==[x.replace('\\','/') for x in expected_arguments(a)],'Exact original default map/flow/258 argv required; no cleanup or other proof')
 need(datetime.fromisoformat(p['created_utc'])<datetime.fromisoformat(launch['started_utc']),'Prereg must precede real process launch')
 return dict(process_id=index['process_id'],internal_runtime_PID='OPEN_not_recorded',association='exclusive_fresh_Root_launch_directory',Knight_cleanup=False,forced_pose_HP_AI_position_time=False,QA_registered_sources=True)
def optical(a,r,c,indices):
 import numpy as np
 from PIL import Image
 _,p,_=setup();P=module(p['pixel_sampler'],'ready_entry_original_sampler');source={x['object_path']:x['source'] for x in c['sources']};cache={}
 receipts=[readline for readline in (a/'原件/native-frame-pixels.jsonl').read_text(encoding='utf-8-sig').splitlines() if readline];movie=[json.loads(x) for x in receipts if json.loads(x)['file'].startswith('MovieFrame')]
 need(len(movie)==len(r['observations']),'Every native observation must map FIFO to one original PNG')
 out=[]
 for i in indices:
  o=r['observations'][i];frame=marker_draw(o,c);side=o['facing'];width=f32(c['display_canvas']);grip=o['grip_screen'];top=[f32(grip[0]-(frame['grip'][0] if side>0 else 512-frame['grip'][0])*c['display_canvas']/512),f32(grip[1]-frame['grip'][1]*c['display_canvas']/512)];sw=o['weapon_width'];pivot=[99/512 if side>0 else 1-99/512,.5];swtop=[f32(grip[k]-pivot[k]*sw) for k in range(2)];slots=[]
  for path in o['draw_stack']:
   sword=path==c['sword'];slots.append(dict(texture=path,top=swtop if sword else top,size=[sw if sword else width]*2,uv=[0 if side>0 else 1,0],uv_size=[side,1],rotation=f32(o['weapon_angle']) if sword else 0,rotation_pivot=pivot if sword else [0,0],component=8 if sword else -1))
  xs=[];ys=[]
  for s in slots:
   angle=math.radians(s['rotation']);co,si=math.cos(angle),math.sin(angle);w=s['size'][0];px,py=s['rotation_pivot']
   for x,y in ((0,0),(w,0),(0,w),(w,w)):
    dx=x-px*w;dy=y-py*w;xs.append(s['top'][0]+px*w+co*dx-si*dy);ys.append(s['top'][1]+py*w+si*dx+co*dy)
  x0=max(0,math.floor(min(xs))-1);x1=min(1280,math.ceil(max(xs))+1);y0=max(0,math.floor(min(ys))-1);y1=min(720,math.ceil(max(ys))+1);need(x1>x0 and y1>y0,'Recorded screen-projected ROI outside viewport');yy,xx=np.mgrid[y0:y1,x0:x1];color=np.zeros((*xx.shape,3));alpha=np.zeros(xx.shape);blade=np.zeros(xx.shape)
  for s in slots:
   path=s['texture']
   if path not in cache:
    with Image.open(check(source[path])) as im:need(im.mode=='RGBA' and im.size==(512,512),'Exact source RGBA512 required');v=np.asarray(im,dtype=np.float64)/255
    v[...,:3]=P.linear(v[...,:3]);cache[path]=v
   v=P.sample(cache[path],s,xx,yy);al=v[...,3];color=v[...,:3]*al[...,None]+color*(1-al[...,None]);alpha=al+alpha*(1-al);blade=al if s['component']==8 else blade*(1-al)
  expected=np.rint(P.srgb(color)*255).astype(np.uint8)
  with Image.open(a/'原件'/movie[i]['file']) as im:actual=np.asarray(im.convert('RGB'))[y0:y1,x0:x1]
  error=np.mean(np.abs(actual.astype(float)-expected.astype(float)),axis=-1);opaque=(alpha>=.999)&(np.max(expected,axis=-1)>=32);steel=(blade>=.98)&(np.min(expected,axis=-1)>=45);bc,sc=int(np.count_nonzero(opaque)),int(np.count_nonzero(steel));need(bc>=150 and sc>=8,'Original fixed opaque body/blade minimum failed')
  bm,bg,sm,sg=float(np.median(error[opaque])),float(np.mean(error[opaque]<=55)),float(np.median(error[steel])),float(np.mean(error[steel]<=65));need(bm<=40 and bg>=.60 and sm<=50 and sg>=.60,'Original fixed source-screen pixel gate failed; preserve enemy flash/occlusion/failure without alignment search')
  out.append(dict(observation=i,clip=o['clip'],frame=o['frame'],draw_id=o['draw_id'],file=movie[i]['file'],body_pixels=bc,blade_pixels=sc,body_median=bm,body_fraction_le55=bg,blade_median=sm,blade_fraction_le65=sg))
 return dict(passed=True,source_screen_coordinate_witnesses=out,registration_search_used=False,pixels_modified=False,current_GPU_source_closure='OPEN',independent_world_projection='OPEN',tint_assumption='fixed white; unknown actual hitflash must fail rather than fit',FinalAccepted=False)
def native(archive,compiled_manifest,source_admission):
 pre=preflight(compiled_manifest,source_admission);pins,_,c=setup();a=resolved(archive);session=verify_session(a,pre['compiled_manifest_pin'],pre['source_admission_pin']);r=read(a/'原件/runtime-report.json');flow=verify_flow(r,c)
 p=subprocess.run([sys.executable,'-B','-X','utf8',str(check(pins['native_PNG_checker'])),'--archive',str(a)],capture_output=True,text=True)
 need(p.returncode==0,'Unmodified native PNG/FIFO/CRC helper failed: '+p.stderr);crc=json.loads(p.stdout);need(crc['passed'] is True and crc['native_async_writer_verified'] is True,'Original full PNG async/FIFO/CRC gates required')
 pixels=optical(a,r,c,flow['witness_indices'])
 return dict(schema='request258-ready-entry-independent-native-v001',passed=True,compiled_manifest_pin=pre['compiled_manifest_pin'],source_admission_pin=pre['source_admission_pin'],native_report_pin=pin(a/'原件/runtime-report.json'),session=session,flow=flow,original_native_PNG_checker_pin=pins['native_PNG_checker'],original_native_PNG_FIFO_CRC=crc,source_screen_pixels=pixels,audio_recorded=False,OPEN=list(OPEN),formal_complete_units=0,visual_reviewed=False,audio_listened=False,FinalAccepted=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');ap.add_argument('--archive');ap.add_argument('--compiled-manifest',required=True);ap.add_argument('--source-admission',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
 need(not Path(args.out).exists(),'Never overwrite prior output')
 try:
  need(args.preflight is not bool(args.archive),'Select --preflight or --archive');value=preflight(args.compiled_manifest,args.source_admission) if args.preflight else native(args.archive,args.compiled_manifest,args.source_admission);code=0
 except(ValueError,KeyError,TypeError,OSError,AssertionError,StopIteration) as error:value=dict(passed=False,error=str(error),OPEN=list(OPEN),FinalAccepted=False);code=3
 with Path(args.out).open('x',encoding='utf-8') as file:json.dump(value,file,ensure_ascii=False,indent=2);file.write('\n')
 print(json.dumps(value,ensure_ascii=False));return code
if __name__=='__main__':raise SystemExit(main())
