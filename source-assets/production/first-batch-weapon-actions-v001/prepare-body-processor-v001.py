"""Use existing skill fixed512 processor with explicit chroma fringe removal."""
from pathlib import Path
P=Path(__file__).resolve().parent
s=(P.parent/'first-unit-armor-layers-v001/process-fixed-canvas-v001.py').read_text('utf-8')
s=s.replace("  alpha=cell.getchannel('A')", "  extra_chroma=sum(1 for px in cell.get_flattened_data() if px[3] and px[0]>px[1]+30 and px[2]>px[1]+30)\n  cell.putdata([px if px[3] and not(px[0]>px[1]+30 and px[2]>px[1]+30) else (0,0,0,0) for px in cell.get_flattened_data()])\n  alpha=cell.getchannel('A')")
s=s.replace("'erased_non_chroma_pixels':erased_non_chroma,", "'erased_non_chroma_pixels':erased_non_chroma,'extra_chroma_removed_px':extra_chroma,")
s=s.replace("'matte_function':f'generate2dsprite.remove_bg_magenta({threshold},{edge_threshold})+clean_edges(3)'", "'matte_function':f'generate2dsprite.remove_bg_magenta({threshold},{edge_threshold})+clean_edges(3)+explicit_R_G30_B_G30_chroma_mask'")
q=P/'process-body-fixed-canvas-v001.py';assert not q.exists();q.write_text(s,encoding='utf-8');print(q)
