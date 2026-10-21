from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v005.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v005','primary1-other-armors-v006').replace('front-{i}-v005.png','front-{i}-v006.png').replace('-{suffix}-v005.png','-{suffix}-v006.png').replace('candidate-v005.json','candidate-v006.json')
t=t.replace('def union(polygons):',"""# The non-weapon hand's blue wrap continues below the fist in low poses.
OTHER_WRISTS=[[(279,303),(312,304),(318,325),(310,347),(285,350),(275,330)],
[(281,304),(315,305),(321,326),(312,350),(285,350),(276,331)],
[(253,327),(279,326),(287,344),(280,366),(256,365),(247,348)],
[(261,312),(279,312),(285,325),(279,340),(265,345),(252,337),(250,326)],
[(246,308),(270,307),(280,322),(273,340),(252,342),(240,329)],
[(266,308),(295,307),(310,322),(307,341),(282,345),(263,334)]]
def union(polygons):""")
t=t.replace("guard=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))", """q=ImageChops.subtract(q,union([OTHER_WRISTS[i]]))
            guard=ImageChops.lighter(masks['weapon_hand'],masks['other_hand']).filter(ImageFilter.MaxFilter(21))""")
q=p/'extract-primary1-other-armors-v006.py';assert not q.exists();q.write_text(t,'utf-8')
print('v006 traced non-weapon wrist exclusion, no generation')
