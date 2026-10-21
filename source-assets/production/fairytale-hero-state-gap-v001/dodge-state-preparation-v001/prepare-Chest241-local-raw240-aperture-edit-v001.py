from pathlib import Path
from collections import deque
import hashlib,json,math,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('F:/Ourgame');HERE=Path(__file__).resolve().parent
OUT=HERE/'Chest241-local-raw240-edit-input-v001'
MEDIA=ROOT/'过程图稿与视频/2026-10-18_钟盔Dodge胸衣241原稿局部孔位编辑标准输入_v001'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');PY=SG/'.venv/Scripts/python.exe'
assert Path(sys.executable).resolve()==PY.resolve() and not OUT.exists() and not MEDIA.exists();OUT.mkdir()
sys.path.insert(0,str(SG));import sprite_gen.frames.extract as native
EXTRACT=SG/'sprite_gen/frames/extract.py'
assert hashlib.sha256(EXTRACT.read_bytes()).hexdigest()=='f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539'
RUN=HERE/'official-process-runs-v001/chest-native240/run-shared-HD-v001'
REC=RUN/'extraction-receipt-v001.json'
FIT=HERE/'LGT240-235-236-original-owner-integer-fit-v001/Dodge218-Chest240-Near235-Far236-original-owner-SWD050-integer-fit-candidate-v001.json'
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(rel,v):
 p=OUT/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 return p
def closed_regions(a):
 im=Image.fromarray(np.where(a[:,:,3]>=128,255,0).astype(np.uint8)).copy();ImageDraw.floodfill(im,(0,0),128,thresh=0);remain=np.array(im)==0;parts=[]
 while remain.any():
  sy,sx=np.argwhere(remain)[0];q=deque([(int(sy),int(sx))]);remain[sy,sx]=False;coords=[]
  while q:
   y,x=q.popleft();coords.append((x,y))
   for ny,nx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
    if 0<=ny<a.shape[0] and 0<=nx<a.shape[1] and remain[ny,nx]:remain[ny,nx]=False;q.append((ny,nx))
  if len(coords)>=64:
   pts=np.array(coords);parts.append({'area':len(pts),'centroid':pts.mean(axis=0),'bbox':np.array([pts[:,0].min(),pts[:,1].min(),pts[:,0].max()+1,pts[:,1].max()+1],float)})
 parts.sort(key=lambda r:-r['area']);assert len(parts)==2 and parts[0]['centroid'][0]<parts[1]['centroid'][0]
 return parts
