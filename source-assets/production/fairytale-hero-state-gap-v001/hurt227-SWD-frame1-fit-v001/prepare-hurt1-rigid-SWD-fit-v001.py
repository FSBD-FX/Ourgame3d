from pathlib import Path
import hashlib,json,math,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('F:/Ourgame');BASE=ROOT/'source-assets/production/fairytale-hero-state-gap-v001'
HERE=Path(__file__).resolve().parent
assert HERE==BASE/'hurt227-SWD-frame1-fit-v001'
OUT=HERE/'candidate-v001';assert not OUT.exists();OUT.mkdir()
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Hurt227单帧军剑闭握配准候选_v001';assert not MEDIA.exists()
HURT_RUN=BASE/'hero227-hurt4-extraction-v001/runs/run-hurt227-shared-HD-v001'
BODY=HURT_RUN/'curated/frame-1.png';STANDING=HURT_RUN/'curated/frame-3.png'
SWORD=ROOT/'source-assets/production/first-unit-animation-v002/components/military-sword-clean-v001.png'
E_SWORD=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-15_圆盔骑士新基准_v003/原件/components/military-sword-clean-v001.png')
E_GATE=BASE/'hero227-hurt4-extraction-v001/E415-before-curated-View-check-v001.json'
VISIBLE_PROPOSALS=BASE/'hero227-hurt4-extraction-v001/visible-hands-review-v001/visible-hand-proposals-v001.json'
HUD=ROOT/'UnrealGame/Source/CodexDungeon/DungeonHUD.cpp';PRES=ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordPresentation.cpp';PROFILE=ROOT/'UnrealGame/Source/CodexDungeon/DungeonFairytaleSwordBodyV001.inl'

def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def save(rel,im):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True);im.save(p);return p
def box(mask):
 y,x=np.where(mask)
 return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

assert pin(BODY)['sha256']=='21b759173e6e2b4644a0a0eeb9ca374d48689a7e46adb6309f6a04cd12e48621'
assert pin(SWORD)['sha256']=='2efb5519fb3c7ed5a63e58d00c84e39aa02355274af36b43c1775570badded5a'
assert SWORD.read_bytes()==E_SWORD.read_bytes()
gate=json.loads(E_GATE.read_text(encoding='utf-8'));assert gate['root_explicit_View_allowed'] and gate['differences']==0
assert BODY.read_bytes()==Path(gate['frames'][1]['E']['path']).read_bytes()
body=np.array(Image.open(BODY).convert('RGBA'));sword=Image.open(SWORD).convert('RGBA');standing=np.array(Image.open(STANDING).convert('RGBA'))
assert body.shape==(512,512,4) and sword.size==(512,512)
for name,p in [('Hurt227-frame1-original.png',BODY),('Hurt227-frame3-standing-reference-original.png',STANDING),('military-sword-clean-v001-original.png',SWORD)]:
 d=OUT/'source-readcopies'/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)

# New source-specific visible fist segmentation; no Ready or previous fist polygon is read/copied.
# Boundary follows the visible glove/ink silhouette and an author cut along its cuff seam.
polygon=[(175,273),(181,265),(190,261),(201,260),(209,265),(215,273),(220,282),(220,289),
 (216,295),(214,305),(210,312),(202,319),(193,324),(180,323),(170,319),(163,312),
 (159,303),(159,292),(162,284),(168,278)]
poly_image=Image.new('L',(512,512),0);ImageDraw.Draw(poly_image).polygon(polygon,fill=255)
selected=(np.array(poly_image)>0)&(body[:,:,3]>0)
hand=np.where(selected[:,:,None],body,0).astype(np.uint8)
rest=np.where(selected[:,:,None],0,body).astype(np.uint8)
assert not np.any((hand[:,:,3]>0)&(rest[:,:,3]>0))
reconstruction=np.where(selected[:,:,None],hand,rest)
assert np.array_equal(reconstruction,body)
assert np.array_equal(rest[~selected],body[~selected])
hand_path=save('layers/Hurt1-NearHandForeground-exact-sourceRGBA.png',Image.fromarray(hand))
rest_path=save('layers/Hurt1-BodyRest-exact-sourceRGBA.png',Image.fromarray(rest))
mask_path=save('masks/Hurt1-visible-near-fist-author-segmentation-L.png',Image.fromarray(np.where(selected,255,0).astype(np.uint8),'L'))

