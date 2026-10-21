from pathlib import Path
import hashlib,json,math,re,shutil,subprocess,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001';HERE=Path(__file__).resolve().parent
OUT=HERE/'candidate-v002';assert not OUT.exists();OUT.mkdir()
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt227军剑四相持握与400ms回接诊断_v002';assert not MEDIA.exists()
RUN=BASE/'hero227-hurt4-extraction-v001/runs/run-hurt227-shared-HD-v001'
OLD=BASE/'hurt227-SWD-frame1-fit-v001/candidate-v001'
SWORD=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
READY=ROOT/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
READY_MARKERS=ROOT/'source-assets/production/fairytale-sword-v001/ready-measurement-v002/ready-marker-proposal-v002.json'
E419=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-Hurt227-SWD-contact-candidate-v419')
E415=BASE/'hero227-hurt4-extraction-v001/E415-before-curated-View-check-v001.json'
CANVAS=72.*512./416.;K=CANVAS/512.;SWD_GRIP=np.array([99.,256.]);SCALE=.50
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,im):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);im.save(p);return p
def bbox(m):
 y,x=np.where(m)
 return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def measure_shoe(a,roi,threshold=128):
 x0,y0,x1,y1=roi;v=a[y0:y1,x0:x1];y,x=np.where(v[:,:,3]>=threshold);bottom=int(y.max()+y0)
 band=a[bottom-3:bottom+1,x0:x1,3].astype(float);band[band<threshold]=0
 weights=band.sum(axis=0);xx=np.where(weights>0)[0]+x0;cx=float(np.dot(weights,np.arange(x0,x1))/weights.sum())
 assert xx.min()>x0 and xx.max()<x1-1
 point=[round(cx),bottom];assert a[point[1],point[0],3]>=threshold
 return {'artist_ROI_xyxy':roi,'alpha_threshold':threshold,'visible_sole_core_bottom_y':bottom,'floor_edge_y':bottom+1,'bottom4row_alpha_weighted_centroid_x':cx,'bottom4row_actual_xrange':[int(xx.min()),int(xx.max())],'actual_sole_edge_sample_xy':point,'actual_sole_edge_RGBA':a[point[1],point[0]].tolist(),'horizontal_ROI_not_clipped':True}
def rigid_sword(grip,axis):
 angle=math.atan2(axis[1],axis[0]);c,s=math.cos(angle),math.sin(angle);g=np.array(grip,dtype=float)
 aff=(c/SCALE,s/SCALE,float(SWD_GRIP[0]-(c*g[0]+s*g[1])/SCALE),-s/SCALE,c/SCALE,float(SWD_GRIP[1]-(-s*g[0]+c*g[1])/SCALE))
 im=sword.convert('RGBa').transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')
 def tp(q):return (g+SCALE*np.array([[c,-s],[s,c]])@(np.array(q,dtype=float)-SWD_GRIP)).tolist()
 assert np.allclose(tp([99,256]),g)
 return im,aff,math.degrees(angle),tp
def compose_source(a,polygon,grip,axis):
 poly=Image.new('L',(512,512),0);ImageDraw.Draw(poly).polygon(list(map(tuple,polygon)),fill=255)
 m=(np.array(poly)>0)&(a[:,:,3]>0);hand=np.where(m[:,:,None],a,0).astype(np.uint8);rest=np.where(m[:,:,None],0,a).astype(np.uint8)
 assert np.array_equal(np.where(m[:,:,None],hand,rest),a) and not np.any((hand[:,:,3]>0)&(rest[:,:,3]>0))
 swd,aff,deg,tp=rigid_sword(grip,axis)
 whole=Image.alpha_composite(Image.alpha_composite(Image.fromarray(rest),swd),Image.fromarray(hand))
 return m,hand,rest,swd,whole,aff,deg,tp
def place_ground(im,root,outsize=(1280,720),ground=(640,490),k=K):
 aff=(1/k,0.,float(root[0]-ground[0]/k),0.,1/k,float(root[1]-ground[1]/k))
 return im.convert('RGBa').transform(outsize,Image.Transform.AFFINE,aff,resample=Image.Resampling.BICUBIC).convert('RGBA')

