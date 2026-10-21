"""Select real existing robe sleeves/cloth wraps; preserve frozen hands and joints.

This deliberately extends the partial contract with armor_near; consumers must
support that draw order instead of silently importing only the old front layer.
"""
from pathlib import Path
import importlib.util,math,copy
from PIL import Image,ImageChops,ImageFilter
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
s=importlib.util.spec_from_file_location('trace',P/'extract-primary2-four-armors-v003.py');tr=importlib.util.module_from_spec(s);s.loader.exec_module(tr)

# Actual original fist-skin contours. Cloth wrist wraps are garments, not skin;
# they may be covered by real source sleeves while final original grip stays.
FISTS=[
 [(207,350),(223,346),(239,352),(250,364),(251,379),(241,390),(223,393),(211,385),(204,373)],
 [(119,328),(133,322),(146,326),(154,337),(153,350),(143,358),(125,358),(116,348)],
 [(296,223),(309,217),(323,222),(331,232),(332,245),(325,254),(313,260),(299,258),(291,247)],
 [(173,107),(184,97),(198,100),(208,111),(210,123),(201,135),(188,142),(174,135),(164,123)],
 [(149,159),(161,151),(174,155),(183,166),(184,178),(173,188),(160,191),(147,180),(142,169)],
 [(148,216),(161,208),(173,212),(183,222),(189,232),(185,244),(174,252),(160,252),(146,241),(142,229)]]
OTHER_FISTS=[
 [(307,333),(320,326),(334,332),(342,343),(340,357),(329,367),(314,366),(304,356),(301,343)],
 [(308,287),(321,282),(331,289),(337,301),(333,314),(322,323),(307,324),(297,315),(294,301)],
 [(280,299),(291,291),(304,300),(311,314),(308,329),(298,337),(285,339),(273,330),(271,315)],
 [(285,314),(297,309),(310,317),(317,331),(316,344),(306,353),(292,351),(281,341),(278,326)],
 [(283,278),(295,272),(307,278),(316,289),(317,303),(309,314),(298,322),(285,318),(275,308),(273,292)],
 [(284,295),(296,285),(308,289),(319,300),(322,314),(315,326),(302,335),(287,333),(277,322),(276,307)]]


# Actual source arm-only contours end at wrists. The full anatomical hand outline
# is larger than a garment extent and otherwise catches robe hem below the fist.
ARM_CLOTH_ENVELOPES=[
 [(156,305),(174,303),(191,313),(205,329),(211,346),(199,354),(181,344),(165,330),(155,316)],
 [(121,284),(144,283),(157,297),(157,317),(152,332),(123,332),(116,319),(118,299)],
 [(214,245),(232,237),(255,235),(279,232),(296,231),(302,242),(299,258),(282,274),(258,282),(231,286),(215,276)],
 [(132,178),(140,156),(155,143),(173,146),(182,160),(180,184),(171,207),(171,225),(152,231),(138,220),(132,202)],
 [(118,199),(128,187),(145,188),(159,200),(165,219),(157,241),(142,251),(126,244),(116,231)],
 [(115,259),(125,243),(143,246),(157,258),(165,276),(160,292),(148,300),(130,300),(116,290),(112,276)]]
OTHER_CLOTH_ENVELOPES=[
 [(277,302),(293,304),(306,315),(314,328),(311,342),(295,345),(283,333),(275,318)],
 [(260,308),(273,297),(290,295),(302,304),(305,321),(294,337),(280,345),(266,334),(258,322)],
 [(266,292),(279,289),(285,298),(283,316),(274,329),(263,322),(260,307)],
 [(268,303),(280,304),(286,315),(285,332),(275,337),(267,325),(263,313)],
 [(267,284),(280,278),(286,287),(283,305),(273,311),(264,300)],
 [(266,298),(279,289),(285,300),(283,319),(273,326),(264,314)]]


# Visible helmet outline, rather than the old broad head/collar protection.
HELMETS=[
 [(158,188),(164,164),(184,146),(209,137),(236,142),(267,158),(283,184),(291,213),(285,242),(276,266),(260,270),(229,265),(198,254),(168,244),(160,233),(157,210)],
 [(169,191),(177,169),(197,151),(225,144),(253,149),(281,166),(295,194),(298,225),(288,249),(275,275),(260,276),(228,267),(198,256),(174,246),(168,230)],
 [(155,167),(163,146),(183,129),(211,121),(238,126),(265,143),(281,169),(285,197),(279,221),(266,244),(249,247),(222,240),(194,229),(165,220),(155,205),(154,180)],
 [(203,130),(228,124),(256,131),(278,149),(289,178),(287,211),(278,237),(267,250),(251,252),(225,245),(203,233),(190,225),(182,204),(181,181),(185,157)],
 [(181,150),(197,130),(224,123),(251,131),(276,148),(289,177),(288,210),(279,236),(268,252),(250,253),(223,245),(200,235),(180,224),(167,205),(165,184),(172,163)],
 [(160,169),(169,147),(190,129),(219,123),(248,130),(275,148),(288,176),(289,208),(279,237),(269,254),(249,256),(218,247),(192,236),(172,224),(161,208)]]
