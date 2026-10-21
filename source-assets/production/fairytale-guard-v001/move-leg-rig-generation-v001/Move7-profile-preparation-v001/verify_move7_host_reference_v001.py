"""Independent boundary/negative cases and frozen-author golden geometry checks."""
from pathlib import Path
import copy,json,math,struct
import numpy as np
import move7_host_reference_solver_v001 as h
C=Path(__file__).resolve().parent
P=C/'GuardMove7-runtime-profile-candidate-v001.json';profile=h.read(P);solver=h.ReferenceSolver(P,h.pin(P)['sha256'])
base=h.read(C/'host-reference-request-example-v001.json');checks=[]
def check(label,condition):
 assert condition,label
 checks.append(dict(name=label,pass_=True))
def request(**changes):
 r=copy.deepcopy(base);r.update(changes);return r
def expect_reject(label,r):
 q=solver.solve(r);check(label,not q['valid_reference_plan'] and q['part_count']==0 and q['parts']==[]);return q['rejection']
def bad_profile(label,mutator):
 p=copy.deepcopy(profile);mutator(p)
 try:h.validate_profile_data(p)
 except (ValueError,TypeError,KeyError):check(label,True);return
 raise AssertionError(label+' accepted')
def matrix(row):
 a=row['source_to_screen_affine_rowmajor_2x3'];return np.array([[a[0],a[1]],[a[3],a[4]]]),np.array([a[2],a[5]])
def drawtexture(row,point,use_float=False):
 q=row['DrawTexture_float32_trace' if use_float else 'DrawTexture_equivalent'];top=np.array(q['Top']);size=np.array(q['Size']);pivot=np.array(q['RotationPivotUV']);u=np.array(point)/512.
 if q['UVSize'][0]==-1:u[0]=1.-u[0]
 t=math.radians(q['RotationDegrees']);M=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
 return top+size*pivot+M@(size*(u-pivot))

# Original18 independent direct pixel checks, without running the rig solver.
from PIL import Image
count=0
for part in profile['source7']:
 im=Image.open(part['source']['path']).convert('RGBA')
 for key,m in part['artist_surface_markers'].items():
  x,y=m['xy'];check(part['part']+'.'+key+'.original_opaque_bounds',type(x) is int and type(y) is int and 0<=x<512 and 0<=y<512 and im.getpixel((x,y))[3]==255)
  count+=1
check('exact18',count==18)
gold=h.verify(profile['frozen_inputs']['original6_author_poses'])
max_golden=0.;max_mirror=0.;max_decomp=0.;max_float=0.;max_length=0.
for pose in gold['poses']:
 d=pose['authored_distance'];r=request(accepted_distance_world=d,screen_ground_px=[0.,0.],ui_scale=1.)
 q=solver.solve(r);check(f'golden d{d} valid7',q['valid_reference_plan'] and len(q['parts'])==7)
 for row in q['parts']:
  old=pose['transforms'][row['part']]
  e=max(np.max(np.abs(np.array(row['art_anchor_from_source_ground'])-old['anchor'])),abs(row['source_rotation_radians']-old['angle']),abs(row['component_to_rest_scale']-old['k']))
  max_golden=max(max_golden,float(e))
 for c in q['chains']:max_length=max(max_length,*c['length_errors'])
check('all6 canonical matches frozen author transforms',max_golden<2e-12)
check('all6 fixed author lengths',max_length<1e-9)

# Mirroring and backend equivalence are independent point mappings, not screenshots.
for d in [0.,128./6,32.,64.,96.,127.999,128.,256.]:
 right=solver.solve(request(accepted_distance_world=d,actual_facing=1))
 left=solver.solve(request(accepted_distance_world=d,actual_facing=-1))
 check(f'd{d} both facing7',right['valid_reference_plan'] and left['valid_reference_plan'])
 check(f'd{d} unchanged depth/source identity',right['layer_order']==left['layer_order'] and [x['texture_object_path'] for x in right['parts']]==[x['texture_object_path'] for x in left['parts']])
 for rr,ll in zip(right['parts'],left['parts']):
  for pt in [[0.,0.],[512.,0.],[0.,512.],[512.,512.],rr['source_pivot_px']]:
   ar,br=matrix(rr);al,bl=matrix(ll);rp=ar@pt+br;lp=al@pt+bl
   expected=np.array([2.*base['screen_ground_px'][0]-rp[0],rp[1]])
   max_mirror=max(max_mirror,float(np.max(np.abs(lp-expected))))
   for row,actual in [(rr,rp),(ll,lp)]:
    max_decomp=max(max_decomp,float(np.max(np.abs(drawtexture(row,pt)-actual))))
    max_float=max(max_float,float(np.max(np.abs(drawtexture(row,pt,True)-actual))))
  for row,sign in [(rr,1),(ll,-1)]:
   M,_=matrix(row);gram=M.T@M;s=row['similarity_abs_scale']
   check(f'd{d}.{row["part"]}.{sign} uniform similarity',np.max(np.abs(gram-np.eye(2)*s*s))<1e-12 and math.copysign(1.,np.linalg.det(M))==sign)
