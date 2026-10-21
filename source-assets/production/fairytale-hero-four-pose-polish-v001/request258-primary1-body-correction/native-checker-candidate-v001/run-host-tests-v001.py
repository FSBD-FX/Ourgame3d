"""Small synthetic boundary tests. These do not constitute new native proof."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bridge258_tested',HERE/'verify-primary1-bridge258-native-v001.py')
V=importlib.util.module_from_spec(spec);spec.loader.exec_module(V)
B=HERE.parent
MANIFEST=V.read(V.LOADED['import_manifest'])
BASE_SOURCES,AM,AP=V.L.sources_for('J',V.LEGACY,V.C)
SOURCES=V.bridge_sources(BASE_SOURCES,MANIFEST)


def synthetic_native(side):
    # Existing true old native callback structure, with only an in-memory art
    # display variant. Never write or relabel an actual runtime-report file.
    folder=V.ROOT/('过程图稿与视频/2026-10-19_钟盔落地J_'+('left' if side==-1 else 'right')+'_v001/原件')
    r=V.read(folder/'runtime-report.json')
    r['request258_primary1_bridge_optin']=True
    r['request258_primary1_bridge_source_contract_sha256']=V.CONTRACT_SHA
    r['request258_primary1_bridge_source_pins']=V.expected_report_source_pins(MANIFEST)
    for o in r['observations']:
        d=o['old_draw']
        if d['clip']=='sword_primary_1' and d['frame'] in (0,1):
            f=V.DRAW['frames'][d['frame']]
            d['actual_stack']=list(f['draw_stack']);o['rendered_player_stack']=list(f['draw_stack'])
            d['root_source']=list(f['root']);d['grip_source']=list(f['grip'])
            ground=[640+(o['ground'][0]-o['camera_ground'][0])*V.f32(.65),490-o['ground'][1]*V.f32(.38)]
            d['grip_screen']=[V.f32(ground[0]+side*(f['grip'][0]-f['root'][0])*72/416),
                              V.f32(ground[1]-o['jump_height']*.70+(f['grip'][1]-f['root'][1])*72/416)]
    return r,folder


def synthetic_overlay():
    before=V.read(V.LOADED['predecessor_compiled_manifest']);cm=copy.deepcopy(before)
    frozen=[V.read(B/'UE-import-binding-candidate-v001/candidate-freeze-v001.json'),V.read(B/'native-observation-candidate-v001/candidate-freeze-v001.json')]
    members=[frozen[0]['members'],[dict(path=(B/'native-observation-candidate-v001'/x['relative_path']).as_posix(),bytes=x['bytes'],sha256=x['sha256']) for x in frozen[1]['files']]]
    files=V.member_map(cm['files']);before_rows=[];after_rows=[]
    for path, rows in zip((V.PRESENTATION,V.OBSERVER),members):
        suffix='/source/after-' if path==V.PRESENTATION else '/projected/'
        row=next(x for x in rows if suffix in x['path'] and Path(x['path']).name.endswith(Path(path).name))
        before_rows.append(copy.deepcopy(files[path]));new=dict(path=path,bytes=row['bytes'],sha256=row['sha256']);files[path]=new;after_rows.append(new)
    added=[dict(path=V.resolved(x['saved_path']).relative_to(V.ROOT).as_posix(),bytes=100+i,sha256='0'*64) for i,x in enumerate(MANIFEST['assets'])]
    files.update({x['path']:x for x in added});cm['files']=list(files.values());cm['production_files']=1439
    ad=dict(schema='Root-primary1-bridge258-source-admission-v001',RootApproved=True,is_template=False,actual_applied=True,FinalAccepted=False,
            actual_source_files=303,actual_production_files=1439,new_source_files=0,verification_passes=2,
            unrelated_source_tests_content_byte_mismatches=0,before_files=before_rows,after_files=after_rows)
    return before,cm,ad,members,added


class Boundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.right,cls.original=synthetic_native(1);cls.left,_=synthetic_native(-1)
    def test_01_raw_causal_inheritance(self):
        self.assertTrue(V.verify_exact_inheritance()['original_causal_function_bodies_byte_equal'])
    def test_02_exact_129_sources(self):
        self.assertEqual(len(SOURCES),129);self.assertEqual({k:SOURCES[k] for k in BASE_SOURCES},BASE_SOURCES)
    def test_03_normal_right_causal(self):
        V.verify_fixed_normal_inputs(self.right);V.verify_causal(self.right);V.verify_bridge_observation(self.right,MANIFEST)
    def test_04_normal_left_causal(self):
        V.verify_fixed_normal_inputs(self.left);V.verify_causal(self.left);V.verify_bridge_observation(self.left,MANIFEST)
    def test_05_wrong_stack(self):
        r=copy.deepcopy(self.right);i=r['first_action_callback_index'];r['observations'][i]['old_draw']['actual_stack'][0]=V.L.expected_legacy('sword_primary_1',0)[0]
        with self.assertRaises(ValueError):V.verify_causal(r)
    def test_06_wrong_numeric_grip(self):
        r=copy.deepcopy(self.right);i=r['first_action_callback_index'];r['observations'][i]['old_draw']['grip_source'][0]+=1
        with self.assertRaises(ValueError):V.verify_bridge_observation(r,MANIFEST)
    def test_07_wrong_source_metadata(self):
        r=copy.deepcopy(self.right);r['request258_primary1_bridge_source_pins'][0]['source_png_sha256']='0'*64
        with self.assertRaises(ValueError):V.verify_bridge_observation(r,MANIFEST)
    def test_08_optin_absent(self):
        r=copy.deepcopy(self.right);r['request258_primary1_bridge_optin']=False
        with self.assertRaises(ValueError):V.verify_bridge_observation(r,MANIFEST)
    def test_09_missing_new_readbacks(self):
        with self.assertRaises(ValueError):V.L.verify_resources(self.original,self.right,SOURCES,AM,AP)
    def test_10_wrong_source_pin(self):
        m=copy.deepcopy(MANIFEST);m['assets'][0]['source']['sha256']='0'*64
        with self.assertRaises(ValueError):V.bridge_sources(BASE_SOURCES,m)
    def test_11_thirteen_source_rows(self):
        m=copy.deepcopy(MANIFEST);m['assets'].pop()
        with self.assertRaises(ValueError):V.bridge_sources(BASE_SOURCES,m)
    def test_12_duplicate_source_binding(self):
        m=copy.deepcopy(MANIFEST);m['assets'][1]=copy.deepcopy(m['assets'][0])
        with self.assertRaises(ValueError):V.bridge_sources(BASE_SOURCES,m)
    def test_13_extra_f1_input(self):
        r=copy.deepcopy(self.right);r['normal_inputs'].append(dict(key='F1',down=True))
        with self.assertRaises(ValueError):V.verify_fixed_normal_inputs(r)
    def test_14_reenter_input(self):
        r=copy.deepcopy(self.right);r['normal_inputs'][10]['key']='Enter'
        with self.assertRaises(ValueError):V.verify_fixed_normal_inputs(r)
    def test_15_int_instead_bool_input(self):
        r=copy.deepcopy(self.right);r['normal_inputs'][0]['down']=1
        with self.assertRaises(ValueError):V.verify_fixed_normal_inputs(r)
    def test_16_exact_two_source_overlay(self):
        self.assertEqual(V.verify_overlay(*synthetic_overlay())['new_Texture2D_count'],14)
    def test_17_unrelated_source_edit(self):
        before,cm,ad,members,added=synthetic_overlay();row=next(x for x in cm['files'] if x['path'].endswith('/DungeonGameMode.cpp'));row['sha256']='0'*64
        with self.assertRaises(ValueError):V.verify_overlay(before,cm,ad,members,added)
    def test_18_old_soundwave_edit(self):
        before,cm,ad,members,added=synthetic_overlay();row=next(x for x in cm['files'] if '/HeroLocomotion/v001/Audio/' in x['path']);row['sha256']='0'*64
        with self.assertRaises(ValueError):V.verify_overlay(before,cm,ad,members,added)
    def test_19_missing_added_content(self):
        before,cm,ad,members,added=synthetic_overlay();added.pop()
        with self.assertRaises(ValueError):V.verify_overlay(before,cm,ad,members,added)
    def test_20_stale_observer_source(self):
        before,cm,ad,members,added=synthetic_overlay();row=next(x for x in ad['after_files'] if x['path']==V.OBSERVER);row['sha256']='0'*64
        with self.assertRaises(ValueError):V.verify_overlay(before,cm,ad,members,added)
    def test_21_original_other_expected_paths(self):
        for frame in range(2,6):self.assertEqual(V.expected_legacy('sword_primary_1',frame),V.L.expected_legacy('sword_primary_1',frame))
        for frame in range(4):self.assertEqual(V.expected_legacy('sword_ready_idle',frame),V.L.expected_legacy('sword_ready_idle',frame))
    def test_22_exact_new_flag_and_sides(self):
        for side in (-1,1):
            args=V.expected_arguments(Path('F:/Ourgame/synthetic-case'),side)
            self.assertEqual(args.count('-DungeonFairytalePrimary1Bridge258Preview'),1)
            self.assertIn('-DungeonHeroLandingPriorityFacing='+str(side),args)
            self.assertNotIn('-nosound',args)


if __name__=='__main__':
    unittest.main(verbosity=2)
