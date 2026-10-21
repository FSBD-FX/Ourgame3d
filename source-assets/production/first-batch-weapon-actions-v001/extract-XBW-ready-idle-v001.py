"""Separate real near/support hands; assemble the real XBW with fixed transform."""
from pathlib import Path
import importlib.util,math,json
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
weapon_contract=P.parent/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json'
w=r.read(weapon_contract)['weapons']['WPN-XBW-001'];weapon=Image.open(w['path']).convert('RGBA')
out=P/'components/XBW-ready-idle-v001';assert not out.exists();out.mkdir(parents=True)
near_poly=[(213,296),(225,295),(236,299),(241,307),(241,321),(234,331),(221,335),(210,331),(205,323),(205,307)]
near_wrist=[(198,299),(211,296),(218,305),(215,326),(205,331),(198,321)]
support_poly=[(315,304),(326,302),(336,307),(340,319),(336,331),(327,338),(315,335),(309,328),(308,315)]
support_wrist=[(302,306),(315,303),(320,313),(316,332),(305,330),(300,319)]
def union(polygons):
    mask=Image.new('L',(512,512),0);d=ImageDraw.Draw(mask)
    for poly in polygons:d.polygon(poly,fill=255)
    return mask
near_mask=union([near_poly,near_wrist]);support_mask=union([support_poly,support_wrist]);assert ImageChops.multiply(near_mask,support_mask).getbbox() is None
all_hands=ImageChops.lighter(near_mask,support_mask)
def select(source,mask):
    q=source.copy();q.putalpha(ImageChops.multiply(source.getchannel('A'),mask));q.putdata([px if px[3] else (0,0,0,0) for px in q.get_flattened_data()]);return q
def save(image,path,status):
    image.save(path);copies=r.archive(path,path.relative_to(P),status);assert all(r.sha(Path(x))==r.sha(path) for x in copies)
    return {'path':str(path),'sha256':r.sha(path),'canvas_px':[512,512],'mode':'RGBA','alpha_extrema':list(image.getchannel('A').getextrema()),'bbox_px':list(image.getchannel('A').getbbox()),'F_E_copies_verified':True}
for name,mask in [('near',near_mask),('support',support_mask)]:
    q=P/f'masks/XBW-ready-idle-{name}-v001.png';q.parent.mkdir(exist_ok=True);mask.save(q);r.archive(q,q.relative_to(P),'manual_actual_distal_grip_and_short_wrist_semantic_selection')
scale=.48;angle=-5.;a=math.radians(angle);co=math.cos(a);si=math.sin(a);grip=[224,316];support_grip=[325,321]
def point(p):
    x=p[0]-w['primary_grip_px'][0];y=p[1]-w['primary_grip_px'][1]
    return [grip[0]+scale*(co*x-si*y),grip[1]+scale*(si*x+co*y)]
