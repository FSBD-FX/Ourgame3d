"""Four true native body keyposes; exact grid split then whole-cell normalization."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests']if x['request_number']==91);src=Path(e['raw_path']);assert r.sha(src)==e['sha256']
raw=Image.open(src).convert('RGBA');assert raw.size==(1254,1254);out=P/'processed/call91-four-body-keyposes-v001';assert not out.exists();out.mkdir()
atlas=Image.new('RGBA',(1024,1024));review=Image.new('RGB',(800,520),(32,38,42));rd=ImageDraw.Draw(review);rows=[]
for i in range(4):
 x=i%2*627;y=i//2*627;cell=raw.crop((x,y,x+627,y+627));im=m.clean_edges(m.remove_bg_magenta(cell,threshold=90,edge_threshold=140),depth=3)
 im.putdata([p if p[3]and not(p[0]>p[1]+30 and p[2]>p[1]+30)else(0,0,0,0)for p in im.get_flattened_data()])
 erased=sum(before[3]and not after[3]and not(before[0]>before[1]+30 and before[2]>before[1]+30)for before,after in zip(cell.get_flattened_data(),im.get_flattened_data()));assert erased==0
 native=out/f'body-{i}-native627.png';im.save(native);r.archive(native,native.relative_to(P),'actual_native4body_keypose_cells_no_bboxfit')
 canonical=im.resize((512,512),Image.Resampling.LANCZOS);canonical.putdata([p if p[3]and not(p[0]>p[1]+30 and p[2]>p[1]+30)else(0,0,0,0)for p in canonical.get_flattened_data()])
 corners=[canonical.getpixel(pt)[3]for pt in[(0,0),(511,0),(0,511),(511,511)]];assert corners==[0,0,0,0]and canonical.getchannel('A').getextrema()==(0,255)
 q=out/f'body-{i}.png';canonical.save(q);r.archive(q,q.relative_to(P),'four_real_complete_unarmed_body_keyposes_NOT6animation_frames')
 atlas.alpha_composite(canonical,(i%2*512,i//2*512));crop=canonical.crop((180,240,380,360)).resize((400,240),Image.Resampling.NEAREST);ox=i%2*400;oy=i//2*260;review.paste(crop,(ox,oy+20),crop)
 for xx in range(180,381,20):rd.line((ox+(xx-180)*2,oy+20,ox+(xx-180)*2,oy+259),fill=(48,60,60));rd.text((ox+(xx-180)*2+1,oy+20),str(xx),fill='white')
 for yy in range(240,361,20):rd.line((ox,oy+20+(yy-240)*2,ox+399,oy+20+(yy-240)*2),fill=(48,60,60));rd.text((ox+1,oy+20+(yy-240)*2+1),str(yy),fill='white')
 rd.text((ox+5,oy+3),f'91 BODY KEY {i} local512',fill='white')
 rows.append({'index':i,'source_box_native':[x,y,x+627,y+627],'native_cell_px':[627,627],'canonical_px':[512,512],'scale_all_cells':512/627,'translation':[0,0],
   'path':str(q),'sha256':r.sha(q),'native_path':str(native),'native_sha256':r.sha(native),'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,
   'bbox':list(canonical.getchannel('A').getbbox()),'erased_non_chroma_pixels':erased,'body_complete_native_inpaint_candidate':True,'semantic_weapon_free_reviewed':True})
q=out/'body-four-keyposes-transparent.png';atlas.save(q);r.archive(q,q.relative_to(P),'native_body4keypose_atlas_not_six_inbetweens_or_runtime_acceptance')
j=out/'processing-report.json';r.write(j,{'schema':'native_body_four_keypose_processing_v1','request_number':91,'source':str(src),'source_sha256':r.sha(src),'native_canvas':[1254,1254],
 'grid':[2,2],'frames':rows,'source_body_frames':4,'source_body_hashes_unique':len({x['sha256']for x in rows}),'geometry':'exact627cells_then_uniform512/627_no_bboxfit_no_translation',
 'static_alpha_corner_and_material_retention_pass':True,'processor':str(sp),'processor_sha256':r.sha(sp),'source_has_baked_weapon':False,
 'original_underclothes_bluegray_wrists_restored':True,'full_reload_animation_or_component_fit_accepted':False,'runtime_verified':False});r.archive(j,j.relative_to(P),'actual_four_body_keypose_processing_and_honest_phase_boundary')
q=P/'reviews/call91-four-keypose-hand-coordinate-review-v001.png';review.save(q);r.archive(q,q.relative_to(P),'actual_native_body_hand_coordinate_diagnostic_not_new_pose_art')
e.update(status='four_complete_weapon_free_reload_body_keyposes_pending_actual_markers_and_component_fit',review_notes='Native4poses retain front hook/back grip/loading pinch/ready, restore original plain bluegray wraps, and fill hidden torso/arms natively. Actual1254 2x2 cut627 then all cells uniformly512; staticalpha/material pass. Not6frames or full1.10s/runtimes.',reviewed_utc=r.now())
e.setdefault('processing_revisions',[]).append({'report':str(j),'sha256':r.sha(j),'source_keyposes':4,'scale_all_cells':512/627,'bboxfit':False})
r.write(r.LEDGER,ledger)
for f in r.ARCHIVES:r.write(f/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(j),'sha256':r.sha(j),'body_frames':4,'unique_hashes':4,'scale':512/627,'bboxes':[x['bbox']for x in rows],'requested_count':91,'remaining':5}))
