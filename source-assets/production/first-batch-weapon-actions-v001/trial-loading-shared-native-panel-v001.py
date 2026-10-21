"""Runtime-style assembly from real native source panels, no pixels painted."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
basep=P/'processed/call90-single-keypose-v001/keypose-canonical512.png';sharedp=P/'processed/call89-single-keypose-v001/keypose-canonical512.png'
base=Image.open(basep).convert('RGBA');shared=Image.open(sharedp).convert('RGBA');assert base.size==shared.size==(512,512)
out=P/'decomposition-trials/loading-shared-panel-v001';assert not out.exists();out.mkdir(parents=True)
poly=[(289,294),(388,294),(385,305),(312,307),(289,307)]
mask=Image.new('L',(512,512),0);ImageDraw.Draw(mask).polygon(poly,fill=255)
selected=shared.copy();selected.putalpha(ImageChops.multiply(shared.getchannel('A'),mask));selected.putdata([p if p[3] else(0,0,0,0) for p in selected.get_flattened_data()])
canvas=base.copy();canvas.putalpha(ImageChops.multiply(base.getchannel('A'),ImageChops.invert(mask)));canvas.alpha_composite(selected)
outside_changed=sum(1 for p,q,m in zip(base.get_flattened_data(),canvas.get_flattened_data(),mask.get_flattened_data()) if not m and p!=q);assert outside_changed==0
opaque_count=sum(m and px[3]==255 for m,px in zip(mask.get_flattened_data(),shared.get_flattened_data()));mask_count=sum(bool(m)for m in mask.get_flattened_data())
patch=out/'actual-weapon-wood-panel89.png';selected.save(patch);r.archive(patch,patch.relative_to(P),'actual_native_source89_panel_component_no_painted_pixels')
maskq=out/'source89-panel-selection-mask.png';mask.save(maskq);r.archive(maskq,maskq.relative_to(P),'actual_shared_panel_geometry_selection_not_artwork')
q=out/'loading-composite-reference.png';canvas.save(q);r.archive(q,q.relative_to(P),'two_native_source_panel_composite_TRIAL_not_raw90_repaired_or_runtime_accepted')
crop=P/'reviews/loading-shared-panel-contact-v001.png';canvas.crop((210,240,410,355)).resize((800,460),Image.Resampling.NEAREST).save(crop);r.archive(crop,crop.relative_to(P),'actual_two_source_composite_contact_review')
report={'schema':'native_shared_component_panel_trial_v1','base_source':str(basep),'base_source_sha256':r.sha(basep),'shared_source':str(sharedp),'shared_source_sha256':r.sha(sharedp),
 'shared_panel':str(patch),'shared_panel_sha256':r.sha(patch),'shared_panel_polygon_px':poly,'geometry_transform':'none_same512canvas',
 'output':str(q),'output_sha256':r.sha(q),'outside_selection_changed_pixels':outside_changed,'selected_mask_pixels':mask_count,'selected_shared_opaque_pixels':opaque_count,
 'source_art_pixels_painted_or_color_generated':False,'raw90_unchanged':True,'raw90_native_repair_success_claimed':False,
 'exact_reconstruction_of_raw90_claimed':False,'purpose':'feasibility of selecting real clean source89 wood panel to cover source90 duplicate rope, same runtime component composition route',
 'semantic_material_selection_review_pending':True,'source_unseen_body_not_invented':True,'full_reload_accepted':False,'runtime_import_allowed':False}
j=out/'trial-report.json';r.write(j,report);r.archive(j,j.relative_to(P),'native_component_reuse_trial_provenance_no_raw_repair_or_generic_body_claim')
print(json.dumps({'trial':str(j),'sha256':r.sha(j),'outside_changed':outside_changed,'patch_opaque_fraction':opaque_count/mask_count,'runtime_import_allowed':False}))
