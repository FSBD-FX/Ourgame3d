"""Measured source pivots only; presentation diagnostic does not edit original PNGs."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record_wrapper',P/'production-record.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w);r=w.r
pivots=[[252,283],[251,295],[284,293],[296,249],[256,270],[253,272]]
sheet=Image.new('RGBA',(1536,1024));rows=[]
for i,pivot in enumerate(pivots):
 p=P/f'processed/call96-peck-fixed-canvas-v001/frame-{i}.png';im=Image.open(p).convert('RGBA');delta=[256-pivot[0],280-pivot[1]]
 display=Image.new('RGBA',(512,512));display.alpha_composite(im,tuple(delta));assert display.getchannel('A').getbbox() and all(display.getpixel(pt)[3]==0 for pt in[(0,0),(511,0),(0,511),(511,511)])
 sheet.alpha_composite(display,(i%3*512,i//3*512))
 rows.append({'index':i,'path':str(p),'sha256':r.sha(p),'source_pivot_px':pivot,'pivot_kind':'manual_same_chest_stone_Yjoint_center_estimate','uncertainty_source_px':6,
  'display_pivot_px':[256,280],'diagnostic_translation_px':delta,'runtime_origin_metadata_only':True,'source_file_pixels_changed':False,'source_scale_changed':False,
  'source_sample_pivot_rgba':list(im.getpixel(tuple(pivot))),'reason':'native_action_has_whole_source_placement_drift_including44px_vertical_between_active2and3; explicit_source_pivots_remove_it_without_claiming_source_layout_stability'})
q=P/'reviews/peck-six-pivot-aligned-assembly-v001.png';q.parent.mkdir(exist_ok=True);assert not q.exists();sheet.save(q);r.archive(q,q.relative_to(P),'actual_source_pixel_pivot_assembly_diagnostic_not_new_generation_or_engine_capture')
j=P/'reviews/peck-six-pivot-measurement-v001.json';r.write(j,{'schema':'manual_stone_bat_chest_pivot_measurement_v1','actor_id':'ENM-STN-002','request':96,'frames':rows,
 'source_layout_passed':False,'source_pixels_changed':False,'uniform_scale':1,'method':'manual_visible_same_chest_junction_point_per_source_frame; uncertainty6px; integer origin only',
 'purpose':'runtime sprite source origin may vary; actual ActorXYZ and collision never read picture bbox','manual_aligned_sequence_review_passed':False,'runtime_verified':False});r.archive(j,j.relative_to(P),'honest_chest_pivot_source_placement_drift_measurement')
print(json.dumps({'report':str(j),'sha256':r.sha(j),'pivots':pivots}))
