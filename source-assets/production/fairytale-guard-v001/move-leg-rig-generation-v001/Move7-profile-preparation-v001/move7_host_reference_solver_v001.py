"""Pure host geometry oracle for ONE frozen authored Move7 rig; never renders.

All points are artist surface attachments, not measured bones/physics sockets.
The reference resource-ready list is an input assertion, never proof of GPU work.
"""
from pathlib import Path
import argparse, hashlib, json, math, struct
import numpy as np
from PIL import Image

PRE_SHA='d0d275e10ed572396ce914e45f99d226820c26eb5fb125a4291128189aff1236'
OUTPUT_SHA='7a3bb8858febb3807af9d877c5e6a4285b00cb580f8fbea2cfb3c2733404ff60'
PARTS=['bodyrest_fixedaxe','near_thigh','near_shin','near_foot','far_thigh','far_shin','far_foot']
NAMES=['BodyRest','NearThigh','NearShin','NearFoot','FarThigh','FarShin','FarFoot']
NS='/Game/Production/ArtTrials/EV048/v019/GuardMoveRig'
ORDER=['far_foot','far_shin','far_thigh','near_foot','near_shin','near_thigh','bodyrest_fixedaxe']
def rb(p):return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 p=Path(p);b=rb(p);return {'path':p.as_posix(),'bytes':len(b),'sha256':sha(b)}
def read(p):return json.loads(rb(p).decode('utf-8-sig'))
def need(c,why):
 if not c:raise ValueError(why)
def verify(p):need(pin(p['path'])==p,'pin_mismatch:'+p['path']);return read(p['path'])
def finite(v):return type(v) in (int,float) and math.isfinite(v)
def vec(p):return np.array(p,dtype=float)
def rot(t):return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def angle(v):return math.atan2(v[1],v[0])
def f32(v):
 r=struct.unpack('<f',struct.pack('<f',float(v)))[0];need(math.isfinite(r),'float_trace_nonfinite');return r
