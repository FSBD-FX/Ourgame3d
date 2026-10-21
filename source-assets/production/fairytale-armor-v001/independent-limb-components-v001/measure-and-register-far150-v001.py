"""Far150 only: measure its visible PALE-filled/dark-ring rivet, integer placement."""
from pathlib import Path
import datetime, hashlib, json, math, statistics
from PIL import Image

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run-shoulder-far-idle-v001'
OUT=ROOT/'far150-registration-proposed-v001'
if OUT.exists():raise RuntimeError('Never overwrite registration evidence')
OUT.mkdir();(OUT/'armor-far').mkdir();(OUT/'composite-preview').mkdir()
CANON=Path('F:/Ourgame/source-assets/production/fairytale-hero-v001/sprite-run-idle-v002/curated')
CHEST=Path('F:/Ourgame/source-assets/production/fairytale-armor-v001/independent-idle-components-v001/registration-proposed-v001/armor-front')
NEAR=ROOT/'near149-registration-proposed-v001/armor-near'
DOC=Path('F:/Ourgame/docs/production/first-batch-v2/fairytale-armor-component-contract-v003.md')
targets=[[296,255],[296,253],[296,256],[296,255]]
def meta(p):return {'path':p.as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def lum(p):return .2126*p[0]+.7152*p[1]+.0722*p[2]
def rgba_hash(im):return hashlib.sha256(im.tobytes()).hexdigest()
center=[(0,0),(1,0),(0,1),(-1,0),(0,-1)]
ring=[(2,0),(-2,0),(0,2),(0,-2),(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
outer=[(4,0),(-4,0),(0,4),(0,-4),(3,3),(3,-3),(-3,3),(-3,-3)]
old_sources=[meta(CANON/f'frame-{i}.png') for i in range(4)]+[meta(CHEST/f'frame-{i}.png') for i in range(4)]+[meta(NEAR/f'frame-{i}.png') for i in range(4)]
records=[]
for i,bodyA in enumerate(targets):
    source=RUN/f'curated/frame-{i}.png';im=Image.open(source).convert('RGBA')
    bbox=im.getbbox();x0,y0,x1,y1=bbox;w,h=x1-x0,y1-y0
    roi=[x0+math.floor(w*.1),y0+math.floor(h*.15),x0+math.ceil(w*.4),y0+math.ceil(h*.5)]
    candidates=[]
    for y in range(roi[1],roi[3]):
        for x in range(roi[0],roi[2]):
            if im.getpixel((x,y))[3]<128:continue
            c=statistics.mean(lum(im.getpixel((x+dx,y+dy))) for dx,dy in center)
            r=statistics.mean(lum(im.getpixel((x+dx,y+dy))) for dx,dy in ring)
            o=statistics.mean(lum(im.getpixel((x+dx,y+dy))) for dx,dy in outer)
            candidates.append({'xy':[x,y],'center_luminance':c,'dark_ring_luminance':r,'outer_luminance':o,'score':c-r+.5*(o-r)})
    candidates.sort(key=lambda c:(-c['score'],c['xy'][1],c['xy'][0]))
    if len(candidates)<2 or candidates[0]['score']<70 or candidates[0]['score']-candidates[1]['score']<8:
        raise RuntimeError('Far rivet unresolved; no bbox/hidden-center fallback')
    A=candidates[0]['xy'];delta=[bodyA[0]-A[0],bodyA[1]-A[1]]
    registered=Image.new('RGBA',im.size,(0,0,0,0));registered.paste(im,tuple(delta))
    rb=registered.getbbox()
    exact=im.crop(bbox).tobytes()==registered.crop(rb).tobytes()
    if not exact:raise RuntimeError('Registration clipped or changed crop bytes')
    out=OUT/f'armor-far/frame-{i}.png';registered.save(out)
    body_path=CANON/f'frame-{i}.png';chest_path=CHEST/f'frame-{i}.png';near_path=NEAR/f'frame-{i}.png'
    body=Image.open(body_path).convert('RGBA');chest=Image.open(chest_path).convert('RGBA');near=Image.open(near_path).convert('RGBA')
    # Explicit draw order: body THEN far THEN chest THEN near. Far is not
    # hidden under the opaque whole body and is not drawn over the chest.
    composite=Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(body,registered),chest),near)
    without_far=Image.alpha_composite(Image.alpha_composite(body,chest),near)
    prior_near_preview=Image.open(ROOT/f'near149-registration-proposed-v001/composite-preview/frame-{i}.png').convert('RGBA')
    if without_far.tobytes()!=prior_near_preview.tobytes():raise RuntimeError('Prior near composite changed')
    preview=OUT/f'composite-preview/frame-{i}.png';composite.save(preview)
    a=list(registered.getchannel('A').get_flattened_data());before=list(without_far.get_flattened_data());after=list(composite.get_flattened_data())
    outside=all(alpha!=0 or p==q for alpha,p,q in zip(a,before,after))
    if not outside:raise RuntimeError('Unexpected changes beyond actual far alpha')
    difference=sum(p!=q for p,q in zip(before,after))
    records.append({'frame':i,'duration_ms':167,'source':meta(source),'source_RGBA_sha256':rgba_hash(im),'source_bbox':bbox,
        'actual_A':A,'A_method':'Fixed far bbox ROI x10..40%,y15..50%. Visible pale filled rivet center/dark circular rim; score mean center(cross5)-mean radius2 ring +0.5*(mean radius4 outer-mean radius2 ring). No body target enters search.',
        'why_not_near_detector':'Actual150 has a pale filled/dark outlined rivet. Near dark-core/bright-ring maximum would select an edge, not the center; not reused.',
        'ROI':roi,'top6_candidates':candidates[:6],'minimum_score_admission':70,'minimum_top_margin_admission':8,
        'confidence':'Visible round rivet after retained raw/curated review; approximately +/-1px resampling ambiguity. No hidden attachment inferred.',
        'body_target_A':bodyA,'integer_translation':delta,'registered_A':bodyA,'A_zero_error_by_construction':True,
        'B_hard_attachment':None,'B_error_gate':None,'body_B_is_direction_hint_only':True,
        'registered':meta(out),'registered_bbox':rb,'registered_RGBA_sha256':rgba_hash(registered),'cropped_RGBA_bytes_identical':exact,
        'composite':meta(preview),'composite_order':['unchanged131_body','integer_translated150_far','actual147_chest','actual149_near'],
        'body':meta(body_path),'chest':meta(chest_path),'near':meta(near_path),
        'outside_far_alpha_prior_composite_RGBA_unchanged':outside,'final_RGBA_difference_without_far_pixels':difference,
        'positive_pixel_difference_is_readability_or_zero_collision_proof':False})
if old_sources!=[meta(Path(x['path'])) for x in old_sources]:raise RuntimeError('Existing inputs changed')
receipt={'schema':'native150-far-primary-A-registration-proposed-v1','created_local':datetime.datetime.now().astimezone().isoformat(),
    'status':'proposed_unaccepted_pending_E105_composite_review','contract_v003':meta(DOC),'raw':meta(RUN/'raw/armor_shoulder_far_idle.png'),
    'curated_and_raw_reviewed_after_root_retention':True,'new_registered_and_composite_viewed':False,'wait_for_root_E105_before_view':True,
    'frames':records,'fixed_shared_row_ratio':32/251,'individual_refit_rotation_warp_mirror_repaint':False,
    'semantic_masks_exist':False,'zero_collision_claimed':False,'motion_accepted':False,'runtime_imported':False,
    'old_body_chest_near_inputs_unchanged':True,'old149_B_failure_relabelled':False,'native_ue_ubt_import_called':False,'formal_complete_units':0}
receipt_path=OUT/'registration-receipt-v001.json'
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':meta(receipt_path),'frames':[{'frame':x['frame'],'A':x['actual_A'],'delta':x['integer_translation'],'bbox':x['registered_bbox'],'score':x['top6_candidates'][0]['score'],'far_delta_pixels':x['final_RGBA_difference_without_far_pixels']} for x in records]}))
