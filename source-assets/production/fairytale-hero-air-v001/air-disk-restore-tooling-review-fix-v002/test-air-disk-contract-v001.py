"""Explicit HOST_DATA_ONLY fixtures; no native checker, UE, recording or approval."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,struct,unittest,copy,hashlib,zlib,sys
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v144_contract',P/'air_disk_contract_v001.py');C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
RUN=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
FIX=P/'_host-fixtures'/RUN
FIX.mkdir(parents=True,exist_ok=False)
def bits(x,n=8):return struct.pack('>d' if n==8 else '>f',x).hex()
def fixture():
    cp=dict(run='ABCDEF12123456781234567812345678',owner='1',current_room='2',epoch='0',restart_serial='1',sim=2.5,ground=[400.,0.],H=109.,V=-5.,landing_age=struct.unpack('>f',struct.pack('>f',.12))[0],weapon_instance='3',weapon_version='1',armor_instance='4',armor_version='2')
    fighter=dict(Schema='2',RunGuid=cp['run'],RoomInstanceId='2',EntityId='1',Kind='1',GroundPosition=dict(X=bits(400.),Y=bits(0.)),JumpHeight=bits(109.,4),JumpVelocity=bits(-5.,4),LandingVisualAge=bits(.12,4),Facing=bits(1.,4),Dead=False,Player=dict(),WeaponId='WPN-SWD-001',ArmorId='ARM-LGT-001')
    view=dict(Bound=True,RunGuid=cp['run'],OwnerId='1',RoomInstanceId='2',ActiveSlot='0',Slots=[dict(InstanceId='3',Version='1',ContentId='WPN-SWD-001'),dict(InstanceId='0',Version='0',ContentId=''),dict(InstanceId='4',Version='2',ContentId='ARM-LGT-001')])
    root=dict(Schema='2',Scope='2',RunGuid=cp['run'],OwnerId='1',RoomInstanceId='2',RoomNumber='1',SimulationTime=bits(2.5),LastStoneWakeStartedAt=bits(-1.),RoomCleared=False,GameOver=False,WaitingForStart=False,SceneCommitRequested=False,SceneEquipmentTargetLost=False,LastMessage='HOST fixture',SceneEncounterEntityId='0',Geometry={},Equipment=dict(View=view),Scene={},WeaponWorld={},Fighters=[fighter],EnemyOrder=[],Rewards={},Pickups=[],Exploration={},Audio={})
    g={k:str(int(cp['run'][i*8:(i+1)*8],16)) for i,k in enumerate('ABCD')}
    fighter['RunGuid']=g;view['RunGuid']=g;root['RunGuid']=g
    doc=dict(codec='bound-run-v2',snapshot=root)
    data=json.dumps(doc,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    return data,cp

def pristine():
    yes='pristine_api controller_local controller_authoritative controller_input_present controller_player_state_present controller_spectator_pawn_null default_pawn_class_null spectator_class_null world_begun_play player_null controller_pawn_null inventory_null run_guid_invalid'.split()
    no='controller_only_spectator equipment_bound scene_active rewards_bound world_run_valid audio_run_valid enter_down'.split()
    zero='native_pawns native_fighters restart_serial epoch combat_seed next_crit_draw fog_rooms world_bindings audio_records'.split()
    facts={**{k:True for k in yes},**{k:False for k in no},**{k:'0' for k in zero},'gate':'3','simulation_time_bits':bits(0.),'observation_index':0,'wall_offset_s':.01,'api_diagnostic':''}
    o=dict(completed_callback=True,has_player=False,wall_offset_s=.01,phase=10,sim=0.,run='0'*32,owner='0',current_room='0',epoch='0',restart_serial='0',install_gate=3,camera_ground=[0,0],old_draw=dict(clip='',actual_stack=[]),new_air_draw=dict(drawn=False,slot_count=0,actual_stack=[]),rendered_player_stack=[],interface_visible=False,text_calls=0,range_debug=False,range_lines=0)
    return facts,o

def target_fixture(path):
    path.mkdir();data,cp=fixture();source=dict(checkpoint=cp,process_id='10',initial_hp=100.,build_id='HOST_BUILD',**{k:cp[k] for k in C.IDENTITY})
    for name in ['loaded-codec.json','installed-codec.json']+[f'pause-codec-{i:06d}.json' for i in range(4)]:
        with (path/name).open('xb') as f:f.write(data)
    facts,first=pristine();obs=[first]
    # Four Await callbacks: the fourth really follows queued Enter but precedes
    # actual Open. This must pass without pretending InputKey is synchronous.
    for i,(wall,sim,h,v,age,gate) in enumerate([( .03,2.5,109,-5,.12,2),(.13,2.5,109,-5,.12,2),(.24,2.5,109,-5,.12,2),(.26,2.5,109,-5,.12,2),(.28,2.516,108.7,-33.8,.12,0),(.40,2.636,90.,-249.8,.12,0),(.70,2.936,0.,0.,.02,0),(.76,2.996,0.,0.,.08,0),(.82,3.056,0.,0.,.12,0),(.84,3.076,0.,0.,.12,0)],1):
        pose=C.selected_pose(h,v,age);ready=pose<0;stack=[f'HOST_PART_{n}' for n in range(7 if ready else 9)]
        obs.append(dict(completed_callback=True,has_player=True,wall_offset_s=wall,phase=11 if i<=3 else 12,sim=sim,run=cp['run'],owner='1',current_room='2',epoch='1',restart_serial='0',install_gate=gate,camera_ground=[400.,0.],old_draw=dict(clip='sword_ready_idle' if ready else 'sword_nonattack_air',actual_stack=stack,sim=sim,frame=max(0,pose),draw_id=str(i)),new_air_draw=dict(drawn=not ready,slot_count=0 if ready else 9,actual_stack=[] if ready else stack),rendered_player_stack=stack,interface_visible=False,text_calls=0,range_debug=False,range_lines=0,player_entity='1',ground=[400.,0.],facing=1,jump_height=h,vertical_velocity=v,landing_visual_age=C.number_bits(bits(age,4),4) if not h else cp['landing_age'],physical_visual_key=pose,hp=100.,dead=False,native_actor_root_z=0.,melee_time=sim,wa_time=sim,dodge_time=sim,weapon_world_time=sim,weapon_instance='3',weapon_version='1',armor_instance='4',armor_version='2'))
    base=dict(context_sampled_before_InputKey=True,sim=2.5,run=cp['run'],owner='1',current_room='2',epoch='1',restart_serial='0',install_gate=2,player_entity='1',facing=1,weapon_instance='3',weapon_version='1',armor_instance='4',armor_version='2',before_H=109.,after_H=109.,before_V=-5.,after_V=-5.,before_landing_age=cp['landing_age'],after_landing_age=cp['landing_age'])
    releases=[dict(**base,key=k,down=False,forced_release=True,analog_zero_event=False,wall_offset_s=.025) for k in ('Enter','D','SpaceBar')]
    enter=dict(**base,key='Enter',down=True,forced_release=False,analog_zero_event=False,wall_offset_s=.25)
    actors=[dict(local_actor_path='HOST_STAGED_PLAYER',hidden=True,tick_enabled=False,collision_enabled=False,is_player=True)]
    prepare=dict(load_status=0,observed_head_generation='1',generation_id='1',parent_generation='0',loaded_build_id='HOST_BUILD',before_epoch='0',before_restart_serial='0',after_epoch='1',after_restart_serial='0',gate_preparing=1,installed_gate=2,prepared_ready=True,all_staged_hidden_tick_collision_off=True,unpublished_during_prepare=True,install_ok=True,prepared_consumed=True,controller_possesses_restored_player=True,staged_actors=actors,staged_actor_count=1,prepared_player_actor_path='HOST_STAGED_PLAYER',installed_player_actor_path='HOST_STAGED_PLAYER',loaded_codec=C.pin(path/'loaded-codec.json'),installed_codec=C.pin(path/'installed-codec.json'),installed_monotonic_s=100.02)
    pause=[dict(observation_index=i,wall_offset_s=obs[i]['wall_offset_s'],sim=2.5,install_gate=2,epoch='1',restart_serial='0',codec=C.pin(path/f'pause-codec-{i-1:06d}.json'),whole_equal_loaded=True) for i in range(1,5)]
    neutral=[dict(observation_index=i,wall_offset_s=obs[i]['wall_offset_s']+.0001,sim=2.5,install_gate=2,enter_down=i==4,enter_just_pressed=i==4,held_gameplay_keys=['Enter'] if i==4 else [],nonzero_gamepad_axes=[],neutral_all=i!=4) for i in range(1,5)]
    report=dict(schema='hero-air-disk-restore-native-observer-v001',role='target',requested_facing=1,passed=True,flow_complete=True,failure='',final_accepted=False,visual_reviewed=False,audio_listened=False,observer_forced_gameplay_writes=False,snapshot_restoration_via_actual_installer=True,game_tick_called_manually=False,V2_itself_proves_running_binary_compatibility=False,epoch='1',restart_serial='0',initial_hp=100.,capture_final_hp=100.,native_async_capture_writes_flushed=True,observations=obs,capture_timing=dict(use_fixed_time_step=False,capture_start_monotonic_s=100.,capture_stop_monotonic_s=101.,frame_wall_offsets_s=[o['wall_offset_s'] for o in obs]),normal_inputs=releases+[enter],pristine_before=facts,source_process_running_at_target_begin=False,expected_source_pid='10',prepare_install=prepare,pause_checks=pause,neutral_checks=neutral,resume=dict(enter_input_index=3,last_paused_callback_index=3,first_open_callback_index=5,continued_mask=60,ready_join_frames=2,normal_space_down_inputs=0,simulation_advanced_from_saved=True),normal_space_down_inputs=0,build_id='HOST_BUILD',**{k:cp[k] for k in C.IDENTITY})
    return report,source,data

def retain(name,value):
    with (FIX/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(authority='HOST_DATA_ONLY_NOT_NATIVE_OR_ROOT_APPROVAL',fixture=value),f,ensure_ascii=False,indent=2);f.write('\n')

def source_fixture(path):
    template,source,data=target_fixture(path);cp=copy.deepcopy(source['checkpoint']);cp.update(observation_index=7,same_completed_game_thread_boundary=True,is_game_thread=True)
    obs=[];action=dict(kind=2,action_id='1',operation_id='1',source_id='7',instance_id='4',slot=2,start=1.,deadline=1.5)
    for i,(wall,sim,h,v) in enumerate([(.01,0.,0.,0.),(.10,1.,0.,0.),(.35,1.25,0.,0.),(.60,1.5,0.,0.),(.62,2.14,0.,0.),(.66,2.17,12.,594.),(.86,2.37,100.,234.),(1.,2.5,109.,-5.)]):
        o=copy.deepcopy(template['observations'][1]);pose=C.selected_pose(h,v,cp['landing_age']);stack=[f'HOST_SOURCE_PART_{n}' for n in range(9 if h else 7)]
        o.update(wall_offset_s=wall,sim=sim,epoch='0',restart_serial='1',install_gate=0,jump_height=h,vertical_velocity=v,physical_visual_key=pose,melee_time=sim,wa_time=sim,dodge_time=sim,weapon_world_time=sim,equipment_action=dict(**action,active=i in (1,2)),next_operation_id='1' if i<3 else '2')
        o['old_draw'].update(sim=sim,draw_id=str(i+1),clip='sword_nonattack_air' if h else 'sword_ready_idle',frame=max(0,pose),actual_stack=stack);o['rendered_player_stack']=stack;o['new_air_draw'].update(drawn=bool(h),slot_count=9 if h else 0,actual_stack=stack if h else [])
        obs.append(o)
    base=dict(context_sampled_before_InputKey=True,epoch='0',restart_serial='1',install_gate=0,before_H=0.,after_H=0.,before_V=0.,after_V=0.,before_landing_age=cp['landing_age'],after_landing_age=cp['landing_age'],**{k:cp[k] for k in C.IDENTITY})
    inputs=[dict(**base,key='Enter',down=True,forced_release=False,analog_zero_event=False,sim=0.,wall_offset_s=.005),dict(**base,key='D',down=True,forced_release=False,analog_zero_event=False,sim=.01,wall_offset_s=.02),dict(**base,key='E',down=True,forced_release=False,analog_zero_event=False,sim=.99,wall_offset_s=.09,selected_source_id='7',before_equipment_action=dict(active=False,action_id='0')),dict(**base,key='SpaceBar',down=True,forced_release=False,analog_zero_event=False,sim=2.14,wall_offset_s=.64)]
    r=copy.deepcopy(template);r.update(role='source',process_id='10',epoch='0',restart_serial='1',snapshot_restoration_via_actual_installer=False,observations=obs,normal_inputs=inputs,normal_space_down_inputs=1,checkpoint=cp,equipment=dict(equipment_input_index=2,equipment_started_callback_index=1,equipment_commit_callback_index=3,ready_callback_index=4,light_source_id='7',equipment_start=1.,equipment_deadline=1.5,ready_consumed_once=True),capture_timing=dict(use_fixed_time_step=False,capture_start_monotonic_s=100.,capture_stop_monotonic_s=102.,frame_wall_offsets_s=[o['wall_offset_s'] for o in obs]))
    return r,data
class Checks(unittest.TestCase):
    def test_whole_wire_fixture_binds_checkpoint_fields(self):
        data,cp=fixture();self.assertEqual(C.verify_codec_bytes(data,cp)['run'],cp['run'])
    def test_changed_H_without_changed_checkpoint_rejected(self):
        data,cp=fixture();value=json.loads(data);value['snapshot']['Fighters'][0]['JumpHeight']=bits(1.,4)
        with self.assertRaises(ValueError):C.verify_codec_bytes(json.dumps(value,sort_keys=True,separators=(',',':')).encode(),cp)
    def test_duplicate_codec_key_rejected(self):
        data,cp=fixture();data=data.replace(b'"codec":"bound-run-v2"',b'"codec":"bound-run-v2","codec":"bound-run-v2"')
        with self.assertRaises(ValueError):C.verify_codec_bytes(data,cp)
    def test_wrong_codec_identity_rejected(self):
        data,cp=fixture();cp['run']='f'*32
        with self.assertRaises(ValueError):C.verify_codec_bytes(data,cp)
    def test_no_true_OS_exit_cannot_restore(self):
        source=dict(process_id=10,started_utc='2026-10-19T00:00:00+00:00',exited_utc='2026-10-19T00:00:02+00:00',exit_code=0,os_exit_confirmed=True)
        target=dict(process_id=11,started_utc='2026-10-19T00:00:03+00:00',exited_utc='2026-10-19T00:00:04+00:00',exit_code=0,os_exit_confirmed=True)
        self.assertTrue(C.verify_process_order(source,target)['nonoverlapping_native_processes'])
        target['started_utc']='2026-10-19T00:00:01+00:00'
        with self.assertRaises(ValueError):C.verify_process_order(source,target)

    def test_same_PID_or_unconfirmed_OS_exit_rejected(self):
        source=dict(process_id=10,started_utc='2026-10-19T00:00:00+00:00',exited_utc='2026-10-19T00:00:02+00:00',exit_code=0,os_exit_confirmed=True)
        target=dict(process_id=10,started_utc='2026-10-19T00:00:03+00:00',exited_utc='2026-10-19T00:00:04+00:00',exit_code=0,os_exit_confirmed=True)
        with self.assertRaisesRegex(ValueError,'Different actual'):C.verify_process_order(source,target)
        target['process_id']=11;source['os_exit_confirmed']=False;retain(self._testMethodName,dict(source=source,target=target))
        with self.assertRaisesRegex(ValueError,'OS process exit'):C.verify_process_order(source,target)

    def test_missing_whole_root_or_wrong_persisted_guid_shape_rejected(self):
        data,cp=fixture();value=json.loads(data);value['snapshot'].pop('Audio');retain(self._testMethodName,value)
        with self.assertRaisesRegex(ValueError,'Complete bound V2 root'):C.verify_codec_bytes(C.canonical(value).encode(),cp)
        value=json.loads(data);value['snapshot']['RunGuid']=cp['run']
        with self.assertRaisesRegex(ValueError,'four actual uint32'):C.verify_codec_bytes(C.canonical(value).encode(),cp)

    def test_source_only_completed_Apex_and_stale_callback_rejected(self):
        path=FIX/self._testMethodName;r,data=source_fixture(path)
        self.assertEqual(C.verify_source_flow(r,data)['completed_apex_callback'],7)
        r['checkpoint']['observation_index']=6;retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'stop after its own completed Apex'):C.verify_source_flow(r,data)

    def test_source_checkpoint_boundary_or_whole_clock_mismatch_rejected(self):
        path=FIX/self._testMethodName;r,data=source_fixture(path);r['checkpoint']['same_completed_game_thread_boundary']=False;retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'same completed game-thread'):C.verify_source_flow(r,data)
        r['checkpoint']['same_completed_game_thread_boundary']=True;r['checkpoint']['sim']=2.4
        with self.assertRaisesRegex(ValueError,'checkpoint callback|Checkpoint callback'):C.verify_source_flow(r,data)

    def test_pristine_noPawn_noRun_or_old_owner_rejected(self):
        f,o=pristine();self.assertTrue(C.verify_pristine(f,o)['real_pristine_completed_callback'])
        f['equipment_bound']=True
        with self.assertRaises(ValueError):C.verify_pristine(f,o)
        f['equipment_bound']=False;o['owner']='7';retain(self._testMethodName,dict(facts=f,observation=o))
        with self.assertRaises(ValueError):C.verify_pristine(f,o)

    def test_real_queued_Enter_Await_then_Open_and_full_pause_codec(self):
        r,s,data=target_fixture(FIX/self._testMethodName);retain(self._testMethodName,r)
        result=C.verify_target_flow(r,s,data,FIX/self._testMethodName)
        self.assertEqual(result['paused_callback_count'],4);self.assertEqual(result['neutral_callback'],3);self.assertEqual(result['first_open_callback'],5)

    def test_same_HV_but_changed_unrelated_whole_pause_Codec_rejected(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path)
        value=json.loads(data);value['snapshot']['LastMessage']='HOST_CHANGED_OUTSIDE_HV';changed=C.canonical(value).encode();file=path/'changed-whole-pause-codec.json';file.write_bytes(changed);r['pause_checks'][1]['codec']=C.pin(file);retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'Complete Codec bytes differ'):C.verify_target_flow(r,s,data,path)

    def test_missing_one_Await_codec_cannot_be_selected_away(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);r['pause_checks'].pop();retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'Every completed Await'):C.verify_target_flow(r,s,data,path)

    def test_wrong_install_epoch_rejected(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);r['prepare_install']['after_epoch']='0';retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'epoch0to1'):C.verify_target_flow(r,s,data,path)

    def test_stale_completed_draw_id_or_wrong_target_owner_rejected(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);r['observations'][3]['old_draw']['draw_id']=r['observations'][2]['old_draw']['draw_id'];retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'draw ID must be fresh'):C.verify_target_flow(r,s,data,path)
        r['observations'][3]['old_draw']['draw_id']='3';r['observations'][5]['owner']='8'
        with self.assertRaisesRegex(ValueError,'logical player identity'):C.verify_target_flow(r,s,data,path)

    def test_unconsumed_or_visible_staged_actor_rejected(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);r['prepare_install']['prepared_consumed']=False;retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'prepared_consumed'):C.verify_target_flow(r,s,data,path)

    def test_premature_Enter_and_stale_neutral_rejected(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);r['prepare_install']['installed_monotonic_s']=100.10;retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'.20s'):C.verify_target_flow(r,s,data,path)
        r['prepare_install']['installed_monotonic_s']=100.02;r['neutral_checks'][2]['enter_just_pressed']=True
        with self.assertRaisesRegex(ValueError,'released Enter'):C.verify_target_flow(r,s,data,path)

    def test_new_Space_or_reset_Rise_cannot_count_as_continuation(self):
        path=FIX/self._testMethodName;r,s,data=target_fixture(path);q=copy.deepcopy(r['normal_inputs'][-1]);q['key']='SpaceBar';r['normal_inputs'].append(q);retain(self._testMethodName,r)
        with self.assertRaisesRegex(ValueError,'only gameplay down'):C.verify_target_flow(r,s,data,path)
        r['normal_inputs'].pop();r['observations'][5]['vertical_velocity']=630.;r['observations'][5]['physical_visual_key']=0
        with self.assertRaisesRegex(ValueError,'reset into Rise'):C.verify_target_flow(r,s,data,path)

    def test_full_native_bundle_marker_and_wrong_BuildId_head_or_crc(self):
        data,cp=fixture();profile='01234567-89ab-4cde-8123-0123456789ab';build='HOST_EXACT_CM_AND_DLL_BUILD'
        payload=dict(adapter='bound-run-only-v2',buildId=build,generationId='1',parentGeneration='0',profileId=profile.replace('-',''),run=json.loads(data),runGuid=cp['run'].lower(),runSimulationTime=bits(cp['sim']),scope='BoundDevelopmentRunV2',versions=dict(contentRules='bound-development-guard-v2',coordinates='world-cm-v1',schema='bound-run-generation-v2'))
        bundle=json.dumps(dict(container_version=1,ProfileID=profile,GenerationID='1',parent_generation='0',schema_version='bound-run-generation-v2',content_rules_version='bound-development-guard-v2',coordinate_version='world-cm-v1',build_id=build,run_sim_time_or_null=cp['sim'],restored_from_generation='0',payload=payload),ensure_ascii=False,separators=(',',':')).encode()
        marker=dict(container_version=1,ProfileID=profile,GenerationID='1',parent_generation='0',bundle_byte_length=str(len(bundle)),bundle_sha256=hashlib.sha256(bundle).hexdigest(),bundle_crc32=str(zlib.crc32(bundle)&0xffffffff))
        marker['marker_integrity_digest']=hashlib.sha256(json.dumps(marker,separators=(',',':')).encode()).hexdigest();wire=json.dumps(marker,separators=(',',':')).encode()
        retain(self._testMethodName,dict(bundle=bundle.decode(),marker=wire.decode(),checkpoint=cp))
        self.assertTrue(C.verify_store_bytes(bundle,wire,data,cp,profile,build)['complete_payload_codec_byte_equal'])
        with self.assertRaisesRegex(ValueError,'bundle/header/BuildId'):C.verify_store_bytes(bundle,wire,data,cp,profile,'HOST_OTHER_BUILD')
        with self.assertRaisesRegex(ValueError,'bundle/header/BuildId'):C.verify_store_bytes(bundle,wire,data,cp,'01234567-89ab-4cde-8123-0123456789ac',build)
        with self.assertRaisesRegex(ValueError,'bundle/header/BuildId'):C.verify_store_bytes(bundle.replace(b'"GenerationID":"1"',b'"GenerationID":"2"'),wire,data,cp,profile,build)
        with self.assertRaisesRegex(ValueError,'marker digest/head'):C.verify_store_bytes(bundle,wire.replace(marker['bundle_crc32'].encode(),b'0'),data,cp,profile,build)

class CaptureAndGeometryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('v144_checker',P/'verify-air-disk-restore-native-v001.py');cls.M=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.M)
        cls.dep=cls.M.dependencies()

    def audio_fixture(self):
        directory=FIX/self._testMethodName;directory.mkdir();audio_dir=directory/'audio-v001';audio_dir.mkdir()
        rate=48000;channels=2;frames=24000;payload=bytes(frames*channels*2)
        header=b'RIFF'+struct.pack('<I',36+len(payload))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,channels,rate,rate*channels*2,channels*2,16)+b'data'+struct.pack('<I',len(payload))
        for name in ('runtime-mix-engine-export.wav','runtime-mix.wav'):(audio_dir/name).write_bytes(header+payload)
        yes='start_requested stop_requested export_callback_received new_directory_exclusively_created engine_wav_present canonical_wav_ready PCM_payload_unchanged controls_configured controls_restore_requested app_volume_restored submix_auto_disable_request_queued submix_restore_request_queued stop_audio_command_fence_completed'.split()
        no='abort_drain_requested submix_effective_auto_disable_read_back non_silence_checked_by_helper auditioned final_mix_accepted'.split()
        cap={**{k:True for k in yes},**{k:False for k in no},'schema':'native-main-submix-capture-v001','phase':'Complete','failure':'','formal_complete_units':0,'native_audio_device_id':1,'start_monotonic_s':100.,'stop_monotonic_s':100.5,'requested_wall_duration_s':.5,'audio_clock_start_s':1.,'audio_clock_stop_s':1.5,'primary_volume_start':1.,'primary_volume_stop':1.,'disable_app_volume_start':1,'disable_app_volume_stop':1,'previous_disable_app_volume_set_by':0,'disable_app_volume_set_by_start':0,'disable_app_volume_set_by_stop':0,'disable_app_volume_set_by_restored':0,'output_directory':audio_dir.as_posix(),'engine_original_wav':(audio_dir/'runtime-mix-engine-export.wav').as_posix(),'canonical_wav':(audio_dir/'runtime-mix.wav').as_posix(),'channels':channels,'sample_rate_hz':rate,'pcm_frames':frames,'header_block_align_repaired':False}
        r=dict(schema='HOST_AUDIO_FIXTURE_NOT_NATIVE',authority='HOST_DATA_ONLY_NOT_NATIVE_OR_ROOT_APPROVAL',main_submix_capture=cap,capture_timing=dict(use_fixed_time_step=False,capture_start_monotonic_s=100.,capture_stop_monotonic_s=100.5,frame_wall_offsets_s=[.01,.02,.03]),observations=[dict(wall_offset_s=x) for x in (.01,.02,.03)])
        report=directory/'HOST-runtime-report.json';report.write_text(json.dumps(r),encoding='utf-8')
        policy=dict(target_audio_policy_addendum_pin=self.dep[0]['pins']['audio_policy_addendum'],target_audio_audit_evidence_pin=self.dep[0]['pins']['audio_gap_source_audit'])
        return report,r,policy

    def test_complete_target_zero_PCM_allowed_but_source_same_zero_rejected(self):
        report,r,p=self.audio_fixture();result=self.M.audio_audit(report,'target',self.dep,p)
        self.assertTrue(result['actual_complete_zero_PCM']);self.assertTrue(result['decoded_PCM']['full_decode_passed']);self.assertFalse(result['signal_or_each_cue_or_audition_acceptance'])
        with self.assertRaisesRegex(ValueError,'silent or below'):self.M.audio_audit(report,'source',self.dep,p)

    def test_target_missing_WAV_rejected(self):
        report,r,p=self.audio_fixture();r['main_submix_capture']['canonical_wav']=str(report.parent/'audio-v001/MISSING.wav');report.write_text(json.dumps(r),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'WAV binding'):self.M.audio_audit(report,'target',self.dep,p)

    def test_target_zero_length_and_changed_PCM_rejected(self):
        report,r,p=self.audio_fixture();path=Path(r['main_submix_capture']['canonical_wav']);path.write_bytes(b'');
        with self.assertRaisesRegex(ValueError,'fixed44'):self.M.audio_audit(report,'target',self.dep,p)

    def test_target_modified_PCM_and_truncated_full_recording_rejected(self):
        report,r,p=self.audio_fixture();path=Path(r['main_submix_capture']['canonical_wav']);data=path.read_bytes();path.write_bytes(data[:-2]+b'\x01\x00')
        with self.assertRaisesRegex(ValueError,'PCM/header replacement|Only BlockAlign'):self.M.audio_audit(report,'target',self.dep,p)

    def test_target_complete_but_wrong_WAV_wall_duration_rejected(self):
        report,r,p=self.audio_fixture();cap=r['main_submix_capture'];cap['stop_monotonic_s']=100.9;cap['requested_wall_duration_s']=.9;r['capture_timing']['capture_stop_monotonic_s']=100.9;report.write_text(json.dumps(r),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'150ms'):self.M.audio_audit(report,'target',self.dep,p)

    def test_target_wrong_capture_device_or_volume_rejected(self):
        report,r,p=self.audio_fixture();r['main_submix_capture']['native_audio_device_id']=-1;report.write_text(json.dumps(r),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'device ID'):self.M.audio_audit(report,'target',self.dep,p)
        r['main_submix_capture']['native_audio_device_id']=1;r['main_submix_capture']['primary_volume_start']=0.;report.write_text(json.dumps(r),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'volume'):self.M.audio_audit(report,'target',self.dep,p)

    def test_target_wrong_timing_rejected_even_for_complete_silence(self):
        report,r,p=self.audio_fixture();r['capture_timing']['capture_start_monotonic_s']=100.001;report.write_text(json.dumps(r),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'exact real helper origin'):self.M.audio_audit(report,'target',self.dep,p)

    def test_historical_pure_Air_geometry_missing_slot_or_resident_rejected(self):
        base=P.parent/'landing-priority-observer-candidate-v001/tooling-review-fix-v002/geometry-fixture-origins-v002.json';origins=C.read(base)
        origin=next(x for x in origins['members'] if x['kind']=='Air' and x['side']=='right');r=C.read(C.resolve_pin(origin))
        o=next(copy.deepcopy(x) for x in r['observations'] if x['new_air_draw']['drawn'] and x['new_air_draw']['slot_count']==9 and x['physical_visual_key']==2 and x['new_air_draw']['armor_kind']==1)
        am=C.read(P.parent/'native-ready-candidate-v001/import-Air48-v001.json');ap=C.read(P.parent/'native-ready-candidate-v001/Air-runtime-profile-data-v001.json')
        L=self.dep[2];paths={a['component']:a['object_path'] for a in am['assets'] if a['frame']==2};paths['IndependentSword']=L.SWORD;resident={a['object_path'] for a in am['assets']}|{L.SWORD}
        self.assertEqual(len(L.quad_geometry(o,ap['Frames'][2],paths,True,resident)),9)
        retain(self._testMethodName,dict(historical_geometry_only_not_v144_native=True,origin_pin=origin,observation=o))
        o['new_air_draw']['slot_count']=8
        with self.assertRaisesRegex(ValueError,'complete/current pose'):L.quad_geometry(o,ap['Frames'][2],paths,True,resident)
        o['new_air_draw']['slot_count']=9;o['new_air_draw']['resident_textures'].pop()
        with self.assertRaisesRegex(ValueError,'resident preflight'):L.quad_geometry(o,ap['Frames'][2],paths,True,resident)

    def test_missing_original_PNG_receipts_rejected(self):
        directory=FIX/self._testMethodName;directory.mkdir()
        with self.assertRaises(FileNotFoundError):self.dep[4].verify_png_fifo(directory,{})

    def test_Root_false_template_cannot_be_preflight_or_native(self):
        with self.assertRaisesRegex(ValueError,'templates never pass'):self.M.preflight(P/'Root-prereg-TEMPLATE-v001.json')

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
    report=dict(schema='v144-data-only-contract-host-tests-v001',created_utc=datetime.now(timezone.utc).isoformat(),run=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),fixture_directory=FIX.as_posix(),authority='HOST_DATA_ONLY_NOT_NATIVE_OR_APPROVAL',core_pin=C.pin(P/'air_disk_contract_v001.py'),checker_pin=C.pin(P/'verify-air-disk-restore-native-v001.py'),tests_pin=C.pin(Path(__file__)),source_binding_pin=C.pin(P/'source-binding-v001.json'),synthetic_zero_PCM_only_test_fixture_not_audio_acceptance=True,historical_geometry_not_new_native=True,UE_started=False,actual_disk_store_created=False,actual_F_media_written=False,RootApproved=False,FinalAccepted=False)
    with (P/f'host-tests-{RUN}.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