def canonical_hash(p):
 d={k:p[k] for k in ['presentation_type','source7','parameters','layer_order','derived_chains']}
 return sha(json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8'))

def derive_chains(records):
 ps={p['part']:p for p in records};out={}
 def point(n,k):return vec(ps[n]['artist_surface_markers'][k]['xy'])
 for side in ['near','far']:
  k=.36;tp=point(side+'_thigh','hip');tq=point(side+'_thigh','knee');sp=point(side+'_shin','knee');sq=point(side+'_shin','ankle')
  fp=point(side+'_foot','ankle');heel=point(side+'_foot','heel');toe=point(side+'_foot','toe');beta=-angle(toe-heel);M=rot(beta)
  a=np.array(Image.open(ps[side+'_foot']['source']['path']).convert('RGBA'));yy,xx=np.where(a[:,:,3]>=128)
  projected=(np.stack([xx,yy],1)-fp)@M.T*k;mid=((heel+toe)/2-fp)@M.T*k
  out[side]={'thigh_axis_source_px':list(tq-tp),'shin_axis_source_px':list(sq-sp),
   'thigh_length_rest_units':float(np.linalg.norm(tq-tp)*k),'shin_length_rest_units':float(np.linalg.norm(sq-sp)*k),
   'foot_rotation_radians':beta,'foot_core_sole_offset_y_rest':float(projected[:,1].max()),
   'foot_midsole_offset_rest':list(mid),'fixed_branch':-1 if side=='near' else 1}
 return out

def validate_profile_data(p):
 need(p['schema']=='Guard-Move7-frozen-runtime-profile-candidate-v001','profile_schema')
 need(p['presentation_type']=='GuardMoveSevenComponentRigDerived','presentation_type')
 pre=p['frozen_inputs']['pre_render'];out=p['frozen_inputs']['output']
 need(pre['sha256']==PRE_SHA and out['sha256']==OUTPUT_SHA,'wrong_author_freeze')
 pf=verify(pre);of=verify(out)
 reviewpin=p['frozen_inputs']['Root_preparation_review']
 need(reviewpin['sha256']=='988aad91d063be6ba0be253cbc55957fe8e145a93eca56652365c06cd50f1b79','wrong_Root_preparation_review')
 review=verify(reviewpin);need(review['PreparationAllowed'] and not review['RuntimeTrialAllowed'],'Root_scope_not_preparation_only')
 retention=verify(p['frozen_inputs']['E572'])
 need(retention['verification_passes']==2 and retention['source_and_member_hash_mismatches']==0,'E572_not_two_SHA_zero')
 for x in of['files']:need(pin(x['path'])==x,'author_output_member_changed')
 original=verify(pf['markers']);verify(pf['trajectory']);need(pin(pf['script']['path'])==pf['script'],'author_script_changed')
 need(len(p['source7'])==7 and [x['part'] for x in p['source7']]==PARTS,'source7_order_or_count')
 for index,(x,old) in enumerate(zip(p['source7'],original['parts'])):
  need(x['source']==old['source'] and x['RGBA_sha256']==old['source_RGBA_sha256'],'badsource_or_RGBA_pin')
  need(x['decoded_pixel_sha256']==x['RGBA_sha256'] and x['source_size']==[512,512] and x['source_mode']=='RGBA','decoded_pixel_metadata')
  need(x['artist_surface_markers']==old['artist_surface_markers'],'original18_surface_points_changed')
  need(x['source_native_batch_id']==old['native_component_source_id'],'component_provenance_changed')
  need(x['component_to_rest_scale']==old['whole_kit_conversion_to_Rest_art_units'],'kit_density_changed')
  texture=f'{NS}/T_GuardMoveRig_{NAMES[index]}_v001.T_GuardMoveRig_{NAMES[index]}_v001'
  need(x['texture_object_path']==texture,'texture_namespace_or_name')
  need(pin(x['source']['path'])==x['source'],'source_file_changed')
  im=Image.open(x['source']['path']).convert('RGBA');need(im.size==(512,512),'source_not512')
  need(sha(im.tobytes())==x['RGBA_sha256'],'source_pixels_changed')
  for m in x['artist_surface_markers'].values():
   xy=m['xy'];need(len(xy)==2 and all(type(v) is int and 0<=v<512 for v in xy),'surface_point_bounds')
   need(list(im.getpixel(tuple(xy)))==m['actual_RGBA'] and m['actual_RGBA'][3]==255,'surface_point_not_original_opaque')
 need(sum(len(x['artist_surface_markers']) for x in p['source7'])==18,'surface18_count')
 expected=dict(source_ground=[250.,580.],core_crown_y=131.,standing_extent=449.,standing_display_height=100.8,
  screen_scale=100.8/449.,cycle_distance_world=128.,step_distance_world=64.,foot_half_stance_display=20.8,
  swing_lift_display=2.,body_hip_bob_display=4.,branches={'near':-1,'far':1})
 need(json.dumps(p['parameters'],sort_keys=True)==json.dumps(expected,sort_keys=True),'frozen_parameters_changed')
 need(p['layer_order']==ORDER,'layer_order_changed')
 need(p['derived_chains']==derive_chains(p['source7']),'limb_length_or_foot_offset_changed')
 need(p['source_snapshot_sha256']==canonical_hash(p),'source_snapshot_changed')
 return p

def rejection(reason):return dict(valid_reference_plan=False,rejection=reason,parts=[],part_count=0,
 native_runtime_approved=False,GPU_residency_observed=False,ActualAcceptedMovementObserved=False,footlock=False)

class ReferenceSolver:
 def __init__(self,profile_path,expected_profile_sha256):
  q=pin(profile_path);need(q['sha256']==expected_profile_sha256,'profile_pin_mismatch')
  self.profile=validate_profile_data(read(profile_path));self.profile_pin=q
  self.parts={x['part']:x for x in self.profile['source7']}
 def point(self,n,k):return vec(self.parts[n]['artist_surface_markers'][k]['xy'])
 def solve(self,r):
  try:return self._solve(r)
  except (KeyError,ValueError,TypeError,OverflowError,ZeroDivisionError,FloatingPointError) as ex:return rejection(str(ex))
 def _solve(self,r):
  fields={'owner_entity_id','accepted_path_owner_entity_id','accepted_distance_world','actual_facing','screen_ground_px','ui_scale','source_snapshot_sha256','profile_sha256','atomic_texture_ready_paths'}
  need(type(r) is dict and set(r)==fields,'request_fields')
  need(type(r['owner_entity_id']) is int and 0<r['owner_entity_id']<2**64,'owner_id')
  need(r['accepted_path_owner_entity_id']==r['owner_entity_id'] and type(r['accepted_path_owner_entity_id']) is int,'accepted_path_owner_mismatch')
  need(finite(r['accepted_distance_world']) and r['accepted_distance_world']>=0,'accepted_distance_nonfinite_or_negative')
  need(type(r['actual_facing']) is int and r['actual_facing'] in [-1,1],'facing_not_explicit_sign')
  need(len(r['screen_ground_px'])==2 and all(finite(v) for v in r['screen_ground_px']),'screen_ground_nonfinite')
  need(finite(r['ui_scale']) and r['ui_scale']>0,'ui_scale_nonfinite_or_nonpositive')
  need(r['profile_sha256']==self.profile_pin['sha256'] and r['source_snapshot_sha256']==self.profile['source_snapshot_sha256'],'snapshot_binding_mismatch')
  ready=r['atomic_texture_ready_paths'];expected=[x['texture_object_path'] for x in self.profile['source7']]
  need(type(ready) is list and len(ready)==7 and len(set(ready))==7 and set(ready)==set(expected),'atomic_seven_resources_not_ready')
  p=self.profile['parameters'];D=p['screen_scale'];G=vec(p['source_ground']);P=r['accepted_distance_world']%128.
  half=int(P>=64.);u=(P-64.*half)/64.;bob=4.*math.sin(2.*math.pi*P/128.)**2
  tr={'bodyrest_fixedaxe':dict(pivot=self.point('bodyrest_fixedaxe','root'),anchor=self.point('bodyrest_fixedaxe','root')-G-vec([0,bob/D]),angle=0.,k=1.)};cs=[]
  for side in ['near','far']:
   q=self.profile['derived_chains'][side];k=.36
   H0=self.point('bodyrest_fixedaxe',side+'_hip_socket')-G;H=H0-vec([0,bob/D])
   stance=(side=='near' and half==0) or (side=='far' and half==1)
   cx=20.8-41.6*u if stance else -20.8+41.6*u;lift=0. if stance else 2.*math.sin(math.pi*u)**2
   T=vec([H0[0]+cx/D-q['foot_midsole_offset_rest'][0],-q['foot_core_sole_offset_y_rest']-lift/D])
   V=T-H;dist=float(np.linalg.norm(V));L1=q['thigh_length_rest_units'];L2=q['shin_length_rest_units']
   need(abs(L1-L2)<dist<L1+L2,'unreachable_no_stretch_fallback')
   U=V/dist;aa=(L1*L1-L2*L2+dist*dist)/(2*dist);rad=L1*L1-aa*aa;need(rad>=0,'IK_negative_radicand')
   K=H+aa*U+q['fixed_branch']*math.sqrt(rad)*vec([-U[1],U[0]])
   v1=K-H;v2=T-K;errors=[abs(float(np.linalg.norm(v1))-L1),abs(float(np.linalg.norm(v2))-L2)]
   need(max(errors)<1e-9,'limb_length_changed')
   tr[side+'_thigh']=dict(pivot=self.point(side+'_thigh','hip'),anchor=H,angle=angle(v1)-angle(vec(q['thigh_axis_source_px'])),k=k)
   tr[side+'_shin']=dict(pivot=self.point(side+'_shin','knee'),anchor=K,angle=angle(v2)-angle(vec(q['shin_axis_source_px'])),k=k)
   tr[side+'_foot']=dict(pivot=self.point(side+'_foot','ankle'),anchor=T,angle=q['foot_rotation_radians'],k=k)
   cs.append(dict(side=side,stance=stance,hip_art=list(H),knee_art=list(K),ankle_art=list(T),fixed_lengths_art=[L1,L2],length_errors=errors,
    midsole_offset_ownhip_display=cx,core_sole_y_display=-lift,branch=q['fixed_branch']))
  rows=[];mirror=r['actual_facing'];S=np.diag([float(mirror),1.]);UI=float(r['ui_scale']);ground=vec(r['screen_ground_px'])
  for slot,name in enumerate(self.profile['layer_order']):
   t=tr[name];s=D*t['k']*UI;need(s>0 and f32(s)>0,'screen_scale_underflows_float_backend');M=S@rot(t['angle'])*s
   screen_anchor=ground+UI*(S@(D*t['anchor']));b=screen_anchor-M@t['pivot']
   affine=[float(M[0,0]),float(M[0,1]),float(b[0]),float(M[1,0]),float(M[1,1]),float(b[1])]
   need(all(math.isfinite(v) for v in affine),'affine_nonfinite')
   pivotUV=vec([t['pivot'][0]/512.,t['pivot'][1]/512.]);theta=math.degrees(t['angle'])
   if mirror==-1:pivotUV[0]=1.-pivotUV[0];theta=-theta
   size=vec([512.*s,512.*s]);top=screen_anchor-size*pivotUV
   corners=[list(M@vec(v)+b) for v in [[0,0],[512,0],[512,512],[0,512]]]
   rows.append(dict(slot=slot,part=name,texture_object_path=self.parts[name]['texture_object_path'],source_pivot_px=list(t['pivot']),
    art_anchor_from_source_ground=list(t['anchor']),source_rotation_radians=t['angle'],component_to_rest_scale=t['k'],
    source_to_screen_affine_rowmajor_2x3=affine,source_to_screen_affine_float32=[f32(v) for v in affine],
    screen_anchor=list(screen_anchor),source_corners_clockwise_screen=corners,similarity_abs_scale=s,determinant=float(np.linalg.det(M)),
    DrawTexture_equivalent=dict(Top=[float(v) for v in top],Size=[float(v) for v in size],UV=[0.,0.] if mirror==1 else [1.,0.],UVSize=[1.,1.] if mirror==1 else [-1.,1.],
     RotationDegrees=theta,RotationPivotUV=list(pivotUV),DrawScale=1.,ScalePosition=False),
    DrawTexture_float32_trace=dict(Top=[f32(v) for v in top],Size=[f32(v) for v in size],UV=[0.,0.] if mirror==1 else [1.,0.],UVSize=[1.,1.] if mirror==1 else [-1.,1.],
     RotationDegrees=f32(theta),RotationPivotUV=list(pivotUV),DrawScale=1.,ScalePosition=False)))
  need(len(rows)==7,'incomplete_plan')
  return dict(valid_reference_plan=True,rejection=None,scope='PURE_HOST_REFERENCE_ONLY',profile_sha256=self.profile_pin['sha256'],source_snapshot_sha256=self.profile['source_snapshot_sha256'],
   owner_entity_id=r['owner_entity_id'],accepted_distance_world=r['accepted_distance_world'],cycle_position=P,half=half,u=u,bob_up_display=bob,
   standing_basis_height=100.8,dynamic_crown_height=100.8+bob,screen_ground_px=r['screen_ground_px'],ui_scale=UI,facing=mirror,
   reflection_count=1 if mirror==-1 else 0,layer_order=self.profile['layer_order'],parts=rows,part_count=7,chains=cs,
   native_runtime_approved=False,GPU_residency_observed=False,ActualAcceptedMovementObserved=False,footlock=False)

def main():
 a=argparse.ArgumentParser();a.add_argument('--profile',required=True);a.add_argument('--profile-sha256',required=True);a.add_argument('--request',required=True);args=a.parse_args()
 try:result=ReferenceSolver(args.profile,args.profile_sha256).solve(read(args.request))
 except (KeyError,ValueError,TypeError,OSError) as ex:result=rejection(str(ex))
 print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False));return 0 if result['valid_reference_plan'] else 2
if __name__=='__main__':raise SystemExit(main())
