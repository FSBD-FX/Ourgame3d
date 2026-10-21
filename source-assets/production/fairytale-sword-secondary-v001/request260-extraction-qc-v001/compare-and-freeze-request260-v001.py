"""Add numeric260-versus259 QC only; do not alter any technical PNG or old version."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
sys.dont_write_bytecode=True
SKILL=Path('C:/Users/22499/.codex/skills/sprite-gen');sys.path.insert(0,str(SKILL))
from sprite_gen.frames.extract import connected_components
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;OLD=BASE/'request259-extraction-qc-v001'
def pin(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=p.as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def warm_components(a):
 rgb=a[...,:3].astype(np.int32);mask=(a[...,3]>=128)&(rgb[...,0]-rgb[...,1]>=18)&(rgb[...,1]-rgb[...,2]>=14)&(rgb[...,0]>=70)
 out=np.zeros_like(a);out[...,3]=mask.astype(np.uint8)*255
 return [dict(area=x['area'],bbox=list(x['bbox']),width=x['bbox'][2]-x['bbox'][0],height=x['bbox'][3]-x['bbox'][1]) for x in sorted(connected_components(Image.fromarray(out)),key=lambda x:x['area'],reverse=True)]
def nearest(rows,target):
 def d(r):
  x0,y0,x1,y1=r['bbox'];return max(x0-target[0],0,target[0]-(x1-1))**2+max(y0-target[1],0,target[1]-(y1-1))**2
 result=min((x for x in rows if x['area']>=64),key=lambda x:(d(x),-x['area']))
 return dict(**result,target_source_point=list(target),target_to_component_bbox_distance_px=float(d(result)**.5),heuristic_only=True,anatomical_grip_or_glove_measurement=False)
def center(box):return [(box[0]+box[2])/2,(box[1]+box[3])/2]
def centroid(a):
 mask=a[...,3]>=128;y,x=np.nonzero(mask);return [float(np.mean(x)),float(np.mean(y))]
old=read(OLD/'extraction-qc-v001.json');now=read(HERE/'extraction-qc-v001.json');assert now['source_label']=='request260' and now['inputs'][0]['sha256']=='950220ed7af9b0c2e61e927ac852f35846f8b2cc0bf2fed6413753c3fe88593b'
assert pin(OLD/'extraction-freeze-v001.json')['sha256']=='6dad3b4ba041954237916ab765027e59b1f4c24137741ddeccba666b45481e59'
for row in read(OLD/'extraction-freeze-v001.json')['members']+read(OLD/'extraction-freeze-v001.json')['dependency_pins']:assert pin(row['path'])==row
identity_path=BASE/'references/accepted-J1-body-identity.png';ref_warm=warm_components(np.asarray(Image.open(identity_path)));reference_hand=nearest(ref_warm,(159,213))
inputs=[pin(OLD/'extract-uniform-grid-qc-v001.py'),pin(OLD/'extraction-qc-v001.json'),pin(OLD/'extraction-freeze-v001.json')];frames=[]
for index,(a,b) in enumerate(zip(old['frames'],now['frames'])):
 pa=OLD/f'aligned512/K{index}-body-footline464-RGBA.png';pb=HERE/f'aligned512/K{index}-body-footline464-RGBA.png';inputs.append(pin(pa));image_old=np.asarray(Image.open(pa));image_new=np.asarray(Image.open(pb));wa=warm_components(image_old);wb=warm_components(image_new)
 pr_a,pr_b=a['proxies'],b['proxies'];helmet_a=pr_a['helmet_warm_upper55_largest3'][0];helmet_b=pr_b['helmet_warm_upper55_largest3'][0]
 lower_a=sorted(pr_a['lower60_silhouette_largest2'],key=lambda x:x['bbox'][0]);lower_b=sorted(pr_b['lower60_silhouette_largest2'],key=lambda x:x['bbox'][0]);ready_lower=sorted(now['references']['Ready']['proxies']['lower60_silhouette_largest2'],key=lambda x:x['bbox'][0])
 old_center=center(a['aligned512']['bbox_alpha128']);new_center=center(b['aligned512']['bbox_alpha128']);old_foot=sum(pr_a['lower6_solid_span'])/2;new_foot=sum(pr_b['lower6_solid_span'])/2
 target={1:(155,215),2:(150,190),3:(300,300)}.get(index);hand=None
 if target:
  ho=nearest(wa,target);hn=nearest(wb,target);hand=dict(target=list(target),request259=ho,request260=hn,width_ratio_to259=hn['width']/ho['width'],height_ratio_to259=hn['height']/ho['height'],width_ratio_to_accepted_J1_warm_cluster=hn['width']/reference_hand['width'],height_ratio_to_accepted_J1_warm_cluster=hn['height']/reference_hand['height'],caution='Warm connected component may include cuff/forearm and changes with pose; not anatomical hand scale or accepted Grip. K1/2 cluster remains wider than accepted-J1 proxy; K3 needs its own Root markers.')
 frames.append(dict(frame=index,width=b['actual_solid_width'],height=b['actual_solid_height'],width_delta_to259=b['actual_solid_width']-a['actual_solid_width'],height_delta_to259=b['actual_solid_height']-a['actual_solid_height'],
 lower6_span=pr_b['lower6_solid_span'],lower6_span_width=pr_b['lower6_solid_span_width'],lower6_span_ratio_to_Ready=pr_b['lower6_solid_span_width']/now['references']['Ready']['proxies']['lower6_solid_span_width'],lower6_span_ratio_to259=pr_b['lower6_solid_span_width']/pr_a['lower6_solid_span_width'],
 raw627_graphic_bottom_alpha1=b['raw_graphic_foot_boundary_alpha1'],raw627_graphic_bottom_alpha128=b['raw_graphic_foot_boundary_alpha128'],uniform_scale=b['transform']['scale'],x_translation=0,y_integer_translation=b['transform']['y_integer_shift'],final_graphic_bottom_alpha1=b['aligned_graphic_foot_boundary_alpha1'],final_graphic_bottom_alpha128=b['aligned_graphic_foot_boundary_alpha128'],alpha128_footprint_unchanged_by_cleanup=True,
 lower60_components_left_right_heuristic=lower_b,lower60_width_ratios_to_Ready=[q['width']/r['width'] for q,r in zip(lower_b,ready_lower)],lower60_width_ratios_to259=[q['width']/r['width'] for q,r in zip(lower_b,lower_a)],
 helmet_warm_core_heuristic=dict(request259=helmet_a,request260=helmet_b,width_ratio_to_Ready=helmet_b['width']/now['references']['Ready']['proxies']['helmet_warm_upper55_largest3'][0]['width'],height_ratio_to_Ready=helmet_b['height']/now['references']['Ready']['proxies']['helmet_warm_upper55_largest3'][0]['height'],center_x_delta_to259=center(helmet_b['bbox'])[0]-center(helmet_a['bbox'])[0],full_helmet_measurement=False),
 near_hand_warm_cluster_heuristic=hand,
 position_heuristics=dict(whole_alpha128_bbox_center_old=old_center,whole_alpha128_bbox_center_new=new_center,whole_bbox_center_delta=[new_center[i]-old_center[i] for i in range(2)],lower6_span_center_x_old=old_foot,lower6_span_center_x_new=new_foot,lower6_span_center_x_delta=new_foot-old_foot,alpha128_centroid_old=centroid(image_old),alpha128_centroid_new=centroid(image_new),authoring_root_x256_not_anatomically_measured=True,caution='Bbox/centroid changes include pose, hand extension and leg narrowing; do not interpret them as whole-body translation. No registration search or X correction applied.'),
 accepted=False))
report=dict(schema='request260-versus259-numeric-extraction-QC-v001',created_utc=datetime.now(timezone.utc).isoformat(),actual_raw_pin=now['inputs'][0],converter_script_pin=inputs[0],base_converter_output_schema_retained=now['schema'],actual_source_label=now['source_label'],
 actual_raw_size=[1254,1254],raw_cells=[627,627],output_cells=[512,512],all_same_scale=512/627,all_x_translations_zero=True,original259_immutable_members_verified=True,original259_pixel_converter_reused_unmodified=True,
 references=dict(Ready=now['references']['Ready'],accepted_J1=now['references']['accepted_J1'],accepted_J1_hand_warm_cluster_heuristic=reference_hand),frames=frames,
 conclusions=dict(K0to2_graphic_stance='Narrowed to178/176/185 vs Ready184 and259240/239/240',K3_graphic_foot_span='205 vs Ready184 (+11.4%), versus259259 (-20.8%); pose acceptance remains Root visual decision',
 whole_bbox='K1/K2 whole silhouettes remain wide from raised-limb/pose content; cannot use whole bbox alone as zoom/scale proof',helmet='Warm-core widths stable within0..0.5px of259 center and168..173px versusReady168; full helmet dimensions remain OPEN',
 near_hand='Warm-cluster widths63/65/69 versus accepted-J1 proxy46 are a marker/identity risk, but not physical glove measurement; compare poses visually',whole_body_shift='No processing X shift. Helmet warm-core x centers change0/0/+0.5/0px; different wholebbox/foot centers do not prove body sliding'),
 Root_runtime_art_decision='PENDING_Root_after_E658_View',technical_conversion_completed=True,art_or_runtime_accepted=False,physical_anatomical_dimensions='OPEN',creative_image_generation_calls=0,images_viewed=False,actual_Source_Content_tools_E_ledger_status_mutations=0,FinalAccepted=False)
write(HERE/'request260-comparison-qc-v001.json',report)
lines=['# Request260 technical QC handoff','',
 'Original259 converter was run unmodified into this NEW260 directory. Its generic schema/title still says259; actual source_label isrequest260 and raw SHA950220ed… is exact. This supplemental260 report and final260 freeze disambiguate that retained converter metadata. Original259 files and freeze were reverified unchanged.','',
 'All627 RGB cells, chroma627, unshifted512, final aligned512, alpha and cleanup masks are preserved. One512/627 scale, xshift0, integer-Y shifts[-3,-3,+5,+5]. Alpha128 geometry is untouched by uniform edge cleanup. No bbox-fit/warp/art/armor/sword.','',
 'Exact α128 widths242/273/275/283; heights414/414/412/398. Last6 solid-row foot spans178/176/185/205 versus Ready184 and259240/239/240/259. K0–2 graphic stance is much narrower; K3 is still11.4% wider than Ready,20.8% narrower than259.','',
 'Helmet warm-core widths170/173/170/168 compare Ready168; x centers vs259 are0/0/+0.5/0px. Full helmet dimensions/rotation are not segmented. Lower60 silhouette component widths are now76/93,75/92,77/95,83/102 (left/right), versusReady75/95; these include lower leg/pose, not exact boots.','',
 'Near-hand warm clusters closest to prompt points are63×65,65×60,69×61 inK1/K2/K3 versus accepted-J1 proxy46×63. They can include cuff/forearm and pose rotation; this is a risk/Grip-review cue, not measured hand anatomy. K3 nearhand bbox253,263,322,324 requires its own markers; do not copy accepted J1 Grip blindly.','',
 'Wholebbox centers change+13.5/+0.5/+0.5/+2px inX versus259, while helmet core centers remain almost fixed. Narrowed left boot/raised-hand extents alter bbox centers; do not call that whole-body translation. Pipeline never movesX or searches registration. Physical pelvis/root/sole contact remain OPEN.','',
 'Root must retain final full260 packet F/E658 before View. No art/runtime acceptance here; Root visual review is pending. No UE/View/imagegen/Source/Content/tools/E/ledger/status change.']
with (HERE/'HANDOFF-request260-v001.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
# New final closure covers even the unmodified converter's earlier base freeze; do not alter it.
prior=read(HERE/'extraction-freeze-v001.json');deps={Path(x['path']).resolve():x for x in prior['dependency_pins']+inputs};members=[pin(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
for _ in range(2):
 for row in members+list(deps.values()):assert pin(row['path'])==row
output=HERE/'request260-extraction-final-freeze-v001.json';write(output,dict(schema='request260-uniform-extraction-final-QC-freeze-v001',members=members,dependency_pins=list(deps.values()),member_count=len(members),dependency_count=len(deps),verification_passes=2,twoSHA_mismatches=0,technical_derivative_PNG_count=24,original259_unchanged=True,creative_image_generation_calls=0,images_viewed=False,art_or_runtime_accepted=False,Root_review='PENDING_after_E658',FinalAccepted=False))
print(json.dumps(pin(output)));print(json.dumps(dict(widths=[x['width'] for x in frames],heights=[x['height'] for x in frames],foot_spans=[x['lower6_span_width'] for x in frames],y_shifts=[x['y_integer_translation'] for x in frames],helmet_widths=[x['helmet_warm_core_heuristic']['request260']['width'] for x in frames],nearhand_bbox_widths=[None]+[x['near_hand_warm_cluster_heuristic']['request260']['width'] for x in frames[1:]])))
