"""NEW independent v144 whole-byte/disk/causal contracts; no actions at import.

Native Aggregate validation still belongs to the frozen production Codec APIs.
This host checks canonical wire bytes, all root members and checkpoint binding;
it never pretends to replace that full native typed semantic validator.
"""
from pathlib import Path
from datetime import datetime
import hashlib,json,math,re,struct,zlib

ROOT=Path('F:/Ourgame')
IDENTITY=('run','owner','current_room','weapon_instance','weapon_version','armor_instance','armor_version')
ROOT_FIELDS=set('Schema Scope RunGuid OwnerId RoomInstanceId RoomNumber SimulationTime LastStoneWakeStartedAt RoomCleared GameOver WaitingForStart SceneCommitRequested SceneEquipmentTargetLost LastMessage SceneEncounterEntityId Geometry Equipment Scene WeaponWorld Fighters EnemyOrder Rewards Pickups Exploration Audio'.split())

def need(value,why):
    if not value:raise ValueError(why)

def finite(x):return type(x) in (int,float) and math.isfinite(x)

def strict_json(data):
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'Duplicate JSON key');out[k]=v
        return out
    return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON')))

def read(path):return strict_json(Path(path).read_bytes().removeprefix(b'\xef\xbb\xbf'))

def quote(s):
    need(isinstance(s,str),'Native canonical string required')
    return '"'+''.join('\\'+c if c in ('"','\\') else '\\u%04x'%ord(c) if ord(c)<32 else c for c in s)+'"'

def canonical(value):
    if value is None:return 'null'
    if value is True:return 'true'
    if value is False:return 'false'
    if isinstance(value,str):return quote(value)
    if isinstance(value,list):return '['+','.join(canonical(v) for v in value)+']'
    need(isinstance(value,dict),'Native Codec scalars must be typed strings, bool or null; no JSON numbers')
    return '{'+','.join(quote(k)+':'+canonical(value[k]) for k in sorted(value,key=lambda x:x.encode('utf-16-be')))+'}'

def bits(x,n=8):
    need(finite(x),'Finite observed numeric value required')
    return struct.pack('>d' if n==8 else '>f',x).hex()

def number_bits(s,n):
    need(isinstance(s,str) and re.fullmatch('[0-9a-f]{%d}'%(n*2),s),'Exact native IEEE hex string required')
    x=struct.unpack('>d' if n==8 else '>f',bytes.fromhex(s))[0];need(math.isfinite(x),'Nonfinite persisted IEEE value');return x

def uint(x,zero=False):
    need(isinstance(x,str) and re.fullmatch('0|[1-9][0-9]*',x),'Exact uint decimal string required')
    value=int(x);need((0 if zero else 1)<=value<2**64,'Uint range');return value

def guid(value):
    need(isinstance(value,dict) and set(value)==set('ABCD'),'Persisted FGuid requires four actual uint32 members')
    parts=[uint(value[k],True) for k in 'ABCD'];need(all(x<2**32 for x in parts) and any(parts),'Persisted FGuid range/validity differs')
    return ''.join(f'{x:08X}' for x in parts)

def pin(path):
    p=Path(path).resolve();h=hashlib.sha256();n=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
    return dict(path=p.as_posix(),bytes=n,sha256=h.hexdigest())

def resolve_pin(row,base=ROOT):
    need(isinstance(row,dict) and type(row.get('bytes')) is int and row['bytes']>0
         and isinstance(row.get('sha256'),str) and re.fullmatch('[0-9a-f]{64}',row['sha256']),'Complete bytes/SHA pin required')
    p=Path(row['path']);p=(p if p.is_absolute() else Path(base)/p).resolve();value=pin(p)
    need((value['bytes'],value['sha256'])==(row['bytes'],row['sha256']),'Pinned file bytes/SHA differ: '+str(p));return p

def same_pin(a,b):
    norm=lambda r:(Path(r['path']) if Path(r['path']).is_absolute() else ROOT/r['path']).resolve()
    return norm(a)==norm(b) and (a['bytes'],a['sha256'])==(b['bytes'],b['sha256'])

