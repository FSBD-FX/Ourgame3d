from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
im=Image.open(P/'references/stone-bat-hover-actual0-magenta512-v001.png').convert('RGB');sheet=Image.new('RGB',(1024,1024),(255,0,255))
for i in range(4):sheet.paste(im,(i%2*512,i//2*512))
q=P/'references/stone-bat-hover-actual0-four-cell-guide-v001.png';assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'four_repeated_actual_hover0_ANCHOR_GUIDE_not_four_unique_poses')
