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
    return dict({k:v for k,v in identity.items() if k not in ('player_entity','facing')},light_source_id='7',equipment_started_callback_index=0,equipment_commit_callback_index=1,equipment_input_index=0,equipment_start=.3,equipment_deadline=.8,schema='hero-landing-priority-native-observer-v001',requested_action=action,requested_facing=1,initial_hp=100.,ready_callback_index=2,landing_callback_index=7,priority_input_index=2,first_action_callback_index=8,action_start=2.025,action_end=2.625 if action=='J' else 2.425,action_start_landing_age=.045,normal_inputs=[einput,space,q],observations=[equip,committed,*rest],air_mask=15,primary_mask=63 if action=='J' else 0,dodge_mask=15 if action=='Shift' else 0,ready_join_frames=2)

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
    def test_top_Run_only_mutation_rejected(self):self.reject(lambda r:r.update(run='b'*32))
    def test_each_actual_top_identity_field_is_bound(self):
        for field in ('owner','current_room','epoch','weapon_instance','weapon_version','armor_instance','armor_version'):
            with self.subTest(field=field):self.reject(lambda r:r.update({field:'999'}))
    def test_optional_top_player_entity_cannot_override_owner(self):self.reject(lambda r:r.update(player_entity='999'))
    def test_result_identity_comes_from_verified_Ready(self):
        r=fixture();self.assertEqual(V.verify_causal(r)['verified_identity'],{k:r['observations'][r['ready_callback_index']][k] for k in V.IDENTITY})
    def test_skipped_first_Land4_still_under_06_rejected(self):
        def change(r):
            i=r['landing_callback_index'];earlier=copy.deepcopy(r['observations'][i]);earlier.update(sim=1.995,wall_offset_s=1.995,landing_visual_age=.015);earlier['old_draw'].update(sim=1.995,draw_id='1995')
            r['observations'].insert(i,earlier);r['landing_callback_index']+=1;r['first_action_callback_index']+=1
        self.reject(change)

class EveryTypedCallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        loaded,F,C=V.dependencies();_,cls.AM,cls.AP,*_=C.source_only()
        cls.DM=V.read(loaded['import-Dodge32-v001.json']);cls.DP=V.read(loaded['Dodge-runtime-profile-data-v001.json'])
        origins=V.read(p.parent/'geometry-fixture-origins-v002.json');cls.rows=[];cls.unit_rows=[]
        for row in origins['members']:
            if row['side']!='right':continue
            report=V.read(V.resolve_pin(row));key='new_air_draw' if row['kind']=='Air' else 'dodge_draw'
            choices=[o for o in report['observations'] if o[key]['drawn'] and o[key]['frame']==(0 if row['kind']=='Air' else 3) and (row['kind']!='Air' or o[key]['slot_count']==9)][:3]
            assert len(choices)==3
            for original in choices:
                o=copy.deepcopy(original)
                if row['kind']=='Air':o['action']={'active':False};o['dodge_draw']={'drawn':False,'slot_count':0,'actual_stack':[]}
                else:o=cls.adapt_dodge(o)
                cls.rows.append(o)
            if row['kind']=='Dodge':
                for frame in (1,2):cls.unit_rows.append(cls.adapt_dodge(copy.deepcopy(next(o for o in report['observations'] if o[key]['drawn'] and o[key]['frame']==frame))))
        cls.report=dict(requested_action='Shift',observations=cls.rows)
    @staticmethod
    def adapt_dodge(o):
        d=o['dodge_draw'];d['slot_count']=len(d['slots']);d['resident_count']=len(d['resident_textures']);o['owner']=d['owner'];o['jump_height']=d['jump_height'];o['rendered_player_stack']=o['rendered_stack'];o['old_draw']={'clip':'sword_dodge','actual_stack':d['actual_stack']};o['action']={'active':True};o['new_air_draw']={'drawn':False,'slot_count':0,'actual_stack':[]};o['new_air_query_ok']=False;o['physical_visual_key']=-1;return o
    def check(self,r):return V.verify_typed_callbacks(r,self.AM,self.AP,self.DM,self.DP)
    def reject(self,kind,mutation):
        r=copy.deepcopy(self.report);o=r['observations'][0 if kind=='Air' else 3];key='new_air_draw' if kind=='Air' else 'dodge_draw';mutation(o,key)
        with self.assertRaises(ValueError):self.check(r)
    def test_actual_historical_Air_and_Dodge_quads_accept(self):self.assertTrue(self.check(self.report)['passed'])
    def test_all_six_callbacks_really_checked(self):self.assertEqual(self.check(self.report)['counts'],{'Air':3,'Dodge':3})
    def test_actual_Dodge_frame1_and_2_unit_axes_accept(self):self.assertTrue(self.check(dict(requested_action='Shift',observations=self.unit_rows))['passed'])
    def test_Dodge_raw_axis_cannot_replace_actual_unit(self):
        r=dict(requested_action='Shift',observations=copy.deepcopy(self.unit_rows));r['observations'][0]['dodge_draw']['axis_artist']=self.DP['frames'][1]['Axis_artist_raw_xy']
        with self.assertRaises(ValueError):self.check(r)
    def test_Air_Land4_raw_axis_cannot_be_normalized(self):
        origins=V.read(p.parent/'geometry-fixture-origins-v002.json');origin=next(x for x in origins['members'] if x['kind']=='Air' and x['side']=='right');r=V.read(V.resolve_pin(origin));o=copy.deepcopy(next(o for o in r['observations'] if o['new_air_draw']['drawn'] and o['new_air_draw']['slot_count']==9 and o['physical_visual_key']==4));o['dodge_draw']={'drawn':False,'slot_count':0,'actual_stack':[]};o['action']={'active':False};a=o['new_air_draw']['axis_artist'];length=V.math.hypot(*a);o['new_air_draw']['axis_artist']=[x/length for x in a]
        with self.assertRaises(ValueError):self.check(dict(requested_action='J',observations=[o]))
    def test_non_midpoint_Air_wrong_equal_stacks_rejected(self):self.reject('Air',self.wrong_stacks)
    def test_non_midpoint_Dodge_wrong_equal_stacks_rejected(self):self.reject('Dodge',self.wrong_stacks)
    @staticmethod
    def wrong_stacks(o,key):
        bad=['substituted-non-midpoint']*9;o[key]['actual_stack']=bad;o['old_draw']['actual_stack']=bad;o['rendered_player_stack']=bad
    def test_non_midpoint_Air_missing_resident_rejected(self):self.reject('Air',lambda o,k:o[k]['resident_textures'].pop())
    def test_non_midpoint_Dodge_missing_resident_rejected(self):self.reject('Dodge',lambda o,k:o[k]['resident_textures'].pop())

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
