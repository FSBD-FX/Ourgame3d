"""Small causal counterexamples; synthetic fixtures never count as native proof."""
import copy
import importlib.util
from pathlib import Path
import unittest

p = Path(__file__).with_name('verify-landing-priority-native-v001.py')
s = importlib.util.spec_from_file_location('landing_checker', p)
V = importlib.util.module_from_spec(s); s.loader.exec_module(V)

def fixture(action='J'):
    identity=dict(run='a'*32,owner='1',current_room='1',epoch='0',player_entity='1',weapon_instance='1',weapon_version='1',armor_instance='2',armor_version='2',facing=1)
    def obs(sim,age,clip,frame,active=False):
        stack=V.expected_legacy(clip,frame) if clip in ('sword_ready_idle','sword_primary_1') else [str(i) for i in range(9)]
        o=dict(identity,sim=sim,wall_offset_s=sim,jump_height=0.,vertical_velocity=0.,landing_visual_age=age,hp=100.,dead=False,melee_grounded=True,wa_grounded=True,new_air_query_ok=not active,air_query_out_unchanged=active,physical_visual_key=frame if clip=='sword_nonattack_air' else -1,
            old_draw=dict(draw_id=str(round(sim*1000)),sim=sim,clip=clip,frame=frame,facing=1,active=True,supported=True,action_pose_supported=True,texture_ready=True,armor_drawn=True,sword_drawn=True,gear_placeholder=False,action_id='1' if active else '0',actual_stack=stack),
            new_air_draw=dict(drawn=not active and clip=='sword_nonattack_air',slot_count=9 if not active and clip=='sword_nonattack_air' else 0,actual_stack=stack if not active and clip=='sword_nonattack_air' else []),rendered_player_stack=stack,
            action=dict(active=active,id='1',start=2.025,end=2.625 if action=='J' else 2.425,started_airborne=False,stage=0,invulnerable=action=='Shift' and 2.085<=sim<2.225,finish=1,finished_at=2.425,finish_event_id='2'),completed_callback=True)
        o['ground']=[0.,0.];o['action'].update(start_event_id='1',block=0,blocked_at=-1,block_event_id='0',travelled=0.,origin=[0.,0.],direction=[1.,0.])
        o['dodge_draw']=dict(drawn=active,atomic_preflight_ready=True,slot_count=9,resident_count=33,actual_stack=stack,sim=sim,frame=frame)
        return o
    ready=obs(1.,V.f32(.12),'sword_ready_idle',0)
    air=[]
    for i,(h,v) in enumerate([(1.,600.),(90.,200.),(110.,0.),(90.,-200.)]):
        o=obs(1.5+i*.1,V.f32(.12),'sword_nonattack_air',i);o['jump_height']=h;o['vertical_velocity']=v;o['melee_grounded']=o['wa_grounded']=False;air.append(o)
    land=obs(2.,.02,'sword_nonattack_air',4)
    q=dict(identity,key='J' if action=='J' else 'LeftShift',down=True,sim=2.02,wall_offset_s=2.02,before_H=0.,before_V=0.,before_landing_age=.04,after_H=0.,after_V=0.,after_landing_age=.04,before_action_id='0',after_action_id='0',before_melee_grounded=True,before_wa_grounded=True,context_sampled_before_InputKey=True)
    space=dict(identity,key='SpaceBar',down=True,sim=1.4,wall_offset_s=1.4,before_H=0.,after_H=0.,before_V=0.,after_V=0.,before_landing_age=V.f32(.12),after_landing_age=V.f32(.12),before_melee_grounded=True,before_wa_grounded=True)
    acts=[obs(2.04+i*.1,min(V.f32(.12),.06+i*.1),'sword_primary_1' if action=='J' else 'sword_dodge',i,True) for i in range(6 if action=='J' else 4)]
    eq=dict(kind=2,active=True,action_id='1',operation_id='1',source_id='7',instance_id='2',slot=2,start=.3,deadline=.8)
    equip=obs(.4,V.f32(.12),'sword_ready_idle',0);equip['equipment_action']=dict(eq);equip['armor_instance']='0';equip['next_operation_id']='1'
    committed=obs(.85,V.f32(.12),'sword_ready_idle',0);committed['equipment_action']=dict(eq,active=False);committed['next_operation_id']='2'
    rest=[ready,*air,land,*acts,obs(2.8,V.f32(.12),'sword_ready_idle',0),obs(2.82,V.f32(.12),'sword_ready_idle',0)]
    for o in rest:o['equipment_action']=dict(eq,active=False);o['next_operation_id']='2'
    einput=dict(identity,key='E',down=True,sim=.2,wall_offset_s=.2,selected_source_id='7',context_sampled_before_InputKey=True,before_equipment_action=dict(active=False,action_id='0'))
    return dict(light_source_id='7',equipment_started_callback_index=0,equipment_commit_callback_index=1,equipment_input_index=0,equipment_start=.3,equipment_deadline=.8,schema='hero-landing-priority-native-observer-v001',requested_action=action,requested_facing=1,initial_hp=100.,ready_callback_index=2,landing_callback_index=7,priority_input_index=2,first_action_callback_index=8,action_start=2.025,action_end=2.625 if action=='J' else 2.425,action_start_landing_age=.045,normal_inputs=[einput,space,q],observations=[equip,committed,*rest],air_mask=15,primary_mask=63 if action=='J' else 0,dodge_mask=15 if action=='Shift' else 0,ready_join_frames=2)

