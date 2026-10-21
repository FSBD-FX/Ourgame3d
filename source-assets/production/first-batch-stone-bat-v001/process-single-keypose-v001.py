"""Actual native single creature keypose, whole-canvas normalization only."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=argparse.ArgumentParser();p.add_argument('--number',type=int,required=True);p.add_argument('--action',required=True);a=p.parse_args();ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==a.number)
src=Path(e['raw_path']);assert r.sha(src)==e['sha256'];raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
out=P/f'processed/call{a.number}-{a.action}-single-v001';assert not out.exists();out.mkdir(parents=True)
im=m.clean_edges(m.remove_bg_magenta(raw,threshold=90,edge_threshold=140),depth=3);im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
erased=sum(a[3] and not b[3] and not(a[0]>a[1]+30 and a[2]>a[1]+30) for a,b in zip(raw.get_flattened_data(),im.get_flattened_data()));assert erased==0
q=out/'keypose-native1254.png';im.save(q);r.archive(q,q.relative_to(P),'actual_single_native_creature_keypose_matte')
canonical=im.resize((512,512),Image.Resampling.LANCZOS);canonical.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in canonical.get_flattened_data()]);assert canonical.getchannel('A').getextrema()==(0,255)
assert all(canonical.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
q=out/'keypose-canonical512.png';canonical.save(q);r.archive(q,q.relative_to(P),'actual_single_stone_bat_keypose_whole_canvas_normalization_no_fit_or_translation')
ref=P/f'references/stone-bat-{a.action}-keypose{a.number}-magenta512-v001.png';bg=Image.new('RGB',(512,512),(255,0,255));bg.paste(canonical,(0,0),canonical);bg.save(ref);r.archive(ref,ref.relative_to(P),'actual_single_keypose_reference_no_creative_processing')
j=out/'processing-report.json';r.write(j,{'schema':'native_stone_bat_single_keypose_processing_v1','request_number':a.number,'action':a.action,'source':str(src),'source_sha256':r.sha(src),'native_canvas':[1254,1254],
 'path':str(q),'sha256':r.sha(q),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':[0]*4,'bbox_px':list(canonical.getchannel('A').getbbox()),'root_px':[256,280],
 'geometry':'whole_canvas512/1254_only_no_bboxfit_no_translation','erased_non_chroma_native_pixels':erased,'reference':str(ref),'reference_sha256':r.sha(ref),
 'static_alpha_and_material_pass':True,'manual_body_scale_review_passed':False,'runtime_verified':False});r.archive(j,j.relative_to(P),'actual_single_keypose_processing_provenance_no_animation_completion')
e.update(status='single_stone_bat_keypose_processed_pending_scale_review',reviewed_utc=r.now());e.setdefault('processing_revisions',[]).append({'path':str(j),'sha256':r.sha(j)});r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(j),'sha256':r.sha(j),'bbox_px':list(canonical.getchannel('A').getbbox()),'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
