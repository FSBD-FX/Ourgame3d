"""One fixed authored rig trial. No source paint, provider, engine or parameter search."""
from pathlib import Path
import hashlib,json,math,shutil,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont

R=Path('F:/Ourgame');O=R/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001'
C=Path(__file__).resolve().parent
B=R/'过程图稿与视频/2026-10-18_裂岩守卫Rest252固定七件ownhip128与起伏4六相作者试拼_v001'
OLD=O/'two-contact-pilot-v001/surface-markers-and-fixed-conversions-v001.json'
assert not B.exists() and not (C/'surface18-and-fixed-parameters-v001.json').exists()
def rb(p):return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()
def pin(p):
 p=Path(p);b=rb(p);return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(rb(p).decode('utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def vec(p):return np.array(p,dtype=float)
def rot(t):return np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]])
def angle(v):return math.atan2(v[1],v[0])

prior=read(OLD);parts=prior['parts'];parts[0]=dict(parts[0])
newsrc=O/'rest252-extraction-v001/run-rest252-shared-HD-v001/curated/frame-0.png'
e=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18_E565-GuardMove-Rest252-extraction-v001/E-retention-index-v001.json')
er=read(e);fp=pin(newsrc)
assert er['verification_passes']==2 and er['source_and_member_hash_mismatches']==0
member=next(x for x in er['files'] if x['sha256']==fp['sha256'] and x['bytes']==fp['bytes'])
with zipfile.ZipFile(er['packet']['path']) as z:assert z.read(member['member'])==rb(newsrc)
ni=Image.open(newsrc).convert('RGBA')
newpoints={'root':[250,403],'crown':[254,137],'near_hip_socket':[224,404],'far_hip_socket':[277,400]}
newmarks={}
for k,p in newpoints.items():
 rgba=list(ni.getpixel(tuple(p)));assert rgba[3]==255
 newmarks[k]=dict(xy=p,actual_RGBA=rgba,authority='Newly authored opaque252 surface pivot for this isolated offline trial, not a recovered bone, physical joint or center of mass.')
parts[0].update(source=fp,source_RGBA_sha256=hashlib.sha256(ni.tobytes()).hexdigest(),native_component_source_id=252,
 retention_index=pin(e),retained_member_byte_equal=True,actual_source_View_after_E=True,artist_surface_markers=newmarks,
 whole_kit_conversion_to_Rest_art_units=1.)
sources={}
for p in parts:
 assert pin(p['source']['path'])==p['source']
 im=Image.open(p['source']['path']).convert('RGBA');assert hashlib.sha256(im.tobytes()).hexdigest()==p['source_RGBA_sha256']
 for m in p['artist_surface_markers'].values():assert list(im.getpixel(tuple(m['xy'])))==m['actual_RGBA'] and m['actual_RGBA'][3]==255
 sources[p['part']]=im
assert sum(len(p['artist_surface_markers']) for p in parts)==18
ps={p['part']:p for p in parts}
def point(n,k):return vec(ps[n]['artist_surface_markers'][k]['xy'])

# Authored once before any solver or rendering. No results alter these values.
G=vec([250.,580.]);CROWN=131.;EXTENT=580.-CROWN;D=100.8/EXTENT
AMP=20.8;CYCLE=128.;LIFT=2.;BOB=4.;BRANCH={'near':-1,'far':1}
ORDER=['far_foot','far_shin','far_thigh','near_foot','near_shin','near_thigh','bodyrest_fixedaxe']
markers=write(C/'surface18-and-fixed-parameters-v001.json',dict(schema='Guard-Rest252-new4-old14-one-fixed-trial-v001',parts=parts,marker_count=18,
 old_Rest4_not_inherited=True,old_leg14_exact=True,source_RGBA_immutable=True,
 virtual_ground_artist=[250,580],visible_core_crown_y=CROWN,standing_extent_ART_DESIGN=EXTENT,
 standing_basis_authority='Author ground580 minus actual visible core crown131 gives449artunits. Virtual ground is a fixed design plane, not a physical measurement or legless alpha box.',
 final_display_standing_basis=100.8,fixed_global_display_scale=D,conversions={'Rest':1.,'Near_all3':.36,'Far_all3':.36},
 per_part_or_per_pose_rescale=False,author_root=newpoints['root'],draw_order_far_to_near=ORDER,
 root_authority='Opaque pelvis surface attachment pivot only; not measured COM or skeleton.',
 source_acceptance=False,TrialAllowed=False,FinalAccepted=False))
