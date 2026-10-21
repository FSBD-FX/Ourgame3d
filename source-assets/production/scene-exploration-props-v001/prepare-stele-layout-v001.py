from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
im=Image.new('RGB',(512,512),(255,0,255));d=ImageDraw.Draw(im)
d.polygon([(180,174),(205,146),(305,146),(333,177),(328,424),(184,424)],outline='white',width=2)
d.polygon([(195,420),(317,420),(326,448),(186,448)],outline=(0,200,240),width=2);d.line((246,448,266,448),fill=(0,200,240));d.line((256,438,256,458),fill=(0,200,240))
d.text((140,120),'ABSTRACT SIZE ONLY / NOT ART',fill='white');d.text((130,468),'SMALL STONE STELE ROOT256448',fill='white')
q=P/'references/old-city-stele-geometry-layout512-v001.png';assert not q.exists();im.save(q);r.archive(q,q.relative_to(P),'abstract_stele_geometry_only_generation_guide_not_game_asset')
