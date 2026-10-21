"""Native prop matte and whole-canvas512 normalization; never bboxfit or stretch."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=argparse.ArgumentParser();p.add_argument('--number',type=int,required=True);p.add_argument('--slug',required=True);a=p.parse_args();ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==a.number)
src=Path(e['raw_path']);assert r.sha(src)==e['sha256'];raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
out=P/'processed';out.mkdir(exist_ok=True);native=out/f'{a.slug}-matte-native1254-v001.png';target=out/f'{a.slug}-512-v001.png';assert not native.exists() and not target.exists()
im=m.clean_edges(m.remove_bg_magenta(raw,threshold=90,edge_threshold=140),depth=3);im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
erased=sum(a[3] and not b[3] and not(a[0]>a[1]+30 and a[2]>a[1]+30) for a,b in zip(raw.get_flattened_data(),im.get_flattened_data()));assert erased==0
im.save(native);r.archive(native,native.relative_to(P),'actual_native_prop_matte_no_creative_edit')
im=im.resize((512,512),Image.Resampling.LANCZOS);im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()]);corners=[im.getpixel(pt)[3] for pt in[(0,0),(511,0),(0,511),(511,511)]]
assert im.getchannel('A').getextrema()==(0,255) and corners==[0]*4;im.save(target);r.archive(target,target.relative_to(P),'whole_canvas_uniform512_prop_candidate_no_bboxfit_or_stretch')
report=P/'reviews'/f'{a.slug}-processing-v001.json';report.parent.mkdir(exist_ok=True);r.write(report,{'schema':'single_scene_prop_processing_v1','request_number':a.number,'raw_path':str(src),'raw_sha256':r.sha(src),
 'path':str(target),'sha256':r.sha(target),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,'actual_source_bbox_px':list(im.getchannel('A').getbbox()),
 'native_canvas':[1254,1254],'native_matte_path':str(native),'native_matte_sha256':r.sha(native),'geometry':'whole_canvas512/1254_only; no_crop_no_bboxfit_no_translation_no_anisotropic_scale',
 'erased_non_chroma_native_pixels':erased,'processor_path':str(sp),'processor_sha256':r.sha(sp),'runtime_verified':False,'footprint_or_collision_alignment_verified':False});r.archive(report,report.relative_to(P),'real_prop_pixel_and_provenance_processing_gate_not_collision_alignment')
e.update(status='processed_scene_prop_pending_manual_root_footprint_review',reviewed_utc=r.now());e.setdefault('processing_revisions',[]).append({'path':str(report),'sha256':r.sha(report)});r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(report),'sha256':r.sha(report),'PNG':str(target),'PNG_sha256':r.sha(target),'bbox':list(im.getchannel('A').getbbox()),'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
