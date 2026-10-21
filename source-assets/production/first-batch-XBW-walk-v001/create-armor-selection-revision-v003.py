from pathlib import Path
P=Path(__file__).resolve().parent
t=(P/'extract-walk-four-armors-v002.py').read_text('utf-8')
for a,b in [('XBW-walk-four-armors-v002','XBW-walk-four-armors-v003'),('{name}-{i}-v002.png','{name}-{i}-v003.png'),('{name}-selection-v002.png','{name}-selection-v003.png'),('candidate-v002.json','candidate-v003.json')]:t=t.replace(a,b)
t=t.replace("blue=Image.new('L',(512,512));blue.putdata([255 if p[3]and p[2]>p[1]*1.035 and p[1]>p[0]*1.03 else 0 for p in body.get_flattened_data()])", "blue=Image.new('L',(512,512));blue.putdata([255 if p[3]and p[2]>p[1]*1.035 and p[1]>p[0]*1.03 and ((g[0]-65<=j%512<=g[0]+25 and g[1]-35<=j//512<=g[1]+30)or(f['support_grip_px'][0]-40<=j%512<=f['support_grip_px'][0]+25 and f['support_grip_px'][1]-35<=j//512<=f['support_grip_px'][1]+30)) else 0 for j,p in enumerate(body.get_flattened_data())])")
t=t.replace('(bb>gg*1.035 and gg>rr*1.03)','(rr<gg*.97 and bb>gg*.90)')
t=t.replace("[(141,381),(174,376),(203,397),(187,424),(163,435),(134,412)]","[(185,369),(221,385),(214,401),(199,412),(161,394),(174,379)]")
t=t.replace("[(163,376),(201,375),(209,401),(187,417),(161,407)]","[(188,372),(215,376),(234,388),(217,405),(203,413),(183,395)]")
t=t.replace("[(168,382),(205,380),(216,403),(197,421),(170,410)]","[(195,380),(223,382),(241,397),(224,414),(210,421),(191,404)]")
t=t.replace("[(174,375),(207,371),(221,394),(201,412),(174,400)],[(270,387),(303,383),(328,413),(309,437),(284,428)]","[(194,359),(230,365),(248,379),(233,392),(211,396),(189,381)],[(287,373),(315,370),(337,403),(321,418),(296,424),(274,392)]")
needle="   # Shin coordinates were individually measured"
insert="""   robe_hems=[
    [[(184,337),(250,337),(236,424),(170,416),(153,408)],[(263,337),(289,336),(324,412),(275,424),(257,367)]],
    [[(188,337),(250,337),(242,368),(220,418),(154,397),(171,373)],[(263,336),(287,335),(318,409),(275,417),(256,365)]],
    [[(188,337),(243,337),(237,368),(222,417),(178,397),(179,371)],[(181,340),(189,346),(168,378),(161,373)],[(255,337),(280,336),(307,409),(272,417),(252,367)]],
    [[(192,340),(254,340),(238,426),(178,417),(164,409)],[(270,340),(296,338),(325,418),(279,430),(263,369)]],
    [[(200,337),(265,339),(257,371),(241,409),(188,391),(205,356)],[(276,336),(294,335),(337,384),(307,393),(269,356)]],
    [[(178,340),(244,340),(229,428),(166,420),(146,409)],[(256,339),(281,337),(315,418),(269,430),(250,369)]]]
"""
t=t.replace(needle,insert+needle)
t=t.replace("hp=[shifted(p)for p in hems[:1]]+shins[i]if key=='HVY'else[shifted(p)for p in hems]","hp=robe_hems[i] if key=='ROB' else ([shifted(p)for p in hems[:1]]+shins[i] if key=='HVY' else [shifted(p)for p in hems])")
q=P/'extract-walk-four-armors-v003.py';assert not q.exists();q.write_text(t,'utf-8')