GRIP=np.array([194.,289.]);AXIS=np.array([.8,.6]);SCALE=.50;SWORD_GRIP=np.array([99.,256.])
assert np.isclose(np.linalg.norm(AXIS),1.) and selected[289,194]
actual_grip_rgba=body[289,194].tolist();assert actual_grip_rgba==[191,91,41,255]
c,s=AXIS;coeff=(c/SCALE,s/SCALE,float(SWORD_GRIP[0]-(c*GRIP[0]+s*GRIP[1])/SCALE),
 -s/SCALE,c/SCALE,float(SWORD_GRIP[1]-(-s*GRIP[0]+c*GRIP[1])/SCALE))
# Rigid asset transform only, premultiplied for stable transparent-edge interpolation.
placed=sword.convert('RGBa').transform((512,512),Image.Transform.AFFINE,coeff,resample=Image.Resampling.BICUBIC).convert('RGBA')
sword_path=save('layers/Hurt1-SWD-rigid-scale050-axis080060.png',placed)
full=Image.alpha_composite(Image.alpha_composite(Image.fromarray(rest),placed),Image.fromarray(hand))
whole_path=save('composite/Hurt1-SWD-held-candidate-512RGBA.png',full)

def transform_point(p):
 q=np.array(p,dtype=float)-SWORD_GRIP
 return (GRIP+SCALE*np.array([[c,-s],[s,c]])@q).tolist()
assert np.allclose(transform_point([99,256]),GRIP)
# Potential entry/exit through the source-derived fist silhouette are artist-axis intersections,
# not measurements of a real absent source handle or recovered internal grip cavity.
samples=[]
for t in np.arange(-100.,100.25,.25):
 p=GRIP+t*AXIS;x,y=np.rint(p).astype(int)
 if 0<=x<512 and 0<=y<512 and selected[y,x]:samples.append(float(t))
entry_t,exit_t=min(samples),max(samples)
entry=(GRIP+entry_t*AXIS).tolist();exit=(GRIP+exit_t*AXIS).tolist()
sa=np.array(sword);guard_source_mask=(sa[:,:,3]>0)
yy,xx=np.indices((512,512));guard_source_mask&=(xx>=134)&(xx<159)&(yy>=210)&(yy<303)
guard_mask=Image.fromarray((guard_source_mask*255).astype(np.uint8),'L').transform((512,512),Image.Transform.AFFINE,coeff,resample=Image.Resampling.NEAREST)
guard=np.array(guard_mask)>0
wrist_roi=[136,269,175,315];wr=np.zeros((512,512),dtype=bool);wr[wrist_roi[1]:wrist_roi[3],wrist_roi[0]:wrist_roi[2]]=True
guard_wrist_overlap=int(np.count_nonzero(guard&wr&(body[:,:,3]>=128)))
assert guard_wrist_overlap==0
placed_alpha=np.array(placed)[:,:,3]
assert not np.any(placed_alpha[0,:]) and not np.any(placed_alpha[-1,:]) and not np.any(placed_alpha[:,0]) and not np.any(placed_alpha[:,-1])

# Row scale remains shared. StandingRoot is a transparent display-ground convention, not a bone.
CANVAS=72.*512./416.;DISPLAY_PER_SOURCE=CANVAS/512.;STANDING_ROOT=[256.,464.]
ys,xs=np.where(standing[:,:,3]>=128);assert int(ys.min())==48 and int(ys.max())==463
row_measure=[]
for i in range(4):
 p=HURT_RUN/f'curated/frame-{i}.png';a=np.array(Image.open(p).convert('RGBA'));y,x=np.where(a[:,:,3]>=128)
 row_measure.append({'frame':i,'source':pin(p),'visible_body_core_bbox':box(a[:,:,3]>=128),'visible_crown_to_sole_extent':int(y.max()+1-y.min()),'displayed_extent_with_one_row_scale':float((y.max()+1-y.min())*DISPLAY_PER_SOURCE),'fitted_or_normalized_perframe':False})

