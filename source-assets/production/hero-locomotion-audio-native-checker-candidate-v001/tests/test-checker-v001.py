"""Small hostile host fixtures only; no generated recording or native PASS."""
from pathlib import Path
import copy
import importlib.util
import json
import unittest

HERE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('checker_under_test', HERE/'verify-hero-locomotion-audio-native-v001.py')
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)

def fixture():
    times = [0, .2, .4, 1., 1.02, 1.5, 1.9, 2., 2.005, 2.4]
    scope = dict(run='ABC', owner='1', room='1', epoch='0', restart='1')
    bindings = {cue:dict(object_path='/Game/'+cue) for cue in V.CUES}
    r = dict(restart_serial='1', observations=[], normal_inputs=[dict(key='D', down=True, sim=0),
             dict(key='D', down=False, sim=.5), dict(key='D', down=True, sim=.6), dict(key='D', down=False, sim=.7),
             dict(key='SpaceBar', down=True, sim=1.)],
             ready_callback_index=3, landing_callback_index=7, first_action_callback_index=8,
             capture_timing=dict(capture_start_monotonic_s=100., capture_stop_monotonic_s=103.))
    requests = []
    emissions = {1:(0,.19), 2:(1,.39), 4:(2,1.01), 7:(4,1.99), 8:(5,2.003)}
    for i, sim in enumerate(times):
        wall = sim+.01; lower = 100.+(times[i-1]+.01 if i else 0.)
        window = dict(lower_monotonic_s=lower, upper_monotonic_s=100.+wall,
                      lower_offset_s=lower-100., upper_offset_s=wall,
                      semantics='first_seen_between_completed_callbacks_not_emission_timestamp')
        o = dict(sim=sim, phase=i, wall_offset_s=wall, run='ABC', owner='1', current_room='1', epoch='0',
                 jump_height=10 if i in (4,5,6) else 0,
                 action=dict(start=2.003,id='1',start_event_id='3'))
        new = []
        if i in emissions:
            enum, at = emissions[i]; step, land, dodge = enum<2, enum==4, enum==5
            q = dict(sequence=str(len(requests)+1),request_scope=dict(owner='1',room='1',epoch='0',restart='1',run=None,run_available=False),
                     first_seen_current_scope=dict(scope),cue=V.CUES[enum],cue_enum=enum,asset_path=bindings[V.CUES[enum]]['object_path'],
                     volume=.25 if step else .32,pitch=1,at_time_s=at,requested_at_time_s=sim,
                     ground_position_at_dispatch=[i*20,0],first_seen_callback_index=i,first_seen_phase=i,
                     first_seen_sim_time_s=sim,first_seen_wall_window=window,request_wall_time_available=False,request_monotonic_s=None,
                     source_cause=V.CAUSES[enum],source_cause_basis='mapped_existing_cue_enum_not_new_gameplay_event',
                     source_interval_available=False,source_from_time_s=None,source_to_time_s=None,source_distance_available=False,source_distance_cm=None,
                     step_ordinal=str(enum+1) if step else '0',fall_speed_cm_s=600 if land else 0,fall_distance_cm=120 if land else 0,
                     dodge_event_id='3' if dodge else '0',dodge_action_id='1' if dodge else '0',event_id_available=dodge,event_id='3' if dodge else None,
                     landing_fields_applicable=land,step_fields_applicable=step,dodge_fields_applicable=dodge,request_scope_matches_current=True,
                     sequence_gap_before='0',request_only=True,audible_or_mix_attribution_proven=False)
            new.append(q);requests.append(q)
        ground = dict(available=True,semantics='actual_completed_callback_motion_not_event_source_interval',run='ABC',owner='1',room='1',
                      from_time_s=max(0,sim-.005),to_time_s=sim,from_xy=[0,0],to_xy=[.5,0],accepted_distance_cm=.5,
                      walk_distance_cm=.5,grounded=True,ordinary_eligible=True,had_move_intent=True)
        if not sim: ground = dict(available=False,semantics=ground['semantics'])
        o['hero_locomotion_audio'] = dict(schema='hero-locomotion-request-observation-v001',callback_index=i,current_scope=dict(scope),
                 callback_wall_window=window,ground_witness=ground,ring_snapshot_count=len(requests),ring_first_sequence='1' if requests else '0',
                 ring_last_sequence=str(len(requests)),scope_changed=False,new_request_count=len(new),captured_request_prefix_count=len(requests),
                 new_requests=new,ring_limit=256,request_only=True,audible_or_mix_attribution_proven=False)
        r['observations'].append(o)
    r['hero_locomotion_audio'] = dict(schema='hero-locomotion-request-observation-v001',captured_requests=requests,captured_request_count=len(requests),
         callback_count=len(times),scope_change_count=0,sequence_gap_count=0,sequence_gap_missing_sequence_total='0',ring_limit=256,
         ring_limit_seen=False,first_snapshot_truncation_possible=False,request_only=True,audible_or_mix_attribution_proven=False)
    return r, bindings

