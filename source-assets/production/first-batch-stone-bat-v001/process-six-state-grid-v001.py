"""Real creature grid postprocessor; never bbox-fit or reinterpret wing bbox as body size."""
from pathlib import Path
import argparse,importlib.util,json
from PIL import Image
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
sp=Path('C:/Users/22499/.codex/skills/generate2dsprite/scripts/generate2dsprite.py');s=importlib.util.spec_from_file_location('processor',sp);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=argparse.ArgumentParser();a.add_argument('--number',type=int,required=True);a.add_argument('--action',required=True);args=a.parse_args()
ledger=r.read(r.LEDGER);e=next(x for x in ledger['requests'] if x['request_number']==args.number);src=Path(e['raw_path']);assert r.sha(src)==e['sha256'];raw=Image.open(src).convert('RGBA');assert raw.size==(1536,1024)
out=P/f'processed/call{args.number}-{args.action}-fixed-canvas-v001';assert not out.exists();out.mkdir(parents=True)
atlas=Image.new('RGBA',(1536,1024));rows=[]
for i in range(6):
 x=i%3*512;y=i//3*512;cell=raw.crop((x,y,x+512,y+512));im=m.clean_edges(m.remove_bg_magenta(cell,threshold=90,edge_threshold=140),depth=3)
 im.putdata([p if p[3] and not(p[0]>p[1]+30 and p[2]>p[1]+30) else(0,0,0,0) for p in im.get_flattened_data()])
 erased=sum(a[3] and not b[3] and not(a[0]>a[1]+30 and a[2]>a[1]+30) for a,b in zip(cell.get_flattened_data(),im.get_flattened_data()));assert erased==0
 bbox=im.getchannel('A').getbbox();assert bbox is not None
 corners=[im.getpixel(pt)[3] for pt in[(0,0),(511,0),(0,511),(511,511)]];assert corners==[0]*4 and im.getchannel('A').getextrema()==(0,255)
 path=out/f'frame-{i}.png';im.save(path);r.archive(path,path.relative_to(P),'actual_native_creature_action_cell_no_boxfit_no_root_motion_no_runtime_acceptance');atlas.alpha_composite(im,(x,y))
 edge=bool(bbox[0]==0 or bbox[1]==0 or bbox[2]==512 or bbox[3]==512);margin=min(bbox[0],bbox[1],512-bbox[2],512-bbox[3])
 rows.append({'index':i,'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':[0,255],'corner_alpha':corners,'bbox_px':list(bbox),'output_edge_touch':edge,'minimum_output_margin_px':margin,
  'requested_safe_envelope_met':bbox[0]>=48 and bbox[1]>=80 and bbox[2]<=424 and bbox[3]<=416,'erased_non_chroma_pixels':erased,'body_pivot_px':[256,280],'geometry_transform':'exact_grid512_no_translation_no_scale'})
q=out/'sheet-transparent.png';atlas.save(q);r.archive(q,q.relative_to(P),'actual_six_creature_source_frames_transparent_atlas_not_animation_acceptance')
profile=P/'manifests/stone-bat-identity-profile-v001.json';j=out/'processing-report.json';r.write(j,{'schema':'native_stone_bat_six_grid_processing_v1','request_number':args.number,'action':args.action,'source':str(src),'source_sha256':r.sha(src),
 'native_canvas':[1536,1024],'grid_rows_cols':[2,3],'frames':rows,'source_frame_count':6,'unique_source_hashes':len({x['sha256'] for x in rows}),'profile':str(profile),'profile_sha256':r.sha(profile),
 'real_alpha_and_material_retention_pass':True,'output_edge_touch_frames':[x['index'] for x in rows if x['output_edge_touch']],'near_edge_under8px_frames':[x['index'] for x in rows if x['minimum_output_margin_px']<8],
 'requested_envelope_exceed_frames':[x['index'] for x in rows if not x['requested_safe_envelope_met']],
 'pose_aware_scope':'wing extension changes silhouette legitimately; torso/head scale must be visually reviewed; humanoid standing_bbox_CV_is_not_flight_gate',
 'source_body_scale_or_phase_review_passed':False,'runtime_verified':False,'processor':str(sp),'processor_sha256':r.sha(sp)});r.archive(j,j.relative_to(P),'real_pixel_processing_and_honest_edge_envelope_diagnostics')
e.update(status='processed_six_stone_bat_source_frames_pending_pose_aware_review',reviewed_utc=r.now(),review_notes='Six actual native512cells, realalpha/material checks, no fit/translation. Wing-bbox variation not body scaling proof; actual near-edge/envelope flags reported.')
e.setdefault('processing_revisions',[]).append({'path':str(j),'sha256':r.sha(j)});r.write(r.LEDGER,ledger)
for folder in r.ARCHIVES:r.write(folder/'generation-ledger-snapshot.json',ledger)
print(json.dumps({'report':str(j),'sha256':r.sha(j),'bboxes':[x['bbox_px'] for x in rows],'edges':[x['index'] for x in rows if x['output_edge_touch']],'near_edges':[x['index'] for x in rows if x['minimum_output_margin_px']<8],'requested':ledger['requested_count']}))
