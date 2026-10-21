"""Version the mask refinement only; source native image/art bytes stay unchanged."""
from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'trial-split-XBW-keypose86-v001.py').read_text('utf-8')
source=source.replace("out=P/'decomposition-trials/keypose86-v001'","out=P/'decomposition-trials/keypose86-v002'")
source=source.replace("P/'reviews/XBW-keypose86-decomposition-trial-v001.png'","P/'reviews/XBW-keypose86-decomposition-trial-v002.png'")
source=source.replace('triggerhole=[(238,316),(247,316),(251,320),(250,326),(246,329),(238,327),(235,323)]',
 'triggerhole=[(251,315),(256,315),(257,320),(255,326),(251,328),(247,327),(247,323),(250,322)]')
source=source.replace('wm=ImageChops.multiply(polygon(weaponpoly),ImageChops.invert(polygon(triggerhole)))',
 "bow_region=Image.new('L',(512,512),0);ImageDraw.Draw(bow_region).rectangle((339,245,405,346),fill=255)\nwm=ImageChops.multiply(ImageChops.lighter(polygon(weaponpoly),bow_region),ImageChops.invert(polygon(triggerhole)))")
out=P/'trial-split-XBW-keypose86-v002.py';assert not out.exists();out.write_text(source,'utf-8');print(out)