class Contracts(unittest.TestCase):
    def reject(self, mutation, message):
        r,b = fixture(); mutation(r)
        with self.assertRaisesRegex(ValueError,message): V.verify_requests(r,b)
    def test_small_host_fixture_is_not_native_evidence(self):
        r,b = fixture(); result=V.verify_requests(r,b)
        self.assertEqual(result['naturally_covered_cue_types'],5)
        self.assertEqual(result['light_landing'],'UNTRIGGERED')
        self.assertFalse(result['audible_or_mix_attribution_proven'])
    def test_duplicate_sequence(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][1].update(sequence='1'),'sequence duplicate/gap')
    def test_wrong_owner(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][0]['request_scope'].update(owner='2'),'Request scope differs')
    def test_invented_event_distance(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][0].update(source_distance_available=True,source_distance_cm=40),'Unavailable event')
    def test_fake_first_seen_callback_window(self):
        self.reject(lambda r:r['observations'][2]['hero_locomotion_audio']['callback_wall_window'].update(lower_monotonic_s=100.),'adjacent completed callbacks')
    def test_stale_dispatch_before_prior_callback(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][1].update(requested_at_time_s=.2,at_time_s=.19),'simulation interval')
    def test_step_after_release_air_or_dodge_is_backfill(self):
        def alter(r):
            q=r['hero_locomotion_audio']['captured_requests'][1];q.update(at_time_s=.39)
            r['normal_inputs'][1]['sim']=.3
        self.reject(alter,'Footstep outside real movement')
    def test_wrong_foot_parity(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][1].update(step_ordinal='3'),'wrong parity')
    def test_invented_takeoff_eventid(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][2].update(event_id_available=True,event_id='5'),'Only actual Dodge')
    def test_false_firm_landing(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][3].update(fall_speed_cm_s=539,fall_distance_cm=109),'Firm landing')
    def test_wrong_dodge_event(self):
        self.reject(lambda r:r['hero_locomotion_audio']['captured_requests'][4].update(dodge_event_id='4',event_id='4'),'actual accepted Started')
    def test_unseen_ring_loss_cannot_pass(self):
        self.reject(lambda r:r['hero_locomotion_audio'].update(first_snapshot_truncation_possible=True),'truncation/gaps')
    def test_overlay_rejects_unrelated_production_byte_change(self):
        p=V.ROOT/'source-assets/production/backups/v145-HeroLocomotionAudio303-1425-203GREEN-v001/compiled-source-manifest.json'
        old=V.read(p); now=copy.deepcopy(old); after=next(x for x in now['files'] if x['path']==V.OBSERVER);after['sha256']='0'*64
        ad=dict(schema='Root-hero-locomotion-audio-observer-admission-v001',RootApproved=True,is_template=False,actual_applied=True,
                actual_source_files=303,actual_production_files=1425,new_source_files=0,verification_passes=2,
                unrelated_source_tests_content_byte_mismatches=0,before_files=[next(x for x in old['files'] if x['path']==V.OBSERVER)],after_files=[after])
        members=[dict(path='projected/'+Path(V.OBSERVER).name,bytes=after['bytes'],sha256=after['sha256'])]
        self.assertEqual(V.verify_overlay(old,now,ad,members)['actual_source_files'],303)
        next(x for x in now['files'] if x['path'].startswith('UnrealGame/Content/Production/'))['sha256']='1'*64
        with self.assertRaisesRegex(ValueError,'Unrelated source/test/content changed'): V.verify_overlay(old,now,ad,members)

if __name__=='__main__': unittest.main(verbosity=2)