inputs=write('readonly-source-and-binding-evidence-v001.json',{'schema':'Hurt227-SWD-readonly-source-and-binding-evidence-v001','body':pin(BODY),'standing_reference':pin(STANDING),'source_frame_retention':pin(E_GATE),'body_exact_E_copy':pin(Path(gate['frames'][1]['E']['path'])),'newhand_proposal_reference':pin(VISIBLE_PROPOSALS),'independent_SWD_source':pin(SWORD),'SWD_retained_E_original':pin(E_SWORD),'source_E_exact':True,'read_only_actual_code_pins':[pin(HUD),pin(PRES),pin(PROFILE)],'actual_code_facts':[{'file':HUD.as_posix(),'line':649,'fact':'GetCandidateSword loads /Game/Production/FirstBatch/v002/CandidateComponents/T_military_sword_v002.T_military_sword_v002.'},{'file':PRES.as_posix(),'line':308,'fact':'UniformWeaponScale.50, independentweaponComponentGrip[99,256], positivebladeaxis controlled by authoredMarkerAxis; texture rotated aboutGrip.'},{'file':PROFILE.as_posix(),'line':18,'fact':'BodyCanvas72*512/416. Root/Grip fromstate markers, not perframebbox normalization.'}],'scope_limit':'Existing texture asset/source identity and .50 binding are reused; no claim current native presenter consumes Hurt source or this offline candidate. Source snapshots not rewritten.'})
contract=write('Hurt1-authored-Grip-Axis-source-mask-transform-and-row-registration-v001.json',{
 'schema':'HeroHurt227-frame1-real-independentSWD-fit-candidate-v001','status':'UNVIEWEDCOMPOSITECANDIDATE/RootEgate/TrialAllowedfalse','frame':1,'identity_and_binding_evidence':pin(inputs),
 'body_row_registration':{'source_canvas':[512,512],'shared_extraction_scale':.7074829931972789,'standing_basis_frame':3,'standing_crown_core_y':48,'standing_floor_y':464,'standing_equivalent_source_height':416,'display_target_standing_height_px':72.,'display_canvas_px':CANVAS,'source_to_display_scale':DISPLAY_PER_SOURCE,'standingRoot_artist_xy':STANDING_ROOT,'root_role':'Fixed transparent display-ground convention consistentwithReady; not measuredsolemidpoint/hiddenbone/COM orfootlock. Same rowroot/scale held; actualshoecontact/rowjoins neednative review.','all_four_source_extents_with_same_mapping':row_measure,'per_frame_normalization':False},
 'new_hand_source':{'source':pin(BODY),'visible_glove_ROI':[155,258,222,326],'wrist_cuff_ROI':wrist_roi,'foreground_polygon_artist_xy':list(map(list,polygon)),'mask':pin(mask_path),'source_RGBA_foreground':pin(hand_path),'body_without_hand':pin(rest_path),'segmentation_method':'Authored boundary following visible Hurt1 glove/ink and visible wrist seam; polygon clipped to actual nonzero sourcealpha. ExactRGBAcopy within mask. No Ready polygon/hand/mask used.','semantic_uncertainty':'Boundary/seam is an artist source-segmentation proposal; no realhilt/cavity/anatomicalbones in source. Fistmask/replay acceptance pendingactualcomposite review.','foreground_selected_pixels':int(np.count_nonzero(selected)),'source_rgba_at_author_grip':actual_grip_rgba,'body_without_hand_outside_mask_unchanged':True,'exclusive_partition_reconstructs_original_RGBA_all_pixels_exact':True},
 'artist_binding':{'Grip_xy':GRIP.tolist(),'Grip_role':'Author selected visiblepalm sourcepixel, initially fromE417proposal[194289], checkedactualRGBA. Not measurementofrealhandlecenter.','Axis_unit_xy':AXIS.tolist(),'Axis_role':'Explicitartistchoice towardlower-right tokeepbladeoffeyesandtipabovefloor; not inferredfromglovefolds, wristorhiddenbone. Sourcehasnohandleanddoesnot uniquelydetermineaxis.','source_weapon_grip_xy':SWORD_GRIP.tolist(),'source_weapon_axis_xy':[1.,0.],'weapon_scale_relative_to_body_canvas':SCALE,'rotation_degrees_clockwise_y_down':math.degrees(math.atan2(s,c)),'forward_transform':'dest=HurtGrip+0.50*R(axis)*(sourceSwordPixel-[99,256])','inverse_PIL_affine':list(coeff),'resample':'Pillow premultipliedRGBa bicubic; body/handsourceRGBA not resampled or redrawn. Offlinecandidate not pixel-for-pixelUErasterequivalence.','Sword_layer':pin(sword_path),'source_grip_maps_exactly_to_Hurt_grip':True,'authored_axis_mask_intersections':{'butt_side_entry_t':entry_t,'blade_side_exit_t':exit_t,'entry_xy':entry,'exit_xy':exit,'role':'Artistaxis crossingactualhandmask outline only, not observedshaftends orproofholdcontact.'},'guard_source_ROI':[134,210,159,303],'transformed_guard_bbox':box(guard),'guard_overlap_actual_wristROI_core_pixels':guard_wrist_overlap,'guard_check_limit':'PixelROIcheckonly; naturalthumb/hiltentryandguardplacement needRootactualcompositeview.','complete_placed_weapon_alpha_bbox':box(placed_alpha>0),'placed_weapon_touches_output_edge':False,'source_tip_proposal_xy':[482.,256.],'transformed_tip_proposal_xy':transform_point([482,256]),'tip_above_artist_ground_source_px':float(464.-transform_point([482,256])[1])},
 'stack_back_to_front':['Hurt1BodyRest-exactsourceRGBA','IndependentSWD-rigid050-artistaxis','Hurt1NearHandForeground-exactsourceRGBA'],
 'whole_composite':pin(whole_path),'acceptance':{'Sourcebodyclosedhand_already_Root_pose_candidate':True,'independentSword_existing_identity_and_scale_reused':True,'new_composite_viewed':False,'true_SWD_contact_accepted':False,'all_four_held_Hurt_accepted':False,'LGT_accepted_or_prepared_here':False,'native_or_runtime_accepted':False,'TrialAllowed':False,'next':'RootEretainsnewFbatchthenactualsingleframeview. ResolveGripAxis/maskcontactbeforeexpandingallfour. NoAI/sourcepainting/SourceContenttoolsledgerUEchanges.'}})

