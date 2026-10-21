from pathlib import Path
import hashlib,json,math,re,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

ROOT=Path('F:/Ourgame'); BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'; HERE=Path(__file__).resolve().parent
OUT=HERE/'own-partition-SWD-fit-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge218自身五分区军剑持握候选_v001'
assert not OUT.exists() and not MEDIA.exists(); OUT.mkdir()
SWORD=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
READY=ROOT/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
READY_MARKERS=ROOT/'source-assets/production/fairytale-sword-v001/ready-measurement-v002/ready-marker-proposal-v002.json'
OLD_REG=BASE/'hero218-220-extraction-v001/visible-registration-proposal-v001/visible-crown-shoe-support-glove-proposals-v001.json'
AUDIT=HERE/'source-retention-audit-v001.json'
K=72./416.; CANVAS=512*K; SCALE=.50; SOURCE_GRIP=np.array([99.,256.])
def pin(p):
 b=p.read_bytes(); return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel; p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,im):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);im.save(p);return p
def bbox(m):
 y,x=np.where(m);return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def poly_mask(p):
 m=Image.new('L',(512,512),0);ImageDraw.Draw(m).polygon([tuple(q) for q in p],fill=255);return np.array(m)>0
def rigid_sword(grip,axis):
 angle=math.atan2(axis[1],axis[0]);c,s=math.cos(angle),math.sin(angle);g=np.array(grip,float)
 aff=(c/SCALE,s/SCALE,float(SOURCE_GRIP[0]-(c*g[0]+s*g[1])/SCALE),-s/SCALE,c/SCALE,float(SOURCE_GRIP[1]-(-s*g[0]+c*g[1])/SCALE))
 im=sword.convert('RGBa').transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
 def tp(q):return (g+SCALE*np.array([[c,-s],[s,c]])@(np.array(q,float)-SOURCE_GRIP)).tolist()
 assert np.allclose(tp([99,256]),g);return im,aff,math.degrees(angle),tp
