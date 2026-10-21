"""Visible source pixel decomposition trial; no occluded body filling or artwork."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
src=P/'processed/call86-single-keypose-v001/keypose-canonical512.png';source=Image.open(src).convert('RGBA')
out=P/'decomposition-trials/keypose86-v002';assert not out.exists();out.mkdir(parents=True)
nearpoly=[(288,269),(301,263),(317,260),(330,262),(340,266),(347,273),(347,283),(341,292),(328,294),(312,292),(301,292),(289,288)]
supportpoly=[(300,309),(312,307),(323,306),(334,310),(340,317),(341,329),(337,339),(327,343),(315,340),(305,336),(299,327)]
weaponpoly=[(173,302),(177,300),(193,300),(204,305),(216,309),(222,298),(227,294),(239,292),(250,288),(266,286),(273,287),(283,286),(339,285),(342,251),(346,247),(354,248),(365,253),(378,265),(385,277),(385,283),(401,283),(402,293),(390,296),(386,310),(380,325),(370,335),(353,343),(344,343),(341,337),(341,310),(275,315),(265,315),(263,327),(255,331),(245,333),(233,331),(230,326),(218,324),(212,332),(205,335),(195,339),(174,339)]
triggerhole=[(251,315),(256,315),(257,320),(255,326),(251,328),(247,327),(247,323),(250,322)]
def polygon(poly):
    m=Image.new('L',(512,512),0);ImageDraw.Draw(m).polygon(poly,fill=255);return m
nm=polygon(nearpoly);sm=polygon(supportpoly);assert not ImageChops.multiply(nm,sm).getbbox()
bow_region=Image.new('L',(512,512),0);ImageDraw.Draw(bow_region).rectangle((339,245,405,346),fill=255)
wm=ImageChops.multiply(ImageChops.lighter(polygon(weaponpoly),bow_region),ImageChops.invert(polygon(triggerhole)))
wm=ImageChops.multiply(wm,ImageChops.invert(ImageChops.lighter(nm,sm)))
fm=ImageChops.invert(ImageChops.lighter(wm,ImageChops.lighter(nm,sm)))
def selected(m):
    im=source.copy();im.putalpha(ImageChops.multiply(source.getchannel('A'),m));im.putdata([p if p[3] else(0,0,0,0) for p in im.get_flattened_data()]);return im
masks={'body_far':fm,'weapon_core':wm,'body_support':sm,'body_near':nm};parts={key:selected(m) for key,m in masks.items()};rows=[]
rebuild=Image.new('RGBA',(512,512));preview=Image.new('RGBA',(2048,512))
for i,(key,im) in enumerate(parts.items()):
    q=out/f'{key}.png';im.save(q);r.archive(q,q.relative_to(P),'semantic_visible_source_split_trial_NOT_frozen_or_importable')
    maskq=out/f'{key}-mask.png';masks[key].save(maskq);r.archive(maskq,maskq.relative_to(P),'manual_source_polygon_trial_mask')
    rebuild.alpha_composite(im);preview.alpha_composite(im,(i*512,0));rows.append({'track':key,'path':str(q),'sha256':r.sha(q),'canvas_px':[512,512],
      'mode':'RGBA','alpha_extrema':list(im.getchannel('A').getextrema()),'bbox':list(im.getchannel('A').getbbox())})
assert rebuild.tobytes()==source.tobytes()
q=P/'reviews/XBW-keypose86-decomposition-trial-v002.png';preview.save(q);r.archive(q,q.relative_to(P),'four_visible_source_tracks_trial_requires_semantic_review_not_runtime_art')
report={'schema':'visible_source_decomposition_trial_v1','source':str(src),'source_sha256':r.sha(src),'parts':rows,'draw_order':list(parts),'source_exact_RGBA_reconstruction':True,
 'semantic_masks_manually_reviewed':False,'hidden_body_regions_inferred_or_painted':False,'occluded_body_unknown':True,'body_generic_swap_compatible':False,
 'part_geometry_transform':'none','weapon_to_body_affine':[1,0,0,0,1,0],'near_hand_role':'string_manipulation_not_rear_primary_stock_grip',
 'support_grip_body_px':[323,323],'near_string_contact_body_px':[342,282],'outlet_body_px':[404,289],
 'marker_status':'manual_visual_candidate_not_skeleton_or_worldZ_authority','runtime_import_allowed':False,'full_reload_accepted':False,
 'limitations':['Exact reconstruction proves partition only, not semantic selection correctness.','Polygon borders may still include cloth or miss weapon contours; inspect and revise in a new version.',
 'Body under stock/bow/cord is missing in the integrated native source. These coupled tracks cannot silently stand in for a universal clean body.']}
j=out/'trial-report.json';r.write(j,report);r.archive(j,j.relative_to(P),'actual_decomposition_trial_honest_semantic_and_hidden_pixel_boundary')
print(json.dumps({'trial':str(j),'sha256':r.sha(j),'parts':4,'exact_rebuild':True,'runtime_import_allowed':False}))
