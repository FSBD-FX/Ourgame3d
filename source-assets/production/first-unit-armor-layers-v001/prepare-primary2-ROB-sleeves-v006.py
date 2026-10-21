"""Prepare a new, non-overwriting actual sleeve selection revision; no generation."""
from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'select-primary2-ROB-sleeves-v005.py').read_text('utf-8').replace('v005','v006')
insert='''
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
'''
s=s.replace("prior=P/",insert+"\nprior=P/",1)
s=s.replace("    for name in ['head','belt','pouch']:\n        mask=masks[name].filter(ImageFilter.MaxFilter(7)) if name=='head' else masks[name]\n        forbidden=ImageChops.lighter(forbidden,mask)","    sleeve_zone=ImageChops.lighter(selection['weapon_forearm'],selection['other_forearm'])\n    protected={'helmet':tr.w.poly(HELMETS[i]),'belt':ImageChops.subtract(masks['belt'],sleeve_zone),'pouch':ImageChops.subtract(masks['pouch'],sleeve_zone)}\n    for mask in protected.values():forbidden=ImageChops.lighter(forbidden,mask)")
s=s.replace("    for name in ['head','belt','pouch']:\n        assert ImageChops.multiply(front.getchannel('A'),masks[name]).getbbox() is None", "    for mask in protected.values():assert ImageChops.multiply(ImageChops.subtract(front.getchannel('A'),previous.getchannel('A')),mask).getbbox() is None")
s=s.replace("    far=Image.open(base['body_far']['path']).convert('RGBA');hand=Image.open(base['body_near']['path']).convert('RGBA')", "    whole=Image.open(base['body_far']['path']).convert('RGBA');whole.alpha_composite(Image.open(base['body_near']['path']).convert('RGBA'))\n    hand_mask=ImageChops.lighter(tr.w.poly(FISTS[i]).filter(ImageFilter.MaxFilter(5)),tr.w.poly(WRISTS[i]))\n    hand=tr.w.sel.extract(whole,hand_mask);far=tr.w.sel.extract(whole,ImageChops.invert(hand_mask))\n    reconstruct=far.copy();reconstruct.alpha_composite(hand);assert reconstruct.tobytes()==whole.tobytes()\n    assert whole.getpixel(tuple(base['grip_px']))==hand.getpixel(tuple(base['grip_px']))\n    for name,image in [('body_far',far),('body_near',hand)]:paths[name]=tr.w.save(image,out/f'{name}-{i}.png','same_exact_common_body_new_distal_hand_partition')\n    hp=P/f'masks/primary2-ROB-distal-hand-{i}-v006.png';hand_mask.save(hp);r.archive(hp,hp.relative_to(P),'actual_distal_grip_and_short_wrist_partition_no_body_pixel_change')\n    maskpaths['distal_hand']={'path':str(hp),'sha256':r.sha(hp)}")
s=s.replace("'hand_and_base_contract_unchanged':True", "'common_whole_body_RGBA_unchanged':True,'common_near_partition_changed_to_distal_hand_and_short_wrist':True,'exact_body_reconstruction':True")
s=s.replace("'runtime_delta_if_frozen':12", "'runtime_delta_if_frozen':24")
s=s.replace("'Hand skin protected by actual fist contours; real cloth may overlap old wrist-wrap coordinates and original weapon hand/wrap is drawn last.'", "'Hand skin protected by actual fist contours; real cloth may overlap old wrist-wrap coordinates and original weapon hand/short wrist is drawn last.'")
dest=P/'select-primary2-ROB-sleeves-v006.py';assert not dest.exists();dest.write_text(s,encoding='utf-8')
print(dest)