def place(im,root,out=(1280,720),ground=(640,490),k=K):
 aff=(1/k,0.,float(root[0]-ground[0]/k),0.,1/k,float(root[1]-ground[1]/k))
 return im.convert('RGBa').transform(out,Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
def measure_sole(a,roi,t=128):
 x0,y0,x1,y1=roi;v=a[y0:y1,x0:x1,3];yy,xx=np.where(v>=t);bottom=int(yy.max()+y0)
 band=a[bottom-3:bottom+1,x0:x1,3].astype(float);band[band<t]=0;weights=band.sum(axis=0)
 cx=float(np.dot(weights,np.arange(x0,x1))/weights.sum());xs=np.where(weights>0)[0]+x0
 return {'artist_ROI':roi,'alpha_threshold':t,'actual_bottom_y':bottom,'floor_edge_y':bottom+1,'bottom4_alpha_weighted_centroid_x':cx,'actual_bottom_band_xrange':[int(xs.min()),int(xs.max())],'horizontal_ROI_clear':bool(xs.min()>x0 and xs.max()<x1-1),'actual_edge_pixel_xy':[round(cx),bottom],'actual_edge_RGBA':a[bottom,round(cx)].tolist()}

audit=read(AUDIT); old_rows=[r for r in read(OLD_REG)['frames'] if r['state']=='dodge']; assert len(old_rows)==4
E422=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v422'))
idx=read(E422/'source-size-SHA256.json')
for p,sha in [(SWORD,'2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'),(READY,'d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5')]:
 assert pin(p)['sha256']==sha
 rr=next(r for r in idx['files'] if r['sha256']==sha);e=E422/rr['retained_relative']
 for _ in range(2):assert p.read_bytes()==e.read_bytes() and pin(p)['sha256']==pin(e)['sha256']
sword=Image.open(SWORD).convert('RGBA');sa=np.array(sword);yy,xx=np.indices((512,512))
guard_source=(sa[:,:,3]>0)&(xx>=134)&(xx<159)&(yy>=210)&(yy<303)

# Artist-visible boundaries authored on these four Dodge218 originals only.
# The polygons select original pixels. They neither invent a hidden surface nor paint a correction.
SEEDS=[
 {'grip':[184,300],'axis':[.8,.6],'wrist':[125,248,160,287],
  'NearHand':[[159,270],[173,267],[191,273],[207,279],[220,292],[229,305],[218,318],[199,325],[180,324],[163,314],[152,298],[150,283]],
  'NearArmWithoutHand':[[166,229],[196,222],[217,233],[221,253],[203,270],[176,284],[144,285],[130,269],[128,250],[139,237]],
  'HelmetForeground':[[0,0],[512,0],[512,260],[371,260],[347,266],[315,261],[285,250],[264,238],[242,229],[216,219],[188,211],[173,202],[0,202]],
  'FarHandForeground':[[341,281],[365,268],[394,269],[408,280],[418,296],[413,313],[396,317],[378,311],[357,320],[335,315],[321,304],[324,287]]},
 {'grip':[145,319],'axis':[.88,.475],'wrist':[107,264,140,299],
  'NearHand':[[117,289],[137,284],[155,287],[171,299],[181,317],[178,333],[160,342],[134,342],[114,334],[106,321],[106,304]],
  'NearArmWithoutHand':[[136,257],[173,258],[194,270],[191,291],[175,302],[151,309],[117,306],[104,288],[110,272]],
  'HelmetForeground':[[0,0],[512,0],[512,325],[406,325],[400,342],[376,352],[343,350],[300,335],[252,310],[210,281],[183,259],[182,240],[0,240]],
  'FarHandForeground':[[350,385],[372,373],[396,372],[414,385],[424,403],[417,420],[402,426],[382,419],[363,432],[343,426],[328,414],[329,399]]},
 {'grip':[144,300],'axis':[.94,.341],'wrist':[105,248,129,280],
  'NearHand':[[114,269],[137,265],[157,270],[172,281],[181,301],[177,315],[161,324],[139,325],[118,320],[107,309],[104,291]],
  'NearArmWithoutHand':[[135,239],[168,242],[188,252],[198,272],[182,290],[159,303],[122,296],[104,278],[102,261],[113,247]],
  'HelmetForeground':[[0,0],[512,0],[512,271],[394,271],[381,291],[361,304],[336,299],[305,289],[274,272],[245,255],[208,239],[179,225],[165,214],[0,214]],
  'FarHandForeground':[[354,300],[372,285],[401,282],[421,294],[435,310],[431,327],[411,334],[390,327],[370,338],[349,336],[332,324],[333,308]]},
 {'grip':[176,296],'axis':[.96,-.28],'wrist':[118,247,147,282],
  'NearHand':[[147,267],[161,260],[179,262],[194,270],[203,280],[209,288],[207,299],[199,307],[185,315],[167,317],[151,309],[140,301],[135,289],[136,277]],
  'NearArmWithoutHand':[[160,231],[190,235],[207,251],[209,268],[196,283],[167,298],[133,296],[119,278],[120,259],[133,244]],
  'HelmetForeground':[[0,0],[512,0],[512,222],[369,222],[355,239],[332,248],[308,245],[278,233],[250,217],[219,202],[189,193],[165,184],[156,170],[0,170]],
  'FarHandForeground':[[338,272],[357,255],[380,255],[399,266],[411,283],[407,300],[388,306],[368,300],[349,311],[329,309],[315,297],[316,282]]}
]
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground']
PRIORITY=['NearHand','FarHandForeground','HelmetForeground','NearArmWithoutHand']
COLORS={'BodyRest':(150,150,150),'NearArmWithoutHand':(230,95,100),'HelmetForeground':(235,205,85),'NearHand':(95,215,160),'FarHandForeground':(100,155,245)}
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
rows=[];wholes=[];roots=[];displays=[];owner_panels=[]
for i,se in enumerate(SEEDS):
 p=Path(audit['curated4'][i]['F']['path']);e=Path(audit['curated4'][i]['E']['path']);assert pin(p)==audit['curated4'][i]['F'] and p.read_bytes()==e.read_bytes()
 a=np.array(Image.open(p).convert('RGBA'));alive=a[:,:,3]>0;claimed=np.zeros((512,512),bool);masks={};layers={};layerpins={};maskpins={}
 for owner in PRIORITY:
  m=poly_mask(se[owner])&alive&~claimed;claimed|=m;masks[owner]=m
 masks['BodyRest']=~claimed
 for owner in OWNERS:
  m=masks[owner];v=np.where(m[:,:,None],a,0).astype(np.uint8);layers[owner]=v
  layerpins[owner]=pin(save(f'body-layers/{owner}/frame-{i}.png',Image.fromarray(v)))
  maskpins[owner]=pin(save(f'masks/{owner}/frame-{i}-mask-L.png',Image.fromarray(np.where(m&alive,255,0).astype(np.uint8))))
 occup=np.stack([v[:,:,3]>0 for v in layers.values()]).sum(axis=0)
 recon=np.stack([v.astype(np.uint16) for v in layers.values()]).sum(axis=0)
 assert np.array_equal(recon,a) and np.all(occup[alive]==1) and not np.any(occup[~alive])
 assert np.count_nonzero(layers['BodyRest'][:,:,3])<np.count_nonzero(alive)
 gx,gy=se['grip'];assert masks['NearHand'][gy,gx] and a[gy,gx,3]>=192
 swd,aff,deg,tp=rigid_sword(se['grip'],se['axis']);swd_a=np.array(swd);sword_mask=swd_a[:,:,3]>0
 assert not any(np.any(sword_mask[z]) for z in [0,-1]) and not sword_mask[:,0].any() and not sword_mask[:,-1].any()
 base=Image.new('RGBA',(512,512))
 for owner in ['BodyRest','NearArmWithoutHand','HelmetForeground']:base=Image.alpha_composite(base,Image.fromarray(layers[owner]))
 whole=Image.alpha_composite(base,swd)
 for owner in ['FarHandForeground','NearHand']:whole=Image.alpha_composite(whole,Image.fromarray(layers[owner]))
 w=np.array(whole);outside=~sword_mask;changed_outside=int(np.count_nonzero(np.any(w[outside]!=a[outside],axis=1)));assert changed_outside==0
 root=old_rows[i]['display_root_from_paired_visible_shoes_PROPOSAL_ONLY'];roots.append(root)
 soles=[]
 for old in old_rows[i]['visible_shoes']:
  ms=measure_sole(a,old['artist_ROI_xyxy']);expected=old['actual_alpha128_measurement'];assert abs(ms['bottom4_alpha_weighted_centroid_x']-expected['bottom4row_alpha_centroid_x'])<1e-12 and ms['floor_edge_y']==expected['floor_edge_y_proposal'];soles.append(ms)
 guard=np.array(Image.fromarray((guard_source*255).astype(np.uint8)).transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.NEAREST))>0
 x0,y0,x1,y1=se['wrist'];wr=np.zeros((512,512),bool);wr[y0:y1,x0:x1]=True
 guard_wrist=int(np.count_nonzero(guard&wr&(a[:,:,3]>=128)))
 sp=save(f'sword-layers/frame-{i}-SWD-rigid050.png',swd);cp=save(f'composites/frame-{i}-Dodge218-SWD-held-candidate.png',whole)
 unit=np.array([math.cos(math.radians(deg)),math.sin(math.radians(deg))]);g=np.array(se['grip'],float)
 hits=[]
 for t in np.arange(-100.,100.25,.25):
  q=g+t*unit;x,y=np.rint(q).astype(int)
  if 0<=x<512 and 0<=y<512 and masks['NearHand'][y,x]:hits.append(float(t))
 hand_alpha_overlap=int(np.count_nonzero(sword_mask&masks['NearHand']));tip=tp([482,256]);body_bbox=bbox(a[:,:,3]>=128)
 eyes=(a[:,:,3]>=128)&(a[:,:,0]>220)&(a[:,:,1]>90)&(a[:,:,1]<230)&(a[:,:,2]<65)&(a[:,:,0]>a[:,:,1]+35)&(yy>=120)&(yy<350)
 ey,ex=np.where(eyes);eye=[float(ex.mean()),float(ey.mean())]
 row={'frame':i,'source':pin(p),'source_native_id':218,'body_RGBA_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'body_layers':layerpins,'masks':maskpins,
  'source_owned_partition':{'owners':OWNERS,'artist_visible_polygon_by_owner':{o:se[o] for o in PRIORITY},'priority_for_exclusive_ownership':PRIORITY+['BodyRest_remaining_original_pixels'],'core_or_edge_alpha_dilated':False,'whole_body_used_as_BodyRest':False,'each_original_RGBA_reconstructs_exact':True,'nontransparent_pixels_all_exactly_one_owner':True,'owner_alpha_pixel_counts':{o:int(np.count_nonzero(layers[o][:,:,3])) for o in OWNERS},'semantic_boundary_status':'Artist visible boundary candidate, requires E-retained actual partition review. No new surface, hidden body, gray lining, local erase/redraw, fill, Ready/Hurt mask reuse or skeleton inference.'},
  'ground_registration':{'original_visible_registration':pin(OLD_REG),'Root_proposal_xy':root,'independent_actual_paired_shoes':soles,'actual_pairedsole_midpoint_x':sum(z['bottom4_alpha_weighted_centroid_x'] for z in soles)/2.,'standing_basis_source_height':416,'display_body_height':72,'constant_row_canvas_display_px':CANVAS,'natural_body_core_bbox':body_bbox,'natural_body_display_extent_px':(body_bbox[3]-body_bbox[1])*K,'perframe_height_normalized':False,'uncertainty_source_px':2,'physical_bone_COM_footlock':False},
  'author_binding':{'Grip_xy':se['grip'],'actual_source_grip_pixel_RGBA':a[gy,gx].tolist(),'Axis_xy':se['axis'],'unit_axis_xy':unit.tolist(),'angle_degrees':deg,'Axis_authority':'Artist-selected coherent blade hold direction. Source bare fist has no visible shaft; NOT measured handle, wrist bone or rig axis.','independent_sword':pin(SWORD),'independent_source_Grip':[99,256],'weapon_scale_all_four':SCALE,'inverse_affine':list(aff),'sword_layer':pin(sp),'sword_alpha_bbox':bbox(sword_mask),'sword_canvas_clipped':False,'actual_source_mask_axis_intersection_extremes_xy':[(g+min(hits)*unit).tolist(),(g+max(hits)*unit).tolist()],'axis_intersection_not_measured_emergence':True,'sword_alpha_pixels_covered_by_actual_nearhand':hand_alpha_overlap,'artist_wrist_ROI':se['wrist'],'actual_guard_ROI_core_overlap_pixels':guard_wrist,'guard_overlap_is_diagnostic_only':True,'tip_reference_xy':tip,'tip_above_artist_floor_source_px':root[1]-tip[1]},
  'visible_eye_pixel_centroid_xy':eye,'SWD_composite':pin(cp),'SWD_source_review_accepted':False,'LGT_fit':None,'native_import':None,'TrialAllowed':False,'FinalAccepted':False,'body_pixels_changed_outside_sword_alpha':changed_outside}
 rows.append(row);wholes.append(whole)
 own=np.zeros_like(a)
 for o in OWNERS:own[masks[o]&alive,:3]=COLORS[o];own[masks[o]&alive,3]=a[masks[o]&alive,3]
 owner_panels.append(Image.fromarray(own))
 bg=Image.new('RGBA',(1280,720),(45,48,54,255));bg=Image.alpha_composite(bg,place(whole,root));dr=ImageDraw.Draw(bg)
 dr.text((24,20),f'OFFLINE Dodge218 SWD phase{i} / t={i*100}ms / 416->72 common scale',font=font(22),fill='white')
 dr.text((24,53),'Source-owned partition + independent sword .50; artist axis, no native/equipment acceptance.',font=font(19),fill='white')
 save(f'preview-frames/frame-{i:03d}.png',bg.convert('RGB'));displays.append(bg.convert('RGB'))

