"""Actual source plus target contact lines for one bolt-load keypose."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
src=P/'raw/87-XBW-direct-string-latch-keypose-v001.png';im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
rear=[654,705];tip=[969,705];near=[790,701];support=[792,792];bowtips=[[854,619],[850,830]]
d.line([tuple(bowtips[0]),tuple(rear),tuple(bowtips[1])],fill='cyan',width=4);d.line((*rear,*tip),fill='yellow',width=4)
for p,c in [(rear,'cyan'),(near,'red'),(support,'lime')]:x,y=p;d.ellipse((x-10,y-10,x+10,y+10),outline=c,width=3)
d.text((30,80),'TARGET GEOMETRY ONLY: cyan string apex = bolt tail = rear rail (654,705)',fill='white');d.text((30,100),'Red(790,701) loading finger contact; Green(792,792) front support',fill='white')
q=P/'references/XBW-rear-rail-bolt-contact-geometry-v001.png';assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'native_source_plus_rail_string_bolt_contact_geometry_not_final_art')
j=q.with_suffix('.json');r.write(j,{'kind':'mechanical_contact_geometry_only','source':str(src),'source_sha256':r.sha(src),'target_rear_string_apex_and_bolt_tail_native_px':rear,
 'target_bolt_tip_native_px':tip,'target_loading_hand_native_px':near,'far_support_native_px':support,'source_raised_clamp_must_not_be_claimed_valid':True,
 'original_body_pixels_changed':False,'guides_are_not_runtime_art':True,'source_actual_native_size':[1254,1254]});r.archive(j,j.relative_to(P),'contact_guide_provenance')
print(q)
