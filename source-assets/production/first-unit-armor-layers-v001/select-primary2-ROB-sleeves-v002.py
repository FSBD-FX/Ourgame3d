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
prior=P/'manifests/import-armor-primary2-four-v001.json';old=r.read(prior)
out=P/'components/primary2-ROB-real-sleeves-v002';assert not out.exists();out.mkdir()
names=['weapon_arm_cloth','other_arm_cloth','full_robe_isolated','sword_assembled']
sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in names}
sword=Image.open(old['weapon']['path']).convert('RGBA');rows=[]
def alpha_mask(image):return image.getchannel('A').point(lambda a:255 if a else 0)
for i,(base,armor) in enumerate(zip(old['common_body'],old['armors']['ARM-ROB-001'])):
    source_path=P/f'processed/call66-fixed-canvas-v002/frame-{i}.png';source=Image.open(source_path).convert('RGBA')
    previous=Image.open(armor['armor_front']['path']).convert('RGBA');oldmask=Image.open(armor['mask_path']).convert('L');masks=tr.masks_for(i)
    # Dilation changes only selection envelope, never pose/source geometry. Native
    # sleeves are allowed to have actual thickness beyond the bare-arm outline.
    selection={name:masks[name].filter(ImageFilter.MaxFilter(15)) for name in ['weapon_forearm','other_forearm']}
    forbidden=Image.new('L',(512,512),0)
    for name in ['head','weapon_hand','other_hand','belt','pouch']:
        extra=11 if name in ['weapon_hand','other_hand'] else 7 if name=='head' else 1
        mask=masks[name].filter(ImageFilter.MaxFilter(extra)) if extra>1 else masks[name]
        forbidden=ImageChops.lighter(forbidden,mask)
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
                if px[x,y] and hp[x,y] and rr>200 and gg>145 and bb>90 and rr>gg*1.15 and gg>bb*1.22:px[x,y]=0
        pruned[name]=tr.w.prune_tiny(mask,source)
    weapon_cloth=tr.w.sel.extract(source,selection['weapon_forearm'])
    other_cloth=tr.w.sel.extract(source,selection['other_forearm'])
    front_mask=ImageChops.lighter(oldmask,selection['other_forearm']);front=tr.w.sel.extract(source,front_mask)
    near=weapon_cloth
    assert ImageChops.multiply(alpha_mask(front),alpha_mask(near)).getbbox() is None
    for image in [front,near,other_cloth]:
        assert all(a==b for a,b in zip(image.get_flattened_data(),source.get_flattened_data()) if a[3])
    # Prior front was frozen against exact anatomy traces, not the new sleeve's
    # extra selection clearance. Validate both contracts explicitly.
    for image in [near,other_cloth]:
        assert ImageChops.multiply(image.getchannel('A'),forbidden).getbbox() is None
    for name in ['head','weapon_hand','other_hand','belt','pouch']:
        assert ImageChops.multiply(front.getchannel('A'),masks[name]).getbbox() is None
    paths={}
    for name,image in [('armor_front',front),('armor_near',near),('other_arm_cloth',other_cloth)]:
        path=out/f'{name}-{i}.png';paths[name]=tr.w.save(image,path,'actual_native_ROB_sleeve_extension_pending_review')
    maskpaths={}
    for name,mask in [('weapon_arm_cloth',selection['weapon_forearm']),('other_arm_cloth',selection['other_forearm']),('combined_front',front_mask)]:
        path=P/f'masks/primary2-ROB-{name}-{i}-v002.png';mask.save(path);r.archive(path,path.relative_to(P),'actual_visible_cloth_wrap_surface_mask_not_anatomy');maskpaths[name]={'path':str(path),'sha256':r.sha(path)}
    far=Image.open(base['body_far']['path']).convert('RGBA');hand=Image.open(base['body_near']['path']).convert('RGBA')
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
        'hand_and_base_contract_unchanged':True,'new_cloth_material':'native66_gray_robe_sleeve_and_bluegray_extended_cloth_wrap_no_skin_or_hand_repaint',
        'cloth_source_alpha_added_vs_bare_arm_in_selected_zone':sum(1 for a,b in zip(newalpha.get_flattened_data(),oldalpha.get_flattened_data()) if a and not b),
        'cloth_source_alpha_removed_vs_bare_arm_in_selected_zone':sum(1 for a,b in zip(newalpha.get_flattened_data(),oldalpha.get_flattened_data()) if b and not a),
        'source_contour_difference_scope':'actual_clothing_thickness_not_joint_retarget_validation','pruned_detached_fragments':pruned})
for name,image in sheets.items():
    path=P/f'reviews/primary2-ROB-{name}-sleeves-v002.png';image.save(path);r.archive(path,path.relative_to(P),'actual_ROB_cloth_extension_isolated_and_sword_review_pending')
path=P/'manifests/primary2-ROB-real-sleeves-candidate-v002.json'
r.write(path,{'schema':'real-visible-robe-sleeve-extension-candidate-v1','prior_import':str(prior),'prior_import_sha256':r.sha(prior),
    'clip':'primary_2','armor_id':'ARM-ROB-001','source_request':66,'frames':rows,
    'draw_order':['body_far','armor_front','independent_weapon','armor_near','body_near'],
    'skin_or_hand_repaint':False,'source_geometry_transform':'none','source_pixels_only':True,
    'garment_material_policy':'Actual gray sleeve and cloth wrist wrap can cover common bare forearm; original hand/grip remains final.',
    'semantic_visual_review_passed':False,'runtime_verified':False,'complete_armor':False,
    'limitations':['Only actual visible cloth, no hidden full garment or limb skeleton invented.',
        'Cloth arm source differs in material/silhouette thickness; joint poses/grips are inherited, not independently rigged.',
        'Consumers must explicitly draw armor_near after sword and before original hand; dropping it leaves the old partial sleeve.',
        'Hand/cuff seam, right/left occlusion, motion and running appearance await actual review.']})
r.archive(path,path.relative_to(P),'real_ROB_sleeve_source_candidate_not_runtime');print({'runtime_delta_if_frozen':12,'visible_cloth_samples':12,'review_pending':True})
