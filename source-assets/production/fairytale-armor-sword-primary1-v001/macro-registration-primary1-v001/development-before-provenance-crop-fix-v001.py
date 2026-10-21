"""Measure retained features and integer-register actual164/165/167; no generation/import/UE."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
R = OUT.parent
SG = Path('C:/Users/22499/.codex/skills/sprite-gen')
sys.path.insert(0, str(SG))
from sprite_gen.frames import extract as native

assert not (OUT / 'textures').exists(), 'Never overwrite a candidate version'
MEASURE = R / 'primary1-measurement-candidate-v001.json'
HIDDEN = R / 'root-hidden-registration-design-v002.json'
BODY_FREEZE = R / 'body-partition-v001/partition-freeze-v001.json'
BODY_PROOF = R / 'body-partition-v001/proof-v001.json'
DURATIONS = [85,85,60,60,155,155]
STACK = ['BodyRest','ShoulderFar','Chest','NearArmWithoutHand','ShoulderNear','HelmetForeground','NearHand']
BODY_OWNERS = ['BodyRest','HelmetForeground','NearArmWithoutHand','NearHand']
SPECS = {
    'Chest': {
        'runtime':'Chest', 'native':164, 'run':'run-chest-primary1-v001', 'extraction':'chest-extraction-v001',
        'A':[[258,262],[268,261],[271,260],[266,262],[259,262],[258,262]],
        'rim':[
            [[252,262],[263,262],[257,256],[257,267]],
            [[263,261],[273,261],[267,255],[268,266]],
            [[267,260],[275,260],[270,255],[271,265]],
            [[261,262],[270,262],[265,257],[265,267]],
            [[254,262],[264,262],[259,256],[259,267]],
            [[252,262],[263,262],[257,256],[257,267]],
        ],
        'feature':'central raised chest boss physical dark outer rim',
        'basis':'Manually selected opposing physical boss rim points from retained exact unscaled crop plus original-source RGBA rows; rounded half-up rim center. Not highlight/strap bolt/whole-component bbox.',
    },
    'NearShoulder': {
        'runtime':'ShoulderNear', 'native':165, 'run':'run-nearshoulder-primary1-v001', 'extraction':'nearshoulder-extraction-v001',
        'A':[[249,263],[257,262],[257,262],[258,263],[248,263],[248,263]],
        'rim':[
            [[245,263],[252,263],[248,259],[249,266]],
            [[253,262],[260,262],[257,258],[257,265]],
            [[254,262],[260,262],[257,259],[257,265]],
            [[254,264],[261,264],[257,260],[258,266]],
            [[245,263],[252,263],[248,259],[248,266]],
            [[245,263],[252,263],[248,259],[248,266]],
        ],
        'feature':'central washer dark hole',
        'basis':'Manually selected visible dark hole inside the washer; opposing washer rim points are supporting landmarks, not whole-cap bbox. Source dark-core RGBA explicitly sampled.',
    },
    'FarShoulder': {
        'runtime':'ShoulderFar', 'native':167, 'run':'run-farshoulder-primary1-v003', 'extraction':'farshoulder-extraction-v003',
        'A':[[252,253],[254,250],[256,253],[254,254],[252,253],[252,253]],
        'rim':[
            [[249,253],[255,253],[252,250],[252,256]],
            [[251,250],[257,250],[254,247],[254,253]],
            [[253,253],[258,253],[255,250],[256,256]],
            [[251,254],[256,254],[253,251],[254,256]],
            [[249,253],[255,253],[252,250],[252,256]],
            [[249,253],[255,253],[252,250],[252,256]],
        ],
        'feature':'NEW topstrap-rivet trial actual visible rivet face',
        'basis':'Manually selected visible top-strap rivet face using retained original512, retained raw167 existence view and actual source RGBA rows. Its small elliptical ink boundary gives +/-2px uncertainty. Not a central-front boss and not the cap bbox center.',
    },
}


def desc(p):
    b = p.read_bytes()
    return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}


def write(name, value):
    p = OUT / name
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return p


def save(name, a):
    p = OUT / name
    assert not p.exists(), p
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a).save(p)
    assert np.array_equal(np.asarray(Image.open(p)),a)
    return p


def shift(a, dx, dy):
    assert isinstance(dx,int) and isinstance(dy,int)
    support = np.any(a != 0,axis=2)
    yy,xx = np.nonzero(support)
    assert len(xx) and np.all((xx+dx >= 0)&(xx+dx < 512)&(yy+dy >= 0)&(yy+dy < 512)), 'Nonzero RGBA would clip'
    b = np.zeros_like(a)
    sx0,sx1 = max(0,-dx),min(512,512-dx)
    sy0,sy1 = max(0,-dy),min(512,512-dy)
    b[sy0+dy:sy1+dy,sx0+dx:sx1+dx] = a[sy0:sy1,sx0:sx1]
    return b


def pre(a):
    return np.concatenate((a[:,:,:3].astype(np.uint32)*a[:,:,3:4],a[:,:,3:4].astype(np.uint32)*255),axis=2)


def composite(layers):
    im = Image.new('RGBA',(512,512),(0,0,0,0))
    for name in STACK:
        if name in layers:
            im = Image.alpha_composite(im,Image.fromarray(layers[name]))
    return np.asarray(im).copy()


assert desc(HIDDEN)['sha256']=='829ce71b5ded2e9ce37893178f09b119f7f4b4940a9f73de347848aa1d51631d'
# The specific hidden-target contract is pinned by values below, not substituted with a measured point.
measure = json.loads(MEASURE.read_text(encoding='utf-8-sig'))
hidden = json.loads(HIDDEN.read_text(encoding='utf-8'))
trial = {(x['component'],x['phase']):x for x in hidden['trial_targets']}
assert set(trial)=={('Chest',2),('Chest',3),('FarShoulder',2)}
assert trial[('Chest',2)]['trial_body_A']==[268,270]
assert trial[('Chest',3)]['trial_body_A']==[269,276]
assert trial[('FarShoulder',2)]['trial_body_A']==[308,268]
body_proof = json.loads(BODY_PROOF.read_text(encoding='utf-8'))
crop_map = json.loads((R/'review-crops-v001/crop-source-map-v001.json').read_text(encoding='utf-8'))
crops = {(x['component'],x['phase']):x for x in crop_map['crops']}
texture_rows = []
values = [dict() for _ in range(6)]
feature_rows = []
protected = []
for mp in [R/'preparation-freeze-v001.json',BODY_FREEZE,
           R/'chest-extraction-v001/extracted-freeze-v001.json',
           R/'nearshoulder-extraction-v001/extracted-freeze-v001.json',
           R/'farshoulder-extraction-v003/extracted-freeze-v001.json']:
    data = json.loads(mp.read_text(encoding='utf-8'))
    protected.extend({k:f[k] for k in ['path','bytes','sha256']} for f in data['files'])
    protected.append(desc(mp))
for f in protected:
    assert desc(Path(f['path']))==f

for component,s in SPECS.items():
    run = R/s['run']
    ep = R/s['extraction']/'extraction-receipt-v001.json'
    e = json.loads(ep.read_text(encoding='utf-8'))
    assert e['QA_errors']==e['QA_warnings']==[] and e['shared_row_fit']['per_frame_scale_normalization'] is False
    raw = Path(e['raw']['path'])
    keyed = native.remove_chroma_background(Image.open(raw),(0,255,0),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
    parts = native.extract_component_images(keyed,6)
    assert len(parts)==6
    for i in range(6):
        source = run/f'curated/frame-{i}.png'
        assert desc(source)==e['frames'][i]['source']
        with Image.open(source) as im:
            assert im.mode=='RGBA' and im.size==(512,512)
            a = np.asarray(im).copy()
        A = s['A'][i]
        assert int(a[A[1],A[0],3])==255
        visible = measure['frames'][i]['body_design_A_candidates'][component]
        if visible['point'] is None:
            t = trial[(component,i)]
            target,uncertainty = t['trial_body_A'],t['source_px_uncertainty']
            target_kind,target_source = t['kind'],desc(HIDDEN)
        else:
            assert (component,i) not in trial
            target,uncertainty = visible['point'],visible['uncertainty_source_px']
            target_kind,target_source = visible['kind'],desc(MEASURE)
        dx,dy = int(target[0]-A[0]),int(target[1]-A[1])
        b = shift(a,dx,dy)
        back = shift(b,-dx,-dy)
        assert np.array_equal(a,back)
        assert np.array_equal(b[target[1],target[0]],a[A[1],A[0]])
        assert np.count_nonzero(a[:,:,3])==np.count_nonzero(b[:,:,3])
        dest = save(f'textures/{s["runtime"]}/frame-{i}.png',b)
        values[i][s['runtime']] = b
        texture_rows.append({'component':s['runtime'],'frame':i,'source':desc(dest)})
        fr = e['shared_row_fit']['frame_records'][i]
        assert hashlib.sha256(parts[i].tobytes()).hexdigest()==e['shared_row_fit']['raw_component_RGBA_sha256'][i]
        assert list(parts[i].size)==fr['source_component_size']
        local = [A[k]-fr['placement_xy'][k] for k in range(2)]
        mapped = [(local[k]+.5)*fr['source_component_size'][k]/fr['resampled_size'][k]-.5 for k in range(2)]
        crop = crops.get((component,i))
        if crop:
            with Image.open(crop['crop']['path']) as ci, Image.open(source) as si:
                assert ci.tobytes()==si.crop(crop['source_crop_rect']).tobytes()
            crop_observation = {'retained_crop':crop['crop'],'source_rect':crop['source_crop_rect'],
                                'feature_local_crop_A':[A[0]-crop['source_crop_rect'][0],A[1]-crop['source_crop_rect'][1]],
                                'exact_source_pixels_confirmed':True,'viewed_unscaled':True}
        else:
            crop_observation = {'retained_original512_viewed':True,'new_zoom_or_crop_viewed':False}
        feature_rows.append({'component':component,'runtime_component':s['runtime'],'frame':i,'native_request':s['native'],
            'source':desc(source),'feature_kind':s['feature'],'actual_component_A':A,
            'feature_uncertainty_source_px':2,'source_RGBA_at_A':a[A[1],A[0]].tolist(),
            'manual_feature_basis':s['basis'],'supporting_feature_rim_landmarks':[
                {'point':xy,'source_RGBA':a[xy[1],xy[0]].tolist()} for xy in s['rim'][i]],
            'whole_component_bbox_used_as_A':False,'crop_or_original_view':crop_observation,
            'source_alpha_bbox_diagnostic_only':e['frames'][i]['alpha_bbox_px'],
            'measured_visible_body_A':visible['point'],'target_body_trial_A':target,
            'target_body_kind':target_kind,'target_uncertainty_source_px':uncertainty,'target_source':target_source,
            'hidden_measurement_filled':False,'hidden_B':None,'integer_translation_xy':[dx,dy],
            'registered_source':desc(dest),'feature_maps_to_target_exact':True,'source_RGBA_reverse_translation_exact':True,
            'clipped_nonzero_RGBA_pixels':0,'rescale_rotate_warp_repaint':False,
            'raw_component_provenance':{'extraction_receipt':desc(ep),'common_row_scale':e['shared_row_ratio'],
                'frame_record':fr,'raw_component_RGBA_sha256':hashlib.sha256(parts[i].tobytes()).hexdigest(),
                'manual_A_inverse_pixel_center_in_raw_component':mapped,
                'inverse_mapping_is_independent_feature_measurement':False},
            'fit_identity_or_motion_accepted':False})

for i,f in enumerate(body_proof['frames']):
    for owner in BODY_OWNERS:
        original = next(x['file'] for x in f['layers'] if x['owner']==owner)
        source = Path(original['path'])
        assert desc(source)==original
        dest = OUT/f'textures/{owner}/frame-{i}.png'
        assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        assert dest.read_bytes()==source.read_bytes()
        with Image.open(dest) as im:
            assert im.mode=='RGBA' and im.size==(512,512)
            values[i][owner] = np.asarray(im).copy()
        texture_rows.append({'component':owner,'frame':i,'source':desc(dest)})

assert len(texture_rows)==42 and len({(x['component'],x['frame']) for x in texture_rows})==42
texture_rows.sort(key=lambda x:(STACK.index(x['component']),x['frame']))
assemblies = []
for i,layers in enumerate(values):
    assert set(layers)==set(STACK)
    # All four original body owners retain exactly the original159 values before armor insertion.
    original_body = np.asarray(Image.open(measure['frames'][i]['source']['path']))
    body = np.sum(np.stack([layers[n] for n in BODY_OWNERS]),axis=0,dtype=np.uint16).astype(np.uint8)
    assert np.array_equal(body,original_body)
    assembled = composite(layers)
    assembly = save(f'assemblies/frame-{i}-macro-no-sword.png',assembled)
    intersections = []
    diagnostic = np.zeros((512,512,4),dtype=np.uint8)
    armor_names = ['ShoulderFar','Chest','ShoulderNear']
    armor_union = np.any(np.stack([layers[n][:,:,3]>0 for n in armor_names]),axis=0)
    for owner,color in [('BodyRest',[70,155,230]),('NearArmWithoutHand',[215,70,185]),('HelmetForeground',[235,65,65]),('NearHand',[240,190,40])]:
        hit = armor_union & (layers[owner][:,:,3]>0)
        diagnostic[hit,:3] = color
        diagnostic[hit,3] = 255
    overlap_file = save(f'diagnostics/frame-{i}-armor-vs-body-overlap.png',diagnostic)
    for name in armor_names:
        a = layers[name]; support = a[:,:,3]>0
        later = STACK[STACK.index(name)+1:]
        without = composite({k:v for k,v in layers.items() if k!=name})
        intersections.append({'component':name,'source_visible_alpha_pixels':int(support.sum()),
            'raw_alpha_intersection_by_body_owner':{n:int(np.count_nonzero(support & (layers[n][:,:,3]>0))) for n in BODY_OWNERS},
            'raw_alpha_intersection_with_other_armor':{n:int(np.count_nonzero(support & (layers[n][:,:,3]>0))) for n in armor_names if n!=name},
            'pixels_with_any_later_layer_alpha':int(np.count_nonzero(support & np.any(np.stack([layers[n][:,:,3]>0 for n in later]),axis=0))),
            'static_composite_omit_one_premultiplied_difference_pixels':int(np.count_nonzero(np.any(pre(assembled)!=pre(without),axis=2))),
            'counts_are_not_semantic_fit_or_screen_readability':True})
    assemblies.append({'frame':i,'source':desc(assembly),'stack':STACK,'body_RGBA_sum_before_armor_exact':True,
        'armor_body_overlap_diagnostic':desc(overlap_file),'component_numeric_contribution':intersections,
        'weapon_included':False,'grip_or_weapon_occlusion_validated':False,'new_assembly_or_diagnostic_explicitly_viewed':False})

measurement_file = write('feature-measurement-registration-v001.json',{
    'schema':'native159-primary1-three-armor-six-feature-registration-candidate-v1',
    'created_local':datetime.datetime.now().astimezone().isoformat(),'author':'scale_tests',
    'source_retention':'164/165E178;167v003E179;159body partitionE175',
    'identity':'131 sole hero identity; armor164Chest/165Near/167Far, not166 rejected variant',
    'body_visible_measurement':desc(MEASURE),'hidden_target_trial_design':desc(HIDDEN),
    'body_partition_proof':desc(BODY_PROOF),'body_partition_freeze':desc(BODY_FREEZE),
    'feature_rows':feature_rows,'assemblies':assemblies,
    'body_source_copies':[{**row,'original':next(x['file'] for x in body_proof['frames'][row['frame']]['layers'] if x['owner']==row['component'])}
                          for row in texture_rows if row['component'] in BODY_OWNERS],
    'source_canvas':[512,512],'native_facing':1,'fixed_display_canvas':72*512/416,
    'max_visible_hero_source_height':416,'max_visible_hero_screen_height':72,
    'durations_ms':DURATIONS,'standard_GIF_actual_ms':[100]*6,'kernel_phase_required':True,
    'all_mirroring_future_runtime_once_whole_quad':True,'per_frame_fit_or_pose_normalization':False,
    'static_stack_without_weapon':STACK,'future_independent_sword_after':'HelmetForeground','future_independent_sword_before':'NearHand',
    'new_outputs_explicitly_viewed':False,'all_source_pixel_values_preserved':True,
    'hidden_measurement_or_B_fabricated':False,'source_geometry_or_old_masks_modified':False,
    'fit_or_motion_or_equipment_accepted':False,'native_import_UE_called':False,'formal_complete_units':0})
candidate = write('candidate-import-v001.json',{
    'schema':'native159-primary1-macro42-texture-delivery-candidate-v1',
    'created_local':datetime.datetime.now().astimezone().isoformat(),'textures':texture_rows,
    'texture_count':42,'frame_count':6,'durations_ms':DURATIONS,'source_canvas':[512,512],
    'native_facing':1,'display_canvas':72*512/416,'hero_visible_height_limit':72,
    'static_stack_without_sword':STACK,'runtime_sword_between':['HelmetForeground','NearHand'],
    'measurement':desc(measurement_file),'new_outputs_explicitly_viewed':False,
    'runtime_names_or_object_paths_assigned':False,'import_permitted':False,
    'visual_fit_or_motion_accepted':False,'formal_complete_units':0})
for f in protected:
    assert desc(Path(f['path']))==f
checks = write('numeric-checks-v001.json',{
    'schema':'native159-primary1-macro42-numeric-proof-v1','texture_count':42,'registered_armor_count':18,'body_exact_copy_count':24,
    'assemblies_count':6,'overlap_diagnostics_count':6,'all_textures_512_RGBA':True,
    'all_18_A_integer_target_maps_exact':True,'all_18_reverse_RGBA_translations_exact':True,
    'clipped_nonzero_RGBA_pixels':0,'all_24_body_file_copies_byte_exact':True,
    'all_6_original_body_owner_sums_byte_exact':True,'raw_component_provenance_hash_matches':18,
    'old_frozen_source_checks':len(protected),'old_frozen_source_mismatches':0,
    'new_outputs_explicitly_viewed':False,'numeric_proof_is_not_semantic_or_art_acceptance':True})
print(json.dumps({'candidate':desc(candidate),'measurement':desc(measurement_file),'checks':desc(checks),
                  'textures':42,'registered_armor':18,'new_outputs_explicitly_viewed':False},ensure_ascii=False))
