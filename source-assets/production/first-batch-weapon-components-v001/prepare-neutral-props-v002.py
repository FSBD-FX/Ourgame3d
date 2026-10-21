"""Prepare deterministic chroma-fringe cleanup revision. No generation."""
from pathlib import Path
P=Path(__file__).resolve().parent
s=(P/'process-neutral-props-v001.py').read_text('utf-8').replace('neutral-props-v001','neutral-props-v002').replace('neutral-component-v001','neutral-component-v002')
s=s.replace('    erased=sum(','''    native_chroma_removed=sum(1 for px in matte.get_flattened_data() if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30)
    matte.putdata([(0,0,0,0) if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30 else px for px in matte.get_flattened_data()])
    erased=sum(''')
s=s.replace('    normalized.putdata([px if px[3] else (0,0,0,0) for px in normalized.get_flattened_data()])', '''    output_chroma_removed=sum(1 for px in normalized.get_flattened_data() if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30)
    normalized.putdata([px if px[3] and not(px[0]>px[1]+30 and px[2]>px[1]+30) else (0,0,0,0) for px in normalized.get_flattened_data()])''')
s=s.replace("'erased_non_chroma_pixels_native':erased", "'erased_non_chroma_pixels_native':erased,'additional_native_chroma_removed_px':native_chroma_removed,'additional_output_chroma_removed_px':output_chroma_removed,'extra_chroma_mask':'R>G+30 and B>G+30; no such material in requested prop'")
q=P/'process-neutral-props-v002.py';assert not q.exists();q.write_text(s,encoding='utf-8');print(q)
