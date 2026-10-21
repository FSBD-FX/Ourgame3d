"""Unaltered native source contact crops, archived before viewing."""
from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
ledger=r.read(r.LEDGER)
for number in [86,87,88]:
    e=next(x for x in ledger['requests'] if x['request_number']==number);src=Path(e['raw_path']);q=P/f'reviews/XBW-mechanical-contact-{number}-native-crop-v001.png';assert not q.exists()
    Image.open(src).crop((520,590,1010,870)).resize((980,560),Image.Resampling.NEAREST).save(q);r.archive(q,q.relative_to(P),'actual_source_contact_crop2x_nearest_not_runtime_art')
    j=q.with_suffix('.json');r.write(j,{'source':str(src),'source_sha256':r.sha(src),'crop_native_px':[520,590,1010,870],'display_scale':2,'interpolation':'NEAREST','output':str(q),'output_sha256':r.sha(q),'creative_art_added':False});r.archive(j,j.relative_to(P),'review_crop_provenance')
    print(q)
