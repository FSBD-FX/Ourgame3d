from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'review-wing-hurt-origin-grids-v001.py').read_text('utf-8')
source=source.replace("[('wing','call99-wing-fixed-canvas-v001',6,3),('hurt','call100-hurt-four-v001',4,2)]","[('peck','call96-peck-fixed-canvas-v001',6,3)]")
source=source.replace("{action}-actual-chest-coordinate-grids-v001.png","{action}-actual-chest-coordinate-grids-v002.png")
exec(compile(source,str(Path(__file__)),'exec'))
