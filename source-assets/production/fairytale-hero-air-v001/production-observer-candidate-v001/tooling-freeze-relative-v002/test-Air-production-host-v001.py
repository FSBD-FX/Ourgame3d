"""Synthetic host positive/poison cases; no native/GPU/gameplay result claimed."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import hashlib
import importlib.util
import json
import math
import sys
import unittest
from unittest.mock import patch
import zlib
import numpy as np
from PIL import Image
import air_production_contract_v001 as C

HERE = Path(__file__).resolve().parent
RUN = HERE / 'validation-runs' / ('h' + datetime.now(timezone.utc).strftime('%H%M%S%f'))
spec = importlib.util.spec_from_file_location('air_native_checker_tested_source', HERE / 'verify-Air-production-native-v001.py')
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
PROFILE = C.read(C.AIR / 'native-ready-candidate-v001/Air-runtime-profile-data-v001.json')
MANIFEST = C.read(C.AIR / 'native-ready-candidate-v001/import-Air48-v001.json')


def drawn_observation(frame, ordinal, side=1, sim=1., draw_id=1):
    root, grip, axis = [PROFILE['Frames'][frame][k] for k in ('Root', 'Grip', 'AxisArtist')]
    samples = [(0., 630., C.f32(.12)), (10., 200., C.f32(.12)), (20., 0., C.f32(.12)),
               (15., -300., C.f32(.12)), (0., 0., 0.), (0., 0., C.f32(.08))]
    h, v, age = samples[frame]; light = ordinal >= 2; scale = 72 / 416
    world, camera = [-200., 20.], [0., 0.]
    ground = [C.f32(640 + world[0] * C.f32(.65)), C.f32(490 - world[1] * C.f32(.38))]
    lift = [ground[0], ground[1] - h * .7]
    top = [lift[0] - (root[0] if side > 0 else 512 - root[0]) * scale, lift[1] - root[1] * scale]
    at = [lift[0] + side * (grip[0] - root[0]) * scale, lift[1] + (grip[1] - root[1]) * scale]
    angle = math.degrees(math.atan2(axis[1], axis[0])) * side; width = 512 * scale * .5
    pivot = [99 / 512 if side > 0 else 1 - 99 / 512, .5]; sword_top = [at[k] - pivot[k] * width for k in range(2)]
    paths = {a['component']: a['object_path'] for a in MANIFEST['assets'] if a['frame'] == frame}
    paths['IndependentSword'] = PROFILE['independent_sword']['object_path']
    slots = []
    for i, name in enumerate(PROFILE['Frames'][frame]['SlotOrder']):
        if not light and name in ('Chest', 'ShoulderFar', 'ShoulderNear'): continue
        sword = name == 'IndependentSword'
        slots.append(dict(slot=i, component=C.COMPONENTS.index(name), texture=paths[name], drawn=True,
                          known_empty=False, texture_ready=True, top=[C.f32(x) for x in (sword_top if sword else top)],
                          size=[C.f32(width if sword else 512 * scale)] * 2, uv=[0 if side > 0 else 1, 0],
                          uv_size=[side, 1], rotation=C.f32(angle) if sword else 0, rotation_pivot=pivot if sword else [0, 0],
                          draw_scale=1, scale_position=False, trace_tint=[1, 1, 1, 1]))
    residents = [dict(texture=a['object_path'], **{'class':'Texture2D'}, width=512, height=512,
                      resource_ready=True, pending_initialization=False) for a in MANIFEST['assets']]
    residents.append(dict(texture=paths['IndependentSword'], **{'class':'Texture2D'}, width=512, height=512, resource_ready=True, pending_initialization=False))
    stack = [s['texture'] for s in slots]
    d = dict(draw_id=str(draw_id), opt_in=True, drawn=True, atomic_preflight_ready=True, missing_reason='', supported=True,
             sample_valid=True, frame=frame, pose=frame + 1, facing=side, sim=sim, sample_native_time=sim, profile=PROFILE['profile_id'],
             sample_run='a' * 32, binding_run='a' * 32, sample_owner='1', binding_owner='1', player_entity='1', sample_room='1', sample_epoch='0',
             sample_ground=world, sample_H=h, sample_V=v, sample_landing_age=age, jump_height=h,
             weapon_instance='2', weapon_version='1', armor_instance='3' if light else '0', armor_version='2' if light else '0',
             weapon_content='WPN-SWD-001', armor_content='ARM-LGT-001' if light else '', armor_kind=1 if light else 0,
             root_source=root, grip_source=grip, axis_artist=axis, context_ground=ground, ui_scale=1, canvas_size=512 * scale,
             source_to_screen_scale=scale, weapon_scale=.5, weapon_width=width, weapon_angle=angle, texture_u=0 if side > 0 else 1,
             texture_du=side, body_top=top, grip_screen=at, sword_top=sword_top, sword_pivot_uv=pivot,
             tint=[1,1,1,1], slot_count=len(slots), nonempty_count=len(slots), slots=slots, actual_stack=stack, resident_count=49, resident_textures=residents)
    old = dict(draw_id=str(draw_id), active=True, supported=True, action_pose_supported=True, texture_ready=True,
               sword_drawn=True, armor_drawn=light, clip='sword_nonattack_air', gear_placeholder=False, actual_stack=stack,
               sim=sim,frame=frame,facing=side,root_source=root,grip_source=grip,grip_screen=at,canvas_size=512*scale,
               body_texture=paths['BodyRest'],sword_texture=paths['IndependentSword'])
    return dict(wall_offset_s=sim / 10, phase=3 if ordinal == 1 else 6 if ordinal == 2 else 9, sim=sim,
                run='a' * 32, owner='1', current_room='1', epoch='0', player_entity='1', ground=world, camera_ground=camera,
                facing=side, jump_height=h, vertical_velocity=v, landing_visual_age=age, physical_visual_key=frame,
                observed_air_transition_ordinal=ordinal, transition_ordinal_is_gameplay_jump_id=False, hp=100., dead=False,
                native_actor_root_z=0, interface_visible=False, text_calls=0, range_debug=False, range_lines=0,
                melee_time=sim, wa_time=sim, dodge_time=sim, weapon_world_time=sim, melee_active=False, wa_active=False,
                weapon_instance='2', weapon_version='1', armor_instance='3' if light else '0', armor_version='2' if light else '0',
                new_air_query_ok=True, new_air_draw=d, old_draw=old, rendered_player_stack=stack)


def flow_fixture(side=1):
    observations = []
    def add(frame, ordinal):
        o = drawn_observation(frame, ordinal, side, float(len(observations)), len(observations) + 1)
        observations.append(o)
    def ready(ordinal, phase):
        add(5, max(1, ordinal)); o = observations[-1]
        o.update(phase=phase, physical_visual_key=-1, landing_visual_age=C.f32(.12), observed_air_transition_ordinal=ordinal,
                 new_air_query_ok=False)
        o['new_air_draw']['drawn'] = False; o['old_draw'].update(clip='sword_ready_idle', armor_drawn=ordinal >= 2)
    ready(0, 0)
    for f in range(6): add(f, 1)
    ready(1, 3); ready(1, 5)
    for f in range(6): add(f, 2)
    for f in range(6): add(f, 3)
    ready(3, 9); ready(3, 9)
    inputs = []
    for i, key in enumerate(('Enter', 'A' if side < 0 else 'D', 'SpaceBar', 'E', 'SpaceBar', 'SpaceBar')):
        for down in (True, False):
            inputs.append(dict(key=key, down=down, wall_offset_s=[.01,.04,.08,.75,.88,1.48][i] + (0 if down else .001), sim=[0.,0.,0.,7.,8.,14.][i],
                               before_H=0., before_V=0., before_landing_age=C.f32(.08) if i == 5 else C.f32(.12),
                               after_H=0., after_V=630. if down and key == 'SpaceBar' else 0., after_landing_age=C.f32(.12)))
    return dict(schema=C.SCHEMA, scenario=C.SCENARIO, passed=True, flow_complete=True, failure='', profile_closure=C.CLOSURE,
                profile_id=PROFILE['profile_id'], native_ready_freeze_SHA256=C.SOURCE_FREEZE_SHA, final_accepted=False,
                visual_reviewed=False, audio_listened=False, NoArmor_is_formal20_pair=False, transition_ordinals_are_gameplay_jump_ids=False,
                player_Guard_HP_position_AI_time_writes=False,
                additional_scenarios=dict(normal_landing_J_priority='OPEN_not_run', normal_landing_Shift_priority='OPEN_not_run', real_save_restore='OPEN_not_run'),
                requested_facing=side, process_id='1234', owner='1', current_room='1', epoch='0', restart_serial='1',
                weapon_instance='2', weapon_version='1', armor_instance='3', armor_version='2', run='a' * 32,
                initial_hp=100., capture_final_hp=100., normal_inputs=inputs, normal_rejump_issued_inside_original_landing=True,
                rejump_input_landing_age=C.f32(.08), diagnostic_knight_hits=[], observations=observations,
                capture_timing=dict(frame_wall_offsets_s=[o['wall_offset_s'] for o in observations],capture_start_monotonic_s=10.,capture_stop_monotonic_s=12.3),
                starter_NoArmor_mask=63, light_first_mask=63, light_second_mask=63, normal_space_inputs=3, air_transitions=3,
                landing_transitions=3, starter_NoArmor_frames=6, light_frames=12, landing_frames=6, Ready_join_frames=2)


class HostTests(unittest.TestCase):
    def test_01_pure_value_selection_half_open_and_tiny_descending(self):
        cases=[(1,316,0,0),(1,315,0,1),(1,90,0,2),(1,-90,0,2),(1,-91,0,3),(1e-40,-300,0,3),
               (0,630,C.f32(.08),0),(0,0,0,4),(0,0,C.f32(.06),5),(0,0,C.f32(.12),-1)]
        for h,v,a,want in cases:self.assertEqual(C.selection(h,v,a),want)
        with self.assertRaises(ValueError):C.selection(float('nan'),0,0)

    def test_02_none6_and_light9_all6_raw_axis_roots_and_mirrors(self):
        for side in (-1,1):
            r=flow_fixture(side)
            for ordinal in (1,2,3):
                for frame in range(6):C.verify_draw(drawn_observation(frame,ordinal,side),frame,PROFILE,MANIFEST,r)

    def test_03_poisoned_slot_count_renumbering_missing_resident_mirror_and_clock(self):
        changes=[lambda o:o['new_air_draw']['slots'][1].update(slot=1),
                 lambda o:o['new_air_draw']['resident_textures'].pop(),
                 lambda o:o['new_air_draw'].update(texture_du=-1),
                 lambda o:o['new_air_draw'].update(sample_native_time=99),
                 lambda o:o['new_air_draw'].update(root_source=[244,512]),
                 lambda o:o['new_air_draw']['slots'][0].update(top=[0,0]),
                 lambda o:o['new_air_draw'].update(armor_version='99')]
        for change in changes:
            o=drawn_observation(2,1);change(o)
            with self.assertRaises(ValueError):C.verify_draw(o,2,PROFILE,MANIFEST,flow_fixture())

    def test_04_complete_three_real_transitions_and_Ready_positive_both_sides(self):
        for side in (-1,1):V.verify_flow(flow_fixture(side),MANIFEST,PROFILE,dict(requested_facing=side,diagnostic_clear_knight=False))

    def test_05_reject_faked_masks_repeated_DrawId_owner_clock_HP_and_UI(self):
        changes=[lambda r:r.update(light_second_mask=31),lambda r:r['observations'][2]['new_air_draw'].update(draw_id='2'),
                 lambda r:r['observations'][2].update(owner='2'),lambda r:r['observations'][2].update(melee_time=99),
                 lambda r:r['observations'][2].update(hp=99),lambda r:r['observations'][2].update(interface_visible=True),
                 lambda r:r['observations'][2].update(observed_air_transition_ordinal=2),
                 lambda r:r['observations'][-1]['old_draw'].update(draw_id=r['observations'][-2]['old_draw']['draw_id'])]
        for change in changes:
            r=flow_fixture();change(r)
            with self.assertRaises(ValueError):V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=1,diagnostic_clear_knight=False))

    def test_06_rejump_landing_boundary_and_extra_inputs_never_accepted(self):
        for age in (0,C.f32(.12)):
            r=flow_fixture();r['normal_inputs'][-2]['before_landing_age']=age;r['rejump_input_landing_age']=age
            with self.assertRaises(ValueError):V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=1,diagnostic_clear_knight=False))
        r=flow_fixture();r['normal_inputs'][0]['key']='LeftShift'
        with self.assertRaises(ValueError):V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=1,diagnostic_clear_knight=False))

    def test_07_template_wrong_scope_and_unrun_claims_rejected(self):
        p=C.read(HERE/'Root-Air6-prereg-TEMPLATE-v001.json')
        with self.assertRaises(ValueError):C.prereg_header(p)
        p.update(RootApproved=True,is_template=False,pre_registered_before_capture=True,requested_facing=True)
        with self.assertRaises(ValueError):C.prereg_header(p)
        r=flow_fixture();r['additional_scenarios']['real_save_restore']='PASS'
        with self.assertRaises(ValueError):V.verify_flow(r,MANIFEST,PROFILE,dict(requested_facing=1,diagnostic_clear_knight=False))

    def test_08_actual203_rows_required_not_summary_claims(self):
        suite=dict(succeeded=203,succeededWithWarnings=0,failed=0,notRun=0,inProcess=0,
                   tests=[dict(fullTestPath=str(i),state='Success',warnings=0,errors=0,entries=[]) for i in range(203)])
        C.strict203(suite)
        for change in (lambda s:s['tests'][1].update(fullTestPath='0'),lambda s:s['tests'][0].update(errors=1),
                       lambda s:s['tests'][0].update(state='Fail'),lambda s:s.update(notRun=1)):
            s=copy.deepcopy(suite);change(s)
            with self.assertRaises(ValueError):C.strict203(s)

    def test_09_fixed_source_pixel_gates_positive_and_threshold_poison(self):
        error=np.zeros(200);opaque=np.ones(200,dtype=bool);blade=np.zeros(200,dtype=bool);blade[:8]=True
        V.fixed_optical_gate(error,opaque,blade)
        bad=opaque.copy();bad[149:]=False
        with self.assertRaises(ValueError):V.fixed_optical_gate(error,bad,blade)
        small=blade.copy();small[7]=False
        with self.assertRaises(ValueError):V.fixed_optical_gate(error,opaque,small)
        with self.assertRaises(ValueError):V.fixed_optical_gate(np.full(200,41.),opaque,blade)
        e=error.copy();e[:8]=[0,0,0,0,66,66,66,66]
        with self.assertRaises(ValueError):V.fixed_optical_gate(e,opaque,blade)

    def test_10_uint_float_geometry_and_evidence_path_poison(self):
        for value in ('01','-1','1.0',str(2**64),1):
            with self.assertRaises(ValueError):C.uint(value)
        self.assertEqual(C.uint('0',zero=True),0)
        for value in ('../x','F:/x','a\\x','a/./x'):
            with self.assertRaises(ValueError):C.file_under(RUN,value)

    def test_11_raw_GPU_editor49_positive_and_updatedCRC_wrongRGBA_rejected(self):
        original=RUN/'gpu';(original/'texture-readback').mkdir(parents=True)
        rgba=np.zeros((512,512,4),dtype=np.uint8);rgba[:]=[11,71,192,255]
        sp=RUN/'synthetic-source.png';Image.fromarray(rgba).save(sp)
        sha=hashlib.sha256(sp.read_bytes()).hexdigest();rgba_sha=hashlib.sha256(rgba.tobytes()).hexdigest()
        bgra=rgba[:,:,[2,1,0,3]].tobytes();rows=[];assets=[]
        for i in range(49):
            texture='SYNTHETIC-'+str(i);frame=i//8 if i<48 else -1;component=i%8 if i<48 else 8
            if i<48:assets.append(dict(object_path=texture,source=str(sp),frame=frame,component=C.COMPONENTS[component],source_sha256=sha,source_RGBA_sha256=rgba_sha))
            row=dict(texture=texture,**{'class':'Texture2D'},width=512,height=512,frame=frame,component=component,source_SHA_metadata=sha,
                     source_RGBA_SHA_metadata=rgba_sha if i<48 else '',resource_ready=True,pending_initialization=False,sRGB=True,RHI_format=2,
                     editor_source_format='TSF_BGRA8',read_flags='RCM_UNorm/Mip0/LinearToGamma=false; BGRA8/RGBA8 UNORM(_SRGB) byte copy',
                     read_start_monotonic_s=1.,read_stop_monotonic_s=2.)
            for field,crcfield,suffix in (('GPU_file','GPU_BGRA8_CRC32','gpu'),('editor_source_file','editor_source_BGRA8_CRC32','editor')):
                relative=f'texture-readback/{i:03d}-{suffix}.bin';(original/relative).write_bytes(bgra)
                row[field]=relative;row[crcfield]=zlib.crc32(bgra)&0xffffffff
            rows.append(row)
        profile=dict(independent_sword=dict(object_path='SYNTHETIC-48',source=dict(path=str(sp),sha256=sha)))
        r=dict(startup_actual_GPU_source_textures49=rows,startup_readback_complete=True,startup_readback_stop_monotonic_s=3.,
               capture_timing=dict(capture_start_monotonic_s=4.),normal_inputs=[dict(wall_offset_s=.1)])
        C.verify_gpu(original,r,dict(assets=assets),profile)
        wrong=bytearray(bgra);wrong[0]^=1;(original/'texture-readback/bad.bin').write_bytes(wrong)
        bad=copy.deepcopy(r);bad['startup_actual_GPU_source_textures49'][0].update(GPU_file='texture-readback/bad.bin',GPU_BGRA8_CRC32=zlib.crc32(wrong)&0xffffffff)
        with self.assertRaisesRegex(ValueError,'bytes differ'):C.verify_gpu(original,bad,dict(assets=assets),profile)
        bad=copy.deepcopy(r);bad['startup_readback_stop_monotonic_s']=5.
        with self.assertRaises(ValueError):C.verify_gpu(original,bad,dict(assets=assets),profile)

    def test_12_native_original_PNG_CRC_FIFO_and_Stop_before_flush(self):
        rgba=np.zeros((720,1280,4),dtype=np.uint8);rgba[:]=[8,20,120,255]
        crc=zlib.crc32(rgba[:,:,[2,1,0,3]].tobytes())&0xffffffff
        for kind in ('ok','crc','FIFO','flush'):
            original=RUN/('png-'+kind);original.mkdir()
            names=['prewarm-viewport.png','MovieFrame00000.png','MovieFrame00001.png'];rows=[]
            for i,name in enumerate(names):
                Image.fromarray(rgba).save(original/name)
                row=dict(file=name,width=1280,height=720,saved=True,native_BGRA8_crc32=crc,save_wall_s=.001)
                if i:
                    t=10.01+(i-1)*.02
                    row.update(writer_sequence=i,async_writer=True,copy_crc_matches=True,filename_reserved=True,
                               filename_reservation_mode='Windows_CreateFileW_CREATE_NEW',copied_BGRA8_crc32=crc,
                               capture_callback_monotonic_s=t,reservation_completed_monotonic_s=t+.001,enqueued_monotonic_s=t+.002,
                               save_started_monotonic_s=t+.003,save_completed_monotonic_s=t+.004,save_wall_s=.001)
                else:row['async_writer']=False
                rows.append(row)
            metadata=dict(mode='native_viewport_BGRA8_lossless_PNG_zlib0',pixel_mutations=False,simulation_pacing_changed=False,audio_changed=False,
                          async_movie_writer_requested=True,async_movie_writer_active=True,prewarm_synchronous=True,
                          movie_filename_reservation='Windows_CreateFileW_CREATE_NEW_exact_engine_request_before_enqueue')
            summary=dict(requested=True,active=True,closed=True,flushed=True,success=True,
                         movie_reserved=2,movie_enqueued=2,movie_saved=2,movie_completed=2,receipts_saved=2,
                         movie_reservation_failed=0,movie_failed=0,rejected=0,pending=0,flush_completed_monotonic_s=10.06,
                         last_save_completed_monotonic_s=10.034,first_capture_callback_monotonic_s=10.01,last_capture_callback_monotonic_s=10.03)
            r=dict(observations=[{},{}],native_async_capture_writes_flushed=True,
                   capture_timing=dict(capture_start_monotonic_s=10.,capture_stop_monotonic_s=10.045,frame_wall_offsets_s=[.02,.04]))
            if kind=='crc':rows[1]['native_BGRA8_crc32']^=1
            if kind=='FIFO':rows[2]['writer_sequence']=1
            if kind=='flush':summary['flush_completed_monotonic_s']=10.04
            for name,value in (('native-lossless-capture.json',metadata),('native-async-write-summary.json',summary)):
                with (original/name).open('x',encoding='utf-8') as f:json.dump(value,f)
            with (original/'native-frame-pixels.jsonl').open('x',encoding='utf-8') as f:
                for row in rows:f.write(json.dumps(row)+'\n')
            if kind=='ok':self.assertEqual(len(V.verify_png_fifo(original,r)),2)
            else:
                with self.assertRaises(ValueError):V.verify_png_fifo(original,r)

    def test_13_paircheck_fresh_PID_and_same_compiled_source_frozen_contracts(self):
        def result(side,pid):
            return dict(requested_facing=side,process_id=pid,root_prereg_pin=dict(path=str(side)),compiled_manifest_pin={'sha256':'same'},
                        source_probe_freeze_pin={'sha256':'source'},checker_freeze_pin={'sha256':'checker'})
        left,right=result(-1,111),result(1,222)
        with patch.object(V,'verify_native',side_effect=[left,right]):self.assertTrue(V.paircheck(RUN/'left','left',RUN/'right','right')['passed'])
        for bad in (dict(right,process_id=111),dict(right,compiled_manifest_pin={'sha256':'different'}),dict(right,requested_facing=-1)):
            with patch.object(V,'verify_native',side_effect=[left,bad]):
                with self.assertRaises(ValueError):V.paircheck(RUN/'left','left',RUN/'right','right')


if __name__=='__main__':
    RUN.mkdir(parents=True,exist_ok=False)
    sources=[HERE/'air_production_contract_v001.py',HERE/'verify-Air-production-native-v001.py',Path(__file__)]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    with (RUN/'host-tests.log').open('x',encoding='utf-8') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HostTests))
    unchanged=before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    report=dict(schema='Air-production-host-checker-synthetic-tests-v001',passed=result.wasSuccessful() and unchanged,
                tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),sources_unchanged=unchanged,source_sha256=before,
                synthetic_fixtures_only=True,UE_calls=0,actual_Source_Content_writes=0,native_or_GPU_proved=False,FinalAccepted=False)
    with (RUN/'host-tests-result.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(result=str(RUN/'host-tests-result.json'),**report)))
    raise SystemExit(0 if report['passed'] else 1)
