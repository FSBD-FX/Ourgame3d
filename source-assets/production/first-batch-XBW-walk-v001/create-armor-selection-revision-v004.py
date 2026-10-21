from pathlib import Path
P=Path(__file__).resolve().parent
t=(P/'extract-walk-four-armors-v003.py').read_text('utf-8')
for a,b in [('XBW-walk-four-armors-v003','XBW-walk-four-armors-v004'),('{name}-{i}-v003.png','{name}-{i}-v004.png'),('{name}-selection-v003.png','{name}-selection-v004.png'),('candidate-v003.json','candidate-v004.json')]:t=t.replace(a,b)
t=t.replace('(rr<gg*.97 and bb>gg*.90)',"(rr<gg*.97 and bb>gg*.90 and ((g[0]-47<=x<=g[0]-15 and g[1]-18<=y<=g[1]+15)or(f['support_grip_px'][0]-34<=x<=f['support_grip_px'][0]-12 and f['support_grip_px'][1]-16<=y<=f['support_grip_px'][1]+20)))")
t=t.replace("[[(192,340),(254,340),(238,426),(178,417),(164,409)],[(270,340),(296,338),(325,418),(279,430),(263,369)]]", "[[(198,340),(258,338),(248,376),(232,418),(188,397),(187,374)],[(190,343),(197,351),(174,379),(168,375)],[(272,338),(295,338),(322,410),(282,418),(266,366)]]")
t=t.replace("[[(178,340),(244,340),(229,428),(166,420),(146,409)],[(256,339),(281,337),(315,418),(269,430),(250,369)]]", "[[(182,341),(243,341),(227,428),(168,416),(173,385)],[(170,351),(182,345),(153,411),(145,410)],[(256,339),(281,337),(315,418),(269,430),(250,369)]]")
q=P/'extract-walk-four-armors-v004.py';assert not q.exists();q.write_text(t,'utf-8')
