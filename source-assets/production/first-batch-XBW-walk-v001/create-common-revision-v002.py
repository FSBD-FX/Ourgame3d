from pathlib import Path
P=Path(__file__).resolve().parent
t=(P/'prepare-common-walk-v001.py').read_text('utf-8')
for a,b in [('XBW-common-walk-v001','XBW-common-walk-v002'),('common-profile-v001','common-profile-v002'),('near-{i}-v001','near-{i}-v002'),('support-{i}-v001','support-{i}-v002'),('{name}-v001.png','{name}-v002.png'),('candidate-v001.json','candidate-v002.json')]:t=t.replace(a,b)
t=t.replace('body.putdata([px if px[3] else(0,0,0,0) for px in body.get_flattened_data()])','chroma_removed=sum(px[3]>0 and px[0]>px[1]+30 and px[2]>px[1]+30 for px in body.get_flattened_data())\n body.putdata([px if px[3] and not(px[0]>px[1]+30 and px[2]>px[1]+30) else(0,0,0,0) for px in body.get_flattened_data()])')
t=t.replace("'source_sole_px':SOLES[i]","'post_transform_chroma_fringe_pixels_removed':chroma_removed,'source_sole_px':SOLES[i]")
q=P/'prepare-common-walk-v002.py';assert not q.exists();q.write_text(t,'utf-8')