font_path=next(p for p in [Path('C:/Windows/Fonts/arial.ttf'),Path('C:/Windows/Fonts/segoeui.ttf')] if p.exists());font=lambda n:ImageFont.truetype(str(font_path),n)
# New presentation derivatives are deliberately not viewed before Root E retention.
presentation=Image.new('RGB',(1024,580),(45,48,54));d=ImageDraw.Draw(presentation)
d.text((24,14),'Hurt227 frame1 original',font=font(24),fill='white');d.text((536,14),'SWD rigid .50 / artist axis (.8,.6)',font=font(23),fill='white')
presentation.paste(Image.fromarray(body),(0,54),Image.fromarray(body));presentation.paste(full,(512,54),full)
save('presentation/source-and-SWD-fit-512-side-by-side.png',presentation)
detail=Image.new('RGB',(840,400),(45,48,54));dd=ImageDraw.Draw(detail)
for i,(im,label) in enumerate([(Image.fromarray(body),'Original source'),(full,'Rigid sword + NEW fist mask')]):
 crop=im.crop((136,248,236,338)).resize((400,360),Image.Resampling.NEAREST);detail.paste(crop,(i*420,40),crop);dd.text((i*420+8,9),label,font=font(22),fill='white')
save('presentation/Hurt1-contact-source-and-composite-4x-nearest.png',detail)
diagram=Image.new('RGB',(512,512),(45,48,54));diagram.paste(Image.fromarray(body),(0,0),Image.fromarray(body));dd=ImageDraw.Draw(diagram)
dd.line(polygon+[polygon[0]],fill=(255,80,80),width=2)
e=(GRIP-38*AXIS).tolist();f=(GRIP+72*AXIS).tolist();dd.line([tuple(e),tuple(f)],fill=(90,210,255),width=2)
dd.ellipse((190,285,198,293),outline=(255,255,100),width=2);dd.rectangle(wrist_roi,outline=(180,160,255),width=1)
dd.text((8,8),'DIAGNOSTIC: author mask / axis, not bones',font=font(18),fill='white')
save('presentation/Hurt1-new-source-mask-and-artist-axis-diagnostic.png',diagram)
native=Image.new('RGB',(1280,720),(45,48,54));nd=ImageDraw.Draw(native)
# Round only the presentation raster; exactfloatcanvas and coordinate law remain in contract.
small=full.resize((round(CANVAS),round(CANVAS)),Image.Resampling.LANCZOS)
native.paste(small,(596,410),small);nd.text((28,28),'OFFLINE single-frame candidate. Approx89px canvas / standing72px; no native/LGT acceptance.',font=font(22),fill='white')
save('presentation/Hurt1-SWD-display-size-offline-candidate.png',native)
write('HANDOFF.md','''# Hurt227 frame1 + 独立军剑：配准候选v001\n\n复用已核对E原件的独立军剑clean源（SHA2efb5519...badded5a），实际Ready绑定sourceGrip[99,256]及统一scale.50。Hurt1自身source（SHA21b75917...e48621）实际闭拳分割为BodyRest和NearHandForeground，二者排他且全部RGBA逐像素重构原件；没有读取/套用Ready hand mask。军剑只作确定性刚性旋转、平移和.50缩放，原body/手RGBA未绘改。\n\nGrip[194,289]是作者选定的可见掌面像素；Axis[.8,.6]明确是右下斜持的艺术选择，源图没有真实柄或可唯一测出的孔轴。已记录轴穿手mask的两端位置、真实护手alpha对腕口ROI零交叠及完整剑边界；这些数值不等于握持通过，必须看合成。\n\nHurt227同行最大/站立末帧冠底416，固定Canvas72×512/416=88.6154；standingRoot[256,464]是固定地面显示基准，不是隐藏骨或足锁。Hurt1自然收缩显示约67.33px，不能逐帧拉回72。近手foreground覆盖剑柄、其余body在后；新mask边界/遮挡仍待Root实际审。\n\n候选图、放大手部和约实际显示大小图均尚未View。先Root E两SHA保全本批后审单帧；通过/修正后再扩四帧。本批无AI、Source/Content/Roottools/ledger/UE改动，LGT/native、完整Hurt4装备保持和状态衔接仍未完成。\n''')
handoff=write('Root-Hurt1-SWD-fit-review-handoff-v001.json',{'schema':'Hurt227-frame1-SWD-realprop-composite-Root-review-handoff-v001','contract':pin(contract),'source_and_binding_evidence':pin(inputs),'composite':pin(whole_path),'canonical_F_media':MEDIA.as_posix(),'new_images_viewed':False,'new_images_E_retained':False,'TrialAllowed':False,'next_gate':'RootEretain+2SHAthenactualsingleframecontactreview; nofourframeexpansionuntilthiscontactbasisreviewed.','known_gaps':['Actualcompositehilt/guard/maskcontactnotyetviewed','LGT/Hurtarmorunprepared','Hurt4heldrowandnativeplaybacknotcomplete']})
write('candidate-freeze-v001.json',{'schema':'Hurt227-frame1-SWD-fit-freeze-v001','files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'script':pin(Path(__file__)),'new_media_viewed':False,'source_art_redrawn':False,'Source_Content_Roottools_ledger_UE_modified':False})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/单帧配准候选完整包');(MEDIA/'展示副本').mkdir()
for p in sorted((OUT/'presentation').glob('*.png')):shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Hurt227单帧军剑闭握配准候选','version':'v001','status':'newcompositeandmaskUNVIEWED;RootE+actualreviewgated;Trialfalse;LGTnativeHurt4notcomplete','source':OUT.as_posix(),'handoff':pin(handoff),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'handoff':pin(handoff),'contract':pin(contract),'source_hand_pixels':int(selected.sum()),'hand_mask_axis_entry_exit':[entry,exit],'guard_wrist_overlap':guard_wrist_overlap,'weapon_bbox':box(placed_alpha>0),'shared_display_canvas':CANVAS,'F_files':sum(p.is_file() for p in MEDIA.rglob('*')),'F_bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'new_images_viewed':False},ensure_ascii=False,indent=2))
