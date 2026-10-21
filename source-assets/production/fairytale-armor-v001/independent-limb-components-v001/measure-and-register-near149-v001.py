"""Read fixed features and propose INTEGER translation. Never view/fit/repaint images."""
from pathlib import Path
import datetime, hashlib, json, math, statistics
from PIL import Image

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run-shoulder-near-idle-v001'
OUT=ROOT/'near149-registration-proposed-v001'
if OUT.exists():raise RuntimeError('Never overwrite a registration proposal')
OUT.mkdir()
(OUT/'armor-near').mkdir();(OUT/'composite-preview').mkdir()
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated')
CHEST=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front')
contract=json.loads((ROOT/'shoulder-component-contract-v002.json').read_text(encoding='utf-8'))
targets=[x for x in contract['body_targets'] if x['side']=='near']

def meta(p):return {'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def luminance(pixel):return .2126*pixel[0]+.7152*pixel[1]+.0722*pixel[2]
def rgba_hash(im):return hashlib.sha256(im.tobytes()).hexdigest()
ring=[(2,0),(-2,0),(0,2),(0,-2),(1,1),(1,-1),(-1,1),(-1,-1)]
outer=[(4,0),(-4,0),(0,4),(0,-4),(3,3),(3,-3),(-3,3),(-3,-3)]
records=[]
for i,target in enumerate(targets):
    source=RUN/f'curated/frame-{i}.png';im=Image.open(source).convert('RGBA')
    bbox=im.getbbox();x0,y0,x1,y1=bbox;w,h=x1-x0,y1-y0
    roi=[x0+math.floor(w*.15),y0+math.floor(h*.35),x0+math.ceil(w*.45),y0+math.ceil(h*.68)]
    candidates=[]
    for y in range(roi[1],roi[3]):
        for x in range(roi[0],roi[2]):
            if im.getpixel((x,y))[3]<128:continue
            core=luminance(im.getpixel((x,y)))
            if core>100:continue
            ring_lum=statistics.mean(luminance(im.getpixel((x+dx,y+dy))) for dx,dy in ring)
            outer_lum=statistics.mean(luminance(im.getpixel((x+dx,y+dy))) for dx,dy in outer)
            score=(ring_lum-core)+.5*(ring_lum-outer_lum)
            candidates.append({'xy':[x,y],'core_luminance':core,'annulus_luminance':ring_lum,'outer_luminance':outer_lum,'score':score})
    candidates.sort(key=lambda c:(-c['score'],c['xy'][1],c['xy'][0]))
    if not candidates or candidates[0]['score']<80:raise RuntimeError('No clear connected rivet center; no inferred fallback')
    A=candidates[0]['xy']
    # B corresponds to the technical guide's unique lowest flared-lip turn.
    # Never replace it with a left-edge point because that would fit better.
    bottom=[]
    for x in range(x0,x1):
        ys=[y for y in range(y0,y1) if im.getpixel((x,y))[3]>=128]
        if ys:bottom.append([x,max(ys)])
    deepest=max(p[1] for p in bottom)
    plateau=[p[0] for p in bottom if p[1]==deepest]
    B=[round(statistics.median(plateau)),deepest]
    if B[1]<y0+h*.8:raise RuntimeError('Measured contour is not the actual lower lip')
    # The long helmet-like lower rim also has an arc midpoint. Record it as
    # semantic ambiguity only, never substitute it for the guide's lowest turn.
    left_arc=[p for p in bottom if p[0]<=B[0]]
    lengths=[0.]
    for p,q in zip(left_arc,left_arc[1:]):lengths.append(lengths[-1]+math.hypot(p[0]-q[0],p[1]-q[1]))
    half_index=min(range(len(lengths)),key=lambda k:abs(lengths[k]-lengths[-1]/2))
    arc_mid=left_arc[half_index]
    bodyA=target['mount_px'];bodyB=target['lip_support_px'];delta=[bodyA[0]-A[0],bodyA[1]-A[1]]
    registered=Image.new('RGBA',im.size,(0,0,0,0));registered.paste(im,tuple(delta))
    regbbox=registered.getbbox()
    exact_crop=registered.crop(regbbox).tobytes()==im.crop(bbox).tobytes()
    if not exact_crop:raise RuntimeError('Integer registration clipped or changed nontransparent RGBA')
    out=OUT/f'armor-near/frame-{i}.png';registered.save(out)
    actualB=[B[0]+delta[0],B[1]+delta[1]]
    residual=[actualB[0]-bodyB[0],actualB[1]-bodyB[1]]
    body_path=CANON/f'frame-{i}.png';chest_path=CHEST/f'frame-{i}.png'
    body=Image.open(body_path).convert('RGBA');chest=Image.open(chest_path).convert('RGBA')
    prior=Image.alpha_composite(body,chest)
    composite=Image.alpha_composite(prior,registered)
    preview=OUT/f'composite-preview/frame-{i}.png';composite.save(preview)
    rp=list(registered.getchannel('A').get_flattened_data());pp=list(prior.get_flattened_data());cp=list(composite.get_flattened_data())
    outside_unchanged=all(a!=0 or old==new for a,old,new in zip(rp,pp,cp))
    if not outside_unchanged:raise RuntimeError('Composite changed pixels outside actual shoulder alpha')
    records.append({'frame':i,'duration_ms':167,'source':meta(source),'source_RGBA_sha256':rgba_hash(im),'source_bbox':bbox,
        'rivet_A_method':'Fixed bbox-relative x15..45%,y35..68% ROI. Dark rivet core, pale ring radius2, dark outer radius4; maximize ring-core +0.5*(ring-outer). Not selected using body fit.',
        'rivet_roi':roi,'A':A,'rivet_top_candidates':candidates[:5],
        'B_method':'Median X of actual alpha>=128 deepest lower-flared-rim turn/plateau, corresponding to original green guide lowest lip point. Not whole-body bbox or arbitrary left edge.',
        'B':B,'deepest_plateau_xs':plateau,'bottom_alpha128_profile':bottom,
        'rim_long_arc_midpoint_descriptive_only':arc_mid,'A_to_B':[B[0]-A[0],B[1]-A[1]],
        'A_to_arc_midpoint_descriptive_only':[arc_mid[0]-A[0],arc_mid[1]-A[1]],
        'A_confidence':'Dark core/pale ring center has about1px resampling uncertainty; no visual review of derived alpha yet.',
        'B_confidence':'Deepest lip plateau about1-2px contour ambiguity. Helmet-like long rim creates alternative arc-center semantics; do not swap definition to pass.',
        'body_target_A':bodyA,'body_target_B':bodyB,'body_A_to_B':[bodyB[0]-bodyA[0],bodyB[1]-bodyA[1]],
        'integer_translation':delta,'registered_A':bodyA,'registered_B':actualB,'B_residual':residual,
        'B_residual_within_original_design_3px':max(abs(x) for x in residual)<=3,
        'registered':meta(out),'registered_RGBA_sha256':rgba_hash(registered),'crop_RGBA_bytes_unchanged':exact_crop,
        'composite':meta(preview),'composite_order':['unchanged131_body','actual147_registered_chest','integer_translated149_near_cap'],
        'body_source':meta(body_path),'chest_source':meta(chest_path),'outside_shoulder_alpha_prior_RGBA_unchanged':outside_unchanged})
receipt={'schema':'native149-near-shoulder-registration-proposed-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
    'status':'unaccepted_proposal_pending_retained_visual_review','raw':meta(RUN/'raw/armor_shoulder_near_idle.png'),
    'contract':meta(ROOT/'shoulder-component-contract-v002.json'),'frames_manifest':meta(RUN/'frames/frames-manifest.json'),
    'frames':records,'four_source_RGBA_unique':len({x['source_RGBA_sha256'] for x in records})==4,
    'all_B_residuals_within_original_design_3px':all(x['B_residual_within_original_design_3px'] for x in records),
    'registered_A_exact_by_construction_not_two_point_fit_proof':True,'individual_refit_rotation_warp_repaint':False,
    'actual_derived_alpha_composite_GIF_viewed':False,'root_retention_required_before_view':True,
    'native_ue_import_called':False,'far_caps_generated':False,'formal_complete_units':0}
(OUT/'registration-receipt-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':meta(OUT/'registration-receipt-v001.json'),'frames':[{'frame':x['frame'],'A':x['A'],'B':x['B'],'arc_mid':x['rim_long_arc_midpoint_descriptive_only'],'actual_AB':x['A_to_B'],'body_AB':x['body_A_to_B'],'delta':x['integer_translation'],'B_residual':x['B_residual'],'rivet_score':x['rivet_top_candidates'][0]['score']} for x in records],'all_B_design_pass':receipt['all_B_residuals_within_original_design_3px']}))
