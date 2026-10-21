from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-LGT-v002.py').read_text('utf-8')
t=t.replace('primary1-LGT-selection-v002','primary1-LGT-selection-v003').replace('selection-v002.png','selection-v003.png').replace('candidate-v002.json','candidate-v003.json').replace('-{i}-v002.png','-{i}-v003.png')
t=t.replace('from PIL import Image,ImageDraw,ImageChops','from PIL import Image,ImageDraw,ImageChops,ImageFilter')
t=t.replace("base=orig.copy();base.paste(common,(0,0),cloth);base=sel.extract(base,Image.new('L',(512,512),255))", """base=common.copy()
        # The native common body has no residual old shoulder armor; preserve
        # frozen anatomy/waist and every original lower-leg/boot pixel explicitly.
        for k in ['head','weapon_hand','other_hand','belt','pouch']:base.paste(orig,(0,0),masks[k])
        lower=Image.new('L',(512,512),0);ImageDraw.Draw(lower).rectangle((0,410,511,511),fill=255);base.paste(orig,(0,0),lower)
        base=sel.extract(base,Image.new('L',(512,512),255))""")
t=t.replace("for k in ['head','weapon_hand','other_hand','belt','pouch']:armor_mask=ImageChops.subtract(armor_mask,masks[k])", """for k in ['head','weapon_hand','other_hand','belt','pouch']:
            exclusion=masks[k].filter(ImageFilter.MaxFilter(21)) if k in ['weapon_hand','other_hand'] else masks[k]
            armor_mask=ImageChops.subtract(armor_mask,exclusion)""")
t=t.replace("'source_pixels_only_no_paint':True", "'source_pixels_only_no_paint':True,'base_construction':'native52_shared_body_with_frozen_head_forearms_hands_waist_and_lowerlegs_restored','armor_selection_hand_clearance_px':10")
q=p/'extract-primary1-LGT-v003.py';assert not q.exists();q.write_text(t,'utf-8')
print('v003 direct native common body + exact frozen anatomy; armor-only larger forearm exclusion')