WRISTS=[
 [(199,349),(210,344),(220,352),(215,367),(204,369)],
 [(120,316),(143,313),(150,328),(124,333)],
 [(285,228),(298,224),(306,235),(300,251),(286,255)],
 [(158,139),(171,128),(185,139),(178,155),(164,154)],
 [(138,179),(151,171),(167,182),(157,197),(141,195)],
 [(137,242),(148,231),(163,242),(156,256),(142,257)]]
# Entire visible weapon-side sleeve, including the shoulder seam; no lower hem.
ARM_CLOTH_ENVELOPES=[
 [(148,278),(166,257),(191,262),(204,281),(208,310),(211,330),(211,346),(199,354),(181,344),(165,330),(155,316),(146,302)],
 [(121,284),(144,283),(157,297),(157,317),(152,332),(123,332),(116,319),(118,299)],
 [(187,246),(208,236),(232,237),(255,235),(279,232),(296,231),(302,242),(299,258),(282,274),(258,282),(231,291),(208,291),(192,279),(187,262)],
 [(131,170),(140,153),(155,143),(173,146),(181,162),(181,187),(190,216),(198,237),(191,260),(175,270),(156,255),(144,232),(134,202)],
 [(118,199),(127,183),(143,183),(159,198),(166,213),(178,230),(196,249),(191,267),(176,275),(159,267),(139,247),(123,238),(115,223)],
 [(115,259),(124,244),(143,246),(158,257),(166,274),(178,290),(171,310),(154,321),(133,311),(117,292),(111,276)]]


NECK_CLOTH_BRIDGES=[
 [(164,244),(199,254),(228,265),(263,269),(277,265),(282,278),(226,280),(190,267),(164,258)],
 [(171,246),(198,256),(228,267),(260,276),(275,275),(280,287),(230,287),(195,269),(171,259)],
 [(174,226),(195,232),(222,240),(249,247),(268,244),(274,256),(246,261),(220,251),(191,242)],
 [(186,225),(202,232),(226,244),(259,251),(265,263),(224,263),(200,252),(186,245)],
 [(177,223),(199,234),(224,246),(258,252),(265,265),(224,265),(195,250),(179,239)],
 [(167,223),(193,237),(219,248),(253,255),(268,254),(273,267),(225,270),(198,252),(177,243)]]