receipt=read(REC);fit=read(FIT);raw=Path(receipt['F_raw']['path']);assert pin(raw)==receipt['F_raw']
assert receipt['shared_row_fit']['scale']==.3021148036253776
for _ in range(2):assert raw.read_bytes()==Path(receipt['E_raw']['path']).read_bytes()
source=Image.open(raw);assert source.size==(2172,724);source_rgba=source.convert('RGBA');raw_array=np.array(source_rgba)
keyed=native.remove_chroma_background(source,(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
components=native.connected_components(keyed);seeds=sorted(sorted(components,key=lambda r:r['area'],reverse=True)[:4],key=lambda r:r['center_x']);images=native.extract_component_images(keyed,4)
assert len(images)==4
refs=OUT/'references';refs.mkdir();target=refs/'EDIT-TARGET-exact-native240-raw.png';shutil.copyfile(raw,target);assert pin(target)['sha256']==pin(raw)['sha256']
inherited=OUT/'inherited-sprite-request-BYTE-EXACT-from240.json';shutil.copyfile(RUN/'sprite-request.json',inherited);assert inherited.read_bytes()==(RUN/'sprite-request.json').read_bytes()
overlay=Image.new('RGBA',source.size,(0,0,0,0));d=ImageDraw.Draw(overlay);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
maps=[];edit_rows=[]
for i,(seed,im) in enumerate(zip(seeds,images)):
 assert hashlib.sha256(im.tobytes()).hexdigest()==receipt['shared_row_fit']['raw_component_RGBA_sha256'][i]
 assert native.component_group_image(keyed,[seed]).tobytes()==im.tobytes(), 'Do not infer origin if satellites differ'
 raw_box=np.array(seed['bbox'],float);inner=np.array(im.getbbox(),int);crop=im.crop(tuple(inner));record=receipt['shared_row_fit']['frame_records'][i]
 assert list(crop.size)==record['source_component_size']
 resized=crop.resize(tuple(record['resampled_size']),Image.Resampling.LANCZOS);rb=resized.getbbox();assert rb==(0,0,*resized.size)
 rebuilt=Image.new('RGBA',(512,512));rebuilt.alpha_composite(resized,tuple(record['placement_xy']));actual=np.array(Image.open(RUN/f'curated/frame-{i}.png').convert('RGBA'))
 assert np.array_equal(np.array(rebuilt),actual), 'Actual raw->curated closure must match all RGBA pixels'
 origin=raw_box[:2];placement=np.array(record['placement_xy'],float);effective=np.array(record['resampled_size'],float)/np.array(crop.size,float);common=receipt['shared_row_fit']['scale']
 def source_to_raw(q):return origin+(np.array(q,float)-placement+.5)/effective-.5
 def raw_to_source(q):return (np.array(q,float)-origin+.5)*effective-.5+placement
 raw_holes=closed_regions(np.array(im));padded_origin=origin-inner[:2]
 near,neck=raw_holes;near_center=near['centroid']+padded_origin;neck_center=neck['centroid']+padded_origin
 near_box=near['bbox']+np.tile(padded_origin,2);neck_box=neck['bbox']+np.tile(padded_origin,2)
 entry={'frame':i,'raw_component_bbox_xyxy':raw_box.tolist(),'native_padded_component_size':list(im.size),'native_inner_alpha_bbox':inner.tolist(),'curated_placement_xy':placement.tolist(),'shared_scale':common,'rounded_resampled_size':record['resampled_size'],'actual_resize_effective_scale_xy':effective.tolist(),'raw_to_curated_entire_RGBA_exact_reproduction':True,'raw_armhole':{'centroid_xy':near_center.tolist(),'bbox_xyxy':near_box.tolist(),'area':near['area']},'raw_neckhole':{'centroid_xy':neck_center.tolist(),'bbox_xyxy':neck_box.tolist(),'area':neck['area']},'slot_raw_xyxy':[543*i,0,543*(i+1),724],'input_slot_full_RGBA_sha256':hashlib.sha256(raw_array[:,543*i:543*(i+1)].tobytes()).hexdigest()}
 if i in [1,2]:
  cf=fit['frames'][i]['armor_integer_fits']['Chest'];C=np.array(cf['actual_hole_centroid_xy'],float);residual=np.array(cf['hole_vs_visible_junction_residual_xy'],float);T=C-residual
  inverse_current=source_to_raw(C);inverse_target=source_to_raw(T);actual_projection_error=raw_to_source(near_center)-C
  assert np.linalg.norm(actual_projection_error)<2., 'Point mapping and raw aperture must remain close after resampling'
  raw_ellipse_size=near_box[2:]-near_box[:2];target_box=np.r_[inverse_target-raw_ellipse_size/2,inverse_target+raw_ellipse_size/2]
  outside={'left':max(0.,raw_box[0]-target_box[0]),'top':max(0.,raw_box[1]-target_box[1]),'right':max(0.,target_box[2]-raw_box[2]),'bottom':max(0.,target_box[3]-raw_box[3])}
  center_round=np.rint(inverse_target).astype(int);center_alpha=int(np.array(keyed)[center_round[1],center_round[0],3])
  ellipse=Image.new('L',source.size,0);ImageDraw.Draw(ellipse).ellipse(tuple(target_box),fill=255);ellipse_mask=np.array(ellipse)>0;current_alpha=np.array(keyed)[:,:,3]>=128
  roi=np.r_[np.minimum(near_box[:2],target_box[:2])-12,np.maximum(near_box[2:],target_box[2:])+12]
  roi[0]=max(roi[0],543*i+4);roi[2]=min(roi[2],543*(i+1)-4);roi[1]=max(roi[1],4);roi[3]=min(roi[3],720)
  belt_source=np.array(cf['A_artist_visible_component_xy'],float);belt_raw=source_to_raw(belt_source)
  entry['edit']={'curated_actual_armhole_centroid_xy':C.tolist(),'curated_required_armhole_centroid_xy':T.tolist(),'curated_required_delta_xy':(-residual).tolist(),'required_raw_point_exact_PIL_inverse_xy':inverse_target.tolist(),'current_raw_hole_centroid_direct_xy':near_center.tolist(),'current_curated_centroid_inverse_raw_xy':inverse_current.tolist(),'raw_required_delta_between_PIL_mapped_centroids_xy':(inverse_target-inverse_current).tolist(),'raw_required_delta_from_actual_raw_hole_centroid_xy':(inverse_target-near_center).tolist(),'common_scale_only_delta_raw_DIAGNOSTIC_xy':(-residual/common).tolist(),'raw_direct_centroid_projected_minus_actual_curated_centroid_source_px':actual_projection_error.tolist(),'target_ellipse_bbox_raw_xyxy':target_box.tolist(),'target_ellipse_size_equals_actual_raw_hole_bbox':True,'target_ellipse_outside_old_axis_aligned_garment_bbox_raw_px':outside,'target_center_inside_old_axis_bbox':bool(np.all(inverse_target>=raw_box[:2]) and np.all(inverse_target<raw_box[2:])),'target_center_current_garment_alpha':center_alpha,'target_center_currently_outside_actual_garment_contour':center_alpha<128,'target_ellipse_pixels_outside_current_actual_garment_alpha':int(np.count_nonzero(ellipse_mask&~current_alpha)),'target_ellipse_total_pixels':int(ellipse_mask.sum()),'suggested_local_edit_ROI_raw_xyxy':roi.tolist(),'neck_aperture_to_keep_fixed_raw_bbox':neck_box.tolist(),'body_buckle_source_artist_xy':cf['B_artist_visible_body_surface_xy'],'current_buckle_raw_artist_xy_to_keep_fixed':belt_raw.tolist(),'no_whole_component_translation':True,'no_source_pixel_delta_misused_as_raw_delta':True,'geometric_authority':'Inverse of actual240 crop/roundedPILresize/pixel-center/placement, backed fullRGBA reproduction. Raw direct contour centroid and mapped source centroid differ slightly from resampling; both recorded. No bone or hidden joint.'}
  edit_rows.append(entry)
  x0=543*i+8
  d.text((x0,18),f'EDIT ONLY phase{i}: RED=current near hole; CYAN=target',font=font,fill=(255,255,255,255))
  d.text((x0,43),f'Target raw({inverse_target[0]:.2f},{inverse_target[1]:.2f}); fixed belt/neck',font=small,fill=(255,255,255,255))
  d.text((x0,65),f'OUTSIDE old bbox L{outside["left"]:.1f} U{outside["top"]:.1f}; grow brown upper-left',font=small,fill=(255,230,90,255))
  d.rectangle(tuple(raw_box),outline=(240,205,60,255),width=2)
  d.ellipse(tuple(near_box),outline=(255,65,65,255),width=3)
  d.ellipse(tuple(target_box),outline=(55,225,255,255),width=3)
  d.ellipse(tuple(neck_box),outline=(240,205,60,255),width=2)
  d.ellipse((near_center[0]-4,near_center[1]-4,near_center[0]+4,near_center[1]+4),fill=(255,65,65,255))
  d.line((tuple(near_center),tuple(inverse_target)),fill=(55,225,255,255),width=3)
  u=(near_center-inverse_target)/np.linalg.norm(near_center-inverse_target);p=np.array([-u[1],u[0]])
  for sign in [-1,1]:d.line((tuple(inverse_target),tuple(inverse_target+15*u+sign*7*p)),fill=(55,225,255,255),width=3)
 else:d.text((543*i+28,25),f'PROTECT PHASE{i}: keep this cell unchanged',font=font,fill=(245,245,245,255))
 maps.append(entry)

guide=refs/'native240-raw-current-nearholes-to-raw-targets-EDIT-DIAGNOSTIC-ONLY.png';guided=Image.alpha_composite(source_rgba,overlay);guided.save(guide)
ov=refs/'DIAGNOSTIC-OVERLAY-NOT-FINAL-ART.png';overlay.save(ov)
changed=np.any(np.array(guided)!=raw_array,axis=2);om=np.array(overlay)[:,:,3]>0;assert not np.any(changed&~om)
mapping=write('actual240-raw-curated-inverse-and-outside-target-proof-v001.json',{'schema':'Chest241-raw240-exact-inverse-aperture-target-proof-v001','source_raw240':pin(raw),'retained_E500_raw':receipt['E_raw'],'actual240_process_receipt':pin(REC),'actual240_sourcefit':pin(FIT),'installed_extractor':pin(EXTRACT),'chroma_args':{'key':[0,255,0],'thresholds':[96,180,18],'unmix_reach':4,'spill_max_fraction':.005},'component_hashes_match_actual240_extraction':True,'all_four_raw_to_curated_RGBA_rebuild_exact':True,'actual_PIL_pixel_center_inverse_formula':'raw = rawComponentBBoxOrigin + ((curated - placement + .5) / (roundedResampledSize / rawComponentSize)) - .5','common_scale_only_approximation':'rawDelta = sourceDelta / .3021148036253776; separate from exact roundedPIL pixel-center mapping.','rows':maps,'guide':pin(guide),'guide_base_raw_not_rescaled':True,'guide_pixels_outside_diagnostic_overlay_identical_to_source_RGBA':True,'diagnostic_overlay':pin(ov),'target_warning':'Both target centers may lie on current green exterior even while inside the coarse component bbox. The cyan aperture therefore requires adjacent upper-left brown shoulder-side contour expansion, not a green noop on background or whole garment translation. Outside ellipse extents explicitly recorded.','future241_raw':None,'future241_first_last_pixel_preservation':None,'newmedia_View':False})

prompt='''EDIT the FIRST reference image itself: exact native240 2172x724 FOUR-component brown-jerkin row. This is a LOCAL IMAGE EDIT, not a fresh row from a body reference. Keep the same canvas2172x724, four cells543pxwide, same garment style, material, colors, line weight, physical pouch side and all fixed details. Reference2 is the SAME raw240 with diagnostic marks only: RED outlines/centers are the CURRENT near-side arm apertures, CYAN ellipses are the required new aperture locations, CYAN arrows show the shift. GOLD rectangles are the old coarse component bounds; GOLD small ellipse marks the NECK aperture to preserve. NEVER draw any diagnostic marks, arrows, rectangles, ellipses, labels or text in the output.

ONLY edit the SECOND and THIRD components, indices1 and2, at their near-side arm apertures and adjacent UPPER-LEFT brown shoulder/side contour. Do not move the complete vest. Do not move the front round fastening, waist buckle, pouch, belt, neckline/neck aperture, lower hem, front/right chest panel or other details. Protect the FIRST and FOURTH components(indices0,3) from any changes. Retain all green neck apertures exactly; they are not the apertures being relocated. Do not enlarge/recenter/rescale/rotate the row or any whole component.

Precise raw target positions follow the actual crop/sharedscale/roundedresize inverse, NOT source512 pixel coordinates. Phase1(second component): move the near aperture center to approximately RAW(656.14,287.52). Phase2(third component): move it to approximately RAW(1213.12,273.71). Follow the cyan target ellipses in reference2 for actual sizes and positions. The source512 shifts of about(-40.64,-11.35) and(-32.26,-5.29) are NOT raw shifts; do not apply them directly to this raw image. The transform proof records exact coordinates and explains the slight raw-centroid/resize difference.

CRITICAL: the desired aperture locations partly extend left of the OLD garment bbox; the second component also extends above it. In the CURRENT actual contour the target center sits in green exterior. Therefore merely drawing more green there would do nothing. You must reshape and extend the UPPER-LEFT brown shoulder/side contour to surround and connect around the new cyan green aperture, with a continuous narrow brown leather/ink rim matching the current style. This local shoulder-side extension is allowed; fixed belt/pouch/neck/front and whole-row positions remain unchanged. Close the old RED aperture with matching adjacent brown leather so each edited component has ONE near-arm aperture at the new position, plus its separate unchanged neck aperture. Do not leave two near-arm holes, a disconnected fragment, an open accidental gap to the outside, a duplicated panel, or a floating brown loop. Do not fabricate body pixels to make the opening look connected.

The new near-side opening must project up-left relative to the FIXED waist buckle so the existing real Dodge body near sleeve can meet it. All modifications are confined to this aperture and adjacent brown upper-left shoulder-side contour. This change cannot be achieved by translating the full vest or adding a gray foreground collar band. No gray undercloth, torso, collar band, arms, gloves, hands, head/helmet, legs, sword or other armor. No opaque black backing/cavity inside neck or arm openings. Keep both aperture kinds genuine flat #00FF00 green negative space, with narrow dark contour ink only. Keep all surrounding flat green background, four complete independent connected jerkin components, generous separation and no edge clipping. Return ONLY the edited four-component strip, no overlays/guide/text.

This is one local-edit verification candidate. Exact unedited regions will be compared after generation; do not assume any unmeasured preservation or gameplay acceptance. Real source Dodge218 body, Near235/Far236 and independentSword are not being generated or altered.'''
# Insert measured extents and actual deltas rather than pretending the target fits existing material.
details=[]
for r in edit_rows:
 e=r['edit'];o=e['target_ellipse_outside_old_axis_aligned_garment_bbox_raw_px'];details.append(f'Phase{r["frame"]} actual raw hole center={e["current_raw_hole_centroid_direct_xy"]}; exact target={e["required_raw_point_exact_PIL_inverse_xy"]}; actual raw center-to-target delta={e["raw_required_delta_from_actual_raw_hole_centroid_xy"]}; target ellipse={e["target_ellipse_bbox_raw_xyxy"]}; outside oldbbox left={o["left"]:.3f}, top={o["top"]:.3f}px; target center current alpha={e["target_center_current_garment_alpha"]}; keep neckbbox={e["neck_aperture_to_keep_fixed_raw_bbox"]}, belt artistpoint={e["current_buckle_raw_artist_xy_to_keep_fixed"]}.')
promptfile=write('Root-native-LOCAL-EDIT-fullprompt-v001.txt',prompt+'\n\nMEASURED RAW COORDINATE DETAILS:\n'+'\n'.join(details)+'\n')
referencefile=write('Root-native-references-AFTER-E-v001.json',{'references_in_order':[{'file':pin(target),'role':'REFERENCE1 = EXACT native240 raw EDIT TARGET. Edit this image locally, preserve canvas and fixed details/phase0,3. It is not a motion reference for a fresh generation.','already_retained':True},{'file':pin(guide),'role':'REFERENCE2 = Same exact raw240 with RED actualnearholes/CYAN targetellipses+arrows/GOLD oldbbox and fixedneck guides. DIAGNOSTIC ONLY; use locations to edit reference1, never reproduce marks/text.','already_retained':True}],'declaration_timing':'AFTER-E call template. Exactraw240 alreadyE500; newguide and packet must first be RootEretained2SHA0 and reviewed.','newguide_E_retained':False})
output=HERE/'process-batches/2026-10-18-LGT-Dodge4-chest-local-edit-native241-v001/raw/leather_chest_hero_dodge_correction.png'
handoff=write('Root-Chest241-local-raw240-aperture-edit-handoff-v001.json',{'schema':'Chest241-local-EDIT-of-native240-input-v001','planned_Root_native_id':241,'actual_native_receipt':None,'prompt':pin(promptfile),'references_json':pin(referencefile),'source_raw240':pin(raw),'edit_target':pin(target),'diagnostic_guide':pin(guide),'inverse_and_bounds_proof':pin(mapping),'canonical_native_output':output.as_posix(),'canonical_F_media':MEDIA.as_posix(),'inherited_numeric_sprite_request':pin(inherited),'original240_official_request':pin(RUN/'sprite-request.json'),'numeric_request_byte_exact':True,'unchanged_future_pipeline':'Independent newprocess, standard sharedcomponent extraction/compose/curated/preview/inspect;512min/window128x100. No deriving successfulfit fromraw. Actual241raw/cell0,3preservation/crop/commonScale/curated A/B all pending.','actual_first_last_source_slot_RGBA_hashes':{str(r['frame']):r['input_slot_full_RGBA_sha256'] for r in maps if r['frame'] in [0,3]},'protected_regions':'Entire raw cells0,3; in1,2 neckhole/frontbutton/buckle/pouch/belt/lowerhem/front-right panel fixed. Onlynearhole+adjacentupper-leftbrownshoulder/side contour localreshape.','source_targets_outside_existing_material_explicit':True,'generation_calls_by_worker':0,'quota_or_ledger_changed':False,'newmedia_View':False,'newmedia_E_retained':False,'TrialAllowed':False,'FinalAccepted':False})
write('HANDOFF.md','''241为对exact240原raw的局部EDIT，不带body/Ready/bad234再重生。2refs：原raw240本体+同raw诊断guide，后者红=当前nearhole/青=所需新椭圆与箭头/黄=原componentbbox和固定neck。

使用installed sprite-gen原keyer/components重跑只读测量，四componentRGBA SHA与实际240 extraction全部相等；raw crop→roundedLanczos→512placement整幅RGBA重建与curated逐像素相等。逆映射包含crop、rounded size、pixel-center与placement，同时列shared .3021148近似；不把source512位移当raw位移。每孔按实际raw contour分别测，neck不得误移。

两目标中心在原bbox内但位于当前实际green exterior，目标椭圆左侧越bbox，phase1还越上界；必须新增/重塑相邻上左棕肩侧轮廓包住目标孔，不能只在空背景画绿或整个衣片平移。标出extent/目标alpha/需要扩展事实，不假称当前材质已有此孔位。0/3整格与1/2的neck/扣/袋/带/颜色/前右片保持，只局部nearhole+邻接brownside轮廓。所有修像只交Root内置AI EDIT，本worker未画final像素。

原240全保留，未来241原稿/pixelpreservation/QA/scale/两孔与A/B残差都null，不承诺工具保像素。新原稿须独立process同128x100/512门/sharedrow，实际比较0/3及保护区。新guide先F原件/展示/index交RootE两SHA后View/调用。0API/生成/quota/ledger/Source/Content/UE改动，未准入。
''')
freeze=write('Chest241-local-EDIT-input-freeze-v001.json',{'schema':'Chest241-local-EDIT-input-freeze-v001','script':pin(Path(__file__)),'files':[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],'raw240_modified':False,'local_final_character_or_armor_pixels_painted':False,'newmedia_View':False,'native_calls':0})
(MEDIA/'原件').mkdir(parents=True);shutil.copytree(OUT,MEDIA/'原件/局部EDIT输入完整包');shutil.copyfile(Path(__file__),MEDIA/'原件'/Path(__file__).name);(MEDIA/'展示副本').mkdir()
for p in [target,guide]:shutil.copyfile(p,MEDIA/'展示副本'/p.name)
index={'date':'2026-10-18','topic':'钟盔Dodge胸衣241原稿局部孔位编辑标准输入','version':'v001','status':'UNVIEWED exacttarget+diagnosticguide awaiting RootE; planned241 localEDIT Rootonly, notsourcefit/native accepted','handoff':pin(handoff),'freeze':pin(freeze),'files':[pin(p) for p in sorted(MEDIA.rglob('*')) if p.is_file()]}
with (MEDIA/'来源-版本-状态索引.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'canonical_F_media':MEDIA.as_posix(),'files':sum(p.is_file() for p in MEDIA.rglob('*')),'bytes':sum(p.stat().st_size for p in MEDIA.rglob('*') if p.is_file()),'handoff':pin(handoff),'freeze':pin(freeze),'prompt':pin(promptfile),'references_json':pin(referencefile),'raw_edit_targets':[{'phase':r['frame'],'target':r['edit']['required_raw_point_exact_PIL_inverse_xy'],'actual_raw_current':r['edit']['current_raw_hole_centroid_direct_xy'],'raw_delta':r['edit']['raw_required_delta_from_actual_raw_hole_centroid_xy'],'outside_old_bbox':r['edit']['target_ellipse_outside_old_axis_aligned_garment_bbox_raw_px'],'target_center_current_alpha':r['edit']['target_center_current_garment_alpha']} for r in edit_rows],'newmedia_View':False,'nativecalls':0},ensure_ascii=False,indent=2))
