from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
paths=[P/'processed/call94-hover-fixed-canvas-v001/frame-0.png',P/'processed/call97-dormant-single-v001/keypose-canonical512.png',P/'processed/call98-wake-quarter-single-v001/keypose-canonical512.png']
canvas=Image.new('RGB',(1200,340),(35,41,45));d=ImageDraw.Draw(canvas)
for i,p in enumerate(paths):
 im=Image.open(p).convert('RGBA');crop=im.crop((180,200,380,350)).resize((400,300),Image.Resampling.NEAREST);ox=i*400;canvas.paste(crop,(ox,20),crop)
 for xx in range(180,381,20):d.line((ox+(xx-180)*2,20,ox+(xx-180)*2,319),fill=(55,65,65));d.text((ox+(xx-180)*2+1,21),str(xx),fill='white')
 for yy in range(200,351,20):d.line((ox,20+(yy-200)*2,ox+399,20+(yy-200)*2),fill=(55,65,65));d.text((ox+1,21+(yy-200)*2),str(yy),fill='white')
 d.text((ox+3,3),['hover94 source0','dormant97','quarterwake98'][i],fill='white')
q=P/'reviews/anchor-dormant-quarterwake-chest-grid-v001.png';assert not q.exists();canvas.save(q);r.archive(q,q.relative_to(P),'actual_numeric_chest_junction_cross_source_reference_not_new_art')
