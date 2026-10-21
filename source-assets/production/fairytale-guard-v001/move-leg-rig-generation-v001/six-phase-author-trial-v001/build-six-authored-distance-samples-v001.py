"""Six AUTHORED distance samples from the fixed seven-part/two-contact pilot.
No AI, gameplay calls, new pivots, perpose fitting, source paint, or bone stretch.
"""
from pathlib import Path
import hashlib,json,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001';OUT=Path(__file__).resolve().parent
PIVOTS=O/'two-contact-pilot-v001/surface-markers-and-fixed-conversions-v001.json'
MEDIA=R/'过程图稿与视频/2026-10-18_裂岩守卫七件原材固定枢轴六相作者步态试拼_v001'
assert not MEDIA.exists() and not (OUT/'fixed-distance-trajectory-v001.json').exists()
def pin(p):
 b=Path(p).read_bytes();return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def vec(x):return np.array(x,dtype=float)
def angle(v):return math.atan2(v[1],v[0])
def rot(t):return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])

assert pin(PIVOTS)['sha256']=='e792e35cb6aca3aaed8850a5667c77f65fda77a680f530ff33f3134580b3fe09'
j=json.loads(PIVOTS.read_text(encoding='utf-8'));D=j['display_scale'];G=vec(j['virtual_ground_in_Rest_source']);ORDER=j['draw_order_far_to_near'];parts={p['part']:p for p in j['parts']};sources={};chain={}
for name,p in parts.items():
 assert pin(p['source']['path'])==p['source'];im=Image.open(p['source']['path']).convert('RGBA');assert hashlib.sha256(im.tobytes()).hexdigest()==p['source_RGBA_sha256'];sources[name]=im
def point(n,k):return vec(parts[n]['artist_surface_markers'][k]['xy'])
for side in ['near','far']:
 k=parts[side+'_thigh']['whole_kit_conversion_to_Rest_art_units'];assert k==.36 and parts[side+'_shin']['whole_kit_conversion_to_Rest_art_units']==k and parts[side+'_foot']['whole_kit_conversion_to_Rest_art_units']==k
 H=point('bodyrest_fixedaxe',side+'_hip_socket')-G;tp=point(side+'_thigh','hip');tq=point(side+'_thigh','knee');sp=point(side+'_shin','knee');sq=point(side+'_shin','ankle');fp=point(side+'_foot','ankle');heel=point(side+'_foot','heel');toe=point(side+'_foot','toe');beta=-angle(toe-heel);M=rot(beta)
 y,x=np.where(np.array(sources[side+'_foot'])[:,:,3]>=128);fy=((np.stack([x,y],1)-fp)@M.T*k)[:,1].max();mid=((heel+toe)/2-fp)@M.T*k
 chain[side]=dict(k=k,H=H,tp=tp,tq=tq,sp=sp,sq=sq,fp=fp,heel=heel,toe=toe,beta=beta,fy=fy,mid=mid,L1=float(np.linalg.norm(tq-tp)*k),L2=float(np.linalg.norm(sq-sp)*k))

trajectory=write(OUT/'fixed-distance-trajectory-v001.json',dict(schema='Guard-six-author-distance-trajectory-fixed-v001',source_markers_and_parameters=pin(PIVOTS),cycle_distance_world=128.,samples=[128.*i/6 for i in range(6)],
 half_phase='h=floor((d mod128)/64),u=((d mod128)-64*h)/64',
 stance='NEAR if h==0; FAR if h==1. Other chain swings.',
 stance_foot_midsole_x_display='20.8-41.6*u',swing_foot_midsole_x_display='-20.8+41.6*u',
 swing_lift_display='4*sin(pi*u)^2',stance_lift_display=0.,
 ankle='Sourcefoot fixed heel/toe rotation and actualcore sole offsets from frozen markers; translate foot sole up by lift, solve fixed two-axis chain with unchanged branch=-1.',
 source_conversions=dict(Rest=1.,Near_all3=.36,Far_all3=.36),display_scale=D,bodyroot_and_hips='Same frozen Rest-ground placement in ALL6; no bob, warp or perpose normalization.',
 authority='Authored offline straight-X samples only, not actual acceptedMovement receipts. Input d is a sample label here. Future native must accumulate actual collision-resolved path; blocked distance cannot advance.',
 contact_continuity='Positions continuous at0/64/128. Stance worldX is constant under nominal.65 straight-X projection; swing velocity starts/stops abruptly, not C1 smooth motion.',
 immutable_before_render=True,TrialAllowed=False,FinalAccepted=False))

