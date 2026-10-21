"""Four true native creature keyposes; exact627cells uniformly512, no bboxfit."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=argparse.ArgumentParser();p.add_argument('--number',type=int,required=True);p.add_argument('--action',required=True);a=p.parse_args();ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==a.number)
src=Path(e['raw_path']);assert r.sha(src)==e['sha256'];raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
out=P/f'processed/call{a.number}-{a.action}-four-v001';assert not out.exists();out.mkdir(parents=True);atlas=Image.new('RGBA',(1024,1024));rows=[]
for i in range(4):
 x=i%2*627;y=i//2*627;cell=raw.crop((x,y,x+627,y+627));im=m.clean_edges(m.remove_bg_magenta(cell,threshold=90,edge_threshold=140),depth=3)
 im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
 erased=sum(a[3] and not b[3] and not(a[0]>a[1]+30 and a[2]>a[1]+30) for a,b in zip(cell.get_flattened_data(),im.get_flattened_data()));assert erased==0
 native=out/f'frame-{i}-native627.png';im.save(native);r.archive(native,native.relative_to(P),'actual_native_four_creature_cells_no_creative_processing')
 im=im.resize((512,512),Image.Resampling.LANCZOS);im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
 bbox=im.getchannel('A').getbbox();assert bbox and im.getchannel('A').getextrema()==(0,255);corners=[im.getpixel(pt)[3] for pt in[(0,0),(511,0),(0,511),(511,511)]];assert corners==[0]*4
 q=out/f'frame-{i}.png';im.save(q);r.archive(q,q.relative_to(P),'four_actual_creature_keyposes_uniform_wholecell512_no_fit_or_translation');atlas.alpha_composite(im,(i%2*512,i//2*512))
 rows.append({'index':i,'path':str(q),'sha256':r.sha(q),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,'bbox_px':list(bbox),
  'output_edge_touch':bbox[0]==0 or bbox[1]==0 or bbox[2]==512 or bbox[3]==512,'minimum_output_margin_px':min(bbox[0],bbox[1],512-bbox[2],512-bbox[3]),
  'erased_non_chroma_pixels':erased,'whole_cell_uniform_scale':512/627,'source_geometry_translation':[0,0]})
q=out/'sheet-transparent.png';atlas.save(q);r.archive(q,q.relative_to(P),'four_actual_pose_transparent_source_atlas_not_runtime_acceptance')
j=out/'processing-report.json';r.write(j,{'schema':'native_stone_bat_four_grid_processing_v1','request_number':a.number,'action':a.action,'source':str(src),'source_sha256':r.sha(src),'native_canvas':[1254,1254],
 'grid_rows_cols':[2,2],'frames':rows,'source_frame_count':4,'unique_source_hashes':len({x['sha256'] for x in rows}),'real_alpha_material_pass':True,'geometry':'exact627cells_wholecell512/627_only_no_fit_no_translation',
 'source_body_scale_or_phase_review_passed':False,'runtime_verified':False,'processor':str(sp),'processor_sha256':r.sha(sp)});r.archive(j,j.relative_to(P),'real_four_pose_pixel_and_source_provenance_check')
e.update(status='processed_four_stone_bat_keyposes_pending_pose_aware_review',reviewed_utc=r.now());e.setdefault('processing_revisions',[]).append({'path':str(j),'sha256':r.sha(j)});r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(j),'sha256':r.sha(j),'bboxes':[x['bbox_px'] for x in rows],'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
