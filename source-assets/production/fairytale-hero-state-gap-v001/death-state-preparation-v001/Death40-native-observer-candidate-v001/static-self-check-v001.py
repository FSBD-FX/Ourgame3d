"""Candidate-only syntax, contract and adversarial geometry checks. No UE or media read.
Synthetic geometry inputs below test rejection logic; they are never native proof.
"""
from pathlib import Path
import ast,copy,json,math,runpy
C=Path(__file__).resolve().parent
api=runpy.run_path(str(C/'tooling/verify-Death-native-v001.py'))
profile=json.loads((C.parent/'Death40-native-ready-author-candidate-v002/Death-runtime-profile-author-candidate-v002.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((C.parent/'Death40-native-ready-author-candidate-v002/Death40-source-manifest-author-candidate-v002.json').read_text(encoding='utf-8-sig'))
def rejected(call):
 try:call()
 except ValueError:return
 raise AssertionError('Adversarial candidate fixture was not rejected')
for p in C.rglob('*.py'):compile(p.read_text(encoding='utf-8-sig'),str(p),'exec')
api['check_frozen'](C,'Death-observer-source-freeze-v001.json')
inputs=json.loads((C/'read-only-input-pins-v001.json').read_text(encoding='utf-8-sig'))
for pin in list(inputs['inputs'].values())+inputs['actual_DTO_headers']:api['pin'](pin)
rejected(lambda:api['preflight'](C/'NO-SNAPSHOT',C/'Root-Death5-prereg-TEMPLATE-NOT-APPROVED-v001.json'))
ages=[0.,math.nextafter(.2,0.),.2,math.nextafter(.4,0.),.4,math.nextafter(.6,0.),.6,math.nextafter(.8,0.),.8,1.2,1.e30]
assert [api['original_frame'](x)for x in ages]==[0,0,1,1,2,2,3,3,4,4,4]
for age in [-1.,float('nan'),float('inf')]:rejected(lambda:api['original_frame'](age))
positive=negative=0
for side in [-1,1]:
 for frame in range(5):
  f=profile['frames'][frame];scale=72/416;root=f['root_source_author'];anchor=f['weapon_anchor_source_author'];axis=f['weapon_axis_artist'];ground=[640.,490.];theta=math.atan2(axis[1],axis[0]);angle=math.degrees(theta)*side;at=[640+side*(anchor[0]-root[0])*scale,490+(anchor[1]-root[1])*scale];top=[640-(root[0]if side>0 else 512-root[0])*scale,490-root[1]*scale];pivot=[99/512 if side>0 else 1-99/512,.5];width=512*scale*.5;swordtop=[at[i]-pivot[i]*width for i in range(2)];age=[.05,.25,.45,.65,1.2][frame]
  r=dict(actual_approach_side=-side,frozen_sim=20.,player_entity='1',run='run',owner='2',sword_instance='3',light_instance='4')
  d=dict(opt_in=True,drawn=True,atomic_preflight_ready=True,supported=True,missing_reason='',sim=20.,player_entity='1',frame=frame,facing=side,profile=profile['profile_id'],death_active=True,dead=True,death_reported=True,death_health=0,death_animation='death',death_elapsed=age,run='run',owner='2',weapon_instance='3',armor_instance='4',weapon_content='WPN-SWD-001',armor_content='ARM-LGT-001',tint=[1,1,1,1],plan_tint=[1,1,1,1],visual_sword_released=frame>=1,last_frame_held=frame==4,root_source=root,sword_anchor_source=anchor,axis_artist=axis,jump_height=0,ui_scale=1,canvas_size=512*scale,source_to_screen_scale=scale,weapon_scale=.5,weapon_width=width,weapon_angle=angle,texture_u=0 if side>0 else 1,texture_du=side,context_ground=ground,body_top=top,sword_anchor_screen=at,sword_pivot_uv=pivot,sword_top=swordtop,nonempty_count=9)
  d['slots']=[]
  for i,s in enumerate(f['slots_bottom_to_top']):
   sword=s['component']=='IndependentSword';w=width if sword else 512*scale
   d['slots'].append(dict(slot=i,component=api['COMPONENTS'].index(s['component']),texture=s['object_path'],known_empty=False,texture_ready=True,drawn=True,draw_scale=1,scale_position=False,uv=[d['texture_u'],0],uv_size=[side,1],top=swordtop if sword else top,size=[w,w],rotation=angle if sword else 0,rotation_pivot=pivot if sword else [0,0]))
  d['actual_stack']=[s['texture']for s in d['slots']];d['resident_textures']=[dict(texture=p,class_='Texture2D',width=512,height=512,resource_ready=True)for p in [a['object_path']for a in manifest['assets']]+[profile['weapon_native_texture_path']]]
  for s in d['resident_textures']:s['class']=s.pop('class_')
  o=dict(death_draw=d,sim=20.,facing=side,weapon_instance='3',armor_instance='4',death_elapsed=age,animation_time=age,ground=[0,0],camera_ground=[0,0],rendered_stack=d['actual_stack'])
  api['verify_draw'](o,frame,profile,manifest,r);positive+=1
  mutations=[lambda x:x['death_draw']['tint'].__setitem__(0,.4),lambda x:x['death_draw']['resident_textures'].pop(),lambda x:x['death_draw']['resident_textures'][1].__setitem__('texture',x['death_draw']['resident_textures'][0]['texture']),lambda x:x['death_draw']['slots'][0].__setitem__('known_empty',True),lambda x:x['death_draw']['slots'][0].__setitem__('top',[1000,1000]),lambda x:x['death_draw'].__setitem__('weapon_scale',1.),lambda x:x['death_draw'].__setitem__('last_frame_held',frame!=4)]
  for mutate in mutations:
   bad=copy.deepcopy(o);mutate(bad);rejected(lambda:api['verify_draw'](bad,frame,profile,manifest,r));negative+=1
H=C.parents[1]/'hurt-native-observer-candidate-v001/tooling'
old=(H/'verify-Hurt-native-pixels-v001.py').read_text(encoding='utf-8');new=(C/'tooling/verify-Death-native-pixels-v001.py').read_text(encoding='utf-8');a=ast.parse(old);b=ast.parse(new);a.body=a.body[1:];b.body=b.body[1:];assert ast.dump(a)==ast.dump(b)
old=(H/'verify-Hurt-source-pixels-v001.py').read_text(encoding='utf-8');new=(C/'tooling/verify-Death-source-pixels-v001.py').read_text(encoding='utf-8')
expected=old.replace('hurt_observations','death_observations').replace("['hurt_draw']","['death_draw']").replace('range(4)','range(5)').replace('Actual Hurt phase','Actual Death phase').replace("source_paths[profile['independent_sword']['object_path']]=profile['independent_sword']['source']['path']","source_paths[profile['weapon_native_texture_path']]=profile['weapon_source']['path']")
assert expected==new,'Fixed source optical math or predeclared gates changed'
print(json.dumps(dict(candidate_static_only=True,Python_syntax_errors=0,pending_template_rejected_before_snapshot=True,source4_and_input_pins_unchanged=True,synthetic_phase_age_cases=len(ages)+3,synthetic_mirror_quad_positive_cases=positive,synthetic_adversarial_rejections=negative,CRC_FIFO_AST_unchanged=True,fixed_optical_math_and_gates_unchanged=True,UE_UBT_or_native_executed=False,PNG_or_media_decoded=False,FinalAccepted=False)))
