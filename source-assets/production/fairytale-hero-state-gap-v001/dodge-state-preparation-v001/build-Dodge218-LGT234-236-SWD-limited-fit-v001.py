from pathlib import Path
import ast,copy,hashlib,json,math,re,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001';HERE=Path(__file__).resolve().parent
OUT=HERE/'LGT234-236-own-source-integer-fit-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge218棕皮三层军剑有限试拼_v001'
assert not OUT.exists() and not MEDIA.exists();OUT.mkdir()
K=72./416.;CANVAS=512*K;SCALE=.50;SOURCE_GRIP=np.array([99.,256.])
SWORD=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
READY=ROOT/'source-assets/production/fairytale-sword-v001/run-ready-v002/curated/frame-0.png'
READY_MARKERS=ROOT/'source-assets/production/fairytale-sword-v001/ready-measurement-v002/ready-marker-proposal-v002.json'
OLD_REG=BASE/'hero218-220-extraction-v001/visible-registration-proposal-v001/visible-crown-shoe-support-glove-proposals-v001.json'
AUDIT=HERE/'source-retention-audit-v001.json'
OLD_SCRIPT=HERE/'build-Dodge218-own-partition-and-SWD050-candidate-v001.py'
old=ast.parse(OLD_SCRIPT.read_text(encoding='utf-8-sig'))
function_names={'pin','read','write','save','bbox','poly_mask','rigid_sword','place','measure_sole'}
exec(compile(ast.Module(body=[n for n in old.body if isinstance(n,ast.FunctionDef) and n.name in function_names],type_ignores=[]),'reused-pure-deterministic-functions','exec'),globals())
SEEDS=copy.deepcopy(ast.literal_eval(next(n.value for n in old.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SEEDS' for t in n.targets))))
old_grips=[s['grip'][:] for s in SEEDS]
new_grips=[[196,307],[159,324],[158,305],[188,293]]
for s,g in zip(SEEDS,new_grips):s['grip']=g
SEEDS[3]['NearHand']=[[145,264],[159,259],[177,259],[195,267],[205,277],[210,287],[210,300],[200,312],[183,319],[166,319],[150,313],[139,306],[133,294],[133,279],[138,269]]
# These are the actual visible original gray shirt collar/fold, not painted lining.
# They are a separately documented foreground region within the existing HelmetForeground owner.
COLLARS=[
 [[208,222],[239,232],[264,243],[288,250],[286,268],[268,273],[243,264],[222,250],[209,239]],
 [[179,283],[207,298],[237,318],[273,338],[290,341],[282,353],[257,345],[226,329],[198,310],[179,299]],
 [[187,230],[216,246],[246,264],[277,283],[301,294],[290,306],[270,301],[242,284],[214,266],[191,250]],
 [[192,201],[219,213],[248,228],[277,240],[288,243],[284,258],[261,258],[235,247],[208,230],[190,218]]]
OWNERS=['BodyRest','NearArmWithoutHand','HelmetForeground','NearHand','FarHandForeground']
PRIORITY=['NearHand','FarHandForeground','HelmetForeground','NearArmWithoutHand']
ARMOR={'Chest':('chest',234,477),'ShoulderNear':('nearshoulder',235,478),'ShoulderFar':('farshoulder',236,480)}
CHEST_A=[[265,286],[262,289],[261,287],[266,285]]
CHEST_B=[[249,311],[247,355],[248,321],[244,304]]
NEAR_A=[[255,251],[254,252],[254,250],[255,250]]
NEAR_B=[[170,246],[158,267],[157,247],[171,240]]
FAR_A=[[253,247],[253,257],[251,249],[253,247]]
FAR_B=[[302,277],[311,348],[306,298],[296,267]]
VISIBLE_ARM_JUNCTION_B=[[204,260],[190,304],[188,268],[194,249]]
NECK_ROI=[[240,206,286,238],[248,225,293,252],[248,213,294,246],[237,205,284,234]]
BELT_ROI=[[230,301,277,323],[224,343,281,368],[226,310,277,333],[225,294,275,315]]

def translate(a,dx,dy):
 out=np.zeros_like(a);sx0=max(0,-dx);sy0=max(0,-dy);sx1=min(512,512-dx);sy1=min(512,512-dy)
 out[sy0+dy:sy1+dy,sx0+dx:sx1+dx]=a[sy0:sy1,sx0:sx1]
 assert np.count_nonzero(out[:,:,3])==np.count_nonzero(a[:,:,3]);return out
def holes(mask):
 im=Image.fromarray(np.where(mask,255,0).astype(np.uint8)).copy()
 ImageDraw.floodfill(im,(0,0),128,thresh=0)
 return np.array(im)==0
toy=np.zeros((24,24),bool);toy[5:16,5]=True;toy[5:16,15]=True;toy[5,5:16]=True;toy[15,5:16]=True
closed=holes(toy);assert int(closed.sum())==81 and bbox(closed)==[6,6,15,15]
open_toy=toy.copy();open_toy[5,10]=False;assert not holes(open_toy).any()
toy_receipt=write('true-closed-hole-vs-external-corridor-toy-proof-v001.json',{'implementation':'Pillow writable Image.copy then 4-connected exterior flood from0,0; only remaining background0 is closed hole. Input numpy not mutated.','closed_ring_hole_pixels':81,'closed_hole_bbox':[6,6,15,15],'opened_corridor_hole_pixels':0,'ROI_whole_domain_mislabel':False})

audit=read(AUDIT);old_rows=[r for r in read(OLD_REG)['frames'] if r['state']=='dodge']
old_contract=HERE/'own-partition-SWD-fit-v001/Dodge218-own-five-partitions-SWD050-Grip-Axis-ground-candidate-v001.json'
E474=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v474/source-size-SHA256.json'))
armor_sources={};armor_receipts=[]
for component,(token,native,ev) in ARMOR.items():
 run=HERE/f'official-process-runs-v001/{token}-native{native}/run-shared-HD-v001'
 ix=next(Path('E:/OurGame/Knight/过程图稿与视频').glob(f'*v{ev}/source-size-SHA256.json'));idx=read(ix)
 assert idx['verification_passes']==2 and idx['source_and_target_hash_mismatches']==0
 rec=read(run/'extraction-receipt-v001.json');assert len(rec['frames'])==4 and len(rec['commands'])==5 and all(x['exit_code']==0 for x in rec['commands'])
 armor_receipts.append({'component':component,'official_process_receipt':pin(run/'extraction-receipt-v001.json'),'E_retention_index':pin(ix),'original_inspect_errors':rec['inspect_errors'],'original_inspect_warnings':rec['inspect_warnings'],'original_fit_window':rec['fit_window_predeclared'],'original_shared_scale':rec['shared_row_fit']['scale'],'inspect_warnings_not_erased_or_automatically_exempted':True})
 for i in range(4):
  p=run/f'curated/frame-{i}.png';assert pin(p)==rec['frames'][i]['curated'];rr=next(r for r in idx['files'] if r['sha256']==pin(p)['sha256']);e=ix.parent/rr['retained_relative']
  for _ in range(2):assert p.read_bytes()==e.read_bytes() and pin(p)['sha256']==pin(e)['sha256']
  armor_sources[component,i]=(p,np.array(Image.open(p).convert('RGBA')))
sword=Image.open(SWORD).convert('RGBA');assert pin(SWORD)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
sa=np.array(sword);yy,xx=np.indices((512,512));guard_source=(sa[:,:,3]>0)&(xx>=134)&(xx<159)&(yy>=210)&(yy<303)
rows=[];wholes=[];swd_wholes=[];roots=[];displays=[];owner_panels=[]
colors={'BodyRest':(150,150,150),'NearArmWithoutHand':(230,95,100),'HelmetForeground':(235,205,85),'NearHand':(95,215,160),'FarHandForeground':(100,155,245)}
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
for i,se in enumerate(SEEDS):
 source=Path(audit['curated4'][i]['F']['path']);assert pin(source)==audit['curated4'][i]['F'];a=np.array(Image.open(source).convert('RGBA'));alive=a[:,:,3]>0
 claimed=np.zeros((512,512),bool);masks={};layers={};layerpins={}
 collar=poly_mask(COLLARS[i])&alive
 for owner in PRIORITY:
  m=poly_mask(se[owner])
  if owner=='HelmetForeground':m|=collar
  m&=alive&~claimed;claimed|=m;masks[owner]=m
 masks['BodyRest']=~claimed
 for owner in OWNERS:
  v=np.where(masks[owner][:,:,None],a,0).astype(np.uint8);layers[owner]=v
  layerpins[owner]=pin(save(f'body-layers/{owner}/frame-{i}.png',Image.fromarray(v)))
  save(f'body-masks/{owner}/frame-{i}.png',Image.fromarray(np.where(masks[owner]&alive,255,0).astype(np.uint8)))
 assert np.array_equal(np.stack([v.astype(np.uint16) for v in layers.values()]).sum(axis=0),a)
 occupancy=np.stack([v[:,:,3]>0 for v in layers.values()]).sum(axis=0);assert np.all(occupancy[alive]==1)
 gx,gy=se['grip'];assert masks['NearHand'][gy,gx] and a[gy,gx,3]>=192
 swd,aff,deg,tp=rigid_sword(se['grip'],se['axis']);sp=save(f'sword-layers/frame-{i}-SWD050.png',swd);sm=np.array(swd)[:,:,3]>0
 assert not sm[0].any() and not sm[-1].any() and not sm[:,0].any() and not sm[:,-1].any()
 adjusted={};fits={}
 for component,A,B in [('Chest',CHEST_A[i],CHEST_B[i]),('ShoulderNear',NEAR_A[i],NEAR_B[i]),('ShoulderFar',FAR_A[i],FAR_B[i])]:
  p,original=armor_sources[component,i];assert original[A[1],A[0],3]>=128
  dx,dy=B[0]-A[0],B[1]-A[1];v=translate(original,dx,dy);adjusted[component]=v
  pp=save(f'armor-layers/{component}/frame-{i}.png',Image.fromarray(v))
  fits[component]={'source':pin(p),'A_artist_visible_component_xy':A,'source_A_actual_RGBA':original[A[1],A[0]].tolist(),'B_artist_visible_body_surface_xy':B,'body_B_actual_RGBA':a[B[1],B[0]].tolist(),'integer_translation_xy':[dx,dy],'rotation':0,'additional_scale':1,'resampled_after_curated':False,'adjusted':pin(pp),'all_component_nontransparent_pixels_preserved':True,'marker_authority':'Artist visible surface/attachment proposal, not bone, internal socket or physical simulation. A/B uncertainty3px; actual composite review remains required.'}
 ch=adjusted['Chest'];original_ch=armor_sources['Chest',i][1];dx,dy=fits['Chest']['integer_translation_xy'];hole=holes(original_ch[:,:,3]>=128);hy,hx=np.where(hole)
 center=[float(hx.mean()),float(hy.mean())];hole_moved=translate(np.repeat(hole[:,:,None],4,axis=2).astype(np.uint8),dx,dy)[:,:,0]>0
 arm_residual=(np.array(center)+[dx,dy]-VISIBLE_ARM_JUNCTION_B[i]).tolist()
 x0,y0,x1,y1=NECK_ROI[i];neck=np.zeros((512,512),bool);neck[y0:y1,x0:x1]=(original_ch[y0:y1,x0:x1,3]>=128)&(original_ch[y0:y1,x0:x1,:3].max(axis=2)<35)
 neck_moved=translate(np.repeat(neck[:,:,None],4,axis=2).astype(np.uint8),dx,dy)[:,:,0]>0
 fore=np.zeros((512,512),bool)
 for v in [layers['NearArmWithoutHand'],adjusted['ShoulderNear'],layers['HelmetForeground'],np.array(swd),layers['FarHandForeground'],layers['NearHand']]:fore|=v[:,:,3]>=128
 x0,y0,x1,y1=BELT_ROI[i];oldbelt=np.zeros((512,512),bool);v=a[y0:y1,x0:x1];oldbelt[y0:y1,x0:x1]=(v[:,:,3]>=128)&(v[:,:,0]>90)&(v[:,:,0]>1.25*v[:,:,1])&(v[:,:,1]>30)&(v[:,:,2]<100)
 residual_old_belt=oldbelt&~(ch[:,:,3]>=128)&~fore
 far=adjusted['ShoulderFar'];far_core=far[:,:,3]>=128
 fits['Chest'].update({'actual_true_hole_pixels':int(hole.sum()),'actual_hole_bbox':bbox(hole),'actual_hole_centroid_xy':center,'hole_centroid_after_translation':(np.array(center)+[dx,dy]).tolist(),'visible_source_sleeve_torso_junction_artist_xy':VISIBLE_ARM_JUNCTION_B[i],'hole_vs_visible_junction_residual_xy':arm_residual,'residual_semantics':'Visible-surface diagnostic only. Do not force a hidden joint claim. Large residual may be acceptable only if the opening is legally occluded and the visible garment/body join is actual-review sound.','original_neck_dark_ROI':NECK_ROI[i],'original_neck_dark_core_pixels':int(neck.sum()),'opaque_neck_prompt_deviation_preserved':True,'neck_dark_core_still_visible_after_all_foreground_candidates':int(np.count_nonzero(neck_moved&~fore)),'body_original_brown_belt_ROI':BELT_ROI[i],'old_belt_color_pixels_still_exposed_candidate':int(residual_old_belt.sum()),'true_aperture_pixels_visible_and_over_original_body':int(np.count_nonzero(hole_moved&~fore&(a[:,:,3]>=128))),'true_aperture_pixels_visible_outside_original_body':int(np.count_nonzero(hole_moved&~fore&~(a[:,:,3]>=128)))})
 fits['ShoulderFar']['core_pixels_outside_original_body']=int(np.count_nonzero(far_core&~(a[:,:,3]>=128)))
 stack=[('BodyRest',layers['BodyRest']),('ShoulderFar',far),('Chest',ch),('NearArmWithoutHand',layers['NearArmWithoutHand']),('ShoulderNear',adjusted['ShoulderNear']),('HelmetForeground',layers['HelmetForeground']),('IndependentSword',np.array(swd)),('FarHandForeground',layers['FarHandForeground']),('NearHand',layers['NearHand'])]
 whole=Image.new('RGBA',(512,512))
 for _,v in stack:whole=Image.alpha_composite(whole,Image.fromarray(v))
 swd_whole=Image.new('RGBA',(512,512))
 for _,v in stack:
  if _ not in ['ShoulderFar','Chest','ShoulderNear']:swd_whole=Image.alpha_composite(swd_whole,Image.fromarray(v))
 wp=save(f'whole-candidates/frame-{i}-LGT-SWD.png',whole);save(f'SWD-only-candidates/frame-{i}.png',swd_whole);wholes.append(whole);swd_wholes.append(swd_whole)
 root=old_rows[i]['display_root_from_paired_visible_shoes_PROPOSAL_ONLY'];roots.append(root)
 guard=np.array(Image.fromarray((guard_source*255).astype(np.uint8)).transform((512,512),Image.Transform.AFFINE,aff,resample=Image.Resampling.NEAREST))>0
 visible_guard=guard&~masks['NearHand']&~masks['FarHandForeground']
 row={'frame':i,'Dodge218_source':pin(source),'source_native_id':218,'five_body_layers':layerpins,'body_partition_exact_RGBA_reconstruction':True,'body_owners_exclusive':True,'HelmetForeground_includes_actual_visible_gray_collar_only':{'artist_polygon':COLLARS[i],'source_pixel_count':int(collar.sum()),'source_pixels_only_no_invented_lining':True,'semantic_review_pending':True},'NearHand_boundary_changed_only_phase3':i==3,'NearHand_original_own_source_polygon':se['NearHand'],'author_binding':{'previous_Grip':old_grips[i],'Grip':se['grip'],'Grip_source_RGBA':a[gy,gx].tolist(),'Axis_artist_choice':se['axis'],'unit_axis': [math.cos(math.radians(deg)),math.sin(math.radians(deg))],'Axis_not_measured_bone_or_handle':True,'angle_degrees':deg,'SwordScale':.50,'sword_source':pin(SWORD),'source_sword_grip':[99,256],'sword_layer':pin(sp),'inverse_affine':list(aff),'visible_guard_mask_pixels_after_hand_candidates':int(visible_guard.sum()),'visible_guard_not_handhold_certification':True,'tip_reference_xy':tp([482,256]),'sword_canvas_clipped':False},'root_proposal':root,'standing_basis_source_height':416,'display_body_height':72,'canvas_display_px':CANVAS,'per_frame_height_normalized':False,'armor_integer_fits':fits,'nine_slot_order':[n for n,_ in stack],'whole_candidate':pin(wp),'sourcefit_accepted':False,'TrialAllowed':False,'native_receipts':None}
 rows.append(row)
 own=np.zeros_like(a)
 for owner in OWNERS:own[masks[owner]&alive,:3]=colors[owner];own[masks[owner]&alive,3]=a[masks[owner]&alive,3]
 owner_panels.append(Image.fromarray(own))
 bg=Image.new('RGBA',(1280,720),(45,48,54,255));bg=Image.alpha_composite(bg,place(whole,root));dr=ImageDraw.Draw(bg)
 dr.text((24,20),f'OFFLINE Dodge218 LGT+SWD phase{i} / t={100*i}ms / 416->72 common scale',font=font(22),fill='white');dr.text((24,54),'Integer armor fit / original collar pixels / revised artist grip / candidate unaccepted',font=font(19),fill='white')
 save(f'preview-frames/frame-{i:03d}.png',bg.convert('RGB'));displays.append(bg.convert('RGB'))

# Existing accepted Ready source assembly is diagnostic-only; no Ready pixels/masks are reused above.
ready_base=ROOT/'source-assets/production/fairytale-lgt-readability-v003/ready-integer-assembly-v001'
E278=next(Path('E:/OurGame/Knight/过程图稿与视频').glob('*v278/source-size-SHA256.json'));ei=read(E278);rd=read(READY_MARKERS)['frames'][0]
ready_pins=[];ready_layers={}
for name,folder in [('BodyRest','body-layers/BodyRest'),('NearArmWithoutHand','body-layers/NearArmWithoutHand'),('NearHand','body-layers/NearHand'),('ShoulderFar','armor-layers/FarShoulder'),('Chest','armor-layers/Chest'),('ShoulderNear','armor-layers/NearShoulder')]:
 p=ready_base/f'{folder}/frame-0.png';sha=pin(p)['sha256'];rr=next(r for r in ei['files'] if r['sha256']==sha);ep=E278.parent/rr['retained_relative'];assert p.read_bytes()==ep.read_bytes();ready_layers[name]=np.array(Image.open(p).convert('RGBA'));ready_pins.append(pin(p))
rs,raff,rdeg,rtp=rigid_sword(rd['grip_candidate_px'],rd['handle_axis_candidate_xy']);ready_layers['IndependentSword']=np.array(rs)
rwhole=Image.new('RGBA',(512,512))
for name in ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','IndependentSword','NearHand']:rwhole=Image.alpha_composite(rwhole,Image.fromarray(ready_layers[name]))
save('reference-only/Ready158-current-LGT-existing-source-assembly.png',rwhole)
rr=rd['source_root_px'];last=rows[3];gdelta=((np.array(rd['grip_candidate_px'])-rr)-(np.array(last['author_binding']['Grip'])-roots[3]))*K
tdelta=((np.array(rtp([482,256]))-rr)-(np.array(last['author_binding']['tip_reference_xy'])-roots[3]))*K
join=write('Dodge3-to-current-Ready-LGT-known-source-join-v001.json',{'Ready_source_layers':ready_pins,'Ready_marker_contract':pin(READY_MARKERS),'Ready_Root':rr,'Dodge3_Root':roots[3],'shared_body_canvas_px':CANVAS,'Ready_minus_Dodge3_grip_display_xy':gdelta.tolist(),'Ready_minus_Dodge3_tip_display_xy':tdelta.tolist(),'angle_delta_degrees':rdeg-last['author_binding']['angle_degrees'],'mask_or_identity_copied_into_Dodge':False,'zeroPop':False,'native_accepted':False})
full=Image.new('RGB',(2048,562),(45,48,54));torso=Image.new('RGB',(1600,650),(45,48,54));fists=Image.new('RGB',(1600,390),(45,48,54));owners=full.copy();df=ImageDraw.Draw(full);dt=ImageDraw.Draw(torso);dh=ImageDraw.Draw(fists);do=ImageDraw.Draw(owners)
for i,im in enumerate(wholes):
 full.paste(im,(512*i,42),im);df.text((512*i+10,10),f'Dodge{i} / sourcefit candidate',font=font(22),fill='white')
 torso_crop=im.crop((100,200 if i!=1 else 255,420,420 if i!=1 else 475)).resize((400,600),Image.Resampling.NEAREST);torso.paste(torso_crop,(400*i,40),torso_crop);dt.text((400*i+8,8),f'Dodge{i}: torso/shoulders/oldbelt',font=font(19),fill='white')
 gx,gy=SEEDS[i]['grip'];crop=im.crop((gx-50,gy-45,gx+50,gy+45)).resize((400,360),Image.Resampling.NEAREST);fists.paste(crop,(400*i,30),crop);dh.text((400*i+8,7),f'Dodge{i}: revised own fist fit',font=font(20),fill='white')
 owners.paste(owner_panels[i],(512*i,42),owner_panels[i]);do.text((512*i+8,10),f'Dodge{i}: own collar partition',font=font(20),fill='white')
save('presentation/Dodge4-LGT-SWD-all-full-candidate.png',full);save('presentation/Dodge4-torso-shoulder-neck-oldbelt-closeups.png',torso);save('presentation/Dodge4-revised-grip-four-fists-4x.png',fists);save('presentation/Dodge4-own-collar-five-partitions.png',owners)
jc=Image.new('RGBA',(1280,640),(45,48,54,255));jc=Image.alpha_composite(jc,place(wholes[3],roots[3],(1280,640),(320,560),1.));jc=Image.alpha_composite(jc,place(rwhole,rr,(1280,640),(960,560),1.));dj=ImageDraw.Draw(jc)
dj.text((20,12),'Dodge3 new LGT / actual source root',font=font(24),fill='white');dj.text((660,12),'Current Ready LGT / existing binding',font=font(24),fill='white');dj.line((16,560,1264,560),fill=(110,110,110));dj.text((20,601),f'Ready-Dodge3 grip [{gdelta[0]:+.2f},{gdelta[1]:+.2f}]px; sourcejoin only, not zero-pop/native.',font=font(20),fill='white');save('presentation/Dodge3-to-current-Ready-LGT-source-join.png',jc.convert('RGB'))
gif=OUT/'presentation/Dodge4-LGT-SWD-finite400ms-NO-LOOP.gif';displays[0].save(gif,save_all=True,append_images=displays[1:],duration=[100]*4,disposal=2,optimize=False)
with Image.open(gif) as im:
 ds=[]
 for i in range(im.n_frames):im.seek(i);ds.append(im.info['duration'])
 assert im.n_frames==4 and ds==[100]*4 and 'loop' not in im.info
ff=Path(imageio_ffmpeg.get_ffmpeg_exe());mp4=OUT/'presentation/Dodge4-LGT-SWD-finite400ms-offline.mp4';argv=[str(ff),'-hide_banner','-loglevel','info','-framerate','10','-i',str(OUT/'preview-frames/frame-%03d.png'),'-frames:v','4','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)]
r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-encode.log',r.stdout+r.stderr);assert r.returncode==0
dv=[str(ff),'-hide_banner','-i',str(mp4),'-map','0:v:0','-f','null','-'];dec=subprocess.run(dv,capture_output=True,text=True,encoding='utf-8');write('logs/ffmpeg-decode.log',dec.stdout+dec.stderr);assert dec.returncode==0 and 'Duration: 00:00:00.40' in dec.stderr and int(re.findall(r'frame=\s*(\d+)',dec.stderr)[-1])==4
preview=write('actual-finite400ms-offline-preview-receipt-v001.json',{'GIF':pin(gif),'actual_frames':4,'actual_ms':ds,'loop':False,'MP4':pin(mp4),'actual_encode_command':argv,'actual_decode_command':dv,'actual_decoded_frames':4,'actual_duration_ms':400,'native_action_actor_distance_receipts':None})
contract=write('Dodge218-LGT234-236-own-five-layers-SWD050-integer-fit-candidate-v001.json',{'schema':'Dodge218-LGT234-236-own-source-integer-fit-candidate-v001','previous_frozen_sourcefit':pin(old_contract),'previous_E474_retention':pin(E474),'reused_pure_function_source':pin(OLD_SCRIPT),'actual_source_audit':pin(AUDIT),'component_original_QA':armor_receipts,'writable_true_hole_toy_proof':pin(toy_receipt),'source_preservation':'All5bodylayers copy own218RGBA with exclusive exact reconstruction; armor234/235/236 only integer translated; SWD only rigid author .50 transform. No body/armorpainting, erasure, hidden lining, wholebody BodyRest, Ready/Hurt mask reuse or perphase scale.','source_neck_prompt_failure':'Chest234 still has opaque black neck interior. Original request and source failure preserved; proposed original gray collar/helmet foreground MAY legally cover it, subject to actual full/closeup review. This is not declaring original negative-aperture spec passed.','runtime_candidate_texture_count_if_accepted':32,'runtime_candidate_texture_roles':'20 ownbody +12 armor; originalSword reused, not a newSwordsource. No import/namespace/runtime acceptance yet.','row_common_scale':{'standing_source':416,'display_height':72,'canvas_px':CANVAS,'perphase_normalization':False},'frames':rows,'Ready_join':pin(join),'finite_preview':pin(preview),'newmedia_viewed':False,'newmedia_E_retained':False,'sourcefit_accepted':False,'TrialAllowed':False,'native_actual_receipts':None})
write('HANDOFF.md','''Dodge218 + 当前棕皮234/235/236 + 独立军剑.50有限试拼，所有新媒体未View，先Root E两SHA再审。

五个身体owner全部来自各自218原件，排他RGBA重构完全相等。NEW HelmetForeground显式含原图真实可见灰领/颈折边foreground；这只是源像素重新归属，未画内衬/擦黑洞。NEW Grip从实际opaque棕皮拳面向外指侧移动，只有phase3把自身手套边缘多收进NearHand；Axis艺术选择/.50不变。原E474/freeze保留。

三甲原官方shared尺度固定，全部仅整数平移，512/512/256门与原inspect motionwarnings保留。Chest234有opaque黑领内面违反原true-green提示，此语义失败未改写；仅评估真实头盔/灰领是否自然遮挡，无法自然覆盖就不能准入。腰扣A/B严格对齐，真实腋孔中心与可见袖/躯干接合点的残差列出，尤其phase1不可凭mask统计掩盖错误姿态。Far离体像素、旧带残留与黑领可见数均诊断，不自动接受。

32PNG只是未来被实际审过时可用的20身体+12甲候选，现无namespace/import/Source/native收据。416→72全行常量、四原鞋root提案，不逐帧身高归一/不足锁。400ms离线4×100，无loopGIF+实际解码4帧MP4，与现Ready棕皮源装配同ground对照，保留pop，不替代UE装备保持验收。
''')
freeze=write('Dodge-LGT-SWD-limited-sourcefit-freeze-v001.json',{'schema':'Dodge-LGT-SWD-limited-sourcefit-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'newmedia_View':False,'sourcefit_accepted':False,'TrialAllowed':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/有限试拼完整包');shutil.copyfile(Path(__file__),MEDIA/'原件'/Path(__file__).name);(MEDIA/'展示副本').mkdir()
for p in sorted((OUT/'presentation').iterdir()):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Dodge218棕皮三层军剑有限试拼','version':'v001','status':'UNVIEWED candidate; all original QA/spec deviations retained; sourcefit/native unaccepted','candidate':OUT.as_posix(),'contract':pin(contract),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'contract':pin(contract),'freeze':pin(freeze),'four_visible_dark_neck_core_px':[r['armor_integer_fits']['Chest']['neck_dark_core_still_visible_after_all_foreground_candidates'] for r in rows],'four_old_belt_color_residual_px':[r['armor_integer_fits']['Chest']['old_belt_color_pixels_still_exposed_candidate'] for r in rows],'four_armhole_visible_junction_residuals':[r['armor_integer_fits']['Chest']['hole_vs_visible_junction_residual_xy'] for r in rows],'four_far_outside_body_core_px':[r['armor_integer_fits']['ShoulderFar']['core_pixels_outside_original_body'] for r in rows],'four_visible_guard_px':[r['author_binding']['visible_guard_mask_pixels_after_hand_candidates'] for r in rows],'Ready_minus_Dodge3_grip_display_xy':gdelta.tolist(),'newmedia_View':False},ensure_ascii=False,indent=2))
