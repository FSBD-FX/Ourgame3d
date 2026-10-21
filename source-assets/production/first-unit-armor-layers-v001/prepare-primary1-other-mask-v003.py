from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/'extract-primary1-other-armors-v002.py').read_text('utf-8')
t=t.replace('primary1-other-armors-v002','primary1-other-armors-v003').replace('front-{i}-v002.png','front-{i}-v003.png').replace('-{suffix}-v002.png','-{suffix}-v003.png').replace('candidate-v002.json','candidate-v003.json')
t=t.replace('blue_wrist=gp[x,y] and bb>rr*1.05 and bb>gg*1.02','blue_wrist=gg>rr+8 and bb>gg+5 # actual blue wraps; teal, warm steel and grayrobe do not match')
t=t.replace('def union(polygons):',"""# Revised traced mail-hem side corners exclude visible trouser triangles.
for ii,point in enumerate([(142,389),(136,388),(138,391),(123,390),(122,391),(129,392)]):MED_HEMS[ii][-1]=point
def union(polygons):""")
q=p/'extract-primary1-other-armors-v003.py';assert not q.exists();q.write_text(t,'utf-8')
print('v003 actual blue-wrap material exclusion and tighter mail hem trace')