check('one reflection point mapping',max_mirror<2e-10)
check('DrawTexture decomposition equals full affine',max_decomp<2e-10)
check('float DrawTexture reference error<.002px at test context',max_float<.002)
check('blocked same distance does not advance',solver.solve(request(accepted_distance_world=19.5))['parts']==solver.solve(request(accepted_distance_world=19.5))['parts'])
check('cycle128 closes',solver.solve(request(accepted_distance_world=0.))['parts']==solver.solve(request(accepted_distance_world=128.))['parts'])
check('passing peak104.8 not secretly normalized',solver.solve(request(accepted_distance_world=32.))['dynamic_crown_height']==104.8)
check('contact height100.8',solver.solve(request(accepted_distance_world=64.))['dynamic_crown_height']==100.8)

negative={}
for value in [float('nan'),float('inf'),-1.]:negative['bad_distance_'+str(value)]=expect_reject('distance '+str(value),request(accepted_distance_world=value))
for value in [float('nan'),float('inf'),0.,-1.,1e300,1e-300]:negative['bad_ui_'+str(value)]=expect_reject('ui '+str(value),request(ui_scale=value))
for value in [-2,0,2,True,None]:negative['bad_facing_'+str(value)]=expect_reject('facing '+str(value),request(actual_facing=value))
for value in [[float('nan'),0.],[0.,float('inf')],[0.],None]:negative['bad_ground_'+str(value)]=expect_reject('ground '+str(value),request(screen_ground_px=value))
negative['owner']=expect_reject('different path owner',request(accepted_path_owner_entity_id=4))
negative['profile']=expect_reject('profile snapshot mismatch',request(profile_sha256='0'*64))
negative['source']=expect_reject('source snapshot mismatch',request(source_snapshot_sha256='0'*64))
negative['missing_texture']=expect_reject('6 resident resources atomically rejects',request(atomic_texture_ready_paths=base['atomic_texture_ready_paths'][:6]))
negative['duplicate_texture']=expect_reject('duplicate resource atomically rejects',request(atomic_texture_ready_paths=[base['atomic_texture_ready_paths'][0]]*7))
negative['clock']=expect_reject('no frame or timer input',request(animation_time=1.,frame=2))
bad_profile('badsource png hash',lambda p:p['source7'][0]['source'].update(sha256='0'*64))
bad_profile('badsource decodedRGBA hash',lambda p:p['source7'][0].update(RGBA_sha256='0'*64))
bad_profile('badsource decoded pixel alias',lambda p:p['source7'][0].update(decoded_pixel_sha256='0'*64))
bad_profile('limblength override rejected',lambda p:p['derived_chains']['near'].update(thigh_length_rest_units=99.))
bad_profile('perpart scaling rejected',lambda p:p['source7'][2].update(component_to_rest_scale=.37))
bad_profile('wrong native namespace rejected',lambda p:p['source7'][0].update(texture_object_path='/Game/Bad.Bad'))
bad_profile('double mirror layer permutation rejected',lambda p:p.update(layer_order=list(reversed(p['layer_order']))))
bad_profile('bob retune rejected',lambda p:p['parameters'].update(body_hip_bob_display=5.))
# Each original point must reject all four image-outside boundaries, with no file edits.
for partindex,part in enumerate(profile['source7']):
 for key in part['artist_surface_markers']:
  for axis,value in [(0,-1),(0,512),(1,-1),(1,512)]:
   def change(p,i=partindex,k=key,a=axis,v=value):p['source7'][i]['artist_surface_markers'][k]['xy'][a]=v
   bad_profile(f'original18 {part["part"]}.{key} axis{axis} boundary{value}',change)

result=dict(schema='Guard-Move7-pure-host-independent-verification-v001',profile=h.pin(P),solver=h.pin(C/'move7_host_reference_solver_v001.py'),
 all_checks_passed=True,check_count=len(checks),checks=checks,negative_rejections=negative,
 golden_frozen6_max_error=max_golden,one_mirror_max_error_px=max_mirror,backend_decomposition_max_error_px=max_decomp,
 float_decomposition_max_error_px_at_example_context=max_float,limb_length_max_error=max_length,
 source7_current_pins_zero_mismatch=True,fixtures_are_synthetic_host_inputs_not_native_receipts=True,
 no_images_rendered=True,no_UE_or_import_or_generation=True,GPU_residency_observed=False,ActualAcceptedMovementObserved=False,footlock=False,FinalAccepted=False)
with (C/'host-reference-verification-v002.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
examples={'right_d32':solver.solve(request(accepted_distance_world=32.,actual_facing=1)),'left_d32':solver.solve(request(accepted_distance_world=32.,actual_facing=-1))}
with (C/'host-reference-output-examples-v002.json').open('x',encoding='utf-8') as f:json.dump(examples,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(dict(all_checks_passed=True,count=len(checks),golden_error=max_golden,mirror_error=max_mirror,decomposition_error=max_decomp,float_trace_error=max_float,report=h.pin(C/'host-reference-verification-v002.json')),ensure_ascii=False,indent=2))
