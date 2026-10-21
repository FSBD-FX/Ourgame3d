"""Candidate provenance/scope and host-equation checks. Not a UE C++ execution."""
from pathlib import Path
import sys, hashlib, json, re, math, struct, argparse, difflib
import numpy as np

C=Path(__file__).resolve().parent;ROOT=Path('F:/Ourgame')
AUTH=ROOT/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001/Move7-profile-preparation-v001'
sys.path.insert(0,str(AUTH))
import move7_host_reference_solver_v001 as h
CM=ROOT/'source-assets/production/backups/v141-GuardMove7-Stage0-four-semantic-RED-v002/compiled-source-manifest.json'
CM_SHA='62a0e1ab2bdf45d4a6caebc304b8c4bd14306f50327e65e459626d7cba6d8d6e'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':sha(b)}
def read(p):return p.read_text(encoding='utf-8-sig')
def jread(p):return json.loads(read(p))
checks=[]
def check(name, ok):
 assert ok,name
 checks.append(name)
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
def vec(v):return np.array(v,dtype=float)
def angle(v):return math.atan2(v[1],v[0])
def rotate(v,a):return vec([math.cos(a)*v[0]-math.sin(a)*v[1],math.sin(a)*v[0]+math.cos(a)*v[1]])

def equation_model(profile,distance,facing,ground,ui,core):
 # Independent transcription of candidate equations for numerical comparison.
 # Native compiler, query and draw receipt still require Root's real UE run.
 s=profile['source7'];points=lambda i,k:vec(s[i]['artist_surface_markers'][k]['xy'])
 D=100.8/449.;p=math.fmod(distance,128.);half=int(p>=64.);u=(p-half*64.)/64.;bob=4.*math.sin(2.*math.pi*p/128.)**2
 G=vec([250.,580.]);c={0:(points(0,'root'),points(0,'root')-G-vec([0.,bob/D]),0.)}
 for near,b in [(True,1),(False,4)]:
  H0=points(0,'near_hip_socket' if near else 'far_hip_socket')-G;H=H0-vec([0.,bob/D])
  ta=points(b,'knee')-points(b,'hip');sa=points(b+1,'ankle')-points(b+1,'knee')
  l1=math.sqrt(float(ta@ta))*.36;l2=math.sqrt(float(sa@sa))*.36
  beta=-angle(points(b+2,'toe')-points(b+2,'heel'))
  mid=rotate((points(b+2,'heel')+points(b+2,'toe'))*.5-points(b+2,'ankle'),beta)*.36
  stance=(half==0)==near;x=(20.8-41.6*u) if stance else (-20.8+41.6*u);lift=0. if stance else 2.*math.sin(math.pi*u)**2
  T=vec([H0[0]+x/D-mid[0],-core[0 if near else 1]-lift/D]);v=T-H;length=math.sqrt(float(v@v));unit=v/length
  assert abs(l1-l2)<length<l1+l2
  a=(l1*l1-l2*l2+length*length)/(2.*length);k=H+a*unit+(-1 if near else 1)*math.sqrt(l1*l1-a*a)*vec([-unit[1],unit[0]])
  c[b]=(points(b,'hip'),H,angle(k-H)-angle(ta));c[b+1]=(points(b+1,'knee'),k,angle(T-k)-angle(sa));c[b+2]=(points(b+2,'ankle'),T,beta)
 rows=[]
 for i in [6,5,4,3,2,1,0]:
  pivot,anchor,a=c[i];scale=D*(1. if i==0 else .36)*ui;size=512.*scale
  uv=pivot/512.;degrees=a*180./math.pi
  if facing<0:uv=vec([1.-uv[0],uv[1]]);degrees=-degrees
  sa=vec(ground)+vec([facing*D*anchor[0]*ui,D*anchor[1]*ui]);top=sa-size*uv
  rows.append(dict(i=i,pivot=pivot,anchor=anchor,angle=a,screen_anchor=sa,Top=[f32(float(v)) for v in top],Size=[f32(size),f32(size)],RotationDegrees=f32(degrees),RotationPivotUV=list(uv),UV=[1.,0.] if facing<0 else [0.,0.],UVSize=[-1.,1.] if facing<0 else [1.,1.]))
 return dict(cycle=p,bob=bob,rows=rows)

def submitted(q,source):
 top=vec(q['Top']);size=vec(q['Size']);pivot=vec(q['RotationPivotUV']);uv=vec(source)/512.
 if q['UVSize'][0]<0:uv[0]=1.-uv[0]
 # Actual Canvas rounds unrotated corners, beyond the old host's metadata.
 corners=vec([f32(float(top[0]+size[0])),f32(float(top[1]+size[1]))])-top
 local=corners*uv-size*pivot
 return top+size*pivot+rotate(local,q['RotationDegrees']*math.pi/180.)

