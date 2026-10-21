from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'extract-primary2-four-armors-v001.py').read_text('utf-8')
source=source.replace('components/primary2-four-armors-v001','components/primary2-four-armors-v002').replace('primary2-four-armors-candidate-v001.json','primary2-four-armors-candidate-v002.json')
source=source.replace('-{i}-v001.png','-{i}-v002.png').replace('selection-v001.png','selection-v002.png')
insert='''
# Actual source-specific split mail panels exclude the trouser gap below the slit.
MED_PANELS=[
 [[(150,350),(220,352),(218,378),(217,397),(214,406),(146,397),(143,391)],[(239,352),(271,352),(296,377),(292,389),(251,405),(238,386)]],
 [[(146,354),(219,356),(217,382),(216,404),(147,397),(143,387)],[(235,355),(270,352),(291,376),(289,388),(252,406),(237,390)]],
 [[(150,339),(221,341),(220,385),(216,400),(145,391)],[(239,341),(268,339),(287,369),(275,385),(253,398),(237,378)]],
 [[(154,334),(221,336),(220,379),(216,395),(147,386)],[(244,337),(270,337),(295,366),(290,378),(253,396),(235,377)]],
 [[(153,334),(221,336),(220,380),(216,396),(146,386)],[(244,337),(270,337),(295,367),(290,379),(253,396),(235,378)]],
 [[(154,334),(220,336),(219,380),(215,396),(147,386)],[(243,337),(270,337),(295,366),(290,379),(253,396),(235,378)]]]

'''
source=source.replace('\ndef masks_for(i):','\n'+insert+'def masks_for(i):')
source=source.replace("w.union(ROB_HEMS[i] if key=='ROB' else [MED_HEMS[i] if key=='MED' else SHORT_HEMS[i]])", "w.union(ROB_HEMS[i] if key=='ROB' else MED_PANELS[i] if key=='MED' else [SHORT_HEMS[i]])")
source=source.replace("blue=gg>=rr+8 and bb>=gg+5", "blue=(gg>=rr+8 and bb>=gg+5) or (key=='ROB' and gp[xx,yy] and gg>=rr*1.03 and bb>=gg*.91)")
source=source.replace("'Native robe changes cuff position in raised poses; actual sleeve/old wrist seam must be visually reviewed, not claimed complete.'", "'Native robe changes cuff position in raised poses; source-specific wrap material removed within traced arm zones. Actual sleeve/old wrist seam remains a candidate limitation, not complete clothing acceptance.'")
target=P/'extract-primary2-four-armors-v002.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