def solve(distance):
 p=distance%128.;h=int(p>=64);u=(p-64*h)/64.;tr={'bodyrest_fixedaxe':dict(pivot=list(point('bodyrest_fixedaxe','root')),anchor=list(point('bodyrest_fixedaxe','root')-G),angle=0.,k=1.)};cs=[]
 for side in ['near','far']:
  q=chain[side];stance=(side=='near' and h==0) or (side=='far' and h==1);cx=20.8-41.6*u if stance else -20.8+41.6*u;lift=0. if stance else 4.*math.sin(math.pi*u)**2
  T=vec([cx/D-q['mid'][0],-q['fy']-lift/D]);V=T-q['H'];distance_to_ankle=float(np.linalg.norm(V));upper=(q['L1']+q['L2']-distance_to_ankle)*D;lower=(distance_to_ankle-abs(q['L1']-q['L2']))*D
  assert upper>0 and lower>0,'Unreachable fixed limb; no clamp/stretch/search fallback'
  U=V/distance_to_ankle;a=(q['L1']**2-q['L2']**2+distance_to_ankle**2)/(2*distance_to_ankle);rad=q['L1']**2-a*a;assert rad>=0
  K=q['H']+a*U-math.sqrt(rad)*vec([-U[1],U[0]])
  v1=K-q['H'];v2=T-K;cross=float(v1[0]*v2[1]-v1[1]*v2[0]);bend=math.atan2(cross,float(np.dot(v1,v2)));assert cross>0,'Fixed knee bend branch flipped'
  err=[abs(float(np.linalg.norm(v1))-q['L1']),abs(float(np.linalg.norm(v2))-q['L2'])];assert max(err)<1e-9
  tr[side+'_thigh']=dict(pivot=list(q['tp']),anchor=list(q['H']),angle=angle(v1)-angle(q['tq']-q['tp']),k=q['k'])
  tr[side+'_shin']=dict(pivot=list(q['sp']),anchor=list(K),angle=angle(v2)-angle(q['sq']-q['sp']),k=q['k'])
  tr[side+'_foot']=dict(pivot=list(q['fp']),anchor=list(T),angle=q['beta'],k=q['k'])
  cs.append(dict(side=side,stance=stance,u=u,midsole_local_x_display=cx,lift_display=lift,hip_art=list(q['H']),knee_art=list(K),ankle_art=list(T),fixed_lengths_art=[q['L1'],q['L2']],length_errors=err,
   reach_upper_margin_display=upper,reach_lower_margin_display=lower,bend_angle_radians=bend,strict_vertical_hip_knee_ankle_order=bool(q['H'][1]<K[1]<T[1])))
 return dict(authored_distance=distance,not_actual_movement_receipt=True,half=h,u=u,transforms=tr,chains=cs)

dense=[solve(128.*i/1001) for i in range(1001)];summary={}
for side in ['near','far']:
 cs=[next(c for c in p['chains'] if c['side']==side) for p in dense]
 summary[side]=dict(upper_reach_min_display=min(c['reach_upper_margin_display'] for c in cs),lower_reach_min_display=min(c['reach_lower_margin_display'] for c in cs),bend_radians_range=[min(c['bend_angle_radians'] for c in cs),max(c['bend_angle_radians'] for c in cs)],
  unreachable_samples=0,fixed_branch_flips=0,vertical_order_false_samples=sum(not c['strict_vertical_hip_knee_ankle_order'] for c in cs),max_length_error=max(max(c['length_errors']) for c in cs))
poses=[solve(128.*i/6) for i in range(6)]

def raster(pose,size,origin,gain):
 result=Image.new('RGBA',size,(0,0,0,0));masks={}
 for n in ORDER:
  t=pose['transforms'][n];M=rot(t['angle'])*(gain*t['k']);translation=vec(origin)+gain*vec(t['anchor'])-M@vec(t['pivot']);inv=np.linalg.inv(M);q=-inv@translation;svals=np.linalg.svd(M,compute_uv=False);assert abs(svals[0]-svals[1])<1e-10
  layer=sources[n].transform(size,Image.Transform.AFFINE,tuple(inv[0])+tuple([q[0]])+tuple(inv[1])+tuple([q[1]]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0));box=layer.getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<size[0] and box[3]<size[1]
  masks[n]=np.array(layer)[:,:,3];result.alpha_composite(layer)
 return result,masks