rd=read(READY_MARKERS)['frames'][0];ra=np.array(Image.open(READY).convert('RGBA'));rm=poly_mask(rd['visible_fist_replay_polygon_candidate_px'])&(ra[:,:,3]>0)
rs,raff,rdeg,rtp=rigid_sword(rd['grip_candidate_px'],rd['handle_axis_candidate_xy'])
rwhole=Image.alpha_composite(Image.alpha_composite(Image.fromarray(np.where(rm[:,:,None],0,ra).astype(np.uint8)),rs),Image.fromarray(np.where(rm[:,:,None],ra,0).astype(np.uint8)))
save('reference-only/Ready158-known-binding-only.png',rwhole)
last=rows[3];rr=rd['source_root_px'];gdelta=((np.array(rd['grip_candidate_px'])-rr)-(np.array(last['author_binding']['Grip_xy'])-roots[3]))*K
tdelta=((np.array(rtp([482,256]))-rr)-(np.array(last['author_binding']['tip_reference_xy'])-roots[3]))*K
join=write('Dodge3-to-Ready158-join-diagnostic-v001.json',{'Dodge3_source':rows[3]['source'],'Ready158_source':pin(READY),'Ready_existing_marker_contract':pin(READY_MARKERS),'Ready_own_mask_used_only_for_Ready_reference':True,'constant_body_canvas_px_both':CANVAS,'Dodge3_Root':roots[3],'Ready_existing_Root':rr,'Ready_minus_Dodge3_grip_display_xy':gdelta.tolist(),'Ready_minus_Dodge3_tip_display_xy':tdelta.tolist(),'Ready_minus_Dodge3_angle_degrees':rdeg-last['author_binding']['angle_degrees'],'zero_pop':False,'footlock':False,'native_transition_accepted':False})

