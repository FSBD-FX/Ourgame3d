from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v001.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v001','primary1-other-armors-v002').replace('front-{i}-v001.png','front-{i}-v002.png').replace('-{suffix}-v001.png','-{suffix}-v002.png').replace('candidate-v001.json','candidate-v002.json')
t=t.replace('MaxFilter(21)','MaxFilter(7)')
t=t.replace('rr>180 and gg>130 and bb>65 and rr>gg*1.15 and gg>bb*1.25','rr>220 and gg>160 and bb>100 and rr>gg*1.17 and gg>bb*1.25')
t=t.replace('sampled_trousers=y>360 and rr<150 and gg>rr*.68 and bb>gg*.45 and bb<gg*.7','sampled_trousers=False # warm metal/robe shadows overlap trousers; rely on traced garment contours')
q=p/'extract-primary1-other-armors-v002.py';assert not q.exists();q.write_text(t,'utf-8')
print('v002 preserves actual metal/cloth shadows; smaller actual-hand clearance zone')
