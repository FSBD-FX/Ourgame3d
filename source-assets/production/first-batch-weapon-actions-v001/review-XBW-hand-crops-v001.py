"""Diagnostic overlays on existing pixels only; never runtime sprite artwork."""
from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
for number in [82,83]:
    out=P/f'reviews/call{number}-hand-crops-v001.png';assert not out.exists()
    sheet=Image.new('RGB',(1200,800),(35,40,45));d=ImageDraw.Draw(sheet)
    for i in range(6):
        im=Image.open(P/f'processed/call{number}-fixed-canvas-v001/frame-{i}.png').convert('RGBA')
        crop=im.crop((180,200,380,400)).resize((400,400),Image.Resampling.NEAREST)
        ox=i%3*400;oy=i//3*400;sheet.paste(crop,(ox,oy),crop)
        for x in range(180,381,20):d.line((ox+(x-180)*2,oy,ox+(x-180)*2,oy+399),fill=(50,70,70));d.text((ox+(x-180)*2+1,oy+14),str(x),fill='white')
        for y in range(200,401,20):d.line((ox,oy+(y-200)*2,ox+399,oy+(y-200)*2),fill=(50,70,70));d.text((ox+1,oy+(y-200)*2+2),str(y),fill='white')
        d.text((ox+230,oy+3),f'call{number} frame{i} local px',fill='white')
    sheet.save(out);r.archive(out,out.relative_to(P),'manual_source_hand_coordinate_diagnostic_not_runtime_art')
    print(out)
