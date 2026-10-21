"""Read retained source pixels and write NEW metadata only; no renders or rig trial."""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib, json, shutil, zipfile

R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001'
C=Path(__file__).resolve().parent
B=R/'过程图稿与视频/2026-10-18_裂岩守卫Rest252可见冠髋比例与身份漂移补充_v001'
old=O/'rest1-extraction-v001/run-rest249-shared-HD-v001/curated/frame-0.png'
new=O/'rest252-extraction-v001/run-rest252-shared-HD-v001/curated/frame-0.png'
E=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18_E565-GuardMove-Rest252-extraction-v001/E-retention-index-v001.json')
def rb(p):return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()
def pin(p):
 p=Path(p);b=rb(p);return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(rb(p).decode('utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(d if isinstance(d,str) else json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sample(a,p):return dict(xy=p,actual_RGBA=[int(x) for x in a[p[1],p[0]]])
def eyes(a,roi):
 x0,y0,x1,y1=roi;b=a[y0:y1,x0:x1]
 m=(b[:,:,0]>=180)&(b[:,:,1]>=95)&(b[:,:,2]<=100)&(b[:,:,3]>=224)
 seen=set();result=[]
 for yy,xx in zip(*np.where(m)):
  key=(int(xx),int(yy))
  if key in seen:continue
  stack=[key];seen.add(key);pts=[]
  while stack:
   q=stack.pop();pts.append(q)
   for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
    t=(q[0]+dx,q[1]+dy)
    if 0<=t[0]<m.shape[1] and 0<=t[1]<m.shape[0] and m[t[1],t[0]] and t not in seen:
     seen.add(t);stack.append(t)
  if len(pts)>4:
   px=[t[0]+x0 for t in pts];py=[t[1]+y0 for t in pts]
   result.append(dict(pixels=len(pts),bbox=[min(px),min(py),max(px)+1,max(py)+1]))
 return result

assert not B.exists()
ret=read(E);assert ret['verification_passes']==2 and ret['source_and_member_hash_mismatches']==0
matched=[x for x in ret['files'] if x['sha256']==pin(new)['sha256'] and x['bytes']==pin(new)['bytes']]
assert matched
with zipfile.ZipFile(ret['packet']['path']) as z:assert any(z.read(x['member'])==rb(new) for x in matched)
extractfreeze=O/'rest252-extraction-v001/Rest252-extraction-freeze-v001.json'
for f in read(extractfreeze)['files']:assert pin(f['path'])==f
oldmarkers=O/'two-contact-pilot-v001/surface-markers-and-fixed-conversions-v001.json'
legs=[x for x in read(oldmarkers)['parts'] if x['part']!='bodyrest_fixedaxe']
for x in legs:assert pin(x['source']['path'])==x['source']
oldim=Image.open(old).convert('RGBA');newim=Image.open(new).convert('RGBA')
a=np.array(oldim);b=np.array(newim)
def crown(arr):
 ys,_=np.where(arr[100:180,220:290,3]>=224);return int(ys.min())+100
oy,ny=crown(a),crown(b);assert (oy,ny)==(125,131)
oldhips={'near':[216,420],'far':[284,416]}
newhips={'near':[224,404],'far':[277,400]}
for arr,points in [(a,oldhips),(b,newhips)]:
 for p in points.values():assert int(arr[p[1],p[0],3])==255
os={k:p[1]-oy for k,p in oldhips.items()};ns={k:p[1]-ny for k,p in newhips.items()}
def helmet(arr,y):
 xs=np.where(arr[y,170:310,3]>=224)[0]+170
 return dict(y=y,left=int(xs.min()),right=int(xs.max()),inclusive_width=int(xs.max()-xs.min()+1))
oh,nh=helmet(a,oy+40),helmet(b,ny+40)
oldshoulder=[[54,280],[332,299]];newshoulder=[[55,280],[335,301]]
for arr,pts in [(a,oldshoulder),(b,newshoulder)]:
 for p in pts:assert int(arr[p[1],p[0],3])>=224
ow=oldshoulder[1][0]-oldshoulder[0][0]+1;nw=newshoulder[1][0]-newshoulder[0][0]+1
normalizers=[]
for name,oldwidth,newwidth in [('upper_helmet_cap_horizontal_chord',oh['inclusive_width'],nh['inclusive_width']),('near_to_far_shoulder_outer_surface_horizontal_span',ow,nw)]:
 s=oldwidth/newwidth
 normalizers.append(dict(benchmark=name,old_width_px=oldwidth,new_width_px=newwidth,one_uniform_new_to_old_density=s,
  normalized_new_crown_to_hip={k:v*s for k,v in ns.items()},
  normalized_new_over_old={k:ns[k]*s/os[k] for k in os},
  observed_reduction_fraction={k:1-ns[k]*s/os[k] for k in os},
  requested_new_over_old=0.8,requested_reduction_fraction=0.2,
  target_old_equivalent_spans={k:v*.8 for k,v in os.items()},
  remaining_old_equivalent_px_over_target={k:ns[k]*s-os[k]*.8 for k in os}))
eo=eyes(a,(256,211,306,236));en=eyes(b,(256,216,309,246))
assert len(eo)==len(en)==2
audit={
 'schema':'Guard-Rest252-visible-surface-proportion-and-identity-audit-v001',
 'source_old':pin(old),'source_new':pin(new),'new_RGBA_sha256':hashlib.sha256(b.tobytes()).hexdigest(),
 'retention_new':pin(E),'new_retained_member_byte_equal':True,
 'actual_View_sources_after_retention':{'Rest249_after_E549':True,'Rest252_raw_after_E562':True,'Rest252_curated_after_E565':True},
 'authority':'Visible surface comparison only. Hips are newly hand-authored opaque pelvis-plate points, not anatomical joints or inherited old rig pivots. Width chords are projected visual density benchmarks, not physical shoulder measurements.',
 'core_crown_measurement':{'ROI':[220,100,290,180],'alpha_at_least':224,'old_y':oy,'new_y':ny},
 'hips_for_comparison_only':{'old':{k:sample(a,p) for k,p in oldhips.items()},'new':{k:sample(b,p) for k,p in newhips.items()}},
 'old_crown_to_hip_px':os,'new_crown_to_hip_px':ns,
 'helmet_density_benchmark':{'method':'Upper helmet cap chord at core crown+40 sourcepx, x search range170..309 inclusive; same named visible slab region, not whole alpha/axe box.','old':oh,'new':nh},
 'shoulder_density_benchmark':{'method':'Artist-selected near/far shoulder outside surfaces; compare horizontal projected span, including endpoint pixels. Both endpoints verified alpha>=224.','old':[sample(a,p) for p in oldshoulder],'new':[sample(b,p) for p in newshoulder]},
 'normalizations':normalizers,
 'point_selection_boundary':'This is an approximate artist surface comparison, not a statistical confidence interval or registered bone measurement. There is no unique density because the new artwork changed. Both independent visible-width normalizations show only about7.5–8.2% shortening, far less than the requested approximately20%; no pose/registration search was used.',
 'identity_review':{'reference_identity_remains_Ready209':True,'identity_accepted':False,
  'eyes':{'ROIs':{'old':[256,211,306,236],'new':[256,216,309,246]},'selection':'R>=180,G>=95,B<=100,alpha>=224,4-connected components with >4 pixels; color-core area only, not full eye/window outline.','old':eo,'new':en,
   'old_total_yellow_core_pixels':sum(x['pixels'] for x in eo),'new_total_yellow_core_pixels':sum(x['pixels'] for x in en),
   'yellow_core_area_ratio':sum(x['pixels'] for x in en)/sum(x['pixels'] for x in eo),
   'finding':'Both sources already have two amber ovals; new252 has larger yellow cores (+10.0% total under this exact selection), and their positions/face plates changed. Do not misreport a single slit changing into two eyes. The raw visual enlargement is less dramatic after consistent max-extent extraction but is still identity drift.'},
  'ink':{'raw_qualitative_View':'New252 appears to have heavier black contour strokes than old249.','width_measurement':None,'finding':'No precise same-feature normal-direction line-width measurement was made; do not invent a pixel thickness number or claim identity-preserving extraction removes source drift.'}},
 'technical_pipeline_not_identity_acceptance':{'extract_errors':0,'extract_warnings':0,'inspect_errors':0,'inspect_warnings':1,'static_motion_warning_preserved':True},
 'decision':'TARGET_NOT_REACHED_IDENTITY_DRIFT_NOT_ADMITTED_NO_RIG_TRIAL',
 'new_Rest_root_crown_nearhip_farhip_registration':None,'comparison_points_are_runtime_registration':False,
 'unchanged_leg_source_pins':[x['source'] for x in legs],'unchanged_leg_source_count':6,
 'existing44freeze_members_unchanged':True,'existing_extraction_freeze':pin(extractfreeze),
 'final_whole_rig_height':None,'cross_sheet_density':None,'rig_trial_performed':False,
 'no_new_media_rendered':True,'native_calls':0,'Source_Content_tools_ledger_E_modified':False,
 'TrialAllowed':False,'FinalAccepted':False,'formal_complete_units':0}
out=C/'Rest252-visible-proportions-and-identity-audit-v001.json';write(out,audit)
brief=C/'HANDOFF.md';write(brief,'''Rest252 is NOT admitted and no rig trial was performed. New metadata only; E565 input batch/index and all 44 frozen extraction members are unchanged.

After actual retained transparent View: core crown125→131; old author hips[216,420]/[284,416], independently selected new opaque pelvis surfaces[224,404]/[277,400]. Crown-to-hip295/291→273/269. Upper helmet cap chord116→116 gives normalized ratios0.9254/0.9244. Projected shoulder outer span279→281 gives0.9188/0.9178. This is about7.5–8.2% shortening, versus requested approximately20%. Projected visible density benchmarks and hand-authored comparison surfaces are not measured bones or runtime rig pivots. New rig registration remains null; 339/334px alpha boxes include axe and are not standing height.

Both old/new already have two amber eyes. New color-core area259→285(+10.0%) under the pinned selection; eye/window geometry and ink appearance drift remain unapproved. Precise line thickness was not measured. Technical0E1W inspect does not approve identity. Near250/Far251 six image pins remain exact, with no new scaling/warping or trial assembly. Root decides the next source strategy; no generation request is prepared here.
''')
freeze=C/'audit-metadata-freeze-v001.json';write(freeze,dict(schema='Guard-Rest252-new-metadata-freeze-v001',files=[pin(p) for p in sorted(C.rglob('*')) if p.is_file()],new_media_rendered=False,native_calls=0,TrialAllowed=False,FinalAccepted=False))
for p in sorted(C.rglob('*')):
 if p.is_file():
  q=B/'原件'/p.relative_to(C);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for p in [out,brief]:
 q=B/'展示副本'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for _ in range(2):
 for p in C.rglob('*'):
  if p.is_file():assert rb(p)==rb(B/'原件'/p.relative_to(C))
 for p in [out,brief]:assert rb(p)==rb(B/'展示副本'/p.name)
write(B/'index.json',dict(schema='F-Guard-Rest252-new-metadata-supplement-v001',status='SOURCE_NOT_ADMITTED_NO_NEW_IMAGES',
 audit=pin(out),freeze=pin(freeze),files=[pin(p) for p in sorted(B.rglob('*')) if p.is_file()],verification_passes=2,canonical_copy_mismatches=0,
 original_E565_batch_and44members_unchanged=True,new_media_rendered=False,rig_trial_performed=False,TrialAllowed=False,FinalAccepted=False))
print(json.dumps(dict(audit=pin(out),freeze=pin(freeze),F_batch=B.as_posix(),normalizations=normalizers,eye_area_ratio=audit['identity_review']['eyes']['yellow_core_area_ratio']),ensure_ascii=False,indent=2))
