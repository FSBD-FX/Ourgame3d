"""Read-only exact source-coordinate proof and artist standing-root propagation candidate."""
from pathlib import Path
import sys,hashlib,json
import numpy as np
from PIL import Image
ROOT=Path('F:/Ourgame/source-assets/production/fairytale-guard-v001/art-preparation-v001');OUT=ROOT/'death214-standing-root-propagation-v002'
SG=Path('C:/Users/22499/.codex/skills/sprite-gen');sys.path.insert(0,str(SG))
from sprite_gen.frames import extract as native
assert hashlib.sha256((SG/'sprite_gen/frames/extract.py').read_bytes()).hexdigest()=='f2a7902f01069668340d14217bd05c777f5c01853284102e211aba1013a45539'
RUN=ROOT/'stunned213-death214-extraction-v001/run-death6-shared-HD-v001'
RAW=ROOT/'stunned4-death6-generation-ready-v001/run-guard-death6-v001/raw/right/death.png'
OLD=ROOT/'accepted213-214-body-registration-and-death-spec-v002'
fm=json.loads((RUN/'frames/frames-manifest.json').read_text(encoding='utf-8'))
row=next(r for r in fm['rows'] if r['state']=='right_death');fit=row['shared_row_fit'];assert fit['scale']==1.
contact=json.loads((OLD/'death214-body-standing-equivalent-floor-registration-v001.json').read_text(encoding='utf-8'))
prior=json.loads((OLD/'death214-occluded-feet-native-ground-reference-addendum-v001.json').read_text(encoding='utf-8'))
def pin(p):
 b=p.read_bytes();return {'path':p.as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
rawpin=pin(RAW);assert rawpin['sha256']=='d351c3a83396bfafefdbf7ae7ea26fc033b06b459082e437b36d2a3458411d73'
keyed=native.remove_chroma_background(Image.open(RAW),(255,0,255),96.,180.,18.,unmix_reach=4,spill_max_fraction=.005)
records=[];original=native.component_group_image
def observer(source,components,padding=4):
 im=original(source,components,padding)
 origin=[max(0,min(c['bbox'][0] for c in components)-padding),max(0,min(c['bbox'][1] for c in components)-padding)]
 records.append({'group_crop_origin_raw_xy':origin,'group_size':list(im.size),'group_alpha_tight_bbox_xyxy':list(im.getbbox()),'group_RGBA_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
 return im
try:
 native.component_group_image=observer
 images=native.extract_component_images(keyed,6)
finally:native.component_group_image=original
assert images is not None and len(images)==len(records)==6
for i,(im,rec) in enumerate(zip(images,records)):
 assert rec['group_RGBA_sha256']==fit['raw_component_RGBA_sha256'][i]
 bbox=im.getbbox();crop=im.crop(bbox);expected=fit['frame_records'][i]
 assert list(crop.size)==expected['source_component_size']
 curated=Image.open(RUN/f'curated/frame-{i}.png').convert('RGBA');assert np.array_equal(np.array(crop),np.array(curated.crop(curated.getbbox())))
 rec['tight_origin_raw_xy']=[rec['group_crop_origin_raw_xy'][0]+bbox[0],rec['group_crop_origin_raw_xy'][1]+bbox[1]]
 rec['curated_placement_xy']=expected['placement_xy'];rec['pixel_exact_curated_crop_equals_raw_component_tight_crop']=True
anchor=[224.,463.];o0=records[0]['tight_origin_raw_xy'];p0=records[0]['curated_placement_xy']
rawroot0=[o0[0]+anchor[0]-p0[0],o0[1]+anchor[1]-p0[1]]
assert rawroot0==[145.,550.]
pitch=Image.open(RAW).width/6;assert pitch==362.
s=100.8/365
rows=[]
for i,rec in enumerate(records):
 native_root=[rawroot0[0]+pitch*i,rawroot0[1]]
 o=rec['tight_origin_raw_xy'];p=rec['curated_placement_xy'];pivot=[native_root[0]-o[0]+p[0],native_root[1]-o[1]+p[1]]
 assert pivot==prior['rows'][i]['pivot_exact_before_round_xy']
 actual=contact['rows'][i]['artist_body_groundpivot_perframe_proposal_xy'];bbox=fit['frame_records'][i]['alpha_bbox_px']
 rows.append({'frame':i,'curated_source':pin(RUN/f'curated/frame-{i}.png'),'exact_source_component_mapping':rec,'artist_native_slot_standing_root_xy':native_root,'artist_propagated_curated_ground_pivot_xy':pivot,'previous_v001_final_pivot_unchanged':True,'visible_body_support_contact_diagnostic_xy':actual,'visible_contact_role':'Measured shoes for0/1; body rubble/hand support from2 onward, never hidden foot or actor root.','propagated_root_minus_contact_display_px':[(pivot[0]-actual[0])*s,(pivot[1]-actual[1])*s],'whole_alpha_display_bounds_relative_propagated_root_ltrb':[(bbox[0]-pivot[0])*s,(bbox[1]-pivot[1])*s,(bbox[2]-pivot[0])*s,(bbox[3]-pivot[1])*s],'whole_alpha_display_bounds_relative_contact_recenter_ltrb':[(bbox[0]-actual[0])*s,(bbox[1]-actual[1])*s,(bbox[2]-actual[0])*s,(bbox[3]-actual[1])*s]})
result={'schema':'Guard214-death-standing-root-exact-coordinate-chain-proposal-v002','status':'Artist standing-root propagation registration proposal only, pending Root actual native scene trial and explicit lock. Source poses already Root/worker viewed after E375; no repeated visual review or new visual media.','raw_source':rawpin,'source_manifest':pin(RUN/'frames/frames-manifest.json'),'previous_addendum':pin(OLD/'death214-occluded-feet-native-ground-reference-addendum-v001.json'),'actual_visible_body_contacts':pin(OLD/'death214-body-standing-equivalent-floor-registration-v001.json'),'verified_v001_coordinate_chain':'v001 was correct: source tight origins12/184 etc already exclude group padding. Actual group0 origin8/180 plus alpha-tight crop4/4 gives tight origin12/184, then curated placement91/97 and measuredstanding reference224/463 map to raw145/550. Exact all6 component hashes and tight curated crop RGBA match. Six final pivot candidates remain unchanged.', 'failed_speculative_review_attempt':'Initial newv002 diagnostic assumed v001 origins were still padded and asserted raw149/554; actual reconstruction returned145/550 so that assertion failed. Original failed script is preserved. This was a review assumption error, not a native source/SG QA failure or a v001 defect.','measured_standing_reference_Death0_curated_xy':anchor,'exact_raw_standing_reference_Death0_xy':rawroot0,'native_equal_cell_pitch_design_px':pitch,'propagation_assumption':'Artist chooses one unchanged root reference at Death0 actual shoe-pair midpoint/lowestsole boundary, then translates that reference by one nominal362px native cell per pose. Equal source-cell placement is an ARTIST DESIGN coordinate system, not proof raw guide slot-layout passed or feet remain physically fixed. Feet are occluded after2, so later reference is not measurable anatomy.','rows':rows,'ONE_row_display_scale':s,'standing_equivalent_body_basis_px':365,'ONE_row_canvas_display_px':[512*s,512*s],'perframe_ground_pivot_candidates':[r['artist_propagated_curated_ground_pivot_xy'] for r in rows],'selection_recommendation':'Use standing-root propagation as the first Root native registration trial rather than recentering collapsed pile/hand contacts. It keeps the end whole-alpha footprint around the initial actor reference while allowing natural fall and pile width; no moved kernel actor/root. Root may refine artist references after viewing scene.','body_collapse_height_not_normalized':True,'floor_limit':'Constant source standing plane is not every visible ground-support pixel. Body/axe may sit a few pixels on either side because shallow3/4 perspective and native pose artwork; actual scene ground contact must be reviewed.','gameplay_authority':'Died immediately disables hurt/collision and active attack windows/reward eligibility according to actual kernel, independently of600ms art. Only Death0 first100ms amber afterglow variant allowed by Root amendment; frame1 onward eye OFF. No gameplay delay.','all_source_and_installed_pixels_unchanged':True,'hidden_bones_feet_or_COM_inferred':False,'Root_registration_locked':False}
f=OUT/'death214-standing-root-coordinate-proof-and-trial-candidates-v002.json';f.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(pin(f)));print(json.dumps({'rawroot0':rawroot0,'pivots':result['perframe_ground_pivot_candidates'],'final_footprint_prop':rows[-1]['whole_alpha_display_bounds_relative_propagated_root_ltrb'],'final_footprint_contact':rows[-1]['whole_alpha_display_bounds_relative_contact_recenter_ltrb']}))