trajectory=write(C/'one-fixed-distance-trajectory-v001.json',dict(schema='Guard-Rest252-ownhip-C128-bob4-lift2-one-fixed-trial-v001',
 samples=[CYCLE*i/6 for i in range(6)],cycle_distance_world=128,step_distance_world=64,
 phase='P=positive_mod(d,128); h=(P>=64); u=(P-64*h)/64',
 stance='NEAR in half0, FAR in half1; opposite chain swings.',
 stance_midsole_x='own_hip.X + (20.8-41.6*u) displaypx',swing_midsole_x='own_hip.X + (-20.8+41.6*u) displaypx',
 stance_core_sole_y=0,swing_lift_display='2*sin(pi*u)^2',
 body_and_hips_up_display='4*sin(2*pi*d/128)^2; contacts0/64 no bob; passing32/96 up4',
 fixed_knee_branches=BRANCH,ground_plane_y=0,scale=D,standing_baseline=100.8,
 sampled_crown_height_range=[100.8,103.8],continuous_crown_height_range=[100.8,104.8],
 continuous_stance_dx_dd=-.65,
 movement_authority='Offline d values are authored sample labels, not movement receipts. Future runtime input must be actual accepted path; straight-X nominal .65 projection only. No native accepted-distance or footlock claim.',
 boot_pitch='Each original heel/toe line gives one fixed perboot angle; core sole alpha>=128 sets its lowest art point on author ground.',
 no_parameter_search=True,immutable_before_solver=True,TrialAllowed=False,FinalAccepted=False))
prerender=write(C/'pre-render-parameters-freeze-v001.json',dict(schema='Guard-one-fixed-trial-PRE-render-freeze-v001',
 markers=pin(markers),trajectory=pin(trajectory),script=pin(__file__),source7=[p['source'] for p in parts],
 parameter_revision_after_math_or_render=False,mathematical_reach_pending=True,new_images_rendered=False))

chains={};bounds={}
for side in ['near','far']:
 k=ps[side+'_thigh']['whole_kit_conversion_to_Rest_art_units']
 assert k==.36 and ps[side+'_shin']['whole_kit_conversion_to_Rest_art_units']==k and ps[side+'_foot']['whole_kit_conversion_to_Rest_art_units']==k
 H=point('bodyrest_fixedaxe',side+'_hip_socket')-G
 tp=point(side+'_thigh','hip');tq=point(side+'_thigh','knee');sp=point(side+'_shin','knee');sq=point(side+'_shin','ankle')
 fp0=point(side+'_foot','ankle');heel=point(side+'_foot','heel');toe=point(side+'_foot','toe');beta=-angle(toe-heel);M=rot(beta)
 yy,xx=np.where(np.array(sources[side+'_foot'])[:,:,3]>=128)
 fy=float(((np.stack([xx,yy],1)-fp0)@M.T*k)[:,1].max());mid=((heel+toe)/2-fp0)@M.T*k
 L1=float(np.linalg.norm(tq-tp)*k);L2=float(np.linalg.norm(sq-sp)*k)
 q=dict(k=k,H=H,tp=tp,tq=tq,sp=sp,sq=sq,fp=fp0,heel=heel,toe=toe,beta=beta,fy=fy,mid=mid,L1=L1,L2=L2);chains[side]=q
 # Conservative all-d bounds; no sampled-only claim of continuous reach.
 dxmax=AMP/D+abs(float(mid[0]));dybase=-fy-float(H[1]);dymin=dybase-LIFT/D;dymax=dybase+BOB/D
 lower=dymin;upper=math.hypot(dxmax,dymax)
 bounds[side]=dict(fixed_lengths_art=[L1,L2],dx_absolute_max_art=dxmax,dy_interval_art=[dymin,dymax],
  conservative_distance_lower_art=lower,conservative_distance_upper_art=upper,
  lower_reach_margin_display=(lower-abs(L1-L2))*D,upper_reach_margin_display=(L1+L2-upper)*D,
  continuous_strict_reach=(dymin>0 and lower>abs(L1-L2) and upper<L1+L2),
  authority='Triangle reach bound for ALL d: |dx|<=AMP/D+|midX| and dy in [base-LIFT/D,base+BOB/D]. Independent maxima deliberately conservative; fixed lengths never changed.')
reach=write(C/'continuous-reach-bound-before-render-v001.json',dict(schema='Guard-Rest252-fixed-parameters-continuous-reach-bound-v001',pre_render_freeze=pin(prerender),chains=bounds,
 continuous_reachable=all(v['continuous_strict_reach'] for v in bounds.values()),no_parameter_adjustments=True))
