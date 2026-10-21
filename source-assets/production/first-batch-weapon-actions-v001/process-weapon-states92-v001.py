"""Deterministic four native weapon states, exact grid; no creative pixels."""
from pathlib import Path
import importlib.util, json
from PIL import Image, ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==92);src=Path(e['raw_path']);assert r.sha(src)==e['sha256']
raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254)
out=P/'processed/call92-four-weapon-states-v001';assert not out.exists();out.mkdir()
atlas=Image.new('RGBA',(1024,1024));review=Image.new('RGB',(1024,1088),(30,38,42));d=ImageDraw.Draw(review);rows=[]
for i in range(4):
 x=i%2*627;y=i//2*627;cell=raw.crop((x,y,x+627,y+627))
 im=m.clean_edges(m.remove_bg_magenta(cell,threshold=90,edge_threshold=140),depth=3)
 im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
 erased=sum(before[3] and not after[3] and not(before[0]>before[1]+30 and before[2]>before[1]+30) for before,after in zip(cell.get_flattened_data(),im.get_flattened_data()));assert erased==0
 native=out/f'weapon-{i}-native627.png';im.save(native);r.archive(native,native.relative_to(P),'native_complete_crossbow_state_cell_all_components_including_detached_loading_bolt')
 q=im.resize((512,512),Image.Resampling.LANCZOS);q.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in q.get_flattened_data()])
 corners=[q.getpixel(pt)[3] for pt in[(0,0),(511,0),(0,511),(511,511)]];assert corners==[0]*4 and q.getchannel('A').getextrema()==(0,255)
 path=out/f'weapon-{i}.png';q.save(path);r.archive(path,path.relative_to(P),'four_native_reload_weapon_states_no_body_no_boxfit_not_runtime_acceptance')
 atlas.alpha_composite(q,(i%2*512,i//2*512));ox=i%2*512;oy=i//2*544;review.paste(q,(ox,oy+32),q)
 for xx in range(0,512,32):d.line((ox+xx,oy+32,ox+xx,oy+543),fill=(48,60,60));d.text((ox+xx+1,oy+33),str(xx),fill='white')
 for yy in range(0,512,32):d.line((ox,oy+32+yy,ox+511,oy+32+yy),fill=(48,60,60));d.text((ox+1,oy+33+yy),str(yy),fill='white')
 d.text((ox+5,oy+5),f'92 WEAPON STATE {i} local512',fill='white')
 rows.append({'index':i,'source_box_native':[x,y,x+627,y+627],'native_cell_px':[627,627],'canvas_px':[512,512],'scale_all_cells':512/627,'translation':[0,0],
  'path':str(path),'sha256':r.sha(path),'native_path':str(native),'native_sha256':r.sha(native),'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,
  'bbox':list(q.getchannel('A').getbbox()),'erased_non_chroma_pixels':erased})
q=out/'weapon-four-states-transparent.png';atlas.save(q);r.archive(q,q.relative_to(P),'actual_independent_four_weapon_state_atlas_no_body')
j=out/'processing-report.json';r.write(j,{'schema':'native_weapon_four_state_processing_v1','request_number':92,'source':str(src),'source_sha256':r.sha(src),'native_canvas':[1254,1254],
 'grid':[2,2],'frames':rows,'source_weapon_states':4,'unique_source_hashes':len({x['sha256'] for x in rows}),'geometry':'exact627cells_then_uniform512/627_no_bboxfit_no_translation',
 'static_alpha_corner_material_retention_pass':True,'detached_loading_bolt_preserved':True,'processor':str(sp),'processor_sha256':r.sha(sp),'body_fit_or_reload_runtime_accepted':False});r.archive(j,j.relative_to(P),'actual_four_weapon_states_processing_provenance')
q=P/'reviews/call92-four-weapon-state-coordinate-review-v001.png';review.save(q);r.archive(q,q.relative_to(P),'actual_weapon_pixels_with_numeric_grid_for_manual_measurement')
e.update(status='four_native_weapon_states_pending_actual_body_fit_and_contact_review',review_notes='Actual four relaxed/drawn/raised-bolt/seated-bolt states, no third lower cord visually seen. Whole627cells uniform512, no fitted source geometry. Static processing only; no runtime or full reload acceptance.',reviewed_utc=r.now())
e.setdefault('processing_revisions',[]).append({'report':str(j),'sha256':r.sha(j),'weapon_states':4,'scale_all_cells':512/627,'bboxfit':False})
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(j),'sha256':r.sha(j),'bboxes':[x['bbox'] for x in rows],'requested':ledger['requested_count'],'remaining':ledger['remaining_batch_requests']}))
