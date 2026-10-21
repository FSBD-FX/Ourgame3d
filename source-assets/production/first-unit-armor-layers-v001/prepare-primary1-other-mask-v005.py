from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v004.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v004','primary1-other-armors-v005').replace('front-{i}-v004.png','front-{i}-v005.png').replace('-{suffix}-v004.png','-{suffix}-v005.png').replace('candidate-v004.json','candidate-v005.json')
t=t.replace("for name in ['head','weapon_hand','other_hand','belt','pouch']:q=ImageChops.subtract(q,masks[name])", """for name in ['head','weapon_hand','other_hand','belt','pouch']:
                exclusion=masks[name].filter(ImageFilter.MaxFilter(11)) if name in ['weapon_hand','other_hand'] else masks[name]
                q=ImageChops.subtract(q,exclusion)""")
q=p/'extract-primary1-other-armors-v005.py';assert not q.exists();q.write_text(t,'utf-8')
print('v005 wearable pixels strictly exclude frozen anatomy plus 5px seam margin')
