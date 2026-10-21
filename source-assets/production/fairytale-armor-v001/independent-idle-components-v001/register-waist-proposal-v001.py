"""Measure existing component contours and propose integer-only registration.

Does not call generation/extraction or edit existing images. New outputs are
pending retention/visual review, and cannot change the original60px row fit.
"""
from pathlib import Path
import hashlib
import json
import math
import datetime
from PIL import Image

ROOT=Path(__file__).resolve().parent
RUN=ROOT/'run-front-idle-v001'
OUT=ROOT/'registration-proposed-v001'
if OUT.exists():raise RuntimeError('Never overwrite a prior registration proposal')
OUT.mkdir()
(OUT/'armor-front').mkdir()
(OUT/'composite-preview').mkdir()

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def fact(path):
    path=Path(path)
    return {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}
def require(ok,why):
    if not ok:raise RuntimeError(why)

contract=json.loads((ROOT/'component-contract-v001.json').read_text(encoding='utf-8'))
frames=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'))
atlas=json.loads((RUN/'manifest.json').read_text(encoding='utf-8'))
row=frames['rows'][0]
require(frames['ok'] and frames['errors']==frames['warnings']==[],'Native QA did not pass')
require(row['frames']==4 and row['method']=='components','Not four actual components')
fit=row['shared_row_fit']
require(fit['scale']==60/271 and not fit['per_frame_scale_normalization'],'Frozen shared60px baseline changed')
require(atlas['animation']['rows']['armor_front_idle']['durations_ms']==[167]*4,'Original timing changed')

records=[]
rgba_hashes=[]
alpha_hashes=[]
for index in range(4):
    path=RUN/f'curated/frame-{index}.png'
    component=Image.open(path).convert('RGBA')
    alpha=component.getchannel('A')
    bbox=component.getbbox()
    require(component.size==(512,512) and bbox==(221,226,291,286),'Unexpected extracted geometry')
    x0,y0,x1,y1=bbox
    # Collar: deepest point of the upper U-shaped neck opening, inside the same
    # central40%-70% X ROI for every frame. First opaque pixel per column, then
    # deepest upper-boundary plateau median. Never a body-target-derived point.
    collar_roi=[x0+math.ceil((x1-x0)*.40),y0,x0+math.floor((x1-x0)*.70)+1,y0+math.ceil((y1-y0)*.40)]
    profile=[]
    for x in range(collar_roi[0],collar_roi[2]):
        y=next((y for y in range(collar_roi[1],collar_roi[3]) if alpha.getpixel((x,y))>=128),None)
        require(y is not None,'Unmeasurable collar column')
        profile.append([x,y])
    deepest=max(y for _,y in profile)
    plateau=[x for x,y in profile if y==deepest]
    collar=[round(sum(plateau)/len(plateau)),deepest]
    # Waist: visible lower rim directly under the component's horizontal center
    # column. This is not the global lowest fringe or an inferred body/feet root.
    waist_x=(x0+x1)//2
    waist_y=next((y for y in range(y1-1,y0-1,-1) if alpha.getpixel((waist_x,y))>=128),None)
    require(waist_y is not None,'Unmeasurable central lower rim')
    waist=[waist_x,waist_y]
    target=contract['body_attachment_targets'][index]
    dx,dy=target['waist'][0]-waist[0],target['waist'][1]-waist[1]
    translated=Image.new('RGBA',component.size,(0,0,0,0))
    # Copy RGBA directly without a mask: no interpolation or alpha re-blending.
    translated.paste(component,(dx,dy))
    tb=translated.getbbox()
    require(tb==(x0+dx,y0+dy,x1+dx,y1+dy),'Nontransparent pixels were clipped')
    require(translated.crop(tb).tobytes()==component.crop(bbox).tobytes(),'RGBA changed during integer registration')
    translated_path=OUT/'armor-front'/f'frame-{index}.png'
    translated.save(translated_path)
    body_path=ROOT/'references'/f'canonical131-idle-{index}.png'
    original_path=Path(contract['canonical_body_run'])/'curated'/f'frame-{index}.png'
    require(body_path.read_bytes()==original_path.read_bytes(),'Canonical body copy changed')
    body=Image.open(body_path).convert('RGBA')
    composite=Image.alpha_composite(body,translated)
    body_pixels=list(body.getdata());armor_pixels=list(translated.getdata());composite_pixels=list(composite.getdata())
    unchanged_outside=all(b==c for b,a,c in zip(body_pixels,armor_pixels,composite_pixels) if a[3]==0)
    require(unchanged_outside,'Composite changed source pixels outside armor coverage')
    composite_path=OUT/'composite-preview'/f'frame-{index}.png'
    composite.save(composite_path)
    registered_collar=[collar[0]+dx,collar[1]+dy]
    residual=[registered_collar[0]-target['collar'][0],registered_collar[1]-target['collar'][1]]
    rgba_hashes.append(hashlib.sha256(component.tobytes()).hexdigest())
    alpha_hashes.append(hashlib.sha256(alpha.tobytes()).hexdigest())
    records.append({'frame':index,'duration_ms':167,'source':fact(path),'source_RGBA_sha256':rgba_hashes[-1],
        'source_alpha_sha256':alpha_hashes[-1],'source_bbox':list(bbox),
        'collar_method':'deepest top-alpha128 U-notch plateau median in fixed relative central ROI',
        'collar_roi':collar_roi,'collar_top_profile':profile,'collar_plateau_x':plateau,'component_collar':collar,
        'waist_method':'bottom alpha128 boundary at the bbox-center X sampling column; not global alpha bottom',
        'waist_roi':[waist_x,y1-18,waist_x+1,y1],'component_waist':waist,
        'landmark_confidence':'contour meaning fixed after retained-raw review; collar +/-1px, waist +/-1-2px, body design points +/-2-3px; alpha/composite visual confirmation pending E094',
        'target_body_collar':target['collar'],'target_body_waist':target['waist'],
        'component_collar_to_waist':[waist[0]-collar[0],waist[1]-collar[1]],
        'target_collar_to_waist':[target['waist'][0]-target['collar'][0],target['waist'][1]-target['collar'][1]],
        'integer_translation':[dx,dy],'registered_collar':registered_collar,
        'registered_waist':target['waist'],'collar_residual_px':residual,
        'within_original3px_landmark_ambiguity':max(map(abs,residual))<=3,
        'registered_armor':fact(translated_path),'registered_bbox':list(tb),
        'cropped_RGBA_unchanged':True,'nontransparent_clipped_pixels':0,
        'canonical_body':fact(body_path),'body_input_byte_identical_to_original':True,
        'composite_preview':fact(composite_path),'unchanged_outside_actual_armor_alpha':unchanged_outside})