def confined_pin(row,directory):
    p=resolve_pin(row);need(p.is_relative_to(Path(directory).resolve()),'Codec/evidence pin belongs to another archive');return p

def codec_file(row,directory,expected=None):
    p=confined_pin(row,directory);data=p.read_bytes()
    if expected is not None:need(data==expected,'Complete Codec bytes differ; subset equality is insufficient')
    return data

def verify_codec_bytes(data,checkpoint):
    doc=strict_json(data)
    need(canonical(doc).encode('utf-8')==data,'Codec is not exact native canonical bytes')
    need(set(doc)=={'codec','snapshot'} and doc['codec']=='bound-run-v2','Exact complete V2 Codec envelope required')
    s=doc['snapshot'];need(set(s)==ROOT_FIELDS and s['Schema']==s['Scope']=='2','Complete bound V2 root fields required')
    run=guid(s['RunGuid']);need(run==checkpoint['run'] and s['OwnerId']==checkpoint['owner'] and s['RoomInstanceId']==checkpoint['current_room'],'Whole Codec root identity differs from completed checkpoint')
    need(s['SimulationTime']==bits(checkpoint['sim']),'Codec clock bits differ from actual completed callback')
    players=[f for f in s['Fighters'] if f['EntityId']==checkpoint['owner']]
    need(len(players)==1 and players[0]['Kind']=='1' and players[0]['Schema']=='2','Exactly one actual BoundPlayer owner required')
    f=players[0]
    need(guid(f['RunGuid'])==checkpoint['run'] and f['RoomInstanceId']==checkpoint['current_room'] and f['Dead'] is False,'Persisted player identity/death differs')
    for name,observed in (('JumpHeight','H'),('JumpVelocity','V'),('LandingVisualAge','landing_age')):
        need(f[name]==bits(checkpoint[observed],4),'Whole Codec '+name+' bits differ from completed checkpoint')
    need(f['Facing']==bits(1.,4) and all(f['GroundPosition'][a]==bits(checkpoint['ground'][i]) for i,a in enumerate(('X','Y'))),'Whole Codec player facing/ground bits differ')
    view=s['Equipment']['View'];need(view['Bound'] is True and guid(view['RunGuid'])==checkpoint['run'] and view['OwnerId']==checkpoint['owner'] and view['RoomInstanceId']==checkpoint['current_room'],'Whole Codec equipment binding differs')
    active=int(view['ActiveSlot']);need(0<=active<2 and len(view['Slots'])==3,'Actual equipped weapon/armor slots required')
    for item,prefix,content in ((view['Slots'][active],'weapon','WPN-SWD-001'),(view['Slots'][2],'armor','ARM-LGT-001')):
        need(item['InstanceId']==checkpoint[prefix+'_instance'] and item['Version']==checkpoint[prefix+'_version'] and item['ContentId']==content,'Whole Codec committed SWD/LGT instance/version differs')
    return dict(run=run,owner=s['OwnerId'],current_room=s['RoomInstanceId'],simulation_time=number_bits(s['SimulationTime'],8),
                complete_codec_bytes=len(data),complete_codec_sha256=hashlib.sha256(data).hexdigest(),canonical_native_wire=True,
                native_semantic_validator_reimplemented=False)

def utc(value):
    result=datetime.fromisoformat(value.replace('Z','+00:00'));need(result.tzinfo is not None,'Actual timezone-aware OS receipt timestamp required');return result

def verify_process_order(source,target):
    need(type(source['process_id']) is int and type(target['process_id']) is int
         and 0<source['process_id']!=target['process_id']>0,'Different actual positive OS PIDs required')
    for r in (source,target):
        need(r['os_exit_confirmed'] is True and type(r['exit_code']) is int and r['exit_code']==0,'Actual successful OS process exit required')
        need(utc(r['started_utc'])<utc(r['exited_utc']),'Actual process lifetime ordering required')
    need(utc(source['exited_utc'])<utc(target['started_utc']),'Source must fully exit before fresh target launches')
    return dict(nonoverlapping_native_processes=True,source_pid=source['process_id'],target_pid=target['process_id'])