full=Image.new('RGB',(2048,562),(45,48,54));d=ImageDraw.Draw(full)
owner_sheet=full.copy();do=ImageDraw.Draw(owner_sheet)
fists=Image.new('RGB',(1600,390),(45,48,54));df=ImageDraw.Draw(fists)
for i,whole in enumerate(wholes):
 full.paste(whole,(512*i,42),whole);d.text((512*i+10,10),f'Dodge{i} / .50 / {rows[i]["author_binding"]["angle_degrees"]:.2f}deg',font=font(23),fill='white')
 owner_sheet.paste(owner_panels[i],(512*i,42),owner_panels[i]);do.text((512*i+8,10),f'Dodge{i}: own source five owners',font=font(20),fill='white')
 gx,gy=SEEDS[i]['grip'];crop=whole.crop((gx-50,gy-45,gx+50,gy+45)).resize((400,360),Image.Resampling.NEAREST);fists.paste(crop,(400*i,30),crop);df.text((400*i+8,7),f'Dodge{i} own fist / artist axis',font=font(20),fill='white')
save('presentation/Dodge4-all-full-SWD-candidates.png',full)
save('presentation/Dodge4-source-owned-five-partitions-diagnostic.png',owner_sheet)
save('presentation/Dodge4-four-fists-4x-nearest.png',fists)
jc=Image.new('RGBA',(1280,640),(45,48,54,255));jc=Image.alpha_composite(jc,place(wholes[3],roots[3],(1280,640),(320,560),1.));jc=Image.alpha_composite(jc,place(rwhole,rr,(1280,640),(960,560),1.));dj=ImageDraw.Draw(jc)
dj.text((20,12),'Dodge3 source root / end400ms',font=font(24),fill='white');dj.text((660,12),'Ready158 existing own binding',font=font(24),fill='white');dj.line((16,560,1264,560),fill=(110,110,110));dj.text((20,601),f'Ready-Dodge3 grip [{gdelta[0]:+.2f},{gdelta[1]:+.2f}] display px; join unresolved, not zero-pop.',font=font(20),fill='white')
save('presentation/Dodge3-to-current-Ready158-common-ground-join.png',jc.convert('RGB'))
gif=OUT/'presentation/Dodge4-finite400ms-NO-LOOP-offline.gif';displays[0].save(gif,save_all=True,append_images=displays[1:],duration=[100]*4,disposal=2,optimize=False)
with Image.open(gif) as im:
 durations=[]
 for i in range(im.n_frames):im.seek(i);durations.append(im.info['duration'])
 assert im.n_frames==4 and durations==[100]*4 and 'loop' not in im.info
