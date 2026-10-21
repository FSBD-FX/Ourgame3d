from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
im=Image.open(P/'processed/call94-hover-fixed-canvas-v001/frame-0.png').convert('RGBA');bg=Image.new('RGB',(512,512),(255,0,255));bg.paste(im,(0,0),im)
q=P/'references/stone-bat-hover-actual0-magenta512-v001.png';assert not q.exists();bg.save(q);r.archive(q,q.relative_to(P),'actual94hover0_identity_scale_reference_not_new_native_art')
sheet=Image.new('RGB',(1536,1024),(255,0,255))
for i in range(6):sheet.paste(bg,(i%3*512,i//3*512))
q=P/'references/stone-bat-hover-actual0-six-cell-guide-v001.png';assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'six_repeated_actual94hover0_reference_only_not_six_unique_motion_frames')