def expected_payload(codec,checkpoint,profile,build):
    versions=dict(contentRules='bound-development-guard-v2',coordinates='world-cm-v1',schema='bound-run-generation-v2')
    text='{"adapter":"bound-run-only-v2","buildId":'+quote(build)+',"generationId":"1","parentGeneration":"0","profileId":'+quote(profile.replace('-',''))+',"run":'
    text+=codec.decode('utf-8')+',"runGuid":'+quote(checkpoint['run'].lower())+',"runSimulationTime":'+quote(bits(checkpoint['sim']))+',"scope":"BoundDevelopmentRunV2","versions":{"contentRules":'+quote(versions['contentRules'])+',"coordinates":'+quote(versions['coordinates'])+',"schema":'+quote(versions['schema'])+'}}'
    return text,versions

def verify_store_bytes(bundle,marker,codec,checkpoint,profile,build):
    need(re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',profile) and int(profile.replace('-',''),16)>0,'New exact lower hyphenated ProfileGuid required')
    verify_codec_bytes(codec,checkpoint);payload,versions=expected_payload(codec,checkpoint,profile,build)
    expected='{"container_version":1,"ProfileID":'+quote(profile)+',"GenerationID":"1","parent_generation":"0","schema_version":'+quote(versions['schema'])+',"content_rules_version":'+quote(versions['contentRules'])+',"coordinate_version":'+quote(versions['coordinates'])+',"build_id":'+quote(build)+',"run_sim_time_or_null":'+format(checkpoint['sim'],'.17g')+',"restored_from_generation":"0","payload":'+payload+'}'
    need(bundle==expected.encode('utf-8'),'Published complete bundle/header/BuildId/payload is not exact gen1/parent0 native wire')
    sha=hashlib.sha256(bundle).hexdigest();crc=zlib.crc32(bundle)&0xffffffff
    body='{"container_version":1,"ProfileID":'+quote(profile)+',"GenerationID":"1","parent_generation":"0","bundle_byte_length":'+quote(str(len(bundle)))+',"bundle_sha256":'+quote(sha)+',"bundle_crc32":'+quote(str(crc))+'}'
    expected_marker=body[:-1]+',"marker_integrity_digest":'+quote(hashlib.sha256(body.encode()).hexdigest())+'}'
    need(marker==expected_marker.encode(),'Published marker digest/head/length/CRC differs from complete native bundle')
    return dict(generation='1',parent='0',bundle_sha256=sha,bundle_crc32=crc,bundle_bytes=len(bundle),marker_sha256=hashlib.sha256(marker).hexdigest(),complete_payload_codec_byte_equal=True)

def verify_pristine(facts,observation):
    yes='pristine_api controller_local controller_authoritative controller_input_present controller_player_state_present controller_spectator_pawn_null default_pawn_class_null spectator_class_null world_begun_play player_null controller_pawn_null inventory_null run_guid_invalid'.split()
    no='controller_only_spectator equipment_bound scene_active rewards_bound world_run_valid audio_run_valid enter_down'.split()
    zero='native_pawns native_fighters restart_serial epoch combat_seed next_crit_draw fog_rooms world_bindings audio_records'.split()
    need(all(facts[k] is True for k in yes) and all(facts[k] is False for k in no),'Actual pristine native controller/noPawn/noRun facts differ')
    need(all(facts[k]=='0' for k in zero) and facts['gate']=='3' and facts['simulation_time_bits']==bits(0.),'Pristine clock/epoch/restart/history/seed not empty')
    need(observation['completed_callback'] is True and observation['has_player'] is False and observation['install_gate']==3 and observation['epoch']==observation['restart_serial']=='0' and observation['sim']==0,'Pristine needs its own real completed noPawn callback')
    need(observation['run']=='0'*32 and observation['owner']==observation['current_room']=='0','Pristine completed callback cannot borrow a previous Run/owner/room')
    forbidden='player_entity ground facing jump_height vertical_velocity landing_visual_age physical_visual_key hp dead melee_time wa_time dodge_time weapon_world_time native_actor_root_z new_air_query_ok weapon_instance weapon_version armor_instance armor_version'.split()
    need(not any(k in observation for k in forbidden),'Pristine callback cannot borrow old player data')
    need(observation['rendered_player_stack']==[] and observation['new_air_draw']['drawn'] is False and observation['new_air_draw']['slot_count']==0,'Pristine cannot submit a player draw')
    return dict(real_pristine_completed_callback=True,epoch='0',restart_serial='0',install_gate=3)

def verify_prepare(prepare,loaded,source_codec,original,build):
    need(prepare['load_status']==0 and prepare['observed_head_generation']==prepare['generation_id']=='1' and prepare['parent_generation']=='0' and prepare['loaded_build_id']==build,'Actual highest published gen1/parent0 load/BuildId differs')
    need(prepare['before_epoch']==prepare['before_restart_serial']=='0' and prepare['after_epoch']=='1' and prepare['after_restart_serial']=='0' and prepare['gate_preparing']==1 and prepare['installed_gate']==2,'Actual pristine Prepare/Install epoch0to1/restart0 gate differs')
    for key in ('prepared_ready','all_staged_hidden_tick_collision_off','unpublished_during_prepare','install_ok','prepared_consumed','controller_possesses_restored_player'):need(prepare[key] is True,'Actual native prepare/install fact missing: '+key)
    actors=prepare['staged_actors'];need(len(actors)==prepare['staged_actor_count']>0 and len({a['local_actor_path'] for a in actors})==len(actors),'Prepared native actor membership differs')
    need(all(a['local_actor_path'] and a['hidden'] is True and a['tick_enabled'] is False and a['collision_enabled'] is False for a in actors),'Staged actors must remain hidden/tick/collision-off')
    players=[a for a in actors if a['is_player'] is True]
    need(len(players)==1 and players[0]['local_actor_path']==prepare['prepared_player_actor_path']==prepare['installed_player_actor_path'],'Actual staged player was not the installed possessed player')
    need(codec_file(prepare['loaded_codec'],original,source_codec)==loaded and codec_file(prepare['installed_codec'],original,source_codec)==loaded,'Whole loaded/installed Codec differs')
    need(finite(prepare['installed_monotonic_s']) and prepare['installed_monotonic_s']>0,'Actual installed monotonic timestamp required')
    return dict(native_prepare_install_possess_verified=True,staged_actors=len(actors),epoch='1',restart_serial='0')

def selected_pose(h,v,age):
    need(all(finite(x) for x in (h,v,age)) and h>=0,'Finite native physical sample required')
    if h>0 or v>0:return 0 if v>315 else 1 if v>90 else 2 if v>=-90 else 3
    return (4 if age<number_bits(bits(.06,4),4) else 5) if h==v==0 and 0<=age<number_bits(bits(.12,4),4) else -1

def verify_common(r,role):
    need(r['schema']=='hero-air-disk-restore-native-observer-v001' and r['role']==role and type(r['requested_facing']) is int and r['requested_facing']==1,'Wrong actual v144 runtime role/schema/facing')
    need(r['passed'] is True and r['flow_complete'] is True and r['failure']=='','Actual v144 flow must complete; OS exit0 alone insufficient')
    for k in ('final_accepted','visual_reviewed','audio_listened','observer_forced_gameplay_writes','game_tick_called_manually','V2_itself_proves_running_binary_compatibility'):need(r[k] is False,'Native proof scope changed: '+k)
    need(r['snapshot_restoration_via_actual_installer'] is (role=='target'),'Actual Installer restoration must be explicitly distinguished from forbidden observer state forcing')
    obs=r['observations'];need(obs,'Actual completed native callbacks required')
    times=r['capture_timing'];offsets=times['frame_wall_offsets_s'];duration=times['capture_stop_monotonic_s']-times['capture_start_monotonic_s']
    need(times['use_fixed_time_step'] is False and len(offsets)==len(obs) and duration>0,'Original variable audio/video timing required')
    last_draw=0
    for i,o in enumerate(obs):
        need(type(o['has_player']) is bool and type(o['install_gate']) is int and o['install_gate'] in (0,1,2,3),'Actual typed player/gate fields required')
        need(o['completed_callback'] is True and finite(o['wall_offset_s']) and finite(o['sim']) and 0<=o['wall_offset_s']<duration and o['wall_offset_s']==offsets[i],'Completed callback/timestamp binding differs')
        need(not i or (o['wall_offset_s']>obs[i-1]['wall_offset_s'] and o['sim']>=obs[i-1]['sim']),'Actual callback clocks are not monotonic')
        need(o['interface_visible'] is False and o['text_calls']==0 and o['range_debug'] is False and o['range_lines']==0,'Actual traditional UI/range must remain hidden')
        need(len(o['camera_ground'])==2 and all(finite(x) for x in o['camera_ground']),'Actual per-callback camera required')
        if not o['has_player']:continue
        need(o['player_entity']==o['owner']==r['owner'] and o['run']==r['run'] and o['current_room']==r['current_room'],'Actual callback logical player identity differs')
        need(o['hp']==r['initial_hp'] and o['dead'] is False and o['native_actor_root_z']==0,'Actual player HP/death/native plane changed')
        need(all(o[k]==o['sim'] for k in ('melee_time','wa_time','dodge_time','weapon_world_time')),'Native owner clocks differ')
        need(o['physical_visual_key']==selected_pose(o['jump_height'],o['vertical_velocity'],o['landing_visual_age']),'Native physical pose differs from raw H/V/age')
        need(o['old_draw']['sim']==o['sim'] and o['old_draw']['actual_stack']==o['rendered_player_stack'],'Actual completed submitted old stack/time differs')
        draw=uint(o['old_draw']['draw_id']);need(draw>last_draw,'Actual completed player draw ID must be fresh');last_draw=draw
        if role=='target':need(o['facing']==1,'Target must retain its real saved right facing')
    need(r['capture_final_hp']==r['initial_hp'] and r['native_async_capture_writes_flushed'] is True,'Actual final HP or PNG flush differs')
    for q in r['normal_inputs']:
        need(q['context_sampled_before_InputKey'] is True and finite(q['sim']) and finite(q['wall_offset_s']) and 0<=q['wall_offset_s']<duration,'Real input must belong to this capture origin')
        if 'before_H' in q:
            need(q['before_H']==q['after_H'] and q['before_V']==q['after_V'] and q['before_landing_age']==q['after_landing_age'],'InputKey immediate raw values must remain queued; no fabricated synchronous physics')
    return obs

def verify_equipment(r):
    e=r['equipment'];obs=r['observations'];inputs=r['normal_inputs']
    qi,si,ci,ri=(e[k] for k in ('equipment_input_index','equipment_started_callback_index','equipment_commit_callback_index','ready_callback_index'))
    need(all(type(x) is int for x in (qi,si,ci,ri)) and 0<=qi<len(inputs) and 0<=si<ci<=ri<len(obs),'Real E start/commit/completed Ready indices required')
    q=inputs[qi];start=obs[si]['equipment_action'];commit=obs[ci]['equipment_action'];ready=obs[ri]
    need([x for x in inputs if x['key']=='E' and x['down'] is True]==[q] and q['selected_source_id']==e['light_source_id'] and q['before_equipment_action']['active'] is False,'Exactly one real selected-source normal E queue required')
    first=next((i for i,o in enumerate(obs) if o['wall_offset_s']>q['wall_offset_s'] and o['equipment_action']['active']),None)
    need(first==si and q['wall_offset_s']<obs[si]['wall_offset_s'],'First newly active E callback cannot be skipped')
    fields=('kind','action_id','operation_id','source_id','instance_id','slot','start','deadline')
    need(start['active'] is True and commit['active'] is False and start['kind']==2 and start['slot']==2 and start['source_id']==e['light_source_id'] and start['instance_id']==r['armor_instance'],'Actual real PickupArmor source/instance/slot required')
    need(uint(start['action_id'])>uint(q['before_equipment_action']['action_id'],True) and uint(start['operation_id'])>0,'E action/operation must be newly started')
    need(all(start[k]==commit[k]==ready['equipment_action'][k] for k in fields) and start['start']==e['equipment_start'] and start['deadline']==e['equipment_deadline']==start['start']+.50,'Exact original E .50 action/deadline differs')
    need(q['sim']<=start['start']<=obs[si]['sim']<start['deadline']<=obs[ci]['sim']<=ready['sim'],'Actual E .50 operation clock order differs')
    need(all(o['equipment_action']['active'] is True and all(o['equipment_action'][k]==start[k] for k in fields) and o['sim']<start['deadline'] for o in obs[si:ci]),'Actual E cancelled/skipped before commit')
    need(obs[si]['next_operation_id']==start['operation_id'] and uint(obs[ci]['next_operation_id'])==uint(start['operation_id'])+1,'Actual E operation commit boundary differs')
    need(e['ready_consumed_once'] is True and ready['old_draw']['clip']=='sword_ready_idle' and len(ready['rendered_player_stack'])==7 and ready['new_air_draw']['drawn'] is False,'Completed brown Ready token required before source Space')
    need(ready['jump_height']==ready['vertical_velocity']==0 and ready['landing_visual_age']==number_bits(bits(.12,4),4),'Completed actual grounded Ready required')
    return ri

def verify_source_flow(r,codec):
    obs=verify_common(r,'source');need(all(o['has_player'] is True and o['epoch']=='0' and o['restart_serial']=='1' and o['install_gate']==0 for o in obs),'Source must be its real fresh FirstBatch epoch0/restart1/Open')
    need(r['epoch']=='0' and r['restart_serial']=='1' and r['normal_space_down_inputs']==1,'Source must save one original jump only')
    ready=verify_equipment(r);cp=r['checkpoint'];ci=cp['observation_index'];need(type(ci) is int and ci==len(obs)-1 and ci>ready,'Source must stop after its own completed Apex checkpoint')
    o=obs[ci];need(cp['same_completed_game_thread_boundary'] is True and cp['is_game_thread'] is True,'Capture must occur at the same completed game-thread boundary')
    need(all(cp[k]==o[k]==r[k] for k in IDENTITY+('epoch','restart_serial')) and cp['sim']==o['sim'] and cp['ground']==o['ground'],'Checkpoint callback identity/clock/ground differs')
    need(cp['H']==o['jump_height']>0 and cp['V']==o['vertical_velocity'] and -90<=cp['V']<=90 and cp['landing_age']==o['landing_visual_age'] and o['physical_visual_key']==2,'Source checkpoint is not real completed Apex H>0/-90<=V<=90')
    need(all(all(x[k]==cp[k] for k in IDENTITY) and x['facing']==1 for x in obs[ready:]),'Committed source Ready/Air logical gear/facing changed')
    space=[q for q in r['normal_inputs'] if q['key']=='SpaceBar' and q['down'] is True]
    need(len(space)==1,'Exactly one actual source normal Space required');q=space[0]
    need(obs[ready]['wall_offset_s']<q['wall_offset_s']<o['wall_offset_s'] and obs[ready]['sim']<=q['sim']<o['sim'],'Source Space must follow its own completed brown Ready')
    need(all(q[k]==cp[k] for k in IDENTITY+('epoch','restart_serial')) and q['before_H']==q['before_V']==0 and q['before_landing_age']==number_bits(bits(.12,4),4),'Source Space cannot borrow another player or landing jump')
    air=[(i,x) for i,x in enumerate(obs) if x['wall_offset_s']>q['wall_offset_s'] and (x['jump_height']>0 or x['vertical_velocity']>0)]
    need(air and air[0][1]['jump_height']>0 and air[0][1]['vertical_velocity']<=630
         and not any(x['jump_height']>0 or x['vertical_velocity']>0 for x in obs if x['wall_offset_s']<=q['wall_offset_s']),
         'Source cannot borrow a jump that already existed before its only normal Space')
    need(next((i for i,x in air if x['physical_visual_key']==2),None)==ci,'Source skipped/borrowed its first actual completed Apex')
    need(all(x['physical_visual_key'] in (0,1,2) for _,x in air),'Source must save its first real Apex before Fall/landing')
    need(all(x['key'] in ('Enter','D','E','SpaceBar') for x in r['normal_inputs'] if x['down'] is True),'Other gameplay input cannot manufacture source checkpoint')
    need(len([q for q in r['normal_inputs'] if q['key']=='Enter' and q['down'] is True])==1,'Source must start with exactly one normal Enter')
    verified=verify_codec_bytes(codec,cp)
    return dict(ready_callback=ready,completed_apex_callback=ci,one_original_Space=True,observed_rise_apex_poses=sorted({x['physical_visual_key'] for _,x in air}),whole_codec=verified)

def verify_target_flow(r,source,codec,original):
    obs=verify_common(r,'target');cp=source['checkpoint'];need(all(r[k]==source[k] for k in IDENTITY),'Target logical Run/owner/room/gear differs from disk source')
    need(r['epoch']=='1' and r['restart_serial']=='0' and r['initial_hp']==source['initial_hp'],'Installed target epoch/restart/HP differs')
    pristine=r['pristine_before'];pi=pristine['observation_index'];need(type(pi) is int and pi==0 and pristine['wall_offset_s']==obs[pi]['wall_offset_s'],'Target must begin with its own first completed pristine callback')
    for o in obs:
        if not o['has_player']:verify_pristine(pristine,o)
    need(r['source_process_running_at_target_begin'] is False and uint(r['expected_source_pid'])==uint(source['process_id']),'Target source-PID exit fact differs')
    verify_prepare(r['prepare_install'],codec,codec,original,r['build_id'])
    pause=r['pause_checks'];need(len(pause)>=3,'At least three actual paused completed callbacks required')
    indices=[q['observation_index'] for q in pause];need(indices==sorted(set(indices)) and all(type(i) is int and pi<i<len(obs) for i in indices),'Actual pause callback membership differs')
    seen=[i for i,o in enumerate(obs) if o['has_player'] and o['install_gate']==2];need(indices==seen,'Every completed Await callback needs its own wholeCodec, not selected subsets')
    for q,i in zip(pause,indices):
        o=obs[i];need(q['whole_equal_loaded'] is True and q['wall_offset_s']==o['wall_offset_s'] and q['sim']==o['sim']==cp['sim'] and q['install_gate']==o['install_gate']==2 and q['epoch']==o['epoch']=='1' and q['restart_serial']==o['restart_serial']=='0','Paused completed callback clock/gate/epoch differs')
        need(o['physical_visual_key']==2 and o['jump_height']==cp['H'] and o['vertical_velocity']==cp['V'] and o['landing_visual_age']==cp['landing_age'] and o['ground']==cp['ground'],'Installed paused Apex raw state differs from saved sample')
        need(all(o[k]==cp[k] for k in IDENTITY),'Paused target uses another logical Run/gear')
        codec_file(q['codec'],original,codec)
    res=r['resume'];inputs=r['normal_inputs'];qi=res['enter_input_index'];need(type(qi) is int and 0<=qi<len(inputs),'Actual fresh Enter input index required')
    q=inputs[qi];pressed=[x for x in inputs if x['down'] is True]
    need(pressed==[q] and q['key']=='Enter' and q['forced_release'] is False and q['analog_zero_event'] is False,'Target only gameplay down edge must be one fresh normal Enter; no Space/R/restart')
    need(q['install_gate']==2 and q['epoch']=='1' and q['restart_serial']=='0' and all(q[k]==cp[k] for k in IDENTITY),'Fresh Enter context differs from installed original Run')
    need(q['before_H']==cp['H'] and q['before_V']==cp['V'] and q['before_landing_age']==cp['landing_age'] and q['sim']==cp['sim'],'Target Enter cannot alter/resample a different paused jump')
    before_enter=[i for i in indices if obs[i]['wall_offset_s']<q['wall_offset_s']]
    need(len(before_enter)>=3,'At least three actual wholeCodec paused callbacks must precede Enter')
    last=before_enter[-1];need(res['last_paused_callback_index']==last,'Enter must consume its own last completed paused callback')
    installed=r['prepare_install']['installed_monotonic_s'];origin=r['capture_timing']['capture_start_monotonic_s']
    need(origin+q['wall_offset_s']-installed>=.20,'Fresh Enter occurred before original .20s wall-clock pause')
    need(origin+obs[last]['wall_offset_s']-installed>=.20,'Last completed wholeCodec pause must actually reach .20s before Enter')
    neutral=r['neutral_checks'];need(neutral and {n['observation_index'] for n in neutral}==set(indices),'Full neutral controls must be observed on actual paused callbacks')
    neutral_before=[n for n in neutral if n['observation_index']==last and n['neutral_all'] is True and n['enter_down'] is False and n['enter_just_pressed'] is False and n['held_gameplay_keys']==[] and n['nonzero_gamepad_axes']==[]]
    need(len(neutral_before)==1,'Final completed paused callback must observe released Enter and full-neutral controls')
    for n in neutral:
        i=n['observation_index'];upper=obs[i+1]['wall_offset_s'] if i+1<len(obs) else r['capture_timing']['capture_stop_monotonic_s']-r['capture_timing']['capture_start_monotonic_s']
        need(obs[i]['wall_offset_s']<=n['wall_offset_s']<upper and n['sim']==obs[i]['sim'] and n['install_gate']==2,'Neutral fact borrowed another callback/time/gate')
    releases=[x for x in inputs if x['forced_release'] is True and x['down'] is False and x['wall_offset_s']<obs[last]['wall_offset_s']]
    need(any(x['key']=='Enter' for x in releases) and all(x['install_gate']==2 for x in releases),'Public Enter/full-controls release must precede a real observed neutral frame')
    first=res['first_open_callback_index'];need(type(first) is int and indices[-1]<first<len(obs) and q['wall_offset_s']<obs[first]['wall_offset_s'] and obs[first]['install_gate']==0,'Fresh Enter needs its own later completed Open callback; queued Await callbacks are legitimate')
    need(next((i for i,o in enumerate(obs) if o['has_player'] and o['install_gate']==0),None)==first,'First reopened callback was skipped/borrowed')
    continued=obs[first:];need(all(o['has_player'] and o['install_gate']==0 and o['epoch']=='1' and o['restart_serial']=='0' and all(o[k]==cp[k] for k in IDENTITY) for o in continued),'Original continued Run/epoch/gear changed')
    need(obs[first]['sim']>=cp['sim'] and obs[-1]['sim']>cp['sim'] and res['simulation_advanced_from_saved'] is True,'Native simulation must continue from saved time')
    airborne=[o for o in continued if o['jump_height']>0 or o['vertical_velocity']>0]
    need(airborne and airborne[0]['vertical_velocity']<=cp['V'] and all(o['physical_visual_key'] in (2,3) for o in airborne),'Target reset into Rise/new jump instead of original Apex/Fall')
    need(all(b['vertical_velocity']<=a['vertical_velocity'] for a,b in zip(airborne,airborne[1:])),'Original airborne velocity cannot rise/restart without an input')
    poses=[o['physical_visual_key'] for o in continued if o['physical_visual_key']>=0]
    need(3 in poses and 4 in poses and 5 in poses and poses==sorted(poses) and res['continued_mask']==60,'Original Fall/Land4/Land5 continuation incomplete or reordered')
    ready=[o for o in continued if o['old_draw']['clip']=='sword_ready_idle']
    need(len(ready)==res['ready_join_frames']>=2 and all(o['jump_height']==o['vertical_velocity']==0 and o['landing_visual_age']==number_bits(bits(.12,4),4) and o['physical_visual_key']==-1 for o in ready),'At least two genuine original grounded Ready joins required')
    need(r['normal_space_down_inputs']==res['normal_space_down_inputs']==0,'Target must not create another Space jump')
    return dict(pristine_callback=pi,paused_callback_count=len(pause),pause_wall_s=origin+q['wall_offset_s']-installed,neutral_callback=last,fresh_Enter_input=qi,first_open_callback=first,original_trajectory_continued=True,gameplay_substeps_reconstructed=False)
