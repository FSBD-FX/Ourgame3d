"""Preserve one already-reviewed assembled cell for mechanical keypose reference."""
from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
src=P/'reviews/XBW-ready-idle-assembled_right-v001.png';q=P/'references/XBW-ready-assembled-cell0-v001.png';assert not q.exists()
Image.open(src).crop((0,0,512,512)).save(q);r.archive(q,q.relative_to(P),'existing_frozen_assembly_cell_reference_no_geometry_change')
j=q.with_suffix('.json');r.write(j,{'source':str(src),'source_sha256':r.sha(src),'source_crop':[0,0,512,512],'output':str(q),'output_sha256':r.sha(q),'scale':1,'translation_in_cell':[0,0],'creative_art_added':False});r.archive(j,j.relative_to(P),'reference_extraction_provenance')
print(q)
