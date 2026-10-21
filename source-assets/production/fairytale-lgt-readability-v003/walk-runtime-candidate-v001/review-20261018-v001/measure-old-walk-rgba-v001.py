from pathlib import Path
from PIL import Image
import hashlib,json,numpy as np

BASE=Path('source-assets/production/fairytale-hero-v001/sprite-run-walk-v008/curated')
RETAINED=Path('E:/OurGame/Knight/过程图稿与视频/2026-10-17-OurgameUE-walk-source-body-v319/F盘原批次副本/2026-10-17_Walk六身体握剑前源复核_v001/原件')
OUT=Path('source-assets/production/fairytale-lgt-readability-v003/walk-runtime-candidate-v001/review-20261018-v001')
ROIS=[{'near':[274,410,375,465],'far':[135,399,225,465]},
 {'near':[193,416,278,465],'far':[282,397,365,441]},
 {'near':[132,400,225,465],'far':[303,397,398,457]},
 {'near':[134,400,222,466],'far':[286,408,389,465]},
 {'near':[275,398,368,456],'far':[179,420,262,466]},
 {'near':[297,391,389,455],'far':[141,407,230,465]}]
PHASES=['near heel contact + far ending rear support','near flat support + far passing',
 'near rear toe support + far reaching','far heel contact + near ending rear support',
 'far flat support + near passing','far rear toe support + near reaching']

def sha(b):return hashlib.sha256(b).hexdigest()
frames=[]
for i,rs in enumerate(ROIS):
 p=BASE/f'frame-{i}.png';ret=RETAINED/p.name
 im=Image.open(p).convert('RGBA');a=np.asarray(im);assert im.size==(512,512)
 assert p.read_bytes()==ret.read_bytes()
 gy,gx=np.nonzero(a[:,:,3]>=128)
 f={'phase':i,'source':p.as_posix(),'retained_original':ret.as_posix(),
  'source_retained_file_bytes_identical':True,'file_sha256':sha(p.read_bytes()),'rgba_sha256':sha(im.tobytes()),
  'size':[512,512],'alpha128_bbox_xyxy':[int(gx.min()),int(gy.min()),int(gx.max())+1,int(gy.max())+1],
  'intended_support_from_source_contract':PHASES[i],
  'support_identity_status':'Visual interpretation consistent with source intent; no persistent material foot landmark or measured physical stance interval',
  'legacy_display_root_source_px':[256,464],
  'legacy_display_root_status':'Actual old engine pivot only; physical body/support root unmeasured',
  'measured_physical_root_source_px':None,'boots':{}}
 for name,(x0,y0,x1,y1) in rs.items():
  ys,xs=np.nonzero(a[y0:y1,x0:x1,3]>=128);ys+=y0;xs+=x0
  y=int(ys.max());bands=[]
  for dy in [0,2,5]:
   xx=xs[ys>=y-dy]
   bands.append({'band_y_min':y-dy,'band_y_max':y,'x_min':int(xx.min()),'x_max':int(xx.max()),'x_mean':float(xx.mean()),'pixel_count':len(xx)})
  f['boots'][name]={'manual_visual_roi_xyxy':rs[name],
   'alpha128_bbox_xyxy':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],
   'lowest_opaque_row_center_source_px':[float(bands[0]['x_mean']),y],
   'lowest_row_endpoint_uncertainty_px':(bands[0]['x_max']-bands[0]['x_min'])/2.,
   'lowest_outline_bands':bands,
   'contact_semantics':'Opaque boot-outline extrema, not proof of a stationary contact/material point'}
 frames.append(f)

factor=(72/416)/.65
proxies=[]
for foot,start,end in [('near',0,2),('far',3,5)]:
 A=frames[start]['boots'][foot];B=frames[end]['boots'][foot]
 d=A['lowest_opaque_row_center_source_px'][0]-B['lowest_opaque_row_center_source_px'][0]
 u=A['lowest_row_endpoint_uncertainty_px']+B['lowest_row_endpoint_uncertainty_px']
 fraction=2/6
 proxies.append({'foot':foot,'phase_start':start,'phase_end':end,'interval_seconds':.083*2,
  'assumed_cycle_fraction':fraction,'apparent_source_contact_dx_px':d,'outline_endpoint_halfwidth_sum_px':u,
  'pure_world_X_cycle_proxy':d*factor/fraction,
  'outline_only_cycle_proxy_range':[(d-u)*factor/fraction,(d+u)*factor/fraction],
  'not_a_physical_stride_measurement':True,
  'unbounded_systematic_errors':['Contact shifts heel to sole to toe rather than tracking one material point.',
   'Physical per-phase root unmeasured; fixed legacy display root is only presentation convention.',
   'Six held images do not prove continuous support or interval fractions.']})

result={'schema':'fairytale-old-walk-rgba-review-measurement-v001',
 'visual_review':'Reviewer viewed retained E319 originals individually at 512x512 before assigning ROIs; no newly generated diagrams or image edits.',
 'alpha_threshold':128,'pixel_coordinate_convention':'Integer pixel centers; bbox right/bottom exclusive',
 'source_phase_seconds':[.083]*6,'source_cycle_seconds':.498,
 'projection':{'world_ground_to_design_screen':[.65,-.38],
  'source_px_to_design_screen':72/416,'UIScale_cancels':True,'pure_world_X_units_per_source_px':factor,
  'limitations':'Source is side-view and one-facing; no diagonal or pure-Y physical stance calibration.'},
 'frames':frames,'contact_proxies':proxies,
 'approximate_art_tuned_cycle_candidate':{'pure_world_X_cycle_distance_world_units':80.,'exploration_range_world_units':[60.,100.],
  'timing_basis_seconds':.498,'confidence':'Low: rounded visual tuning starting point derived from 74/81-unit outline proxies, not measured stance or confidence interval.',
  'production_profile_authorized':False,'current_contract_measured_physical_stride_satisfied':False,
  'foot_lock_implemented':False,'required_next_step':'Retained per-phase Root/contact/material-foot markers plus native both-facing moving proof; either measure physical stance or explicitly approve art-tuned scope before configuring SourceClosureVerified.'}}
target=OUT/'old-walk-rgba-measurement-v001.json'
assert not target.exists()
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'output':target.as_posix(),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'contact_proxies':proxies,'art_tuned_candidate':result['approximate_art_tuned_cycle_candidate']},ensure_ascii=False,indent=2))
