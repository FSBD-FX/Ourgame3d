from pathlib import Path
P=Path(__file__).resolve().parent
t=(P/'extract-walk-four-armors-v001.py').read_text('utf-8')
for a,b in [('XBW-walk-four-armors-v001','XBW-walk-four-armors-v002'),('{name}-{i}-v001.png','{name}-{i}-v002.png'),('{name}-selection-v001.png','{name}-selection-v002.png'),('candidate-v001.json','candidate-v002.json')]:t=t.replace(a,b)
q=P/'extract-walk-four-armors-v002.py';assert not q.exists();q.write_text(t,'utf-8')
