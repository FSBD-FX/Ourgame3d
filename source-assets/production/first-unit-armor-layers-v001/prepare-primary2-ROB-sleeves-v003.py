from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'select-primary2-ROB-sleeves-v002.py').read_text('utf-8')
source=source.replace('primary2-ROB-real-sleeves-v002','primary2-ROB-real-sleeves-v003').replace('primary2-ROB-real-sleeves-candidate-v002','primary2-ROB-real-sleeves-candidate-v003')
source=source.replace('-{i}-v002.png','-{i}-v003.png').replace('sleeves-v002.png','sleeves-v003.png')
polygons='''
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

'''
source=source.replace("prior=P/'manifests/import-armor-primary2-four-v001.json'",polygons+"prior=P/'manifests/import-armor-primary2-four-v001.json'")
old="""for name in ['head','weapon_hand','other_hand','belt','pouch']:
        extra=11 if name in ['weapon_hand','other_hand'] else 7 if name=='head' else 1
        mask=masks[name].filter(ImageFilter.MaxFilter(extra)) if extra>1 else masks[name]
        forbidden=ImageChops.lighter(forbidden,mask)"""
new="""fist_masks={'weapon_fist':tr.w.poly(FISTS[i]),'other_fist':tr.w.poly(OTHER_FISTS[i])}
    for name in ['head','belt','pouch']:
        mask=masks[name].filter(ImageFilter.MaxFilter(7)) if name=='head' else masks[name]
        forbidden=ImageChops.lighter(forbidden,mask)
    for mask in fist_masks.values():forbidden=ImageChops.lighter(forbidden,mask.filter(ImageFilter.MaxFilter(7)))"""
assert old in source;source=source.replace(old,new)
source=source.replace("for name in ['head','weapon_hand','other_hand','belt','pouch']:\n        assert ImageChops.multiply(front.getchannel('A'),masks[name]).getbbox() is None", "for name in ['head','belt','pouch']:\n        assert ImageChops.multiply(front.getchannel('A'),masks[name]).getbbox() is None\n    for mask in fist_masks.values():assert ImageChops.multiply(front.getchannel('A'),mask).getbbox() is None")
source=source.replace("'hand_and_base_contract_unchanged':True", "'hand_and_base_contract_unchanged':True,'cloth_overlap_with_original_wrap_allowed_final_original_grip_drawn_last':True,'protected_fist_polygons':{'weapon':FISTS[i],'other':OTHER_FISTS[i]}")
source=source.replace("'Hand/cuff seam, right/left occlusion, motion and running appearance await actual review.'", "'Hand skin protected by actual fist contours; real cloth may overlap old wrist-wrap coordinates and original weapon hand/wrap is drawn last. Cuff seams, mirrored occlusion and running motion still require review.'")
target=P/'select-primary2-ROB-sleeves-v003.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