assert pin(SWORD)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
assert pin(READY)['sha256']=='d3f766506a9cc623c38787836a9c23c0126d185d1bdf7e8946181efd554338c5'
e_ready=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-18-OurgameUE-hero218-220-reserved-v382/F盘原批次副本/2026-10-18_钟盔受挫四帧生成预约_v001/原件/006-frame-0.png');assert READY.read_bytes()==e_ready.read_bytes()
gate=json.loads(E415.read_text(encoding='utf-8'));assert gate['root_explicit_View_allowed'] and gate['differences']==0
old_contract=OLD/'Hurt1-authored-Grip-Axis-source-mask-transform-and-row-registration-v001.json';one=json.loads(old_contract.read_text(encoding='utf-8'))
old_view=write('E419-before-expansion-view-receipt-v001.json',{'authority':'Root explicit E41922files twoSHA0 and source-level singleframefit permission, then worker actuallyViewed3existingpresentationPNG afterretention.','E419_manifest':pin(E419/'source-size-SHA256.json'),'actually_viewed_existing3':[pin(OLD/'presentation'/n) for n in ['source-and-SWD-fit-512-side-by-side.png','Hurt1-contact-source-and-composite-4x-nearest.png','Hurt1-SWD-display-size-offline-candidate.png']],'worker_observation':'Sword hilt butt emergesbehindupperfist, guard outsidefingers, handcoversshaft; completebladeendsaboveground. Candidatecontact readable; no anatomy/physicalforce/native/LGTclaim.','Root_acceptance_scope':'Source-level authoredregistrationcandidate only, not measuredtrueboneaxis, LGTornative.'})
sword=Image.open(SWORD).convert('RGBA');sa=np.array(sword);yy,xx=np.indices((512,512));guard_source=(sa[:,:,3]>0)&(xx>=134)&(xx<159)&(yy>=210)&(yy<303)
SEEDS=[
 {'grip':[236,303],'axis':[.7,math.sqrt(.51)],'polygon':[[218,282],[226,276],[237,274],[249,277],[256,284],[259,291],[261,299],[260,309],[254,318],[248,325],[240,332],[228,333],[216,328],[209,319],[205,307],[206,296],[211,288]],'wrist':[174,273,215,326],'shoes':[[135,420,216,466],[269,416,375,466]]},
 {'grip':[194,289],'axis':[.8,.6],'polygon':one['new_hand_source']['foreground_polygon_artist_xy'],'wrist':[136,269,175,315],'shoes':[[150,422,245,466],[297,420,410,466]]},
 {'grip':[205,289],'axis':[.96,.28],'polygon':[[184,269],[196,264],[209,265],[219,268],[229,275],[234,283],[235,292],[231,301],[225,307],[217,314],[207,319],[194,318],[182,313],[174,305],[170,296],[170,284],[176,276]],'wrist':[148,259,187,301],'shoes':[[120,416,205,466],[261,414,364,466]]},
 {'grip':[218,303],'axis':[.94,-.341],'polygon':[[198,284],[209,279],[220,280],[231,286],[240,293],[245,301],[245,311],[240,319],[233,326],[224,332],[213,335],[201,332],[191,326],[185,316],[182,304],[185,294],[191,288]],'wrist':[164,276,200,318],'shoes':[[133,418,213,466],[261,415,366,466]]}]