renders=OUT/'rendered';renders.mkdir();records=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
fullplate=Image.new('RGB',(1980,1420),(35,35,40));fd=ImageDraw.Draw(fullplate)
seamplate=Image.new('RGB',(2100,1120),(35,35,40));sd=ImageDraw.Draw(seamplate)
gifs=[]
for i,p in enumerate(poses):
 big,masks=raster(p,(768,768),(384,650),1.);small,_=raster(p,(160,160),(80,132),D);bp=renders/f'phase-{i}-ARTUNIT768.png';sp=renders/f'phase-{i}-DISPLAY100p8-160.png';big.save(bp);small.save(sp)
 x=(i%3)*660;y=(i//3)*700;enlarged=small.resize((640,640),Image.Resampling.NEAREST);fullplate.paste(enlarged,(x+10,y+40),enlarged);fd.text((x+10,y+5),f'{i}: AUTHOR d={p["authored_distance"]:.3f}',font=font,fill='white')
 crop=big.crop((215,405,565,655)).resize((700,500),Image.Resampling.NEAREST);sx=(i%3)*700;sy=(i//3)*550;seamplate.paste(crop,(sx,sy+35),crop);sd.text((sx+8,sy+5),f'{i}: leg/cap source region x2 nearest',font=font,fill='white')
 canvas=Image.new('RGB',(220,200),(35,35,40));canvas.paste(small,(30,35),small);gd=ImageDraw.Draw(canvas);gd.text((8,8),f'AUTHOR {i} d={p["authored_distance"]:.1f}',font=font,fill='white');gifs.append(canvas.resize((880,800),Image.Resampling.NEAREST))
 coverage=[]
 for c in p['chains']:
  side=c['side']
  for label,a,b in [('hip','bodyrest_fixedaxe',side+'_thigh'),('knee',side+'_thigh',side+'_shin'),('ankle',side+'_shin',side+'_foot')]:
   center=vec(c[label+'_art'])+[384,650];Y,X=np.ogrid[:768,:768];disk=(X-center[0])**2+(Y-center[1])**2<=36;ma=masks[a]>=128;mb=masks[b]>=128;coverage.append(dict(side=side,seam=label,local_only=True,union_core_coverage=float(((ma|mb)&disk).sum()/disk.sum()),overlap_pixels=int((ma&mb&disk).sum())))
 records.append(dict(phase=i,distance=p['authored_distance'],big=pin(bp),actual_display=pin(sp),local_cap_diagnostics_not_interface_acceptance=coverage))
fd.text((10,1400),'Fixed sources/pivots/kit scale. Six authored samples; not native / footlock / finished Move.',font=font,fill=(255,210,130));fp=OUT/'six-phase-ACTUAL100p8-x4-nearest-DIAGNOSTIC.png';fullplate.save(fp)
sd.text((8,1100),'Cap coverage at points cannot prove complete seams, occlusion, stance or physical locomotion.',font=font,fill=(255,210,130));cp=OUT/'six-phase-leg-seams-ARTUNIT-x2-nearest-DIAGNOSTIC.png';seamplate.save(cp)
gp=OUT/'six-authored-distance-samples-uniform100ms-NOT-native.gif';gifs[0].save(gp,save_all=True,append_images=gifs[1:],duration=[100]*6,loop=0,optimize=False,disposal=2)
proof=write(OUT/'six-phase-authored-poses-and-proof-v001.json',dict(schema='Guard-rigged-six-author-distance-samples-v001',frozen_markers=pin(PIVOTS),fixed_trajectory=pin(trajectory),poses=poses,renders=records,whole_trajectory_1001sample_check=summary,
 unchanged_seven_source_file_and_RGBA=True,no_new_source_pixels_or_AI=True,uniform_scale_only=True,Rest_bodyroot_and_hips_identical=True,near_layer_foreground_in_all6=True,
 rendering='Direct source uniformscale/rotation/translation withBICUBICAA. Small100.8 andlargeartunit render are eachdirect, no double resize. Plates are integernearest diagnostics only.',
 offline_GIF_uniform_ms=[100]*6,offline_GIF_not_speed_or_native_clock=True,
 wholebody_native_source_id=None,source_provenance='Derived authored2D rig from component native249/250/251; not an AI wholebody6row.',
 limitations=['FAR minimumreach margin.915display; no reach claim for differentRootheight/turn/depthpath.','FAR419/1001samples haveankleabovevisiblekneepivot; fixedbranchdoesnotflip, but thisfold maylookwrong.','Sourcecapunion islocalonly; sixphasewhole-seams/artreadabilityneedretainedView.','Swingxvelocity starts/stopsabruptly; no C1foottrajectory claim.','Fixedupperbody andfixedbootpitch maylookstiff. No inventedbob/torsoanimation.','Onlystraight+Xauthorgeometry; reversefacing/turns/diagonal2Dground andrealmovementreceipts stillunverified.','Sixdiscretebakes versuscontinuousformula are different future native policies and mustnot be conflated.'],
 TrialAllowed=False,FinalAccepted=False,NativeAcceptedMovementObserved=False,footlock=False,MoveComplete=False,new_media_View=False))
native_doc='''Future native formula (proposal only)\n\nUse D from actual collision-resolved acceptedMovement path, never speed*time, heldinput, drawcount or animationclock. P=positive_mod(D,128); h=(P>=64); u=(P-64*h)/64. Nearstances in h0, Farstances in h1. LocalmidsoleX=20.8-41.6*u forstance, -20.8+41.6*u forswing. Lift=0 forstance; 4*sin(pi*u)^2 forswing. Use frozenfootrotation/core-soleoffsets, unchangedhipplacement and fixedtwo-surface-axis lengths/branch=-1. Reject unreachablegeometry; do not stretch, clampreach, moveactorXY or rescaleparts to fit. BodyRest1/Near3.36/Far3.36 plusglobal100.8/455 stayconstant. Mirror completedwholehierarchy once fromactualFacing; never swapNear/Far sourceidentity.\n\nThese offline D values are authoredsamplelabels, not actualMovement receipts. Formula's stanceworldX relation assumesstraightX andnominalprojection.65. Current fullselector already requirespositiveacceptedMovement atactualcompletedboundary andusesDmod128; unchangedblocked/Ready/statepriority needsrealnativevalidation. Turning anddiagonalworldYneedexplicitRootpolicy andactualgroundprojection, not reinterpretationoftheseimages.\n\nSmallestnextintegration choice remainsRoot-owned aftervisualreview: bake6exact512derivedrigframes with explicitprovenance/basis/pivots, or draw7existingparts fromformula. ExistingFull gates requirepositiveNativeSourceId and6wholeframes, so do not assign249/250/251 as a fabricatedAIwholebodyMove6 or weakenrejected221/223checks. This packet changes noSource/profile/Content/import/snapshot and approvesneitherchoice.\n\nLimits: rigidupperbody/fixedbootpitch, swingvelocity discontinuities, Farrearreachmargin~.915px, Farfoldedshin mayreadwrong; localjointcoverage doesnotclosefullseams. Six100msGIF is uniformofflinepreview only, not a600msgamecycle. No native/fullMove/footlock/Finalacceptance.\n'''
nd=write(OUT/'distance-to-pose-native-handoff-PROPOSAL-v001.txt',native_doc)
freeze=write(OUT/'six-phase-author-trial-freeze-v001.json',dict(schema='Guard-six-phase-author-trial-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],new_media_View=False,TrialAllowed=False))
assert all(pin(p['source']['path'])==p['source'] for p in parts.values())
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/六相作者试拼完整包');(MEDIA/'原件/七件源原图').mkdir()
for n,p in parts.items():shutil.copy2(p['source']['path'],MEDIA/f'原件/七件源原图/{n}.png')
(MEDIA/'展示副本').mkdir()
for p in [fp,cp,gp]:shutil.copy2(p,MEDIA/'展示副本'/p.name)
for p in renders.iterdir():shutil.copy2(p,MEDIA/'展示副本'/p.name)
write(MEDIA/'source-version-status-index.json',dict(schema='F-dated-source-version-status-v001',proof=pin(proof),freeze=pin(freeze),native_formula=pin(nd),files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Six authoredoffline distance samples only; newimages/GIF pendingRootEbeforeView. No sourcepaint/native/footlock/completeMove acceptance.',Root_E_retention_pending=True,new_media_View=False))
print(json.dumps(dict(F_batch=MEDIA.as_posix(),proof=pin(proof),freeze=pin(freeze),native_formula=pin(nd),trajectory=pin(trajectory),whole_trajectory_check=summary,new_images_viewed=False),ensure_ascii=False,indent=2))