prior=P/'manifests/import-armor-primary2-four-v001.json';old=r.read(prior)
out=P/'components/primary2-ROB-real-sleeves-v007';assert not out.exists();out.mkdir()
names=['weapon_arm_cloth','other_arm_cloth','full_robe_isolated','sword_assembled']
sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in names}
sword=Image.open(old['weapon']['path']).convert('RGBA');rows=[]
def alpha_mask(image):return image.getchannel('A').point(lambda a:255 if a else 0)
for i,(base,armor) in enumerate(zip(old['common_body'],old['armors']['ARM-ROB-001'])):
    source_path=P/f'processed/call66-fixed-canvas-v002/frame-{i}.png';source=Image.open(source_path).convert('RGBA')
    previous=Image.open(armor['armor_front']['path']).convert('RGBA');oldmask=Image.open(armor['mask_path']).convert('L');masks=tr.masks_for(i)
    # Dilation changes only selection envelope, never pose/source geometry. Native
    # sleeves are allowed to have actual thickness beyond the bare-arm outline.
    selection={'weapon_forearm':tr.w.poly(ARM_CLOTH_ENVELOPES[i]).filter(ImageFilter.MaxFilter(7)),'other_forearm':tr.w.poly(OTHER_CLOTH_ENVELOPES[i]).filter(ImageFilter.MaxFilter(7))}
    forbidden=Image.new('L',(512,512),0)
    fist_masks={'weapon_fist':tr.w.poly(FISTS[i]),'other_fist':tr.w.poly(OTHER_FISTS[i])}
    sleeve_zone=ImageChops.lighter(selection['weapon_forearm'],selection['other_forearm'])
    protected={'helmet':tr.w.poly(HELMETS[i]),'belt':ImageChops.subtract(masks['belt'],sleeve_zone),'pouch':ImageChops.subtract(masks['pouch'],sleeve_zone)}
    for mask in protected.values():forbidden=ImageChops.lighter(forbidden,mask)
    for mask in fist_masks.values():forbidden=ImageChops.lighter(forbidden,mask.filter(ImageFilter.MaxFilter(7)))
    for name in selection:
        selection[name]=ImageChops.subtract(selection[name],forbidden)
        selection[name]=ImageChops.subtract(selection[name],oldmask)
    # Assign overlapping visible cloth once. This is the weapon-arm clothing
    # track, not a whole original arm copied as armor; fingertips stay original.
    selection['other_forearm']=ImageChops.subtract(selection['other_forearm'],selection['weapon_forearm'])
    # The robe's gray sleeve and blue-gray extended wrap are both real generated
    # clothing. Only accidental warm hand skin close to the excluded fist is
    # omitted; there is no blanket rule banning existing cloth-colored wraps.
    near_hands=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))
    pruned={}
    for name,mask in selection.items():
        px=mask.load();sp=source.load();hp=near_hands.load()
        for y in range(512):
            for x in range(512):
                rr,gg,bb,aa=sp[x,y]
                if px[x,y] and rr>200 and gg>145 and bb>90 and rr>gg*1.15 and gg>bb*1.22:px[x,y]=0
        pruned[name]=tr.w.prune_tiny(mask,source)
    weapon_cloth=tr.w.sel.extract(source,selection['weapon_forearm'])
    other_cloth=tr.w.sel.extract(source,selection['other_forearm'])
    bridge=ImageChops.subtract(tr.w.poly(NECK_CLOTH_BRIDGES[i]),forbidden)
    bridge=ImageChops.subtract(bridge,selection['weapon_forearm'])
    front_mask=ImageChops.lighter(ImageChops.lighter(oldmask,selection['other_forearm']),bridge);front=tr.w.sel.extract(source,front_mask)
    near=weapon_cloth
    assert ImageChops.multiply(alpha_mask(front),alpha_mask(near)).getbbox() is None
    for image in [front,near,other_cloth]:
        assert all(a==b for a,b in zip(image.get_flattened_data(),source.get_flattened_data()) if a[3])
    # Prior front was frozen against exact anatomy traces, not the new sleeve's
    # extra selection clearance. Validate both contracts explicitly.
    for image in [near,other_cloth]:
        assert ImageChops.multiply(image.getchannel('A'),forbidden).getbbox() is None
    for mask in protected.values():assert ImageChops.multiply(ImageChops.subtract(front.getchannel('A'),previous.getchannel('A')),mask).getbbox() is None
    for mask in fist_masks.values():assert ImageChops.multiply(front.getchannel('A'),mask).getbbox() is None
    paths={}
    for name,image in [('armor_front',front),('armor_near',near),('other_arm_cloth',other_cloth)]:
        path=out/f'{name}-{i}.png';paths[name]=tr.w.save(image,path,'actual_native_ROB_sleeve_extension_pending_review')
    maskpaths={}
    for name,mask in [('weapon_arm_cloth',selection['weapon_forearm']),('other_arm_cloth',selection['other_forearm']),('combined_front',front_mask),('collar_bridge',bridge)]:
        path=P/f'masks/primary2-ROB-{name}-{i}-v007.png';mask.save(path);r.archive(path,path.relative_to(P),'actual_visible_cloth_wrap_surface_mask_not_anatomy');maskpaths[name]={'path':str(path),'sha256':r.sha(path)}
    whole=Image.open(base['body_far']['path']).convert('RGBA');whole.alpha_composite(Image.open(base['body_near']['path']).convert('RGBA'))
    hand_mask=ImageChops.lighter(tr.w.poly(FISTS[i]).filter(ImageFilter.MaxFilter(5)),tr.w.poly(WRISTS[i]))
    hand=tr.w.sel.extract(whole,hand_mask);far=tr.w.sel.extract(whole,ImageChops.invert(hand_mask))
    reconstruct=far.copy();reconstruct.alpha_composite(hand);assert reconstruct.tobytes()==whole.tobytes()
    assert whole.getpixel(tuple(base['grip_px']))==hand.getpixel(tuple(base['grip_px']))
    for name,image in [('body_far',far),('body_near',hand)]:paths[name]=tr.w.save(image,out/f'{name}-{i}.png','same_exact_common_body_new_distal_hand_partition')
    hp=P/f'masks/primary2-ROB-distal-hand-{i}-v007.png';hand_mask.save(hp);r.archive(hp,hp.relative_to(P),'actual_distal_grip_and_short_wrist_partition_no_body_pixel_change')
    maskpaths['distal_hand']={'path':str(hp),'sha256':r.sha(hp)}
    assembled=far.copy();assembled.alpha_composite(front)
    a=math.radians(base['weapon_angle_image_clockwise_deg']);co=math.cos(a);si=math.sin(a);gx,gy=base['grip_px'];scale=.4
    assembled.alpha_composite(sword.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,99-(co*gx+si*gy)/scale,-si/scale,co/scale,256-(-si*gx+co*gy)/scale),resample=Image.Resampling.BICUBIC))
    assembled.alpha_composite(near);assembled.alpha_composite(hand)
    full=front.copy();full.alpha_composite(near)
    for name,image in [('weapon_arm_cloth',near),('other_arm_cloth',other_cloth),('full_robe_isolated',full),('sword_assembled',assembled)]:sheets[name].alpha_composite(image,((i%3)*512,(i//3)*512))
    original_body=Image.open(tr.r.read(P/'manifests/primary2-four-armors-candidate-v003.json')['common_body'][i]['source_original_path']).convert('RGBA')
    sample=ImageChops.lighter(selection['weapon_forearm'],selection['other_forearm'])
    oldalpha=ImageChops.multiply(alpha_mask(original_body),sample);newalpha=ImageChops.multiply(alpha_mask(source),sample)
    rows.append({'index':i,'parts':paths,'mask_paths':maskpaths,'source_path':str(source_path),'source_sha256':r.sha(source_path),
        'root_px':base['root_px'],'grip_px':base['grip_px'],'weapon_angle_image_clockwise_deg':base['weapon_angle_image_clockwise_deg'],
        'common_whole_body_RGBA_unchanged':True,'common_near_partition_changed_to_distal_hand_and_short_wrist':True,'exact_body_reconstruction':True,'cloth_overlap_with_original_wrap_allowed_final_original_grip_drawn_last':True,'protected_fist_polygons':{'weapon':FISTS[i],'other':OTHER_FISTS[i]},'new_cloth_material':'native66_gray_robe_sleeve_and_bluegray_extended_cloth_wrap_no_skin_or_hand_repaint',
        'cloth_source_alpha_added_vs_bare_arm_in_selected_zone':sum(1 for a,b in zip(newalpha.get_flattened_data(),oldalpha.get_flattened_data()) if a and not b),
        'cloth_source_alpha_removed_vs_bare_arm_in_selected_zone':sum(1 for a,b in zip(newalpha.get_flattened_data(),oldalpha.get_flattened_data()) if b and not a),
        'source_contour_difference_scope':'actual_clothing_thickness_not_joint_retarget_validation','pruned_detached_fragments':pruned})
for name,image in sheets.items():
    path=P/f'reviews/primary2-ROB-{name}-sleeves-v007.png';image.save(path);r.archive(path,path.relative_to(P),'actual_ROB_cloth_extension_isolated_and_sword_review_pending')
path=P/'manifests/primary2-ROB-real-sleeves-candidate-v007.json'
r.write(path,{'schema':'real-visible-robe-sleeve-extension-candidate-v1','prior_import':str(prior),'prior_import_sha256':r.sha(prior),
    'clip':'primary_2','armor_id':'ARM-ROB-001','source_request':66,'frames':rows,
    'draw_order':['body_far','armor_front','independent_weapon','armor_near','body_near'],
    'skin_or_hand_repaint':False,'source_geometry_transform':'none','selection_edge_envelope_dilation_px':3,'source_pixels_only':True,
    'garment_material_policy':'Actual gray sleeve and cloth wrist wrap can cover common bare forearm; original hand/grip remains final.',
    'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,
    'limitations':['Only actual visible cloth, no hidden full garment or limb skeleton invented. Source pose0 has a narrow actual bare-skin gap at cuff; it is excluded from the cloth layer and original common skin remains. Full wrist-covering robe appearance is not asserted.',
        'Cloth arm source differs in material/silhouette thickness; joint poses/grips are inherited, not independently rigged.',
        'Consumers must explicitly draw armor_near after sword and before original hand; dropping it leaves the old partial sleeve.',
        'Hand skin protected by actual fist contours; real cloth may overlap old wrist-wrap coordinates and original weapon hand/wrap is drawn last. Cuff seams, mirrored occlusion and running motion still require review.']})
r.archive(path,path.relative_to(P),'real_ROB_sleeve_source_candidate_not_runtime');print({'runtime_delta_if_frozen':24,'visible_cloth_samples':12,'review_pending':True})