font_path=next(p for p in [Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/segoeui.ttf')] if p.exists());font=lambda n:ImageFont.truetype(str(font_path),n)
rows=[];composites=[];roots=[];display=[]
for i,se in enumerate(SEEDS):
 source=RUN/f'curated/frame-{i}.png';assert source.read_bytes()==Path(gate['frames'][i]['E']['path']).read_bytes()
 a=np.array(Image.open(source).convert('RGBA'));m,hand,rest,swd,whole,aff,deg,tp=compose_source(a,se['polygon'],se['grip'],se['axis']);gx,gy=se['grip'];assert m[gy,gx] and a[gy,gx,3]>=192
 hp=save(f'layers/frame-{i}/NearHandForeground-exact-sourceRGBA.png',Image.fromarray(hand));rp=save(f'layers/frame-{i}/BodyRest-exact-sourceRGBA.png',Image.fromarray(rest));mp=save(f'masks/frame-{i}-new-visible-fist-mask-L.png',Image.fromarray(np.where(m,255,0).astype(np.uint8),'L'));sp=save(f'layers/frame-{i}/SWD-rigid050.png',swd);cp=save(f'composite/frame-{i}-Hurt227-SWD-held-512RGBA.png',whole)
 (OUT/'source-readcopies').mkdir(exist_ok=True);shutil.copyfile(source,OUT/f'source-readcopies/Hurt227-frame-{i}-original.png')
 if i==1:
  assert np.array_equal(hand,np.array(Image.open(OLD/'layers/Hurt1-NearHandForeground-exact-sourceRGBA.png')))
  assert np.array_equal(np.array(swd),np.array(Image.open(OLD/'layers/Hurt1-SWD-rigid-scale050-axis080060.png')))
  assert np.array_equal(np.array(whole),np.array(Image.open(OLD/'composite/Hurt1-SWD-held-candidate-512RGBA.png')))
 shoes=[measure_shoe(a,r) for r in se['shoes']];root=[sum(s['bottom4row_alpha_weighted_centroid_x'] for s in shoes)/2.,max(s['floor_edge_y'] for s in shoes)]
 sweeps=[]
 for threshold in [64,192]:
  stats=[measure_shoe(a,r,threshold) for r in se['shoes']];sweeps.append({'threshold':threshold,'paired_root':[sum(s['bottom4row_alpha_weighted_centroid_x'] for s in stats)/2.,max(s['floor_edge_y'] for s in stats)]})
 guard=np.array(Image.fromarray((guard_source*255).astype(np.uint8),'L').transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.NEAREST))>0
 x0,y0,x1,y1=se['wrist'];wr=np.zeros((512,512),bool);wr[y0:y1,x0:x1]=True;guard_overlap=int(np.count_nonzero(guard&wr&(a[:,:,3]>=128)));assert guard_overlap==0
 palpha=np.array(swd)[:,:,3];assert not np.any(palpha[0]) and not np.any(palpha[-1]) and not np.any(palpha[:,0]) and not np.any(palpha[:,-1])
 unit=np.array([math.cos(math.radians(deg)),math.sin(math.radians(deg))]);g=np.array(se['grip'],float);inside=[]
 for t in np.arange(-100.,100.25,.25):
  q=g+t*unit;x,y=np.rint(q).astype(int)
  if 0<=x<512 and 0<=y<512 and m[y,x]:inside.append(float(t))
 tip=tp([482,256]);assert tip[1]<root[1]
 core=a[:,:,3]>=128;ys,xs=np.where(core)
 eyes=(a[:,:,3]>=128)&(a[:,:,0]>220)&(a[:,:,1]>90)&(a[:,:,1]<230)&(a[:,:,2]<65)&(a[:,:,0]>a[:,:,1]+35)&(yy>=130)&(yy<280)
 ey,ex=np.where(eyes);eye=[float(ex.mean()),float(ey.mean())]
 row={'frame':i,'source':pin(source),'source_native_facing':'right_shallow_elevated3quarter','source_body_core_bbox':bbox(core),'natural_visible_height_source_px':int(ys.max()+1-ys.min()),'one_row_displayed_body_extent_px':float((ys.max()+1-ys.min())*K),'shared_canvas_px':CANVAS,'perframe_height_normalized':False,
  'source_hand':{'author_segmentation_polygon_xy':se['polygon'],'mask':pin(mp),'foreground_exact_RGBA':pin(hp),'BodyRest_exact_RGBA':pin(rp),'pixel_count':int(m.sum()),'source_grip_pixel_RGBA':a[gy,gx].tolist(),'exclusive_reconstructs_original_all_RGBA_exact':True,'outside_hand_mask_body_source_unchanged':True,'no_Ready_handmask_or_polygon_reused':True,'segmentation_limit':'Visiblegloveandwristseam artistboundary only; actualmask/swordcontactreviewpendingafterE. No cavity/boneinference.'},
  'author_binding':{'Grip_xy':se['grip'],'Axis_xy':se['axis'],'Axis_is_artist_choice_not_source_handle_measurement':True,'angle_degrees':deg,'axis_reason':'Heavyretainedweapon droopsinimpact and coherentlyreturns towardexistingReadyangle byframe3; no bladeend/hiddenhandleaxis measurablefrombarebody.','independent_source_grip':[99,256],'weapon_scale_constant':SCALE,'inverse_affine':list(aff),'Sword_layer':pin(sp),'guard_wrist_ROI':se['wrist'],'guard_over_wrist_actual_core_pixels':guard_overlap,'actual_handmask_axis_entry_exit_xy':[(g+min(inside)*unit).tolist(),(g+max(inside)*unit).tolist()],'entry_exit_meaning':'Authoredaxis intersectsactualvisiblemask; sourcehasnohandle, so theseareproposedemergence notobservedshaftends.','complete_sword_bbox':bbox(palpha>0),'sword_clipped':False,'tip_reference_transformed_xy':tip,'tip_above_artist_floor_source_px':root[1]-tip[1]},
  'ground_registration':{'visible_shoes_independent_ROIs':shoes,'pairedshoe_Root_artist_xy':root,'formula':'X=arithmeticmeanofbothactualbottom4rowalphaweightedsolecentroids;Y=maxactualcorefloor-edgeY. Perframe sourcewholecomponentplacementcompensation, not actorXYmovement.','threshold_sweeps':sweeps,'meaning':'Explicitnewpairedvisible-sole artistgroundregistrationcandidate. Curvedsoles/differentprojectedbootdepthmake thisnot truephysicalmidfoot/bone/COM orfootlock; do not claimshoesfixedinworld.','replaces_unmeasured_fixed256_candidate':True,'one_row_scale_constant':True},
  'visible_amber_eye_centroid_source_xy':eye,'eye_measurement_role':'ActualwarmbrightpixelcentroidinexplicitfaceverticalROI; visibleeye-art comparisonnotheadbone.','stack_back_to_front':['BodyRest','SWD-rigid050','NearHandForeground'],'composite':pin(cp),'true_SWD_fourframe_fit_accepted':False,'LGT_native_accepted':False}
 rows.append(row);composites.append(whole);roots.append(root)
 bg=Image.new('RGBA',(1280,720),(45,48,54,255));bg=Image.alpha_composite(bg,place_ground(whole,root));db=ImageDraw.Draw(bg);db.text((24,20),f'OFFLINE Hurt227 SWD / phase{i} / t={i*100}ms / shared body72px standing',font=font(22),fill='white');db.text((24,54),'Real source pixels + independent sword .50. Source-fit candidate only; LGT/native unaccepted.',font=font(19),fill='white')
 save(f'preview-frames/actual-scale-{i:03d}.png',bg.convert('RGB'));display.append(bg.convert('RGB'))

for p in [SWORD,READY]:shutil.copyfile(p,OUT/'source-readcopies'/p.name.replace('frame-0','Ready158-frame0'))
rd=json.loads(READY_MARKERS.read_text(encoding='utf-8'))['frames'][0];ready_a=np.array(Image.open(READY).convert('RGBA'));rpolygon=rd['visible_fist_replay_polygon_candidate_px'];rg=rd['grip_candidate_px'];ra=rd['handle_axis_candidate_xy'];rr=rd['source_root_px']
rm,rh,rrest,rsword,rwhole,raff,rdeg,rtp=compose_source(ready_a,rpolygon,rg,ra)
rpath=save('reference-only/Ready158-existing-binding-reconstruction-512RGBA.png',rwhole)
# Existing Ready ownmask is used ONLY for this reference reconstruction, never for a Hurt mask.
last=rows[3];lp=np.array(last['author_binding']['Grip_xy'])-np.array(roots[3]);rrel=np.array(rg)-np.array(rr);gdelta=(rrel-lp)*K
tdelta=((np.array(rtp([482,256]))-rr)-(np.array(last['author_binding']['tip_reference_transformed_xy'])-roots[3]))*K
reyes=(ready_a[:,:,3]>=128)&(ready_a[:,:,0]>220)&(ready_a[:,:,1]>90)&(ready_a[:,:,1]<230)&(ready_a[:,:,2]<65)&(ready_a[:,:,0]>ready_a[:,:,1]+35)&(yy>=130)&(yy<280);ey,ex=np.where(reyes);reye=np.array([ex.mean(),ey.mean()]);edelta=((reye-rr)-(np.array(last['visible_amber_eye_centroid_source_xy'])-roots[3]))*K
ready_shoes=[measure_shoe(ready_a,r) for r in [[142,425,240,466],[261,424,356,466]]]
shoe_join=[]
for j in range(2):
 lh0=last['ground_registration']['visible_shoes_independent_ROIs'][j];rh0=ready_shoes[j]
 before=np.array([lh0['bottom4row_alpha_weighted_centroid_x'],lh0['floor_edge_y']])-roots[3];after=np.array([rh0['bottom4row_alpha_weighted_centroid_x'],rh0['floor_edge_y']])-rr
 shoe_join.append({'visible_role':'image_left_shoe' if j==0 else 'image_right_shoe','Ready_minus_Hurt3_display_xy':((after-before)*K).tolist(),'not_footlock':True})
join=write('Hurt3-to-current-Ready158-existing-binding-join-diagnostic-v001.json',{'schema':'Hurt227end-to-existingReady158-offline-join-v001','Hurt3_source':rows[3]['source'],'Ready0_source':pin(READY),'Ready_source_E_exact':pin(e_ready),'Ready_existing_marker_contract':pin(READY_MARKERS),'Ready_baseline_composite':pin(rpath),'Ready_original_root_grip_axis':{'Root':rr,'Grip':rg,'Axis':ra,'angle_degrees':rdeg,'SwordScale':.50},'Hurt3_pairedshoe_root':roots[3],'shared_body_canvas_px_both':CANVAS,'Ready_minus_Hurt3_grip_display_xy':gdelta.tolist(),'Ready_minus_Hurt3_blade_tip_display_xy':tdelta.tolist(),'artist_axis_angle_delta_degrees':rdeg-last['author_binding']['angle_degrees'],'visible_eye_centroid_delta_display_xy':edelta.tolist(),'visible_shoe_deltas':shoe_join,'body_crown_extent_display_px':{'Hurt3':rows[3]['one_row_displayed_body_extent_px'],'Ready0':(rd.get('body_height_source_px',415))*K},'scope':'Pureofflineexactsourceandknownbindingdiagnostic, samegroundpoint, nointerpolation/morph/actorjump orperframeheightnormalization. ExistingReadyownfistpolygon is onlybaseline; notcopiedtoHurt. Deltaquantifiesremainingpose/solechanges, doesnotprovezeropop/footlock/nativeentryageorstatepriority. Sourceartcandidateonly.'})

sheet=Image.new('RGB',(2048,576),(45,48,54));ds=ImageDraw.Draw(sheet)
for i,im in enumerate(composites):
 sheet.paste(im,(i*512,48),im);ds.text((i*512+12,12),f'Hurt{i} / {rows[i]["author_binding"]["angle_degrees"]:.2f}deg / .50',font=font(24),fill='white')
save('presentation/Hurt4-all-full-composites-contact.png',sheet)
hand_sheet=Image.new('RGB',(1600,390),(45,48,54));hs=ImageDraw.Draw(hand_sheet)
for i,im in enumerate(composites):
 gx,gy=SEEDS[i]['grip'];crop=im.crop((gx-50,gy-45,gx+50,gy+45)).resize((400,360),Image.Resampling.NEAREST);hand_sheet.paste(crop,(i*400,30),crop);hs.text((i*400+6,6),f'Hurt{i} / new ownsource fist',font=font(20),fill='white')
save('presentation/Hurt4-contact-four-fists-4x-nearest.png',hand_sheet)
ground_sheet=Image.new('RGB',(2048,570),(45,48,54));gg=ImageDraw.Draw(ground_sheet)
for i,row in enumerate(rows):
 a=Image.open(RUN/f'curated/frame-{i}.png').convert('RGBA');ground_sheet.paste(a,(i*512,40),a);r=roots[i]
 for st in row['ground_registration']['visible_shoes_independent_ROIs']:
  x=st['bottom4row_alpha_weighted_centroid_x']+i*512;y=st['floor_edge_y']+40;gg.ellipse((x-3,y-3,x+3,y+3),outline=(90,210,255),width=2)
 gg.line((r[0]+i*512-9,r[1]+40,r[0]+i*512+9,r[1]+40),fill=(255,230,90),width=2);gg.text((i*512+10,8),f'Hurt{i} pairedshoe root [{r[0]:.3f},{r[1]}]',font=font(20),fill='white')
save('presentation/Hurt4-actual-pairedshoe-ground-registration-candidate.png',ground_sheet)
join_canvas=Image.new('RGBA',(1280,640),(45,48,54,255));join_canvas=Image.alpha_composite(join_canvas,place_ground(composites[3],roots[3],(1280,640),(320,560),1.));join_canvas=Image.alpha_composite(join_canvas,place_ground(rwhole,rr,(1280,640),(960,560),1.));jj=ImageDraw.Draw(join_canvas);jj.text((26,12),'Hurt3 pairedshoe root / end400ms',font=font(26),fill='white');jj.text((666,12),'Current Ready158 own root / existing binding',font=font(24),fill='white');jj.line((15,560,1260,560),fill=(110,110,110),width=1);jj.text((28,601),f'Ready-Hurt3 display grip delta [{gdelta[0]:+.3f},{gdelta[1]:+.3f}]px; angle delta {rdeg-last["author_binding"]["angle_degrees"]:+.3f}deg. No zero-pop claim.',font=font(20),fill='white')
save('presentation/Hurt3-to-Ready158-common-ground-join-diagnostic.png',join_canvas.convert('RGB'))

gif=OUT/'presentation/Hurt4-actual400ms-NO-LOOP-offline.gif';display[0].save(gif,save_all=True,append_images=display[1:],duration=[100]*4,disposal=2,optimize=False)
with Image.open(gif) as check:
 durations=[]
 for i in range(check.n_frames):check.seek(i);durations.append(check.info['duration'])
 assert check.n_frames==4 and durations==[100]*4 and 'loop' not in check.info
ff=Path(imageio_ffmpeg.get_ffmpeg_exe());video=OUT/'presentation/Hurt4-actual400ms-finite-offline.mp4'
argv=[str(ff),'-hide_banner','-loglevel','info','-framerate','10','-i',str(OUT/'preview-frames/actual-scale-%03d.png'),'-frames:v','4','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');log=write('logs/ffmpeg-four-frame-finite-encode.log',r.stdout+r.stderr);assert r.returncode==0
dec_argv=[str(ff),'-hide_banner','-i',str(video),'-map','0:v:0','-f','null','-'];dec=subprocess.run(dec_argv,capture_output=True,text=True,encoding='utf-8');dec_log=write('logs/ffmpeg-actual-video-decode-inspection.log',dec.stdout+dec.stderr);assert dec.returncode==0
assert 'Duration: 00:00:00.40' in dec.stderr and int(re.findall(r'frame=\s*(\d+)',dec.stderr)[-1])==4
preview=write('offline-preview-actual-four-frames-400ms-finite-receipt-v001.json',{'schema':'Hurt4-offline-preview-finite400ms-v001','GIF':pin(gif),'GIF_actual_frame_count':4,'GIF_actual_durations_ms':durations,'GIF_loop_extension_present':False,'MP4':pin(video),'actual_encode_command':argv,'encode_exit_code':r.returncode,'encode_log':pin(log),'actual_decode_command':dec_argv,'decode_exit_code':dec.returncode,'decode_log':pin(dec_log),'decoded_frames':4,'container_duration_ms':400,'fps':10,'body_canvas_px':CANVAS,'each_frame_actual_pairedshoe_root':roots,'movement':'Fixedsampleground[640490] offlineonly, noUE/actor/movementreceiptinvention.','not_native':'This isa finite source-pose playbackcandidate, not trueHurt event/timing/statepriority/gearbinding proof. No animationviewedbeforeE.'})
contract=write('Hurt227-four-SWD-independent-masks-art-Grip-Axis-pairedshoe-registration-candidate-v002.json',{'schema':'Hurt227-SWD-fourphase-authored-fit-v002','status':'AllfourcompositesUNVIEWED-newmedia/RootEgate/TrialAllowedfalse','singleframe_parent_root_authority':pin(old_view),'singleframe_frozen_contract':pin(old_contract),'frame1_source_layers_and_composite_RGBA_exact_to_E419_accepted_candidate':True,'source_whole_row_shared_scale':.7074829931972789,'one_body_display_canvas_px':CANVAS,'standing_equivalent_body_source_height':416,'standing_reference_frame':3,'body_heights_not_normalized_perframe':True,'independent_SWD_source':pin(SWORD),'source_weapon_grip':[99,256],'weapon_scale_constant_all_four':SCALE,'artist_axes_clockwise_y_down_degrees':[r['author_binding']['angle_degrees'] for r in rows],'artist_axis_sequence_scope':'Authoredretainedsworddroop→steadyreturn, allanglesareexplicitartchoicesratherthanmeasuredhiddenshaftaxes. OnlyendanglealignsReadyreference; noReadyhandmaskappliedtoHurt.','rows':rows,'preview':pin(preview),'join':pin(join),'acceptance':{'newfourframes_composite_viewed':False,'firstframe1_sourcefit_allowed_by_Root_E419':True,'allfour_source_SWDFit_accepted':False,'truebone_or_handleaxis_measured':False,'pairedshoe_registration_footlock':False,'LGT_armor_prepared':False,'native_runtime_accepted':False,'TrialAllowed':False},'worker_scope':{'AI_native_API_calls':0,'Source_Content_Roottools_ledger_UE_modified':False,'originalsourcepixels_drawn_or_edited':False,'newmedia_viewed':False}})
write('HANDOFF.md','''# Hurt227 SWD四相持握：source候选v002\n\n先实际View E419已保全三张后扩0/2/3，每帧自己的source拳部独立分割；Hurt1 mask/剑层/合成与E419候选RGBA精确相等。所有四帧BodyRest+NearHand排他、全部RGBA重构各自原件；没有套用Ready mask。独立剑只作.50常量刚性变换，四帧护手与各自腕口ROI实际core交叠0、整剑无裁边。作者轴45.57°→36.87°→16.26°→-19.94°保持从低垂受挫向Ready收回；不是测得骨轴/隐藏柄轴。\n\n身体Canvas88.6153846以站立末相冠底416映射72px，整行唯一尺度。每帧独立实际左右鞋alpha128底四行质心配对均值与最低core边作为NEW artist ground root（约259.918/463、283.339/464、247.068/464、252.447/464）；原全256提案保留，仅本版采用新pairedshoe候选。不同鞋深度、曲底和姿态使该统计量不等于物理脚中心/COM/足锁，native仍需审。\n\n实际离线四帧400ms：GIF无loop扩展且4×100ms；MP4 encode/decode0，容器400ms、解码4帧。不是SDK循环便利GIF，也不替代UE实际受伤状态。另有末相到当前Ready158自己已有绑定/遮罩的common-ground诊断；Ready mask仅用于Ready参考，不用于Hurt。量化Grip/剑尖/眼与鞋的残余变化，不冒zeroPop。\n\n全部新四帧、配准诊断、GIF/MP4与回接图均未View，先Root E两SHA保全再实际审。四相SWD sourcefit、LGT/native/状态切换仍未验收；本批未调用AI或修改Source/Content/Roottools/ledger/UE。\n''')
handoff=write('Root-Hurt4-SWD-sourcefit-offline400ms-and-Ready-join-handoff-v002.json',{'schema':'HeroHurt227-SWD-four-sourcefit-offline400ms-Root-review-v002','contract':pin(contract),'preview':pin(preview),'join':pin(join),'canonical_F_media':MEDIA.as_posix(),'four_full_composites':[r['composite'] for r in rows],'newimages_viewed':False,'newimages_E_retained':False,'TrialAllowed':False,'next':'RootEretainallnewmediawith2SHAthenactualfourposes/maskcontact/finitenonlooppreview/Readyjoinreview. SWDsourcefitfirst,LGTnext;neithernative norfullrowcontactclaimedpassed.'})
write('candidate-freeze-v002.json',{'schema':'Hurt227-four-SWD-sourcefit-freeze-v002','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'script':pin(Path(__file__)),'newmedia_View':False,'actualSource_modified':False,'old_v001_unchanged':True})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/四相持握候选完整包');(MEDIA/'展示副本').mkdir()
for p in sorted((OUT/'presentation').iterdir()):
 if p.is_file():shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Hurt227军剑四相持握与400ms回接诊断','version':'v002','status':'sourcefitfour-newmediaUNVIEWEDawaitRootE;finite400msofflineonly;LGTnativeunaccepted','source':OUT.as_posix(),'handoff':pin(handoff),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'handoff':pin(handoff),'contract':pin(contract),'pairshoe_roots':roots,'angles_degrees':[r['author_binding']['angle_degrees'] for r in rows],'join_display_Grip_delta':gdelta.tolist(),'join_display_tip_delta':tdelta.tolist(),'join_eye_display_delta':edelta.tolist(),'join_shoe_display_delta':shoe_join,'video_duration_ms':400,'video_decoded_frames':4,'GIF_no_loop':True,'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'newmedia_View':False},ensure_ascii=False,indent=2))
