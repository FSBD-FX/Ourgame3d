"""Reference only: frozen lower-body pixels with ready upper-body pixels. Never a deliverable body."""
from pathlib import Path
import importlib.util
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rec',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
old=P.parent/'first-unit-animation-v003/assembly-markers-import-v007.json'
ready=P.parent/'first-batch-weapon-actions-v001/manifests/import-XBW-ready-idle-v001.json'
walk=next(x for x in r.read(old)['actions'] if x['action']=='walk')['frames']
base=Image.open(P/'references/frozen-XBW-ready-idle-pose-plate-v001.png').convert('RGBA').crop((0,0,512,512))
sheet=Image.new('RGBA',(1536,1024),(255,0,255,255));rows=[]
for i,f in enumerate(walk):
 src=Path(f['frame_path']);assert r.sha(src)==f['frame_sha256'];leg=Image.open(src).convert('RGBA')
 dx=262-f['belt_proxy_px'][0];dy=338-f['belt_proxy_px'][1]
 cell=base.copy();cell.paste((255,0,255,255),(0,350,512,512))
 lower=leg.crop((0,350,512,512));cell.alpha_composite(lower,(dx,350+dy))
 sheet.paste(cell,((i%3)*512,(i//3)*512))
 rows.append({'frame_index':i,'source_path':str(src),'sha256':r.sha(src),'reference_only_translation_px':[dx,dy],'crop_y_min_px':350})
out=P/'references/XBW-walk-structure-guide-v001.png';assert not out.exists();sheet.save(out);r.archive(out,out.relative_to(P),'reference_only_splice_not_game_art_or_complete_pose')
q=P/'references/XBW-walk-structure-guide-provenance-v001.json';r.write(q,{'schema':'reference-only-pose-splice-v1','guide_path':str(out),'guide_sha256':r.sha(out),'upper_reference_path':str(P/'references/frozen-XBW-ready-idle-pose-plate-v001.png'),'upper_reference_sha256':r.sha(P/'references/frozen-XBW-ready-idle-pose-plate-v001.png'),'lower_sources':rows,'deliverable':False,'actual_new_body_must_come_from_imagegen':True});r.archive(q,q.relative_to(P),'reference_provenance_no_runtime_asset')