if not all(v['continuous_strict_reach'] for v in bounds.values()):
 write(C/'STOP-unreachable-no-media-v001.json',dict(reason='Continuous conservative reach could not be established; stop without stretch/clamp/search or images.',bounds=bounds,TrialAllowed=False))
 print(json.dumps(dict(stopped=True,reach=pin(reach),bounds=bounds),ensure_ascii=False,indent=2));raise SystemExit(0)

def solve(distance):
 P=distance%CYCLE;half=int(P>=64);u=(P-64*half)/64;bob=BOB*math.sin(2*math.pi*P/CYCLE)**2
 root=point('bodyrest_fixedaxe','root')-G-vec([0,bob/D])
 tr={'bodyrest_fixedaxe':dict(pivot=list(point('bodyrest_fixedaxe','root')),anchor=list(root),angle=0.,k=1.)};cs=[]
 for side in ['near','far']:
  q=chains[side];stance=(side=='near' and half==0) or (side=='far' and half==1)
  cx=AMP-2*AMP*u if stance else -AMP+2*AMP*u;lift=0. if stance else LIFT*math.sin(math.pi*u)**2
  H=q['H']-vec([0,bob/D]);T=vec([q['H'][0]+cx/D-q['mid'][0],-q['fy']-lift/D])
  V=T-H;dd=float(np.linalg.norm(V));upper=(q['L1']+q['L2']-dd)*D;lower=(dd-abs(q['L1']-q['L2']))*D
  assert upper>0 and lower>0,'Unreachable fixed chain: no stretch/clamp/search'
  U=V/dd;aa=(q['L1']**2-q['L2']**2+dd*dd)/(2*dd);hh=math.sqrt(q['L1']**2-aa*aa)
  K=H+aa*U+BRANCH[side]*hh*vec([-U[1],U[0]])
  v1=K-H;v2=T-K;cross=float(v1[0]*v2[1]-v1[1]*v2[0]);assert cross*BRANCH[side]<0
  errors=[abs(float(np.linalg.norm(v1))-q['L1']),abs(float(np.linalg.norm(v2))-q['L2'])];assert max(errors)<1e-9
  tr[side+'_thigh']=dict(pivot=list(q['tp']),anchor=list(H),angle=angle(v1)-angle(q['tq']-q['tp']),k=q['k'])
  tr[side+'_shin']=dict(pivot=list(q['sp']),anchor=list(K),angle=angle(v2)-angle(q['sq']-q['sp']),k=q['k'])
  tr[side+'_foot']=dict(pivot=list(q['fp']),anchor=list(T),angle=q['beta'],k=q['k'])
  cs.append(dict(side=side,stance=stance,hip_art=list(H),knee_art=list(K),ankle_art=list(T),own_hip_center_display=float(q['H'][0])*D,
   midsole_offset_from_own_hip_display=cx,core_sole_display_y=-lift,lift_display=lift,bob_up_display=bob,
   fixed_lengths_art=[q['L1'],q['L2']],length_errors=errors,branch=BRANCH[side],
   reach_upper_margin_display=upper,reach_lower_margin_display=lower,
   absolute_knee_flexion_degrees=abs(math.degrees(math.atan2(cross,float(v1@v2)))),
   vertical_hip_knee_ankle_order=bool(H[1]<K[1]<T[1])))
 return dict(authored_distance=distance,not_actual_movement_receipt=True,half=half,u=u,bob_up_display=bob,continuous_crown_height=100.8+bob,transforms=tr,chains=cs)

dense=[solve(128.*i/1024) for i in range(1024)];summary={}
for side in ['near','far']:
 cs=[next(c for c in p['chains'] if c['side']==side) for p in dense]
 summary[side]=dict(sample_count=len(cs),upper_margin_min_display=min(c['reach_upper_margin_display'] for c in cs),
  flexion_degrees_range=[min(c['absolute_knee_flexion_degrees'] for c in cs),max(c['absolute_knee_flexion_degrees'] for c in cs)],
  vertical_order_false_samples=sum(not c['vertical_hip_knee_ankle_order'] for c in cs),branch_flips=0,
  length_error_max=max(max(c['length_errors']) for c in cs))
poses=[solve(128.*i/6) for i in range(6)]

