from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'extract-primary3-four-armors-v001.py').read_text('utf-8')
source=source.replace('components/primary3-four-armors-v001','components/primary3-four-armors-v002').replace('primary3-four-armors-candidate-v001.json','primary3-four-armors-candidate-v002.json')
source=source.replace('-{i}-v001.png','-{i}-v002.png').replace('selection-v001.png','selection-v002.png')
patch='''
# Native low-followthrough coat/mail ends above the trouser wedges. Select the
# actual two panels separately; the diagonal robe end follows its real border.
SHORT_PANELS={
 2:[[(131,365),(196,369),(208,378),(199,407),(126,384)],[(212,371),(240,371),(252,395),(232,408),(207,406)]],
 3:[[(135,363),(211,364),(218,378),(209,398),(132,376),(126,366)],[(220,371),(244,374),(256,394),(231,400),(214,394)]]}
MED_PANELS[2]=[[(129,364),(194,369),(203,382),(191,414),(119,400)],[(210,373),(239,371),(252,399),(233,414),(209,403)]]
MED_PANELS[3]=[[(135,363),(211,364),(218,379),(207,400),(190,409),(132,392)],[(220,372),(245,375),(262,398),(251,405),(218,399)]]
ROB_HEMS[2][1]=[(215,371),(245,367),(263,390),(281,407),(296,421),(234,445)]
ROB_HEMS[3][1]=[(225,377),(248,375),(270,405),(286,424),(239,441)]

'''
source=source.replace('\ndef masks_for(i):','\n'+patch+'def masks_for(i):')
old="q=ImageChops.lighter(q,w.union(ROB_HEMS[i] if key=='ROB' else MED_PANELS[i] if key=='MED' else [SHORT_HEMS[i]]))"
new="hems=ROB_HEMS[i] if key=='ROB' else MED_PANELS[i] if key=='MED' else SHORT_PANELS[i] if key=='LGT' and i in SHORT_PANELS else [SHORT_HEMS[i]]\n            q=ImageChops.lighter(q,w.union(hems))"
assert old in source;source=source.replace(old,new)
target=P/'extract-primary3-four-armors-v002.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
