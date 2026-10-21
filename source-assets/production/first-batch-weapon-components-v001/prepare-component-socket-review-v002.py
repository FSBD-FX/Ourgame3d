"""Manual existing-pixel landmarks and geometric diagnostic marks, not sprite art."""
from pathlib import Path
import importlib.util,json,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
specs={
 'XBW':{'primary_grip_px':[128,253],'support_grip_px':[337,282],'emit_px':[489,224],'emit_surface_px':[475,224],
        'tip_px':None,'cocking_lever_grip_px':[137,205],'trigger_px':[174,268],'canonical_forward_axis':[1,0],
        'emit_kind':'manual_visible_open_forward_bolt_slot_exit_in_clear_air; alpha0_expected',
        'handling':'two_hands; primary_leather_stock_neck_and_support_vertical_foregrip',
        'limitations':['Single neutral empty crossbow only. No loaded/released string or cocking-lever states.',
          'The visible forward slot establishes the candidate emission point; actual actor shoot/reload hand poses and world muzzle height remain unverified.']},
 'STF':{'primary_grip_px':[181,251],'support_grip_px':[282,251],'emit_px':[499,251],'emit_surface_px':[492,251],
        'tip_px':[495,251],'canonical_forward_axis':[1,0],
        'emit_kind':'manual_forward_lantern_lens_exit_in_clear_air; lens_surface_separate_opaque_marker',
        'handling':'primary_wrapped_grip; optional_support_on_unobstructed_wood_shaft',
        'limitations':['Lantern contains bounded ember/candle artwork, not a detached fireball/FX animation.',
          'Primary cast and downward fireline require distinct body motions. Neutral component does not provide either motion.']},
 'SPR':{'primary_grip_px':[137,253],'support_grip_px':[326,253],'emit_px':None,'emit_surface_px':None,
        'tip_px':[488,253],'canonical_forward_axis':[1,0],
        'emit_kind':'none_melee_spear','handling':'two_hands_rear_and_front_leather_bands',
        'limitations':['Spear-tip landmark is artwork geometry, not a change to combat range or weak zone.',
          'Actual paired-hand thrust body frames, nearest-target skill presentation and transitions remain unverified.']},
 'GSW':{'primary_grip_px':[169,256],'support_grip_px':[101,256],'emit_px':None,'emit_surface_px':None,
        'tip_px':[494,256],'canonical_forward_axis':[1,0],
        'emit_kind':'none_melee_greatsword','handling':'two_hands_front_and_rear_of_long_leather_handle',
        'limitations':['Broad chisel blade/long grip provides distinct heavy weapon silhouette only.',
          'Current singlehand sword body frames do not certify a twohand heavy swing; new body poses/weight recovery remain required.']}}
rows={}
for family,markers in specs.items():
    path=P/f'components/{family}001-neutral-component-v002.png';image=Image.open(path).convert('RGBA');assert image.size==(512,512)
    measured={}
    for key,point in markers.items():
        if not key.endswith('_px') or point is None:continue
        rgba=list(image.getpixel(tuple(point)));measured[key]=rgba
        if key in ['primary_grip_px','support_grip_px']:assert rgba[3]>=245
        if key=='tip_px':assert rgba[3]>0
        if key=='emit_surface_px':assert rgba[3]>=245
        if key=='emit_px':assert rgba[3]==0
    drawimage=Image.new('RGBA',(512,512),(30,35,39,255));drawimage.alpha_composite(image);d=ImageDraw.Draw(drawimage)
    for key,color in [('primary_grip_px',(70,170,255,255)),('support_grip_px',(80,240,130,255)),('emit_px',(255,100,80,255)),('tip_px',(250,250,230,255))]:
        point=markers.get(key)
        if point is None:continue
        x,y=point;d.line([(x-6,y),(x+6,y)],fill=color,width=1);d.line([(x,y-6),(x,y+6)],fill=color,width=1)
        label=key.removesuffix('_px')+f' {x},{y}';tx=min(max(3,x-35),350);d.text((tx,y+12 if key!='support_grip_px' else y-24),label,fill=color)
    d.text((12,12),family+' neutral component: manual socket review only',fill=(240,240,240,255))
    q=P/f'reviews/{family}001-socket-diagnostic-v002.png';assert not q.exists();q.parent.mkdir(exist_ok=True);drawimage.save(q)
    r.archive(q,q.relative_to(P),'manual_landmarks_over_actual_prop_not_runtime_sprite_or_motion_proof')
    rows[family]={'weapon_id':f'WPN-{family}-001','path':str(path),'sha256':r.sha(path),**markers,
         'sampled_landmark_RGBA':measured,'support_distance_px':math.dist(markers['primary_grip_px'],markers['support_grip_px']),
         'manual_measurement_status':'measured_existing_normalized_pixels_pending_diagnostic_review',
         'diagnostic':str(q),'diagnostic_sha256':r.sha(q),'two_hand_body_assembly_verified':False,'runtime_verified':False}
q=P/'reviews/component-socket-measurement-candidate-v002.json';assert not q.exists();r.write(q,{'schema':'manual-neutral-weapon-sockets-v1','weapons':rows,
    'coordinate_system':'source_component512_image_Xright_Ydown','marker_geometry_transform_from_native':'all coordinates measured on normalized512 source, not prompt guesses',
    'media_generation_calls_added':0,'new_art_pixels_painted':False});r.archive(q,q.relative_to(P),'actual_pixel_grip_tip_emit_measurements_pending_final_review')
print(json.dumps({family:{k:v for k,v in row.items() if k in ['primary_grip_px','support_grip_px','emit_px','tip_px','sampled_landmark_RGBA']} for family,row in rows.items()}))
