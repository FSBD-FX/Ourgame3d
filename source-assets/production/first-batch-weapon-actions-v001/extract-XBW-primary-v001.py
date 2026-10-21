"""Manual original-pixel hand selections; rigid real weapon, no body transforms."""
from pathlib import Path
import importlib.util,math,json
from PIL import Image,ImageDraw,ImageChops
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('record',P/'production-record.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
wc=P.parent/'first-batch-weapon-components-v001/manifests/import-weapon-components-v001.json';w=r.read(wc)['weapons']['WPN-XBW-001'];weapon=Image.open(w['path']).convert('RGBA')
out=P/'components/XBW-primary-v001';assert not out.exists();out.mkdir(parents=True)
near=[[(199,299),(214,294),(225,294),(238,299),(243,307),(242,325),(231,334),(216,336),(205,330),(199,321)],
[(218,245),(230,239),(248,235),(261,237),(270,244),(273,252),(268,261),(268,271),(256,279),(239,280),(228,274),(218,264)],
[(221,254),(234,245),(253,240),(266,245),(272,252),(272,268),(265,282),(250,285),(234,280),(223,273)],
[(222,251),(233,242),(248,240),(263,245),(270,253),(270,269),(263,281),(245,284),(232,279),(222,270)],
[(213,284),(228,277),(242,274),(255,278),(262,285),(261,302),(255,311),(242,317),(228,317),(215,309)],
[(199,299),(214,294),(225,294),(238,299),(243,307),(242,325),(231,334),(216,336),(205,330),(199,321)]]
support=[[(302,306),(315,303),(326,302),(337,307),(342,316),(340,331),(329,339),(315,336),(305,330),(300,319)],
[(323,252),(338,243),(350,240),(363,243),(370,251),(368,268),(361,279),(349,283),(338,278),(325,275)],
[(322,252),(335,242),(349,240),(363,244),(370,254),(368,270),(359,279),(347,281),(335,275),(323,273)],
[(324,253),(337,242),(349,240),(363,243),(370,251),(368,268),(362,280),(348,284),(336,277),(325,275)],
[(312,286),(324,280),(337,279),(348,284),(354,293),(353,308),(345,318),(331,321),(319,315),(310,304)],
[(302,306),(315,303),(326,302),(337,307),(342,316),(340,331),(329,339),(315,336),(305,330),(300,319)]]
grips=[[224,316],[250,260],[255,267],[250,267],[240,300],[224,316]]
supports=[[325,321],[352,262],[356,264],[352,261],[341,302],[325,321]]
times=[0,.08,.16,.18,.20,.44,.68];scale=.48
def mask(poly):
    im=Image.new('L',(512,512),0);ImageDraw.Draw(im).polygon(poly,fill=255);return im
def select(source,m):
    q=source.copy();q.putalpha(ImageChops.multiply(q.getchannel('A'),m));q.putdata([px if px[3] else(0,0,0,0) for px in q.get_flattened_data()]);return q
def save(im,path,status):
    im.save(path);copies=r.archive(path,path.relative_to(P),status);assert all(r.sha(Path(x))==r.sha(path) for x in copies)
    return {'path':str(path),'sha256':r.sha(path),'canvas_px':list(im.size),'mode':im.mode,'alpha_extrema':list(im.getchannel('A').getextrema()),'bbox_px':list(im.getchannel('A').getbbox()),'four_archive_copies_verified':True}
sheets={key:Image.new('RGBA',(1536,1024),(0,0,0,0)) for key in ['body_far','body_support','body_near','assembled_right','assembled_left','hand_coordinates']};rows=[]
for i in range(6):
    src=P/f'processed/call82-fixed-canvas-v001/frame-{i}.png';source=Image.open(src).convert('RGBA');nm=mask(near[i]);sm=mask(support[i]);assert not ImageChops.multiply(nm,sm).getbbox()
    parts={'body_far':select(source,ImageChops.invert(ImageChops.lighter(nm,sm))),'body_support':select(source,sm),'body_near':select(source,nm)}
    rebuilt=parts['body_far'].copy();rebuilt.alpha_composite(parts['body_support']);rebuilt.alpha_composite(parts['body_near']);assert source.tobytes()==rebuilt.tobytes()
    g=grips[i];h=supports[i];assert source.getpixel(tuple(g))[3]==source.getpixel(tuple(h))[3]==255
    base=[w['support_grip_px'][j]-w['primary_grip_px'][j] for j in range(2)];v=[h[j]-g[j] for j in range(2)]
    angle=math.atan2(v[1],v[0])-math.atan2(base[1],base[0]);co=math.cos(angle);si=math.sin(angle)
    # Forward component->body affine; only the independent prop is transformed.
    tx=g[0]-scale*(co*w['primary_grip_px'][0]-si*w['primary_grip_px'][1]);ty=g[1]-scale*(si*w['primary_grip_px'][0]+co*w['primary_grip_px'][1])
    matrix=[scale*co,-scale*si,tx,scale*si,scale*co,ty]
    def point(p):return[matrix[0]*p[0]+matrix[1]*p[1]+matrix[2],matrix[3]*p[0]+matrix[4]*p[1]+matrix[5]]
    actual=point(w['support_grip_px']);emit=point(w['emit_px']);err=math.dist(actual,h);assert err<1.0
    render=weapon.transform((512,512),Image.Transform.AFFINE,(co/scale,si/scale,w['primary_grip_px'][0]-(co*g[0]+si*g[1])/scale,-si/scale,co/scale,w['primary_grip_px'][1]-(-si*g[0]+co*g[1])/scale),resample=Image.Resampling.BICUBIC)
    assembled=parts['body_far'].copy();assembled.alpha_composite(render);assembled.alpha_composite(parts['body_support']);assembled.alpha_composite(parts['body_near'])
    mirrored=assembled.transform((512,512),Image.Transform.AFFINE,(-1,0,512,0,1,0),resample=Image.Resampling.NEAREST)
    measured=assembled.copy();d=ImageDraw.Draw(measured)
    for p,c in [(g,'red'),(h,'lime'),(emit,'cyan')]:d.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),outline=c,width=1)
    d.text((20,25),f'frame{i} {times[i]:.2f}..{times[i+1]:.2f} support error {err:.3f}px',fill='white')
    infos={key:save(im,out/f'{key}-{i}.png','native_XBW_primary_original_body_and_distal_hand_selection_candidate') for key,im in parts.items()}
    for key,m in [('near',nm),('support',sm)]:
        q=P/f'masks/XBW-primary-{key}-{i}-v001.png';q.parent.mkdir(exist_ok=True);m.save(q);r.archive(q,q.relative_to(P),'manual_source_hand_polygon_mask_not_new_hand_art')
    for key,im in {**parts,'assembled_right':assembled,'assembled_left':mirrored,'hand_coordinates':measured}.items():sheets[key].alpha_composite(im,((i%3)*512,(i//3)*512))
    rows.append({'index':i,'source_body_path':str(src),'source_body_sha256':r.sha(src),'parts':infos,'ground_root_px':[256,472],
      'root_kind':'inherited_profile; boots_bottom483; no_new_footlock_certificate','grip_px':g,'primary_grip_px':g,'support_grip_px':h,
      'sampled_grip_RGBA':list(source.getpixel(tuple(g))),'sampled_support_RGBA':list(source.getpixel(tuple(h))),
      'manual_measurement_scope':'actual_grasp_contact_points_inside_native_fists; placement_fit_checked_not_prompt_coordinates',
      'near_hand_polygon_px':near[i],'support_hand_polygon_px':support[i],'weapon_scale':scale,'weapon_angle_image_clockwise_deg':math.degrees(angle),
      'component_primary_grip_px':w['primary_grip_px'],'component_support_grip_px':w['support_grip_px'],'component_emit_px':w['emit_px'],
      'component_to_body_affine_2x3':matrix,'transformed_support_px':actual,'support_alignment_error_px':err,'transformed_emit_body_px':emit,
      'emit_delta_from_ground_root_body_px':[emit[0]-256,emit[1]-472],'phase':['windup','windup','active','active','recovery','recovery'][i],
      'time_start_s':times[i],'time_end_s':times[i+1],'body_three_track_exact_source_reconstruction':True,'weapon_visible':True,
      'damage_or_projectile_emission_events':[{'nominal_source_time_s':.16,'event':'single_primary_bolt','authority':'actor_kernel_only_not_image_or_HUD'}] if i==2 else []})
for key,im in sheets.items():save(im,P/f'reviews/XBW-primary-{key}-v001.png','static_body_weapon_contact_and_phase_candidate_pending_engine_review')
q=P/'reviews/XBW-primary-layer-candidate-v001.json';assert not q.exists();r.write(q,{'schema':'weapon_body_three_track_candidate_v1','request_number':82,'frames':rows,
 'weapon_contract':str(wc),'weapon_contract_sha256':r.sha(wc),'weapon':w,'draw_order':['body_far','independent_XBW_weapon','body_support','body_near'],
 'body_geometry_transform':'none','weapon_uniform_scale_all_frames':scale,'source_timing':{'windup_s':.16,'active_s':.04,'recovery_s':.48,'duration_s':.68,'nominal_emit_s':.16},
 'string_release_component_animation_complete':False,'runtime_verified':False,'full_action_accepted':False,
 'limitations':['Actual native arms and shoulder recoil form a primary-shot body candidate. Static prop does not provide string-release/bolt mechanical states.',
 'Primary/support points are manual source-image grasp contacts, not skeleton joints; all share one rigid affine with emit. Runtime origin/mirror/depth must still be proven.',
 'Only common underclothes; no four-armor surface compatibility is certified for these new poses.',
 'Source timing is nominal unmodified equipment-v1. Accepted actor start/effective clock remains authoritative and must remap phase fractions when appropriate.']});r.archive(q,q.relative_to(P),'actual_primary_hand_points_affine_and_phase_source_candidate')
print(json.dumps({'candidate':str(q),'sha256':r.sha(q),'new_body_PNGs':18,'support_errors':[x['support_alignment_error_px'] for x in rows],'emit_at_release_body_px':rows[2]['transformed_emit_body_px']}))
