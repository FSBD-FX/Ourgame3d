"""Refine observed native hand-contour remnants; never alter source art."""
from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'trial-split-XBW-keypose86-v002.py').read_text('utf-8')
source=source.replace("out=P/'decomposition-trials/keypose86-v002'","out=P/'decomposition-trials/keypose86-v003'")
source=source.replace("P/'reviews/XBW-keypose86-decomposition-trial-v002.png'","P/'reviews/XBW-keypose86-decomposition-trial-v003.png'")
source=source.replace('nearpoly=[(288,269),(301,263),(317,260),(330,262),(340,266),(347,273),(347,283),(341,292),(328,294),(312,292),(301,292),(289,288)]',
 'nearpoly=[(288,269),(301,263),(315,259),(328,259),(340,263),(347,269),(347,281),(341,291),(330,294),(313,292),(301,292),(289,288)]')
source=source.replace('supportpoly=[(300,309),(312,307),(323,306),(334,310),(340,317),(341,329),(337,339),(327,343),(315,340),(305,336),(299,327)]',
 'supportpoly=[(300,309),(312,307),(323,306),(333,306),(339,309),(342,316),(342,329),(338,340),(327,344),(315,340),(305,336),(299,327)]')
source=source.replace('rectangle((339,245,405,346),fill=255)','rectangle((339,242,407,353),fill=255);ImageDraw.Draw(bow_region).rectangle((169,299,174,344),fill=255)')
out=P/'trial-split-XBW-keypose86-v003.py';assert not out.exists();out.write_text(source,'utf-8');print(out)
