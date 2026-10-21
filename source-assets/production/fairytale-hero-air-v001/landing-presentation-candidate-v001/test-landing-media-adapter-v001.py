"""Small data-only adapter checks. Never invokes an official checker, encodes media, or claims native success."""
from pathlib import Path
from datetime import datetime
import copy
import importlib.util
import json
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('landing_media_adapter',HERE/'prepare-landing-presentation-v001.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
RUN=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
FIX=HERE/'_host-fixtures'/RUN


def fixture(action='J'):
    kinds=['Ready']+['Air']*5+[action]*(6 if action=='J' else 4)+['Ready','Ready']
    seen={};obs=[];witnesses=[];movie=[]
    for i,kind in enumerate(kinds):
        frame=seen.get(kind,0);seen[kind]=frame+1
        if kind=='Ready':frame=0 if i==0 else 1
        count=9 if kind in ('Air','Shift') else 8 if kind=='J' else 7
        stack=[f'HOST_ONLY_PART_{j}' for j in range(count)]
        old=dict(actual_stack=stack,body_texture='DELIBERATELY_STALE_METADATA_NOT_A_SUBMITTED_PART',
                 clip={'Ready':'sword_ready_idle','Air':'sword_nonattack_air','J':'sword_primary_1','Shift':'sword_dodge'}[kind],frame=frame)
        air=dict(drawn=kind=='Air',slot_count=9 if kind=='Air' else 0,actual_stack=stack if kind=='Air' else [],context_ground=[640,490])
        dodge=dict(drawn=kind=='Shift',slot_count=9 if kind=='Shift' else 0,resident_count=33 if kind=='Shift' else 0,
                   actual_stack=stack if kind=='Shift' else [],frame=frame,context_ground=[640,490])
        obs.append(dict(completed_callback=True,wall_offset_s=.1+i*.016,sim=i*.016,physical_visual_key=frame if kind=='Air' else -1,
                        old_draw=old,new_air_draw=air,dodge_draw=dodge,rendered_player_stack=stack,
                        action=dict(active=kind in ('J','Shift')),ground=[0,0],camera_ground=[0,0]))
        name=f'MovieFrame{i:05d}.png';movie.append(dict(file=name))
        if kind!='Ready' or i in (0,len(kinds)-1):witnesses.append(dict(observation=i,kind=kind,frame=frame,file=name))
    report=dict(schema=M.RUNTIME_SCHEMA,requested_action=action,requested_facing=-1,observations=obs,
                ready_callback_index=0,landing_callback_index=5,first_action_callback_index=6,
                capture_timing=dict(frame_wall_offsets_s=[o['wall_offset_s'] for o in obs],
                                    capture_start_monotonic_s=10.,capture_stop_monotonic_s=10.+obs[-1]['wall_offset_s']+.05))
    independent=dict(source_pixels=dict(source_pixel_witnesses=witnesses))
    return report,independent,movie


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):FIX.mkdir(parents=True,exist_ok=False)

    def save(self,r,v,m):
        path=FIX/self._testMethodName;path.mkdir()
        for name,value in [('report.json',r),('witness-data.json',v),('movie-data.json',m)]:
            M.write_new(path/name,dict(authority='HOST_DATA_ONLY_NOT_NATIVE_OR_APPROVAL',fixture=value))

    def test_J8_actualstack_and_true_adjacent_joins(self):
        r,v,m=fixture();self.save(r,v,m);samples,joins=M.choose_samples(r,v,m)
        self.assertEqual(len(samples),13);self.assertEqual(len([s for s in samples if s['kind']=='J']),6)
        self.assertTrue(all(len(s['actual_submitted_stack'])==8 for s in samples if s['kind']=='J'))
        self.assertTrue(all(j['after']==j['before']+1 for j in joins))

    def test_Shift9_33_all_four_poses(self):
        r,v,m=fixture('Shift');self.save(r,v,m);samples,joins=M.choose_samples(r,v,m)
        self.assertEqual(len(samples),11);self.assertEqual({s['frame'] for s in samples if s['kind']=='Shift'},{0,1,2,3})

    def test_missing_actual_pose_witness_rejected(self):
        r,v,m=fixture();v['source_pixels']['source_pixel_witnesses'].pop(2);self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'missing/duplicate'):M.choose_samples(r,v,m)

    def test_witness_borrowed_from_another_PNG_rejected(self):
        r,v,m=fixture();v['source_pixels']['source_pixel_witnesses'][1]['file']='HOST_OTHER.png';self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'actual PNG/pose'):M.choose_samples(r,v,m)

    def test_legacy_body_metadata_cannot_replace_actual_stack(self):
        r,v,m=fixture();r['observations'][6]['old_draw']['actual_stack']=['HOST_WRONG_PART'];self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'actual submitted|Actual submitted'):M.choose_samples(r,v,m)

    def test_nonadjacent_Land4_has_explicit_gap_and_actual_previous_Land5(self):
        r,v,m=fixture();extra=copy.deepcopy(r['observations'][5]);extra['physical_visual_key']=5
        r['observations'].insert(6,extra);m.insert(6,dict(file='MovieFrameHOSTINSERT.png'));r['first_action_callback_index']=7
        for witness in v['source_pixels']['source_pixel_witnesses']:
            if witness['observation']>=6:witness['observation']+=1
        self.save(r,v,m)
        samples,joins=M.choose_samples(r,v,m)
        previous=joins[0];token=joins[1]
        self.assertTrue(previous['actual_adjacent_callbacks']);self.assertEqual(previous['before_pose'],5)
        self.assertEqual((previous['before'],previous['after']),(6,7))
        self.assertFalse(token['actual_adjacent_callbacks']);self.assertEqual(token['intervening_callback_indices'],[6])
        self.assertEqual(token['role'],'causal_token_endpoints_gap_explicit')

    def test_last_action_gap_is_labelled_and_actual_adjacent_boundaries_preserved(self):
        r,v,m=fixture();r['observations'][12]['old_draw']['clip']='HOST_UNSUPPORTED_GAP';self.save(r,v,m)
        samples,joins=M.choose_samples(r,v,m)
        ready=joins[2];self.assertFalse(ready['actual_adjacent_callbacks'])
        self.assertEqual(ready['intervening_callback_indices'],[12])
        self.assertEqual([(x['before'],x['after']) for x in joins[-2:]],[(11,12),(12,13)])
        self.assertEqual(joins[-2]['after_kind'],'Observed_other')

    def test_changed_causal_token_mapping_rejected(self):
        r,v,m=fixture();r['landing_callback_index']=4;self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'Land4 pose'):M.choose_samples(r,v,m)

    def test_final_checker_binding_exact_and_wrong_explicit_checker_rejected(self):
        binding=M.read(HERE/'checker-binding-v001.json')
        checker=M.resolve_pinned(binding['checker_pin']);freeze=M.resolve_pinned(binding['checker_freeze_pin'])
        prereg=dict(checker_freeze_pin=M.pin(freeze))
        self.assertEqual(M.verify_current_checker(checker,freeze,prereg),binding)
        with self.assertRaisesRegex(ValueError,'Explicit checker/freeze'):M.verify_current_checker(Path(__file__),freeze,prereg)

    def test_wrong_runtime_schema_or_count_rejected(self):
        r,v,m=fixture();r['schema']='HOST_WRONG_SCHEMA';self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'schema'):M.verify_timeline(r,m)
        r['schema']=M.RUNTIME_SCHEMA
        with self.assertRaisesRegex(ValueError,'count'):M.verify_timeline(r,m[:-1])

    def test_original_monotonic_callback_timeline(self):
        r,v,m=fixture();self.save(r,v,m);offsets,duration=M.verify_timeline(r,m)
        self.assertEqual(offsets,r['capture_timing']['frame_wall_offsets_s']);self.assertGreater(duration,offsets[-1])
        r['capture_timing']['frame_wall_offsets_s'][2]=offsets[1]
        with self.assertRaisesRegex(ValueError,'strictly increasing'):M.verify_timeline(r,m)

    def test_duplicate_movie_filename_rejected(self):
        r,v,m=fixture();m[1]['file']=m[0]['file'];self.save(r,v,m)
        with self.assertRaisesRegex(ValueError,'filename membership'):M.verify_timeline(r,m)

    def test_exact_independent_dict_is_typed(self):
        self.assertFalse(M.exact_json_equal({'passed':True},{'passed':1}))
        self.assertFalse(M.exact_json_equal({'n':1.0},{'n':1}))
        self.assertTrue(M.exact_json_equal({'a':1,'b':[2.0]},{'b':[2.0],'a':1}))

    def test_retained_four_case_branch_is_unique(self):
        cases=[]
        for i,(action,side) in enumerate((('J',-1),('J',1),('Shift',-1),('Shift',1))):
            cases.append(dict(requested_action=action,requested_facing=side,process_id=i+1,run=f'HOST_RUN_{i}',
                              root_prereg_pin=dict(path=str(FIX/f'HOST_PREREG_{i}.json'),bytes=1,sha256=str(i)*64)))
        value=dict(schema=M.FOUR_SCHEMA,passed=True,four_fresh_processes=True,cases=cases)
        selected,lineage=M.retained_case(value,cases[2]);self.assertEqual(selected,cases[2]);self.assertEqual(lineage['selected_index'],2)
        cases[1]['root_prereg_pin']=copy.deepcopy(cases[2]['root_prereg_pin'])
        with self.assertRaisesRegex(ValueError,'absent/duplicate'):M.retained_case(value,cases[2])

    def test_retained_timing_gate_rejects_fake_or_changed_frames(self):
        header='#tb 0: 1/1000000\n'
        rows=header+'0,10000,10000,10000,1,HOST\n0,20000,20000,10000,1,HOST\n'
        M.timing_rows(rows,2,[.01,.02])
        with self.assertRaisesRegex(ValueError,'dropped/added'):M.timing_rows(rows,3,[.01,.02,.03])
        with self.assertRaisesRegex(ValueError,'PTS differ'):M.timing_rows(rows,2,[.01,.04])
        with self.assertRaisesRegex(ValueError,'timebase'):M.timing_rows(rows.replace('1/1000000','1/1000'),2,[.01,.02])


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests))
    report=dict(schema='landing-media-adapter-small-host-tests-v001',run=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                passed=result.wasSuccessful(),fixture_directory=FIX.as_posix(),authority='HOST_DATA_ADAPTER_ONLY_NOT_NATIVE_OR_ROOT_APPROVAL',
                candidate_source=M.pin(HERE/'prepare-landing-presentation-v001.py'),
                official_checker_invoked=False,media_encoded=False,actual_case_verified=False,actual_F_media_written=False,UE_started=False,View=False)
    M.write_new(HERE/f'host-tests-result-{RUN}.json',report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