actual_support=point(w['support_grip_px']);emit=point(w['emit_px']);error=math.dist(actual_support,support_grip);assert error<1
render=weapon.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,w['primary_grip_px'][0]-(co*grip[0]+si*grip[1])/scale,-si/scale,co/scale,w['primary_grip_px'][1]-(-si*grip[0]+co*grip[1])/scale),resample=Image.Resampling.BICUBIC)
sheets={name:Image.new('RGBA',(1536,1024),(0,0,0,0)) for name in ['body_far','body_support','body_near','assembled_right','assembled_left']};rows=[]
for i in range(6):
    src=P/f'processed/call81-fixed-canvas-v001/frame-{i}.png';source=Image.open(src).convert('RGBA')
    near=select(source,near_mask);support=select(source,support_mask);far=select(source,ImageChops.invert(all_hands))
    reconstructed=far.copy();reconstructed.alpha_composite(support);reconstructed.alpha_composite(near);assert reconstructed.tobytes()==source.tobytes()
    assert source.getpixel(tuple(grip))[3]==255 and source.getpixel(tuple(support_grip))[3]==255
    parts={key:save(im,out/f'{key}-{i}.png','actual_XBW_body_and_two_distal_hand_tracks_candidate_pending_assembly_review') for key,im in [('body_far',far),('body_support',support),('body_near',near)]}
    assembled=far.copy();assembled.alpha_composite(render);assembled.alpha_composite(support);assembled.alpha_composite(near)
    mirrored=assembled.transform((512,512),Image.Transform.AFFINE,(-1,0,512,0,1,0),resample=Image.Resampling.NEAREST)
    for name,image in [('body_far',far),('body_support',support),('body_near',near),('assembled_right',assembled),('assembled_left',mirrored)]:sheets[name].alpha_composite(image,((i%3)*512,(i//3)*512))
    rows.append({'index':i,'source_body_path':str(src),'source_body_sha256':r.sha(src),'parts':parts,
     'ground_root_px':[256,472],'root_kind':'existing_profile_origin_preserved; source_boot_bbox_bottom483_not_new_footlock_certificate',
     'grip_px':grip,'primary_grip_px':grip,'support_grip_px':support_grip,'sampled_grip_RGBA':list(source.getpixel(tuple(grip))),'sampled_support_RGBA':list(source.getpixel(tuple(support_grip))),
     'weapon_scale':scale,'weapon_angle_image_clockwise_deg':angle,'component_primary_grip_px':w['primary_grip_px'],'component_support_grip_px':w['support_grip_px'],
     'transformed_support_px':actual_support,'support_alignment_error_px':error,'component_emit_px':w['emit_px'],'transformed_emit_body_px':emit,
     'emit_delta_from_ground_root_body_px':[emit[0]-256,emit[1]-472],'phase':'ready_idle','time_start_s':i*.15,'time_end_s':(i+1)*.15,
     'body_three_track_exact_source_reconstruction':True,'hand_selection_scope':'actual_original_distal_trigger_fist_and_support_fist_with_short_wrist_only',
     'damage_or_projectile_emission_events':[]})
for name,image in sheets.items():
    q=P/f'reviews/XBW-ready-idle-{name}-v001.png';q.parent.mkdir(exist_ok=True);image.save(q);r.archive(q,q.relative_to(P),'two_hand_XBW_static_assembly_review_not_shoot_or_reload_acceptance')
q=P/'reviews/XBW-ready-idle-layer-candidate-v001.json';assert not q.exists();r.write(q,{'schema':'XBW_ready_three_body_track_candidate_v1','request_number':81,'frames':rows,
 'canvas_px':[512,512],'frame_count':6,'unique_source_body_hashes':len({x['source_body_sha256'] for x in rows}),'weapon_contract':str(weapon_contract),'weapon_contract_sha256':r.sha(weapon_contract),
 'weapon':w,'draw_order':['body_far','independent_XBW_weapon','body_support','body_near'],'fixed_component_scale_all_frames':scale,'fixed_component_angle_all_frames_deg':angle,
 'skin_or_limb_repaint':False,'source_geometry_transform':'none','manual_review_passed':False,'runtime_verified':False,
 'limitations':['Only common-underclothes XBW ready idle; four armor appearance surfaces are not made for this new pose.',
  'No firing, cocking, reload, spell, damage or world-origin authority is certified by static assembly.',
  'Actual grip centers are manual image measurements, not skeleton joints. Support fit below1sourcepx in this geometry model still requires running-game contact/occlusion review.',
  'Root256472 is the inherited source profile origin. Boots extend to483; this does not certify physical footlock.']})
r.archive(q,q.relative_to(P),'actual_two_hand_XBW_ready_source_and_fixed_component_matrix_candidate');print({'new_runtime_body_PNGs':18,'unique_body_source_hashes':len({x['source_body_sha256'] for x in rows}),'support_error_px':error,'emit_px':emit})
