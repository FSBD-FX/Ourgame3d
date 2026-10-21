"""Correct crossbow slot lip sample to opaque physical lip, leaving emit in air."""
from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'prepare-component-socket-review-v001.py').read_text('utf-8')
s=s.replace('socket-diagnostic-v001','socket-diagnostic-v002').replace('measurement-candidate-v001','measurement-candidate-v002').replace('[479,224]','[475,224]')
s=s.replace("if key=='tip_px':assert rgba[3]>0", "if key=='tip_px':assert rgba[3]>0\n        if key=='emit_surface_px':assert rgba[3]>=245")
q=P/'prepare-component-socket-review-v002.py';assert not q.exists();q.write_text(s,encoding='utf-8');print(q)