require(len(set(rgba_hashes))==4,'Four copies are not four native components')
receipt={'schema':'fairytale-armor147-waist-registration-proposal-v1',
    'created_local':datetime.datetime.now().astimezone().isoformat(),
    'status':'proposed_not_accepted_original_collar_contract_missed',
    'original_contract_unchanged':fact(ROOT/'component-contract-v001.json'),
    'raw':fact(RUN/'raw/armor_front_idle.png'),'frames_manifest':fact(RUN/'frames/frames-manifest.json'),
    'atlas_manifest':fact(RUN/'manifest.json'),'native_extraction_QA_passed':True,
    'source_component_count':4,'unique_component_RGBA_hashes':len(set(rgba_hashes)),
    'unique_component_alpha_hashes':len(set(alpha_hashes)),
    'shared_scale':fit['scale'],'per_frame_scaling':False,'registration_resampling':False,
    'repainted':False,'source_or_curated_images_modified':False,'body_pixels_replaced':False,
    'all_original_collar_constraints_met':all(r['within_original3px_landmark_ambiguity'] for r in records),
    'waist_error_is_zero_by_construction_not_proof_of_two_point_fit':True,
    'visual_reviewed_new_outputs':False,'new_media_retention_pending':'root E094 before any view',
    'native_generation_called_by_this_script':False,'ue_or_import_called':False,
    'back_near_shoulders_bracers_shins_complete':False,'full_armor_complete':False,
    'formal_complete_units':0,'frames':records}
(OUT/'registration-receipt-v001.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':receipt['status'],'scale':fit['scale'],'source_RGBA_unique':len(set(rgba_hashes)),
    'collars':[r['component_collar'] for r in records],'waists':[r['component_waist'] for r in records],
    'translations':[r['integer_translation'] for r in records],
    'collar_residuals':[r['collar_residual_px'] for r in records],
    'original_collar_contract_met':receipt['all_original_collar_constraints_met'],
    'new_outputs_viewed':False},ensure_ascii=False))