def main():
 a=argparse.ArgumentParser();a.add_argument('--version',default='v001');args=a.parse_args()
 check('immutable Stage0 manifest pin',sha(CM.read_bytes())==CM_SHA)
 cm=jread(CM);sourcepins={x['path']:x for x in cm['files'] if x['path'].startswith('UnrealGame/Source/')}
 check('279 frozen actual sources',len(sourcepins)==279)
 for n in range(2):
  for key,old in sourcepins.items():
   actual=pin(ROOT/key);check(f'actual Source pass{n+1}: {key}',actual['bytes']==old['bytes'] and actual['sha256']==old['sha256'])
 before=[]
 for p in sorted((C/'before').iterdir()):
  key='UnrealGame/Source/CodexDungeon/'+p.name;old=sourcepins[key];now=pin(p)
  check('exact before '+p.name,now['bytes']==old['bytes'] and now['sha256']==old['sha256']);before.append(dict(actual_path=key,**now))
 profilepath=AUTH/'GuardMove7-runtime-profile-candidate-v001.json';profile=jread(profilepath)
 solver=h.ReferenceSolver(profilepath,'03156e971171f597ca504e9c0176d5a2fdf3c31c09b3eddae2995e2245193b51')
 data=read(C/'new-source/DungeonFairytaleGuardMoveRigDataV001.inl')
 approval=ROOT/'docs/production/first-batch-v2/evidence/GuardMove7-v141-v001/root-runtime-trial-approval-v001/Root-limited-runtime-trial-approval-v001.json'
 check('true Root approval byte pin',sha(approval.read_bytes())=='d78bcbca8cd47caa781ee9a1bdcc1c25c5f9a3036be5d72dc2a2dcceb57feb9e')
 check('typed Root approval and bounded gates',str(approval.relative_to(ROOT)).replace('\\','/') in data and 'P.TrialAllowed=true;P.FinalAccepted=false' in data and sha(approval.read_bytes()) in data)
 blocks=re.findall(r'\{FSourcePart S;(.+?)P.Sources.Add\(MoveTemp\(S\)\);\}',data,re.S)
 check('seven separately typed parts',len(blocks)==7)
 names=['BodyRest','NearThigh','NearShin','NearFoot','FarThigh','FarShin','FarFoot'];marker_count=0
 for i,(b,old) in enumerate(zip(blocks,profile['source7'])):
  check('typed source identity/pins '+names[i],f'S.Component=EComponent::{names[i]};' in b and old['texture_object_path'] in b and old['source']['sha256'] in b and old['RGBA_sha256'] in b and f'S.NativeBatchId={old["source_native_batch_id"]};S.ComponentToRestScale={old["component_to_rest_scale"]};' in b)
  marks=re.findall(r'S.Markers.Add\(\{TEXT\("([^"]+)"\),FVector2D\(([\d]+)\.,([\d]+)\.\),FColor\(([\d,]+)\)\}\);',b)
  want=[(name,str(m['xy'][0]),str(m['xy'][1]),','.join(map(str,m['actual_RGBA']))) for name,m in old['artist_surface_markers'].items()]
  check('all exact opaque surface markers '+names[i],marks==want);marker_count+=len(marks)
 check('eighteen original surface points',marker_count==18)
 cpp=read(C/'changed-source/DungeonFairytaleGuardMoveRigV001.cpp')
 core=[float(v) for v in re.search(r'const double CoreSole=Near\?([^:]+):([^;]+);',cpp).groups()]
 check('original alpha-core sole offsets',core==[profile['derived_chains']['near']['foot_core_sole_offset_y_rest'],profile['derived_chains']['far']['foot_core_sole_offset_y_rest']])
 check('double pi avoids Unreal float macro', 'constexpr double MovePi=3.14159265358979323846' in cpp and not re.search(r'\bPI\b',cpp))
 check('actual float vertex collapse gate', 'Right<=Q.X||Bottom<=Q.Y' in cpp)
 check('failure preserves caller solve/plan output',cpp.count('Out=MoveTemp(Candidate)')==2)
 ready=[r['texture_object_path'] for r in profile['source7']];max_meta=0.;max_surface=0.;max_hip=0.;cases=0
 for distance in [0.,.000001,1.6,2.,24.,32.,48.,64.,72.,96.,120.,127.999999,128.,134.,256.]+[i*.5 for i in range(256)]:
  for facing in [1,-1]:
   for ui in [1.,1.25]:
    request=dict(owner_entity_id=95104,accepted_path_owner_entity_id=95104,accepted_distance_world=distance,actual_facing=facing,screen_ground_px=[640.125,420.875],ui_scale=ui,source_snapshot_sha256=profile['source_snapshot_sha256'],profile_sha256=sha(profilepath.read_bytes()),atomic_texture_ready_paths=ready)
    oracle=solver.solve(request);model=equation_model(profile,distance,facing,request['screen_ground_px'],ui,core)
    check('host reachable d/f/ui '+repr((distance,facing,ui)),oracle['valid_reference_plan'] and len(model['rows'])==7)
    max_meta=max(max_meta,abs(model['cycle']-oracle['cycle_position']),abs(model['bob']-oracle['bob_up_display']))
    byid={q['i']:q for q in model['rows']}
    for row,oq in zip(model['rows'],oracle['parts']):
     tq=oq['DrawTexture_float32_trace']
     max_meta=max(max_meta,float(np.max(np.abs(row['anchor']-oq['art_anchor_from_source_ground']))),abs(row['angle']-oq['source_rotation_radians']))
     for key in ['Top','Size','RotationDegrees','RotationPivotUV','UV','UVSize']:max_meta=max(max_meta,float(np.max(np.abs(np.array(row[key])-tq[key]))))
     # API-boundary geometry checks, including actual float corner rounds.
     M,b=h.rot(oq['source_rotation_radians'])*oq['component_to_rest_scale']*(100.8/449.)*ui,None
     for point in [[0.,0.],[512.,512.],list(row['pivot'])]:
      affine=oq['source_to_screen_affine_rowmajor_2x3'];want=vec([affine[0]*point[0]+affine[1]*point[1]+affine[2],affine[3]*point[0]+affine[4]*point[1]+affine[5]])
      max_surface=max(max_surface,float(np.linalg.norm(submitted(row,point)-want)))
    near=np.linalg.norm(submitted(byid[0],[224.,404.])-submitted(byid[1],[280.,126.]));far=np.linalg.norm(submitted(byid[0],[277.,400.])-submitted(byid[4],[263.,124.]));max_hip=max(max_hip,float(near),float(far));cases+=1
 check('frozen host equation metadata error < 2e-12',max_meta<2e-12)
 check('actual float surface reconstruction error < .001',max_surface<.001)
 check('actual float body hip attachment error < .001',max_hip<.001)
 huge=equation_model(profile,32.,1,[1.e20,1.e20],1.,core)
 check('finite1e20 actual float corners collapse and must reject',all(f32(q['Top'][0]+q['Size'][0])==q['Top'][0] and f32(q['Top'][1]+q['Size'][1])==q['Top'][1] for q in huge['rows']))
 fighter=read(C/'changed-source/DungeonFighter.cpp');q=fighter.split('bool ADungeonFighter::QueryCompletedGuardMove(',1)[1].split('bool ADungeonFighter::QueryDodgePresentation',1)[0]
 check('query no mutation/Sweep/time/AI/save reuse',all(x not in q for x in ['StepTo(', 'QuerySweep(', 'QueryResolvedMovement(', 'BeginCombat(', 'CaptureOwnerSnapshot(', 'HurtTime','bAIEnabled=', 'CompletedGroundMotion']))
 check('read current stable native scope/time/projection',all(x in q for x in ['Game->bRunTickActive','Game->bSimulationBatch','Game->bSimulatingMotion','Game->PendingDamage.IsEmpty','W.RunGuid!=V.RunGuid','W.Time!=Now','Game->FindWorldFighter(Id)!=this','Bindings!=1','NativeOwnerPositionProjection','LastGuardSyncTime!=S.Time','GetRunPresentationEpoch()','std::hypot','Candidate.BlockKnown=false']))
 presentation=read(C/'new-source/DungeonFairytaleGuardMovePresentationV001.cpp')
 check('renderer exact same submitted quad and one feedback',presentation.count('DrawTexture(Texture,Q.X,Q.Y,Q.Width,Q.Height,Q.U,Q.V,Q.UL,Q.VL,Q.Tint')==1 and 'Submitted.Quad=Q;' in presentation and presentation.count('DrawGuardFeedback(F)')==1)
 check('only Rest body enters legacy actor masks','if(Part.Component==EComponent::BodyRest)' in presentation and presentation.count('ActorQuads.Add')==1)
 check('five existing and two new source files',len(list((C/'changed-source').iterdir()))==5 and len(list((C/'new-source').iterdir()))==2)
 for p in sorted((C/'changed-source').iterdir()):
  diff=''.join(difflib.unified_diff(read(C/'before'/p.name).splitlines(True),read(p).splitlines(True),fromfile='a/UnrealGame/Source/CodexDungeon/'+p.name,tofile='b/UnrealGame/Source/CodexDungeon/'+p.name))
  patch=C/'patches'/(p.name+'.patch')
  if not patch.exists():patch.write_text(diff,encoding='utf-8',newline='\n')
  check('exact patch '+p.name,read(patch)==diff)
 result=dict(schema='GuardMove7-production-candidate-host-checks-'+args.version,all_checks_passed=True,checks=checks,check_count=len(checks),numerical_cases=cases,max_equation_metadata_error=max_meta,max_actual_float_surface_error=max_surface,max_body_hip_attachment_error=max_hip,before=before,stage0_manifest=pin(CM),native_Cpp_executed=False,native_query_verified=False,native_GPU_or_DrawTexture_verified=False,actual_Source_written=False,scope='Static scope/provenance and synthetic stateless numerical transcription versus frozen independent host; Root must compile/run frozen tests and record real native game')
 out=C/('host-checks-'+args.version+'.json')
 with out.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:result[k] for k in ['all_checks_passed','check_count','numerical_cases','max_equation_metadata_error','max_actual_float_surface_error','max_body_hip_attachment_error']}))
if __name__=='__main__':main()
