from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-LGT-v003.py').read_text('utf-8')
t=t.replace('primary1-LGT-selection-v003','primary1-LGT-selection-v004').replace('selection-v003.png','selection-v004.png').replace('candidate-v003.json','candidate-v004.json').replace('-{i}-v003.png','-{i}-v004.png')
t=t.replace("""for k in ['head','weapon_hand','other_hand','belt','pouch']:
            exclusion=masks[k].filter(ImageFilter.MaxFilter(21)) if k in ['weapon_hand','other_hand'] else masks[k]
            armor_mask=ImageChops.subtract(armor_mask,exclusion)""", """for k in ['head','weapon_hand','other_hand','belt','pouch']:armor_mask=ImageChops.subtract(armor_mask,masks[k])
        # Manual limb zone plus sampled actual warm skin/under-sleeve material
        # selection removes anatomy leaks without a ten-pixel cloth erosion.
        guard=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))
        q=armor_mask.load();pixels=armored.load();g=guard.load()
        for yy in range(512):
            for xx in range(512):
                rr,gg,bb,aa=pixels[xx,yy]
                if q[xx,yy] and g[xx,yy] and rr>180 and gg>130 and bb>65:q[xx,yy]=0""")
t=t.replace("'armor_selection_hand_clearance_px':10", "'armor_selection_hand_clearance_px':0,'limb_zone_material_selection':'within_manual_forearm_masks_dilated10_remove_actual_native_Rgt180_Ggt130_Bgt65_skin_or_under_sleeve_pixels_only_no_RGB_paint'")
q=p/'extract-primary1-LGT-v004.py';assert not q.exists();q.write_text(t,'utf-8')
print('v004 sampled material selection within manual forearm guard only')
