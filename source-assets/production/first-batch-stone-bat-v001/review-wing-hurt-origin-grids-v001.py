from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
for action,folder,count,cols in [('wing','call99-wing-fixed-canvas-v001',6,3),('hurt','call100-hurt-four-v001',4,2)]:
 canvas=Image.new('RGB',(cols*400,680),(35,41,45));d=ImageDraw.Draw(canvas)
 for i in range(count):
  im=Image.open(P/f'processed/{folder}/frame-{i}.png').convert('RGBA');crop=im.crop((180,200,380,350)).resize((400,300),Image.Resampling.NEAREST);ox=i%cols*400;oy=i//cols*340;canvas.paste(crop,(ox,oy+20),crop)
  for xx in range(180,381,20):d.line((ox+(xx-180)*2,oy+20,ox+(xx-180)*2,oy+319),fill=(55,65,65));d.text((ox+(xx-180)*2+1,oy+21),str(xx),fill='white')
  for yy in range(200,351,20):d.line((ox,oy+20+(yy-200)*2,ox+399,oy+20+(yy-200)*2),fill=(55,65,65));d.text((ox+1,oy+21+(yy-200)*2),str(yy),fill='white')
  d.text((ox+3,oy+3),f'{action} source{i} actual chest pixels',fill='white')
 q=P/f'reviews/{action}-actual-chest-coordinate-grids-v001.png';assert not q.exists();canvas.save(q);r.archive(q,q.relative_to(P),'actual_source_chest_coordinate_diagnostic_for_manual_origin_not_new_art')