class Causal(unittest.TestCase):
    def reject(self,mutation,action='J'):
        r=fixture(action);mutation(r)
        with self.assertRaises(ValueError):V.verify_causal(r)
    def test_valid_queued_J(self):self.assertTrue(V.verify_causal(fixture())['passed'])
    def test_valid_queued_Shift(self):self.assertTrue(V.verify_causal(fixture('Shift'))['passed'])
    def test_late_first_render_age_is_allowed(self):
        r=fixture();r['observations'][r['first_action_callback_index']]['landing_visual_age']=V.f32(.12);self.assertTrue(V.verify_causal(r)['passed'])
    def test_late_start_at_half_open_end_is_rejected(self):
        def change(r):
            r['action_start']=2.10;r['action_start_landing_age']=.12;r['action_end']=2.7
            for o in r['observations'][r['first_action_callback_index']:-2]:
                o['sim']+=.075;o['wall_offset_s']+=.075;o['old_draw']['sim']=o['sim'];o['old_draw']['draw_id']=str(round(o['sim']*1000));o['action']['start']=2.10;o['action']['end']=2.7
        self.reject(change)
    def test_enqueue_after_window_is_rejected(self):self.reject(lambda r:r['normal_inputs'][r['priority_input_index']].update(before_landing_age=V.f32(.12),after_landing_age=V.f32(.12)))
    def test_immediate_action_mutation_is_rejected(self):self.reject(lambda r:r['normal_inputs'][r['priority_input_index']].update(after_action_id='1'))
    def test_immediate_H_mutation_is_rejected(self):self.reject(lambda r:r['normal_inputs'][r['priority_input_index']].update(after_H=1.))
    def test_wrong_owner_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']].update(owner='2'))
    def test_wrong_epoch_is_rejected(self):self.reject(lambda r:r['normal_inputs'][r['priority_input_index']].update(epoch='1'))
    def test_wrong_gear_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']].update(armor_version='3'))
    def test_wrong_grounded_budget_is_rejected(self):self.reject(lambda r:r['normal_inputs'][r['priority_input_index']].update(before_wa_grounded=False))
    def test_stale_draw_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']]['old_draw'].update(draw_id=r['observations'][r['landing_callback_index']]['old_draw']['draw_id']))
    def test_cross_jump_ready_token_is_rejected(self):self.reject(lambda r:r['normal_inputs'][1].update(owner='2'))
    def test_first_action_skip_is_rejected(self):self.reject(lambda r:r.update(first_action_callback_index=r["first_action_callback_index"]+1))
    def test_land5_is_not_land4_is_rejected(self):self.reject(lambda r:r['observations'][r['landing_callback_index']].update(physical_visual_key=5,landing_visual_age=.08))
    def test_Air_partial_submission_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']]['new_air_draw'].update(slot_count=1))
    def test_Air_query_mutates_out_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']].update(air_query_out_unchanged=False))
    def test_wrong_clip_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']]['old_draw'].update(clip='sword_ready_idle'))
    def test_old_grey_armor_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']]['old_draw']['actual_stack'].__setitem__(2,'old-v007-grey'))
    def test_incomplete_primary_pose_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']+5]['old_draw'].update(frame=4))
    def test_missing_Ready2_is_rejected(self):self.reject(lambda r:r.update(ready_join_frames=1))
    def test_changed_Dodge_duration_is_rejected(self):self.reject(lambda r:r.update(action_end=2.426),'Shift')
    def test_wrong_iframe_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']+1]['action'].update(invulnerable=False),'Shift')
    def test_Dodge_collision_receipt_mismatch_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']+1]['action'].update(travelled=10.),'Shift')
    def test_Dodge_partial_resources_is_rejected(self):self.reject(lambda r:r['observations'][r['first_action_callback_index']+1]['dodge_draw'].update(resident_count=32),'Shift')
    def test_space_immediate_jump_is_rejected(self):self.reject(lambda r:r['normal_inputs'][1].update(after_V=630.))
    def test_equipment_deadline_changed_is_rejected(self):self.reject(lambda r:r.update(equipment_deadline=.79))
    def test_equipment_operation_changed_is_rejected(self):self.reject(lambda r:r['observations'][1]['equipment_action'].update(operation_id='2'))
    def test_ready_before_actual_equipment_commit_is_rejected(self):self.reject(lambda r:r.update(equipment_commit_callback_index=3))
    def test_equipment_real_shortened_duration_is_rejected(self):
        def change(r):
            r['equipment_deadline']=.79
            for o in r['observations']:o['equipment_action']['deadline']=.79
        self.reject(change)
    def test_equipment_borrowed_owner_is_rejected(self):self.reject(lambda r:r['observations'][0].update(owner='2'))
    def test_repeated_E_queue_is_rejected(self):self.reject(lambda r:r['normal_inputs'].append(copy.deepcopy(r['normal_inputs'][0])))
    def test_preexisting_equipment_action_is_rejected(self):self.reject(lambda r:r['normal_inputs'][0]['before_equipment_action'].update(active=True))
    def test_borrowed_equipment_action_id_is_rejected(self):self.reject(lambda r:r['normal_inputs'][0]['before_equipment_action'].update(action_id='1'))
    def test_false_completed_Dodge_is_rejected(self):self.reject(lambda r:r['observations'][-1]['action'].update(finish=2),'Shift')

class SourceOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lineage=V.read(p.parent/'Root-actual-input-pins-v001.json')
        cls.before=V.read(p.parent.parent/'before-source-pins-v001.json')
        cls.admission=V.read(V.resolve_pin(cls.lineage['source_admission_pin']))
        cls.repair=V.read(V.resolve_pin(cls.lineage['source_repair_admission_pin']))
        cls.freeze=V.read(V.resolve_pin(cls.lineage['source_candidate_freeze_pin']))
        cls.cm=V.read(V.resolve_pin(cls.lineage['compiled_manifest_pin']))
    def valid(self,cm=None,repair=None):return V.verify_source_overlay(self.before,self.admission,repair or self.repair,self.freeze,cm or self.cm)
    def test_real_298_overlay_and_repair_chain(self):self.assertEqual(self.valid()['source_files'],298)
    def test_real_exact_three_repairs_reproduce_actual_after_pin(self):
        original=next(x for x in self.freeze['members'] if x['path'].replace('\\','/').endswith('/new-source/DungeonHeroLandingPriorityProbeV001.cpp'))
        data=V.printf_repair_bytes(V.resolve_pin(original).read_bytes())
        self.assertEqual(len(data),self.repair['after']['bytes']);self.assertEqual(V.hashlib.sha256(data).hexdigest(),self.repair['after']['sha256'])
        self.assertEqual(data,V.resolve_pin(self.repair['after']).read_bytes())
    def test_changed_frozen_test_rejected(self):
        cm=copy.deepcopy(self.cm);next(x for x in cm['files'] if '/Source/' in x['path'] and '/Tests/' in x['path'])['sha256']='0'*64
        with self.assertRaises(ValueError):self.valid(cm=cm)
    def test_unrelated_fighter_change_rejected(self):
        cm=copy.deepcopy(self.cm);next(x for x in cm['files'] if x['path'].endswith('/DungeonFighter.cpp'))['sha256']='0'*64
        with self.assertRaises(ValueError):self.valid(cm=cm)
    def test_unknown_new_source_rejected(self):
        cm=copy.deepcopy(self.cm);cm['files'].append(dict(path='UnrealGame/Source/CodexDungeon/Unexpected.cpp',bytes=0,sha256='0'*64))
        with self.assertRaises(ValueError):self.valid(cm=cm)
    def test_wrong_repair_before_rejected(self):
        repair=copy.deepcopy(self.repair);repair['before']['sha256']='0'*64
        with self.assertRaises(ValueError):self.valid(repair=repair)
    def test_changed_repair_output_rejected(self):
        repair=copy.deepcopy(self.repair);repair['after']['sha256']='0'*64
        with self.assertRaises(ValueError):self.valid(repair=repair)
    def test_wrong_repair_target_rejected(self):
        repair=copy.deepcopy(self.repair);repair['after']['path']=repair['after']['path'].replace('ProbeV001.cpp','Other.cpp')
        with self.assertRaises(ValueError):self.valid(repair=repair)
    def test_partial_old_printf_source_rejected(self):
        with self.assertRaises(ValueError):V.printf_repair_bytes(b'FString::Printf(TEXT("no matching old source"));')

if __name__=='__main__':unittest.main()
