from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'select-primary2-ROB-sleeves-v004.py').read_text('utf-8')
source=source.replace('primary2-ROB-real-sleeves-v004','primary2-ROB-real-sleeves-v005').replace('primary2-ROB-real-sleeves-candidate-v004','primary2-ROB-real-sleeves-candidate-v005')
source=source.replace('-{i}-v004.png','-{i}-v005.png').replace('sleeves-v004.png','sleeves-v005.png')
source=source.replace("selection={'weapon_forearm':tr.w.poly(ARM_CLOTH_ENVELOPES[i]),'other_forearm':tr.w.poly(OTHER_CLOTH_ENVELOPES[i])}", "selection={'weapon_forearm':tr.w.poly(ARM_CLOTH_ENVELOPES[i]).filter(ImageFilter.MaxFilter(7)),'other_forearm':tr.w.poly(OTHER_CLOTH_ENVELOPES[i]).filter(ImageFilter.MaxFilter(7))}")
source=source.replace("'source_geometry_transform':'none'", "'source_geometry_transform':'none','selection_edge_envelope_dilation_px':3")
target=P/'select-primary2-ROB-sleeves-v005.py';assert not target.exists();target.write_text(source,'utf-8');print(target)