def raster(pose,size,origin,gain):
 result=Image.new('RGBA',size,(0,0,0,0));masks={};boxes={}
 for n in ORDER:
  t=pose['transforms'][n];M=rot(t['angle'])*(gain*t['k']);v=vec(origin)+gain*vec(t['anchor'])-M@vec(t['pivot']);inv=np.linalg.inv(M);z=-inv@v
  singular=np.linalg.svd(M,compute_uv=False);assert abs(singular[0]-singular[1])<1e-10
  layer=sources[n].transform(size,Image.Transform.AFFINE,tuple(inv[0])+tuple([z[0]])+tuple(inv[1])+tuple([z[1]]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
  box=layer.getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<size[0] and box[3]<size[1]
  masks[n]=np.array(layer)[:,:,3];boxes[n]=list(box);result.alpha_composite(layer)
 return result,masks,boxes

renders=C/'rendered';renders.mkdir();records=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
full=Image.new('RGB',(1980,1420),(35,35,40));fd=ImageDraw.Draw(full)
seams=Image.new('RGB',(2040,1080),(35,35,40));sd=ImageDraw.Draw(seams);gifs=[]
for i,p in enumerate(poses):
 big,masks,boxes=raster(p,(768,768),(384,650),1.)
 small,_,_=raster(p,(160,160),(80,136),D)
 bp=renders/f'phase-{i}-ARTUNIT768.png';sp=renders/f'phase-{i}-STANDING100p8-160.png';big.save(bp);small.save(sp)
 x=(i%3)*660;y=(i//3)*700;tile=small.resize((640,640),Image.Resampling.NEAREST);full.paste(tile,(x+10,y+40),tile)
 fd.text((x+10,y+5),f'{i}: d={p["authored_distance"]:.3f} bob={p["bob_up_display"]:.1f}px',font=font,fill='white')
 crop=big.crop((220,420,560,656)).resize((680,472),Image.Resampling.NEAREST)
 sx=(i%3)*680;sy=(i//3)*530;seams.paste(crop,(sx,sy+35),crop);sd.text((sx+8,sy+5),f'{i}: same leg region x2 nearest',font=font,fill='white')
 canvas=Image.new('RGB',(220,200),(35,35,40));canvas.paste(small,(30,30),small);gd=ImageDraw.Draw(canvas)
 gd.text((8,8),f'AUTHOR {i} d={p["authored_distance"]:.1f}',font=font,fill='white');gifs.append(canvas.resize((880,800),Image.Resampling.NEAREST))
 coverage=[]
 for c in p['chains']:
  side=c['side']
  for label,aa,bb in [('hip','bodyrest_fixedaxe',side+'_thigh'),('knee',side+'_thigh',side+'_shin'),('ankle',side+'_shin',side+'_foot')]:
   center=vec(c[label+'_art'])+[384,650];Y,X=np.ogrid[:768,:768];disk=(X-center[0])**2+(Y-center[1])**2<=36
   ma=masks[aa]>=128;mb=masks[bb]>=128;coverage.append(dict(side=side,seam=label,local_only=True,
    union_core_coverage=float(((ma|mb)&disk).sum()/disk.sum()),overlap_pixels=int((ma&mb&disk).sum())))
 records.append(dict(phase=i,distance=p['authored_distance'],big=pin(bp),actual_display=pin(sp),source_layer_bounds=boxes,local_cap_diagnostics_not_interface_acceptance=coverage))
fd.text((10,1400),'100.8 standing basis, sampled heights100.8/103.8; continuous bob peak104.8. Offline author trial only.',font=font,fill=(255,210,130))
fp=C/'six-phase-standing100p8-ownhip-bob4-x4-nearest-DIAGNOSTIC.png';full.save(fp)
sd.text((8,1060),'One fixed parameter set; source RGBA unchanged. Cap-point coverage is not whole-seam acceptance.',font=font,fill=(255,210,130))
cp=C/'six-phase-leg-seams-ARTUNIT-x2-nearest-DIAGNOSTIC.png';seams.save(cp)
gp=C/'six-author-phases-uniform100ms-NOT-native.gif';gifs[0].save(gp,save_all=True,append_images=gifs[1:],duration=[100]*6,loop=0,optimize=False,disposal=2)
assert all(pin(p['source']['path'])==p['source'] for p in parts)
proof=write(C/'one-limited-six-phase-author-trial-proof-v001.json',dict(schema='Guard-Rest252-one-fixed-seven-part-author-trial-v001',
 pre_render_freeze=pin(prerender),continuous_reach_bound=pin(reach),markers=pin(markers),trajectory=pin(trajectory),poses=poses,renders=records,dense1024_diagnostics=summary,
 source_provenance='Derived genuinely authored2D rig from native component252/250/251; no fabricated wholebodyMove NativeSourceId.',
 source7_file_and_RGBA_unchanged=True,per_pose_scale_or_limb_stretch=False,parameter_adjustment_after_math_or_render=False,
 nominal_stance_dx_dd=-.65,stance_world_ground_core_y=0,actual_accepted_distance_observed=False,
 standing_basis_height=100.8,six_sample_crown_heights=[p['continuous_crown_height'] for p in poses],continuous_crown_height_max=104.8,
 offline_GIF_frame_ms=[100]*6,offline_GIF_not_real_game_cycle=True,
 limitations=['Rest252 only shortened~7.5–8.2%, not requested20%; identity risk retained, source not admitted.',
 'Rigid fixed-axe torso moves vertically as one piece; dynamic crown rises4px rather than hidden perframe normalization.',
 'Only straight-X authored distance geometry. Blocking/turning/diagonalground, runtime facing mirror, acceptedPath input and stepaudio remain unverified.',
 'Fixedboot pitch and piece caps may look stiff, overlap, expose doubleink or leave full seams. Local disk coverage is not interface/footlock acceptance.',
 'Sixsamples miss exact passing peaks32/96; formula and dense math include4pxbob, six rendered noncontact samples use3pxbob.',
 'Offline rotations/resampling are derivative output; original7RGBA unchanged, not pixel-identical rendered pixels.'],
 mathematical_continuous_reach_bound_pass=True,new_media_View=False,TrialAllowed=False,NativeAccepted=False,footlock=False,MoveComplete=False,FinalAccepted=False))
doc=write(C/'distance-to-pose-handoff-PROPOSAL-v001.txt','''One isolated fixed author trial; no currentSource changes.

Future input d must be actual collision-resolved accepted path, never speed*time/input/drawclock. P=positive_mod(d,128), h=(P>=64), u=(P-64h)/64. Near stance in half0, Far in half1. Each foot is centered on its OWN authored hipX; stance relative midsoleX=20.8-41.6u, swing=-20.8+41.6u. Nominal straight-X stance derivative=-.65px/worldunit, algebraically cancels .65 ground projection; not observed footlock. Core sole groundY=0 for stance; swing lift2*sin(piu)^2. BodyRest and both hips translate upward4*sin(2pi*d/128)^2 displaypx. Fixed branches Near-1/Far+1, fixed source two-axis lengths, kit.36 for all3 each, one fixed display scale100.8/449. No reach clamp, part scaling, actorXY mutation or postcapture parameter search.

Author ground[250,580], visible core crown131, static standing extent449→100.8. Continuous dynamic crown height reaches104.8; six sample crown heights are100.8 or103.8. Six100ms GIF is an offline inspection convenience, not a600ms game clock claim. New Rest four opaque authored points are not inherited bone/joint measurements. Source identity drift and missed0.8 compact-torso target remain unapproved. Review new retained images before any future native policy choice.
''')
freeze=write(C/'limited-author-trial-output-freeze-v001.json',dict(schema='Guard-Rest252-one-trial-output-freeze-v001',files=[pin(p) for p in sorted(C.rglob('*')) if p.is_file()],new_media_View=False,TrialAllowed=False,FinalAccepted=False))
(B/'原件').mkdir(parents=True);shutil.copytree(C,B/'原件/一次有限试拼完整包');(B/'原件/七件源原图').mkdir()
for p in parts:shutil.copy2(p['source']['path'],B/f"原件/七件源原图/{p['part']}.png")
(B/'展示副本').mkdir()
for p in [fp,cp,gp,*sorted(renders.iterdir())]:shutil.copy2(p,B/'展示副本'/p.name)
for _ in range(2):
 for p in C.rglob('*'):
  if p.is_file():assert rb(p)==rb(B/'原件/一次有限试拼完整包'/p.relative_to(C))
 for p in parts:assert rb(p['source']['path'])==rb(B/f"原件/七件源原图/{p['part']}.png")
 for p in [fp,cp,gp,*sorted(renders.iterdir())]:assert rb(p)==rb(B/'展示副本'/p.name)
write(B/'source-version-status-index.json',dict(schema='F-Guard-Rest252-one-limited-author-trial-status-v001',proof=pin(proof),freeze=pin(freeze),pre_render_freeze=pin(prerender),native_formula=pin(doc),
 files=[pin(p) for p in sorted(B.rglob('*')) if p.is_file()],verification_passes=2,canonical_copy_mismatches=0,
 status='NEW_MEDIA_UNVIEWED_PENDING_ROOT_E; one fixed parameter trial only, no source/native/footlock/Move acceptance.',Root_E_retention_pending=True,new_media_View=False,TrialAllowed=False,FinalAccepted=False))
print(json.dumps(dict(F_batch=B.as_posix(),proof=pin(proof),output_freeze=pin(freeze),pre_render_freeze=pin(prerender),continuous_bound=bounds,dense=summary,new_media_viewed=False),ensure_ascii=False,indent=2))