ff=Path(imageio_ffmpeg.get_ffmpeg_exe());mp4=OUT/'presentation/Dodge4-finite400ms-offline.mp4'
argv=[str(ff),'-hide_banner','-loglevel','info','-framerate','10','-i',str(OUT/'preview-frames/frame-%03d.png'),'-frames:v','4','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-encode.log',r.stdout+r.stderr);assert r.returncode==0
dec_argv=[str(ff),'-hide_banner','-i',str(mp4),'-map','0:v:0','-f','null','-'];dec=subprocess.run(dec_argv,capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-decode.log',dec.stdout+dec.stderr);assert dec.returncode==0 and 'Duration: 00:00:00.40' in dec.stderr and int(re.findall(r'frame=\s*(\d+)',dec.stderr)[-1])==4
preview=write('finite400ms-offline-preview-receipt-v001.json',{'GIF':pin(gif),'actual_GIF_frames':4,'actual_durations_ms':durations,'loop_extension_present':False,'MP4':pin(mp4),'encode_command':argv,'decode_command':dec_argv,'actual_decoded_frames':4,'actual_container_duration_ms':400,'native_or_accepted_distance_receipt':None,'not_native':'Fixed offline sample ground, four source poses; no actor/world travel, dodge event, invulnerability or equipment proof.'})
contract=write('Dodge218-own-five-partitions-SWD050-Grip-Axis-ground-candidate-v001.json',{'schema':'Dodge218-own-source-five-partitions-SWD050-sourcefit-candidate-v001','source_audit':pin(AUDIT),'source_native218_not_Hurt':True,'source_body_common_scale':{'standing_height':416,'display_body_height':72,'canvas_display_px':CANVAS,'perframe_height_normalized':False},'body_owners':OWNERS,'FarHandForeground':'Every phase owns its actual visible far open glove, distinct from near closed fist; source-owned body partition, not a new armor component. No Ready/Hurt masks reused.','future_LGT_stack':['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','IndependentSword','FarHandForeground','NearHand'],'current_SWD_stack':['BodyRest','NearArmWithoutHand','HelmetForeground','IndependentSword','FarHandForeground','NearHand'],'independent_sword_source':pin(SWORD),'frames':rows,'Ready_join_diagnostic':pin(join),'offline_finite_preview':pin(preview),'newmedia_viewed':False,'newmedia_E_retained':False,'sourcefit_accepted':False,'LGT_armor_actual_source_or_fit':None,'runtime_actual_receipts':None,'TrialAllowed':False,'FinalAccepted':False})
write('HANDOFF.md','''Dodge218自身四相五分区：BodyRest/NearArmWithoutHand/HelmetForeground/NearHand/FarHandForeground。只选择并复制该帧已有RGBA，余下原像素归BodyRest；所有有alpha像素排他唯一owner，整数RGBA和逐像素重构原件。没有WholeBody冒BodyRest，没有灰内衬补画、局部擦色、手/身局部变形、Ready/Hurt mask复用。所有语义轮廓仍是作者可见边界候选，需实际E后看遮挡。

各帧近闭拳Grip是作者可见拳面设计点，轴是明确艺术持剑选择；空拳源没有剑柄可供测量，绝不称骨轴/实测柄轴。独立现用军剑保持全四相.50，唯一确定性刚体旋转/平移，手像素不动。护手/腕ROI重叠值只是可核诊断，不自动证明自然持握。

standing416→72及512canvas88.6153846全行常量，Root使用先前实际paired-shoe提案234/216/227/247,Y464，各鞋原ROI独立复核；不同压低高度保留，非逐相归一/COM/足锁。400ms4×100的GIF无loop、MP4实际解码4帧/400ms，仅离线源审查。Dodge3→Ready实际握点/剑尖角度差保留，不冒zeroPop/native。新媒体先F原件/展示/index，Root E两SHA后才能View。LGT12片仍待Root生成+官方提取+实际整数fit，实际Source/Content/UE未动。
''')
freeze=write('Dodge-own-partition-SWD-sourcefit-freeze-v001.json',{'schema':'Dodge218-own-partition-SWD-sourcefit-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'actual_rgba_partition_proof_four_pass':True,'newmedia_View':False,'native_calls':0})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/自身五分区军剑候选完整包');shutil.copyfile(Path(__file__),MEDIA/'原件'/Path(__file__).name)
(MEDIA/'展示副本').mkdir()
for p in sorted((OUT/'presentation').iterdir()):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Dodge218自身五分区军剑持握候选','version':'v001','status':'All4 exact source-owned partitions proven; artist Grip/Axis/SWD050 unviewed pending RootE; no LGT/runtime acceptance','candidate':OUT.as_posix(),'contract':pin(contract),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'contract':pin(contract),'freeze':pin(freeze),'four_guard_wrist_overlap_px':[r['author_binding']['actual_guard_ROI_core_overlap_pixels'] for r in rows],'Ready_minus_Dodge3_grip_display_xy':gdelta.tolist(),'newmedia_View':False,'native_calls':0},ensure_ascii=False,indent=2))
