"""Join actual robe collar pixels to the sleeves; no repaint or generation."""
from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'select-primary2-ROB-sleeves-v006.py').read_text('utf-8').replace('v006','v007')
insert='''
NECK_CLOTH_BRIDGES=[
 [(164,244),(199,254),(228,265),(263,269),(277,265),(282,278),(226,280),(190,267),(164,258)],
 [(171,246),(198,256),(228,267),(260,276),(275,275),(280,287),(230,287),(195,269),(171,259)],
 [(174,226),(195,232),(222,240),(249,247),(268,244),(274,256),(246,261),(220,251),(191,242)],
 [(186,225),(202,232),(226,244),(259,251),(265,263),(224,263),(200,252),(186,245)],
 [(177,223),(199,234),(224,246),(258,252),(265,265),(224,265),(195,250),(179,239)],
 [(167,223),(193,237),(219,248),(253,255),(268,254),(273,267),(225,270),(198,252),(177,243)]]
'''
s=s.replace("prior=P/",insert+"\nprior=P/",1)
s=s.replace("    front_mask=ImageChops.lighter(oldmask,selection['other_forearm']);front=tr.w.sel.extract(source,front_mask)", "    bridge=ImageChops.subtract(tr.w.poly(NECK_CLOTH_BRIDGES[i]),forbidden)\n    bridge=ImageChops.subtract(bridge,selection['weapon_forearm'])\n    front_mask=ImageChops.lighter(ImageChops.lighter(oldmask,selection['other_forearm']),bridge);front=tr.w.sel.extract(source,front_mask)")
s=s.replace("('combined_front',front_mask)","('combined_front',front_mask),('collar_bridge',bridge)")
dest=P/'select-primary2-ROB-sleeves-v007.py';assert not dest.exists();dest.write_text(s,encoding='utf-8');print(dest)
