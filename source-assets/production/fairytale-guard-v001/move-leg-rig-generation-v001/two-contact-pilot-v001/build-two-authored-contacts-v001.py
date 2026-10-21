"""Seven source parts, eighteen ARTIST surface markers, two static IK contacts.
No engine/physics/input calls. This is a genuine authored2D rig pilot, not Move6.
"""
from pathlib import Path
import hashlib,json,math,shutil,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path('F:/Ourgame');O=ROOT/'source-assets/production/fairytale-guard-v001/move-leg-rig-generation-v001';OUT=Path(__file__).resolve().parent
MEDIA=ROOT/'过程图稿与视频/2026-10-18_裂岩守卫七组件18作者点两相反触地试拼_v001'
assert not MEDIA.exists() and not (OUT/'surface-markers-and-fixed-conversions-v001.json').exists()
def data(p):return Path('\\\\?\\'+str(Path(p).resolve())).read_bytes()
def pin(p):
 b=data(p);return dict(path=Path(p).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(data(p).decode('utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def rotation(theta):return np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
def vec(x):return np.array(x,dtype=float)
def angle(v):return math.atan2(v[1],v[0])

specs=[
 ('bodyrest_fixedaxe','rest1-extraction-v001/run-rest249-shared-HD-v001',0,249,{'root':[252,419],'crown':[254,132],'near_hip_socket':[216,420],'far_hip_socket':[284,416]},'v549'),
 ('near_thigh','near250-extraction-v001/run-near250-threeparts-shared-HD-v001',0,250,{'hip':[280,126],'knee':[214,389]},'v553'),
 ('near_shin','near250-extraction-v001/run-near250-threeparts-shared-HD-v001',1,250,{'knee':[268,184],'ankle':[260,400]},'v553'),
 ('near_foot','near250-extraction-v001/run-near250-threeparts-shared-HD-v001',2,250,{'ankle':[216,294],'heel':[108,445],'toe':[420,445]},'v553'),
 ('far_thigh','far251-extraction-v001/run-far251-threeparts-shared-HD-v001',0,251,{'hip':[263,124],'knee':[228,389]},'v556'),
 ('far_shin','far251-extraction-v001/run-far251-threeparts-shared-HD-v001',1,251,{'knee':[237,193],'ankle':[267,407]},'v556'),
 ('far_foot','far251-extraction-v001/run-far251-threeparts-shared-HD-v001',2,251,{'ankle':[220,258],'heel':[105,430],'toe':[418,442]},'v556')]
sources={};parts=[];retention_paths={
 'v549':'2026-10-18-OurgameUE-GuardMoveRest249-extraction-v549',
 'v553':'2026-10-18-OurgameUE-GuardMoveNear250-extraction-v553',
 'v556':'2026-10-18-OurgameUE-GuardMoveFar251-extraction-v556'}
for name,run,i,native,points,retid in specs:
 p=O/run/f'curated/frame-{i}.png';im=Image.open(p).convert('RGBA');assert im.size==(512,512)
 e=Path('E:/OurGame/Knight/过程图稿与视频')/retention_paths[retid]/'E-retention-index-v001.json';er=load(e)
 assert er['verification_passes']==2 and er['source_and_member_hash_mismatches']==0
 fp=pin(p);m=next(x for x in er['files'] if x['bytes']==fp['bytes'] and x['sha256']==fp['sha256'])
 with zipfile.ZipFile(er['packet']['path']) as z:assert z.read(m['member'])==data(p)
 marks={}
 for label,xy in points.items():
  color=list(im.getpixel(tuple(xy)));assert color[3]==255,(name,label,color)
  marks[label]=dict(xy=xy,actual_RGBA=color,authority='Hand-authored visible opaque cap/plate/sole surface point; not recovered bone/physical joint.')
 sources[name]=dict(im=im,points=points,k=1. if name=='bodyrest_fixedaxe' else .36)
 parts.append(dict(part=name,source=fp,source_RGBA_sha256=hashlib.sha256(im.tobytes()).hexdigest(),native_component_source_id=native,retention_index=pin(e),retained_member_byte_equal=True,actual_source_View_after_E=True,
  artist_surface_markers=marks,whole_kit_conversion_to_Rest_art_units=sources[name]['k']))
assert sum(len(p['artist_surface_markers']) for p in parts)==18

# These values are authored and frozen BEFORE rendering. No image/search feedback.
GROUND=vec([252,580]);CROWN_CORE=125;EXTENT=455.;DISPLAY=100.8/EXTENT;HALF_CONTACT=20.8
ORDER=['far_foot','far_shin','far_thigh','near_foot','near_shin','near_thigh','bodyrest_fixedaxe']
marker_path=write(OUT/'surface-markers-and-fixed-conversions-v001.json',dict(
 schema='Guard-seven-component-eighteen-ARTIST-surface-markers-PROPOSAL-v001',parts=parts,marker_count=18,
 Rest_units=1.,Near_whole_threepart_conversion=.36,Far_whole_threepart_conversion=.36,
 kit_conversion_authority='Artist fixed whole-kit proposal, not measured shared native illustration density. One value for ALL3 parts in each kit and bothposes; no perpart/perpose scale.',
 display_scale=DISPLAY,body_height_target=100.8,body_crown_core_y=CROWN_CORE,virtual_ground_in_Rest_source=list(GROUND),
 standing_equivalent_art_extent_ART_DESIGN=EXTENT,standing_extent_authority='455 is authored ground580 minus actual visible crown125. It is a proposed assembly design extent, not legless339bbox, measured anatomy or certified standing/physical scale.',
 hierarchy='GroundRoot -> opaque BodyRest.root; its distinctNear/Far authored sockets -> respective thigh -> shin -> foot.',
 draw_order_far_to_near=ORDER,
 static_body_root_same_in_bothposes=True,source_pixels_immutable=True,rig_transform='Deterministic uniform-scale+rotation+translation only; rendered AA changes are not claimed pixel-exact source copies.',
 knee_branch=-1,foot_orientation='One fixed perfoot angle authored from opaque heel/toe markers; same in bothposes.',
 contact_local_x_display=[HALF_CONTACT,-HALF_CONTACT],cycle_distance_world_ART_CONTRACT=128,contact_sample_distances=[0,64],nominal_projection_x_per_world=.65,
 movement_authority='These are TWO AUTHORED test samples, not actual acceptedMovement receipts or native movement proof. No speed*time or input/clock mutation. Future phase must consume actual collision-resolved path.',
 sources_reviewed_only_as_component_candidates=True,physical_density_measured=False,interface_fit_accepted=False,TrialAllowed=False,footlock_or_Move6_or_FinalAccepted=False))

def make_chain(side,front):
 thigh=sources[side+'_thigh'];shin=sources[side+'_shin'];foot=sources[side+'_foot'];k=thigh['k']
 assert shin['k']==foot['k']==k
 H=vec(sources['bodyrest_fixedaxe']['points'][side+'_hip_socket'])-GROUND
 u0=vec(thigh['points']['hip']);u1=vec(thigh['points']['knee']);s0=vec(shin['points']['knee']);s1=vec(shin['points']['ankle'])
 f0=vec(foot['points']['ankle']);heel=vec(foot['points']['heel']);toe=vec(foot['points']['toe'])
 beta=-angle(toe-heel);M=rotation(beta);yy,xx=np.where(np.array(foot['im'])[:,:,3]>=128)
 projected=(np.stack([xx,yy],1)-f0)@M.T*k;lowest=float(projected[:,1].max());mid=((heel+toe)/2-f0)@M.T*k
 contact_x=HALF_CONTACT if front else -HALF_CONTACT;T=vec([contact_x/DISPLAY-mid[0],-lowest])
 L1=float(np.linalg.norm(u1-u0)*k);L2=float(np.linalg.norm(s1-s0)*k);V=T-H;D=float(np.linalg.norm(V))
 assert abs(L1-L2)<D<L1+L2,'Unreachable authored contact; no stretch fallback'
 unit=V/D;a=(L1*L1-L2*L2+D*D)/(2*D);h=math.sqrt(L1*L1-a*a);K=H+a*unit-h*vec([-unit[1],unit[0]])
 assert H[1]<K[1]<T[1],'Source surface-axis bend inverted; reject rather than search perpose'
 errors=[abs(float(np.linalg.norm(K-H))-L1),abs(float(np.linalg.norm(T-K))-L2)]
 assert max(errors)<1e-9
 transforms={side+'_thigh':dict(pivot=list(u0),anchor=list(H),rotation_radians=angle(K-H)-angle(u1-u0),conversion=k),
  side+'_shin':dict(pivot=list(s0),anchor=list(K),rotation_radians=angle(T-K)-angle(s1-s0),conversion=k),
  side+'_foot':dict(pivot=list(f0),anchor=list(T),rotation_radians=beta,conversion=k)}
 heelpos=T+(heel-f0)@M.T*k;toepos=T+(toe-f0)@M.T*k
 return transforms,dict(side=side,leading=front,hip=list(H),knee=list(K),ankle=list(T),fixed_lengths_art_units=[L1,L2],measured_pose_lengths_art_units=[float(np.linalg.norm(K-H)),float(np.linalg.norm(T-K))],
  length_abs_errors=errors,reach_margin_display=(L1+L2-D)*DISPLAY,heel_display=list(heelpos*DISPLAY),toe_display=list(toepos*DISPLAY),
  opaque_core_sole_lowest_display_y=0.,heel_toe_points_not_both_floor=True,foot_rotation_radians=beta,contact_midsole_display_x=contact_x)

poses=[]
for distance in [0,64]:
 n,nproof=make_chain('near',distance==0);f,fproof=make_chain('far',distance==64)
 tr={**f,**n,'bodyrest_fixedaxe':dict(pivot=[252,419],anchor=list(vec([252,419])-GROUND),rotation_radians=0.,conversion=1.)}
 poses.append(dict(authored_distance_sample=distance,not_actual_movement_receipt=True,transforms=tr,chains=[nproof,fproof]))

def raster(pose,size,origin,gain):
 result=Image.new('RGBA',size,(0,0,0,0));masks={};bounds={}
 for name in ORDER:
  t=pose['transforms'][name];M=rotation(t['rotation_radians'])*(gain*t['conversion']);translation=vec(origin)+gain*vec(t['anchor'])-M@vec(t['pivot']);inv=np.linalg.inv(M);q=-inv@translation
  assert abs(np.linalg.svd(M,compute_uv=False)[0]-np.linalg.svd(M,compute_uv=False)[1])<1e-10
  layer=sources[name]['im'].transform(size,Image.Transform.AFFINE,tuple(inv[0])+tuple([q[0]])+tuple(inv[1])+tuple([q[1]]),resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
  bounds[name]=list(layer.getbbox());masks[name]=np.array(layer)[:,:,3];result.alpha_composite(layer)
  b=bounds[name];assert b[0]>0 and b[1]>0 and b[2]<size[0] and b[3]<size[1],'Pilot canvas clips source'
 return result,masks,bounds

renders=OUT/'rendered';renders.mkdir();proofs=[]
for pose in poses:
 dist=pose['authored_distance_sample'];big,masks,bounds=raster(pose,(768,768),(384,650),1.)
 small,_,_=raster(pose,(160,160),(80,132),DISPLAY)
 bp=renders/f'contact-{dist:03d}-ARTUNIT768.png';sp=renders/f'contact-{dist:03d}-DISPLAY100p8-160.png';big.save(bp);small.save(sp)
 # Diagnostic cap union at the authored surface seam, not footlock certification.
 coverage=[]
 for side in ['near','far']:
  chain=next(c for c in pose['chains'] if c['side']==side)
  for label,a,b in [('hip','bodyrest_fixedaxe',side+'_thigh'),('knee',side+'_thigh',side+'_shin'),('ankle',side+'_shin',side+'_foot')]:
   center=vec(chain[label])+[384,650];Y,X=np.ogrid[:768,:768];disk=(X-center[0])**2+(Y-center[1])**2<=6**2
   ma=masks[a]>=128;mb=masks[b]>=128
   coverage.append(dict(side=side,seam=label,diagnostic_radius_art_units=6,union_core_coverage=float(((ma|mb)&disk).sum()/disk.sum()),both_core_overlap_pixels=int((ma&mb&disk).sum())))
 proofs.append(dict(distance=dist,source_artunit_render=pin(bp),actual100p8_render=pin(sp),layer_bounds=bounds,seam_diagnostics=coverage))

# Small reading plates are diagnostics only, never substitute source art.
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
plate=Image.new('RGB',(1340,720),(35,35,40));draw=ImageDraw.Draw(plate)
for i,pose in enumerate(poses):
 dist=pose['authored_distance_sample'];small=Image.open(renders/f'contact-{dist:03d}-DISPLAY100p8-160.png').resize((640,640),Image.Resampling.NEAREST)
 plate.paste(small,(20+i*660,56),small);draw.text((20+i*660,15),f'AUTHORED distance {dist}: '+('NEAR leads' if dist==0 else 'FAR leads'),font=font,fill='white')
draw.text((20,695),'Two static IK samples only; 100.8 display height shown x4 nearest. No native / footlock / Move6 acceptance.',font=font,fill=(255,210,130))
pp=OUT/'two-contact-100p8-display-x4-nearest-DIAGNOSTIC.png';plate.save(pp)
markerplate=Image.new('RGB',(2048,1100),(35,35,40));md=ImageDraw.Draw(markerplate)
for i,p in enumerate(parts):
 name=p['part'];tile=sources[name]['im'].copy();dd=ImageDraw.Draw(tile)
 for j,(label,m) in enumerate(p['artist_surface_markers'].items()):
  x,y=m['xy'];dd.ellipse((x-5,y-5,x+5,y+5),fill=(255,40,50,255),outline=(255,255,255,255),width=1);dd.text((x+7,y-8),label,font=font,fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
 x=(i%4)*512;y=40+(i//4)*530;markerplate.paste(tile,(x,y),tile);md.text((x+10,y-25),name,font=font,fill='white')
mp=OUT/'18-ARTIST-opaque-surface-points-DIAGNOSTIC.png';markerplate.save(mp)
near0=next(c for c in poses[0]['chains'] if c['side']=='near');near64=next(c for c in poses[1]['chains'] if c['side']=='near')
# Only an algebraic two-sample anchor relation, not observed movement.
anchor_delta=near64['contact_midsole_display_x']+64*.65-near0['contact_midsole_display_x']
result=write(OUT/'two-authored-contact-poses-and-proof-v001.json',dict(schema='Guard-two-static-rigged-contact-pilot-v001',markers_and_fixed_parameters=pin(marker_path),poses=poses,renders=proofs,
  near_two_sample_nominal_world_anchor_delta_x=anchor_delta,anchor_authority='Algebraic author-sample relation under nominal xprojection. No actualacceptedMovement receipt, intervening swing/stance, turning or collision test.',
  mathematical_fixed_length_and_uniform_scale_checks_pass=True,source_RGBA_inputs_unchanged=True,no_native_generation=True,near_foreground_even_when_trailing=True,
  old_full57_and_partial_contracts_unchanged=True,no_fabricated_wholebody_native_source_id=True,
  risks=['Far rear reach margin only about0.915display; fullcycle/turnreach not proven.','Near rear lower-axis almost horizontal; silhouette must be visually assessed.','Joint-cap simple overlap may show doubleink/bulges; cap union diagnostics are not a visiblefit acceptance.','Rest virtual455design extent and fixedkit.36 are artist density proposals; proportional match to Ready not certified.','Staticfixedupperbody can appear stiff; no bob/turn/swing animation fabricated.','Actual two opposite legs and layerdepth remain E-retained visual review gates.'],
  new_media_View=False,ActualMovementProof=False,InterfaceFitAccepted=False,TrialAllowed=False,FinalAccepted=False,footlock=False,Move6=False))
write(OUT/'HANDOFF.md','Seven actualretained sources/18 opaque255 ARTIST surface points. Rest1 unit; Near3 all.36 andFar3 all.36; display100.8/455.455 is virtualground580 minusvisiblecrown125 ARTdesign, not leglessbbox/physicalstanding measurement. Eachpart uses only deterministicuniformscale/rotation/translation; bothfixedchains mathematicallyreach twoauthoredcontact samples0/64. Body/hips fixed, branch-1 fixed, Nearforeground evenwhenback. SourceRGBA immutable. No actualMovement/native/footlock/Move6 or interfacefit acceptance. Farrear reachmargin~.915px andNearrear nearlyhorizontalshin are explicitrisks. NEW images unviewed pending RootE; evaluate real artwork before extending anything.\n')
freeze=write(OUT/'two-contact-pilot-freeze-v001.json',dict(schema='Guard-two-static-contact-pilot-freeze-v001',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],new_media_View=False,TrialAllowed=False))
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/两触地试拼完整包');(MEDIA/'原件/七件源原图').mkdir()
for p in parts:shutil.copy2(p['source']['path'],MEDIA/f"原件/七件源原图/{p['part']}.png")
(MEDIA/'展示副本').mkdir();shutil.copy2(pp,MEDIA/'展示副本'/pp.name);shutil.copy2(mp,MEDIA/'展示副本'/mp.name)
for p in renders.iterdir():shutil.copy2(p,MEDIA/'展示副本'/p.name)
write(MEDIA/'source-version-status-index.json',dict(schema='F-dated-source-version-status-v001',markers=pin(marker_path),proof=pin(result),freeze=pin(freeze),files=[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()],status='Twoauthoredstaticrigcontacts only; NEWmedia pendingRootEbeforeView, no completeMove6/native/footlock.',Root_E_retention_pending=True,new_media_View=False))
print(json.dumps(dict(F_batch=MEDIA.as_posix(),markers=pin(marker_path),proof=pin(result),freeze=pin(freeze),display_scale=DISPLAY,kit_conversion=.36,
  near_nominal_anchor_delta=anchor_delta,reach_margins_display=[dict(distance=p['authored_distance_sample'],chains=[dict(side=c['side'],margin=c['reach_margin_display']) for c in p['chains']]) for p in poses],seam_diagnostics=[p['seam_diagnostics'] for p in proofs],new_images_viewed=False),ensure_ascii=False,indent=2))
