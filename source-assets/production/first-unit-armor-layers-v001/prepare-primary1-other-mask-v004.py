from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v003.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v003','primary1-other-armors-v004').replace('front-{i}-v003.png','front-{i}-v004.png').replace('-{suffix}-v003.png','-{suffix}-v004.png').replace('candidate-v003.json','candidate-v004.json')
t=t.replace('MaxFilter(7)','MaxFilter(21)').replace('blue_wrist=gg>rr+8 and bb>gg+5','blue_wrist=gg>=rr+8 and bb>=gg+5')
q=p/'extract-primary1-other-armors-v004.py';assert not q.exists();q.write_text(t,'utf-8')
print('v004 extends strict native skin selection to actual sleeve boundary; no trousers filter')
